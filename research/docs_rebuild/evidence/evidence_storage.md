# STORAGE Evidence

Extracted evidence from chat transcripts. Format: Quote (1-2 lines) + Source + Date + Type + Tags.

---

## SD Card Physical Structure

### E-STORAGE-001: No MBR/Partition Table
- **Quote:** "Das mit MBR/Partitionstabellen/Boot-Strukturen habe ich schon x-mal durchgekaut, alles ist raw auf der SD-Karte"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=3
- **Date:** 2025-12-14
- **Type:** OBSERVATION
- **Tags:** sd-card, layout, raw, no-mbr

### E-STORAGE-002: SD Card Capacity
- **Quote:** "SD-Karten-Image ist 4026531840 Bytes = 3.75 GB genau. Das passt zu einer 4GB SD-Karte"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=15
- **Date:** 2025-12-14
- **Type:** OBSERVATION (image analysis)
- **Tags:** sd-card, capacity, geometry

### E-STORAGE-003: Boot Signature Location
- **Quote:** "+00000200: A5 5A 42 57 00 00 70 00 00 31 00 00 57 42 5A A5  .ZBW..p..1..WBZ."
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=20
- **Date:** 2025-12-14
- **Type:** OBSERVATION (hex dump)
- **Tags:** boot, signature, zbw, offset

### E-STORAGE-004: Stage-1 Bootloader Signature
- **Quote:** "Am Anfang befindet sich ein Stage‑1‑Bootloader (Signatur „ZBWp1WBZ"), gefolgt von einem größeren Stage‑2‑Loader"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=8
- **Date:** 2025-12-14
- **Type:** DOC-REF (boot_analysis_methodology.md)
- **Tags:** boot, stage1, zbwp1wbz, bootloader

---

## Volume Structure & Filesystem Layout

### E-STORAGE-005: MINI Volume Offset
- **Quote:** "Erst ab Offset 711 MB erscheint ein FAT‑ähnliches Dateisystem, das im Menü als „MINI" geführt wird. 711 MB = ~0x2C800000 Bytes = 0x164000 Sektoren"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=8
- **Date:** 2025-12-14
- **Type:** DOC-REF (boot_analysis_methodology.md)
- **Tags:** volume, mini, offset, fat, 711mb

### E-STORAGE-006: No Classical Partition Table
- **Quote:** "Die Firmware liegt auf einer entnehmbaren SD‑Karte, die keine klassische Partitionstabelle besitzt"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=10
- **Date:** 2025-12-14
- **Type:** DOC-REF
- **Tags:** sd-card, partition, firmware, raw-layout

### E-STORAGE-007: SD Card as Boot Medium
- **Quote:** "Ohne SD‑Karte startet das Gerät nicht. SD‑Karte als Bootmedium"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=10
- **Date:** 2025-12-14
- **Type:** DOC-REF
- **Tags:** boot, sd-card, requirement, bootmedium

### E-STORAGE-008: Capacity Display Issues on Larger Cards
- **Quote:** "Bei größeren SD-Karten (z.b. 8 oder 32GB) schlägt die Speichergrößen-Analyse im About-Screen fehl"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=8
- **Date:** 2025-12-14
- **Type:** DOC-REF (boot_analysis_methodology.md)
- **Tags:** capacity, bug, display, limitation

### E-STORAGE-009: Device Display Shows 0.8/3.8GB
- **Quote:** "Display zeigt '0.8/3.8GB' an - das würde bedeuten dass 0.8GB belegt sind von 3.8GB total"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=6
- **Date:** 2025-12-14
- **Type:** OBSERVATION
- **Tags:** display, capacity, usage, 0.8gb, 3.8gb

---

## Volume Identification & Numbering

### E-STORAGE-010: Volume 3 Missing Reference
- **Quote:** "Volume 3 fehlt komplett in diesem Image (oder ist woanders als 0x152C20)"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=22
- **Date:** 2025-12-14
- **Type:** OBSERVATION (analysis)
- **Tags:** volume-3, missing, 0x152C20

