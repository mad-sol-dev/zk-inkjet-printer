# BOOT Claims (From E3-Old RE-KB Archive)

Propositional claims synthesized from historical RE-KB findings. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## Firmware Boot and Update

### ✅ Verified CL-RKO-BOOT-001: Firmware Upgrade Orchestrator and Message Handler Table
**Claim:** Upgrade orchestrator @ 0x0020EAEC (~1500 bytes, Thumb mode) manages firmware upgrade process by walking free-block list, accumulating memory statistics, binning block sizes, and dispatching logging callbacks. Message handler table @ 0x003D3E00 contains 287 entries in 12-byte format: handler_addr (4 bytes), string_addr (4 bytes), flag (4 bytes).

**Evidence:**
- E-RKO-BOOT-001: Upgrade orchestrator function (~1500 bytes, Thumb mode). Manages firmware upgrade: walks free-block list, accumulates memory stats, bins block sizes by bit-width, dispatches logging callbacks. Verified through call graph analysis and systematic disassembly.
- E-RKO-BOOT-001: Message handler table at 0x003D3E00. Array of 12-byte entries (287 total parsed). Structure: {uint32_t handler_addr; uint32_t string_addr; uint32_t flag;}. Verified through structure analysis.

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-BOOT-011, CL-BOOT-012
**Next Tests:** None listed

---

### ✅ Verified CL-RKO-BOOT-002: Upgrade UI Handler Functions (Queue Maintenance)
**Claim:** Five upgrade UI handler functions verified at 95%+ confidence via message dispatch table @ 0x003D3E00. Functions manage upgrade queue and UI display: update_complete @ 0x002C2048 (clamps queue depth, updates head pointer using 0x66666667 multiply pattern, 25KB stack frame), no_upgrade_found @ 0x002C47F0 (compacts 0x14-byte queue records with divide-by-10 pattern), usb_error @ 0x002C4524 (slides records in 8/16-byte strides), upgrade_found_staging @ 0x002C28D0 (chains 5 UI/formatter helpers), file_open_failed @ 0x002C3A94 (Thumb error wrapper). All handlers confirmed in dispatch table with Dutch localized strings. No direct xrefs found (indirect calls via dispatch table). Note: No checksum/CRC routines observed in upgrade path.

**Evidence:**
- E-RKO-BOOT-002: Clamps queue depth [base+0x144], updates head [base+0x14C] via 0x66666667 multiply pattern, forces status banner to VRAM pointer
- E-RKO-BOOT-002: Compacts 0x14-byte queue records, recomputes head pointer with divide-by-10 pattern, cleans queue when nothing matches
- E-RKO-BOOT-002: Chains through UI/formatter helpers (0x2C70F4, 0x2C7334, 0x2C6CA0, 0x2C61DC, 0x28ACF0). Stages metadata/UI only, no checksum/hash logic observed.
- E-RKO-BOOT-002: Dispatch table analysis (Ghidra): Message dispatch table @ 0x003D3E00 confirmed with 12-byte entries (handler_addr, string_addr, flag). All 5 upgrade handlers located: usb_error @ Entry 0 (flag=1, Dutch: 'U disk format error'), update_complete @ Entry 7 (flag=2, Dutch: 'De update is voltooid'), upgrade_found_staging @ Entry ~15 (flag=1), no_upgrade_found @ Entry ~38 (flag=1, Dutch: 'Geen upgradebestand gevonden'), file_open_failed @ Extended (flag=3, Dutch: 'Openen mislukt'). Disassembly confirms: update_complete has 25KB stack frame, no_upgrade_found uses divide-by-10 (0x66666667), usb_error slides records, upgrade_found_staging chains 5 helpers, file_open_failed calls 0x229D34. Cross-references: 0 direct xrefs (indirect calls via dispatch table confirmed). Confidence increased from 85-90% to 95%+ with dispatch table evidence.

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-BOOT-011
**Next Tests:** None listed

---

### 🔬 Hypothesis CL-RKO-BOOT-003: Additional Firmware Functions Requiring Verification
**Claim:** Medium-confidence functions now have stronger evidence: shared_notifier @ 0x002302EC (display/update notifier with layout + raster copy), flash_writer @ 0x002BFC34 (packs/stores RGB565 value in global, 40 callsites), queue_controller @ 0x00244F8C (large queue/allocator with many dispatch/alloc calls), queue_vtable_callback @ 0x00208592/0x002081b4 (state-driven comparator: cases 0/1/2 string sort, 3/4 region-A sort on 0x218-0x21d, 5/6 region-B sort on 0x221-0x226, 7 overlap/order on 0x228/0x22c), hw_display_update @ 0x00230E04 (programs display/BLT registers @0xB100D000, waits for idle then kicks start). Remaining gap: tie queue state values to concrete message types/enums; optional RAM/trace to finalize.

