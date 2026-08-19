# SOC Evidence

Extracted evidence from chat transcripts. Format: Quote (1-2 lines) + Source + Date + Type + Tags.

---

## Chip Identity & Model Confirmation

### E-SOC-001: Chip Model Identification via Pin Measurements
- **Quote:** "Zwischenergebnis: Das Pinout entspricht exakt der U-Serie (N3290xUxDN). Die K-Serie ist aufgrund der abweichenden Masse- und Referenz-Pins (besonders Pin 31 und 29) auszuschließen."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=11
- **Date:** 2025-12-19
- **Type:** OBSERVATION (hardware measurement analysis)
- **Tags:** chip-id, u-series, pinout, verification

### E-SOC-002: N32903U5DN Confirmed by Memory Size
- **Quote:** "DRAM-Kapazität: Die Angabe '3.83/8M' identifiziert den verbauten Speicher eindeutig als 8 MB. N32903-Serie: 8 MB DDR SDRAM (Übereinstimmung mit Readout)."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=11
- **Date:** 2025-12-19
- **Type:** OBSERVATION (system readout)
- **Tags:** chip-id, memory-size, n32903, verification

### E-SOC-003: W55FA93 String in USB Enumeration
- **Quote:** "scsi 2:0:0:0: Direct-Access W55FA93 SPI Disk 1.00 PQ: 0 ANSI: 0 CCS"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** w55fa93, usb-string, device-identity, scsi

### E-SOC-004: W55FA93 Family Analysis
- **Quote:** "Die Geräte-Strings 'W55FA93 SPI Disk' / 'USB MSC' deuten sehr stark auf die ältere W55FA93-Familie (ARM9) hin"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=12
- **Date:** 2025-09-29
- **Type:** OBSERVATION (analysis)
- **Tags:** w55fa93, arm9, family-analysis

---

## Memory Architecture

### E-SOC-005: DDR SDRAM Voltage Confirmation
- **Quote:** "MVDD (Pin 30): Die gemessene Spannung von ~1,8 V entspricht der Spezifikation für DDR- oder DDR2-SDRAM. Die N32901-Serie (3,3 V SDRAM) ist damit ausgeschlossen."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=11
- **Date:** 2025-12-19
- **Type:** OBSERVATION (voltage measurement)
- **Tags:** mvdd, voltage, ddr-sdram, 1.8v

### E-SOC-006: DDR Reference Voltage
- **Quote:** "MVREF (Pin 23): Das Vorhandensein einer Referenzspannung von ~1,0 V (typisch VMVDD / 2) bestätigt den Einsatz eines DDR-Speicherinterfaces."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=11
- **Date:** 2025-12-19
- **Type:** OBSERVATION (voltage measurement)
- **Tags:** mvref, voltage, ddr-reference, 1.0v

### E-SOC-007: 8 MB DDR in Multi-Chip-Package
- **Quote:** "Beim Nuvoton N32903U5DN sind die 8 MB Arbeitsspeicher nicht extern anzuschließen: Das ist LPDDR/DDR-SDRAM, das im selben Gehäuse mit dem SoC 'gestapelt' ist (Multi-Chip-Package)."
- **Source:** Chats/54_GPT_Nuvoton_N32903U5DN_SRAM_Erklärung_18.12.2025.json#msg=12
- **Date:** 2025-12-18
- **Type:** OBSERVATION (datasheet analysis)
- **Tags:** mcp, 8mb-ddr, stacked-memory

### E-SOC-008: Internal SRAM and Boot ROM
- **Quote:** "Im Chip selbst gibt es nur 8 KB internes SRAM (plus 16 KB Boot-ROM)."
- **Source:** Chats/54_GPT_Nuvoton_N32903U5DN_SRAM_Erklärung_18.12.2025.json#msg=12
- **Date:** 2025-12-18
- **Type:** OBSERVATION (datasheet)
- **Tags:** sram, 8kb, boot-rom, 16kb, internal-memory