### E-STORAGE-011: TestDisk Log Reference
- **Quote:** "schau dir bitte mal $HOME/workspace/zk-inkjet-printer/data/raw/testdisk.log an!"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=22
- **Date:** 2025-12-14
- **Type:** DOC-REF (external file)
- **Tags:** testdisk, volume-3, log, recovery

---

## Filesystem Type Analysis

### E-STORAGE-012: FAT-like Filesystem for MINI
- **Quote:** "FAT‑ähnliches Dateisystem, das im Menü als „MINI" geführt wird"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=8
- **Date:** 2025-12-14
- **Type:** DOC-REF
- **Tags:** fat, mini, filesystem, menu

---

## SD Card Image Files

### E-STORAGE-013: Working SD Card Image Path
- **Quote:** "mit $HOME/workspace/zk-inkjet-printer/data/raw/sdcard.workout.img solltest Du eigentlich alles anstellen können"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=13
- **Date:** 2025-12-14
- **Type:** OBSERVATION
- **Tags:** image-file, sdcard, path, artifact

---

## ext4 Filesystem Analysis (Binwalk 0x188FFC00)

### E-STORAGE-014: Binwalk Detection at 0x188FFC00
- **Quote:** "Binwalk zeigt bei 0x188FFC00 ein ext4‑'rootfs'"
- **Source:** Chats/834_GPT_Binwalk_output_analysis_29.09.2025.json#msg=55
- **Date:** 2025-09-29
- **Type:** OBSERVATION (binwalk output)
- **Tags:** binwalk, ext4, 0x188FFC00, rootfs

### E-STORAGE-015: ext4 Volume Name "rootfs"
- **Quote:** "Linux rev 1.0 ext4 filesystem data, UUID=11bf1134-ed79-497f-bdb1-5a75c9d73601, volume name 'rootfs'"
- **Source:** Chats/834_GPT_Binwalk_output_analysis_29.09.2025.json#msg=394
- **Date:** 2025-09-29
- **Type:** LOG (file command output)
- **Tags:** ext4, rootfs, uuid, volume-name

### E-STORAGE-016: ext4 Geometry Mismatch
- **Quote:** "BlockSize=4096, Blocks=1937920, ExpectedBytes=7937720320 but ActualBytes=1984430080"
- **Source:** Chats/834_GPT_Binwalk_output_analysis_29.09.2025.json#msg=404
- **Date:** 2025-09-29
- **Type:** OBSERVATION (superblock analysis)
- **Tags:** ext4, geometry, mismatch, truncated

### E-STORAGE-017: ext4 Bad Geometry Kernel Error
- **Quote:** "EXT4-fs (loop3): bad geometry: block count 1937920 exceeds size of device (484480 blocks)"
- **Source:** Chats/834_GPT_Binwalk_output_analysis_29.09.2025.json#msg=404
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** ext4, kernel-error, geometry, mount-failure

### E-STORAGE-018: ext4 False Positive Conclusion
- **Quote:** "Der von binwalk gemeldete ext4-Treffer bei 0x188FFC00 ist praktisch sicher ein Fehlalarm bzw. nur ein angeschnittenes Filesystem"
- **Source:** Chats/834_GPT_Binwalk_output_analysis_29.09.2025.json#msg=421
- **Date:** 2025-09-30
- **Type:** OBSERVATION (analysis conclusion)
- **Tags:** ext4, false-positive, binwalk, truncated

### E-STORAGE-019: No Valid ext4 Magic Found
- **Quote:** "Scan nach der ext-Magie an der richtigen Stelle (EF 53 bei offset + 1024 + 0x38) liefert gar keine Kandidaten → im Original-Image gibt es keinen vollständigen ext-Superblock"
- **Source:** Chats/834_GPT_Binwalk_output_analysis_29.09.2025.json#msg=421
- **Date:** 2025-09-30
- **Type:** TEST (magic byte scan)
- **Tags:** ext4, magic-bytes, scan-result, negative

### E-STORAGE-020: ext4 Analysis on Drucker Image
- **Quote:** "dd if=drucker_image.img bs=1 skip=$((0x188FFC00+1024+0x38)) count=2 2>/dev/null | hexdump → '53 ef'"
- **Source:** Chats/834_GPT_Binwalk_output_analysis_29.09.2025.json#msg=425
- **Date:** 2025-09-30
- **Type:** TEST (hex verification)
- **Tags:** ext4, magic-bytes, 0x188FFC00, drucker-image

