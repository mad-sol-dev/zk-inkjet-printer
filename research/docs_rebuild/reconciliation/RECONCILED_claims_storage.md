# STORAGE Reconciled Claims (Phase 2C-3)

Authority order: E0 > E3-New > E1 > E3-Old > E4 (E2 = context only).

---

## CL-STORAGE-REC-001: Raw SD Layout Without MBR/GPT

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** The SD card uses a raw layout with no MBR/GPT partition table; partition table bytes are all zero and no 0x55AA signature is present.

**Evidence (All Tiers):**
- **E0:** `firmware/image/sdcard.work.img` (MBR signature bytes 0x0000; partition table bytes 0x0000)
- **E3-New:** None
- **E1:** E-STORAGE-001 (raw layout), E-STORAGE-006 (no partition table)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-STORAGE-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** None required.

**Tags:** storage, sd-card, layout, raw

---

## CL-STORAGE-REC-002: SD Card Capacity Is 4,026,531,840 Bytes

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** The SD card image size is 4,026,531,840 bytes (3.75 GiB), consistent with a 4 GB card.

**Evidence (All Tiers):**
- **E0:** `firmware/image/sdcard.work.img` (file size 4,026,531,840 bytes)
- **E3-New:** None
- **E1:** E-STORAGE-002 (capacity 4,026,531,840 bytes)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-STORAGE-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** None required.

**Tags:** storage, sd-card, capacity

---

## CL-STORAGE-REC-003: Boot Signature at Offset 0x200

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** The SD image contains the ZBW boot signature at offset 0x200.

**Evidence (All Tiers):**
- **E0:** `firmware/image/sdcard.work.img` (offset 0x200 bytes = `a5 5a 42 57 00 00 70 00 00 31 00 00 57 42 5a a5`)
- **E3-New:** None
- **E1:** E-STORAGE-003 (hex dump), E-STORAGE-004 (ZBWp1WBZ signature)
- **E3-Old:** E-RKO-STORAGE-002 (raw offset 0x200) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-STORAGE-003
- E3-Old: CL-RKO-STORAGE-002 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Confirm stage-2 loader boundaries after the signature region.

**Tags:** storage, boot, signature, offset

---

## CL-STORAGE-REC-004: Raw Firmware Binaries Stored at 0x200 and 0x100000

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** BOOT.bin and APP.bin are stored at raw SD offsets 0x200 and 0x100000, respectively, outside FAT filesystems.

**Evidence (All Tiers):**
- **E0:** `firmware/image/sdcard.work.img` (boot header at 0x200 and APP IVT at 0x100000)
- **E3-New:** None
- **E1:** E-STORAGE-010 (raw firmware areas), E-STORAGE-029 (BOOT size at 0x200), E-STORAGE-031 (IBR loads BOOT at 0x200)
- **E3-Old:** E-RKO-STORAGE-002 (raw offsets 0x200 and 0x100000) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-STORAGE-004
- E1: CL-STORAGE-010
- E3-Old: CL-RKO-STORAGE-002 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Confirm raw offsets in a fresh SD dump to rule out imaging shifts.

**Tags:** storage, firmware, raw, offsets

---

## CL-STORAGE-REC-005: SD Card Required for Boot

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** The device does not boot without the SD card inserted.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-STORAGE-007 (SD required for boot)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-STORAGE-005

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Power-cycle the device with the SD card removed and verify no boot output.

**Tags:** storage, boot, sd-card

---

## CL-STORAGE-REC-006: Volume 0 FAT16 at LBA 0x20000 (Fonts)

**Status:** verified
**Confidence:** 0.90
**Authority:** E0

**Statement:** A FAT16 filesystem begins at LBA 0x20000 (offset 0x04000000) and corresponds to Volume 0 containing font resources.

**Evidence (All Tiers):**
- **E0:** `firmware/image/sdcard.work.img` (offset 0x04000000 shows FAT16 boot sector with 0x55AA and "FAT16" label)
- **E3-New:** None
- **E1:** E-STORAGE-025 (Volume 0 FAT16 with fonts), E-STORAGE-026 (LBA offset +0x20000)
- **E3-Old:** E-RKO-STORAGE-001 (0:/ used for resources) [ghidra-v1]
- **E4:** E-OLD-STORAGE-004 (0:/ reserved for resources) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E1: CL-STORAGE-007
- E1: CL-STORAGE-016 (partial overlap)
- E3-Old: CL-RKO-STORAGE-001 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Mount the volume and confirm font file list (ARIAL.TTF, etc.).

