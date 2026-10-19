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
   abgeleitet und nicht autoritativ. Sitzungen koennen sich irren und
   Irrwegen folgen; die Triage, das Destillat, ist `TRUTH.csv`. Ein
   Sitzungslog in `research/sessions/` erzaehlt diese Geschichte und entsteht
   nur, wenn der Maintainer es verlangt (Format im README dort).
3. **Das Register nur ueber das Werkzeug aendern:** `tools/scripts/truth.py`
   (Kommandozeile) oder die `truth_*`-Werkzeuge des MCP-Servers `truth`. Keine
   eigenen Schnipsel -- eines davon hat die Datei am 2026-08-21 auf null Bytes
   gekuerzt. Kann das Werkzeug etwas nicht, wird es in der Vorlage
   `truth-register` (eigenes Repository, lokal `../../truth-register`)
   erweitert (mit Selbsttest) und hierher kopiert, nicht umgangen. Keine Kopien von `TRUTH.csv`; Git ist die
   Historie.
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

9. **Eine Zelle ist ein Urteil, kein Laborjournal.** `Statement` nennt das
   Urteil zuerst, dann die tragenden Belege -- hoechstens 2000 Zeichen,
   `Next_Test` hoechstens 1000 (ab 2026-10-16 geaenderte Zeilen, der
   Validator prueft es). Der Weg dorthin steht in den Commit-Nachrichten mit
   der Claim-ID. Ein Ergebnis, das fuer sich gilt, wird eine eigene Zeile.

10. **Das Repository ist englisch.** Was neu ins Repository kommt, wird
    englisch geschrieben: Zellen in `TRUTH.csv` (Topic, Statement,
    Next_Test, Evidenz), Commit-Nachrichten, Kommentare und Docstrings,
    Ausgaben und Meldungen von Skripten, neue Dateien. Die Unterhaltung mit
    dem Maintainer bleibt deutsch. Der deutsche Bestand wird nicht
    nachtraeglich uebersetzt; wer eine Zelle ohnehin neu schreibt, schreibt
    sie englisch. Ergaenzungen in einer bestehenden deutschen Datei folgen
    der Sprache der Datei, bis sie als Ganzes uebersetzt wird -- eine Datei
    halb deutsch, halb englisch hilft niemandem.

11. **Erkunden mit jedem Mittel, belegen nur mit einem wiederholbaren.**
    Inline-Python, capstone und Skripte im Scratchpad sind zum Suchen
    erlaubt. Was als Zahl, Zaehlung, Mengenvergleich oder Negativbefund in
    eine O2-Zeile geht, laeuft ueber die Bruecke (Werkzeug mit Argumenten
    oder `run_script <skript>.py`) oder ueber ein versioniertes Skript,
    unter `tools/scripts/` oder neben seiner Ausgabe im Artefaktordner.
    `Evidence_E0` nennt genau diesen Aufruf. Ein Skript, das nur im
    Scratchpad lag, ist kein Beleg, Prosa wie 'python3 Bytesuche nach ...'
    auch nicht. Ein Disassemblat an genannten Adressen ist eine Lesung und
    darf so stehen.

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

Ein pre-commit-Hook laesst `check_truth.py` mitlaufen. Ein pre-push-Hook
prueft die ausgehenden Commits mit `tools/scripts/check_privat.py` auf private
Daten (Login, Hostname, Heimatpfad, MAC-Adressen/BSSIDs, dazu lokale Muster aus
`.git/info/privat-muster`) und laedt danach die LFS-Objekte hoch. Beide liegen
in `.githooks/` (aktiv ueber `git config core.hooksPath .githooks`); Selbsttest:
`python3 tools/scripts/check_privat_selbsttest.py`.

