# TOOL Claims (Old Docs)

Propositional claims synthesized from old_docs (E4 tier).

---

## CL-OLD-TOOL-001: MCP Workflow Standardizes Ghidra Tool Usage
- **Status:** supported
- **Confidence:** 0.70
- **Statement:** The MCP workflow prescribes a standard set of Ghidra bridge tools (search_scalars, search_strings, search_functions, search_xrefs_to, disassemble_at, read_bytes, list_functions_in_range) for reproducible analysis.
- **Evidence:**
  - E4: E-OLD-TOOL-001 (tooling inventory)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Align tool naming with current MCP server interfaces and update workflow docs.
- **Tags:** tool, mcp, ghidra, workflow
- **Cross-Reference:** E1 CL-TOOL-001 (partial overlap)

## CL-OLD-TOOL-002: Addressing Conventions Use VA = 0x200000 + File Offset
- **Status:** supported
- **Confidence:** 0.75
- **Statement:** Addressing conventions define virtual addresses as 0x200000 + file_offset with Thumb LSB handling and explicit MMIO labeling.
- **Evidence:**
  - E4: E-OLD-TOOL-002 (addressing conventions)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Validate the base offset against current Ghidra project settings.
- **Tags:** tool, conventions, addressing
- **Cross-Reference:** None (unique)

## CL-OLD-TOOL-003: Legacy UI Decode Is Incomplete
- **Status:** supported
- **Confidence:** 0.65
- **Statement:** Legacy UI decode scripts produce a 480x480 PNG but leave residual artifacts, indicating brute-force decode is incomplete.
- **Evidence:**
  - E4: E-OLD-TOOL-003 (legacy decode output)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Extract the firmware decode routine and compare output to the legacy PNG.
- **Tags:** tool, ui-decode, legacy
- **Cross-Reference:** None (unique)

## CL-OLD-TOOL-004: MCP Example Uses Full Caller Enumeration
- **Status:** supported
- **Confidence:** 0.70
- **Statement:** MCP workflow demonstrates exhaustive caller analysis (12 pin-mux callers) to confirm GPIO configuration findings.
- **Evidence:**
  - E4: E-OLD-TOOL-004 (systematic verification example)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Repeat the enumeration with current APP.bin to confirm call-site count.
- **Tags:** tool, methodology, verification
- **Cross-Reference:** E3-Old CL-RKO-HARDWARE-001 (method overlap)
