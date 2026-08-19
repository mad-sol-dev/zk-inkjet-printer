# ZK‑Inkjet Prompt Pack

Diese Prompts sind dafür gedacht, **gemischte Chat‑Korpora** (Projekt‑Inhalte + Tool‑Entwicklung + Noise) in **zwei saubere Outputs** zu überführen:

1) **Wahrheitsfindung / Technical Truth Ledger** (intern, streng evidenzbasiert, inkl. Widersprüche + Tests)
2) **Projekt‑Geschichte / Public History** (GitHub‑tauglich, „so lief’s ab“, inkl. Korrekturen, ohne unnötige Rohdetails)

Die Prompts sind so gebaut, dass du **nicht** auf eine feste Anzahl Files begrenzt bist und dass Tool‑Chats nicht versehentlich als Drucker‑Wissen „verkauft“ werden.

---

## Grundprinzipien (für alle Prompts)

### Quellen-Typen (immer explizit markieren)
- **E1 (Primary):** `research/Chats/*.json` mit Pointer `#msg=<index>`
- **E2 (Secondary):** `research/sessions/*.md` (Pointers/Handoff; selten originäre Beweise)
- **E3 (Structured):** `.re_kb/findings/*.json` (Findings sind **Hypothesen/Claims** mit Evidenz, nicht automatisch „wahr“)
- **E0 (Artifact):** Dateien/Images/Binaries/PDFs im Repo (z.B. `findings/n32903_registers.json`, `vendor/*.pdf`)

### Claim-Regel (wichtig!)
**KEINE Token‑Claims** wie „msg erwähnt Wort USB“.
Ein Claim muss **propositional** sein (eine Aussage über die Welt), z.B.:
- „UDC base ist 0xB8007000“
- „BOOT lädt APP nach 0x03000000“
- „USB VID/PID 0416:0093 enumeriert als MSC“

### Lanes (nicht nur anhand des Dateinamens!)
- **DEVICE:** konkrete Hardware/Firmware/Protokolle/Offsets/Register/Flows
- **TOOL:** Ghidra/MCP/re-kb/Workflows/Automatisierung (ohne Device‑Aussagen)
- **META:** Organisation/Dokumentation/Repo‑Umbau/Privacy
- **NOISE:** Offtopic / generisches LLM‑Gelaber / irrelevante Exkurse

Ein Chat kann **multi‑lane** sein (z.B. TOOL+DEVICE). Wenn unklar: **META** statt DEVICE.

### Scope
- **PUBLIC_OK:** GitHub‑tauglich (keine sensiblen Logs/Keys/Paths; keine unnötigen Rohdaten)
- **INTERNAL_ONLY:** Debug‑Details, Rohlogs, lokale Pfade, private Notizen

---

## Prompt A3 — Semantic Claim Extraction (statt Keyword‑Token‑Backlog)

**Ziel:** Aus allen Chats (und optional Sessions + re-kb) eine **kurze, deduplizierte Liste echter Kandidaten‑Claims** ziehen.

**INPUTS:**
- `research/Chats/*.json`
- `research/sessions/*.md`
- `research/findings/.re_kb/findings/*.json` (oder Zip entpackt)
- vorhandene Synthesen als Seeds: `research/ANALYSIS_red-threads-and-progression.md`, `research/Chats/KNOWLEDGE_technical-knowledge.md`

**OUTPUT:** `research/CLAIM_BACKLOG_SEMANTIC.md`

**Vorgehen / Regeln:**
1. Iteriere über alle Chats.
2. Extrahiere nur Aussagen, die mindestens **eins** haben:
   - konkrete Zahlen/Offsets/Adressen (`0x…`, Größen, VID/PID, GB/MB)
   - identifizierbare Komponenten/Subsysteme (UDC, FatFS, HP45, ADC, Timer, MMIO)
   - benannte Artefakte/Dateipfade im Device‑Kontext (`BOOT.bin`, `APP.bin`, `3:/…`)
   - beobachtete Runtime‑Ereignisse (USB‑Enumeration, Menüpfad, Fehlerzustand)
3. Pro Claim:
   - `Claim:` ein Satz, präzise
   - `Lane:` DEVICE/TOOL/META (+ optional)
   - `Scope:` PUBLIC_OK/INTERNAL_ONLY
   - `Evidence:` mindestens ein Pointer (E1/E2/E3/E0)
   - `Date:` aus Filename ableiten (oder unknown)
   - `Tags:` (usb, storage, boot, mmio, hp45, adc, tooling…)
   - `Conflict:` Cluster‑Label, falls widersprüchlich
