# B2 — Die Brücke vom USB-Kanal in die Dokumentablage

Sonde vom 2026-08-31. Programm `ZK-INKJET-NANO-APP.bin.orig`, Ghidra-Basis
0x00200000 (`get_current_program` → `state: READY`).
Rohdatei für alle Eigen-Suchen: `firmware/bin/ZK-INKJET-NANO-APP.bin`,
2 576 940 Bytes.

## 0. Vorbemerkung zur Datei und zur VA-Abbildung

`CL-USB-REC-119` nennt für dieselbe Suche eine Dateigröße von 2 577 964 Bytes;
die Datei im Repo hat 2 576 940 Bytes, 1024 weniger. Die Abbildung
VA = Dateioffset + 0x200000 wurde deshalb gegen die dort protokollierten
Fundstellen nachgeprüft:

```
python3: d=open('firmware/bin/ZK-INKJET-NANO-APP.bin','rb').read()
  size 2576940 0x27522c
  at 0x1CA5C: 00 40 61 2a
  at 0x1CAAC: 00 40 61 2a
  0x2A614000 LE occurrences: ['0x1ca5c', '0x1caac']
```

Genau zwei Treffer, genau an den in `CL-USB-REC-119` genannten Offsets. Die
Abbildung stimmt; die Größenangabe in der Zeile stimmt nicht. Alles Weitere
verwendet die Repo-Datei.

---

# Aufgabe 1 — wer füllt `*(*(0x000007D8) + 0x98)` mit 65536?

## 1.1 Die Werkzeugaufrufe und ihre Ausgabe

### `disassemble_at(0x0021984C, 16)`

```
0021984c: 0010A0E1 mov r1,r0
00219850: 28009FE5 ldr r0,[0x219880]
00219854: 940090E5 ldr r0,[r0,#0x94]
00219858: 010050E1 cmp r0,r1
0021985c: 0500001A bne 0x00219878
00219860: 1C009FE5 ldr r0,[0x219884]
00219864: 000090E5 ldr r0,[r0,#0x0]
00219868: 980090E5 ldr r0,[r0,#0x98]
0021986c: 8000A0E1 mov r0,r0, lsl #0x1
00219870: 08209FE5 ldr r2,[0x219880]
00219874: 3C0082E5 str r0,[r2,#0x3c]
00219878: 0000A0E3 mov r0,#0x0
0021987c: 1EFF2FE1 bx lr
```

### `read_words(0x00219880, 4)`

```
["0x000082ec", "0x000007d8", "0xe92d4fff", "0xe24ddb02"]
```

0x82EC wird als **Strukturbasis** benutzt (`ldr r0,[r0,#0x94]`), 0x7D8 als
**Zeigervariable** (`ldr r0,[r0,#0x0]`).

### `grep -rn "DISK_DATA_T" vendor/N32901-3_NonOS_BSP/`

20 Treffer; die Definition steht in `SIC/Src/fmi.h:41-52`,
`SIC_SECC/Src/fmi.h:29-40` und `SPI/Lib/SPIGlue.h:17-28`, alle drei identisch:

```
  +0x00  next
  +0x04  totalSectorN
  +0x08  diskSize            /* disk size in Kbytes */
  +0x0C  sectorSize
  +0x10  vendor[32]
  +0x30  product[32]
  +0x50  serial[32]
  sizeof = 0x70 (112)
```

**`diskSize` liegt bei +0x08, nicht bei +0x98.** Die Vermutung aus
`CL-USB-REC-120`, `*(0x7D8)` sei ein `DISK_DATA_T`, ist damit auf Strukturebene
widerlegt.

### Die Struktur, die passt — `PDISK_T` aus NVTFAT

Die Spur führt über `SIC/Src/SDGlue.c:562`, `pDisk->uDiskSize =
pSDDisk->diskSize;`. `pDisk` ist ein `PDISK_T`, definiert in
`vendor/N32901-3_NonOS_BSP/NVTFAT/lib/nvtfat.h:222-248`
(`typedef struct physical_disk_S`). Ausgerechnetes Layout (ARM EABI,
4-Byte-Ausrichtung):

```
  +0x00  nDiskType          +0x9C  nPartitionN
  +0x04  szManufacture[32]  +0xA0  ptPartList
  +0x24  szProduct[32]      +0xA4  nPreferDriveNo
  +0x44  szSerialNo[64]     +0xA8  ptSelf
  +0x84  nCylinderNum       +0xAC  ptDriver
  +0x88  nHeadNum           +0xB0  ptPDiskAllLink
  +0x8C  nSectorNum         +0xB4  pvPrivate
  +0x90  uTotalSectorN      +0xB8  os_mutex
  +0x94  nSectorSize        +0xBC  os_priv
  +0x98  uDiskSize   /* disk size in Kbytes */
  sizeof = 0xC0 (192)
```

`uDiskSize` liegt **exakt bei +0x98** und ist in KiB angegeben — das `lsl #1`
bei 0x0021986C rechnet KiB in 512-Byte-Blöcke um. Zur Vollständigkeit wurde
auch `LDISK_T` (nvtfat.h:279-300) geprüft: dort liegt `uDiskSize` bei +0x20 und
zählt Sektoren; passt nicht.

### Vier-Modi-Suche nach 65536

Regel 3 des Auftrags. Alle vier Modi über die ganze Datei:

**(a) `search_scalars(65536)` und `search_scalars("0x10000")`** — beide liefern
dieselbe Liste, >50 Treffer, `has_more: true`, `truncated: true`. Kein
`method_note` (nur Leerergebnisse tragen einen). Die Treffer sind fast
durchgehend `tst r0,#0x10000` (CPSR-Bittests) und `mov/add/cmp`-Formen.

**(b) Bytesuche `00 00 01 00` über die ganze Datei:** 245 Treffer, davon die
große Mehrheit unausgerichtet und im Ressourcenbereich ab 0x2C7000 — also
Bilddaten, keine Literale.

**(c) PC-relative Literale mit dem Wert 0x00010000:**

```
=== all pool constants equal to 0x00010000 that are PC-load targets ===
  0 sites
```

Über alle 1895 verschiedenen Poolkonstanten der Datei kommt 0x10000 als
Poolwort **nicht** vor. Der Scan zählt jedes `ldr Rd,[pc,#±imm]`
(Maske `0x0F7F0000 == 0x051F0000`), löst das Ziel auf und liest das Wort.

