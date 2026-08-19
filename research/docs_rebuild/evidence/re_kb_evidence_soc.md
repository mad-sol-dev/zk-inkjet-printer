# SOC Evidence (E3-New RE-KB Current)

**Source:** research/findings/.re_kb/findings/*.json (2 current findings)
**Tier:** E3-New (structured findings from post-optimization analysis)
**Note:** Post-Ghidra-optimization (1.3k functions). No [ghidra-v1] tag.

---

## BSP and Register Map

### E-RKN-SOC-001: N32903 MMIO Register Map Extracted from BSP
- **RE-KB ID:** finding-0002
- **Status:** in_progress
- **Type:** behavior
- **Summary:** Extracted 1544 hardware register definitions from N32901-3 NonOS BSP headers. Key peripherals: USB_BA=0xB1008000, GPIO_BA=0xB8001000, ADC_BA=0xB800E000, TMR_BA=0xB8002000, SPI0_BA=0xB800C000. Register map stored in research/findings/n32903_registers.json for Ghidra import.
- **Evidence:**
  - E1: Automated extraction via scripts/extract_bsp_mmio_registers.py from BSP headers in docs/vendor/N32901-3_NonOS_BSP/. Output file: research/findings/n32903_registers.json (9616 lines, 1544 register definitions).; source_type=other
- **Tags:** hardware, mmio, bsp, foundation, usb
- **Confidence:** 1.0
- **Component:** hardware
- **Created:** 2025-12-27T22:30:15.032287Z
- **Updated:** 2025-12-27T22:30:15.032287Z