4. Dedupliziere:
   - gleiche Aussage mit anderer Formulierung → ein Claim, mehrere Evidence‑Pointers
5. Priorisiere:
   - HIGH: beeinflusst Systemmodell (SoC, RAM‑Map, Storage‑Mapping, Update‑Chain, USB‑Stack)
   - MED: stützt HIGH‑Claims
   - LOW: nice-to-have

**Format:**
- Überschrift pro Tag/Fokus
- darunter Claims als Bullet‑Blöcke

---

## Prompt A4 — Claim Ledger (kuratiert + Status + Revisionen)

**Ziel:** Aus dem semantischen Backlog eine **kurze, kuratierte** `research/CLAIMS.md` machen.

**OUTPUT:** `research/CLAIMS.md`

**Regeln:**
- Max 40–80 Claims (nicht 145+), dafür hochwertig.
- Jeder Claim bekommt:
  - `ID` (CL-###)
  - `Status` (hypothesis/supported/verified/refuted/superseded)
  - `Confidence` 0.0–1.0
  - `Evidence` (E1/E0 bevorzugt)
  - `Counter-evidence` falls vorhanden
  - `Revisions` (was wurde wann korrigiert)
  - `Next test` (wie verifizieren/falsifizieren)

---

## Prompt B1 — Contradiction Clusters (Risikogesteuert)

**Ziel:** Widersprüche nicht nur auflisten, sondern **entscheidbar machen**.

**OUTPUT:** `research/CONTRADICTIONS.md`

**Regeln:**
- Cluster nach “entscheidet das Systemmodell?” priorisieren:
  1) SoC‑Identität / RAM‑Reality
  2) Storage/Volumes (0:/ vs 3:/, Partition‑Map)
  3) Update‑Validator/CRC
  4) USB Controller Base / Descriptor Offsets
- Pro Cluster:
  - Was sind die konkurrierenden Claims (IDs)
  - Evidence pro Seite
  - Minimaler Testplan (1–3 Aktionen)
  - Entscheidungskriterium („wenn X beobachtet, dann …“)

---

## Prompt B2 — Master Timeline (Two Lanes)

**Ziel:** Chronik + Erkenntnis‑Fortschritt + Korrekturen.

**OUTPUT:** `research/MASTER_TIMELINE.md`

**Lanes:**
- **Lane A (DEVICE):** Entdeckungen am Drucker/SoC/FW
- **Lane B (TOOL/META):** Tooling, Workflow, Repo‑Struktur

**Regeln:**
- Eintrag pro Datum (oder Datumsspanne)
- Immer: Was wurde geglaubt → welches Evidence kam dazu → was wurde korrigiert
- Verlinke Claim‑IDs statt wieder alles auszuschreiben

---

## Prompt C1 — Public History (GitHub‑tauglich)

**Ziel:** Leser:innen verstehen: *was wurde versucht*, *was hat sich geändert*, *wo steht das Projekt* – ohne Rohlogs.

**OUTPUT:** `docs/HISTORY.md`

**Regeln:**
- Phase‑basiert (z.B. Okt–Dez 2025)
- Status‑Sprache (supported/verified/refuted)
- Abschnitt „What we got wrong and how we corrected it“ ist Pflicht
- Verweise auf `research/CLAIMS.md` + `research/MASTER_TIMELINE.md`

---

## Prompt D1 — re‑kb Integration (Findings als Evidence, nicht als Wahrheit)

**Ziel:** `.re_kb` als zusätzliche Quelle nutzen und sauber an Claims anbinden.

**OUTPUT:**
- `research/REKB_CROSSWALK.md` (Mapping: finding-XXXX ↔ Claim IDs)

**Regeln:**
- Wenn ein re‑kb finding keine belastbare Evidence enthält → Status höchstens hypothesis.
- Wenn es Evidence hat → supported, aber nur wenn Evidence nachvollziehbar ist.

---

## Mini‑Checkliste (wenn du das laufen lässt)

- [ ] Gibt es irgendwo noch „Token‑Claims“? → raus / in ein separates `research/KEYWORD_INDEX.md`
- [ ] Lane‑Klassifikation basiert auf Content, nicht nur Dateinamen.
- [ ] Jeder HIGH‑Claim hat einen Next‑Test.
- [ ] Public History enthält Korrekturen und keine sensiblen Rohdaten.

