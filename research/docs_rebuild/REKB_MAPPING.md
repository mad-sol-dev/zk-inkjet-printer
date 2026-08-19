# RE-KB to Claims Mapping

**Phase 2C: RE-KB Integration**
**Generated:** 2026-01-03 21:46:56 UTC
**RE-KB Findings:** 2
**Claims Analyzed:** 118 across 7 clusters

---

## Mapping Summary

| RE-KB Finding | Type | Maps To | Relationship | Action |
|---------------|------|---------|--------------|--------|
| finding-0001 | behavior | CL-BOOT-007, CL-BOOT-016 | PARTIAL_OVERLAP | Add new claim for ARM/Thumb mixed-mode and add RE-KB reference to BOOT claims |
| finding-0002 | behavior | CL-HARDWARE-017, CL-USB-010 | PARTIAL_OVERLAP | Reconcile: BSP map shows USBD_BA/USB_BA=0xB1008000 while 0xB8007000 maps to PWM_BA; verify firmware refs |

---

## Finding-by-Finding Analysis

### finding-0001: Firmware uses ARM/Thumb Mixed-Mode Code
**RE-KB Status:** verified
**RE-KB Tags:** architecture, thumb, arm, foundation
**RE-KB Confidence:** 1.0

**Mapping:**
- Maps to: CL-BOOT-007 (APP.bin Stored at SD Offset 0x100000 with ARM IVT), CL-BOOT-016 (APP.bin is a Proprietary Resource Container Loaded into RAM)
- Relationship: PARTIAL_OVERLAP

**Comparison:**
- RE-KB summary: "APP.bin firmware contains both ARM (32-bit) and Thumb (16-bit) instruction sets. Region 0x00210000-0x0021FFFF uses Thumb mode (2-byte instructions), while other regions use ARM mode (4-byte instructions)."
- Claim statement: "APP.bin appears in the SD image at offset 0x100000 and contains an ARM interrupt vector table." / "APP.bin is a ~2.6 MB proprietary resource container that the bootloader loads into RAM."

**Evidence Delta:**
- RE-KB evidence count: 1
- Claim evidence count: 2 (CL-BOOT-007), 2 (CL-BOOT-016)
- Quality: Claims stronger (multiple E1 entries; RE-KB evidence is a single analysis note without direct Ghidra references)

**Recommendation:**
Add a new BOOT claim focused on mixed ARM/Thumb code regions and attach the RE-KB finding as an E3 pointer; keep existing claims unchanged.

---

### finding-0002: N32903 MMIO Register Map Extracted from BSP
**RE-KB Status:** in_progress
**RE-KB Tags:** hardware, mmio, bsp, foundation, usb
**RE-KB Confidence:** 1.0

**Mapping:**
- Maps to: CL-HARDWARE-017 (USB Device Pins Are Unused And Available For USB-CDC), CL-USB-010 (USB Device Controller Base Address)
- Relationship: PARTIAL_OVERLAP

**Comparison:**
- RE-KB summary: "Extracted 1544 hardware register definitions from N32901-3 NonOS BSP headers. Key peripherals: USB_BA=0xB1008000, GPIO_BA=0xB8001000, ADC_BA=0xB800E000, TMR_BA=0xB8002000, SPI0_BA=0xB800C000."
- Register map detail (BSP extraction): USB_BA/USBD_BA = 0xB1008000; PWM_BA = 0xB8007000 (from research/findings/n32903_registers.json).
- Claim statement: "The SoC USB device pins (pins 26-28 and 86) are reported unused, implying the native USB device interface is available for USB-CDC via the on-chip UDC at 0xB1008000." / "USB Device Controller (UDC) registers are mapped at MMIO base address 0xB8007000, with 10 references found in APP.bin."

**Evidence Delta:**
- RE-KB evidence count: 1
- Claim evidence count: 2 (CL-HARDWARE-017), 1 (CL-USB-010)
- Quality: RE-KB stronger for base address provenance (scripted BSP extraction + artifact). BSP map indicates 0xB8007000 is PWM_BA, suggesting CL-USB-010 may be misattributed unless firmware refs are confirmed to USBD registers.

**Recommendation:**
Cross-reference the finding in CL-HARDWARE-017, re-validate the APP.bin references attributed to UDC, and update CL-USB-010 if those references target PWM or another peripheral. Add a SOC claim covering the BSP-derived register map once validated.
Resolution note (2026-01-03): Ghidra MCP scalar searches in `ZK-INKJET-NANO-APP.bin.orig` found 0 refs for both 0xB8007000 and 0xB1008000; firmware usage remains unconfirmed.

