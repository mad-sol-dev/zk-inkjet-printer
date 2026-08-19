# BOOT Evidence

Raw facts extracted from chat transcripts. No interpretation, only concrete observations.

---

## Boot Sequence

### E-BOOT-001: Stage-1 and Stage-2 Loader Signature
- **Quote:** "Am Anfang befindet sich ein Stage‑1‑Bootloader (Signatur „ZBWp1WBZ"), gefolgt von einem größeren Stage‑2‑Loader"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=10
- **Date:** 2025-12-14
- **Type:** OBSERVATION
- **Tags:** stage-1, stage-2, ZBWp1WBZ, sd-card

### E-BOOT-002: SD Card Required to Boot
- **Quote:** "The device does not boot without the SD card."
- **Source:** Chats/842_GPT_Dateizugriff_klären_11.10.2025.json#msg=11
- **Date:** 2025-10-11
- **Type:** OBSERVATION
- **Tags:** sd-card, boot-required, boot-medium

### E-BOOT-003: Internal SRAM and IBR Sizes
- **Quote:** "Zusätzlich verfügen alle Chips über einen internen Speicher von:\n* **8 KB SRAM**\n* **16 KB IBR (Internal Booting ROM)**"
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=1
- **Date:** 2025-12-29
- **Type:** OBSERVATION
- **Tags:** sram, ibr, boot-rom, memory

### E-BOOT-004: Supported Boot Modes
- **Quote:** "Die Chips unterstützen verschiedene Boot-Modi direkt beim Start:\n* Speicherkarten (SD, SD-to-NAND Flash Bridge)\n* Raw NAND Flash\n* SPI Flash\n* USB"
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=1
- **Date:** 2025-12-29
- **Type:** OBSERVATION
- **Tags:** boot-modes, sd, nand, spi, usb

### E-BOOT-005: IBR Loads BOOT.bin at 0x200
- **Quote:** "1. IBR (Internal Boot ROM) lädt BOOT.bin von Offset 0x200"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=68
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** ibr, boot.bin, 0x200, load

### E-BOOT-006: BOOT.bin Initializes the System
- **Quote:** "2. BOOT.bin führt aus, initialisiert System"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=68
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** boot.bin, init, boot-sequence

### E-BOOT-007: BOOT.bin Loads APP.bin
- **Quote:** "3. BOOT.bin muss dann APP.bin laden"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=68
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** boot.bin, app.bin, chainload

### E-BOOT-008: BOOT.bin Can Load APP.bin from FAT
- **Quote:** "Der User hat recht - sobald BOOT.bin läuft, kann es das Filesystem mounten und APP.bin von ÜBERALL laden (solange es im FAT ist oder über einen custom mount-point erreichbar ist)."
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=68
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** fat, app.bin, boot.bin, filesystem

### E-BOOT-009: IBR Loads SD Loader from Start of Card
- **Quote:** "1. **Boot-Code am Anfang** - IBR (16KB internes ROM) lädt SD-Loader vom Anfang der Karte"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=10
- **Date:** 2025-12-14
- **Type:** OBSERVATION
- **Tags:** ibr, sd-loader, boot-code, sd-card

---

## Memory Map & Load Addresses

### E-BOOT-010: BOOT.bin Offset and Signature
- **Quote:** "1. **Offset 0x200 (Sector 1)**: NANO-BOOT.bin (12,736 bytes) mit \"ZBWp1WBZ\" signature"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=66
- **Date:** 2025-12-14
- **Type:** OBSERVATION
- **Tags:** boot.bin, 0x200, sector-1, ZBWp1WBZ

### E-BOOT-011: APP.bin Offset in Image
- **Quote:** "2. **Offset 0x100000 (1 MiB)**: NANO-APP.bin (2,576,940 bytes) mit ARM IVT"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=66
- **Date:** 2025-12-14
- **Type:** OBSERVATION
- **Tags:** app.bin, 0x100000, arm-ivt, offset

### E-BOOT-012: APP.bin Load Address
- **Quote:** "- APP.bin wird zu 0x03000000 im RAM kopiert"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=68
- **Date:** 2025-12-14
- **Type:** OBSERVATION
- **Tags:** app.bin, load-address, 0x03000000, ram

### E-BOOT-013: SDLoader Sector Range
- **Quote:** "Sector 1-33:      System Image (SDLoader)"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=66
- **Date:** 2025-12-14
- **Type:** ARTIFACT
- **Tags:** sdloader, sector-map, system-image

