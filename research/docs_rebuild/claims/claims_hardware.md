# HARDWARE Claims

Propositional claims synthesized from evidence. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## GPIO Allocation

### ⚠️ CL-HARDWARE-001: GPIO Count And Usage Split
**Claim:** The SoC exposes 72 GPIOs, with 31 used and 41 remaining free per pinout analysis.

**Evidence:**
- E-HARDWARE-001: Reports 41 of 72 GPIOs are free.
- E-HARDWARE-002: Reports 31 GPIOs are occupied (30 printhead + 1 encoder).
- E-SOC-026: Documents the complete 72-GPIO pinout table.

**Status:** ⚠️ Supported (consistent analysis entries, not yet confirmed by PCB trace)

**Next Tests:** Validate the 31/41 split by continuity probing a random sample from both the used and free sets.

---

### ⚠️ CL-HARDWARE-002: Printhead Uses 30 GPIOs Via CM504B Drivers
**Claim:** The printhead driver section uses 30 GPIOs routed into six CM504B ICs, including multiple GPA lines.

**Evidence:**
- E-HARDWARE-002: States 30 GPIOs are allocated to six CM504B ICs.
- E-HARDWARE-019: Maps CM504B IC1 inputs to GPA pins.
- E-HARDWARE-020: Maps CM504B IC2 inputs to GPA and GPD pins.

**Status:** ⚠️ Supported (multi-entry mapping, but not fully traced)

**Next Tests:** Trace two additional CM504B ICs to confirm their GPIO groups and total pin count.

---

### ⚠️ CL-HARDWARE-003: MT6701 Encoder Consumes One GPIO
**Claim:** The MT6701 encoder uses a single GPIO connected to SoC pin 117 (GPE[10]/NALE), consuming one GPIO line.

**Evidence:**
- E-HARDWARE-002: Notes one GPIO used for MT6701.
- E-HARDWARE-018: Describes encoder connection to SoC pin 117.
- E-SOC-025: Confirms MT6701 pin 6 maps to SoC pin 117 (GPE[10]/NALE).

**Status:** ⚠️ Supported (cross-cluster consistency, no direct trace listed)

**Next Tests:** Continuity probe MT6701 pin 6 to SoC pin 117 on the PCB to confirm the mapping.

---

### 🔬 CL-HARDWARE-004: Large Untested GPIO Set Remains
**Claim:** There are 35 GPIOs categorized as untested and therefore of unknown allocation.

**Evidence:**
- E-HARDWARE-010: Labels 35 GPIOs as mystery/untested.

**Status:** 🔬 Hypothesis (single analysis entry)

**Next Tests:** Create a probing matrix for the 35 pins and record continuity to connectors, test pads, and peripherals.

---

## Peripheral Connections

### ⚠️ CL-HARDWARE-005: Display Uses SPI0 And Dedicated Control Pins
**Claim:** The display is connected to SPI0 on GPD[12-15] with chip-select on GPE[8] (pin 120), indicating SPI0 is occupied by the display.

**Evidence:**
- E-HARDWARE-012: States the display is on SPI0.
- E-HARDWARE-007: Lists GPD[12-14], GPD[0], and GPE[8] as display-related pins.
- E-HARDWARE-015: Confirms SPI0 CS0 on GPD[13] and SPI0 DI on GPD[14].
- E-HARDWARE-017: Confirms FFC pin 4 maps to pin 120.
- E-HARDWARE-008: Identifies pin 120 as NCS0_/GPE[8].

**Status:** ⚠️ Supported (multiple PCB traces and analysis entries)

**Next Tests:** Trace SPI0 CLK and DO lines to confirm all SPI0 signals are fully occupied by the display.

---

### ⚠️ CL-HARDWARE-006: Backlight Controlled By PWM0 On GPD0
**Claim:** The display backlight is driven by PWM0 on GPD[0] (SoC pin 81) via transistor Q8.

**Evidence:**
- E-HARDWARE-005: Identifies Q8 connected to pin 81, PWM0/GPD0.
- E-HARDWARE-016: Confirms pin 81 is GPD[0] used for PWM0 backlight.

**Status:** ⚠️ Supported (PCB trace corroboration)

**Next Tests:** Measure PWM waveform at Q8 during brightness changes to confirm runtime control.

---

### 🔬 CL-HARDWARE-007: Touch Panel Routed To SoC Touch ADC Pins
**Claim:** The touch panel is wired directly to the N32903U5DN touch ADC pins.

**Evidence:**
- E-HARDWARE-014: States the touch panel connects exactly to SoC touch pins.

**Status:** 🔬 Hypothesis (single PCB trace note without pin list)

**Next Tests:** Identify touch controller pins on the FFC and map them to specific SoC ADC pins.

---

### 🔬 CL-HARDWARE-008: Display Module Likely ST7789V 18-Pin SPI TFT
**Claim:** The display module likely matches an 18-pin SPI TFT panel with ST7789V controller.

**Evidence:**
- E-HARDWARE-013: Suggests an 18-pin ST7789V SPI display module based on FFC pinout.

**Status:** 🔬 Hypothesis (single observation)

**Next Tests:** Compare the observed FFC pin order to a known ST7789V 18-pin module datasheet.

---

## Power Supply

### 🔬 CL-HARDWARE-009: MVDD Rail Target Is 1.8 V
**Claim:** The MVDD rail for DDR SDRAM is expected to be 1.8 V.

