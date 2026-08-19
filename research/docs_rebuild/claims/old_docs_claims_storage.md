# STORAGE Claims (Old Docs)

Propositional claims synthesized from old_docs (E4 tier).

---

## CL-OLD-STORAGE-001: Update Filenames Are Hardcoded On 3:/
- **Status:** supported
- **Confidence:** 0.80
- **Statement:** Firmware update logic scans the 3:/ root for a fixed list of update filenames (BOOT/APP/UI/UI-QVGA and legacy names).
- **Evidence:**
  - E4: E-OLD-STORAGE-001 (hardcoded filename list)
  - E4: E-OLD-STORAGE-004 (3:/ only, 0:/ reserved for resources)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Verify filename list against live update flow on hardware.
- **Tags:** storage, update, filenames, 3:/
- **Cross-Reference:** E1 CL-BOOT-011 (partial overlap), E3-Old CL-RKO-STORAGE-001 (partial overlap)

## CL-OLD-STORAGE-002: Update Filename Matching Uses Literal Pool + memcmp Loops
- **Status:** supported
- **Confidence:** 0.75
- **Statement:** Update matching uses a literal pool at VA 0x0037E820 and memcmp loops at 0x0025A930/0x0025A990/0x0025A9F0, branching to upgrade-found or not-found handlers.
- **Evidence:**
  - E4: E-OLD-STORAGE-002 (literal pool + memcmp loops)
  - E4: E-OLD-STORAGE-003 (handler linkage)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Trace the matcher in Ghidra and confirm pointer pool entries at runtime.
- **Tags:** storage, update, memcmp, handlers
- **Cross-Reference:** E3-Old CL-RKO-STORAGE-001 (partial overlap)

## CL-OLD-STORAGE-003: No CRC/Checksum Gate In Update Path (Old Docs)
- **Status:** hypothesis
- **Confidence:** 0.55
- **Statement:** Static analysis reported no CRC/checksum routines in the APP/BOOT update path; validator checks status bytes only.
- **Evidence:**
  - E4: E-OLD-STORAGE-005 (no CRC/checksum routines found)
- **Counter-Evidence:** Documentation later flags a CRC/size-guard contradiction in the same update path.
- **Contradictions:** old_docs/analysis/documentation_contradictions_map.md (update validation conflict)
- **Revisions:** None
- **Next Test:** Re-evaluate validator function at 0x002BFDDC in current binaries for CRC logic.
- **Tags:** storage, update, checksum, hypothesis
- **Cross-Reference:** E3-Old CL-RKO-STORAGE-002 (partial overlap)

## CL-OLD-STORAGE-004: U-Disk Resource Bulk Update Copies ZKML
- **Status:** supported
- **Confidence:** 0.75
- **Statement:** `udisk_bulk_asset_update` copies `0:/ZK-INKJET-RES-HW.zkml` and related resources into internal flash using `update_copy_or_flash`.
- **Evidence:**
  - E4: E-OLD-STORAGE-006 (resource bulk update trace)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Trace the function in current APP.bin to confirm copy destinations and size checks.
- **Tags:** storage, resources, zkml, udisk
- **Cross-Reference:** E3-Old CL-RKO-STORAGE-001 (partial overlap)