### E-SOC-009: DDR Specification (4M×16)
- **Quote:** "Im Datenblatt steht für die N32903x-Serie 4 M×16 DDR-SDRAM → 4 M Wörter × 16 Bit = 64 MBit = 8 MB."
- **Source:** Chats/54_GPT_Nuvoton_N32903U5DN_SRAM_Erklärung_18.12.2025.json#msg=12
- **Date:** 2025-12-18
- **Type:** OBSERVATION (datasheet calculation)
- **Tags:** ddr-spec, 4m-16, memory-calculation

---

## CPU & Architecture

### E-SOC-010: ARM926EJ-S Core at 192 MHz
- **Quote:** "CPU-Takt: Angabe '192M' korreliert mit dem maximalen Takt von 200 MHz des ARM926EJ-S Kerns der N3290x-Serie."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=11
- **Date:** 2025-12-19
- **Type:** OBSERVATION (system readout)
- **Tags:** cpu, arm926ej-s, 192mhz, clock-speed

### E-SOC-011: ARM9 Family Confirmation
- **Quote:** "Die Geräte-Strings 'W55FA93 SPI Disk' / 'USB MSC' deuten sehr stark auf die ältere W55FA93-Familie (ARM9) hin"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=12
- **Date:** 2025-09-29
- **Type:** OBSERVATION (analysis)
- **Tags:** arm9, cpu-family

---

## Series Differentiation (K vs U Series)

### E-SOC-012: U-Serie = Typical, K-Serie = Enhanced
- **Quote:** "Die K-Serie stellt innerhalb der N3290x-Familie die 'Enhanced'-Variante (erweiterte Version) dar, während die U-Serie als 'Typical' (Standardversion) klassifiziert wird."
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=6
- **Date:** 2025-12-29
- **Type:** OBSERVATION (datasheet analysis)
- **Tags:** k-series, u-series, typical, enhanced

### E-SOC-013: K-Serie Has 2 SPI Controllers
- **Quote:** "Während die U-Serie (N3290xUxDN) nur einen SPI-Controller unterstützt, bietet die K-Serie (N3290xKxDN) bis zu zwei unabhängige SPI-Controller."
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=6
- **Date:** 2025-12-29
- **Type:** OBSERVATION (datasheet comparison)
- **Tags:** spi-controller, k-series, u-series, peripheral

### E-SOC-014: GPIO Count Difference (64 vs 70)
- **Quote:** "Die K-Serie bietet bis zu 70 GPIOs, während die U-Serie auf maximal 64 GPIOs begrenzt ist."
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=6
- **Date:** 2025-12-29
- **Type:** OBSERVATION (datasheet comparison)
- **Tags:** gpio-count, k-series, u-series, pinout

---

## Memory Variants Across Series

### E-SOC-015: N32901 = 2 MB SDRAM
- **Quote:** "N32901U1DN / N32901K3DN: 2 MB, 1Mbit x 16, 3,3V SDRAM"
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=3
- **Date:** 2025-12-29
- **Type:** OBSERVATION (datasheet table)
- **Tags:** n32901, 2mb-sdram, 3.3v, memory-variant

### E-SOC-016: N32903 = 8 MB DDR SDRAM
- **Quote:** "N32903U5DN / N32903K5DN: 8 MB, 4Mbit x 16, 1,8V DDR SDRAM"
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=3
- **Date:** 2025-12-29
- **Type:** OBSERVATION (datasheet table)
- **Tags:** n32903, 8mb-ddr, 1.8v, memory-variant

### E-SOC-017: N32905 = 32 MB DDR2 SDRAM
- **Quote:** "N32905U3DN / N32905K5DN: 32 MB, 16Mbit x 16, 1,8V DDR2 SDRAM"
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=3
- **Date:** 2025-12-29
- **Type:** OBSERVATION (datasheet table)
- **Tags:** n32905, 32mb-ddr2, 1.8v, memory-variant

