# STORAGE Evidence (E2 Tier: Sessions)

**Source:** research/sessions/*.md (chronological research logs)
**Tier:** E2 (navigation/context layer, unique session-level evidence)
**Note:** E2 tier captures technical deep-dives and analysis narratives not present in E1/E3 tiers.

---

## SD Card Write Mechanisms

### E2-STORAGE-012: RAW SD Sector Write Chain Discovery
- **Session ID:** S-012 (2025-12-15)
- **File:** sessions/2025-12-15_raw-write-chain-discovery.md
- **Type:** Technical analysis narrative
- **Summary:** Deep-dive investigation into SD card raw sector write mechanism used for firmware updates. Traced complete write chain from high-level firmware update functions through SD card driver to raw sector write operations. Critical for understanding how BOOT.bin and APP.bin are written to SD card during firmware upgrades.
- **Key Evidence:**
  - Write chain discovered: update_copy_or_flash (entry) → sd_write_wrapper → sd_write_blocks (0x00294584)
  - Raw sector writes bypass FAT filesystem layer - direct LBA (Logical Block Address) access
  - BOOT.bin written to raw sectors (likely sectors 0-N)
  - APP.bin written to raw sectors (offset determined by size constraints)
  - Update workflow: (1) Hold-key boot trigger → (2) maybe_update_from_udisk scans USB "MINI" volume → (3) memcmp filename match → (4) Raw sector write via sd_write_blocks
  - No checksums or signatures validated - trust by filename only
  - SD card layout: Volume 0 (MINI, FAT16, 64MB USB-exposed) + Volume 3 (internal storage, ~3GB) + Raw sectors (firmware)
- **Outcome:** Complete firmware update write chain mapped, security implications documented
- **Research Value:** Explains low-level firmware update mechanism, shows why firmware can be modified without signature checks
- **Cross-Reference:** CL-STORAGE-004 (SD card layout), CL-BOOT-011 (firmware update workflow), CL-RKO-BOOT-* (E3-Old update mechanism)
- **Security Implications:** No cryptographic verification enables firmware modification attacks via USB
- **Tags:** storage, sd-card, firmware-update, raw-write, security, boot-chain
- **Created:** 2025-12-15
- **Evidence Tier:** E2 (technical deep-dive narrative)

---

## Integration Notes

**E2-STORAGE Evidence Type:** Technical analysis narratives that document:
1. Low-level firmware update mechanisms
2. Write chain call graphs
3. Security implications of implementation choices

**Relationship to Other Tiers:**
- **E1 Tier:** E2-STORAGE-012 deep-dive contextualizes CL-STORAGE-004 and CL-STORAGE-006
- **E3-Old:** Complements CL-RKO-BOOT-023 (SD card raw binary layout) with write chain details
- **E3-New:** Provides technical foundation for future firmware modification claims

**Security Note:** E2-STORAGE-012 documents lack of signature verification in firmware update process - critical for understanding attack surface and modification feasibility.

---

*Evidence file created: 2026-01-04*
*E2 Tier: Technical deep-dive and security analysis*
