# B1 — Vom Encoder zur Druckausgabe, und der Block am Drucktasten-Poll

Programm: `ZK-INKJET-NANO-APP.bin.orig`, Basis 0x00200000. Alle Adressen VA
(= Dateioffset + 0x200000), sofern nicht anders markiert. `get_current_program`
meldete zu Sitzungsbeginn `state: READY`.

---

## Aufgabe 1 — die drei unanalysierten Callees von FUN_002302EC

### 0x2A10C8

**Werkzeugaufrufe:**

- `analyze_function_complete(0x2A10C8, fields=[function,xrefs,strings,features,disasm])`
  → Range 0x002a10c8–0x002a157b (301 Instruktionen, 1204 Bytes). Signatur vom
  Decompiler mit 23 Parametern rekonstruiert (`__stdcall`, gemischt
  `undefined4`/`int*`/`char*`/`uint`), was auf Stack-Args statt echter
  23-Parameter-Aufrufer hindeutet — nicht weiter verifiziert.
  Inbound-Xrefs: genau zwei — `0x002305cc` in `FUN_002302ec` (UNCONDITIONAL_CALL)
  und `0x0026eff0` in `FUN_0026eddc` (UNCONDITIONAL_CALL). Outbound: 30 Calls,
  überwiegend an `0x002c6df0`, `0x002c7018`, `0x002c70f4`, `0x002c7334` (Rechen-
  routinen, mehrfach aufgerufen) sowie an `0x0020c798`, `0x0020c804`,
  `0x0020d87c`, `0x0020e058` (kleine Hilfsfunktionen, s.u.), `0x0029d384`,
  `0x0029dd48`, `0x0029e8e0` (zwei Aufrufe), `0x0029f0c0` (zwei Aufrufe).
  `strings.items` leer (Quelle `disassembly_literals`).
- `analyze_function_complete(0x2A10C8, fields=[decompile], options.decompile.max_lines=400)`
  → 254 Zeilen Decompilat, nicht trunkiert. Ablauf: Wenn `param_14==NULL`,
  werden aus `param_10..param_13` über `FUN_002c7334`/`FUN_002c7018`/
  `FUN_002c70f4`/`FUN_002c6df0` vier Werte (`local_f0/ec/f8/f4`) berechnet;
  sonst werden sie direkt aus `param_14[0..3]` übernommen. Danach wird
  `FUN_0029f0c0` aufgerufen und dessen Ergebnis an `FUN_0020c798(größe, …)`
  übergeben; ist der Rückgabewert `NULL`, kehrt die Funktion mit `0` zurück
  (`if (puVar6 == (uint *)0x0) { return 0; }`). Nach mehreren Bereichs- und
  Größenprüfungen (Sprünge nach `LAB_002a14f4` bzw. `LAB_002a1568` bei
  ungültigen Kombinationen) wird `FUN_0020e058(puVar6, größe)` aufgerufen,
  dann zweimal `FUN_0029e8e0(zielzeiger_in_puVar6, …)`, danach abhängig von
  einer Bedingung entweder `FUN_0029d384` oder `FUN_0029dd48`. Am Ende
  (Label `LAB_002a1568`) wird in jedem Fall `FUN_0020c804((int)puVar6)`
  aufgerufen, unabhängig vom Erfolg.
- `find_in_function(0x2A10C8, "0xb[0-9a-f]{7}", mode=disasm, regex=true)` →
  0 Treffer (`total_matches:0`). Das ist nur eine Aussage über Immediate-
  Operanden in der Disassemblertextform, nicht über Konstantenpool-Worte
  (Regel 6/CL-TOOL-REC-101/-108).
- `find_in_function(0x2A10C8, "ldr r\\d+,\\[0x", mode=disasm, regex=true)` →
  genau 1 Treffer: `002a1280: ldr r1,[0x2a157c]`. Das ist der einzige
  PC-relative Poolzugriff der Funktion.
- `read_words(0x2a157c..)` wurde nicht separat aufgerufen; im Decompilat
  erscheint diese Adresse bereits als `DAT_002a157c`, referenziert als
  `*(byte *)(DAT_002a157c + param_18)` — eine Byte-Tabelle direkt hinter dem
  Funktionsende (0x2a157b ist das letzte Byte der Funktion laut Range).