Nach jedem Commit (ebenso nach pull, Branchwechsel, rebase) erzeugt ein
post-commit-Hook die Ansicht des Registers neu: `build/truth_ansicht.html`
(gitignored), eine Seite mit Front, einem Graphen der Abhaengigkeiten,
tragenden Zeilen, Registertabelle mit Filtern, Verweisen in beide Richtungen
und dem Laborjournal je Zeile. Sie ist aus `TRUTH.csv` und `git log`
abgeleitet und fuehrt nichts Eigenes. Den Graphen ordnet Graphviz an (`dot`,
Paket graphviz); fehlt es, entsteht die Seite ohne Graph. Von Hand:
`python3 tools/scripts/truth_ansicht.py --oeffnen`. Oeffentlich baut
`.github/workflows/register-ansicht.yml` dieselbe Seite bei jedem Push auf
master: https://mad-sol-dev.github.io/zk-inkjet-printer/

Derselbe Hook und derselbe Workflow erzeugen die Kartenkarte
`build/card_map.html` (oeffentlich `.../card_map.html`): was wo auf der Karte
liegt, wer es schreibt und liest, und den Update-Weg. Inhalt sind die Tabellen
`REGIONS`, `FLOW` und `FACTS` in `tools/scripts/card_map.py`; jeder Eintrag
nennt seine Claim-IDs. Geschrieben wird die Seite nur, wenn jede zitierte Zeile
entschieden, nicht abgeloest, nicht O1 und mit Konfidenz ab 0.9 ist; sonst
nennt das Skript die Zeilen und bricht ab. Wer eine dort zitierte Zeile
abloest oder einen Bereich neu klaert, zieht die Tabelle nach. Pruefen ohne
Schreiben: `python3 tools/scripts/card_map.py --check`.

## Register lesen und aendern -- tools/scripts/truth.py

Seit 2026-10-15 gibt es dafuer ein Werkzeug, statt dass jede Sitzung ihr
eigenes Skript schreibt. Es ist dieselbe Datei wie in der Vorlage
`truth-register` (lokal `../../truth-register`); was ZK-Inkjet anders hat (Evidenz in
`Evidence_E0` als `Anzahl [Beleg]`, Vorgaben fuer die Altspalten), steht in
`tools/scripts/truth_local.py`.

```bash
python3 tools/scripts/truth.py front
python3 tools/scripts/truth.py find --offen --subsystem USB
python3 tools/scripts/truth.py show CL-USB-REC-131 --felder Statement,Next_Test
python3 tools/scripts/truth.py deps CL-BOOT-REC-113
python3 tools/scripts/truth.py journal CL-USB-REC-128        # das Laborjournal einer Zeile
python3 tools/scripts/truth_ansicht.py --oeffnen             # das ganze Register im Browser
python3 tools/scripts/truth.py add --subsystem USB --topic "..." --statement "..." \
        --oracle O1 --confidence 0.5 --next-test "..." --prio next --depends CL-BOOT-REC-113
python3 tools/scripts/truth.py close CL-USB-REC-131 --oracle O3 --confidence 0.95 \
        --evidence "Vorgang am Geraet, Testkarte, Abzug ..." --urteil "..." --dry-run
python3 tools/scripts/truth.py supersede CL-ALT --by CL-NEU --notiz "warum"   # listet Abhaengige
python3 tools/scripts/truth.py commit "truth: CL-USB-REC-131 -- Weg zum Urteil"
```

Jede Aenderung wird vor dem Schreiben mit `check_truth.py` geprueft und nur
geschrieben, wenn sie keinen Verstoss bringt, den es vorher nicht gab.
`--dry-run` zeigt sie vorher. Lange Texte: `--json datei.json` oder `-` fuer
stdin, statt Anfuehrungszeichen in der Shell. Bei `supersede` schreibt das
Werkzeug nichts, solange nicht ueber jede abhaengige Zeile entschieden ist
(`--umhaengen` oder `--mitabloesen`).

