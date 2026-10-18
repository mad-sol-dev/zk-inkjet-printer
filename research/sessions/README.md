# Session logs

Written by Claude; not yet reviewed by the maintainer.

This folder holds the logs of working sessions on the firmware. Until 2025-12
they were, next to the RE-KB, where findings were written down. Since August
2026 only `research/TRUTH.csv` is authoritative (rules in `research/TRUTH.md`),
and the RE-KB is frozen. From October 2026 the maintainer (@mad-sol-dev)
collects session logs again, for the story of how the work went, not as a
second register.

## What a log is

A log tells the story of a session: where it started, what was tried in which
order, what did not hold, what the device did, and which threads are left
open. It is a source, not an authority (rule 7 in `CLAUDE.md`).

A finding exists only as a row in `TRUTH.csv`. A log names the claim IDs and
commits that carry it and does not restate the rows. Where a log and the
register disagree, the register is right.

The step-by-step path to a single row stays in the commit messages
(`python3 tools/scripts/truth.py journal <ID>`). The log covers what spans
several rows, and what never became a row: refuted ideas, handling at the
device, mistakes.

## Older logs

The logs up to 2026-01 were written for the RE-KB. Their finding IDs are no
valid reference, because the two RE-KBs reuse each other's IDs
(CL-TOOL-REC-103).

Addresses in the logs up to 2026-08 use older counts: VA = file offset +
0x200000, which is 0x1A8000 too high, and in parts of 2025-12 VA = file
offset. The file offsets are right in all of them. The current count is VA =
file offset + 0x58000 (CL-BOOT-REC-113).

The logs of 2026-08 are in German. They are not translated (rule 10 in
`CLAUDE.md`).

## Writing a new log

### Name and language

`YYYY-MM-DD_topic-description.md`, in English. Add a line to
[INDEX.md](INDEX.md).

### Head

The first lines say that the log is not authoritative, list the commits of
the session, and say whether they are pushed:

```markdown
Not authoritative. Authoritative is `research/TRUTH.csv`.
Commits: `63dd232`, `f43c79c` (pushed to origin/master).
```

### Facts and story

Device observations and code readings appear as the register records them,
with their oracle level (O1 derived, O2 reproducible command, O3 seen on the
device). The account of the session is written by Claude in the first person,
so a misunderstanding reads as Claude's reading and not as a fact.

### Sections

Use what the session needs: starting point, what was done, results (claim
IDs), what did not hold, device and artefacts (what ran, what was written,
state at the end), open threads with the row that carries each, and mistakes
of the session. Keep it short; a log is read to pick up a thread.

## Privacy

Session logs are public. No real names (the maintainer is @mad-sol-dev), no
home paths, hostnames, MAC addresses or BSSIDs, no e-mail addresses other than
noreply ones, no keys or tokens. When documenting how anonymization works,
anonymize that text as well.

The pre-push hook checks every outgoing commit with
`tools/scripts/check_privat.py`; local patterns live in
`.git/info/privat-muster`. By hand, before a push:

```bash
python3 tools/scripts/check_privat.py --bereich origin/master..HEAD
```

Background: `2025-12-28_repository-anonymization-security-cleanup.md`.
