# Boot Header Analysis

Image: `firmware/image/sdcard.work.img`
Size: 0xf0000000 (4026531840 bytes)

## Task 1: Header Locations vs FAT Volumes

Header Offset | Location Type | Volume | Offset from Volume Start
---|---|---|---
0x200 | before all FAT volumes | - | -
0x179dcc | before all FAT volumes | - | -
0x247aa68 | before all FAT volumes | - | -
0x306cfa8 | before all FAT volumes | - | -
0x3c7bd70 | before all FAT volumes | - | -
0x24098fa8 | inside FAT volume | Volume 2 | 0x911a8

## Task 2: Post-Header Content (128 bytes after header)

### Header at 0x200

32-byte header (hex):
```text
a55a4257000070000031000057425aa510100000008888000000000000000000
```
128 bytes after header (hex):
```text
dbf021e334d09fe5d7f021e330d09fe5d2f021e32cd09fe5d1f021e328d09fe5dff021e324d09fe5d3f021e320d09fe5100f11ee020ac0e3100f01ee050000ea00f07f0000f47f0000f87f0000fc7f000000800000ec7f00000000eb3c0000eb2c008fe2000c90e800a08ae000b08be001704ae20b005ae10000001a340000eb
```
ARM/Thumb heuristic:

- Looks like ARM/Thumb code: yes
- Vector table pattern: no
- ARM opcode hits: B/BL (0xea000005), B/BL (0x1a000000)
- Thumb opcode hits: BL/BLX prefix (0xf0db), BL/BLX prefix (0xf0d7), BL/BLX prefix (0xf0d2), BL/BLX prefix (0xf0d1), BL/BLX prefix (0xf0df), BL/BLX prefix (0xf0d3) ...
- Estimated code-like block size: 0x3200 bytes (stop: score_drop)
- Next boot header found at 0x179dcc (distance 0x179bcc)

### Header at 0x179dcc

32-byte header (hex):
```text
a55a4257000070000031000057425aa510100000008888000000000000000000
```
128 bytes after header (hex):
```text
58810e00e8820e00cdcc4c3d0ad7a33d72620000cdcccc3d77620000cdcc4c3e333a2f5a4b2d494e4b4a45542d424f4f542e62696e000000333a2f5a4b2d494e4b4a45542d435554452d424f4f542e62696e0000333a2f5a4b2d54494a5350532d383030783438302d424f4f542e62696e000000333a2f5a4b2d494e4b4a4554
```
ARM/Thumb heuristic:

- Looks like ARM/Thumb code: yes
- Vector table pattern: no
- ARM opcode hits: B/BL (0x5a2f3a33), B/BL (0x5a2f3a33), B/BL (0x5a2f3a33), B/BL (0x5a2f3a33)
- Thumb opcode hits: LDR literal (0x4954)
- Estimated code-like block size: 0x800 bytes (stop: score_drop)
- Next boot header found: not within 0x200000 scan window

### Header at 0x247aa68

32-byte header (hex):
```text
a55a4257000070000031000057425aa510100000008888000000000000000000
```
128 bytes after header (hex):
```text
00880e0090890e00cdcc4c3d0ad7a33d72620000cdcccc3d77620000cdcc4c3e333a2f5a4b2d494e4b4a45542d424f4f542e62696e000000333a2f5a4b2d494e4b4a45542d435554452d424f4f542e62696e0000333a2f5a4b2d54494a5350532d383030783438302d424f4f542e62696e000000333a2f5a4b2d494e4b4a4554
```
ARM/Thumb heuristic:

- Looks like ARM/Thumb code: yes
- Vector table pattern: no
- ARM opcode hits: B/BL (0x5a2f3a33), B/BL (0x5a2f3a33), B/BL (0x5a2f3a33), B/BL (0x5a2f3a33)
- Thumb opcode hits: LDR literal (0x4954)
- Estimated code-like block size: 0x1a200 bytes (stop: score_drop)
- Next boot header found: not within 0x200000 scan window

### Header at 0x306cfa8

32-byte header (hex):
```text
a55a4257000070000031000057425aa510100000008888000000000000000000
```
128 bytes after header (hex):
```text
cdcc4c3d0ad7a33d72620000cdcccc3d77620000cdcc4c3e333a2f5a4b2d494e4b4a45542d54494e592d424f4f542e62696e0000333a2f5a4b2d494e4b4a45542d50554e592d424f4f542e62696e0000333a2f5a4b2d494e4b4a45542d4e414e4f2d424f4f542e62696e0000333a2f5a4b2d494e4b4a45542d55492e62696e00
```
ARM/Thumb heuristic:

