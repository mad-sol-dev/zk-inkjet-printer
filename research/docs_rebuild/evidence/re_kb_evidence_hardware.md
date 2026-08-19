# HARDWARE Evidence (E3-New RE-KB Current)

**Source:** research/findings/.re_kb/findings/*.json (2 current findings)
**Tier:** E3-New (structured findings from post-optimization analysis)
**Note:** Post-Ghidra-optimization (1.3k functions). No [ghidra-v1] tag.

---

## USB Device Controller Base

### E-RKN-HARDWARE-001: USB_BA Register Definition from BSP
- **RE-KB ID:** finding-0002
- **Status:** in_progress
- **Type:** behavior
- **Summary:** USB_BA=0xB1008000 and USBD_BA=0xB1008000 from BSP extraction; PWM_BA=0xB8007000 is distinct.
- **Evidence:**
  - E1: Automated extraction via scripts/extract_bsp_mmio_registers.py from BSP headers in docs/vendor/N32901-3_NonOS_BSP/. Output file: research/findings/n32903_registers.json (9616 lines, 1544 register definitions).; source_type=other
- **Tags:** bsp, foundation, hardware, mmio, udc-base, usb
- **Confidence:** 1.0
- **Component:** hardware
- **Created:** 2025-12-27T22:30:15.032287Z
- **Updated:** 2025-12-27T22:30:15.032287Z
- **Note:** Relevant for CL-HARDWARE-017 (USB Device pins availability)

