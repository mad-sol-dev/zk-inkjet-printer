# Phase 1 Reconciliation Complete

**Status:** COMPLETE
**Date:** 2026-01-05
**Duration:** 4 days (2026-01-02 to 2026-01-05)
**Reconciler:** Codex (GPT-5.1) + Claude (Sonnet 4.5)

---

## Executive Summary

Phase 1 (Systematic Merging) reconciled 189 input claims from 5 evidence tiers (E0/E1/E2/E3-Old/E3-New/E4) across 9 subsystems into 152 documented reconciliation claims.

**Key Achievement:** Established the authority hierarchy (E0 > E3-New > E1 > E3-Old > E4) and resolved major contradictions via ground truth artifacts (BSP headers, firmware images), including the USB base address conflict (CONTRADICTION-USB-001).

**Quality:** All reconciled claims include authority tier assignment, traceable evidence across contributing tiers, superseded evidence flags ([ghidra-v1]/[superseded]), cross-subsystem references where applicable, and next-test guidance.

**Next Phase:** Technical validation (verify claims through analysis, correct errors, resolve remaining contradictions).

---

## Final Statistics

### By Subsystem

| Subsystem | Input Claims | Output Claims | Reduction | Authority Distribution |
|-----------|--------------|---------------|-----------|------------------------|
| USB | 22 | 21 | +1 | E1: 16, E3-Old: 2, E0: 2, E4: 1 |
| SOC | 26 | 20 | +6 | E1: 18, E3-Old: 1, E0: 1 |
| HARDWARE | 29 | 23 | +6 | E1: 15, E3-Old: 4, E4: 3, E0: 1 |
| BOOT | 26 | 22 | +4 | E1: 10, E0: 3, E3-Old: 5, E3-New: 1, E4: 3 |
| STORAGE | 22 | 16 | +6 | E0: 7, E1: 4, E3-Old: 2, E4: 3 |
| HP45 | 24 | 15 | +9 | E1: 11, E3-Old: 4 |
| DISPLAY | 10 | 7 | +3 | E1-Recent: 2, E3-Old: 4, E0: 1 |
| MMIO | 9 | 6 | +3 | E0: 5, E4: 1 |
| TOOL | 21 | 22 | -1 | E1: 15, E0: 2, E4: 3, E2: 2 |
| **TOTAL** | **189** | **152** | **+37** | E0: 22, E3-New: 1, E1: 89, E1-Recent: 2, E3-Old: 22, E4: 14, E2: 2 |

### By Evidence Tier (Input)

| Tier | Claims | Evidence Entries | Status |
|------|--------|------------------|--------|
| E0 (Artifacts) | 0* | 35 references | Ground truth |
| E3-New (Current RE-KB) | 4 | 3 | Post-optimization |
| E1 (Chats) | 118 | 216 | Primary evidence |
| E1-Recent (New findings) | 2 | 2 | Recent analysis |
| E3-Old (Archive) | 33 | 33 | [ghidra-v1] |
| E4 (old_docs) | 34 | 42 | [ghidra-v1] |
| E2 (Sessions) | 2 | 9 | Methodology |

*E0 artifacts do not generate claims directly; they provide ground truth references.

### Status Distribution (Output)

| Status | Count | Percentage |
|--------|-------|------------|
| Verified | 49 | 32.2% |
| Supported | 81 | 53.3% |
| Hypothesis | 20 | 13.2% |
| Refuted | 2 | 1.3% |
| **TOTAL** | **152** | **100%** |

---

## Key Achievements

### 1. Critical Corrections via Ground Truth

**USB Base Address Correction**
- **Before:** E1/E3-Old claimed UDC base = 0xB8007000.
- **After:** E0 BSP headers show USB_BA = 0xB1008000, PWM_BA = 0xB8007000.
- **Root Cause:** [ghidra-v1] scalar search error.
- **Impact:** Corrected in `research/reconciliation/RECONCILED_claims_usb.md` (CL-USB-REC-011); E-USB-019 superseded.
- **Resolution:** CONTRADICTION-USB-001 resolved.

**Chip Identity Clarification**
- **Before:** E3-Old/E4 claimed N32903K5DN (K-series, no SDRAM).
- **After:** E1 measurements and readouts confirm N32903U5DN (U-series, 8MB DDR).
- **Root Cause:** K-series inference from incomplete datasheet matching.
- **Impact:** SoC identity conflict resolved in `research/reconciliation/RECONCILED_claims_soc.md` (CL-SOC-REC-001) with RAM size conflict resolved.

