# HP45 Subsystem Reconciliation Decisions

**Date:** 2026-01-05
**Reconciler:** Codex (GPT-5.1)
**Input Tiers:** E0, E1, E2, E3-Old, E4

## Decision Summary

- Total Claims Input: 24
- Merged Claims Output: 15
- EXACT_MATCH merges: 0
- PARTIAL_OVERLAP merges: 8
- UNIQUE kept: 7
- REFUTED: 0

## Claim-by-Claim Decisions

### CL-HP45-REC-001: HP45 Nozzle Matrix Is 22x14 With 300 Active Nozzles

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-HP45-002 (E1), CL-RKO-HP45-002 (E3-Old)
**Reasoning:** Both tiers describe the same matrix geometry and nozzle count.
**Authority:** E1
**Evidence Merged:** E-HP45-003, E-HP45-004, E-RKO-HP45-002
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-002: Nozzles Fire On HA/HP Overlap With 22 Sub-Lines

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-HP45-001 (E1), CL-HP45-012 (E1), CL-RKO-HP45-001 (E3-Old)
**Reasoning:** HA/HP overlap plus 22-phase loop aligns across E1 and E3-Old.
**Authority:** E1
**Evidence Merged:** E-HP45-001, E-HP45-002, E-HP45-024, E-RKO-HP45-001
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-003: HA/HP Electrical Timing And Voltage Requirements

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-HP45-009 (E1), CL-HP45-010 (E1), CL-RKO-HP45-002 (E3-Old)
**Reasoning:** E1 timing/voltage specs align with datasheet-driven E3-Old details.
**Authority:** E1
**Evidence Merged:** E-HP45-019, E-HP45-020, E-HP45-022, E-RKO-HP45-002
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-004: Incorrect HP/HA Sequencing Can Damage Hardware

**Decision:** UNIQUE
**Source Claims:** CL-HP45-011 (E1)
**Reasoning:** Single analysis statement retained as hypothesis.
**Authority:** E1
**Evidence Merged:** E-HP45-021
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-005: Driver Hardware Uses CM504B Level Shifters And Dual MOSFETs

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-HP45-007 (E1), CL-RKO-HP45-005 (E3-Old)
**Reasoning:** Both tiers agree on the CM504B + dual MOSFET hardware set.
**Authority:** E3-Old
**Evidence Merged:** E-HP45-014, E-HP45-015, E-RKO-HP45-005
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-006: HA Lines Use CM504B, HP Lines Use High-Current Drivers

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-HP45-005 (E1), CL-HP45-006 (E1), CL-RKO-HP45-004 (E3-Old)
**Reasoning:** E1 distinguishes HA vs HP drivers; E3-Old adds MOSFET context.
**Authority:** E1
**Evidence Merged:** E-HP45-010, E-HP45-011, E-HP45-013, E-RKO-HP45-004
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-007: HA Address Line Mapping Uses GPC/GPE/GPB/GPD

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-HP45-003 (E3-Old), CL-OLD-HP45-001 (E4)
**Reasoning:** E3-Old mapping and E4 LVDATA note agree on GPC/GPE usage.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-HP45-003, E-OLD-HP45-001
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-008: HP Primitive Line Mapping Uses GPA/GPD/GPB

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-HP45-008 (E1), CL-RKO-HP45-004 (E3-Old), CL-OLD-HP45-002 (E4)
**Reasoning:** All tiers map HP lines to GPA/GPD/GPB pins.
**Authority:** E3-Old
**Evidence Merged:** E-HP45-016, E-HP45-017, E-HP45-018, E-RKO-HP45-004, E-OLD-HP45-002
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-009: C10X And CTSR Feedback Pins Are Exposed

**Decision:** UNIQUE
**Source Claims:** CL-HP45-003 (E1)
**Reasoning:** Single E1 pinout observation.
**Authority:** E1
**Evidence Merged:** E-HP45-006, E-HP45-008
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-010: HP/VDD Pin Pairs Follow A Repeating Pattern

**Decision:** UNIQUE
**Source Claims:** CL-HP45-004 (E1)
**Reasoning:** Single PCB trace list in E1.
**Authority:** E1
**Evidence Merged:** E-HP45-009
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-011: VADJ Rail Is About 9.09 V For Printhead

**Decision:** UNIQUE
**Source Claims:** CL-HP45-013 (E1)
**Reasoning:** Single board measurement.
**Authority:** E1
**Evidence Merged:** E-HP45-025
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-012: ADC Channels 0/1 Are Unused In Firmware

**Decision:** UNIQUE
**Source Claims:** CL-HP45-014 (E1)
**Reasoning:** Single analysis statement.
**Authority:** E1
**Evidence Merged:** E-HP45-026
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-013: MT6701 Encoder Connects To SoC Pin 117

**Decision:** UNIQUE
**Source Claims:** CL-HP45-015 (E1)
**Reasoning:** PCB trace evidence is direct.
**Authority:** E1
**Evidence Merged:** E-HP45-027, E-HP45-028
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-014: Encoder Value Is Displayed On About Screen

**Decision:** UNIQUE
**Source Claims:** CL-HP45-016 (E1)
**Reasoning:** Single UI observation.
**Authority:** E1
**Evidence Merged:** E-HP45-029
**Superseded:** None
**Contradiction:** None

---

### CL-HP45-REC-015: Firmware Strings Reference Nozzle Voltage And HA/HP Counts

**Decision:** UNIQUE
**Source Claims:** CL-RKO-HP45-006 (E3-Old)
**Reasoning:** E3-Old Ghidra findings retained with ghidra-v1 caution.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-HP45-006
**Superseded:** None
**Contradiction:** None