---

## Peripherals & Integrated Features

### E-SOC-018: Integrated Peripherals Overview
- **Quote:** "Display-Steuerung (VPOST): Maximale Auflösung bis zu XVGA (1.024 x 768) für TFT-LCD-Panels. JPEG Codec: Integrierter Beschleuniger. 2D-Grafikbeschleuniger (BitBLT). Sound (SPU): 32-Kanal mit 16-Bit Stereo Audio DAC. USB: 1x USB 2.0 High-Speed Device und 1x USB 1.1 Host."
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=3
- **Date:** 2025-12-29
- **Type:** OBSERVATION (datasheet)
- **Tags:** peripherals, jpeg, 2d, spu, usb, display

### E-SOC-019: Boot Options Supported
- **Quote:** "Die Chips unterstützen verschiedene Boot-Modi direkt beim Start: Speicherkarten (SD, SD-to-NAND Flash Bridge), Raw NAND Flash, SPI Flash, USB"
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=3
- **Date:** 2025-12-29
- **Type:** OBSERVATION (datasheet)
- **Tags:** boot-modes, sd-card, nand, spi, usb-boot

---

## Pin Measurements & Verification

### E-SOC-020: Pin 31 Ground Measurement
- **Quote:** "Pin 31: Niederohmige Verbindung zu Masse (GND/VSS)."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=11
- **Date:** 2025-12-19
- **Type:** OBSERVATION (multimeter measurement)
- **Tags:** pin-31, ground, vss, measurement

### E-SOC-021: Pin 30 MVDD Measurement
- **Quote:** "Pin 30: Messspannung ~1,8 V bis 2,0 V; gepuffert durch einen Keramikkondensator gegen Masse."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=11
- **Date:** 2025-12-19
- **Type:** OBSERVATION (multimeter measurement)
- **Tags:** pin-30, mvdd, 1.8v, measurement

### E-SOC-022: Pin 29 USB Reference Resistor
- **Quote:** "Pin 29: Widerstand von 12 kΩ gegen Masse gemessen."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=11
- **Date:** 2025-12-19
- **Type:** OBSERVATION (multimeter measurement)
- **Tags:** pin-29, ud-rext, 12kohm, usb-reference

### E-SOC-023: Pin 23 MVREF Measurement
- **Quote:** "Pin 23: Messspannung ~1,0 V; gepuffert durch einen Kondensator gegen Masse."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=11
- **Date:** 2025-12-19
- **Type:** OBSERVATION (multimeter measurement)
- **Tags:** pin-23, mvref, 1.0v, measurement

---

## Hardware Connections (Verified)

### E-SOC-024: SD0 Interface Pin Mapping
- **Quote:** "SD0-Interface: Pin 9 (GPE[4]/SD0_DAT[2]), Pin 10 (GPE[5]/SD0_DAT[3]), Pin 11 (GPE[6]/SD0_CMD), Pin 12 (GPE[7]/SD0_CLK - logisch abgeleitet), Pin 13 (GPE[2]/SD0_DAT[0]), Pin 14 (GPE[3]/SD0_DAT[1])"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=16
- **Date:** 2025-12-19
- **Type:** OBSERVATION (PCB tracing)
- **Tags:** sd0, gpe, pins-9-14, boot-medium

### E-SOC-025: MT6701 Encoder Connection Mystery
- **Quote:** "IC-Beschriftung = 6701-AKD aber nur Pin 6 vom SOP-8 geht zum SoC Pin 117. Laut 'Part Number List' im MT6701 MagnTek Dateblatt, ist der MT6701CT-AKD = Analog out auf Pin 3. Das passt nicht zu unserer Belegung"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=18
- **Date:** 2025-12-19
- **Type:** OBSERVATION (PCB analysis - mystery)
- **Tags:** mt6701, pin-117, encoder, discrepancy

---

## Pinout Documentation

