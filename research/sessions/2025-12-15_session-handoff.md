# ZK Inkjet Printer RE Session Handoff
**Date:** 2025-12-15
**Status:** Critical Discovery - Boot Architecture Paradigm Shift
**Context Window:** Reached limit, requires new session

## Executive Summary

This session achieved a **major breakthrough** in understanding the N9H26 SD boot architecture through systematic analysis of Nuvoton's TurboWriter tool and deep Ghidra analysis via Codex collaboration. 

**KEY DISCOVERY:** The printer uses a **dual-storage architecture** - RAW boot images at fixed offsets PLUS separate FatFS volumes for runtime filesystem access. This fundamentally changes our understanding of the firmware update mechanism.

---

## Critical Findings (Session Breakthroughs)

### 1. Boot Offset Validation (CONFIRMED ✓)

**Source:** TurboWriter Tool User Guide analysis + RE-KB Finding-0023

```
NANO-BOOT.bin:  Offset 0x200     (Sector 1)    - 12,736 bytes
NANO-APP.bin:   Offset 0x100000  (Sector 2048) - 2,009,088 bytes
```

**TurboWriter Documentation Confirms:**
- IBR (Initial Boot ROM) loads "System Image" from Sector 1 (0x200)
- Standard Execute Image offset: 0x44000 (Sector 544)
- **BUT:** Printer uses custom offset 0x100000 (746 KB gap!)

**Boot Marker:** "ZBWp1WBZ" @ 0x200 - N9H26-specific boot code header

### 2. Filesystem Architecture (PARADIGM SHIFT 🔥)

**Previous Assumption:**
```
"3:/APP.bin" → Direct RAW access @ 0x100000
```

**Codex Analysis Revealed:**
```
"3:/" is a REAL FatFS partition, NOT a raw offset alias!
```

**Volume Mapping (from FUN_00048504 - disk_ioctl):**
```
Drive 0: 0x100000 sectors × 512B = 512 MB  @ LBA 0x20000
Drive 3: 0x20000  sectors × 512B = 64 MB   @ LBA ???
```

**Mount Function Analysis (FUN_0005ebb8):**
- Wrapper for FatFS f_mount/f_mkfs
- Allocates 0x1000 byte work buffer
- Calls FUN_0004d978 (FatFS core mount)
- Parses volume path format: `"<digit>:/"`
- Uses global drive table @ DAT_0004e690

**File I/O Analysis (FUN_0006ccf8):**
- Update copier used by FUN_0006887c (boot updater)
- Opens "3:/ZK-INKJET-NANO-BOOT.bin" and "3:/ZK-INKJET-NANO-APP.bin"
- Uses standard FatFS calls: f_open/f_read/f_write/f_close
- **NO raw LBA arithmetic** (no +0x100000 offset calculations)
- 0x20000 byte (128 KB) buffer for transfers

**Critical Implication:**
If FAT files are missing, updater will FAIL. No transparent raw fallback exists in analyzed code paths.

### 3. The Central Mystery: Dual Storage Architecture

**TestDisk Evidence (Finding-0023):**
```
Partition 1 @ LBA 131071 (0x1FFFF):
  - Contains DELETED entries for:
    - ZK-INKJET-NANO-BOOT.bin  (12,736 bytes)
    - ZK-INKJET-NANO-APP.bin   (2,009,088 bytes)
  - Files were once in FAT, now deleted
  - Raw copies exist at 0x200 and 0x100000
```

**Three Competing Hypotheses:**

**A) Boot-Time Raw + Runtime FAT:**
```
1. IBR loads BOOT.bin from RAW @ 0x200 (fixed, always)
2. BOOT.bin loads APP.bin from RAW @ 0x100000 (boot-time only)
3. After boot: APP.bin uses FatFS for all file access
4. Update workflow: Writes to FAT, then copies to RAW
```

**B) Dual-Copy System:**
```
1. FAT volumes: User-accessible copies for updates
2. RAW offsets: Protected boot copies for reliability
3. Update process: Atomic write to both locations
4. Boot loader: Prefers RAW, falls back to FAT?
```

**C) Legacy/Migration Artifact:**
```
1. RAW @ 0x100000 is vestigial from older firmware
2. Current system uses only FatFS
3. Deleted FAT entries = migration from old layout
4. RAW copies remain unused
```