---

## Volume 0:/ (Fonts/MINI Volume)

### E-STORAGE-025: Volume 0 FAT16 Structure
- **Quote:** "FAT16 @ CHS (8,40,33)-(73,109,36) = 1,048,576 sectors = 512 MiB - Enthält: Fonts (ARIAL.TTF, etc.) - Das ist Volume 0"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=37
- **Date:** 2025-12-14
- **Type:** OBSERVATION (testdisk analysis)
- **Tags:** volume-0, fat16, fonts, 512mb

### E-STORAGE-026: Volume 0 LBA Offset Calculation
- **Quote:** "disk_read für Volume 0: LBA = requested_sector + 0x20000"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=25
- **Date:** 2025-12-14
- **Type:** OBSERVATION (Ghidra analysis)
- **Tags:** volume-0, lba, offset, 0x20000, disk-read

---

## Volume 3:/ (Boot+APP Storage)

### E-STORAGE-027: Volume 3 Missing at Expected Offset
- **Quote:** "Volume 3 fehlt komplett in diesem Image (oder ist woanders als 0x152C20)"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=22
- **Date:** 2025-12-14
- **Type:** OBSERVATION
- **Tags:** volume-3, location, 0x152C20, missing

### E-STORAGE-028: Volume 3 Mount Function Reference
- **Quote:** "Finding-0020 zeigt mount bei FUN_0005ebb8(&'0:/'...) - Analyse ob '3:/' echter FAT-Mount ist oder Raw-Accessor der 0x100000 mapped"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=70
- **Date:** 2025-12-15
- **Type:** DOC-REF (Finding-0020)
- **Tags:** volume-3, mount, fun_0005ebb8, raw-accessor

---

## Boot Binaries & Raw Layout

### E-STORAGE-029: NANO-BOOT.bin at 0x200
- **Quote:** "User fragt ob ich nach NANO-BOOT.bin bei Offset 0x200 suche. NANO-BOOT.bin ist laut TestDisk 12,736 bytes = 0x31c0"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=45
- **Date:** 2025-12-15
- **Type:** OBSERVATION
- **Tags:** nano-boot, offset-0x200, testdisk, boot-binary

### E-STORAGE-030: Firmware Binaries Written Raw
- **Quote:** "Die Firmware-Binaries werden von der Firmware absichtlich auf raw Bereiche der SD-Karte geschrieben (nicht im FAT-Dateisystem)"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=41
- **Date:** 2025-12-15
- **Type:** OBSERVATION
- **Tags:** firmware, raw-write, sd-layout, intentional

### E-STORAGE-031: IBR Boot Process
- **Quote:** "IBR (Internal Boot ROM) lädt BOOT.bin von Offset 0x200, BOOT.bin initialisiert System, dann muss BOOT.bin APP.bin laden"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=68
- **Date:** 2025-12-15
- **Type:** OBSERVATION (boot sequence)
- **Tags:** ibr, boot-sequence, 0x200, boot-bin, app-bin

### E-STORAGE-032: Nuvoton IBR Standard Process
- **Quote:** "Das SD-Karte Image Layout ist Nuvoton-Standard IBR Boot-Prozess - nicht ZK-Inkjet spezifisch"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=60
- **Date:** 2025-12-15
- **Type:** OBSERVATION
- **Tags:** nuvoton, ibr, standard, vendor-specific

---

## USB Mass Storage & Volume Exposure

### E-STORAGE-033: USB MSC Device String
- **Quote:** "Device: 'W55FA93 SPI Disk' - dmesg log shows USB mass storage enumeration"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=33
- **Date:** 2025-12-14
- **Type:** LOG (dmesg)
- **Tags:** usb-msc, w55fa93, device-string, enumeration

---

## Filesystem Repair Attempts

