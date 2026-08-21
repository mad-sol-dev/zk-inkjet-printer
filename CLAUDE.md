<!-- ZK-TRUTH-RULES: Anfang. Diese Sitzungsregeln gelten fuer jede Sitzung,
     unabhaengig davon, in welchem Chat sie stattfindet. -->

# Regeln fuer jede Sitzung an diesem Projekt

**Autoritativ ist `research/TRUTH.csv`. Sonst nichts.** Die Spielregeln stehen
in `research/TRUTH.md`, die Pruefung in `tools/scripts/check_truth.py`.

1. **Sitzungsanfang -- ein Befehl:** `python3 tools/scripts/next.py`. Er prueft
   die Datei, druckt die Arbeitsfront (`Prio=now`, hoechstens 6 Zeilen) mit dem
   jeweils naechsten Test und die Restmenge. Meldet er einen Verstoss, wird der
   zuerst behoben. Sonst wird an der Front gearbeitet, nicht an etwas anderem.
2. **Eine Sitzung darf** Zeilen in `TRUTH.csv` aendern oder hinzufuegen und
   Rohartefakte erzeugen. **Eine Sitzung darf kein neues beschreibendes
   Dokument anlegen.** `research/system_understanding.md` und alles daneben ist
   abgeleitet und nicht autoritativ.
3. **Keine Kopien** von `TRUTH.csv`. Git ist die Historie. Vor groesseren
   Aenderungen committen, nicht kopieren.
4. **Keine offene Zeile ohne `Next_Test`.** Eine Frage ohne definiertes
   Experiment ist kein Arbeitspaket, sondern ein Thema.
5. **Zeilen werden nie geloescht**, nur per `Superseded_By` abgeloest.
6. **Ein Negativbefund aus einem Werkzeug ist erst dann ein Fakt, wenn die
   Methode als tauglich belegt ist.** Ghidras Scalar-Suche findet keine
   Konstantenpool-Worte (CL-TOOL-REC-101); eine Byte-Suche in der Datei findet
   keine ARM-Immediates (CL-TOOL-REC-108). Beide Suchmodi laufen lassen.
7. **Alte Dokumente sind Quellen, keine Autoritaeten.** Ihre Aussagen gelten
   erst, wenn sie als Zeile in `TRUTH.csv` stehen -- mit Evidenzstufe.
   Autoritaetshierarchie: E0 > E3-New > E1-Recent > E1 > E3-Old > E4.
8. **Sitzungsende:** `check_truth.py` sauber, committen, Front nachfuehren
   (erledigte `now`-Zeilen schliessen, aus `next` nachruecken). Nicht
   committete Arbeit ist die haeufigste Verlustursache in diesem Projekt
   gewesen.

<!-- ZK-TRUTH-RULES: Ende -->

# CLAUDE.md

Diese Datei ist die **Bedienungsanleitung** fuer das Projekt: wie man die
Werkzeuge benutzt und welche Konventionen gelten. Sie ist **kein Statusbericht**.
Der Stand steht in `research/TRUTH.csv` und wird mit `python3 tools/scripts/next.py`
abgerufen. Frueher stand hier ein zweiter, konkurrierender Status -- der war nach
drei Wochen falsch und hat genau das Chaos erzeugt, gegen das die Regeln oben
geschrieben wurden.

## Projekt

Reverse Engineering der Firmware eines ZK-INKJET-Handdruckers. SoC ist ein
Nuvoton N32903U5DN (ARM926EJ-S). Ziel ist es, das Geraet vom PC aus zu treiben,
um Lithiumzellen automatisch zu beschriften -- also einen Weg zu finden, ein
Etikett von aussen in das Geraet zu bekommen und den Druck auszuloesen.

## Sitzungsablauf

1. `python3 tools/scripts/next.py` -- prueft die Datei und druckt die Front.
2. An der Front arbeiten. Nicht an etwas anderem.
3. Ergebnisse als Zeilen in `TRUTH.csv`, nicht als Prosa daneben.
4. `python3 tools/scripts/check_truth.py` sauber, committen, Front nachfuehren.

Ein pre-commit-Hook laesst `check_truth.py` mitlaufen.

## TRUTH.csv wird atomar geschrieben -- nie in place

`TRUTH.csv` ist die einzige autoritative Datei des Projekts. Sie wird **niemals
direkt zum Schreiben geoeffnet.** Der Grund ist nicht theoretisch: am
2026-08-21 hat ein Skript `open(P, 'w')` ausgewertet, ist danach an einem
Tippfehler in derselben Zeile abgebrochen -- und hinterliess eine Datei mit
null Bytes. Python oeffnet und kuerzt, bevor es den Rest des Aufrufs prueft.
Ein `assert` weiter unten im Skript kommt zu spaet.

Richtig ist: in eine Temporaerdatei schreiben, das Ergebnis pruefen, dann
`os.replace` -- das ist auf einem Dateisystem atomar, es gibt keinen Zustand
dazwischen.

