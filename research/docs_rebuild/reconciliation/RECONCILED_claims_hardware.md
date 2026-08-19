# HARDWARE Reconciled Claims (Phase 2C-3)

Authority order: E0 > E3-New > E1 > E3-Old > E4 (E2 = context only).

---

## CL-HARDWARE-REC-001: GPIO Usage Split (31 Used, 41 Free)

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** The pinout analysis reports 31 GPIOs in use and 41 remaining free out of 72 total.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HARDWARE-001 (41 free), E-HARDWARE-002 (31 used)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Continuity-probe a random sample from the “free” list to confirm availability.

**Tags:** hardware, gpio, allocation

---

## CL-HARDWARE-REC-002: Printhead Uses ~30 GPIOs Via CM504B Drivers

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** The printhead driver section uses about 30 GPIOs routed through CM504B level shifters.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HARDWARE-002 (30 printhead GPIOs), E-HARDWARE-019 (IC1 mapping), E-HARDWARE-020 (IC2 mapping)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Trace two additional CM504B ICs to confirm GPIO group counts.

**Tags:** hardware, printhead, gpio

---

## CL-HARDWARE-REC-003: MT6701 Encoder Uses SoC Pin 117

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** The MT6701 encoder connects to SoC pin 117 (GPE[10]/NALE) using a single signal line.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HARDWARE-018 (pin 117 connection), E-SOC-025 (pin 6 to SoC 117)
- **E3-Old:** None
- **E4:** None
- **E2:** E2-HARDWARE-014 (encoder interface narrative)

**Source Claims:**
- E1: CL-HARDWARE-003

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Confirm whether GPE[10] is configured as GPIO input or alternate function in firmware.

**Tags:** hardware, encoder, mt6701

---

## CL-HARDWARE-REC-004: Untested GPIO Set Remains

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E1

**Statement:** Roughly 35 GPIOs remain untested and unassigned in the current pinout inventory.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HARDWARE-010 (35 untested pins)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-004

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Build a probe matrix and log continuity for the untested pins.

**Tags:** hardware, gpio, unknown

---

## CL-HARDWARE-REC-005: GPB[2-5] Not Configured In Firmware

**Status:** supported
**Confidence:** 0.85
**Authority:** E3-Old

**Statement:** Firmware does not configure GPB[2-5] in pin-mux calls; only GPB[0] and GPB[6] are explicitly configured.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-HARDWARE-001 (systematic pin-mux analysis) [ghidra-v1]
- **E4:** E-OLD-HARDWARE-001 (GPB[2-5] absent) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-HARDWARE-001
- E4: CL-OLD-HARDWARE-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Re-run pin-mux caller analysis on the current APP.bin build.

**Tags:** hardware, gpio, pin-mux

---

## CL-HARDWARE-REC-006: GPIO Helper Functions Identified

**Status:** supported
**Confidence:** 0.85
**Authority:** E3-Old

**Statement:** GPIO helper functions are identified at 0x00031F34 (pin-mux), 0x00031EC4 (read), and 0x0003224C (write).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-HARDWARE-003 (pin-mux/read/write functions) [ghidra-v1]
- **E4:** E-OLD-HARDWARE-002, E-OLD-HARDWARE-003 (helpers) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-HARDWARE-003
- E4: CL-OLD-HARDWARE-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Rename these functions in Ghidra and confirm via call-site analysis.

**Tags:** hardware, gpio, firmware

---

## CL-HARDWARE-REC-007: Display Uses SPI0 And GPE[8] Control Pin

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** The display uses SPI0 (GPD[12-15]) with a control pin on GPE[8] (pin 120), so SPI0 is occupied by the display.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (SPI0_BA=0xB800C000)
- **E3-New:** None
- **E1:** E-HARDWARE-007 (display pins), E-HARDWARE-012 (display on SPI0), E-HARDWARE-015 (SPI0 CS/DI), E-HARDWARE-017 (FFC pin 4 to pin 120)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-005
- E1: CL-HARDWARE-014

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Continuity-probe SPI0 CLK/DO lines to confirm full signal occupancy.

**Tags:** hardware, display, spi0

---

## CL-HARDWARE-REC-008: Backlight PWM0 On GPD0 (Pin 81)

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** LCD backlight is driven by PWM0 on GPD[0] (pin 81).

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (PWM_BA=0xB8007000)
- **E3-New:** None
- **E1:** E-HARDWARE-005 (Q8 on pin 81), E-HARDWARE-016 (PWM0 backlight)
- **E3-Old:** None
- **E4:** E-OLD-HARDWARE-005 (JTAG TCK shared with backlight PWM) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-006

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Measure PWM duty cycle on pin 81 while adjusting brightness.

