# Session Log: Incremental Claims Strategy + USB Prototype

**Date:** 2026-01-02
**Duration:** ~2 hours
**Participants:** Martin (User), Claude Code (Sonnet 4.5)
**Goal:** Build evidence-based claims extraction strategy to replace failed A1-A4 approach

---

## Context

### Problem Statement
Previous Codex runs (A1-A4) attempted to process 112 Chats + 47 Sessions atomically and produced **token-claims** (raw log lines, shell commands) instead of **propositional claims** (technical statements about the system).

**Root Cause:** Trying to extract claims from entire corpus at once → lost semantic meaning, copied evidence as claims.

**Example of failed output:**
- ❌ CL-001: `"[131350.838188] scsi 3:0:0:0: Direct-Access W55FA93..."` (raw log)
- ❌ CL-055: `"dd if=sdcard.work.img bs=1 skip=$((0x188FFC00...)"` (shell command)

### Solution Strategy
**Subsystem-by-subsystem incremental extraction:**
1. Evidence Collection (per cluster) → rohe Fakten aus Chats
2. Claim Synthesis (per cluster) → propositionale Aussagen bilden
3. Validation → automatisch prüfen
4. Integration → RE-KB/sessions/old_docs später einbinden

---

## Accomplishments Today

### 1. Strategy Document Created ✅
**File:** `research/STRATEGY_claims_incremental.md`

**Key Sections:**
- **Phase 1:** Subsystem clusters defined (USB, BOOT, STORAGE, SOC, HP45, TOOL)
- **Phase 2A:** Evidence collection (per cluster, chat-first)
- **Phase 2B:** Evidence validation (automated quality control)
- **Phase 2C:** RE-KB integration (findings as knowledge source)
- **Phase 2D:** Sessions integration (pointer layer, not evidence)
- **Phase 2E:** old_docs reconciliation (optional cleanup)
- **Phase 3:** Claim synthesis (propositional, no token-claims)
- **Phase 4:** Contradiction detection
- **Phase 5:** Timeline assembly
- **Phase 6:** Public history

**Merge Plan:** Chats first (strongest E1 evidence) → then layer RE-KB/sessions/old_docs.

---

### 2. USB Cluster Prototype - COMPLETE ✅

#### Evidence File
**File:** `research/evidence/evidence_usb.md`

- **Entries:** 28 evidence items
- **Sources:** Chats 833, 51 (USB-focused)
- **Categories:**
  - VID/PID & Device Identity (8 entries)
  - Device Class & Capacity (6 entries)
  - I/O Errors & Behavior (4 entries)
  - Controller & Hardware (4 entries)
  - CDC Template (BSP) (2 entries)
  - Test Results (2 entries)
  - Open Questions (2 entries)

**Format:**
```markdown
### E-USB-001: VID/PID Enumeration
- **Quote:** "idVendor=0416, idProduct=0093, bcdDevice=11.00"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** vid-pid, enumeration, identity
```

#### Claims File
**File:** `research/claims/claims_usb.md`

- **Claims:** 17 propositional statements
- **Status Distribution:**
  - ✅ Verified: 9 claims (high confidence, multiple E1 sources)
  - ⚠️ Supported: 7 claims (solid E1, needs cross-check)
  - 🔬 Hypothesis: 1 claim (single E1 or inference)

**Examples of GOOD propositional claims:**
- ✅ CL-USB-001: "USB device enumerates as VID:PID 0416:0093, which is registered to Nuvoton/Winbond"
- ✅ CL-USB-004: "Device supports two operational modes: Normal MSC (PID 0093) and IBR-Boot recovery mode (PID 9396)"
- ✅ CL-USB-010: "USB Device Controller (UDC) registers are mapped at MMIO base address 0xB8007000"

**Quality Markers:**
- ❌ NO token-claims (no raw logs as claims)
- ❌ NO shell commands as claims
- ❌ NO incomplete sentences
- ✅ Specific next tests (not generic "confirm in chat")
- ✅ Evidence-links with msg-numbers
- ✅ Counter-evidence tracked
- ✅ Contradictions identified (Cluster-SOC-001)

