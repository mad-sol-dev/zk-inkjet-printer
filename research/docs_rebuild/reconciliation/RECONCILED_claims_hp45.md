# HP45 Reconciled Claims (Phase 2C-3)

Authority order: E0 > E3-New > E1-Recent > E1 > E3-Old > E4 (E2 = context only).

---

## CL-HP45-REC-001: HP45 Nozzle Matrix Is 22x14 With 300 Active Nozzles

**Status:** verified
**Confidence:** 0.95
**Authority:** E1

**Statement:** The HP45/HP45SI printhead uses a 22x14 nozzle matrix with 300 active nozzles (308 positions with 8 unused).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-003 (22x14 matrix), E-HP45-004 (300 nozzles)
- **E3-Old:** E-RKO-HP45-002 (matrix, 22 HA, 14 HP) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-002
- E3-Old: CL-RKO-HP45-002 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** None required.

**Tags:** hp45, matrix, nozzles

---

## CL-HP45-REC-002: Nozzles Fire On HA/HP Overlap With 22 Sub-Lines

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** A nozzle fires only when its HA address line and HP primitive line are active together, implemented as 22 sub-lines with a 14-bit HP mask per sub-line.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-001 (HA/HP definitions), E-HP45-002 (overlap firing), E-HP45-024 (22 sub-lines, 14-bit mask)
- **E3-Old:** E-RKO-HP45-001 (22-phase loop expectation) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-001
- E1: CL-HP45-012
- E3-Old: CL-RKO-HP45-001 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Search firmware for a 22-iteration loop applying 14-bit HP masks.

**Tags:** hp45, firing, ha, hp

---

## CL-HP45-REC-003: HA/HP Electrical Timing And Voltage Requirements

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** HA lines use roughly 10-12 V gate drive and HP primitives are pulsed for about 1.5-2 microseconds at roughly 9-13 V.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-019 (HA 10-12 V), E-HP45-020 (HP ~2 us), E-HP45-022 (HP 1.5-2 us, 9-13 V)
- **E3-Old:** E-RKO-HP45-002 (1.8 us at VDD, current draw) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-009
- E1: CL-HP45-010
- E3-Old: CL-RKO-HP45-002 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Capture HA/HP waveforms on the board with a fast oscilloscope.

**Tags:** hp45, timing, voltage

---

## CL-HP45-REC-004: Incorrect HP/HA Sequencing Can Damage Hardware

**Status:** hypothesis
**Confidence:** 0.55
**Authority:** E1

**Statement:** Incorrect sequencing of HA and HP activation may damage FETs or nozzles.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-021 (ordering can destroy FETs/nozzles)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-011

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Verify ordering constraints in the HP45 datasheet or reference schematics.

**Tags:** hp45, safety, timing

---

## CL-HP45-REC-005: Driver Hardware Uses CM504B Level Shifters And Dual MOSFETs

**Status:** supported
**Confidence:** 0.85
**Authority:** E3-Old

**Statement:** The printhead driver uses six CM504B level shifters and seven dual N-MOSFET packages to interface the SoC to HP45 signals.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-014 (six CM504B), E-HP45-015 (pin set)
- **E3-Old:** E-RKO-HP45-005 (6x CM504B, 7x dual MOSFETs) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-007
- E3-Old: CL-RKO-HP45-005

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Validate CM504B and MOSFET markings on the PCB.

**Tags:** hp45, drivers, cm504b, mosfet

---

## CL-HP45-REC-006: HA Lines Use CM504B, HP Lines Use High-Current Drivers

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** HA address lines are driven by CM504B level shifters, while HP primitives are driven by separate high-current driver stages.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-010 (CM504B on HA), E-HP45-011 (HP needs high-current), E-HP45-013 (CM504B current limits)
- **E3-Old:** E-RKO-HP45-004 (HP primitives via MOSFETs) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-005
- E1: CL-HP45-006
- E3-Old: CL-RKO-HP45-004 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Identify the exact MOSFET driver ICs connected to HP lines.

**Tags:** hp45, ha, hp, drivers

---

## CL-HP45-REC-007: HA Address Line Mapping Uses GPC/GPE/GPB/GPD

**Status:** supported
**Confidence:** 0.75
**Authority:** E3-Old

