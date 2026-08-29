# A1 — Encoder-Lesepfad über GPE[10]

Datum: 2026-08-29
Programm: `ZK-INKJET-NANO-APP.bin.orig`, `get_current_program` → `state: READY`,
`domain_file_id 7f011b29394182027168923`.
Basis 0x00200000; VA = Dateioffset + 0x200000.
Rohdatei für die eigenen Suchen: `firmware/bin/ZK-INKJET-NANO-APP.bin`, 2576940 Bytes.

Nichts in `research/TRUTH.csv` geschrieben. Keine neuen Dateien im Repo.
`.re_kb` und `re_kb_archive` nur gelesen.

---

## Aufgabe 1 — Aufrufer von VA 0x231F30

### 1.1 Bytesuche über die Rohdatei (eigener Code, 4-aligned)

```
GPIO_BA        0xb8001000: 11x  0x1D778, 0x2A498, 0x2A4B8, 0x32230, 0x6FD10, 0x6FD8C,
                                0x6FDD0, 0x80884, 0x80AE0, 0x80B40, 0x80B78
REG_GPIOE_PIN  0xb800104c:  1x  0x31F30  (VA 0x231F30)
REG_GPIOE_OMD  0xb8001040:  1x  0x32238  (VA 0x232238)
REG_GPIOE_PUEN 0xb8001044:  0x
REG_GPIOE_DOUT 0xb8001048:  1x  0x322BC  (VA 0x2322BC)
```

Registernamen und Offsets aus `vendor/N32901-3_NonOS_BSP_header.md`
(Zeile 27465 `GPIO_BA 0xB8001000`, Zeilen 29131 ff. `REG_GPIOA_OMD/PUEN/DOUT/PIN`
= GPIO_BA + 0x00/0x04/0x08/0x0C, je Port +0x10).

### 1.2 `search_xrefs_to 0x231F30`

```json
{"total": 1, "items": [{"from_address": "0x00231f00",
 "context": "00231f00 in FUN_00231ec4 [READ]", "target_address": "0x00231f30"}]}
```

### 1.3 `analyze_function_complete 0x00231ec4`

```json
{"function": {"name": "FUN_00231ec4", "entry_point": "0x00231ec4",
  "signature": "uint __stdcall FUN_00231ec4(int param_1, uint param_2)",
  "range": {"start": "0x00231ec4", "end": "0x00231f23"}},
 "features": {"instruction_count": 24, "xrefs_inbound_count": 4,
              "xrefs_outbound_count": 0, "size_bytes": 96},
 "xrefs": {"inbound": [
   {"address": "0x00231e2c", "function": "FUN_00231e0c", "type": "UNCONDITIONAL_CALL"},
   {"address": "0x00231e58", "function": "FUN_00231e0c", "type": "UNCONDITIONAL_CALL"},
   {"address": "0x00231eb0", "function": "FUN_00231e90", "type": "UNCONDITIONAL_CALL"},
   {"address": "0x0026fc08", "function": "FUN_0026fbf8", "type": "UNCONDITIONAL_CALL"}]}}
```

### 1.4 `disassemble_at 0x231ec4 count=24`

```
00231ec4: 58209FE5 ldr r2,[0x231f24]
00231ec8: 040050E3 cmp r0,#0x4
00231ecc: 20208202 addeq r2,r2,#0x20
00231ed0: 0E00000A beq 0x00231f10
00231ed4: 050000CA bgt 0x00231ef0
00231ed8: 010050E3 cmp r0,#0x1
00231edc: 0B00000A beq 0x00231f10
00231ee0: 020050E3 cmp r0,#0x2
00231ee4: 3C209F05 ldreq r2,[0x231f28]
00231ee8: 0800000A beq 0x00231f10
00231eec: 050000EA b 0x00231f08
00231ef0: 080050E3 cmp r0,#0x8
00231ef4: 30209F05 ldreq r2,[0x231f2c]
00231ef8: 0400000A beq 0x00231f10
00231efc: 100050E3 cmp r0,#0x10
00231f00: 28209F05 ldreq r2,[0x231f30]
00231f04: 0100000A beq 0x00231f10
00231f08: 0000A0E3 mov r0,#0x0
00231f0c: 1EFF2FE1 bx lr
00231f10: 002092E5 ldr r2,[r2,#0x0]
00231f14: 0100A0E3 mov r0,#0x1
00231f18: 100112E0 ands r0,r2,r0, lsl r1
00231f1c: 0100A013 movne r0,#0x1
00231f20: 1EFF2FE1 bx lr
```

### 1.5 `read_words 0x231f24 count=4` — der Literalpool der Funktion

```json
{"address": "0x00231f24", "words":
 ["0xb800100c", "0xb800101c", "0xb800103c", "0xb800104c"]}
```

Gegen den BSP-Header: 0xB800100C = REG_GPIOA_PIN, 0xB800101C = REG_GPIOB_PIN,
0xB800103C = REG_GPIOD_PIN, 0xB800104C = REG_GPIOE_PIN. Der Pfad für `r0 == 4`
bildet 0xB800100C + 0x20 = 0xB800102C = REG_GPIOC_PIN.

### 1.6 Die Maske

Die Funktion enthält **keine** feste Bitmaske. Bei 0x231F14/0x231F18 steht

```
mov  r0,#0x1
ands r0,r2,r0, lsl r1
```

Die Maske ist `1 << param_2` und wird vom Aufrufer bestimmt. 0x400 kommt in der
Funktion nicht vor.

### 1.7 Die tatsächlichen Argumente an den vier Aufrufstellen

`disassemble_batch ["0x00231e0c","0x00231e90","0x0026fbf8"] count=36`

