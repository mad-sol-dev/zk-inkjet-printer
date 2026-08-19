# SOC Claims

Propositional claims synthesized from evidence. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## Chip Identity

### ✅ CL-SOC-001: Device Uses Nuvoton N32903U5DN SoC
**Claim:** The device uses a Nuvoton N32903U5DN SoC in LQFP-128 package with U-Serie (Typical) pinout, confirmed through systematic pin measurements and system readout.

**Evidence:**
- E-SOC-001: Pin measurements (31, 30, 29, 23) match U-Serie pinout exactly
- E-SOC-002: System displays "3.83/8M" confirming 8 MB memory → N32903
- E-SOC-005: MVDD=1.8V excludes N32901 (3.3V SDRAM)
- E-SOC-028: LQFP-128 package confirmed

**Status:** ✅ Verified (multiple E1 hardware measurements, system readout)

**Next Tests:** None required - conclusively established

---

### ⚠️ CL-SOC-002: Chip Marking Shows Third-Party "M5 dwin.com.cn"
**Claim:** Physical chip package is marked "M5 dwin.com.cn" instead of Nuvoton part number, indicating third-party integration or OEM branding by DWIN Technology (HMI manufacturer).

**Evidence:**
- E-SOC-031: Physical inspection shows "M5 dwin.com.cn" marking

**Status:** ⚠️ Supported (E1 observation, needs photo documentation)

**Next Tests:**
- Photograph chip marking for documentation
- Research DWIN M5 series products for context
- Confirm if DWIN uses Nuvoton SoCs in M5 line

---

### ⚠️ CL-SOC-003: USB Enumeration Uses Legacy W55FA93 Name
**Claim:** USB mass storage enumeration reports "W55FA93 SPI Disk" instead of N32903, reflecting Winbond's pre-acquisition naming scheme that predates Nuvoton's N3290x series rebranding.

**Evidence:**
- E-SOC-003: dmesg shows "scsi 2:0:0:0: Direct-Access W55FA93 SPI Disk"
- E-SOC-004: Analysis links W55FA93 to ARM9 family (same as N3290x)
- E-SOC-031: W55FA93 was Winbond naming before Nuvoton takeover

**Status:** ⚠️ Supported (E1 log + analysis, historical context needs vendor docs)

**Next Tests:**
- Search Nuvoton docs for W55FA93→N3290x migration guide
- Check if BSP code references W55FA93 strings
- Determine if firmware can be updated to report N32903

---

## Memory Architecture

### ✅ CL-SOC-004: 8 MB DDR SDRAM in Multi-Chip-Package
**Claim:** The N32903U5DN integrates 8 MB DDR SDRAM (4M×16, 1.8V) stacked in the same package as the CPU die using Multi-Chip-Package (MCP) technology. No external DRAM is required.

**Evidence:**
- E-SOC-007: Datasheet confirms 8 MB DDR in MCP, no external connection
- E-SOC-009: Specification is 4M words × 16 bit = 64 Mbit = 8 MB
- E-SOC-016: N32903 series defined as 8 MB DDR SDRAM variant
- E-SOC-029: All N3290x chips use MCP design (no external DRAM option)

**Status:** ✅ Verified (datasheet + part number encoding)

**Next Tests:** None required - architecture well documented

---

### ✅ CL-SOC-005: DDR SDRAM Voltage is 1.8V (MVDD/MVREF)
**Claim:** DDR SDRAM operates at 1.8V supply voltage (MVDD, Pin 30) with 1.0V reference voltage (MVREF, Pin 23), confirming DDR (not DDR2 or SDRAM) technology.

**Evidence:**
- E-SOC-021: Pin 30 measures ~1.8V to 2.0V with decoupling capacitor
- E-SOC-023: Pin 23 measures ~1.0V (MVDD/2) with capacitor
- E-SOC-005: 1.8V voltage excludes N32901 (3.3V SDRAM)
- E-SOC-006: MVREF presence confirms DDR interface

**Status:** ✅ Verified (direct voltage measurements)

**Next Tests:** None required - measured on hardware

---

### ✅ CL-SOC-006: Internal 8 KB SRAM and 16 KB Boot ROM
**Claim:** In addition to 8 MB external DDR, the N32903U5DN contains 8 KB internal SRAM and 16 KB Internal Boot ROM (IBR).

**Evidence:**
- E-SOC-008: Datasheet specifies 8 KB SRAM + 16 KB Boot-ROM

**Status:** ✅ Verified (datasheet)

**Next Tests:**
- Identify SRAM usage in firmware (stack, heap, critical code)
- Analyze IBR boot process for SD card loading

---

## CPU Architecture

### ✅ CL-SOC-007: ARM926EJ-S Core Running at 192 MHz
**Claim:** The SoC uses ARM926EJ-S CPU core running at 192 MHz nominal clock (200 MHz maximum per datasheet).

