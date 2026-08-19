# STORAGE Claims

Propositional claims synthesized from evidence. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## SD Card Physical Layout

### ✅ CL-STORAGE-001: No Partition Table (Raw Layout)
**Claim:** The SD card uses a raw, non-partitioned layout without MBR or GPT partition tables. All filesystems and boot structures are placed at fixed raw offsets.

**Evidence:**
- E-STORAGE-001: User explicitly states "alles ist raw auf der SD-Karte" (MBR/partition tables discussed many times)
- E-STORAGE-006: Documentation confirms "keine klassische Partitionstabelle besitzt"

**Status:** ✅ Verified (multiple E1 sources, user confirmation)

**Next Tests:** None required - well established

---

### ✅ CL-STORAGE-002: SD Card Capacity is 4GB
**Claim:** The device uses a 4GB SD card (3.75 GiB actual capacity = 4,026,531,840 bytes).

**Evidence:**
- E-STORAGE-002: Image analysis shows 4026531840 bytes = 3.75 GB

**Status:** ✅ Verified (E0 artifact - sdcard.workout.img)

**Next Tests:** None required - measured from image

---

### ✅ CL-STORAGE-003: Boot Signature at Offset 0x200
**Claim:** Boot loader signature "ZBW" magic bytes (A5 5A 42 57 ... 57 42 5A A5) appear at offset 0x200 on the SD card.

**Evidence:**
- E-STORAGE-003: Hex dump shows "+00000200: A5 5A 42 57 00 00 70 00 00 31 00 00 57 42 5A A5"
- E-STORAGE-004: Documentation references "Signatur ZBWp1WBZ"

**Status:** ✅ Verified (hex dump confirmed)

**Next Tests:** None required - directly observable in image

---

## Boot Process

### ⚠️ CL-STORAGE-004: Nuvoton IBR Standard Boot Process
**Claim:** The boot process follows Nuvoton's standard IBR (Internal Boot ROM) mechanism. IBR loads NANO-BOOT.bin from offset 0x200, which then initializes the system and loads NANO-APP.bin.

**Evidence:**
- E-STORAGE-031: "IBR lädt BOOT.bin von Offset 0x200, BOOT.bin initialisiert System, dann muss BOOT.bin APP.bin laden"
- E-STORAGE-032: "SD-Karte Image Layout ist Nuvoton-Standard IBR Boot-Prozess - nicht ZK-Inkjet spezifisch"
- E-STORAGE-029: TestDisk shows NANO-BOOT.bin at 0x200, size 12,736 bytes

**Status:** ⚠️ Supported (consistent E1 evidence, vendor documentation expected)

**Next Tests:**
- Verify against N3290x Design Guide IBR chapter
- Analyze NANO-BOOT.bin binary for IBR compliance

---

### ⚠️ CL-STORAGE-005: SD Card Required for Boot
**Claim:** The device cannot boot without the SD card inserted - the SD card serves as the primary boot medium.

**Evidence:**
- E-STORAGE-007: "Ohne SD‑Karte startet das Gerät nicht. SD‑Karte als Bootmedium"

**Status:** ⚠️ Supported (E2 doc-ref, needs empirical test)

**Next Tests:**
- Test device boot behavior with SD card removed
- Confirm no alternative boot path exists

---

## Volume Structure

### ⚠️ CL-STORAGE-006: MINI Volume at 711MB Offset
**Claim:** A FAT-like filesystem labeled "MINI" begins at offset 711 MB (0x2C800000 bytes = 0x164000 sectors) on the SD card.

**Evidence:**
- E-STORAGE-005: "Erst ab Offset 711 MB erscheint ein FAT‑ähnliches Dateisystem, das im Menü als „MINI" geführt wird"
- E-STORAGE-012: "FAT‑ähnliches Dateisystem, das im Menü als „MINI" geführt wird"

**Status:** ⚠️ Supported (E2 doc-ref, needs direct verification)

**Next Tests:**
- Examine bytes at 0x2C800000 for FAT boot sector signature (0x55AA)
- Mount volume and verify contents match "MINI" menu label
- Determine if MINI is same as Volume 0 or separate

---

### ✅ CL-STORAGE-007: Volume 0 is FAT16 (Fonts)
**Claim:** Volume 0:/ is a FAT16 filesystem containing fonts (ARIAL.TTF, etc.), located at 512 MiB capacity. Firmware accesses it with LBA offset +0x20000.

**Evidence:**
- E-STORAGE-025: "FAT16 @ CHS (8,40,33)-(73,109,36) = 512 MiB - Enthält: Fonts - Das ist Volume 0"
- E-STORAGE-026: "disk_read für Volume 0: LBA = requested_sector + 0x20000"

**Status:** ✅ Verified (TestDisk E1 output + Ghidra E1 analysis)

**Next Tests:**
- Verify 0x20000 sectors × 512 bytes = offset where FAT16 boot sector appears
- Mount Volume 0 and list font files

---

