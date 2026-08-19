# HARDWARE Claims (From E3-New RE-KB Current)

Propositional claims synthesized from current RE-KB findings. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## USB Device Controller

### ✅ Verified CL-RKN-HARDWARE-001: USB Device Controller Registers at 0xB1008000
**Claim:** N32903 USB Device Controller (USBD) registers are memory-mapped at base address 0xB1008000 per BSP headers.

**Evidence:**
- E-RKN-HARDWARE-001: BSP extraction confirms USB_BA/USBD_BA=0xB1008000

**Status:** ✅ Verified

**Cross-Reference:**
- E1: CL-HARDWARE-017 (USB Device pins availability for CDC)
- CONTRADICTION-USB-001: Corrects E1 CL-USB-010 base address
- E3-New: CL-RKN-SOC-002 (same finding, SOC perspective)

**Next Tests:** Verify firmware usage at 0xB1008000, check if UDC is initialized