Derselbe Funktionsumfang als MCP-Server: `tools/scripts/truth_mcp.py`, fuer
Claude Code eingebunden ueber eine lokale `.mcp.json` (gitignored; Vorlage
`mcp/claude-code.mcp.json.example`, einfach kopieren) (Werkzeuge `truth_front`,
`truth_find`, `truth_show`, `truth_deps`, `truth_journal`, `truth_check`,
`truth_add`, `truth_close`, `truth_supersede`, `truth_set`, `truth_prio`,
`truth_commit`). Fuer die Desktop-App denselben Eintrag mit absolutem Pfad in
deren Konfiguration.

Nach einer Aenderung am Werkzeug oder am Validator:
`python3 tools/scripts/truth_selbsttest.py` -- muss "Alle Kontrollen
bestanden" melden. Der laufende MCP-Server laedt `check_truth.py` bei jedem
Aufruf neu, eine Regelaenderung gilt also sofort; eine Aenderung an `truth.py`
selbst wirkt dort erst nach einem Neustart des Servers.

## TRUTH.csv wird atomar geschrieben -- nie in place

Das Folgende ist der Hintergrund und der Notfallweg, wenn das Werkzeug nicht
verfuegbar ist. Im Normalfall schreibt nur `truth.py`.

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

**Ghidra-Skripte ueber `run_script`** liegen in `tools/scripts/ghidra/`
(`GHIDRA_MCP_SCRIPT_DIR`). Erst mit `dry_run=true` laufen lassen, dann echt.
Ob ein Skript durchgelaufen ist, sagt nur `data.ok`, nicht das aeussere `ok`
der Antwort (CL-TOOL-REC-124). Vor Plugin 1.3.71 kamen Jython-Fehler still mit
`ok:true` zurueck; solche Ergebnisse sind nicht belegt.

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

- **VA = Dateioffset + 0x00058000.** APP.bin ist nach 0x00058000 gelinkt und
  wird dorthin geladen (CL-BOOT-REC-113, gemessen am Scatter-Table der Datei).
  Schreibweise: `VA 0x00064798 (file+0xC798)`. BOOT.bin liegt bei 0x00700000.
- **Achtung, zwei Zaehlweisen.** Bis zum 2026-08-31 galt `Dateioffset +
  0x00200000`. Die Ghidra-Datenbank ist seit dem 2026-10-11 auf 0x00058000
  verschoben (CL-TOOL-REC-121), der MCP-Server nennt also die richtigen
  Adressen. Jede aeltere Zeile in `TRUTH.csv` und jedes aeltere Protokoll
  nennt dagegen Adressen, die um **0x1A8000 zu hoch** sind. Die Dateioffsets stimmen in beiden Zaehlweisen -- deshalb ist
  keiner der alten Befunde falsch, nur jedes alte Etikett. Im Zweifel den
  Dateioffset nennen; der ist eindeutig.
- **MMIO** liegt in 0xB0000000-0xBFFFFFFF und wird immer als solches
  gekennzeichnet: `MMIO 0xB1008000 (USB_BA)`.
- **Unterhalb des Images** liegt kein zweites Programm, sondern die RW/ZI-Region,
  die APP.bin sich beim Start selbst anlegt: 0x00000000-0x00044FC0, mit der
  ARM-Vektortabelle bei 0 (CL-BOOT-REC-114). Absolute Adressen wie `0x7D8` oder
  `0x82EC` sind Globals dort und stehen in keiner Datei.
- **ARM/Thumb gemischt.** Thumb-Code liegt laut Ghidra-Listing vor allem bei
  file+0xC74C-0x11B72, file+0x27550-0x29F62 und file+0xC3A18-0xC3FF8, dazu
  einige Kleinstlaeufe (CL-BOOT-REC-117, gemessen mit
  `tools/scripts/ghidra/thumb_ranges.py`). Das fruehere Fenster
  file+0x10000-0x1FFFF (CL-BOOT-REC-016) war falsch. Eigene Decoder nehmen
  die Thumb-Bereiche aus dem Listing, nicht aus einem festen Fenster; das
  Listing selbst ist eine Untergrenze. Alles uebrige Code ist ARM, etwa
  `mov r8,#0x28800000` bei file+0x65FE4.

