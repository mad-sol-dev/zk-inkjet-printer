# DISPLAY Claims (Old Docs)

Propositional claims synthesized from old_docs (E4 tier).

---

## CL-OLD-DISPLAY-001: Display Uses SPI0 Pins And RS Line
- **Status:** supported
- **Confidence:** 0.80
- **Statement:** Display wiring uses SPI0 (GPD[12-14]) with RS/A0 on GPE[8], indicating SPI0 is dedicated to the display path.
- **Evidence:**
  - E4: E-OLD-DISPLAY-001 (SPI0 pin mapping)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Continuity-probe SPI0 CLK/CS/DI lines to the display FFC.
- **Tags:** display, spi0, pinout
- **Cross-Reference:** E1 CL-HARDWARE-005 (partial overlap), E1 CL-HARDWARE-014 (partial overlap)

## CL-OLD-DISPLAY-002: Backlight PWM On GPD0
- **Status:** supported
- **Confidence:** 0.75
- **Statement:** LCD backlight is driven by PWM0 on GPD[0] (pin 81), which is shared with JTAG TCK.
- **Evidence:**
  - E4: E-OLD-DISPLAY-002 (backlight PWM mapping)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Measure PWM duty changes while adjusting backlight brightness.
- **Tags:** display, backlight, pwm
- **Cross-Reference:** E1 CL-HARDWARE-006 (partial overlap)

## CL-OLD-DISPLAY-003: Display Controller MMIO Base @ 0xB100D000
- **Status:** verified
- **Confidence:** 0.90
- **Statement:** Firmware uses MMIO base 0xB100D000 for display updates, waiting on bit 0 and toggling it to latch updates.
- **Evidence:**
  - E4: E-OLD-DISPLAY-003 (display controller usage)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Identify specific register meanings under 0xB100D000 in vendor docs.
- **Tags:** display, mmio, controller
- **Cross-Reference:** E3-Old CL-RKO-MMIO-003 (partial overlap)