**(d) `mov Rd,#0x10000` (imm8=1, rot=8) mit anschließendem Store:** 32 Fundstellen.
Für jede wurde geprüft, ob das geladene Register innerhalb der nächsten 12
Befehle nach `+0x98` gespeichert wird:

```
  VA 0x0021733C  mov r1,#0x10000   -> stores of that reg within 12: []
  VA 0x002182EC  mov r0,#0x10000   -> [(2,'str r0,[r4,#0x4]'), (4,'str r0,[r4,#0x8]')]
  ... (alle 32 aufgelistet, keine mit Offset 0x98) ...
  VA 0x002C1088  mov r0,#0x10000   -> [(1,'str r0,[r4,#0x68]')]
```

Kein einziger Treffer auf `str Rd,[Rn,#0x98]`.

### Alle Zugriffe auf Offset +0x98, unabhängig vom Wert

Eigener Scan über die ganze Datei nach `ldr/str Rd,[Rn,#±0x98]` (vorindiziert,
Immediate-Form):

```
ARM LDR/STR with immediate offset 0x98 (pre-indexed): 153 hits
  stores: 53   loads: 100
```

Von den 53 Stores haben 30 `r13` als Basis (Stack-Frames) und scheiden aus.
Die verbleibenden 23 wurden nach der `PDISK_T`-Signatur sortiert — Stores auf
+0x00, +0x90, +0x94, +0x9C, +0xA0, +0xAC mit **derselben Basis** im Fenster
±60 Befehle:

```
  score 6/6  VA 0x0025164C  ['0x0','0x90','0x94','0x9c','0xa0','0xac']
  score 4/6  VA 0x002AF660 / 0x002AF1C8 / 0x0029421C / 0x002818CC
  score 3/6  VA 0x00236248
  score 2/6  VA 0x002AEE04, 0x002AEC58, 0x0029E074, 0x0029E008, 0x0029DF68,
             0x0029DF50, 0x0029DD18, 0x0029DD00, 0x0029D5A8, 0x0029D594,
             0x00276E10, 0x0023DF60, 0x00215D34
  score 1/6  VA 0x0029DEE8, 0x0029DECC, 0x0029D638
  score 0/6  VA 0x0029D68C
```

Die Kandidaten mit score ≥ 2 wurden einzeln disassembliert. Ergebnis:
0x002818CC schreibt Funktionszeiger (0x000FB1EC, 0x000DB898 …), 0x0023DF60
und 0x00215D34 nullen Felder, 0x0029421C kopiert einen Stack-Block,
0x002AF1C8/0x002AF660 kopieren Felder zwischen zwei Strukturen (+0x190/0x19C/
0x1A8/0x1AC ↔ +0x7C/0x88/0x94/0x98), 0x00276E10 gehört zum MSC-Zustand — sein
Poolwort `read_words(0x00276e4c)` ist `0x000082ec`, also dieselbe Basis wie in
0x0021984C, nicht `*(0x7D8)`.

### Der einzige echte `PDISK_T`-Konstruktor: 0x002515F0

`disassemble_at(0x002515C0, 48)`:

```
002515f0: C000A0E3 mov r0,#0xc0          ; sizeof(PDISK_T) = 0xC0
002515f4: 67ECFEFA blx 0x0020c798        ; malloc
002515f8: 0060B0E1 movs r6,r0
00251600: C010A0E3 mov r1,#0xc0
00251604: A3F2FEEB bl 0x0020e098         ; memset(pDisk,0,0xC0)
00251608: 301087E2 add r1,r7,#0x30       ; pSDDisk->product   (DISK_DATA_T+0x30)
0025160c: 240086E2 add r0,r6,#0x24       ; pDisk->szProduct   (PDISK_T+0x24)
00251610: 0490C6E5 strb r9,[r6,#0x4]     ; szManufacture[0]='\0'
00251614: 7FF1FEFA blx 0x0020dc18        ; strcpy
00251618: 501087E2 add r1,r7,#0x50       ; pSDDisk->serial    (DISK_DATA_T+0x50)
0025161c: 440086E2 add r0,r6,#0x44       ; pDisk->szSerialNo  (PDISK_T+0x44)
00251620: 7CF1FEFA blx 0x0020dc18        ; strcpy
00251624: 2010A0E3 mov r1,#0x20
00251628: 001086E5 str r1,[r6,#0x0]      ; nDiskType = 0x20
0025162c: 020CA0E3 mov r0,#0x200
00251630: 9C9086E5 str r9,[r6,#0x9c]     ; nPartitionN = 0
00251634: 940086E5 str r0,[r6,#0x94]     ; nSectorSize = 512
00251638: A09086E5 str r9,[r6,#0xa0]     ; ptPartList = NULL
0025163c: 040097E5 ldr r0,[r7,#0x4]      ; pSDDisk->totalSectorN
00251644: 900086E5 str r0,[r6,#0x90]     ; pDisk->uTotalSectorN
00251648: 080097E5 ldr r0,[r7,#0x8]      ; pSDDisk->diskSize   (DISK_DATA_T+0x08)
0025164c: 980086E5 str r0,[r6,#0x98]     ; pDisk->uDiskSize    <-- DER STORE
00251650: 0B00000A beq 0x00251684        ; r5 == 0  (cardSel)
00251654: 010055E3 cmp r5,#0x1
0025165c: 020055E3 cmp r5,#0x2
```

und der Zweig für cardSel==0:

```
00251684: 8C009FE5 ldr r0,[0x251718]
00251688: AC0086E5 str r0,[r6,#0xac]     ; pDisk->ptDriver = &_SD0DiskDriver
0025168c: 0600A0E1 mov r0,r6
00251690: 106084E5 str r6,[r4,#0x10]     ; <-- hier wird der Zeiger abgelegt
00251694: AACCFEEB bl 0x00204944         ; fsPhysicalDiskConnected-artig
```

`read_words(0x002516d8, 20)` liefert für `ldr r4,[0x2516e4]` den Wert
`0x00000974`. Der fertige `PDISK_T*` landet also in `*(0x974+0x10)` = 0x984
(bzw. 0x988 / 0x98C für cardSel 1/2) — **nicht** in 0x7D8.

Zur Absicherung: `disassemble_at(0x00204D00, 40)` zeigt bei 0x00204D30
`mov r0,#0xc0` / malloc / `mov r2,#0xc0` / memcpy und danach eine Verkettung
über `+0xB0` (`ptPDiskAllLink`) und `+0xA0` (`ptPartList`) — das ist
`fsGetFullDiskInfomation()`; der Listenkopf steht laut
`read_words(0x00204e94,12)` bei `0x00000B80`. Auch das ist nicht 0x7D8.

