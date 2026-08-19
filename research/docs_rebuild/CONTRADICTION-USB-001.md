# CONTRADICTION-USB-001: USB Device Controller Base Address

**Status:** ACTIVE
**Severity:** CRITICAL (blocks USB-CDC implementation)
**Discovered:** 2026-01-03 (Phase 2C RE-KB Integration)

---

## The Contradiction

**Claim (CL-USB-010):**
- USB Device Controller (UDC) base address = 0xB8007000
- Evidence: E-USB-019 "10 refs in APP.bin"
- Source: Chat 51 (2025-12-06)

**BSP Headers (finding-0002):**
- USB_BA/USBD_BA = 0xB1008000 (USB Device Controller)
- PWM_BA = 0xB8007000 (PWM Controller)
- Source: research/findings/n32903_registers.json (BSP extraction)

---

## Investigation Results

### Firmware References to 0xB8007000
- **Count:** 0 refs found (Ghidra MCP scalar search)
- **Functions:** None
- **Access Pattern:** None observed
- **Analysis:** No 0xB8007000 scalar references found in `ZK-INKJET-NANO-APP.bin.orig` via Ghidra MCP

### Firmware References to 0xB1008000
- **Count:** 0 refs found (Ghidra MCP scalar search)
- **Functions:** None
- **Access Pattern:** None observed
- **Analysis:** No 0xB1008000 scalar references found in `ZK-INKJET-NANO-APP.bin.orig` via Ghidra MCP

### Register Offset Comparison
- BSP-derived base addresses indicate 0xB8007000 = PWM_BA, 0xB1008000 = USB_BA/USBD_BA.
- No firmware scalar refs were found to compare offset usage against PWM or USB register layouts.

---

## Resolution

**Root Cause:**
The original claim (E-USB-019) was derived from Chat 51 session notes and is not reproducible via the current Ghidra MCP scalar search against `ZK-INKJET-NANO-APP.bin.orig`.

**Correct Base Address:**
- USB Device Controller: 0xB1008000 (per BSP)
- PWM Controller: 0xB8007000 (per BSP)

**Firmware Usage:**
- USB Device Controller usage in APP.bin is **UNCONFIRMED** (no scalar refs found).
- PWM Controller usage in APP.bin is **UNCONFIRMED** (no scalar refs found).

**Impact on USB-CDC:**
USB-CDC implementation remains blocked until firmware references to the actual UDC base are confirmed or the initialization path is located via non-scalar patterns (e.g., MOV/MOVT or computed addresses).

---

## Recommended Actions

- [ ] Re-run scalar searches after confirming the correct APP.bin program is loaded (non-.orig if available)
- [ ] Search for UDC base construction via MOV/MOVT or constant-pool patterns (non-literal scalar refs)
- [ ] Update CL-USB-010 with corrected base address if firmware refs validate 0xB1008000
- [ ] Add evidence entry documenting the Ghidra search results (0 refs found for both bases)
- [ ] Mark E-USB-019 as corrected if the 0xB8007000 attribution is disproven
- [ ] Update research/REKB_MAPPING.md with resolution status

---

## Next Steps

1. Confirm active program identity and load `ZK-INKJET-NANO-APP.bin` if distinct from `.orig`.
2. Use Ghidra to search for UDC register offsets (EPA_CFG, EPB_CFG, EP*_MPS) to identify base via offset usage.
3. Check for references to USBH_BA (0xB1009000) to locate the USB controller block and adjacent device base.
