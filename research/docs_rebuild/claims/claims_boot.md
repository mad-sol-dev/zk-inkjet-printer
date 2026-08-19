# BOOT Claims

Propositional claims synthesized from evidence. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## Boot Sequence

### ⚠️ CL-BOOT-001: SD Card Required for Boot
**Claim:** The device does not boot without the SD card installed.

**Evidence:**
- E-BOOT-002: States the device does not boot without the SD card.

**Status:** ⚠️ Supported (single direct observation)

**Cross-Reference:** CL-STORAGE-004 (IBR boot process), CL-SOC-012 (boot options supported)

**Next Tests:** Power-cycle the device with the SD card removed and confirm no boot progress or display activity.

---

### ⚠️ CL-BOOT-002: Three-Stage Boot Chain via IBR and BOOT.bin
**Claim:** The boot chain proceeds from IBR (internal Boot ROM) to BOOT.bin, which initializes the system and then loads APP.bin into RAM.

**Evidence:**
- E-BOOT-003: IBR size is 16 KB and internal SRAM is 8 KB.
- E-BOOT-005: IBR loads BOOT.bin from offset 0x200.
- E-BOOT-006: BOOT.bin initializes the system.
- E-BOOT-007: BOOT.bin loads APP.bin.
- E-BOOT-012: APP.bin is copied to 0x03000000 in RAM.

**Status:** ⚠️ Supported (chain assembled from multiple evidence entries in one session)

**Cross-Reference:** CL-STORAGE-004 (IBR standard boot process), CL-SOC-012 (boot options)

**Next Tests:** Disassemble BOOT.bin in Ghidra and confirm the load-and-jump sequence for APP.bin with RAM destination 0x03000000.

---

### ⚠️ CL-BOOT-003: Stage-1 and Stage-2 Loaders with ZBW Signature
**Claim:** The SD card boot area includes a Stage-1 loader with the ZBWp1WBZ signature followed by a larger Stage-2 loader.

**Evidence:**
- E-BOOT-001: Describes a Stage-1 loader with ZBWp1WBZ signature followed by Stage-2 loader.
- E-BOOT-010: BOOT.bin at offset 0x200 includes ZBWp1WBZ signature.

**Status:** ⚠️ Supported (two aligned observations)

**Cross-Reference:** E-STORAGE-003 (ZBW signature at 0x200), E-STORAGE-029 (BOOT.bin size at 0x200)

**Next Tests:** Verify the ZBWp1WBZ signature in a raw SD dump at 0x200 and locate the subsequent Stage-2 loader region.

---

### 🔬 CL-BOOT-004: BOOT.bin Can Load APP.bin from FAT
**Claim:** After BOOT.bin starts, it can mount a FAT filesystem and load APP.bin by pathname rather than fixed offsets.

**Evidence:**
- E-BOOT-008: Notes BOOT.bin can mount a filesystem and load APP.bin from FAT.

**Status:** 🔬 Hypothesis (single analytical statement)

**Cross-Reference:** CL-STORAGE-004 (IBR boot process), CL-SOC-012 (boot options)

**Next Tests:** Trace BOOT.bin file I/O calls in Ghidra to confirm FatFS mount and f_open/f_read usage.

---

### ⚠️ CL-BOOT-005: Multiple Boot Media Are Supported by SoC
**Claim:** The SoC boot ROM supports booting from SD, raw NAND, SPI flash, and USB.

**Evidence:**
- E-BOOT-004: Lists supported boot modes (SD, NAND, SPI, USB).

**Status:** ⚠️ Supported (single documented list)

**Cross-Reference:** CL-SOC-012 (multiple boot options supported)

**Next Tests:** Check the Nuvoton boot-mode selection table and correlate with board strap configuration.

---

## Memory Map & Load Addresses

### ⚠️ CL-BOOT-006: BOOT.bin Stored at SD Offset 0x200 with ZBW Signature
**Claim:** BOOT.bin is stored at SD card offset 0x200 (sector 1) and includes the ZBWp1WBZ boot signature.

**Evidence:**
- E-BOOT-010: BOOT.bin at offset 0x200 with ZBWp1WBZ signature.
- E-BOOT-026: BOOT.bin size is ~12.7 KB with ARM instructions.

**Status:** ⚠️ Supported (two observations, no artifact validation in this claim set)

**Cross-Reference:** E-STORAGE-003 (ZBW signature at 0x200), E-STORAGE-029 (BOOT.bin size at 0x200)

**Next Tests:** Hex-dump the SD image at 0x200 to confirm the signature and exact BOOT.bin length.

---

### ⚠️ CL-BOOT-007: APP.bin Stored at SD Offset 0x100000 with ARM IVT
**Claim:** APP.bin appears in the SD image at offset 0x100000 and contains an ARM interrupt vector table.

**Evidence:**
- E-BOOT-011: APP.bin found at 0x100000 with ARM IVT.
- E-BOOT-028: APP.bin is approximately 2.6 MB.

**Status:** ⚠️ Supported (single session evidence with corroborating size)

**Cross-Reference:** CL-STORAGE-004 (IBR standard boot process)

**Next Tests:** Verify the IVT signature by disassembling the first 0x40 bytes at 0x100000 in the SD image.

---

### ⚠️ CL-BOOT-008: APP.bin Loads to RAM Address 0x03000000
**Claim:** The application image is copied into DDR SDRAM at address 0x03000000 during boot.

**Evidence:**
- E-BOOT-012: APP.bin is copied to 0x03000000 in RAM.

