# Session Log: Update Chain + SD Raw Mapping

**Date:** 2026-01-08  
**Project:** ZK inkjet printer RE  
**Scope:** SD raw layout validation, APP integrity fix, update-chain reverse engineering

## Goals
- Resolve APP.bin mismatch vs raw SD image.
- Confirm raw SD offsets for BOOT/APP and staging copies.
- Identify update chain (file → raw SD write) and label functions.
- Characterize the unknown blob at `0x00100000`.
- Record UI blob raw location and verify hash.

## Key Discoveries
- **APP raw SD mapping confirmed:** APP at `0x03000000` matches `ZK-INKJET-NANO-APP.bin.orig` (SHA256 `3be9028b…`).
- **Update chain found in APP:** `update_entry_boot_app` → `update_flash_file_to_raw` → `sd_raw_write_aligned` → `sd_fmi_block_io`.
- **Raw SD writes use LBA:** `sd_raw_write_aligned` shifts addr >> 9 and calls SD/FMI block I/O.
- **UI blob location:** `ZK-INKJET-UI-QVGA.bin` found at raw SD `0x242a2000` (volume 2); hash matches extracted UI file.
- **Unknown stub at `0x00100000`:** Carved size `0x002DD000` (3,002,368 bytes). Mixed content (vector table + strings + PNG/BMP/tar/LZMA/ELF signatures). Likely not clean firmware; possibly residual data.

## Technical Details

### Integrity Fixes
The file `firmware/bin/ZK-INKJET-NANO-APP.bin` was not identical to the raw SD APP.
It was replaced with the clean `.orig` image to avoid checksum drift.

Correct hash now in `firmware/README.md`:
```
3be9028b01c0007aab9192877341918a0bc155beef55ac17e7e8f3bcc95151ea  ZK-INKJET-NANO-APP.bin
```

### Raw SD Offsets (confirmed)
- BOOT code: `0x00000220` (matches `ZK-INKJET-NANO-BOOT.bin`)
- APP: `0x03000000` (matches `ZK-INKJET-NANO-APP.bin.orig`)
- Volume 2 staging copies:
  - BOOT: `0x24028000`
  - APP: `0x2402C000`

### Update Chain (APP.bin)
Renamed and commented:
- `update_entry_boot_app` (`0x0026887c`)
  - Loads `3:/ZK-INKJET-NANO-BOOT.bin`
  - Then loads `3:/ZK-INKJET-NANO-APP.bin` with base `0x03000000`
- `update_flash_file_to_raw` (`0x0026ccf8`)
  - Treats param_2 as raw SD base offset
  - Writes in 0x200-byte blocks via `sd_raw_write_aligned`
- `sd_raw_write_aligned` (`0x00232500`)
  - Requires 0x200 alignment
  - Calls `sd_fmi_block_io(LBA,count,buf)`
- `sd_fmi_block_io` (`0x00294584`)
  - Programs FMI/SD/DMAC MMIO regs (e.g., `0xB1006408`, `0xB100682C`, `0xB1006838`)

### Unknown Stub at `0x00100000`
Carved file: `research/phase_a_sd_analysis/artifacts/unknown_0x00100000_stub.bin`
- Size: `0x002DD000` (3,002,368 bytes)
- Entropy: mixed (avg ~5.8, max ~7.7)
- Strings: UI/printf formats, font engines, USB alloc errors, barcode library messages
- Magic signatures:
  - PNG @ `0x0E3621`
  - BMP @ `0x0ABA18`
  - tar @ `0x253806`
  - LZMA @ `0x276E62`
  - ELF @ `0x2D8F24`
Likely not a clean firmware image; could be residual data from prior SD use.

### UI Blob in Raw SD
Carved file: `research/phase_a_sd_analysis/artifacts/ui_qvga_vol2_0x242a2000.bin`
- Size: 460,800 bytes
- Hash matches `ZK-INKJET-UI-QVGA.bin`

## RE-KB References
- `finding-0006`: update chain writes raw SD at `0x03000000` via SD/FMI block I/O.

## Open Questions / Next Steps
- Confirm whether `0x00100000` is valid firmware or leftover data by comparing to a fresh TurboWriter image.
- If needed, import full FMI/DMAC register labels into Ghidra (tooling may require a script; MMIO indirection blocks auto-annotation).

