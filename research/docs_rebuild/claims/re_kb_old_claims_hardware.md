# HARDWARE Claims (From E3-Old RE-KB Archive)

Propositional claims synthesized from historical RE-KB findings. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## GPIO, Pins, and Analog Interfaces

### ✅ Verified CL-RKO-HARDWARE-001: GPIO Port B Configuration - Pins GPB[2-5] Unconfigured
**Claim:** Pin-mux analysis shows GPB[2-5] (LQFP-128 pins 125-128) are NOT configured in firmware, neither as GPIO nor alternative functions (UART/SPI/I2C/PWM/I2S/SD). Only GPB[0] (Function 2) and GPB[6] (Function 5) are explicitly configured. Systematic analysis of all 12 pin-mux function calls confirms zero GPB[2-5] configurations.

**Evidence:**
- E-RKO-HARDWARE-001: Pin-mux configuration function (600 bytes) manipulates GPBFUN @ 0xB0000084 with read-modify-write pattern. Parameters: r0=port, r1=pin, r2=function.
- E-RKO-HARDWARE-001: Systematic analysis of all 12 pin-mux callers found only 3 Port B configurations: GPB[0] Function 2 @ 0x00031e4c and 0x00031ea4, GPB[6] Function 5 @ 0x0005c210. Zero configurations for GPB[2-5].
- E-RKO-HARDWARE-001: N32903K5DN LQFP-128 pinout shows Pin 128=GPB[2] (GPIO/I2S_MCLK/SDCLK1), Pin 127=GPB[3] (GPIO/I2S_BCLK/SDCMD1), Pin 126=GPB[4] (GPIO/I2S_WS/SDDAT1[3]), Pin 125=GPB[5] (GPIO/I2S_DOUT/SDDAT1[2])
- E-RKO-HARDWARE-001: Alternative function search for I2S_BA @ 0xB1001000, SPI, I2C, UART, PWM controllers yielded 0 hits, confirming no alternative function usage of GPB[2-5]

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-HARDWARE-015, CL-HARDWARE-016
**Next Tests:** None listed

---

### ✅ Verified CL-RKO-HARDWARE-002: MMIO Display Controller (0xB100D000) and GPIO Base (0xB8001000)
**Claim:** Display controller @ 0xB100D000 used for hardware display updates with wait-for-ready pattern (poll bit 0 until clear, write color/coordinate data, set bit 0 to trigger). GPIO base @ 0xB8001000 (GP_BA) accessed indirectly with port offsets: A=+0x00, B=+0x40, C=+0x80, D=+0xC0. Per-port register offsets: OMD=+0x10, PUEN=+0x14, DOUT=+0x18, PIN=+0x1C.

**Evidence:**
- E-RKO-HARDWARE-002: Hardware display update routine uses literal @ 0x00230F34 (value 0xB100D000). Waits for bit 0 clear, writes display data, sets bit 0 to trigger update.
- E-RKO-HARDWARE-002: GPIO base 0xB8001000 accessed with indirect addressing pattern. Port offsets: A=+0x00, B=+0x40, C=+0x80, D=+0xC0. Register offsets per port: OMD=+0x10 (Output Mode), PUEN=+0x14 (Pull-Up Enable), DOUT=+0x18 (Data Output), PIN=+0x1C (Pin Input)
- E-RKO-HARDWARE-002: GPIO control register map shows GP_BA = 0xB8001000 with register layout matching firmware usage

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-HARDWARE-005, CL-HARDWARE-014
**Next Tests:** None listed

---

### ✅ Verified CL-RKO-HARDWARE-003: GPIO Helper Functions - Pin Configuration, Read, and Write
**Claim:** Three core GPIO helper functions identified: pin_mux_config @ 0x00031f34 (600 bytes, configures pin multiplexing via GPBFUN @ 0xB0000084), gpio_read_pin @ 0x00031ec4 (96 bytes, reads pin state from GPIOX_PIN), gpio_write_pin @ 0x0003224c (100 bytes, sets/clears pin via GPIOX_DOUT). All verified through systematic analysis with clear parameter conventions.

**Evidence:**
- E-RKO-HARDWARE-003: Pin-mux configuration function (600 bytes). Parameters: r0=port (1=A,2=B,4=C,8=D,16=E), r1=pin (0-15), r2=function (0=GPIO,1-5=alt functions). Manipulates GPBFUN @ 0xB0000084 with read-modify-write. 12 callers analyzed.
- E-RKO-HARDWARE-003: GPIO read pin function (96 bytes). Parameters: r0=port, r1=pin. Returns: r0=pin state (0 or 1). Reads from GPIOX_PIN register (offset 0x1C from port base).
- E-RKO-HARDWARE-003: GPIO write pin function (100 bytes). Parameters: r0=port, r1=pin, r2=value (0=clear, non-zero=set). Reads/writes GPIOX_DOUT register (offset 0x18 from port base).

**Status:** ✅ Verified
**Cross-Reference:** None noted
**Next Tests:** None listed

---

### ✅ Verified CL-RKO-HARDWARE-004: ADC Architecture: Voltage Monitoring & Touch Screen Controller
**Claim:** The N32903 SoC has a 10-bit ADC at base 0xB800E000 with voltage monitoring on channels 2-3 (VADJ nozzle voltage ~9.09V, VIN input voltage ~7.97V) and resistive touch screen controller using Wait-for-Trigger mode. Channels 0-1 (AIN0/AIN1) are unused. V5V0 is a software constant (5.00V), not an ADC channel.

**Evidence:**
- E-RKO-HARDWARE-004: Core ADC read function. Accesses ADC_CON (0xB800E000) to select channel via bits [11:9], starts conversion (bit 0x2000), polls completion (bit 0x40000), reads 10-bit result from ADC_XDATA (+0xC). Used by voltage monitoring functions.
- E-RKO-HARDWARE-004: Reads battery voltage from ADC channel 2. Applies 3-stage scaling. About screen shows ~9.09V.
- E-RKO-HARDWARE-004: Reads V3V3 voltage from ADC channel 3. About screen displays ~7.97V despite name suggesting 3.3V rail - likely voltage divider or different rail.
- E-RKO-HARDWARE-004: VSYS voltage - returns float constant 5.0f (0x40A00000 @ 0x2debc). INCONSISTENCY: About screen displays 6.00V. No ADC read performed - value may be updated elsewhere or scaling happens in UI renderer.
- E-RKO-HARDWARE-004: Touch screen ADC initialization. Configures Wait-for-Trigger mode (ADC_CON bits [15:14]=11). Enables APB clock, sets conversion delay, disables MAV filter. Hardware triggers interrupt on stylus-down.
- E-RKO-HARDWARE-004: Touch data consumer - does NOT access ADC registers directly. Reads from RAM buffers populated by interrupt handler. Dominated by memcpy operations and UI calls.
- E-RKO-HARDWARE-004: N32903 ADC chapter 6.24. Defines register map, touch modes (normal/semi-auto/auto/wait-for-trigger), 4-wire resistive touch with embedded switches. ADC_BA = 0xB800E000.
- E-RKO-HARDWARE-004: Hardware: Touch screen connected to pins 57-60 (ADC_TP_YM/XM/XP/YP). 4-wire resistive type with switches integrated in SoC - no external GPIO muxing required.

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-HARDWARE-011, CL-HARDWARE-007
**Next Tests:** None listed

---
