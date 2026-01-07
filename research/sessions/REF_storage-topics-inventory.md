# Storage/Memory Themen - Fakten vs. Spekulationen

**Stand:** 2025-12-15, 21:00 UTC  
**Zweck:** Systematische Bestandsaufnahme vor Konsolidierung

---

## 🔵 VERIFIZIERTE FAKTEN (confidence 1.0)

### Hardware

✅ **Ein einzige physische SD-Karte**
- Quelle: Finding-0023, Session Log
- Evidenz: N9H26 hat keinen internen Flash
- Ohne SD-Karte: IBR USB Boot Mode (tot)

✅ **Reserved Area (Sektor 0-2047)**
- BOOT.bin @ Offset 0x200 (Sektor 1), 12,736 bytes
- APP.bin @ Offset 0x100000 (Sektor 2048), 2,576,940 bytes
- Quelle: Image Analysis, TestDisk, Finding-0023

✅ **RAW Write Chain**
```
FUN_0006887c → FUN_0006ccf8 → FUN_00032500 → FUN_00094584
```
- FUN_00094584: Direct SD controller MMIO (0xb0000000)
- FUN_00032500: Sector alignment wrapper (byte → LBA)
- Call Sites: 0x6d0f4 (BOOT), 0x6d184 (APP)
- Quelle: Codex Analysis, Finding-0023

✅ **Keine Checksums / Minimale Validierung**
- FUN_0006ccf8 prüft nur: bytes_read == file_size
- KEIN CRC, KEIN Hash, KEINE Signatur
- Quelle: Finding-0021, Finding-0023

✅ **MMU/RAM Configuration**
- TTBR @ 0x00004000, Identity-Mapping 0-2GB
- APP.bin loaded to 0x03000000 (48 MB)
- Quelle: Finding-0021

---

## 🟡 VERMUTLICH KORREKT (confidence 0.7-0.9)

### Partitionen & Volumes

🟡 **Multiple FAT Partitions auf einer SD-Karte**
- "0:/" und "3:/" sind FAT Partitionen auf DERSELBEN Karte
- Quelle: Finding-0020, Finding-0023, Code Strings
- **ABER:** Widersprüche in den Details!

🟡 **About Screen Memory (0.8/3.8 GB)**
- Finding-0020 erwähnt dies
- **OFFEN:** Woher kommen diese Zahlen?
- **OFFEN:** Bezieht sich das auf Partitionsgrößen?

🟡 **APP.bin Size Limit**
- Theoretisch: ~16 MB (RAM-basiert, Finding-0021)
- Praktisch: Unklar ob Storage-Limit existiert
- Current: 2.6 MB (viel Headroom)

---

## ❌ WIDERSPRÜCHLICH / UNKLAR

### Volume-Zuordnung - KRITISCHES PROBLEM! ⚠️

Es gibt **3 verschiedene Aussagen** über die Volumes:

**Quelle 1: Finding-0020 (2025-12-02)**
```
0:/ = working/internal mount point
3:/ = source volume (firmware/UI)
```

**Quelle 2: Finding-0023 + Session Log (2025-12-15)**
```
0:/ = System/Working partition
3:/ = User/Update partition
```

**Quelle 3: ZK_TEST_README.md**
```
Volume 3:/ = Firmware (~256 MB) mit BOOT/APP/UI
Volume 0:/ = MINI (64 MB) = USB MSC export
```

**FRAGE:** Welche ist korrekt?

---

### Staging Area Workflow - WIDERSPRUCH!

**Finding-0020 sagt:**
```
3:/ → 0:/ Copy
"3:/ ist source, 0:/ ist working"
```

**Finding-0023 sagt:**
```
3:/ → 0:/ Copy
"3:/ ist user/update, 0:/ ist system staging"
```

**Session Log erklärt:**
```
Staging Area = Partition Isolation
- 3:/ = User-accessible (kann geändert werden)
- 0:/ = Firmware-controlled (safe)
```

**ABER:** ZK_TEST_README sagt:
```
Volume 3:/ enthält die Firmware-Files!
Volume 0:/ ist USB-MSC (MINI)!
```

**FRAGE:** Wo liegen die Firmware-Files WIRKLICH?

---

## 🔴 SPEKULATION / UNBESTÄTIGT

❓ **RAM Size: 64 MB vs 8 MB**
- About Screen: "8 MB"
- Finding-0021 Analysis: ">48 MB" nötig für APP @ 0x03000000
- **OFFEN:** Tatsächliche DDR-Größe?

❓ **USB MSC Volume Export**
- Finding-0020: "USB MSC volume selection not yet resolved"
- ZK_TEST_README: "Volume 0:/ (MINI) ist USB-MSC"
- **OFFEN:** Welches Volume wird via USB exportiert?