### Vier-Modi-Suche nach der Adresse 0x000007D8 selbst

```
=== B: 0x7D8 as LE word (d8 07 00 00) ===
[0x7D8] pattern d8070000 -> 1 hits
   file+0x19884  VA 0x00219884  aligned=yes

=== MOV/MVN + ADD/ORR/SUB immediate chains producing 0x7D8 (ARM) ===
  total: 0
=== Thumb LDR literal (halfword-scan) yielding 0x7D8 anywhere in file ===
  total: 0
=== 0x7D8 in BOOT.bin ===  size 12736
  d8 07 00 00 found at: not present
```

0x7D8 ist als ARM-Immediate nicht kodierbar (11 signifikante Bits), deshalb der
Kettentest. Zusätzlich ein konstantenpropagierender Scan über die ganze Datei:
Basisregister aus PC-Literalen und `mov/add/sub`-Immediates verfolgen, für jedes
`ldr/str Rd,[Rn,#±imm]` die absolute Effektivadresse ausrechnen:

```
absolute accesses resolving to 0x7D8: 1
  VA 0x00219864  ldr r0,[r0(=0x7D8),#+0x0]
```

### Die 18 Ghidra-Xrefs auf 0x7D8 sind keine

`search_xrefs_to(0x000007d8)` meldet `total: 18`. Der erste ist der echte Lesezugriff,
die anderen 17 sind mit `[DATA]` markiert. `disassemble_batch` über elf davon:

```
0x0022a530: D87784E5 str r7,[r4,#0x7d8]     0x0026f480: D80797E5 ldr r0,[r7,#0x7d8]
0x0025f350: D8578015 strne r5,[r0,#0x7d8]   0x0026f490: D86787E5 str r6,[r7,#0x7d8]
0x0025f388: D85783E5 str r5,[r3,#0x7d8]     0x002c1ec4: D85780E5 str r5,[r0,#0x7d8]
0x002c1fcc: D83782E5 str r3,[r2,#0x7d8]     0x002c2000: D83788E5 str r3,[r8,#0x7d8]
```

Das sind Strukturfeldzugriffe mit Offset 0x7D8 auf fremden Basen, keine
Referenzen auf die absolute Adresse 0x7D8. Nachgeprüft an
`disassemble_at(0x0026f40c, 36)`: dort ist die Basis
`r7 = r4 + (r5*[0x26f630]) << 3`, also ein indizierter Strukturzeiger, sicher
nicht 0. Ghidras Xref-Liste ist an dieser Stelle **irreführend**, nicht
unvollständig.

### Und der Fensterbasis-Teil von CL-USB-REC-119

`disassemble_batch(["0x0021C998","0x0021CA60"], 22)`:

```
0021c99c: B8C09FE5 ldr r12,[0x21ca5c]        ; 0x2A614000
0021c9a4: 80548CE0 add r5,r12,r0, lsl #0x9   ; base + lba*512
0021ca64: 40309FE5 ldr r3,[0x21caac]         ; 0x2A614000
0021ca6c: 804483E0 add r4,r3,r0, lsl #0x9
```

Beide Funktionen holen die Basis aus dem eigenen Pool und fragen `*(0x7D8)`
**nicht** ab.

## 1.2 Was das zeigt

- Das Feld bei +0x98 ist `PDISK_T.uDiskSize`, Größe in KiB, belegt durch den
  Herstellerheader `NVTFAT/lib/nvtfat.h`. Das Offset trifft exakt, die
  Verdopplung bei 0x0021986C ist die KiB→512-Byte-Block-Umrechnung. Damit ist
  die *Semantik* aus `CL-USB-REC-120` bestätigt, die *Struktur* dagegen
  korrigiert: nicht `DISK_DATA_T` (dort +0x08), sondern `PDISK_T`.
- 65536 ist **keine Codekonstante**. Alle vier Suchmodi sind gelaufen: 0x10000
  kommt als Poolwort nirgends vor, und keine der 32 `mov Rd,#0x10000`-Stellen
  speichert nach +0x98. Es gibt in der ganzen Datei genau 53 ARM-Stores auf
  +0x98; 30 davon auf den Stack, und von den 23 übrigen ist genau einer
  (0x0025164C) ein `PDISK_T`-Konstruktor.
- Dieser Konstruktor ist Befehl für Befehl der Rumpf von `SDCARD_Open` aus
  `SIC/Src/SDGlue.c:541-570` — malloc(0xC0), memset, die beiden strcpy auf
  +0x24/+0x44 aus `DISK_DATA_T`+0x30/+0x50, `nSectorSize=512`,
  `uTotalSectorN` aus +0x04, `uDiskSize` aus +0x08. Der Wert stammt also aus
  dem CSD der SD-Karte über `fmiGet_SD_info`, **nicht** aus einem MBR und
  **nicht** aus einem Literal.
- Dieser `PDISK_T` ist aber nicht der, auf den 0x7D8 zeigt: er wird nach
  `*(0x974+0x10/0x14/0x18)` geschrieben. Die Karte in den Abzügen ist 2 GiB
  groß, ihr `uDiskSize` wäre rund 2 000 000 KiB, nicht 65536.
- **Die Kette reißt an der Zeigervariablen 0x000007D8 ab.** In APP.bin wird die
  Adresse 0x7D8 genau einmal materialisiert: als Poolwort bei 0x00219884, gelesen
  von 0x00219860. Kein Poolwort, keine Immediate-Kette, kein Thumb-Literal, kein
  auflösbarer Basis+Offset-Zugriff schreibt sie. In BOOT.bin kommt sie nicht vor.
- `read_words(0x000007d8, 4)` liefert `[null, null, null, null]`: die Adresse
  liegt **außerhalb jedes gemappten Blocks** des Ghidra-Programms. Dasselbe gilt
  für 0x82EC, 0x974, 0xB80, 0xD00.
- Für den Acht-Byte-Patch aus `CL-USB-REC-119` ist die praktisch entscheidende
  Aussage trotzdem gesichert: Basis und Kapazität sind im Code entkoppelt.
  `usb_lun_read_blocks`/`usb_lun_write_blocks` holen 0x2A614000 aus ihrem eigenen
  Pool und rühren `*(0x7D8)` nicht an; und es existiert im ganzen Bild keine
  Stelle, die einen MBR-Eintrag nach +0x98 schreibt — der einzige +0x98-Schreiber
  mit `PDISK_T`-Signatur liest aus `DISK_DATA_T`.