**Display Controller Uncertainty Acknowledged**
- **Before:** E3-Old treated ST7789V as verified.
- **After:** E1-Recent analysis leaves controller unconfirmed (ST7789V or ILI9341).
- **Root Cause:** LCD init sequence extraction incomplete.
- **Impact:** Controller claims downgraded to hypothesis in `research/reconciliation/RECONCILED_claims_display.md` (CL-DISPLAY-REC-002).

**MMIO Base Corrections**
- **Before:** E3-Old interpreted 0xB800C000 as a doorbell/parameter block.
- **After:** E0 BSP confirms 0xB800C000 = SPI0_BA.
- **Impact:** Corrected in `research/reconciliation/RECONCILED_claims_mmio.md` (CL-MMIO-REC-004).

### 2. Evidence Versioning Policy Established

**[ghidra-v1] Tagging**
- [ghidra-v1] tags applied to 102 evidence references in reconciled claims.
- Superseded evidence explicitly marked (3 [superseded] tags across 14 claims).
- Pre-optimization artifacts preserved for provenance but de-prioritized in authority hierarchy.

**Authority Hierarchy**
- E0 (BSP/artifacts) trumps all firmware analysis.
- E3-New (post-optimization) supersedes E1/E3-Old/E4 when present.
- E1-Recent overrides older tiers for display hardware when conflicts exist.

### 3. Cross-Subsystem Integration

**Hardware-Software Linkage**
- HP45 GPIO allocation cross-referenced against HARDWARE pin map.
- DISPLAY SPI0 wiring and PWM0 backlight aligned with HARDWARE interface claims.
- BOOT update chain aligned with STORAGE volume mapping (3:/ volume assumptions).
- USB device pin availability cross-referenced with HARDWARE interface availability.

**Tool-Enabled Discoveries**
- Ghidra MCP enabled USB base address validation and BSP extraction.
- BSP extraction (finding-0002) provided 1544-register MMIO ground truth.
- RE-KB system preserved historical analysis provenance across tiers.

### 4. Unresolved Contradictions Documented

**Storage Volume Mapping**
- CONTRADICTION-STORAGE-001: Volume 3 location unresolved.
- CONTRADICTION-STORAGE-002: MINI vs Volume 0 mapping unresolved.

**Update Validation Mechanism**
- E1 vs E4 disagreement on update validation (CRC/guard checks) remains unresolved.

**Base Address Convention (TOOL)**
- E4 uses 0x200000; E1 uses 0x02000000 for APP.bin base.
- Marked as a tooling convention mismatch requiring verification.

---

## Methodology

### Reconciliation Process

**1. Evidence Collection (Phase 2A-2E)**
- E1 (Chats): 216 evidence entries, 118 claims extracted.
- E2 (Sessions): 9 evidence entries (methodology).
- E3-Old (Archive): 33 evidence entries, 33 claims.
- E3-New (Current): 3 evidence entries, 4 claims.
- E4 (old_docs): 42 evidence entries, 34 claims.
- E1-Recent: 1 display report referenced across 2 reconciled claims.

**2. Systematic Merging (Phase 2C-3)**
- Batch 1: USB, SOC, HARDWARE.
- Batch 2: BOOT, STORAGE.
- Batch 3: HP45, DISPLAY, MMIO.
- Batch 4: TOOL.

**3. Decision Framework**
- **EXACT_MATCH merges:** 9
- **PARTIAL_OVERLAP merges:** 49
- **UNIQUE kept:** 88
- **REFUTED:** 5

**4. Quality Controls**
- Every input claim accounted for (no silent drops).
- Authority tier explicitly stated for each output claim.
- Superseded evidence marked with [ghidra-v1] or [superseded] tags.
- Cross-subsystem references added where appropriate.
- Specific next-test steps included for validation.

### Tools Used

**Codex (GPT-5.1):** Primary reconciliation engine, extraction and decision log generation.

**Claude (Sonnet 4.5):** Prompt engineering, template refinement, quality validation.

**Desktop Commander MCP:** File operations and validation support.

---

## Quality Metrics

### Evidence Quality by Tier

**E0 (Ground Truth):**
- BSP headers and firmware artifacts used as authoritative references.
- 35 E0 references cited across reconciled claims.

**E3-New (Post-Optimization):**
- 4 claims, 3 evidence entries (1.3k function analysis).

**E1 (Primary Evidence):**
- 118 claims, 216 evidence entries.

**E3-Old (Archive):**
- 33 claims, 33 evidence entries, [ghidra-v1] tagged.

**E4 (old_docs):**
- 34 claims, 42 evidence entries, [ghidra-v1] tagged.

**E2 (Sessions):**
- 9 evidence entries (methodology context), 2 meta-claims integrated into TOOL.

### Authority Distribution Analysis

