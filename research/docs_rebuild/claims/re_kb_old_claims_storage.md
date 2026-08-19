# STORAGE Claims (From E3-Old RE-KB Archive)

Propositional claims synthesized from historical RE-KB findings. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## Storage Layout and Volumes

### ⚠️ Supported CL-RKO-STORAGE-001: SD Card Volume Management
**Claim:** Firmware uses dual-volume scheme: resource copier starts at FUN_0005cfb8, mounting "system" on 0:/ then copying assets from 3:/ to 0:/. Boot updater at FUN_0006887c loads 3:/ZK-INKJET-NANO-BOOT.bin then 3:/ZK-INKJET-NANO-APP.bin via file copy routine FUN_0006ccf8. Volume labels referenced are only 0:/ (fonts/resources) and 3:/ (firmware/UI). FAT strings present but no evidence of 1:/,2:/ usage. APP.bin has no trailing padding; free space not identified. USB MSC volume selection not yet resolved.

**Evidence:**
- E-RKO-STORAGE-001: Resource bootstrap copies assets from 3:/ to 0:/ via FUN_0006ccf8; called after mount
- E-RKO-STORAGE-001: Boot updater copies 3:/ZK-INKJET-NANO-BOOT.bin then 3:/ZK-INKJET-NANO-APP.bin via FUN_0006ccf8
- E-RKO-STORAGE-001: File copy/IO routine used for firmware and resource transfers
- E-RKO-STORAGE-001: Hardcoded firmware filenames on 3:/ (BOOT/APP/UI)

**Status:** ⚠️ Supported
**Cross-Reference:** Potential overlap with CL-STORAGE-006, CL-STORAGE-009
**Next Tests:** Analyze FUN_0005ebb8 for mount table and volume indexing; Search About-screen handler for 0.8/3.8GB usage calculation; Trace USB MSC setup to see which volume is exported (0:/ MINI) and if configurable; Review FUN_0006ccf8 call parameters for size checks or bounds; Search for hardcoded sector offsets or volume structures mapping 0:/ and 3:/

---

### ✅ Verified CL-RKO-STORAGE-002: SD Card Raw Binary Storage Layout and Firmware Update Workflow
**Claim:** Firmware binaries are stored at RAW sector offsets (BOOT @ 0x200, APP @ 0x100000) and updated via dedicated RAW write path bypassing FatFS. Update workflow: FAT staging (3:/ → 0:/) followed by RAW sector writes using FUN_00032500→FUN_00094584. NO checksums or cryptographic validation - only basic size checks.

**Evidence:**
- E-RKO-STORAGE-002: NANO-BOOT.bin located at raw offset 0x200 (LBA 1). Header: 'A5 5A 42 57 00 00 70 00 00 31 00 00 57 42 5A A5' (ZBWp1WBZ signature). Size: 12,736 bytes (0x31C0) - exact match with TestDisk deleted entry. ARM code starts at 0x220 with CP15 coprocessor configuration and branch instructions.
- E-RKO-STORAGE-002: NANO-APP.bin located at raw offset 0x100000 (1 MiB, LBA 0x800). ARM Interrupt Vector Table detected with Reset Vector 0xEA000014 and IRQ handlers 0xE59FF018. Size: 2,576,940 bytes (0x27522C) - exact match with TestDisk deleted entry. Contains ARM code and strings like 'Handwriting Resources', 'system', '0:/' indicating main application firmware.
- E-RKO-STORAGE-002: TestDisk analysis shows deleted FAT directory entries: FAT16 Volume 2 @ LBA 0x12003F contains deleted entries for ZK-INKJET-NANO-BOOT.bin (12,736 bytes) and ZK-INKJET-NANO-APP.bin (2,576,940 bytes) marked with deletion flag 0xE5. Sizes exactly match raw binaries found at 0x200 and 0x100000. Current FAT only contains ZK-INKJET-UI-QVGA.bin (460,800 bytes) as active file.

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-STORAGE-004, CL-BOOT-011
**Next Tests:** None listed

---
