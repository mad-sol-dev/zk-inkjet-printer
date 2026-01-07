# Tools

Analysis and automation scripts for ZK-Inkjet reverse engineering.

---

## Ghidra Scripts (scripts/ghidra/)

Scripts for Ghidra-based binary analysis.

### check_small_funcs.py
Counts functions by size buckets inside the firmware flash address range and prints a distribution summary.
Run from Ghidra's Script Manager (Jython).

---

## BSP Parsing Scripts

### extract_bsp_mmio_registers.py
Parses the N32901-3 NonOS BSP headers to extract MMIO register definitions, then writes a JSON register map.
Defaults to `docs/vendor/N32901-3_NonOS_BSP` as the header root and `.re_kb/n32903_registers.json` as output (per script constants).
Run with `python3 tools/scripts/extract_bsp_mmio_registers.py`.

---

## Validation Scripts

### validate_evidence.py
Validates evidence entries in `research/evidence/evidence_*.md` by checking referenced chat logs under `research/Chats/`.
Run with `python3 tools/scripts/validate_evidence.py`.

---

## Usage

Ghidra scripts run inside Ghidra; Python scripts run from the repository root with `python3`.

**Related Documentation:**
- [ANALYSIS_WORKFLOW.md](../ANALYSIS_WORKFLOW.md) - MCP workflow overview
- [CLAUDE.md](../CLAUDE.md) - Agent guidelines for tool usage
