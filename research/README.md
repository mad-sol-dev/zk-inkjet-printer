# ZK-Inkjet Printer - Research Documentation

**Project:** USB-CDC Implementation for ZK-Inkjet Printer  
**Hardware:** Nuvoton N32903U5DN SoC, HP45 Printhead  
**Goal:** Automatic lithium cell labeling via USB virtual serial port

---

## Quick Navigation

### Main Reference
- [System Understanding](./system_understanding.md) - Master reference document (Phase 1 Reconciliation)

### Phase A: SD Image Analysis (COMPLETED)
- [Phase A Summary](./phase_a_sd_analysis/SUMMARY.md) - Quick overview of findings
- [Final Summary](./phase_a_sd_analysis/phase_a_final_summary.md) - Complete Phase A results with corrections
- [Methods](./phase_a_sd_analysis/methods_phase_a_sd_analysis.md) - Analysis methodology and tools used

**Key Findings:**
- [Boot Locations Verified](./phase_a_sd_analysis/boot_locations_verified.md) - BOOT.bin structure and locations
- [Boot Header Structure](./phase_a_sd_analysis/boot_header_structure.md) - IBR 32-byte header analysis
- [Volume Identification](./phase_a_sd_analysis/volume_identification_corrected.md) - FAT volumes verified

**Updates Pending:**
- [System Understanding Updates](./phase_a_sd_analysis/system_understanding_updates_phase_a.md) - Changes to apply to main doc

### Phase B: Firmware Analysis (NOT STARTED)
*Coming next: Ghidra analysis of APP.bin for volume mount code and USB controller usage*

### Supporting Data
- [N32903 Registers](./reference/n32903_registers.json) - BSP register definitions
- [Phase A Artifacts](./phase_a_sd_analysis/artifacts/) - Raw analysis outputs

### Other Directories
- `docs_rebuild/` - Documentation rebuild work
- `findings/` - Structured findings database
- `sessions/` - Analysis session logs

---

## Phase A Achievements

### Verified Ground Truth:
- IBR header structure: 32 bytes @ 0x200 with `0xA5 [ZBW...WBZ] 0xA5` pattern
- BOOT.bin locations: Raw @ 0x200 (with header), deleted copy in Volume 2
- Three FAT volumes identified and inspected:
  - Volume 1 @ 0x04000000: 512 MB fonts/resources
  - Volume 2 @ 0x24007E00: 256 MB system/staging
  - Volume 3 @ 0x2A61BE00: 64 MB "MINI" (empty, user USB drive)

### Confidence Levels:
- **High (Verified):** Boot structure, FAT volumes, Volume 3 identity
- **Medium (Supported):** Update workflow, Volume 2 staging role
- **Low (Hypothesis):** Volume mount mapping (0:/ location), IBR header field meanings

---

## How to Use This Documentation

### For Initial Review:
1. Start with [Phase A Summary](./phase_a_sd_analysis/SUMMARY.md)
2. Read [Phase A Final Summary](./phase_a_sd_analysis/phase_a_final_summary.md) for complete details
3. Check [System Understanding](./system_understanding.md) for overall system knowledge

### For Specific Topics:
- **Boot Process:** [Boot Locations](./phase_a_sd_analysis/boot_locations_verified.md) + [Header Structure](./phase_a_sd_analysis/boot_header_structure.md)
- **Storage/Volumes:** [Volume Identification](./phase_a_sd_analysis/volume_identification_corrected.md)
- **Methods/Tools:** [Phase A Methods](./phase_a_sd_analysis/methods_phase_a_sd_analysis.md)

### For Development:
- [System Understanding Updates](./phase_a_sd_analysis/system_understanding_updates_phase_a.md) - Apply these changes before Phase B

---

## Next Steps (Phase B)

**Priority Tasks:**
1. Verify firmware volume mount code (f_mount("3:/") -> LBA 0x2A61BE00)
2. Locate USB controller usage (USBD_BA @ 0xB1008000)
3. Find update system code (file detection, header injection)
4. Identify Volume 0:/ mapping

**Tools Required:**
- Ghidra with N32903 BSP headers loaded
- ghidra-mcp for remote analysis
- RE-KB for findings management

---

## Project Timeline

- **2026-01-05:** Phase 1 Reconciliation complete (152 claims, 9 subsystems)
- **2026-01-07:** Phase A complete (SD image ground truth established)
- **Next:** Phase B (firmware analysis)

---

**Last Updated:** 2026-01-07  
**Status:** Phase A Complete, Phase B Pending
