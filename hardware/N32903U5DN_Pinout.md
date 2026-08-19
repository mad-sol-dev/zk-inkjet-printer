# N32903U5DN — Pinbelegung ZK-Inkjet (DP20)

> **Herkunft.** Diese Datei war bis 2026-08-19 **0 Byte gross** — seit dem
> 2025-12-27, also auch schon vor der Rechner-Migration. Der Inhalt unten stammt aus
> `research/docs_rebuild/old_docs/hardware/zk-dp20/circuit/N32903U5DN_GPIO_Pinout.md`
> (2025-12-22), erzeugt in einem Gemini-Thread am 29.12.2025 aus Trace-Arbeit,
> Platinenfotos und Datenblattauszuegen. `research/system_understanding.md` zitiert
> seit Januar eine Datei `N32903U5DN_GPIO_Pinout.md` unter `hardware/`, die es dort
> nie gab.
>
> **Vertrauensgrad.** Die ✅-Marken stammen unveraendert aus dem Quelldokument und
> sind **nicht** durchgaengig nachgeprueft. Zwei Spalten mit sehr verschiedener
> Belastbarkeit stehen hier nebeneinander:
>
> - *GPIO / Signal* und *Alt. Function* — SoC-Seite, gegen das Nuvoton-Datenblatt
>   pruefbar (N3290X.PDF §4.1, S. 20–32). Stichproben siehe unten.
> - *In-Circuit Function* — Platinenseite, stammt aus Sichtpruefung und Durchgangs-
>   messung am Geraet. Von hier aus nicht nachpruefbar; nur am Tisch zu bestaetigen.
>
> Autoritativ fuer den Projektstand ist `research/TRUTH.csv` (CL-HARDWARE-*, CL-HP45-*).

## Stichprobe gegen das Datenblatt (2026-08-19)

Aus `vendor/N3290X.PDF` §4.1 (N3290xUxDN Pin Description) automatisch extrahiert.
Die Tabelle im PDF nutzt vertikal zentrierte Zellen ohne Rahmen; die Extraktion war
nur dort eindeutig, wo eine Zelle genau eine Signalzeile enthaelt. Fuer die restlichen
Pins ist sie **nicht** belastbar — deshalb steht hier nur, was eindeutig war.

**Bestaetigt:**

| Pin | Datenblatt | Deckt sich mit |
| --: | :--------- | :------------- |
| 66 | ADC_AIN[3] | VIN Batteriespannung |
| 79 | GPA[0] | HP-Treiberkette IC1 |
| 81 | GPD[0] / PWM0 / TCK | Backlight teilt sich den Pin mit JTAG TCK |
| 86 | UD_CDET | USB-Detect |
| 103 | GPA[7] / KPI_SO[5] | HP07 |
| 116 | GPE[11] / NCLE | untraced |
| 117 | GPE[10] / NALE | Encoder MT6701 |
| 118 | GPE[9] / NCS1_ | untraced |
| 125–128 | GPB[5..2] / I2S_DOUT, I2S_WS, I2S_BCLK, I2S_MCLK | Pogopin-Header |
| 57–60 | ADC_TP_YM / XM / XP / YP | Touchpanel |

**Abweichung, zu klaeren:**

| Pin | Quelldokument | Datenblatt (Extraktion) | Anmerkung |
| --: | :------------ | :---------------------- | :-------- |
| 120 | GPE[8] / **NCS0** | GPE[8] / SD2_DAT[1] | NCS0 nicht gefunden — moeglich, dass die Zelle weitere Alt-Funktionen enthaelt, die die Extraktion verloren hat |
| 122 | GPA[10] / **URTXD** | GPA[10] / SPI1_CS1_ | URTXD nicht gefunden; Pin 123 URRXD ist bestaetigt. Fuer die Aussage „UART0 ist durch den Druckkopf belegt" ist das der zu haertende Punkt |
| 24 | PLL_VDD18 | PLL_UD_VDD18 | reine Namensvariante |

Offen als `CL-HARDWARE-REC-108` in TRUTH.csv: vollstaendiger Abgleich aller 128 Pins
gegen §4.1 mit einem Parser, der die Zellgrenzen korrekt rekonstruiert.

