# DISPLAY Claims (From E3-Old RE-KB Archive)

Propositional claims synthesized from historical RE-KB findings. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## Display and UI

### 🔬 Hypothesis CL-RKO-DISPLAY-001: SPI0 LCD command/data wrappers (ST7789V path)
**Claim:** SPI0 helper set driving the LCD. D/C line toggled in FUN_0006fd70 by flipping bit 0x2000 in *(0xb8003000+0x38). Commands flow through FUN_0006fd90 (writes byte to SPI base 0xb800c000 via offsets +0xb000/+0xb010 after clearing GO_BUSY), while FUN_0006fdd4 and FUN_0006fdf8 push 16-bit words or RGB565 pixel bursts using control words 0x85/0x305. FUN_0006fd18 reads bytes back. These primitives underpin all LCD window/pixel routines (set-address, draws, pixel read).

**Evidence:**
- E-RKO-DISPLAY-001: D/C GPIO toggle via *(0xb8003000+0x38) bit 0x2000
- E-RKO-DISPLAY-001: LCD command byte write; clears control bit at base+0x48, writes param to base+0xb010, triggers GO_BUSY at 0xb800c000
- E-RKO-DISPLAY-001: Single 16-bit data write via SPI0 (control 0x85)
- E-RKO-DISPLAY-001: Burst RGB565 writer filling TX0..TX3 and triggering control 0x305 in a loop

**Status:** 🔬 Hypothesis
**Cross-Reference:** Potential overlap with CL-HARDWARE-005, CL-HARDWARE-014
**Next Tests:** None listed

---

### 🔬 Hypothesis CL-RKO-DISPLAY-002: ST7789V display bring-up and backlight enable
**Claim:** ST7789V init sequence lives in FUN_0001d5a4: it drives the LCD over SPI0 using the LCD helpers and pushes a command/data stream ending in COLMOD=0x55 (16bpp), MADCTL=0xb4, and DISPON (0x29) after SLPOUT (0x11). Intermediate writes include parameters 0x0a/0x10/0x1a/0x3b/0x34/0x4e/0x17/0x16/0x21/0x22 before enabling display. D/C toggles the same GPIO bit 0x2000 at base 0xb8003000. Board-level init in FUN_0005c1a0 enables SPI0 clocks/pinmux, calls FUN_00080b7c (SPI0 setup at 0xb800c000), and configures PWM block at 0xb8007000 (backlight) by manipulating registers at offsets 0x40/0x30/0x34 and setting duty values from constants at 0x0005c3dc..0x0005c3e4.

**Evidence:**
- E-RKO-DISPLAY-002: LCD init sequence writes data values (0x0/0xa/0x10/0x11/…0x22), then issues CMD 0x3A with 0x55, CMD 0x36 with 0xb4, and CMD 0x29; uses same GPIO bit 0x2000 for D/C
- E-RKO-DISPLAY-002: Hardware init enabling SPI0 and PWM backlight; sets *_b0000208 clock bits, calls FUN_00080b7c (SPI0 setup), manipulates PWM base 0xb8007000 offsets 0x40/0x30/0x34 with duty constants

**Status:** 🔬 Hypothesis
**Cross-Reference:** Potential overlap with CL-HARDWARE-006
**Next Tests:** None listed

---

### 🔬 Hypothesis CL-RKO-DISPLAY-003: LCD rendering primitives (window set, blit, pixel read/write)
**Claim:** Rendering pipeline built atop the LCD SPI helpers. FUN_0001cab0 is the main blitter: asserts D/C low, issues CASET/RASET (0x2A/0x2B), then RAMWR (0x2C) and streams pixel data in multiple formats (RGB565 bulk via FUN_0006fdf8, indexed/alpha paths, etc.). FUN_0001d0c0 fills rectangles by setting a window and calling FUN_00070190 to repeat a color, then restores full-screen window. FUN_0001d77c writes a single pixel (0x2A/0x2B/0x2C with one color word). FUN_0001d1c0 performs RAMRD (0x2E) after setting an address window and converts the returned bytes to RGB565. All of these use the D/C GPIO toggle (bit 0x2000 at 0xb8003000) and SPI0 TX path at 0xb800c000.

**Evidence:**
- E-RKO-DISPLAY-003: Sets window with 0x2A/0x2B, issues 0x2C, streams pixel payload via FUN_0006fdf8/FUN_0006fdd4
- E-RKO-DISPLAY-003: Rectangle fill: sets window, RAMWR, floods color via FUN_00070190, restores full window
- E-RKO-DISPLAY-003: Single-pixel write using 0x2A/0x2B/0x2C followed by one color word
- E-RKO-DISPLAY-003: Pixel read via RAMRD (0x2E) after window set; reads 4 bytes through FUN_0006fd18 and returns RGB565

