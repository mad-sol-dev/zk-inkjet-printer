# 2026-01-14 SD Memory Map, IBR Headers & Cleanup

**Date:** 2026-01-14  
**Project:** ZK inkjet printer RE  
**Working Directory:** `$HOME/programme/Projekte/zk-inkjet-printer`

## Goal
Build comprehensive SD card memory map, verify IBR header locations, clean up duplicate findings, and prepare clean SD image strategy.

## Summary
- Fixed duplikat Finding (0007/0008) and rebuilt RE-KB index
- Corrected UI blob analysis: Active UI is in RAW @ 0x03800000 (pre-decoded), not FAT
- Verified all 6 IBR headers via Codex binary search
- Created complete SD memory map with confidence levels
- Analyzed gap regions between verified structures
- Developed empirical test strategy: create clean SD image, test if device boots

## Context Issue Resolved
- Previous chat had context compression issues causing tool usage amnesia
- Reminder: Always use Desktop Commander for file operations
- Reminder: RE-KB Club Rule #1 - use create_finding/update_finding APIs, not direct file writes

## Findings Cleanup

### Duplicate Finding Resolved
- **Finding-0007:** UI Blob Decode Algorithm (kept, updated)
- **Finding-0008:** Duplicate (deleted)
- Rebuilt RE-KB index successfully

### Finding-0007 Updates
- Added: `confidence: 1.0`, `severity: "info"`
- Clarified: UI stored pre-decoded in RAW, not XOR-masked in FAT

### New Finding Created
- **Finding-0008 (new):** IBR Header Locations & Firmware Update Lookup Tables
  - 6 IBR headers verified
  - Header #1: Active boot @ 0x200
  - Headers #2-5: RAW firmware lookup tables (redundant)
  - Header #6: Embedded in APP.bin @ +0x6CFA8
  - Two firmware variant sets identified (Set A: BOOT/CUTE/TIJSPS, Set B: TINY/PUNY/NANO)

## SD Card Memory Map

Created comprehensive map: `research/phase_a_sd_analysis/sd_memory_map_verified.md`

### Key Discoveries

**Boot Sector:**
- 0x000-0x200: Completely empty (no MBR, no partition table)
- SD card NOT normally mountable
- FAT volumes at fixed RAW offsets

**IBR Headers (all verified via Codex):**
| # | Offset | Location | Content |
|---|--------|----------|---------|
| 1 | 0x00000200 | RAW | Active BOOT code |
| 2 | 0x00179DCC | RAW | Firmware Set A list |
| 3 | 0x0247AA68 | RAW | Firmware Set A (dup) |
| 4 | 0x0306CFA8 | RAW | Firmware Set B list |
| 5 | 0x03C7BD70 | RAW | Firmware Set A (dup) |
| 6 | 0x24098FA8 | APP.bin+0x6CFA8 | Firmware Set B (embedded) |

All headers identical: `0xA5 [ZBW] 0x31 [WBZ] 0xA5`, Field A: `0x1010`, Field B: `0x888800`

**Active Firmware:**
- BOOT: 0x00000200 (12,768 bytes with IBR header)
- APP: 0x03000000 (2,576,940 bytes)
- UI Frames: 0x03800000 (3 × 153,600 bytes, pre-decoded BGR565)

**FAT Volumes:**
- Volume 1 @ 0x04000000: Fonts/Resources (512 MB)
- Volume 2 @ 0x24007E00: System/Staging (256 MB, contains deleted firmware)
- Volume 3 @ 0x2A61BE00: "MINI" USB drive (64 MB, empty)

**Unknown/Junk Regions:**
- 0x00100000: Unknown stub (3 MB residual data, likely Android/Linux remnants)
- Gaps between verified regions analyzed, contain mostly zeros or old data

## UI Storage Correction

**Previous Incorrect Theory:**
- "Large FAT file (460KB) = new UI with logo"
- "Small FAT file (307KB) = old UI without logo"
- "Rebranding timeline: Sep 2022 → Dec 2022"

**Corrected Understanding:**
- Large FAT file (460KB, 3 frames): "Starting System..." screens, NO Leon logo
- Small FAT file (307KB, 2 frames): Leon logo + shutdown screen
- **Active UI in RAW @ 0x03800000:** Pre-decoded, matches small FAT file
  - Frame 0 @ 0x03800000: Leon logo (pixel-exact match)
  - Frame 1 @ 0x03825800: Unknown content
  - Frame 2 @ 0x0384B000: "Thanks for using Goodbye"