---

# ZK-Inkjet Hardware Specification (Rev 2.0)

**SoC:** Nuvoton N32903U5DN (128-LQFP)
**System:** Handheld Inkjet Printer
**Status:** Hardware Mapping Verified via Trace & Image Analysis

### ⚠️ Critical Hardware Conflicts & Corrections
1.  **UART0 (Console) is BLOCKED:** Pins 122 (TX) and 123 (RX) are physically wired to **Printhead Driver IC2**. Attempting to use them for debugging will corrupt print data or damage the driver.
2.  **JTAG TCK is Shared:** Pin 81 (TCK) drives the **LCD Backlight (PWM)**. Hardware debugging requires disabling the backlight.
3.  **Pogopin PCB Header:** Pins 125-128 connect to a header on the cartridge PCB, suggesting an external interface (Encoder/Sensor/Cartridge ID) rather than internal generic GPIO.

---

## Master Pinout List (1-128)

**Legend:**
*   ✅ **VERIFIED:** Confirmed by physical trace/image analysis or measurement.
*   ⛔ **BLOCKED:** Physically connected to a peripheral (Printhead, LCD, SD).
*   ⚠️ **CONFLICT/CAUTION:** Pin has a specific condition (shared function/Boot CFG).
*   ❓ **UNTRACED:** Physical connection unknown (might be NC or connected to hidden vias).

