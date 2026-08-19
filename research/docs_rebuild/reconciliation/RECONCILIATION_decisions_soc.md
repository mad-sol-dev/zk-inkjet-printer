# SOC Subsystem Reconciliation Decisions

**Date:** 2026-01-04
**Reconciler:** Codex (GPT-5.1)
**Input Tiers:** E0, E1, E2, E3-Old, E3-New, E4

## Decision Summary

- Total Claims Input: 26 (E1=18, E3-Old=2, E3-New=2, E4=4)
- Merged Claims Output: 20
- EXACT_MATCH merges: 2
- PARTIAL_OVERLAP merges: 8
- UNIQUE kept: 8
- REFUTED: 2

**E0 Source Note:** No local `vendor/datasheets/N3290x_Design_Guide_A1.pdf` was found. E0 ground truth uses BSP headers at `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` and the derived `research/findings/n32903_registers.json`.

---

## Claim-by-Claim Decisions

### CL-SOC-REC-001: SoC Identity Is N32903U5DN (U-Serie)

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-SOC-001 (E1), CL-RKO-SOC-002 (E3-Old), CL-OLD-SOC-001 (E4)
**Reasoning:** E1 has strongest physical measurements + memory readout. E3-Old/E4 identify K5DN and no SDRAM, which conflicts and is superseded.
**Authority:** E1
**Evidence Merged:** E-SOC-001/002/005/028; E-RKO-SOC-002 [ghidra-v1]; E-OLD-SOC-001 [ghidra-v1]; E2-SOC-003 (context)
**Superseded:** K5DN variant assertions from E3-Old/E4
**Contradiction:** old_docs/analysis/documentation_contradictions_map.md (SoC identity)

---

### CL-SOC-REC-002: SoC Marking Shows "M5 dwin.com.cn"

**Decision:** MERGE (EXACT_MATCH)
**Source Claims:** CL-SOC-002 (E1), CL-RKO-SOC-001 (E3-Old)
**Reasoning:** Both tiers report the same marking observation.
**Authority:** E1
**Evidence Merged:** E-SOC-031; E-RKO-SOC-001 [ghidra-v1]

---

### CL-SOC-REC-003: Firmware Contains W55FA93/Nuvoton Descriptor Strings

**Decision:** MERGE (EXACT_MATCH)
**Source Claims:** CL-OLD-SOC-002 (E4), CL-RKO-SOC-002 (E3-Old)
**Reasoning:** Both tiers document W55FA93/Nuvoton descriptor strings in firmware.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-SOC-002 [ghidra-v1], E-OLD-SOC-002 [ghidra-v1], E-SOC-003 (dmesg corroboration)

---

### CL-SOC-REC-004: W55FA93 Is Legacy Winbond Naming

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-SOC-003 (E1), CL-SOC-018 (E1)
**Reasoning:** Both claims interpret W55FA93 as legacy naming; merged into one supported statement.
**Authority:** E1
**Evidence Merged:** E-SOC-003/004/031

---

### CL-SOC-REC-005: 8 MB DDR SDRAM In MCP Package

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-SOC-004 (E1), CL-OLD-SOC-004 (E4), CL-RKO-SOC-002 (E3-Old)
**Reasoning:** E1 establishes DDR MCP; E3-Old/E4 assert no SDRAM and are contradicted.
**Authority:** E1
**Evidence Merged:** E-SOC-007/009/016; E-OLD-SOC-004 [ghidra-v1]; E-RKO-SOC-002 [ghidra-v1]
**Superseded:** No-SDRAM assertions from E3-Old/E4
**Contradiction:** old_docs/analysis/documentation_contradictions_map.md (RAM size)

---

### CL-SOC-REC-006: DDR Supply/Reference Voltages

**Decision:** UNIQUE
**Source Claims:** CL-SOC-005 (E1)
**Reasoning:** Hardware measurements only in E1.
**Authority:** E1
**Evidence Merged:** E-SOC-021/023/005

---

### CL-SOC-REC-007: Internal SRAM 8 KB and Boot ROM 16 KB

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-SOC-006 (E1)
**Reasoning:** E1 datasheet evidence; E4 memory map summary aligns but is not a claim.
**Authority:** E1
**Evidence Merged:** E-SOC-008; E-OLD-SOC-005 [ghidra-v1]

---

### CL-SOC-REC-008: ARM926EJ-S Core and 192 MHz Clock

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-SOC-007 (E1), CL-OLD-SOC-003 (E4), CL-RKO-SOC-002 (E3-Old)
**Reasoning:** E1 readout plus E3-Old/E4 CP15 evidence confirm ARM926EJ-S.
**Authority:** E1
**Evidence Merged:** E-SOC-010/018; E-OLD-SOC-003 [ghidra-v1]; E-RKO-SOC-002 [ghidra-v1]

