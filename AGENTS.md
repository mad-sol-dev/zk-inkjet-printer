<!-- ZK-TRUTH-RULES: Anfang. Diese Sitzungsregeln gelten fuer jede Sitzung,
     unabhaengig davon, in welchem Chat sie stattfindet. -->

# Regeln fuer jede Sitzung an diesem Projekt

**Autoritativ ist `research/TRUTH.csv`. Sonst nichts.** Die Spielregeln stehen
in `research/TRUTH.md`, die Pruefung in `tools/scripts/check_truth.py`.

1. **Sitzungsanfang -- ein Befehl:** `python3 tools/scripts/next.py`. Er prueft
   die Datei, druckt die Arbeitsfront (`Prio=now`, hoechstens 6 Zeilen) mit dem
   jeweils naechsten Test und die Restmenge. Meldet er einen Verstoss, wird der
   zuerst behoben. Sonst wird an der Front gearbeitet, nicht an etwas anderem.
2. **Eine Sitzung darf** Zeilen in `TRUTH.csv` aendern oder hinzufuegen und
   Rohartefakte erzeugen. **Eine Sitzung darf kein neues beschreibendes
   Dokument anlegen.** `research/system_understanding.md` und alles daneben ist
   abgeleitet und nicht autoritativ.
3. **Das Register nur ueber das Werkzeug aendern:** `tools/scripts/truth.py`
   (Kommandozeile) oder die `truth_*`-Werkzeuge des MCP-Servers `truth`. Keine
   eigenen Schnipsel -- eines davon hat die Datei am 2026-08-21 auf null Bytes
   gekuerzt. Kann das Werkzeug etwas nicht, wird es in der Vorlage
   `$HOME/workspace/truth-register` erweitert (mit Selbsttest) und
   hierher kopiert, nicht umgangen. Keine Kopien von `TRUTH.csv`; Git ist die
   Historie.
4. **Keine offene Zeile ohne `Next_Test`.** Eine Frage ohne definiertes
   Experiment ist kein Arbeitspaket, sondern ein Thema.
5. **Zeilen werden nie geloescht**, nur per `Superseded_By` abgeloest.
6. **Ein Negativbefund aus einem Werkzeug ist erst dann ein Fakt, wenn die
   Methode als tauglich belegt ist.** Ghidras Scalar-Suche findet keine
   Konstantenpool-Worte (CL-TOOL-REC-101); eine Byte-Suche in der Datei findet
   keine ARM-Immediates (CL-TOOL-REC-108). Beide Suchmodi laufen lassen.
7. **Alte Dokumente sind Quellen, keine Autoritaeten.** Ihre Aussagen gelten
   erst, wenn sie als Zeile in `TRUTH.csv` stehen -- mit Evidenzstufe.
   Autoritaetshierarchie: E0 > E3-New > E1-Recent > E1 > E3-Old > E4.
8. **Sitzungsende:** `check_truth.py` sauber, committen, Front nachfuehren
   (erledigte `now`-Zeilen schliessen, aus `next` nachruecken). Nicht
   committete Arbeit ist die haeufigste Verlustursache in diesem Projekt
   gewesen.

9. **Eine Zelle ist ein Urteil, kein Laborjournal.** `Statement` nennt das
   Urteil zuerst, dann die tragenden Belege -- hoechstens 2000 Zeichen,
   `Next_Test` hoechstens 1000 (ab 2026-10-16 geaenderte Zeilen, der
   Validator prueft es). Der Weg dorthin steht in den Commit-Nachrichten mit
   der Claim-ID. Ein Ergebnis, das fuer sich gilt, wird eine eigene Zeile.

<!-- ZK-TRUTH-RULES: Ende -->

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
