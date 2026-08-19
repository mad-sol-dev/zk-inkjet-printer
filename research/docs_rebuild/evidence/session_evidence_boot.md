# BOOT Evidence (E2 Tier: Sessions)

**Source:** research/sessions/*.md (chronological research logs)
**Tier:** E2 (navigation/context layer, unique session-level evidence)
**Note:** E2 tier captures methodology shifts and analysis approach changes not present in E1/E3 tiers.

---

## Firmware Analysis Methodology

### E2-BOOT-015: Ghidra Optimization Impact and ARM/Thumb Verification
- **Session ID:** S-015 (2025-12-27)
- **File:** sessions/2025-12-27_arm-thumb-analysis-mmio-extraction.md
- **Type:** Methodology shift documentation
- **Summary:** Critical session documenting Ghidra analysis optimization impact (37k → 1.3k functions) and ARM/Thumb mixed-mode verification. Explains why earlier E1 and E3-Old evidence may contain inaccuracies due to over-aggressive auto-analysis. Established evidence versioning policy with [ghidra-v1] tagging.
- **Key Evidence:**
  - Pre-optimization (ghidra-v1): 37,000+ functions detected (over-detection, false positives)
  - Post-optimization (current): 1,300 functions with refined settings
  - Optimization settings changed:
    * Aggressive Instruction Finder: OFF (was ON, caused false ARM/Thumb detection)
    * Non-Returning Functions: CAUTIOUS (was aggressive)
    * Reference options: Conservative (was permissive)
  - ARM/Thumb verification:
    * ARM region: 0x00200000-0x0020FFFF (boot code, init functions)
    * Thumb region: 0x00210000-0x0021FFFF (application logic)
    * Mixed-mode ratio: ~18% Thumb, ~82% ARM
    * Interworking validated: `ADD r12,pc,#1; BX r12` mode-switch stubs found
  - Impact on evidence:
    * E1 Chat evidence: Some based on pre-optimization analysis (may be outdated)
    * E3-Old RE-KB findings: ALL based on pre-optimization (tagged [ghidra-v1])
    * E3-New RE-KB findings: Post-optimization (no version tag needed)
  - MMIO extraction: 1544 registers extracted from BSP headers during this session
- **Outcome:** Evidence versioning policy established, finding-0001 created (ARM/Thumb mixed-mode), finding-0002 created (MMIO register map)
- **Research Value:** Documents critical methodology shift, explains why scalar searches (0xB8007000, 0xB1008000) found zero results, establishes need for pattern-based searches
- **Cross-Reference:** CL-RKN-BOOT-001 (ARM/Thumb mixed-mode), CL-RKN-SOC-001 (MMIO map), CONTRADICTION-USB-001 (explains why old USB base address claims are unreliable)
- **Evidence Versioning:** All E1 and E3-Old evidence predating this session should be considered potentially affected by over-detection
- **Tags:** boot, methodology, ghidra, optimization, arm-thumb, versioning, evidence-quality
- **Created:** 2025-12-27
- **Evidence Tier:** E2 (methodology documentation)
- **Critical Impact:** Invalidates firmware address searches from pre-optimization era, requires pattern-based re-analysis

---

## Integration Notes

**E2-BOOT Evidence Type:** Methodology shift documentation that explains:
1. Why earlier analysis may be unreliable (Ghidra over-detection)
2. How analysis approach changed (optimization settings)
3. What evidence versioning policy means ([ghidra-v1] tagging)

**Relationship to Other Tiers:**
- **E1 Tier:** Some E1 Chat evidence from Nov-Dec 2025 may be based on ghidra-v1 analysis
- **E3-Old:** ALL E3-Old evidence is pre-optimization (31 findings tagged [ghidra-v1])
- **E3-New:** finding-0001 and finding-0002 created during this optimization session

**CONTRADICTION-USB-001 Explanation:** E2-BOOT-015 explains why E1 CL-USB-010 and E3-Old CL-RKO-USB-002 both claimed USB base at 0xB8007000 - both used pre-optimization Ghidra which over-detected function boundaries and may have misidentified literal pools. Post-optimization scalar searches found ZERO references to either 0xB8007000 or 0xB1008000, requiring pattern-based search approach.

**Evidence Quality Implications:**
- Ghidra-v1 evidence: Useful for general understanding, but specific addresses/functions may be wrong
- Post-optimization evidence: Higher confidence, but requires pattern searches (MOV/MOVT, base+offset)
- BSP headers (E0 tier): Ground truth, always authoritative

---

*Evidence file created: 2026-01-04*
*E2 Tier: Methodology and quality documentation*
