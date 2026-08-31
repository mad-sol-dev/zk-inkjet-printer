# Auftrag: Vom Encoder zur Druckausgabe, und der Block am Drucktasten-Poll

Repo: `$HOME/workspace/zk-inkjet-printer/firmware`
Programm in Ghidra: `ZK-INKJET-NANO-APP.bin.orig`, Basis 0x00200000
(VA = Dateioffset + 0x200000).

Lies zuerst `CLAUDE.md` und `research/TRUTH.md`. Die Zeilen
`CL-FIRMWARE-REC-103`, `CL-HARDWARE-REC-109`, `CL-HARDWARE-REC-112` und
`CL-TOOL-REC-117` in `research/TRUTH.csv` enthalten den Stand; lies sie, bevor
du anfängst.

## Vier Regeln, die über allem stehen

**1. Berichte, was du liest — nicht, was es bedeutet.**
„FUN_002BAD40 schreibt Bytes in einen mit malloc geholten Puffer" ist ein
Befund. „FUN_002BAD40 ist der Rasterizer" ist eine Deutung und gehört nicht in
den Bericht, solange sie nicht aus einem String, einem Herstellerdokument oder
dem Zint-Quelltext folgt.

**2. Jede genannte Adresse kommt mit dem Werkzeugaufruf, der sie erzeugt hat.**
Keine Adresse aus dem Gedächtnis, keine aus dem Fließtext einer früheren
Sitzung.

**3. Ein leeres Werkzeugergebnis ist kein Befund über die Firmware.**
Es ist ein Befund über die Suche. Wenn `search_xrefs_to` oder `search_scalars`
nichts liefert, berichte das als „Suche X mit Parametern Y lieferte 0 Treffer"
und lauf den zweiten Modus (Scalar *und* Byte). ARM-Immediates sind in der
Bytesuche unsichtbar, Konstantenpool-Worte in der Scalar-Suche. Das `method_note`
der Werkzeugantwort gehört in den Bericht. Eine Aussage der Form „die Firmware
tut X nicht" ist ohne belegte Tauglichkeit der Methode unzulässig.

**4. Bekannte Blindstelle.** VA 0x280AE8–0x280B7B ist in Ghidra nicht
disassembliert (`CL-TOOL-REC-117`). Fällt eine Xref-Kette in diesen Bereich,
sag es, statt die Lücke als Abwesenheit zu lesen.

### Das Gegenbeispiel, das Regel 1 erzwingt

Am 2025-12-20 fand ein Agent korrekt, dass eine Routine `0xA5EB1357` nach
`[0xB8003000]` schreibt. Die zusammenfassende Sitzung machte daraus einen
„dedizierten Encoder-Capture-Block", verified, Konfidenz 1.0. Tatsächlich ist
`RTC_BA = 0xB8003000` und die Konstante die RTC-Freischaltsequenz aus dem Design
Guide. Die Messung war richtig, die Zuschreibung von Bedeutung falsch — und sie
hat acht Monate lang drei abhängige Zeilen vergiftet.

## Aufgabe 1 — die drei unanalysierten Callees von FUN_002302EC

`FUN_002302EC` (0x2302EC–0x230A5F) ist nach Form und Umfang das Zint-Äquivalent
zu `ZBarcode_Encode_Segs`. Von seinen 23 Callees sind drei nie angesehen worden:
**0x2A10C8, 0x2BAD40, 0x2BAD5C**.

Für jeden der drei:

- `analyze_function_complete`. Umfang, Signaturform, Aufrufer.
- Welche Puffer werden angefasst? Kommt der Zielzeiger als Argument herein, aus
  einer Allokation, oder ist es eine feste Adresse?
- Werden MMIO-Register berührt? Wenn ja: Basis über
  `grep -rhiE 'define.*_BA' vendor/N32901-3_NonOS_BSP/` auflösen, bevor du sie
  benennst. Nicht raten.