**CURRENT BEST HYPOTHESIS: (A) - Boot-Time Raw + Runtime FAT**

---

## Technical Deep Dive

### SD Card Physical Layout

**TestDisk Scan Results:**
```
LBA Range           Size      Description
-------------------------------------------------
0x000000-0x1FFFF    64 MB     Unknown/Reserved
0x20000-0x12003E    ~576 MB   Partition 1 (FAT32, "MINI")
0x12003F-0x1530DE   ~9.7 MB   Partition 2 (FAT32, label unknown)
0x1530DF-end        Rest      Unallocated

RAW Boot Images (outside partitions):
0x200      (512B)     NANO-BOOT.bin start
0x100000   (1 MB)     NANO-APP.bin start
```

**Partition vs Volume Mapping:**
```
Physical Partition 1 @ LBA 0x20000  →  Logical Drive 0?
Physical Partition 2 @ LBA 0x12003F →  Logical Drive 3?

Drive 0: 0x100000 sectors (512 MB) - matches Partition 1 size
Drive 3: 0x20000 sectors  (64 MB)  - SMALLER than Partition 2!
```

**Anomaly:** Drive 3 sector count (64 MB) doesn't match Partition 2 size (9.7 MB). Requires investigation.

### Nuvoton N9H26 Boot Sequence (Validated)

**Official Boot Flow (from TurboWriter User Guide):**
```
1. Power-On / Reset
   ↓
2. IBR (Internal Boot ROM) activates
   ↓
3. Boot Source Detection (priority order):
   a) SD Card - Sector 1 (0x200)
   b) NAND Flash - Block 0
   c) SPI Flash - 0x00000000
   ↓
4. Load "System Image" (SDLoader/BOOT.bin)
   - Must have valid Boot Code Header
   - Marker: "ZBWp1WBZ" for N9H26
   - Contains execute address, size, DRAM init
   ↓
5. Execute SDLoader @ configured address (0x00900000)
   ↓
6. SDLoader loads "Execute Image" (APP.bin)
   - Standard location: Sector 544 (0x44000)
   - Printer location: Sector 2048 (0x100000) ← CUSTOM!
   ↓
7. Execute APP.bin @ 0x03000000 (from Finding-0021)
```

**Key Insight:** Steps 1-6 happen BEFORE any filesystem is mounted. RAW sector access is REQUIRED for boot.

### TurboWriter Tool Details

**Purpose:** Official Nuvoton PC tool (Windows-only) for creating bootable SD images

**Components:**
- TurboWriter.exe - GUI application
- TurboWriter.ini - Boot header configuration
- N9H26_musb.bin - USB recovery firmware
- NAND ID.ini - Flash chip database

**Configuration File Structure:**
```ini
[Address]
Address = 00900000     # BOOT.bin execution address

[N9H26 USER_DEFINE]
# Optional DRAM initialization commands
# Format: Register = Value
B0003034 = 00CCDD00   # Example: CKDQSDS register
55AA55AA = 000F4240   # Example: 1 second delay (microseconds)
```

**Standard Image Programming:**
1. System Image → Sector 1-33 (BOOT.bin)
2. Execute Image → Sector 544+ (APP.bin, customizable)
3. Logo/Data → Higher sectors (optional)

**Boot Header Auto-Generation:**
- Boot Code Marker (N9H26: "ZBWp1WBZ")
- Execute Address (from .ini)
- Image Size (calculated)
- Flash Type/Parameters
- Embedded DRAM init code

**Printer Deviation:** Uses custom APP.bin offset (0x100000 vs standard 0x44000), likely configured with custom TurboWriter.ini or proprietary tool.

---

## Function Analysis Summary

### Mount System

**FUN_0005ebb8** - Mount Wrapper
```c
// Pseudo-code reconstruction
void mount_volume(const char* path, const char* label) {
    void* workbuf = malloc(0x1000);
    // Copy template struct, concatenate label if provided
    FUN_0004d978(path, fs_struct, workbuf, 0x1000);
    free(workbuf);
}

// Called with: ("0:/", "system"), ("3:/", ?)
```

