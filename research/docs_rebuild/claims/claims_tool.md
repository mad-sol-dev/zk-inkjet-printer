# TOOL Claims

Propositional claims synthesized from evidence. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## Ghidra MCP Capabilities

### ✅ CL-TOOL-001: Operator Prompt Enforces Allowlist And Single-Step Actions
**Claim:** The Ghidra MCP operator prompt restricts tool usage to a fixed allowlist and requires short, single-action steps per response.

**Evidence:**
- E-TOOL-001: Operator prompt lists the allowed MCP calls.
- E-TOOL-002: Operator prompt mandates one ACTION at a time.

**Status:** ✅ Verified (multiple CONFIG entries define the operator constraints).

**Cross-Reference:** CL-BOOT-002 (operator prompt discipline supported consistent boot chain discovery steps).

**Next Tests:** None required - conclusively established.

---

### ✅ CL-TOOL-002: BATCH Mode Enables Sequential Multi-Step MCP Runs
**Claim:** The MCP operator prompt supports a single BATCH containing multiple sequential ACTION steps and restricts output to one BATCH per message.

**Evidence:**
- E-TOOL-005: BATCH mode allows multiple ACTION steps sequentially.
- E-TOOL-006: Only one BATCH per message is permitted.

**Status:** ✅ Verified (two CONFIG entries define BATCH behavior).

**Cross-Reference:** CL-BOOT-002 (batch querying supports boot chain discovery workflows).

**Next Tests:** Execute a two-step BATCH (list_segments + list_strings) and confirm sequential execution in server logs.

---

### 🔬 CL-TOOL-003: ops_runner Automates ACTION/ARGUMENTS HTTP Dispatch
**Claim:** The proposed ops_runner workflow parses ACTION/ARGUMENTS from chat output and dispatches them to GhidraMCP HTTP endpoints against a local server.

**Evidence:**
- E-TOOL-003: Adapter concept calls /list_*, /get_*, /rename_* endpoints from ACTION/ARGUMENTS.
- E-TOOL-007: ops_runner is instructed to run against local GhidraMCP.
- E-TOOL-008: ops_runner is described as executing HTTP calls to `http://127.0.0.1:8081/...`.

**Status:** 🔬 Hypothesis (analysis/config describing a proposed runner without execution confirmation).

**Cross-Reference:** CL-USB-010 (ops_runner could automate scalar searches used for USB base address work).

**Next Tests:** Run `ops_runner.py` with a known ACTION (e.g., list_segments) and verify HTTP calls and returned summaries.

---

### 🔬 CL-TOOL-004: Autoanalysis Pre-Run Is Recommended For MCP Performance
**Claim:** Running Ghidra autoanalysis before MCP use is recommended to improve performance and focus MCP calls on targeted steps.

**Evidence:**
- E-TOOL-004: Autoanalysis pre-run is recommended for speed.

**Status:** 🔬 Hypothesis (single analysis recommendation without measured confirmation).

**Cross-Reference:** CL-BOOT-002 (autoanalysis supports faster boot-chain exploration).

**Next Tests:** Measure MCP response times before/after autoanalysis on the same binary and compare tool latency.

---

### ✅ CL-TOOL-005: GhidraMCP Server Runs On Port 8080 And Exposes Program Context Selection
**Claim:** The GhidraMCP HTTP server starts on port 8080 and the toolset includes integrated `select_program` and `get_current_program` functions for program context.

**Evidence:**
- E-TOOL-009: Server startup log shows port 8080.
- E-TOOL-010: `select_program` and `get_current_program` are described as integrated.

**Status:** ✅ Verified (ARTIFACT log plus analysis of integrated functions).

**Cross-Reference:** CL-BOOT-002 (program selection is required for boot vs app analysis).

**Next Tests:** Call `project_overview` then `select_program` and verify `get_current_program` reflects the selection.

---

## RE-KB Knowledge Management

