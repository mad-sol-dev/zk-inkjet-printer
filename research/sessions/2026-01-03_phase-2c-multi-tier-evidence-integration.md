# Session Log: Phase 2C - Multi-Tier Evidence Integration

**Date:** 2026-01-03
**Duration:** ~3 hours
**Participants:** User, Claude Code (Sonnet 4.5), Codex (GPT-5.1)
**Phase:** Phase 2C (Multi-Tier Evidence Integration)

---

## Objective

After completing all 7 subsystem clusters (118 claims from E1 Chat tier), integrate multiple overlapping knowledge sources:
- **E3-Old Tier:** 31 historical RE-KB findings from old project
- **E3-New Tier:** 2 current RE-KB findings
- **E2 Tier:** ~47 session logs (future)
- **E? Tier:** old_docs legacy documentation (future)

**Goal:** Maintain provenance across knowledge tiers using tier-prefixed evidence/claims structure, enable systematic reconciliation.

---

## Execution Summary

### Phase 2C-1: E3-New RE-KB Mapping (2 findings)

**Discovery:** Started with mapping 2 current RE-KB findings to existing E1 claims.

**Key Files Created:**
- `research/REKB_MAPPING.md` - Initial E3-New to E1 mapping
- `research/CONTRADICTION-USB-001.md` - Critical USB base address conflict

**Critical Finding: USB Base Address Contradiction**
- **E1 Claim (CL-USB-010):** UDC base = 0xB8007000 (from E-USB-019, Chat 51, 2025-12-06)
- **E3 RE-KB (finding-0002):** BSP headers show USB_BA=0xB1008000, PWM_BA=0xB8007000
- **Resolution Attempt:** Codex used Ghidra MCP to search firmware for both addresses
- **Result:** 0 refs found for BOTH addresses in optimized Ghidra analysis!
- **Root Cause Hypothesis:** Ghidra optimization (37k → 1.3k functions) means old evidence is from pre-optimization analysis
- **Status:** ACTIVE - requires pattern search (MOV/MOVT, register offsets) to resolve

**Key Insight: Evidence Versioning Problem**
User identified that Ghidra analysis optimization invalidates older evidence. This led to the multi-tier evidence strategy.

---

### Strategy Pivot: Multi-Tier Evidence Structure

**Problem Statement:**
- Multiple knowledge sources need integration
- Ghidra optimization changed analysis (37k → 1.3k functions)
- Old Ghidra-based evidence potentially outdated
- Need to maintain historical provenance

**Solution: Tier-Prefixed Files**
```
evidence/
├── evidence_*.md              # E1 (Chats) - 216 entries ✅
├── re_kb_old_evidence_*.md    # E3-Old (31 findings) ← NEW
├── re_kb_evidence_*.md        # E3-New (2 findings) ← FUTURE
└── session_evidence_*.md      # E2 (Sessions) ← FUTURE

claims/
├── claims_*.md                # From E1 - 118 claims ✅
├── re_kb_old_claims_*.md      # From E3-Old ← NEW
└── re_kb_claims_*.md          # From E3-New ← FUTURE
```

**Evidence Versioning Policy:**
- Evidence entries are **snapshot-in-time** observations
- NOT auto-updating truth
- Mark old Ghidra refs with `[ghidra-v1]` tag
- New Ghidra searches create new evidence entries (not replacements)
- Conflicts resolved in Phase 4 (Contradiction Detection)

**STRATEGY Updated:** `research/STRATEGY_claims_incremental.md` updated with Phase 2C multi-tier approach.

---

### Phase 2C-2: E3-Old RE-KB Cataloging (31 findings)

**Discovery:** User identified 31 historical RE-KB findings in old project that need cataloging.

**Step 1: Archive Old RE-KB**
```bash
# Copied old .re_kb to current project for Codex access
cp -r ~/zk-inkjet-printer_old/.re_kb/* research/findings/re_kb_archive/
```

