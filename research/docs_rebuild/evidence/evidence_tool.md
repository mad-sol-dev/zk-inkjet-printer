# TOOL Evidence

Raw facts extracted from chat transcripts. No interpretation, only concrete observations.

---

## Ghidra MCP Integration

### E-TOOL-001: MCP Call Allowlist In Operator Prompt
- **Quote:** "- Only use these MCP calls: list_segments, list_functions, list_strings,
  get_function_by_address, decompile_function_by_address, get_function_xrefs,
  rename_function_by_address, set_decompiler_comment, set_function_prototype."
- **Source:** Chats/27_GPT_GhidraMCP_und_Open-WebUI_17.10.2025.json#msg=1
- **Date:** 2025-10-17
- **Type:** CONFIG
- **Tags:** ghidra-mcp, allowlist, operator-prompt, tool-calls

### E-TOOL-002: Single-Action Step Discipline
- **Quote:** "- Prefer short, incremental steps. One ACTION at a time."
- **Source:** Chats/27_GPT_GhidraMCP_und_Open-WebUI_17.10.2025.json#msg=1
- **Date:** 2025-10-17
- **Type:** CONFIG
- **Tags:** workflow, action-template, deterministic, mcp

### E-TOOL-003: ACTION/ARGUMENTS Adapter Calls HTTP Endpoints
- **Quote:** "- Nimmt „ACTION/ARGUMENTS“ aus der Chat-Nachricht, ruft die HTTP-Endpoints (/list_*, /get_*, /rename_*) auf."
- **Source:** Chats/27_GPT_GhidraMCP_und_Open-WebUI_17.10.2025.json#msg=1
- **Date:** 2025-10-17
- **Type:** ANALYSIS
- **Tags:** ops-runner, http-endpoints, action-arguments, automation

### E-TOOL-004: Autoanalysis Pre-Run For MCP Speed
- **Quote:** "- **Geschwindigkeit:** Ghidra-Autoanalysis vorab durchlaufen lassen; MCP dann nur für gezielte Schritte."
- **Source:** Chats/27_GPT_GhidraMCP_und_Open-WebUI_17.10.2025.json#msg=1
- **Date:** 2025-10-17
- **Type:** ANALYSIS
- **Tags:** autoanalysis, performance, ghidra, mcp

### E-TOOL-005: BATCH Mode For Multi-Step MCP Runs
- **Quote:** "You may also output a single BATCH with multiple ACTION steps to be executed sequentially:"
- **Source:** Chats/27_GPT_GhidraMCP_und_Open-WebUI_17.10.2025.json#msg=13
- **Date:** 2025-10-17
- **Type:** CONFIG
- **Tags:** batch-mode, mcp, operator-prompt, multi-step

### E-TOOL-006: BATCH Output Constraint
- **Quote:** "Return only one BATCH per message when you have a clear multi-step plan."
- **Source:** Chats/27_GPT_GhidraMCP_und_Open-WebUI_17.10.2025.json#msg=13
- **Date:** 2025-10-17
- **Type:** CONFIG
- **Tags:** batch-mode, mcp, output-format, operator-prompt

### E-TOOL-007: ops_runner Execution Against Local MCP
- **Quote:** "Speichere als `ops_runner.py` und starte ihn gegen deinen lokalen GhidraMCP (Port ggf. anpassen)."
- **Source:** Chats/27_GPT_GhidraMCP_und_Open-WebUI_17.10.2025.json#msg=13
- **Date:** 2025-10-17
- **Type:** CONFIG
- **Tags:** ops-runner, ghidra-mcp, local-server, tooling

### E-TOOL-008: ops_runner Parsing And HTTP Execution
- **Quote:** "Wenn du willst, schreibe ich dir **jetzt** einen 40-Zeilen-Python-„ops_runner“, der ACTION/ARGUMENTS aus dem Chat parst, gegen `http://127.0.0.1:8081/...` ausführt und die Antworten wieder als kompakte Summary zurückgibt."
- **Source:** Chats/27_GPT_GhidraMCP_und_Open-WebUI_17.10.2025.json#msg=1
- **Date:** 2025-10-17
- **Type:** ANALYSIS
- **Tags:** ops-runner, http, automation, ghidra-mcp

