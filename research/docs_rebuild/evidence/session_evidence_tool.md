# TOOL Evidence (E2 Tier: Sessions)

**Source:** research/sessions/*.md (chronological research logs)
**Tier:** E2 (navigation/context layer, unique session-level evidence)
**Note:** E2 tier captures meta-analysis, strategy evolution, and framework design not present in E1/E3 tiers.

---

## Strategy Evolution and Framework Design

### E2-TOOL-019: Incremental Claims Extraction Strategy Evolution
- **Session ID:** S-019 (2026-01-02)
- **File:** sessions/2026-01-02_incremental-claims-strategy-usb-prototype.md
- **Type:** Meta-analysis and strategy design
- **Summary:** Critical session documenting failure of initial A1-A4 approach (atomic corpus processing) and design of incremental subsystem-by-subsystem extraction strategy. Explains difference between token-claims (raw logs/commands) and propositional claims (technical statements), establishing foundation for entire evidence/claims framework.
- **Key Evidence:**
  - **Failed Approach (A1-A4):** Attempted to process 112 Chats + 47 Sessions atomically
    * Result: Token-claims extracted instead of propositional claims
    * Examples of failures:
      - ❌ CL-001: `"[131350.838188] scsi 3:0:0:0: Direct-Access W55FA93..."` (raw dmesg log)
      - ❌ CL-055: `"dd if=sdcard.work.img bs=1 skip=$((0x188FFC00...)"` (shell command)
    * Root cause: Lost semantic meaning by processing entire corpus at once
  - **Solution - Incremental Strategy:**
    * Phase 1: Define subsystem clusters (USB, BOOT, STORAGE, SOC, HP45, TOOL)
    * Phase 2A: Evidence collection (per cluster, chat-first)
    * Phase 2B: Evidence validation (automated quality control)
    * Phase 2C: RE-KB integration (findings as knowledge source)
    * Phase 2D: Sessions integration (pointer layer, not evidence)
    * Phase 2E: old_docs reconciliation (optional cleanup)
    * Phase 3: Claim synthesis (propositional, no token-claims)
    * Phase 4: Contradiction detection
    * Phase 5: Timeline assembly
    * Phase 6: Public history
  - **USB Prototype Success:**
    * Evidence file: 28 entries from Chats 833, 51
    * Claims file: 17 propositional statements
    * Format validated: Quote → Source → Date → Type → Tags structure
    * Example claim: ✅ "Device uses VID:PID 0416:0093 for MSC mode" (propositional)
  - **Merge Plan:** Chats first (E1 tier, strongest evidence) → then layer RE-KB/sessions/old_docs
- **Outcome:** Incremental strategy adopted, USB prototype validated approach, strategy document created
- **Research Value:** Documents why approach changed, establishes evidence hierarchy (E1 > E3 > E2), defines token-claims vs propositional claims distinction
- **Cross-Reference:** All E1 tier claims (CL-*), STRATEGY_claims_incremental.md
- **Methodology Impact:** All subsequent evidence/claims extraction follows this framework
- **Tags:** tool, strategy, methodology, claims-synthesis, evidence-hierarchy, meta-analysis
- **Created:** 2026-01-02
- **Evidence Tier:** E2 (meta-framework design)
- **Critical Decision:** Chat-first approach ensures highest-quality evidence (E1) forms foundation before layering secondary sources

### E2-TOOL-021: Multi-Tier Evidence Integration Framework Design
- **Session ID:** S-021 (2026-01-03)
- **File:** sessions/2026-01-03_phase-2c-multi-tier-evidence-integration.md
- **Type:** Framework design and provenance management
- **Summary:** Pivotal session establishing multi-tier evidence integration framework (E0/E1/E2/E3-Old/E3-New) to handle overlapping knowledge sources while preserving historical provenance. Designed evidence versioning policy with [ghidra-v1] tagging to handle Ghidra optimization impact (37k → 1.3k functions). Critical for maintaining data integrity across analysis iterations.
- **Key Evidence:**
  - **Problem:** Multiple overlapping knowledge sources discovered
    * E1 Tier (Chats): 216 evidence, 118 claims - PRIMARY source
    * E3-Old Tier (RE-KB archive): 31 findings from pre-optimization era
    * E3-New Tier (RE-KB current): 2 findings from post-optimization
    * E2 Tier (Sessions): ~47 logs - navigation/pointer layer
    * E? Tier (old_docs): Legacy documentation - future
  - **Evidence Tier Hierarchy:**
    * E0 (Artifacts): Binary files, datasheets, BSP headers - GROUND TRUTH, highest authority
    * E1 (Chats): Primary evidence from research/Chats/*.json
    * E2 (Sessions): Pointer/navigation layer, methodology narratives
    * E3-Old (Archive): Historical RE-KB findings (pre-optimization, 31 findings)
    * E3-New (Current): Current RE-KB findings (post-optimization, 2 findings)
  - **Evidence Versioning Policy:**
    * Core principle: Evidence entries are snapshot-in-time observations, NOT auto-updating truth
    * Version tagging: [ghidra-v1] marks pre-optimization Ghidra analysis (37k functions)
    * Conflict resolution: Newer analysis wins, older evidence marked with version tag
    * Provenance preservation: Tier-prefixed filenames (evidence_*.md, re_kb_old_evidence_*.md, session_evidence_*.md)
  - **Tier-Prefixed File Structure:**
    ```
    evidence/
    ├── evidence_*.md              # E1 (Chats) - 216 entries
    ├── re_kb_old_evidence_*.md    # E3-Old (31 findings) - 123 entries
    ├── re_kb_evidence_*.md        # E3-New (2 findings) - 3 files
    └── session_evidence_*.md      # E2 (sessions) - navigation layer

    claims/
    ├── claims_*.md                # E1 (Chats) - 118 claims
    ├── re_kb_old_claims_*.md      # E3-Old - 33 claims
    └── re_kb_claims_*.md          # E3-New - 4 claims
    ```
  - **Critical Discovery: CONTRADICTION-USB-001**
    * E1 CL-USB-010: USB UDC base = 0xB8007000 (from Chat 51, ghidra-v1 analysis)
    * E3-Old CL-RKO-USB-002: USB UDC base = 0xB8007000 (from RE-KB finding-0019, ghidra-v1)
    * E0 BSP Headers: USB_BA = 0xB1008000, PWM_BA = 0xB8007000
    * Resolution: Both E1 and E3-Old wrong (systematic error from ghidra-v1 over-detection), E3-New CL-RKN-SOC-002 corrects via BSP ground truth
  - **Cataloging Results:**
    * E3-Old: 31 findings → 8 evidence files (123 entries), 8 claims files (33 claims)
    * E3-New: 2 findings → 3 evidence files, 3 claims files (4 claims)
    * All E3-Old Ghidra evidence tagged [ghidra-v1]
    * Cross-references mapped: 31 E3-Old findings to E1 potential overlaps
  - **Subsystem Coverage:**
    * E3-Old: USB, BOOT, STORAGE, SOC, HARDWARE, HP45, DISPLAY (7 in E3-Old), MMIO
    * E3-New: BOOT, SOC, HARDWARE
    * Gap identified: DISPLAY subsystem present in E3-Old but missing from E1 Chats
- **Outcome:** Multi-tier framework established, 126 E3 evidence entries cataloged, CONTRADICTION-USB-001 identified and documented, evidence versioning policy operational
- **Research Value:** Establishes meta-framework for handling overlapping/conflicting knowledge sources, explains how to reconcile pre/post-optimization analysis, documents systematic error propagation (same ghidra-v1 analysis → same errors in E1 and E3-Old)
- **Cross-Reference:** All tier structures, CONTRADICTION-USB-001, REKB_MAPPING.md, RE_KB_OLD_CATALOG.md, RE_KB_NEW_CATALOG.md
- **Framework Impact:** All future integration work (Phase 2D/2E/3/4/5/6) depends on this tier structure
- **Tags:** tool, framework, evidence-tiers, versioning, provenance, contradiction-handling, integration
- **Created:** 2026-01-03 (extended session)
- **Evidence Tier:** E2 (meta-framework design)
- **Critical Insight:** Same analysis version = same systematic errors. E1 and E3-Old both used ghidra-v1, both claimed USB base = 0xB8007000 (wrong). Only E0 tier (BSP) and post-optimization E3-New corrected this.

---

## Integration Notes

**E2-TOOL Evidence Type:** Meta-analysis and framework design that documents:
1. Strategy evolution (failed approaches → working solutions)
2. Evidence tier hierarchies (E0 > E1 > E3 > E2)
3. Versioning policies (how to handle analysis iterations)
4. Systematic error propagation (ghidra-v1 over-detection)

**Relationship to Other Tiers:**
- **E0 Tier:** E2-TOOL-021 establishes E0 as ground truth authority
- **E1 Tier:** E2-TOOL-019 explains how all E1 claims were extracted (incremental strategy)
- **E3 Tiers:** E2-TOOL-021 establishes E3-Old vs E3-New distinction and [ghidra-v1] tagging
- **All Future Work:** Both sessions define framework for Phases 2D-6

**Critical Meta-Findings:**
1. **Token-claims vs Propositional Claims:** E2-TOOL-019 establishes distinction - only propositional claims are valid
2. **Evidence Snapshot Principle:** E2-TOOL-021 establishes evidence as historical record, not auto-updating truth
3. **Systematic Error Propagation:** E2-TOOL-021 shows how same analysis version creates same errors across tiers
4. **Ground Truth Hierarchy:** E0 (artifacts) > E3-New (post-opt) > E1/E3-Old (pre-opt) when conflicts arise

**Phase 2D Impact:** This SESSION_INDEX.md and associated session_evidence_*.md files are direct outputs of E2-TOOL-021 framework design.

---

*Evidence file created: 2026-01-04*
*E2 Tier: Meta-framework and strategy evolution documentation*
