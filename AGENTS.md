# Agent & Repository Guidelines

This repository is both a **real reverse-engineering project** (ZK1696 handheld inkjet printer) and a **reference template** for running LLM agents against firmware using the Model Context Protocol (MCP).

It is designed to showcase how three MCP servers can work together:

- **GhidraMCPd** – token-efficient Ghidra backend (batch disassembly, scalar search with context, etc.)
- **re-kb-mcp** – JSON-based reverse-engineering knowledge base (findings, assets, threads) under `.re_kb/`
- **PDF Reader MCP** – high-performance PDF reader (`read_pdf` tool) for vendor manuals under `docs/vendor/` :contentReference[oaicite:1]{index=1}

The instructions below target both **human contributors** and **LLM agents** (Codex, Aider Desk, Claude Code, etc.).

---

## 1. Project Structure & Context

Core layout:

```text
zk-inkjet-printer/
  data/
    raw/        # firmware, SD card images, raw dumps
    processed/  # decoded UI blobs, extracted file systems, logs, CSVs, images
  docs/
    vendor/     # vendor PDFs: SoC datasheets, design guides, manuals
    ...         # analysis notes, methodology docs, traceability logs
  .re_kb/
    project.json
    index.json
    findings/
    assets/
    threads/
  scripts/
    ...         # Python and shell helpers for carving, decoding, analysis
```

## 2. Quick Start for Agents (MCP)
- **Activate re-kb**: `bash .re_kb/select_this_project.sh` (required before using re-kb tools).
- **Ghidra MCPd**: `mcp__ghidra-bridge__project_overview` → `select_program(domain_file_id="...")`; then use `search_strings/search_functions/search_scalars_with_context/disassemble_at`.
- **re-kb MCP**: `mcp__re-kb__get_finding_template`, `list_finding_enums`, `create_finding`, `attach_evidence`. Findings live in `.re_kb/findings/`.
- **PDF reader MCP**: `mcp__pdf-reader__read_pdf(sources=[{"path": "docs/vendor/N3290x_Design_Guide_A1.pdf", "pages": "645-668"}])` for GPIO/UART/etc. (Design Guide has 897 pages).

## 3. Safety & Conventions
- Treat everything in `data/raw/` as **untrusted**; never modify in place. Place derived artifacts in `data/processed/` with deterministic names.
- Document commands in `docs/analysis_traceability.md`; log significant work in `docs/sessions/`.
- Address notation follows `docs/CONVENTIONS.md` (VA vs MMIO); keep verification status updated via `tools/generate_verification_summary.py`.
- Binary operations: capture SHA256 for modified binaries; avoid executing firmware.

## 4. Useful Commands
- Env: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt`
- Tests: `make test` or `python3 -m pytest -q`
- Verification tables: `make lint-docaddrs` and `python tools/generate_verification_summary.py`
- Export: `make export` or `tools/make_export.sh --with-binaries`

## 5. Key Docs
- Onboarding: `docs/guide/orientation.md`, `docs/guide/operations.md`
- Findings index: `docs/README.md`, verification status: `docs/VERIFICATION_STATUS.md`
- Vendor PDFs: `docs/vendor/N3290x_Design_Guide_A1.pdf` (Design Guide), `docs/vendor/N3290X.PDF` (datasheet mirror)
