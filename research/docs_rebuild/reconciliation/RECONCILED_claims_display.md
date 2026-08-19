# DISPLAY Reconciled Claims (Phase 2C-3)

Authority order: E0 > E3-New > E1-Recent > E1 > E3-Old > E4 (E2 = context only).

---

## CL-DISPLAY-REC-001: 2.8 Inch TFT With 18-Pin FFC And SPI0 Wiring

**Status:** supported
**Confidence:** 0.85
**Authority:** E1-Recent

**Statement:** The device uses a 2.8 inch TFT with an 18-pin FFC; SPI0 (SCL/SDA/SDO + CS) connects to the display, with RS/A0 on SoC pin 120 and a 4-wire resistive touch panel (XL/YU/XR/YD).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E1-Recent: `research/findings/report_analyse_2_8_tft_lcd_18_pin_ffc_vermuteter_controller.md` (SPI0 wiring, RS/A0 on pin 120, 4-wire touch)
- **E3-Old:** E-RKO-DISPLAY-004 (SPI0 wiring claim) [ghidra-v1]
- **E4:** E-OLD-DISPLAY-001 (SPI0 pins + RS line) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-DISPLAY-004 (partial overlap)
- E4: CL-OLD-DISPLAY-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Continuity-probe SPI0 and RS/A0 lines from the SoC to the display FFC.

**Tags:** display, spi0, pinout, touch

---

## CL-DISPLAY-REC-002: Display Controller Identity Unconfirmed (ST7789V or ILI9341)

**Status:** hypothesis
**Confidence:** 0.55
**Authority:** E1-Recent

**Statement:** The display controller is not confirmed; candidates include ST7789V and ILI9341, and the current init sequence evidence is inconclusive.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E1-Recent: `research/findings/report_analyse_2_8_tft_lcd_18_pin_ffc_vermuteter_controller.md` (controller not confirmed)
- **E3-Old:** E-RKO-DISPLAY-002 (ST7789V init hypothesis) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-DISPLAY-002 (downgraded)
- E3-Old: CL-RKO-DISPLAY-004 (downgraded)

**Superseded Evidence:** ST7789V-specific claims from E3-Old are downgraded to hypothesis pending verified init sequence.

**Contradictions Resolved:** None

**Next Test:** Extract a reliable command/data sequence (0x2A/0x2B/0x2C or 0x20/0x21/0x22) from the actual SPI path.

**Tags:** display, controller, st7789v, ili9341

---

## CL-DISPLAY-REC-003: SPI0 LCD Command/Data Helpers And D/C Toggle

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E3-Old

**Statement:** LCD command/data helpers toggle a D/C GPIO bit and write to SPI0 registers to send command and pixel data.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-DISPLAY-001 (SPI0 helper and D/C toggle) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-DISPLAY-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Re-validate helper functions in the optimized Ghidra project and match to SPI0 register definitions.

**Tags:** display, spi0, lcd, helpers

---

## CL-DISPLAY-REC-004: Rendering Primitives Use CASET/RASET/RAMWR

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E3-Old

**Statement:** Rendering primitives set window registers with CASET/RASET and write pixels via RAMWR (and RAMRD for reads).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-DISPLAY-003 (window set, RAMWR/RAMRD) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-DISPLAY-003
- E3-Old: CL-RKO-DISPLAY-005 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Confirm actual command bytes in the optimized disassembly and trace the real call path.

**Tags:** display, rendering, ramwr

---

## CL-DISPLAY-REC-005: Backlight Is Controlled By PWM0 On GPD0

**Status:** supported
**Confidence:** 0.80
**Authority:** E3-Old

**Statement:** The LCD backlight is driven by PWM0 on GPD0 (pin 81), shared with JTAG TCK.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (PWM_BA=0xB8007000)
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-DISPLAY-007 (PWM backlight init) [ghidra-v1]
- **E4:** E-OLD-DISPLAY-002 (PWM0 on GPD0) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-DISPLAY-007
- E4: CL-OLD-DISPLAY-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Measure PWM duty changes while adjusting brightness.

**Tags:** display, backlight, pwm

---

## CL-DISPLAY-REC-006: Display BLT Engine Base Is 0xB100D000

**Status:** verified
**Confidence:** 0.90
**Authority:** E0

**Statement:** The BitBlt display engine base address is 0xB100D000 and is used for hardware display updates.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (BLT_BA=0xB100D000)
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-DISPLAY-006 (display update routines) [ghidra-v1]
- **E4:** E-OLD-DISPLAY-003 (display controller base) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-DISPLAY-006 (partial overlap)
- E4: CL-OLD-DISPLAY-003

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Correlate BLT registers with observed display update behavior in firmware.

**Tags:** display, mmio, blt

---

## CL-DISPLAY-REC-007: UI Architecture Includes Touch Input And About Screen

**Status:** supported
**Confidence:** 0.75
**Authority:** E3-Old

**Statement:** The UI uses touch ADC input and includes an About screen showing time, voltages, SD status, ink volume, and serial.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-DISPLAY-006 (touch handlers, menu dispatcher, About screen strings) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-DISPLAY-006

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Re-verify UI handlers with optimized Ghidra and confirm touch ADC mappings.

**Tags:** display, ui, touch, about
