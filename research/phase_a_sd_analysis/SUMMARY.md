# Phase A: SD Image Analysis - Quick Summary

**Date:** 2026-01-07  
**Status:** COMPLETE

---

## What We Did

1. Verified BOOT.bin structure and locations
2. Identified and inspected all three FAT volumes
3. Corrected previous assumptions about firmware storage
4. Documented complete boot chain and update workflow

---

## Key Findings (TL;DR)

### Boot Structure:
- IBR Header: 32 bytes @ 0x200 (0xA5 signature, Fields A/B)
- BOOT.bin code: Starts @ 0x220 (12,736 bytes ARM code)
- APP.bin: @ 0x100000 (ARM vector table confirmed)

### FAT Volumes:
- Volume 1 (512 MB): Fonts/Resources (168 MB used)
- Volume 2 (256 MB): System/Staging (450 KB used, deleted firmware)
- Volume 3 "MINI" (64 MB): EMPTY (user USB drive, 88 bytes metadata)

### Critical Corrections:
- "ZBWp1WBZ" signature -> Spaced pattern: [ZBW...WBZ]
- Firmware in Volume 3 -> Volume 3 empty, firmware was deleted in Volume 2
- Volume 3 unknown -> Volume 3 verified @ 0x2A61BE00, label "MINI"

---

## Confidence Levels

**VERIFIED (Hardware Ground Truth):**
- Boot header structure
- FAT volume locations and contents
- Volume 3 identity and empty status

**HYPOTHESIS (Needs Firmware Verification):**
- Volume 0:/ mapping (likely Volume 2)
- Update system header injection
- IBR header Field A/B meanings

---

## Documents to Read

1. **Quick Start:** This file (SUMMARY.md)
2. **Complete:** [phase_a_final_summary.md](./phase_a_final_summary.md)
3. **Details:** Individual topic files (boot_locations, volumes, etc.)
4. **Methods:** [methods_phase_a_sd_analysis.md](./methods_phase_a_sd_analysis.md)

---

## Next Phase

**Phase B:** Firmware analysis in Ghidra to verify volume mounts and USB controller usage.
