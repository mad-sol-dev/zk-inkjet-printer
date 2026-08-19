# HP45 Claims (From E3-Old RE-KB Archive)

Propositional claims synthesized from historical RE-KB findings. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## Printhead Control and Drivers

### ⚠️ Supported CL-RKO-HP45-001: HP45 Cartridge Control - Complete Pin Mapping and Driver Architecture
**Claim:** Complete hardware reverse engineering of HP45 cartridge control. The printer uses 6× CM504B level shifters and 7× dual N-MOSFETs to drive the HP45's 22×14 nozzle matrix. Pin mapping identified: HA0-HA21 address lines on GPC0-15/GPE0-1/GPB15/GPD9-11, HP0-HP13 primitive lines on GPA0-11/GPD5-8. Firmware should implement 22-phase loop with ~1.8µs pulse timing per nozzle. UI strings confirm nozzle voltage monitoring. See findings 0014-0017 for detailed specifications.

**Evidence:**
- E-RKO-HP45-001: String 'Nozzle Voltage' found in firmware, indicating UI/monitoring for nozzle voltage control
- E-RKO-HP45-001: Hardware: 6x CM504B hex level shifters provide direct GPIO to HP45 nozzles. No shift registers, direct pin control. 128-pin N32903K5DN has ample GPIO.
- E-RKO-HP45-001: N3290x Timer Controller specification (pages 669-672). TMR_BA @ 0xB8002000 not referenced in firmware.

**Status:** ⚠️ Supported
**Cross-Reference:** Potential overlap with CL-HP45-005, CL-HP45-007
**Next Tests:** Search firmware for GPIO configuration code (GPA/GPC/GPD/GPE/GPB setup); Find 22-iteration print loop in firmware; Verify HP04 source pin (currently TBD in finding-0016); Trace C10X/CTSR sensor pins to ADC inputs; Identify delay routine for ~1.8µs pulse timing

---

### ✅ Verified CL-RKO-HP45-002: HP45 Cartridge Architecture - 22×14 Nozzle Matrix Control
**Claim:** The HP45(SI) cartridge contains 300 nozzles arranged as a 22×14 matrix with 22 address lines (HA0-HA21), 14 primitive lines (HP0-HP13), and common heater ground (HGND). Each nozzle has an internal MOSFET (gate on HAx) and heating resistor (~30Ω, on HPx line). Nozzles fire when both the HA address is active and the HP primitive receives a ~1.8µs pulse at VDD (~12V), drawing ~0.3-0.4A per nozzle.

**Evidence:**
- E-RKO-HP45-002: HP45 cartridge datasheet analysis and hardware reverse engineering

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-HP45-002
**Next Tests:** None listed

---

### ✅ Verified CL-RKO-HP45-003: HP45 Address Lines (HA0-HA21) - Pin Mapping to Nuvoton SoC
**Claim:** The 22 HP45 address lines (HA0-HA21) are driven by four CM504B level shifters (IC3-IC6) from Nuvoton SoC GPIO pins. IC3-IC5 use primarily GPC0-GPC15 and GPE0-GPE1 for HA0-HA17. IC6 uses GPB15, GPD9-GPD11 for HA18-HA21. All HA lines are level-shifted from MCU VCC (~3.3V) to VDD (~12V) and drive FET gates inside the HP45 cartridge.

**Evidence:**
- E-RKO-HP45-003: PCB trace analysis and CM504B pinout verification

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-HP45-005, CL-HP45-008
**Next Tests:** None listed

---

### ⚠️ Supported CL-RKO-HP45-004: HP45 Primitive Lines (HP0-HP13) - Pin Mapping and High-Side MOSFET Drivers
**Claim:** The 14 HP45 primitive lines (HP0-HP13) control which nozzles fire within the selected HA address. Each HP line is driven by a dual N-MOSFET (Q7-Q13, marking 'DS01') configured as high-side switches with common drain at VDD (~12V). Gates are driven by three CM504B level shifters (IC1, IC2, IC6) from SoC pins GPA0-GPA11, GPD5-GPD8. Multiple HP lines can be active simultaneously to fire multiple nozzles in parallel.

**Evidence:**
- E-RKO-HP45-004: PCB trace analysis, MOSFET pinout verification, CM504B routing

**Status:** ⚠️ Supported
**Cross-Reference:** Potential overlap with CL-HP45-006, CL-HP45-010
**Next Tests:** Verify HP04 source pin in firmware GPIO code; Clarify HP07/HP10 pin overlap (both show GPA7); Confirm HP09 exact pin (GPA10 vs GPA11)

---

### ✅ Verified CL-RKO-HP45-005: HP45 Driver Hardware Components - CM504B Level Shifters and Dual N-MOSFETs
**Claim:** The printer uses 6× CM504B (CD4504B-compatible) hex level shifters and 7× dual N-MOSFET packages (marking 'DS01', SOT-23-6) to interface between the Nuvoton SoC and HP45 cartridge. CM504B chips convert 3.3V MCU logic to ~12V head voltage (VDD). IC1/IC2/IC6 drive HP primitive MOSFETs, IC3-IC6 drive HA address lines. The dual MOSFETs (Q7-Q13) act as high-side switches for the 14 HP lines.

**Evidence:**
- E-RKO-HP45-005: Visual PCB inspection, component markings, datasheet cross-reference

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-HP45-005, CL-HP45-006
**Next Tests:** None listed

---

### ⚠️ Supported CL-RKO-HP45-006: Firmware Analysis - HP45 Control Code Patterns and MMIO References
**Claim:** Initial Ghidra analysis of ZK-INKJET-NANO-APP.bin reveals ARM v5T firmware with direct MMIO references. Found 'Nozzle Voltage' string @ 0x001f2cf4, GCR_BA (0xB0000000) referenced 10+ times, and numerous scalar values matching HP45 parameters (0x16=22 for HA lines, 0x0e=14 for HP primitives). GPIO base (0xB8001000) not found as direct scalar - likely loaded from data section or constructed at runtime.

**Evidence:**
- E-RKO-HP45-006: String 'Nozzle Voltage' found in firmware
- E-RKO-HP45-006: GCR_BA (0xB0000000) references found - confirms MMIO usage
- E-RKO-HP45-006: Scalar value 22 (0x16) found in multiple contexts - matches 22 HA address lines

**Status:** ⚠️ Supported
**Cross-Reference:** Potential overlap with CL-HP45-012, CL-HP45-015
**Next Tests:** Manually analyze functions with MMIO patterns to find GPIO port operations; Search data sections for GPIO base address pointers; Trace message handlers back to HP45 print entry points; Identify GPIO write sequences matching HA/HP pin patterns; Locate microsecond delay implementation

---
