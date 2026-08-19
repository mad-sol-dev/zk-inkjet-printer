# Dokumentenablage der Beschriftungen

Stand 2026-08-19, aus Schreibmessungen am Geraet. Autoritativ: `research/TRUTH.csv`
(CL-STORAGE-REC-121 ff.).

## Lage

100 Eintraege fester Groesse im RAW-Bereich der SD-Karte:

```
Eintrag i  =  0x28800000 + i * 0x4D000        i = 0 .. 99
Groesse    =  0x4D000 = 315 392 Bytes = 307,94 KB
```

Die 307,94 KB entsprechen exakt der Groessenangabe, die das Geraet im
Oeffnen-Dialog neben jedem Dokument anzeigt. Die Datensatzgroesse ist fest,
unabhaengig vom Inhalt.

Die Anzahl der belegten Eintraege steht in `settings + 0x180`
(0x28000000 + 0x180). Beobachtet: 1 auf der Originalkarte, 0 nach der
Initialisierung durch das Minimalimage, 2 nach dem Anlegen zweier Dokumente.

## Header-Sektor (die ersten 512 Bytes eines Eintrags)

| Offset | Typ | Bedeutung | Beobachtung |
|---|---|---|---|
| `+0x000` | u32 | Magic / Version | `0x2022` in beiden Dokumenten |
| `+0x004` | u32 | Eintragsindex | 0 bzw. 1 |
| `+0x008` | u32 | Zaehler | 1 bzw. 2 |
| `+0x010` | u32 ×6 | Erstellzeit: Jahr, Monat, Tag, Stunde, Minute, Sekunde | 2005, 8, 30, 21, 1, 42 |
| `+0x028` | u32 ×6 | Aenderungszeit, gleiche Kodierung | 2005, 8, 30, 21, 3, 24 |
| `+0x040` | char[] | **Dokumentname, ASCII, NUL-terminiert** | `Neu-001`, `DC-MINI PRINTER` |
| `+0x144` | u32 | 1 | in beiden gleich |
| `+0x14C` | u32 | Farbe? | `ff ff ff 00` |
| `+0x150` | u32 | 0x195 = 405 | in beiden gleich |
| `+0x158` | u32 | 0x195 = 405 | in beiden gleich |
| `+0x160` | u32 | 1 | |
| `+0x164` | u32 | 0x19 = 25 | Schriftgroesse? |
| `+0x178` | char[] | **Textinhalt, ASCII, NUL-terminiert** | `DCJET` |

Bei Eintrag 0 sind die Felder ab `+0x010` bis `+0x027` null — nur die
Aenderungszeit ist gesetzt. Die Zeitstempel stimmen mit der Anzeige im
Oeffnen-Dialog ueberein (2005-08-30 21:01:32 bzw. 21:03:24); die RTC war
offensichtlich nie gestellt.

## Der Rest des Datensatzes

Beim Speichern werden pro Dokument fuenf Sektoren geschrieben:
`+0x00`, `+0x200`, `+0x600`, `+0x6600`, `+0x4CE00`.

Die letzten vier sind zwischen beiden Dokumenten **byte-identisch** und
enthalten verstreute Werte, darunter bei `+0x4CFC0` die Bytes
`04 10 96 e5 0b 00 a0 e1` — das sind ARM-Befehlsworte (`ldr r1,[r6,#4]`,
`mov r0,r11`). Es handelt sich also um mitgeschriebenen RAM-Restinhalt, nicht
um Dokumentdaten. Dieselben Werte stehen auch im ungenutzten Bereich von
Eintrag 0 der Originalkarte.

**Der gesamte Dokumentinhalt steckt damit im ersten Sektor.**

## Konsequenz

Ein Label programmatisch anzulegen heisst: einen 512-Byte-Sektor an
`0x28800000 + i*0x4D000` schreiben und `settings+0x180` hochzaehlen.
Kein Firmware-Patch, kein USB-CDC, kein Ghidra.

Offen ist, wie sich der Datensatz bei laengeren Texten, mehreren Textobjekten,
Barcodes oder Sonderfeldern veraendert. Der Block `+0x144 .. +0x178` sieht nach
dem Deskriptor genau eines Textobjekts aus (Flag, Farbe, zwei Masse, Typ,
Groesse, dann der String).
