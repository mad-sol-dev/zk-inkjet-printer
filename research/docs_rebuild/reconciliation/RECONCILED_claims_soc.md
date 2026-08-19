# SOC Reconciled Claims (Phase 2C-3)

Authority order: E0 > E3-New > E1 > E3-Old > E4 (E2 = context only).

---

## CL-SOC-REC-001: SoC Identity Is N32903U5DN (U-Serie)

**Status:** verified
**Confidence:** 0.95
**Authority:** E1

**Statement:** The device uses a Nuvoton N32903U5DN SoC (U-Serie) in LQFP-128 package.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-001 (U-Serie pin measurements), E-SOC-002 (8 MB readout), E-SOC-005 (1.8V MVDD excludes N32901), E-SOC-028 (LQFP-128)
- **E3-Old:** E-RKO-SOC-002 (N32903K5DN identification, mixed evidence) [ghidra-v1]
- **E4:** E-OLD-SOC-001 (N32903K5DN identification) [ghidra-v1]
- **E2:** E2-SOC-003 (identification narrative)

**Source Claims:**
- E1: CL-SOC-001
- E3-Old: CL-RKO-SOC-002 (partial overlap)
- E4: CL-OLD-SOC-001 (partial overlap)

**Superseded Evidence:**
- E-RKO-SOC-002 and E-OLD-SOC-001 identify the K5DN variant; superseded by E1 pin measurements and memory readout.

**Contradictions Resolved:** old_docs/analysis/documentation_contradictions_map.md (SoC identity conflict)

**Next Test:** Capture a photo of the SoC package marking and attach to E1 evidence.

**Tags:** soc, chip-id, n32903u5dn

---

## CL-SOC-REC-002: SoC Marking Shows "M5 dwin.com.cn"

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** The SoC package is marked "M5 dwin.com.cn", indicating OEM/third-party branding rather than the Nuvoton part number.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-031 (chip marking observation)
- **E3-Old:** E-RKO-SOC-001 (M5 marking discrepancy) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-002
- E3-Old: CL-RKO-SOC-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Photograph the marking and link to hardware image inventory.

**Tags:** soc, marking, dwin-m5

---

## CL-SOC-REC-003: Firmware Contains W55FA93/Nuvoton Descriptor Strings

**Status:** supported
**Confidence:** 0.85
**Authority:** E3-Old

**Statement:** Firmware embeds USB descriptor strings including "W55FA93 USB Card Reader 1.00" and vendor "Nuvoton".

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-003 (W55FA93 USB string in dmesg)
- **E3-Old:** E-RKO-SOC-002 (descriptor strings at 0x00475140) [ghidra-v1]
- **E4:** E-OLD-SOC-002 (descriptor strings in app.bin) [ghidra-v1]
- **E2:** E2-SOC-003 (UTF-16LE discovery narrative)

**Source Claims:**
- E4: CL-OLD-SOC-002
- E3-Old: CL-RKO-SOC-002 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Validate descriptor offsets in the current APP.bin using `strings -tx` and pointer tracing.

**Tags:** soc, usb, w55fa93, descriptors

---

## CL-SOC-REC-004: W55FA93 Is Legacy Winbond Naming

**Status:** supported
**Confidence:** 0.70
**Authority:** E1

**Statement:** "W55FA93" in USB strings reflects Winbond's legacy naming for the N3290x family rather than the actual silicon label.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-004 (family analysis), E-SOC-031 (naming history), E-SOC-003 (W55FA93 string)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-003
- E1: CL-SOC-018

**Superseded Evidence:** None

**Contradictions Resolved:** old_docs/analysis/documentation_contradictions_map.md (chip naming conflict)

**Next Test:** Locate a Nuvoton/Winbond migration note or BSP define linking W55FA93 to N3290x.

**Tags:** soc, w55fa93, legacy-name

---

## CL-SOC-REC-005: 8 MB DDR SDRAM In MCP Package

**Status:** verified
**Confidence:** 0.95
**Authority:** E1

**Statement:** The SoC integrates 8 MB DDR SDRAM in a multi-chip package (no external DRAM).