**Evidence:**
- E-HARDWARE-021: States MVDD must be 1.8 V for DDR SDRAM.

**Status:** 🔬 Hypothesis (analysis note only)

**Next Tests:** Measure MVDD at the DDR supply pin during operation to verify 1.8 V.

---

### 🔬 CL-HARDWARE-010: MVREF Rail Target Is 0.9 V
**Claim:** The MVREF pins (23 and 89) are expected to be 0.9 V for DDR VREF.

**Evidence:**
- E-HARDWARE-022: Specifies MVREF at 0.9 V on pins 23 and 89.

**Status:** 🔬 Hypothesis (analysis note only)

**Next Tests:** Probe MVREF pins with a high-impedance DMM to confirm 0.9 V.

---

### ⚠️ CL-HARDWARE-011: Firmware UI Shows Battery And System Voltages
**Claim:** The device UI reports V3V3, VBAT, and VSYS values, indicating firmware-level voltage monitoring.

**Evidence:**
- E-HARDWARE-025: About screen lists V3V3, VBAT, and VSYS readings.

**Status:** ⚠️ Supported (single observation with explicit values)

**Next Tests:** Compare UI voltage readings to multimeter measurements at the corresponding rails.

---

### 🔬 CL-HARDWARE-012: Printhead Voltages Use Dedicated DC-DC Converters
**Claim:** Dedicated DC-DC converters provide supply voltages for the printhead/nozzle subsystem.

**Evidence:**
- E-HARDWARE-023: Notes multiple DC-DC converters for printer voltages.
- E-HARDWARE-024: Mentions nozzle/printhead voltage indicators and battery voltage.

**Status:** 🔬 Hypothesis (observational statements without trace)

**Next Tests:** Identify DC-DC converter outputs by probing inductors and correlate to printhead rails.

---

## Interface Availability

### ⚠️ CL-HARDWARE-013: Standard UART On GPA[10-11] Is Occupied
**Claim:** The standard UART on GPA[10-11] is already used by the printhead control path, so it is not available for other interfaces.

**Evidence:**
- E-HARDWARE-003: Reports GPA[10-11] UART is occupied by IC2 printhead control.
- E-HARDWARE-020: Maps CM504B IC2 inputs including GPA[10] and GPA[11].

**Status:** ⚠️ Supported (pin mapping corroborates UART lines used by CM504B)

**Next Tests:** Trace GPA[10-11] to confirm they only connect to printhead drivers and not a header.

---

### ⚠️ CL-HARDWARE-014: SPI0 Interface Is Used By The Display
**Claim:** SPI0 is allocated to the display and is not available for reuse without rework.

**Evidence:**
- E-HARDWARE-012: States display is on SPI0.
- E-HARDWARE-015: Confirms SPI0 CS0 and DI on GPD[13-14].
- E-HARDWARE-007: Lists display signals on GPD[12-14] and GPE[8].

**Status:** ⚠️ Supported (multi-evidence trace and mapping)

**Next Tests:** Confirm SPI0 CLK/DO line usage by continuity from SoC to display FFC pins.

---

### 🔬 CL-HARDWARE-015: I2C On GPB[13-14] Appears Unused And Available
**Claim:** The I2C bus on GPB[13-14] is listed as available and appears unused, making it a candidate interface.

**Evidence:**
- E-HARDWARE-030: Lists I2C on GPB[13-14] as completely available.

**Status:** 🔬 Hypothesis (availability list without trace)

**Next Tests:** Check GPB[13-14] for pull-ups and activity during boot to confirm they are unused.

---

### 🔬 CL-HARDWARE-016: High-Speed UART Pins GPD[1-4] Are Candidate USB-CDC GPIOs
**Claim:** GPD[1-4] are listed as a free high-speed UART block and are the primary GPIO candidates for implementing USB-CDC via a UART bridge, while GPD[0] is already used for backlight PWM.

**Evidence:**
- E-HARDWARE-030: Lists high-speed UART on GPD[1-4] as completely available.
- E-HARDWARE-005: Shows GPD[0] used for PWM0 backlight.
- E-HARDWARE-016: Confirms GPD[0] is PWM0 for backlight.

**Status:** 🔬 Hypothesis (availability list without PCB trace confirmation)

**Next Tests:** Probe GPD[1-4] for continuity to test pads or headers and check for runtime toggling.

---

### 🔬 CL-HARDWARE-017: USB Device Pins Are Unused And Available For USB-CDC
**Claim:** The SoC USB device pins (pins 26-28 and 86) are reported unused, implying the native USB device interface is available for USB-CDC via the on-chip UDC at 0xB1008000.

**Evidence:**
- E-HARDWARE-031: Reports USB device pins 26-28 and 86 are unused.
- E-USB-010: Identifies UDC base address 0xB1008000 in firmware.

**Status:** 🔬 Hypothesis (unused status not confirmed by PCB trace)

**Next Tests:** Verify continuity from pins 26-28/86 to any connectors; confirm no competing loads on DP/DM.

---

### 🔬 CL-HARDWARE-018: GPC[4] Is Free But Reserved For Boot Configuration
**Claim:** GPC[4] is physically free but constrained as boot configuration pin CFG[8], limiting safe reuse.

**Evidence:**
- E-HARDWARE-004: Notes GPC[4] is free but a boot config pin.

**Status:** 🔬 Hypothesis (single analysis entry)

**Next Tests:** Review boot strap requirements in the SoC datasheet before repurposing GPC[4].

---