### ✅ CL-TOOL-006: RE-KB Stores Knowledge As JSON And Requires MCP-Gated Writes
**Claim:** The RE-KB persists project knowledge as plain JSON in `.re_kb/` and requires MCP tools for modifying structured JSON files.

**Evidence:**
- E-TOOL-011: Knowledge is stored as plain JSON under `.re_kb/`.
- E-TOOL-012: Structured JSON modifications are restricted to MCP tools.

**Status:** ✅ Verified (two CONFIG policy entries).

**Cross-Reference:** CL-USB-010 (USB findings are recorded through RE-KB JSON workflow).

**Next Tests:** Attempt a manual edit and confirm MCP validation rejects non-tool changes or that policy is enforced in workflow docs.

---

### ⚠️ CL-TOOL-007: RE-KB Index Is Rebuildable From Individual Findings
**Claim:** The RE-KB index can be reconstructed entirely from the individual finding files.

**Evidence:**
- E-TOOL-013: Index can always be rebuilt from findings.

**Status:** ⚠️ Supported (single observation of index rebuild property).

**Cross-Reference:** None.

**Next Tests:** Run the index rebuild tool and verify it regenerates `index.json` from existing findings.

---

### ✅ CL-TOOL-008: create_finding And attach_evidence Use Structured Inputs
**Claim:** RE-KB creation and evidence attachment require structured inputs: `create_finding` expects finding data without an id, and `attach_evidence` expects an id plus a single evidence block.

**Evidence:**
- E-TOOL-014: `create_finding` input excludes `id`.
- E-TOOL-015: `attach_evidence` input is id plus one evidence block.

**Status:** ✅ Verified (CONFIG input requirements for both tools).

**Cross-Reference:** CL-USB-010 (USB claims rely on structured evidence attachment).

**Next Tests:** Submit a minimal `create_finding` payload and a follow-up `attach_evidence` call to confirm validation behavior.

---

### ⚠️ CL-TOOL-009: list_findings And get_finding Read From Index And Finding Files
**Claim:** The RE-KB read APIs load `index.json` for filtered listing and read `findings/finding-XXXX.json` for direct retrieval without write access.

**Evidence:**
- E-TOOL-016: `list_findings` loads `index.json` and applies filters.
- E-TOOL-017: `get_finding` loads the finding file without write access.

**Status:** ⚠️ Supported (two observational behaviors across read tools).

**Cross-Reference:** None.

**Next Tests:** Call `list_findings` with a status filter and `get_finding` for a known id to verify read-only behavior.

---

### 🔬 CL-TOOL-010: Ghidra Context Uses domain_file_id Instead Of program_id
**Claim:** The Ghidra MCP tool surface returns `domain_file_id` for program context rather than a `program_id`.

**Evidence:**
- E-TOOL-018: `get_current_program` returns domain_file_id, not program_id.

**Status:** 🔬 Hypothesis (single analysis statement).

**Cross-Reference:** CL-BOOT-002 (program context is needed to separate BOOT vs APP).

**Next Tests:** Call `get_current_program` on the active session and inspect the returned identifiers.

---

## Codex Agent Orchestration

### ✅ CL-TOOL-011: Codex Agent CWD Tracks Server Process Directory
**Claim:** Codex agents report their working directory as the codex-as-mcp server directory, indicating the server resolves agent CWD via `os.getcwd()` and can mismatch MCP config `cwd` settings.

**Evidence:**
- E-TOOL-021: Agent reported `$HOME/workspace/codex-as-mcp` as CWD.
- E-TOOL-022: MCP config set `cwd` to zk-inkjet-printer but Codex reported codex-as-mcp.
- E-TOOL-023: Server resolves working directory via `os.getcwd()`.

**Status:** ✅ Verified (observed CWD plus configuration mismatch explained by server behavior).

**Cross-Reference:** None.

**Next Tests:** Spawn an agent after setting `CODEX_AGENT_CWD` or removing `--directory` to confirm the working directory changes.

---

