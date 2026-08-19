# TOOL Reconciled Claims (Phase 2C-3)

Authority order: E0 > E3-New > E1 > E3-Old > E4 (E2 = context only).

---

## CL-TOOL-REC-001: MCP Operator Prompt Uses Allowlist And Single-Action Steps

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** The Ghidra MCP operator prompt restricts tool usage to a fixed allowlist and requires single-action steps.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-001 (allowlist), E-TOOL-002 (single ACTION)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** None required.

**Tags:** tool, mcp, workflow

---

## CL-TOOL-REC-002: MCP BATCH Mode Supports Sequential Actions

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** The MCP prompt supports a single BATCH with multiple sequential ACTION steps and limits output to one BATCH per message.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-005 (BATCH multi-step), E-TOOL-006 (one BATCH per message)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Run a two-step BATCH (list_functions, list_strings) and confirm sequential execution.

**Tags:** tool, mcp, batch

---

## CL-TOOL-REC-003: ops_runner Automates ACTION/ARGUMENTS HTTP Calls

**Status:** hypothesis
**Confidence:** 0.55
**Authority:** E1

**Statement:** The proposed ops_runner workflow parses ACTION/ARGUMENTS and dispatches HTTP calls to GhidraMCP endpoints.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-003 (ACTION/ARGUMENTS adapter), E-TOOL-007 (run against local MCP), E-TOOL-008 (HTTP execution)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-003

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Execute an ops_runner script against the local MCP and verify responses.

**Tags:** tool, mcp, automation

---

## CL-TOOL-REC-004: Autoanalysis Pre-Run Is Recommended For MCP Performance

**Status:** hypothesis
**Confidence:** 0.55
**Authority:** E1

**Statement:** Running Ghidra autoanalysis before MCP use is recommended to improve performance.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-004 (autoanalysis pre-run recommendation)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-004

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Benchmark MCP response time before and after autoanalysis.

**Tags:** tool, ghidra, autoanalysis

---

## CL-TOOL-REC-005: GhidraMCP Server Uses Port 8080 And Program Selection Calls

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** The GhidraMCP server starts on port 8080 and supports select_program/get_current_program for program context selection.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-009 (server port 8080 log), E-TOOL-010 (select_program/get_current_program)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-005

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Call project_overview -> select_program and verify get_current_program.

**Tags:** tool, ghidra, mcp

---

## CL-TOOL-REC-006: RE-KB Stores JSON In research/findings/.re_kb

**Status:** verified
**Confidence:** 0.90
**Authority:** E0

**Statement:** The RE-KB stores project data as JSON files under research/findings/.re_kb with index.json and findings/ entries.

**Evidence (All Tiers):**
- **E0:** `research/findings/.re_kb/index.json`, `research/findings/.re_kb/findings/`
- **E1:** E-TOOL-011 (plain JSON storage), E-TOOL-012 (writes gated through MCP)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-006

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Create a new finding via MCP and confirm JSON persisted under `.re_kb/findings/`.

**Tags:** tool, re-kb, storage

---

## CL-TOOL-REC-007: RE-KB Index Is Rebuildable From Findings

**Status:** supported
**Confidence:** 0.70
**Authority:** E1

**Statement:** The RE-KB index can be reconstructed from individual finding files.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-013 (index rebuild statement)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-007

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Run the index rebuild tool and compare regenerated index.json.

**Tags:** tool, re-kb, index

---

## CL-TOOL-REC-008: create_finding And attach_evidence Require Structured Inputs

**Status:** verified
**Confidence:** 0.85
**Authority:** E1

**Statement:** RE-KB create_finding expects data without id and attach_evidence expects an id plus a single evidence block.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-014 (create_finding input), E-TOOL-015 (attach_evidence input)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-008

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Submit a minimal create_finding payload and attach evidence to confirm validation.

**Tags:** tool, re-kb, schema

---

## CL-TOOL-REC-009: list_findings And get_finding Are Read-Only Queries

**Status:** supported
**Confidence:** 0.70
**Authority:** E1

**Statement:** list_findings reads index.json with filters and get_finding reads the finding JSON without write access.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-016 (list_findings), E-TOOL-017 (get_finding)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-009

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Run list_findings with a filter and confirm results match index.json.

**Tags:** tool, re-kb, read-only

---

## CL-TOOL-REC-010: Ghidra MCP Returns domain_file_id For Program Context

**Status:** hypothesis
**Confidence:** 0.55
**Authority:** E1

**Statement:** get_current_program returns domain_file_id rather than program_id.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-018 (domain_file_id mention)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-010

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Call get_current_program and inspect returned fields.

**Tags:** tool, ghidra, context

---

## CL-TOOL-REC-011: Codex Agent CWD Follows MCP Server Process CWD

**Status:** verified
**Confidence:** 0.90
**Authority:** E0

**Statement:** Codex agent CWD is inherited from the MCP server process (os.getcwd), which can differ from the configured project cwd.

**Evidence (All Tiers):**
- **E0:** `.mcp.json` (CODEX_AGENT_CWD configured)
- **E1:** E-TOOL-021 (reported CWD), E-TOOL-022 (cwd mismatch), E-TOOL-023 (os.getcwd behavior)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-011

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Spawn an agent after changing CODEX_AGENT_CWD and confirm reported cwd.

**Tags:** tool, codex, cwd

---

## CL-TOOL-REC-012: Codex Agents Are Spawned With spawn_agent

**Status:** supported
**Confidence:** 0.70
**Authority:** E1

**Statement:** Codex agent orchestration uses the spawn_agent tool with a prompt to query runtime state.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-019 (spawn plan), E-TOOL-020 (spawn_agent tool use)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-012

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Spawn an agent and have it return pwd to confirm the flow.