```
00231e24: 0410A0E3 mov r1,#0x4
00231e28: 0800A0E3 mov r0,#0x8
00231e2c: 240000EB bl 0x00231ec4        -> Port D (8), Bit 4,  Maske 0x010

00231e50: 0010A0E3 mov r1,#0x0
00231e54: 0200A0E3 mov r0,#0x2
00231e58: 190000EB bl 0x00231ec4        -> Port B (2), Bit 0,  Maske 0x001

00231ea8: 0010A0E3 mov r1,#0x0
00231eac: 0200A0E3 mov r0,#0x2
00231eb0: 030000EB bl 0x00231ec4        -> Port B (2), Bit 0,  Maske 0x001

0026fbfc: 0910A0E3 mov r1,#0x9
0026fc00: 1000A0E3 mov r0,#0x10
0026fc04: 04E02DE5 str lr,[sp,#-0x4]!
0026fc08: AD08FFEB bl 0x00231ec4        -> Port E (0x10), Bit 9, Maske 0x200
0026fc0c: 000050E3 cmp r0,#0x0
0026fc10: 0130A013 movne r3,#0x1
0026fc14: 0300A0E1 mov r0,r3
0026fc18: 04F09DE4 ldr pc,[sp],#0x4
```

Die einzige Stelle, die Port E an diese Funktion übergibt, ist FUN_0026fbf8, und
sie übergibt **Bit 9 (Maske 0x200), nicht Bit 10 (0x400)**.

### 1.8 Zwei Ebenen nach oben

`search_xrefs_to 0x0026fbf8` → total 4:

```
0x0025b120  in boot_init
0x0025b1cc  in boot_init
0x0025c424  in FUN_0025c41c
0x0025c4e8  in FUN_0025c41c
```

`search_xrefs_to 0x0025c41c` → total 1: `0x0025b0d0 in boot_init`.

Damit endet die Kette in einer Ebene: alles läuft über `boot_init`.

### 1.9 Zeit- und Zählerkomponente in der Kette

`disassemble_at 0x0025b1b4 count=24` (Aufrufstelle 0x25b1cc):

```
0025b1c0: 66A3FFEB bl 0x00243f60
0025b1c4: 025B80E2 add r5,r0,#0x800
0025b1c8: EE5F85E2 add r5,r5,#0x3b8      ; r5 = tick + 0xBB8 (3000)
0025b1cc: 895200EB bl 0x0026fbf8         ; GPE[9] lesen
0025b1d0: 010010E3 tst r0,#0x1
0025b1d4: 0200000A beq 0x0025b1e4        ; Pin 0 -> Schleife verlassen
0025b1d8: 60A3FFEB bl 0x00243f60
0025b1dc: 000055E1 cmp r5,r0
0025b1e0: F9FFFF8A bhi 0x0025b1cc        ; sonst weiter bis zur Frist
```

`disassemble_at 0x00243f60 count=16` und `read_words 0x243f6c count=1`:

```
00243f60: 04009FE5 ldr r0,[0x243f6c]
00243f64: D800C0E1 ldrd r0,r1,[r0,#0x8]
00243f68: 1EFF2FE1 bx lr
```
```json
{"address": "0x00243f6c", "words": ["0x00000c10"]}
```

Der Rückgabewert ist also ein 64-Bit-Wert an der absoluten Adresse 0x00000C18.
`search_xrefs_to 0x00243f60` meldet `total: 104`.

Woher der Zähler kommt — Bytesuche über die Rohdatei plus eigener LDR-Literal-Decoder:

```
TMR_BA 0xB8002000: 5x  VA 0x232758, 0x2327D0, 0x2A3B00, 0x2B3748, 0x2B376C
tick   0x00000C18: 1x  VA 0x2A3AA8
  Literal VA 0x2A3AA8 geladen von VA 0x2A3A8C
  Literal VA 0x2A3B00 geladen von VA 0x2A3AAC
```

Der Bereich 0x2A3A88–0x2A3B0B ist in Ghidra nicht disassembliert; mit Capstone
über die Rohdatei:

```
002a3a8c: 14109fe5 ldr   r1, [pc, #0x14]      ; -> 0x2A3AA8 = 0x00000C18
002a3a90: 0120a0e1 mov   r2, r1
002a3a94: d000c1e1 ldrd  r0, r1, [r1]
002a3a98: 010090e2 adds  r0, r0, #1
002a3a9c: 0010a1e2 adc   r1, r1, #0
002a3aa0: f000c2e1 strd  r0, r1, [r2]
002a3aa4: 1eff2fe1 bx    lr

002a3aac: 4c009fe5 ldr   r0, [pc, #0x4c]      ; -> 0x2A3B00 = 0xB8002000 = TMR_BA
002a3ab0: 181090e5 ldr   r1, [r0, #0x18]      ; TMR_BA+0x18 = REG_TISR
002a3ab4: 020011e3 tst   r1, #2
002a3ab8: 1eff2f01 bxeq  lr
002a3abc: 10402de9 push  {r4, lr}
002a3ac0: 0210a0e3 mov   r1, #2
002a3ac4: 181080e5 str   r1, [r0, #0x18]      ; Statusbit 1 zurückschreiben
002a3ac8: efffffeb bl    #0x2a3a8c            ; Zähler +1
```

`REG_TISR = (TMR_BA+0x18)` steht in `vendor/N32901-3_NonOS_BSP_header.md` Zeile 27961,
`TMR_BA 0xB8002000` in Zeile 27466.

### 1.10 Nebenbefund: GPE[10] wird konfiguriert, aber nirgends gelesen

`search_xrefs_to 0x00231f34` (die Konfigurationsroutine neben dem Leser) → total 19.
Eine davon, `disassemble_at 0x25c368 count=16`:

