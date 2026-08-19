# HP45 Claims

Propositional claims synthesized from evidence. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## Matrix Architecture & Pinout

### ⚠️ CL-HP45-001: Nozzle firing requires HA and HP overlap
**Claim:** A nozzle fires only when an HA address line and an HP primitive line are active at the same time.

**Evidence:**
- E-HP45-001: Defines HA as address lines and HP as primitive lines.
- E-HP45-002: States a nozzle fires only when both are active.

**Status:** ⚠️ Supported (two consistent analysis statements)

**Cross-Reference:** CL-HARDWARE-002 (printhead GPIO allocation)

**Next Tests:** Capture HA/HP waveforms during printing to confirm simultaneous activation.

---

### ✅ CL-HP45-002: HP45/HP45SI uses a 22×14 matrix with 300 active nozzles
**Claim:** The HP45/HP45SI printhead is organized as a 22×14 matrix that yields 300 active nozzles (308 positions with 8 unused).

**Evidence:**
- E-HP45-003: States the 22×14 matrix structure.
- E-HP45-004: Provides the 300-nozzle count from the matrix.

**Status:** ✅ Verified (datasheet-backed structural specification)

**Cross-Reference:** CL-HARDWARE-002 (printhead GPIO allocation)

**Next Tests:** None required - conclusively established.

---

### ⚠️ CL-HP45-003: C10X and CTSR are exposed as separate feedback pins
**Claim:** The HP45 connector exposes C10X and CTSR as separate feedback/sense pins.

**Evidence:**
- E-HP45-006: Notes C10X and CTSR are separate pins consistent with feedback functions.
- E-HP45-008: PCB trace line lists C10X and CTSR on the connector map.

**Status:** ⚠️ Supported (PCB trace plus corroborating analysis)

**Cross-Reference:** CL-SOC-025 (MT6701 connection mapping)

**Next Tests:** Measure continuity from C10X/CTSR to ADC input nets to confirm sensing path.

---

### ⚠️ CL-HP45-004: HP/VDD pin pairs are routed through the FCC connector
**Claim:** The FCC connector groups VDD and HP pins in a repeating VDD–HP pattern for HP01 through HP13.

**Evidence:**
- E-HP45-009: FCC connector line lists VDD interleaved with HP01–HP13.

**Status:** ⚠️ Supported (single PCB trace line)

**Cross-Reference:** CL-HARDWARE-002 (printhead GPIO allocation)

**Next Tests:** Verify FCC connector pinout with continuity tests from VDD rails to HP pads.

---

## Driver IC Implementation

### ⚠️ CL-HP45-005: CM504B level shifters are used for HA lines
**Claim:** CM504B (CD4504B) level shifters are used to drive HA address lines, not HP primitives.

**Evidence:**
- E-HP45-010: States CM504B carries HA lines.
- E-HP45-012: Identifies CM504B as a 6-channel level shifter.
- E-HP45-013: Notes CM504B can only source a few mA, matching HA gate drive use.

**Status:** ⚠️ Supported (analysis aligned with datasheet capability)

**Cross-Reference:** CL-HARDWARE-002 (printhead uses CM504B GPIOs)

**Next Tests:** Confirm HA net connections from CM504B outputs to the cartridge connector with a continuity sweep.

---

### ⚠️ CL-HP45-006: HP primitives are driven by separate high-current stages
**Claim:** HP primitive lines are driven by separate high-current driver stages rather than CM504B level shifters.

**Evidence:**
- E-HP45-011: States HP lines require separate high-current drivers.
- E-HP45-023: Notes primitives require hundreds of mA per active strand.

**Status:** ⚠️ Supported (analysis plus current requirement statement)

**Cross-Reference:** CL-HARDWARE-002 (printhead GPIO allocation)

**Next Tests:** Identify the high-current driver ICs or MOSFET arrays connected to HP lines on the PCB.

---

### ⚠️ CL-HP45-007: Six CM504B ICs are used for printhead control
**Claim:** The printhead driver stage uses six CM504B ICs, each with standard A–F channel pins plus VCC/VDD and SELECT.

**Evidence:**
- E-HP45-014: States six ICs are used for printhead control.
- E-HP45-015: Lists the CM504B pin set.

**Status:** ⚠️ Supported (single-session analysis plus pin list)

**Cross-Reference:** CL-HARDWARE-002 (printhead uses 30 GPIOs via CM504B)

**Next Tests:** Verify CM504B footprints and pin labels on the PCB against the listed pin set.

---

### ⚠️ CL-HP45-008: IC1/IC2 use GPA/GPD GPIOs for printhead control
**Claim:** CM504B IC1 and IC2 map printhead control signals to GPA/GPD GPIOs (e.g., GPA0 and GPA6 are used on AIN pins).

**Evidence:**
- E-HP45-016: IC1 AIN uses SoC GPA0.
- E-HP45-017: IC2 AIN uses SoC GPA6.
- E-HP45-018: IC2 ordering aligns HP06–HP09 in sequence.