**Evidence (All Tiers):**
- **E0:** None (datasheet not present in repo)
- **E3-New:** None
- **E1:** E-SOC-007 (MCP DDR), E-SOC-009 (4M×16 = 8 MB), E-SOC-016 (N32903 = 8 MB DDR)
- **E3-Old:** E-RKO-SOC-002 (no-SDRAM variant claim) [ghidra-v1]
- **E4:** E-OLD-SOC-004 (no SDRAM init noted) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E1: CL-SOC-004
- E4: CL-OLD-SOC-004 (contradiction)

**Superseded Evidence:**
- E-RKO-SOC-002 and E-OLD-SOC-004 (no-SDRAM claim) superseded by E1 memory evidence.

**Contradictions Resolved:** old_docs/analysis/documentation_contradictions_map.md (RAM size conflict)

**Next Test:** Confirm DDR init path in BOOT.bin or check DRAM controller registers at runtime.

**Tags:** soc, ddr, mcp, memory

---

## CL-SOC-REC-006: DDR Supply/Reference Voltages (MVDD/MVREF)

**Status:** verified
**Confidence:** 0.95
**Authority:** E1

**Statement:** MVDD is ~1.8V and MVREF is ~1.0V, consistent with DDR SDRAM operation.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-021 (MVDD), E-SOC-023 (MVREF), E-SOC-005 (DDR voltage)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-005

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Measure MVDD/MVREF under different power states for stability.

**Tags:** soc, ddr, voltage

---

## CL-SOC-REC-007: Internal SRAM 8 KB and Boot ROM 16 KB

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** The SoC includes 8 KB internal SRAM and 16 KB internal Boot ROM.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-008 (datasheet note)
- **E3-Old:** None
- **E4:** E-OLD-SOC-005 (memory map summary) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E1: CL-SOC-006

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Identify SRAM usage in early boot routines.

**Tags:** soc, sram, boot-rom

---

## CL-SOC-REC-008: ARM926EJ-S Core and 192 MHz Clock

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** The SoC uses an ARM926EJ-S core and runs at ~192 MHz (200 MHz max).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-010 (192M readout), E-SOC-018 (ARM926EJ-S in datasheet)
- **E3-Old:** E-RKO-SOC-002 (CP15/ARMv5TEJ evidence) [ghidra-v1]
- **E4:** E-OLD-SOC-003 (CP15 + interworking) [ghidra-v1]
- **E2:** E2-SOC-003 (ARM926EJ-S identification narrative)

**Source Claims:**
- E1: CL-SOC-007
- E4: CL-OLD-SOC-003 (partial overlap)
- E3-Old: CL-RKO-SOC-002 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Inspect PLL registers to confirm configured CPU clock.

**Tags:** soc, cpu, arm926

---

## CL-SOC-REC-009: U-Serie vs K-Serie Feature Split

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** U-Serie is the typical variant (1 SPI, fewer GPIOs) and K-Serie is enhanced (2 SPI, more GPIOs); the device matches U-Serie.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-012 (U vs K), E-SOC-013 (SPI count), E-SOC-014 (GPIO count), E-SOC-001 (U-Serie pin measurements)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-008

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Validate SPI controller count via firmware MMIO access.

**Tags:** soc, u-series, k-series

---

## CL-SOC-REC-010: N3290x Memory Variants and Part-Number Encoding

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** N3290x variants encode memory size in the part number: N32901=2 MB SDRAM, N32903=8 MB DDR, N32905=32 MB DDR2.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-015/016/017 (variant table), E-SOC-030 (encoding rule)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-009

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Cross-check with official datasheet table if available locally.

**Tags:** soc, variants, memory

---

## CL-SOC-REC-011: Integrated Multimedia Peripherals

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** The SoC integrates JPEG codec, BitBLT, SPU audio, VPOST display, and camera interface.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-018 (peripheral list)
- **E3-Old:** E-RKO-SOC-002 (peripheral list summary) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-010
- E3-Old: CL-RKO-SOC-002 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Identify which peripherals are actually used in firmware.

**Tags:** soc, peripherals, multimedia

---

## CL-SOC-REC-012: Dual USB Controllers (Device + Host)

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** The SoC provides one USB 2.0 HS device controller and one USB 1.1 host controller.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-018 (USB device + host in datasheet)
- **E3-Old:** E-RKO-SOC-002 (USB host/device feature list) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-011

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Check firmware for USB host initialization patterns.

**Tags:** soc, usb, controllers

---

