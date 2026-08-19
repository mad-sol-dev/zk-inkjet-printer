# HARDWARE Evidence (E3-Old RE-KB Archive)

**Source:** research/findings/re_kb_archive/findings/*.json (31 findings from historical RE-KB)
**Tier:** E3-Old (structured findings from earlier analysis sessions)
**Note:** These findings predate Ghidra optimization (37k→1.3k functions). Ghidra-based evidence should be marked [ghidra-v1].

---

## GPIO, Pins, and Analog Interfaces

### E-RKO-HARDWARE-001: GPIO Port B Configuration - Pins GPB[2-5] Unconfigured
- **RE-KB ID:** finding-0003
- **Status:** verified
- **Type:** behavior
- **Summary:** Pin-mux analysis shows GPB[2-5] (LQFP-128 pins 125-128) are NOT configured in firmware, neither as GPIO nor alternative functions (UART/SPI/I2C/PWM/I2S/SD). Only GPB[0] (Function 2) and GPB[6] (Function 5) are explicitly configured. Systematic analysis of all 12 pin-mux function calls confirms zero GPB[2-5] configurations.
- **Evidence:**
  - E1: Pin-mux configuration function (600 bytes) manipulates GPBFUN @ 0xB0000084 with read-modify-write pattern. Parameters: r0=port, r1=pin, r2=function.; source_type=ghidra; function_address=0x31f34; function_name=pin_mux_config; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Systematic analysis of all 12 pin-mux callers found only 3 Port B configurations: GPB[0] Function 2 @ 0x00031e4c and 0x00031ea4, GPB[6] Function 5 @ 0x0005c210. Zero configurations for GPB[2-5].; source_type=other [ghidra-v1]
  - E3: N32903K5DN LQFP-128 pinout shows Pin 128=GPB[2] (GPIO/I2S_MCLK/SDCLK1), Pin 127=GPB[3] (GPIO/I2S_BCLK/SDCMD1), Pin 126=GPB[4] (GPIO/I2S_WS/SDDAT1[3]), Pin 125=GPB[5] (GPIO/I2S_DOUT/SDDAT1[2]); source_type=pdf; page=645 [ghidra-v1]
  - E4: Alternative function search for I2S_BA @ 0xB1001000, SPI, I2C, UART, PWM controllers yielded 0 hits, confirming no alternative function usage of GPB[2-5]; source_type=other [ghidra-v1]
- **Tags:** gpio, hardware, pin-mux, portb, verified
- **Confidence:** None
- **Component:** None
- **Created:** 2025-11-27T00:13:09.758396Z
- **Updated:** 2025-12-02T03:04:57.066108Z

### E-RKO-HARDWARE-002: MMIO Display Controller (0xB100D000) and GPIO Base (0xB8001000)
- **RE-KB ID:** finding-0006
- **Status:** verified
- **Type:** behavior
- **Summary:** Display controller @ 0xB100D000 used for hardware display updates with wait-for-ready pattern (poll bit 0 until clear, write color/coordinate data, set bit 0 to trigger). GPIO base @ 0xB8001000 (GP_BA) accessed indirectly with port offsets: A=+0x00, B=+0x40, C=+0x80, D=+0xC0. Per-port register offsets: OMD=+0x10, PUEN=+0x14, DOUT=+0x18, PIN=+0x1C.
- **Evidence:**
  - E1: Hardware display update routine uses literal @ 0x00230F34 (value 0xB100D000). Waits for bit 0 clear, writes display data, sets bit 0 to trigger update.; source_type=ghidra; function_address=0x230e04; function_name=hw_display_update; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: GPIO base 0xB8001000 accessed with indirect addressing pattern. Port offsets: A=+0x00, B=+0x40, C=+0x80, D=+0xC0. Register offsets per port: OMD=+0x10 (Output Mode), PUEN=+0x14 (Pull-Up Enable), DOUT=+0x18 (Data Output), PIN=+0x1C (Pin Input); source_type=other [ghidra-v1]
  - E3: GPIO control register map shows GP_BA = 0xB8001000 with register layout matching firmware usage; source_type=pdf; page=646 [ghidra-v1]
- **Tags:** mmio, display, gpio, verified
- **Confidence:** None
- **Component:** None
- **Created:** 2025-11-27T00:14:06.741544Z
- **Updated:** 2025-12-02T03:05:27.684680Z

### E-RKO-HARDWARE-003: GPIO Helper Functions - Pin Configuration, Read, and Write
- **RE-KB ID:** finding-0008
- **Status:** verified
- **Type:** behavior
- **Summary:** Three core GPIO helper functions identified: pin_mux_config @ 0x00031f34 (600 bytes, configures pin multiplexing via GPBFUN @ 0xB0000084), gpio_read_pin @ 0x00031ec4 (96 bytes, reads pin state from GPIOX_PIN), gpio_write_pin @ 0x0003224c (100 bytes, sets/clears pin via GPIOX_DOUT). All verified through systematic analysis with clear parameter conventions.
- **Evidence:**
  - E1: Pin-mux configuration function (600 bytes). Parameters: r0=port (1=A,2=B,4=C,8=D,16=E), r1=pin (0-15), r2=function (0=GPIO,1-5=alt functions). Manipulates GPBFUN @ 0xB0000084 with read-modify-write. 12 callers analyzed.; source_type=ghidra; function_address=0x31f34; function_name=pin_mux_config; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: GPIO read pin function (96 bytes). Parameters: r0=port, r1=pin. Returns: r0=pin state (0 or 1). Reads from GPIOX_PIN register (offset 0x1C from port base).; source_type=ghidra; function_address=0x31ec4; function_name=gpio_read_pin; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E3: GPIO write pin function (100 bytes). Parameters: r0=port, r1=pin, r2=value (0=clear, non-zero=set). Reads/writes GPIOX_DOUT register (offset 0x18 from port base).; source_type=ghidra; function_address=0x3224c; function_name=gpio_write_pin; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
- **Tags:** gpio, functions, pin-mux, verified
- **Confidence:** None
- **Component:** None
- **Created:** 2025-11-27T00:14:39.627081Z
- **Updated:** 2025-12-02T03:05:50.622635Z

### E-RKO-HARDWARE-004: ADC Architecture: Voltage Monitoring & Touch Screen Controller
- **RE-KB ID:** finding-0031
- **Status:** verified
- **Type:** behavior
- **Summary:** The N32903 SoC has a 10-bit ADC at base 0xB800E000 with voltage monitoring on channels 2-3 (VADJ nozzle voltage ~9.09V, VIN input voltage ~7.97V) and resistive touch screen controller using Wait-for-Trigger mode. Channels 0-1 (AIN0/AIN1) are unused. V5V0 is a software constant (5.00V), not an ADC channel.
- **Evidence:**
  - E1: Core ADC read function. Accesses ADC_CON (0xB800E000) to select channel via bits [11:9], starts conversion (bit 0x2000), polls completion (bit 0x40000), reads 10-bit result from ADC_XDATA (+0xC). Used by voltage monitoring functions.; source_type=ghidra; function_address=0x2df28; function_name=adc_read_channel; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Reads battery voltage from ADC channel 2. Applies 3-stage scaling. About screen shows ~9.09V.; source_type=ghidra; function_address=0x2dee8; function_name=voltage_read_vbat; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E3: Reads V3V3 voltage from ADC channel 3. About screen displays ~7.97V despite name suggesting 3.3V rail - likely voltage divider or different rail.; source_type=ghidra; function_address=0x2dec0; function_name=voltage_read_v3v3; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E4: VSYS voltage - returns float constant 5.0f (0x40A00000 @ 0x2debc). INCONSISTENCY: About screen displays 6.00V. No ADC read performed - value may be updated elsewhere or scaling happens in UI renderer.; source_type=ghidra; function_address=0x2deb4; function_name=voltage_read_vsys; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E5: Touch screen ADC initialization. Configures Wait-for-Trigger mode (ADC_CON bits [15:14]=11). Enables APB clock, sets conversion delay, disables MAV filter. Hardware triggers interrupt on stylus-down.; source_type=ghidra; function_address=0x8adcc; function_name=adc_touch_init; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E6: Touch data consumer - does NOT access ADC registers directly. Reads from RAM buffers populated by interrupt handler. Dominated by memcpy operations and UI calls.; source_type=ghidra; function_address=0x618dc; function_name=touch_adc_read; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E7: N32903 ADC chapter 6.24. Defines register map, touch modes (normal/semi-auto/auto/wait-for-trigger), 4-wire resistive touch with embedded switches. ADC_BA = 0xB800E000.; source_type=pdf; page=812 [ghidra-v1]
  - E8: Hardware: Touch screen connected to pins 57-60 (ADC_TP_YM/XM/XP/YP). 4-wire resistive type with switches integrated in SoC - no external GPIO muxing required.; source_type=other [ghidra-v1]
- **Tags:** hardware, adc, touch, voltage, soc
- **Confidence:** None
- **Component:** adc
- **Created:** 2025-12-20T21:58:02.202200Z
- **Updated:** 2025-12-20T23:24:02.435551Z

