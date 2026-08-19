# SD Card Memory Map - Verified

**Date:** 2026-01-14  
**Status:** Verified via Codex binary analysis + Session logs  
**SD Image:** firmware/image/sdcard.work.img (3.8 GB)

---

## Executive Summary

The SD card uses **fixed RAW offsets without a partition table**. The boot sector (0x000-0x200) is completely empty. FAT volumes are located at hardcoded offsets and require direct offset mounting (mtools). Six IBR headers exist: one active bootloader, four RAW-stored firmware lookup tables, and one embedded in APP.bin firmware.

---

## Memory Map

```
┌─────────────────────────────────────────────────────────────────┐
│ BOOT SECTOR (0x00000000 - 0x000001FF)                           │
├─────────────────────────────────────────────────────────────────┤
│ 0x00000000  Empty (512 bytes of zeros)                          │ ✅ VERIFIED
│             No MBR, no partition table, no 0x55AA signature     │
│             SD card NOT normally mountable                       │
├─────────────────────────────────────────────────────────────────┤
│ RAW BOOT AREA (0x00000200 - 0x03FFFFFF)                         │
├─────────────────────────────────────────────────────────────────┤
│ 0x00000200  IBR Header #1 (32 bytes)                            │ ✅ VERIFIED
│ 0x00000220  └─ BOOT.bin ARM code (12,736 bytes)                 │ ✅ VERIFIED
│ 0x00003420  └─ BOOT.bin ends                                    │ ⚠️ CALCULATED
│                                                                  │
│ 0x00100000  Unknown stub (3,002,368 bytes)                      │ ✅ VERIFIED
│ 0x003DD000  └─ Residual data from previous partitioning (junk)  │ ⚠️ CALCULATED
│                                                                  │
│ 0x00179DCC  IBR Header #2 (32 bytes) + Firmware Set A list      │ ✅ VERIFIED
│             Filenames: BOOT, CUTE-BOOT, TIJSPS-800x480-BOOT     │
│                                                                  │
│ 0x03000000  APP.bin (2,576,940 bytes = 0x27511C)                │ ✅ VERIFIED
│ 0x0327511C  └─ APP.bin ends                                     │ ⚠️ CALCULATED
│                                                                  │
│ 0x03800000  UI Frame Storage (RAW, pre-decoded)                 │ ✅ VERIFIED
│ 0x03800000  ┌─ Frame 0 (153,600 bytes = 0x25800)                │ ✅ VERIFIED
│             │  Leon Logo (pixel-exact match)                    │
│ 0x03825800  ├─ Frame 1 (153,600 bytes = 0x25800)                │ ✅ VERIFIED
│             │  Content: TBD                                     │
│ 0x0384B000  └─ Frame 2 (153,600 bytes = 0x25800)                │ ✅ VERIFIED
│             │  "Thanks for using Goodbye"                       │
│ 0x03870800  └─ UI frames end                                    │ ⚠️ CALCULATED
├─────────────────────────────────────────────────────────────────┤
│ RAW AREA - IBR HEADERS (Firmware Update Lookup Tables)          │
├─────────────────────────────────────────────────────────────────┤
│ 0x0247AA68  IBR Header #3 + Firmware Set A list (duplicate)     │ ✅ VERIFIED
│ 0x0306CFA8  IBR Header #4 + Firmware Set B list                 │ ✅ VERIFIED
│             Filenames: TINY, PUNY, NANO-BOOT, UI.bin            │
│ 0x03C7BD70  IBR Header #5 + Firmware Set A list (duplicate)     │ ✅ VERIFIED
├─────────────────────────────────────────────────────────────────┤
│ FAT VOLUME 1 (0x04000000 - 0x23FFFFFF) - 512 MB                 │
├─────────────────────────────────────────────────────────────────┤
│ 0x04000000  Fonts/Resources (28 TrueType fonts, 168 MB used)    │ ✅ VERIFIED
│             CJK: MSYH, SimSun, SourceHan, etc.                  │
│             Western: Arial, Times, Calibri, etc.                │
│ 0x23FFFFFF  └─ Volume 1 ends                                    │ ⚠️ CALCULATED
├─────────────────────────────────────────────────────────────────┤
│ FAT VOLUME 2 (0x24007E00 - 0x2A61BDFF) - 256 MB                 │
├─────────────────────────────────────────────────────────────────┤
│ 0x24007E00  Volume 2 Start (System/Staging)                     │ ✅ VERIFIED
│ 0x24028000  BOOT.bin (DELETED, 12,736 bytes, 9-Dec-2022)        │ ✅ VERIFIED
│ 0x2402C000  APP.bin (DELETED, 2,576,940 bytes, 9-Dec-2022)      │ ✅ VERIFIED
│ 0x24098FA8  └─ IBR Header #6 @ APP.bin+0x6CFA8 (embedded)       │ ✅ VERIFIED
│             └─ Firmware Set B list (same as header #4)          │
│ 0x242A2000  UI-QVGA.bin (DELETED, 460,800 bytes, 5-Dec-2022)    │ ✅ VERIFIED
│                                                                  │
│ 0x28000000  SETTINGS BLOCK (400 bytes = 0x190)                  │ ✅ VERIFIED
│             RAW write within Volume 2 (NOT FAT file)            │
│             Contains: Language, UI config, general settings     │
│             Functions: settings_load_validate_save (0x262778)   │
│                       settings_save_block (0x2661e0)            │
│                                                                  │
│ 0x28800000  CALIBRATION DATA (100 slots × 16 bytes)             │ ✅ VERIFIED
│ 0x28B2B000  └─ Range: 0x28800000 + i×0x4D000 per slot           │
│             Contains: Touch calibration points, alignment data  │
│             Function: settings_save_calibration_slots (0x265ea8)│
│                                                                  │
│ 0x2A61BDFF  └─ Volume 2 ends                                    │ ⚠️ CALCULATED
├─────────────────────────────────────────────────────────────────┤
│ FAT VOLUME 3 (0x2A61BE00 - 0x2E61BDFF) - 64 MB "MINI"           │
├─────────────────────────────────────────────────────────────────┤
│ 0x2A61BE00  User USB Drive (EMPTY, 88 bytes metadata only)      │ ✅ VERIFIED
│             Volume label: "MINI"                                │
│             Update INPUT area (users place firmware here)        │
│ 0x2E61BDFF  └─ Volume 3 ends                                    │ ⚠️ CALCULATED
├─────────────────────────────────────────────────────────────────┤
│ POST-VOLUME RAW AREA (0x2E61BE00 - EOF)                         │
├─────────────────────────────────────────────────────────────────┤
│ 0x2E61BE00  Unmapped region (likely empty/unused)               │ ❓ UNKNOWN
└─────────────────────────────────────────────────────────────────┘
```

