# Research Session Logs

Session logs capture detailed, chronological reverse-engineering work on the ZK inkjet printer firmware. They provide the narrative context and technical depth behind RE-KB findings and ongoing investigations.

## Session Index

For a chronological overview of all sessions, see **[INDEX.md](INDEX.md)**.

## Purpose & Usage

Session logs serve as:
1. **Detailed documentation** of discoveries not yet in RE-KB
2. **Backup storage** for findings when RE-KB tools fail
3. **Context preservation** for future work
4. **Decision tracking** - why certain approaches were taken
5. **Bug reports** for tooling issues

## Session Log Format

Each session log should include:
- Date and time
- Session goals
- Major discoveries
- Technical details (addresses, function chains, evidence)
- Findings that couldn't be stored in RE-KB
- Cross-references to RE-KB findings
- Next steps and open questions

## Naming Convention

Format: `YYYY-MM-DD_topic-description.md`

Examples:
- `2025-12-27_arm-thumb-analysis-mmio-extraction.md`
- `2025-12-15_raw-write-chain-discovery.md`

## Relationship to RE-KB

Session logs are **complementary** to RE-KB:
- **RE-KB:** Structured, validated findings database
- **Session Logs:** Narrative documentation with context

When RE-KB tools work properly, findings migrate from session logs to RE-KB. Session logs remain as historical context and detailed technical notes.

## When to Create a Session Log

Create a session log when:
- Major discoveries are made
- RE-KB tools fail or findings are blocked
- Complex analysis needs detailed documentation
- Multiple findings are interconnected
- Tooling bugs are encountered
- Architectural insights emerge

## Reading Session Logs

Session logs are designed to be:
- **Self-contained:** Include all context needed
- **Technical:** Specific addresses, code snippets, evidence
- **Referenced:** Link to RE-KB findings, Ghidra programs, transcripts
- **Actionable:** Clear next steps and open questions

---

*See [INDEX.md](INDEX.md) for chronological session overview.*