```
0025c368: 0030A0E3 mov r3,#0x0
0025c36c: 0220A0E3 mov r2,#0x2
0025c370: 0910A0E3 mov r1,#0x9
0025c374: 1000A0E3 mov r0,#0x10
0025c378: ED56FFEB bl 0x00231f34      ; Port E, Bit  9, Modus 0x02, Param 0
0025c37c: 64309FE5 ldr r3,[0x25c3e8]
0025c380: 3320A0E3 mov r2,#0x33
0025c384: 0B10A0E3 mov r1,#0xb
0025c388: 1000A0E3 mov r0,#0x10
0025c38c: E856FFEB bl 0x00231f34      ; Port E, Bit 11, Modus 0x33, Param [0x25c3e8]
0025c390: 54309FE5 ldr r3,[0x25c3ec]
0025c394: 2320A0E3 mov r2,#0x23
0025c398: 0A10A0E3 mov r1,#0xa
0025c39c: 1000A0E3 mov r0,#0x10
0025c3a0: E356FFEB bl 0x00231f34      ; Port E, Bit 10, Modus 0x23, Param [0x25c3ec]
```

`read_words 0x25c3e8 count=2` → `["0x0008247c", "0x0008249c"]`.

Wie FUN_00231f34 den Modus auswertet, `disassemble_at 0x00231f8c` / `0x00232058`
/ `0x00232118`:

```
00231f9c: 0B0051E3 cmp r1,#0xb            ; Port E: Bit > 11 -> Rücksprung
00231fa0: 90429FE5 ldr r4,[0x232238]      ; 0xB8001040 = REG_GPIOE_OMD
00231fa4: 04C084E2 add r12,r4,#0x4        ; 0xB8001044 = REG_GPIOE_PUEN
00231fa8: 506084E2 add r6,r4,#0x50        ; 0xB8001090
00231fac: 700084E2 add r0,r4,#0x70        ; 0xB80010B0
...
00231fc8: 0FB009E2 and r11,r9,#0xf        ; unteres Nibble -> OMD/PUEN-Muster
00231fcc: 06005BE3 cmp r11,#0x6
00231fd0: 0BF19F37 ldrcc pc,[pc,r11,lsl #0x2]
...
002320c8: F04009E2 and r4,r9,#0xf0        ; oberes Nibble -> Trigger-Pfad
002320d0: 400054E3 cmp r4,#0x40
...
00232138: F00019E3 tst r9,#0xf0
0023213c: F09FBD08 ldmiaeq sp!,{...,pc}   ; oberes Nibble 0 -> hier ist Schluss
00232140: 000096E5 ldr r0,[r6,#0x0]
00232144: FC409FE5 ldr r4,[0x232248]      ; 0x000007DC
00232148: 0700C0E1 bic r0,r0,r7
0023214c: 2C1094E5 ldr r1,[r4,#0x2c]      ; Belegungsbits für vier IRQ-Plätze
00232150: 010011E3 tst r1,#0x1
...
0023217c: 0510A0E3 mov r1,#0x5
00232180: 0700A0E3 mov r0,#0x7
00232184: 3FBF01EB bl 0x002a1e88          ; (Prio, IRQ, Param_4)
00232188: 0500A0E3 mov r0,#0x5
0023218c: 0FBE01EB bl 0x002a19d0
002321f4: 700088E5 str r0,[r8,#0x70]      ; r8 = GPIO_BA, also 0xB8001070
```

`disassemble_at 0x002a19d0`:

```
002a19e0: 0110A0E3 mov r1,#0x1
002a19e4: 1100A0E1 mov r0,r1, lsl r0
002a19e8: 2E23A0E3 mov r2,#0xb8000000     ; AIC_BA (BSP Zeile 27464)
002a19ec: 200182E5 str r0,[r2,#0x120]     ; AIC_BA+0x120
```

Modus 0x02 und 0x05 haben oberes Nibble 0 und nehmen den Trigger-Pfad nicht.
Modus 0x23 und 0x33 haben oberes Nibble 2 bzw. 3 und nehmen ihn.

### Was das zeigt

VA 0x231F30 ist der Literalpool-Eintrag `REG_GPIOE_PIN` der Funktion
FUN_00231ec4 (0x231EC4–0x231F23, 24 Instruktionen). Die Funktion ist
portgeneriert: `param_1` wählt über 1/2/4/8/0x10 eines der fünf PIN-Register,
`param_2` ist die Bitnummer, die Maske ist `1 << param_2`, der Rückgabewert 0
oder 1. Ein Portselektor außerhalb {1,2,4,8,0x10} liefert 0.

Die Funktion hat vier Aufrufer. Drei lesen Port D Bit 4 bzw. Port B Bit 0. Der
vierte, FUN_0026fbf8, ist der einzige mit Port E — und er liest **Bit 9, Maske
0x200**. In der gesamten Kette kommt Maske 0x400 an dieser Funktion nicht vor.

Über FUN_0026fbf8 führen vier Aufrufstellen nach oben, alle in `boot_init`
(zwei direkt, zwei über FUN_0025c41c, das selbst nur von `boot_init` aufgerufen
wird).

Eine Zeitkomponente ist da, aber sie hat die Form einer Frist, nicht die einer
Messung: an beiden Poll-Stellen wird vorher ein Zählerstand geholt, um 0xBB8
(3000) erhöht und als Abbruchgrenze der Warteschleife benutzt. Der Zähler ist
ein 64-Bit-Wert an absolut 0x00000C18, den eine Routine bei VA 0x2A3A8C um 1
erhöht; ihr einziger sichtbarer Aufrufer bei VA 0x2A3AAC liest TMR_BA+0x18
(REG_TISR laut BSP), prüft Bit 1 und schreibt es zurück. Es gibt kein
Capture-Register, keine Flankenzeitstempel, keine Pulsbreitenrechnung in der
Kette.

