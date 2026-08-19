# HARDWARE Subsystem Reconciliation Decisions

**Date:** 2026-01-05
**Reconciler:** Codex (GPT-5.1)
**Input Tiers:** E0, E1, E2, E3-Old, E3-New, E4

## Decision Summary

- Total Claims Input: 29
- Merged Claims Output: 23
- EXACT_MATCH merges: 4
- PARTIAL_OVERLAP merges: 2
- UNIQUE kept: 16
- REFUTED: 1

## Claim-by-Claim Decisions

### CL-HARDWARE-REC-001: GPIO Usage Split (31 Used, 41 Free)

**Decision:** UNIQUE
**Source Claims:** CL-HARDWARE-001 (E1)
**Reasoning:** Single E1 pinout inventory claim.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-001, E-HARDWARE-002
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-002: Printhead Uses ~30 GPIOs Via CM504B Drivers

**Decision:** UNIQUE
**Source Claims:** CL-HARDWARE-002 (E1)
**Reasoning:** Single E1 hardware trace claim.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-002, E-HARDWARE-019, E-HARDWARE-020
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-003: MT6701 Encoder Uses SoC Pin 117

**Decision:** UNIQUE
**Source Claims:** CL-HARDWARE-003 (E1)
**Reasoning:** Single E1 claim corroborated by SOC pin mapping narrative.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-018, E-SOC-025, E2-HARDWARE-014
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-004: Untested GPIO Set Remains

**Decision:** UNIQUE
**Source Claims:** CL-HARDWARE-004 (E1)
**Reasoning:** Single E1 estimate for untested pins.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-010
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-005: GPB[2-5] Not Configured In Firmware

**Decision:** MERGE (EXACT_MATCH)
**Source Claims:** CL-RKO-HARDWARE-001 (E3-Old), CL-OLD-HARDWARE-001 (E4)
**Reasoning:** Both tiers report GPB[2-5] absent from firmware pin-mux configuration.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-HARDWARE-001, E-OLD-HARDWARE-001
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-006: GPIO Helper Functions Identified

**Decision:** MERGE (EXACT_MATCH)
**Source Claims:** CL-RKO-HARDWARE-003 (E3-Old), CL-OLD-HARDWARE-002 (E4)
**Reasoning:** Both tiers identify the same helper function addresses.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-HARDWARE-003, E-OLD-HARDWARE-002, E-OLD-HARDWARE-003
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-007: Display Uses SPI0 And GPE[8] Control Pin

**Decision:** MERGE (EXACT_MATCH)
**Source Claims:** CL-HARDWARE-005 (E1), CL-HARDWARE-014 (E1)
**Reasoning:** Both E1 claims describe the same SPI0 display wiring.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-007, E-HARDWARE-012, E-HARDWARE-015, E-HARDWARE-017
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-008: Backlight PWM0 On GPD0 (Pin 81)

**Decision:** UNIQUE
**Source Claims:** CL-HARDWARE-006 (E1)
**Reasoning:** Single E1 claim; E4 evidence adds context on JTAG sharing.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-005, E-HARDWARE-016, E-OLD-HARDWARE-005
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-009: UART0 Pins Occupied By Printhead Driver

**Decision:** MERGE (EXACT_MATCH)
**Source Claims:** CL-HARDWARE-013 (E1), CL-OLD-HARDWARE-003 (E4)
**Reasoning:** Both tiers agree UART0 pins are routed to the printhead driver.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-003, E-HARDWARE-020, E-OLD-HARDWARE-004
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-010: JTAG TCK Shares Backlight PWM

**Decision:** UNIQUE
**Source Claims:** CL-OLD-HARDWARE-004 (E4)
**Reasoning:** Only E4 explicitly documents the JTAG/PWM conflict.
**Authority:** E4
**Evidence Merged:** E-OLD-HARDWARE-005
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-011: Touch Panel Uses SoC Touch ADC Pins