**Tags:** hardware, backlight, pwm

---

## CL-HARDWARE-REC-009: UART0 Pins Occupied By Printhead Driver

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** UART0 pins GPA[10-11] are wired to printhead driver IC2 and are not available for console UART.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (UART_BA=0xB8008000)
- **E3-New:** None
- **E1:** E-HARDWARE-003 (UART occupied), E-HARDWARE-020 (IC2 mapping)
- **E3-Old:** None
- **E4:** E-OLD-HARDWARE-004 (UART0 pins wired to printhead) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-013
- E4: CL-OLD-HARDWARE-003

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Continuity-probe GPA[10-11] to confirm they only reach printhead drivers.

**Tags:** hardware, uart0, printhead

---

## CL-HARDWARE-REC-010: JTAG TCK Shares Backlight PWM

**Status:** supported
**Confidence:** 0.75
**Authority:** E4

**Statement:** JTAG TCK is shared with the backlight PWM pin (GPD0), requiring backlight control during JTAG use.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** None
- **E4:** E-OLD-HARDWARE-005 (JTAG/PWM conflict) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-HARDWARE-004

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Verify JTAG pin multiplexing while toggling PWM0.

**Tags:** hardware, jtag, pwm

---

## CL-HARDWARE-REC-011: Touch Panel Uses SoC Touch ADC Pins

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** The touch panel is wired to the SoC’s resistive touch ADC pins (ADC_TP_*).

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (ADC_BA=0xB800E000)
- **E3-New:** None
- **E1:** E-HARDWARE-014 (touch on touch pins)
- **E3-Old:** None
- **E4:** None
- **E2:** E2-HARDWARE-014 (touch ADC mapping narrative)

**Source Claims:**
- E1: CL-HARDWARE-007

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Identify touch ADC channels in firmware and confirm pin-to-channel mapping.

**Tags:** hardware, touch, adc

---

## CL-HARDWARE-REC-012: ADC Architecture For Voltage Monitoring

**Status:** supported
**Confidence:** 0.80
**Authority:** E3-Old

**Statement:** The SoC’s ADC (0xB800E000) is used for voltage monitoring (VADJ/VBAT/V3V3) and touch controller operation.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (ADC_BA=0xB800E000)
- **E3-New:** None
- **E1:** E-HARDWARE-025 (UI voltage values)
- **E3-Old:** E-RKO-HARDWARE-004 (ADC architecture, channel usage) [ghidra-v1]
- **E4:** None
- **E2:** E2-HARDWARE-014 (ADC mapping narrative; resolution mismatch)

**Source Claims:**
- E3-Old: CL-RKO-HARDWARE-004
- E1: CL-HARDWARE-011 (partial overlap)

**Superseded Evidence:**
- E2-HARDWARE-014 states 12-bit ADC; E3-Old indicates 10-bit (needs verification).

**Contradictions Resolved:** None

**Next Test:** Confirm ADC resolution in BSP or datasheet and verify channel mapping in firmware.

**Tags:** hardware, adc, voltage

---

## CL-HARDWARE-REC-013: Display Module Likely ST7789V 18-Pin SPI TFT

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E1

**Statement:** The display module likely matches an 18-pin SPI TFT panel using an ST7789V controller.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HARDWARE-013 (18-pin FFC match)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-008

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Compare FFC pin order to a known ST7789V datasheet and validate with scope captures.

**Tags:** hardware, display, st7789v

---

## CL-HARDWARE-REC-014: MVDD/MVREF Rails For DDR

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** DDR rails target MVDD ≈ 1.8V and MVREF ≈ 0.9–1.0V (VREF/2).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HARDWARE-021 (MVDD target), E-HARDWARE-022 (MVREF target), E-SOC-021/023 (measured MVDD/MVREF)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-009
- E1: CL-HARDWARE-010

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Measure MVDD/MVREF on a second board to confirm nominal levels.

**Tags:** hardware, power, ddr

---

## CL-HARDWARE-REC-015: Printhead Power Uses DC-DC Converters

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E1

**Statement:** Dedicated DC-DC converters supply the printhead/nozzle voltages.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HARDWARE-023 (DC-DC note), E-HARDWARE-024 (nozzle voltage display)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-012

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Probe converter outputs and map them to printhead rails.