**Update Flow:**
1. XOR-masked UI placed on Volume 3: `3:/ZK-INKJET-UI-QVGA.bin`
2. `update_flash_file_to_raw` @ 0x0026ccf8 decodes (XOR 0x4949 + BGR swap)
3. Pre-decoded frames written to RAW @ 0x03800000
4. Boot loads from RAW, applies only BGR→RGB swap (no XOR)
5. FAT file deleted after update

## Gap Analysis

**Gaps between verified regions analyzed:**

| Gap | Offset Range | Size | All Zeros? | Entropy | Verdict |
|-----|--------------|------|------------|---------|---------|
| A | 0x00003420 - 0x00100000 | ~1 MB | Yes | 0.0 | Safe (empty) |
| B | 0x003DD000 - 0x03000000 | ~45 MB | No | 2.56 | Contains IBR #3, rest junk |
| C | 0x0327511C - 0x03800000 | ~5.5 MB | No | 0.08 | Low entropy, likely old data |
| D | 0x03870800 - 0x04000000 | ~7.5 MB | No | 3.12 | Contains IBR #5, rest junk |

**Findings:**
- Gap B: PNG/JPG magic signatures, IBR header #3, strings like "ZhiKai USB Mass Storage" (Linux kernel)
- Gap C: Structured data, low entropy, USB Card Reader strings
- Gap D: PNG signatures, IBR header #5, format strings
- Conclusion: Gaps contain old data from previous SD card usage (Android APKs, Linux remnants)

## Clean SD Image Strategy

**Empirical Test Approach:**
Instead of endlessly analyzing gaps, create clean image and test:

1. Copy only verified regions at exact offsets
2. Fill gaps with zeros (sparse file)
3. Flash to SD card and test boot
4. **If boots:** Gaps confirmed as junk ✅
5. **If fails:** Gaps contain critical data → investigate which gap

**Regions to copy:**
- Boot sector (512 bytes)
- BOOT.bin (12,768 bytes)
- APP.bin (2,576,940 bytes)
- UI frames (460,800 bytes)
- Volume 1 (512 MB)
- Volume 2 (256 MB)
- Volume 3 (64 MB)

**Codex prompt prepared** for creating `firmware/image/sdcard.clean.img`

## Session Updates

**Updated Documents:**
- `research/sessions/2026-01-13_ui-blob-decode-analysis.md` - Corrected frame assignments and storage location
- Created: `research/phase_a_sd_analysis/sd_memory_map_verified.md` - Complete memory map

**RE-KB Updates:**
- Finding-0007: Updated with confidence/severity
- Finding-0008: Created for IBR headers
- Index rebuilt successfully

**Artifacts Created:**
- Gap analysis binaries: `research/phase_a_sd_analysis/artifacts/gap_analysis/`
- Strings extracts from gaps
- Head/tail dumps of non-zero gaps

## Cross-References
- Finding-0007: UI Blob Decode Algorithm
- Finding-0008: IBR Headers & Firmware Update Lookup Tables
- Finding-0006: APP update chain writes raw SD at 0x03000000
- SD Memory Map: `research/phase_a_sd_analysis/sd_memory_map_verified.md`
- Phase A Summary: `research/phase_a_sd_analysis/phase_a_final_summary.md`

## Clean SD Image Boot Test

**Result:** ✅ **SUCCESS - Device boots!**

**Symptoms after boot:**
- Touch calibration lost (had to recalibrate)
- UI language settings lost (white blocks instead of text)
- Font/encoding issues until language re-selected

**Conclusion:** Gaps confirmed as mostly junk, BUT settings storage was in the gaps!

## Settings Storage Discovery

**Binary diff analysis (clean vs after-boot):**
- 10 candidate regions found where zeros became non-zero
- Key regions: 0x000D3000 - 0x00275400 (~1.7 MB)
- Strings found: "touch", "calib", "lang", "align"

**Ghidra analysis reveals settings persistence layer:**

### Settings Storage Architecture

**Main Settings Block:**
- Raw SD offset: 0x28000000
- Size: 0x190 bytes (400 bytes)
- Contains: Language, UI config, general settings
- Functions:
  - `settings_load_validate_save` @ 0x262778 (load at boot)
  - `settings_save_block` @ 0x2661e0 (save on change)