---

## Confidence Levels

- ✅ **VERIFIED:** Direct evidence from session logs or binary analysis
- ⚠️ **CALCULATED:** Derived from verified start offset + size
- ❓ **UNKNOWN:** Not yet investigated

---

## IBR Headers Summary

| # | Offset | Location | Content After Header | Firmware Set |
|---|--------|----------|---------------------|--------------|
| 1 | 0x00000200 | RAW | ARM bootloader code | N/A (active boot) |
| 2 | 0x00179DCC | RAW | Filename lookup table | Set A |
| 3 | 0x0247AA68 | RAW | Filename lookup table | Set A (dup) |
| 4 | 0x0306CFA8 | RAW | Filename lookup table | Set B |
| 5 | 0x03C7BD70 | RAW | Filename lookup table | Set A (dup) |
| 6 | 0x24098FA8 | APP.bin+0x6CFA8 | Filename lookup table | Set B (dup) |

**Firmware Set A:** BOOT, CUTE-BOOT, TIJSPS-800x480-BOOT  
**Firmware Set B:** TINY-BOOT, PUNY-BOOT, NANO-BOOT, UI.bin

All IBR headers are identical:
- Signature: `0xA5 [ZBW] 0x31 [WBZ] 0xA5`
- Field A: `0x00001010`
- Field B: `0x00888800`

---

## Key Findings

### ✅ Verified Facts

1. **No partition table:** Boot sector (0x000-0x200) is completely empty
2. **FAT volumes at fixed offsets:** Not discoverable via partition table
3. **Six IBR headers exist:** One active boot, five lookup tables (four RAW, one embedded)
4. **UI frames stored pre-decoded:** RAW offsets contain BGR565 data (no XOR mask)
5. **Volume 3 "MINI" is empty:** User update input area, cleaned after updates
6. **Deleted firmware in Volume 2:** Previous update artifacts (BOOT/APP/UI)
7. **Settings stored in Volume 2 (RAW):** Device settings written directly to Volume 2 region via RAW SD writes, not as FAT files
   - Settings block: 0x28000000 (400 bytes) - language, UI config
   - Calibration data: 0x28800000 + i×0x4D000 (100 slots × 16 bytes) - touch cal points

### ⚠️ Hypothesis

1. **Update mechanism:**
   - User places files on Volume 3 (`3:/`)
   - Firmware scans IBR header lookup tables
   - Files decoded/processed → written to RAW offsets
   - Files deleted from Volume 3 after successful update
   - Optional backup copy in Volume 2 (later deleted)

2. **Firmware variants:**
   - Set A: BOOT, CUTE, TIJSPS (different hardware variants)
   - Set B: TINY, PUNY, NANO (our device variant)
   - Multiple lookup tables = redundancy/recovery mechanism

---

## UI Frame Storage Details

UI splash screens stored in **RAW area @ 0x03800000**, NOT in FAT volumes.

**Storage format:**
- Pre-decoded (no XOR 0x4949 mask)
- BGR565 little-endian
- Requires BGR→RGB swap at boot

**Frame layout:**
- Frame 0 @ 0x03800000: Leon logo (pixel-exact match with recovered FAT blob)
- Frame 1 @ 0x03825800: Unknown content
- Frame 2 @ 0x0384B000: "Thanks for using Goodbye" screen

**Update flow:**
1. XOR-masked UI file placed on Volume 3: `3:/ZK-INKJET-UI-QVGA.bin`
2. `update_flash_file_to_raw` @ 0x0026ccf8 decodes (XOR + swap)
3. Pre-decoded frames written to RAW @ 0x03800000
4. Boot code loads from RAW, applies only BGR→RGB swap

---

## References

- Finding-0007: UI Blob Decode Algorithm
- Finding-0008: IBR Headers & Firmware Update Lookup Tables
- Finding-0009: Settings Persistence Layer
- Session: 2026-01-14_sd-memory-map-ibr-headers-cleanup.md
- Session: 2026-01-08_update-chain-sd-raw-mapping.md
- Session: 2026-01-08_usb-session-sd-image-integrity.md
- Phase A: volume_identification_corrected.md
- Phase A: boot_locations_verified.md
- Codex binary analysis: 2026-01-14

---

**Document Status:** Complete - All major regions mapped and verified (including settings storage)  
**Last Updated:** 2026-01-14 (Settings layer added)
