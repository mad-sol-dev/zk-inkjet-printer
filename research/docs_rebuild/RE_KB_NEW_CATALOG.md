# RE-KB Current Catalog (E3-New)

**Source:** research/findings/.re_kb/findings/*.json (2 current findings)
**Extraction Date:** 2026-01-03
**Tier:** E3-New (post-Ghidra-optimization, 1.3k functions)

---

## Summary

- **Total Findings:** 2
- **Subsystems:** 3 (BOOT, SOC, HARDWARE)
- **Evidence Files:** 3 (re_kb_evidence_*.md)
- **Claims Files:** 3 (re_kb_claims_*.md)

## Subsystem Breakdown

| Subsystem | Findings | Evidence Entries | Claims | Status |
|-----------|----------|------------------|--------|--------|
| BOOT | 1 | 1 | 1 | 1V |
| SOC | 1 | 1 | 2 | 2V |
| HARDWARE | 1 | 1 | 1 | 1V |

**Note:** finding-0002 appears in SOC, HARDWARE (same as E3-Old pattern for multi-subsystem findings).

## Key Findings

### BOOT (1 finding)
- **finding-0001:** Firmware uses ARM/Thumb Mixed-Mode Code
  - Region 0x00210000-0x0021FFFF uses Thumb mode (16-bit instructions)
  - Other regions use ARM mode (32-bit instructions)
  - Ghidra correctly detected and disassembled both modes
  - Codex agent verified 18% Thumb / 82% ARM instruction ratio

### SOC (1 finding)
- **finding-0002:** N32903 MMIO Register Map Extracted from BSP
  - 1544 hardware register definitions from N32901-3 NonOS BSP headers
  - Key peripherals: USB_BA=0xB1008000, GPIO_BA=0xB8001000, ADC_BA=0xB800E000, TMR_BA=0xB8002000, SPI0_BA=0xB800C000
  - **Critical:** USB_BA=0xB1008000 (NOT 0xB8007000)
  - **Critical:** PWM_BA=0xB8007000 (E1/E3-Old confused this with USB)

### HARDWARE (1 finding)
- **finding-0002:** USB Device Controller Base from BSP
  - USB_BA/USBD_BA=0xB1008000 confirmed for USB-CDC implementation
  - Refutes E1 CL-USB-010 and E3-Old CL-RKO-USB-002

---

## Integration Notes

**Overlap with E1 Claims:**
- finding-0001: Partial overlap with CL-BOOT-007, CL-BOOT-016 (REKB_MAPPING documented)
- finding-0002: Partial overlap with CL-HARDWARE-017, CL-USB-010 (REKB_MAPPING documented)

**Contradictions:**
- finding-0002 REFUTES CL-USB-010 (E1) and CL-RKO-USB-002 (E3-Old)
- CONTRADICTION-USB-001 documents the USB base address conflict

**Evidence Quality:**
- finding-0001: E1 tier (other/analysis), post-optimization Ghidra
- finding-0002: E0 tier (BSP artifact = ground truth)

**Ghidra Version:**
- Post-optimization (1.3k functions)
- NO [ghidra-v1] tags needed

**Next Steps:**
- Map E3-New claims to E1 claims (Phase 2C-3)
- Update REKB_MAPPING.md with E3-New integration
- Resolve CONTRADICTION-USB-001 with firmware pattern search