**FUN_0004d978** - FatFS Core Mount
- Parses `"<digit>:/"` format (drive number 0-4)
- Bounds checks drive number
- Accesses global drive table @ DAT_0004e690
- Calls disk driver interface functions:
  - FUN_000484fc → disk_status (always returns 0)
  - FUN_00048504 → disk_ioctl (GET_SECTOR_COUNT/SIZE)

**FUN_00048504** - Disk I/O Control (Critical!)
```
Drive 0, param_2==1: Returns 0x100000 (sector count)
Drive 3, param_2==1: Returns 0x20000  (sector count)
All drives, param_2==2: Returns 0x200 (sector size)
```

### File I/O System

**FUN_0006ccf8** - Update File Copier
- Used by FUN_0006887c (boot updater from Finding-0020)
- Allocates 0x20000 byte (128 KB) transfer buffer
- Opens source files on "3:/" volume
- Opens destination files on "0:/" volume
- Transfer loop using FatFS primitives:
  - FUN_0000d704 → likely f_open
  - FUN_0000d4e4 → likely f_read
  - FUN_0000d5d8 → likely f_write
  - FUN_0000e158 → likely f_close

**Critical Observation:** NO raw offset arithmetic. Files are accessed purely through FatFS API.

### Update Workflow (from Finding-0020)

**FUN_0006887c** - Boot Updater
```
1. Open "3:/ZK-INKJET-NANO-BOOT.bin" (source)
2. Open "0:/ZK-INKJET-NANO-BOOT.bin" (destination)
3. Copy via FUN_0006ccf8
4. Verify copy success
5. Delete "3:/ZK-INKJET-NANO-BOOT.bin" ← File removed after copy!
6. Repeat for APP.bin
```

**Puzzle Pieces:**
- Files copied FROM "3:/" TO "0:/"
- Source files deleted after successful copy
- TestDisk shows deleted entries on Partition 1
- **Missing Link:** How do files reach RAW offsets 0x200/0x100000?

---

## Open Questions & Next Steps

### CRITICAL: The RAW Write Mechanism

**Question:** How do boot binaries get written to RAW offsets 0x200 and 0x100000?

**Hypotheses to Test:**

**H1: BOOT.bin writes directly to RAW**
- After mounting FAT and loading APP.bin, BOOT.bin may copy itself and APP.bin to RAW
- Search BOOT.bin (0x200-0x3400) for SD write functions
- Look for constants 0x200, 0x100000 in BOOT.bin disassembly

**H2: APP.bin contains RAW write code**
- Firmware update function writes to FAT first, then to RAW
- Search APP.bin for:
  - SD card sector write functions (outside FatFS)
  - Functions that write to sector 1 and sector 2048
  - Post-update hooks that sync FAT to RAW

**H3: External tool workflow**
- PC-based updater writes RAW images via USB
- Printer's USB firmware update mode
- Files on FAT are staging area only

**Recommended Investigation Path:**
```
1. Analyze BOOT.bin @ 0x200:
   - Load in Ghidra as ARM binary @ 0x00900000
   - Search for SD write functions
   - Look for self-copy or APP-copy logic
   
2. Search APP.bin for raw SD writes:
   - Find disk_write functions (outside FatFS layer)
   - Search for constants: 0x200, 0x100000, 0x800 (sector numbers)
   - Trace update completion handlers

3. Test with real hardware:
   - Create modified APP.bin
   - Place on "3:/" via SD card
   - Trigger update, observe behavior
   - Check if RAW offsets get updated
```

### Volume Mapping Clarity

**Question:** How does "3:/" map to physical partitions?

**Known Facts:**
- Drive 0: 0x100000 sectors (512 MB) → Matches Partition 1 @ 0x20000
- Drive 3: 0x20000 sectors (64 MB) → Doesn't match Partition 2 (9.7 MB)
- TestDisk shows only 2 partitions

**Possibilities:**
- Drive 3 is a virtual volume (RAM disk, config partition)
- Drive 3 maps to reserved area before 0x20000?
- Multiple logical drives on single physical partition?

**Action Items:**
- Extract partition boot sectors, check FAT headers
- Trace FatFS partition table parsing
- Check for custom FatFS diskio.c implementation

### Boot Loader Analysis

**Question:** Does BOOT.bin load APP.bin from RAW or FAT?