**Tags:** hardware, power, printhead

---

## CL-HARDWARE-REC-016: I2C On GPB[13-14] Appears Available

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E1

**Statement:** I2C on GPB[13-14] is listed as available but remains unverified by trace or firmware config.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (I2C_BA=0xB8004000)
- **E3-New:** None
- **E1:** E-HARDWARE-030 (available interfaces list)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-015

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Check GPB[13-14 for pull-ups and runtime activity.

**Tags:** hardware, i2c, availability

---

## CL-HARDWARE-REC-017: High-Speed UART GPD[1-4] Are Candidate Pins

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E1

**Statement:** GPD[1-4] are listed as available high-speed UART pins, pending physical trace confirmation.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (UART_BA=0xB8008000)
- **E3-New:** None
- **E1:** E-HARDWARE-030 (available interfaces list)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-016

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Probe GPD[1-4] for continuity to headers/test pads.

**Tags:** hardware, uart, availability

---

## CL-HARDWARE-REC-018: USB Device Pins Are Wired (Not Unused)

**Status:** supported
**Confidence:** 0.80
**Authority:** E4

**Statement:** USB device pins (UD_DP/UD_DM/UD_REXT) are wired to the USB-C connector with a 12 kΩ reference resistor; they are not electrically unused.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HARDWARE-031 (claimed unused), E-USB-009 (MSC activity), E-USB-010 (MSC interface descriptors)
- **E3-Old:** None
- **E4:** E-OLD-HARDWARE-008 (USB-C wiring) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-017

**Superseded Evidence:**
- E-HARDWARE-031 "USB pins unused" superseded by USB MSC activity and USB-C wiring evidence.

**Contradictions Resolved:** None

**Next Test:** Confirm DP/DM continuity to the connector and inspect for series resistors/ESD diodes.

**Tags:** hardware, usb, pins

---

## CL-HARDWARE-REC-019: GPC[4] Is Free But Boot-Config Constrained

**Status:** supported
**Confidence:** 0.70
**Authority:** E1

**Statement:** GPC[4] is free but reserved as a boot configuration pin (CFG[8]).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HARDWARE-004 (boot config constraint), E-SOC-027 (CFG pins)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-HARDWARE-018

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Review boot strap requirements before repurposing GPC[4].

**Tags:** hardware, boot-config, gpio

---

## CL-HARDWARE-REC-020: MicroSD Slot Uses GPE[2-7]

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** The microSD slot connects to GPE[2-7] (SD0_DAT0-3/CMD/CLK).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-HARDWARE-006 (SD0 uses GPE[2-7]), E-SOC-024 (pin mapping)
- **E3-Old:** None
- **E4:** E-OLD-HARDWARE-007 (microSD wiring) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-HARDWARE-006

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Continuity-probe SD pins to confirm signal mapping.

**Tags:** hardware, sd0, pinout

---

## CL-HARDWARE-REC-021: GPB[2-5] Routed To Cartridge Pogo Header

**Status:** supported
**Confidence:** 0.70
**Authority:** E4

**Statement:** GPB[2-5] are routed to the cartridge pogo header, suggesting an external interface.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** None
- **E4:** E-OLD-HARDWARE-006 (pogo header wiring) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-HARDWARE-005

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Trace pogo header pins to any cartridge circuitry or sensors.

**Tags:** hardware, pogo, gpb

---

## CL-HARDWARE-REC-022: Display Controller MMIO Base and GPIO Base

**Status:** supported
**Confidence:** 0.80
**Authority:** E3-Old

**Statement:** Firmware uses display controller MMIO base 0xB100D000 and GPIO base 0xB8001000 with standard port offsets.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (GPIO_BA=0xB8001000)
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-HARDWARE-002 (display controller + GPIO base) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-HARDWARE-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Confirm display controller usage via current APP.bin disassembly.

**Tags:** hardware, mmio, display

---

## CL-HARDWARE-REC-023: USB Device Controller MMIO Base

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** The USB device controller MMIO base address is 0xB1008000.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (USB_BA=0xB1008000)
- **E3-New:** E-RKN-HARDWARE-001 (USB_BA from BSP extraction)
- **E1:** None
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E3-New: CL-RKN-HARDWARE-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Search current firmware for references to 0xB1008000 to confirm active usage.

**Tags:** hardware, usb, mmio