### E-SOC-026: Complete GPIO Port Mapping
- **Quote:** "79 GPIO-Pins (GPA, GPB, GPC, GPD, GPE) mit bis zu 4 alternativen Funktionen pro Pin. Port A (GPA): 12 Pins - UART, SPI, USB Host, SD Card Detect, KPI. Port C (GPC): 16 Pins - LCD Data Bus, Sensor Interface, KPI. Port D (GPD): 16 Pins - JTAG, UART, SPI, PWM, NAND, SD2, LCD Control. Port E (GPE): 12 Pins - SD0, NAND, SD2, Sensor Sync."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=2
- **Date:** 2025-12-19
- **Type:** ARTIFACT (pinout documentation)
- **Tags:** gpio-pinout, ports, alternate-functions

### E-SOC-027: Boot Configuration Pins
- **Quote:** "Pins 104-111 + 43-45 sind Boot-Konfigurationspins (CFG[0:10])"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=4
- **Date:** 2025-12-19
- **Type:** OBSERVATION (pinout analysis)
- **Tags:** boot-config, cfg-pins, configuration

---

## Package & Physical Characteristics

### E-SOC-028: LQFP-128 Package
- **Quote:** "Gehäuse: 128-pin LQFP. Pinout-Typ: U-Serie (Typical)."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=11
- **Date:** 2025-12-19
- **Type:** OBSERVATION (physical inspection + datasheet)
- **Tags:** lqfp-128, package, form-factor

---

## MCP Architecture Confirmation

### E-SOC-029: All N3290x Use MCP Design
- **Quote:** "Ja, das ist das Kernkonzept der N3290x-Serie. Nuvoton vermarktet diese Chips als MCP (Multi-Chip-Package). Das bedeutet, dass der Prozessor-Die und der Speicher-Die (DRAM) physisch im selben Gehäuse übereinander gestapelt sind. Es gibt in dieser Serie keine Version 'ohne' internen DRAM."
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=6
- **Date:** 2025-12-29
- **Type:** OBSERVATION (datasheet analysis)
- **Tags:** mcp, stacked-die, architecture, no-external-dram

### E-SOC-030: Part Number Encoding
- **Quote:** "Die Ziffer an der fünften Stelle der Modellnummer verrät dir immer die Größe des verbauten Speichers: N32901... = 2 MB (SDRAM), N32903... = 8 MB (DDR SDRAM), N32905... = 32 MB (DDR2 SDRAM)"
- **Source:** Chats/80_GEM_N3290x__Speicher_Boot_Peripherie_Details_29122025_29.12.2025.json#msg=6
- **Date:** 2025-12-29
- **Type:** OBSERVATION (part number analysis)
- **Tags:** part-number, memory-encoding, naming-scheme

---

## Open Questions / Contradictions

### E-SOC-031: Chip Marking Shows Third-Party Branding
- **Observation:** Physical chip marking shows "M5 dwin.com.cn" (third-party branding), not Nuvoton part number. Chip identification achieved through pin measurements (E-SOC-001, E-SOC-020-023) and system readout (E-SOC-002). USB enumeration reports "W55FA93" (E-SOC-003), which is the old Winbond naming before Nuvoton takeover and N3290x renaming.
- **Evidence:** Physical inspection + E-SOC-001 through E-SOC-003
- **Date:** 2025-12-19
- **Type:** OBSERVATION (chip marking + naming history)
- **Tags:** dwin, m5, chip-marking, w55fa93, n3290x, winbond-nuvoton

---

**Summary:**
- 31 evidence entries extracted
- Coverage: Chip Identity, Memory Architecture, CPU, K vs U Series, Pinout Verification, Hardware Connections
- Primary sources: Chats 57 (hardware analysis), 54 (memory specs), 80 (series comparison), 833 (USB strings)
- Key contradiction: W55FA93 USB string vs N32903U5DN hardware identity
- All measurements confirm N32903U5DN with 8MB DDR in U-Serie package