- Looks like ARM/Thumb code: yes
- Vector table pattern: yes (SP=0x3d4ccccd RV=0x3da3d70a)
- ARM opcode hits: B/BL (0x5a2f3a33), B/BL (0x5a2f3a33), B/BL (0x5a2f3a33), B/BL (0x5a2f3a33)
- Thumb opcode hits: none
- Estimated code-like block size: 0xa100 bytes (stop: score_drop)
- Next boot header found: not within 0x200000 scan window

### Header at 0x3c7bd70

32-byte header (hex):
```text
a55a4257000070000031000057425aa510100000008888000000000000000000
```
128 bytes after header (hex):
```text
ac900e003c920e00cdcc4c3d0ad7a33d72620000cdcccc3d77620000cdcc4c3e333a2f5a4b2d494e4b4a45542d424f4f542e62696e000000333a2f5a4b2d494e4b4a45542d435554452d424f4f542e62696e0000333a2f5a4b2d54494a5350532d383030783438302d424f4f542e62696e000000333a2f5a4b2d494e4b4a4554
```
ARM/Thumb heuristic:

- Looks like ARM/Thumb code: yes
- Vector table pattern: no
- ARM opcode hits: B/BL (0x5a2f3a33), B/BL (0x5a2f3a33), B/BL (0x5a2f3a33), B/BL (0x5a2f3a33)
- Thumb opcode hits: LDR literal (0x4954)
- Estimated code-like block size: 0x10900 bytes (stop: score_drop)
- Next boot header found: not within 0x200000 scan window

### Header at 0x24098fa8

32-byte header (hex):
```text
a55a4257000070000031000057425aa510100000008888000000000000000000
```
128 bytes after header (hex):
```text
cdcc4c3d0ad7a33d72620000cdcccc3d77620000cdcc4c3e333a2f5a4b2d494e4b4a45542d54494e592d424f4f542e62696e0000333a2f5a4b2d494e4b4a45542d50554e592d424f4f542e62696e0000333a2f5a4b2d494e4b4a45542d4e414e4f2d424f4f542e62696e0000333a2f5a4b2d494e4b4a45542d55492e62696e00
```
ARM/Thumb heuristic:

- Looks like ARM/Thumb code: yes
- Vector table pattern: yes (SP=0x3d4ccccd RV=0x3da3d70a)
- ARM opcode hits: B/BL (0x5a2f3a33), B/BL (0x5a2f3a33), B/BL (0x5a2f3a33), B/BL (0x5a2f3a33)
- Thumb opcode hits: none
- Estimated code-like block size: 0xa100 bytes (stop: score_drop)
- Next boot header found: not within 0x200000 scan window

## Task 3: Header Field Comparison

Header Offset | Field A (bytes 16-19) | Field B (bytes 20-23)
---|---|---
0x200 | 0x00001010 | 0x00888800
0x179dcc | 0x00001010 | 0x00888800
0x247aa68 | 0x00001010 | 0x00888800
0x306cfa8 | 0x00001010 | 0x00888800
0x3c7bd70 | 0x00001010 | 0x00888800
0x24098fa8 | 0x00001010 | 0x00888800

Field A and Field B are identical across all six headers.

Potential meaning (hypotheses):
- Field A (0x00001010) could be a version/flags field (e.g., header version + attributes).
- Field B (0x00888800) could be a size, address, or checksum seed; its repeated value suggests a constant parameter for this header type.

## Task 4: Hypotheses About Multiple Headers

- Redundant boot headers: multiple copies spread across the image for recovery or boot-fallback when earlier copies are corrupted.
- Placement at specific offsets may align to erase blocks or partition boundaries, indicating update slots or checkpointed stages.
- Only the first header (0x200) is followed by ARM-like code; others appear to be data blocks, suggesting either placeholder headers or markers for alternate images/components.
- Headers inside FAT volumes (Volume 1 and 2) might be embedded within files or reserved areas used by the bootloader or update system.

## Recommendations for Ghidra Analysis

- Prioritize 0x200 (+0x20) for disassembly: it shows strong ARM opcode patterns and likely contains actual boot code.
- Inspect headers within FAT volumes (0x24098fa8 in Volume 2, and 0x3c7bd70 in Volume 1) in case they map to files or update slots; cross-reference with FAT directory entries.
- Treat 0x179dcc, 0x247aa68, 0x306cfa8 as likely data until corroborated; they did not show code-like signatures in the immediate 128-byte window.