```python
import csv, os
P = 'research/TRUTH.csv'; T = P + '.tmp'
rows = list(csv.DictReader(open(P, encoding='utf-8')))
COLS = list(rows[0].keys())
n_vorher = len(rows)

# ... Zeilen aendern oder anhaengen ...

with open(T, 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader(); w.writerows(rows)
assert len(rows) >= n_vorher, 'Zeilen verschwunden'
os.replace(T, P)
```

Drei Punkte dazu:

- **Zeilenzahl darf nie sinken.** Regel 5 oben: Zeilen werden nie geloescht,
  nur per `Superseded_By` abgeloest. Ein `assert` auf die Zeilenzahl faengt
  jeden Schreibfehler, der das verletzt.
- **`newline=''` und `csv.DictWriter`** beibehalten -- die Datei hat CRLF, und
  `csv` schreibt genau das. Ohne `newline=''` entsteht ein Diff ueber alle 259
  Zeilen statt ueber die geaenderten.
- **Wenn es doch passiert:** `git checkout -- research/TRUTH.csv`. Deshalb
  steht in Regel 3 oben, dass vor groesseren Aenderungen committet wird. Am
  2026-08-21 hat genau das den Schaden auf null reduziert.

Vorsicht auch bei `check_truth.py`: bei leerer Datei bricht es derzeit mit
einem `IndexError` ab statt einen Verstoss zu melden. Ein Traceback ist dort
also ein Alarmzeichen, kein Werkzeugproblem.

## MCP-Server

**Die Server werden ueber Werkzeugnamen angesprochen, nicht ueber URLs.** Wer
mit `curl` am Port misst, misst nichts: der SSE-Endpunkt antwortet einem
gewoehnlichen GET nicht sinnvoll, und ein leeres Ergebnis sagt nichts darueber
aus, ob der Server laeuft. Das ist am 2026-08-21 einmal passiert und hat eine
halbe Sitzung auf den Umweg geschickt. Richtig ist:

```
mcp__zk-inkjet-ghidramcpd__get_current_program
```

Liefert `state: READY` (Analyse fertig, alle Abfragen erlaubt) oder `LOADING`
(die meisten Abfragen verweigern). Das ist der Lebenstest.

Bei Claude Code sind die Werkzeuge **deferred**: die Namen stehen zwar im
Kontext, die Schemata aber nicht. Vor dem ersten Aufruf einmal laden --

```
ToolSearch: select:mcp__zk-inkjet-ghidramcpd__get_current_program,mcp__zk-inkjet-ghidramcpd__disassemble_at
```

-- danach sind sie normal aufrufbar. Ein direkter Aufruf ohne das vorherige
Laden scheitert mit `InputValidationError`; das ist kein Serverproblem.

Nuetzliche Operationen: `project_overview`, `select_program`, `search_strings`,
`search_functions`, `search_scalars` / `search_scalars_with_context`,
`search_xrefs_to`, `disassemble_at` / `disassemble_batch`, `read_bytes` /
`read_words`, `find_in_function`. Mehrere Abfragen buendelt `collect` in einem
Aufruf -- das ist bei Token-Budget der Normalfall, nicht die Ausnahme.

Aktives Programm ist `ZK-INKJET-NANO-APP.bin.orig`; das ist die gepflegte
Datenbank (CL-TOOL-REC-102), nicht die Datei ohne Suffix.

Der Bridge war am 2026-08-21 noch in Erprobung. **Ein leeres Ergebnis ist
deshalb kein Befund, sondern ein Anlass, dieselbe Frage mit eigenem Code ueber
der Rohdatei zu wiederholen.** Siehe CL-TOOL-REC-114.

## Konstantensuche -- vier Modi

Regel 6 oben verlangt, dass eine Methode als tauglich belegt ist, bevor ihr
Negativbefund zaehlt. Praktisch heisst das, es gibt vier Wege, wie eine
32-Bit-Konstante im Bild auftaucht, und keiner findet die anderen:

| Modus | Werkzeug | blind fuer |
|---|---|---|
| Literalpool | Bytesuche ueber die Datei | ARM-Immediates (CL-TOOL-REC-108) |
| Immediate | Ghidra `search_scalars` | Poolwoerter (CL-TOOL-REC-101) |
| ADR (`ADD/SUB Rd,PC,#imm`) | eigener Decoder | beide (CL-TOOL-REC-114) |
| Immediate-Kette (MOV + ORR/ADD) | eigener Decoder | beide (CL-TOOL-REC-114) |

Zwei Fallen dazu: Eine Scalar-Suche nach einem Wert, der gar kein kodierbares
ARM-Immediate ist (8 Bit rotiert), ist keine Frage, sondern ein Nullergebnis
per Konstruktion. Und eine dichte, monotone Tabelle trifft einen grossen Teil
der ausgerichteten Adressen eines Bereichs von allein -- eine hohe Trefferquote
gegen eine Kandidatenmenge beweist ohne Dichte-Vergleich nichts.

## Adresskonventionen

- **VA = Dateioffset + 0x00200000.** APP.bin wird nach 0x00200000 geladen
  (CL-BOOT: entschieden, nicht 0x03000000). Schreibweise:
  `VA 0x0020C798 (file+0xC798)`.
