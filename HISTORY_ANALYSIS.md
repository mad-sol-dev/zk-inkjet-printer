# HISTORY.md Modernization Analysis

**Date:** 2026-01-08  
**Purpose:** Compare current HISTORY.md against project evolution

---

## Current HISTORY.md Issues

### Outdated References:
- "The SoC was reported as marked \"DWIN M5,\" while the firmware contains the string \"W55FA93 USB Card Reader 1.00\" (CL-002, supported)." (Phase 1)
- "Firmware string extraction showed update file paths under 3:/ (CL-013, supported)..." (Phase 1)
- "A consolidated summary described USB VID/PID pairs, IBR boot behavior, SD layout, and update flow (CL-003, CL-004, CL-005, CL-006, supported)." (Phase 2)
- "Boot flow notes described BOOT.bin loading APP.bin to 0x03000000 with no CRC/size check (CL-007, CL-008, supported)." (Phase 2)
- "A patch at file offset 0x275140 was initially treated as a descriptor edit and caused a brick (CL-009, refuted)." (Phase 3)
- "Subsequent analysis identified string descriptors at VA 0x00475148 and config/interface data around 0x00475140 (CL-010, CL-011, supported)." (Phase 3)
- "Touch panel wiring was reported as using dedicated ADC_TP pins (CL-014, supported)." (Phase 4)
- "A low-memory mirror (LOW_MIRROR) was identified as a source of duplicate functions in Ghidra analysis (CL-012, supported)." (Phase 4)
- "USB descriptor patch location... (CL-009, refuted)... (CL-010, CL-011, supported)." (What we got wrong)
- "Runtime vs analysis base addresses... (CL-007 vs CL-012)." (What we got wrong)
- "SoC identity is supported as N32903U5DN/W55FA93 family (CL-001)..." (Current state)
- "USB/SD/update architecture is supported... (CL-003 through CL-008)." (Current state)
- "Descriptor region mapping is corrected and supported (CL-010, CL-011)." (Current state)

### Missing Information:
- Phase A completion (2026-01-07) and the verified SD image ground truth.
- Verified boot header structure (32-byte IBR header with 0xA5 [ZBW...WBZ] 0xA5 pattern).
- Verified FAT volume layout and offsets (three volumes at 0x04000000, 0x24007E00, 0x2A61BE00).
- Confirmation that Volume 3 "MINI" is empty and used as update input, not storage.
- Corrected update workflow (files placed on Volume 3, header prepended, raw offsets written).
- Repo evolution milestones from red-threads (MCP integration, re-kb findings expansion, BSP MMIO extraction, anonymization, etc.).
- Phase B focus items (mount mapping and USBD_BA usage).

### Incorrect/Outdated Facts:
- USB/SD/update architecture marked as merely "supported" now contradicts Phase A ground truth (boot offsets and FAT volumes are verified).
- Boot header description relies on old claim framing rather than the verified 32-byte IBR header structure.
- Volume 3 update path is still framed as a hint; Phase A verifies it as the USB "MINI" volume and update input.
- SD layout described as pending verification conflicts with verified volume offsets and contents.

---

## Key Milestones from red-threads-and-progression.md

- **2025-10-09:** SD boot medium confirmed; APP.bin treated as resource container; early UI decoding pipeline.
- **2025-11-03:** SoC confirmed as Nuvoton N3290X; USB strings identified; update path noted as lacking CRC.
- **2025-11-26:** MCP integration validated; re-kb setup fixed; first finding created.
- **2025-11-27:** Dispatch table verified; update UI handlers validated; USB file processing strings identified.
- **2025-11-28:** USB MSC device-mode correction; boot-time hold-key update trigger documented; MINI volume exposure clarified.
- **2025-12-01:** HP45 hardware chain documented into findings 0014-0018; re-kb workflows stabilized.
- **2025-12-02:** CDC patch plan drafted; descriptor blob location and UDC base references enumerated.
- **2025-12-15:** RAW SD write chain confirmed; staging flow (3:/ -> 0:/ -> RAW) mapped; volume contradictions captured.
- **2025-12-21:** ADC base corrected to 0xB800E000; channel mapping verified.
- **2025-12-27:** ARM/Thumb mixed-mode confirmed; BSP MMIO register map extracted.
- **2025-12-28:** Repository anonymization and security cleanup; docs normalized for public sharing.

---

## Phase A Ground Truth (2026-01-07)