### 🔬 CL-STORAGE-008: Volume 3:/ Purpose Unclear
**Claim:** References to "Volume 3:/" appear in firmware code, but its physical location on SD card is uncertain. It may be a raw accessor rather than a mounted FAT volume.

**Evidence:**
- E-STORAGE-010: "Volume 3 fehlt komplett in diesem Image (oder ist woanders als 0x152C20)"
- E-STORAGE-027: Same observation about Volume 3 missing
- E-STORAGE-028: "Analyse ob '3:/' echter FAT-Mount ist oder Raw-Accessor der 0x100000 mapped"

**Status:** 🔬 Hypothesis (conflicting evidence, needs investigation)

**Counter-Evidence:**
- Volume not found at expected TestDisk locations
- Mount function FUN_0005ebb8 behavior unclear

**Next Tests:**
- Analyze FUN_0005ebb8 mount function in Ghidra for Volume 3 handling
- Check if "3:/" is hardcoded raw offset accessor
- Review Finding-0020 for volume mount mechanisms

---

### ⚠️ CL-STORAGE-009: Firmware Update Volume is FAT16 (256 MiB)
**Claim:** A second FAT16 volume (256 MiB) contains firmware update binaries: ZK-INKJET-NANO-BOOT.bin, ZK-INKJET-NANO-APP.bin, ZK-INKJET-UI-QVGA.bin.

**Evidence:**
- E-STORAGE-037: "FAT16 @ (73,110,37)-(106,16,38) = 256 MiB - Enthält Firmware-Update Binaries"

**Status:** ⚠️ Supported (TestDisk E1 output)

**Next Tests:**
- Mount this FAT16 volume and verify file list
- Determine relationship to main firmware storage
- Check if this is Volume 3 or separate update partition

---

### ⚠️ CL-STORAGE-010: Firmware Binaries Stored in Raw Areas
**Claim:** Active firmware binaries (BOOT.bin, APP.bin) are intentionally written to raw SD card areas outside FAT filesystems, not as FAT file entries.

**Evidence:**
- E-STORAGE-030: "Firmware-Binaries werden absichtlich auf raw Bereiche der SD-Karte geschrieben (nicht im FAT-Dateisystem)"
- E-STORAGE-003: Boot signature at raw offset 0x200

**Status:** ⚠️ Supported (analysis conclusion from E1)

**Next Tests:**
- Verify NANO-APP.bin location on raw SD (expected after NANO-BOOT.bin)
- Check if firmware update process writes to raw areas or FAT volumes

---

## Capacity & Display

### 🔬 CL-STORAGE-011: Display Shows 0.8/3.8GB Usage
**Claim:** The device display reports "0.8/3.8GB" indicating 0.8GB used of 3.8GB total. The 3.8GB value doesn't precisely match the physical 3.75GB card size, suggesting firmware calculation or rounding.

**Evidence:**
- E-STORAGE-009: "Display zeigt '0.8/3.8GB' an"

**Status:** 🔬 Hypothesis (single E1 observation, calculation mechanism unknown)

**Counter-Evidence:**
- Physical card is 3.75 GiB, not 3.8 GB
- Discrepancy of ~50 MB unexplained

**Next Tests:**
- Analyze firmware code for capacity calculation routine
- Determine if 3.8GB includes/excludes boot areas
- Check if display uses GB (decimal) vs GiB (binary) units

---

### ⚠️ CL-STORAGE-012: Larger SD Cards Cause Display Failure
**Claim:** When using SD cards larger than 4GB (e.g., 8GB or 32GB), the "About" screen's storage analysis fails or displays incorrect values.

**Evidence:**
- E-STORAGE-008: "Bei größeren SD-Karten schlägt die Speichergrößen-Analyse im About-Screen fehl"

**Status:** ⚠️ Supported (E2 doc-ref, needs empirical test)

**Next Tests:**
- Test device with 8GB and 32GB SD cards
- Capture "About" screen behavior
- Identify hardcoded size assumptions in firmware

---

## ext4 Filesystem at 0x188FFC00

### ⚠️ CL-STORAGE-013: ext4 at 0x188FFC00 is False Positive
**Claim:** Binwalk reports an ext4 filesystem with volume name "rootfs" at offset 0x188FFC00, but this is likely a false positive or truncated/corrupted filesystem that cannot be mounted.

**Evidence:**
- E-STORAGE-014: "Binwalk zeigt bei 0x188FFC00 ein ext4‑'rootfs'"
- E-STORAGE-015: File command recognizes ext4 with UUID and volume name
- E-STORAGE-018: Analysis concludes "praktisch sicher ein Fehlalarm bzw. nur ein angeschnittenes Filesystem"
- E-STORAGE-019: "Scan nach ext-Magie liefert gar keine Kandidaten → kein vollständiger ext-Superblock"

**Status:** ⚠️ Supported (analysis conclusion, failed mount attempts)

**Counter-Evidence:**
- E-STORAGE-020: Magic bytes 53 ef found at expected superblock location
- E-STORAGE-015: Valid ext4 superblock detected with UUID

