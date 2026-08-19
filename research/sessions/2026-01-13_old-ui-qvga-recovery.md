# 2026-01-13 Old UI QVGA Recovery

## Summary
- Recovered deleted `ZK-INKJET-UI-QVGA.bin` (307,200 bytes) from FAT volume at offset 0x2A61BE00 (Volume 3).
- Decoded old UI frames (320x240, 2 frames) with XOR 0x4949 + BGR565->RGB565 swap.
- Decoded current UI frames (320x240, 3 frames) for comparison.

## Artifacts
- `research/phase_a_sd_analysis/artifacts/ui_qvga_old_vol3.bin`
- `UI_QVGA_OLD_frame00.png`
- `UI_QVGA_OLD_frame01.png`
- `UI_QVGA_NEW_frame00.png`
- `UI_QVGA_NEW_frame01.png`
- `UI_QVGA_NEW_frame02.png`

## Commands
- `tsk_recover -o 1388767 -e firmware/image/sdcard.work.img research/phase_a_sd_analysis/artifacts/old_ui_recovery_vol3`
- `python3 firmware/decode_ui_qvga.py --input research/phase_a_sd_analysis/artifacts/ui_qvga_old_vol3.bin --width 320 --height 240 --output UI_QVGA_OLD.png`
- `python3 firmware/decode_ui_qvga.py --input firmware/resources/ZK-INKJET-UI-QVGA.bin --width 320 --height 240 --output UI_QVGA_NEW.png`
