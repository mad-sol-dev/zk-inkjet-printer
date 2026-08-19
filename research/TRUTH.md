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
2. **`system_understanding.md` wird aus TRUTH.csv abgeleitet, nie direkt editiert.**
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

## Einstieg in eine neue Session

```bash
# Was ist offen?
python3 - <<'P'
import csv
for r in csv.DictReader(open('research/TRUTH.csv')):
    if r['Decided']=='no' and not r['Superseded_By']:
        print(f"[{r['Claim_ID']}] {r['Subsystem']:9s} c={r['Confidence']}  {r['Topic']}")
        print(f"    -> {r['Next_Test']}")
P
```
