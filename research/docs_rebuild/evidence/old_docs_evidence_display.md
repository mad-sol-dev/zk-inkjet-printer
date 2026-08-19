# DISPLAY Evidence (Old Docs)

Extracted evidence from research/old_docs/ (E4 tier). Format: Content (1-3 lines) + Source + Date + Type + Provenance + Tags.

---

### E-OLD-DISPLAY-001: Display Uses SPI0 Signals
- **Content:** Display wiring uses SPI0 signals on GPD[12-14] (CLK/CS0/DI) with command/data select on GPE[8].
- **Source:** old_docs/hardware/zk-dp20/circuit/N32903U5DN_GPIO_Pinout.md#Master-Pinout-List-1-128
- **Date:** 2025-11-03
- **Type:** OBSERVATION
- **Provenance:** None
- **Tags:** display, spi0, pinout

### E-OLD-DISPLAY-002: Backlight PWM On Pin 81
- **Content:** LCD backlight is driven by PWM0 on GPD[0] (pin 81), shared with JTAG TCK.
- **Source:** old_docs/hardware/zk-dp20/circuit/N32903U5DN_GPIO_Pinout.md#Master-Pinout-List-1-128
- **Date:** 2025-11-03
- **Type:** OBSERVATION
- **Provenance:** None
- **Tags:** display, backlight, pwm0, pinout

### E-OLD-DISPLAY-003: Display Controller Base @ 0xB100D000
- **Content:** Firmware uses MMIO base 0xB100D000 for hardware display updates, toggling bit 0 for readiness and latching.
- **Source:** old_docs/findings/mmio_map.md#0xB100D000---Display-Controller
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** display, mmio, controller
- **Note:** [ghidra-v1]
