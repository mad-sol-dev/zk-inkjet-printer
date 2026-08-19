# USB Subsystem Reconciliation Decisions

**Date:** 2026-01-04
**Reconciler:** Codex (GPT-5.1)
**Input Tiers:** E0, E1, E2, E3-Old, E4

## Decision Summary

- Total Claims Input: 22 (E1=17, E3-Old=3, E4=2)
- Merged Claims Output: 21
- EXACT_MATCH merges: 3
- PARTIAL_OVERLAP merges: 8
- UNIQUE kept: 8
- REFUTED: 2

**E0 Source Note:** The requested `vendor/bsp/.../N329xx_USBD.h` is not present in the repo. E0 ground truth was taken from `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (USBD_BA/USB_BA=0xB1008000, endpoint register names).

---

## Claim-by-Claim Decisions

### CL-USB-REC-001: USB VID/PID Identity (0416:0093)

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-USB-001 (E1), CL-RKO-USB-003 (E3-Old)
**Reasoning:** E1 provides direct enumeration logs; E3-Old references VID/PID from descriptor analysis.
**Authority:** E1
**Evidence Merged:** E-USB-001, E-USB-006; E-RKO-USB-003 [ghidra-v1]

---

### CL-USB-REC-002: USB Descriptor Strings (Manufacturer/Product/Serial)

**Decision:** MERGE (EXACT_MATCH)
**Source Claims:** CL-USB-002 (E1), CL-RKO-USB-003 (E3-Old)
**Reasoning:** Both tiers agree on manufacturer/product/serial strings.
**Authority:** E1
**Evidence Merged:** E-USB-002/003/004; E-RKO-USB-003 [ghidra-v1]

---

### CL-USB-REC-003: Firmware Descriptor Block Contains W55FA93/Nuvoton Strings

**Decision:** MERGE (EXACT_MATCH)
**Source Claims:** CL-OLD-USB-001 (E4), CL-RKO-USB-002 (E3-Old)
**Reasoning:** Both claim firmware contains W55FA93/Nuvoton strings.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-USB-002 [ghidra-v1], E-OLD-USB-001 [ghidra-v1]

---

### CL-USB-REC-004: SCSI Device String Identifies "W55FA93 SPI Disk"

**Decision:** UNIQUE
**Source Claims:** CL-USB-003 (E1)
**Reasoning:** Only E1 dmesg evidence directly supports the SCSI string.
**Authority:** E1
**Evidence Merged:** E-USB-005

---

### CL-USB-REC-005: USB Mass Storage Class Operation

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-USB-006 (E1), CL-RKO-USB-001 (E3-Old)
**Reasoning:** E1 logs prove MSC; E3-Old confirms device mode vs host and MINI workflow.
**Authority:** E1
**Evidence Merged:** E-USB-009/010; E-RKO-USB-001 [ghidra-v1]; E2-USB-006 (context)

---

### CL-USB-REC-006: MSC Capacity (64 MiB)

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-USB-007 (E1), CL-RKO-USB-001 (E3-Old)
**Reasoning:** E1 provides block count; E3-Old notes 64MB MINI volume.
**Authority:** E1
**Evidence Merged:** E-USB-011; E-RKO-USB-001 [ghidra-v1]; E2-USB-006 (context)

---

### CL-USB-REC-007: Single Partition Exposed (sda1)

**Decision:** UNIQUE
**Source Claims:** CL-USB-008 (E1)
**Reasoning:** Only E1 dmesg evidence reports sda1.
**Authority:** E1
**Evidence Merged:** E-USB-012

---

### CL-USB-REC-008: LBA Access Restriction Behavior

**Decision:** UNIQUE
**Source Claims:** CL-USB-009 (E1)
**Reasoning:** LBA restriction evidence is only in E1 logs/analysis.
**Authority:** E1
**Evidence Merged:** E-USB-015/016/017/018

---

### CL-USB-REC-009: Dual-Mode Operation (MSC vs IBR-Boot)

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-USB-004 (E1), CL-RKO-USB-003 (E3-Old)
**Reasoning:** E1 confirms PIDs; E3-Old adds IBR endpoint details.
**Authority:** E1
**Evidence Merged:** E-USB-007/008; E-RKO-USB-003 [ghidra-v1]; E2-USB-011

---

### CL-USB-REC-010: IBR-Boot Mode Characteristics

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-USB-005 (E1)
**Reasoning:** E1 provides WPMUSB + fake size; E2 adds context.
**Authority:** E1
**Evidence Merged:** E-USB-008; E2-USB-011

---

### CL-USB-REC-011: USB Device Controller Base Address (BSP)

**Decision:** REFUTE E1/E3-Old, ACCEPT E0
**Source Claims:** CL-USB-010 (E1), CL-RKO-USB-002 (E3-Old)
**Conflict:** E1/E3-Old claim 0xB8007000, E0 BSP defines 0xB1008000
**Reasoning:** BSP is ground truth; contradiction file documents no firmware refs for 0xB8007000; 0xB8007000 is PWM_BA.
**Authority:** E0
**Evidence Merged:** w55fa93_reg.h (USBD_BA/USB_BA=0xB1008000)
**Superseded:** E-USB-019, E-RKO-USB-002 base mapping
**Contradiction:** Resolves CONTRADICTION-USB-001

---

### CL-USB-REC-012: UDC Register Names (BSP Ground Truth)

**Decision:** MERGE (EXACT_MATCH)
**Source Claims:** CL-USB-014 (E1)
**Reasoning:** E1 register names match BSP header names; E0 supersedes.
**Authority:** E0
**Evidence Merged:** w55fa93_reg.h (EPA_CFG/EPB_CFG/EP*_MPS/EP*_START/END)

---

### CL-USB-REC-013: SPI Flash As MSC Backend (Inference)

**Decision:** UNIQUE
**Source Claims:** CL-USB-011 (E1)
**Reasoning:** Inference only present in E1 analysis.
**Authority:** E1
**Evidence Merged:** E-USB-005, E-USB-021

---

### CL-USB-REC-014: USB-ISP/TurboWriter Support In SoC Family

**Decision:** UNIQUE
**Source Claims:** CL-USB-012 (E1)
**Reasoning:** Single analysis entry; no higher-tier artifacts available.
**Authority:** E1
**Evidence Merged:** E-USB-022

---

### CL-USB-REC-015: CDC Template Available In Related BSP

**Decision:** UNIQUE
**Source Claims:** CL-USB-013 (E1)
**Reasoning:** CDC template evidence exists only in E1; N9H26 BSP not in repo.
**Authority:** E1
**Evidence Merged:** E-USB-023; E2-USB-011 (context)

---

### CL-USB-REC-016: Descriptor Patch At 0x275140 Bricked Device

**Decision:** UNIQUE
**Source Claims:** CL-USB-015 (E1)
**Reasoning:** Only E1 test result documents the brick.
**Authority:** E1
**Evidence Merged:** E-USB-025; E2-USB-011 (context)

---

### CL-USB-REC-017: APP.bin Extension Preserves MSC

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-USB-016 (E1), CL-RKO-USB-002 (E3-Old)
**Reasoning:** E1 confirms successful padding; E3-Old notes no trailing padding, supporting extensibility inference.
**Authority:** E1
**Evidence Merged:** E-USB-026; E-RKO-USB-002 [ghidra-v1]

---

### CL-USB-REC-018: UDC Init Candidates Require Revalidation

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-USB-017 (E1), CL-RKO-USB-002 (E3-Old)
**Reasoning:** E1 lists candidate functions; E3-Old maps them to incorrect base. Needs revalidation against BSP base.
**Authority:** E1
**Evidence Merged:** E-USB-028; E-RKO-USB-002 [ghidra-v1]; E2-USB-011 (context)

---

### CL-USB-REC-019: Descriptor Location Mapping (Refuted)

**Decision:** REFUTE (E3-Old)
**Source Claims:** CL-RKO-USB-003 (E3-Old)
**Conflict:** E3-Old offset mapping conflicts with E1 brick test at 0x275140.
**Authority:** E1
**Evidence Merged:** E-USB-025 (brick test); E2-USB-011 (base offset mismatch)
**Superseded:** E-RKO-USB-003 descriptor offsets

---

### CL-USB-REC-020: USB Update Workflow (MINI Volume + Hold-Key)

**Decision:** UNIQUE
**Source Claims:** CL-RKO-USB-001 (E3-Old)
**Reasoning:** Detailed USB update workflow exists only in E3-Old with E2 context.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-USB-001 [ghidra-v1]; E2-USB-006

---

### CL-USB-REC-021: USB-C Wiring And Detect Pin

**Decision:** UNIQUE
**Source Claims:** CL-OLD-USB-002 (E4)
**Reasoning:** Hardware wiring observation only in old_docs.
**Authority:** E4
**Evidence Merged:** E-OLD-USB-002, E-OLD-USB-003 [ghidra-v1]

