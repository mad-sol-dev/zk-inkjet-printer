# SOC Evidence (Old Docs)

Extracted evidence from research/old_docs/ (E4 tier). Format: Content (1-3 lines) + Source + Date + Type + Provenance + Tags.

---

### E-OLD-SOC-001: N32903K5DN Chip Identification
- **Content:** Chip identified as Nuvoton N32903K5DN (LQFP-128), marked "DWIN M5", with K5DN variant noted as no external SDRAM.
- **Source:** old_docs/findings/chip_identification.md#Finding
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** soc, chip-id, n32903, k5dn, lqfp-128, marking
- **Note:** [ghidra-v1]

### E-OLD-SOC-002: USB Descriptor Strings (W55FA93 + Nuvoton)
- **Content:** Firmware contains UTF-16LE descriptor strings "W55FA93 USB Card Reader 1.00" (0x00475180) and vendor "Nuvoton" (0x00475140).
- **Source:** old_docs/findings/chip_identification.md#USB-Descriptor-Block
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** usb, descriptor, w55fa93, nuvoton, strings
- **Note:** [ghidra-v1]

### E-OLD-SOC-003: ARM926EJ-S / ARMv5TEJ Fingerprint
- **Content:** CP15 instructions and ARM/Thumb interworking stubs indicate an ARM926EJ-S (ARMv5TEJ) core and N32903-series vector layout.
- **Source:** old_docs/findings/chip_identification.md#CPU--Architecture-Fingerprint
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** arm926, armv5tej, cp15, architecture
- **Note:** [ghidra-v1]

### E-OLD-SOC-004: No SDRAM Initialization Observed
- **Content:** BOOT.bin and APP.bin show no SDRAM init routines; RAM references stay within SRAM at 0xFF000000, pointing to K5DN "no external SDRAM" variant.
- **Source:** old_docs/findings/chip_identification.md#Memory-Configuration
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** sram, no-sdram, k5dn, memory
- **Note:** [ghidra-v1]

### E-OLD-SOC-005: N32903 Memory Map Summary
- **Content:** Quick reference lists GCR_BA 0xB0000000, APB 0xB8000000, SRAM_BA 0xFF000000, and IBR_BA 0xFFFF0000 as core regions.
- **Source:** old_docs/reference/N32903_cheat_sheet.md#System-Memory-Map
- **Date:** 2025-11-03
- **Type:** REFERENCE
- **Provenance:** None
- **Tags:** memory-map, gcr, apb, sram, ibr
