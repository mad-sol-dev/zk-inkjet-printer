# USB Claims (From E3-Old RE-KB Archive)

Propositional claims synthesized from historical RE-KB findings. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## USB Stack and Descriptors

### ✅ Verified CL-RKO-USB-001: USB File Scanning Trigger - Boot-Time Hold-Key Detection
**Claim:** USB trigger mechanisms identified: (1) Boot-time hold-key detection calls maybe_update_from_udisk @ VA 0x0026887C. (2) Runtime menu via "OS Update"/"UI Update" menus. Device has USB DEVICE mode (MSC), NOT USB host. Exposes 64MB "MINI" volume (FAT16) when "USB" menu activated. User copies files to MINI via PC, then uses Update menus which COPY files from MINI (volume 0:/) to internal storage (volume 3:/) for processing. BMP printing via File → USB file browser: browse MINI volume, select BMP, Open in editor, adjust (zoom/rotate/mirror), press Start to print. No special filename pattern required. About screen shows 0.8/3.8GB used on internal storage, ~3GB free. No checksums - files trusted by filename match. Complete workflow documented for remote text-to-print via BMP conversion.

**Evidence:**
- E-RKO-USB-001: Boot-time trigger documented in docs/analysis_traceability.md (2025-11-05 session): 'Boot-time helper maybe_update_from_udisk (0x0026887c) invokes update_copy_or_flash twice (BOOT then APP) after boot_holdkey_update_check arms the pipeline.'
- E-RKO-USB-001: Entry point called by bootloader after hold-key detection. Initiates USB scanning pipeline.
- E-RKO-USB-001: First filename matching loop. Calls memcmp @ 0x0020E158, branches to 0x002C28D0 on success or 0x002C47F0 on failure.
- E-RKO-USB-001: Upgrade mechanism fully documented in docs/update_file_rules.md with objdump evidence, memcmp call sites, and handler linkages. No checksums found in upgrade pipeline.

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-USB-004, CL-BOOT-011
**Next Tests:** None listed

---

### ⚠️ Supported CL-RKO-USB-002: USB Stack Architecture for CDC Extension
**Claim:** Preliminary USB stack map for adding CDC: device descriptor blob at 0x00475140 contains MSC product string "W55FA93 USB Card Reader 1.00" (VID:PID 0416:0093 assumed). Firmware uses MMIO base 0xB8007000 (literal at 0x00030ab8); small init stub at 0x00030a94 sets *(DAT_00030ab4+4)=0x32 and ORs bit1 into *(0xB8007000+0x7C), likely enabling the USB device controller. APP.bin is fully occupied (2,576,940 bytes) with no trailing 0xFF padding, so space must be reclaimed for CDC code.

**Evidence:**
- E-RKO-USB-002: Descriptor blob at VA 0x00475140 decodes to "W55FA93 USB Card Reader 1.00"
- E-RKO-USB-002: Literal pool at 0x00030ab8 holds MMIO base 0xB8007000
- E-RKO-USB-002: Init stub at 0x00030a94 writes 0x32 to DAT_00030ab4+4 and sets bit1 in *(0xB8007000+0x7C)
- E-RKO-USB-002: APP.bin size 2,576,940 bytes; no trailing 0xFF padding
- E-RKO-USB-002: USB UDC Init function - writes 0x32 to DAT_00030ab4+4, sets bit1 at UDC_BASE+0x7C (0xB8007000+0x7C |= 0x2). Likely enables USB device controller. Called from 7+ functions: FUN_00012520, FUN_0002b930, FUN_00000264, FUN_0005dc78, FUN_0006406c, FUN_00068808, FUN_0006c4e0
- E-RKO-USB-002: UDC base 0xb8007000 identified via literal pools at 0x30ab8/0x323cc/0x46c28/0x46ebc/0x5c3d8/0x8b03c/0xb4068. Register access map: (1) FUN_00032310 writes base+0=0x1b1, base+4=0x4444, sets control bits at base+8 (|=0x80800 then |=0x10100), programs base+0x18=99, +0x1c=0x31, +0x24=0x3e7, +0x28=1, clears bits1-2 at base+0x40, and sets bit2 at base+0x7c – looks like SIE/PHY init and global interrupt enable. (2) FUN_0005c1a0 (top-level USB init) zeroes base+0x30/+0x34, clears bit3 at base+0x40, clears bit1 at base+0x7c, programs analog/PHY regs at base-0x5000..-0x4fe4 (0xb8002000/2004/200c/2018/201c) with 0/1/0x2ee0 and mask 0x68000000, then configures endpoint/FIFO region at base+0x1108/0x110c/0x1120/0x1124 (values 7→1, 3, 0xa0→0x7f, 0x30000066) before re-enabling clocks. (3) FUN_00046bfc and FUN_000b3f3c clamp a parameter 1..1000 then write base+0x28 (likely SOF interval/timeout). (4) FUN_00046e48 uses base+0x30=24000 and base+8 |=0x0100_0000, polling base+0x38 until 0 then clearing +0x30 (looped param times); FUN_0008adcc performs same sequence with base+0x30=0xf0. (5) FUN_00030a94 ORs base+0x7c with 0x2 (per-FIQ/interrupt enable). These touchpoints outline UDC init, timing, and interrupt paths where CDC hooks would attach.
- E-RKO-USB-002: Main USB bringup routine FUN_0002b930: Called only by FUN_000644d4 (high in boot). Performs full USB controller config with descriptor setup, endpoint configuration, and crypto/token generation. Calls USB init (FUN_00030a94) 5 times - one retry loop with 500ms delay until ready, four conditional resets based on state flag [r6+0xc8]. Programs MMIO bases 0x60000000 and 0x48000000 via helpers (in addition to known 0xB8007000). Key callees: FUN_00065954 (endpoint config, 4x), FUN_00065d64 (callback registration), FUN_000323dc (setup stages, 3x).
- E-RKO-USB-002: FUN_0005c1a0 detailed endpoint/FIFO register sequence: UDC base loaded from DAT_0005c3d8. Writes base+0x1108 (7→1, likely endpoint selector), base+0x110c (3), base+0x1120 (0xa0→0x7f, FIFO size/offset), base+0x1124 (0x30000066, config flags). Also clears base+0x30, base+0x34, base+0x40 bit3, base+0x7c bit1. Helper functions: FUN_000a1928 (early init), FUN_00031f34 (5 calls), FUN_0003224c (3 calls), FUN_00032310 (SIE/PHY), FUN_00080b7c (unknown setup).
- E-RKO-USB-002: FUN_00065d64 is NOT a direct callback registrar but an init/wrapper function. Signature: (int flagA, int flagB, int ctx, void *maybe_cb, void *arg5). Parses descriptors via FUN_000c2b58, calls FUN_00064094 to build endpoint dispatch tables (bitmask arrays, not function pointers), enables USB hardware/IRQs when flagB=1. Call from FUN_0002b930 passes all zeros for callback params, only triggers hardware init. Real callback handlers stored elsewhere. FUN_00064094 builds endpoint tables using globals DAT_000644b8/bc, allocates buffers via FUN_0002f530.

