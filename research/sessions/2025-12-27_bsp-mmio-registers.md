# Session: BSP MMIO Register Extraction
**Date:** 2025-12-27  
**Session Duration:** ~30 minutes  
**Focus:** Extract MMIO base addresses and register offsets from the N32901-3 NonOS BSP headers

---

## Summary
- Parsed BSP headers under `docs/vendor/N32901-3_NonOS_BSP/` to resolve MMIO addresses in the 0xB0000000-0xBFFFFFFF range.
- Captured base addresses and derived register addresses from `BASE + OFFSET` macros.
- Wrote output to `.re_kb/n32903_registers.json` for USB-CDC and peripheral analysis.

## Commands
- `rg --files -g '*.h' docs/vendor/N32901-3_NonOS_BSP`
- `rg -n "REG_|_BA|0xB8" docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h`
- `python3 scripts/extract_bsp_mmio_registers.py`
