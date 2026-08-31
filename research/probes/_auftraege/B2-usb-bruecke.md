# Auftrag: Die Brücke vom USB-Kanal in die Dokumentablage

Repo: `$HOME/workspace/zk-inkjet-printer/firmware`
Programm in Ghidra: `ZK-INKJET-NANO-APP.bin.orig`, Basis 0x00200000
(VA = Dateioffset + 0x200000).

Lies zuerst `CLAUDE.md` und `research/TRUTH.md`. Dann die Zeilen
`CL-USB-REC-119`, `CL-USB-REC-120`, `CL-USB-REC-108`, `CL-STORAGE-REC-123`
und `CL-STORAGE-REC-131` in `research/TRUTH.csv`. Sie enthalten den Stand;
ohne sie ist der Auftrag nicht verständlich.

## Vier Regeln, die über allem stehen

**1. Berichte, was du liest — nicht, was es bedeutet.**
„Bei 0x21984C wird `*(*(0x7D8)+0x98)` mit 2 multipliziert" ist ein Befund.
„0x7D8 zeigt auf DISK_DATA_T" ist eine Deutung und braucht den Header, der
das Feldoffset bestätigt.

**2. Jede genannte Adresse kommt mit dem Werkzeugaufruf, der sie erzeugt hat.**

**3. Ein leeres Werkzeugergebnis ist kein Befund über die Firmware.**
Diese Aufgabe ist genau die, bei der das gefährlich wird. Der gesuchte Wert
65536 = `0x10000` ist auf ARM als Immediate kodierbar (`imm8=1, rot=8`) **und**
kann als Konstantenpool-Wort vorliegen **und** kann zur Laufzeit berechnet
werden, etwa aus einer Sektoranzahl der SD-Karte. Wer einen Modus laufen lässt
und nichts findet, hat nichts gemessen. Laufen zu lassen sind mindestens:
`search_scalars` auf 65536 und auf 0x10000, eine Bytesuche über die Datei nach
dem Little-Endian-Wort `00 00 01 00`, und eine Suche nach Schreibzugriffen auf
Offset `+0x98` (`str r*,[r*,#0x98]`) unabhängig vom Wert. Das `method_note`
jeder leeren Antwort gehört in den Bericht.

**4. Bekannte Blindstelle.** VA 0x280AE8–0x280B7B ist nicht disassembliert
(`CL-TOOL-REC-117`). Fällt eine Xref-Kette dort hinein, sag es.

### Das Gegenbeispiel, das diese Regeln erzwingt

`CONTRADICTION-USB-001` galt sieben Monate als projektblockierend: eine
Scalar-Suche fand 0 Referenzen auf `0xB1008000`, und niemand prüfte, dass
Ghidras Scalar-Suche Konstantenpool-Worte grundsätzlich nicht sieht. Die
Adresse stand die ganze Zeit im Pool bei 0x002AFB4C. Nicht das Wissen fehlte,
sondern die Prüfung der Methode.

## Aufgabe 1 — wer füllt `*(*(0x000007D8) + 0x98)` mit 65536?

`msc_lun_set_capacity_21984c` (0x0021984C, 52 Bytes) rechnet
`blocks = *(*(0x000007D8) + 0x98) * 2` und legt das Ergebnis nach
`state(0x000082EC)+0x3C`. Gemessen am Host: 131072 Blöcke à 512 Byte, also
steht in dem Feld 65536. Offen ist, wer es dort hinschreibt.

Die Antwort entscheidet einen Acht-Byte-Patch (`CL-USB-REC-119`): ist der Wert
eine feste Einstellung, dürfen die beiden Fensterliterale allein wandern; wird
er aus dem MBR am aktuellen Fensterrand geparst, braucht der Patch eine zweite
Änderung.

**Erster Ansatz, billig und mit eingebauter Kontrolle:** `CL-USB-REC-120`
vermutet die Nuvoton-Struktur `DISK_DATA_T` mit `diskSize` in KiB. Das ist
prüfbar:
`grep -rn "DISK_DATA_T" vendor/N32901-3_NonOS_BSP/` und das Feld-Layout aus dem
Header ausrechnen. Liegt `diskSize` bei Offset 0x98, ist die Struktur
identifiziert und die Frage verschiebt sich auf „wer ruft die
SD-Initialisierung auf, die `DISK_DATA_T` füllt" — im BSP typischerweise
`fmiSD_Initial`/`SDCARD_Open`-artige Routinen, deren Namen im Header stehen.
Passt das Offset **nicht**, ist die Vermutung widerlegt, und das ist ein
ebenso gültiges Ergebnis, das berichtet wird.