GPE[10] und GPE[11] werden bei VA 0x25C3A0 bzw. 0x25C38C mit den Modusbytes 0x23
und 0x33 konfiguriert. Diese Modusbytes haben ein von null verschiedenes oberes
Nibble und nehmen damit in FUN_00231f34 den Zweig, der einen von vier
Interruptplätzen belegt, FUN_002a1e88 mit dem vierten Parameter aufruft und über
FUN_002a19d0 `1 << IRQ` nach AIC_BA+0x120 schreibt. GPE[9] — der einzige
gepollte Port-E-Pin — wird mit Modus 0x02 konfiguriert und nimmt diesen Zweig
nicht.

### Was das nicht zeigt

- **Nicht, dass irgendetwas hier der Encoder ist.** Kein String und kein
  Herstellerdokument verbindet FUN_00231ec4, FUN_0026fbf8, GPE[9] oder GPE[10]
  mit dem MT6701. `CL-HARDWARE-REC-003` steht auf einer Durchgangsmessung an der
  Platine, nicht auf dem Binary; dieser Bericht berührt diese Messung nicht.
- **Nicht, dass GPE[10] ungelesen bleibt.** Er wird nicht *über diese Funktion*
  gelesen. Ein Interrupt-Handler liest den Pin typischerweise gar nicht.
  Welcher Code beim GPE[10]-Interrupt läuft, ist hier nicht ermittelt.
- **Nicht, was 0x0008249C ist.** Der Wert liegt unterhalb der Ladebasis
  0x200000. Die naheliegende Lesart „Dateioffset, also VA 0x28249C" trägt nicht:
  `read_words 0x0028247c` liefert `0xe041a00a, 0xe15a0000, …`, also
  Funktionsmitte, keinen Prolog. Ob die beiden Werte Handler-Adressen,
  Tabellenindizes oder etwas Drittes sind, ist offen. Die dritte
  Parameterposition von FUN_002a1e88 habe ich nicht bis zu ihrer Verwendung
  verfolgt.
- **Nicht, dass die Modusbytes das bedeuten, was ich schreibe.** „Oberes Nibble
  ungleich null nimmt den Zweig ab 0x232140" ist aus `tst r9,#0xf0` /
  `ldmiaeq …,pc` abgelesen. Dass dieser Zweig eine *Interrupt*-Konfiguration ist,
  stützt sich auf AIC_BA aus dem BSP-Header und auf den Schreibzugriff nach
  AIC_BA+0x120 — nicht auf ein Registerdatenblatt für 0xB8001090 / 0xB80010B0,
  das ich nicht nachgeschlagen habe.
- **Nicht, dass 0x00000C18 eine Millisekunde zählt.** Die Frist 0xBB8 = 3000
  legt Millisekunden nahe; die Timer-Periode habe ich nicht gemessen. Bei
  VA 0x2A3B0C wird der Wert zusammen mit dem Nachbarwert bei 0x00000C10 addiert
  und durch 0x3E8 = 1000 geteilt, was zu Millisekunden passt, sie aber nicht
  belegt.
- **Nicht, dass 0x2A3AAC ein Interrupt-Handler ist.** Dass er als solcher
  installiert wird, habe ich nicht verfolgt.
- **Nicht, dass `boot_init` das Ende der Kette ist.** Wer `boot_init` aufruft,
  ist nicht geprüft.

---

## Aufgabe 2 — die elf GPIO_BA-Ladestellen

### 2.1 Die Liste, selbst geprüft

Bytesuche über die Rohdatei (siehe 1.1) bestätigt genau elf 4-alignte Vorkommen
von 0xB8001000. Die sieben in der Auftragszeile genannten stimmen; die vier
weiteren sind **0x80884, 0x80AE0, 0x80B40, 0x80B78** (VA 0x280884, 0x280AE0,
0x280B40, 0x280B78).

### 2.2 Wer lädt sie — eigener LDR-Literal-Decoder über die ganze Datei

```
Literal VA 0x21D778: Lader 0x21D244
Literal VA 0x22A498: Lader 0x22A47C
Literal VA 0x22A4B8: Lader 0x22A49C
Literal VA 0x232230: Lader 0x231F48
Literal VA 0x26FD10: Lader 0x26FC9C
Literal VA 0x26FD8C: Lader 0x26FD74
Literal VA 0x26FDD0: Lader 0x26FD90
Literal VA 0x280884: Lader 0x28083C
Literal VA 0x280AE0: Lader 0x280890
Literal VA 0x280B40: Lader 0x280AE8
Literal VA 0x280B78: Lader 0x280B50
```

Jede Ladestelle hat genau einen Lader. `search_xrefs_to` findet neun davon; für
0x280B40 und 0x280B78 meldet es `total: 0` mit dem `method_note`-Hinweis. Grund:
Ghidra hat 0x280AE8–0x280B7B nicht disassembliert. `read_words 0x00280ae0`
zeigt, dass dort Code steht (`0xe59f1050`, `0xe1a02800`, …), und Capstone
bestätigt es:

```
00280ae8: 50109fe5 ldr r1, [pc, #0x50]     ; -> 0x280B40
00280aec: 0028a0e1 lsl r2, r0, #0x10
00280af0: 2228a0e1 lsr r2, r2, #0x10
00280af4: 282081e5 str r2, [r1, #0x28]
00280af8: 483091e5 ldr r3, [r1, #0x48]
...
00280b50: 20109fe5 ldr r1, [pc, #0x20]     ; -> 0x280B78
00280b5c: 083081e5 str r3, [r1, #8]
00280b60: 383091e5 ldr r3, [r1, #0x38]
00280b70: 380081e5 str r0, [r1, #0x38]
00280b74: 1eff2fe1 bx lr
```

### 2.3 Welche Offsets auf dem geladenen Register benutzt werden