### ⚠️ CL-TOOL-012: Codex Agent Spawning Uses spawn_agent Tool Calls
**Claim:** Codex agent orchestration uses the `codex:spawn_agent` tool with a prompt to query runtime state such as the working directory.

**Evidence:**
- E-TOOL-019: Plan to spawn Codex agent to check working directory.
- E-TOOL-020: `codex:spawn_agent` tool is used with a prompt.

**Status:** ⚠️ Supported (two observations of spawn workflow).

**Cross-Reference:** None.

**Next Tests:** Issue a `spawn_agent` call that returns `pwd` and record the result in the session log.

---

### ✅ CL-TOOL-013: Codex spawn_agent Supports Timeout Parameters
**Claim:** The Codex MCP server supports `timeout_seconds` for `spawn_agent` and per-agent overrides for `spawn_agents_parallel`.

**Evidence:**
- E-TOOL-024: `spawn_agent` timeout_seconds parameter (default 8 hours).
- E-TOOL-025: `spawn_agents_parallel` supports per-agent timeout overrides.

**Status:** ✅ Verified (CONFIG notes describe timeout parameter support for both APIs).

**Cross-Reference:** None.

**Next Tests:** Spawn a short-timeout agent and confirm timeout handling in the server response.

---

## Analysis Infrastructure Setup

### 🔬 CL-TOOL-014: BSP Header Import Targets Ghidra Datatype Generation
**Claim:** Nuvoton N32903 BSP headers are imported into Ghidra 11.4.2 on Linux to generate datatypes for reverse engineering.

**Evidence:**
- E-TOOL-026: BSP header import is described as the goal for datatype generation.

**Status:** 🔬 Hypothesis (single observation of intent without confirmation of import success).

**Cross-Reference:** CL-SOC-001 (BSP types support SoC identification and register mapping).

**Next Tests:** Import the BSP headers into Ghidra and verify new datatypes appear in the Data Type Manager.

---

### ⚠️ CL-TOOL-015: Keil Keyword Mitigations Use Preprocessor Defines And Shim Parsing
**Claim:** Ghidra C-Parser issues with Keil `__inline` are mitigated by defining `__inline=` in Parse C Source settings and parsing a shim header via the Data Type Manager.

**Evidence:**
- E-TOOL-027: Keil `__inline` causes Ghidra parser failure.
- E-TOOL-028: Parse C Source defines include `__inline=`.
- E-TOOL-029: Shim header is parsed via Data Type Manager.

**Status:** ⚠️ Supported (analysis plus configuration steps describe the mitigation).

**Cross-Reference:** CL-SOC-001 (datatype import supports SoC register and type analysis).

**Next Tests:** Apply the `__inline=` define and shim workflow, then confirm parsing completes without `UINT32` last-valid errors.

---

### ⚠️ CL-TOOL-016: Correct Base Address And Language Are Required For Auto-Analysis
**Claim:** Ghidra auto-analysis for ARMv5T firmware relies on setting the correct base address (0x02000000) and the ARM v5T little-endian language definition to avoid bad instruction errors.

**Evidence:**
- E-TOOL-030: Import settings specify base address and ARM v5T little-endian language.

**Status:** ⚠️ Supported (single detailed analysis statement).

**Cross-Reference:** CL-BOOT-002 (proper analysis settings enable boot-chain investigation).

**Next Tests:** Import the same image with incorrect base address and compare error bookmarks versus the correct configuration.

---

### 🔬 CL-TOOL-017: Ghidra Headless Wrapper Supports Scripted Disassembly
**Claim:** The `./scripts/gh.sh` wrapper launches Ghidra headless (analyzeHeadless) and enables scripted disassembly workflows.

**Evidence:**
- E-TOOL-031: Headless wrapper launch is observed with analyzeHeadless banner and scripted disassembly use.

**Status:** 🔬 Hypothesis (single observation without repeated confirmation).

**Cross-Reference:** CL-USB-010 (headless workflows can automate USB analysis runs).

**Next Tests:** Run `./scripts/gh.sh -help | head` and a scripted import to confirm headless operation on the target project.

---
