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
   Dokument anlegen.** Alles ausser `TRUTH.csv` -- READMEs, `METHOD.md`,
   `research/docs_rebuild/` -- ist abgeleitet und nicht autoritativ. Sitzungen koennen sich irren und
   Irrwegen folgen; die Triage, das Destillat, ist `TRUTH.csv`. Ein
   Sitzungslog in `research/sessions/` erzaehlt diese Geschichte und entsteht
   nur, wenn der Maintainer es verlangt (Format im README dort).
3. **Das Register nur ueber das Werkzeug aendern:** `tools/scripts/truth.py`
   (Kommandozeile) oder die `truth_*`-Werkzeuge des MCP-Servers `truth`. Keine
   eigenen Schnipsel -- eines davon hat die Datei am 2026-08-21 auf null Bytes
   gekuerzt. Kann das Werkzeug etwas nicht, wird es in der Vorlage
   `truth-register` (eigenes Repository, lokal `../../truth-register`)
   erweitert (mit Selbsttest) und hierher kopiert, nicht umgangen. Keine Kopien von `TRUTH.csv`; Git ist die
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

10. **Das Repository ist englisch.** Was neu ins Repository kommt, wird
    englisch geschrieben: Zellen in `TRUTH.csv` (Topic, Statement,
    Next_Test, Evidenz), Commit-Nachrichten, Kommentare und Docstrings,
    Ausgaben und Meldungen von Skripten, neue Dateien. Die Unterhaltung mit
    dem Maintainer bleibt deutsch. Der deutsche Bestand wird nicht
    nachtraeglich uebersetzt; wer eine Zelle ohnehin neu schreibt, schreibt
    sie englisch. Ergaenzungen in einer bestehenden deutschen Datei folgen
    der Sprache der Datei, bis sie als Ganzes uebersetzt wird -- eine Datei
    halb deutsch, halb englisch hilft niemandem.

11. **Erkunden mit jedem Mittel, belegen nur mit einem wiederholbaren.**
    Inline-Python, capstone und Skripte im Scratchpad sind zum Suchen
    erlaubt. Was als Zahl, Zaehlung, Mengenvergleich oder Negativbefund in
    eine O2-Zeile geht, laeuft ueber die Bruecke (Werkzeug mit Argumenten
    oder `run_script <skript>.py`) oder ueber ein versioniertes Skript,
    unter `tools/scripts/` oder neben seiner Ausgabe im Artefaktordner.
    `Evidence_E0` nennt genau diesen Aufruf. Ein Skript, das nur im
    Scratchpad lag, ist kein Beleg, Prosa wie 'python3 Bytesuche nach ...'
    auch nicht. Ein Disassemblat an genannten Adressen ist eine Lesung und
    darf so stehen.

<!-- ZK-TRUTH-RULES: Ende -->

# Agent guide

This file is for agents other than Claude Code (Codex, Aider and the like).
The rules above are the same block as at the top of `CLAUDE.md` and apply to
every agent.

The operating manual is `CLAUDE.md` (in German): reading and changing the
register, the Ghidra and PDF MCP servers, the four modes of constant search,
address conventions, testing patches live from RAM, repository layout and the
frozen sources. All of it applies to every agent; only the notes on deferred
tool schemas (`ToolSearch`) are specific to Claude Code.

## Start

```bash
python3 tools/scripts/next.py
```

It checks `research/TRUTH.csv` and prints the work front. A reported violation
is fixed first.

## The few things that break most often

- Only `research/TRUTH.csv` is authoritative. Change it only through
  `tools/scripts/truth.py` or the MCP server `tools/scripts/truth_mcp.py`
  (client template `mcp/claude-code.mcp.json.example`), never by hand.
- APP.bin addresses: VA = file offset + 0x00058000 (CL-BOOT-REC-113). Rows and
  logs written before 2026-08-31 count file offset + 0x00200000; their file
  offsets are right.
- `firmware/bin/` and `firmware/image/` are never edited in place. Derived
  artefacts go to `research/phase_a_sd_analysis/`.
- Hooks live in `.githooks/` (`git config core.hooksPath .githooks`): the
  register is validated on commit, outgoing commits are checked for private
  data on push.
- Session logs in `research/sessions/` only when the maintainer asks for one
  (rule 2); format in `research/sessions/README.md`.
- The RE-KB (`research/findings/.re_kb/`), `research/docs_rebuild/` and the
  reports next to them are frozen sources, not references.