### E-BOOT-014: Execute Image Start Sector
- **Quote:** "Sector 544+:      Execute Image (NvtLoader)"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=66
- **Date:** 2025-12-14
- **Type:** ARTIFACT
- **Tags:** nvtloader, execute-image, sector-map

### E-BOOT-015: FAT Filesystem Starts at 711 MB
- **Quote:** "2. **Ab Offset 711 MB** kommt das FAT \"MINI\" (das ist Volume 3!)"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=10
- **Date:** 2025-12-14
- **Type:** OBSERVATION
- **Tags:** fat, mini, offset, sd-card

### E-BOOT-016: SD Card Has No Partition Table
- **Quote:** "3. **Keine Partitionstabelle** - alles hardcodiert"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=10
- **Date:** 2025-12-14
- **Type:** OBSERVATION
- **Tags:** sd-card, partition-table, boot-medium

### E-BOOT-017: Volume 0 Size Limit
- **Quote:** "2. Drive 0: 0x100000 Sektoren = 512 MB"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=70
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** volume-0, size, 0x100000, sectors

### E-BOOT-018: Volume 3 Size Limit
- **Quote:** "3. Drive 3: 0x20000 Sektoren = 64 MB"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=70
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** volume-3, size, 0x20000, sectors

---

## Firmware Update Mechanism

### E-BOOT-019: Firmware Scans 3:/ for Updates
- **Quote:** "- Finding-0020: Firmware scannt `3:/` für Updates"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=60
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** update, scan, volume-3, firmware

### E-BOOT-020: Update Workflow MINI to Internal
- **Quote:** "- Finding-0013: Update-Workflow MINI → Internal"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=60
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** update, mini, internal, workflow

### E-BOOT-021: User Copies Update Binaries to MINI
- **Quote:** "User kopiert *.bin zu MINI (0:/)"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=60
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** update, mini, copy, binaries

### E-BOOT-022: TurboWriter Uses .bin Files
- **Quote:** "   - TurboWriter nimmt unsere .bin Files"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=62
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** turbowriter, update, bin-files

### E-BOOT-023: TurboWriter Builds Bootable SD Image
- **Quote:** "   - Erstellt ein bootfähiges SD-Image mit korrekten Headers"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=62
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** turbowriter, sd-image, headers, update

### E-BOOT-024: Updater Uses FatFS File Reads
- **Quote:** "5. Der Updater liest via FatFS f_open/f_read - KEINE Raw-Offsets"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=70
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** update, fatfs, f_open, f_read

### E-BOOT-025: TurboWriter vs Found APP.bin Offset
- **Quote:** "TurboWriter würde NANO-APP.bin zu Sector 544 schreiben, ABER wir finden es bei 0x100000!"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=66
- **Date:** 2025-12-14
- **Type:** ANALYSIS
- **Tags:** turbowriter, app.bin, offset, update

---

## Binary Structure

### E-BOOT-026: BOOT.bin Characteristics
- **Quote:** "**ZK-INKJET-NANO-BOOT.bin (~12.7 KB)**: Low entropy (~5.8 bit/byte), almost exclusively ARM instructions with hardly any ASCII strings."
- **Source:** Chats/842_GPT_Dateizugriff_klären_11.10.2025.json#msg=11
- **Date:** 2025-10-11
- **Type:** OBSERVATION
- **Tags:** boot.bin, size, entropy, arm

### E-BOOT-027: BOOT.bin Role as Stage-2 Loader
- **Quote:** "Likely the stage-2 bootloader that copies the APP module and GUI resources into RAM."
- **Source:** Chats/842_GPT_Dateizugriff_klären_11.10.2025.json#msg=11
- **Date:** 2025-10-11
- **Type:** ANALYSIS
- **Tags:** bootloader, stage-2, app.bin, gui

### E-BOOT-028: APP.bin Size and Composition
- **Quote:** "**Structure**: Approximately 2.6 MB, a mix of binary payloads and human-readable strings."
- **Source:** Chats/842_GPT_Dateizugriff_klären_11.10.2025.json#msg=11
- **Date:** 2025-10-11
- **Type:** OBSERVATION
- **Tags:** app.bin, size, structure, strings

### E-BOOT-029: APP.bin as Resource Container
- **Quote:** "Conclusion: `APP.bin` is a proprietary resource container loaded into RAM by the bootloader."
- **Source:** Chats/842_GPT_Dateizugriff_klären_11.10.2025.json#msg=11
- **Date:** 2025-10-11
- **Type:** ANALYSIS
- **Tags:** app.bin, resource-container, bootloader, ram
