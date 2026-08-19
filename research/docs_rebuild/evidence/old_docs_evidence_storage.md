# STORAGE Evidence (Old Docs)

Extracted evidence from research/old_docs/ (E4 tier). Format: Content (1-3 lines) + Source + Date + Type + Provenance + Tags.

---

### E-OLD-STORAGE-001: Hardcoded Update Filenames On 3:/
- **Content:** Firmware enumerates update filenames on volume 3:/ including BOOT, APP, UI, UI-QVGA, and legacy TINY/PUNY boot names.
- **Source:** old_docs/update_file_rules.md#Enumerated-.bin-strings
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** None
- **Tags:** update, filenames, sd, 3:/

### E-OLD-STORAGE-002: Literal Pool And memcmp Loops For Update Matching
- **Content:** Literal table at VA 0x0037E820 feeds memcmp loops at 0x0025A930/0x0025A990/0x0025A9F0 to match update filenames.
- **Source:** old_docs/update_file_rules.md#Literal-tables-and-compare-loops
- **Date:** 2025-11-03
- **Type:** ANALYSIS
- **Provenance:** None
- **Tags:** update, memcmp, literal-pool, matching

### E-OLD-STORAGE-003: Update Match Success/Failure Handlers
- **Content:** Successful matches feed handler 0x002C28D0 (upgrade-found) while failures dispatch handler 0x002C47F0 (no upgrade found).
- **Source:** old_docs/update_file_rules.md#Handler-linkages
- **Date:** 2025-11-03
- **Type:** ANALYSIS
- **Provenance:** None
- **Tags:** update, handlers, ui

### E-OLD-STORAGE-004: Update Files Only On 3:/ Root
- **Content:** Firmware searches only volume 3:/ root for update binaries; 0:/ is reserved for fonts/resources.
- **Source:** old_docs/update_file_rules.md#Practical-rule
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** None
- **Tags:** update, filesystem, 3:/, 0:/

### E-OLD-STORAGE-005: No CRC/Checksum Routines Found
- **Content:** Static analysis reports no checksum/CRC routines in APP/BOOT update path; validator compares status bytes only.
- **Source:** old_docs/update_file_rules.md#Integrity-checks-what-we-looked-for
- **Date:** 2025-11-03
- **Type:** ANALYSIS
- **Provenance:** None
- **Tags:** update, validation, checksum, crc

### E-OLD-STORAGE-006: U-Disk Resource Bulk Update
- **Content:** `udisk_bulk_asset_update` copies `0:/ZK-INKJET-RES-HW.zkml` and related assets into internal flash via `update_copy_or_flash`.
- **Source:** old_docs/analysis_traceability.md#Resource-File-Usage
- **Date:** 2025-11-05
- **Type:** FINDING
- **Provenance:** None
- **Tags:** storage, resources, udisk, zkml
- **Note:** [ghidra-v1]