Ermittelt mit einem Capstone-Vorwärtslauf ab jedem Lader, der das Zielregister
verfolgt, `add`/`sub`/`mov`-Ableitungen mitrechnet und die Verfolgung abbricht,
sobald das Register überschrieben wird.

| Ladestelle | Lader | benutzte Offsets |
|---|---|---|
| 0x21D778 | 0x21D244 | **+0x38** GPIOD_DOUT (4x); +0xB000 / +0xB010 (je 84x) = SPI0_BA+0x00 / +0x10 |
| 0x22A498 | 0x22A47C | +0xF8 (ldr 0x22A484, str 0x22A48C) |
| 0x22A4B8 | 0x22A49C | +0xF8 (ldr 0x22A4A4, str 0x22A4AC) |
| 0x232230 | 0x231F48 | **+0x70** (str 0x2321F4) — siehe 2.4 |
| 0x26FD10 | 0x26FC9C | **+0x48** GPIOE_DOUT (0x26FCA0 ldr, 0x26FCA8 str); +0x38 GPIOD_DOUT; +0x04 GPIOA_PUEN; +0x00 GPIOA_OMD; +0x08 GPIOA_DOUT |
| 0x26FD8C | 0x26FD74 | +0x38 GPIOD_DOUT (ldr 0x26FD78, str 0x26FD84) |
| 0x26FDD0 | 0x26FD90 | **+0x48** GPIOE_DOUT (0x26FD94, 0x26FD9C, 0x26FDC0, 0x26FDC8); +0xB000 / +0xB010 = SPI0_BA |
| 0x280884 | 0x28083C | +0x08 GPIOA_DOUT; +0x38 GPIOD_DOUT; +0x28 GPIOC_DOUT; **+0x48** GPIOE_DOUT (0x28085C, 0x280864); +0x18 GPIOB_DOUT |
| 0x280AE0 | 0x280890 | +0x18, +0x38, **+0x48** (0x2808A4, 0x280918, 0x280A30), +0x28, +0x08 |
| 0x280B40 | 0x280AE8 | +0x28, **+0x48** (0x280AF8, 0x280B0C), +0x18, +0x38 |
| 0x280B78 | 0x280B50 | +0x08 GPIOA_DOUT; +0x38 GPIOD_DOUT |

### 2.4 Die Ladestelle 0x232230 im Einzelnen

Der Vorwärtslauf endet hier an der Sprungtabelle bei 0x231FD0
(`ldrcc pc,[pc,r11,lsl #0x2]`). Deshalb über Ghidra,
`find_in_function 0x00231f34 query="r8"`:

```
00231f48: ldr r8,[0x232230]
00231ffc: mov r4,r8
002321f4: str r0,[r8,#0x70]
```

`read_words 0x232230 count=8`:

```json
["0xb8001000", "0xb8001010", "0xb8001040", "0xb8001004",
 "0xb8001020", "0xb8001030", "0x000007dc", "0xe59f305c"]
```

Die Funktion hält also GPIO_BA in r8 und benutzt es für **+0x70**. Die
Portregister erreicht sie über eigene Literale — 0xB8001000 (GPIOA_OMD),
0xB8001010 (GPIOB_OMD), 0xB8001040 (**GPIOE_OMD**), 0xB8001004 (GPIOA_PUEN),
0xB8001020 (GPIOC_OMD), 0xB8001030 (GPIOD_OMD) — und leitet daraus je Port ab:

```
00231fa0: ldr r4,[0x232238]      ; r4  = <Port>_OMD   (Port E: 0xB8001040)
00231fa4: add r12,r4,#0x4        ; r12 = <Port>_PUEN  (Port E: 0xB8001044)
...
00232058: ldr r11,[r4,#0x0]      ; OMD lesen
00232060: str r11,[r4,#0x0]      ; OMD schreiben
00232064: ldr r4,[r12,#0x0]      ; PUEN lesen
002320b4: str r4,[r12,#0x0]      ; PUEN schreiben
```

**REG_GPIOE_PUEN (0xB8001044) wird geschrieben**, obwohl die Bytesuche für
diese Konstante 0 Treffer liefert (1.1): die Adresse entsteht als
`GPIOE_OMD + 4`.

### 2.5 Gegenprobe nach CL-TOOL-REC-114 — Immediate-Ketten

Capstone-Lauf über das ganze Bild, ARM und Thumb, der `mov`/`mvn`-Immediates je
Register verfolgt und `orr`/`add`/`sub`-Immediates daraufrechnet:

```
=== ARM: Immediate-Ketten mit Ergebnis in 0xB8001000-0xB80010FF: 0 ===
=== Thumb (Rohscan über das ganze Bild): Immediate-Ketten … : 0 ===
```

### Was das zeigt

Die Liste im Auftrag ist unvollständig gewesen; die vollständige hat elf
Einträge, vier davon bei VA 0x280884/0x280AE0/0x280B40/0x280B78. Zwei davon sind
über Ghidras Xref-Index gar nicht auffindbar, weil dort 148 Bytes Code nicht
disassembliert sind.

Der Vorbehalt aus `CL-HARDWARE-REC-111` ist in beide Richtungen zu beantworten:

**Es gibt base+offset-Zugriffe, die die Literalsuche nicht sieht** — und zwar
nicht wenige. `REG_GPIOE_DOUT` (+0x48) wird an fünf der elf Ladestellen benutzt
(0x26FC9C, 0x26FD90, 0x28083C, 0x280890, 0x280AE8), zusammen zwölf Zugriffe,
während die Bytesuche für 0xB8001048 nur den einen Treffer bei VA 0x2322BC
liefert. `REG_GPIOE_PUEN` (+0x44) wird in FUN_00231f34 geschrieben, obwohl die
Konstante 0xB8001044 im ganzen Bild nicht vorkommt.