### E-STORAGE-034: ext4 Superblock Magic Confirmed
- **Quote:** "Die Superblock-Magic ist da (53 ef), der Volume-Name ist 'rootfs', aber die Group-Descriptor-Tables / Bitmaps sind so kaputt dass Kernel und e2fsck nicht sauber arbeiten"
- **Source:** Chats/15_GPT_Teilgespräch__Handheld-Drucker_Analyse_Tipps_01.10.2025.json#msg=23
- **Date:** 2025-10-01
- **Type:** OBSERVATION (filesystem analysis)
- **Tags:** ext4, superblock, magic-53ef, rootfs, corruption

### E-STORAGE-035: ext4 Group Descriptor Corruption
- **Quote:** "EXT4-fs: ext4_check_descriptors: Block bitmap for group 0 overlaps superblock"
- **Source:** Chats/15_GPT_Teilgespräch__Handheld-Drucker_Analyse_Tipps_01.10.2025.json#msg=16
- **Date:** 2025-10-01
- **Type:** LOG (kernel dmesg)
- **Tags:** ext4, group-descriptor, corruption, kernel-error

### E-STORAGE-036: Mount Loop Device at 0x188FFC00
- **Quote:** "offset=$((0x188FFC00)); sudo losetup --find --show -o $offset sdcard.work.img → /dev/loop3"
- **Source:** Chats/15_GPT_Teilgespräch__Handheld-Drucker_Analyse_Tipps_01.10.2025.json#msg=22
- **Date:** 2025-10-01
- **Type:** TEST (losetup command)
- **Tags:** losetup, offset, 0x188FFC00, loop-device

---

## FAT Volumes Found by TestDisk

### E-STORAGE-037: Two FAT16 Volumes Found
- **Quote:** "FAT16 @ (8,40,33)-(73,109,36) = 512 MiB - Enthält Fonts - Das ist Volume 0. FAT16 @ (73,110,37)-(106,16,38) = 256 MiB - Enthält Firmware-Update Binaries"
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=37
- **Date:** 2025-12-14
- **Type:** OBSERVATION (testdisk output)
- **Tags:** testdisk, fat16, volume-0, firmware-volume

---

## Open Questions

### E-STORAGE-021: Volume 3 Location Unknown
- **Question:** Where is Volume 3 located on the SD card? Expected at 0x152C20 but not found there.
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=22
- **Date:** 2025-12-14
- **Type:** OPEN-QUESTION
- **Tags:** volume-3, location, unknown

### E-STORAGE-022: Volume Numbering Scheme
- **Question:** How are volumes numbered? Why "MINI" at 711MB and reference to "Volume 3"? What about Volume 0, 1, 2?
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=37
- **Date:** 2025-12-14
- **Type:** OPEN-QUESTION
- **Tags:** volumes, numbering, scheme

### E-STORAGE-023: USB MSC Volume Exposure
- **Question:** Which volume(s) are exposed via USB Mass Storage Class? Is it the MINI volume or a different one?
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=33
- **Date:** 2025-12-14
- **Type:** OPEN-QUESTION
- **Tags:** usb-msc, volume, exposure

### E-STORAGE-024: Total Capacity Calculation
- **Question:** Display shows 0.8/3.8GB but SD card is 3.75GB. How is the 3.8GB calculated and why doesn't it match physical size?
- **Source:** Chats/915_CL_SD-Karte_Image_rekonstruieren_aus_Raw-Daten_1_14.12.2025.json#msg=6
- **Date:** 2025-12-14
- **Type:** OPEN-QUESTION
- **Tags:** capacity, calculation, display, mismatch

---

**Total Evidence Entries:** 37
**Categories:**
- SD Card Physical (4)
- Volume Structure (5)
- Volume ID (2)
- Filesystem (1)
- Image Files (1)
- ext4 Analysis (7)
- Volume 0:/ (2)
- Volume 3:/ (2)
- Boot Binaries (4)
- USB MSC (1)
- Filesystem Repair (3)
- FAT TestDisk (1)
- Open Questions (4)

**Evidence Quality:**
- ✅ All sources include message index numbers
- ✅ No token-claims (raw shell output avoided)
- ✅ Mix of LOG, OBSERVATION, TEST, DOC-REF types
- ✅ Clear categorization by subsystem
- ✅ Open questions tracked separately