## 1.3 Was das nicht zeigt

- Es zeigt **nicht**, wer 65536 in das Feld schreibt. Die Frage aus
  `CL-USB-REC-119` bleibt formal offen; nur der Teil „es ist keine Konstante im
  Code und wird nicht aus dem MBR am Fensterrand geparst" ist belegt — und auch
  dieser Teil nur für APP.bin.
- Es zeigt **nicht**, dass `*(0x7D8)` wirklich ein `PDISK_T` ist. Das ist ein
  Offset-Abgleich mit einem Header, kein Symbol. Die Zahlen passen (65536 KiB ×
  2 = 131072 Blöcke, gemessen am Host), aber eine andere Struktur mit einem
  passenden Feld bei +0x98 würde ebenso passen. Der Zweifel steht als
  `set_comment` bei 0x00219868 im Programm.
- Es zeigt **nicht**, dass es keinen Schreiber gibt. Zwei Lücken bleiben in der
  Methode: (i) Stores in Registerversatz-Form (`str Rd,[Rn,Rm]`) wurden nicht
  aufgelöst; (ii) Stores, deren Basisregister als Parameter hereinkommt oder aus
  dem Speicher geladen wird, kann die Konstantenpropagation nicht auflösen. Für
  beide Fälle wäre der Zeiger allerdings vorher irgendwo materialisiert worden,
  und das ist ausgeschlossen.
- Es zeigt **nicht**, dass 65536 nichts mit dem Fensterrand zu tun hat. Der MBR
  bei 0x2A614000 beschreibt Start-LBA 63 plus 131009 Sektoren = **131072
  Sektoren = exakt 65536 KiB**. Ob die Firmware diesen MBR aus einer festen
  64-MiB-Vorgabe erzeugt hat oder umgekehrt, ist mit dem Code allein nicht zu
  entscheiden, solange der Schreiber fehlt.

## 1.4 Ein Nebenbefund, der die Kette erklärt

Mehrere absolute Zeiger in APP.bin zeigen unterhalb von 0x00200000 und lassen
sich weder mit Basis 0x200000 noch mit Basis 0 in APP.bin auflösen. Der
auffälligste ist die **Rückruffunktion 0x0008A434**, die an vier unabhängigen
Stellen als Poolwort geladen und auf dem Stack an die Slot-Routinen übergeben
wird:

```
0025e2a8: E59FB2D8 ldr r11,[pc,#0x2d8] ; [0x0025E588]=0x0008A434
0025f230: E59F0178 ldr r0,[pc,#0x178]  ; [0x0025F3B0]=0x0008A434
0026b048: E59F2288 ldr r2,[pc,#0x288]  ; [0x0026B2D8]=0x0008A434
0026f544: E59F20F0 ldr r2,[pc,#0xf0]   ; [0x0026F63C]=0x0008A434
0026b044: E59F3288 ldr r3,[pc,#0x288]  ; [0x0026B2D4]=0x0008A500
```

Aufgerufen wird sie in `FUN_0028A248` als `blx r6` und in `FUN_0028A3DC` als
`blx r11`, jeweils mit `(Rohadresse, Puffer, 0x10)`. Ebenso zeigen die
Zeigertabelle bei 0x00281890-0x002818D4 (0x000D9934 … 0x000FB1EC) und die
Zeichenketten-/Ressourcenzeiger 0x00128154, 0x00144D4C, 0x0014F7AC dorthin;
die letzten drei enthalten in der Datei RGBA-Pixeldaten, unter Basis 0
Bilddaten — sie gehören nicht zu APP.bin.

Prüfung der Ladebasis: APP.bin beginnt bei Offset 0 mit
`msr cpsr,#0xdb / ldr sp,[pc,…]` und einer Stack-Tabelle
(0x007FF000 … 0x00800000) bei Offset 0x40 — also mit einem Reset-Handler, nicht
mit einer ARM-Vektortabelle. `firmware/image/APP.header.bin` dagegen beginnt mit
`b +0x50` und sieben `ldr pc,[pc,#0x18]` samt Vektorzeigertabelle, ist also das
bei 0 liegende Vektorbild und stimmt mit APP.bin an keiner Stelle überein
(`cmp -n 4096` → Byte 1 verschieden, die ersten 64 Header-Bytes kommen in
APP.bin nicht vor). APP.bin liegt also nicht bei 0; Basis 0x00200000 bleibt
richtig.

Damit ist die naheliegende Erklärung: **unterhalb von 0x00200000 liegt ein
zweites, resident geladenes Code- und Datenbild**, das die Rohzugriffs-Primitive
(0x8A434, 0x8A500), Ressourcen (0x128154 ff.) und die Globalen 0x7D8, 0x82EC,
0x974, 0xB80, 0xD00 stellt. Der Schreiber von `*(0x7D8)` liegt mit hoher
Wahrscheinlichkeit dort — außerhalb von APP.bin und außerhalb des
Ghidra-Programms. Das ist genau die Stelle, an der die Kette abreißt, und der
Grund dafür.

Die bekannte Blindstelle VA 0x280AE8–0x280B7B (`CL-TOOL-REC-117`) wurde von
keiner Kette getroffen; alle Eigen-Scans laufen ohnehin über die Rohdatei und
schließen sie ein.

---

# Aufgabe 2 — wer liest die Dokumentablage?

## 2.1 Die Werkzeugaufrufe und ihre Ausgabe

### Vier-Modi-Suche nach dem Magic 0x2022

`search_scalars("0x2022")` → `items: []`, mit `method_note`:

> „Blind spot: this searches instruction operands only. A value held in a
> constant pool and reached by a PC-relative load — the usual ARM way to
> materialise a 32-bit constant — never appears as an operand, and neither does
> a value assembled from several immediates. …"

Das Leerergebnis ist erwartet: 0x2022 ist als ARM-Immediate **nicht kodierbar**
(geprüft: kein `imm8 ror 2n` erzeugt 0x2022). Eine Scalar-Suche danach ist
Nullergebnis per Konstruktion.

Bytesuche und Literalsuche über die Rohdatei:

```
===== document magic = 0x2022 =====
  [byte search, whole file] 5 hits:
      file+0x29F35 (VA 0x00229F35) UNALIGNED
      file+0x65D4C (VA 0x00265D4C)
      file+0x8A3D8 (VA 0x0028A3D8)
      file+0x8A538 (VA 0x0028A538)
      file+0xF4EA7 (VA 0x002F4EA7) UNALIGNED
  [PC-literal loads] 3 hits:
      VA 0x00265B4C -> r11  pool 0x00265D4C
      VA 0x0028A25C -> r11  pool 0x0028A3D8
      VA 0x0028A4C0 -> r0   pool 0x00265... (0x0028A538)
  [ARM immediates] 0 hits
```