**Status:** ⚠️ Supported (PCB mapping plus logical ordering)

**Cross-Reference:** CL-HARDWARE-002 (printhead GPIO usage)

**Next Tests:** Trace IC1/IC2 AIN/BIN/CIN/DIN pins to SoC pads and confirm GPIO port assignments.

---

## Nozzle Firing Control

### ✅ CL-HP45-009: HA address lines use ~10–12 V gate drive
**Claim:** HA address lines are driven at approximately 10–12 V to open the FET gates for a nozzle row.

**Evidence:**
- E-HP45-019: Specifies HA drive at 10–12 V.

**Status:** ✅ Verified (datasheet-backed voltage requirement)

**Cross-Reference:** CL-HARDWARE-002 (printhead driver allocation)

**Next Tests:** None required - conclusively established.

---

### ✅ CL-HP45-010: HP primitives use short high-voltage pulses
**Claim:** HP primitive lines are pulsed for roughly 1.5–2 µs at about 9–13 V to fire selected nozzles.

**Evidence:**
- E-HP45-020: States ~2 µs pulses at 10–12 V.
- E-HP45-022: States ~1.5–2 µs pulses at 9–13 V after ~1 µs delay.

**Status:** ✅ Verified (datasheet-aligned pulse specs)

**Cross-Reference:** CL-HARDWARE-002 (printhead driver allocation)

**Next Tests:** Capture HP line pulse widths on the board during printing with a fast oscilloscope.

---

### 🔬 CL-HP45-011: Incorrect sequencing can damage FETs or nozzles
**Claim:** Incorrect sequencing of HP/HA activation can damage the FETs or the printhead nozzles.

**Evidence:**
- E-HP45-021: States that other ordering can destroy FETs or nozzles.

**Status:** 🔬 Hypothesis (single analysis statement)

**Cross-Reference:** CL-HARDWARE-002 (printhead driver allocation)

**Next Tests:** Review HP45 reference schematics or datasheet notes for explicit ordering constraints.

---

### ⚠️ CL-HP45-012: Each print line is emitted as 22 sub-lines with 14-bit HP masks
**Claim:** A single print line is emitted as 22 sub-lines, each activating a 14-bit HP pattern for a given HA address.

**Evidence:**
- E-HP45-024: Describes 22 sub-lines and a 14-bit pattern per sub-line.

**Status:** ⚠️ Supported (single analysis statement)

**Cross-Reference:** CL-HARDWARE-002 (printhead driver allocation)

**Next Tests:** Search firmware for a 22-iteration loop that applies 14-bit HP masks per HA address.

---

## Sensor Integration

### ⚠️ CL-HP45-013: VADJ rail is ~9.09 V for the printhead
**Claim:** The printhead supply rail VADJ is measured at approximately 9.09 V and is distinct from VIN at 7.97 V.

**Evidence:**
- E-HP45-025: Lists VIN 7.97 V and VADJ 9.09 V for printhead/nozzle voltage.

**Status:** ⚠️ Supported (single board observation)

**Cross-Reference:** CL-HARDWARE-002 (printhead driver allocation)

**Next Tests:** Confirm VADJ measurement at the printhead connector during idle and firing states.

---

### ⚠️ CL-HP45-014: ADC channels 0 and 1 are unused in firmware
**Claim:** ADC channels 0 and 1 are not used by the firmware, while other ADC channels are used for voltage monitoring.

**Evidence:**
- E-HP45-026: Reports no adc_read_channel calls for channels 0 or 1.

**Status:** ⚠️ Supported (single analysis statement)

**Cross-Reference:** CL-SOC-025 (ADC availability)

**Next Tests:** Verify ADC channel usage in Ghidra by enumerating all adc_read_channel call sites.

---

### ✅ CL-HP45-015: MT6701 encoder connects to SoC pin 117 (GPE[10]/NALE)
**Claim:** The MT6701 encoder output is wired to SoC pin 117 on GPE[10]/NALE.

**Evidence:**
- E-HP45-028: PCB trace line shows MT6701 A_Out to SoC 117 (NALE_/GPE[10]).
- E-HP45-027: Notes encoder connection to SoC 117.

**Status:** ✅ Verified (PCB trace plus corroborating analysis)

**Cross-Reference:** CL-HARDWARE-003 (MT6701 encoder), CL-SOC-025 (MT6701 mapping)

**Next Tests:** None required - conclusively established.

---

### ⚠️ CL-HP45-016: Encoder value is displayed in the About screen
**Claim:** The About screen reports an encoder status and a numeric encoder value (e.g., "Encoder OK | 66602").

**Evidence:**
- E-HP45-029: About screen note identifies "Encoder OK | 66602" as the encoder value.

**Status:** ⚠️ Supported (single observation)

**Cross-Reference:** CL-HARDWARE-003 (MT6701 encoder)

**Next Tests:** Capture the About screen while rotating the encoder and confirm the value changes.