**Archive Contents:**
- 31 findings (finding-0001 through finding-0031)
- index.json with metadata
- n32903_registers.json (MMIO register map - bonus!)
- Full RE-KB schema and README

**Step 2: Codex Cataloging Task**

**Prompt Strategy:** Comprehensive Codex CLI prompt with:
- Full context (Phase 2A complete, multi-tier strategy)
- Clear input/output structure (8 subsystems)
- Evidence format template with [ghidra-v1] tagging
- Propositional claims synthesis requirements
- Status mapping rules (verified/supported/hypothesis)

**Codex Execution:**
- Read all 31 findings from archive
- Grouped by subsystem (USB, BOOT, STORAGE, SOC, HARDWARE, HP45, DISPLAY, MMIO)
- Generated 8 evidence files (123 total evidence entries)
- Generated 8 claims files (33 propositional claims)
- Created catalog summary document
- Identified cross-subsystem duplicates (finding-0023, finding-0006)
- Mapped all findings to potential E1 claim overlaps

**Output Quality:**
- ✅ All evidence entries have complete metadata (RE-KB ID, status, type, summary, tags, timestamps)
- ✅ All Ghidra-based evidence tagged [ghidra-v1]
- ✅ Propositional claims (no token-claims)
- ✅ Status correctly mapped (20 Verified, 10 Supported, 4 Hypothesis)
- ✅ Cross-references to E1 claims documented
- ✅ Next tests preserved from findings

---

## Files Created

### Configuration/Strategy (2 files)
1. `research/STRATEGY_claims_incremental.md` - **UPDATED**
   - Added Phase 2C: Multi-Tier Evidence Integration
   - Documented evidence versioning policy
   - Updated Phase 2C-1 (E3-New) and 2C-2 (E3-Old) checklists
   - Added lessons learned for multi-tier strategy

### Mapping/Contradiction (2 files)
2. `research/REKB_MAPPING.md` - **NEW**
   - E3-New findings (2) mapped to E1 claims
   - Partial overlap relationships documented
   - USB base address discrepancy identified

3. `research/CONTRADICTION-USB-001.md` - **NEW**
   - Critical: UDC base 0xB8007000 vs 0xB1008000
   - BSP shows PWM_BA=0xB8007000, USB_BA=0xB1008000
   - Ghidra search: 0 refs found for both (optimized analysis)
   - Status: ACTIVE, needs pattern search resolution

### E3-Old Evidence Files (8 files)
4. `research/evidence/re_kb_old_evidence_usb.md` - 3 findings, 19 evidence entries
5. `research/evidence/re_kb_old_evidence_boot.md` - 5 findings, 21 evidence entries
6. `research/evidence/re_kb_old_evidence_storage.md` - 2 findings, 7 evidence entries
7. `research/evidence/re_kb_old_evidence_soc.md` - 2 findings, 8 evidence entries
8. `research/evidence/re_kb_old_evidence_hardware.md` - 4 findings, 18 evidence entries
9. `research/evidence/re_kb_old_evidence_hp45.md` - 6 findings, 10 evidence entries
10. `research/evidence/re_kb_old_evidence_display.md` - 7 findings, 27 evidence entries
11. `research/evidence/re_kb_old_evidence_mmio.md` - 4 findings, 13 evidence entries

**Total:** 123 evidence entries from 31 findings

### E3-Old Claims Files (8 files)
12. `research/claims/re_kb_old_claims_usb.md` - 3 claims (1V, 2S)
13. `research/claims/re_kb_old_claims_boot.md` - 5 claims (3V, 1S, 1H)
14. `research/claims/re_kb_old_claims_storage.md` - 2 claims (1V, 1S)
15. `research/claims/re_kb_old_claims_soc.md` - 2 claims (2V)
16. `research/claims/re_kb_old_claims_hardware.md` - 4 claims (4V)
17. `research/claims/re_kb_old_claims_hp45.md` - 6 claims (3V, 3S)
18. `research/claims/re_kb_old_claims_display.md` - 7 claims (2V, 2S, 3H)
19. `research/claims/re_kb_old_claims_mmio.md` - 4 claims (4V)

