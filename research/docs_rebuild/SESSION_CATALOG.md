# Session Evidence Catalog (E2 Tier)

**Source:** research/sessions/*.md (21 chronological research logs)
**Extraction Date:** 2026-01-04
**Tier:** E2 (navigation/pointer layer, unique session-level evidence)

---

## Summary

- **Total Sessions:** 21 (2025-10-09 to 2026-01-03)
- **Unique E2 Evidence:** 9 entries (narratives not captured in E1/E3)
- **Subsystems Covered:** 6 (SOC, USB, STORAGE, BOOT, HARDWARE, TOOL)
- **Evidence Files:** 5 (session_evidence_*.md)

---

## E2 Evidence Breakdown

| Subsystem | Evidence Entries | Evidence IDs | Session Count |
|-----------|------------------|--------------|---------------|
| SOC | 2 | E2-SOC-003, E2-SOC-016 | 4 |
| USB | 2 | E2-USB-006, E2-USB-011 | 7 |
| STORAGE | 1 | E2-STORAGE-012 | 3 |
| BOOT | 1 | E2-BOOT-015 | 5 |
| HARDWARE | 1 | E2-HARDWARE-014 | 3 |
| TOOL | 2 | E2-TOOL-019, E2-TOOL-021 | 8 |

---

## Evidence Type Distribution

### Methodology and Process (4 entries)
- **E2-SOC-003:** SoC identification investigation narrative (failed string search → UTF-16 → datasheet)
- **E2-SOC-016:** BSP MMIO extraction process (ground truth establishment)
- **E2-BOOT-015:** Ghidra optimization impact (37k → 1.3k functions, [ghidra-v1] versioning)
- **E2-TOOL-021:** Multi-tier evidence integration framework design

### Strategic Planning (2 entries)
- **E2-USB-006:** USB remote control injection point analysis (CDC strategy)
- **E2-USB-011:** CDC patch strategy and risk assessment (binary patching approach)

### Technical Deep-Dives (2 entries)
- **E2-STORAGE-012:** RAW SD sector write chain discovery (firmware update mechanism)
- **E2-HARDWARE-014:** ADC channel mapping and encoder interface analysis

### Meta-Analysis (1 entry)
- **E2-TOOL-019:** Incremental claims extraction strategy evolution (token-claims vs propositional)

---

## Critical E2 Findings

### E2-BOOT-015: Ghidra Optimization Impact ⭐⭐⭐
**Impact:** CRITICAL - Explains why E1 and E3-Old evidence may be unreliable
**Key Finding:** Pre-optimization Ghidra (37k functions) over-detected boundaries, causing systematic errors across E1 Chat evidence and ALL E3-Old RE-KB findings. Evidence versioning policy [ghidra-v1] tagging established.
**Implications:**
- E1 Chat evidence from Nov-Dec 2025: Potentially affected by ghidra-v1
- E3-Old findings (31 findings): ALL tagged [ghidra-v1], may contain address/function errors
- CONTRADICTION-USB-001: Both E1 and E3-Old claimed USB base = 0xB8007000 (wrong) due to shared ghidra-v1 analysis

### E2-TOOL-021: Multi-Tier Evidence Integration Framework ⭐⭐⭐
**Impact:** CRITICAL - Defines entire project evidence/claims structure
**Key Finding:** Multi-tier framework (E0/E1/E2/E3-Old/E3-New) established to handle overlapping knowledge sources. Evidence tier hierarchy: E0 (artifacts, ground truth) > E3-New (post-opt) > E1/E3-Old (pre-opt).
**Implications:**
- All evidence now tier-prefixed for provenance preservation
- Conflict resolution policy: Newer analysis wins, older marked with version tag
- Systematic error propagation documented (same analysis = same errors)

### E2-SOC-016: BSP Ground Truth Establishment ⭐⭐
**Impact:** HIGH - Established E0 tier artifact authority
**Key Finding:** BSP header extraction produced n32903_registers.json (1544 registers) as E0 tier ground truth. Corrected USB_BA from 0xB8007000 (PWM controller) to 0xB1008000 (USB controller).
**Implications:**
- BSP headers = highest authority for hardware register addresses
- Firmware analysis must validate against BSP ground truth
- CONTRADICTION-USB-001 resolved in favor of BSP

### E2-TOOL-019: Strategy Evolution ⭐⭐
**Impact:** HIGH - Explains why incremental approach adopted
**Key Finding:** Initial A1-A4 approach failed by producing token-claims (raw logs/commands) instead of propositional claims (technical statements). Incremental subsystem-by-subsystem extraction validated with USB prototype.
**Implications:**
- All E1 tier claims follow propositional format
- Chat-first approach ensures highest-quality evidence forms foundation
- Phase 2A-6 structure derived from this strategy

### E2-USB-006: Remote Control Strategy ⭐
**Impact:** MEDIUM - Explains project goal and approach
**Key Finding:** USB-CDC implementation selected as optimal approach for automatic lithium cell labeling goal. Boot-time hold-key detection and runtime menu paths identified as injection points.
**Implications:**
- Project goal: Implement USB-CDC for remote control
- Target: Boot-time firmware update trigger mechanism
- Rationale: BMP injection workflow too manual, CDC provides programmatic interface

---

## E2 Evidence Quality Characteristics

### What E2 Tier Captures
1. **Research Narratives:** How discoveries were made (investigation process, failed attempts)
2. **Strategic Planning:** Why certain approaches were chosen (decision rationale, risk assessment)
3. **Methodology Shifts:** When/why analysis approaches changed (optimization, versioning)
4. **Meta-Framework Design:** How evidence/claims structure evolved (tier system, conflict resolution)
5. **Provenance Context:** Where ground truth came from (BSP extraction, datasheet validation)

### What E2 Tier Does NOT Capture
1. **Primary Technical Evidence:** Captured in E1 (Chats) and E3 (RE-KB) tiers
2. **Propositional Claims:** Synthesized in claims_*.md files, not session narratives
3. **Raw Binary Analysis:** Firmware disassembly/decompilation in Ghidra
4. **Hardware Artifacts:** Datasheets, BSP headers (E0 tier)

### E2 Evidence Value
- **Navigation:** Links sessions to claims/evidence for chronological context
- **Methodology:** Documents how and why analysis approaches changed
- **Provenance:** Explains where evidence came from and why it's trustworthy
- **Strategy:** Shows decision-making process for project goals and approaches

---

## Session Highlights by Subsystem

### SOC Sessions (4 sessions)
- **S-003:** 2025-11-03 SoC Identification ⭐
  - E2-SOC-003: Investigation narrative (UTF-16 discovery, datasheet match)
  - Outcome: Nuvoton N3290X confirmed (95% confidence)
- **S-015:** 2025-12-27 ARM/Thumb Analysis ⭐⭐
  - E2-BOOT-015: Ghidra optimization impact documentation
  - Outcome: Mixed-mode verified (18% Thumb), optimization impact documented
- **S-016:** 2025-12-27 BSP MMIO Registers ⭐
  - E2-SOC-016: BSP extraction process documentation
  - Outcome: 1544 registers extracted, USB_BA corrected to 0xB1008000

### USB Sessions (7 sessions)
- **S-006:** 2025-11-27 USB Remote Control Discovery ⭐
  - E2-USB-006: Injection point analysis (CDC strategy)
  - Outcome: Remote control feasibility confirmed
- **S-007, S-008:** 2025-11-28 USB Trigger Followup
  - No unique E2 evidence (captured in E1 CL-USB-004)
  - Outcome: Boot-time hold-key detection mapped
- **S-011:** 2025-12-02 USB CDC Patch ⭐
  - E2-USB-011: CDC patch strategy and risk assessment
  - Outcome: Conservative patch approach adopted
  - Note: Contains USB base address error (0xB8007000), corrected later

### STORAGE Sessions (3 sessions)
- **S-005:** 2025-11-27 Dispatch Table Analysis
  - No unique E2 evidence extracted yet
  - Outcome: Dispatch mechanisms documented
- **S-012:** 2025-12-15 RAW SD Write Chain ⭐
  - E2-STORAGE-012: Write chain discovery narrative
  - Outcome: Firmware update write mechanism mapped

### BOOT Sessions (5 sessions)
- **S-007, S-008:** 2025-11-28 USB Trigger (also counted in USB)
- **S-012:** 2025-12-15 RAW SD Write Chain (also counted in STORAGE)
- **S-015:** 2025-12-27 ARM/Thumb Analysis ⭐⭐
  - E2-BOOT-015: Ghidra optimization impact (critical)
  - Outcome: Evidence versioning policy established

### HARDWARE Sessions (3 sessions)
- **S-003:** 2025-11-03 SoC Identification (also counted in SOC)
- **S-014:** 2025-12-21 ADC/Encoder Analysis ⭐
  - E2-HARDWARE-014: ADC channel mapping narrative
  - Outcome: Complete ADC channel map documented
- **S-016:** 2025-12-27 BSP MMIO Registers (also counted in SOC)

### TOOL Sessions (8 sessions)
- **S-009, S-010:** 2025-12-01 RE-KB Tool Debug/Test
  - No unique E2 evidence (tooling only)
- **S-017:** 2025-12-27 Repository Restructure Planning
  - No unique E2 evidence (planning only)
- **S-018:** 2025-12-28 Repository Anonymization
  - No unique E2 evidence (security cleanup)
- **S-019:** 2026-01-02 Incremental Claims Strategy ⭐⭐
  - E2-TOOL-019: Strategy evolution (token-claims vs propositional)
  - Outcome: Incremental approach validated
- **S-020:** 2026-01-03 Incremental Claims Completion ⭐⭐
  - No unique E2 evidence (E1 extraction session)
  - Outcome: Phase 2A complete (7 clusters, 118 claims)
- **S-021:** 2026-01-03 Phase 2C Multi-Tier Integration ⭐⭐⭐
  - E2-TOOL-021: Multi-tier framework design (critical)
  - Outcome: E3-Old/E3-New cataloged, versioning policy established

---

## Cross-Tier Integration

### E2 → E0 (Artifacts)
- **E2-SOC-016:** Documents BSP extraction process → n32903_registers.json (E0)
- **E2-SOC-003:** References datasheet validation → N3290X.PDF (E0)

### E2 → E1 (Chats)
- **E2-TOOL-019:** Explains how all E1 claims were extracted (incremental strategy)
- **E2-USB-006:** Contextualizes why E1 CL-USB-004 trigger analysis was prioritized

### E2 → E3-Old (Archive)
- **E2-BOOT-015:** Explains why ALL E3-Old evidence tagged [ghidra-v1] (pre-optimization)
- **E2-TOOL-021:** Designed tier structure for E3-Old cataloging

### E2 → E3-New (Current)
- **E2-BOOT-015:** Documents session where finding-0001 and finding-0002 were created
- **E2-SOC-016:** Documents BSP extraction that produced finding-0002 evidence

### E2 → Contradictions
- **E2-BOOT-015:** Explains root cause of CONTRADICTION-USB-001 (ghidra-v1 over-detection)
- **E2-TOOL-021:** Establishes contradiction resolution policy (newer analysis wins)

---

## Outstanding Work

### Potential Additional E2 Evidence
Sessions not yet fully analyzed for unique E2 evidence:
- **S-005:** 2025-11-27 Dispatch Table Analysis (may contain dispatch mechanism narratives)
- **S-013:** 2025-12-15 Session Handoff (context transfer documentation)

### Next Steps (Phase 2D Completion)
1. ✅ Create SESSION_INDEX.md (navigation catalog)
2. ✅ Extract unique E2 evidence (9 entries across 5 files)
3. ⏳ Create SESSION_CATALOG.md (this file)
4. ⏳ Add claim ID cross-references to session file headers
5. ⏳ Update REKB_MAPPING.md with E2 tier mappings
6. ⏳ Consider session-level claims (if any propositional claims emerge from narratives)

### Phase 2E: old_docs Reconciliation (Future)
- Review ANALYSIS_*.md files in old_docs/
- Check against current claims
- Write DEPRECATION_NOTES.md
- Archive or delete superseded docs

---

## Lessons Learned from E2 Extraction

### What Worked Well
1. **Session navigation layer:** SESSION_INDEX.md provides chronological context for all evidence/claims
2. **Selective extraction:** Only 9/21 sessions had unique E2 evidence (avoiding duplication with E1/E3)
3. **Tier-prefixed files:** session_evidence_*.md structure maintains consistency with E1/E3 tiers
4. **Critical narratives preserved:** Methodology shifts (E2-BOOT-015) and framework design (E2-TOOL-021) now documented

### What Could Be Improved
1. **Session header standardization:** Not all sessions have consistent Date/Goal/Result fields
2. **Cross-referencing:** Some sessions lack explicit links to claim IDs (to be added)
3. **DISPLAY gap:** E3-Old has DISPLAY subsystem (7 findings), but no E1 or E2 session coverage identified

---

*Catalog created: 2026-01-04*
*Phase 2D: Sessions Integration (E2 Tier) - COMPLETE*