### Major Achievements:
- Boot header structure verified (32-byte IBR header at 0x200, 0xA5 [ZBW...WBZ] 0xA5 pattern).
- BOOT.bin and APP.bin raw offsets verified (0x200 and 0x100000).
- FAT volumes mapped and verified (3 volumes at 0x04000000, 0x24007E00, 0x2A61BE00).
- Volume 3 "MINI" located and verified as empty user update input.
- Update workflow structure documented (Volume 3 input, header prepend, raw write, delete).
- Confidence level: High (85% system understood).

### Corrections Made:
- Volume 3 location: unresolved → VERIFIED (0x2A61BE00).
- IBR signature: "ZBWp1WBZ" string framing → 0xA5 [ZBW...WBZ] 0xA5 (spaced pattern).
- Volume 3 role: firmware storage assumption → verified update input (empty during imaging).
- Firmware files in Volume 3: corrected to deleted files in Volume 2 (TestDisk recovery).

---

## Proposed New HISTORY.md Structure

### Suggested Timeline:

**2024-XX: Project Initiation**
- Motivation: automatic lithium cell labeling via USB-CDC.

**2024-XX: Hardware Analysis**
- PCB teardown and SoC identification path.
- Pin mapping and peripheral discovery.
- Datasheet collection (N32903 series, legacy W55FA93 strings).

**2024-XX: Boot Chain Discovery**
- IBR boot mechanism and BOOT.bin/APP.bin offsets identified.
- SD raw offset boot structure understood.

**2024-XX: USB Interface Analysis**
- MSC device-mode behavior documented; VID:PID 0416:0093.
- IBR-boot mode behavior recorded.

**2025-XX: Claims Reconciliation (Phase 1)**
- 189 claims processed; 152 verified/reconciled across 9 subsystems.

**2025-10 to 2025-12: Evidence Expansion**
- Dispatch table and update UI handlers verified.
- USB file processing paths (BMP/CSV/update) identified.
- Boot-time update trigger and MSC device-mode correction.
- HP45 hardware chain documented; ADC mapping verified.
- BSP MMIO register map extracted; ARM/Thumb mixed-mode confirmed.
- MCP + re-kb workflows stabilized; repository anonymized.

**2026-01-07: Phase A - SD Image Ground Truth**
- Boot chain verified (32-byte IBR header at 0x200; APP at 0x100000).
- Three FAT volumes identified and mapped; Volume 3 "MINI" verified at 0x2A61BE00.
- Update workflow structure established (Volume 3 input → raw write).
- Documentation reorganized for Phase B.

**Current Status:**
- System understanding: 85% complete.
- Confidence level: High.
- Next phase: Firmware analysis (Phase B) focused on mount mapping and USBD controller usage.

---

## Recommendations

### Keep:
- The phase-based narrative structure and "what we got wrong" section (useful for traceability).
- References to key correction events (descriptor offset brick, LOW_MIRROR discovery).

### Remove:
- CL-XX claim references and claim-status framing.
- Language implying boot/SD/update architecture is still only supported rather than verified.

### Add:
- Phase A completion and verified SD ground truth (boot header, offsets, FAT volumes).
- Milestones from red-threads (MCP integration, dispatch table validation, BSP MMIO extraction, anonymization).
- Project timeline anchors (2026-01-05 Phase 1 completion; 2026-01-07 Phase A completion).

### Restructure:
- Replace claim-based notes with evidence-based milestones and verified facts.
- Add a short "Current Status" section aligned with `research/README.md` and `research/system_understanding.md`.

---

## Notes for Human Review

- Exact 2024 initiation and hardware analysis dates are not explicitly recorded in the reviewed docs; confirm or leave as month/quarter placeholders.
- Decide how much internal tooling/process detail (MCP, re-kb workflow issues) is appropriate for a public-facing HISTORY.
- Confirm whether to keep the descriptor-brick event in a public timeline or move to internal notes.

---

## Draft Sections (Optional)

**Phase A Ground Truth (2026-01-07):**
Phase A established SD image ground truth: the IBR boot header is a 32-byte structure at offset 0x200 with a 0xA5 [ZBW...WBZ] 0xA5 pattern, BOOT.bin loads APP.bin from 0x100000 into 0x03000000, and three FAT volumes are present at verified offsets. The "MINI" volume at 0x2A61BE00 is empty during normal operation and serves as the user update input; update files are staged there, header-prepended, written to raw offsets, and then removed.
