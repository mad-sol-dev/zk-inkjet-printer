# HP45 Evidence (E3-Old RE-KB Archive)

**Source:** research/findings/re_kb_archive/findings/*.json (31 findings from historical RE-KB)
**Tier:** E3-Old (structured findings from earlier analysis sessions)
**Note:** These findings predate Ghidra optimization (37k→1.3k functions). Ghidra-based evidence should be marked [ghidra-v1].

---

## Printhead Control and Drivers

### E-RKO-HP45-001: HP45 Cartridge Control - Complete Pin Mapping and Driver Architecture
- **RE-KB ID:** finding-0012
- **Status:** in_progress
- **Type:** behavior
- **Summary:** Complete hardware reverse engineering of HP45 cartridge control. The printer uses 6× CM504B level shifters and 7× dual N-MOSFETs to drive the HP45's 22×14 nozzle matrix. Pin mapping identified: HA0-HA21 address lines on GPC0-15/GPE0-1/GPB15/GPD9-11, HP0-HP13 primitive lines on GPA0-11/GPD5-8. Firmware should implement 22-phase loop with ~1.8µs pulse timing per nozzle. UI strings confirm nozzle voltage monitoring. See findings 0014-0017 for detailed specifications.
- **Evidence:**
  - E1: String 'Nozzle Voltage' found in firmware, indicating UI/monitoring for nozzle voltage control; source_type=ghidra; function_address=0x1f2cf4; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Hardware: 6x CM504B hex level shifters provide direct GPIO to HP45 nozzles. No shift registers, direct pin control. 128-pin N32903K5DN has ample GPIO.; source_type=other [ghidra-v1]
  - E3: N3290x Timer Controller specification (pages 669-672). TMR_BA @ 0xB8002000 not referenced in firmware.; source_type=pdf; page=672 [ghidra-v1]
- **Tags:** hp45, cartridge, nozzle, gpio, hardware, pin-mapping, cm504b, verified
- **Confidence:** 0.9
- **Component:** hp45
- **Created:** 2025-11-27T22:30:20.979463Z
- **Updated:** 2025-12-02T03:06:23.085378Z

### E-RKO-HP45-002: HP45 Cartridge Architecture - 22×14 Nozzle Matrix Control
- **RE-KB ID:** finding-0014
- **Status:** verified
- **Type:** behavior
- **Summary:** The HP45(SI) cartridge contains 300 nozzles arranged as a 22×14 matrix with 22 address lines (HA0-HA21), 14 primitive lines (HP0-HP13), and common heater ground (HGND). Each nozzle has an internal MOSFET (gate on HAx) and heating resistor (~30Ω, on HPx line). Nozzles fire when both the HA address is active and the HP primitive receives a ~1.8µs pulse at VDD (~12V), drawing ~0.3-0.4A per nozzle.
- **Evidence:**
  - E1: HP45 cartridge datasheet analysis and hardware reverse engineering; source_type=other [ghidra-v1]
- **Tags:** hp45, cartridge, hardware, matrix, nozzles, printhead
- **Confidence:** 1.0
- **Component:** hp45
- **Created:** 2025-12-01T17:49:44.528505Z
- **Updated:** 2025-12-02T03:06:41.517560Z

### E-RKO-HP45-003: HP45 Address Lines (HA0-HA21) - Pin Mapping to Nuvoton SoC
- **RE-KB ID:** finding-0015
- **Status:** verified
- **Type:** behavior
- **Summary:** The 22 HP45 address lines (HA0-HA21) are driven by four CM504B level shifters (IC3-IC6) from Nuvoton SoC GPIO pins. IC3-IC5 use primarily GPC0-GPC15 and GPE0-GPE1 for HA0-HA17. IC6 uses GPB15, GPD9-GPD11 for HA18-HA21. All HA lines are level-shifted from MCU VCC (~3.3V) to VDD (~12V) and drive FET gates inside the HP45 cartridge.
- **Evidence:**
  - E1: PCB trace analysis and CM504B pinout verification; source_type=other [ghidra-v1]
- **Tags:** hp45, gpio, pin-mapping, ha-lines, address, cm504b, level-shifter
- **Confidence:** 1.0
- **Component:** hp45
- **Created:** 2025-12-01T17:50:12.135045Z
- **Updated:** 2025-12-02T03:06:51.040853Z

### E-RKO-HP45-004: HP45 Primitive Lines (HP0-HP13) - Pin Mapping and High-Side MOSFET Drivers
- **RE-KB ID:** finding-0016
- **Status:** in_progress
- **Type:** behavior
- **Summary:** The 14 HP45 primitive lines (HP0-HP13) control which nozzles fire within the selected HA address. Each HP line is driven by a dual N-MOSFET (Q7-Q13, marking 'DS01') configured as high-side switches with common drain at VDD (~12V). Gates are driven by three CM504B level shifters (IC1, IC2, IC6) from SoC pins GPA0-GPA11, GPD5-GPD8. Multiple HP lines can be active simultaneously to fire multiple nozzles in parallel.
- **Evidence:**
  - E1: PCB trace analysis, MOSFET pinout verification, CM504B routing; source_type=other [ghidra-v1]
- **Tags:** hp45, gpio, pin-mapping, hp-lines, primitive, mosfet, high-side, cm504b
- **Confidence:** 0.85
- **Component:** hp45
- **Created:** 2025-12-01T17:51:02.722108Z
- **Updated:** 2025-12-02T03:07:01.384215Z

### E-RKO-HP45-005: HP45 Driver Hardware Components - CM504B Level Shifters and Dual N-MOSFETs
- **RE-KB ID:** finding-0017
- **Status:** verified
- **Type:** behavior
- **Summary:** The printer uses 6× CM504B (CD4504B-compatible) hex level shifters and 7× dual N-MOSFET packages (marking 'DS01', SOT-23-6) to interface between the Nuvoton SoC and HP45 cartridge. CM504B chips convert 3.3V MCU logic to ~12V head voltage (VDD). IC1/IC2/IC6 drive HP primitive MOSFETs, IC3-IC6 drive HA address lines. The dual MOSFETs (Q7-Q13) act as high-side switches for the 14 HP lines.
- **Evidence:**
  - E1: Visual PCB inspection, component markings, datasheet cross-reference; source_type=other [ghidra-v1]
- **Tags:** hp45, hardware, cm504b, level-shifter, mosfet, high-side, driver
- **Confidence:** 1.0
- **Component:** hp45
- **Created:** 2025-12-01T17:51:32.301894Z
- **Updated:** 2025-12-02T03:07:11.130519Z

### E-RKO-HP45-006: Firmware Analysis - HP45 Control Code Patterns and MMIO References
- **RE-KB ID:** finding-0018
- **Status:** in_progress
- **Type:** behavior
- **Summary:** Initial Ghidra analysis of ZK-INKJET-NANO-APP.bin reveals ARM v5T firmware with direct MMIO references. Found 'Nozzle Voltage' string @ 0x001f2cf4, GCR_BA (0xB0000000) referenced 10+ times, and numerous scalar values matching HP45 parameters (0x16=22 for HA lines, 0x0e=14 for HP primitives). GPIO base (0xB8001000) not found as direct scalar - likely loaded from data section or constructed at runtime.
- **Evidence:**
  - E1: String 'Nozzle Voltage' found in firmware; source_type=ghidra; function_address=0x1f2cf4; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: GCR_BA (0xB0000000) references found - confirms MMIO usage; source_type=ghidra; function_address=0x2df2c; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E3: Scalar value 22 (0x16) found in multiple contexts - matches 22 HA address lines; source_type=ghidra; function_address=0x1900c; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
- **Tags:** firmware, ghidra, hp45, mmio, gpio, arm, analysis
- **Confidence:** 0.7
- **Component:** firmware
- **Created:** 2025-12-01T18:11:18.573574Z
- **Updated:** 2025-12-02T03:07:23.297624Z

