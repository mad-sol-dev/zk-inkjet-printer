# Session: USB Remote Control Discovery

**Date:** 2025-11-27
**Goal:** Identify practical injection points for USB-based remote control
**Tools:** Ghidra MCP, re-kb MCP, PDF reader MCP

---

## Session Summary

Initial goal was to find "oil" (valuable discoveries) in the firmware. Clarified actual objective: **remote control via USB to send text and trigger printing** (not full reverse engineering). User has tremor making hardware probing difficult, so software-only approaches preferred.

---

## Key Discoveries

### 1. HP45 Cartridge Control Strings
**Location:** String cluster @ 0x001f2xxx
**Evidence:**
- `"Nozzle Voltage"` @ 0x001f2cf4
- `"Cartridge Type"` @ 0x001f2df8
- `"Cartridge Num."` @ 0x001f2ba8
- `"Ink cartridge abnormal!"` @ 0x001f2994

**Hardware Context (per user):**
- 6x CM504B CMOS hex voltage level shifters
- Direct GPIO pin control (no shift registers)
- N32903K5DN LQFP-128 package (plenty of GPIO)
- Ports D and E actively used

**Documented:** Created finding-0012 in re-kb

---

### 2. USB File Processing Capabilities

**BMP Images (Printing):**
- Pattern: `3:/inkjet-ui-%04d%02d%02d %02d%02d%02d %d.bmp` @ 0x0001282c
- Format: `inkjet-ui-YYYYMMDD HHMMSS N.bmp`
- Volume 3:/ = USB stick
- **Implication:** Device already reads BMP files from USB for printing

**CSV Files (Configuration):**
- Path: `3:\inkjet-lite-vadj-sample.csv` @ 0x0006d577
- Purpose: Voltage adjustment / calibration data

**ZKML Resources:**
- Internal: `0:/ZK-INKJET-RES-HW.zkml`
- External: `3:/obds/res/ZK-INKJET-RES-HW.zkml`

**Firmware Upgrades:**
- Volume 3:/ (USB stick)
- Filename literal pool @ VA 0x0037E820
- Comparison function @ VA 0x0020E158 (memcmp)
- Success handler @ VA 0x0025AA54
- **NO checksums/CRC validation** (per update_file_rules.md)

---

### 3. Upgrade Pipeline Analysis

**Filename Matching:**
- Loop @ VA 0x0025a930 - scans literal pool
- memcmp @ VA 0x0020E158 - compares filenames
- Success branch @ VA 0x0025AA54 - processes matched file

**File Classification:**
- classify_basename @ VA 0x0027b61c
- Checks first character: 'i', 'u', 'v' (0x69, 0x75, 0x76)
- Different handlers for UI files vs firmware

**File Processing:**
- Upgrade handler @ VA 0x002c28d0
- Multiple function calls for buffer management
- Complex pipeline (not fully traced)

---

### 4. Timer Controller

**Specification (N3290x Design Guide pp. 669-672):**
- TMR_BA @ 0xB8002000
- Two channels: TIMER0, TIMER1
- Max time: (1/25MHz) * 2^8 * 2^32

**Firmware Usage:**
- No references to 0xB8002000 found
- **Implication:** Simple delay loops instead of hardware timers for nozzle timing

---

### 5. GPIO Configuration Clarification

**4-pin "Debug" Header:**
- Physical pins: 125-128 (GPB[2-5])
- Functions: GPIO / I2S / SD / Video sync
- **Status:** Unconfigured in firmware
- **NOT UART** (UART init goes to NOP loop elsewhere)
- Potential for interface hacking if firmware configured them

---

## Ruled Out / Corrected

1. ❌ Hardware timer usage for nozzle control
2. ❌ UART on 4-pin test pads (GPB[2-5] unconfigured)
3. ❌ Need to reverse engineer print engine (can use existing BMP pipeline)
4. ✅ DWIN/DGUS protocol ruled out (chip is Nuvoton, DWIN is just branding)

---

## Potential Attack Vectors for Remote Control

### Option 1: BMP Pipeline (No Firmware Mod)
**Pros:** Uses existing infrastructure, no patching needed
**Cons:** Requires external text→BMP converter, need to find trigger mechanism

**Approach:**
1. Create tool to convert text to BMP image
2. Use filename format: `3:/inkjet-ui-YYYYMMDD HHMMSS 0.bmp`
3. Determine trigger (UI menu? Auto-scan? Button?)

### Option 2: CSV Command Injection
**Pros:** Text-based format, already parsed by device
**Cons:** Need to hook parser, understand CSV format/purpose

