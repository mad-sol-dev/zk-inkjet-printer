# Phase A: SD Image Analysis Methods

**Date:** 2026-01-07  
**Objective:** Establish ground truth for boot chain and FAT volume locations from SD card image  
**Source Image:** firmware/image/sdcard.work.img  
**Image SHA256:** 6c19248aa79b6f990b45aa1d4f18c58c92d1317a23d0bd36c285d83cadb8b95b

---

## Image Verification

All three image files are identical (verified by SHA256):
- `sdcard.work.img` 
- `sdcard.workout.img` 
- `sdcard.work.img.xz` (decompressed)

**Method:**
```bash
sha256sum sdcard.work.img sdcard.workout.img
xz -dc sdcard.work.img.xz | sha256sum
```

**Result:** All hashes = `6c19248aa79b6f990b45aa1d4f18c58c92d1317a23d0bd36c285d83cadb8b95b`

---

## A1: BOOT.bin Location Verification

**Hypothesis (from system_understanding.md):**
- Location: SD offset 0x200 (512 bytes)
- Signature: "ZBWp1WBZ" (hex: 5a 42 57 70 31 57 42 5a)
- Size: 12.7 KB (~13000 bytes)

**Method:**
```python
with open('sdcard.work.img', 'rb') as f:
    f.seek(0x200)
    header = f.read(16)
    print(header.hex())
```

**Results:**
- Bytes at 0x200: `a5 5a 42 57 00 00 70 00 00 31 00 00 57 42 5a a5`
- **Signature Check: FAIL** - Does NOT match expected "ZBWp1WBZ" sequence
- Extracted BOOT.bin SHA256: `142a8ff5457df4ff86aeff1e6b7d63773f410074fb3d8660545b01b7f4537ce7`
- Reference firmware/bin/ZK-INKJET-NANO-BOOT.bin SHA256: `a651630c374c5441190cc35887baa814b4820c8ba2be100c9614f622cca6264d`
- **Comparison: DIFFER** - SD image contains different version than standalone bin file

**Saved artifact:** firmware/image/BOOT.extracted.bin

---

## A2: APP.bin Location Verification

**Hypothesis (from system_understanding.md):**
- Location: SD offset 0x100000 (1048576 bytes)
- Size: ~2.6 MB
- Contains ARM interrupt vector table

**Method:**
```python
with open('sdcard.work.img', 'rb') as f:
    f.seek(0x100000)
    header = f.read(64)
    print(hexdump(header))
```

**Results:**
- First 64 bytes at 0x100000:
  ```
  14 00 00 ea 18 f0 9f e5 18 f0 9f e5 18 f0 9f e5
  18 f0 9f e5 00 00 00 00 18 f0 9f e5 18 f0 9f e5
  58 00 00 00 40 00 00 00 44 00 00 00 48 00 00 00
  4c 00 00 00 00 00 00 00 50 00 00 00 54 00 00 00
  ```
- **ARM Vector Table: CONFIRMED**
  - First instruction: 0xEA000014 (ARM branch)
  - Multiple 0xE59FF018 (ldr pc, [pc, #0x18]) entries
  - Followed by address table
- APP header 4KB SHA256 (SD): `d3dc92fcd2e9a307bbd8fe8ce0a7c8f4ec94bebf7db46614ae1a2b98be00208a`
- APP header 4KB SHA256 (bin): `560e6e43beb9201f12258f8738d6f74b5a745ea8b0771749a75266373d4df6ed`
- **Comparison: DIFFER** - SD image contains different version than standalone bin file

**Saved artifact:** firmware/image/APP.header.bin

---

## A3: FAT Volume Discovery

**Method:**
Scan entire SD image for FAT boot sector signatures:
1. Search for 0x55AA at offset 510-511 (512-byte aligned)
2. Verify FAT boot sector structure (jump instruction at start)
3. Parse boot sector fields to extract volume metadata

**Python Implementation:**
```python
# Read SD image in 512-byte chunks
# Check for 0x55AA signature
# Verify jump instruction (EB xx 90 or E9 xx xx)
# Parse BPB (BIOS Parameter Block) fields
```

**Results:**

| Offset | FS Type | Size (MB) | Label | Sectors/Cluster | Reserved | FATs | Root Entries | Total Sectors |
|--------|---------|-----------|-------|-----------------|----------|------|--------------|---------------|
| 0x04000000 | FAT16 | 512.00 | NO NAME | 128 | 6 | 2 | 512 | 1048576 |
| 0x24007E00 | FAT | 255.97 | NO NAME | 16 | 1 | 1 | 512 | 524225 |
| 0x2A61BE00 | FAT | 63.97 | NO NAME | 8 | 1 | 1 | 512 | 131041 |

**Notes:**
- Volume 1 (FAT16, 512 MB): Largest volume, likely system/resource storage
- Volume 2 (FAT, 256 MB): Medium size, possibly staging area
- Volume 3 (FAT, 64 MB): Matches "MINI" USB drive size mentioned in firmware references

**Saved artifact:** research/sd_fat_volumes.txt (detailed boot sector analysis)

---

## Key Findings

### ✅ Confirmed
1. **APP.bin location:** 0x100000 contains valid ARM vector table
2. **FAT volumes:** 3 distinct FAT filesystems identified at known offsets
3. **64 MB volume:** Found at 0x2A61BE00, matches expected "MINI" USB drive size

### ❌ Contradictions Found
1. **BOOT.bin signature:** Expected "ZBWp1WBZ" not found at 0x200
2. **Version mismatch:** SD image firmware ≠ standalone bin files (different SHA256)

### ⚠️ Open Questions
1. What is the actual BOOT.bin signature/header structure?
2. Why do SD image and standalone bins differ? (Different firmware versions?)
3. Which FAT volume corresponds to "0:/" and which to "3:/"?
4. Is there additional boot code before 0x200?

---

## Next Steps (Phase B)

Firmware analysis required to resolve:
1. Search for volume mount code (f_mount calls with "0:/" and "3:/")
2. Find FatFS volume-to-LBA mapping configuration
3. Locate update function references to determine volume usage
4. Verify BOOT.bin loading mechanism in IBR/bootloader

---

## Tools Used
- Python 3 (byte extraction, SHA256)
- Desktop Commander (file operations)
- Codex CLI (automated analysis tasks)

## Artifacts Generated
- firmware/image/BOOT.extracted.bin (13000 bytes from 0x200)
- firmware/image/APP.header.bin (4096 bytes from 0x100000)  
- research/sd_fat_volumes.txt (detailed FAT boot sector analysis)
- research/methods_phase_a_sd_analysis.md (this document)
