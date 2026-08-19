# HARDWARE Evidence (E2 Tier: Sessions)

**Source:** research/sessions/*.md (chronological research logs)
**Tier:** E2 (navigation/context layer, unique session-level evidence)
**Note:** E2 tier captures hardware-level analysis narratives not present in E1/E3 tiers.

---

## ADC and Peripheral Mapping

### E2-HARDWARE-014: ADC Channel Mapping and Encoder Interface Analysis
- **Session ID:** S-014 (2025-12-21)
- **File:** sessions/2025-12-21_adc-encoder-analysis.md
- **Type:** Hardware mapping analysis
- **Summary:** Deep-dive session analyzing ADC (Analog-to-Digital Converter) channel assignments and encoder interface on the ZK-INKJET printer hardware. Mapped physical inputs to firmware ADC channels and identified voltage monitoring and touch screen controller usage.
- **Key Evidence:**
  - ADC base address: 0xB800E000 (per BSP headers)
  - ADC channels identified:
    * Channel 0: Battery voltage monitoring (lithium cell voltage sense)
    * Channel 1: Touch screen X-axis position
    * Channel 2: Touch screen Y-axis position
    * Channel 3: Touch screen pressure/Z-axis
    * Channel 4: Encoder position (rotary encoder for menu navigation)
    * Channels 5-7: Unassigned/reserved
  - ADC configuration:
    * Resolution: 12-bit (0-4095 counts)
    * Reference voltage: 3.3V (typical for N32903)
    * Conversion trigger: Software poll or timer-based
  - Encoder interface:
    * Type: Incremental rotary encoder (likely optical)
    * Signal processing: ADC-based position sensing (not GPIO interrupt)
    * Integration: Menu scroll detection in UI firmware
  - Touch screen controller:
    * 4-wire resistive touch (X, Y, Z channels)
    * Calibration data stored in firmware or config partition
- **Outcome:** Complete ADC channel map documented, voltage monitoring architecture understood
- **Research Value:** Hardware-level peripheral mapping, shows how physical controls interface with firmware
- **Cross-Reference:** CL-HARDWARE-007 (ADC channels), CL-HARDWARE-010 (encoder interface), CL-RKO-HARDWARE-031 (E3-Old ADC architecture)
- **Hardware Implications:** Battery voltage monitoring via ADC suggests low-voltage detection for print quality control
- **Tags:** hardware, adc, encoder, touch-screen, voltage-monitoring, peripherals
- **Created:** 2025-12-21
- **Evidence Tier:** E2 (hardware analysis narrative)

---

## Integration Notes

**E2-HARDWARE Evidence Type:** Hardware-level analysis narratives that document:
1. Physical peripheral mappings (ADC channels to real-world inputs)
2. Signal processing architecture (ADC-based vs GPIO-based)
3. Hardware/firmware integration points

**Relationship to Other Tiers:**
- **E1 Tier:** E2-HARDWARE-014 provides hardware context for CL-HARDWARE-007 (ADC usage)
- **E3-Old:** Complements CL-RKO-HARDWARE-031 (ADC architecture) with channel-level detail
- **BSP (E0):** ADC base address 0xB800E000 confirmed via BSP headers (n32903_registers.json)

**Hardware Context:** Understanding ADC channel assignments is critical for:
1. Battery management (channel 0 voltage monitoring)
2. Touch UI implementation (channels 1-3 position sensing)
3. Menu navigation (channel 4 encoder position)

---

*Evidence file created: 2026-01-04*
*E2 Tier: Hardware analysis and peripheral mapping*
