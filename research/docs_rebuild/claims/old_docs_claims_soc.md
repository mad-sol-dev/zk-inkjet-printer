# SOC Claims (Old Docs)

Propositional claims synthesized from old_docs (E4 tier).

---

## CL-OLD-SOC-001: N32903K5DN Chip Identification (Old Docs)
- **Status:** supported
- **Confidence:** 0.60
- **Statement:** Old docs identify the SoC as Nuvoton N32903K5DN (LQFP-128) with "DWIN M5" marking and no external SDRAM.
- **Evidence:**
  - E4: E-OLD-SOC-001 (chip identification summary)
  - E4: E-OLD-SOC-004 (no SDRAM init observed)
- **Counter-Evidence:** E1 evidence indicates N32903U5DN with 8 MB DDR (CL-SOC-004).
- **Contradictions:** old_docs/analysis/documentation_contradictions_map.md (SoC identity + RAM size conflicts)
- **Revisions:** None
- **Next Test:** Confirm SDRAM presence via hardware probe and RAM load address tracing in BOOT.bin.
- **Tags:** soc, chip-id, k5dn, contradiction
- **Cross-Reference:** E3-Old CL-RKO-SOC-002 (exact match), E1 CL-SOC-001 (partial overlap)

## CL-OLD-SOC-002: Firmware USB Descriptor Strings Identify W55FA93/Nuvoton
- **Status:** verified
- **Confidence:** 0.90
- **Statement:** Firmware embeds USB descriptor strings "W55FA93 USB Card Reader 1.00" and "Nuvoton" in app.bin.
- **Evidence:**
  - E4: E-OLD-SOC-002 (USB descriptor strings in firmware)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Cross-check offsets in the current APP.bin build to confirm strings are unchanged.
- **Tags:** soc, usb, w55fa93, strings
- **Cross-Reference:** E1 CL-SOC-003 (partial overlap), E1 CL-USB-003 (partial overlap), E3-Old CL-RKO-SOC-002 (exact match)

## CL-OLD-SOC-003: ARM926EJ-S / ARMv5TEJ Core Fingerprint
- **Status:** verified
- **Confidence:** 0.92
- **Statement:** Firmware contains CP15 instructions and ARM/Thumb interworking patterns consistent with an ARM926EJ-S (ARMv5TEJ) core.
- **Evidence:**
  - E4: E-OLD-SOC-003 (CP15 + interworking evidence)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** None required (already corroborated by E1/E3 tiers).
- **Tags:** soc, arm926, armv5tej, cp15
- **Cross-Reference:** E1 CL-SOC-007 (partial overlap), E3-Old CL-RKO-SOC-002 (exact match)

## CL-OLD-SOC-004: No SDRAM Init Seen In Firmware (Old Docs)
- **Status:** hypothesis
- **Confidence:** 0.45
- **Statement:** BOOT.bin and APP.bin show no SDRAM initialization, suggesting SRAM-only execution in the old analysis.
- **Evidence:**
  - E4: E-OLD-SOC-004 (no SDRAM init noted)
- **Counter-Evidence:** E1 CL-SOC-004 (8 MB DDR SDRAM MCP) and boot claims loading APP.bin to 0x03000000.
- **Contradictions:** old_docs/analysis/documentation_contradictions_map.md (RAM size conflict)
- **Revisions:** None
- **Next Test:** Locate DDR init or memory controller setup in BOOT.bin with current toolchain.
- **Tags:** soc, sdram, memory, hypothesis
- **Cross-Reference:** E1 CL-SOC-004 (contradiction), E3-Old CL-RKO-SOC-002 (overlap)