**Evidence:**
- E-SOC-010: System "About" screen displays "192M" CPU frequency
- E-SOC-018: Datasheet specifies ARM926EJ-S core up to 200 MHz

**Status:** ✅ Verified (system readout + datasheet)

**Next Tests:**
- Verify PLL configuration registers in firmware
- Test if clock can be reduced for power saving

---

## Series Variants (K vs U, Memory Sizes)

### ✅ CL-SOC-008: U-Serie = Typical, K-Serie = Enhanced
**Claim:** Nuvoton N3290x series has two pinout variants: U-Serie (Typical, 64 GPIOs, 1 SPI) and K-Serie (Enhanced, 70 GPIOs, 2 SPIs). Device confirmed as U-Serie.

**Evidence:**
- E-SOC-012: Datasheet defines U=Typical, K=Enhanced
- E-SOC-001: Pin measurements match U-Serie exclusively
- E-SOC-013: K-Serie has 2 SPI controllers vs U-Serie's 1
- E-SOC-014: K-Serie offers 70 GPIOs vs U-Serie's 64

**Status:** ✅ Verified (datasheet + pin measurements)

**Next Tests:** None required - K-Serie excluded by hardware

---

### ✅ CL-SOC-009: N3290x Family Has Three Memory Variants
**Claim:** The N3290x series comes in three memory configurations encoded in part number: N32901 (2 MB SDRAM, 3.3V), N32903 (8 MB DDR, 1.8V), N32905 (32 MB DDR2, 1.8V).

**Evidence:**
- E-SOC-015: N32901 = 2 MB, 1M×16, 3.3V SDRAM
- E-SOC-016: N32903 = 8 MB, 4M×16, 1.8V DDR SDRAM
- E-SOC-017: N32905 = 32 MB, 16M×16, 1.8V DDR2 SDRAM
- E-SOC-030: Part number 5th digit encodes memory size (1/3/5)

**Status:** ✅ Verified (datasheet tables, part number scheme)

**Next Tests:** None required - documented by vendor

---

## Peripherals & Features

### ✅ CL-SOC-010: Integrated Multimedia Peripherals
**Claim:** N32903U5DN integrates JPEG codec, 2D graphics accelerator (BitBLT), 32-channel sound processor (SPU) with 16-bit stereo DAC, display controller (VPOST), and camera interface.

**Evidence:**
- E-SOC-018: Datasheet lists JPEG codec, 2D BitBLT, SPU with DAC, VPOST (up to 1024×768), camera (2MP CMOS)

**Status:** ✅ Verified (datasheet feature list)

**Next Tests:**
- Identify which peripherals are actually used in firmware
- Check if JPEG/2D/SPU drivers are present in code

---

### ✅ CL-SOC-011: Dual USB Controllers (Device + Host)
**Claim:** SoC provides 1× USB 2.0 High-Speed Device controller and 1× USB 1.1 Host controller (Host-Lite).

**Evidence:**
- E-SOC-018: Datasheet specifies "1x USB 2.0 High-Speed Device und 1x USB 1.1 Host"

**Status:** ✅ Verified (datasheet)

**Cross-Reference:** Links to USB cluster CL-USB-010 (UDC base 0xB1008000)

**Next Tests:**
- Confirm if USB Host controller is used (for external devices)
- Check USB Device descriptor configuration in firmware

---

### ✅ CL-SOC-012: Multiple Boot Options Supported
**Claim:** The SoC supports booting from SD card, NAND flash (raw or with SD-to-NAND bridge), SPI flash, or USB (ISP mode).

**Evidence:**
- E-SOC-019: Datasheet lists SD, SD-to-NAND, Raw NAND, SPI Flash, USB boot modes
- E-SOC-027: Boot configuration pins CFG[0:10] select boot source

**Status:** ✅ Verified (datasheet)

**Cross-Reference:** Links to STORAGE cluster CL-STORAGE-004 (IBR boot process)

**Next Tests:**
- Read CFG pin states to determine configured boot mode
- Test alternate boot modes (SPI flash, USB ISP)

---

## Pin Mapping & Verification

### ✅ CL-SOC-013: SD0 Interface on GPE[2-7] (Pins 9-14)
**Claim:** Micro-SD card boot medium connects via SD0 interface using pins 9-14: GPE[4]=DAT2, GPE[5]=DAT3, GPE[6]=CMD, GPE[7]=CLK, GPE[2]=DAT0, GPE[3]=DAT1 (4-bit SD mode).

**Evidence:**
- E-SOC-024: PCB tracing confirms Pin 9-14 mapping to SD card
- E-SOC-026: GPIO Port E pinout shows SD0 alternate functions

**Status:** ✅ Verified (PCB tracing + pinout)

**Cross-Reference:** Links to STORAGE cluster (SD card as boot medium)

**Next Tests:** None required - physically traced and verified

---