**Tags:** tool, codex, spawn_agent

---

## CL-TOOL-REC-013: spawn_agent Supports timeout_seconds

**Status:** verified
**Confidence:** 0.85
**Authority:** E1

**Statement:** spawn_agent supports timeout_seconds and spawn_agents_parallel supports per-agent overrides.

**Evidence (All Tiers):**
- **E0:** `.mcp.json` (MCP request timeout env variables)
- **E1:** E-TOOL-024 (spawn_agent timeout), E-TOOL-025 (parallel overrides)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-013

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Run a short timeout and confirm timeout handling.

**Tags:** tool, codex, timeout

---

## CL-TOOL-REC-014: BSP Headers Imported For Ghidra Datatypes

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E1

**Statement:** BSP headers are imported into Ghidra to generate datatypes for analysis.

**Evidence (All Tiers):**
- **E0:** `tools/scripts/ghidra/extract_bsp_mmio_registers.py` (BSP extraction tooling)
- **E1:** E-TOOL-026 (BSP header import context)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-014

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Import BSP headers in Ghidra and confirm new datatypes appear.

**Tags:** tool, bsp, ghidra

---

## CL-TOOL-REC-015: Keil __inline Mitigation Uses Preprocessor Defines And Shim

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** Ghidra C-parser issues with Keil __inline are mitigated by defining __inline= and parsing a shim header.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-027 (parser failure), E-TOOL-028 (define __inline=), E-TOOL-029 (shim header parsing)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-015

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Apply the define/shim workflow and verify parsing succeeds.

**Tags:** tool, ghidra, c-parser

---

## CL-TOOL-REC-016: Ghidra Import Requires Base Address And ARMv5T Language

**Status:** supported
**Confidence:** 0.70
**Authority:** E1

**Statement:** Correct Ghidra import requires base address 0x02000000 and ARM v5T little-endian language to avoid bad instruction errors.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-030 (base address + language requirement)
- **E4:** E-OLD-TOOL-002 (addressing conventions, 0x200000 base) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-016
- E4: CL-OLD-TOOL-002 (partial overlap)

**Superseded Evidence:** E-OLD-TOOL-002 uses 0x200000 base and may be outdated; current imports use 0x02000000.

**Contradictions Resolved:** Address base mismatch noted between E4 conventions and current import settings.

**Next Test:** Import with 0x00200000 vs 0x02000000 and compare disassembly quality.

**Tags:** tool, ghidra, import

---

## CL-TOOL-REC-017: Headless Ghidra Wrapper Supports Scripted Disassembly

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E1

**Statement:** The headless wrapper (analyzeHeadless) is used for scripted disassembly workflows.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** E-TOOL-031 (headless wrapper observed)
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-TOOL-017

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Run the wrapper and confirm analyzeHeadless banner in logs.

**Tags:** tool, ghidra, headless

---

## CL-TOOL-REC-018: MCP Workflow Lists Core Ghidra Bridge Tools

**Status:** supported
**Confidence:** 0.70
**Authority:** E4

**Statement:** The MCP workflow defines a core inventory of Ghidra bridge tools for reproducible analysis.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** None
- **E4:** E-OLD-TOOL-001 (tooling inventory)
- **E2:** None

**Source Claims:**
- E4: CL-OLD-TOOL-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Update the inventory to match current MCP server interfaces.

**Tags:** tool, mcp, workflow

---

## CL-TOOL-REC-019: Legacy UI Decode Output Is Incomplete

**Status:** supported
**Confidence:** 0.65
**Authority:** E4

**Statement:** Legacy UI decode scripts produce a 480x480 PNG with artifacts, indicating incomplete decoding.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** None
- **E4:** E-OLD-TOOL-003 (legacy decode artifacts)
- **E2:** None

**Source Claims:**
- E4: CL-OLD-TOOL-003

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Compare decoded output to a firmware-extracted render routine.

**Tags:** tool, ui-decode, legacy

---

## CL-TOOL-REC-020: MCP Example Uses Full Caller Enumeration

**Status:** supported
**Confidence:** 0.70
**Authority:** E4

**Statement:** MCP workflow example enumerates all 12 pin-mux callers to confirm GPIO configuration.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** None
- **E4:** E-OLD-TOOL-004 (systematic pin-mux caller analysis)
- **E2:** None

**Source Claims:**
- E4: CL-OLD-TOOL-004

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Repeat the enumeration on the current APP.bin to confirm caller count.

**Tags:** tool, mcp, verification

---

## CL-TOOL-REC-021: Incremental Claims Strategy Adopted

**Status:** supported
**Confidence:** 0.70
**Authority:** E2

**Statement:** The project adopted an incremental, subsystem-by-subsystem claims strategy after token-claim failures.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** None
- **E4:** None
- **E2:** E2-TOOL-019 (strategy evolution)

**Source Claims:**
- E1: None
- E4: None

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** None required.

**Tags:** tool, strategy, methodology

---

## CL-TOOL-REC-022: Multi-Tier Evidence Framework Established

**Status:** supported
**Confidence:** 0.75
**Authority:** E2

**Statement:** A multi-tier evidence framework (E0/E1/E2/E3-Old/E3-New) with [ghidra-v1] versioning was established to manage conflicting sources.

**Evidence (All Tiers):**
- **E0:** None
- **E1:** None
- **E4:** None
- **E2:** E2-TOOL-021 (framework design and versioning policy)

**Source Claims:**
- E1: None
- E4: None

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** None required.

**Tags:** tool, framework, evidence
