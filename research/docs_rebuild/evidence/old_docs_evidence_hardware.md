# HARDWARE Evidence (Old Docs)

Extracted evidence from research/old_docs/ (E4 tier). Format: Content (1-3 lines) + Source + Date + Type + Provenance + Tags.

---

### E-OLD-HARDWARE-001: GPB[2-5] Not Configured In Firmware
- **Content:** Firmware configures GPB[0] (Function 2) and GPB[6] (Function 5) but never configures GPB[2-5] in pin-mux calls.
- **Source:** old_docs/findings/gpio_configuration.md#Finding
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** gpio, gpb, pin-mux, firmware
- **Note:** [ghidra-v1]

### E-OLD-HARDWARE-002: Pin-Mux Configuration Function @ 0x00031F34
- **Content:** Pin-mux helper at 0x00031F34 sets GPxFUN registers with parameters r0=port, r1=pin, r2=function (0=GPIO, 1-5 alt).
- **Source:** old_docs/findings/firmware_functions.md#Pin-Mux-Configuration-0x00031f34
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** gpio, pin-mux, gpbfun, function-map
- **Note:** [ghidra-v1]

### E-OLD-HARDWARE-003: GPIO Read/Write Helpers
- **Content:** GPIO read at 0x00031EC4 returns PIN bit state; GPIO write at 0x0003224C sets/clears DOUT bit per r2.
- **Source:** old_docs/findings/firmware_functions.md#GPIO-Read-Pin--0x00031ec4
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** gpio, read, write, helpers
- **Note:** [ghidra-v1]

### E-OLD-HARDWARE-004: UART0 Pins Wired To Printhead Driver
- **Content:** UART0 TX/RX (pins 122/123) are physically wired to printhead driver IC2, blocking console UART usage.
- **Source:** old_docs/hardware/zk-dp20/circuit/N32903U5DN_GPIO_Pinout.md#Critical-Hardware-Conflicts--Corrections
- **Date:** 2025-11-03
- **Type:** OBSERVATION
- **Provenance:** None
- **Tags:** uart0, printhead, pinout, hardware

### E-OLD-HARDWARE-005: JTAG TCK Shared With Backlight PWM
- **Content:** JTAG TCK (pin 81) is shared with LCD backlight PWM, so hardware debug requires disabling the backlight.
- **Source:** old_docs/hardware/zk-dp20/circuit/N32903U5DN_GPIO_Pinout.md#Critical-Hardware-Conflicts--Corrections
- **Date:** 2025-11-03
- **Type:** OBSERVATION
- **Provenance:** None
- **Tags:** jtag, pwm, backlight, conflict

### E-OLD-HARDWARE-006: GPB[2-5] Routed To Cartridge Pogo Header
- **Content:** GPB[2-5] (pins 125-128) connect to a cartridge pogo header, suggesting an external interface rather than internal GPIO use.
- **Source:** old_docs/hardware/zk-dp20/circuit/N32903U5DN_GPIO_Pinout.md#Critical-Hardware-Conflicts--Corrections
- **Date:** 2025-11-03
- **Type:** OBSERVATION
- **Provenance:** None
- **Tags:** gpb, pogo, header, cartridge

### E-OLD-HARDWARE-007: MicroSD Slot Wiring (GPE2-7)
- **Content:** MicroSD slot uses GPE[2-7] pins for SD0_DAT0-3, SD0_CMD, and SD0_CLK connections.
- **Source:** old_docs/hardware/zk-dp20/circuit/N32903U5DN_GPIO_Pinout.md#Master-Pinout-List-1-128
- **Date:** 2025-11-03
- **Type:** OBSERVATION
- **Provenance:** None
- **Tags:** sd, microsd, gpe, pinout

### E-OLD-HARDWARE-008: USB-C Wiring (UD_DP/UD_DM + UD_REXT)
- **Content:** USB D+/D- and UD_REXT pins connect to the USB-C connector with a 12k resistor (active USB PHY).
- **Source:** old_docs/hardware/zk-dp20/circuit/N32903U5DN_GPIO_Pinout.md#Master-Pinout-List-1-128
- **Date:** 2025-11-03
- **Type:** OBSERVATION
- **Provenance:** None
- **Tags:** usb, usb-c, ud_dp, ud_dm, ud_rext