**Tags:** storage, fat16, volume-0, fonts

---

## CL-STORAGE-REC-007: Firmware Update FAT16 Volume at LBA 1179711

**Status:** supported
**Confidence:** 0.85
**Authority:** E0

**Statement:** A FAT filesystem begins at LBA 1,179,711 (offset 0x24007E00) and corresponds to the firmware update volume (~255 MiB).

**Evidence (All Tiers):**
- **E0:** `firmware/image/sdcard.work.img` (offset 0x24007E00 shows FAT boot sector with 0x55AA and "FAT" label)
- **E3-New:** None
- **E1:** E-STORAGE-037 (TestDisk: 256 MiB firmware update volume)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-STORAGE-009
- E1: CL-STORAGE-016 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Mount the volume and verify BOOT/APP/UI binaries are present.

**Tags:** storage, fat, firmware-update, volume

---

## CL-STORAGE-REC-008: Small FAT Volume at LBA 1388767 Likely MINI/USB

**Status:** supported
**Confidence:** 0.70
**Authority:** E0

**Statement:** A small FAT filesystem (~63 MiB) begins at LBA 1,388,767 (offset 0x2A61BE00), likely corresponding to the MINI/USB-exposed volume.

**Evidence (All Tiers):**
- **E0:** `firmware/image/sdcard.work.img` (offset 0x2A61BE00 shows FAT boot sector with 0x55AA and "FAT" label)
- **E3-New:** None
- **E1:** E-STORAGE-005 (MINI at ~711 MB), E-STORAGE-012 (MINI FAT), E-STORAGE-033 (USB MSC device string)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-STORAGE-006

**Superseded Evidence:**
- E-STORAGE-005 offset 0x2C800000 is not a FAT boot sector in `firmware/image/sdcard.work.img` (offset likely incorrect).

**Contradictions Resolved:** CONTRADICTION-STORAGE-002 (MINI vs Volume 0) remains unresolved; MINI is distinct from Volume 0 in the current image.

**Next Test:** Mount the 0x2A61BE00 volume and confirm it matches the MINI menu and USB MSC contents.

**Tags:** storage, mini, usb-msc, fat

---

## CL-STORAGE-REC-009: Volume 0:/ and 3:/ Roles Referenced, 3:/ Mapping Unresolved

**Status:** supported
**Confidence:** 0.70
**Authority:** E3-Old

**Statement:** Firmware references 0:/ for resources and 3:/ for firmware/UI updates, but the physical location of 3:/ remains unresolved in the SD image.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-STORAGE-010 (Volume 3 missing), E-STORAGE-027 (missing at expected offset), E-STORAGE-028 (mount function analysis)
- **E3-Old:** E-RKO-STORAGE-001 (0:/ resources, 3:/ firmware/UI) [ghidra-v1]
- **E4:** E-OLD-STORAGE-004 (3:/ update-only, 0:/ resources) [ghidra-v1]
- **E2:** E2-STORAGE-012 (volume roles narrative)

**Source Claims:**
- E1: CL-STORAGE-008
- E3-Old: CL-RKO-STORAGE-001

**Superseded Evidence:** None

**Contradictions Resolved:** CONTRADICTION-STORAGE-001 (Volume 3 location) remains unresolved.

**Next Test:** Analyze FUN_0005ebb8 (mount) in the optimized Ghidra project to locate 3:/ mapping.

**Tags:** storage, volume-3, mapping, update

---

## CL-STORAGE-REC-010: Update Filenames Hardcoded On 3:/ Root

**Status:** supported
**Confidence:** 0.80
**Authority:** E4

**Statement:** Firmware update logic scans 3:/ root for a fixed list of update filenames (BOOT/APP/UI/UI-QVGA and legacy names).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-STORAGE-001 (hardcoded firmware filenames on 3:/) [ghidra-v1]
- **E4:** E-OLD-STORAGE-001 (filename list), E-OLD-STORAGE-004 (3:/ only) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-STORAGE-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Verify filename list against live update flow on hardware.

