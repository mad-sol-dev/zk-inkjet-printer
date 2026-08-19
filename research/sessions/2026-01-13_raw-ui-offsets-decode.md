# 2026-01-13 Raw UI Offsets Decode

## Summary
- Extracted three 320x240 RGB565 frames from raw SD offsets:
  - 0x03800000, 0x03825800, 0x0384b000 (each 0x25800 bytes).
- Decoded each with XOR 0x4949 + BGR565->RGB565 swap.
- Compared against recovered old UI (2 frames) and current FAT UI (3 frames).

## Artifacts
- `research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame0_raw.bin`
- `research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame1_raw.bin`
- `research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame2_raw.bin`
- `research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame0_decoded.png`
- `research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame1_decoded.png`
- `research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame2_decoded.png`
- `research/phase_a_sd_analysis/artifacts/ui_raw_offsets/ui_old_decoded_frame00.png`
- `research/phase_a_sd_analysis/artifacts/ui_raw_offsets/ui_old_decoded_frame01.png`
- `research/phase_a_sd_analysis/artifacts/ui_raw_offsets/ui_new_decoded_frame00.png`
- `research/phase_a_sd_analysis/artifacts/ui_raw_offsets/ui_new_decoded_frame01.png`
- `research/phase_a_sd_analysis/artifacts/ui_raw_offsets/ui_new_decoded_frame02.png`

## Commands
- `dd if=firmware/image/sdcard.work.img of=research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame0_raw.bin bs=1 skip=58720256 count=153600`
- `dd if=firmware/image/sdcard.work.img of=research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame1_raw.bin bs=1 skip=58873856 count=153600`
- `dd if=firmware/image/sdcard.work.img of=research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame2_raw.bin bs=1 skip=59027456 count=153600`
- `python3 tools/scripts/decode_ui_qvga.py --input research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame0_raw.bin --width 320 --height 240 --output research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame0_decoded.png`
- `python3 tools/scripts/decode_ui_qvga.py --input research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame1_raw.bin --width 320 --height 240 --output research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame1_decoded.png`
- `python3 tools/scripts/decode_ui_qvga.py --input research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame2_raw.bin --width 320 --height 240 --output research/phase_a_sd_analysis/artifacts/ui_raw_offsets/frame2_decoded.png`
- `python3 tools/scripts/decode_ui_qvga.py --input research/phase_a_sd_analysis/artifacts/ui_qvga_old_vol3.bin --width 320 --height 240 --output research/phase_a_sd_analysis/artifacts/ui_raw_offsets/ui_old_decoded.png`
- `python3 tools/scripts/decode_ui_qvga.py --input firmware/resources/ZK-INKJET-UI-QVGA.bin --width 320 --height 240 --output research/phase_a_sd_analysis/artifacts/ui_raw_offsets/ui_new_decoded.png`

## Notes
- OCR detected "Thanks for using Goodbye" on raw frames 1 and 2.
- OCR did not detect "Starting System..." in the raw frames; it appears in FAT UI frames.
- Raw frames did not match old/new FAT UI frames by exact pixel comparison.
