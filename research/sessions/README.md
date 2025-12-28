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

## Privacy & Anonymization

**CRITICAL:** Session logs are public and committed to GitHub. All sensitive information must be anonymized before committing.

### Anonymization Rules

**Always replace:**
- Real names: `martinm` → `user`, `Martin` → `User`
- Home paths: `/home/martinm/` → `$HOME/`
- Project paths: `/home/martinm/programme/Projekte/` → `$HOME/workspace/`
- Hostnames: `roadwarrior` → `host`
- System paths: `/usr/lib/jvm/jdk-21.0.8-oracle-x64/` → `$JAVA_HOME/`

**Never commit:**
- API keys, tokens, passwords
- Private email addresses (use `mad-sol-dev@users.noreply.github.com`)
- Absolute paths containing usernames
- Internal hostnames or network information

### Verification Before Commit

Before committing a new session log:

```bash
# Check for sensitive data
grep -n "martinm\|roadwarrior\|/home/martinm" research/sessions/YYYY-MM-DD_*.md

# Anonymize if needed
sed -i 's|/home/martinm/programme/Projekte/|$HOME/workspace/|g' research/sessions/YYYY-MM-DD_*.md
sed -i 's|/home/martinm/|$HOME/|g' research/sessions/YYYY-MM-DD_*.md
sed -i 's|martinm|user|g' research/sessions/YYYY-MM-DD_*.md
sed -i 's|roadwarrior|host|g' research/sessions/YYYY-MM-DD_*.md
```

**Golden Rule:** When documenting anonymization procedures (like in session logs about privacy work), those documents must also be anonymized. Meta-documentation is not exempt.

### Reference

See `2025-12-28_repository-anonymization-security-cleanup.md` for complete anonymization process and security audit.

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
