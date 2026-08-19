# SOC Evidence (E2 Tier: Sessions)

**Source:** research/sessions/*.md (chronological research logs)
**Tier:** E2 (navigation/context layer, unique session-level evidence)
**Note:** E2 tier captures research narratives, methodology shifts, and strategic context not present in E1/E3 tiers.

---

## SoC Identification and Architecture

### E2-SOC-003: SoC Identification Investigation Narrative
- **Session ID:** S-003 (2025-11-03)
- **File:** sessions/2025-11-03_soc-identification.md
- **Type:** Investigation narrative
- **Summary:** Step-by-step discovery process documenting how Nuvoton N3290X SoC was identified through failed string search → raw memory scan → USB descriptor analysis → datasheet cross-reference. Methodology shows importance of UTF-16LE encoding awareness and multi-source validation.
- **Key Evidence:**
  - Initial string search for "Nuvoton"/"W55FA93" failed (only UI strings found)
  - Raw memory scan at 0x00475140-0x004751A0 revealed USB String Descriptor block
  - UTF-16LE encoded "nuvoTon" string: `6e 12 75 12 76 12 6f` = `n\0u\0v\0o`
  - ASCII string "W55FA93 USB Card Reader 1.00" at 0x00475180
  - Datasheet cross-reference: ARM926EJ-S @ 200MHz matches ARMv5TEJ instructions observed
  - MMIO fingerprint documented: 0xB0000xxx (clock/power), 0xB800Cxxx (USB host likely)
- **Outcome:** 95% confidence SoC identification
- **Research Value:** Demonstrates multi-method validation approach, establishes need for UTF-16 string search tools
- **Cross-Reference:** CL-SOC-001 (SoC identification), CL-USB-001 (USB descriptor location)
- **Tags:** soc, identification, methodology, usb-descriptor, utf16
- **Created:** 2025-11-03
- **Evidence Tier:** E2 (session narrative)

### E2-SOC-016: BSP MMIO Register Extraction Process
- **Session ID:** S-016 (2025-12-27)
- **File:** sessions/2025-12-27_bsp-mmio-registers.md
- **Type:** Ground truth establishment methodology
- **Summary:** Documents BSP header parsing process that extracted 1544 MMIO register definitions from N32901-3 NonOS BSP headers. Establishes provenance for E0 tier artifact (n32903_registers.json) and explains how ground truth registers were obtained for cross-referencing firmware analysis.
- **Key Evidence:**
  - BSP source: `vendor/bsp/N32901-3_NonOS_BSP/Include/N329*.h`
  - Parsing method: C preprocessor macro expansion → struct field extraction
  - Output: `research/findings/n32903_registers.json` (1544 register definitions)
  - Critical discovery: USB_BA=0xB1008000 (NOT 0xB8007000 which is PWM_BA)
  - Validation: BSP headers compiled for exact N32903U5DN variant (highest authority)
- **Outcome:** E0 tier artifact created, USB base address contradiction discovered
- **Research Value:** Establishes methodology for using vendor BSP as ground truth, explains why firmware searches may fail (firmware may use base+offset patterns)
- **Cross-Reference:** CL-RKN-SOC-001 (MMIO map), CL-RKN-SOC-002 (USB_BA correction), CONTRADICTION-USB-001
- **Provenance Link:** E0 artifact `research/findings/n32903_registers.json` → BSP extraction process documented here
- **Tags:** soc, mmio, bsp, ground-truth, methodology, usb-correction
- **Created:** 2025-12-27
- **Evidence Tier:** E2 (extraction process narrative)

---

## Integration Notes

**E2-SOC Evidence Type:** Methodology and provenance narratives that explain:
1. How discoveries were made (investigation process)
2. Why certain approaches were needed (failed attempts)
3. Where ground truth came from (BSP extraction)

**Relationship to Other Tiers:**
- **E0 Tier:** E2-SOC-016 documents provenance of E0 artifact (n32903_registers.json)
- **E1 Tier:** E2-SOC-003 contextualizes why CL-SOC-001 uses USB descriptor evidence
- **E3-New:** E2-SOC-016 explains how CL-RKN-SOC-001 and CL-RKN-SOC-002 were derived

---

*Evidence file created: 2026-01-04*
*E2 Tier: Session narratives and methodology documentation*