Die Liste aus `CL-USB-REC-108` ist damit selbst nachgeprüft und stimmt: drei
ausgerichtete Poolwörter, zwei unausgerichtete Zufallstreffer. Neu sind die drei
**ladenden Befehle**.

### Vier-Modi-Suche nach Basis und Schrittweite

```
0x28800000 encodable as ARM immediate: [(rot=10, imm8=162)]
0x4D000    encodable as ARM immediate: [(rot=20, imm8=77)]

===== store base = 0x28800000 =====
  [byte search] 2 hits, beide UNALIGNED (0x3A9222, 0x3D49FE) -> Ressourcendaten
  [PC-literal loads] 0 hits
  [ARM immediates] 14 hits: 0x0025E2B0 mov r10, 0x0025F234 mov r2,
     0x002625D0 mov r2, 0x00265B70 mov r7, 0x00265FE4 mov r8, 0x0026B060 mov r3,
     0x0026B35C mov r3, 0x0026F54C mov r0,  (+6 Treffer ab 0x0038BAC8, Datenbereich)

===== store stride = 0x4D000 =====
  [byte search] 0 hits
  [PC-literal loads] 0 hits
  [ARM immediates] 19 hits: 0x0025E360 mov r3, 0x0025E488 mov r3,
     0x0025F24C mov r3, 0x002625E8 mov r1, 0x00265B6C mov r8, 0x00265FE0 mov r7,
     0x0026B058 mov r2, 0x0026B354 mov r2, 0x0026F554 mov r3
     (+ teq/tst/cmp-Treffer, keine Adressbildung)
```

Genau wie der Auftrag es vorwegnimmt: Basis und Schrittweite sind reine
MOV-Immediates und für die Bytesuche unsichtbar, das Magic steht im Pool und ist
für die Scalar-Suche unsichtbar. **Acht** Codestellen bilden Slot-Adressen, nicht
eine — `CL-STORAGE-REC-123` nennt nur 0x00265FE0/0x00265FE4.

### Die acht Stellen im Einzelnen

| # | Basis/Stride | bildet Adresse | ruft | Funktion |
|---|---|---|---|---|
| A | 0x25E2B0 / 0x25E360, 0x25E488 | über Rückruf | `bl 0x28A248` @0x25E37C, 0x25E49C | 0x0025E288 |
| B | 0x25F234 / 0x25F24C | über Rückruf | `bl 0x28A248` @0x25F264 | 0x0025F228 |
| C | 0x2625D0 / 0x2625E8 | über Rückruf | `bl 0x28A1D0` @0x2625EC | 0x0026200C |
| D | 0x265B70 / 0x265B6C | `mla r4,r6,r8,r7` @0x265B80 | `bl 0x232434`, `bl 0x28A248` | **0x00265B08** |
| E | 0x265FE4 / 0x265FE0 | `mla r0,r5,r7,r8` @0x265FF8 | `bl 0x232500` (Schreiben) | 0x00265EA8 |
| F | 0x26B060 / 0x26B058 | über Rückruf | `bl 0x28A3DC` @0x26B068 | (Prolog nicht gefunden) |
| G | 0x26B35C / 0x26B354 | über Rückruf | `bl 0x28A3DC` @0x26B364 | (Prolog nicht gefunden) |
| H | 0x26F54C / 0x26F554 | über Rückruf | `bl 0x28A248` @0x26F564 | 0x0026F40C |

### Was mit dem Magic geschieht — die drei Poolstellen

**0x0028A3D8, gelesen bei 0x0028A25C, in `FUN_0028A248` — Vergleich:**

```
0028a248: E92D4FFF stmdb sp!,{r0,r1,r2,r3,r4,...,lr}
0028a250: E59D405C ldr r4,[sp,#0x5c]      ; Anzahl (0x64)
0028a254: E59D6060 ldr r6,[sp,#0x60]      ; Rückruf = 0x0008A434
0028a258: E59D7058 ldr r7,[sp,#0x58]      ; Basis   = 0x28800000
0028a25c: E59FB174 ldr r11,[0x28a3d8]     ; Magic 0x2022
0028a270: E0207093 mla r0,r3,r0,r7        ; Adresse = Stride*Index + Basis
0028a28c: E3A02010 mov r2,#0x10
0028a290: E1A0100D mov r1,sp
0028a294: E12FFF36 blx r6                 ; Rückruf(Adresse, Puffer, 16)
0028a2a8: E59D0000 ldr r0,[sp,#0x0]
0028a2ac: E150000B cmp r0,r11             ; Kopfwort gegen Magic
0028a2b8: E1500004 cmp r0,r4              ; Feld[1] < Anzahl
0028a2c0: E1CD00D8 ldrd r0,r1,[sp,#0x8]   ; Feld[2..3], 64 Bit
```

**0x0028A538, gelesen bei 0x0028A4C0, in `FUN_0028A3DC` — Schreiben:**

```
0028a4c0: E59F0070 ldr r0,[0x28a538]      ; Magic 0x2022
0028a4c4: E8990006 ldmia r9,{r1,r2}       ; 64-Bit-Zähler
0028a4c8: E5850000 str r0,[r5,#0x0]       ; Kopf.magic = 0x2022   <-- Schreiben
0028a4cc: E5851008 str r1,[r5,#0x8]
0028a4d0: E585200C str r2,[r5,#0xc]
0028a4dc: E0207098 mla r0,r8,r0,r7        ; Zieladresse des Slots
```

Das ist die einzige Stelle im Bild, an der das Magic **geschrieben** wird.

**0x00265D4C, gelesen bei 0x00265B4C — Vergleich, im Exporter (unten).**

### Ein vierter Modus, den beide Suchen verfehlen

`FUN_0028A3DC` prüft das Magic zusätzlich **als Zwei-Befehl-Immediatkette**:

```
0028a3fc: E2421A02 sub r1,r2,#0x2000
0028a400: E2511022 subs r1,r1,#0x22       ; == 0x2022 ?
...
0028a46c: E2410A02 sub r0,r1,#0x2000
0028a470: E2500022 subs r0,r0,#0x22
```

