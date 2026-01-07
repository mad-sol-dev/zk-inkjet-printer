# Repository Documentation Consistency Report

**Date:** 2026-01-07
**Scope:** Post-Phase A reorganization
**Perspective:** New repository visitor

---

## Executive Summary

The repository communicates a clear reverse-engineering goal and offers deep,
well-structured Phase A deliverables, but the entry points and navigation do
not yet reflect the post-Phase A reorganization. A newcomer can understand the
project intent quickly, yet must piece together the updated workflow by jumping
between several documents that are not linked from the root README.

The strongest content lives under `research/phase_a_sd_analysis/`, where the
Phase A results are documented with high rigor. However, the primary system
reference (`research/system_understanding.md`) and several root-level guidance
documents still reflect pre-Phase A assumptions and an older repository layout.
This creates visible contradictions (for example, Volume 3 location status and
BOOT.bin signature format) and yields a number of broken or stale references.

Overall, documentation depth is excellent, but newcomer accessibility suffers
from link rot, outdated structure maps, and scattered entry points. A small set
of targeted consistency updates would significantly improve trust and
navigability without changing the core content.

**Strengths:**
- Clear project intent and motivation in the root README.
- High-quality Phase A documentation with explicit corrections and evidence.
- Rich hardware context including a large photo gallery and pinout mapping.
- Research index (`research/README.md`) that acts as a solid internal table of contents.
- Safety warning about firmware update risk is prominent and actionable.
- Session logs are well organized and indexed for chronological review.
- Multiple perspectives provided (architecture, history, research notes).
- Strong emphasis on evidence and verification levels in Phase A materials.

**Concerns:**
- Root README quick-start references files and commands that do not exist.
- Core references still point to old directory layout (`docs/`, `data/`, `.re_kb/`).
- System understanding document is not updated with Phase A ground truth.
- CONTRIB and agent guidance contain conflicting technical details.
- Multiple missing or stale file references (claims timeline, workflow docs).
- `tools/` and `firmware/` lack local README indexes, reducing discoverability.
- Archive / rebuild content sits alongside current docs without clear labeling.
- Multiple phase naming schemes (Phase 1, Phase A, Phase B) are not unified.

**Priority Improvements:**
- Integrate Phase A corrections into `research/system_understanding.md`.
- Update root README quick start and navigation to point to current paths.
- Fix or remove broken links to missing files and deprecated directory names.
- Align CONTRIBUTING / AGENTS / CLAUDE structure maps with current repo layout.
- Add brief README indexes in `firmware/` and `tools/`.

---

## 1. Entry Point Analysis (README.md)

### Strengths:
- Clearly states the device class and reverse-engineering objective.
- Provides a concise status table for key subsystems.
- Includes a safety warning about update integrity risks.
- Immediately shows a representative hardware image.
- Presents a compact repository layout overview.

### Gaps:
- No explicit "Start here" link to `research/README.md` or `ARCHITECTURE.md`.
- Quick start references missing files and commands.
- Repository layout section does not identify the main research index file.
- No mention of Phase A completion or where to find Phase A results.
- No link to CONTRIBUTING or HISTORY, which a newcomer may expect.
- MCP tooling and RE-KB usage are not surfaced from the landing page.

### Specific Findings:
- `README.md:32` links to `tools/mcp_bridge`, which is missing.
- `README.md:52` references `requirements-dev.txt`, which is missing.
- `README.md:58` references `make test`, but no `Makefile` exists in root.
- `README.md:61` references `tools/generate_verification_summary.py`, which is missing.
- `README.md:35-40` lists directories but does not link to `research/README.md` or `ARCHITECTURE.md`.
- `README.md:6-23` status table is strong, but it is not aligned with Phase A corrections noted elsewhere.

---

## 2. Navigation & Structure

