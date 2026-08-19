# Prompts & Workflow-Canvas (zk-inkjet-printer)

Dieses Canvas ist eine **Paste‑ready Prompt-Sammlung** (für Codex/Claude/LLM), um aus einem gewachsenen RE-Projekt eine **prüfbare Wahrheitsschicht** plus **öffentliche Projektgeschichte** zu bauen.

## Grundmodell

### Rollen der Quellen
- **Chats (research/Chats/*.json)** = Primärmaterial (Ground Truth für Zitate/Belege)
- **Sessions (research/sessions/*.md)** = kuratierte Pointer/„Handoff“-Notizen (Navigation, aber nicht Beweis)
- **RE‑KB (.re_kb/findings/*.json + exportierte KNOWLEDGE_*.md)** = **Wissensquelle**, aber **nicht automatisch Wahrheit** (enthält Hypothesen, Zwischenstände, Irrtümer)
- **Sekundärdokus (ANALYSIS_*.md, old_docs/**)** = Kontext/Landkarte
- **Artefakte (z.B. findings/n32903_registers.json, Bilder, Dumps)** = starke Evidenz

### Evidence-Tiers (für Claim-Status)
- **E0**: Artefakt / Messung / Dump / Registerliste / Foto-Beleg
- **E1**: Chat-Transkriptstelle (Chats/<file>.json#msg=<index>)
- **E2**: Session-Notiz (Pointer, kein Beweis)
- **E3**: Sekundäranalyse (nur Kontext)

**Regel:** Ein Claim darf **nur** `VERIFIED` werden, wenn mindestens **E0 oder E1** existiert.

### Lanes
- **Lane A (DEVICE)**: Drucker/RE/Technik
- **Lane B (TOOL)**: Tooling/Workflow/Doku-Engineering
- **Lane C (META)**: Orga, Repo-Hygiene, Anonymisierung, Prozess

### Claim-Status
- `VERIFIED` (E0/E1 stark)
- `SUPPORTED` (E1 vorhanden, aber noch nicht „entscheidend“)
- `WEAK` (Indizien, wenig/indirekte E1)
- `HYPOTHESIS` (plausibel, aber unbewiesen)
- `REFUTED` (widerlegt, mit Gegenbeleg)
- `UNKNOWN` (unentschieden / widersprüchlich)

---

## Prompt 0 — Projektpfade (einmal setzen)
> **Passe nur diese Variablen an**, der Rest kann unverändert bleiben.

- ROOT: `./` (Repo root)
- RESEARCH: `research/`
- CHATS: `research/Chats/`
- SESSIONS: `research/sessions/`
- FINDINGS: `research/findings/`
- REKB: `research/findings/.re_kb/`

---

## Prompt A1 — Inventory & Coverage (Basisdiagnose)

```text
Scan the repository subtree: research/

OUTPUT
1) Write research/inventory.txt with:
   - file counts per folder (Chats, sessions, findings, old_docs)
   - list of generated/derivative docs (ANALYSIS_*, KNOWLEDGE_*, chat_index*, keyword_hits, codex_agent logs)
   - list of primary sources (Chats/*.json, findings/*.json, sessions/*.md)
   - flag potential duplicates/near-duplicates (e.g., multiple ANALYSIS_red-threads variants)

2) Write research/CHAT_COVERAGE.md
   - list every chat file in research/Chats/
   - classify each: Lane=DEVICE|TOOL|MIXED|NOISE
   - mark: used_as_evidence=yes/no (in current CLAIMS/CONTRADICTIONS/TIMELINE)
   - reason if not used

QUALITY
- Do not infer facts.
- sessions are pointers only.
```

---

## Prompt A2 — CLAIM_BACKLOG v2 (inkl. RE‑KB als Wissensquelle, nicht als Wahrheit)

```text
Build/refresh research/CLAIM_BACKLOG.md from:
- research/Chats/*.json (primary evidence)
- research/sessions/*.md (pointers)
- research/findings/.re_kb/findings/*.json (RE-KB knowledge source)
- research/findings/n32903_registers.json and other artifacts (E0)

GOAL
Create 160–260 candidate claims, grouped by focus area, with explicit lane/signal/scope tags.

HARD RULES
- Claims must cite Evidence as E0/E1 whenever possible.
- RE-KB findings can propose claims, but if they lack E0/E1, tag as HYPOTHESIS and add a “next decisive test”.
- sessions are pointers only.

FORMAT (one item per claim)
- [<FOCUS>] [Lane=<DEVICE|TOOL|META>] [Signal=<RAW_LOG|BYTE_DUMP|ARTIFACT|SCREENSHOT|INFERENCE|PLAN>] [Scope=<PUBLIC_OK|INTERNAL_ONLY>]
  Claim: <one-line>
  Evidence:
    - E0: <path + anchor if possible> (optional)
    - E1: Chats/<file>.json#msg=<n> (one or more) (preferred)
    - E2: sessions/<file>.md (pointer only) (optional)
    - REKB: findings/.re_kb/findings/finding-XXXX.json (optional)
  Contradiction: <Cluster ID or ->
  Notes: <why it matters / what would falsify>

FOCUS AREAS (minimum counts)
- USB >= 35
- STO (storage/update/volumes) >= 35
- BOOT (boot/memory/arm-thumb) >= 30
- HW (SoC/pinout/ADC/encoder/display/HP45) >= 40
- TOOL >= 25
- META >= 15

COVERAGE TARGET
- Reference >= 40 unique chat files as E1 OR explain why not possible.

OUTPUT
- research/CLAIM_BACKLOG.md
- update research/CHAT_COVERAGE.md stats section with “unique chat files referenced in backlog”.
```

---

## Prompt B1 — Build/Update Truth Layer (CLAIMS + CONTRADICTIONS)

```text
Using research/CLAIM_BACKLOG.md, update:

1) research/CLAIMS.md
- Select 90–140 high-impact claims (not all).
- Each claim must include:
  ID (stable), Status, Confidence, Lane, Signal, Scope,
  Evidence (E0/E1), Contradictions, Revision history, Next decisive test.
- VERIFIED requires E0 or strong E1.
- If evidence is weak/indirect, keep SUPPORTED/WEAK/HYPOTHESIS.

2) research/CONTRADICTIONS.md
- At least 12 contradiction clusters.
- Each cluster includes:
  - Competing claims (IDs)
  - Evidence pointers for both sides
  - Impact if wrong
  - Single best decisive test (the one experiment/observation that resolves it)

HARD RULES
- RE-KB is a knowledge source; do not upgrade status based solely on RE-KB text.
- sessions are pointers only.
- No invented facts.
```

---

## Prompt B2 — Two-Lane Timeline + Internal Worklog + Public History

```text
From research/CLAIMS.md + research/CONTRADICTIONS.md + sessions pointers, update:

1) research/MASTER_TIMELINE.md
- Two lanes:
  Lane A (DEVICE): claim lifecycle events (created/verified/refuted) with evidence
  Lane B (TOOL/META): workflow/tool changes that enable evidence capture
- Minimum 35 timeline events.
- Each DEVICE event references Claim IDs and at least one E1/E0 evidence pointer.

2) research/WORKLOG.md (internal, rich)
- Chronological narrative: hypotheses, wrong turns, corrections, re-check points.
- Must link every important statement to Claim IDs or contradiction clusters.
- Include a “Where to re-check” index.

3) docs/HISTORY.md (public, curated)
- Phase-based story (3–6 phases)
- Only PUBLIC_OK claims
- Explicit language for status (Verified/Supported/Hypothesis)
- Include a “Corrections & Lessons learned” section.

RULES
- Do not turn hypotheses into facts.
- sessions may be used as narrative glue, but evidence must be E0/E1.
```

---

## Prompt C — RE‑KB Reconciliation (Findings ↔ Claims)

```text
Reconcile RE-KB with the Claim system.

INPUT
- research/findings/.re_kb/findings/*.json
- research/CLAIMS.md
- research/CONTRADICTIONS.md

GOAL
1) For each RE-KB finding, map it to one or more Claim IDs (or create new claims if missing).
2) Detect:
   - findings that assert something without E0/E1 evidence
   - claims that should reference a finding
   - duplicates (multiple findings describing same thing)

OUTPUT
- research/REKB_MAPPING.md
  For each finding-XXXX:
  - Summary
  - Linked claim IDs
  - Evidence gaps (missing E0/E1)
  - Recommended status changes (if any) BUT do not apply automatically

- research/REKB_CLEANUP_TODO.md
  A prioritized TODO list:
  - add missing evidence pointers
  - split/merge findings
  - mark refuted hypotheses

RULES
- Never promote to VERIFIED solely from RE-KB text.
- Prefer adding E1 pointers from Chats.
```

---

## Prompt D — Maintenance (nach neuen Chats)

```text
When new chat JSON files are added:
1) Append them to research/CHAT_COVERAGE.md
2) Update research/CLAIM_BACKLOG.md (only add new claims; dedupe)
3) Update research/CLAIMS.md (only if new evidence changes status)
4) Update research/CONTRADICTIONS.md (only if a new conflict appears or a decisive test resolves one)
5) Update research/MASTER_TIMELINE.md with the new events
6) Update docs/HISTORY.md only for major phase changes

Output a short change summary at the end.
```

---

## Templates (zum manuellen Nachpflegen)

### Claim Template
```md
## <ID>: <Short title>
- Status: <VERIFIED|SUPPORTED|WEAK|HYPOTHESIS|REFUTED|UNKNOWN>
- Confidence: <High|Med|Low>
- Lane: <DEVICE|TOOL|META>
- Signal: <RAW_LOG|BYTE_DUMP|ARTIFACT|SCREENSHOT|INFERENCE|PLAN>
- Scope: <PUBLIC_OK|INTERNAL_ONLY>
- Statement: <1–2 Sätze>
- Evidence:
  - E0: ...
  - E1: Chats/...#msg=...
- Contradictions: <Cluster-… / none>
- Revision history:
  - YYYY-MM-DD: <changed status because ...>
- Next decisive test:
  - <one concrete test>
```

### Contradiction Cluster Template
```md
## Cluster <X>: <Topic>
- Competing claims: <IDs>
- What differs:
- Evidence pointers (both sides):
- Impact if wrong:
- Decisive test (ONE):
- Secondary tests (optional):
```

### Timeline Entry Template
```md
### YYYY-MM-DD — <Milestone>
Lane A (DEVICE): <what changed> (Claims: ...)
Evidence: E1/E0 pointers
Lane B (TOOL/META): <workflow/tool change>
Pointers: sessions/... (optional)
```

