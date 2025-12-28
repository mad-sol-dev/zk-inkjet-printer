# Repository Migration Plan

**Date:** 2025-12-27  
**From:** `zk-inkjet-printer_old` structure  
**To:** New flattened structure with vendor/ top-level

---

## Phase 1: Firmware Directory ✅ (Partially Done)

### Already Migrated
- ✅ `firmware/app/` - Contains APP.bin
- ✅ `firmware/boot/` - Contains BOOT.bin
- ✅ `firmware/memory_map.md`
- ✅ `firmware/update_protocol.md`
- ✅ `firmware/update_system.md`

### Still Needed

```bash
# From: zk-inkjet-printer_old/data/raw/
# To: firmware/

# UI graphics
cp zk-inkjet-printer_old/data/raw/ZK-INKJET-UI-QVGA.bin \
   firmware/UI-QVGA.bin

# Resources
cp zk-inkjet-printer_old/data/raw/ZK-INKJET-RES-HW.zkml \
   firmware/RES-HW.zkml

cp zk-inkjet-printer_old/data/processed/ZK-INKJET-GUI-RES.zkml \
   firmware/GUI-RES.zkml

# SD card image
cp zk-inkjet-printer_old/data/raw/sdcard.work.img \
   firmware/sdcard.img

# Flatten app/ and boot/ subdirectories
mv firmware/app/APP.bin firmware/APP.bin
mv firmware/boot/BOOT.bin firmware/BOOT.bin
rmdir firmware/app firmware/boot
```

**Status:** ⚠️ Needs execution

---

## Phase 2: Research Directory ✅ (Done)

### Already Migrated
- ✅ `research/findings/.re_kb/` - New knowledge base initialized
- ✅ `research/findings/n32903_registers.json` - MMIO register map
- ✅ `research/sessions/2025-12-27_*.md` - Session log created
- ✅ Findings: finding-0001.json, finding-0002.json

### Still Needed

```bash
# From: zk-inkjet-printer_old/data/processed/
# To: research/analysis/

mkdir -p research/analysis

cp zk-inkjet-printer_old/data/processed/UI_QVGA_480x480.png \
   research/analysis/decoded_ui.png

cp zk-inkjet-printer_old/data/processed/app_strings_report.md \
   research/analysis/strings_report.md

cp zk-inkjet-printer_old/data/processed/upgrade_orchestrator_*.{json,txt} \
   research/analysis/
```

**Status:** ⚠️ Needs execution

---

## Phase 3: Vendor Directory ❌ (Not Started)

**Current State:**
- `docs/vendor/` exists with BSP
- vendor/ was in .gitignore (large files)

**Decision Needed:**

### Option A: Move docs/vendor/ → vendor/
```bash
# Move entire vendor directory
mv docs/vendor vendor/

# Update .gitignore
echo "vendor/" >> .gitignore
```

### Option B: Keep in docs/vendor/
```bash
# No action needed
# Update CLAUDE.md to reference docs/vendor/
```

### Option C: Split BSP and Datasheets
```bash
# Create structure
mkdir -p vendor/datasheets
mkdir -p vendor/bsp

# Move BSP
mv docs/vendor/N32901-3_NonOS_BSP vendor/bsp/

# Datasheets stay or move to vendor/datasheets/
# (if they exist)

# Remove docs/vendor/
rmdir docs/vendor/
```

**Status:** 🔴 **Decision required from user**

**Recommendation:** Option A (move to vendor/ top-level)
- Cleaner structure
- Vendor material separated from own docs
- Aligns with new flat layout

---

## Phase 4: Tools Directory ✅ (Done)

### Already Exists
- ✅ `tools/scripts/` - Python analysis tools
- ✅ `tools/legacy/` - Archived tools
- ✅ `tools/mcp_bridge/` - MCP integrations

### Verify Content
```bash
# Check if old scripts/ needs migration
ls -la zk-inkjet-printer_old/scripts/

# If files exist there, copy to tools/scripts/
# (Skip if already migrated)
```

**Status:** ✅ Likely complete (verify)

---

## Phase 5: Hardware Directory ✅ (Done)

### Already Exists
- ✅ `hardware/N32903U5DN_Pinout.md`
- ✅ `hardware/README.md`
- ✅ `hardware/images/`

**Status:** ✅ Complete

---

## Phase 6: Docs Directory Cleanup ⚠️ (Needs Review)

**Current State:**
```
docs/
├── ARCHITECTURE.md
└── vendor/          ← To be moved/decided
```

**Actions:**