❓ **Partition Sizes**
- ZK_TEST_README: "Volume 3:/ ~256MB, Volume 0:/ 64MB"
- About Screen: "0.8/3.8 GB"
- **OFFEN:** Tatsächliche Partition-Größen?

❓ **Volumes 1:/ und 2:/**
- Finding-0020: "No 1:/ or 2:/ usage found"
- **OFFEN:** Existieren diese Partitions? Wofür?

---

## 📋 OFFENE FRAGEN (Finding-0020 next_steps)

1. ❓ Mount table/volume array bei FUN_0005ebb8
2. ❓ About-screen Usage Calculation (0.8/3.8GB)
3. ❓ USB MSC Setup - welches Volume wird exportiert?
4. ❓ Warum Indices 0 und 3? Wo sind 1 und 2?
5. ❓ Hardcoded sector offsets/volume structures

---

## 🔧 KONKRETE DISKREPANZEN

### Issue 1: Volume Content Assignment

**Widersprechende Aussagen über "wo liegen die Firmware-Files":**

A) **Auf 3:/ (Finding-0020, Finding-0023)**
   - Code referenziert "3:/ZK-INKJET-NANO-*.bin"
   - Update-Flow: User kopiert zu 3:/

B) **Auf 3:/ ODER 0:/? (ZK_TEST_README)**
   - "Volume 3:/ (Firmware)" - klingt nach primärem Speicher
   - Aber Update-Flow: 3:/ → 0:/ → RAW

**FRAGE AN MARTIN:** 
- Wenn User Files per USB-MSC kopiert, auf welches Volume?
- Welches Volume sieht man als "MINI" am Computer?
- Wo liegen Fonts/Resources vs. Firmware-Files?

---

### Issue 2: Staging Direction Confusion

**Finding-0023 sagt: "3:/ → 0:/ ist staging"**
- User kopiert zu 3:/
- Firmware kopiert zu 0:/ (staging)
- RAW write aus 0:/

**ABER:** Wenn 0:/ = USB-MSC (MINI), wie passt das?
- User würde zu 0:/ (MINI) kopieren
- Firmware findet Files auf 0:/
- Kopiert zu... 3:/? Oder direkt RAW?

---

### Issue 3: About Screen vs. Code

**Finding-0020:** "About screen 0.8/3.8GB"

**Mögliche Interpretationen:**
A) 0.8 GB used / 3.8 GB free auf einer Partition?
B) Partition 0:/ = 0.8 GB, Partition 3:/ = 3.8 GB?
C) Komplett andere Bedeutung?

---

## 📊 VORSCHLAG FÜR KONSOLIDIERUNG

### Phase 1: Klärung der Basics

**Zu beantworten:**
1. Welches Volume ist USB-MSC "MINI"? (0:/ oder 3:/)
2. Wo liegen Firmware-Files beim Shipping? (0:/ oder 3:/)
3. Was bedeutet "0.8/3.8 GB"?
4. Gibt es Partitions 1:/ und 2:/? (TestDisk Ergebnis?)

### Phase 2: Update-Flow verifizieren

**Zu testen:**
1. USB-MSC mounten → welches Volume?
2. Files kopieren → wo landen sie? (0:/ oder 3:/)
3. About Screen → was zeigt es an?

### Phase 3: Findings konsolidieren

**Nach Klärung:**
- Finding-0020 updaten (Volume-Zuordnung klären)
- Finding-0023 korrigieren falls nötig
- ZK_TEST_README.md updaten

---

## 💡 VERMUTUNG (zu prüfen)

**Hypothese:** Volume-Indices sind verwir

rend

**Mögliche Realität:**
```
SD Card Layout:
├─ Sector 0-2047:        Reserved Area (RAW)
│  ├─ Sector 1:          BOOT.bin @ 0x200
│  └─ Sector 2048:       APP.bin @ 0x100000
├─ Partition 1 @ 2048+:  "0:/" System (Fonts/Resources)
└─ Partition 2 @ X+:     "3:/" User (USB-MSC "MINI")
```

**Update Flow wäre dann:**
1. User kopiert zu 3:/ (USB-MSC)
2. Firmware kopiert 3:/ → 0:/ (staging)
3. RAW write aus 0:/ zu Reserved Area

**ABER:** Das widerspricht ZK_TEST_README!

---

## ⚡ NÄCHSTE SCHRITTE

**Jetzt sofort (mit User):**
1. Klären: Welches Volume ist USB-MSC?
2. Klären: Wo liegen Firmware-Files standardmäßig?
3. Klären: Was ist 0.8/3.8 GB?

**Nach Klärung:**
1. Finding-0020 komplett rewrite
2. Finding-0023 korrigieren
3. ZK_TEST_README.md aktualisieren
4. Session Log nachtragen

**Später:**
1. FUN_0005ebb8 analysieren (mount table)
2. About Screen Handler finden
3. USB MSC Setup Code analysieren

---

**Ende der Bestandsaufnahme**