Weder `search_scalars(0x2022)` noch die Bytesuche nach `22 20 00 00` findet
diese beiden Stellen. Sie sind als `set_comment` bei 0x0028A3FC vermerkt.

### Der Leser: 0x00265B08

`disassemble_at(0x00265b08, 22)` und eigener Dump 0x265B30-0x265D48:

```
00265b08: 34029FE5 ldr r0,[0x265d44]      ; 0x00000D00
00265b0c: 801190E5 ldr r1,[r0,#0x180]     ; -> 0x00000E80
00265b10: 840190E5 ldr r0,[r0,#0x184]     ; -> 0x00000E84
00265b14: 010090E1 orrs r0,r0,r1
00265b18: 1EFF2F01 bxeq lr                ; Torwächter: 64-Bit-Wert != 0
00265b1c: F04F2DE9 stmdb sp!,{r4,...,lr}
00265b20: 20A29FE5 ldr r10,[0x265d48]     ; 0x0004CFC0 = 0x4D000 - 0x40
00265b2c: 199BFEFA blx 0x0020c798         ; malloc(Slot ohne 64-Byte-Kopf)
00265b4c: F8B19FE5 ldr r11,[0x265d4c]     ; Magic 0x2022
00265b6c: E3A08A4D mov r8,#0x4d000
00265b70: E3A075A2 mov r7,#0x28800000
00265b80: E0247896 mla r4,r6,r8,r7        ; r6 = Slotindex 0..0x63
00265b98: E3A02010 mov r2,#0x10
00265b9c: E28D10A0 add r1,sp,#0xa0
00265ba0: EBFF3223 bl 0x00232434          ; Rohlesen(Adresse, Puffer, 16)
00265bac: 0150000B cmpeq r0,r11           ; Kopfwort == 0x2022 ?
00265bb8: E3500064 cmp r0,#0x64           ; Feld[1] < 100
00265be0: EBFF3213 bl 0x00232434          ; Rohlesen(Adresse, Puffer, r10)
00265cb0: EB009164 bl 0x0028a248          ; Slot-Scan mit Rückruf 0x0008A434
00265cc0: E28F208C adr r2,0x00265d54      ; "3:/%d-%s"
00265cdc: FAFE9BFE blx 0x0020ccdc         ; snprintf(sp+0x10, 0x80, "3:/%d-%s", ...)
00265ce0: E28F1078 adr r1,0x00265d60      ; "wb+"
00265ce8: FAFE9E85 blx 0x0020d704         ; fopen
00265d08: FAFEAEEE blx 0x002118c8         ; fwrite(buf, 1, r10, FILE)
00265d24: FAFE9E8D blx 0x0020d760         ; fclose
00265d28: E2866001 add r6,r6,#0x1
00265d2c: E3560064 cmp r6,#0x64
00265d30: BAFFFF89 blt 0x00265b5c         ; über alle 100 Slots
```

Die Zeichenketten dahinter, direkt aus der Datei gelesen:

```
0x00265D54: '3:/%d-%s'
0x00265D60: 'wb+'
```

### Das Rohlese-Primitiv 0x00232434

```
00232434: E92D47F0 stmdb sp!,{r4,...,lr}
00232438: E1A04000 mov r4,r0              ; Byteadresse auf der Karte
0023244c: E1A054A4 mov r5,r4,lsr #9       ; -> Sektornummer
0023247c: EBFFF42B bl 0x0022f530          ; Puffer holen
002324a0: EB018828 bl 0x00294548          ; SD-Sektoren lesen
002324b0: E044000A sub r0,r4,r10          ; Rest-Offset im Sektor
002324bc: E1A00008 mov r0,r8              ; memcpy in den Zielpuffer
```

Dieselbe Bauform wie `usb_lun_read_blocks`, nur ohne aufaddierte Fensterbasis:
`0x00232434` nimmt eine **absolute Rohbyteadresse auf der Karte**. Kein
Dateihandle, kein `3:/`.

### Die Geometrie — die Zielprobe

```
stride     = 315392 0x4d000
100*stride = 31539200 0x1e14000
store end  = 0x2a614000
LUN base   = 0x2a614000
equal: True
slot 99 range: 0x2a5c7000 - 0x2a614000
store size MiB: 30.078125
```

100 × 0x4D000 ab 0x28800000 endet **auf das Byte genau** an der LUN-Basis
0x2A614000.

### Die selbstlaufenden Kandidaten aus den Zeichenketten

Zeichenketten und ihre einzigen Codeverweise (ADR- und Poolsuche über die ganze
Datei):

```
'3:/obds/res/ZK-INKJET-RES-HW.zkml'  VA 0x0025D14C  adr @0x0025CFFC
'3:/obds/fonts/%s'                   VA 0x0025D17C  adr @0x0025D03C
'3:/obds/fonts/SYMBOL.TTF'           VA 0x0025D1AC  adr @0x0025D0AC
'0:/ZK-INKJET-RES-HW.zkml'           VA 0x0025D130  adr @0x0025CFF8
'3:\inkjet-lite-vadj-sample.csv'     VA 0x0026D578  adr @0x0026D4F0
'3:/%d-%s'                           VA 0x00265D54  adr @0x00265CC0
```

Der Ressourcen-/Fontlader beginnt bei 0x0025CFB8 und wird von 0x0025CF8C und
0x00263CB0 aus aufgerufen. Der csv-Pfad liegt in 0x0026D300, aufgerufen von
0x00263DA4; dort steht

```
0026d4f0: E28F0080 adr r0,0x0026d578      ; "3:\inkjet-lite-vadj-sample.csv"
0026d4f4: E28F109C adr r1,0x0026d598      ; "wb"
0026d4f8: FAFE8081 blx 0x0020d704         ; fopen
0026d518: E3A01001 mov r1,#0x1
0026d51c: E1A00005 mov r0,r5              ; fwrite
```

— also **Schreiben**, nicht Lesen.

### Warnung zu den vermeintlichen Zeigertabellen

Erste Suchen nach Aufrufern lieferten für sieben verschiedene Funktionsadressen
je ein „ausgerichtetes Poolwort" im Bereich 0x37C000-0x39A000. Dichteprüfung:

```
region 0x37C000-0x39A000: 30720 words, 23382 (76.1%) lie in 0x200000-0x2D0000,
  22960 distinct
aligned addresses in that span: 212992; coverage of distinct values: 10.8%
```