**Approach:**
1. Analyze CSV parser code
2. Create command file: `3:/inkjet-commands.csv`
3. Format: `COMMAND,ARGS`

### Option 3: Firmware Upgrade Hijack
**Pros:** No checksums, well-documented
**Cons:** Meant for binary updates, not commands

**Approach:**
1. Add custom filename to literal pool @ 0x0037E820
2. Hook success handler @ 0x0025AA54
3. Parse command file instead of upgrade binary

### Option 4: Custom File Handler
**Pros:** Clean separation from existing files
**Cons:** Requires firmware patch

**Approach:**
1. Add new extension to file scanner
2. Minimal patch to dispatcher
3. Reuse existing text rendering functions

---

## Critical Unknowns

1. **File Trigger Mechanism:** How/when are USB files scanned and processed?
   - UI menu selection?
   - Auto-scan on USB insert?
   - Button combination?
   - Boot-time check?

2. **BMP Parsing Pipeline:** Where does BMP data go after parsing?
   - Direct to print buffer?
   - Callback functions?
   - Queue system?

3. **CSV Format Details:** What structure does the CSV parser expect?
   - Column format?
   - Header requirements?
   - Validation checks?

4. **Text Rendering Integration:** How to connect file input to text display/print?
   - Existing functions @ 0x002bad5c, 0x002be3ac, 0x002bb07c (per uart_control_consolidated.md)
   - Need to understand calling convention and parameters

---

## Next Steps

**Immediate:**
1. ✅ Create session log (this document)
2. ✅ Commit findings to repository
3. Find USB file trigger mechanism (UI handlers, event loops)
4. Trace BMP parsing pipeline to understand print path

**Medium-term:**
1. Choose attack vector based on trigger mechanism findings
2. Prototype minimal injection (BMP or CSV)
3. Test on hardware

**Long-term:**
1. Full text-to-print pipeline via USB
2. Command interface (print, display, config)
3. Documentation for end users

---

## MCP Server Status

**GhidraMCP (http://127.0.0.1:8099/sse):**
- ✅ Operational
- ✅ Program loaded: ZK-INKJET-NANO-APP.bin
- ✅ Search, disassembly, function listing working

**re-kb MCP (http://127.0.0.1:8000/sse):**
- ✅ Operational
- ✅ Project: zk-inkjet-printer
- ✅ Finding-0012 created successfully
- ⚠️ Requires reactivation after reconnect

**pdf-reader-mcp (stdio):**
- ✅ Operational
- ✅ N3290x_Design_Guide_A1.pdf accessible
- Used for Timer Controller specs (pp. 669-672)
- Used for GPIO specs (pp. 645-668)

---

## Files Modified

- `.re_kb/findings/finding-0012.json` - New finding created
- `.re_kb/index.json` - Updated with finding-0012

---

## References

**Documentation:**
- `docs/uart_control_consolidated.md` - Text rendering functions
- `docs/update_file_rules.md` - Firmware upgrade mechanism (no checksums)
- `docs/findings/gpio_configuration.md` - GPB[2-5] unconfigured
- `docs/analysis/gpio_pins_analysis.md` - Port D/E usage
- `docs/vendor/N3290x_Design_Guide_A1.pdf` - SoC specifications

**Firmware Addresses (VA = Virtual Address):**
- String cluster: 0x001f2xxx (cartridge/nozzle UI)
- Upgrade literal pool: VA 0x0037E820
- Filename comparison: VA 0x0020E158 (memcmp)
- Match success: VA 0x0025AA54
- File classifier: VA 0x0027b61c
- Upgrade handler: VA 0x002c28d0
- Text rendering: VA 0x002bad5c, 0x002be3ac, 0x002bb07c

**MCP Tools Used:**
- `mcp__ghidra__search_strings` - Found cartridge/nozzle strings
- `mcp__ghidra__disassemble_at` - Traced upgrade flow
- `mcp__ghidra__search_scalars_with_context` - Timer controller search
- `mcp__pdf-reader-mcp__read_pdf` - N3290x specs
- `mcp__re-kb__create_finding` - Documented discovery

---

## Verification Status

- ✅ MCP servers functioning correctly
- ✅ String discoveries verified in Ghidra
- ✅ Upgrade mechanism cross-referenced with update_file_rules.md
- ⏳ File trigger mechanism - pending investigation
- ⏳ BMP parsing pipeline - pending investigation
- ⏳ Attack vector selection - pending trigger discovery

---

**Session End:** 2025-11-27
**Outcome:** Identified multiple USB-based remote control vectors; pending trigger mechanism discovery
