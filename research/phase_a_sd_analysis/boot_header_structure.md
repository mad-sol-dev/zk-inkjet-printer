# Boot sector header structure analysis

## Summary
- Header located at `sdcard.work.img` offset `0x200` (32 bytes)
- ARM code starts at `0x220` and matches `ZK-INKJET-NANO-BOOT.bin` byte-for-byte

## 1) Hex dump of 32-byte header (offset 0x200)
```
0x0200: a55a4257000070000031000057425aa5
0x0210: 10100000008888000000000000000000
```

### Byte-by-byte annotation
| Offset | Hex | ASCII | Interpretation |
| --- | --- | --- | --- |
| 0x00 | 0xa5 | . | Start marker (0xA5) |
| 0x01 | 0x5a | Z | Signature: 'Z' |
| 0x02 | 0x42 | B | Signature: 'B' |
| 0x03 | 0x57 | W | Signature: 'W' |
| 0x04 | 0x00 | . | Reserved/padding |
| 0x05 | 0x00 | . | Reserved/padding |
| 0x06 | 0x70 | p | Value 0x70 (ASCII 'p' if interpreted as char) |
| 0x07 | 0x00 | . | Reserved/padding |
| 0x08 | 0x00 | . | Reserved/padding |
| 0x09 | 0x31 | 1 | Value 0x31 (ASCII '1' if interpreted as char) |
| 0x0a | 0x00 | . | Reserved/padding |
| 0x0b | 0x00 | . | Reserved/padding |
| 0x0c | 0x57 | W | Signature (reverse): 'W' |
| 0x0d | 0x42 | B | Signature (reverse): 'B' |
| 0x0e | 0x5a | Z | Signature (reverse): 'Z' |
| 0x0f | 0xa5 | . | End marker (0xA5) |
| 0x10 | 0x10 | . | Field A (0x10) |
| 0x11 | 0x10 | . | Field A (0x10) |
| 0x12 | 0x00 | . | Field A (0x00) |
| 0x13 | 0x00 | . | Field A (0x00) => 0x00001010 (LE) or 0x10100000 (BE) |
| 0x14 | 0x00 | . | Field B (0x00) |
| 0x15 | 0x88 | . | Field B (0x88) |
| 0x16 | 0x88 | . | Field B (0x88) |
| 0x17 | 0x00 | . | Field B (0x00) => 0x00888800 (LE) or 0x00888800 (BE) |
| 0x18 | 0x00 | . | Field C (0x00) |
| 0x19 | 0x00 | . | Field C (0x00) |
| 0x1a | 0x00 | . | Field C (0x00) |
| 0x1b | 0x00 | . | Field C (0x00) => 0x00000000 |
| 0x1c | 0x00 | . | Field D (0x00) |
| 0x1d | 0x00 | . | Field D (0x00) |
| 0x1e | 0x00 | . | Field D (0x00) |
| 0x1f | 0x00 | . | Field D (0x00) => 0x00000000 |

## 2) SD@0x220 vs BOOT.bin@0x00 (first 128 bytes)
| Offset | SD (hex) | BOOT.bin (hex) |
| --- | --- | --- |
| 0x00 | dbf021e334d09fe5d7f021e330d09fe5 | dbf021e334d09fe5d7f021e330d09fe5 |
| 0x10 | d2f021e32cd09fe5d1f021e328d09fe5 | d2f021e32cd09fe5d1f021e328d09fe5 |
| 0x20 | dff021e324d09fe5d3f021e320d09fe5 | dff021e324d09fe5d3f021e320d09fe5 |
| 0x30 | 100f11ee020ac0e3100f01ee050000ea | 100f11ee020ac0e3100f01ee050000ea |
| 0x40 | 00f07f0000f47f0000f87f0000fc7f00 | 00f07f0000f47f0000f87f0000fc7f00 |
| 0x50 | 0000800000ec7f00000000eb3c0000eb | 0000800000ec7f00000000eb3c0000eb |
| 0x60 | 2c008fe2000c90e800a08ae000b08be0 | 2c008fe2000c90e800a08ae000b08be0 |
| 0x70 | 01704ae20b005ae10000001a340000eb | 01704ae20b005ae10000001a340000eb |

## 3) Match verification
- Compared length: 12736 bytes (entire BOOT.bin)
- Prefix match length: 12736 bytes
- Full match: true

## 4) Proposed header field structure
Proposed field layout (16-byte rows):
- 0x00-0x03: Magic start + signature "ZBW" (0xA5 0x5A 0x42 0x57)
- 0x04-0x0B: Two small numeric fields with padding (0x0070, 0x0031) if treated as 16-bit BE, zeros elsewhere
- 0x0C-0x0E: Signature mirror "WBZ" (0x57 0x42 0x5A)
- 0x0F: End marker (0xA5)
- 0x10-0x13: Field A = 0x00001010 (LE) / 0x10100000 (BE)
- 0x14-0x17: Field B = 0x00888800 (LE/BE)
- 0x18-0x1F: Field C/D = 0x00000000 (reserved)

Hypotheses:
- `0xA5` markers likely delimit header start/end.
- "ZBW" and reversed "WBZ" look like a symmetric signature or a sanity check for byte order.
- The zeros between numeric bytes suggest 16-bit aligned fields or reserved padding.
- Field A (0x00001010 or 0x10100000) could be load address, header size, or flags.
- Field B (0x00888800) looks like a patterned constant, possibly a checksum seed or a fixed load address segment.
- Final 8 bytes are zero, consistent with reserved space for future fields (e.g., CRC, length).

## 5) ASCII art diagram of header layout
```
+00                                   +0F
[0xA5][Z][B][W][00][00][0x70][00][00][0x31][00][00][W][B][Z][0xA5]
+10                                   +1F
[0x10 0x10 0x00 0x00][0x00 0x88 0x88 0x00][0x00 0x00 0x00 0x00][0x00 0x00 0x00 0x00]
```

## 6) Other occurrences of the header pattern (0xA5 0x5A 0x42 0x57)
- 0x200: matches header
- 0x179dcc: matches header
- 0x247aa68: matches header
- 0x306cfa8: matches header
- 0x3c7bd70: matches header
- 0x24098fa8: matches header
- 0x62d3f2c7: pattern only (header does not match)

Notes:
- Six offsets contain the exact 32-byte header sequence.
- One offset is a false-positive pattern where the remaining 28 bytes do not match the header.