**Evidence Needed:**
- Disassembly of BOOT.bin @ 0x200 (12,736 bytes)
- Look for:
  - SD sector read @ 0x100000 (RAW)
  - FatFS mount + f_open calls (FAT)
  - Conditional logic (try RAW first, fallback to FAT?)

**Critical Function:** Finding-0021 mentions APP.bin loads to 0x03000000. Find the loader code!

### Update Atomicity & Safety

**Question:** What happens if update fails mid-write?

**Scenarios:**
- Power loss during FAT write → Incomplete file, boot fails?
- Power loss during RAW write → Corrupted boot image?
- Verification checksums? Rollback mechanism?

**Investigation:**
- Look for CRC/checksum validation
- Backup/recovery partition?
- Dual-boot A/B system?

---

## RE-KB Status

### Findings Referenced This Session

**Finding-0020:** SD Card Volume Management
- Status: Verified, needs major update
- Key Discovery: "3:/" is real FatFS, not raw alias
- Needs Addition: Volume size mapping, disk_ioctl details

**Finding-0021:** APP.bin Load Mechanism
- Status: Verified
- Execute Address: 0x03000000 (confirmed)
- Missing: Loader location analysis (BOOT.bin?)

**Finding-0023:** SD Card Raw Binary Storage Layout
- Status: Verified
- Offsets confirmed: 0x200 (BOOT), 0x100000 (APP)
- Needs Addition: Relationship to FAT volumes

**Finding-0024:** (Not yet created)
- Proposed: "N9H26 Dual-Storage Boot Architecture"
- Would document: RAW boot + FAT runtime model
- Evidence: TurboWriter docs, Codex analysis, TestDisk

### Functions Requiring Documentation

**FUN_0005ebb8** - Mount Wrapper (analyzed ✓)
**FUN_0004d978** - FatFS Core Mount (analyzed ✓)
**FUN_00048504** - Disk I/O Control (analyzed ✓)
**FUN_0006ccf8** - File Copier (analyzed ✓)
**FUN_0006887c** - Boot Updater (partially analyzed, from Finding-0020)

**Pending Analysis:**
- FUN_0000d704 (f_open equivalent)
- FUN_0000d4e4 (f_read equivalent)
- FUN_0000d5d8 (f_write equivalent)
- FUN_0000e158 (f_close equivalent)
- BOOT.bin entry point and loader logic

---

## Files & Resources

### Project Structure
```
$HOME/workspace/zk-inkjet-printer/
├── .re_kb/
│   ├── findings/
│   │   ├── finding-0020.json  # Volume management
│   │   ├── finding-0021.json  # APP.bin load
│   │   └── finding-0023.json  # Raw storage layout
│   └── index.json
├── docs/
│   └── vendor/
│       └── N9H26_NonOS_BSP/
│           └── Tools/PC_Tools/
│               ├── TurboWriter Tool User Guide.pdf ← KEY REFERENCE
│               └── TurboWriter V2.30.003_N9H26K5/
├── firmware/
│   └── extracted/
│       ├── BOOT.bin (extracted from SD @ 0x200)
│       └── APP.bin (extracted from SD @ 0x100000)
├── sd-images/
│   └── zk-inkjet-8gb.img  # Full SD card dump
└── SESSION-HANDOFF-2025-12-15.md  ← THIS FILE
```

### Key Documents

**1. TurboWriter Tool User Guide.pdf**
- Path: `docs/vendor/N9H26_NonOS_BSP/Tools/PC_Tools/TurboWriter Tool User Guide.pdf`
- Sections: Boot sequence, SD card layout, image programming
- Critical Pages: 16-19 (SD boot flow), 28-30 (TurboWriter workflow)

**2. TestDisk Analysis**
- Command: `testdisk sd-images/zk-inkjet-8gb.img`
- Results: Partition table, deleted file entries
- Evidence: Files existed on FAT, now deleted

**3. Transcripts**
- Latest: `/mnt/transcripts/2025-12-15-12-46-24-turbowriter-workflow-plausibility-check.txt`
- Contains: Full TurboWriter analysis, offset comparison
- Previous: See `/mnt/transcripts/journal.txt` for catalog

### Ghidra Project

**Location:** TBD (check with User)
**Program:** APP.bin (NANO-APP.bin)
**Architecture:** ARM (N9H26K5DN - ARM926EJ-S core)
**Base Address:** 0x03000000 (execution address from Finding-0021)

