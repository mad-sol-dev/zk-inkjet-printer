# HARDWARE Evidence

Raw facts extracted from chat transcripts. No interpretation, only concrete observations.

---

## GPIO Allocation

### E-HARDWARE-001: Free GPIO Count
- **Quote:** "- ✅ **41 von 72 GPIOs sind noch frei!**"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=10
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** gpio, availability, count

### E-HARDWARE-002: Printhead + Encoder GPIO Use
- **Quote:** "- 31 GPIOs belegt: 30 für Druckkopf (6× CM504B ICs) + 1 für MT6701 Encoder"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=10
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** gpio, printhead, mt6701

### E-HARDWARE-003: Standard UART Pins Used
- **Quote:** "- Standard-UART (GPA[10-11]) ist **belegt** durch IC2 Druckkopf-Ansteuerung"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=10
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** uart, gpa10, printhead

### E-HARDWARE-004: GPC[4] Boot Config Constraint
- **Quote:** "- GPC[4] ist frei, aber **Boot Config Pin** (CFG[8])"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=10
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** gpc4, boot-config, reserved

### E-HARDWARE-005: Backlight Transistor Pin
- **Quote:** "Q8 = Pin 81, PWM0 /  GPD 0"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=30
- **Date:** 2025-12-20
- **Type:** PCB_TRACE
- **Tags:** gpd0, pwm0, backlight

### E-HARDWARE-006: SD0 Port Usage
- **Quote:** "- SD nutzt GPE[2-7] (Pins 9-14)"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=37
- **Date:** 2025-12-20
- **Type:** PCB_TRACE
- **Tags:** sd0, gpe2-gpe7, allocation

### E-HARDWARE-007: Display Port Usage
- **Quote:** "- Display nutzt GPD[12-14] (Pins 5-7), GPD[0] (Pin 81), GPE[8] (Pin 120)"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=37
- **Date:** 2025-12-20
- **Type:** PCB_TRACE
- **Tags:** display, gpd12-14, gpe8

### E-HARDWARE-008: Pin 120 Multiplexing
- **Quote:** "Perfekt! Pin 120 = NCS0_ / GPE[8] / SD2_DAT[1]"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=29
- **Date:** 2025-12-20
- **Type:** ANALYSIS
- **Tags:** gpe8, ncs0, sd2

### E-HARDWARE-009: GPC Dominance in Used Pins
- **Quote:** "Die Analyse umfasst 31 verwendete Pins über verschiedene GPIO-Gruppen, wobei GPC mit 14 Pins am stärksten vertreten ist."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=10
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** gpc, usage, allocation

### E-HARDWARE-010: Untested GPIO Set
- **Quote:** "6. **Mystery-GPIOs** (35 ungetestete Pins)"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=35
- **Date:** 2025-12-20
- **Type:** ANALYSIS
- **Tags:** untested, gpio, unknown

### E-HARDWARE-011: Power Button Not Traced
- **Quote:** "Der Power-On-Taster, den habe ich nicht ausgemessen."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=34
- **Date:** 2025-12-20
- **Type:** OBSERVATION
- **Tags:** power-button, unknown, gpio

## Peripheral Connections

### E-HARDWARE-012: Display on SPI0
- **Quote:** "Schau dir das Pinout an ($HOME/workspace/zk-inkjet-printer/docs/hardware/zk-dp20/circuit/N32903U5DN_GPIO_Pinout.md), das Display hängt an SPI0 (mir fehlen ein paar Signale, weil nicht durchgeklingelt, aber das reicht.)."
- **Source:** Chats/58_CL_ZK-Inkjet_Projekt_Platine_analysieren_20.12.2025.json#msg=2
- **Date:** 2025-12-20
- **Type:** PCB_TRACE
- **Tags:** display, spi0, pcb-trace

### E-HARDWARE-013: 18-Pin FFC Display Match
- **Quote:** "Das 18Pin FCC und das Pinout spricht für ein \"2,8 zoll TFT Display 240x320 Pixel IPS LCD Display Panel 18Pin FPC SPI ST7789V Driver HH28-18134-01 TFT LCD modul\" (Aliexpress),"
- **Source:** Chats/58_CL_ZK-Inkjet_Projekt_Platine_analysieren_20.12.2025.json#msg=2
- **Date:** 2025-12-20
- **Type:** OBSERVATION
- **Tags:** fpc-18, st7789v, display

### E-HARDWARE-014: Touch Panel Connection
- **Quote:** "das Touch-Panel hängt exakt an den N32903U5DN Touch-Pins"
- **Source:** Chats/58_CL_ZK-Inkjet_Projekt_Platine_analysieren_20.12.2025.json#msg=2
- **Date:** 2025-12-20
- **Type:** PCB_TRACE
- **Tags:** touch, adc, pcb-trace

### E-HARDWARE-015: SPI0 CS/DI Pins
- **Quote:** "- Pin 6 = GPD[13] / SPI0_CS0_ ✅\n- Pin 7 = GPD[14] / SPI0_DI ✅"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=29
- **Date:** 2025-12-20
- **Type:** ANALYSIS
- **Tags:** spi0, gpd13, gpd14

