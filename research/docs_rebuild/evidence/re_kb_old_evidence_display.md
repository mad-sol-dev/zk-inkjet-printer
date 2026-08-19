# DISPLAY Evidence (E3-Old RE-KB Archive)

**Source:** research/findings/re_kb_archive/findings/*.json (31 findings from historical RE-KB)
**Tier:** E3-Old (structured findings from earlier analysis sessions)
**Note:** These findings predate Ghidra optimization (37k→1.3k functions). Ghidra-based evidence should be marked [ghidra-v1].

---

## Display and UI

### E-RKO-DISPLAY-001: SPI0 LCD command/data wrappers (ST7789V path)
- **RE-KB ID:** finding-0024
- **Status:** open
- **Type:** behavior
- **Summary:** SPI0 helper set driving the LCD. D/C line toggled in FUN_0006fd70 by flipping bit 0x2000 in *(0xb8003000+0x38). Commands flow through FUN_0006fd90 (writes byte to SPI base 0xb800c000 via offsets +0xb000/+0xb010 after clearing GO_BUSY), while FUN_0006fdd4 and FUN_0006fdf8 push 16-bit words or RGB565 pixel bursts using control words 0x85/0x305. FUN_0006fd18 reads bytes back. These primitives underpin all LCD window/pixel routines (set-address, draws, pixel read).
- **Evidence:**
  - E1: D/C GPIO toggle via *(0xb8003000+0x38) bit 0x2000; source_type=ghidra; function_address=0x6fd70; function_name=FUN_0006fd70; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: LCD command byte write; clears control bit at base+0x48, writes param to base+0xb010, triggers GO_BUSY at 0xb800c000; source_type=ghidra; function_address=0x6fd90; function_name=FUN_0006fd90; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E3: Single 16-bit data write via SPI0 (control 0x85); source_type=ghidra; function_address=0x6fdd4; function_name=FUN_0006fdd4; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E4: Burst RGB565 writer filling TX0..TX3 and triggering control 0x305 in a loop; source_type=ghidra; function_address=0x6fdf8; function_name=FUN_0006fdf8; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
- **Tags:** display, spi, hardware
- **Confidence:** None
- **Component:** None
- **Created:** 2025-12-20T19:03:43.888434Z
- **Updated:** 2025-12-20T19:03:43.888434Z

### E-RKO-DISPLAY-002: ST7789V display bring-up and backlight enable
- **RE-KB ID:** finding-0025
- **Status:** open
- **Type:** behavior
- **Summary:** ST7789V init sequence lives in FUN_0001d5a4: it drives the LCD over SPI0 using the LCD helpers and pushes a command/data stream ending in COLMOD=0x55 (16bpp), MADCTL=0xb4, and DISPON (0x29) after SLPOUT (0x11). Intermediate writes include parameters 0x0a/0x10/0x1a/0x3b/0x34/0x4e/0x17/0x16/0x21/0x22 before enabling display. D/C toggles the same GPIO bit 0x2000 at base 0xb8003000. Board-level init in FUN_0005c1a0 enables SPI0 clocks/pinmux, calls FUN_00080b7c (SPI0 setup at 0xb800c000), and configures PWM block at 0xb8007000 (backlight) by manipulating registers at offsets 0x40/0x30/0x34 and setting duty values from constants at 0x0005c3dc..0x0005c3e4.
- **Evidence:**
  - E1: LCD init sequence writes data values (0x0/0xa/0x10/0x11/…0x22), then issues CMD 0x3A with 0x55, CMD 0x36 with 0xb4, and CMD 0x29; uses same GPIO bit 0x2000 for D/C; source_type=ghidra; function_address=0x1d5a4; function_name=FUN_0001d5a4; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Hardware init enabling SPI0 and PWM backlight; sets *_b0000208 clock bits, calls FUN_00080b7c (SPI0 setup), manipulates PWM base 0xb8007000 offsets 0x40/0x30/0x34 with duty constants; source_type=ghidra; function_address=0x5c1a0; function_name=FUN_0005c1a0; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
- **Tags:** display, spi, hardware
- **Confidence:** None
- **Component:** None
- **Created:** 2025-12-20T19:04:00.481491Z
- **Updated:** 2025-12-20T19:04:00.481491Z

### E-RKO-DISPLAY-003: LCD rendering primitives (window set, blit, pixel read/write)
- **RE-KB ID:** finding-0026
- **Status:** open
- **Type:** behavior
- **Summary:** Rendering pipeline built atop the LCD SPI helpers. FUN_0001cab0 is the main blitter: asserts D/C low, issues CASET/RASET (0x2A/0x2B), then RAMWR (0x2C) and streams pixel data in multiple formats (RGB565 bulk via FUN_0006fdf8, indexed/alpha paths, etc.). FUN_0001d0c0 fills rectangles by setting a window and calling FUN_00070190 to repeat a color, then restores full-screen window. FUN_0001d77c writes a single pixel (0x2A/0x2B/0x2C with one color word). FUN_0001d1c0 performs RAMRD (0x2E) after setting an address window and converts the returned bytes to RGB565. All of these use the D/C GPIO toggle (bit 0x2000 at 0xb8003000) and SPI0 TX path at 0xb800c000.
- **Evidence:**
  - E1: Sets window with 0x2A/0x2B, issues 0x2C, streams pixel payload via FUN_0006fdf8/FUN_0006fdd4; source_type=ghidra; function_address=0x1cab0; function_name=FUN_0001cab0; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Rectangle fill: sets window, RAMWR, floods color via FUN_00070190, restores full window; source_type=ghidra; function_address=0x1d0c0; function_name=FUN_0001d0c0; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E3: Single-pixel write using 0x2A/0x2B/0x2C followed by one color word; source_type=ghidra; function_address=0x1d77c; function_name=FUN_0001d77c; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E4: Pixel read via RAMRD (0x2E) after window set; reads 4 bytes through FUN_0006fd18 and returns RGB565; source_type=ghidra; function_address=0x1d1c0; function_name=FUN_0001d1c0; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
- **Tags:** display, ui, spi
- **Confidence:** None
- **Component:** None
- **Created:** 2025-12-20T19:04:15.680837Z
- **Updated:** 2025-12-20T19:04:15.680837Z

### E-RKO-DISPLAY-004: ST7789V SPI Display Driver - Core Functions and Init Sequence
- **RE-KB ID:** finding-0027
- **Status:** in_progress
- **Type:** behavior
- **Summary:** Complete ST7789V display driver architecture with SPI helpers, initialization sequence, and rendering primitives. Display connected via SPI0 (GPD12-14, GPE8, GPD0), using RGB565 format on 240x320 TFT panel.
- **Evidence:**
  - E1: SPI/LCD helper: toggles D/C on GPIO base 0xb8003000 bit 0x2000; source_type=ghidra; function_address=0x6fd70; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Issues command bytes on SPI0 (0xb800c000 via offsets +0xb000/+0xb010); source_type=ghidra; function_address=0x6fd90; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E3: Writes single 16-bit data words to display; source_type=ghidra; function_address=0x6fdd4; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E4: Streams RGB565 bursts to display; source_type=ghidra; function_address=0x6fdf8; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E5: Reads pixels from display; source_type=ghidra; function_address=0x6fd18; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E6: ST7789V init sequence: COLMOD 0x3A/0x55 (RGB565), MADCTL 0x36/0xb4, DISPON 0x29 after SLPOUT 0x11; source_type=ghidra; function_address=0x1d5a4; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
- **Tags:** st7789v, spi, display, lcd, gpio, rendering
- **Confidence:** 1.0
- **Component:** display
- **Created:** 2025-12-20T19:19:36.008655Z
- **Updated:** 2025-12-20T19:19:36.008655Z

### E-RKO-DISPLAY-005: ST7789V Display Rendering Primitives - Blitter and Fill Functions
- **RE-KB ID:** finding-0028
- **Status:** verified
- **Type:** behavior
- **Summary:** Core rendering functions for ST7789V display: main blitter with CASET/RASET/RAMWR commands, rectangle fill, pixel read/write. All use SPI helpers and support RGB565 format.
- **Evidence:**
  - E1: Main blitter: CASET/RASET 0x2A/0x2B, RAMWR 0x2C, data via SPI helpers, multiple format paths; source_type=ghidra; function_address=0x1cab0; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Fills rectangles and restores full-screen window; source_type=ghidra; function_address=0x1d0c0; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E3: Writes a single pixel to display; source_type=ghidra; function_address=0x1d77c; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E4: Reads a pixel with RAMRD 0x2E command; source_type=ghidra; function_address=0x1d1c0; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
- **Tags:** st7789v, rendering, blitter, graphics
- **Confidence:** 1.0
- **Component:** display
- **Created:** 2025-12-20T19:20:11.130499Z
- **Updated:** 2025-12-20T19:20:11.130499Z

### E-RKO-DISPLAY-006: UI Architecture - Menu System and About Screen
- **RE-KB ID:** finding-0029
- **Status:** verified
- **Type:** behavior
- **Summary:** Complete UI architecture with touch input, menu dispatcher, and About screen renderer. Touch ADC reads feed into UI main loop, which dispatches to menu screens including About screen showing time, voltages (V3V3/VBAT/VSYS), SD status, ink volume, and device serial (MAGIC number).
- **Evidence:**
  - E1: Touch ADC input handler with large stack frame, samples touch panel; source_type=ghidra; function_address=0x618dc; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Touch input wrapper, formats 0x40-byte buffer and calls handlers at 0x5ba78 and 0x4f23c; source_type=ghidra; function_address=0x61840; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E3: UI main loop: polls touch handlers (0x6c910, 0x6c934), dispatches to menu screens; source_type=ghidra; function_address=0x6c4e0; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E4: Menu dispatcher state machine: calls 0x62c10 for menu selection, branches to screen renderers; source_type=ghidra; function_address=0x6a7f8; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E5: About screen renderer with format strings: time (%02d-%02d-%02d %02d:%02d:%02d), voltages (%5.2f V), SD status (%s|%.1f/%.1fGB), ink (%.3f ml / %lld pl), MAGIC serial (%-7lld); source_type=ghidra; function_address=0x62ef0; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E6: MAGIC string literal found at addresses 0x63634 and 0x6363c, matches screenshot; source_type=other [ghidra-v1]
- **Tags:** ui, menu, about-screen, touch, adc
- **Confidence:** 1.0
- **Component:** ui
- **Created:** 2025-12-20T19:21:19.702534Z
- **Updated:** 2025-12-20T19:21:19.702534Z

### E-RKO-DISPLAY-007: Display Backlight and PWM Control
- **RE-KB ID:** finding-0030
- **Status:** in_progress
- **Type:** behavior
- **Summary:** Display backlight controlled via PWM at base address 0xb8007000. Initialization function enables backlight/PWM and SPI0 clocks, calls SPI0 setup at 0x80b7c.
- **Evidence:**
  - E1: Enables backlight/PWM and SPI0 clocks, programs PWM base 0xb8007000, calls SPI0 setup at 0x80b7c; source_type=ghidra; function_address=0x5c1a0; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
- **Tags:** pwm, backlight, display, mmio
- **Confidence:** 0.9
- **Component:** display
- **Created:** 2025-12-20T19:21:55.285503Z
- **Updated:** 2025-12-20T19:21:55.285503Z