**Statement:** HA0-HA21 are mapped through CM504B ICs to SoC GPIOs on GPC0-15, GPE0-1, GPB15, and GPD9-11 (LVDATA bus reuse).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-HP45-003 (HA mapping) [ghidra-v1]
- **E4:** E-OLD-HP45-001 (LVDATA bus to HA lines) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-HP45-003
- E4: CL-OLD-HP45-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Continuity-probe at least two HA lines from GPC to the printhead connector.

**Tags:** hp45, ha, gpio, pinout

---

## CL-HP45-REC-008: HP Primitive Line Mapping Uses GPA/GPD/GPB

**Status:** supported
**Confidence:** 0.75
**Authority:** E3-Old

**Statement:** HP0-HP13 primitives are mapped to SoC GPIOs on GPA0-11, GPD5-8, and GPB15 via CM504B/MOSFET stages.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-016 (IC1 mapping), E-HP45-017 (IC2 mapping), E-HP45-018 (HP order)
- **E3-Old:** E-RKO-HP45-004 (HP mapping) [ghidra-v1]
- **E4:** E-OLD-HP45-002 (GPA/GPD/GPB mapping) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E1: CL-HP45-008
- E3-Old: CL-RKO-HP45-004
- E4: CL-OLD-HP45-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Trace two HP lines to confirm GPA and GPD assignments.

**Tags:** hp45, hp, gpio, pinout

---

## CL-HP45-REC-009: C10X And CTSR Feedback Pins Are Exposed

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** The printhead connector exposes C10X and CTSR as separate feedback/sense pins.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-006 (C10X/CTSR separate), E-HP45-008 (connector mapping)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-003

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Trace C10X/CTSR to ADC input nets.

**Tags:** hp45, feedback, pins

---

## CL-HP45-REC-010: HP/VDD Pin Pairs Follow A Repeating Pattern

**Status:** supported
**Confidence:** 0.70
**Authority:** E1

**Statement:** The FCC connector interleaves VDD and HP pins in a repeating VDD-HP pattern for HP01 through HP13.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-009 (FCC mapping)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-004

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Verify FCC pinout with continuity checks from VDD rails to HP pads.

**Tags:** hp45, connector, vdd

---

## CL-HP45-REC-011: VADJ Rail Is About 9.09 V For Printhead

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** The printhead VADJ rail is measured at about 9.09 V (distinct from VIN at about 7.97 V).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-025 (VIN 7.97 V, VADJ 9.09 V)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-013

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Measure VADJ during print firing to confirm stability.

**Tags:** hp45, power, vadj

---

## CL-HP45-REC-012: ADC Channels 0/1 Are Unused In Firmware

**Status:** supported
**Confidence:** 0.70
**Authority:** E1

**Statement:** Firmware does not call adc_read_channel for channels 0 or 1.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-026 (no adc_read_channel for 0/1)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-014

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Re-run call-site enumeration in the optimized Ghidra project.

**Tags:** hp45, adc, firmware

---

## CL-HP45-REC-013: MT6701 Encoder Connects To SoC Pin 117

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** The MT6701 encoder output is wired to SoC pin 117 (GPE[10]/NALE).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-027 (pin 117 note), E-HP45-028 (trace line)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-015

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** None required.

**Tags:** hp45, encoder, mt6701

---

## CL-HP45-REC-014: Encoder Value Is Displayed On About Screen

**Status:** supported
**Confidence:** 0.70
**Authority:** E1

**Statement:** The About screen shows an encoder status and numeric value (e.g., "Encoder OK | 66602").

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HP45-029 (About screen encoder value)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HP45-016

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Rotate the encoder and confirm value changes.

**Tags:** hp45, encoder, ui

---

## CL-HP45-REC-015: Firmware Strings Reference Nozzle Voltage And HA/HP Counts

**Status:** supported
**Confidence:** 0.65
**Authority:** E3-Old

**Statement:** Firmware contains strings and scalar values consistent with nozzle voltage monitoring and 22/14 matrix parameters, but code paths remain unverified.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-HP45-006 (Nozzle Voltage string, scalar 22) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-HP45-006

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Re-run string and scalar analysis in optimized Ghidra and link to concrete functions.

**Tags:** hp45, firmware, strings
