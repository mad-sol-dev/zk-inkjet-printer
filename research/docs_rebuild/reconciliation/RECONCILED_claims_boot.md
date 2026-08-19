# BOOT Reconciled Claims (Phase 2C-3)

Authority order: E0 > E3-New > E1 > E3-Old > E4 (E2 = context only).

---

## CL-BOOT-REC-001: SD Card Required for Boot

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** The device does not boot without the SD card installed.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-BOOT-002 (no boot without SD)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Power-cycle the device with the SD card removed and confirm no display/boot progress.

**Tags:** boot, sd-card, requirement

---

## CL-BOOT-REC-002: Boot Chain IBR -> BOOT.bin -> APP.bin

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** The boot chain proceeds from internal Boot ROM (IBR) to BOOT.bin, which initializes hardware and then loads APP.bin into RAM.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-BOOT-003 (IBR/SRAM sizes), E-BOOT-005 (IBR loads BOOT.bin), E-BOOT-006 (BOOT init), E-BOOT-007 (BOOT loads APP), E-BOOT-012 (APP copied to 0x03000000)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Disassemble BOOT.bin and confirm the load-and-jump sequence into APP.bin.

**Tags:** boot, chain, ibr, app

---

## CL-BOOT-REC-003: BOOT.bin Header at SD Offset 0x200 (ZBWp1WBZ)

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** The SD image contains a BOOT.bin header at offset 0x200 with the ZBWp1WBZ signature, indicating the stage-1 loader region.

**Evidence (All Tiers):**
- **E0:** `firmware/image/sdcard.work.img` (offset 0x200 bytes = `a5 5a 42 57 00 00 70 00 00 31 00 00 57 42 5a a5`)
- **E3-New:** None
- **E1:** E-BOOT-001 (stage-1/2 signature), E-BOOT-010 (offset 0x200 signature)
- **E3-Old:** E-RKO-BOOT-005 (raw offset 0x200, ZBWp1WBZ signature) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-003
- E1: CL-BOOT-006
- E3-Old: CL-RKO-BOOT-005 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Confirm the stage-2 loader boundaries following the 0x200 header region.

**Tags:** boot, sd-card, boot.bin, signature

---

## CL-BOOT-REC-004: BOOT.bin Is a Small ARM Loader (~12.7 KB)

**Status:** verified
**Confidence:** 0.90
**Authority:** E0

**Statement:** BOOT.bin is a compact ARM loader of 12,736 bytes with minimal strings and loader-style structure.

**Evidence (All Tiers):**
- **E0:** `firmware/boot/ZK-INKJET-NANO-BOOT.bin` (size 12,736 bytes; ARM vectors at file start)
- **E3-New:** None
- **E1:** E-BOOT-026 (low-entropy ARM loader), E-BOOT-027 (stage-2 loader role)
- **E3-Old:** E-RKO-BOOT-005 (BOOT size 12,736 bytes, ARM code start) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-015
- E3-Old: CL-RKO-BOOT-005 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Extract strings from BOOT.bin and confirm minimal symbol presence.

**Tags:** boot, boot.bin, arm, size

---

## CL-BOOT-REC-005: BOOT.bin Can Load APP.bin From FAT

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E1

**Statement:** BOOT.bin can mount a FAT filesystem and load APP.bin by pathname instead of fixed offsets.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-BOOT-008 (FAT mount + APP load)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-004

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Trace BOOT.bin file I/O routines for FatFS f_open/f_read calls.

**Tags:** boot, boot.bin, fatfs, app

---

## CL-BOOT-REC-006: SoC Boot ROM Supports SD/NAND/SPI/USB

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** The SoC boot ROM supports booting from SD, raw NAND, SPI flash, and USB.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-BOOT-004 (boot mode list)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-005

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Cross-check SoC strap table in the BSP or datasheet.

**Tags:** boot, soc, boot-modes

---

## CL-BOOT-REC-007: APP.bin Located at SD Offset 0x100000 With ARM IVT

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** APP.bin resides at raw SD offset 0x100000 (LBA 0x800) and begins with an ARM interrupt vector table; file size is about 2,576,940 bytes.