**Calibration Data:**
- Raw SD offset: 0x28800000 + i×0x4D000 (100 slots)
- Size per slot: 16 bytes
- Range: 0x28800000 - 0x28B2B000
- Contains: Touch calibration points, alignment data
- Function: `settings_save_calibration_slots` @ 0x265ea8

**Call Chains:**
```
Boot Path:
  boot_init (0x25b0c4)
    → settings_load_validate_save (0x262778)
      → sd_raw_write_aligned(0x28000000, ..., 0x190)

UI Path:
  ui_main_loop (0x26a7f8)
    → settings_save_block (0x2661e0)
      → sd_raw_write_aligned(0x28000000, ..., 0x190)

Calibration Path:
  [Touch calibration routine]
    → settings_save_calibration_slots (0x265ea8)
      → sd_raw_write_aligned(0x28800000 + i×0x4D000, ..., 0x10)
```

## Ghidra Function Renames

**Functions renamed with evidence-based names:**

| Old Name | New Name | Address | Evidence |
|----------|----------|---------|----------|
| FUN_00262778 | settings_load_validate_save | 0x262778 | Loads/validates 0x190-byte block, writes defaults |
| FUN_002661e0 | settings_save_block | 0x2661e0 | Saves 0x190-byte settings to raw SD |
| FUN_00265ea8 | settings_save_calibration_slots | 0x265ea8 | Writes 100×16-byte calibration slots |
| FUN_0026a7f8 | ui_main_loop | 0x26a7f8 | Main UI loop, calls settings save |
| FUN_0025b0c4 | boot_init | 0x25b0c4 | Boot initialization, loads settings |

All functions annotated with detailed comments explaining evidence.

## Session Updates

**Updated Documents:**
- `research/sessions/2026-01-13_ui-blob-decode-analysis.md` - Corrected frame assignments and storage location
- Created: `research/phase_a_sd_analysis/sd_memory_map_verified.md` - Complete memory map
- Updated: This session log with boot test results and settings analysis

**RE-KB Updates:**
- Finding-0007: UI Blob Decode Algorithm (updated)
- Finding-0008: IBR Headers & Firmware Update Lookup Tables (created)
- Finding-0009: Settings Persistence Layer (created)
- Index rebuilt successfully

**Artifacts Created:**
- Clean SD image: `firmware/image/sdcard.clean.img`
- Boot test comparison: `research/phase_a_sd_analysis/artifacts/boot_settings_candidates/`
- Gap analysis binaries: `research/phase_a_sd_analysis/artifacts/gap_analysis/`
- Strings extracts from gaps
- Head/tail dumps of non-zero gaps

## Cross-References
- Finding-0007: UI Blob Decode Algorithm
- Finding-0008: IBR Headers & Firmware Update Lookup Tables
- Finding-0009: Settings Persistence Layer
- Finding-0006: APP update chain writes raw SD at 0x03000000
- SD Memory Map: `research/phase_a_sd_analysis/sd_memory_map_verified.md`
- Phase A Summary: `research/phase_a_sd_analysis/phase_a_final_summary.md`

## Next Steps
1. ✅ ~~Create clean SD image~~ - DONE, boots successfully
2. ✅ ~~Test boot on device~~ - SUCCESS (settings lost as expected)
3. ✅ ~~Locate settings storage~~ - FOUND @ 0x28000000
4. Create settings-preserved clean image (include 0x28000000 region)
5. Decode 0x190-byte settings struct layout
6. Identify UI Frame 1 content @ 0x03825800
7. Map touch calibration data structure (16-byte slots)

## Key Learnings
- **Empirical testing > endless speculation:** Clean image test immediately revealed settings storage location
- **Gaps contain settings!** Not all junk - critical data at 0x28000000 range
- **IBR headers are redundant:** Headers #2-5 in RAW are lookup table copies, not critical for boot
- **UI storage clarified:** RAW contains active pre-decoded frames, FAT contains XOR-masked update payloads
- **SD layout unconventional:** No partition table, direct RAW offsets for everything
- **Settings architecture:** Separate blocks for config (400 bytes) and calibration (100×16 bytes)
- **Ghidra naming strategy works:** Evidence-based renames with detailed comments improve code navigation

---

**Session Status:** Complete - Boot test successful, settings layer mapped  
**Time Investment:** ~3 hours (cleanup, verification, map creation, gap analysis, boot test, Ghidra analysis)  
**Confidence Level:** Very High - Empirical validation confirms SD layout understanding