### Current Organization:
```
.
|-- README.md
|-- ARCHITECTURE.md
|-- HISTORY.md
|-- CONTRIBUTING.md
|-- CLAUDE.md
|-- AGENTS.md
|-- MIGRATION_PLAN.md
|-- LICENSE
|-- SENSITIVE_DATA_SCAN_REPORT.md
|-- hardware/
|   |-- README.md
|   |-- N32903U5DN_Pinout.md
|   `-- images/
|-- firmware/
|   |-- update_system.md
|   |-- memory_map.md
|   |-- bin/
|   `-- image/
|-- research/
|   |-- README.md
|   |-- system_understanding.md
|   |-- phase_a_sd_analysis/
|   |-- sessions/
|   |-- findings/
|   `-- docs_rebuild/
|-- tools/
|   `-- scripts/
|-- vendor/
|-- mcp/
`-- ghidra_projects/
```

### Discoverability Assessment:
- Hardware info: Moderate - `hardware/README.md` and photo index exist, but root README lacks a direct link to hardware details.
- Research findings: Moderate - strong `research/README.md`, but not linked from the root entry point.
- Technical docs: Moderate - `ARCHITECTURE.md` and `HISTORY.md` exist, but are not referenced from README.
- Contribution guidance: Moderate to Difficult - `CONTRIBUTING.md` exists but references missing paths.
- Tooling/MCP usage: Difficult - detailed in `CLAUDE.md`, but not surfaced from README or research index.

### Directory Purpose Clarity:
- `hardware/`: Clear purpose; has README and image index.
- `firmware/`: Purpose implied, but lacks an index and mixes binaries with docs.
- `research/`: Clear purpose, with a good README, but contains legacy material.
- `tools/`: Purpose unclear beyond scripts; no README.
- `vendor/`: Contains PDFs and BSP files, but not described in root README.
- `mcp/`: Example configs only; not described in root README or ARCHITECTURE.
- `ghidra_projects/`: Present but not documented for newcomers.

### Recommendations:
- Add a short "Start here" block in root README linking to `research/README.md`, `ARCHITECTURE.md`, and `HISTORY.md`.
- Add `firmware/README.md` to index `memory_map.md`, `update_system.md`, and the binary layout.
- Add `tools/README.md` to describe `tools/scripts/` and any MCP-related tools.
- Label `research/docs_rebuild/` as archive or work-in-progress to reduce ambiguity.
- Add a one-line summary in `hardware/README.md` pointing to the photo gallery.
- Add a simple overview for `vendor/` so readers know where datasheets live.

---

## 3. Consistency Check

### Contradictions Found:
- `research/system_understanding.md:77-81` describes a contiguous "ZBWp1WBZ" signature, while `research/phase_a_sd_analysis/phase_a_final_summary.md:31-38` documents the spaced `0xA5 [ZBW...WBZ] 0xA5` pattern.
- `research/system_understanding.md:254-255` and `research/system_understanding.md:296-298` still mark Volume 3 location as unresolved, while `research/phase_a_sd_analysis/phase_a_final_summary.md:33-38` and `research/README.md:43-54` mark Volume 3 as verified.
- `research/system_understanding.md:114-116` lists SD image verification as pending, while Phase A docs provide completed results.
- `CONTRIBUTING.md:23` lists `0xB8007000` as the USB Device Controller base, while `research/system_understanding.md:133` lists `0xB1008000` and `hardware/README.md:20` assigns `0xB8007000` to PWM.
- `ARCHITECTURE.md:21` references `.re_kb/findings/` in repo root, but the RE-KB is nested under `research/findings/.re_kb/`.
- `AGENTS.md:19-35` documents a legacy `data/` + `docs/` layout not present in the current tree.

### Outdated References:
- `HISTORY.md:3` and `HISTORY.md:38` reference `research/CLAIMS.md` and `research/MASTER_TIMELINE.md`, which do not exist.
- `hardware/README.md:12` references `docs/vendor/N3290x_Design_Guide_A1.pdf`, but vendor PDFs are under `vendor/`.
- `hardware/README.md:38` references `docs/findings/finding-0012.json`, which is not present.
- `CONTRIBUTING.md:19` references `docs/guide/operations.md`, which is missing.
- `CONTRIBUTING.md:16` references `tools/generate_verification_summary.py`, which is missing.
- `AGENTS.md:38-58` references `.re_kb/`, `docs/`, and `data/` paths that no longer exist at root.
- `CLAUDE.md:22-56` documents `firmware/APP.bin`, `firmware/BOOT.bin`, and `vendor/datasheets/`, which are not present as described.
- `MIGRATION_PLAN.md:12-43` still references `firmware/app/` and `firmware/boot/` as if they exist.
- `MIGRATION_PLAN.md:81-116` references `docs/vendor/`, which no longer exists.
- `MIGRATION_PLAN.md:127-133` claims `tools/mcp_bridge/` and `tools/legacy/` exist, but they are not in the tree.
- `research/analysis_traceability.md:3` references `research/sd_fat_volumes.txt`, but the file is under `research/phase_a_sd_analysis/artifacts/`.
- `research/phase_a_sd_analysis/methods_phase_a_sd_analysis.md:67` references `research/sd_fat_volumes.txt`, but the file is under `research/phase_a_sd_analysis/artifacts/`.
- `README.md:52-61` references `requirements-dev.txt`, `make test`, and `tools/generate_verification_summary.py`, which are missing.

### Terminology Consistency:
- Phase naming is split across documents: "Phase 1" (reconciliation), "Phase A" (SD analysis), and "Phase B" (firmware analysis) without a unified glossary.
- Boot component naming varies: `BOOT.bin` vs `ZK-INKJET-NANO-BOOT.bin` vs `NANO-BOOT.bin` without a cross-reference note.
- USB controller naming alternates between USB_BA and USBD_BA; the base address is consistent in most docs but not in CONTRIBUTING.
- "MINI" volume is described as unknown in older docs and verified in Phase A docs, with no explicit consolidation note.
- BSP references appear both as "N3290x Design Guide" and "N3290X.PDF" with no single canonical name.

---

## 4. Research Documentation (research/)

### Structure Assessment:
- `research/README.md`: Strong navigation hub with Phase A summary and next steps. Clear status and timeline.
- `research/system_understanding.md`: Comprehensive but now out of sync with Phase A corrections and verification.
- `research/phase_a_sd_analysis/`: Well organized with summary, methods, and detailed topic files.
- `research/phase_a_sd_analysis/system_understanding_updates_phase_a.md`: Clear update plan, but not yet applied to the main doc.
- `research/phase_a_sd_analysis/methods_phase_a_sd_analysis.md`: Captures methodology and hash verification; includes an outdated artifact path reference.
- `research/phase_a_sd_analysis/volume_identification_corrected.md`: Detailed ground truth for FAT volumes and contents.
- `research/phase_a_sd_analysis/boot_header_structure.md`: Detailed boot header breakdown and signature analysis.
- `research/findings/`: Contains RE-KB at `research/findings/.re_kb/`, which is not surfaced in the root README.
- `research/docs_rebuild/`: Large, legacy or rebuild content with its own internal links; not labeled as archive.
- `research/sessions/`: Detailed session logs with an index, but only linked from `research/README.md`.

### Navigation Quality:
- Phase A results are accessible if the visitor enters `research/README.md`.
- The main system narrative (`research/system_understanding.md`) is not clearly marked as out-of-date relative to Phase A.
- `docs_rebuild/` increases cognitive load because it is adjacent to current research without a status note.
- The RE-KB location is buried in nested directories and not explained outside `CLAUDE.md` and `AGENTS.md`.

### Phase Progression Clarity:
- The progression from Phase 1 (reconciliation) to Phase A (SD analysis) is described in `research/README.md`, but not connected to `HISTORY.md` or `README.md`.
- Phase B is clearly marked as pending, but entry points to Phase B expectations are fragmented across files.
- `HISTORY.md` focuses on earlier phases but does not mention Phase A completion.

---

## 5. Missing Elements

### Critical Gaps:
- A "Start here" section in root README pointing to research and architecture.
- A `firmware/README.md` describing file purpose and entry points.
- A `tools/README.md` explaining available scripts and how they relate to MCP work.
- A consistent description of the RE-KB location and activation steps in public docs.
- A reconciled system understanding doc that reflects Phase A results.

### Nice-to-Have:
- A short glossary of abbreviations (IBR, BSP, MMIO, CDC, MSC, FAT, LBA).
- A short FAQ or newcomer roadmap ("If you only read one file, read X").
- A small "current status" badge or changelog link at root.
- A CONTRIBUTING refresh that points to current paths and commands.
- A clear separation label for archive or legacy materials.
- A list of recommended tools and versions beyond Python and Ghidra.

---

## 6. Technical Accessibility

### Jargon & Abbreviations:
- Common terms (IBR, BSP, MMIO, CDC, MSC, FAT, LBA, UDC, SPI) appear in multiple files without consistent definitions.
- `research/system_understanding.md` and `firmware/update_system.md` are highly technical and assume reverse-engineering familiarity.
- Root README is accessible, but does not define key abbreviations used in the status table.
- Phase A docs provide strong evidence but not a short glossary for newcomers.

### Abbreviations Observed (not consistently defined):
- SoC
- IBR
- BSP
- MMIO
- CDC
- MSC
- FAT
- LBA
- UDC
- SPI
- ADC
- PWM
- GPIO
- AIC
- SD
- USB

### Target Audience Clarity:
- The documentation is written primarily for experienced RE practitioners and embedded engineers.
- Newcomers can follow the story but may struggle to connect the narrative to actual repo paths.
- MCP-focused guidance lives in `CLAUDE.md` and `AGENTS.md`, which is not signposted for general visitors.

---

## 7. Link Validation Report

### Broken Links:
- Total broken links found by scan: 29
- README.md:32: tools/mcp_bridge
- research/docs_rebuild/Chats/ANALYSIS_chronicle-and-common-thread.md:370: images/ghidraMCPd.png
- research/docs_rebuild/old_docs/README.md:21: sessions/session-2025-11-03-soc-identification.md
- research/docs_rebuild/old_docs/README.md:22: sessions/session-2025-11-03-soc-identification.md
- research/docs_rebuild/old_docs/README.md:23: sessions/session-2025-11-03-soc-identification.md
- research/docs_rebuild/old_docs/README.md:24: sessions/session-2025-11-03-soc-identification.md
- research/docs_rebuild/old_docs/README.md:33: sessions/
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:14: sessions/session-2025-11-03-soc-identification.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:15: sessions/session-2025-11-03-soc-identification.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:16: sessions/session-2025-11-03-soc-identification.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:17: sessions/session-2025-11-03-soc-identification.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:32: sessions/
- research/docs_rebuild/old_docs/archive/CLEANUP_PLAN_legacy.md:10: guide/
- research/docs_rebuild/old_docs/archive/CLEANUP_PLAN_legacy.md:11: archive/README.md
- research/docs_rebuild/old_docs/archive/PROJECT_STATUS_legacy.md:34: docs/status_dashboard.md
- research/docs_rebuild/old_docs/archive/README.md:13: documentation-20251009.md
- research/docs_rebuild/old_docs/archive/README.md:18: 2025-10-10-session-notes.md
- research/docs_rebuild/old_docs/archive/old-structure/session_status.md:10: archive/2025-10-10-session-notes.md
- research/docs_rebuild/old_docs/guide/orientation.md:18: ../sessions/
- research/docs_rebuild/old_docs/guide/orientation.md:32: ../../tools/generate_verification_summary.py
- research/docs_rebuild/old_docs/guide/orientation.md:41: ../sessions/
- research/docs_rebuild/old_docs/guide/orientation.md:42: ../../scripts/
- research/docs_rebuild/old_docs/guide/research_notebook.md:16: ../sessions/
- research/findings/.re_kb/README.md:162: ../../docs/re_kb_workflow.md
- research/findings/re_kb_archive/README.md:162: ../../docs/re_kb_workflow.md
- research/sessions/.backup_pre_anonymization/2025-12-27_arm-thumb-analysis-mmio-extraction.md:22: ../findings/.re_kb/findings/finding-0001.json
- research/sessions/.backup_pre_anonymization/2025-12-27_arm-thumb-analysis-mmio-extraction.md:44: ../findings/.re_kb/findings/finding-0002.json
- research/sessions/.backup_pre_anonymization/2025-12-27_arm-thumb-analysis-mmio-extraction.md:177: ../findings/.re_kb/findings/finding-0001.json
- research/sessions/.backup_pre_anonymization/2025-12-27_arm-thumb-analysis-mmio-extraction.md:178: ../findings/.re_kb/findings/finding-0002.json
### Working Links:
- Total working links found by scan: 151
- README.md:4: hardware/images/processed/dp20_printer_front_display.jpg
- README.md:37: hardware/
- README.md:38: firmware/
- README.md:39: tools/
- README.md:40: research/
- hardware/README.md:27: N32903U5DN_Pinout.md
- hardware/images/index.md:6: thumbs/dp20_printer_front_display.jpg
- hardware/images/index.md:7: thumbs/dp20_printer_back.jpg
- hardware/images/index.md:8: thumbs/dp20_printer_label.jpg
- hardware/images/index.md:11: thumbs/dp20_mainboard_overview.jpg
- hardware/images/index.md:12: thumbs/dp20_mainboard_overview_2.jpg
- hardware/images/index.md:15: thumbs/dp20_mainboard_soc_sd_closeup_1.jpg
- hardware/images/index.md:16: thumbs/dp20_mainboard_soc_sd_closeup_2.jpg
- hardware/images/index.md:17: thumbs/dp20_mainboard_soc_sd_closeup_3.jpg
- hardware/images/index.md:18: thumbs/dp20_mainboard_soc_pins.jpg
- hardware/images/index.md:19: thumbs/dp20_mainboard_soc_oscillator.jpg
- hardware/images/index.md:20: thumbs/dp20_mainboard_soc_section_2.jpg
- hardware/images/index.md:23: thumbs/dp20_board_power_section.jpg
- hardware/images/index.md:24: thumbs/dp20_mainboard_power_connector.jpg
- hardware/images/index.md:25: thumbs/dp20_mainboard_sd_and_display_connectors.jpg
- hardware/images/index.md:26: thumbs/dp20_mainboard_driver_row.jpg
- hardware/images/index.md:29: thumbs/dp20_display_board_with_adapter.jpg
- hardware/images/index.md:30: thumbs/dp20_display_driver_ic.jpg
- hardware/images/index.md:31: thumbs/dp20_display_pogo_adapter.jpg
- hardware/images/index.md:34: thumbs/dp20_incremental_rotation_sensor.jpg
- hardware/images/index.md:37: thumbs/dp20_printer_google_results.jpg
- research/README.md:12: ./system_understanding.md
- research/README.md:15: ./phase_a_sd_analysis/SUMMARY.md
- research/README.md:16: ./phase_a_sd_analysis/phase_a_final_summary.md
- research/README.md:17: ./phase_a_sd_analysis/methods_phase_a_sd_analysis.md
- research/README.md:20: ./phase_a_sd_analysis/boot_locations_verified.md
- research/README.md:21: ./phase_a_sd_analysis/boot_header_structure.md
- research/README.md:22: ./phase_a_sd_analysis/volume_identification_corrected.md
- research/README.md:25: ./phase_a_sd_analysis/system_understanding_updates_phase_a.md
- research/README.md:31: ./reference/n32903_registers.json
- research/README.md:32: ./phase_a_sd_analysis/artifacts/
- research/README.md:61: ./phase_a_sd_analysis/SUMMARY.md
- research/README.md:62: ./phase_a_sd_analysis/phase_a_final_summary.md
- research/README.md:63: ./system_understanding.md
- research/README.md:66: ./phase_a_sd_analysis/boot_header_structure.md
- research/README.md:66: ./phase_a_sd_analysis/boot_locations_verified.md
- research/README.md:67: ./phase_a_sd_analysis/volume_identification_corrected.md
- research/README.md:68: ./phase_a_sd_analysis/methods_phase_a_sd_analysis.md
- research/README.md:71: ./phase_a_sd_analysis/system_understanding_updates_phase_a.md
- research/docs_rebuild/old_docs/README.md:10: guide/orientation.md
- research/docs_rebuild/old_docs/README.md:11: guide/operations.md
- research/docs_rebuild/old_docs/README.md:12: guide/research_notebook.md
- research/docs_rebuild/old_docs/README.md:21: findings/chip_identification.md
- research/docs_rebuild/old_docs/README.md:22: findings/firmware_functions.md
- research/docs_rebuild/old_docs/README.md:23: findings/gpio_configuration.md
- research/docs_rebuild/old_docs/README.md:24: findings/mmio_map.md
- research/docs_rebuild/old_docs/README.md:29: findings/
- research/docs_rebuild/old_docs/README.md:30: analysis/
- research/docs_rebuild/old_docs/README.md:31: methodology/
- research/docs_rebuild/old_docs/README.md:32: reference/
- research/docs_rebuild/old_docs/README.md:34: hardware/
- research/docs_rebuild/old_docs/README.md:35: archive/
- research/docs_rebuild/old_docs/README.md:41: VERIFICATION_STATUS.md
- research/docs_rebuild/old_docs/README.md:46: analysis_traceability.md
- research/docs_rebuild/old_docs/README.md:47: archive/firmware_mod_plan_legacy.md
- research/docs_rebuild/old_docs/README.md:48: uart_control_consolidated.md
- research/docs_rebuild/old_docs/README.md:49: vendor_resources.md
- research/docs_rebuild/old_docs/README.md:50: archive/README.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:7: findings/
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:14: findings/chip_identification.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:15: findings/firmware_functions.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:16: findings/gpio_configuration.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:17: findings/mmio_map.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:31: findings/
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:32: analysis_traceability.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:33: README.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:38: guide/operations.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:39: guide/research_notebook.md
- research/docs_rebuild/old_docs/VERIFICATION_STATUS.md:40: archive/README.md
- research/docs_rebuild/old_docs/archive/CLEANUP_PLAN_legacy.md:9: RESTRUCTURE_COMPLETE.md
- research/docs_rebuild/old_docs/archive/README.md:9: RESTRUCTURE_COMPLETE.md
- research/docs_rebuild/old_docs/archive/README.md:10: CLEANUP_PLAN_legacy.md
- research/docs_rebuild/old_docs/archive/README.md:11: documentation_reorg_proposal_legacy.md
- research/docs_rebuild/old_docs/archive/README.md:12: old-structure/
- research/docs_rebuild/old_docs/archive/README.md:14: PROJECT_STATUS_legacy.md
- research/docs_rebuild/old_docs/archive/README.md:19: aiderdesk-subagent-profiles.json
- research/docs_rebuild/old_docs/archive/README.md:20: jt-scan-batch-0-4.json
- research/docs_rebuild/old_docs/archive/README.md:20: jt-scan-subagent-test-results.json
- research/docs_rebuild/old_docs/archive/README.md:21: ghidra_headless_cli.md
- research/docs_rebuild/old_docs/archive/README.md:21: tools/ghidra_headless.sh
- research/docs_rebuild/old_docs/archive/README.md:22: uiqvga_bruteforce_notes.md
- research/docs_rebuild/old_docs/archive/README.md:26: N32903U5DN_K5DN_CheatCheet.docx
- research/docs_rebuild/old_docs/archive/README.md:38: ../guide/
- research/docs_rebuild/old_docs/archive/old-structure/README_NEW_STRUCTURE.md:3: ../README.md
- research/docs_rebuild/old_docs/archive/old-structure/analysis_traceability_FULL_ARCHIVE.md:3: ../README.md
- research/docs_rebuild/old_docs/archive/old-structure/documentation.md:3: ../README.md
- research/docs_rebuild/old_docs/archive/old-structure/session_status.md:3: ../README.md
- research/docs_rebuild/old_docs/archive/old-structure/session_status.md:8: status_dashboard.md
- research/docs_rebuild/old_docs/archive/old-structure/status_dashboard.md:3: ../README.md
- research/docs_rebuild/old_docs/archive/old-structure/storage_probe_notes.md:3: ../README.md
- research/docs_rebuild/old_docs/archive/old-structure/subagent-orchestration-guide.md:3: ../README.md
- research/docs_rebuild/old_docs/archive/old-structure/subagent-profiles-reverse-engineering.md:3: ../README.md
- research/docs_rebuild/old_docs/guide/operations.md:25: ../VERIFICATION_STATUS.md
- research/docs_rebuild/old_docs/guide/operations.md:26: ../analysis_traceability.md
- research/docs_rebuild/old_docs/guide/operations.md:75: ../findings/mmio_map.md
- research/docs_rebuild/old_docs/guide/operations.md:88: ../CONVENTIONS.md
- research/docs_rebuild/old_docs/guide/operations.md:89: ../vendor_resources.md
- research/docs_rebuild/old_docs/guide/operations.md:90: ../update_file_rules.md
- research/docs_rebuild/old_docs/guide/orientation.md:13: ../README.md
- research/docs_rebuild/old_docs/guide/orientation.md:19: ../VERIFICATION_STATUS.md
- research/docs_rebuild/old_docs/guide/orientation.md:25: operations.md
- research/docs_rebuild/old_docs/guide/orientation.md:26: research_notebook.md
- research/docs_rebuild/old_docs/guide/orientation.md:27: ../archive/README.md
- research/docs_rebuild/old_docs/guide/orientation.md:31: ../findings/
- research/docs_rebuild/old_docs/guide/orientation.md:43: ../CONVENTIONS.md
- research/docs_rebuild/old_docs/guide/research_notebook.md:9: ../findings/
- research/docs_rebuild/old_docs/guide/research_notebook.md:10: ../methodology/mcp_workflow.md
- research/docs_rebuild/old_docs/guide/research_notebook.md:11: ../analysis_traceability.md
- research/docs_rebuild/old_docs/guide/research_notebook.md:21: ../analysis/gpio_pins_analysis.md
- research/docs_rebuild/old_docs/guide/research_notebook.md:21: ../findings/chip_identification.md
- research/docs_rebuild/old_docs/guide/research_notebook.md:22: ../analysis/boot_analysis_methodology.md
- research/docs_rebuild/old_docs/guide/research_notebook.md:23: ../analysis/app_message_handlers.md
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:6: thumbs/dp20_printer_front_display.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:7: thumbs/dp20_printer_back.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:8: thumbs/dp20_printer_label.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:11: thumbs/dp20_mainboard_overview.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:12: thumbs/dp20_mainboard_overview_2.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:15: thumbs/dp20_mainboard_soc_sd_closeup_1.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:16: thumbs/dp20_mainboard_soc_sd_closeup_2.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:17: thumbs/dp20_mainboard_soc_sd_closeup_3.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:18: thumbs/dp20_mainboard_soc_pins.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:19: thumbs/dp20_mainboard_soc_oscillator.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:20: thumbs/dp20_mainboard_soc_section_2.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:23: thumbs/dp20_board_power_section.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:24: thumbs/dp20_mainboard_power_connector.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:25: thumbs/dp20_mainboard_sd_and_display_connectors.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:26: thumbs/dp20_mainboard_driver_row.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:29: thumbs/dp20_display_board_with_adapter.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:30: thumbs/dp20_display_driver_ic.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:31: thumbs/dp20_display_pogo_adapter.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:34: thumbs/dp20_incremental_rotation_sensor.jpg
- research/docs_rebuild/old_docs/hardware/zk-dp20/photos/index.md:37: thumbs/dp20_printer_google_results.jpg
- research/phase_a_sd_analysis/SUMMARY.md:53: ./phase_a_final_summary.md
- research/phase_a_sd_analysis/SUMMARY.md:55: ./methods_phase_a_sd_analysis.md
- research/sessions/.backup_pre_anonymization/2025-10-09_documentation-status-archive.md:3: README.md
- research/sessions/.backup_pre_anonymization/INDEX.md:4: README.md
- research/sessions/.backup_pre_anonymization/README.md:7: INDEX.md
- research/sessions/.backup_pre_anonymization/README.md:65: INDEX.md
- research/sessions/2025-10-09_documentation-status-archive.md:3: README.md
- research/sessions/2025-12-27_arm-thumb-analysis-mmio-extraction.md:22: ../findings/.re_kb/findings/finding-0001.json
- research/sessions/2025-12-27_arm-thumb-analysis-mmio-extraction.md:44: ../findings/.re_kb/findings/finding-0002.json
- research/sessions/2025-12-27_arm-thumb-analysis-mmio-extraction.md:177: ../findings/.re_kb/findings/finding-0001.json
- research/sessions/2025-12-27_arm-thumb-analysis-mmio-extraction.md:178: ../findings/.re_kb/findings/finding-0002.json
- research/sessions/INDEX.md:4: README.md
- research/sessions/README.md:7: INDEX.md
- research/sessions/README.md:105: INDEX.md
### Non-Link References to Missing Paths:
- `README.md:52-61` references missing `requirements-dev.txt` and `tools/generate_verification_summary.py` in code blocks.
- `CONTRIBUTING.md:19` references missing `docs/guide/operations.md` in inline code.
- `CONTRIBUTING.md:16` references missing `tools/generate_verification_summary.py` in inline code.
- `hardware/README.md:12` references missing `docs/vendor/N3290x_Design_Guide_A1.pdf` in inline code.
- `hardware/README.md:38` references missing `docs/findings/finding-0012.json` in inline code.
- `HISTORY.md:3` and `HISTORY.md:38` reference missing `research/CLAIMS.md` and `research/MASTER_TIMELINE.md` in inline code.
- `AGENTS.md:19-58` references missing `data/`, `docs/`, and `.re_kb/` directories.
- `CLAUDE.md:22-56` references `firmware/APP.bin`, `firmware/BOOT.bin`, and `vendor/datasheets/` paths that are not present.

### Image References:
- `README.md:4` image reference to `hardware/images/processed/dp20_printer_front_display.jpg` exists.
- `hardware/images/index.md:17` has a space between `]` and `(`, so the link does not render even though the file exists.
- `hardware/images/index.md:26` has a space between `]` and `(`, so the link does not render even though the file exists.
- All other thumbnail image references in `hardware/images/index.md` point to existing files.

---

## 8. Visitor Journey Scenarios

### Scenario 1: Hardware Engineer
"I want to understand the hardware architecture"
- Path: README -> hardware/ -> hardware/README.md -> hardware/images/index.md -> N32903U5DN_Pinout.md -> vendor/ datasheets.
- Friction points: datasheet path in `hardware/README.md` points to `docs/vendor/` which does not exist.
- Friction points: root README does not link directly to hardware README or pinout.
- Friction points: vendor PDFs are not indexed from hardware or root README.
- Friction points: no quick "hardware summary" section in root README.

### Scenario 2: Firmware Developer
"I want to see firmware analysis results"
- Path: README -> firmware/ -> update_system.md -> memory_map.md -> research/README.md -> phase_a_sd_analysis/.
- Friction points: no firmware README to explain the binary layout or what files to open first.
- Friction points: system understanding doc is out of sync with Phase A results.
- Friction points: quick start instructions reference missing files.
- Friction points: CONTRIBUTING and AGENTS mention paths that do not exist.

### Scenario 3: General Curious Developer
"I want to understand what this project achieved"
- Path: README -> research/README.md -> SUMMARY.md -> phase_a_final_summary.md -> HISTORY.md.
- Friction points: README does not link to research index, so this path is not obvious.
- Friction points: HISTORY.md references missing claim/timeline docs.
- Friction points: multiple "phase" labels are used without a simple glossary.
- Friction points: current achievements are not summarized outside research/README.

---

## 9. Priority Recommendations

### High Priority (Fix Now):
1. Update `research/system_understanding.md` with Phase A corrections from `research/phase_a_sd_analysis/system_understanding_updates_phase_a.md`.
2. Fix or remove broken links in root README and CONTRIBUTING quick-start sections.
3. Align USB controller base address references across CONTRIBUTING and system docs.
4. Replace legacy `docs/` and `data/` references in AGENTS/CLAUDE/CONTRIBUTING with current paths.
5. Clarify RE-KB location consistently across ARCHITECTURE, CLAUDE, and AGENTS.

### Medium Priority (Phase B):
6. Add `firmware/README.md` and `tools/README.md` with navigation pointers.
7. Add a short glossary of abbreviations and phase naming in `research/README.md` or root README.
8. Mark `research/docs_rebuild/` as archive or WIP to reduce confusion.
9. Add a short Phase A completion note to HISTORY or README to align status.

### Low Priority (Future):
10. Add a minimal newcomer guide or FAQ section for non-RE visitors.
11. Add a short "status dashboard" page linking to Phase A outcomes and Phase B goals.
12. Add a section listing supported tool versions and sample workflows.

---

## 10. Appendix: Files Reviewed
- README.md - Root entry point, status table, quick start, and safety warning.
- ARCHITECTURE.md - MCP workflow overview and toolchain description.
- HISTORY.md - Public history and claim references.
- CONTRIBUTING.md - Contribution guidance and update workflow notes.
- CLAUDE.md - Agent-oriented structure and MCP usage guidance.
- AGENTS.md - Agent guidelines and legacy repo layout.
- MIGRATION_PLAN.md - Legacy reorganization plan and status notes.
- hardware/README.md - Hardware summary and peripheral map.
- hardware/images/index.md - Photo gallery index.
- firmware/update_system.md - Update mechanism description.
- firmware/memory_map.md - Memory and MMIO map (verification status noted).
- research/README.md - Research index and Phase A navigation.
- research/system_understanding.md - Primary system narrative (pre-Phase A state).
- research/analysis_traceability.md - Traceability log reference.
- research/phase_a_sd_analysis/SUMMARY.md - Phase A quick summary.
- research/phase_a_sd_analysis/phase_a_final_summary.md - Phase A final summary and corrections.
- research/phase_a_sd_analysis/system_understanding_updates_phase_a.md - Pending updates for system understanding.
- research/phase_a_sd_analysis/boot_locations_verified.md - BOOT.bin location analysis and evidence.
- research/phase_a_sd_analysis/boot_header_structure.md - Boot header breakdown and signature analysis.
- research/phase_a_sd_analysis/volume_identification_corrected.md - FAT volume identification and contents.
- research/phase_a_sd_analysis/methods_phase_a_sd_analysis.md - Phase A methodology and hash verification.
- research/sessions/README.md - Session log purpose and indexing guidance.
---

**Report Status:** Complete
**Methodology:** Manual review from new visitor perspective plus automated internal link scan across all Markdown files.
**Limitations:** Did not validate binary contents or external URL availability; non-markdown references in code blocks and backticks were inspected manually only where clearly visible.
