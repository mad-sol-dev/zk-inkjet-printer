# TOOL Subsystem Reconciliation Decisions

**Date:** 2026-01-05
**Reconciler:** Codex (GPT-5.1)
**Input Tiers:** E0, E1, E2, E4

## Decision Summary

- Total Claims Input: 21
- Merged Claims Output: 22 (includes 2 E2-only meta-claims)
- EXACT_MATCH merges: 0
- PARTIAL_OVERLAP merges: 1
- UNIQUE kept: 20
- REFUTED: 0

## Claim-by-Claim Decisions

### CL-TOOL-REC-001: MCP Operator Prompt Uses Allowlist And Single-Action Steps

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-001 (E1)
**Reasoning:** E1 operator prompt constraints are specific and stand alone.
**Authority:** E1
**Evidence Merged:** E-TOOL-001, E-TOOL-002
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-002: MCP BATCH Mode Supports Sequential Actions

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-002 (E1)
**Reasoning:** BATCH rules are a distinct operator prompt constraint.
**Authority:** E1
**Evidence Merged:** E-TOOL-005, E-TOOL-006
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-003: ops_runner Automates ACTION/ARGUMENTS HTTP Calls

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-003 (E1)
**Reasoning:** Proposed workflow only described in E1; not validated.
**Authority:** E1
**Evidence Merged:** E-TOOL-003, E-TOOL-007, E-TOOL-008
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-004: Autoanalysis Pre-Run Is Recommended For MCP Performance

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-004 (E1)
**Reasoning:** Single recommendation in E1.
**Authority:** E1
**Evidence Merged:** E-TOOL-004
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-005: GhidraMCP Server Uses Port 8080 And Program Selection Calls

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-005 (E1)
**Reasoning:** Single E1 log + analysis, no conflicting sources.
**Authority:** E1
**Evidence Merged:** E-TOOL-009, E-TOOL-010
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-006: RE-KB Stores JSON In research/findings/.re_kb

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-006 (E1)
**Reasoning:** E1 policy matches repository JSON structure (E0).
**Authority:** E0
**Evidence Merged:** E-TOOL-011, E-TOOL-012, `research/findings/.re_kb/`
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-007: RE-KB Index Is Rebuildable From Findings

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-007 (E1)
**Reasoning:** Single E1 statement; no E0 tooling referenced.
**Authority:** E1
**Evidence Merged:** E-TOOL-013
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-008: create_finding And attach_evidence Require Structured Inputs

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-008 (E1)
**Reasoning:** E1 config notes define structured inputs.
**Authority:** E1
**Evidence Merged:** E-TOOL-014, E-TOOL-015
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-009: list_findings And get_finding Are Read-Only Queries

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-009 (E1)
**Reasoning:** E1 observations describe read behavior; no conflicts.
**Authority:** E1
**Evidence Merged:** E-TOOL-016, E-TOOL-017
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-010: Ghidra MCP Returns domain_file_id For Program Context

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-010 (E1)
**Reasoning:** Single E1 observation retained as hypothesis.
**Authority:** E1
**Evidence Merged:** E-TOOL-018
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-011: Codex Agent CWD Follows MCP Server Process CWD

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-011 (E1)
**Reasoning:** E1 observations plus MCP config indicate CWD inheritance.
**Authority:** E0
**Evidence Merged:** E-TOOL-021, E-TOOL-022, E-TOOL-023, `.mcp.json`
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-012: Codex Agents Are Spawned With spawn_agent

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-012 (E1)
**Reasoning:** E1 notes and tool usage only.
**Authority:** E1
**Evidence Merged:** E-TOOL-019, E-TOOL-020
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-013: spawn_agent Supports timeout_seconds

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-013 (E1)
**Reasoning:** E1 config notes and MCP timeouts in config support claim.
**Authority:** E1
**Evidence Merged:** E-TOOL-024, E-TOOL-025, `.mcp.json`
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-014: BSP Headers Imported For Ghidra Datatypes

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-014 (E1)
**Reasoning:** E1 intent noted; tooling exists but import not verified.
**Authority:** E1
**Evidence Merged:** E-TOOL-026, `tools/scripts/ghidra/extract_bsp_mmio_registers.py`
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-015: Keil __inline Mitigation Uses Preprocessor Defines And Shim

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-015 (E1)
**Reasoning:** E1 describes specific mitigation steps; no conflicts.
**Authority:** E1
**Evidence Merged:** E-TOOL-027, E-TOOL-028, E-TOOL-029
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-016: Ghidra Import Requires Base Address And ARMv5T Language

**Decision:** MERGE (PARTIAL_OVERLAP)
**Source Claims:** CL-TOOL-016 (E1), CL-OLD-TOOL-002 (E4)
**Reasoning:** Both describe address conventions; E1 uses 0x02000000 and is considered current.
**Authority:** E1
**Evidence Merged:** E-TOOL-030, E-OLD-TOOL-002
**Superseded:** E-OLD-TOOL-002 base address 0x200000 likely outdated.
**Contradiction:** Base address mismatch noted between E4 and current import settings.

---

### CL-TOOL-REC-017: Headless Ghidra Wrapper Supports Scripted Disassembly

**Decision:** UNIQUE
**Source Claims:** CL-TOOL-017 (E1)
**Reasoning:** Single E1 observation; wrapper not present in repo.
**Authority:** E1
**Evidence Merged:** E-TOOL-031
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-018: MCP Workflow Lists Core Ghidra Bridge Tools

**Decision:** UNIQUE
**Source Claims:** CL-OLD-TOOL-001 (E4)
**Reasoning:** E4 lists the tool inventory; no E1 equivalent.
**Authority:** E4
**Evidence Merged:** E-OLD-TOOL-001
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-019: Legacy UI Decode Output Is Incomplete

**Decision:** UNIQUE
**Source Claims:** CL-OLD-TOOL-003 (E4)
**Reasoning:** Single E4 observation about decode artifacts.
**Authority:** E4
**Evidence Merged:** E-OLD-TOOL-003
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-020: MCP Example Uses Full Caller Enumeration

**Decision:** UNIQUE
**Source Claims:** CL-OLD-TOOL-004 (E4)
**Reasoning:** Single E4 methodology example.
**Authority:** E4
**Evidence Merged:** E-OLD-TOOL-004
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-021: Incremental Claims Strategy Adopted

**Decision:** UNIQUE (E2-only)
**Source Claims:** None (E2-only)
**Reasoning:** E2 methodology evidence is not captured in E1/E4 claims.
**Authority:** E2
**Evidence Merged:** E2-TOOL-019
**Superseded:** None
**Contradiction:** None

---

### CL-TOOL-REC-022: Multi-Tier Evidence Framework Established

**Decision:** UNIQUE (E2-only)
**Source Claims:** None (E2-only)
**Reasoning:** E2 framework design is foundational and distinct from E1/E4 tool claims.
**Authority:** E2
**Evidence Merged:** E2-TOOL-021
**Superseded:** None
**Contradiction:** None
