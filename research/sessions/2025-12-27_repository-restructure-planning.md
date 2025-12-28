# Session Continuation: Repository Restructure Planning

**Date:** 2025-12-27  
**Time:** 22:29 - 23:50 (UTC+1)  
**Focus:** CLAUDE.md rewrite + Migration planning

---

## Context

User reviewed session documentation and noticed CLAUDE.md was massively outdated with old repository structure. Requested update to match new layout.

## Key Discussion: Repository Structure

**Original Question:** Where should vendor/ materials go?
- Old: `docs/vendor/` 
- Gemini suggestion: No docs/ folder (repository is documentation)
- Consideration: vendor/ was gitignored (large files)

**Decision Process:**
1. Reviewed old `data/` structure - more than just firmware binaries
2. Discussed flattening vs. deep nesting
3. User chose: **Flat structure with vendor/ top-level**

**Final Structure:**
```
firmware/          # All binaries (flat, not subdirs per file)
├── APP.bin
├── BOOT.bin  
├── UI-QVGA.bin
├── RES-HW.zkml
├── GUI-RES.zkml
└── sdcard.img

vendor/            # External reference (gitignored)
├── datasheets/
└── bsp/

research/          # Our work
├── findings/
├── sessions/
└── analysis/

tools/             # Analysis scripts
hardware/          # Hardware docs
ghidra_projects/   # Ghidra work
```

## Deliverables Created

### 1. CLAUDE.md Rewrite (585 lines)

**Complete rewrite covering:**
- New repository structure
- MCP integration (Ghidra, RE-KB, PDF Reader)
- Firmware analysis workflow
- Codex agent best practices
- Critical rules (RE-KB Club Rule #1)
- Current project state

**Key Sections:**
- Repository Structure (visual tree)
- MCP Integration (3 servers with examples)
- Firmware Analysis Workflow (4 phases)
- Using Codex Agents (when/how)
- Critical Rules (what NOT to do)
- Common Tasks (code examples)

### 2. MIGRATION_PLAN.md (320 lines)

**Comprehensive 9-phase migration plan:**
1. Firmware Directory (needs flattening)
2. Research Directory (complete)
3. Vendor Directory (**decision needed**)
4. Tools Directory (complete)
5. Hardware Directory (complete)
6. Docs Cleanup (depends on #3)
7. Ghidra Projects (complete)
8. Root Files (needs review)
9. Cleanup Old Structure (DON'T delete yet)

**Critical Decisions Documented:**
- vendor/ location (A/B/C options)
- docs/ fate
- Migration timing

**Risk Mitigation:**
- Rollback strategy
- Testing checklist
- Backup commands

## Open Items for Next Session

**Decisions Needed:**
1. Execute vendor/ migration (Option A recommended)
2. Flatten firmware/app/ and firmware/boot/
3. Copy analysis outputs to research/analysis/
4. Review and update root documentation (README, CONTRIBUTING, AGENTS)
5. Update .gitignore for vendor/

**Migration Execution:**
- MIGRATION_PLAN.md ready to execute
- _old repository preserved as archive
- Git tag recommended before major changes

**Documentation Updates:**
- README.md likely references old paths
- CONTRIBUTING.md may need updates
- AGENTS.md may need updates
- Search for "data/raw", "docs/vendor" references

## Files Modified

- `/CLAUDE.md` - Complete rewrite (241 → 585 lines)
- `/MIGRATION_PLAN.md` - New file (320 lines)

## Session Statistics

- **Duration:** ~80 minutes
- **Documents Created:** 2 (905 total lines)
- **Decisions Made:** Repository structure finalized
- **Ready for Execution:** Migration can start next session

---

*Session note created: 2025-12-27 23:50 by Claude Sonnet 4.5*