### If vendor/ moves to top-level:
```bash
# Keep only ARCHITECTURE.md
mv docs/ARCHITECTURE.md ./ARCHITECTURE.md
rmdir docs/  # If empty after vendor/ move
```

### If vendor/ stays:
```bash
# Keep docs/ directory
# Update CLAUDE.md references
```

**Status:** 🟡 **Depends on Phase 3 decision**

---

## Phase 7: Ghidra Projects ✅ (Done)

### Already Exists
- ✅ `ghidra_projects/zk-inkjet/`
- ✅ Clean project with optimized analysis settings
- ✅ BSP structs imported (143 structs, 79 enums)

**Status:** ✅ Complete

---

## Phase 8: Root Files 🔄 (Partially Done)

### Already Updated
- ✅ `CLAUDE.md` - Completely rewritten (2025-12-27)
- ✅ `.mcp.json` - MCP server config
- ✅ `.mcp-stdio.json` - stdio MCP config

### Needs Review
- ⚠️ `README.md` - May reference old structure
- ⚠️ `.gitignore` - Needs vendor/ entry
- ⚠️ `CONTRIBUTING.md` - May need updates
- ⚠️ `AGENTS.md` - May reference old paths

```bash
# Check and update these files manually
# Search for "data/raw", "data/processed", "docs/vendor" references
grep -r "data/raw" README.md CONTRIBUTING.md AGENTS.md
grep -r "docs/vendor" README.md CONTRIBUTING.md AGENTS.md
```

**Status:** ⚠️ Needs manual review

---

## Phase 9: Cleanup Old Structure

### Files to Delete (After Migration Complete)

```bash
# Remove old data/ directories (after firmware/ populated)
# rm -rf zk-inkjet-printer_old/data/raw/
# rm -rf zk-inkjet-printer_old/data/processed/

# Remove old scripts/ (after tools/scripts/ verified)
# rm -rf zk-inkjet-printer_old/scripts/

# Remove testdisk artifacts
# rm -rf zk-inkjet-printer_old/data/raw/testdisk/
# rm zk-inkjet-printer_old/data/raw/testdisk.log

# Remove backup files
# rm zk-inkjet-printer_old/data/raw/*.backup
# rm zk-inkjet-printer_old/data/raw/*.orig

# Remove obsolete checksums
# rm zk-inkjet-printer_old/data/raw/CHECKSUMS.*.txt
```

**Status:** 🔴 **DO NOT DELETE YET** - Keep _old as archive until migration verified

---

## Migration Checklist

### Pre-Migration
- [x] CLAUDE.md updated with new structure
- [x] Migration plan created
- [ ] User decision on vendor/ location (Phase 3)
- [ ] Backup verification (git status clean)

### Execution Order
1. [ ] **Phase 1** - Complete firmware/ flattening
2. [ ] **Phase 2** - Copy analysis outputs to research/analysis/
3. [ ] **Phase 3** - Decide and execute vendor/ migration
4. [ ] **Phase 6** - Cleanup docs/ based on Phase 3
5. [ ] **Phase 8** - Update root documentation files
6. [ ] **Phase 9** - Archive _old repository (don't delete yet)

### Post-Migration Verification
- [ ] Test MCP servers still work
- [ ] Verify Ghidra project loads
- [ ] Check RE-KB activation script path
- [ ] Run `ls -R` and compare to expected structure
- [ ] Git commit new structure

### Final Steps
- [ ] Tag old structure in git: `git tag pre-restructure-2025-12-27`
- [ ] Commit new structure: `git commit -m "Repository restructure: flat layout with vendor/ top-level"`
- [ ] Keep _old directory as archive (don't delete)

---

## Critical Decisions Needed

1. **vendor/ location** (Phase 3)
   - Option A: vendor/ top-level ← Recommended
   - Option B: Keep docs/vendor/
   - Option C: Split BSP and datasheets

2. **docs/ directory fate** (Phase 6)
   - Remove if vendor/ moves
   - Keep if vendor/ stays
   - Move ARCHITECTURE.md to root?

3. **Timing**
   - Execute now?
   - Review first?
   - Incremental migration?

---

## Risk Mitigation

**Rollback Strategy:**
- Old structure preserved in `zk-inkjet-printer_old/`
- Git history maintains all changes
- Can revert via `git reset` or manual copy

**Testing:**
- Verify MCP paths after each phase
- Test Ghidra project opens
- Confirm RE-KB activation works

**Backup:**
```bash
# Create tarball before major changes
tar -czf migration-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  firmware/ research/ tools/ hardware/ vendor/ docs/
```

---

*Migration plan created: 2025-12-27 by Claude Sonnet 4.5*
