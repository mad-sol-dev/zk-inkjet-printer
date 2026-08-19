# SOC Claims (From E3-Old RE-KB Archive)

Propositional claims synthesized from historical RE-KB findings. Status: ✅ Verified | ⚠️ Supported | 🔬 Hypothesis

---

## SoC Identification and Architecture

### ✅ Verified CL-RKO-SOC-001: SoC Marking Discrepancy - DWIN M5 vs Nuvoton N32903K5DN
**Claim:** The main SoC is marked 'DWIN M5' on the PCB, but the actual chip is a Nuvoton N32903K5DN. This naming discrepancy appears throughout the firmware and documentation. The M5 designation may refer to a DWIN display module family, while the underlying silicon is Nuvoton's N32903 series.

**Evidence:**
- E-RKO-SOC-001: System architecture and peripheral documentation
- E-RKO-SOC-001: Visual inspection of PCB confirmed M5 marking on the main SoC chip

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-SOC-002
**Next Tests:** None listed

---

### ✅ Verified CL-RKO-SOC-002: N32903K5DN SoC Identification and Architecture
**Claim:** Device uses Nuvoton N32903K5DN (ARM926EJ-S, LQFP-128, K5DN variant with no external SDRAM). Marked as 'DWIN M5'. Confirmed via USB descriptors, CP15 instructions, GPIO pinout match, and MMIO fingerprint. Features include USB 1.1 host, USB 2.0 HS device, LCD controller, SD/MMC, and GPIO multiplexing.

**Evidence:**
- E-RKO-SOC-002: USB descriptor contains UTF-16LE string 'W55FA93 USB Card Reader 1.00' and vendor string 'Nuvoton' at 0x00475140, uniquely identifying controller vendor
- E-RKO-SOC-002: CP15 instructions (mrc p15,0,pc,c7,c14,3 for cache drain, mrc p15,0,rx,c1,c0,0 for SCTLR read) prove ARM926EJ-S / ARMv5TEJ core. ARM/Thumb interworking stubs and vector layout match N32903 series (Ghidra analysis)
- E-RKO-SOC-002: GPIO register writes to GPBFUN @ 0xB0000084 match published multiplexer layout. Hardware probing confirmed GPB[2-5] on pins 125-128 matching N32903U5DN LQFP-128 pinout.
- E-RKO-SOC-002: No SDRAM initialization routine in BOOT.bin or APP.bin. All RAM references within 8KB SRAM at 0xFF000000, confirming K5DN 'no external SDRAM' variant (firmware-wide analysis)
- E-RKO-SOC-002: N32903 architecture, memory map, and peripheral specifications
- E-RKO-SOC-002: MMIO fingerprint: Clock/power registers at 0xB0000204/208/18/14, GPIO mux at 0xB000008C/84, doorbell at 0xB800C000, display controller at 0xB100D000

**Status:** ✅ Verified
**Cross-Reference:** Potential overlap with CL-SOC-001, CL-SOC-007
**Next Tests:** None listed

---