- E0 authority: 22 claims (14.5%)
- E3-New authority: 1 claims (0.7%)
- E1 authority: 89 claims (58.6%)
- E1-Recent authority: 2 claims (1.3%)
- E3-Old authority: 22 claims (14.5%)
- E4 authority: 14 claims (9.2%)
- E2 authority: 2 claims (1.3%)

**Interpretation:** Most reconciled claims remain E1-led (interactive evidence), while E0/E3-New provide decisive corrections in base address and MMIO mapping. E3-Old/E4 still contribute supporting context but are frequently tagged [ghidra-v1].

### Superseded Evidence Statistics

- Total evidence entries marked [superseded]: 3
- [ghidra-v1] tags in reconciled claims: 102
- Claims with non-empty superseded evidence: 14

---

## Subsystem Highlights

### USB (Communication Interface)
- **Key Claim:** USB_BA = 0xB1008000 (BSP-backed, refuted 0xB8007000).
- **Architecture:** Dual-mode operation (MSC + IBR-Boot).
- **Capacity:** 64 MiB MSC exposure (MINI volume).
- **Status:** 21 claims reconciled, CONTRADICTION-USB-001 resolved.

### SOC (System-on-Chip)
- **Key Claim:** N32903U5DN (U-series, 8MB DDR, LQFP-128).
- **Memory:** 8 MB DDR SDRAM @ 1.8V (refuted no-SDRAM K5DN claims).
- **Pinout:** 72 GPIOs mapped with alternate functions.
- **Status:** 20 claims reconciled, SoC identity conflict resolved.

### HARDWARE (GPIO/Peripherals)
- **Key Claim:** 31 GPIOs used, 41 free (allocation map).
- **Interfaces:** SPI0 (display), PWM0 (backlight), I2C candidates (GPB[13-14]).
- **USB Device:** Pins 26-28/86 unused, UDC available for CDC.
- **Status:** 23 claims reconciled, interface availability documented.

### BOOT (Firmware Boot Process)
- **Key Claim:** IBR -> BOOT.bin @ 0x200 -> APP.bin @ 0x100000 -> RAM 0x03000000.
- **ARM/Thumb:** Mixed-mode code verified (E3-New).
- **Update:** 3:/ volume scan, FatFS, TurboWriter workflow.
- **Status:** 22 claims reconciled, boot chain complete.

### STORAGE (SD Card Layout)
- **Key Claim:** Raw SD layout (no MBR/GPT), 4GB capacity.
- **Volumes:** FAT16 at LBA 0x20000, 1179711, 1388767 (E0 verified).
- **Contradiction:** Volume 3 location unresolved.
- **Status:** 16 claims reconciled, contradictions documented.

### HP45 (Printhead)
- **Key Claim:** 22x14 nozzle matrix, HA+HP overlap firing.
- **Drivers:** CM504B level shifters (30 GPIOs), high-current HP drivers.
- **Timing:** HA 10-12V, HP 1.5-2us @ 9-13V.
- **Status:** 15 claims reconciled, encoder Pin 117 mystery documented.

### DISPLAY (LCD Interface)
- **Key Claim:** 2.8 inch TFT, 18-pin FFC, SPI0 wiring, 4-wire resistive touch.
- **Controller:** ST7789V or ILI9341 (unconfirmed hypothesis).
- **Hardware:** Pin 120 RS/A0, PWM0 backlight.
- **Status:** 7 claims reconciled, controller ID downgraded to hypothesis.

### MMIO (Memory-Mapped I/O)
- **Key Claim:** Peripheral bases aligned to BSP (GCR, GPIO, USB, SPI0, BLT).
- **Correction:** 0xB800C000 = SPI0_BA (not doorbell).
- **Status:** 6 claims reconciled, [ghidra-v1] errors corrected.

### TOOL (Analysis Infrastructure)
- **Key Claim:** Ghidra MCP workflow (allowlist, batch mode, port 8080).
- **RE-KB:** JSON storage with MCP-gated writes and structured inputs.
- **Codex:** CWD behavior, spawn patterns, timeout control.
- **Status:** 22 claims reconciled (includes 2 E2 meta-claims).

---

## Known Issues and Limitations

### Unresolved Technical Questions

1. **Volume 3 Location (STORAGE)**
   - Status: Hypothesis
   - Next Step: Analyze `FUN_0005ebb8` mount function in optimized Ghidra.
   - Impact: Update mechanism mapping incomplete.

2. **Update Validation (BOOT/STORAGE)**
   - Status: Conflicting evidence (E1 vs E4).
   - Next Step: Verify update path for CRC or size-guard validation.
   - Impact: Update integrity mechanism unclear.