**Status:** 🔬 Hypothesis
**Cross-Reference:** None noted
**Next Tests:** None listed

---

### ⚠️ Supported CL-RKO-DISPLAY-004: ST7789V SPI Display Driver - Core Functions and Init Sequence
**Claim:** Complete ST7789V display driver architecture with SPI helpers, initialization sequence, and rendering primitives. Display connected via SPI0 (GPD12-14, GPE8, GPD0), using RGB565 format on 240x320 TFT panel.

**Evidence:**
- E-RKO-DISPLAY-004: SPI/LCD helper: toggles D/C on GPIO base 0xb8003000 bit 0x2000
- E-RKO-DISPLAY-004: Issues command bytes on SPI0 (0xb800c000 via offsets +0xb000/+0xb010)
- E-RKO-DISPLAY-004: Writes single 16-bit data words to display
- E-RKO-DISPLAY-004: Streams RGB565 bursts to display
- E-RKO-DISPLAY-004: Reads pixels from display
- E-RKO-DISPLAY-004: ST7789V init sequence: COLMOD 0x3A/0x55 (RGB565), MADCTL 0x36/0xb4, DISPON 0x29 after SLPOUT 0x11

**Status:** ⚠️ Supported
**Cross-Reference:** Potential overlap with CL-HARDWARE-005, CL-HARDWARE-014
**Next Tests:** Verify GPIO pin mapping (GPD12-14, GPE8, GPD0) against schematic; Extract complete init sequence and compare with ST7789V datasheet; Map SPI0 peripheral registers at 0xb800c000

---

### ✅ Verified CL-RKO-DISPLAY-005: ST7789V Display Rendering Primitives - Blitter and Fill Functions
**Claim:** Core rendering functions for ST7789V display: main blitter with CASET/RASET/RAMWR commands, rectangle fill, pixel read/write. All use SPI helpers and support RGB565 format.

**Evidence:**
- E-RKO-DISPLAY-005: Main blitter: CASET/RASET 0x2A/0x2B, RAMWR 0x2C, data via SPI helpers, multiple format paths
- E-RKO-DISPLAY-005: Fills rectangles and restores full-screen window
- E-RKO-DISPLAY-005: Writes a single pixel to display
- E-RKO-DISPLAY-005: Reads a pixel with RAMRD 0x2E command

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-HARDWARE-005
**Next Tests:** None listed

---

### ✅ Verified CL-RKO-DISPLAY-006: UI Architecture - Menu System and About Screen
**Claim:** Complete UI architecture with touch input, menu dispatcher, and About screen renderer. Touch ADC reads feed into UI main loop, which dispatches to menu screens including About screen showing time, voltages (V3V3/VBAT/VSYS), SD status, ink volume, and device serial (MAGIC number).

**Evidence:**
- E-RKO-DISPLAY-006: Touch ADC input handler with large stack frame, samples touch panel
- E-RKO-DISPLAY-006: Touch input wrapper, formats 0x40-byte buffer and calls handlers at 0x5ba78 and 0x4f23c
- E-RKO-DISPLAY-006: UI main loop: polls touch handlers (0x6c910, 0x6c934), dispatches to menu screens
- E-RKO-DISPLAY-006: Menu dispatcher state machine: calls 0x62c10 for menu selection, branches to screen renderers
- E-RKO-DISPLAY-006: About screen renderer with format strings: time (%02d-%02d-%02d %02d:%02d:%02d), voltages (%5.2f V), SD status (%s|%.1f/%.1fGB), ink (%.3f ml / %lld pl), MAGIC serial (%-7lld)
- E-RKO-DISPLAY-006: MAGIC string literal found at addresses 0x63634 and 0x6363c, matches screenshot

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-HARDWARE-011
**Next Tests:** None listed

---

### ⚠️ Supported CL-RKO-DISPLAY-007: Display Backlight and PWM Control
**Claim:** Display backlight controlled via PWM at base address 0xb8007000. Initialization function enables backlight/PWM and SPI0 clocks, calls SPI0 setup at 0x80b7c.

**Evidence:**
- E-RKO-DISPLAY-007: Enables backlight/PWM and SPI0 clocks, programs PWM base 0xb8007000, calls SPI0 setup at 0x80b7c

**Status:** ⚠️ Supported
**Cross-Reference:** Potential overlap with CL-HARDWARE-006
**Next Tests:** Map PWM registers at 0xb8007000 to N32903 PWM peripheral; Verify backlight GPIO pin connection

---
