# TOOL Evidence (Old Docs)

Extracted evidence from research/old_docs/ (E4 tier). Format: Content (1-3 lines) + Source + Date + Type + Provenance + Tags.

---

### E-OLD-TOOL-001: MCP Tooling Inventory (Ghidra Bridge)
- **Content:** Workflow lists core Ghidra bridge tools: search_scalars, search_strings, search_functions, search_xrefs_to, disassemble_at, read_bytes, list_functions_in_range.
- **Source:** old_docs/methodology/mcp_workflow.md#MCP-Tools-Available
- **Date:** 2025-11-03
- **Type:** REFERENCE
- **Provenance:** None
- **Tags:** mcp, ghidra, tooling

### E-OLD-TOOL-002: Addressing Conventions (VA vs File Offset)
- **Content:** Virtual address equals 0x200000 + file offset; Thumb targets keep LSB set and MMIO addresses are labeled explicitly.
- **Source:** old_docs/CONVENTIONS.md#Addressing-Conventions
- **Date:** 2025-11-03
- **Type:** REFERENCE
- **Provenance:** None
- **Tags:** conventions, addressing, va, thumb

### E-OLD-TOOL-003: Legacy UI Decode Produces 480x480 PNG With Artifacts
- **Content:** Legacy UI decode script outputs a 480x480 PNG with residual artifacts; brute-force decoding is incomplete.
- **Source:** old_docs/guide/operations.md#Quick-Commands
- **Date:** 2025-11-03
- **Type:** OBSERVATION
- **Provenance:** None
- **Tags:** tooling, ui-decode, legacy, artifacts

### E-OLD-TOOL-004: Systematic MCP Verification Example
- **Content:** MCP workflow example analyzes all 12 pin-mux callers to confirm only GPB[0] and GPB[6] are configured, with GPB[2-5] unused.
- **Source:** old_docs/methodology/mcp_workflow.md#Example-Complete-Analysis-Flow
- **Date:** 2025-11-03
- **Type:** ANALYSIS
- **Provenance:** None
- **Tags:** mcp, verification, gpio, methodology