---

### CL-SOC-REC-009: U-Serie vs K-Serie Feature Split

**Decision:** UNIQUE
**Source Claims:** CL-SOC-008 (E1)
**Reasoning:** Only E1 provides series comparison.
**Authority:** E1
**Evidence Merged:** E-SOC-012/013/014/001

---

### CL-SOC-REC-010: N3290x Memory Variants and Part-Number Encoding

**Decision:** UNIQUE
**Source Claims:** CL-SOC-009 (E1)
**Reasoning:** Single-tier datasheet synthesis.
**Authority:** E1
**Evidence Merged:** E-SOC-015/016/017/030

---

### CL-SOC-REC-011: Integrated Multimedia Peripherals

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-SOC-010 (E1), CL-RKO-SOC-002 (E3-Old)
**Reasoning:** E1 datasheet list aligns with E3-Old feature list.
**Authority:** E1
**Evidence Merged:** E-SOC-018; E-RKO-SOC-002 [ghidra-v1]

---

### CL-SOC-REC-012: Dual USB Controllers (Device + Host)

**Decision:** UNIQUE
**Source Claims:** CL-SOC-011 (E1)
**Reasoning:** Only E1 claim; E3-Old includes feature list but no claim.
**Authority:** E1
**Evidence Merged:** E-SOC-018

---

### CL-SOC-REC-013: Multiple Boot Options Supported

**Decision:** UNIQUE
**Source Claims:** CL-SOC-012 (E1)
**Reasoning:** E1 datasheet evidence only.
**Authority:** E1
**Evidence Merged:** E-SOC-019/027

---

### CL-SOC-REC-014: SD0 Interface Pin Mapping

**Decision:** UNIQUE
**Source Claims:** CL-SOC-013 (E1)
**Reasoning:** PCB trace evidence only in E1.
**Authority:** E1
**Evidence Merged:** E-SOC-024/026

---

### CL-SOC-REC-015: MT6701 Encoder Connected To Pin 117

**Decision:** UNIQUE
**Source Claims:** CL-SOC-014 (E1)
**Reasoning:** Single PCB observation; no higher-tier evidence.
**Authority:** E1
**Evidence Merged:** E-SOC-025

---

### CL-SOC-REC-016: Complete LQFP-128 Pinout Documentation

**Decision:** UNIQUE
**Source Claims:** CL-SOC-015 (E1)
**Reasoning:** Only E1 contains full pinout table claim.
**Authority:** E1
**Evidence Merged:** E-SOC-026/027/028

---

### CL-SOC-REC-017: USB PHY Reference Resistor (12 kΩ)

**Decision:** UNIQUE
**Source Claims:** CL-SOC-016 (E1)
**Reasoning:** Hardware measurement only in E1.
**Authority:** E1
**Evidence Merged:** E-SOC-022

---

### CL-SOC-REC-018: N3290x Family Uses MCP Design

**Decision:** UNIQUE
**Source Claims:** CL-SOC-017 (E1)
**Reasoning:** Single datasheet-derived claim.
**Authority:** E1
**Evidence Merged:** E-SOC-029/030

---

### CL-SOC-REC-019: BSP MMIO Base Addresses (Ground Truth)

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKN-SOC-001 (E3-New), CL-RKN-SOC-002 (E3-New)
**Reasoning:** Both E3-New claims derive from BSP extraction; merged into single ground-truth MMIO base claim.
**Authority:** E0
**Evidence Merged:** w55fa93_reg.h (USBD_BA/USB_BA, base defines), E-RKN-SOC-001 (BSP extraction), E2-SOC-016 (methodology)
**Contradiction:** CONTRADICTION-USB-001 (USB base address correction)

---

### CL-SOC-REC-020: K5DN No-SDRAM Variant (Refuted)

**Decision:** REFUTE
**Source Claims:** CL-RKO-SOC-002 (E3-Old), CL-OLD-SOC-001 (E4), CL-OLD-SOC-004 (E4)
**Reasoning:** E1 measurements and DDR evidence establish U5DN with 8 MB DDR; no-SDRAM K5DN hypothesis is wrong.
**Authority:** E1
**Evidence Merged:** E-SOC-001/002/005; E-OLD-SOC-001/004 [ghidra-v1]; E-RKO-SOC-002 [ghidra-v1]
**Superseded:** K5DN/no-SDRAM assertions
**Contradiction:** old_docs/analysis/documentation_contradictions_map.md (RAM size conflict)