**Evidence (All Tiers):**
- **E0:** `firmware/image/sdcard.work.img` (offset 0x100000 begins with ARM IVT words like `0xEA000014`); `firmware/app/ZK-INKJET-NANO-APP.bin` (size 2,576,940 bytes)
- **E3-New:** None
- **E1:** E-BOOT-011 (APP at 0x100000 with IVT), E-BOOT-028 (APP size ~2.6 MB)
- **E3-Old:** E-RKO-BOOT-005 (raw offset 0x100000, IVT, size) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-007
- E3-Old: CL-RKO-BOOT-005 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Disassemble the first 0x40 bytes at 0x100000 to confirm IVT vectors.

**Tags:** boot, app.bin, ivt, sd-card

---

## CL-BOOT-REC-008: APP.bin Loads to RAM Address 0x03000000

**Status:** supported
**Confidence:** 0.85
**Authority:** E1

**Statement:** The boot process copies APP.bin into DDR at address 0x03000000 before execution.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-BOOT-012 (APP copied to 0x03000000)
- **E3-Old:** E-RKO-BOOT-004 (APP copy to 0x03000000) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-008
- E3-Old: CL-RKO-BOOT-004 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Locate the copy routine in BOOT.bin and confirm the jump target.

**Tags:** boot, app.bin, ram, load-address

---

## CL-BOOT-REC-009: BOOT Enables MMU/Cache and Identity Maps RAM

**Status:** supported
**Confidence:** 0.75
**Authority:** E3-Old

**Statement:** BOOT.bin uses CP15 control to enable MMU/cache with a 1 MB section table at TTBR 0x00004000, identity-mapping VA 0x03000000 to PA 0x03000000.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-BOOT-004 (MMU enable + TTBR mapping details) [ghidra-v1]
- **E4:** E-OLD-BOOT-004 (CP15 cache/MMU control sequence) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E3-Old: CL-RKO-BOOT-004
- E4: CL-OLD-BOOT-004

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Validate MMU table contents in BOOT.bin and confirm domain/control register values.

**Tags:** boot, mmu, cp15, memory-map

---

## CL-BOOT-REC-010: SDLoader and Execute Image Sector Ranges

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** The SDLoader occupies sectors 1-33 and the execute-image region begins at sector 544 in the TurboWriter map.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-BOOT-013 (SDLoader sectors 1-33), E-BOOT-014 (execute image starts sector 544)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-009

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Compare a TurboWriter-generated image against the SD dump for sector placement.

**Tags:** boot, sd-card, sectors, turbowriter

---

## CL-BOOT-REC-011: MINI FAT Appears at ~711 MB With No Partition Table

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** The SD card has no partition table, and the MINI FAT-like filesystem begins around the 711 MB offset.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-BOOT-015 (MINI FAT offset), E-BOOT-016 (no partition table)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-010

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Scan the SD image for FAT boot-sector signatures around 711 MB.

**Tags:** boot, sd-card, fat, layout

---

## CL-BOOT-REC-012: Update Workflow Reads FAT and Writes Raw Offsets

**Status:** supported
**Confidence:** 0.80
**Authority:** E3-Old

**Statement:** Firmware updates scan 3:/, read update files via FatFS, then write BOOT/APP to raw SD offsets without checksum/crypto verification.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-BOOT-019 (scan 3:/), E-BOOT-020 (MINI to internal workflow), E-BOOT-024 (FatFS f_open/f_read)
- **E3-Old:** E-RKO-BOOT-005 (raw write path, no checksum) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-011
- E1: CL-BOOT-012
- E3-Old: CL-RKO-BOOT-005 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Locate update handler functions in APP.bin and confirm raw write routines.

**Tags:** boot, update, fatfs, raw-write

---

## CL-BOOT-REC-013: TurboWriter Builds Bootable SD Images

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** TurboWriter consumes .bin files and produces bootable SD images with the required headers.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-BOOT-022 (TurboWriter uses .bin), E-BOOT-023 (bootable SD image with headers)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-013

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Generate a TurboWriter image and diff headers vs sdcard.work.img.

**Tags:** boot, turbowriter, sd-card, tooling

---

## CL-BOOT-REC-014: APP.bin Offset Differs From TurboWriter Default

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E1

**Statement:** The observed APP.bin offset at 0x100000 differs from TurboWriter's default execute-image start (sector 544).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-BOOT-011 (APP at 0x100000), E-BOOT-025 (TurboWriter default sector 544)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-014

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Compare a TurboWriter-generated image to the device SD image for offset differences.

**Tags:** boot, app.bin, turbowriter, layout

---

## CL-BOOT-REC-015: APP.bin is a Proprietary Resource Container

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** APP.bin appears to be a proprietary resource container loaded into RAM by the bootloader.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-BOOT-028 (mixed binary/string content), E-BOOT-029 (resource container)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-BOOT-016

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Identify container headers or index tables inside APP.bin.

