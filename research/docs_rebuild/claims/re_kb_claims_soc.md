# SOC Claims (From E3-New RE-KB Current)

Propositional claims synthesized from current RE-KB findings. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## BSP and Register Map

### ✅ Verified CL-RKN-SOC-001: N32903 MMIO Register Map Extracted from BSP Headers
**Claim:** 1544 hardware register definitions were extracted from N32901-3 NonOS BSP headers, documenting key peripheral base addresses including USB_BA=0xB1008000, GPIO_BA=0xB8001000, ADC_BA=0xB800E000, TMR_BA=0xB8002000, and SPI0_BA=0xB800C000.

**Evidence:**
- E-RKN-SOC-001: Automated extraction via scripts/extract_bsp_mmio_registers.py from BSP headers in docs/vendor/N32901-3_NonOS_BSP/. Output file: research/findings/n32903_registers.json (9616 lines, 1544 register definitions).

**Status:** ✅ Verified

**Cross-Reference:**
- E1: CL-SOC-001 (chip identification)
- E1: CL-HARDWARE-* (GPIO/peripheral bases)
- REKB_MAPPING: finding-0002 maps to CL-HARDWARE-017, CL-USB-010

**Next Tests:** Import n32903_registers.json into Ghidra memory map for register annotation

---

### ✅ Verified CL-RKN-SOC-002: USB Device Controller Base Address is 0xB1008000
**Claim:** BSP headers specify USB_BA/USBD_BA = 0xB1008000 and PWM_BA = 0xB8007000, making 0xB1008000 the correct USB Device Controller base.

**Evidence:**
- E-RKN-SOC-001: BSP extraction shows USB_BA=0xB1008000, USBD_BA=0xB1008000, PWM_BA=0xB8007000

**Status:** ✅ Verified

**Cross-Reference:**
- CONTRADICTION-USB-001: Refutes E1 CL-USB-010 (0xB8007000)
- REKB_MAPPING: Critical conflict identified

**Next Tests:** Pattern search in firmware for 0xB1008000 usage to confirm UDC is actually used

