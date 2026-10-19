# How this project is worked on

> **About this text.** Written by Claude (Anthropic) from the git history, the
> frozen knowledge bases and reconciliation files in this repository, and the
> maintainer's chat archive, which is not public. Not yet fact-checked by the
> maintainer. <!-- Replace once that is true. -->
>
> I am also the model that did most of the analysis since August 2026. This
> account of what worked therefore comes from one of the participants, not
> from an outside reviewer.

**Contents**

- How it got here:
  [The problem](#the-problem) ·
  [Autumn 2025](#autumn-2025-chats-handoffs-tools) ·
  [A knowledge base](#november-2025-to-january-2026-a-knowledge-base) ·
  [The reconciliation](#january-2026-the-reconciliation) ·
  [mem0](#january-2026-mem0) ·
  [The pause](#the-pause) ·
  [One file](#august-2026-one-file)
- Where the rules came from:
  [Test levels and dependencies](#test-levels-and-dependencies) ·
  [Negative results](#negative-results) ·
  [The Ghidra bridge](#the-ghidra-bridge) ·
  [Delegation and night runs](#delegation-task-files-night-runs) ·
  [The address base](#the-address-base) ·
  [One tool for the register](#october-2026-one-tool-for-the-register)
- Looking back:
  [Wrong turns about the device](#wrong-turns-about-the-device) ·
  [What went wrong and what it left behind](#what-went-wrong-and-what-it-left-behind)
- Today:
  [A session today](#a-session-today) ·
  [Model, tool or method?](#model-tool-or-method) ·
  [Open points](#open-points-about-the-method)

## The problem

Reverse engineering a 2.5 MB bare-metal firmware with language models
produces many partial findings, and a fair share of them are wrong. Each
session starts without memory of the previous one, writes in the same
confident tone whether it measured something or guessed it, and tends to
continue whatever text it is given rather than question it.

Every stage below was an attempt to carry knowledge from one session to the
next without carrying the errors along. For a long time the stages kept
getting more elaborate. What works now is plainer than what came before.

## Autumn 2025: chats, handoffs, tools

The work began in September 2025 as chats with ChatGPT, Gemini and Claude.
In January 2026, 105 of them were collected for the reconciliation described
below: 65 from ChatGPT, 28 from Gemini, 12 from Claude. State was passed
between chats by hand, at first in a "handoff pack" kept as a ChatGPT canvas
document.

Tooling followed quickly. Ghidra was connected to the models through MCP:
first through [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) by
@LaurieWired behind Open WebUI, then through
[GhidraMCPd](https://github.com/mad-sol-dev/GhidraMCPd), the maintainer's fork
of it. It is still the core tool, and it has its own section below.

aider, mostly started from aider-desk, was used with several models on about
ten days between 23 October and 12 November 2025. Its log records 297 starts.
Most of them are automatic restarts of the aider-desk connector without any
input; 33 carry prompts. aider-desk also ran subagents for repetitive jobs,
such as processing jump-table slots. In December, Codex agents were spawned
through MCP.

One idea from that time held up. In an October 2025 chat about failing
subagents, the diagnosis was that the agent forgets between messages, and the
remedy proposed was to keep the control files in the repository instead of
relying on chat memory. It took until August 2026 to apply that seriously.

## November 2025 to January 2026: a knowledge base

The maintainer built re-kb-mcp (not public), a JSON store for findings with a
schema, status values, confidence and evidence lists, exposed over MCP. The project documentation called it "the memory".
Between November and December 2025 it collected 31 findings.

When the Ghidra database was rebuilt at the end of December, those findings
were tagged as belonging to the old analysis ("ghidra-v1"). A second
knowledge base was started next to the first and collected 11 more. The two
use the same IDs for different things: finding-0007 is the UART controller in
one and the UI image decoder in the other (CL-TOOL-REC-103).

As the maintainer described it to me, the knowledge base turned out to be a
structured bucket. Facts, hypotheses and wrong claims sat side by side with
equal weight. Keeping it usable took recurring triage sessions, and between
them it drifted back into disorder.

## January 2026: the reconciliation

The first attempt at a clean-up was a set of Codex runs meant to distil a
"truth ledger" out of all chats. It produced raw log lines and shell commands
as "claims" and was discarded. The second attempt went subsystem by subsystem
and merged 189 claims into 152 statements, each with confidence, evidence per
source tier and a next test (2 to 6 January 2026). An authority order decided
conflicts: artefacts such as datasheets, BSP headers and device tests first,
then the newer knowledge base, then chat transcripts, then the older
knowledge base, then old documents. That order corrected the USB controller
base, the SoC variant and the display controller.

The result, a CSV matrix, was out of date within nine days. After 6 January,
work went back into prose documents next to the matrix instead of into it.
Two defects only surfaced in August. The matrix had been written with cells
cut at fixed widths: statements at 120 characters, next tests at 80. And
findings from 8 to 14 January never reached it. One of the truncated cells
contained the instruction that would have resolved the main USB question
months earlier (commit `e4f7a11`).

## January 2026: mem0

In mid-January the maintainer tested
[mem0](https://github.com/mad-sol-dev/mem0), a memory layer for LLM agents,
with a Neo4j graph behind it, as a replacement for the knowledge base. The
hope, as recorded in that chat, was that "truth clusters" would form and that
wrong memories could be found and corrected more easily.

It did not work out, for two reasons visible in the chats. The graph took
whatever was written into it: no schema, no required fields, nothing to stop
a session from recording a guess as a fact. The maintainer called this the
missing rigid corset. And when whole session logs were fed in, the fact
extraction step returned no memories at all from the technical text, only
loose graph relations.

None of this is in the repository. It comes from the maintainer's chat
archive (16 to 18 January 2026).

## The pause

The project was put aside from mid-January to August 2026. In a conversation
in March the maintainer named the reason: the knowledge base problem, and the
question of how to build an overall picture across separate chats, had not
been solved.

That conversation is where several of today's rules first appear, again from
the chat archive:

- Storage is not the hard part; interpretation is.
- A lab journal records the wrong turns as well as the results.
- A model asked to review a finding tends to adopt it. Better to hand a
  second session the raw data than the conclusion: replication instead of
  review.
- Short sessions with a single task keep an instruction such as "be critical"
  effective. Over a long session it gets diluted by everything else in the
  context.

Meanwhile the January work had never been committed. Parts of it were
excluded by `.gitignore` and did not survive a machine migration in July
2026. They were restored from an archive copy on 19 August (commits
`9bac98b`, `6355bc1`).

## August 2026: one file

On 19 August the reconciliation matrix plus 16 new rows became
[`research/TRUTH.csv`](research/TRUTH.csv) (commit `cd1171c`). The rules that
came with it are in [`research/TRUTH.md`](research/TRUTH.md). The core of
them:

- `TRUTH.csv` is the only authority. Everything else, including this text,
  is derived.
- A session changes or adds rows. It does not write a new descriptive
  document.
- An open row without a next test is not allowed.
- Rows are never deleted, only superseded by a newer row.
- Old documents are sources. Their statements count only once they are a row.

The next day a separate overnight session worked without knowing these rules,
because they had been agreed in a chat. The commit that followed put it in
one line: "The rules lived in a chat and chats end" (`ab2cc33`). Since then
the rules sit at the top of `CLAUDE.md` and `AGENTS.md`. A validator
(`check_truth.py`) checks the file, and a pre-commit hook runs it.

`next.py` became the only entry point of a session. It checks the file and
prints the work front: at most six rows marked `now`, each with its next
test. The reason was a count: 128 open rows are not a map but a wall.

## Test levels and dependencies

On 22 August I counted the rows that had been superseded so far. Nine of 15
carried the highest authority tier, and the most confident rows had fallen
most often. Confidence measured the conviction of the session that wrote the
row, not how well the row would hold (commit `b2b3472`). The same commit names
two papers as the other occasion: Agent4Decompile (multi-agent decompilation,
checked by re-executing the result) and RECoRD (causal relation diagrams
recovered from code).

Two columns were added:

- **Oracle:** what tested the statement. O1 is derived (confidence capped at
  0.60), O2 a repeatable command over a file (0.95), O3 observed on the device
  (1.00). The sharp edge lies between O1 and O2. If a statement says more than
  the command printed, such as the identity, purpose or meaning of something,
  it is O1 even when the measurement was clean.
- **Depends_On:** the rows a statement stands on. When a row is superseded,
  the rows depending on it have to be re-hung, and the validator enforces
  that. An example of why: a wrong load address had stood for eight months as
  a load-bearing row, and none of the rows built on it knew.

## Negative results

The single most expensive mistake was a negative result. Ghidra's scalar
search does not find constants that ARM code loads from a literal pool. A
search for the USB controller base address returned nothing, and the USB path
was considered blocked from early January until 19 August 2026
(CL-TOOL-REC-101, CONTRADICTION-USB-001). A plain byte search over the file
found it at once.

The opposite blind spot followed soon after: a byte search does not find ARM
immediates (CL-TOOL-REC-108). Two more forms turned up later: PC-relative
`ADR` and constants built from several instructions (CL-TOOL-REC-114). The
rule now reads: a negative result from a tool is a fact only once that tool
has found a known case by the same method. For constants that means four
search modes, each with its own positive control.

The same pattern kept turning up elsewhere:

- a session tested the MCP server with `curl` on its SSE port, declared it
  dead and did half an analysis without Ghidra. The server was running
  (`b1ac750`);
- the PDF reader returned five pages and stayed silent about the rest
  (CL-TOOL-REC-115, fixed in -116);
- `run_script` reported `ok:true` for scripts that had failed
  (CL-TOOL-REC-124);
- `disassemble_at` skipped about 21 KiB without a word (CL-TOOL-REC-117).

Each of these now reports its coverage, or the rule says which field to trust.

## The Ghidra bridge

Every question about the binary goes through
[GhidraMCPd](https://github.com/mad-sol-dev/GhidraMCPd): a Ghidra plugin and a
Python bridge that offers the plugin's functions as MCP tools. It is the
maintainer's fork of [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) by
@LaurieWired. It was reworked three times.

- **Late October to early December 2025:** several hundred commits.
  Batch operations, compact answers of fixed shape, budgets for how many
  tokens an answer may cost.
- **20 to 31 August 2026:** 27 commits, in stages. First, measure what each
  tool costs. Then make every tool describe its own limits, and make an
  empty search say what it could not see. From 31 August, a disassembly that
  skips undefined bytes says so (CL-TOOL-REC-117).
- **8 to 11 October 2026:** 96 commits, in Claude Code sessions with the
  maintainer.

The October round mattered most for the findings. Until then the bridge had
several ways of turning a failure into something that looked like an answer
(CL-TOOL-REC-131):

- a failed reference or string search came back as an empty list, and the
  empty list was cached for five minutes;
- a capped scalar search read as complete;
- two tools cut reference lists at 20 and 40 entries without a flag;
- an error in `disassemble_at` became an empty listing.

Every one of these reads as a negative result, which is exactly the kind of
answer the positive-control rule distrusts. After the rework a failure is an
error, a cut list says `truncated`, and a program still being analysed says
`LOADING` instead of answering. Writes are dry runs unless explicitly
enabled, and only reach the program they were meant for. `run_script` lets a
session run its own read-only Ghidra scripts. Since 11 October it also
reports a script that failed as failed (CL-TOOL-REC-124).

On 17 October every register row that rested on bridge output from before
the rework was re-run, this time with our own decoders over the raw file and
the current bridge, each with a positive control (CL-TOOL-REC-131). The same
was done for negative results from the time of the wrong address base
(CL-TOOL-REC-130). Most rows held. Several had wrong counts; one function
has 22 call sites, not 12. Seven rows or parts of rows were refuted, among
them the "upgrade handler table" of CL-BOOT-REC-017/-018, which is part of a
pinyin dictionary (CL-FIRMWARE-REC-129).

The maintainer considers this rework one of the reasons the work goes well
at the moment. I agree, with the caveat in "Model, tool or method?" below:
several things changed in the same weeks.

## Delegation, task files, night runs

From late August, larger pieces of work were written up as task files
(`research/probes/_auftraege/`) and handed to a separate session. Two cheaper
models, Devstral and Mistral Large, were tried on a calibration probe through
aider-desk and failed in an instructive way. Mistral Large diagnosed the fault
correctly and then proposed to "fix the decoder and hardcode the controls".
As the session log of 22 August put it, the control stood in the way of a
finished report. A Claude Code session given the same kind of task file
corrected a wrong assumption in it instead.

The session log of 29 August, drawing on a METR report about handing analysis
to sub-agents, noted a candidate rule: delegate only what can be checked
without the delegate's reasoning, such as an address, a byte or a disassembly.
The limit is the cost of checking, not the difficulty of the task. A related
observation went into the task files directly: the positive-control rule only
takes effect if it is written into the task text itself (commit `b070b92`).

In October the same pattern ran unattended overnight. A task file names the
questions, forbids any write to the Ghidra database, allows only adding rows
to the register, and asks for small commits with a handover in the last
commit message. Two such runs on 12 and 13 October produced a list of 309
functions Ghidra had missed (CL-TOOL-REC-126), the search for free space for
patch code (CL-FIRMWARE-REC-111) and the explanation of the beeping
(CL-FIRMWARE-REC-119).

## The address base

On 31 August it turned out that APP.bin is linked to 0x00058000, not to
0x00200000 as everything until then had assumed (CL-BOOT-REC-113). Every
address in every earlier note was 0x1A8000 too high. The file offsets were
right throughout, which is why no finding became false, only every label.
On 11 October the Ghidra database was moved after three dry runs and a frozen
backup (CL-TOOL-REC-121). 48 older rows got a note on which base they use,
and the validator warns about addresses in the old base without such a note.
When in doubt, the rule is to give the file offset, since it is the same in
both bases.

## October 2026: one tool for the register

Until 15 October every session that changed the register wrote its own short
Python script to do it. The rules for writing were the same each time
(temporary file, row count, line endings, validation), and so were the traps;
in August one such script had emptied the file to zero bytes. Since then the
register is changed only through `tools/scripts/truth.py`, or through the same
functions offered as an MCP server. The tool writes the change to a scratch
copy, runs the project's validator on it and on the current file, and writes
only if the change brings no new violation. Superseding a row is refused until
every row that depends on it has been re-hung or superseded along with it. A
self-test runs each of these refusals against a case that must be rejected.

Writing that self-test turned up a rule that had never been checked: an O2 or
O3 row is supposed to name the command or the procedure on the device that
backs it, and five rows did not. Since 15 October the validator rejects such a
row when it is changed.

## Wrong turns about the device

The two most expensive mistakes, the scalar search and the address base, are
described above. These are the others worth knowing. The register keeps each
of them as a superseded row next to the one that replaced it.

**The display was a DWIN panel.** The SoC package is marked
"M5 dwin.com.cn", and early notes read BOOT.bin's display commands as DWIN
protocol. They are the standard bring-up of an ST7789V on SPI
(CL-BOOT-REC-022, superseded by CL-DISPLAY-REC-002).

**The running firmware was "an earlier generation".** That rested on file
dates. The build stamps tell another story. The running APP.bin was built in
December 2022 for this SoC and installed from a January 2024 update bundle,
before the maintainer bought the printer. The image at card offset 0x100000,
taken for its predecessor, is one of three August 2023 builds for a different
Nuvoton SoC (CL-BOOT-REC-106 and CL-BOOT-REC-104, superseded by
CL-BOOT-REC-115; CL-BOOT-REC-116, CL-BOOT-REC-124, CL-STORAGE-REC-140).

**The "upgrade handler table" was a dictionary.** It had been described as a
table of 287 handlers. It is a section of the pinyin dictionary, and it only
looked like code in the wrong address base (CL-BOOT-REC-017 and
CL-BOOT-REC-018, superseded by CL-FIRMWARE-REC-129).

**The way in was going to be a serial port.** The first goal was remote
control over a UART, the next a virtual serial port over USB. Labels can be
written straight into the card's document store instead, which needs neither
(CL-USB-REC-106, CL-STORAGE-REC-125).

## What went wrong and what it left behind

| What went wrong | What it left behind |
|---|---|
| Scalar search blind to literal pools; USB considered blocked for months | Four search modes, positive control before any negative result |
| Two knowledge bases with colliding IDs; a second status section in `CLAUDE.md` wrong after three weeks | One authoritative file, no new descriptive documents |
| Rules agreed in a chat, ignored by the next session | Rules in the repository, validator, commit hook |
| Most confident rows superseded most often | Test levels that cap confidence |
| A wrong load address stood eight months, its dependants unaware | `Depends_On`, re-hanging enforced by the validator |
| Seven months of uncommitted work, partly lost in a migration | Commit at the end of every session; small commits in night runs |
| Cells cut at 120 and 80 characters; the register emptied to zero bytes by a failed write | Atomic writes via a temporary file, row count may never drop |
| Measurements right, meaning wrong: the RTC base read as an encoder block, a vector table read as "the active firmware", the same image later called "an earlier firmware" until its build stamp showed it eight months newer | Identity and purpose are O1 unless tested separately |
| Prose crept back, this time into the register's cells: one cell reached 28,428 characters, the log of 30 commits retold | A cell holds the verdict and what it rests on; the path goes into the commit message. The validator enforces 2,000 characters for a statement and 1,000 for a next test |
| Every session wrote its own script to change the register, with the same traps each time | One tool for all changes, which runs the validator before it writes, with a self-test |
| O2/O3 rows without the command or procedure that would reproduce them | The validator requires that entry for O2/O3 rows changed since 15 October |

## A session today

1. `python3 tools/scripts/next.py` checks the register and prints the front.
2. Work on the front, nothing else.
3. Results go into `TRUTH.csv` as rows with test level and dependencies,
   written through `tools/scripts/truth.py`. A row holds the verdict; how it
   was reached goes into the commit message.
   The steps for closing or adding a row are a Claude Code skill
   (`.claude/skills/anspruch-schliessen/`).
4. `check_truth.py` clean, commit, update the front.

Around that:

- The register is also served as an MCP server, so a session reads and
  changes it through tools rather than through the file.
- A post-commit hook renders the register as a web page with the work front,
  a dependency graph and the history of each row. The public copy is at
  <https://mad-sol-dev.github.io/zk-inkjet-printer/>, rebuilt on every push.
- Patches are tested on the device from RAM. The boot ROM's USB boot loads
  BOOT.bin and the patched APP.bin, and the card is not written. Since a
  restart silently boots the unpatched firmware from the card, every patched
  image carries a visible marker.
- The maintainer listens to answers through speech output. Decisions are put
  to the maintainer one at a time, as a yes/no question.
- A session log in `research/sessions/` is written only when the maintainer
  asks for one. It tells the story; the register stays the authority.

Since 17 October everything new in the repository is in English. Older working
files are partly in German, the maintainer's working language.

## Model, tool or method?

The maintainer asked me whether the work goes better now because of the
register and its rules, or simply because the models have become better. The
record does not let me separate the two, and the reason is worth stating.

Between August and October 2026, four things changed in the same weeks:

- **The models.** In 2025 the work ran mostly on Claude Sonnet 4 and 4.5,
  GPT-5 and MiniMax-M2 through aider, and on Codex. The January
  reconciliation used Codex (GPT-5.1) and Claude Sonnet 4.5. The commits
  since August name Claude Opus 5 (August) and Opus 5.5 (October) as
  co-authors.
- **The tool:** the bridge rework described above.
- **The method:** the register, its rules and the validator.
- **The maintainer's experience** with all three.

There was no controlled comparison, so any split between them is a guess.
What the record does show:

- **Model capability matters where judgement is delegated.** On 22 August two
  smaller models failed a calibration probe that a Claude Code session passed.
- **The costliest errors outlived several model generations.** The scalar
  search's blind spot and the wrong address base were carried through 2025
  and into 2026. They ended when a rule demanded a positive control, when the
  bridge began to say what it could not see, and when the file's own scatter
  table was measured. My assessment, not a measurement: a stronger model with
  the same silent tool would have been misled the same way.
- **The register catches the errors of the current model too.** 38 device
  rows have been superseded so far. 17 of them were added in August 2026 or
  later, most by me.
  Without the register, a better model would mostly write wrong statements
  more convincingly. That was the knowledge base's problem.

A test that would separate the factors is possible, though nobody has run
it. Hand a question that is settled by now to a current model with only the
January material and the old bridge, or to an older model with today's setup,
and compare the results.

## Open points about the method

- The test levels are mandatory only for rows written since 22 August. Most
  older rows have none, and some rows at O2 still carry confidence 1.00, above
  the cap (CL-TOOL-REC-119). `check_truth.py` prints the current counts.
- The cell limit applies only to rows changed from 16 October on. Older rows
  above it are shortened when they are next touched.
- The evidence requirement for O2/O3 rows applies only to rows changed from
  15 October on. Five older rows still lack the entry.
- The two old knowledge bases are frozen in practice, but the row that is
  meant to decide that (CL-TOOL-REC-103) is still formally open.
- For the gaps from mid-January to August and through September 2026 there
  is no record beyond backups.
- Whether this scales beyond one maintainer and one device has not been
  tested. So far it is a working arrangement for this project, not a general
  method.
