# HARDWARE Claims (Old Docs)

Propositional claims synthesized from old_docs (E4 tier).

---

## CL-OLD-HARDWARE-001: GPB[2-5] Not Configured In Firmware
- **Status:** verified
- **Confidence:** 0.95
- **Statement:** Firmware configures GPB[0] and GPB[6] but does not configure GPB[2-5] in any pin-mux calls.
- **Evidence:**
  - E4: E-OLD-HARDWARE-001 (GPB[2-5] absence in pin-mux analysis)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Confirm with runtime tracing of GPBFUN writes during boot.
- **Tags:** gpio, gpb, pin-mux
- **Cross-Reference:** E3-Old CL-RKO-HARDWARE-001 (exact match)

## CL-OLD-HARDWARE-002: GPIO Driver Helpers Identified
- **Status:** verified
- **Confidence:** 0.93
- **Statement:** GPIO helper functions are identified at 0x00031F34 (pin-mux), 0x00031EC4 (read), and 0x0003224C (write) with consistent parameter conventions.
- **Evidence:**
  - E4: E-OLD-HARDWARE-002 (pin-mux helper)
  - E4: E-OLD-HARDWARE-003 (read/write helpers)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Rename functions in Ghidra and verify via call-site analysis.
- **Tags:** gpio, helpers, firmware
- **Cross-Reference:** E3-Old CL-RKO-HARDWARE-003 (exact match)

## CL-OLD-HARDWARE-003: UART0 Lines Are Occupied By Printhead Driver
- **Status:** supported
- **Confidence:** 0.80
- **Statement:** UART0 TX/RX on GPA[10-11] are wired to a printhead driver IC, blocking use as a console UART.
- **Evidence:**
  - E4: E-OLD-HARDWARE-004 (pinout shows UART0 to printhead IC2)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Continuity probe GPA[10-11] to confirm connection to the printhead driver.
- **Tags:** uart0, printhead, pinout
- **Cross-Reference:** E1 CL-HARDWARE-013 (partial overlap)

## CL-OLD-HARDWARE-004: JTAG TCK Shares Backlight PWM
- **Status:** supported
- **Confidence:** 0.75
- **Statement:** JTAG TCK is shared with the LCD backlight PWM on GPD[0], so debug access requires backlight control.
- **Evidence:**
  - E4: E-OLD-HARDWARE-005 (pinout conflict note)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Measure PWM on pin 81 while toggling backlight settings.
- **Tags:** jtag, backlight, pwm
- **Cross-Reference:** E1 CL-HARDWARE-006 (partial overlap)

## CL-OLD-HARDWARE-005: GPB[2-5] Routed To Cartridge Pogo Header
- **Status:** supported
- **Confidence:** 0.70
- **Statement:** GPB[2-5] connect to a cartridge pogo header, implying an external interface (encoder/sensor/ID) rather than internal GPIO use.
- **Evidence:**
  - E4: E-OLD-HARDWARE-006 (pogo header wiring)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Trace pogo header pins to any cartridge circuitry or sensors.
- **Tags:** pogo, cartridge, gpb
- **Cross-Reference:** None (unique)

## CL-OLD-HARDWARE-006: MicroSD Slot Uses GPE2-7
- **Status:** supported
- **Confidence:** 0.75
- **Statement:** MicroSD slot lines map to GPE[2-7] for SD0_DAT0-3, CMD, and CLK.
- **Evidence:**
  - E4: E-OLD-HARDWARE-007 (microSD pin mapping)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Verify SD signal routing with continuity checks.
- **Tags:** microsd, sd, pinout
- **Cross-Reference:** None (unique)