Der Rohinhalt zeigt, warum: ab 0x003997A0 stehen
`0x0028A198, 0x0028A1A0, 0x0028A1A8, 0x0028A1B8, 0x0028A1B0, …` — eine dichte,
fast monotone Folge mit Schrittweite 8, und um 0x00386FC0 eine mit Schrittweite
0x2BC. Eine solche Folge trifft in ihrem Abschnitt praktisch jede ausgerichtete
Adresse von allein. **Diese „Treffer" sind keine Referenzen.** Alle
Aufruferangaben unten stützen sich deshalb ausschließlich auf echte
`bl`/`blx`-Ziele.

## 2.2 Was das zeigt

- Der **Leser der Ablage ist gefunden**: `0x00265B08`. Er läuft über alle 100
  Slots, bildet die Adresse als `0x28800000 + Index × 0x4D000`, liest über das
  Rohprimitiv `0x00232434` erst 16 Kopfbytes, prüft das Magic 0x2022 und zwei
  Plausibilitätsfelder, liest bei einem Treffer den Slot ohne seinen 64-Byte-Kopf
  (0x4CFC0 Bytes) und schreibt ihn per `fopen("3:/%d-%s","wb+")` / `fwrite` /
  `fclose` als Datei auf das FAT16-Volume `3:/`.
- **Die Quelladresse ist eine berechnete Rohadresse auf der Karte**, kein
  Dateihandle. Dasselbe gilt für alle acht Adressbildungsstellen.
- **Richtung: Ablage → 3:/.** Das ist eine Brücke, aber die vom Gerät zum Host,
  nicht umgekehrt. Für die Fernsteuerung ist sie als Rückkanal interessant (ein
  Etikett aus der Ablage wird als Datei sichtbar, die der PC lesen kann), nicht
  als Eingang.
- **Zielprobe, negativ und exakt:** Die Ablage belegt
  [0x28800000, 0x2A614000) — 100 × 0x4D000 = 0x1E14000 = 30,08 MiB — und endet
  auf das Byte genau dort, wo die LUN-Basis beginnt. Slot 99 reicht bis
  0x2A614000 exklusive. Kein einziger Slot liegt bei oder oberhalb der LUN-Basis.
  Damit ist `CL-USB-REC-108` für **alle acht** Zugriffsstellen sauber verneint:
  über USB ist an die Ablage nicht heranzukommen, ohne die Fensterbasis zu
  verschieben. Die Zahlen bestätigen zugleich die Rechnung in `CL-USB-REC-119`:
  ein 64-MiB-Fenster ab 0x28800000 deckt die 30,08 MiB Ablage vollständig ab und
  reicht danach noch 34 MiB weit, also bis 0x2C800000 — über die alte
  MINI-Partition hinweg.
- **Was das Magic wo tut:** verglichen bei 0x00265B4C (Exporter) und 0x0028A25C
  (`FUN_0028A248`, generischer Slot-Scan), geschrieben ausschließlich bei
  0x0028A4C8 in `FUN_0028A3DC`, das den Kopf eines Datensatzes stempelt und
  danach dessen Zielslot adressiert. `FUN_0028A3DC` prüft es zusätzlich zweimal
  als Immediatkette (0x0028A3FC, 0x0028A46C), die keine der beiden im Auftrag
  geforderten Suchen findet.
- **Die Schnittstelle der Slot-Routinen ist gemessen:** `FUN_0028A248` nimmt
  `r3` = Schrittweite, `[sp+0x58]` = Basis, `[sp+0x5C]` = Anzahl (0x64),
  `[sp+0x60]` = Rückruf zum Rohlesen. Basis und Schrittweite sind also
  **Parameter**, keine fest verdrahteten Werte in der Scan-Routine selbst — an
  acht Aufrufstellen werden sie jeweils frisch als MOV-Immediate gesetzt. Ein
  Patch, der die Ablage verschieben wollte, müsste alle acht anfassen.
- **Die Font- und Ressourcenpfade sind keine Brücke.** `3:/obds/fonts/%s`,
  `3:/obds/res/ZK-INKJET-RES-HW.zkml` und `SYMBOL.TTF` werden von 0x0025CFB8
  gelesen; die Datei `inkjet-lite-vadj-sample.csv` wird **geschrieben**
  (`fopen(...,"wb")` bei 0x0026D4F8), nicht gelesen. Keiner dieser Pfade
  berührt die Ablage bei 0x28800000.

## 2.3 Was das nicht zeigt

- Es zeigt **nicht**, dass der Exporter 0x00265B08 ohne UI läuft. Es zeigt
  nicht einmal, wer ihn aufruft: in ganz APP.bin gibt es **kein** `bl`/`blx` auf
  0x00265B08, und die einzigen Wortvorkommen der Adresse liegen in dem
  Datenbereich, dessen Dichte oben nachgewiesen ist. Sein Torwächter — der
  64-Bit-Wert bei 0x00000E80 — liegt in demselben nicht gemappten Bereich unter
  0x00200000 wie 0x7D8; dieselbe Grenze wie in Aufgabe 1.
- Es zeigt **nicht**, was die 100 Slots im Einzelnen enthalten, und nicht, ob
  die exportierten `3:/<n>-<name>`-Dateien wieder eingelesen werden können. Ein
  Importpfad, der `3:/<n>-<name>` liest und in einen Slot schreibt, wurde nicht
  gesucht — der einzige gefundene Slot-Schreiber ist `FUN_0028A1D0` von
  0x002625EC aus, und `0x00265EA8` (Kopfsätze löschen) über `0x00232500`.
- Es zeigt **nicht** die Rangfolge, die der Auftrag verlangt. Für A (0x0025E288),
  F und G (0x0026B0xx) wurde kein direkter Aufrufer gefunden; für B (0x0025F228)
  führt `bl` von 0x0026A7FC, für H (0x0026F40C) von 0x0026F160, für C
  (0x0026200C) von 0x0025E558, für E (0x00265EA8) von 0x00262848 und 0x00266154.
  Die nächste Ebene darüber (0x0026A78C, 0x0026F0F8, 0x002637E4) hat wiederum
  keine auffindbaren direkten Aufrufer. Ob eine dieser Ketten ohne
  Menü-Navigation feuert, ist damit **nicht entschieden**.
- Es zeigt **nicht**, dass es nur acht Adressbildungsstellen gibt. Die
  Immediate-Suche erfasst `mov Rd,#0x28800000` und `mov Rd,#0x4D000`; eine Basis,
  die zur Laufzeit aus einer Konfiguration gelesen oder aus zwei Immediates
  zusammengesetzt wird, fiele durch. Für 0x4D000 wurden 19 Immediates gefunden,
  von denen zehn `teq/tst/cmp/and/sub` sind und offensichtlich keine
  Adressbildung — die wurden nicht einzeln geprüft.