**Decision:** UNIQUE
**Source Claims:** CL-HARDWARE-007 (E1)
**Reasoning:** E1 claim directly identifies touch ADC pin usage.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-014, E2-HARDWARE-014
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-012: ADC Architecture For Voltage Monitoring

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-RKO-HARDWARE-004 (E3-Old), CL-HARDWARE-011 (E1)
**Reasoning:** E3-Old defines ADC architecture; E1 UI voltage readings corroborate monitoring usage.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-HARDWARE-004, E-HARDWARE-025, E2-HARDWARE-014
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-013: Display Module Likely ST7789V 18-Pin SPI TFT

**Decision:** UNIQUE
**Source Claims:** CL-HARDWARE-008 (E1)
**Reasoning:** Single E1 hypothesis based on connector match.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-013
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-014: MVDD/MVREF Rails For DDR

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-HARDWARE-009 (E1), CL-HARDWARE-010 (E1)
**Reasoning:** Two related rail measurements merged into a single DDR power statement.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-021, E-HARDWARE-022, E-SOC-021, E-SOC-023
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-015: Printhead Power Uses DC-DC Converters

**Decision:** UNIQUE
**Source Claims:** CL-HARDWARE-012 (E1)
**Reasoning:** Single E1 observation of DC-DC circuitry and nozzle voltages.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-023, E-HARDWARE-024
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-016: I2C On GPB[13-14] Appears Available

**Decision:** UNIQUE
**Source Claims:** CL-HARDWARE-015 (E1)
**Reasoning:** Only E1 lists I2C as available; no corroborating traces yet.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-030
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-017: High-Speed UART GPD[1-4] Are Candidate Pins

**Decision:** UNIQUE
**Source Claims:** CL-HARDWARE-016 (E1)
**Reasoning:** Single E1 availability list; needs validation.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-030
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-018: USB Device Pins Are Wired (Not Unused)

**Decision:** REFUTE
**Source Claims:** CL-HARDWARE-017 (E1)
**Reasoning:** USB-C wiring plus MSC activity contradicts the “unused” assertion.
**Authority:** E4
**Evidence Merged:** E-OLD-HARDWARE-008, E-USB-009, E-USB-010
**Superseded:** E-HARDWARE-031 (USB pins unused)
**Contradiction:** None

---

### CL-HARDWARE-REC-019: GPC[4] Is Free But Boot-Config Constrained

**Decision:** UNIQUE
**Source Claims:** CL-HARDWARE-018 (E1)
**Reasoning:** Single E1 boot-strap constraint note.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-004, E-SOC-027
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-020: MicroSD Slot Uses GPE[2-7]

**Decision:** UNIQUE
**Source Claims:** CL-OLD-HARDWARE-006 (E4)
**Reasoning:** E1 pin mapping corroborates E4 wiring note.
**Authority:** E1
**Evidence Merged:** E-HARDWARE-006, E-SOC-024, E-OLD-HARDWARE-007
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-021: GPB[2-5] Routed To Cartridge Pogo Header

**Decision:** UNIQUE
**Source Claims:** CL-OLD-HARDWARE-005 (E4)
**Reasoning:** Only E4 documents the pogo header routing.
**Authority:** E4
**Evidence Merged:** E-OLD-HARDWARE-006
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-022: Display Controller MMIO Base and GPIO Base

**Decision:** UNIQUE
**Source Claims:** CL-RKO-HARDWARE-002 (E3-Old)
**Reasoning:** Single E3-Old claim, with GPIO base confirmed in BSP.
**Authority:** E3-Old
**Evidence Merged:** E-RKO-HARDWARE-002
**Superseded:** None
**Contradiction:** None

---

### CL-HARDWARE-REC-023: USB Device Controller MMIO Base

**Decision:** UNIQUE
**Source Claims:** CL-RKN-HARDWARE-001 (E3-New)
**Reasoning:** BSP-derived base address is authoritative and stands alone.
**Authority:** E0
**Evidence Merged:** E-RKN-HARDWARE-001
**Superseded:** None
**Contradiction:** None