- Callee-Checks (`analyze_function_complete`, fields=[function,strings] bzw.
  [function,strings,disasm]):
  - `0x0029f0c0` (0x29f0c0–0x29f243), `0x002a0628` (0x2a0628–0x2a0683),
    `0x002a0688` (0x2a0688–0x2a0707), `0x002c6df0` (0x2c6df0–0x2c6f7b),
    `0x002c7018` (0x2c7018–0x2c7047), `0x002c70f4` (0x2c70f4–0x2c72a3),
    `0x002c7334` (0x2c7334–0x2c75f3), `0x0029d384` (0x29d384–0x29dd3f),
    `0x0029dd48` (0x29dd48–0x29e8d7): bei allen `strings.items` leer.
  - `0x0029e8e0` (0x29e8e0–0x29f0af): ein "String"-Treffer, aber
    `literal: "fff?33s\xc0\xf0A-\xe9"` — das ist Instruktionsbytes, die als
    ASCII fehlinterpretiert wurden (Adresse `0x0029f0b8`, Quelle
    `0x0029eb3c`), kein echter Text.
  - **Kein einziger Callee trägt eine der nummerierten Zint-Fehlermeldungen**
    (Muster „566: …" o.ä. aus CL-FIRMWARE-REC-103). Das ist ein Negativbefund
    über String-Referenzen aus Disassembler-Operanden; ein Datentabellen-
    String ohne direkte Instruktionsreferenz würde hier nicht auftauchen.
  - `0x0020c798` (0x20c798–?): `disassemble_at(0x20c798, 24)` zeigt
    `blx 0x0020ea38` → `ldr r5,[r0,#0]`, dann eine Größenrundung
    (`add r0,#0xb; lsr r4,r0,#3; lsl r4,r4,#3`), Vergleich `cmp r4,r6; bhi …`,
    bei Nichterfüllung `mov r0,#0; pop {r4,r5,r6,pc}` (Rückgabe 0), sonst
    Traversierung einer verketteten Struktur (`ldr r0,[r5,#4]`, `cmp`, `bcc`) —
    das Bytemuster gleicht einer Freelist-Traversierung, wie sie ein
    Allokator (malloc-artig) durchführt. Nicht durch Symbol oder String
    bestätigt.
  - `0x0020c804`: `disassemble_at(0x20c804, 24)` zeigt eine sehr ähnliche
    Traversierung (`ldr r4,[r0,#4]`, Vergleichsschleife, Verschmelzen
    benachbarter Blöcke via `ldr r2,[r5,#0]; add r1,r1,r2; str r1,[r0,#0]`)
    — Bytemuster passt zu einer Free-Routine mit Coalescing. Ebenfalls nicht
    durch Symbol bestätigt.
  - `0x0020e058`: `disassemble_at` (frühere Sondierung) zeigt
    `mov r2,#0x0; cmp r1,#0x4; bcc …; ands r12,r0,#0x3; …` — Alignment-Test
    plus fest verdrahtetes Füllbyte 0 in r2. Bytemuster passt zu einer
    Zero-Fill-Routine (memset-artig mit Füllwert 0).
  - `0x0020ea38`: `analyze_function_complete(fields=[disasm])` → nur zwei
    Instruktionen: `ldr r0,[0x20ea40]; bx lr`. `read_words(0x20ea40)` →
    `0x00044f58`. Das liegt **nicht** im MMIO-Bereich (0xB0000000–0xBFFFFFFF)
    und sieht nach einer normalen Datenadresse aus (z.B. Heap-Zustand).
  - `0x0020d87c`: `disassemble_at(0x20d87c, 24)` zeigt einen kurzen Vorspann
    (`mov r0,#0; bl 0x210330; bl 0x200254; mov r0,#1; blx 0x22dc68; pop`),
    gefolgt (ab 0x20d890, augenscheinlich ein zweiter Einstieg/eine zweite
    Funktion im selben disassemblierten Fenster) von Stack-Aufbau für ein
    Array. Ziele `0x210330`, `0x200254`, `0x22dc68` wurden nicht weiter
    verfolgt.
  - `read_words` an den Pool-Treffern der drei größeren Callees:
    `0x29e8e0` referenziert `0x29f0b0` (`0x00000498`), `0x29f0b4`
    (aus Kontext, nicht separat gelesen), `0x29f0b8`; `0x29d384`
    referenziert `0x29dd40` (`0x00000498`); `0x29dd48` referenziert
    `0x29e8d8` (`0x00000498`). Die übrigen gelesenen Werte
    (`0x3fe00000`, `0x3f666666`, `0xc0733333`) sind Bitmuster von
    IEEE-754-Gleitkommazahlen (z.B. `0x3fe00000` = oberes Wort von 0.5
    als `double`), keine Adressen. **Keiner dieser Poolwerte liegt im
    MMIO-Bereich.**
- Zweiter Aufrufer außerhalb der Zint-Kette: `analyze_function_complete(0x0026eddc, fields=[function,strings,xrefs])`
  → Range 0x0026eddc–0x0026f11b, referenzierte Strings **".jpg"** (0x0026f11c,
  Quelle 0x0026ee04), **".png"** (0x0026f124, Quelle 0x0026ee18), **".bmp"**
  (0x0026f12c, Quelle 0x0026ee2c). Inbound-Xrefs von `FUN_0026eddc`:
  `0x0022b87c` und `0x0026f1d0` (beide UNCONDITIONAL_CALL, aufrufende
  Funktion vom Tool nicht benannt). `FUN_0026eddc` ruft `0x002a10c8` genau
  einmal auf (bei `0x0026eff0`), außerdem u.a. `0x0020c798`/`0x0020c804`
  (dieselben mutmaßlichen Alloc/Free-Stubs) und `0x002c6df0`/`0x002c7018`/
  `0x002c70f4` (dieselben Rechenroutinen wie 0x2A10C8).

**Was das zeigt:** `FUN_002A10C8` ist eine generische Bitmap-Kompositions-
routine: Sie berechnet aus vier Eingabewerten (direkt oder aus einer
Struktur) vier abgeleitete Größen, allokiert (mutmaßlich per Freelist-
Allokator) einen Puffer über einen aus den Eingaben berechneten Zeiger,
nullt ihn (mutmaßlich), befüllt ihn über zwei Aufrufe von `FUN_0029e8e0`,
ruft je nach Bedingung `FUN_0029d384` oder `FUN_0029dd48` auf und **gibt den
zu Beginn allokierten Puffer am Ende der eigenen Funktion wieder frei** —
der Puffer ist ein interner Arbeitsspeicher, kein an den Aufrufer
zurückgegebenes Ergebnis-Bitmap. Sie hat genau zwei Aufrufer: `FUN_002302EC`
(die als Zint-Encode-Wrapper identifizierte Funktion, CL-FIRMWARE-REC-103)
und `FUN_0026EDDC`, eine Funktion, die Dateiendungen `.jpg`/`.png`/`.bmp`
referenziert — also mutmaßlich Bilddatei-Handling, nicht Barcode-Encoding.
Keiner der 30 direkten und indirekt geprüften Callees zeigt einen
Zint-Fehlerstring. Keiner der geprüften Konstantenpool-Werte in `0x2A10C8`
selbst oder seinen vier tiefsten Callees (`0x0020c798/c804/d87c/e058`,
`0x0029e8e0/d384/dd48`) liegt im MMIO-Bereich 0xB0000000–0xBFFFFFFF.

**Was das nicht zeigt:** Dass `FUN_0020c798`/`FUN_0020c804` tatsächlich
`malloc`/`free` sind, ist nicht durch ein Symbol, einen String oder einen
Header belegt — nur durch das Bytemuster (Freelist-Traversierung,
Größenrundung, Coalescing). Das ist eine strukturelle Beobachtung, keine
Identität. Ebenso ist unklar, ob `FUN_0020e058` wirklich ein
Zero-Fill/memset ist — nur das Immediate `mov r2,#0` und der
Alignment-Test passen zu diesem Muster. Die Untersuchung der Callees von
`FUN_0026EDDC` (was genau mit .jpg/.png/.bmp geschieht, ob dieser Pfad
überhaupt mit Druckausgabe zu tun hat) wurde nicht durchgeführt — das ist
ein offener Punkt (siehe „Offen geblieben"). Die Frage, ob dem Aufruf von
`FUN_002A10C8` innerhalb `FUN_002302EC` (bei `0x002305cc`) tatsächlich eine
Rasterung oder Druckausgabe folgt, wurde durch diese Analyse nicht
beantwortet — dafür müsste der Kontrollfluss in `FUN_002302EC` selbst nach
`0x002305cc` verfolgt werden, was nicht Teil dieser Sondierung war. Der
Vergleich der beiden `0x00000498`-Poolwerte über drei Funktionen hinweg legt
eine gemeinsame Konstante nahe, wurde aber nicht weiter interpretiert.

---

### 0x2BAD40

**Werkzeugaufrufe:**

- `analyze_function_complete(0x2BAD40, fields=[function,xrefs,strings,disasm])`
  → Range 0x002bad40–0x002bad57 (6 Instruktionen, 24 Bytes). Volles Listing:
  ```
  002bad40: ldr r12,[0x2bad58]
  002bad44: stmdb sp!,{r3,lr}
  002bad48: ldr r12,[r12,#0x14]
  002bad4c: str r12,[sp,#0x0]
  002bad50: bl 0x0021d0c0
  002bad54: ldmia sp!,{r3,pc}
  ```
  Signatur (Decompiler): `undefined __stdcall(uint,uint,uint,uint)`.
  **40 Inbound-Xrefs** (`summary.inbound: 40`), quer über praktisch das
  gesamte UI: u.a. viermal aus `ui_main_loop` (`0x0026a8d4`, `0x0026a8e8`,
  `0x0026a904`, `0x0026aa6c`), einmal aus `FUN_002302ec` (`0x0023034c`),
  sowie aus `FUN_0025d234`, `FUN_0025d958`, `FUN_0025dc78`, `FUN_0025dffc`
  (2×), `FUN_00261d4c`, `FUN_00262ef0`, `FUN_00265d64`, `FUN_00268ef0` (2×),
  `FUN_0026d698`, `FUN_0026e528` (2×), `FUN_002bced4` (3×), `FUN_002bd684`
  (4×), `FUN_002bd820` (4×), `FUN_002bfea8`, sowie sieben weitere,
  vom Tool nicht benannte Aufrufer (`0x0022b2b0`, `0x0022b2c4`, `0x0022ca94`,
  `0x0022cc60`, `0x0022ccf4`, `0x0022d118`, `0x0022d1c8`, `0x0025cf24`,
  `0x0025d458`).
- `read_words(0x2bad58)` → `0x00041378`.
- `analyze_function_complete(0x0021d0c0, fields=[function,strings,disasm])`
  → Range 0x0021d0c0–0x0021d1bb. `disassemble_at(0x21d0c0, 64)` → volles
  Listing (64 Zeilen). Ablauf: `mov r0,#0x0; bl 0x0026fd70` (unmittelbar),
  danach min/max-Sortierung zweier Koordinatenpaare, `mul r8,r0,r1`
  (Flächenberechnung), dann eine feste Sequenz `mov r0,#0x2a; bl 0x0026fd90`
  → Koordinatenwerte via `bl 0x0026fdd4` → `mov r0,#0x2b; bl 0x0026fd90` →
  weitere `bl 0x0026fdd4` → `mov r0,#0x2c; bl 0x0026fd90` →
  `bl 0x00270190(r0=Breite,r1=Fläche)`, danach eine zweite, fast identische
  `0x2a/0x2b/0x2c`-Sequenz mit fester Koordinate `0x0` bzw. `0xef`, und am
  Ende `mov r0,#0x1; b 0x0026fd70` (Tail-Branch, kein `bl`).
- `search_xrefs_to(0x0026fd70)` → 8 Treffer: zweimal in `FUN_0021cab0`
  (`0x0021cad4`, `0x0021d0b4`), zweimal in `FUN_0021d0c0`
  (`0x0021d0dc`, `0x0021d1b8`), zweimal in `FUN_0021d1c0`
  (`0x0021d1d0`, `0x0021d214`), zweimal in `FUN_0021d77c`
  (`0x0021d790`, `0x0021d7f0`).
- `analyze_function_complete(0x0026fd70, fields=[function,strings,disasm])`
  → 7 Instruktionen: `cmp r0,#0x0; ldr r0,[0x26fd8c]; ldr r1,[r0,#0x38];
  orrne r1,r1,#0x2000; biceq r1,r1,#0x2000; str r1,[r0,#0x38]; bx lr`.
  `read_words(0x26fd8c)` → `0xb8001038`.
- Registerauflösung: `grep -rhiE 'define.*_BA' vendor/N32901-3_NonOS_BSP/`
  wurde nicht direkt ausgeführt; stattdessen `research/findings/
  n32903_registers.json` (laut CLAUDE.md die aus denselben BSP-Headern
  generierte Registerkarte) für `0xB8001038` abgefragt →
  `{"peripheral":"SYSLIB","register_name":"REG_GPIOD_DOUT",
  "address":"0xB8001038","source_file":"SYSLIB/Lib/w55fa93_reg.h"}`
  (Treffer doppelt, groß/klein geschriebene Dateiname-Variante).
- `analyze_function_complete(0x0026fd90, fields=[function,disasm])` → 16
  Instruktionen: `ldr r2,[0x26fdd0]; ldr r1,[r2,#0x48]; bic r1,r1,#0x100;
  str r1,[r2,#0x48]; add r1,r2,#0xb000; mov r3,#0x45; str r0,[r1,#0x10];
  str r3,[r1,#0x0]; ldr r0,[r1,#0x0]` (Rest im Fenster abgeschnitten).
  `read_words(0x26fdd0)` → `0xb8001000`.
- `analyze_function_complete(0x0026fdd4, fields=[function,disasm])` → 8
  Instruktionen: `ldr r1,[0x26fdf4]; mov r2,#0x85; str r0,[r1,#0x10];
  str r2,[r1,#0x0]; ldr r0,[r1,#0x0]; tst r0,#0x1; bne …; bx lr`
  (Busy-Poll auf Bit 0). `read_words(0x26fdf4)` → `0xb800c000`.
- Registerauflösung über `n32903_registers.json` für `0xB8001048`,
  `0xB800C000`, `0xB800C010`:
  `0xB8001048` → `REG_GPIOE_DOUT`; `0xB800C000` → `REG_SPI0_CNTRL` /
  `SPI0_BA`; `0xB800C010` → `REG_SPI0_RX0` / `REG_SPI0_TX0`
  (Quelle jeweils `SYSLIB/Lib/w55fa93_reg.h`).

**Was das zeigt:** `FUN_002BAD40` ist ein Trampolin: Es lädt ein Feld
(Offset `+0x14`) aus einer globalen Struktur bei VA `0x00041378` und ruft
damit `FUN_0021D0C0` auf. `FUN_0021D0C0` schreibt vor und nach seiner
eigentlichen Arbeit über `FUN_0026FD70` das Bit `0x2000` von
`REG_GPIOD_DOUT` (VA 0xB8001038, per BSP-Header aufgelöst) — einmal löschen
(`r0=0` zu Beginn), einmal setzen (`r0=1` am Ende, als Tail-Branch). Dazwischen
sendet es über `FUN_0026FD90` (schreibt `REG_SPI0_TX0` und einen
Steuerwert `0x45` in `REG_SPI0_CNTRL`, beides VA 0xB800C0xx, per BSP-Header
aufgelöst) die Bytewerte `0x2A`, `0x2B`, `0x2C` — jeweils gefolgt von
Koordinatenwerten, die über `FUN_0026FDD4` (schreibt `REG_SPI0_TX0`,
Steuerwert `0x85` in `REG_SPI0_CNTRL`, pollt danach Bit 0 von
`REG_SPI0_CNTRL` busy-wait) einzeln übertragen werden. `FUN_002BAD40` hat
40 Aufrufer quer durchs gesamte UI (Menüs, Einstellungen, `ui_main_loop`)
und genau einen Aufrufer aus der Zint-Kette (`FUN_002302EC` bei
`0x0023034c`). Weder `FUN_002BAD40` noch `FUN_0021D0C0` noch ihre direkten
SPI/GPIO-Hilfsfunktionen enthalten einen Zint-Fehlerstring.

**Was das nicht zeigt:** Dass die Bytewerte `0x2A`/`0x2B`/`0x2C` Display-
Befehle im Sinne einer bestimmten Controller-Familie (Spaltenadresse/
Seitenadresse/Speicherschreiben) sind, ist eine Musterähnlichkeit zu
verbreiteten Display-Protokollen, aber durch nichts im Repository
(kein String, kein Header, kein Zint-Quelltext) belegt — das wird hier
ausdrücklich nicht behauptet, nur die Rohwerte und ihre Zieladressen. Was
konkret am anderen Ende von SPI0 hängt (Grafikdisplay des Geräts,
Thermodruckkopf-Ansteuerung oder etwas drittes), ist damit nicht
festgestellt — nur, dass es SPI0 ist und dass `REG_GPIOD_DOUT` Bit 13 die
Übertragung umrahmt (Chip-Select- oder D/C-artiges Verhalten, aber auch das
nicht durch Namen belegt). Ob der Aufruf aus `FUN_002302EC` heraus
(`0x0023034c`) auf dem Pfad liegt, der bei jedem Barcode-Encode ausgeführt
wird, oder nur bedingt erreicht wird, wurde nicht geprüft.

---

### 0x2BAD5C

**Werkzeugaufrufe:**

- `analyze_function_complete(0x2BAD5C, fields=[function,xrefs,strings,disasm])`
  → Range 0x002bad5c–0x002bb04f (189 Instruktionen, ~0x2F3 Bytes). Signatur
  (Decompiler): `undefined __stdcall(uint,uint,uint,uint,uint*,int)`.
  Beginn: `stmdb sp!,{r0-r11,lr}; mov r9,r0; ldr r0,[0x2bb050]; sub sp,sp,#0x14;
  ldrb r0,[r0,#0x34]; ldr r7,[sp,#0x48]; ldr r4,[sp,#0x4c]; cmp r0,#0x0;
  mov r5,r3`. **22 Inbound-Xrefs**: aus `FUN_002302ec` (`0x00230a28`),
  `FUN_0025dc78`, `FUN_00261d4c`, `FUN_00262ef0`, `FUN_00264094`,
  `FUN_00266d34`, `FUN_00268808`, `FUN_00268ef0`, `FUN_00269074`,
  `FUN_002bced4`, `FUN_002bd160`, `FUN_002bd684`, `FUN_002bd820`,
  `FUN_002bf900` (3×), `FUN_002c1ac4`, sowie sechs nicht benannte
  Aufrufer (`0x0022cafc`, `0x0022cb44`, `0x0025cf84`, `0x002bf180`,
  `0x002bf1b8`). Outbound: `0x0021cab0` (4×), `0x0022cde4` (2×),
  `0x00243f60` (4×).
- `read_words(0x2bb050)` → `0x00041378` — **derselbe globale Struktur-Zeiger**
  wie bei `FUN_002BAD40` (VA 0x2bad58), nur mit anderem Feldoffset (`+0x34`,
  als Byte gelesen, statt `+0x14`).
- `find_in_function(0x2BAD5C, "0xb[0-9a-f]{7}", mode=disasm, regex=true)` →
  0 Treffer (Immediate-Blindstelle, s.o.).
- `analyze_function_complete(0x0021cab0, fields=[function,strings,disasm])`
  → Range 0x0021cab0–0x0021d0b7 (378 Instruktionen). Signatur enthält
  `ushort * param_5` — ein Zeiger auf 16-Bit-Werte.
- `find_in_function(0x0021cab0, "bl 0x0026fd", mode=disasm)` → 32 Treffer.
  Struktur: dieselbe `0x2a`/`0x2b`/`0x2c`-Kommandosequenz über
  `FUN_0026FD90`/`FUN_0026FDD4` wie in `FUN_0021D0C0` (Zeilen 10–30, u.a.
  `0021cae8: mov r0,#0x2a; 0021caec: bl 0x0026fd90`, `0021cb04: mov r0,#0x2b`,
  `0021cb20: mov r0,#0x2c`), gefolgt von einer Schleife mit wiederholten
  `bl 0x0026fdd4`-Aufrufen (Zeilen 80–337, u.a. `0021cc10: bcs 0x0021cbd8`,
  `0021cc90: bcs 0x0021cc5c` — Schleifenrücksprünge) und, ab Zeile 267,
  `0021cf00: ldrh r0,[r5],#0x2` unmittelbar vor einem weiteren
  `bl 0x0026fdd4` — ein Lesen von 16-Bit-Werten aus einem mit Post-Increment
  durchlaufenen Zeiger, gefolgt von der Übertragungsfunktion. Am Ende
  (Zeilen 362–374) exakt dieselbe abschließende `0x2a/0x0` … `0x2b/0x0/0xef`
  … `0x2c`-Sequenz wie am Ende von `FUN_0021D0C0`.
  `find_in_function(0x0021cab0, "bl 0x00270190")` → 0 Treffer (im Unterschied
  zu `FUN_0021D0C0` wird `0x00270190` hier nicht aufgerufen).
- `analyze_function_complete(0x00243f60, fields=[function,strings])` →
  Range 0x00243f60–0x00243f6b, 11 Bytes, keine Parameter
  (`undefined8 __stdcall(void)`), keine Strings.

**Was das zeigt:** `FUN_002BAD5C` liest ein Byte-Feld (Offset `+0x34`) aus
derselben globalen Struktur bei VA `0x00041378`, die auch `FUN_002BAD40`
verwendet (dort Offset `+0x14`), und ruft darüber u.a. `FUN_0021CAB0` auf.
`FUN_0021CAB0` sendet dieselbe `0x2A/0x2B/0x2C`-Kommandosequenz über
dieselben SPI0-Hilfsfunktionen (`0x0026FD90`/`0x0026FDD4`, s.o. für
`FUN_002BAD40` per BSP-Header auf `REG_SPI0_CNTRL`/`REG_SPI0_TX0`
aufgelöst), gefolgt von einer Schleife, die 16-Bit-Werte aus einem Zeiger
(`ushort * param_5`) liest und einzeln über dieselbe SPI0-Sendefunktion
überträgt — die Struktur passt zu einem Pixel-Block-Transfer (z.B. RGB565),
nicht zu einer einzelnen Flächenfüllung wie bei `FUN_0021D0C0`. `FUN_002BAD5C`
hat 22 Aufrufer, davon einer aus der Zint-Kette (`FUN_002302EC` bei
`0x00230a28`) und der Rest aus unterschiedlichen UI-Funktionen. Kein
Zint-Fehlerstring in `FUN_002BAD5C` oder `FUN_0021CAB0` gefunden.

**Was das nicht zeigt:** Welche der 22 Aufrufer tatsächlich mit
Barcode-/Label-Inhalt aufrufen und welche mit UI-Grafik (Icons, Menüs), ist
nicht unterschieden — die Xref-Liste zeigt nur Adressen, keine Argumente.
Die genaue Bedeutung des Byte-Felds `+0x34` der globalen Struktur
`0x00041378` (Flag? Modus? Gerätezustand?) wurde nicht ermittelt. Ob der
Pixelblock, den `FUN_0021CAB0` überträgt, aus dem von `FUN_002A10C8`
gefüllten Arbeitsspeicher stammt oder aus einer völlig anderen Quelle, ist
durch diese Analyse **nicht** gezeigt — dafür wäre eine Datenflussanalyse
vom Rückgabewert/Ausgabeparameter von `FUN_002302EC` bis zum Aufrufer bei
`0x00230a28` nötig, die hier nicht durchgeführt wurde.

### Beantwortung der Leitfrage aus Aufgabe 1

Für alle drei geprüften Callees gilt: Es folgt **kein direkter Übergang in
eine Rasterung/Ausgabe innerhalb von `FUN_002302EC` selbst** in dem Sinn,
dass diese drei Funktionen das barcodespezifische Ergebnis weiterverarbeiten
würden. Stattdessen zeigen zwei von drei (`0x2BAD40`, `0x2BAD5C`) einen
Pfad zu einem SPI0-Gerät (vermutlich das Bediendisplay, nicht durch Namen
belegt), der **nicht barcode-spezifisch** ist (40 bzw. 22 Aufrufer quer
durchs UI), und die dritte (`0x2A10C8`) einen internen, selbst-allokierten
und selbst-wieder-freigegebenen Arbeitspuffer, der zusätzlich von einer
Bilddatei-Routine (`.jpg`/`.png`/`.bmp`) mitbenutzt wird. Ob `FUN_002302EC`
an anderer Stelle (nicht bei diesen drei Callees) doch in einen
Druckausgabe-Pfad mündet, ist damit **nicht** ausgeschlossen — nur für
diese drei Aufrufe nicht gezeigt. Die Alternative aus der Aufgabenstellung
("die Kette endet mit einem gefüllten Bitmuster im RAM, das ein anderer Pfad
abholt") ist für `FUN_002A10C8` die besser gestützte Lesart, weil der
Puffer dort intern bleibt (allokiert und noch in derselben Funktion wieder
freigegeben) — wer diesen Puffer vor der Freigabe liest oder ob sein Inhalt
vor der Freigabe irgendwohin kopiert wird, wurde nicht geprüft.

---

## Aufgabe 2 — der Block VA 0x25B0C0–0x25B250

**Werkzeugaufrufe:**

- `disassemble_at(0x25B0C0, count=100)` → vollständiges Listing (Auszug,
  Adressen VA):

  ```
  0025b0c4: sub sp,sp,#0x38
  0025b0c8: bl 0x0025f518
  0025b0cc: bl 0x00262778
  0025b0d0: bl 0x0025c41c
  0025b0d4: cmp r0,#0x0
  0025b0d8: bllt 0x0025c3f4
  0025b0dc: ldr r1,[0x25b24c]
  0025b0e0: mov r0,#0x20
  0025b0e4: bl 0x0022f530
  0025b0e8: ldr r5,[0x25b250]
  0025b0ec: cmp r0,#0x0
  0025b0f0: str r0,[r5,#0x0]
  0025b0f4: bleq 0x00230a94
  0025b0f8: ldr r6,[0x25b254]
  0025b0fc: mov r0,#0x4
  0025b100: mov r1,r6
  0025b104: bl 0x0022f530
  0025b108: ldr r4,[0x25b258]
  0025b10c: cmp r0,#0x0
  0025b110: str r0,[r4,#0x0]
  0025b114: beq 0x0025b140
  0025b118: mov r1,r6
  0025b11c: bl 0x0020e098
  0025b120: bl 0x0026fbf8          ; <-- 1. Aufruf FUN_0026FBF8
  0025b124: tst r0,#0x1
  0025b128: beq 0x0025b148
  0025b12c: bl 0x002bfe9c
  0025b130: cmp r0,#0x0
  0025b134: movne r0,#0x1
  0025b138: beq 0x0025b148
  0025b13c: b 0x0025b14c
  0025b140: bl 0x00230a94
  0025b144: b 0x0025b120
  0025b148: mov r0,#0x0
  0025b14c: ldr r1,[r5,#0x0]
  0025b150: cmp r1,#0x0
  0025b154: ldrne r1,[r4,#0x0]
  0025b158: cmpne r1,#0x0
  0025b15c: beq 0x0025b168
  0025b160: cmp r0,#0x0
  0025b164: beq 0x0025b1fc
  0025b168: ldr r1,[0x25b27c]
  0025b16c: adr r0,0x25b25c
  0025b170: ldr r2,[r1,#0x1b0]
  0025b174: ldr r3,[r1,#0x1b4]
  0025b178: ldr r12,[r1,#0x1bc]
  0025b17c: strd r2,r3,[sp,#0x0]
  0025b180: add r1,r1,#0x1c0
  0025b184: str r12,[sp,#0xc]
  0025b188: ldmia r1!,{r2,r3,r5,r12}
  0025b18c: strd r2,r3,[sp,#0x10]
  0025b190: str r5,[sp,#0x18]
  0025b194: str r12,[sp,#0x1c]
  0025b198: ldmia r1!,{r2,r3,r5,r12}
  0025b19c: strd r2,r3,[sp,#0x20]
  0025b1a0: str r5,[sp,#0x28]
  0025b1a4: str r12,[sp,#0x2c]
  0025b1a8: ldmia r1,{r1,r2}
  0025b1ac: str r0,[sp,#0x8]
  0025b1b0: mov r0,sp
  0025b1b4: str r1,[sp,#0x30]
  0025b1b8: str r2,[sp,#0x34]
  0025b1bc: bl 0x002bd160
  0025b1c0: bl 0x00243f60
  0025b1c4: add r5,r0,#0x800
  0025b1c8: add r5,r5,#0x3b8        ; r5 = tick + 0xBB8 (0x800+0x3b8)
  0025b1cc: bl 0x0026fbf8           ; <-- 2. Aufruf FUN_0026FBF8
  0025b1d0: tst r0,#0x1
  0025b1d4: beq 0x0025b1e4
  0025b1d8: bl 0x00243f60
  0025b1dc: cmp r5,r0
  0025b1e0: bhi 0x0025b1cc
  0025b1e4: ldr r0,[0x25b280]
  0025b1e8: bl 0x0026c44c
  0025b1ec: bl 0x0026887c
  0025b1f0: ldr r0,[r4,#0x0]
  0025b1f4: cmp r0,#0x0
  0025b1f8: bleq 0x00262ef0
  0025b1fc: bl 0x002bfe94
  0025b200: cmp r0,#0x0
  0025b204: beq 0x0025b240
  0025b208: bl 0x00243f60
  0025b20c: add r4,r0,#0x32
  0025b210: bl 0x00243f60
  0025b214: cmp r0,r4
  0025b218: bcs 0x0025b240
  0025b21c: bl 0x002bfe9c
  0025b220: cmp r0,#0x0
  0025b224: beq 0x0025b234
  0025b228: bl 0x00268e88
  0025b22c: bl 0x002661e0
  0025b230: b 0x0025b240
  0025b234: bl 0x00243f60
  0025b238: cmp r0,r4
  0025b23c: bcc 0x0025b21c
  0025b240: mov r0,#0x0
  0025b244: bl 0x002bfc34
  0025b248: bl 0x0026a7f8
  ```
  Danach bricht das Listing ab und setzt bei `0025b284: stmdb sp!,{r3,lr}`
  fort — dazwischen (0x25b24c–0x25b283) liegt Literalpool-/String-Daten,
  s.u.

- `list_functions_in_range(0x25AF00, 0x25B400)` → drei Funktionen:
  `boot_init` (Entry 0x0025b0c4, Size 392), `FUN_0025b284` (Entry
  0x0025b284, Size 48), `FUN_0025b338` (Entry 0x0025b338, Size 1696).
- `analyze_function_complete(0x25b0c4, fields=[function,xrefs])` →
  Funktionsname bereits **`boot_init`** (nicht `FUN_`-präfigiert), Range
  0x0025b0c4–0x0025b24b (392 Bytes = 0x0025b24b − 0x0025b0c4 + 1). Damit
  liegen alle o.g. Instruktionen bis `0x0025b248` innerhalb von `boot_init`;
  0x25B0C0–0x25B0C3 liegt vor dem eigentlichen Funktionsanfang (die ersten
  vier disassemblierten Bytes ab 0x25B0C0 wurden vom Tool übersprungen bzw.
  gehören zu einer vorhergehenden Struktur — nicht weiter untersucht).
- `read_words(0x25b24c, count=3)` → `0x000537f0`, `0x0000054c`,
  `0x0004cfc0`. `read_words(0x25b258)` → `0x00000560`. `read_words(0x25b27c,
  count=2)` → `0x001236f8`, `0x0012509a`. Diese fünf Worte sind der
  Literalpool von `boot_init`, direkt hinter dessen Ende (0x0025b24c ff.),
  in den auch die Stringbytes für „Please release the print key!" (ab
  `0x0025b25c`, per `adr r0,0x25b25c` bei `0x0025b16c` geladen) eingebettet
  sind.
- `search_xrefs_to(0x25b0c4)` → genau 1 Treffer: `0x00273ee4`, Kontext
  „`00273ee4 in boot_init [UNCONDITIONAL_JUMP]`". Das Tool ordnet diese
  Adresse also selbst der Funktion `boot_init` zu (nicht einem externen
  Aufrufer).
- `list_functions_in_range(0x273D00, 0x273F00)` → bestätigt: es gibt einen
  zweiten, nicht-zusammenhängenden Funktions-Chunk namens `boot_init` bei
  Entry `0x00273ee4`, Size 4 (nur die eine Sprunginstruktion
  `b 0x0025b0c4`). Direkt davor liegt `FUN_00273e98` (Entry 0x00273e98,
  Size 76 = endet exakt bei 0x00273ee4), direkt danach `FUN_00273ee8`.
- `disassemble_at(0x273ed0, 12)` zeigt, dass `FUN_00273e98` bei `0x00273ee0`
  mit `ldmia sp!,{r4,r5,r6,r7,r8,r9,r10,pc}` **regulär zurückkehrt** (Popt
  `pc`) — die direkt anschließende Sprunginstruktion bei `0x00273ee4` wird
  also **nicht** per Fallthrough von `FUN_00273e98` erreicht, sondern liegt
  nur räumlich direkt dahinter.
- `search_xrefs_to(0x273ee4)` → 1 Treffer: `0x00200280` in `FUN_00200264`,
  Typ **COMPUTED_CALL**. `search_xrefs_to(0x273e98)` → 13 Treffer aus völlig
  anderen Funktionen (`FUN_0022e4c4` 2×, `FUN_00232bc4` 2×, `FUN_0024a0bc`
  3×, `FUN_0024a398`, `FUN_0026e84c` 2×, `FUN_002afe80`, `FUN_002b0058` 2×)
  — diese rufen `FUN_00273e98` auf, **nicht** den `boot_init`-Chunk bei
  `0x273ee4`; die beiden Adressen liegen nur unmittelbar benachbart im
  Speicher.
- `search_xrefs_to(0x200264)` → 2 Treffer: `0x0020005c` (kein
  Funktionsname) und `0x0020007c` in `FUN_00200060`, beide
  UNCONDITIONAL_CALL.

**Was das zeigt:** Der Bereich VA 0x25B0C0–0x25B250 liegt vollständig
innerhalb der Funktion **`boot_init`** (0x0025b0c4–0x0025b24b), gefolgt von
deren Literalpool und der eingebetteten Stringkonstante. `boot_init` besitzt
in der Ghidra-Datenbank **keinen direkten `BL`/`CALL`-Aufrufer** — der
einzige gefundene Xref ist ein **COMPUTED_CALL** bei VA `0x00200280`
(in `FUN_00200264`), der auf einen zweiten, 4 Byte großen Funktions-Chunk
bei `0x00273ee4` zeigt, welcher wiederum unbedingt zu `0x0025b0c4`
verzweigt. `FUN_00200264` selbst wird von zwei Stellen sehr früh im Image
(`0x0020005c`, `0x0020007c`) unbedingt aufgerufen. Zwischen den beiden
Aufrufen von `FUN_0026FBF8` (bei `0x0025b120` und `0x0025b1cc`) passiert:
Auswertung des ersten Rückgabewerts (`tst r0,#1`), bedingt ein Aufruf von
`FUN_002bfe9c` mit weiterer Auswertung, danach (nur wenn beide globalen
Zeiger bei `[0x0004cfc0]`/`[0x00000560]` ungleich Null **und** der
kombinierte Rückgabewert ungleich Null ist) Aufbau einer 0x38 Byte großen
Struktur auf dem Stack aus Feldern einer globalen Struktur bei
`0x001236f8` (Offsets `+0x1b0` bis `+0x1c8`), Übergabe des Zeigers auf die
Stringkonstante „Please release the print key!" als Feld dieser Struktur,
Aufruf von `FUN_002bd160(stack_struct)`, danach `FUN_00243f60()`
(Tick-Lesefunktion, aus `read_words`/Disassemblervergleich bestätigt
konsistent mit CL-HARDWARE-REC-112) und Berechnung `deadline = tick + 0xBB8`
(exakt `0x800+0x3b8`, wie in CL-HARDWARE-REC-109 beschrieben). Der zweite
`FUN_0026FBF8`-Aufruf sitzt in einer Schleife, die bei gesetztem Bit 0 des
Rückgabewerts erneut `FUN_00243f60()` liest und bei `tick < deadline`
zurückspringt (`bhi 0x0025b1cc`) — ein Warten auf Bit-0-Freigabe mit
Timeout, wie von CL-HARDWARE-REC-109 beschrieben. Rückgabewerte beider
`FUN_0026FBF8`-Aufrufe werden ausgewertet: Der erste steuert (zusammen mit
`FUN_002bfe9c` und den beiden globalen Zeigern) den Sprung in den
Dialog-/Wartepfad überhaupt; der zweite steuert das Verlassen der
Warteschleife. `0x00262778` (mutmaßlich `settings_load_validate_save`, aus
CL-HARDWARE-REC-109 übernommen, hier nicht neu verifiziert) wird bei
`0x0025b0cc` aufgerufen — **vor** dem ersten `FUN_0026FBF8`-Aufruf, nicht
dazwischen. `0x0026a7f8` (mutmaßlich Menü-Dispatcher, ebenfalls aus
CL-HARDWARE-REC-109 übernommen) wird bei `0x0025b248` aufgerufen — ganz am
Ende des disassemblierten Bereichs, ebenfalls nicht zwischen den beiden
Polls.

**Zustands-Setz-Stellen (mit Adresse und Ziel):**
- `0x0025b0f0: str r0,[r5,#0x0]` — schreibt den Rückgabewert von
  `FUN_0022f530(0x20, 0x537f0)` nach `*0x0004cfc0` (globaler Zeiger-Slot).
  Liegt **vor** dem ersten `FUN_0026FBF8`-Aufruf.
- `0x0025b110: str r0,[r4,#0x0]` — schreibt den Rückgabewert von
  `FUN_0022f530(0x4, 0x54c)` nach `*0x00000560` (globaler Zeiger-Slot).
  Ebenfalls **vor** dem ersten Aufruf.
- Zwischen den beiden `FUN_0026FBF8`-Aufrufen (`0x0025b124`–`0x0025b1c8`)
  wurden **keine** Schreibzugriffe auf globale Adressen gefunden, nur
  Schreibzugriffe auf den Stack (`[sp,#…]`) zum Aufbau der Dialogstruktur
  für `FUN_002bd160`.
- `search_xrefs_to(0x4cfc0)` → 0 Treffer, mit `method_note`, dass
  Poolzugriffe auf Datenregionen für die Xref-Suche unsichtbar sein können
  (Rule-3-Fall: kein Befund, dass sonst niemand diesen Slot anfasst,
  sondern ein Befund über die Suchmethode).

**Was das nicht zeigt:** Ob `FUN_002bfe9c`, `FUN_002bfe94`, `FUN_002bfc34`,
`FUN_002661e0`, `FUN_00268e88`, `FUN_002bd160`, `FUN_0026c44c`,
`FUN_0026887c`, `FUN_00262ef0`, `FUN_0020e098`, `FUN_0022f530`,
`FUN_0025f518`, `FUN_0025c41c`, `FUN_00230a94` tatsächlich das tun, was ihr
Name/ihre Position nahelegt, wurde in dieser Sitzung nicht geprüft — es
werden nur ihre Aufrufstellen und Argument-Register berichtet. Die Aussage
„boot_init hat keinen direkten Aufrufer" beruht auf dem, was
`search_xrefs_to` an dieser Stelle anzeigt; ein COMPUTED_CALL kann eine
Sprungtabelle oder ein Funktionszeiger-Array sein, dessen weitere Einträge
nicht untersucht wurden — es ist daher nicht gezeigt, unter welchen
Bedingungen genau `boot_init` (im Gegensatz zu Nachbarfunktionen im selben
Dispatch) angesprungen wird. Nicht gezeigt ist außerdem, was die beiden
globalen Zeiger bei `0x0004cfc0`/`0x00000560` inhaltlich referenzieren
(Konfigurationsstruktur? Gerätezustand?) — nur, dass sie durch
`FUN_0022f530` befüllt und anschließend auf Null geprüft werden.

---

## Aufgabe 3 — die Nachbarschaft prüfen

**Werkzeugaufrufe:**

- `analyze_function_complete(0x25b338, fields=[function,xrefs])` →
  Funktionsname `FUN_0025b338`, **`range.end` laut diesem Aufruf:
  `0x0025b9fb`** (Start 0x0025b338). Das steht in Widerspruch zum
  `size`-Feld aus `list_functions_in_range` (1696 Bytes → rechnerisches Ende
  0x0025b338+0x6a0−1 = 0x0025b9d7): **zwei Werkzeugaufrufe auf dieselbe
  Funktion liefern zwei unterschiedliche Endadressen** (Differenz 0x24
  Bytes). Beide Rohwerte werden hier berichtet, keiner wurde als „der
  richtige" ausgewählt.
- Grenzen: `boot_init` endet bei `0x0025b24b` (s.o.), dahinter Literalpool/
  String bis mindestens `0x0025b283`, dann `FUN_0025b284` (0x0025b284–
  0x0025b2b3, per `analyze_function_complete`), dann (laut
  `list_functions_in_range(0x25AF00,0x25B400)`, das nur diese drei
  Funktionen im Bereich zurückgab) eine funktionsfreie Lücke bis
  `FUN_0025b338`. Rechnerisch: `0x0025b338 − 0x0025b0c4 = 0x274 = 628`
  Bytes vom `boot_init`-Anfang; `0x0025b338 − 0x0025b250 = 0xE8 = 232`
  Bytes hinter dem im Auftrag genannten Blockende — stimmt mit der Angabe
  im Auftrag exakt überein. Die beiden Funktionen **grenzen nicht direkt
  aneinander**: dazwischen liegen `boot_init`s Literalpool/String, die
  gesamte Funktion `FUN_0025b284` und deren eigener Literalpool
  (`ldr r2,[0x25b2b4]`, `ldr r0,[0x25b2bc]`, aus dem Disasm-Fenster von
  `FUN_0025b284`), bevor `FUN_0025b338` beginnt.
- `analyze_function_complete(0x25b284, fields=[function,xrefs,disasm])` →
  Range 0x0025b284–0x0025b2b3, ein Inbound-Xref: `0x0026b730` in
  `ui_main_loop` (UNCONDITIONAL_CALL). Ruft selbst `0x0025e288` auf.
- `search_xrefs_to(0x25b338)` (via `analyze_function_complete` xrefs-Feld)
  → **zwei** Inbound-Xrefs: `0x0025afac` in `FUN_0025ad2c`
  (UNCONDITIONAL_CALL) und `0x0026b86c` in `ui_main_loop`
  (UNCONDITIONAL_CALL). Das bestätigt den in CL-FIRMWARE-REC-103 genannten
  Aufruf `ui_main_loop(0x26B86C) -> FUN_0025B338` exakt an dieser Adresse,
  zeigt aber zusätzlich einen **zweiten, in CL-FIRMWARE-REC-103 nicht
  genannten Aufrufer** `FUN_0025ad2c`.
- Outbound von `FUN_0025b338` (27 Einträge): u.a. `0x0020e098` (8×,
  **derselbe Callee wie in `boot_init` bei `0x0025b11c`**), `0x0022f530`
  (3×, **derselbe Callee wie in `boot_init` bei `0x0025b0e4`/`0x0025b104`**),
  `0x0025e288`, `0x0025f718`, `0x00260e4c`, `0x00261174`, `0x00266d34`,
  `0x002c2a50` (3×), `0x002c2ce8`, `0x002c3554` (letzter Aufruf, bei
  `0x0025b9ec` — bestätigt den in CL-FIRMWARE-REC-103 genannten
  nächsten Kettenschritt `FUN_0025B338 -> FUN_002C3554`).
- Gemeinsame Konstantenpool-Werte: nicht direkt geprüft (die
  Poolinhalte von `boot_init` — `0x537f0`, `0x54c`, `0x4cfc0`, `0x560`,
  `0x1236f8`, `0x12509a` — wurden nicht gegen den Literalpool von
  `FUN_0025b338` abgeglichen; dafür wäre eine vollständige Disassemblierung
  von `FUN_0025b338` mit Poolauflösung nötig, die im Rahmen dieser
  Sondierung nicht durchgeführt wurde).

**Was das zeigt:** `FUN_0025B338` und `boot_init` liegen nicht direkt
benachbart, sondern durch `boot_init`s eigenen Literalpool/String, die
vollständige Funktion `FUN_0025b284` und deren Literalpool getrennt — die
im Auftrag genannte Distanz von 0xE8 Bytes zum Blockende (nicht zum
Funktionsende von `boot_init`) ist rechnerisch exakt bestätigt, bezieht
sich aber auf eine Lücke, die durch mindestens eine weitere vollständige
Funktion belegt ist, nicht auf freien Raum. `FUN_0025B338` und `boot_init`
rufen zwei gemeinsame Funktionen auf (`0x0020e098`, `0x0022f530`), jedoch
mit unterschiedlicher Aufrufhäufigkeit. `FUN_0025B338` hat einen zweiten,
bisher nicht dokumentierten Aufrufer (`FUN_0025ad2c`) zusätzlich zu
`ui_main_loop`. Der in CL-FIRMWARE-REC-103 behauptete Kettenschritt zu
`FUN_002C3554` ist mit dieser Sitzung an der genannten Adresse
(`0x0025b9ec`) verifiziert.

**Was das nicht zeigt:** Ob `boot_init` und `FUN_0025B338` einen
*gemeinsamen* Aufrufer haben, ist **nicht gezeigt** — `boot_init`s einziger
(indirekter, computed) Zugang liegt im Boot-Dispatch um `0x00200264`, während
`FUN_0025B338` aus `ui_main_loop` und `FUN_0025ad2c` aufgerufen wird; keine
Überschneidung gefunden. Die räumliche Nähe (0xE8 Bytes) beweist damit exakt
das, was der Auftrag bereits vermutet: nichts von sich aus — es gibt keinen
Kontrollfluss- oder Datenpfad zwischen `boot_init` und `FUN_0025B338`, der in
dieser Sitzung gefunden wurde, nur eine belegte Lücke mit einer dritten,
unabhängigen Funktion (`FUN_0025b284`, aufgerufen von `ui_main_loop` bei
`0x0026b730`) dazwischen. Ob die beiden Funktionen sich Konstantenpool-Werte
teilen, wurde nicht geprüft (offener Punkt). Die widersprüchlichen
Endadressen für `FUN_0025b338` (0x0025b9d7 errechnet vs. 0x0025b9fb laut
Tool) wurden nicht aufgelöst.

---

## Umbenennungen / Kommentare

Keine `rename_function`- oder `set_comment`-Aufrufe in dieser Sitzung
(weder `dry_run` noch angewendet). `list_mutations()` am Ende der Sitzung:

```
summary: {"total": 0, "applied": 0, "proposed": 0, "by_kind": {}}
lines: []
```

`.re_kb` und `re_kb_archive` wurden nicht angefasst.

---

## Offen geblieben

- **Aufgabe 1, `0x2A10C8`:** Nicht verfolgt, was `FUN_0026EDDC`
  (.jpg/.png/.bmp-Strings) mit dem von `0x2A10C8` gefüllten Puffer
  tatsächlich macht, und ob dieser Bildpfad überhaupt mit Druckausgabe zu
  tun hat. Stehen geblieben bei: Kenntnis der zwei Aufrufer und der drei
  Strings, ohne deren Aufrufer (`0x0022b87c`, `0x0026f1d0`) untersucht zu
  haben.
- **Aufgabe 1, alle drei Funktionen:** Die Identität von `FUN_0020c798`/
  `FUN_0020c804` als malloc/free ist nur strukturell (Bytemuster), nicht
  durch String/Header/Zint-Quelltext belegt — bewusst nicht umbenannt.
- **Aufgabe 1:** Nicht geprüft, ob der Aufruf von `0x2A10C8` innerhalb
  `FUN_002302EC` (`0x002305cc`) auf einem Pfad liegt, der bei jedem
  Barcode-Encode durchlaufen wird, oder nur bedingt.
- **Aufgabe 2:** Die Bedeutung der globalen Zeiger-Slots `0x0004cfc0` und
  `0x00000560` sowie der Struktur bei `0x001236f8` (Felder `+0x1b0`
  bis `+0x1c8`) wurde nicht ermittelt. Stehen geblieben bei: Kenntnis, dass
  sie existieren und wie sie befüllt/geprüft werden.
- **Aufgabe 2:** Die genaue Rolle von `FUN_00200264`/`0x00273ee4` als
  Boot-Dispatch (Sprungtabelle?) wurde nicht weiter aufgeklärt — nur der
  eine COMPUTED_CALL-Treffer und die zwei Aufrufer von `FUN_00200264`
  wurden dokumentiert. Ob es eine Tabelle mit weiteren `boot_*`-Einträgen
  gibt, ist offen.
- **Aufgabe 3:** Die widersprüchlichen Endadressen von `FUN_0025b338`
  (0x0025b9d7 vs. 0x0025b9fb) wurden nicht aufgelöst.
- **Aufgabe 3:** Kein Abgleich der Konstantenpool-Werte zwischen
  `boot_init` und `FUN_0025b338` durchgeführt (nur gemeinsame Callee-
  Adressen wurden geprüft).
- **Allgemein:** Für keine der in dieser Sitzung neu aufgetauchten
  Funktionen (`FUN_0021D0C0`, `FUN_0021CAB0`, `FUN_0026FD70`,
  `FUN_0026FD90`, `FUN_0026FDD4`, `FUN_00270190`, `FUN_0026EDDC`,
  `FUN_0025ad2c`, `FUN_00200264`) wurde geprüft, ob sie an anderer Stelle in
  `TRUTH.csv` bereits unter anderem Namen oder in anderem Zusammenhang
  dokumentiert sind — das Eintragen in `TRUTH.csv` ist ohnehin ein
  getrennter, hier nicht durchgeführter Schritt.