**Zweiter Ansatz, unabhängig davon:** Wer schreibt überhaupt auf `0x7D8`?
`search_xrefs_to(0x7d8)`, plus eine Bytesuche nach dem Wort `d8 07 00 00` über
die Datei, weil ein Poolwort in der Xref-Liste fehlen kann. Von dort aus die
Funktion suchen, die den Zeiger setzt, und deren Aufrufer.

Zu berichten: die Schreibstelle mit Adresse, die Herkunft des Wertes (Literal,
Immediate, Rechnung, geparst) und — falls Rechnung — die Eingangsgröße. Wenn
sich der Wert nicht bis zu seiner Quelle verfolgen lässt, ist das kein
Misserfolg, sondern das Ergebnis; dann gehört in den Bericht, an welcher Stelle
die Kette abreißt und woran.

## Aufgabe 2 — wer liest die Dokumentablage?

Die Ablage liegt bei 0x28800000, Schrittweite 0x4D000, Magic `0x2022` im
Kopfsektor. `CL-STORAGE-REC-123` hat den Schreiber eines einzelnen Slots
(`FUN_0028A1D0`) und die Adressbildung (`mov r7,#0x4D000`, `mov r8,#0x28800000`
bei 0x265FE0/0x265FE4, `mla r0,index,stride,base`). Der **Leser** fehlt.

Einstiegspunkte: die Konstantenpool-Treffer des Magic `0x2022` bei
VA 0x265D4C, 0x28A3D8, 0x28A538. Prüf die Liste selbst nach, verlass dich nicht
auf diese Zeile — und beachte, dass Base und Stride als MOV-Immediates
vorliegen, also von einer Literalsuche nicht gefunden werden, während das Magic
im Pool steht und von der Scalar-Suche nicht gefunden wird. Beide Modi.

Für jede Fundstelle: welche Funktion, was tut sie mit dem Magic (Vergleich?
Schreiben?), wer ruft sie auf, und **woher kommt die Quelladresse, aus der
gelesen wird** — eine berechnete Rohadresse auf der Karte, oder ein Dateihandle
auf `3:/`?

**Die Rangfolge, die den Auftrag lohnend macht:** Ein Leser, der nur nach
Menü-Navigation feuert, nützt für die Fernsteuerung wenig. Gesucht ist einer,
der **von selbst** läuft — beim Boot oder zyklisch. Kandidaten aus den Strings:
der Font-Ladepfad `3:/obds/fonts/%s`, die Ressourcendatei
`3:/obds/res/ZK-INKJET-RES-HW.zkml`, der Lesezugriff auf
`inkjet-lite-vadj-sample.csv`. Für jeden gefundenen Leser also zusätzlich:
läuft er ohne UI-Interaktion?

**Die Zielprobe für jeden Kandidaten:** Bildet er eine physische Kartenadresse,
liegt diese **bei oder oberhalb** der LUN-Basis 0x2A614000 — dem einzigen
Bereich, den ein PC über USB beschreiben kann — und landet der Inhalt
**unterhalb** davon? Nur dann ist es eine patchfreie Brücke vom Host in die
Ablage. Liegt die Leseadresse unterhalb der LUN-Basis, ist es keine Brücke,
sondern nur ein interner Leser; auch das ist zu berichten, dann ist die Frage
für diesen Kandidaten sauber verneint.

## Ausgabe

Ein Bericht nach
`$HOME/workspace/zk-inkjet-printer/firmware/research/probes/B2-usb-bruecke/report.md`.

**Nichts** in `research/TRUTH.csv`, keine weiteren neuen Dateien im Repo.

Gliederung pro Aufgabe: erst die Werkzeugaufrufe mit ihrer Ausgabe, dann „Was
das zeigt", dann „Was das nicht zeigt". Der letzte Absatz ist Pflicht.
Am Schluss eine Liste „Offen geblieben" mit der Stelle, an der du jeweils
stehen geblieben bist.

## Umbenennungen in Ghidra

Nur wenn die Identität aus einem Herstellerheader oder einem String im Binary
folgt — bei dieser Aufgabe also erlaubt, sobald ein BSP-Header ein Feld oder
eine Funktion benennt. Nicht erlaubt für alles, was du aus dem Kontrollfluss
erschließt. Im Zweifel `set_comment` statt `rename_function`, mit dem Zweifel
im Kommentar. `list_mutations` am Ende laufen lassen und die Ausgabe anhängen.

`.re_kb` und `re_kb_archive` sind eingefroren.