**Status:** ⚠️ Supported (single direct statement)

**Cross-Reference:** CL-SOC-012 (boot options supported)

**Next Tests:** Identify the memcpy or load routine in BOOT.bin that writes to 0x03000000 and confirm control transfer.

---

### ⚠️ CL-BOOT-009: SDLoader and Execute Image Sector Ranges
**Claim:** The SDLoader occupies sectors 1–33 and the execute image area begins at sector 544 in the TurboWriter map.

**Evidence:**
- E-BOOT-013: SDLoader sector range is 1–33.
- E-BOOT-014: Execute image starts at sector 544.

**Status:** ⚠️ Supported (artifact-based notes from TurboWriter map)

**Cross-Reference:** CL-STORAGE-004 (IBR standard boot process)

**Next Tests:** Compare a TurboWriter-generated SD image to confirm the sector placement of SDLoader and execute image blocks.

---

### ⚠️ CL-BOOT-010: FAT "MINI" Filesystem Starts Near 711 MB and No Partition Table Exists
**Claim:** The SD card lacks a partition table and the FAT-like "MINI" filesystem appears around a 711 MB offset.

**Evidence:**
- E-BOOT-015: FAT-like "MINI" appears at 711 MB offset.
- E-BOOT-016: SD card has no partition table.

**Status:** ⚠️ Supported (two observations in the same session)

**Cross-Reference:** CL-STORAGE-004 (raw SD layout)

**Next Tests:** Scan the SD image for FAT boot-sector signatures at ~711 MB and confirm the absence of MBR/GPT headers.

---

## Firmware Update Mechanism

### ⚠️ CL-BOOT-011: Firmware Scans 3:/ for Update Files
**Claim:** The firmware update logic scans the 3:/ volume for update binaries and stages them into internal storage.

**Evidence:**
- E-BOOT-019: Firmware scans 3:/ for updates.
- E-BOOT-020: Update workflow is MINI to internal.
- E-BOOT-021: User copies update .bin files to MINI (0:/).

**Status:** ⚠️ Supported (workflow described but not independently verified)

**Cross-Reference:** CL-STORAGE-004 (raw SD layout), CL-SOC-012 (boot options supported)

**Next Tests:** Identify update-handler functions in APP.bin and verify their path strings and destination writes.

---

### ⚠️ CL-BOOT-012: Updater Uses FatFS File Reads
**Claim:** The update process uses FatFS file APIs (f_open/f_read) rather than raw-sector reads.

**Evidence:**
- E-BOOT-024: Updater reads via FatFS f_open/f_read with no raw offsets.

**Status:** ⚠️ Supported (single analytical summary)

**Cross-Reference:** CL-STORAGE-004 (FAT layout on SD)

**Next Tests:** Trace disk I/O calls in the update routine to confirm FatFS APIs and absence of direct sector access.

---

### ⚠️ CL-BOOT-013: TurboWriter Builds Bootable SD Images from .bin Files
**Claim:** TurboWriter takes .bin files and generates a bootable SD image with the required headers.

**Evidence:**
- E-BOOT-022: TurboWriter takes .bin files.
- E-BOOT-023: TurboWriter creates a bootable SD image with correct headers.

**Status:** ⚠️ Supported (single-session workflow statement)

**Cross-Reference:** CL-STORAGE-004 (IBR standard boot process)

**Next Tests:** Run TurboWriter with known BOOT/APP binaries and compare the resulting image headers against the SD dump.

---

### 🔬 CL-BOOT-014: APP.bin Offset Differs from TurboWriter Default
**Claim:** The observed APP.bin placement at 0x100000 suggests a custom SD layout compared to TurboWriter’s default execute-image start at sector 544 (0x44000).

**Evidence:**
- E-BOOT-011: APP.bin at offset 0x100000.
- E-BOOT-025: TurboWriter default execute start is sector 544, not 0x100000.

**Status:** 🔬 Hypothesis (inference from two observations)

**Cross-Reference:** CL-STORAGE-004 (raw SD layout)

**Next Tests:** Generate a TurboWriter SD image and compare APP.bin offsets to the device’s SD image to quantify the layout delta.

---

## Binary Structure

### ⚠️ CL-BOOT-015: BOOT.bin is a Small ARM Loader
**Claim:** BOOT.bin is a ~12.7 KB, low-entropy ARM binary with few ASCII strings, consistent with a compact loader role.

**Evidence:**
- E-BOOT-026: BOOT.bin size and low-entropy ARM content.
- E-BOOT-027: BOOT.bin likely acts as a stage-2 loader copying APP and GUI resources.

**Status:** ⚠️ Supported (observation plus interpretation)

**Cross-Reference:** CL-STORAGE-004 (BOOT.bin location at 0x200)

**Next Tests:** Disassemble BOOT.bin and confirm minimal string table and loader-style control flow.

---

### ⚠️ CL-BOOT-016: APP.bin is a Proprietary Resource Container Loaded into RAM
**Claim:** APP.bin is a ~2.6 MB proprietary resource container that the bootloader loads into RAM.

**Evidence:**
- E-BOOT-028: APP.bin is about 2.6 MB and contains mixed binary/string content.
- E-BOOT-029: APP.bin is a proprietary resource container loaded into RAM by the bootloader.

**Status:** ⚠️ Supported (observation plus interpretation)

**Cross-Reference:** CL-STORAGE-004 (raw SD layout)

**Next Tests:** Locate and parse container headers in APP.bin to confirm structure and load routines.