**Status:** ⚠️ Supported
**Cross-Reference:** Potential overlap with CL-USB-010, CL-USB-017
**Next Tests:** Find all xrefs to literal pool at 0x00030ab8 (0xB8007000) to map UDC register usage and endpoints; Locate descriptor pointer tables referencing 0x00475140 and VID/PID fields; Identify USB IRQ handler by searching for writes to UDC INT/EP status registers (offsets near 0x7c, etc.); Map MSC class callbacks and SCSI command dispatch to mirror for CDC; Assess code/data regions that can be freed for CDC stub insertion

---

### ⚠️ Supported CL-RKO-USB-003: USB Descriptor Locations and CDC Patch Strategy
**Claim:** Complete mapping of USB descriptor structures in APP.bin for CDC patching. Ghidra memory layout: image_base=0x0, FLASH block at 0x200000-0x47522B (VA to file offset: VA - 0x200000). USB descriptors located: Device @ VA 0x475101 (file 0x275101), Config @ VA 0x475118 (file 0x275118), Strings @ VA 0x475140 (file 0x275140). MSC mode uses VID:PID 0416:0093, EP1 IN (0x81) + EP2 OUT (0x02), 512 byte packets (HS). EP3 is free for CDC interrupt endpoint. CDC patch strategy: reuse EP1/EP2 for bulk data, add CDC control interface with EP3 INT, extend config descriptor. APP.bin is extensible (Test A: +4KB succeeded), descriptors patchable at known offsets.

**Evidence:**
- E-RKO-USB-003: Ghidra memory layout: image_base=0x0, FLASH block 0x200000-0x47522B. VA to file offset formula: VA - 0x200000. Explains Test B brick: file offset 0x275140 was correct but contained critical code alongside strings.
- E-RKO-USB-003: USB Device Descriptor at VA 0x00475101 (file offset 0x275101). Pattern: 12 01... VID:PID 0416:0093
- E-RKO-USB-003: USB Configuration Descriptor at VA 0x00475118 (file offset 0x275118). Pattern: 09 02...
- E-RKO-USB-003: USB String Descriptors at VA 0x00475140 (file offset 0x275140). Contains UTF-16-LE strings: 'nuvoTon', 'USB MSC', '00000055FA93', 'W55FA93 USB Card Reader 1.00'
- E-RKO-USB-003: lsusb -v output for MSC mode (VID:PID 0416:0093): High Speed USB 2.0, EP1 IN (0x81) + EP2 OUT (0x02), 512 byte bulk packets, MSC SCSI Bulk-Only protocol
- E-RKO-USB-003: lsusb -v output for IBR boot mode (VID:PID 0416:9396): Uses EP2 IN (0x82) + EP3 OUT (0x03), confirming EP3 is available in APP.bin

**Status:** ⚠️ Supported
**Cross-Reference:** Potential overlap with CL-USB-015, CL-USB-014
**Next Tests:** Create Python script to build CDC descriptor blob; Test conservative patch: change only string descriptors ("USB MSC"→"CDC Test"); Verify descriptor location with string patch before full CDC replacement; Map FUN_00065954 (endpoint config) and FUN_00065d64 (callback registration) for CDC handler hooks; Design minimal CDC handler: echo/loopback for initial testing

---