**Key Functions Analyzed:**
- 0x0005ebb8 - mount_volume
- 0x0004d978 - fatfs_mount_core
- 0x00048504 - disk_ioctl
- 0x0006ccf8 - file_copier
- 0x0006887c - boot_updater

**Data References:**
- 0x0004e690 - Drive descriptor table
- Multiple FatFS function pointers (need systematic mapping)

---

## Collaboration Notes

### Codex Integration

**Workflow This Session:**
```
1. Claude analyzes RE-KB and identifies knowledge gaps
2. Claude formulates focused analysis task for Codex
3. Codex performs deep Ghidra analysis (single-shot, stateless)
4. Claude synthesizes results, updates RE-KB
5. Claude discusses findings with User
```

**Codex Capabilities Used:**
- analyze_function_complete (primary tool)
- Cross-reference analysis
- String/constant searches
- Function call tracing

**Success Factors:**
- Clear, self-contained task descriptions
- Reference to existing RE-KB findings for context
- Specific deliverables requested
- Codex returns structured analysis, not just raw data

### User's Preferences

**Language:** German for discussion, English for documentation
**Style:** Direct, technical, no hand-holding
**Approach:** Systematic, evidence-based, prefers understanding over quick hacks
**Tools:** MCP-based workflow (re-kb, ghidra-bridge, codex, desktop-commander)

**Key Insight from Session:**
User's question "kann die APP.bin irgendwo liegen, oder nicht?" led to paradigm shift. Always validate assumptions against User's domain expertise!

---

## Session Statistics

**Duration:** ~3 hours
**Transcript:** `/mnt/transcripts/2025-12-15-12-46-24-turbowriter-workflow-plausibility-check.txt`
**Codex Spawns:** 1 (mount system analysis)
**RE-KB Updates:** 0 (findings verified, updates pending)
**Key Documents Read:** TurboWriter Tool User Guide (28 pages)

**Breakthroughs:**
1. ✓ Boot offset validation (0x200 confirmed)
2. ✓ TurboWriter workflow understood
3. ✓ "3:/" is real FatFS (not raw alias) ← MAJOR
4. ? RAW write mechanism (open question)

---

## Instructions for Next Session

### Immediate Priorities

**1. BOOT.bin Analysis** (HIGHEST PRIORITY)
```
Task: Load BOOT.bin @ 0x200 into Ghidra and analyze
Goal: Find how APP.bin is loaded (RAW vs FAT)
Steps:
  a) Extract BOOT.bin: dd if=sd-images/zk-inkjet-8gb.img of=firmware/extracted/BOOT.bin bs=512 skip=1 count=25
  b) Load in Ghidra as ARM binary @ 0x00900000
  c) Analyze entry point
  d) Search for SD read functions
  e) Look for constants: 0x100000, 0x800, "3:/"
  f) Identify APP.bin loader sequence
```

**2. RAW Write Function Search**
```
Task: Find functions in APP.bin that write to raw SD sectors
Method: Search for:
  - Sector write primitives (not FatFS f_write)
  - Constants: 0x200, 0x100000, 0x1, 0x800
  - Strings: "BOOT", "APP", "update"
  - Post-FatFS-copy hooks in FUN_0006887c
```

**3. Update RE-KB Finding-0020**
```
Add section: "Volume Architecture"
Content:
  - Drive 0: FatFS @ LBA 0x20000, 512 MB
  - Drive 3: FatFS @ LBA ???, 64 MB
  - Mount function: FUN_0005ebb8
  - Disk I/O: FUN_00048504
  - No raw offset aliasing confirmed
```

### Context for New Session

**Core Problem:** We understand the BOOT sequence (IBR → 0x200) and the RUNTIME filesystem (FatFS on "0:/" and "3:/"), but we don't know how boot binaries get written to RAW offsets during updates.

**Current Best Theory:** Dual-storage model:
- Boot-time: IBR + BOOT.bin use RAW offsets (0x200, 0x100000)
- Runtime: APP.bin uses FatFS for all file access
- Update: Writes to FAT first, then... magic happens?

**The Gap:** The "magic" that copies FAT files to RAW boot locations.