### E-TOOL-009: MCP HTTP Server Startup Log
- **Quote:** "2025-11-23\t22:52:04\tINFO\t(GhidraMCPPlugin) GhidraMCP HTTP server started on port 8080"
- **Source:** Chats/77_GEM_Ghidra-Server_Gestartet_Projekt_Geöffnet_29122025_29.12.2025.json#msg=0
- **Date:** 2025-12-29
- **Type:** ARTIFACT
- **Tags:** ghidra-mcp, server, port-8080, log

### E-TOOL-010: Program Selection Functions Integrated
- **Quote:** "I've been examining the current implementation of program selection within GhidraMCP. The `select_program` and `get_current_program` functions seem to be successfully integrated."
- **Source:** Chats/77_GEM_Ghidra-Server_Gestartet_Projekt_Geöffnet_29122025_29.12.2025.json#msg=1
- **Date:** 2025-12-29
- **Type:** ANALYSIS
- **Tags:** select_program, get_current_program, ghidra-mcp, program-context

---

## RE-KB Workflow

### E-TOOL-011: RE-KB Uses Plain JSON Storage
- **Quote:** "- All project knowledge must be stored as **plain JSON files** inside `.re_kb/` in the project repo."
- **Source:** Chats/46_GPT_Ghidra_MCPd_Integration_26.11.2025.json#msg=1
- **Date:** 2025-11-26
- **Type:** CONFIG
- **Tags:** re-kb, json, storage, policy

### E-TOOL-012: RE-KB Writes Through MCP Tools Only
- **Quote:** "- Structured JSON under `.re_kb/` must **only** be modified through MCP tools."
- **Source:** Chats/46_GPT_Ghidra_MCPd_Integration_26.11.2025.json#msg=1
- **Date:** 2025-11-26
- **Type:** CONFIG
- **Tags:** re-kb, write-gate, mcp-tools, policy

### E-TOOL-013: Index Rebuild From Findings
- **Quote:** "The index can always be rebuilt from the individual findings."
- **Source:** Chats/46_GPT_Ghidra_MCPd_Integration_26.11.2025.json#msg=1
- **Date:** 2025-11-26
- **Type:** OBSERVATION
- **Tags:** re-kb, index, rebuild, findings

### E-TOOL-014: create_finding Input Requirements
- **Quote:** "* Input: finding data **without** `id` (type, status, title, optional summary/tags/evidence)."
- **Source:** Chats/46_GPT_Ghidra_MCPd_Integration_26.11.2025.json#msg=1
- **Date:** 2025-11-26
- **Type:** CONFIG
- **Tags:** create_finding, schema, re-kb, workflow

### E-TOOL-015: attach_evidence Input Requirements
- **Quote:** "* Input: id + one evidence block."
- **Source:** Chats/46_GPT_Ghidra_MCPd_Integration_26.11.2025.json#msg=1
- **Date:** 2025-11-26
- **Type:** CONFIG
- **Tags:** attach_evidence, re-kb, evidence, workflow

### E-TOOL-016: list_findings Behavior
- **Quote:** "* Behavior: loads `index.json`, applies the filters, and enforces the batch limit guard."
- **Source:** Chats/46_GPT_Ghidra_MCPd_Integration_26.11.2025.json#msg=1
- **Date:** 2025-11-26
- **Type:** OBSERVATION
- **Tags:** list_findings, index, filters, batch-limit

### E-TOOL-017: get_finding Read-Only Behavior
- **Quote:** "* Behavior: loads `findings/finding-XXXX.json` without requiring write access."
- **Source:** Chats/46_GPT_Ghidra_MCPd_Integration_26.11.2025.json#msg=1
- **Date:** 2025-11-26
- **Type:** OBSERVATION
- **Tags:** get_finding, read-only, re-kb, findings