## Patches live testen -- ohne die Karte zu schreiben

APP.bin laeuft auch aus dem RAM, hochgeladen ueber den USB-Boot des
Boot-ROMs (am Geraet seit 2026-10-18: Original mit Diagnose M0 A0, Endstand
VBUS-Waechter mit 42 s Kabel ziehen). Werkzeuge: das Nachbar-Repository
`../n329-usbboot` (Linux-Ersatz fuer TurboWriter, eigenes Git, Belege in
dessen README und `docs/protocol.md`) und hier `tools/scripts/live_image.py`.

Einmal am PC einrichten (sudo, macht der Maintainer): udev-Regel und
usb-storage-Quirk aus `../n329-usbboot/linux/`. Ohne den Quirk haelt der
Kernel den Boot-ROM fuer eine 1-TiB-Platte, liest deren letzten Sektor und
setzt das Geraet nach 30 s zurueck.

```bash
# 1. Platine ohne SD-Karte an USB: Boot-ROM meldet sich als 0416:9396
(cd ../n329-usbboot && python3 -m n329usb list)
# 2. Karte einstecken, dann:
python3 tools/scripts/live_image.py --stand vbus_waechter_end --run
python3 tools/scripts/live_image.py --patch 0xVA=ALT:NEU --run     # Versuch auf dem Original
```

Was passiert: BOOT.bin nach 0x700000, in der Kopie Wort 0x702FC8
`ldr r0,[r5]` -> `b 0x703028` (beide SD-Lesungen der APP.bin und der memcmp
uebersprungen), der Block nach 0x58000, Start bei 0x700000. BOOT.bin stellt
den Takt ein, zeigt das Startbild von der Karte und springt in die Kopie. Auf
die Karte wird nichts geschrieben.

Der Block ist das, was BOOT.bin sonst von der Karte liest: 0x280000 Bytes,
Image plus Stub-Sektoren dahinter (ab Datei 0x275400), Rest Null. Ein
Patch-Stand ist also nicht nur seine Image-Datei; seine Stub-Sektoren liegen
oft in mehreren Artefaktordnern, weil die Patches aufeinander aufbauen. Neue
Staende in `STANDS` in `live_image.py` eintragen. Das Skript prueft das
ALT-Wort jedes `--patch`, rechnet danach den MD5-Kopf neu und schreibt
keinen Block, dessen Pruefwert [0x558] nicht 0 ist (sonst Dauerton und
'NG', CL-FIRMWARE-REC-119).

Grenzen:

- **Ohne Batterie** startet der Drucker beim Oeffnen des Druck- oder
  Diagnosemenues oft neu, zufaellig und auch beim Kartenboot, also nicht
  wegen des USB-Boots (CL-HARDWARE-REC-118). Tests, die diese Menues
  oeffnen, also mit Batterie. Ohne Batterie kommt ausserdem zuerst der
  Ladebildschirm, und Hooks in `ui_main_loop` laufen erst nach einem Tippen
  auf den Bildschirm.
- **Die RAM-Kopie verschwindet erst stromlos.** Zum Aufraeumen USB und
  Batterie ab.
- **Ein Reset bootet die Karte.** Steckt die Karte, startet nach einem Reset
  (etwa dem Watchdog oder dem Neustart ohne Batterie) die Firmware von der
  Karte, und alle weiteren Versuche laufen dann unbemerkt auf ihr. Deshalb
  einen sichtbaren Marker mitpatchen, etwa ein geaendertes Etikett in einer
  Diagnosezeile (so in CL-HARDWARE-REC-118 mit 'VOFF'), und nach jedem
  Neustart neu hochladen.

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
- `research/sessions/` -- die Protokolle der RE-KB-Zeit bis 2026-01 werden
  nicht mehr geaendert. Neue Logs kommen nur dazu, wenn der Maintainer es
  verlangt (Regel 2); sie erzaehlen und belegen nichts.
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