---

### 3. Evidence Validation Tool ✅

#### Script Created
**File:** `tools/scripts/validate_evidence.py`

**Function:**
- Parses `evidence_*.md` files
- Extracts source references (e.g., `Chats/833#msg=2`)
- Opens JSON files and checks if quotes appear in message content
- Reports: Valid (exact match) | Partial (key words match) | Mismatch | Error

**USB Cluster Validation Result:**
```
Total entries:    28
✅ Valid:         20 (exact quote matches)
⚠️  Partial:       8 (all key words found, reformulated)
❌ Mismatch:      0
🔴 Error:         0

Success rate: 100.0%
```

**Conclusion:** All evidence links are valid and traceable. Partial matches are acceptable (reformulated quotes with all key words present).

**Usage for next clusters:**
```bash
python3 tools/scripts/validate_evidence.py
```

---

## Key Decisions

### 1. Evidence-Tiers (for claim status)
- **E0:** Artifacts (binaries, dumps, register maps, photos)
- **E1:** Chat transcripts (`Chats/*.json#msg=N`) **← Primary evidence**
- **E2:** Session notes (pointers only, rarely evidence)
- **E3:** RE-KB findings (knowledge source, not auto-truth)

**Rule:** Claim can only be VERIFIED if E0 or strong E1 exists.

### 2. RE-KB Integration Strategy
- **NOT immediate:** First build claims from chats (E1)
- **Phase 2C (later):** Map RE-KB findings to claims
  - If finding has E0/E1 → add to claim evidence
  - If finding has no E0/E1 → mark claim as hypothesis
  - Detect duplicates (multiple findings = one claim)

**Rationale:** Chats are strongest evidence; RE-KB contains hypotheses mixed with facts.

### 3. Sessions Integration Strategy
- **NOT as evidence:** Sessions explain "why" something was investigated
- **Phase 2D (later):** Build index: Session → Claims, Claim → Sessions
- **Use case:** Navigation, context, progression tracking

**Rationale:** Sessions are pointers/handoffs, not primary sources.

### 4. Execution Preference: Sequential (Option B)
- **User preference:** Sequential cluster-by-cluster (like USB prototype)
- **Reason:** Codex-as-MCP buggy, low usage quota remaining
- **Next cluster:** STORAGE or SOC (both critical, have contradictions)

---

## Outputs Created

### Files
1. `research/STRATEGY_claims_incremental.md` - Complete strategy doc
2. `research/evidence/evidence_usb.md` - 28 USB evidence entries
3. `research/claims/claims_usb.md` - 17 USB propositional claims
4. `tools/scripts/validate_evidence.py` - Evidence validation tool
5. `research/sessions/2026-01-02_incremental-claims-strategy-usb-prototype.md` - This log

### Directories
- `research/evidence/` - Evidence files per cluster
- `research/claims/` - Claim files per cluster

---

## Template Validated ✅

**Evidence → Claims Ratio:** 28 evidence → 17 claims (1.6:1) is reasonable.

**Quality Metrics Met:**
- ✅ No token-claims
- ✅ All sentences complete
- ✅ Specific next tests
- ✅ 100% validation success rate
- ✅ Clear status/confidence assignment

**Template ready for:**
- BOOT cluster
- STORAGE cluster
- SOC cluster
- HP45 cluster
- TOOL cluster

---

## Next Session Tasks (Sequential Execution)

### Immediate (Tomorrow/Next Session)

#### Option 1: STORAGE Cluster (Recommended)
**Why:** Critical for understanding volume mappings (0:/, 3:/), ties to BOOT and USB MSC.

**Chats to scan:** 915, 834, 14, 15
**Keywords:** "3:/", "0:/", "SD", "ext4", "0x188FFC00", "partition", "volume"
**Expected:** 30-40 evidence entries → 12-18 claims
**Key topics:**
- Volume 0:/ (MINI) exposed via USB MSC
- Volume 3:/ (BOOT+APP storage)
- Filesystem layout (no MBR/GPT, raw FAT16)
- SD card geometry