**Contradiction:** Superblock magic exists but filesystem is unmountable

**Next Tests:**
- Determine if 0x188FFC00 region is used by device at all
- Check for any ext4 usage in Nuvoton BSP or firmware
- Verify if region overlaps with any active data

---

### ✅ CL-STORAGE-014: ext4 Geometry Mismatch Prevents Mount
**Claim:** The ext4 superblock at 0x188FFC00 claims 1,937,920 blocks × 4096 bytes = 7.94 GB logical size, but only ~1.85 GB of data exists, causing "bad geometry" kernel errors when mounting.

**Evidence:**
- E-STORAGE-016: "BlockSize=4096, Blocks=1937920, ExpectedBytes=7937720320 but ActualBytes=1984430080"
- E-STORAGE-017: "EXT4-fs: bad geometry: block count 1937920 exceeds size of device (484480 blocks)"
- E-STORAGE-034: "Superblock-Magic ist da (53 ef)... aber Group-Descriptor-Tables / Bitmaps sind kaputt"
- E-STORAGE-035: "Block bitmap for group 0 overlaps superblock"

**Status:** ✅ Verified (kernel logs, dumpe2fs output)

**Next Tests:** None required - mount failure thoroughly documented

---

## USB Mass Storage

### ⚠️ CL-STORAGE-015: USB MSC Exposes SD as "W55FA93 SPI Disk"
**Claim:** When connected via USB, the device enumerates as a mass storage device with SCSI product string "W55FA93 SPI Disk", exposing (part of) the SD card.

**Evidence:**
- E-STORAGE-033: "Device: 'W55FA93 SPI Disk' - dmesg log shows USB mass storage enumeration"

**Status:** ⚠️ Supported (E1 dmesg log from USB cluster)

**Cross-Reference:** Links to USB cluster CL-USB-005 (SCSI device string)

**Next Tests:**
- Determine which volume(s) are exposed via USB MSC
- Verify if entire SD or only specific volumes accessible
- Test USB MSC capacity reporting

---

## TestDisk Analysis

### ✅ CL-STORAGE-016: TestDisk Finds Two FAT16 Volumes
**Claim:** TestDisk recovery tool successfully identifies two FAT16 filesystems on the raw SD card: Volume 0 (512 MiB fonts) and a firmware update volume (256 MiB).

**Evidence:**
- E-STORAGE-037: "FAT16 @ (8,40,33)-(73,109,36) = 512 MiB - Fonts - Volume 0. FAT16 @ (73,110,37)-(106,16,38) = 256 MiB - Firmware Binaries"
- E-STORAGE-011: User references testdisk.log for Volume 3 information

**Status:** ✅ Verified (TestDisk E0/E1 output)

**Next Tests:**
- Extract complete testdisk.log for full volume list
- Mount both FAT16 volumes and catalog contents

---

## Open Contradictions

### CONTRADICTION-STORAGE-001: Volume 3 Location
**Issue:** Volume 3:/ is referenced in firmware code but not found at expected location.

**Evidence:**
- Firmware mount code references "3:/"  (E-STORAGE-028)
- TestDisk doesn't show volume at expected offset 0x152C20 (E-STORAGE-010, E-STORAGE-027)

**Possible Resolutions:**
1. Volume 3 is a raw accessor, not a FAT mount
2. Volume 3 is dynamically created or overlaps with another volume
3. Offset calculation for Volume 3 is incorrect

**Resolution Test:** Analyze FUN_0005ebb8 mount function behavior

---

### CONTRADICTION-STORAGE-002: 711MB MINI vs Volume 0
**Issue:** Unclear if "MINI" volume at 711MB is the same as "Volume 0" containing fonts.

**Evidence:**
- MINI at 711 MB (0x2C800000) per documentation (E-STORAGE-005)
- Volume 0 FAT16 at different CHS location per TestDisk (E-STORAGE-025)

**Possible Resolutions:**
1. MINI and Volume 0 are the same (different naming in docs vs code)
2. MINI is yet another volume not captured by TestDisk
3. Offset calculations differ between sources

**Resolution Test:** Calculate byte offset of TestDisk CHS (8,40,33) and compare to 0x2C800000

---

## Summary

**Total Claims:** 16
**Status Distribution:**
- ✅ Verified: 6 claims
- ⚠️ Supported: 8 claims
- 🔬 Hypothesis: 2 claims

**Contradictions:** 2 active

**Key Findings:**
1. Raw SD card layout confirmed (no partition table)
2. Nuvoton IBR boot process identified
3. Multiple FAT16 volumes exist (fonts, firmware update)
4. Volume numbering scheme unclear (0:/, 3:/ mapping unknown)
5. ext4 at 0x188FFC00 likely irrelevant to device operation

**High Priority Tests:**
1. Resolve Volume 3 location (analyze mount function)
2. Clarify MINI vs Volume 0 relationship
3. Test larger SD cards for size limit bug
4. Mount and catalog all FAT16 volumes