- Gibt es Strings in der Funktion oder in ihren Callees, die aus dem
  Zint-Katalog stammen (Fehlermeldungen mit Nummernpräfix wie „566: …")? Wenn
  ja, ist die Funktion Zint-intern und **nicht** Druckausgabe.

Die Leitfrage: folgt hinter dem Encode direkt Rasterung und Ausgabe, oder endet
die Kette mit einem gefüllten Bitmuster im RAM, das ein anderer Pfad abholt?
Beide Antworten sind gültige Ergebnisse. Wenn die drei Funktionen sämtlich
Zint-intern sind, ist das der Befund — dann lautet die Anschlussfrage, wer den
Ausgabepuffer von `FUN_002302EC` liest, und die gehört in den Bericht, nicht in
eine Behauptung.

## Aufgabe 2 — der Block VA 0x25B0C0–0x25B250

Dieser Block ruft `FUN_0026FBF8` (gpio_read auf GPE[9], Deadline tick+0xBB8)
zweimal auf, bei 0x25B120 und 0x25B1CC, und lädt dazwischen per `adr` den String
„Please release the print key!" bei 0x25B25C. Er ruft außerdem 0x262778
(`settings_load_validate_save`) und 0x26A7F8 (Menü-Dispatcher).

- `disassemble_at` über den vollständigen Bereich 0x25B0C0–0x25B250. Berichte
  das Listing, nicht eine Zusammenfassung davon.
- Zu welcher Funktion gehört der Bereich? Wo liegen ihr Anfang und ihr Ende, und
  wer ruft sie auf (`search_xrefs_to`, zwei Ebenen)?
- Was passiert **zwischen** den beiden `FUN_0026FBF8`-Aufrufen? Konkret: welche
  Aufrufe, welche Speicherzugriffe, welche Verzweigungsbedingungen.
- Wird ein Rückgabewert von `FUN_0026FBF8` ausgewertet, und wenn ja, wohin führt
  jeder der Zweige?
- Gibt es in dem Block eine Stelle, an der ein Zustand *gesetzt* wird — ein Flag,
  eine Variable, ein Funktionszeiger —, statt nur gelesen? Solche Stellen sind
  die Kandidaten für „Druck von außen auslösen" und sind einzeln zu berichten,
  mit Adresse und Ziel.

## Aufgabe 3 — die Nachbarschaft prüfen

`FUN_0025B338` ist laut `CL-FIRMWARE-REC-103` das zweite Glied einer der beiden
Ketten von `ui_main_loop` zum Zint-Encoder:
`ui_main_loop(0x26B86C) -> FUN_0025B338 -> FUN_002C3554 -> FUN_002302EC`.

Sie liegt 0xE8 Bytes hinter dem Ende des Blocks aus Aufgabe 2. Das ist zunächst
nur räumliche Nähe und beweist nichts.

- Wo genau beginnt und endet `FUN_0025B338`, und wo endet die Funktion, die den
  Block aus Aufgabe 2 enthält? Grenzen die beiden aneinander, überlappen sie,
  oder liegt etwas dazwischen?
- Teilen sie sich Aufrufer, globale Variablen oder Konstantenpool-Einträge?
  (`find_in_function`, `search_xrefs_to` auf die gemeinsamen Ziele.)
- Falls ein gemeinsamer Aufrufer existiert: welcher, und in welcher Reihenfolge
  ruft er die beiden?

Wenn sich kein Zusammenhang zeigt, ist das ein vollwertiges Ergebnis. Schreib es
hin, statt einen zu konstruieren.

## Ausgabe

Ein Bericht nach
`$HOME/workspace/zk-inkjet-printer/firmware/research/probes/B1-druckpfad/report.md`.

**Nichts** in `research/TRUTH.csv` — das Eintragen ist ein getrennter Schritt und
wird nicht von dieser Sitzung gemacht. Keine weiteren neuen Dateien im Repo.

Gliederung pro Aufgabe: erst die Werkzeugaufrufe mit ihrer Ausgabe, dann ein
Absatz „Was das zeigt", dann ein Absatz „Was das nicht zeigt". Der letzte ist
Pflicht und darf nicht leer sein.

Am Schluss eine Liste „Offen geblieben" mit den Fragen, die du angefangen und
nicht zu Ende gebracht hast — samt der Stelle, an der du stehen geblieben bist.
Eine abgebrochene Untersuchung, die als solche gemeldet wird, ist brauchbar; eine
abgebrochene Untersuchung, die als Ergebnis auftritt, ist Schaden.

## Umbenennungen in Ghidra

Erlaubt nur, wenn die Identität aus einem Herstellerheader, einem String im
Binary oder dem Zint-Quelltext folgt. Nicht erlaubt für alles, was du aus dem
Kontrollfluss erschließt. Im Zweifel `set_comment` statt `rename_function`, und
den Zweifel in den Kommentar schreiben. `list_mutations` am Ende der Sitzung
laufen lassen und die Ausgabe an den Bericht anhängen.

`.re_kb` und `re_kb_archive` sind eingefroren und dürfen nicht geschrieben
werden.
