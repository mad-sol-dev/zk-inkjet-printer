# old_docs Evidence Catalog (E4 Tier)

**Source:** research/old_docs/ (25 technical documentation files, Oct-Nov 2025)
**Extraction Date:** 2026-01-04
**Tier:** E4 (pre-claims structured documentation)

## Summary
- **Total Files Processed:** 25 (excluding 23 archive files)
- **Subsystems:** USB, BOOT, STORAGE, SOC, HARDWARE, HP45, DISPLAY, MMIO, TOOL
- **Evidence Files:** 9 (`old_docs_evidence_*.md`)
- **Claims Files:** 9 (`old_docs_claims_*.md`)
- **Total Evidence Entries:** 42
- **Total Claims:** 34

## Subsystem Breakdown
| Subsystem | Evidence Entries | Claims | Status Distribution |
|-----------|------------------|--------|---------------------|
| USB | 3 | 2 | {NV=1, NS=1, NH=0} |
| BOOT | 4 | 4 | {NV=0, NS=3, NH=1} |
| STORAGE | 6 | 4 | {NV=0, NS=3, NH=1} |
| SOC | 5 | 4 | {NV=2, NS=1, NH=1} |
| HARDWARE | 8 | 6 | {NV=2, NS=4, NH=0} |
| MMIO | 7 | 5 | {NV=3, NS=1, NH=1} |
| HP45 | 2 | 2 | {NV=0, NS=2, NH=0} |
| DISPLAY | 3 | 3 | {NV=1, NS=2, NH=0} |
| TOOL | 4 | 4 | {NV=0, NS=4, NH=0} |

## Key Findings by Subsystem
- **SOC:** Old docs assert N32903K5DN identification via USB descriptors and CP15 fingerprints; SDRAM absence is flagged but conflicts with later evidence.
- **MMIO:** Verified GCR_BA (0xB0000000), doorbell block (0xB800C000), and display controller base (0xB100D000) with concrete access patterns.
- **HARDWARE:** GPB[2-5] never configured in firmware; UART0 lines are wired to printhead driver; JTAG TCK shares backlight PWM.
- **DISPLAY:** Display wired to SPI0 pins; backlight on PWM0; firmware uses display controller MMIO for updates.
- **STORAGE/UPDATE:** Update filenames are hardcoded on 3:/ with memcmp-based matching; no CRC found in static update path (flagged as contradictory).
- **HP45:** Printhead drivers reuse GPC LVDATA bus and multiple GPA/GPD control lines.
- **TOOL:** MCP workflow defines tool usage and address conventions; legacy UI decode remains artifact-prone.

## Cross-Tier Integration
- **Exact matches to E3-Old:** SOC (CL-RKO-SOC-002), MMIO (CL-RKO-MMIO-001..004), HARDWARE (CL-RKO-HARDWARE-001..003) map directly to E4 claims.
- **Partial overlaps with E1:** USB descriptor naming (CL-USB-003), display SPI/backlight wiring (CL-HARDWARE-005/006/014), update file scanning (CL-BOOT-011).
- **Contradictions flagged:** SoC RAM (K5DN no SDRAM vs E1 DDR MCP) and update validation (no CRC vs CRC/size-guard language). See `research/old_docs/analysis/documentation_contradictions_map.md`.
- **Unique E4 additions:** Detailed pinout conflicts (UART0 blocked, JTAG/backlight share) and explicit update matcher offsets.

## Evidence Quality Notes
- **[ghidra-v1] Tagging:** 15 entries marked (pre-optimization analysis from Nov 2025).
- **Provenance:** Many findings tie back to `sessions/session-2025-11-03-soc-identification.md` and subsequent Nov 2025 tool runs.
- **Relationship to E1:** E4 supports several E1 hardware and USB claims but diverges on SDRAM assumptions.
- **Relationship to E3-Old:** Strong overlap; E4 mostly captures the same pre-optimization evidence set in narrative form.

## Next Steps
- Phase 2C-3: Reconcile E4 with E1/E2/E3 (resolve overlaps/contradictions)
- Update REKB_MAPPING.md with E4 tier