- Es zeigt **nicht**, dass die Ablage genau 100 Slots hat. 0x64 ist an jeder
  Stelle ein Immediate; dass die Ablage exakt an der LUN-Basis endet, ist eine
  arithmetische Übereinstimmung, kein gelesenes Layoutfeld.

---

# Offen geblieben

1. **Wer schreibt `*(0x000007D8)`?** Stehengeblieben bei: die Adresse wird in
   APP.bin genau einmal materialisiert (Poolwort 0x00219884), in BOOT.bin gar
   nicht, und `read_words(0x7d8)` meldet den Bereich als nicht gemappt. Nächster
   Schritt: das Bild unterhalb 0x00200000 beschaffen und laden — es liefert
   0x0008A434, 0x0008A500, die Zeigertabelle 0x000D9934…0x000FB1EC und die
   Ressourcen ab 0x00128154. Kandidaten in
   `research/phase_a_sd_analysis/artifacts/`: `unknown_0x00100000_0x20000.bin`,
   `app_vol2_0x2402c000.bin`.
2. **Wer schreibt 65536 nach `PDISK_T+0x98`?** Stehengeblieben bei: in APP.bin
   niemand — alle 53 `str …,#0x98` sind aufgelistet, der einzige
   `PDISK_T`-Konstruktor speist aus `DISK_DATA_T.diskSize`, und der landet in
   `*(0x974+0x10)`. Offen bleibt, ob 65536 aus dem MBR am Fensterrand stammt
   (Start-LBA 63 + 131009 Sektoren = 131072 = 2 × 65536 — die Zahl passt exakt)
   oder ob der MBR aus einer festen 64-MiB-Vorgabe erzeugt wurde. Nächster
   Schritt: entweder das untere Bild analysieren, oder empirisch — eine
   Testkarte mit anderem MBR am Fensterrand bespielen und die vom Host
   gemeldete Kapazität ablesen. Das entscheidet die Frage in einem Versuch.
3. **Aufrufer des Exporters 0x00265B08.** Stehengeblieben bei: kein direktes
   Sprungziel, und die Wortvorkommen sind Zufall einer dichten Tabelle. Nächster
   Schritt: den 64-Bit-Torwächter bei 0x00000E80 verfolgen — dieselbe Adresse
   erscheint auch bei 0x002625C8 und gattert 0x0025E33C und 0x0025F270; wer ihn
   setzt, setzt vermutlich auch den Auslöser.
4. **Läuft irgendein Ablage-Leser ohne UI?** Stehengeblieben bei der zweiten
   Aufruferebene (0x0026A78C, 0x0026F0F8, 0x002637E4), die keine direkten
   Aufrufer mehr hat. Nächster Schritt: die Einstiegsfunktion von APP.bin ab
   Dateioffset 0 verfolgen, statt rückwärts zu suchen.
5. **Gibt es einen Importpfad `3:/…` → Slot?** Nicht gesucht. Nächster Schritt:
   Aufrufer von `FUN_0028A1D0` und `0x00232500` (Rohschreiben) prüfen, ob einer
   davon seine Daten aus `fread` bezieht.
6. **Ist `*(0x7D8)` wirklich ein `PDISK_T`?** Das Offset-Argument trägt, ein
   Symbol fehlt. Fällt mit Punkt 1.

---

# Umbenennungen in Ghidra

Keine `rename_function`. Vier `set_comment`, jeweils dort, wo ein
Herstellerheader oder eine Zeichenkette im Binary die Aussage trägt; der Zweifel
steht im Kommentar.

`list_mutations` (Rohausgabe):

```
summary: {"total": 4, "applied": 4, "proposed": 0, "by_kind": {"comment": 4}}

0x00219868  comment   ? -> +0x98 == PDISK_T.uDiskSize (disk size in KiB) per vendor/N32…(+645)  (decompiler)
0x0025164C  comment   ? -> PDISK_T constructor, byte-for-byte the BSP's SDCARD_Open tai…(+613)  (decompiler)
0x0028A3FC  comment   ? -> Magic 0x2022 compared as a two-instruction immediate chain (…(+524)  (decompiler)
0x00265B08  comment   ? -> Document-store EXPORTER (probe B2, 2026-08-31). Gate: return…(+841)  (decompiler)
```

Nicht gespeichert (`save_program` nicht aufgerufen) — die Kommentare stehen im
Sitzungszustand des Servers.

# Methodische Nachträge

- **Ghidras `disassemble_at` springt still weiter.** Anfragen auf 0x002818A0,
  0x0023DF40, 0x002AEDE4 und 0x002AF1A8 lieferten Disassemblat ab 0x00286D94,
  0x0023FFD0 bzw. 0x002AF7C8 — die angefragten Adressen liegen in Bereichen, die
  im Ghidra-Programm nicht als Code definiert sind, und das Werkzeug meldet das
  nicht. Die Lücken sind erheblich größer als die dokumentierte Blindstelle
  `CL-TOOL-REC-117`: zwischen 0x002AEC64 und 0x002AF7C4 liegen rund 2,7 KiB,
  zwischen 0x002818B0 und 0x00286D90 rund 21 KiB. Alle Befunde dieses Berichts
  aus diesen Bereichen stammen aus einem eigenen Decoder über die Rohdatei.
- **`search_xrefs_to` kann falsch positiv sein.** 17 der 18 gemeldeten
  Referenzen auf 0x7D8 waren `[rN,#0x7d8]`-Feldzugriffe auf fremden Basen.
  Ein `total: 18` ist hier keine Bestätigung, sondern eine Falle.
- Der eigene ARM-Decoder hatte anfangs zwei Fehler, die beide auffielen und
  behoben wurden: MUL/MLA wurden verwechselt (Maske 0x0FC000F0 statt
  0x0FE000F0) — dadurch las sich `mla r4,r6,r8,r7` bei 0x00265B80 zunächst als
  `mul r4,r6,r8` und die Basis 0x28800000 schien unbenutzt; und die
  Extra-Load/Store-Klasse (LDRD/STRD) fehlt bis jetzt, weshalb 0x00265C48 und
  0x0028A2C0 als `bic` erscheinen statt als `ldrd r0,r1,[sp,#0xA8]` bzw.
  `ldrd r0,r1,[sp,#0x8]`. Die im Bericht zitierten Zeilen aus diesen Stellen
  sind von Hand nachdekodiert.