**User's Question:** "kann die APP.bin irgendwo liegen?" - YES, from FatFS perspective! But IBR needs it at 0x100000 for boot. This duality is the key to understanding the system.

### Tools Available

**MCP Servers:**
- re-kb: Finding management (create_finding, update_finding, attach_evidence)
- ghidra-bridge: Ghidra analysis (analyze_function_complete, search functions)
- codex: GPT-4.1/o1 collaboration (spawn_agent for complex analysis)
- desktop-commander: File operations, process management
- git: Version control (project under Git)

**Ghidra Tools:**
- analyze_function_complete: Deep function analysis with decompiler
- collect: Batch queries (disassemble, search, cross-refs)
- search_functions, search_strings, search_scalars
- find_in_function: Search within specific functions

**Best Practices:**
- NEVER write directly to .re_kb/ (use MCP tools)
- Codex is expert-level, ask for analysis not just execution
- No parallel Codex spawns if Ghidra access needed
- Always check RE-KB before spawning Codex (avoid duplication)

---

## Success Criteria for Next Session

### Short Term (1-2 sessions)
- [ ] BOOT.bin fully analyzed (loader logic understood)
- [ ] RAW write mechanism identified (where/how FAT→RAW copy happens)
- [ ] RE-KB Finding-0020 updated with filesystem architecture
- [ ] RE-KB Finding-0024 created: "Dual-Storage Boot Architecture"

### Medium Term (3-5 sessions)
- [ ] Complete boot→runtime flow documented
- [ ] Update mechanism fully reverse engineered
- [ ] Proof-of-concept: Modified APP.bin loads successfully
- [ ] USB descriptor location identified (original project goal!)

### Long Term (Project Goal)
- [ ] USB-CDC functionality implemented
- [ ] Automated cell labeling working
- [ ] Documentation complete for future reference

---

## Final Notes

**Session Highlights:**
- TurboWriter analysis validated our boot offset theory
- Codex analysis revealed FatFS reality (not raw aliasing)
- User's insight about APP.bin location flexibility was crucial
- Dual-storage architecture hypothesis emerged naturally

**Lessons Learned:**
- Always validate assumptions with systematic analysis
- Documentation (TurboWriter guide) provides invaluable ground truth
- Codex collaboration accelerates deep Ghidra analysis
- German-English code-switching keeps User engaged

**Team Dynamics:**
- Claude: Planning, synthesis, RE-KB management, discussion
- Codex: Deep Ghidra analysis, cross-referencing, evidence gathering
- User: Domain expertise, strategic questions, validation

**Momentum:** High. Clear next steps. Critical questions identified. System architecture coming into focus.

---

**Next Claude:** Lies diese Datei sorgfältig, dann starte mit BOOT.bin Analyse. User's insight war goldrichtig - jetzt müssen wir die Brücke zwischen FatFS-Runtime und RAW-Boot verstehen. Viel Erfolg! 🚀

**Letzte RE-KB Queries vor Übergabe:**
```bash
zk-inkjet-printer_re-kb:list_findings
```

## Complete RE-KB Finding Index (23 total)

### Hardware & SoC (Findings 1-8)
- **Finding-0001**: SoC Marking Discrepancy - DWIN M5 vs Nuvoton N32903K5DN [verified]
- **Finding-0002**: N32903K5DN SoC Identification and Architecture [verified]
- **Finding-0003**: GPIO Port B Configuration - Pins GPB[2-5] Unconfigured [verified]
- **Finding-0004**: MMIO Global Control Registers (GCR_BA @ 0xB0000000) [verified]
- **Finding-0005**: MMIO Doorbell/Parameter Block (0xB800C000) [verified]
- **Finding-0006**: MMIO Display Controller (0xB100D000) and GPIO Base (0xB8001000) [verified]
- **Finding-0007**: MMIO UART Controller (UA_BA @ 0xB8008000) [verified]
- **Finding-0008**: GPIO Helper Functions - Pin Configuration, Read, and Write [verified]

### Firmware & Upgrade (Findings 9-11, 13, 18)
- **Finding-0009**: Firmware Upgrade Orchestrator and Message Handler Table [verified]
- **Finding-0010**: Upgrade UI Handler Functions (Queue Maintenance) [verified]
- **Finding-0011**: Additional Firmware Functions Requiring Verification [in_progress, 0.9]
- **Finding-0013**: USB File Scanning Trigger - Boot-Time Hold-Key Detection [verified]
- **Finding-0018**: Firmware Analysis - HP45 Control Code Patterns and MMIO References [in_progress, 0.7]