**Auf `REG_GPIOE_PIN` (+0x4C) greift keine der elf Ladestellen zu** — weder
direkt noch über eine `add`-Ableitung. Es gibt auch keine Immediate-Kette, die
irgendeine Adresse im Bereich 0xB8001000–0xB80010FF bildet. Damit bleibt
VA 0x231F30 die einzige Stelle im Bild, über die Port-E-Pinzustände gelesen
werden, und sie gehört zu einer portgenerischen Hilfsfunktion (Aufgabe 1).

### Was das nicht zeigt

- **Nicht, dass die Zugriffsliste je Ladestelle vollständig ist.** Der
  Vorwärtslauf ist linear und rechnet nur `add`/`sub`/`mov` mit konstantem
  Immediate nach. Eine Basis, die über einen Registeroffset (`ldr r0,[r1,r2]`),
  über den Stack oder über einen Funktionsaufruf weitergereicht wird, sieht er
  nicht. Bei 0x232230 ist er an der Sprungtabelle bei 0x231FD0 stehengeblieben;
  dort habe ich mit Ghidras `find_in_function` nachgesetzt, an den übrigen zehn
  Stellen nicht.
- **Nicht, dass GPIO_BA nur elfmal in ein Register gelangt.** Geprüft sind
  Literalpool (Bytesuche) und Immediate-Ketten (eigener Decoder). Eine Basis,
  die aus einer Datenstruktur im RAM oder aus einer Tabelle geladen wird, findet
  keiner der beiden Modi. `CL-TOOL-REC-114` deckt ADR-Formen ab; die habe ich
  für 0xB8001000 nicht separat gesucht, weil ADR den Wert nur PC-relativ und
  damit nur innerhalb des Bildes bilden kann, 0xB8001000 aber außerhalb liegt.
- **Nicht, was die Offsets +0xF8 und +0x70 sind.** Beide liegen außerhalb des
  Blocks GPIO_BA+0x00…0x4F, den der BSP-Header als OMD/PUEN/DOUT/PIN der fünf
  Ports beschreibt. Der Header nennt in der Umgebung `REG_IRQSRCGPB (GPIO_BA+0x84)`,
  `REG_IRQENGPB (GPIO_BA+0xA4)`, `REG_IRQLHSEL (GPIO_BA+0xC0)`,
  `REG_IRQTGSRC0 (GPIO_BA+0xF0)`, `REG_IRQTGSRC1 (GPIO_BA+0xB8)` — teils
  auskommentiert und mit widersprechenden Alternativwerten. +0xF8 und +0x70 sind
  darin nicht enthalten. Ich habe sie nicht im Design Guide nachgeschlagen und
  deute sie nicht.
- **Nicht, dass die +0xB000/+0xB010-Zugriffe SPI-Transfers sind.** Gemessen ist,
  dass 0xB8001000 + 0xB000 = 0xB800C000 = SPI0_BA laut BSP-Zeile 27472 ist. Was
  die Firmware dort tut, ist in Aufgabe 3 nur so weit berührt, wie es die Basen
  betrifft.
- **Nicht, dass die undisassemblierten 148 Bytes bei 0x280AE8 die einzige solche
  Lücke sind.** Ich habe nicht systematisch nach weiteren gesucht.

---

## Aufgabe 3 — MMIO-Basen der Display-Findings

Gelesen aus `research/findings/re_kb_archive/findings/` (nur dort vorhanden;
`.re_kb/findings/` enthält 0001–0011). Nichts geschrieben.

Die Findings geben Funktionsadressen als Dateioffsets an (`0x6fd70` = VA 0x26FD70).