- **MMIO** liegt in 0xB0000000-0xBFFFFFFF und wird immer als solches
  gekennzeichnet: `MMIO 0xB1008000 (USB_BA)`.
- **ARM/Thumb gemischt.** Thumb-Code liegt im Bereich 0x00210000-0x0021FFFF
  (CL-BOOT-REC-016). Das heisst *nicht*, dass ARM auf 0x00200000-0x0020FFFF
  beschraenkt waere -- der weitaus groesste Teil des Bildes darueber ist
  ebenfalls ARM, etwa `mov r8,#0x28800000` bei 0x00265FE4.

## Repository

```text
firmware/bin/        ZK-INKJET-NANO-APP.bin (2576940 B), -BOOT.bin
firmware/image/      SD-Karten-Abzuege
research/TRUTH.csv   die einzige autoritative Quelle
research/TRUTH.md    die Spielregeln dazu
research/phase_a_sd_analysis/artifacts/   Rohartefakte aus der Kartenanalyse
research/findings/n32903_registers.json   MMIO-Registerkarte (1544 Eintraege)
tools/scripts/       next.py, check_truth.py, Decoder und Carving-Helfer
vendor/              Datenblaetter und BSP (gitignored, liegen flach in vendor/)
ghidra_projects/     Ghidra-Projekt zk-inkjet
```

Abgeleitete Artefakte gehoeren nach `research/phase_a_sd_analysis/` mit
deterministischen Namen. `firmware/bin/` und `firmware/image/` gelten als
unveraenderlich -- nie in place bearbeiten.

## Eingefroren -- Quellen, keine Autoritaeten

Nach Regel 7 gelten Aussagen aus diesen Ablagen erst, wenn sie als Zeile in
`TRUTH.csv` stehen. Es wird dort **nicht mehr geschrieben**:

- `research/findings/.re_kb/` und `research/findings/re_kb_archive/` -- beide
  RE-KBs sind eingefroren, ihre IDs kollidieren (CL-TOOL-REC-103). Eine
  Finding-ID allein ist keine gueltige Referenz.
- `research/sessions/` -- alte Sitzungsprotokolle bis 2025-12. Neue Sitzungen
  legen dort nichts mehr an (Regel 2).
- `research/system_understanding.md`, `research/docs_rebuild/` und die
  Berichte daneben -- abgeleitet, teils veraltet.

## Vendor-Unterlagen und der PDF-Reader

Die PDFs liegen **flach in `vendor/`**, nicht in `vendor/datasheets/`. Der BSP
unter `vendor/N32901-3_NonOS_BSP/` ist fuer genau diesen Chip uebersetzt und
schlaegt bei Konflikt den generischen Design Guide.

Der `pdf-reader`-MCP ist angebunden und am 2026-08-21 nach dem Systemneuaufbau
geprueft. Wie bei Ghidra gilt: Schemata erst per `ToolSearch` laden, dann
aufrufen.

```
ToolSearch: select:mcp__pdf-reader__pdf_read,mcp__pdf-reader__pdf_search
```

Der Server wurde am selben Tag nachgebessert; seither laufen alle acht
Werkzeuge, `pdf_info`, `pdf_read`, `pdf_search`, `pdf_extract_image`,
`pdf_vision`, `pdf_ocr`, `pdf_ocr_document` und der Cache-Reset. Zwei Dinge
bleiben wissenswert:

- **Pfade absolut angeben.** Das Arbeitsverzeichnis des Servers ist nicht das
  Repository.
- **`pdf_search` sucht das ganze Dokument** und meldet das jetzt nachpruefbar
  mit `pages_searched` und `total_pages` im Ergebnis. Ein `total_hits: 0` ist
  damit ein echter Negativbefund -- vorausgesetzt, `pages_searched` deckt das
  Dokument ab. Bei gesetztem `max_hits` bricht die Suche frueher ab, dann ist
  `pages_searched` kleiner und sagt genau, wie weit gesucht wurde.

`pdf_read` liefert Text mit `[IMAGE n: BxHpx]`-Markern; `pdf_extract_image`
holt das Bild dazu als PNG. Das UDC-Blockdiagramm auf Seite 485 ist so
zugaenglich.

Fundstellen im Design Guide (`N3290x_Design_Guide_A1.pdf`, 897 Seiten):

| Thema | Seiten |
|---|---|
| System Memory Map | 47-49 |
| **USB 2.0 Device Controller (Kap. 6.13)** | **484 ff., Registeruebersicht 485** |
| Interrupt Controller (AIC), Vektortabelle | 624-644, UDC_INT ist IRQ 16 auf S. 625 |
| GPIO Controller | 645-668 |
| Timer Controller | 669-680 |
| UART Controller | 750-779 |
| SPI Controller | 780-811 |

Achtung, das Dokument widerspricht sich bei den Endpunkten: S. 11 nennt sechs
konfigurierbare Endpunkte, S. 484 vier plus Control-Endpunkt. Fuer USB-CDC
(zwei Bulk plus ein Interrupt) reicht beides, aber die Zahl ist nicht belegt,
solange sie nicht am BSP oder am Geraet geprueft ist.