**Evidence:**
- E-RKO-BOOT-003: Likely display message processor (85% confidence). Allocates 0x200-byte buffer, calls text/layout helpers, updates status flags. Invoked by multiple message handlers.
- E-RKO-BOOT-003: Likely flash writer (80% confidence). Only called when validator @ 0x002BFDDC returns non-zero. Needs guard condition verification.
- E-RKO-BOOT-003: Hypothesis (60% confidence). Literal @ 0x002113CC resolves to this Thumb address. Needs RAM dump for runtime behavior verification.
- E-RKO-BOOT-003: shared_notifier callgraph: 2 inbound callers (0x002c2098, 0x002c3554); allocates 0x200-byte stack buffer, copies strings, calls layout helpers (0x0022714c), image alloc (0x0020c798) and raster copy (0x0020ddbc) before returning; consistent with display/update notifier role.
- E-RKO-BOOT-003: flash_writer @0x002BFC34 actually writes 24-bit color value into global struct (RGB565 packing) and returns previous value; 18 instr, no outbound calls, 40 inbound callsites incl. update_copy_or_flash.
- E-RKO-BOOT-003: queue_controller @0x00244F8C (actually starts at 0x244cd4 per decomp) is a large queue/allocator managing messages; 635 instr, 40 outbound calls to alloc/copy/dispatch helpers (0x20c798, 0x20dcac, 0x3467c, 0x33178, etc.), consistent with upgrade/UI queue management.
- E-RKO-BOOT-003: hw_display_update @0x00230E04 programs a register block (likely BLT/VPOST): waits on bit0 idle, sets bit11, writes color and stride/coords, sets start bit; inbound caller at 0x002590a8.
- E-RKO-BOOT-003: hw_display_update MMIO base: DAT_00230f34 = 0xB100D000 (display/BLT base), confirming register writes target VPOST/BitBLT block.
- E-RKO-BOOT-003: queue_vtable_callback @0x00208592 (actually function at 0x002081b4) is a comparator/controller for queued items: heavy branching on state byte @+0x251, compares ranges at offsets 0x228/0x22c, calls compare helpers (0x07f5c, 0x08088, 0x09570) and queue ops (0x06490, 0x07c14).
- E-RKO-BOOT-003: queue comparator cases: state byte @+0x251 selects comparator—cases 0/1/2 use string compare (0x09570); cases 3/4 use region-A compare (0x07f5c on packed fields @0x218-0x21d); cases 5/6 use region-B compare (0x08088 on packed fields @0x221-0x226); case 7 compares 0x228/0x22c with borrow logic (overlap/order check).

**Status:** 🔬 Hypothesis
**Cross-Reference:** None noted
**Next Tests:** Analyze call-sites for shared_notifier; Verify guard condition for flash_writer; Obtain RAM dump for runtime verification; Identify peripheral type for hw_display_update

---

### ⚠️ Supported CL-RKO-BOOT-004: APP.bin load mechanism and size constraints
**Claim:** BOOT enables the MMU with a 1 MB section table at TTBR=0x00004000. The table identity-maps VA 0x00000000–0x7FF00000 (2 GB) with section descriptors 0xDF2/0xDFE and aliases VA 0x80000000–0x83F00000 back to low memory (wrap). Domain register is set to 0x40000000 and control register enables MMU+I-cache. Therefore VA 0x03000000 is mapped 1:1 to PA 0x03000000; the loader assumes physical RAM of at least ~48 MB. APP.bin is copied there by the BOOT flow (in APP update logic) with no checksum. Practical size limit is the RAM remaining above 0x03000000; if DDR is 64 MB, headroom is ~16 MB minus runtime stacks/heaps, so APP can be safely grown well beyond current ~2.6 MB.

**Evidence:**
- E-RKO-BOOT-004: Boot updater copies APP from 3:/ to dest 0x03000000 via FUN_0006ccf8
- E-RKO-BOOT-004: File copy routine allocates 0x1000 buffer, reads file, writes to dest, checks bytes-read == file size; no checksum

**Status:** ⚠️ Supported
**Cross-Reference:** Potential overlap with CL-BOOT-008, CL-BOOT-016
**Next Tests:** Trace BOOT.bin caller after copy to find actual branch/jump to APP entry; Confirm actual DDR size (via MMIO or about-screen correction) to tighten max APP.bin size estimate; Check runtime heap/stack allocation to refine usable space above 0x03000000

---

### ✅ Verified CL-RKO-BOOT-005: SD Card Raw Binary Storage Layout and Firmware Update Workflow
**Claim:** Firmware binaries are stored at RAW sector offsets (BOOT @ 0x200, APP @ 0x100000) and updated via dedicated RAW write path bypassing FatFS. Update workflow: FAT staging (3:/ → 0:/) followed by RAW sector writes using FUN_00032500→FUN_00094584. NO checksums or cryptographic validation - only basic size checks.

**Evidence:**
- E-RKO-BOOT-005: NANO-BOOT.bin located at raw offset 0x200 (LBA 1). Header: 'A5 5A 42 57 00 00 70 00 00 31 00 00 57 42 5A A5' (ZBWp1WBZ signature). Size: 12,736 bytes (0x31C0) - exact match with TestDisk deleted entry. ARM code starts at 0x220 with CP15 coprocessor configuration and branch instructions.
- E-RKO-BOOT-005: NANO-APP.bin located at raw offset 0x100000 (1 MiB, LBA 0x800). ARM Interrupt Vector Table detected with Reset Vector 0xEA000014 and IRQ handlers 0xE59FF018. Size: 2,576,940 bytes (0x27522C) - exact match with TestDisk deleted entry. Contains ARM code and strings like 'Handwriting Resources', 'system', '0:/' indicating main application firmware.
- E-RKO-BOOT-005: TestDisk analysis shows deleted FAT directory entries: FAT16 Volume 2 @ LBA 0x12003F contains deleted entries for ZK-INKJET-NANO-BOOT.bin (12,736 bytes) and ZK-INKJET-NANO-APP.bin (2,576,940 bytes) marked with deletion flag 0xE5. Sizes exactly match raw binaries found at 0x200 and 0x100000. Current FAT only contains ZK-INKJET-UI-QVGA.bin (460,800 bytes) as active file.

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-STORAGE-004, CL-BOOT-011
**Next Tests:** None listed

---
