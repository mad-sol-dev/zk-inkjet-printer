# BOOT Subsystem Reconciliation Decisions

**Date:** 2026-01-05
**Reconciler:** Codex (GPT-5.1)
**Input Tiers:** E0, E1, E2, E3-Old, E3-New, E4

## Decision Summary

- Total Claims Input: 26 (E1 file contains 16 claims; prompt listed 13)
- Merged Claims Output: 22
- EXACT_MATCH merges: 0
- PARTIAL_OVERLAP merges: 6
- UNIQUE kept: 16
- REFUTED: 0

## Claim-by-Claim Decisions

### CL-BOOT-REC-001: SD Card Required for Boot

**Decision:** UNIQUE
**Source Claims:** CL-BOOT-001 (E1)
**Reasoning:** Single direct observation in E1.
**Authority:** E1
**Evidence Merged:** E-BOOT-002
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-002: Boot Chain IBR -> BOOT.bin -> APP.bin

**Decision:** UNIQUE
**Source Claims:** CL-BOOT-002 (E1)
**Reasoning:** E1 chain assembled from multiple boot sequence observations.
**Authority:** E1
**Evidence Merged:** E-BOOT-003, E-BOOT-005, E-BOOT-006, E-BOOT-007, E-BOOT-012
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-003: BOOT.bin Header at SD Offset 0x200 (ZBWp1WBZ)

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-BOOT-003 (E1), CL-BOOT-006 (E1), CL-RKO-BOOT-005 (E3-Old)
**Reasoning:** All sources identify ZBWp1WBZ at offset 0x200; E3-Old claim also includes update workflow and is split.
**Authority:** E0
**Evidence Merged:** E-BOOT-001, E-BOOT-010, E-RKO-BOOT-005, `firmware/image/sdcard.work.img` offset 0x200
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-004: BOOT.bin Is a Small ARM Loader (~12.7 KB)

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-BOOT-015 (E1), CL-RKO-BOOT-005 (E3-Old)
**Reasoning:** E1 describes loader characteristics; E3-Old confirms exact size; E0 file size is authoritative.
**Authority:** E0
**Evidence Merged:** E-BOOT-026, E-BOOT-027, E-RKO-BOOT-005, `firmware/boot/ZK-INKJET-NANO-BOOT.bin` size
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-005: BOOT.bin Can Load APP.bin From FAT

**Decision:** UNIQUE
**Source Claims:** CL-BOOT-004 (E1)
**Reasoning:** Single analytical claim in E1.
**Authority:** E1
**Evidence Merged:** E-BOOT-008
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-006: SoC Boot ROM Supports SD/NAND/SPI/USB

**Decision:** UNIQUE
**Source Claims:** CL-BOOT-005 (E1)
**Reasoning:** Single documented list of boot modes in E1.
**Authority:** E1
**Evidence Merged:** E-BOOT-004
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-007: APP.bin Located at SD Offset 0x100000 With ARM IVT

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-BOOT-007 (E1), CL-RKO-BOOT-005 (E3-Old)
**Reasoning:** E1/E3-Old agree on raw offset and IVT; E0 SD image confirms.
**Authority:** E0
**Evidence Merged:** E-BOOT-011, E-BOOT-028, E-RKO-BOOT-005, `firmware/image/sdcard.work.img` offset 0x100000
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-008: APP.bin Loads to RAM Address 0x03000000

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-BOOT-008 (E1), CL-RKO-BOOT-004 (E3-Old)
**Reasoning:** E1 states load address; E3-Old supports via update copy routine analysis.
**Authority:** E1
**Evidence Merged:** E-BOOT-012, E-RKO-BOOT-004
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-009: BOOT Enables MMU/Cache and Identity Maps RAM

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-BOOT-004 (E3-Old), CL-OLD-BOOT-004 (E4)
**Reasoning:** E3-Old provides mapping details; E4 corroborates CP15 cache/MMU control sequence.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-BOOT-004, E-OLD-BOOT-004
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-010: SDLoader and Execute Image Sector Ranges

**Decision:** UNIQUE
**Source Claims:** CL-BOOT-009 (E1)
**Reasoning:** Single TurboWriter map statement in E1.
**Authority:** E1
**Evidence Merged:** E-BOOT-013, E-BOOT-014
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-011: MINI FAT Appears at ~711 MB With No Partition Table