### ⚠️ CL-SOC-014: Pin 117 Connected to MT6701 Encoder (Unexplained)
**Claim:** MT6701 magnetic encoder IC (SOP-8) connects to SoC Pin 117 (GPE[10]/NALE), but the connection purpose is unclear. MT6701 datasheet indicates analog output on Pin 3, but only Pin 6 traces to SoC, suggesting possible I2C/SPI digital interface mode.

**Evidence:**
- E-SOC-025: PCB shows MT6701 Pin 6 → SoC Pin 117
- E-SOC-025: MT6701 part number "-AKD" specifies analog output, but wiring doesn't match

**Status:** ⚠️ Supported (PCB traced, function unclear)

**Counter-Evidence:**
- Analog output would typically use ADC pins, not GPIO/NALE
- Pin 117 is GPE[10] with NALE (NAND Address Latch) alternate function

**Next Tests:**
- Analyze firmware for MT6701 driver code (I2C/SPI/Analog)
- Check if GPE[10] configured as GPIO input or alternate function
- Verify MT6701 operating mode (may support digital interfaces)

---

## Pinout Documentation

### ✅ CL-SOC-015: Complete 128-Pin GPIO Mapping Documented
**Claim:** All 128 pins of LQFP package are documented with primary function, GPIO assignment (where applicable), and up to 4 alternate functions per GPIO. Total of 72 GPIOs across 5 ports (GPA, GPB, GPC, GPD, GPE).

**Evidence:**
- E-SOC-026: Complete pinout table created covering all 79 GPIO pins
- E-SOC-014: U-Serie offers 64 GPIOs (not all 72 brought out)
- E-SOC-027: Boot config pins CFG[0:10] identified

**Status:** ✅ Verified (datasheet extraction + pinout analysis)

**Next Tests:**
- Create Ghidra memory map with GPIO register addresses
- Import BSP struct definitions for GPIO configuration

---

## USB Reference Circuitry

### ✅ CL-SOC-016: USB PHY Has 12kΩ Reference Resistor
**Claim:** USB Device PHY reference resistor (UD_REXT, Pin 29) measures 12kΩ to ground, matching USB 2.0 High-Speed PHY requirements.

**Evidence:**
- E-SOC-022: Multimeter reads 12kΩ from Pin 29 to ground

**Status:** ✅ Verified (hardware measurement)

**Cross-Reference:** Confirms USB hardware is functional (links to USB cluster)

**Next Tests:** None required - standard USB PHY design

---

## MCP Architecture

### ✅ CL-SOC-017: All N3290x Variants Use MCP Design
**Claim:** Every chip in the N3290x family uses Multi-Chip-Package architecture with stacked DRAM die. There is no variant without internal memory - all models integrate 2/8/32 MB as part of the package.

**Evidence:**
- E-SOC-029: Nuvoton markets entire series as MCP, no external-DRAM variant exists
- E-SOC-030: Part number encoding always includes memory size (1/3/5)

**Status:** ✅ Verified (vendor documentation, product line structure)

**Next Tests:** None required - confirmed by vendor

---

## Winbond → Nuvoton History

### 🔬 CL-SOC-018: W55FA93 is Legacy Winbond Name for N3290x
**Claim:** The W55FA93 designation appearing in USB strings represents Winbond's original part number before Nuvoton acquired Winbond's microcontroller division and rebranded the series as N3290x. Firmware likely contains legacy strings from BSP development.

**Evidence:**
- E-SOC-003: USB enumeration shows "W55FA93"
- E-SOC-004: Analysis links W55FA93 to ARM9 family (same as N3290x)
- E-SOC-031: Observation notes W55FA93 as old Winbond naming

**Status:** 🔬 Hypothesis (analysis + historical context, needs vendor documentation)

**Next Tests:**
- Search Nuvoton application notes for W55FA93 migration references
- Check if Nuvoton BSP contains W55FA93 compatibility defines
- Search firmware for "W55FA93" string locations

---

## Summary

**Total Claims:** 18
**Status Distribution:**
- ✅ Verified: 14 claims
- ⚠️ Supported: 3 claims
- 🔬 Hypothesis: 1 claim

**Contradictions:** None (chip identity fully resolved)

**Key Findings:**
1. Chip conclusively identified as N32903U5DN via pin measurements + system readout
2. Physical marking shows "M5 dwin.com.cn" (third-party OEM branding)
3. USB enumeration uses legacy "W55FA93" name from pre-Nuvoton era
4. 8 MB DDR SDRAM in MCP confirmed at 1.8V
5. U-Serie pinout verified (not K-Serie)
6. Complete 72-GPIO pinout documented with alternate functions
7. SD0 interface physically traced to Pins 9-14
8. MT6701 encoder connection on Pin 117 unexplained (needs firmware analysis)

**High Priority Tests:**
1. Analyze firmware for MT6701 driver (resolve Pin 117 mystery)
2. Search for W55FA93 strings in firmware (confirm legacy BSP usage)
3. Identify active peripherals (JPEG, 2D, SPU) in code
4. Document DWIN M5 product line (understand OEM relationship)
