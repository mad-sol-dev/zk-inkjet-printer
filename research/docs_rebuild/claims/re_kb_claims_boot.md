# BOOT Claims (From E3-New RE-KB Current)

Propositional claims synthesized from current RE-KB findings. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## Execution Architecture

### ✅ Verified CL-RKN-BOOT-001: Firmware Uses ARM/Thumb Mixed-Mode Code
**Claim:** APP.bin firmware contains both ARM (32-bit) and Thumb (16-bit) instruction sets, with the 0x00210000-0x0021FFFF region in Thumb mode and other regions in ARM mode.

**Evidence:**
- E-RKN-BOOT-001: Disassembly analysis at 0x00210000 shows clean Thumb instructions (ldr, mov, blx). Codex agent verified 18% Thumb / 82% ARM instruction ratio across sampled regions.

**Status:** ✅ Verified

**Cross-Reference:**
- E1: CL-BOOT-007 (APP.bin ARM IVT)
- E1: CL-BOOT-016 (APP.bin resource container)
- E3: REKB_MAPPING notes partial overlap with BOOT claims

**Next Tests:** None listed

