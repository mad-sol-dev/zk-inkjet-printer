# Agent & Repository Guidelines

This repository is both a **real reverse-engineering project** (ZK1696 handheld inkjet printer) and a **reference template** for running LLM agents against firmware using the Model Context Protocol (MCP).

It is designed to showcase how three MCP servers can work together:

- **GhidraMCPd** – token-efficient Ghidra backend (batch disassembly, scalar search with context, etc.)
- **re-kb-mcp** – JSON-based reverse-engineering knowledge base (findings, assets, threads) under `research/findings/.re_kb/`
- **PDF Reader MCP** – high-performance PDF reader (`read_pdf` tool) for vendor manuals under `vendor/` :contentReference[oaicite:1]{index=1}

The instructions below target both **human contributors** and **LLM agents** (Codex, Aider Desk, Claude Code, etc.).

---

## 1. Project Structure & Context

Core layout:

```text
zk-inkjet-printer/
  firmware/
    bin/        # firmware binaries
    image/      # SD card images, raw dumps
  research/
    phase_a_sd_analysis/  # decoded UI blobs, extracted file systems, logs, CSVs, images
    ...         # analysis notes, methodology docs, traceability logs
  vendor/
    ...         # vendor PDFs: SoC datasheets, design guides, manuals
  research/findings/.re_kb/
    project.json
    index.json
    findings/
    assets/
    threads/
  tools/
    scripts/    # Python and shell helpers for carving, decoding, analysis
    ...         # Python and shell helpers for carving, decoding, analysis
```

## 2. Quick Start for Agents (MCP)
- **Activate re-kb**: `bash research/findings/.re_kb/select_this_project.sh` (required before using re-kb tools).
- **Ghidra MCPd**: `mcp__ghidra-bridge__project_overview` → `select_program(domain_file_id="...")`; then use `search_strings/search_functions/search_scalars_with_context/disassemble_at`.
- **re-kb MCP**: `mcp__re-kb__get_finding_template`, `list_finding_enums`, `create_finding`, `attach_evidence`. Findings live in `research/findings/.re_kb/findings/`.
- **PDF reader MCP**: `mcp__pdf-reader__read_pdf(sources=[{"path": "vendor/N3290x_Design_Guide_A1.pdf", "pages": "645-668"}])` for GPIO/UART/etc. (Design Guide has 897 pages).

## 3. Safety & Conventions
- Treat everything in `firmware/bin/` and `firmware/image/` as **untrusted**; never modify in place. Place derived artifacts in `research/phase_a_sd_analysis/` with deterministic names.
- Document commands in `research/analysis_traceability.md`; log significant work in `research/sessions/`.
- Address notation follows `research/system_understanding.md` (VA vs MMIO).
- Binary operations: capture SHA256 for modified binaries; avoid executing firmware.

## 4. Useful Commands
- Env: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt`
- Tests: `make test` or `python3 -m pytest -q`
- Export: `make export` or `tools/make_export.sh --with-binaries`

## 5. Key Docs
- Onboarding: `research/README.md`, `research/system_understanding.md`
- Findings index: `research/findings/.re_kb/findings/`, verification status: `research/system_understanding.md`
- Vendor PDFs: `vendor/N3290x_Design_Guide_A1.pdf` (Design Guide), `vendor/N3290X.PDF` (datasheet mirror)