**Total:** 33 claims (20 Verified, 10 Supported, 4 Hypothesis)

### Catalog (1 file)
20. `research/RE_KB_OLD_CATALOG.md` - **NEW**
   - Summary of 31 findings across 8 subsystems
   - Subsystem breakdown table
   - Key findings by subsystem
   - Integration notes (overlaps with E1 claims)
   - Ghidra version tagging documentation

### Archive (copied)
21. `research/findings/re_kb_archive/` - **NEW DIRECTORY**
   - 31 finding JSON files
   - index.json
   - n32903_registers.json (MMIO map)
   - project.json, README.md, schema/

---

## Key Findings by Subsystem

### USB (3 findings)
- **finding-0013:** USB File Scanning Trigger - boot-time hold-key detection, MINI volume exposure
- **finding-0019:** USB Stack Architecture - descriptor blob at 0x00475140, **UDC base 0xB8007000** [CONFLICT!]
- **finding-0022:** USB Descriptor Locations - complete memory layout, CDC patch strategy

**Critical:** CL-RKO-USB-002 confirms same incorrect UDC base (0xB8007000) as E-USB-019!

### BOOT (5 findings)
- **finding-0009:** Firmware Upgrade Orchestrator and Message Handler Table
- **finding-0010:** Upgrade UI Handler Functions (Queue Maintenance)
- **finding-0011:** Additional Firmware Functions Requiring Verification
- **finding-0021:** APP.bin load mechanism (2,576,940 bytes, no padding)
- **finding-0023:** SD Card Raw Binary Storage Layout [BOOT + STORAGE]

### SOC (2 findings)
- **finding-0001:** SoC Marking Discrepancy - DWIN M5 vs Nuvoton N32903K5DN
- **finding-0002:** N32903K5DN SoC Identification and Architecture

**Overlap:** Strong overlap with CL-SOC-001, CL-SOC-002 from E1 tier.

### HARDWARE (4 findings)
- **finding-0003:** GPIO Port B Configuration - Pins GPB[2-5] Unconfigured
- **finding-0006:** MMIO Display Controller + GPIO Base [HARDWARE + MMIO]
- **finding-0008:** GPIO Helper Functions - Pin Configuration, Read, Write
- **finding-0031:** ADC Architecture - Voltage Monitoring & Touch Screen

### HP45 (6 findings)
- **finding-0012:** HP45 Cartridge Control - Complete Pin Mapping
- **finding-0014:** HP45 Cartridge Architecture - 22×14 Nozzle Matrix
- **finding-0015:** HP45 Address Lines (HA0-HA21) Pin Mapping
- **finding-0016:** HP45 Primitive Lines (HP0-HP13) Pin Mapping
- **finding-0017:** HP45 Driver Hardware - CM504B Level Shifters
- **finding-0018:** Firmware Analysis - HP45 Control Code Patterns

**Coverage:** Comprehensive HP45 documentation, strong overlap with CL-HP45-* claims.

### DISPLAY (7 findings)
**New subsystem not in E1 tier!**
- **finding-0024:** SPI0 LCD command/data wrappers (ST7789V)
- **finding-0025:** ST7789V display bring-up and backlight enable
- **finding-0026:** LCD rendering primitives (window set, blit, pixel)
- **finding-0027:** ST7789V SPI Display Driver - Core Functions
- **finding-0028:** ST7789V Display Rendering Primitives - Blitter
- **finding-0029:** UI Architecture - Menu System and About Screen
- **finding-0030:** Display Backlight and PWM Control

**Significance:** E3-Old has LCD/Display subsystem documentation not present in E1 Chats!