## CL-SOC-REC-013: Multiple Boot Options Supported

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** The SoC boot ROM supports SD, NAND, SPI flash, and USB boot modes.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-019 (boot mode list), E-SOC-027 (CFG pins)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-012

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Read CFG pin states on the PCB to confirm configured boot path.

**Tags:** soc, boot, modes

---

## CL-SOC-REC-014: SD0 Interface Pin Mapping (Pins 9-14)

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** SD0 connects on pins 9-14 (GPE[2-7]) with DAT0-3, CMD, and CLK in 4-bit mode.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-024 (PCB tracing), E-SOC-026 (pinout alt functions)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-013

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Confirm SD0 line continuity with a second board.

**Tags:** soc, sd0, pinout

---

## CL-SOC-REC-015: MT6701 Encoder Connected To Pin 117

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** MT6701 encoder pin 6 connects to SoC pin 117 (GPE[10]/NALE), with the interface mode still unclear.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-025 (PCB analysis of MT6701 pin wiring)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-014

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Search firmware for MT6701-related I2C/SPI or GPIO polling code.

**Tags:** soc, encoder, mt6701

---

## CL-SOC-REC-016: Complete LQFP-128 Pinout Documentation

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** A full LQFP-128 pinout table exists with GPIO assignments and alternate functions across ports.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-026 (pinout table), E-SOC-027 (CFG pins), E-SOC-028 (LQFP-128)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-015

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Convert the pinout table into a structured CSV for cross-checking.

**Tags:** soc, pinout, gpio

---

## CL-SOC-REC-017: USB PHY Reference Resistor (12 kΩ)

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** The USB PHY reference resistor (UD_REXT, pin 29) measures ~12 kΩ to ground.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-022 (12 kΩ measurement)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-016

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Measure UD_REXT on another unit to confirm consistency.

**Tags:** soc, usb, phy

---

## CL-SOC-REC-018: N3290x Family Uses MCP Design

**Status:** verified
**Confidence:** 0.85
**Authority:** E1

**Statement:** The N3290x family uses MCP stacking with integrated DRAM across all variants.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-029 (MCP design statement), E-SOC-030 (memory encoding)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-SOC-017

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Validate MCP claim against a vendor package or datasheet snapshot.

**Tags:** soc, mcp, memory

---

## CL-SOC-REC-019: BSP MMIO Base Addresses (Ground Truth)

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** BSP headers define key MMIO bases, including USB_BA=0xB1008000, GPIO_BA=0xB8001000, ADC_BA=0xB800E000, TMR_BA=0xB8002000, and SPI0_BA=0xB800C000.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (base address defines)
- **E3-New:** E-RKN-SOC-001 (BSP extraction summary)
- **E1:** None
- **E3-Old:** None
- **E4:** E-OLD-SOC-005 (memory map summary) [ghidra-v1]
- **E2:** E2-SOC-016 (extraction methodology)

**Source Claims:**
- E3-New: CL-RKN-SOC-001
- E3-New: CL-RKN-SOC-002

**Superseded Evidence:** None

**Contradictions Resolved:** CONTRADICTION-USB-001 (USB base address)

**Next Test:** Import `research/findings/n32903_registers.json` into Ghidra memory map.

**Tags:** soc, mmio, bsp

---

## CL-SOC-REC-020: K5DN No-SDRAM Variant (Refuted)

**Status:** refuted
**Confidence:** 0.80
**Authority:** E1

**Statement:** The claim that the device is an N32903K5DN without SDRAM is refuted by U-Serie pin measurements and 8 MB DDR evidence.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-SOC-001/002/005 (U-Serie and DDR evidence)
- **E3-Old:** E-RKO-SOC-002 (K5DN, no SDRAM) [ghidra-v1]
- **E4:** E-OLD-SOC-001, E-OLD-SOC-004 [ghidra-v1]
- **E2:** E2-SOC-003 (identification narrative)

**Source Claims:**
- E3-Old: CL-RKO-SOC-002
- E4: CL-OLD-SOC-001
- E4: CL-OLD-SOC-004

**Superseded Evidence:**
- E-RKO-SOC-002 and E-OLD-SOC-001/004 no-SDRAM assertions superseded by E1 measurements.

**Contradictions Resolved:** old_docs/analysis/documentation_contradictions_map.md (RAM size conflict)

**Next Test:** Verify DRAM size via firmware memory map or bootloader load address inspection.

**Tags:** soc, sdram, refuted