#### Option 2: SOC Cluster (Alternative)
**Why:** Has contradiction with USB cluster (W55FA93 vs N32903U5DN chip name).

**Chats to scan:** 833, 54, 55, 56, 57, 58, 80
**Keywords:** "N32903", "W55FA93", "ARM9", "SoC", "MMIO", "0xB"
**Expected:** 30-40 evidence entries → 12-18 claims
**Key topics:**
- Chip identity (W55FA93 string vs N32903U5DN marking)
- MMIO register map (findings/n32903_registers.json as E0)
- BSP compatibility
- Pinout verification

**Contradiction to resolve:** Why does USB enumerate as "W55FA93" but chip marking shows "N32903U5DN"?

### Workflow (Same as USB Prototype)
1. **Scan chats** for cluster-specific keywords
2. **Extract evidence** (30-40 entries) → `evidence_{cluster}.md`
3. **Validate evidence** → `python3 tools/scripts/validate_evidence.py`
4. **Synthesize claims** (12-18 propositional) → `claims_{cluster}.md`
5. **Review & iterate** if needed

### After All Clusters Complete
- **Phase 2B:** Validate all evidence files
- **Phase 2C:** RE-KB integration (map findings to claims)
- **Phase 2D:** Sessions integration (build index)
- **Phase 4:** Contradiction detection (especially SOC vs USB)
- **Phase 5:** Timeline assembly
- **Phase 6:** Public history

---

## Open Questions

1. **Which cluster next?** STORAGE (volume mappings) or SOC (chip identity contradiction)?
2. **Contradiction priority:** Should SOC cluster be done early to resolve W55FA93/N32903 conflict?
3. **RE-KB activation:** When to activate `.re_kb` project? (After all chat-based clusters, per strategy)

---

## User Preferences Noted

- **Execution:** Sequential (Option B) due to Codex-as-MCP bugs and quota limits
- **Pace:** One cluster per session, quality over speed
- **Integration:** Chat-first approach validated, RE-KB/sessions/old_docs later

---

## Success Metrics

**USB Cluster:**
- ✅ 28/28 evidence entries validated (100%)
- ✅ 17 propositional claims (0 token-claims)
- ✅ Template proven viable
- ✅ Validation workflow established

**Overall Project:**
- **Target:** 60-100 total claims across 6 clusters
- **Current:** 17 claims (USB) = 17-28% complete
- **Projected:** 5 more clusters × ~15 claims each = ~92 total claims

---

## Handoff for Next Session

### Resume Points
1. **If continuing with STORAGE cluster:**
   - Start with `research/STRATEGY_claims_incremental.md` Phase 2A → STORAGE Cluster checklist
   - Scan Chats: 915, 834, 14, 15
   - Create `research/evidence/evidence_storage.md`

2. **If continuing with SOC cluster:**
   - Start with `research/STRATEGY_claims_incremental.md` Phase 2A → SOC Cluster checklist
   - Scan Chats: 833, 54, 55, 56, 57, 58, 80
   - **Also load:** `research/findings/n32903_registers.json` (E0 artifact)
   - Create `research/evidence/evidence_soc.md`

### Key Files to Reference
- Strategy: `research/STRATEGY_claims_incremental.md`
- USB Evidence (template): `research/evidence/evidence_usb.md`
- USB Claims (template): `research/claims/claims_usb.md`
- Validation Tool: `tools/scripts/validate_evidence.py`

### Commands to Run
```bash
# Start validation after creating evidence file
python3 tools/scripts/validate_evidence.py

# Check strategy progress
cat research/STRATEGY_claims_incremental.md | grep -A 5 "Phase 2A"
```

---

**End of Session 2026-01-02**
**Next Session:** STORAGE or SOC cluster (user decides)
**Status:** USB cluster complete ✅, template validated ✅, 5 clusters remaining