| Finding | Status/Konf. | genannte Basis | laut BSP-Header | stimmt? |
|---|---|---|---|---|
| 0024 | open / null | `0xb8003000` für D/C-Toggle in FUN_0006fd70, `+0x38`, Bit 0x2000 | `RTC_BA 0xB8003000` (Z. 27467) — gemeint war `GPIO_BA 0xB8001000` (Z. 27465) | **nein** |
| 0024 | | `0xb800c000` (GO_BUSY / SPI0) | `SPI0_BA 0xB800C000` (Z. 27472) | ja |
| 0024 | | „clears control bit at base+0x48, writes param to base+0xb010" | +0x48 und +0xB010 sind **GPIO_BA**-relativ: 0xB8001048 = REG_GPIOE_DOUT und 0xB800C010 = SPI0_BA+0x10 | Adressen richtig, Formulierung irreführend |
| 0025 | open / null | `0xb8003000` für D/C („same GPIO bit 0x2000 at base 0xb8003000") | `RTC_BA` — gemeint `GPIO_BA` | **nein** |
| 0025 | | `0xb800c000` (SPI0-Setup in FUN_00080b7c) | `SPI0_BA` (Z. 27472) | ja |
| 0025 | | `0xb8007000` (PWM/Backlight), Offsets 0x40/0x30/0x34 | `PWM_BA 0xB8007000` (Z. 27470) | ja |
| 0025 | | `*_b0000208` (Clock-Bits) | `CLK_BA 0xB0000200` (Z. 27449), +0x08; im Code als `SYS_BA 0xB0000000` + 0x208 gebildet | ja |
| 0027 | in_progress / 1.0 | `0xb8003000` („GPIO base 0xb8003000 bit 0x2000") | `RTC_BA` — gemeint `GPIO_BA` | **nein** |
| 0027 | | `0xb800c000` (SPI0 via +0xb000/+0xb010) | `SPI0_BA` | ja (Adresse), Offsets sind GPIO_BA-relativ |
| 0028 | verified / 1.0 | keine MMIO-Basis genannt | — | — |
| 0030 | in_progress / 0.9 | `0xb8007000` (PWM/Backlight) | `PWM_BA` (Z. 27470) | ja |
| 0030 | | „SPI0 setup at 0x80b7c" | VA 0x280B7C lädt 0xB800C000 aus 0x280CB0 | ja |

### Belege der Messungen in der Tabelle

**D/C-Toggle — `disassemble_at 0x0026fd70 count=8`:**

```
0026fd70: 000050E3 cmp r0,#0x0
0026fd74: 10009FE5 ldr r0,[0x26fd8c]
0026fd78: 381090E5 ldr r1,[r0,#0x38]
0026fd7c: 021A8113 orrne r1,r1,#0x2000
0026fd80: 021AC103 biceq r1,r1,#0x2000
0026fd84: 381080E5 str r1,[r0,#0x38]
0026fd88: 1EFF2FE1 bx lr
```
Der Literal bei 0x26FD8C ist `0xb8001000` (Bytesuche 1.1 und `read_words`). Also
GPIO_BA+0x38 = REG_GPIOD_DOUT, Bit 13. Nicht 0xB8003000, nicht RTC.

**Kommandoschreiber — `disassemble_at 0x0026fd90 count=16`:**

```
0026fd90: 38209FE5 ldr r2,[0x26fdd0]      ; 0xB8001000
0026fd94: 481092E5 ldr r1,[r2,#0x48]      ; REG_GPIOE_DOUT
0026fd98: 011CC1E3 bic r1,r1,#0x100       ; Bit 8 löschen  -> GPE[8]
0026fd9c: 481082E5 str r1,[r2,#0x48]
0026fda0: 0B1A82E2 add r1,r2,#0xb000      ; SPI0_BA
0026fda4: 4530A0E3 mov r3,#0x45
0026fda8: 100081E5 str r0,[r1,#0x10]      ; SPI0_BA+0x10
0026fdac: 003081E5 str r3,[r1,#0x0]       ; SPI0_BA+0x00 <- 0x45
0026fdb0: 000091E5 ldr r0,[r1,#0x0]
0026fdb4: 010010E3 tst r0,#0x1
0026fdb8: FCFFFF1A bne 0x0026fdb0         ; auf Bit 0 warten
0026fdbc: 100091E5 ldr r0,[r1,#0x10]
0026fdc0: 480092E5 ldr r0,[r2,#0x48]
0026fdc4: 010C80E3 orr r0,r0,#0x100       ; Bit 8 setzen
0026fdc8: 480082E5 str r0,[r2,#0x48]
0026fdcc: 1EFF2FE1 bx lr
```

**PWM — `find_in_function 0x0025c1a0` (Literalladungen), `read_words 0x25c3d8`,
`disassemble_at 0x25c228`:**

```json
{"address": "0x0025c3d8", "words": ["0xb8007000", "0x00002ee0", "0x000fbaac",
  "0x30000066", "0x0008247c", "0x0008249c", "0x000004b2", "0xe92d4010"]}
```
```
0025c228: A8619FE5 ldr r6,[0x25c3d8]      ; 0xB8007000 = PWM_BA
0025c22c: 080294E5 ldr r0,[r4,#0x208]     ; r4 = 0xB0000000, also 0xB0000208
0025c230: 040080E3 orr r0,r0,#0x4
0025c234: 080284E5 str r0,[r4,#0x208]
0025c238: 400096E5 ldr r0,[r6,#0x40]      ; PWM_BA+0x40
0025c23c: 0800C0E3 bic r0,r0,#0x8
0025c240: 400086E5 str r0,[r6,#0x40]
0025c244: 307086E5 str r7,[r6,#0x30]      ; PWM_BA+0x30
0025c248: 347086E5 str r7,[r6,#0x34]      ; PWM_BA+0x34
```

**SPI0-Setup bei VA 0x280B7C — `read_words 0x280cb0 count=2`:**

```json
{"address": "0x00280cb0", "words": ["0xb800c000", "0x00000c04"]}
```

**Funktionsadressen aus finding-0028 — `disassemble_batch`:**

```
0x0021cab0: stmdb sp!,{r4,...,lr}        -> echter Funktionseinstieg
0x0021d0c0: stmdb sp!,{r4,...,lr}        -> echter Funktionseinstieg
0x0021d77c: stmdb sp!,{r4,r5,r6,lr}      -> echter Funktionseinstieg
0x0021d1c0: stmdb sp!,{r3,r4,r5,lr}      -> echter Funktionseinstieg
0x0021d5a4: ldr r0,[r4,#0x10]            -> KEIN Funktionseinstieg
```

`search_xrefs_to 0x0026fd70` → total 8, alle aus FUN_0021cab0, FUN_0021d0c0,
FUN_0021d1c0, FUN_0021d77c — exakt die vier Funktionen aus finding-0028.

### Was das zeigt

Der Zahlendreher RTC_BA statt GPIO_BA steht in **drei** der fünf Findings, nicht
in zweien: 0024, 0025 und 0027 nennen alle 0xB8003000 für dieselbe
D/C-Leitung. Gemessen ist an jeder dieser Stellen 0xB8001000+0x38 =
REG_GPIOD_DOUT, Bit 13. Das deckt sich mit `CL-SOC-REC-021` und erweitert es um
finding-0025.

**Alle übrigen in diesen fünf Findings genannten Basen stimmen** gegen den
BSP-Header: SPI0_BA 0xB800C000, PWM_BA 0xB8007000, CLK_BA+0x08 = 0xB0000208.
Auch die Offsets 0x40/0x30/0x34 am PWM-Block sind an VA 0x25C238/0x25C244/0x25C248
so vorhanden.

Eine zweite, kleinere Ungenauigkeit: finding-0024 und -0027 schreiben die
Offsets `+0x48` und `+0xb000/+0xb010` so, als wären sie SPI0-relativ. Sie sind
GPIO_BA-relativ. `+0x48` ist REG_GPIOE_DOUT und gehört zur Chip-Select-Leitung
GPE[8], nicht zum SPI-Block; `+0xb010` ist SPI0_BA+0x10.

Die Annahme des Auftrags, die Funktionsadressen seien richtig, trifft für vier
von fünf zu. **finding-0025 nennt `FUN_0001d5a4`, und VA 0x21D5A4 ist kein
Funktionseinstieg**, sondern liegt im Rumpf des Blocks 0x21D244–0x21D774, den
Ghidra der Funktion „FUN_002bd0e0" zuordnet (sichtbar in den
`search_xrefs_to 0x0026fd90`-Kontexten). Inhaltlich passt es: aus diesem Block
gehen 13 Aufrufe an den Kommandoschreiber FUN_0026fd90 — die Init-Sequenz ist
dort. Nur der genannte Einstiegspunkt ist es nicht.

### Was das nicht zeigt

- **Nicht, dass die Findings inhaltlich stimmen.** Geprüft sind ausschließlich
  die MMIO-Basen. „ST7789V", „240x320", „RGB565", „CASET/RASET/RAMWR",
  „Backlight" sind Deutungen der Findings, die ich weder bestätigt noch
  widerlegt habe. Ob der Controller ein ST7789V ist, folgt aus keinem der hier
  gelesenen Werkzeugausgaben.
- **Nicht, dass GPE[8] die Chip-Select-Leitung ist.** Gemessen ist, dass
  FUN_0026fd90 Bit 8 in REG_GPIOE_DOUT um den SPI-Transfer herum löscht und
  wieder setzt. Die Rolle „Chip Select" ist die naheliegende Lesart, folgt aber
  nicht aus einem Herstellerdokument.
- **Nicht, dass 0xB800C000+0x00 mit Wert 0x45 „GO_BUSY" heißt.** Ich habe die
  SPI-Registerbeschreibung im Design Guide (S. 780–811) nicht gelesen. Dass Bit 0
  gepollt wird, ist abgelesen; der Name stammt aus finding-0024 und ist hier
  nicht nachgeprüft.
- **Nicht, dass GPIO_BA+0x38 Bit 13 an GPD[13] hängt.** Der Offset ist laut
  BSP-Header REG_GPIOD_DOUT, das Bit ist 13. Welcher physische Pin das ist,
  hängt an der Pinmux-Konfiguration und am Pinout und ist hier nicht geprüft.
- **Nicht, dass die Findings-IDs eindeutig sind.** `CL-TOOL-REC-103`: die IDs
  der beiden RE-KBs kollidieren. 0024/0025/0027/0028/0030 existieren nur im
  Archiv; im aktuellen `.re_kb` liegen 0001–0011. Welche davon dieselben
  Nummern belegen, habe ich nicht abgeglichen.
- **Nicht, wo die Init-Funktion aus finding-0025 wirklich beginnt.** Ich habe
  nur festgestellt, dass 0x21D5A4 kein Einstieg ist und dass Ghidra den Block ab
  0x21D244 einer Funktion mit dem Namen „FUN_002bd0e0" zuordnet — was selbst
  nach einem Ghidra-Artefakt aussieht. Die tatsächliche Einstiegsadresse habe
  ich nicht bestimmt.

---

## Umbenennungen und Kommentare in Ghidra

Keine Umbenennung. Keine der hier untersuchten Funktionen hat eine Identität,
die aus einem Herstellerheader oder einem String im Binary folgt — die
Portauswahl in FUN_00231ec4, die Modusnibbles in FUN_00231f34 und die Rolle von
FUN_0026fbf8 sind sämtlich aus dem Kontrollfluss erschlossen. Nach der Regel im
Auftrag bleibt es deshalb bei `set_comment`; die gesetzten Kommentare sind unten
aufgeführt.

Gesetzt mit `set_comment` (`comment_type: decompiler`, `dry_run: false`),
danach `save_program` → `{"saved": true, "mutations_cleared": 9}`:

| Adresse | Inhalt (Kurzfassung) |
|---|---|
| 0x00231EC4 | Portgenerischer Pin-Leser; Poolzuordnung A/B/C/D/E; Maske = `1 << param_2`; die vier Aufrufer mit ihren Argumenten. Zweifel: Zweck nicht belegt. |
| 0x00231FA0 | Port-E-Pfad von FUN_00231F34: r4 = GPIOE_OMD, r12 = GPIOE_PUEN (= OMD+4, Literal existiert nicht), Bitgrenze 0xB; +0x4C wird nirgends berührt. |
| 0x00232730 | Der von `CL-HARDWARE-REC-003` als MF_GPE10-Kandidat genannte Ort ist keiner: SYS_BA+0x20 und TMR_BA+0x1C (REG_WTCR), dann Endlosschleife. |
| 0x00243F60 | Tickquelle: 64-Bit-Wert an absolut 0xC18, erhöht von 0x2A3A8C, aufgerufen aus 0x2A3AAC nach REG_TISR-Prüfung. Zweifel: Einheit nicht gemessen. |
| 0x0025C3A0 | GPE[10] wird hier konfiguriert (Modus 0x23); Nibble-Auswertung in FUN_00231F34; AIC_BA+0x120. Zweifel: Interruptdeutung, und der Parameterwert 0x0008249C ist ungeklärt. |
| 0x0026FBF8 | Einziger Port-E-Aufrufer: Bit 9, Maske 0x200, nicht 0x400; die Warteschleife ist ein Timeout. |
| 0x0026FD70 | Basis ist GPIO_BA, nicht RTC_BA; der Zahlendreher steht in finding-0024, -0025 **und** -0027. |
| 0x00280AE8 | Von Ghidra nicht disassemblierter Codebereich; erklärt die zwei fehlenden Xrefs; Offsetliste beider Routinen. |
