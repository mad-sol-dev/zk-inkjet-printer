# Auftrag: Encoder-Lesepfad über GPE[10] lokalisieren

Repo: `$HOME/workspace/zk-inkjet-printer/firmware`
Programm in Ghidra: `ZK-INKJET-NANO-APP.bin.orig`, Basis 0x00200000
(VA = Dateioffset + 0x200000).

Lies zuerst `CLAUDE.md` und `research/TRUTH.md`. Die Zeilen
`CL-HARDWARE-REC-111`, `CL-HARDWARE-REC-003` und `CL-SOC-REC-021` in
`research/TRUTH.csv` enthalten den Stand; lies sie, bevor du anfängst.

## Drei Regeln, die über allem stehen

**1. Berichte, was du liest — nicht, was es bedeutet.**
„Funktion X schreibt 0xA5EB1357 nach [0xB8003000]" ist ein Befund.
„Funktion X ist der Encoder-Handler" ist eine Deutung und gehört nicht in den
Bericht, solange sie nicht aus einem Herstellerdokument oder einem String folgt.

**2. Jede genannte Adresse kommt mit dem Werkzeugaufruf, der sie erzeugt hat.**
Keine Adresse aus dem Gedächtnis, keine aus dem Fließtext einer früheren Sitzung.

**3. Unbekannte Konstanten erst nachschlagen, dann deuten.**
`grep -rhiE 'define.*_BA' vendor/N32901-3_NonOS_BSP/` löst jede MMIO-Basis in
einer Sekunde auf. Der Design Guide ist `vendor/…/N3290X.PDF`.

### Das Gegenbeispiel, das diese Regeln erzwingt

Am 2025-12-20 fand ein Agent korrekt, dass eine Routine `0xA5EB1357` nach
`[0xB8003000]` und `0xA965` nach `[0xB8003004]` schreibt. Die zusammenfassende
Sitzung machte daraus einen „dedizierten Encoder-Capture-Block" und legte das als
`verified`, Konfidenz 1.0, im RE-KB ab. Tatsächlich ist `RTC_BA = 0xB8003000`,
und beide Konstanten stehen wörtlich im Design Guide als RTC-Freischaltsequenz.
Derselbe Zahlendreher steht ein zweites Mal in `finding-0024/0027`, dort als
„GPIO base 0xb8003000" für den Display-D/C-Toggle. Die Messungen waren jedes Mal
richtig. Falsch war jedes Mal die Zuschreibung von Bedeutung.

## Aufgabe 1 — Aufrufer von VA 0x231F30

`REG_GPIOE_PIN` (0xB800104C) kommt genau einmal als 4-aligned Literal vor,
Dateioffset 0x31F30, VA 0x231F30. Das ist die einzige Stelle, die Port-E-Pins
über eine vollständig gebildete Adresse liest.

- Welche Funktion enthält VA 0x231F30? (`analyze_function_complete`)
- Welche Bitmaske wird auf den gelesenen Wert angewandt? GPE[10] wäre Bit 10,
  Maske 0x400. Berichte die tatsächliche Maske, auch wenn sie eine andere ist.
- Wer ruft diese Funktion auf, zwei Ebenen tief? (`search_xrefs_to`)
- Gibt es in der Kette eine Zeit- oder Zählerkomponente (Timer-Register,
  Schleifenzähler, Systick), die zu einer Software-PWM-Auswertung passen würde?

## Aufgabe 2 — die elf GPIO_BA-Ladestellen

`GPIO_BA` (0xB8001000) kommt elfmal als Literal vor:
0x1D778, 0x2A498, 0x2A4B8, 0x32230, 0x6FD10, 0x6FD8C, 0x6FDD0 und vier weitere —
prüfe die Liste selbst mit einer Bytesuche, verlass dich nicht auf diese Zeile.

Für jede Ladestelle: welche Offsets werden auf dem geladenen Register verwendet?
Gesucht sind Zugriffe auf `+0x40` (GPIOE_OMD), `+0x44` (PUEN), `+0x48` (DOUT),
`+0x4C` (PIN). Damit wird der Vorbehalt aus `CL-HARDWARE-REC-111` entschieden:
ob 0x231F30 wirklich der einzige Port-E-Leser ist oder ob es base+offset-Zugriffe
gibt, die die Literalsuche nicht sieht.

## Aufgabe 3 — MMIO-Basen der Display-Findings nachziehen

`.re_kb` und `re_kb_archive` sind eingefroren und dürfen nicht geschrieben werden.
Lies `finding-0024`, `-0025`, `-0027`, `-0028`, `-0030`, sammle jede darin
genannte MMIO-Basis und prüfe sie gegen die BSP-Header. Berichte eine Tabelle:
Finding, genannte Basis, Basis laut Header, stimmt / stimmt nicht.

Die Funktionsadressen in diesen Findings sind vermutlich richtig — sie kamen
direkt aus Ghidra. Verdächtig sind nur die Basen.

## Ausgabe

Ein Bericht nach `research/probes/A1-encoder-gpio/report.md`.
**Nichts** in `research/TRUTH.csv` — das Eintragen ist ein getrennter Schritt.
Keine neuen Dateien im Repo.

Gliederung: pro Aufgabe erst die Werkzeugaufrufe mit ihrer Ausgabe, dann ein
Absatz „Was das zeigt", dann ein Absatz „Was das nicht zeigt". Der letzte ist
Pflicht und darf nicht leer sein.

## Umbenennungen in Ghidra

Erlaubt nur, wenn die Identität aus einem Herstellerheader oder einem String im
Binary folgt — etwa `rtc_unlock` für die Routine bei 0x28F9A8, weil INIR/AER und
beide Magic-Werte im Design Guide stehen. Nicht erlaubt für alles, was du aus dem
Kontrollfluss erschließt. Im Zweifel: `set_comment` statt `rename_function`, und
den Zweifel in den Kommentar schreiben.
