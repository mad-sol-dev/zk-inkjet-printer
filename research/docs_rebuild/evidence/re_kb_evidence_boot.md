# BOOT Evidence (E3-New RE-KB Current)

**Source:** research/findings/.re_kb/findings/*.json (2 current findings)
**Tier:** E3-New (structured findings from post-optimization analysis)
**Note:** Post-Ghidra-optimization (1.3k functions). No [ghidra-v1] tag.

---

## Execution Architecture

### E-RKN-BOOT-001: Firmware ARM/Thumb Mixed-Mode Code
- **RE-KB ID:** finding-0001
- **Status:** verified
- **Type:** behavior
- **Summary:** APP.bin firmware contains both ARM (32-bit) and Thumb (16-bit) instruction sets. Region 0x00210000-0x0021FFFF uses Thumb mode (2-byte instructions), while other regions use ARM mode (4-byte instructions). Ghidra correctly detected and disassembled both modes.
- **Evidence:**
  - E1: Disassembly analysis at 0x00210000 shows clean Thumb instructions (ldr, mov, blx). Codex agent verified 18% Thumb / 82% ARM instruction ratio across sampled regions.; source_type=other
- **Tags:** architecture, thumb, arm, foundation
- **Confidence:** 1.0
- **Component:** firmware
- **Created:** 2025-12-27T22:29:22.720461Z
- **Updated:** 2025-12-27T22:29:22.720461Z