### MMIO (4 findings)
- **finding-0004:** MMIO Global Control Registers (GCR_BA @ 0xB0000000)
- **finding-0005:** MMIO Doorbell/Parameter Block (0xB800C000)
- **finding-0006:** MMIO Display Controller + GPIO Base [HARDWARE + MMIO]
- **finding-0007:** MMIO UART Controller (UA_BA @ 0xB8008000)

### STORAGE (2 findings)
- **finding-0020:** SD Card Volume Management
- **finding-0023:** SD Card Raw Binary Storage Layout [BOOT + STORAGE]

---

## Cross-Tier Discoveries

### Evidence Tier Comparison

| Tier | Source | Entries | Claims | Status |
|------|--------|---------|--------|--------|
| E1 | Chats (research/Chats/*.json) | 216 | 118 | ✅ Complete |
| E3-Old | RE-KB Archive (31 findings) | 123 | 33 | ✅ Cataloged |
| E3-New | Current RE-KB (2 findings) | ~10 | ~2 | ⏳ Pending |
| E2 | Sessions (~47 logs) | - | - | ⏳ Future |

**Total Documented:** 339+ evidence entries, 151+ claims

### Overlap Analysis

**High Overlap Subsystems:**
- **USB:** 3 E3-Old findings map to CL-USB-004, 010, 014, 015, 017
- **SOC:** 2 E3-Old findings map to CL-SOC-001, 002, 007
- **HP45:** 6 E3-Old findings map to CL-HP45-002, 005, 006, 007, 008, 010, 012, 015

**Unique Content:**
- **DISPLAY subsystem:** 7 E3-Old findings with NO E1 equivalent (LCD driver, UI, rendering)
- **MMIO detail:** 4 E3-Old findings with granular register base documentation

### Contradiction Patterns

**Same Error Propagation:**
- E-USB-019 (E1 tier, 2025-12-06): "UDC-Base=0xB8007000"
- CL-RKO-USB-002 (E3-Old, 2025-12-02): "MMIO base 0xB8007000"
- Both predate Ghidra optimization (37k functions)
- BSP ground truth: USB_BA=0xB1008000, PWM_BA=0xB8007000

**Implication:** Multiple analysis sessions reached same incorrect conclusion, suggests systematic analysis error (likely literal pool misidentification).

---

## Decisions Made

### 1. Multi-Tier Evidence Structure
**Decision:** Use tier-prefixed filenames (`re_kb_old_evidence_*.md`) instead of merging immediately.

**Rationale:**
- Preserves provenance (which tier/source)
- Maintains historical accuracy
- Enables systematic reconciliation later
- Handles Ghidra version conflicts cleanly

### 2. Evidence Versioning Policy
**Decision:** Evidence = snapshot-in-time, not auto-updating truth.

**Implementation:**
- Mark old Ghidra evidence with `[ghidra-v1]` tag
- New Ghidra searches create new evidence entries
- Conflicts documented as CONTRADICTION-*.md
- Phase 4 handles systematic reconciliation

### 3. Cross-Subsystem Duplicates
**Decision:** Keep duplicates in multiple subsystem files for now.

**Examples:**
- finding-0023 in both BOOT and STORAGE
- finding-0006 in both HARDWARE and MMIO

**Rationale:**
- Subsystem-focused navigation (user finds claim where they look)
- Reconciliation phase will add cross-links
- No data loss

### 4. Archive Location
**Decision:** Copy old .re_kb to `research/findings/re_kb_archive/` (not hidden dotfile).

**Rationale:**
- Codex can access without special permissions
- Visible in file listings
- Clear naming convention (archive vs current)

---

## Outstanding Questions

### Critical (Blocks USB-CDC)
1. **USB Base Address:** Is UDC at 0xB8007000 (old analysis) or 0xB1008000 (BSP)?
   - **Next:** Pattern search (MOV/MOVT, register offsets) in optimized Ghidra analysis
   - **Impact:** CRITICAL for USB-CDC implementation

2. **Ghidra Analysis Validation:** Which functions are correct - 37k or 1.3k?
   - **Next:** Validate function count against BSP expectations
   - **Impact:** Determines which evidence tier to trust

### Documentation (Phase 2C-3)
3. **E1 ↔ E3-Old Overlap Resolution:** How to handle 31 identified overlaps?
   - Merge claims? Cross-reference only? Evidence upgrades?

4. **DISPLAY Subsystem:** E3-Old has 7 findings, E1 has zero. Why?
   - Was LCD/Display not discussed in analyzed Chats?
   - Should we extract DISPLAY evidence from other Chats?

5. **Evidence Confidence:** How to score evidence from different tiers?
   - E1 (Chats) = primary, but may be outdated
   - E3 (RE-KB) = structured, but also may be outdated
   - Newer wins? Or highest quality wins?

---

## Next Steps

### Immediate (Phase 2C-3: Reconciliation)
- [ ] Extract E3-New findings (finding-0001, finding-0002) into tier structure
- [ ] Resolve 31 E3-Old overlaps with E1 claims
- [ ] Identify evidence upgrades (E3 stronger than E1)
- [ ] Document evidence versioning decisions
- [ ] Update REKB_MAPPING.md with full E1 ↔ E3-Old ↔ E3-New reconciliation

### Phase 4: Contradiction Detection
- [ ] Systematic cross-cluster contradiction scan
- [ ] USB base address resolution (CONTRADICTION-USB-001)
- [ ] Ghidra version conflict analysis
- [ ] Create CONTRADICTIONS.md with decisive tests

### Phase 2D: Sessions Integration (Future)
- [ ] Catalog ~47 session logs in research/sessions/
- [ ] Extract E2 tier evidence where appropriate
- [ ] Build SESSION_INDEX.md for navigation

### Critical Block Resolution (USB-CDC)
- [ ] Ghidra pattern search for USB Device Controller usage
- [ ] Validate 0xB1008000 as correct UDC base
- [ ] Update CL-USB-010 with corrected information
- [ ] Mark E-USB-019 and CL-RKO-USB-002 as [refuted] or [corrected]

---

## Metrics

### Time Investment
- Phase 2C-1 (E3-New mapping): ~30 minutes
- Strategy pivot (multi-tier design): ~30 minutes
- Phase 2C-2 (E3-Old cataloging): ~2 hours
  - Archive copy: 5 minutes
  - Codex prompt creation: 20 minutes
  - Codex execution: 10 minutes
  - Quality review: 15 minutes
  - STRATEGY update: 10 minutes
  - Session log creation: 60 minutes

**Total:** ~3 hours

### Productivity Metrics
- **Files Created:** 21 (17 evidence/claims + 3 mapping/catalog + 1 strategy update)
- **Evidence Entries:** 123 (from 31 findings)
- **Claims Synthesized:** 33 propositional claims
- **Overlaps Mapped:** 31 potential E1 overlaps identified
- **Contradictions Found:** 1 critical (USB base address)

### Automation Success
- **Codex cataloging:** ✅ Excellent quality, zero manual corrections needed
- **Evidence tagging:** ✅ All Ghidra refs correctly tagged [ghidra-v1]
- **Claims synthesis:** ✅ Propositional structure maintained
- **Cross-references:** ✅ All 31 findings mapped to E1 overlaps

---

## Lessons Learned

### What Worked Well
1. **Multi-Tier Strategy:** Tier-prefixed filenames preserve provenance and enable clean reconciliation
2. **Codex Cataloging:** Comprehensive prompt with templates produces excellent quality output
3. **Evidence Versioning:** [ghidra-v1] tagging clearly marks potentially outdated evidence
4. **Archive Accessibility:** Copying old .re_kb to current project enabled Codex access

### What Could Be Improved
1. **Ghidra Version Tracking:** Should have documented analysis settings/versions earlier
2. **Cross-Subsystem Handling:** Need clearer policy for findings spanning multiple subsystems
3. **DISPLAY Gap:** E1 tier missing entire subsystem present in E3-Old

### Key Insights
1. **Evidence Provenance is Critical:** Can't merge tiers without understanding analysis context
2. **Same Analysis = Same Errors:** E1 and E3-Old share UDC base error (systematic issue)
3. **Ghidra Optimization Impact:** 37k → 1.3k function change invalidates old searches
4. **Catalog-First Approach:** Inventory before reconciliation prevents premature decisions

---

## Conclusion

Phase 2C established the **multi-tier evidence integration framework** required to reconcile overlapping knowledge sources while maintaining historical provenance. Successfully cataloged 31 historical RE-KB findings (123 evidence entries, 33 claims) and identified critical USB base address contradiction affecting both E1 and E3-Old tiers.

**Current State:**
- ✅ E1 tier: 216 evidence, 118 claims (complete)
- ✅ E3-Old tier: 123 evidence, 33 claims (cataloged)
- ✅ E3-New tier: 3 evidence files, 4 claims (complete)
- ⏳ E2 tier: ~47 sessions (next)

**Next Priority:** E2 Sessions integration (Phase 2D) to catalog chronological research logs, then reconciliation (Phase 2C-3).

---

## UPDATE: E3-New Extraction Complete (2026-01-04)

### Phase 2C-1 Completion

**E3-New Findings Processed:**
- finding-0001 (ARM/Thumb Mixed-Mode) → 1 evidence file, 1 claim
- finding-0002 (N32903 MMIO Register Map) → 2 evidence files (SOC+HARDWARE), 3 claims

**Files Created:**
- `research/evidence/re_kb_evidence_boot.md` (E-RKN-BOOT-001)
- `research/evidence/re_kb_evidence_soc.md` (E-RKN-SOC-001)
- `research/evidence/re_kb_evidence_hardware.md` (E-RKN-HARDWARE-001)
- `research/claims/re_kb_claims_boot.md` (CL-RKN-BOOT-001)
- `research/claims/re_kb_claims_soc.md` (CL-RKN-SOC-001, CL-RKN-SOC-002)
- `research/claims/re_kb_claims_hardware.md` (CL-RKN-HARDWARE-001)
- `research/RE_KB_NEW_CATALOG.md`

**Key Claims:**
- **CL-RKN-BOOT-001:** ARM/Thumb mixed-mode verified (18% Thumb, 82% ARM)
- **CL-RKN-SOC-001:** 1544 MMIO registers from BSP extraction (E0 tier ground truth)
- **CL-RKN-SOC-002:** USB_BA=0xB1008000 correction (refutes CL-USB-010 and CL-RKO-USB-002)
- **CL-RKN-HARDWARE-001:** USBD registers at 0xB1008000 confirmed

**Evidence Quality:**
- No [ghidra-v1] tagging (post-optimization analysis)
- finding-0002 evidence is E0 tier (BSP artifact = highest authority)
- finding-0001 evidence is E1 tier (post-optimization Ghidra)

**E3 Tier Summary:**
- Total findings: 33 (31 E3-Old + 2 E3-New)
- Total evidence entries: 126 (123 E3-Old + 3 E3-New)
- Total claims: 37 (33 E3-Old + 4 E3-New)
- Subsystems covered: USB, BOOT, STORAGE, SOC, HARDWARE, HP45, DISPLAY, MMIO

**Critical Finding:** E3-New tier definitively establishes USB_BA=0xB1008000 via BSP headers, resolving CONTRADICTION-USB-001 in favor of BSP ground truth over firmware analysis.

**Next:** Phase 2D - Sessions Integration (E2 tier: ~47 chronological logs)

---

*Session log created: 2026-01-03, updated: 2026-01-04*
*Claude Code (Sonnet 4.5) + Codex (GPT-5.1)*
