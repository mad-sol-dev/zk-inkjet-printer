# MMIO Subsystem Reconciliation Decisions

**Date:** 2026-01-05
**Reconciler:** Codex (GPT-5.1)
**Input Tiers:** E0, E3-Old, E4

## Decision Summary

- Total Claims Input: 9
- Merged Claims Output: 6
- EXACT_MATCH merges: 0
- PARTIAL_OVERLAP merges: 4
- UNIQUE kept: 2
- REFUTED: 0

## Claim-by-Claim Decisions

### CL-MMIO-REC-001: GCR_BA Base At 0xB0000000

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-MMIO-001 (E3-Old), CL-OLD-MMIO-001 (E4)
**Reasoning:** Both tiers describe GCR_BA access; BSP provides authoritative base.
**Authority:** E0
**Evidence Merged:** E-RKO-MMIO-001, E-OLD-MMIO-001, E-OLD-MMIO-007, BSP GCR_BA definition
**Superseded:** None
**Contradiction:** None

---

### CL-MMIO-REC-002: GPIO_BA Base And Port Offsets

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-MMIO-003 (E3-Old), CL-OLD-MMIO-003 (E4)
**Reasoning:** E3-Old/E4 offsets align with BSP GPIO_BA definition.
**Authority:** E0
**Evidence Merged:** E-RKO-MMIO-003, E-OLD-MMIO-003, E-OLD-MMIO-004, BSP GPIO_BA definition
**Superseded:** None
**Contradiction:** None

---

### CL-MMIO-REC-003: BLT_BA Base At 0xB100D000

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-MMIO-003 (E3-Old), CL-OLD-MMIO-003 (E4)
**Reasoning:** BSP confirms 0xB100D000 as BLT_BA; E3-Old/E4 show firmware usage.
**Authority:** E0
**Evidence Merged:** E-RKO-MMIO-003, E-OLD-MMIO-003, BSP BLT_BA definition
**Superseded:** None
**Contradiction:** None

---

### CL-MMIO-REC-004: SPI0_BA Base At 0xB800C000 (Not Doorbell)

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-MMIO-002 (E3-Old), CL-OLD-MMIO-002 (E4)
**Reasoning:** BSP defines SPI0_BA at 0xB800C000; doorbell interpretation downgraded.
**Authority:** E0
**Evidence Merged:** E-RKO-MMIO-002, E-OLD-MMIO-002, BSP SPI0_BA definition
**Superseded:** Doorbell/parameter block interpretation from E3-Old/E4.
**Contradiction:** None

---

### CL-MMIO-REC-005: UART_BA Base At 0xB8008000 With No Direct References

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-MMIO-004 (E3-Old), CL-OLD-MMIO-005 (E4)
**Reasoning:** BSP defines UART_BA; E3-Old notes no scalar references.
**Authority:** E0
**Evidence Merged:** E-RKO-MMIO-004, E-OLD-MMIO-006, BSP UART_BA definition
**Superseded:** None
**Contradiction:** None

---

### CL-MMIO-REC-006: 0xB1006800 Mapping Is A False Positive

**Decision:** UNIQUE
**Source Claims:** CL-OLD-MMIO-004 (E4)
**Reasoning:** Only E4 documents the correction.
**Authority:** E4
**Evidence Merged:** E-OLD-MMIO-005
**Superseded:** None
**Contradiction:** None