**Tags:** storage, update, filenames, 3:/

---

## CL-STORAGE-REC-011: Update Filename Matching Uses Literal Pool + memcmp

**Status:** supported
**Confidence:** 0.75
**Authority:** E4

**Statement:** Update filename matching uses a literal pool and memcmp loops that branch to upgrade-found or no-upgrade handlers.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** None
- **E4:** E-OLD-STORAGE-002 (literal pool + memcmp), E-OLD-STORAGE-003 (handler linkage) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-STORAGE-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Re-check the matcher in the optimized Ghidra project for exact pool entries.

**Tags:** storage, update, memcmp, handlers

---

## CL-STORAGE-REC-012: Update Path Uses Raw Writes Without Checksums

**Status:** supported
**Confidence:** 0.80
**Authority:** E3-Old

**Statement:** The update path stages files via FAT and then writes raw SD sectors without cryptographic verification or checksums.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-STORAGE-030 (raw write to SD)
- **E3-Old:** E-RKO-STORAGE-002 (raw write path, no checksum) [ghidra-v1]
- **E4:** E-OLD-STORAGE-005 (no CRC routines) [ghidra-v1]
- **E2:** E2-STORAGE-012 (raw write chain narrative)

**Source Claims:**
- E3-Old: CL-RKO-STORAGE-002 (partial overlap)
- E4: CL-OLD-STORAGE-003

**Superseded Evidence:** None

**Contradictions Resolved:** Update validation conflict noted in `research/old_docs/analysis/documentation_contradictions_map.md` remains unresolved.

**Next Test:** Re-evaluate validator function in current APP.bin to confirm checksum behavior.

**Tags:** storage, update, raw-write, validation

---

## CL-STORAGE-REC-013: U-Disk Bulk Resource Update Copies ZKML

**Status:** supported
**Confidence:** 0.75
**Authority:** E4

**Statement:** The u-disk bulk update copies `0:/ZK-INKJET-RES-HW.zkml` and related resources into internal flash via `update_copy_or_flash`.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** None
- **E4:** E-OLD-STORAGE-006 (resource bulk update) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-STORAGE-004

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Trace `udisk_bulk_asset_update` in current APP.bin to confirm destinations.

**Tags:** storage, resources, zkml, update

---

## CL-STORAGE-REC-014: ext4 Superblock Present But Geometry Invalid

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** An ext4 superblock magic is present at 0x188FFC00, but the filesystem geometry is invalid and the volume is not mountable.

**Evidence (All Tiers):**
- **E0:** `firmware/image/sdcard.work.img` (ext4 magic 0x53ef at 0x188FFC00+0x438)
- **E3-New:** None
- **E1:** E-STORAGE-014 (binwalk detection), E-STORAGE-016 (geometry mismatch), E-STORAGE-017 (bad geometry log), E-STORAGE-034 (superblock magic), E-STORAGE-035 (descriptor overlap)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-STORAGE-013
- E1: CL-STORAGE-014

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Determine whether the 0x188FFC00 region overlaps active data or is unused padding.

**Tags:** storage, ext4, false-positive, geometry

---

## CL-STORAGE-REC-015: Storage Capacity UI Is Inconsistent

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E1

**Statement:** The About screen reports 0.8/3.8GB and fails on larger SD cards, indicating inconsistent capacity calculations.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-STORAGE-009 (0.8/3.8GB display), E-STORAGE-008 (failure on larger cards)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-STORAGE-011
- E1: CL-STORAGE-012

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Locate the About-screen capacity calculation and check unit assumptions (GB vs GiB).

**Tags:** storage, capacity, ui, bug

---

## CL-STORAGE-REC-016: USB MSC Device String "W55FA93 SPI Disk"

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** When connected over USB, the device enumerates as a mass storage device with the product string "W55FA93 SPI Disk".

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-STORAGE-033 (dmesg device string)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-STORAGE-015

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Check which volume is exposed via USB MSC and compare to the 63 MiB FAT volume.

**Tags:** storage, usb-msc, device-string
