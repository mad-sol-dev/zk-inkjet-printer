# TRUTH.csv — die einzige autoritative Quelle

`research/TRUTH.csv` ist der Stand des Projekts. Alles andere im Repository ist
Rohmaterial, Herleitung oder Archiv.

## Herkunft

Basis sind die 152 Aussagen der Phase-1-Reconciliation (2026-01-02 bis 2026-01-05,
`docs_rebuild/CONFIDENCE_MATRIX.csv`). Ergänzt am 2026-08-19 um 16 Zeilen: die
RE-KB-Findings 0003–0011 vom Januar, die nie in die Matrix eingespeist wurden, und
die Ergebnisse der Verifikationssitzung vom selben Tag.

## Spalten

Die ersten 14 Spalten stammen unverändert aus der Reconciliation:
`Subsystem, Topic, Statement, Status, Confidence, Evidence_E0, Evidence_E3New,
Evidence_E1, Evidence_E3Old, Evidence_E4, Authority, Open_Question, Next_Test, Claim_ID`

Neu hinzugekommen:

| Spalte | Bedeutung |
|---|---|
| `Decided` | `yes` = Frage ist beantwortet, `no` = offen. Für die 152 Altzeilen aus `Status` abgeleitet (verified/refuted → yes); bitte beim Durchgehen korrigieren. |
| `Superseded_By` | Claim-ID, die diese Zeile abgelöst hat. Zeilen werden **nie gelöscht** — nur überschrieben markiert. |
| `Updated` | Datum der letzten Änderung. |
| `Source` | Woher die Zeile stammt. |
| `Prio` | Nur bei `Decided=no`. `now` = Arbeitsfront (hoechstens 6 Zeilen, handverlesen), `next` = Nachruecker aus laufender Arbeit, `later` = Altlast aus der Phase-1-Reconciliation, `park` = betrifft unser Werkzeug, nicht das Geraet. Bei entschiedenen Zeilen leer. |
| `Depends_On` | Claim-IDs, mit `;` getrennt, auf denen diese Zeile *steht*. Probe: waere die genannte Zeile falsch, fiele diese hier mit. Macht tragende Zeilen zaehlbar und Abloesungen durchreichbar. |
| `Oracle` | Was die Aussage geprueft hat, nicht wie sicher sie sich anfuehlt. `O1` hergeleitet (Deckel c=0.60), `O2` wiederholbares Kommando ueber eine Datei (0.95), `O3` beobachtetes Geraeteverhalten (1.00). Geht die Zeile ueber das hinaus, was das Kommando ausgibt -- Identitaet, Zweck, Bedeutung -- ist sie O1. Pflicht fuer Zeilen mit `Updated` ab 2026-08-22. |

`Prio` ist am 2026-08-20 eingefuehrt worden, weil 128 offene Zeilen keine Karte
sind, sondern eine Wand. Die Vergaberegel ist mechanisch und jederzeit
nachvollziehbar: `park` per Namensliste (Werkzeugzeilen) oder wenn `Next_Test`
leer im Sinne von *None required* ist, `now` per Handauswahl, `later` fuer alles
mit `Source = Phase-1-Reconciliation`, `next` fuer den Rest.

`Open_Question` stand in allen 152 Altzeilen auf `YES` und war damit als Filter
wertlos — deshalb `Decided`. Die alte Spalte bleibt zur Nachvollziehbarkeit stehen.

## Autoritätshierarchie

`E0 > E3-New > E1-Recent > E1 > E3-Old > E4`

- **E0** — Artefakte: BSP-Header, Datenblätter, Binärbefunde, empirische Gerätetests
- **E3-New** — aktuelles RE-KB (nach Ghidra-Optimierung)
- **E1** — Chat-Transkripte
- **E3-Old** — archiviertes RE-KB (31 Findings, `[ghidra-v1]`)
- **E4** — alte Dokumentation

Bei Konflikt gewinnt die höhere Stufe. Diese Regel hat historisch funktioniert:
sie hat die UDC-Basisadresse, die SoC-Variante, den Display-Controller und
SPI0_BA korrigiert.

## Arbeitsregeln

1. **Eine Session ändert Zeilen oder fügt Zeilen hinzu.** Sie legt kein neues
   beschreibendes Dokument an. Genau daran ist es im Januar gekippt: nach dem
   6. Januar wurde wieder Prosa produziert statt Zeilen, und binnen neun Tagen war
   die Matrix veraltet.
2. **Zusammenfassungen werden aus TRUTH.csv abgeleitet, nie als zweiter Stand
   gepflegt.** Die fruehere `system_understanding.md` ist am 2026-10-20
   entfernt worden; Git hat sie.