**Tags:** boot, app.bin, container

---

## CL-BOOT-REC-016: Firmware Uses ARM/Thumb Mixed-Mode Code

**Status:** verified
**Confidence:** 0.95
**Authority:** E3-New

**Statement:** APP.bin contains a mix of ARM and Thumb instruction regions, with Thumb code in the 0x00210000-0x0021FFFF range.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** E-RKN-BOOT-001 (mixed-mode disassembly, Thumb region)
- **E1:** None
- **E3-Old:** None
- **E4:** None
- **E2:** E2-BOOT-015 (methodology + ARM/Thumb verification)

**Source Claims:**
- E3-New: CL-RKN-BOOT-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Expand ARM/Thumb mapping across full APP.bin to refine mode boundaries.

**Tags:** boot, arm, thumb, architecture

---

## CL-BOOT-REC-017: Upgrade Orchestrator and Message Handler Table

**Status:** supported
**Confidence:** 0.70
**Authority:** E3-Old

**Statement:** An upgrade orchestrator at 0x0020EAEC manages firmware updates and dispatches via a 287-entry message handler table at 0x003D3E00.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-BOOT-001 (orchestrator + dispatch table) [ghidra-v1]
- **E4:** None
- **E2:** E2-BOOT-015 (ghidra-v1 caution)

**Source Claims:**
- E3-Old: CL-RKO-BOOT-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Re-validate the handler table with post-optimization Ghidra settings.

**Tags:** boot, update, message-handler

---

## CL-BOOT-REC-018: Upgrade UI Handlers Identified in Dispatch Table

**Status:** supported
**Confidence:** 0.70
**Authority:** E3-Old

**Statement:** Multiple upgrade UI handlers (update_complete, no_upgrade_found, usb_error, upgrade_found_staging, file_open_failed) are mapped in the 0x003D3E00 dispatch table.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-BOOT-002 (upgrade UI handlers in dispatch table) [ghidra-v1]
- **E4:** None
- **E2:** E2-BOOT-015 (ghidra-v1 caution)

**Source Claims:**
- E3-Old: CL-RKO-BOOT-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Confirm handler entry points in the optimized Ghidra project.

**Tags:** boot, update, ui, dispatch-table

---

## CL-BOOT-REC-019: Additional Firmware Functions Need Verification

**Status:** hypothesis
**Confidence:** 0.55
**Authority:** E3-Old

**Statement:** Several medium-confidence functions (shared_notifier, flash_writer, queue_controller, queue_vtable_callback, hw_display_update) are likely involved in update/display handling but require confirmation.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-BOOT-003 (candidate functions and behavior) [ghidra-v1]
- **E4:** None
- **E2:** E2-BOOT-015 (ghidra-v1 caution)

**Source Claims:**
- E3-Old: CL-RKO-BOOT-003

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Validate these functions via dynamic traces or symbol-based call graph analysis.

**Tags:** boot, firmware, hypothesis

---

## CL-BOOT-REC-020: BOOT.bin Initializes CPU Modes and Stacks

**Status:** supported
**Confidence:** 0.70
**Authority:** E4

**Statement:** BOOT.bin uses CPSR writes and literal stack pointers to initialize per-mode stacks during early execution.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** None
- **E4:** E-OLD-BOOT-001 (CPSR + stack setup) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-BOOT-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Reconfirm CPSR stack initialization in current BOOT.bin disassembly.

**Tags:** boot, cpsr, stack

---

## CL-BOOT-REC-021: BOOT.bin Relocates Vectors Before Branching

**Status:** supported
**Confidence:** 0.70
**Authority:** E4

**Statement:** BOOT.bin copies vector data to a relocated address and branches to the new entry point.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** None
- **E4:** E-OLD-BOOT-002 (vector relocation routine) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-BOOT-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Identify the exact relocation target and confirm control transfer.

**Tags:** boot, vectors, relocation

---

## CL-BOOT-REC-022: BOOT.bin Issues Display Init Command IDs

**Status:** hypothesis
**Confidence:** 0.55
**Authority:** E4

**Statement:** BOOT.bin emits display init command IDs (0x2A..0xE0) consistent with DWIN/T5L protocols.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** None
- **E4:** E-OLD-BOOT-003 (display init constants) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-BOOT-003

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Match command IDs against a T5L display command table.

**Tags:** boot, display, init