|   SoC Pin   | GPIO / Signal | Alt. Function  | **In-Circuit Function / Connection**                | Status |
| :---------: | :------------ | :------------- | :-------------------------------------------------- | :----: |
|    **1**    | GPB[1]        | SDDAT1[0]      | ❓ Untraced                                          |   ❓    |
|    **2**    | GPB[0]        | SDDAT1[1]      | ❓ Untraced                                          |   ❓    |
|    **3**    | GPB[14]       | I2C_SDA        | ❓ Untraced                                          |   ❓    |
|    **4**    | GPB[13]       | I2C_SCL        | ❓ Untraced                                          |   ❓    |
|    **5**    | GPD[12]       | SPI0_CLK       | ✅ **Display SCLK** (Native SPI)                     |   ⛔    |
|    **6**    | GPD[13]       | SPI0_CS0       | ✅ **Display CS**                                    |   ⛔    |
|    **7**    | GPD[14]       | SPI0_DI        | ✅ **Display SDA/MOSI**                              |   ⛔    |
|    **8**    | GPD[15]       | SPI0_DO        | ❓ Untraced                                          |   ❓    |
|    **9**    | GPE[4]        | SD0_DAT[2]     | ✅ **MicroSD Slot D2**                               |   ⛔    |
|   **10**    | GPE[5]        | SD0_DAT[3]     | ✅ **MicroSD Slot D3**                               |   ⛔    |
|   **11**    | GPE[6]        | SD0_CMD        | ✅ **MicroSD Slot CMD**                              |   ⛔    |
|   **12**    | GPE[7]        | SD0_CLK        | ✅ **MicroSD Slot CLK**                              |   ⛔    |
|   **13**    | GPE[2]        | SD0_DAT[0]     | ✅ **MicroSD Slot D0**                               |   ⛔    |
|   **14**    | GPE[3]        | SD0_DAT[1]     | ✅ **MicroSD Slot D1**                               |   ⛔    |
|   **15**    | XIN           | -              | ✅ 12MHz Crystal                                     |   ⛔    |
|   **16**    | XOUT          | -              | ✅ 12MHz Crystal                                     |   ⛔    |
|   **17**    | VDD18         | Core Power     | ✅ 1.8V Supply                                       |   ⛔    |
|   **18**    | VSSQ          | MVDD GND       | ✅ GND                                               |   ⛔    |
|   **19**    | MVDD          | SDRAM Power    | ✅ 1.8V DDR Supply                                   |   ⛔    |
|   **20**    | VSSQ          | -              | ✅ GND                                               |   ⛔    |
|   **21**    | MVDD          | -              | ✅ 1.8V                                              |   ⛔    |
|   **22**    | MVDD          | -              | ✅ 1.8V                                              |   ⛔    |
|   **23**    | MVREF         | DDR Ref        | ✅ 0.9V Reference                                    |   ⛔    |
|   **24**    | PLL_VDD18     | -              | ✅ Power                                             |   ⛔    |
|   **25**    | UD_VSS        | -              | ✅ GND                                               |   ⛔    |
|   **26**    | **UD_DM**     | USB D-         | ✅ **USB-C Connector**                               |   ⚠️    |
|   **27**    | **UD_DP**     | USB D+         | ✅ **USB-C Connector**                               |   ⚠️    |
|   **28**    | UD_VDD33      | USB PHY Pwr    | ✅ 3.3V                                              |   ⛔    |
|   **29**    | **UD_REXT**   | USB Ref        | ✅ **12kΩ Resistor** (USB PHY Active)                |   ⛔    |
|   **30**    | MVDD          | SDRAM Power    | ✅ 1.8V                                              |   ⛔    |
|   **31**    | VSS           | GND            | ✅ GND                                               |   ⛔    |
|   **32**    | GPE[1]        | LVDATA[17]     | ✅ **Printhead IC5 Pin 14 (FIN)** -> HA17            |   ⛔    |
|   **33**    | GPE[0]        | LVDATA[16]     | ✅ **Printhead IC5 Pin 11 (EIN)** -> HA16            |   ⛔    |
|   **34**    | GPC[15]       | LVDATA[15]     | ✅ **Printhead IC5 Pin 9 (DIN)** -> HA15             |   ⛔    |
|   **35**    | GPC[14]       | LVDATA[14]     | ✅ **Printhead IC5 Pin 7 (CIN)** -> HA14             |   ⛔    |
|   **36**    | GPC[13]       | LVDATA[13]     | ✅ **Printhead IC5 Pin 5 (BIN)** -> HA13             |   ⛔    |
|   **37**    | GPC[12]       | LVDATA[12]     | ✅ **Printhead IC5 Pin 3 (AIN)** -> HA12             |   ⛔    |
|   **38**    | GPC[11]       | LVDATA[11]     | ✅ **Printhead IC4 Pin 14 (FIN)** -> HA11            |   ⛔    |
|   **39**    | GPC[10]       | LVDATA[10]     | ✅ **Printhead IC4 Pin 11 (EIN)** -> HA10            |   ⛔    |
|   **40**    | GPC[9]        | LVDATA[9]      | ✅ **Printhead IC4 Pin 9 (DIN)** -> HA09             |   ⛔    |
|   **41**    | GPC[8]        | LVDATA[8]      | ✅ **Printhead IC4 Pin 7 (CIN)** -> HA08             |   ⛔    |
|   **42**    | GPC[7]        | LVDATA[7]      | ✅ **Printhead IC4 Pin 5 (BIN)** -> HA07             |   ⛔    |
|   **43**    | GPC[6]        | LVDATA[6]      | ✅ **Printhead IC4 Pin 3 (AIN)** -> HA06             |   ⛔    |
|   **44**    | GPC[5]        | LVDATA[5]      | ✅ **Printhead IC3 Pin 14 (FIN)** -> HA05            |   ⛔    |
|   **45**    | GPC[4]        | LVDATA[4]      | ✅ **Printhead IC3 Pin 11 (EIN)** -> HA04            |   ⛔    |
|   **46**    | GPC[3]        | LVDATA[3]      | ✅ **Printhead IC3 Pin 9 (DIN)** -> HA03             |   ⛔    |
|   **47**    | GPC[2]        | LVDATA[2]      | ✅ **Printhead IC3 Pin 7 (CIN)** -> HA02             |   ⛔    |
|   **48**    | GPC[1]        | LVDATA[1]      | ✅ **Printhead IC3 Pin 5 (BIN)** -> HA01             |   ⛔    |
|   **49**    | GPC[0]        | LVDATA[0]      | ✅ **Printhead IC3 Pin 3 (AIN)** -> HA00             |   ⛔    |
|   **50**    | GPD[11]       | LVDE           | ✅ **Printhead IC6 Pin 9 (DIN)** -> HA21             |   ⛔    |
|   **51**    | GPD[10]       | LVSYNC         | ✅ **Printhead IC6 Pin 7 (CIN)** -> HA20             |   ⛔    |
|   **52**    | GPD[9]        | LHSYNC         | ✅ **Printhead IC6 Pin 5 (BIN)** -> HA19             |   ⛔    |
|   **53**    | VDD18         | Core Power     | ✅ Power                                             |   ⛔    |
|   **54**    | GPB[15]       | LPCLK          | ✅ **Printhead IC6 Pin 3 (AIN)** -> HA18             |   ⛔    |
|   **55**    | VDD33         | IO Power       | ✅ 3.3V                                              |   ⛔    |
|   **56**    | ADC_VSS       | ADC GND        | ✅ GND                                               |   ⛔    |
|   **57**    | **ADC_TP_YM** | Touch Y-       | ✅ **Touch Screen Y-**                               |   ⛔    |
|   **58**    | **ADC_TP_XM** | Touch X+       | ✅ **Touch Screen X+** (Note: Naming swapped on PCB) |   ⛔    |
|   **59**    | **ADC_TP_XP** | Touch X-       | ✅ **Touch Screen X-** (Note: Naming swapped on PCB) |   ⛔    |
|   **60**    | **ADC_TP_YP** | Touch Y+       | ✅ **Touch Screen Y+**                               |   ⛔    |
|   **61**    | ADC_VDD       | ADC Power      | ✅ 3.3V                                              |   ⛔    |
|   **62**    | ADC_AIN[0]    | -              | X **NC**                                             |   ❓    |
|   **63**    | ADC_AIN[1]    | -              | X **NC**                                             |   ❓    |
|   **64**    | ADC_AIN[2]    | -              | ✅ **VADJ - Nozzle/Printhead voltage**               |   ⛔    |
|   **65**    | VSS           | -              | ✅ GND                                               |   ⛔    |
|   **66**    | ADC_AIN[3]    | -              | ✅ **VIN - Battery voltage**                         |   ⛔    |
|   **67**    | RTC_XOUT      | -              | ✅ **RTC Crystal**                                   |   ⛔    |
|   **68**    | RTC_XIN       | -              | ✅ **RTC Crystal**                                   |   ⛔    |
|   **69**    | RTC_WAKE      | -              | ❓ Untraced                                          |   ❓    |
|   **70**    | RTC_RPWR      | -              | ❓ Untraced                                          |   ❓    |
|   **71**    | RTC_VDD       | -              | ✅ **RTC Power**                                     |   ⛔    |
|   **72**    | VDD33         | IO Power       | ✅ 3.3V                                              |   ⛔    |
|   **73**    | GPA[6]        | SPI1_CS1       | ✅ **Printhead IC2 Pin 3 (AIN)** -> HP06             |   ⛔    |
|   **74**    | GPA[5]        | SPI0_CS1       | ✅ **Printhead IC1 Pin 14 (FIN)** -> HP05            |   ⛔    |
|   **75**    | GPA[4]        | USB_H_DM       | ✅ **Printhead IC1 Pin 11 (EIN)** -> HP04            |   ⛔    |
|   **76**    | GPA[3]        | USB_H_DP       | ✅ **Printhead IC1 Pin 9 (DIN)** -> HP03             |   ⛔    |
|   **77**    | GPA[2]        | LMVSYNC        | ✅ **Printhead IC1 Pin 7 (CIN)** -> HP02             |   ⛔    |
|   **78**    | GPA[1]        | SD_CD          | ✅ **Printhead IC1 Pin 5 (BIN)** -> HP01             |   ⛔    |
|   **79**    | GPA[0]        | -              | ✅ **Printhead IC1 Pin 3 (AIN)** -> Q7:G1            |   ⛔    |
|   **80**    | /RST          | Reset          | ✅ System Reset                                      |   ⛔    |
|   **81**    | GPD[0]        | **PWM0** / TCK | ✅ **LCD Backlight** (Brightness)                    |   ⚠️    |
|   **82**    | GPD[1]        | **HUR_TXD**    | ❓ **Untraced**                                      |   ❓    |
|   **83**    | GPD[2]        | **HUR_RXD**    | ❓ **Untraced**                                      |   ❓    |
|   **84**    | GPD[3]        | HUR_CTS        | ❓ **Untraced**                                      |   ❓    |
|   **85**    | GPD[4]        | HUR_RTS        | ❓ **Untraced**                                      |   ❓    |
|   **86**    | **UD_CDET**   | USB Detect     | ✅ **USB Detect** (Details pending FW analysis)      |   ⚠️    |
|   **87**    | VDD18         | Core Power     | ✅ Power                                             |   ⛔    |
|   **88**    | MVSS          | SDRAM GND      | ✅ GND                                               |   ⛔    |
|   **89**    | MVREF         | DDR Ref        | ✅ 0.9V Reference                                    |   ⛔    |
|  **90-93**  | VSSQ/GND      | -              | ✅ Power/GND                                         |   ⛔    |
|   **94**    | ADAC_HPVDD    | Audio Pwr      | ✅ **SOT-23 Regulator/Ref** (Connected)              |   ⛔    |
|   **95**    | ADAC_HPL      | Audio Out      | ❓ Untraced                                          |   ❓    |
|   **96**    | VSS           | -              | ✅ GND                                               |   ⛔    |
|   **97**    | ADAC_HPR      | Audio Out      | ❓ Untraced                                          |   ❓    |
| **98-102**  | Audio/Pwr     | -              | ❓ Untraced                                          |   ❓    |
|   **103**   | GPA[7]        | KPI_SO5        | ✅ **Printhead IC2 Pin 5 (BIN)** -> HP07             |   ⛔    |
|   **104**   | ND[0]         | Boot CFG       | ❓ Boot Config / NAND                                |   ❓    |
| **105-111** | ND[1-7]       | Boot CFG       | ❓ Boot Config / NAND                                |   ❓    |
|   **112**   | GPD[6]        | NBUSY1         | ✅ **Printhead IC2 Pin 14 (FIN)** -> HP11            |   ⛔    |
|   **113**   | GPD[5]        | NBUSY0         | ✅ **Printhead IC2 Pin 11 (EIN)** -> HP10            |   ⛔    |
|   **114**   | GPD[8]        | NWR            | ✅ **Printhead IC6 Pin 14 (FIN)** -> HP13            |   ⛔    |
|   **115**   | GPD[7]        | NRE            | ✅ **Printhead IC6 Pin 11 (EIN)** -> HP12            |   ⛔    |
|   **116**   | GPE[11]       | NCLE           | ❓ Untraced                                          |   ❓    |
|   **117**   | GPE[10]       | NALE           | ✅ **Encoder MT6701 Pin 6** (Single wire?)           |   ⚠️    |
|   **118**   | GPE[9]        | NCS1           | ❓ Untraced                                          |   ❓    |
|   **119**   | VSS           | GND            | ✅ GND                                               |   ⛔    |
|   **120**   | GPE[8]        | NCS0           | ✅ **Display RS/A0** (Cmd/Data Select)               |   ⛔    |
|   **121**   | VDD33         | IO Power       | ✅ 3.3V                                              |   ⛔    |
|   **122**   | GPA[10]       | **URTXD**      | ✅ **Printhead IC2 Pin 9 (DIN)** -> HP09             |   ⛔    |
|   **123**   | GPA[11]       | **URRXD**      | ✅ **Printhead IC2 Pin 7 (CIN)** -> HP08             |   ⛔    |
|   **124**   | GPB[6]        | I2S_DIN        | ✅ **Q9 -> ?**                                       |   ⚠️    |
|   **125**   | GPB[5]        | I2S_DOUT       | ✅ **Pogopin PCB "Debug" Header**                    |   ⚠️    |
|   **126**   | GPB[4]        | I2S_WS         | ✅ **Pogopin PCB "Debug" Header**                    |   ⚠️    |
|   **127**   | GPB[3]        | I2S_BCLK       | ✅ **Pogopin PCB "Debug" Header**                    |   ⚠️    |
|   **128**   | GPB[2]        | I2S_MCLK       | ✅ **Pogopin PCB "Debug" Header**                    |   ⚠️    |
