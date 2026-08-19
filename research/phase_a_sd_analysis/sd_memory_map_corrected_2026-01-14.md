# SD Card Memory Map - Corrected (2026-01-14)

> **Nicht autoritativ.** Abgeleiteter bzw. historischer Stand vom 2026-01-14.
> Autoritativ ist ausschliesslich `research/TRUTH.csv` (siehe `research/TRUTH.md`).
> Widersprueche zwischen diesem Dokument und TRUTH.csv werden zugunsten von
> TRUTH.csv aufgeloest.

**Date:** 2026-01-14  
**Status:** Facts vs. Hypotheses separated  
**SD Image:** firmware/image/sdcard.work.img (3.8 GB)  
**Cross-References:** Finding-0009, Finding-0010, Finding-0011

---

## Critical Corrections

### FAT Volumes (VERIFIED FACTS)
1. **Only TWO FAT volumes exist in firmware:**
   - `0:/` @ 0x04000000 (Fonts/Resources)
   - `3:/` @ 0x2A61BE00 (Update Staging "MINI")
2. **NO `1:/` or `2:/` mount points in firmware** (Finding-0010)
3. **Settings/Calibration use RAW SD writes**, not FAT volumes (Finding-0009)

### Region 0x24000000-0x2A61BDFF (STRONG EVIDENCE)
- **FACT:** Firmware does NOT mount this as FAT volume
- **FACT:** Contains FAT-like structures (boot sector @ 0x24007E00, deleted files)
- **FACT:** Firmware writes RAW data to 0x28000000 (settings) within this region
- **STRONG EVIDENCE (confidence: 0.9):** Recycled SD card - ext4 partition remnants found, garbage data between regions
- **See Finding-0011 for detailed analysis**

---

## Memory Map (Facts Only)

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
│ FAT VOLUME 0 (0x04000000 - 0x23FFFFFF) - 512 MB                 │
│ Mount Point: "0:/" (Finding-0010)                               │
├─────────────────────────────────────────────────────────────────┤
│ 0x04000000  Fonts/Resources (28 TrueType fonts, 168 MB used)    │ ✅ VERIFIED
│             CJK: MSYH, SimSun, SourceHan, etc.                  │
│             Western: Arial, Times, Calibri, etc.                │
│ 0x23FFFFFF  └─ Volume 0 ends                                    │ ⚠️ CALCULATED
├─────────────────────────────────────────────────────────────────┤
│ UNMOUNTED RAW REGION (0x24000000 - 0x2A61BDFF) - ~102 MB        │
│ CRITICAL: NOT A FAT VOLUME (Finding-0011)                       │
├─────────────────────────────────────────────────────────────────┤
│ 0x24007E00  FAT-like boot sector signature (OBSERVATION)        │ ❓ UNKNOWN
│             Volume label remnants, filesystem structures         │
│             Origin: Legacy firmware OR recycled SD card?         │
│                                                                  │
│ 0x24028000  Deleted BOOT.bin traces (12,736 bytes, 9-Dec-2022)  │ ✅ VERIFIED
│ 0x2402C000  Deleted APP.bin traces (2,576,940 bytes, 9-Dec-2022)│ ✅ VERIFIED
│ 0x24098FA8  └─ IBR Header #6 @ APP.bin+0x6CFA8 (embedded)       │ ✅ VERIFIED
│ 0x242A2000  Deleted UI-QVGA.bin traces (460,800 bytes, 5-Dec-22)│ ✅ VERIFIED
│                                                                  │
│ 0x28000000  SETTINGS BLOCK (400 bytes = 0x190)                  │ ✅ VERIFIED
│             RAW write (Finding-0009)                            │
│             Contains: Language, UI config, general settings     │
│             Functions: settings_load_validate_save (0x262778)   │
│                       settings_save_block (0x2661e0)            │
│                                                                  │
│ 0x28800000  CALIBRATION DATA (100 slots × 16 bytes)             │ ✅ VERIFIED
│ 0x28B2B000  └─ Range: 0x28800000 + i×0x4D000 per slot           │
│             RAW write (Finding-0009)                            │
│             Contains: Touch calibration points, alignment data  │
│             Function: settings_save_calibration_slots (0x265ea8)│
│                                                                  │
│ 0x2A61BDFF  └─ Unmounted region ends                            │ ⚠️ CALCULATED
├─────────────────────────────────────────────────────────────────┤
│ FAT VOLUME 3 (0x2A61BE00 - 0x2E61BDFF) - 64 MB "MINI"           │
│ Mount Point: "3:/" (Finding-0010)                               │
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

- ✅ **VERIFIED:** Direct evidence from firmware/binary/empirical test
- ⚠️ **CALCULATED:** Derived from verified start offset + size  
- ❓ **UNKNOWN:** Requires further investigation
- 🤔 **HYPOTHESIS:** Educated guess with stated confidence

---

## Key Facts (Confidence: 1.0)

1. **TWO FAT volumes only:** `0:/` and `3:/` (Finding-0010)
2. **NO `1:/` or `2:/` mount points** in firmware code
3. **Settings @ 0x28000000** use RAW SD writes (Finding-0009)
4. **Calibration @ 0x28800000** use RAW SD writes (Finding-0009)
5. **Region 0x24000000-0x2A61BDFF** is NOT mounted as FAT volume
6. **NVTFAT BSP uses 'A'-'Z' drive letters** - firmware uses "X:/" syntax (mapping unknown)

---

## Open Questions (Confidence: 0.0-0.9)

1. **What is the origin of FAT-like structures at 0x24007E00?**
   - Hypothesis A (confidence: 0.9): **Recycled SD card, not fully erased** - Evidence: ext4 partition remnants (7GB on 4GB card), extensive garbage between functional regions
   - Hypothesis B (confidence: 0.1): Legacy firmware generation, no longer used
   - Hypothesis C (confidence: 0.0): Intentional backup/staging area (no evidence)

2. **Why are deleted files timestamped 9-Dec-2022 and 5-Dec-2022?**
   - Hypothesis: Previous owner/usage before SD card recycling
   - Cannot verify without firmware version history or card provenance

3. **How does firmware map "0:/" and "3:/" to NVTFAT's 'A'-'Z' drive letters?**
   - Hypothesis A: Custom wrapper/abstraction layer
   - Hypothesis B: Direct internal mapping
   - Hypothesis C: Firmware uses different FAT library entirely (not NVTFAT)
   - Cannot verify without analyzing FAT filesystem code in APP.bin

---

## References

- **Finding-0009:** Settings Persistence Layer  
- **Finding-0010:** FAT Volume Mount Points (0:/ and 3:/ only)
- **Finding-0011:** SD Region 0x24000000-0x2A61BDFF Analysis
- **Session:** 2026-01-14_sd-memory-map-ibr-headers-cleanup.md
- **Session:** 2026-01-08_update-chain-sd-raw-mapping.md
- **NVTFAT BSP:** FA93VA93 Non-OS Library Reference Guide, p.78-92

---

**Document Status:** Corrected - Facts separated from speculation  
**Last Updated:** 2026-01-14