### E-TOOL-018: Ghidra Tool Returns domain_file_id
- **Quote:** "Looking at the available tools, get_current_program returns domain_file_id, not program_id."
- **Source:** Chats/46_GPT_Ghidra_MCPd_Integration_26.11.2025.json#msg=0
- **Date:** 2025-11-26
- **Type:** ANALYSIS
- **Tags:** re-kb, program-id, domain-file-id, ghidra

---

## Codex/Agent Usage

### E-TOOL-019: Spawn Codex Agent For CWD Check
- **Quote:** "Ich sollte einen Codex-Agenten spawnen und ihn fragen, sein aktuelles Arbeitsverzeichnis zu überprüfen.Ich frage Codex nach seinem aktuellen Arbeitsverzeichnis."
- **Source:** Chats/920_CL_Codex_Verzeichnisstandort_abfragen_15.12.2025.json#msg=1
- **Date:** 2025-12-15
- **Type:** OBSERVATION
- **Tags:** codex, spawn_agent, working-directory, check

### E-TOOL-020: spawn_agent Tool Use
- **Quote:** "Ich verwende den codex:spawn_agent tool mit einem einfachen Prompt.Ich frage Codex nach dem aktuellen Verzeichnis:"
- **Source:** Chats/920_CL_Codex_Verzeichnisstandort_abfragen_15.12.2025.json#msg=2
- **Date:** 2025-12-15
- **Type:** OBSERVATION
- **Tags:** codex, spawn_agent, prompt, tool-use

### E-TOOL-021: Codex CWD Returned From Agent
- **Quote:** "Codex hat geantwortet, dass das aktuelle Arbeitsverzeichnis `$HOME/workspace/codex-as-mcp` ist. Das ist das Verzeichnis des Codex-MCP-Projekts selbst.Codex befindet sich aktuell im Verzeichnis `$HOME/workspace/codex-as-mcp` - also im Verzeichnis des Codex-MCP-Projekts selbst."
- **Source:** Chats/920_CL_Codex_Verzeichnisstandort_abfragen_15.12.2025.json#msg=2
- **Date:** 2025-12-15
- **Type:** OBSERVATION
- **Tags:** codex, cwd, codex-as-mcp, workspace

### E-TOOL-022: MCP Config CWD Mismatch
- **Quote:** "Ah, ich sehe das Problem! In der MCP-Konfiguration ist für den Codex-Server ein `cwd` (oder `pwd`, was wahrscheinlich von Claude Desktop interpretiert wird) auf `$HOME/workspace/zk-inkjet-printer` gesetzt, aber Codex meldet, dass es in `$HOME/workspace/codex-as-mcp` ist."
- **Source:** Chats/920_CL_Codex_Verzeichnisstandort_abfragen_15.12.2025.json#msg=4
- **Date:** 2025-12-15
- **Type:** OBSERVATION
- **Tags:** mcp-config, cwd, codex, mismatch

### E-TOOL-023: codex-as-mcp Uses os.getcwd
- **Quote:** "The server resolves the working directory via ``os.getcwd()`` so it inherits
whatever environment the MCP process currently has."
- **Source:** Chats/920_CL_Codex_Verzeichnisstandort_abfragen_15.12.2025.json#msg=6
- **Date:** 2025-12-15
- **Type:** ANALYSIS
- **Tags:** codex-server, os-getcwd, cwd, process

### E-TOOL-024: spawn_agent Timeout Parameter Added
- **Quote:** "1. `spawn_agent` bekommt jetzt einen `timeout_seconds` Parameter (default 8 Stunden)"
- **Source:** Chats/916_CL_Timeout-inducing_task_for_Codex_14.12.2025.json#msg=4
- **Date:** 2025-12-14
- **Type:** CONFIG
- **Tags:** codex, spawn_agent, timeout, mcp