3. **Keine Zeile ohne `Next_Test`, solange `Decided=no`.** Eine Frage ohne
   definiertes Experiment ist kein Arbeitspaket, sondern ein Thema — und Themen
   sind das, was das Chaos erzeugt hat.
4. **Beide RE-KBs sind eingefroren** (`re_kb_archive/` und `.re_kb/`). Sie bleiben
   als Detailarchiv lesbar; geschrieben wird nur noch hier. Ihre IDs kollidieren
   (siehe CL-TOOL-REC-103) — eine Finding-ID allein ist keine gültige Referenz.
5. **Ein Negativbefund aus einem Werkzeug ist erst dann ein Fakt, wenn die Methode
   als tauglich belegt ist.** Siehe CL-TOOL-REC-101: acht Monate lang galt der
   USB-Pfad als blockiert, weil eine Ghidra-Scalar-Suche Konstantenpool-Literale
   nicht findet.

6. **Eine Zeile steht nur so hoch wie das, was sie geprueft hat.** Die
   `Oracle`-Stufe wird vor der Konfidenz vergeben und deckelt sie. Geht die
   Aussage ueber das hinaus, was das Kommando ausgibt, ist sie O1 -- auch wenn
   sauber gemessen wurde. `CL-BOOT-REC-007` stand auf E0 mit c=0.95: die
   Vektortabelle war gemessen, die Zuordnung geraten.
7. **Eine Abloesung wird durchgereicht, nicht nur eingetragen.** Wer
   `Superseded_By` setzt, geht die Zeilen durch, die per `Depends_On` an der
   alten haengen, und haengt sie um. Das Umhaengen ist die Pruefung.
   `check_truth.py` erzwingt, dass keine Zeile an einer abgeloesten haengt.

8. **Eine Zelle ist ein Urteil, kein Laborjournal.** `Statement` sagt, was
   gilt und worauf es steht: Urteil zuerst, dann die tragenden Belege.
   Kandidaten, Fehlversuche und Zwischenstaende gehoeren in die
   Commit-Nachrichten, die die Claim-ID nennen; dort stehen sie ohnehin schon
   (CL-USB-REC-128: 30 Commits). Wieder lesbar mit
   `git log --date=short --format='%ad %h %s' | grep CL-USB-REC-128`.
   Ein Ergebnis, das fuer sich gilt, wird eine eigene Zeile statt eines
   Absatzes. Grenzen fuer Zeilen, die ab dem 2026-10-16 geaendert werden:
   `Statement` 2000 Zeichen, `Next_Test` 1000. Wer eine laengere Altzeile
   anfasst, kuerzt sie auf das Urteil; der Weg bleibt im Git-Log.
   Anlass: im Januar wanderte die Arbeit aus der Matrix zurueck in
   Prosadokumente. Im Oktober wanderte sie in die Zellen -- CL-USB-REC-128
   hatte 28 428 Zeichen, 42 lebende Zeilen lagen ueber 2000.

9. **Geaendert wird nur ueber das Werkzeug** `tools/scripts/truth.py` (oder
   die `truth_*`-Werkzeuge des MCP-Servers). Es prueft jede Aenderung vor dem
   Schreiben gegen `check_truth.py` und schreibt atomar. Anlass: bis
   2026-10-15 schrieb jede Sitzung ihr eigenes Schnipsel, mit denselben Fallen
   jedes Mal; eines davon hat die Datei auf null Bytes gekuerzt.

Der Ablauf dazu steht in `.claude/skills/anspruch-schliessen/SKILL.md`.

## Einstieg in eine neue Session

Ein Befehl, immer derselbe, als erste Handlung:

```bash
python3 tools/scripts/next.py
```

Er prueft die Datei, druckt die Arbeitsfront mit dem jeweils naechsten Test und
die Restmenge nach Prioritaet und Subsystem. Mehr braucht eine neue Sitzung
nicht, um anzufangen. Wenn er einen Verstoss meldet, wird der zuerst behoben --
danach erst inhaltlich gearbeitet.

## Sitzungsende / Uebergabe

1. `python3 tools/scripts/check_truth.py` muss sauber sein.
2. Committen. Nicht committete Arbeit ist die haeufigste Verlustursache in
   diesem Projekt gewesen.
3. Die Front nachfuehren: erledigte `now`-Zeilen auf `Decided=yes` setzen, aus
   `next` nachruecken, damit die naechste Sitzung nicht neu auswaehlen muss.
4. Den Projektstand in der Projekt-Ablage aktualisieren (`claude/stand-*.md`),
   falls sich die Front geaendert hat.

Der naechste Chat braucht dann kein Gedaechtnis, nur das Repository.
