# STORAGE Subsystem Reconciliation Decisions

**Date:** 2026-01-05
**Reconciler:** Codex (GPT-5.1)
**Input Tiers:** E0, E1, E2, E3-Old, E4

## Decision Summary

- Total Claims Input: 22
- Merged Claims Output: 16
- EXACT_MATCH merges: 0
- PARTIAL_OVERLAP merges: 8
- UNIQUE kept: 8
- REFUTED: 0

## Claim-by-Claim Decisions

### CL-STORAGE-REC-001: Raw SD Layout Without MBR/GPT

**Decision:** UNIQUE
**Source Claims:** CL-STORAGE-001 (E1)
**Reasoning:** Single E1 claim, now grounded by E0 image inspection.
**Authority:** E0
**Evidence Merged:** E-STORAGE-001, E-STORAGE-006, `firmware/image/sdcard.work.img`
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-002: SD Card Capacity Is 4,026,531,840 Bytes

**Decision:** UNIQUE
**Source Claims:** CL-STORAGE-002 (E1)
**Reasoning:** E1 observation confirmed by E0 image size.
**Authority:** E0
**Evidence Merged:** E-STORAGE-002, `firmware/image/sdcard.work.img`
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-003: Boot Signature at Offset 0x200

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-STORAGE-003 (E1), CL-RKO-STORAGE-002 (E3-Old)
**Reasoning:** Both tiers identify ZBW signature at 0x200; E0 image validates.
**Authority:** E0
**Evidence Merged:** E-STORAGE-003, E-STORAGE-004, E-RKO-STORAGE-002, `firmware/image/sdcard.work.img`
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-004: Raw Firmware Binaries Stored at 0x200 and 0x100000

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-STORAGE-004 (E1), CL-STORAGE-010 (E1), CL-RKO-STORAGE-002 (E3-Old)
**Reasoning:** E1 and E3-Old agree on raw offsets; E0 image confirms.
**Authority:** E0
**Evidence Merged:** E-STORAGE-010, E-STORAGE-029, E-STORAGE-031, E-RKO-STORAGE-002, `firmware/image/sdcard.work.img`
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-005: SD Card Required for Boot

**Decision:** UNIQUE
**Source Claims:** CL-STORAGE-005 (E1)
**Reasoning:** Single E1 observation; kept pending hardware test.
**Authority:** E1
**Evidence Merged:** E-STORAGE-007
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-006: Volume 0 FAT16 at LBA 0x20000 (Fonts)

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-STORAGE-007 (E1), CL-STORAGE-016 (E1), CL-RKO-STORAGE-001 (E3-Old)
**Reasoning:** E1 TestDisk output and firmware LBA mapping align; E0 boot sector confirms.
**Authority:** E0
**Evidence Merged:** E-STORAGE-025, E-STORAGE-026, E-RKO-STORAGE-001, E-OLD-STORAGE-004, `firmware/image/sdcard.work.img`
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-007: Firmware Update FAT16 Volume at LBA 1179711

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-STORAGE-009 (E1), CL-STORAGE-016 (E1)
**Reasoning:** TestDisk identifies the 256 MiB update volume; E0 confirms FAT boot sector at LBA 1,179,711.
**Authority:** E0
**Evidence Merged:** E-STORAGE-037, `firmware/image/sdcard.work.img`
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-008: Small FAT Volume at LBA 1388767 Likely MINI/USB

**Decision:** UNIQUE
**Source Claims:** CL-STORAGE-006 (E1)
**Reasoning:** E1 identifies MINI; E0 finds a small FAT volume near the expected region but offset differs.
**Authority:** E0
**Evidence Merged:** E-STORAGE-005, E-STORAGE-012, E-STORAGE-033, `firmware/image/sdcard.work.img`
**Superseded:** E-STORAGE-005 offset 0x2C800000 not a FAT boot sector in the current image.
**Contradiction:** CONTRADICTION-STORAGE-002 (MINI vs Volume 0) unresolved.

---

### CL-STORAGE-REC-009: Volume 0:/ and 3:/ Roles Referenced, 3:/ Mapping Unresolved

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-STORAGE-008 (E1), CL-RKO-STORAGE-001 (E3-Old)
**Reasoning:** Both tiers reference 0:/ and 3:/ roles; neither fixes physical mapping.
**Authority:** E3-Old
**Evidence Merged:** E-STORAGE-010, E-STORAGE-027, E-STORAGE-028, E-RKO-STORAGE-001, E-OLD-STORAGE-004, E2-STORAGE-012
**Superseded:** None
**Contradiction:** CONTRADICTION-STORAGE-001 (Volume 3 location) unresolved.

---

### CL-STORAGE-REC-010: Update Filenames Hardcoded On 3:/ Root

**Decision:** UNIQUE
**Source Claims:** CL-OLD-STORAGE-001 (E4)
**Reasoning:** Only E4 details filename list; E3-Old corroborates hardcoded filenames.
**Authority:** E4
**Evidence Merged:** E-OLD-STORAGE-001, E-OLD-STORAGE-004, E-RKO-STORAGE-001
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-011: Update Filename Matching Uses Literal Pool + memcmp

**Decision:** UNIQUE
**Source Claims:** CL-OLD-STORAGE-002 (E4)
**Reasoning:** Only E4 provides literal pool and memcmp loop detail.
**Authority:** E4
**Evidence Merged:** E-OLD-STORAGE-002, E-OLD-STORAGE-003
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-012: Update Path Uses Raw Writes Without Checksums

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-STORAGE-002 (E3-Old), CL-OLD-STORAGE-003 (E4)
**Reasoning:** E3-Old documents raw write path; E4 notes no CRC; E2 confirms chain.
**Authority:** E3-Old
**Evidence Merged:** E-STORAGE-030, E-RKO-STORAGE-002, E-OLD-STORAGE-005, E2-STORAGE-012
**Superseded:** None
**Contradiction:** Update validation conflict noted in `research/old_docs/analysis/documentation_contradictions_map.md` unresolved.

---

### CL-STORAGE-REC-013: U-Disk Bulk Resource Update Copies ZKML

**Decision:** UNIQUE
**Source Claims:** CL-OLD-STORAGE-004 (E4)
**Reasoning:** Only E4 documents the bulk resource update path.
**Authority:** E4
**Evidence Merged:** E-OLD-STORAGE-006
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-014: ext4 Superblock Present But Geometry Invalid

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-STORAGE-013 (E1), CL-STORAGE-014 (E1)
**Reasoning:** E1 claims combine ext4 detection with geometry failure; E0 confirms magic.
**Authority:** E1
**Evidence Merged:** E-STORAGE-014, E-STORAGE-016, E-STORAGE-017, E-STORAGE-034, E-STORAGE-035, `firmware/image/sdcard.work.img`
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-015: Storage Capacity UI Is Inconsistent

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-STORAGE-011 (E1), CL-STORAGE-012 (E1)
**Reasoning:** Both claims refer to capacity UI inconsistencies and failures on larger cards.
**Authority:** E1
**Evidence Merged:** E-STORAGE-009, E-STORAGE-008
**Superseded:** None
**Contradiction:** None

---

### CL-STORAGE-REC-016: USB MSC Device String "W55FA93 SPI Disk"

**Decision:** UNIQUE
**Source Claims:** CL-STORAGE-015 (E1)
**Reasoning:** Single E1 dmesg observation retained as its own claim.
**Authority:** E1
**Evidence Merged:** E-STORAGE-033
**Superseded:** None
**Contradiction:** None
