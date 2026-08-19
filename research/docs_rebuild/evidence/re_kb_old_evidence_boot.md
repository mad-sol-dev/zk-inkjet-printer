# BOOT Evidence (E3-Old RE-KB Archive)

**Source:** research/findings/re_kb_archive/findings/*.json (31 findings from historical RE-KB)
**Tier:** E3-Old (structured findings from earlier analysis sessions)
**Note:** These findings predate Ghidra optimization (37k→1.3k functions). Ghidra-based evidence should be marked [ghidra-v1].

---

## Firmware Boot and Update

### E-RKO-BOOT-001: Firmware Upgrade Orchestrator and Message Handler Table
- **RE-KB ID:** finding-0009
- **Status:** verified
- **Type:** behavior
- **Summary:** Upgrade orchestrator @ 0x0020EAEC (~1500 bytes, Thumb mode) manages firmware upgrade process by walking free-block list, accumulating memory statistics, binning block sizes, and dispatching logging callbacks. Message handler table @ 0x003D3E00 contains 287 entries in 12-byte format: handler_addr (4 bytes), string_addr (4 bytes), flag (4 bytes).
- **Evidence:**
  - E1: Upgrade orchestrator function (~1500 bytes, Thumb mode). Manages firmware upgrade: walks free-block list, accumulates memory stats, bins block sizes by bit-width, dispatches logging callbacks. Verified through call graph analysis and systematic disassembly.; source_type=ghidra; function_address=0x20eaec; function_name=upgrade_orchestrator; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Message handler table at 0x003D3E00. Array of 12-byte entries (287 total parsed). Structure: {uint32_t handler_addr; uint32_t string_addr; uint32_t flag;}. Verified through structure analysis.; source_type=ghidra; function_address=0x3d3e00; function_name=message_handler_table; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
- **Tags:** upgrade, message-handler, functions, verified
- **Confidence:** None
- **Component:** None
- **Created:** 2025-11-27T00:14:39.774507Z
- **Updated:** 2025-12-02T03:05:54.308322Z

### E-RKO-BOOT-002: Upgrade UI Handler Functions (Queue Maintenance)
- **RE-KB ID:** finding-0010
- **Status:** verified
- **Type:** behavior
- **Summary:** Five upgrade UI handler functions verified at 95%+ confidence via message dispatch table @ 0x003D3E00. Functions manage upgrade queue and UI display: update_complete @ 0x002C2048 (clamps queue depth, updates head pointer using 0x66666667 multiply pattern, 25KB stack frame), no_upgrade_found @ 0x002C47F0 (compacts 0x14-byte queue records with divide-by-10 pattern), usb_error @ 0x002C4524 (slides records in 8/16-byte strides), upgrade_found_staging @ 0x002C28D0 (chains 5 UI/formatter helpers), file_open_failed @ 0x002C3A94 (Thumb error wrapper). All handlers confirmed in dispatch table with Dutch localized strings. No direct xrefs found (indirect calls via dispatch table). Note: No checksum/CRC routines observed in upgrade path.
- **Evidence:**
  - E1: Clamps queue depth [base+0x144], updates head [base+0x14C] via 0x66666667 multiply pattern, forces status banner to VRAM pointer; source_type=ghidra; function_address=0x2c2048; function_name=update_complete; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Compacts 0x14-byte queue records, recomputes head pointer with divide-by-10 pattern, cleans queue when nothing matches; source_type=ghidra; function_address=0x2c47f0; function_name=no_upgrade_found; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E3: Chains through UI/formatter helpers (0x2C70F4, 0x2C7334, 0x2C6CA0, 0x2C61DC, 0x28ACF0). Stages metadata/UI only, no checksum/hash logic observed.; source_type=ghidra; function_address=0x2c28d0; function_name=upgrade_found_staging; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E4: Dispatch table analysis (Ghidra): Message dispatch table @ 0x003D3E00 confirmed with 12-byte entries (handler_addr, string_addr, flag). All 5 upgrade handlers located: usb_error @ Entry 0 (flag=1, Dutch: 'U disk format error'), update_complete @ Entry 7 (flag=2, Dutch: 'De update is voltooid'), upgrade_found_staging @ Entry ~15 (flag=1), no_upgrade_found @ Entry ~38 (flag=1, Dutch: 'Geen upgradebestand gevonden'), file_open_failed @ Extended (flag=3, Dutch: 'Openen mislukt'). Disassembly confirms: update_complete has 25KB stack frame, no_upgrade_found uses divide-by-10 (0x66666667), usb_error slides records, upgrade_found_staging chains 5 helpers, file_open_failed calls 0x229D34. Cross-references: 0 direct xrefs (indirect calls via dispatch table confirmed). Confidence increased from 85-90% to 95%+ with dispatch table evidence.; source_type=other [ghidra-v1]
- **Tags:** upgrade, ui, queue, verified, dispatch-table
- **Confidence:** None
- **Component:** None
- **Created:** 2025-11-27T00:15:15.176921Z
- **Updated:** 2025-12-02T03:06:03.218323Z

### E-RKO-BOOT-003: Additional Firmware Functions Requiring Verification
- **RE-KB ID:** finding-0011
- **Status:** in_progress
- **Type:** hypothesis
- **Summary:** Medium-confidence functions now have stronger evidence: shared_notifier @ 0x002302EC (display/update notifier with layout + raster copy), flash_writer @ 0x002BFC34 (packs/stores RGB565 value in global, 40 callsites), queue_controller @ 0x00244F8C (large queue/allocator with many dispatch/alloc calls), queue_vtable_callback @ 0x00208592/0x002081b4 (state-driven comparator: cases 0/1/2 string sort, 3/4 region-A sort on 0x218-0x21d, 5/6 region-B sort on 0x221-0x226, 7 overlap/order on 0x228/0x22c), hw_display_update @ 0x00230E04 (programs display/BLT registers @0xB100D000, waits for idle then kicks start). Remaining gap: tie queue state values to concrete message types/enums; optional RAM/trace to finalize.
- **Evidence:**
  - E1: Likely display message processor (85% confidence). Allocates 0x200-byte buffer, calls text/layout helpers, updates status flags. Invoked by multiple message handlers.; source_type=ghidra; function_address=0x2302ec; function_name=shared_notifier; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: Likely flash writer (80% confidence). Only called when validator @ 0x002BFDDC returns non-zero. Needs guard condition verification.; source_type=ghidra; function_address=0x2bfc34; function_name=flash_writer; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E3: Hypothesis (60% confidence). Literal @ 0x002113CC resolves to this Thumb address. Needs RAM dump for runtime behavior verification.; source_type=ghidra; function_address=0x208592; function_name=queue_vtable_callback; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E4: shared_notifier callgraph: 2 inbound callers (0x002c2098, 0x002c3554); allocates 0x200-byte stack buffer, copies strings, calls layout helpers (0x0022714c), image alloc (0x0020c798) and raster copy (0x0020ddbc) before returning; consistent with display/update notifier role.; source_type=ghidra; function_address=0x2302ec; function_name=shared_notifier; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E5: flash_writer @0x002BFC34 actually writes 24-bit color value into global struct (RGB565 packing) and returns previous value; 18 instr, no outbound calls, 40 inbound callsites incl. update_copy_or_flash.; source_type=ghidra; function_address=0x2bfc34; function_name=FUN_002bfc34; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E6: queue_controller @0x00244F8C (actually starts at 0x244cd4 per decomp) is a large queue/allocator managing messages; 635 instr, 40 outbound calls to alloc/copy/dispatch helpers (0x20c798, 0x20dcac, 0x3467c, 0x33178, etc.), consistent with upgrade/UI queue management.; source_type=ghidra; function_address=0x244f8c; function_name=queue_controller; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E7: hw_display_update @0x00230E04 programs a register block (likely BLT/VPOST): waits on bit0 idle, sets bit11, writes color and stride/coords, sets start bit; inbound caller at 0x002590a8.; source_type=ghidra; function_address=0x230e04; function_name=FUN_00230e04; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E8: hw_display_update MMIO base: DAT_00230f34 = 0xB100D000 (display/BLT base), confirming register writes target VPOST/BitBLT block.; source_type=ghidra; function_address=0x230e04; function_name=FUN_00230e04; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E9: queue_vtable_callback @0x00208592 (actually function at 0x002081b4) is a comparator/controller for queued items: heavy branching on state byte @+0x251, compares ranges at offsets 0x228/0x22c, calls compare helpers (0x07f5c, 0x08088, 0x09570) and queue ops (0x06490, 0x07c14).; source_type=ghidra; function_address=0x208592; function_name=queue_vtable_callback; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E10: queue comparator cases: state byte @+0x251 selects comparator—cases 0/1/2 use string compare (0x09570); cases 3/4 use region-A compare (0x07f5c on packed fields @0x218-0x21d); cases 5/6 use region-B compare (0x08088 on packed fields @0x221-0x226); case 7 compares 0x228/0x22c with borrow logic (overlap/order check).; source_type=ghidra; function_address=0x2081b4; function_name=queue_vtable_callback; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
- **Tags:** functions, hypothesis, needs-verification, medium-confidence
- **Confidence:** 0.9
- **Component:** firmware
- **Created:** 2025-11-27T00:15:15.329971Z
- **Updated:** 2025-12-02T03:06:10.592069Z

### E-RKO-BOOT-004: APP.bin load mechanism and size constraints
- **RE-KB ID:** finding-0021
- **Status:** in_progress
- **Type:** behavior
- **Summary:** BOOT enables the MMU with a 1 MB section table at TTBR=0x00004000. The table identity-maps VA 0x00000000–0x7FF00000 (2 GB) with section descriptors 0xDF2/0xDFE and aliases VA 0x80000000–0x83F00000 back to low memory (wrap). Domain register is set to 0x40000000 and control register enables MMU+I-cache. Therefore VA 0x03000000 is mapped 1:1 to PA 0x03000000; the loader assumes physical RAM of at least ~48 MB. APP.bin is copied there by the BOOT flow (in APP update logic) with no checksum. Practical size limit is the RAM remaining above 0x03000000; if DDR is 64 MB, headroom is ~16 MB minus runtime stacks/heaps, so APP can be safely grown well beyond current ~2.6 MB.
- **Evidence:**
  - E1: Boot updater copies APP from 3:/ to dest 0x03000000 via FUN_0006ccf8; source_type=ghidra; function_address=0x6887c; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: File copy routine allocates 0x1000 buffer, reads file, writes to dest, checks bytes-read == file size; no checksum; source_type=ghidra; function_address=0x6ccf8; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
- **Tags:** boot, filesystem, firmware, loader, app.bin, size-limit
- **Confidence:** None
- **Component:** storage
- **Created:** 2025-12-02T15:18:41.427414Z
- **Updated:** 2025-12-02T15:50:39.573781Z

### E-RKO-BOOT-005: SD Card Raw Binary Storage Layout and Firmware Update Workflow
- **RE-KB ID:** finding-0023
- **Status:** verified
- **Type:** behavior
- **Summary:** Firmware binaries are stored at RAW sector offsets (BOOT @ 0x200, APP @ 0x100000) and updated via dedicated RAW write path bypassing FatFS. Update workflow: FAT staging (3:/ → 0:/) followed by RAW sector writes using FUN_00032500→FUN_00094584. NO checksums or cryptographic validation - only basic size checks.
- **Evidence:**
  - E1: NANO-BOOT.bin located at raw offset 0x200 (LBA 1). Header: 'A5 5A 42 57 00 00 70 00 00 31 00 00 57 42 5A A5' (ZBWp1WBZ signature). Size: 12,736 bytes (0x31C0) - exact match with TestDisk deleted entry. ARM code starts at 0x220 with CP15 coprocessor configuration and branch instructions.; source_type=other [ghidra-v1]
  - E2: NANO-APP.bin located at raw offset 0x100000 (1 MiB, LBA 0x800). ARM Interrupt Vector Table detected with Reset Vector 0xEA000014 and IRQ handlers 0xE59FF018. Size: 2,576,940 bytes (0x27522C) - exact match with TestDisk deleted entry. Contains ARM code and strings like 'Handwriting Resources', 'system', '0:/' indicating main application firmware.; source_type=other [ghidra-v1]
  - E3: TestDisk analysis shows deleted FAT directory entries: FAT16 Volume 2 @ LBA 0x12003F contains deleted entries for ZK-INKJET-NANO-BOOT.bin (12,736 bytes) and ZK-INKJET-NANO-APP.bin (2,576,940 bytes) marked with deletion flag 0xE5. Sizes exactly match raw binaries found at 0x200 and 0x100000. Current FAT only contains ZK-INKJET-UI-QVGA.bin (460,800 bytes) as active file.; source_type=other [ghidra-v1]
- **Tags:** sd-card, storage, firmware, boot, raw-binary, update-workflow, hypothesis
- **Confidence:** 1.0
- **Component:** storage
- **Created:** 2025-12-15T00:18:03.039777Z
- **Updated:** 2025-12-15T19:57:59.040762Z