### E-TOOL-025: spawn_agents_parallel Timeout Overrides
- **Quote:** "6. `spawn_agents_parallel` unterstützt jetzt auch per-agent `timeout_seconds` overrides"
- **Source:** Chats/916_CL_Timeout-inducing_task_for_Codex_14.12.2025.json#msg=4
- **Date:** 2025-12-14
- **Type:** CONFIG
- **Tags:** codex, spawn_agents_parallel, timeout, overrides

---

## Analysis Infrastructure

### E-TOOL-026: BSP Header Import Context
- **Quote:** "Ich versuche gerade, C-Header-Dateien aus einem Nuvoton N32903 BSP (ursprünglich für Keil MDK Compiler) in Ghidra 11.4.2 auf Linux zu importieren, um Datentypen für das Reverse Engineering zu generieren."
- **Source:** Chats/62_GPT_C-Header_Import_in_Ghidra_26.12.2025.json#msg=0
- **Date:** 2025-12-26
- **Type:** OBSERVATION
- **Tags:** ghidra, c-headers, bsp, datatypes

### E-TOOL-027: Keil __inline Breaks Ghidra C-Parser
- **Quote:** "`__inline` ist ein **Keil-Spezialwort** (Keil MDK = „Microcontroller Development Kit“). Ghidras C-Parser kennt das nicht → er stolpert genau nach deinen Basis-Typen (letzter gültiger Datentyp `UINT32`)."
- **Source:** Chats/62_GPT_C-Header_Import_in_Ghidra_26.12.2025.json#msg=1
- **Date:** 2025-12-26
- **Type:** ANALYSIS
- **Tags:** ghidra-cparser, keil, inline, parse-error

### E-TOOL-028: Parse C Source Defines For __inline
- **Quote:** "In Ghidra beim **Parse C Source**-Dialog in den **Preprocessor/Defines** (Makro-Definitionen) aufnehmen:\n\n- `__inline=`"
- **Source:** Chats/62_GPT_C-Header_Import_in_Ghidra_26.12.2025.json#msg=1
- **Date:** 2025-12-26
- **Type:** CONFIG
- **Tags:** ghidra-cparser, parse-c-source, preprocessor, defines

### E-TOOL-029: Parse Shim Header Only
- **Quote:** "Dann in Ghidra **nicht die ganze Headerliste**, sondern **diesen Shim** parsen:\n`Data Type Manager → File → Parse C Source… → ghidra_shim.h`"
- **Source:** Chats/62_GPT_C-Header_Import_in_Ghidra_26.12.2025.json#msg=3
- **Date:** 2025-12-26
- **Type:** CONFIG
- **Tags:** ghidra-shim, parse-c-source, datatypes, workflow

### E-TOOL-030: Auto-Analyze Import Settings
- **Quote:** "Vergewissern Sie sich, dass beim Import die **Basisadresse** richtig gesetzt ist (hier `0x02000000`) und die **CPU-Sprachdefinition** “ARM v5T little-endian” gewählt wurde. Eine falsche Adresse oder Endianness führt zu vielen *Bad Instruction*-Fehlern und falsch interpretiertem Code."
- **Source:** Chats/63_GPT_Ghidra_Auto-Analyze_Optionen_27.12.2025.json#msg=5
- **Date:** 2025-12-27
- **Type:** ANALYSIS
- **Tags:** auto-analysis, base-address, armv5t, endianness

### E-TOOL-031: Headless Wrapper Verified
- **Quote:** "• Perfekt—./scripts/gh.sh now launches the Ghidra headless tool (we see the analyzeHeadless usage banner), so we can use it for scripted\n  disassembly."
- **Source:** Chats/17_GPT_Ghidra_headless_troubleshooting_10.10.2025.json#msg=5
- **Date:** 2025-10-10
- **Type:** OBSERVATION
- **Tags:** ghidra-headless, scripts, analyzeHeadless, tooling
