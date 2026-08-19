# DISPLAY Subsystem Reconciliation Decisions

**Date:** 2026-01-05
**Reconciler:** Codex (GPT-5.1)
**Input Tiers:** E0, E1-Recent, E3-Old, E4

## Decision Summary

- Total Claims Input: 10
- Merged Claims Output: 7
- EXACT_MATCH merges: 0
- PARTIAL_OVERLAP merges: 4
- UNIQUE kept: 3
- REFUTED: 0

## Claim-by-Claim Decisions

### CL-DISPLAY-REC-001: 2.8 Inch TFT With 18-Pin FFC And SPI0 Wiring

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-DISPLAY-004 (E3-Old), CL-OLD-DISPLAY-001 (E4)
**Reasoning:** E1-Recent wiring details are newer and supersede older pinout notes, but they align on SPI0 usage.
**Authority:** E1-Recent
**Evidence Merged:** E1-Recent report, E-RKO-DISPLAY-004, E-OLD-DISPLAY-001
**Superseded:** None
**Contradiction:** None

---

### CL-DISPLAY-REC-002: Display Controller Identity Unconfirmed (ST7789V or ILI9341)

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-DISPLAY-002 (E3-Old), CL-RKO-DISPLAY-004 (E3-Old)
**Reasoning:** E1-Recent explicitly flags controller ID as unconfirmed; ST7789V claims downgraded to hypothesis.
**Authority:** E1-Recent
**Evidence Merged:** E1-Recent report, E-RKO-DISPLAY-002
**Superseded:** ST7789V-specific verified status from E3-Old.
**Contradiction:** None

---

### CL-DISPLAY-REC-003: SPI0 LCD Command/Data Helpers And D/C Toggle

**Decision:** UNIQUE
**Source Claims:** CL-RKO-DISPLAY-001 (E3-Old)
**Reasoning:** E3-Old Ghidra analysis retained with ghidra-v1 caution.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-DISPLAY-001
**Superseded:** None
**Contradiction:** None

---

### CL-DISPLAY-REC-004: Rendering Primitives Use CASET/RASET/RAMWR

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-DISPLAY-003 (E3-Old), CL-RKO-DISPLAY-005 (E3-Old)
**Reasoning:** Both claims describe rendering primitives; kept as hypothesis pending post-optimization verification.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-DISPLAY-003, E-RKO-DISPLAY-005
**Superseded:** None
**Contradiction:** None

---

### CL-DISPLAY-REC-005: Backlight Is Controlled By PWM0 On GPD0

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-DISPLAY-007 (E3-Old), CL-OLD-DISPLAY-002 (E4)
**Reasoning:** E3-Old and E4 both map backlight to PWM0 on GPD0.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-DISPLAY-007, E-OLD-DISPLAY-002
**Superseded:** None
**Contradiction:** None

---

### CL-DISPLAY-REC-006: Display BLT Engine Base Is 0xB100D000

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-OLD-DISPLAY-003 (E4), CL-RKO-DISPLAY-006 (E3-Old)
**Reasoning:** BSP confirms BLT_BA at 0xB100D000; E3-Old/E4 provide supporting behavior.
**Authority:** E0
**Evidence Merged:** E-OLD-DISPLAY-003, E-RKO-DISPLAY-006, BSP BLT_BA definition
**Superseded:** None
**Contradiction:** None

---

### CL-DISPLAY-REC-007: UI Architecture Includes Touch Input And About Screen

**Decision:** UNIQUE
**Source Claims:** CL-RKO-DISPLAY-006 (E3-Old)
**Reasoning:** Only E3-Old provides UI architecture details.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-DISPLAY-006
**Superseded:** None
**Contradiction:** None