### E-HARDWARE-016: Backlight PWM Pin
- **Quote:** "- Pin 81: GPD[0] → PWM0 (Backlight)"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=37
- **Date:** 2025-12-20
- **Type:** PCB_TRACE
- **Tags:** backlight, pwm0, gpd0

### E-HARDWARE-017: FCC Pin 4 Mapping
- **Quote:** "FCC Pin4 = Pin 120 erneut bestätigt!!"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=30
- **Date:** 2025-12-20
- **Type:** PCB_TRACE
- **Tags:** fcc, pin120, display

### E-HARDWARE-018: Encoder Connection to SoC 117
- **Quote:** "Der magnetische Encoder wird über Pin 6 mit SoC 117 verbunden, was die Gesamtkomplexität der Pinbelegung unterstreicht."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=10
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** mt6701, gpe10, encoder

### E-HARDWARE-019: CM504B IC1 Pin Mapping
- **Quote:** "IC1:\n- Pin 3 (AIN): SoC 79 (GPA0)\n- Pin 5 (BIN): SoC 78 (GPA1)\n- Pin 7 (CIN): SoC 77 (GPA[2])\n- Pin 9 (DIN): SoC 76 (GPA[3])\n- Pin 14 (FIN): SoC 74 (GPA[5])"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=10
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** cm504b, printhead, gpa

### E-HARDWARE-020: CM504B IC2 Pin Mapping
- **Quote:** "IC2:\n- Pin 3 (AIN): SoC 73 (GPA[6])\n- Pin 5 (BIN): SoC 103 (GPA[7])\n- Pin 7 (CIN): SoC 123 (GPA[11])\n- Pin 9 (DIN): SoC 122 (GPA[10])\n\n\n- Pin 14 (FIN): SoC 112 (GPD[6])"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=10
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** cm504b, printhead, gpa

## Power Supply

### E-HARDWARE-021: MVDD Voltage Requirement
- **Quote:** "- MVDD muss 1.8V sein (DDR SDRAM)"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=4
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** mvdd, ddr, power

### E-HARDWARE-022: MVREF Voltage
- **Quote:** "- MVREF (Pins 23, 89) = 0.9V für DDR_VREF"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=4
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** mvref, ddr, power

### E-HARDWARE-023: Printer DC-DC Supplies
- **Quote:** "Dann gibt es diverse... DC-DC-Wandler, um Spannung für den Drucker herzustellen."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=34
- **Date:** 2025-12-20
- **Type:** OBSERVATION
- **Tags:** dc-dc, printhead, power

### E-HARDWARE-024: Nozzle/Battery Voltage Display
- **Quote:** "da gibt es dann einmal... eine Anzeige von wegen Düsenspannung oder Druckerspannung und so weiter. Und Batteriespannung, denke ich, auch."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=34
- **Date:** 2025-12-20
- **Type:** OBSERVATION
- **Tags:** voltage, battery, nozzle

### E-HARDWARE-025: About Screen Voltage Values
- **Quote:** "  - V3V3: 3.97 V, -1\n  - VBAT: 9.09 V\n  - VSYS: 6.00 V, External, M: 6"
- **Source:** Chats/58_CL_ZK-Inkjet_Projekt_Platine_analysieren_20.12.2025.json#msg=1
- **Date:** 2025-12-20
- **Type:** OBSERVATION
- **Tags:** v3v3, vbat, vsys

## Interface Availability

### E-HARDWARE-026: Port A Function Mix
- **Quote:** "- **Port A (GPA)**: 12 Pins - hauptsächlich für UART, SPI, USB Host, SD Card Detect, KPI"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=4
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** gpa, uart, usb-host

### E-HARDWARE-027: Port B Function Mix
- **Quote:** "- **Port B (GPB)**: 16 Pins - hauptsächlich für SD1, USB Host, I2S, Sensor Interface"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=4
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** gpb, i2s, sd1

### E-HARDWARE-028: Port D Function Mix
- **Quote:** "- **Port D (GPD)**: 16 Pins - JTAG, UART, SPI, PWM, NAND, SD2, LCD Control"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=4
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** gpd, pwm, spi

### E-HARDWARE-029: Port E Function Mix
- **Quote:** "- **Port E (GPE)**: 12 Pins - SD0, NAND, SD2, Sensor Sync Signale"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=4
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** gpe, sd0, nand

### E-HARDWARE-030: Available Interfaces List
- **Quote:** "**Komplett verfügbare Interfaces:**\n- **SD0**: 6 Pins (GPE[2-7]) \n- **I2C**: 2 Pins (GPB[13-14])\n- **I2S Audio**: 5 Pins (GPB[2-6])\n- **SPI0**: 4 Pins (GPD[12-15])\n- **PWM**: 4 Kanäle (GPD[0-3])\n- **High-Speed UART**: 4 Pins (GPD[1-4])\n- **JTAG Debug**: 5 Pins (GPD[0-4])"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=10
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** spi0, i2c, pwm

### E-HARDWARE-031: USB Device Pins Unused
- **Quote:** "✅ **Hardware-USB ist komplett ungenutzt** (Pins 26-28, 86)!"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=10
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** usb-device, ud_dp, ud_dm