3. **MT6701 Encoder Pin 117 (SOC/HARDWARE/HP45)**
   - Status: Documented but unexplained.
   - Next Step: Locate MT6701 driver or SPI/I2C access path in firmware.
   - Impact: Encoder integration unclear.

4. **Display Controller Identity (DISPLAY)**
   - Status: Hypothesis (ST7789V or ILI9341).
   - Next Step: Extract clean init sequence from firmware.
   - Impact: Display driver specifics unresolved.

5. **Base Address Convention (TOOL)**
   - Status: E1 uses 0x02000000; E4 uses 0x200000.
   - Next Step: Re-import APP.bin with both bases and compare disassembly quality.
   - Impact: Historical analysis reproducibility unclear.

6. **USB Firmware Usage (USB)**
   - Status: BSP defines USB_BA = 0xB1008000; firmware references unconfirmed.
   - Next Step: Search for base construction via MOV/MOVT or offset usage patterns.
   - Impact: USB controller usage not yet verified in APP.bin.

### Evidence Gaps

1. **DISPLAY Subsystem:**
   - No E1 chat tier claims; relies on E3-Old/E4 plus E1-Recent hardware report.

2. **MMIO Subsystem:**
   - No E1 chat tier claims; relies on E3-Old/E4 plus BSP extraction.

### Validation Status

- USB: Base address corrected; firmware usage unconfirmed.
- SOC: Chip identity and DDR verified; MT6701 integration unknown.
- BOOT: Boot chain and memory map validated from artifacts.
- STORAGE: Raw layout and FAT locations validated; Volume 3 unresolved.
- DISPLAY: Controller identity pending firmware analysis.

---

## Lessons Learned

### What Worked Well

1. **Multi-Tier Framework:** Clear provenance preserved while enabling conflict resolution.
2. **BSP Ground Truth:** E0 artifacts definitively resolved base address and MMIO conflicts.
3. **Systematic Approach:** Subsystem-by-subsystem reconciliation kept scope manageable.
4. **Codex Automation:** Consistent templates and decision logs across all subsystems.
5. **Evidence Versioning:** [ghidra-v1] tagging prevented false certainty from legacy analysis.

### What Could Be Improved

1. **E1 Coverage Gaps:** DISPLAY and MMIO lacked chat-tier coverage.
2. **Validation Timing:** Some claims marked verified without firmware usage confirmation.
3. **Cross-Subsystem Planning:** Dependency mapping could have been planned earlier.
4. **Evidence QA:** Validation script failures reduced confidence in some quote checks.

### Key Insights

1. **Multiple Sources Provide Complementary Perspectives:** Reconciliation merged overlapping artifacts into unified truth.
2. **Ghidra Optimization Impact Was Massive:** 37k to 1.3k functions changed interpretation of scalar searches.
3. **BSP Artifacts Are Ultimate Authority:** Vendor headers resolved core contradictions.
4. **Versioning Is Essential:** Historical analysis is preserved without polluting current truth.

---

## Next Steps: Phase 2 (Technical Validation)

### Objectives

1. **Verify Verified Claims:** Cross-check all verified claims against firmware and artifacts.
2. **Resolve Contradictions:** Volume 3 location, update validation, base address convention.
3. **Upgrade Hypotheses:** Display controller ID, USB firmware usage, MT6701 driver path.
4. **Error Correction:** Update statuses and record revisions as new evidence appears.

### Approach

**Phase 2A: Critical Claims First**
- USB base usage (CL-USB-REC-011)
- Volume 3 location (CL-STORAGE-REC-009)
- Display controller identity (CL-DISPLAY-REC-002)

**Phase 2B: Hypothesis Upgrades**
- Review all hypothesis-status claims and run targeted tests.

**Phase 2C: Cross-Validation**
- Verify consistency across subsystems and resolve any new contradictions.

**Phase 2D: Final Review**
- Status distribution check, evidence quality assessment, documentation update.

### Success Criteria

- All verified claims confirmed through analysis.
- All unresolved contradictions resolved or documented as unknowable.
- Hypotheses upgraded or refuted with evidence.
- Error corrections documented in revision history.
- Cross-subsystem consistency verified.

---

## Conclusion

Phase 1 (Systematic Merging) established a documented truth across 9 subsystems by reconciling 189 input claims into 152 authoritative claims.

**Key Achievement:** Multi-tier evidence framework preserved provenance while enabling conflict resolution through E0 ground truth.

**Status:** Phase 1 COMPLETE. Ready for Phase 2 (Technical Validation).

---

Document created: 2026-01-05
Phase 1 Duration: 4 days (2026-01-02 to 2026-01-05)
Next Phase: Technical Validation and Error Correction