**Decision:** UNIQUE
**Source Claims:** CL-BOOT-010 (E1)
**Reasoning:** Single E1 observation pair about MINI FAT location and lack of partition table.
**Authority:** E1
**Evidence Merged:** E-BOOT-015, E-BOOT-016
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-012: Update Workflow Reads FAT and Writes Raw Offsets

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-BOOT-011 (E1), CL-BOOT-012 (E1), CL-RKO-BOOT-005 (E3-Old)
**Reasoning:** E1 describes scanning and FatFS reads; E3-Old adds raw write path and no-checksum note. E3-Old claim is split across layout and update workflow.
**Authority:** E3-Old
**Evidence Merged:** E-BOOT-019, E-BOOT-020, E-BOOT-024, E-RKO-BOOT-005
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-013: TurboWriter Builds Bootable SD Images

**Decision:** UNIQUE
**Source Claims:** CL-BOOT-013 (E1)
**Reasoning:** Single E1 workflow note on TurboWriter usage.
**Authority:** E1
**Evidence Merged:** E-BOOT-022, E-BOOT-023
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-014: APP.bin Offset Differs From TurboWriter Default

**Decision:** UNIQUE
**Source Claims:** CL-BOOT-014 (E1)
**Reasoning:** Inference from observed offsets; no counter-evidence.
**Authority:** E1
**Evidence Merged:** E-BOOT-011, E-BOOT-025
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-015: APP.bin is a Proprietary Resource Container

**Decision:** UNIQUE
**Source Claims:** CL-BOOT-016 (E1)
**Reasoning:** E1 observation + interpretation of APP.bin content.
**Authority:** E1
**Evidence Merged:** E-BOOT-028, E-BOOT-029
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-016: Firmware Uses ARM/Thumb Mixed-Mode Code

**Decision:** UNIQUE
**Source Claims:** CL-RKN-BOOT-001 (E3-New)
**Reasoning:** Post-optimization disassembly confirms mixed ARM/Thumb regions; E2 explains methodology shift.
**Authority:** E3-New
**Evidence Merged:** E-RKN-BOOT-001, E2-BOOT-015
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-017: Upgrade Orchestrator and Message Handler Table

**Decision:** UNIQUE
**Source Claims:** CL-RKO-BOOT-001 (E3-Old)
**Reasoning:** Single E3-Old finding; no higher-tier evidence yet.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-BOOT-001, E2-BOOT-015
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-018: Upgrade UI Handlers Identified in Dispatch Table

**Decision:** UNIQUE
**Source Claims:** CL-RKO-BOOT-002 (E3-Old)
**Reasoning:** Single E3-Old finding with dispatch table evidence; requires re-validation post-optimization.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-BOOT-002, E2-BOOT-015
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-019: Additional Firmware Functions Need Verification

**Decision:** UNIQUE
**Source Claims:** CL-RKO-BOOT-003 (E3-Old)
**Reasoning:** Hypothesis-level E3-Old findings retained for future validation.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-BOOT-003, E2-BOOT-015
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-020: BOOT.bin Initializes CPU Modes and Stacks

**Decision:** UNIQUE
**Source Claims:** CL-OLD-BOOT-001 (E4)
**Reasoning:** Single E4 claim from BOOT.bin analysis.
**Authority:** E4
**Evidence Merged:** E-OLD-BOOT-001
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-021: BOOT.bin Relocates Vectors Before Branching

**Decision:** UNIQUE
**Source Claims:** CL-OLD-BOOT-002 (E4)
**Reasoning:** Single E4 claim from BOOT.bin relocation analysis.
**Authority:** E4
**Evidence Merged:** E-OLD-BOOT-002
**Superseded:** None
**Contradiction:** None

---

### CL-BOOT-REC-022: BOOT.bin Issues Display Init Command IDs

**Decision:** UNIQUE
**Source Claims:** CL-OLD-BOOT-003 (E4)
**Reasoning:** Hypothesis-level E4 display init sequence evidence.
**Authority:** E4
**Evidence Merged:** E-OLD-BOOT-003
**Superseded:** None
**Contradiction:** None
