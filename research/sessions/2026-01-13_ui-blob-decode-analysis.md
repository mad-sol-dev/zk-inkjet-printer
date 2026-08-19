# 2026-01-13 UI Blob Decode Analysis

**Date:** 2026-01-13  
**Time:** not recorded  
**Project:** ZK inkjet printer RE  
**Working Directory:** `$HOME/workspace/zk-inkjet-printer`

## Goal
Reverse engineer the UI splash screen blob decoding algorithm and validate old/new UI frame layouts.

## Summary
- Located the actual XOR mask (`0x4949`) and BGR565→RGB565 swap implementation in `APP.bin`.
- Confirmed previous speculation (`0xAAAA` XOR) was incorrect; the firmware applies per-pixel XOR `0x4949`.
- **CORRECTED 2026-01-14:** Decoded FAT UI blobs and discovered:
  - **Large file (460,800 bytes, 3 frames):** "Starting System..." (2×) + "Thanks..." - **NO Leon logo**
  - **Small file (307,200 bytes, 2 frames):** **Leon logo** + "Thanks..." - This is ACTIVE on device
  - Active UI stored in RAW @ 0x03800000 (pre-decoded, no XOR), loaded at boot
  - FAT UI blobs are XOR-masked UPDATE PAYLOADS only
- Logged structured result in RE-KB (`finding-0007`).
- Cleaned workspace (moved PNGs into artifacts, removed temp directories).

## Technical Details

### Firmware Decode Path (APP.bin)
- **Function:** `update_flash_file_to_raw` @ `0x0026ccf8`
  - XOR loop at `0x0026d11c`–`0x0026d128` applies mask `0x4949` per 16-bit pixel.
  - This matches observed decoded images; earlier `0xAAAA` speculation is incorrect.

### Color Conversion
- **Function:** `FUN_002bf4dc` @ `0x002bf4dc`
  - Performs BGR565→RGB565 swap using masks: `0xf800`, `0x7e0`, `0x1f`.
  - Output: `(blue << 11) | (green << 5) | red`.
  - Confirms display expects RGB565 ordering after swap.

### UI Blob Format
- Resolution: **320×240**, **RGB565**, multi-frame.
- **FAT Volume 2 (deleted):**
  - Large file: **460,800 bytes** (3 frames) - "Starting System..." screens, NO logo
  - Small file: **307,200 bytes** (2 frames) - Leon logo + shutdown screen
- **RAW Storage @ 0x03800000 (ACTIVE):**
  - Frame 0 @ 0x03800000: **Leon logo** (matches small FAT file frame 0)
  - Frame 1 @ 0x03825800: Unknown content
  - Frame 2 @ 0x0384B000: **"Thanks for using Goodbye"** (matches small FAT file frame 1)
  - Stored **pre-decoded** (no XOR, only BGR565 format, swap needed at boot)

### Update Flow
1. XOR-masked UI file placed on Volume 3: `3:/ZK-INKJET-UI-QVGA.bin`
2. `update_flash_file_to_raw` @ 0x0026ccf8 decodes (XOR 0x4949 + BGR→RGB swap)
3. Pre-decoded frames written to RAW @ 0x03800000
4. Boot code loads from RAW, applies only BGR→RGB swap (no XOR)
5. FAT file deleted after successful update

### Display Controller
- SPI-connected LCD controller identified as **ILI9341** or **ST7789V** (pending init-sequence confirmation).

## Artifacts
- Decode script: `tools/scripts/decode_ui_qvga.py`
- PNG outputs: `research/phase_a_sd_analysis/artifacts/ui_decoded/`
- RE-KB finding: `research/findings/.re_kb/findings/finding-0007.json`

## Cross-References
- RE-KB: `finding-0007` — "UI Blob Decode Algorithm (XOR 0x4949 + BGR565 Color Swap)"
- RE-KB: `finding-0008` — "IBR Headers & Firmware Update Lookup Tables"
- SD Memory Map: `research/phase_a_sd_analysis/sd_memory_map_verified.md`
- Prior speculation: `research/report_analyse_2_8_tft_lcd_18_pin_ffc_vermuteter_controller.md`
- Note: The actual implementation was found in live code where manual review had previously only found dead code.

## Cleanup Notes
- Moved decoded PNGs into `research/phase_a_sd_analysis/artifacts/ui_decoded/`.
- Removed temporary decode directories from the workspace.

## Next Steps
- ~~Create clean SD image (strip garbage data).~~ NOT NEEDED - UI stored in RAW, not FAT
- Document display initialization sequence (match controller).
- Continue SPI LCD controller analysis and register mapping.
- Identify Frame 1 content @ 0x03825800