---

## Gap Analysis

### Claims with NO RE-KB finding:
- CL-BOOT-001
- CL-BOOT-002
- CL-BOOT-003
- CL-BOOT-004
- CL-BOOT-005
- CL-BOOT-006
- CL-BOOT-008
- CL-BOOT-009
- CL-BOOT-010
- CL-BOOT-011
- CL-BOOT-012
- CL-BOOT-013
- CL-BOOT-014
- CL-BOOT-015
- CL-HARDWARE-001
- CL-HARDWARE-002
- CL-HARDWARE-003
- CL-HARDWARE-004
- CL-HARDWARE-005
- CL-HARDWARE-006
- CL-HARDWARE-007
- CL-HARDWARE-008
- CL-HARDWARE-009
- CL-HARDWARE-010
- CL-HARDWARE-011
- CL-HARDWARE-012
- CL-HARDWARE-013
- CL-HARDWARE-014
- CL-HARDWARE-015
- CL-HARDWARE-016
- CL-HARDWARE-018
- CL-HP45-001
- CL-HP45-002
- CL-HP45-003
- CL-HP45-004
- CL-HP45-005
- CL-HP45-006
- CL-HP45-007
- CL-HP45-008
- CL-HP45-009
- CL-HP45-010
- CL-HP45-011
- CL-HP45-012
- CL-HP45-013
- CL-HP45-014
- CL-HP45-015
- CL-HP45-016
- CL-SOC-001
- CL-SOC-002
- CL-SOC-003
- CL-SOC-004
- CL-SOC-005
- CL-SOC-006
- CL-SOC-007
- CL-SOC-008
- CL-SOC-009
- CL-SOC-010
- CL-SOC-011
- CL-SOC-012
- CL-SOC-013
- CL-SOC-014
- CL-SOC-015
- CL-SOC-016
- CL-SOC-017
- CL-SOC-018
- CL-STORAGE-001
- CL-STORAGE-002
- CL-STORAGE-003
- CL-STORAGE-004
- CL-STORAGE-005
- CL-STORAGE-006
- CL-STORAGE-007
- CL-STORAGE-008
- CL-STORAGE-009
- CL-STORAGE-010
- CL-STORAGE-011
- CL-STORAGE-012
- CL-STORAGE-013
- CL-STORAGE-014
- CL-STORAGE-015
- CL-STORAGE-016
- CL-TOOL-001
- CL-TOOL-002
- CL-TOOL-003
- CL-TOOL-004
- CL-TOOL-005
- CL-TOOL-006
- CL-TOOL-007
- CL-TOOL-008
- CL-TOOL-009
- CL-TOOL-010
- CL-TOOL-011
- CL-TOOL-012
- CL-TOOL-013
- CL-TOOL-014
- CL-TOOL-015
- CL-TOOL-016
- CL-TOOL-017
- CL-USB-001
- CL-USB-002
- CL-USB-003
- CL-USB-004
- CL-USB-005
- CL-USB-006
- CL-USB-007
- CL-USB-008
- CL-USB-009
- CL-USB-011
- CL-USB-012
- CL-USB-013
- CL-USB-014
- CL-USB-015
- CL-USB-016
- CL-USB-017

### RE-KB findings with NO claim match:
- finding-0001 (Thumb-mode region detail is not represented as a dedicated claim)

---

## Evidence Upgrade Opportunities

- CL-HARDWARE-017: Potential upgrade from hypothesis to supported once BSP-derived USBD_BA=0xB1008000 is reconciled with firmware references.
- CL-USB-010: Re-evaluate after confirming whether 0xB8007000 references in APP.bin are PWM-related; update base address if needed.

---

## Recommendations

1. **Merge candidates:** None (keep findings as RE-KB sources and add cross-references)
2. **Cross-reference additions:** CL-BOOT-007, CL-BOOT-016, CL-HARDWARE-017, CL-USB-010
3. **Status upgrades:** CL-HARDWARE-017 (only after base address reconciliation)
4. **Keep separate:** finding-0001 (retain as a distinct mixed-mode code observation)

---

## Next Steps

- [ ] Review mapping decisions
- [ ] Execute recommended merges
- [ ] Add RE-KB cross-references to claims
- [ ] Upgrade claim statuses where justified
- [ ] Document RE-KB ↔ Claims relationship in strategy