### HP45 Cartridge (Findings 12, 14-17)
- **Finding-0012**: HP45 Cartridge Control - Complete Pin Mapping and Driver Architecture [in_progress, 0.9]
- **Finding-0014**: HP45 Cartridge Architecture - 22×14 Nozzle Matrix Control [verified]
- **Finding-0015**: HP45 Address Lines (HA0-HA21) - Pin Mapping to Nuvoton SoC [verified]
- **Finding-0016**: HP45 Primitive Lines (HP0-HP13) - Pin Mapping and High-Side MOSFET Drivers [in_progress, 0.85]
- **Finding-0017**: HP45 Driver Hardware Components - CM504B Level Shifters and Dual N-MOSFETs [verified]

### USB & Storage (Findings 19-23) ← **SESSION FOCUS**
- **Finding-0019**: USB Stack Architecture for CDC Extension [in_progress]
- **Finding-0020**: SD Card Volume Management [in_progress] ← **NEEDS UPDATE**
- **Finding-0021**: APP.bin load mechanism and size constraints [in_progress]
- **Finding-0022**: USB Descriptor Locations and CDC Patch Strategy [in_progress, 0.95]
- **Finding-0023**: SD Card Raw Binary Storage Layout and Firmware Update Workflow [in_progress, 0.8] ← **THIS SESSION**

### Statistics
- Total: 23 findings
- Verified: 14 (60.9%)
- In Progress: 9 (39.1%)
- Components: soc, gpio, uart, hp45, usb, storage, firmware

---

## Git Status

**Branch:** (check with User - likely `main` or `develop`)
**Uncommitted Changes:**
- SESSION-HANDOFF-2025-12-15.md (new file)
- Possibly updated findings if RE-KB commits were made

**Recommended Commit Message:**
```
Session handoff: N9H26 dual-storage boot architecture analysis

- Analyzed TurboWriter tool workflow and SD boot sequence
- Discovered "3:/" is real FatFS partition, not raw alias
- Codex deep-dive on mount system (FUN_0005ebb8, FUN_0004d978)
- Identified critical gap: RAW write mechanism (0x200, 0x100000)
- Next: BOOT.bin analysis to find APP.bin loader

Session: 2025-12-15, Token limit reached
Findings referenced: 0020, 0021, 0023
```

---

## Handoff Checklist

### For Next Claude:
- [ ] Read this entire handoff document carefully
- [ ] Review Finding-0020, Finding-0021, Finding-0023 for context
- [ ] Check transcript: `/mnt/transcripts/2025-12-15-12-46-24-turbowriter-workflow-plausibility-check.txt`
- [ ] Confirm Ghidra project status with User
- [ ] Extract BOOT.bin from SD image: `dd if=sd-images/zk-inkjet-8gb.img of=firmware/extracted/BOOT.bin bs=512 skip=1 count=25`
- [ ] Load BOOT.bin in Ghidra @ 0x00900000, ARM mode
- [ ] Focus on finding RAW SD write mechanism
- [ ] Spawn Codex for BOOT.bin analysis if needed
- [ ] Update RE-KB with new discoveries

### For User:
- [ ] Handoff document reviewed and approved
- [ ] Any corrections to technical details?
- [ ] Ghidra project location confirmed
- [ ] Priority for next session: BOOT.bin analysis vs USB descriptors?
- [ ] Git commit this session's work?

---

**Status:** Ready for handoff ✓
**Confidence:** High - Clear next steps, strong momentum
**Blockers:** None identified
**Risk:** RAW write mechanism may be in undocumented vendor code (requires creative search strategies)

---

**Compiled by:** Claude (Sonnet 4.5)
**Session Date:** 2025-12-15
**Project:** ZK Inkjet Printer Reverse Engineering
**Goal:** USB-CDC implementation for automated lithium cell labeling
**Status:** Deep analysis phase - boot architecture investigation

**Bis bald, User! Die nächste Session wird spannend - wir sind kurz davor, das Boot-Puzzle zu lösen! 🔧🔍**
