# SOC Evidence (E3-Old RE-KB Archive)

**Source:** research/findings/re_kb_archive/findings/*.json (31 findings from historical RE-KB)
**Tier:** E3-Old (structured findings from earlier analysis sessions)
**Note:** These findings predate Ghidra optimization (37k→1.3k functions). Ghidra-based evidence should be marked [ghidra-v1].

---

## SoC Identification and Architecture

### E-RKO-SOC-001: SoC Marking Discrepancy - DWIN M5 vs Nuvoton N32903K5DN
- **RE-KB ID:** finding-0001
- **Status:** verified
- **Type:** behavior
- **Summary:** The main SoC is marked 'DWIN M5' on the PCB, but the actual chip is a Nuvoton N32903K5DN. This naming discrepancy appears throughout the firmware and documentation. The M5 designation may refer to a DWIN display module family, while the underlying silicon is Nuvoton's N32903 series.
- **Evidence:**
  - E1: System architecture and peripheral documentation; source_type=pdf; page=1 [ghidra-v1]
  - E2: Visual inspection of PCB confirmed M5 marking on the main SoC chip; source_type=other [ghidra-v1]
- **Tags:** soc, hardware, nuvoton, m5, dwin, pcb-marking
- **Confidence:** None
- **Component:** soc
- **Created:** 2025-11-26T22:28:18.267624Z
- **Updated:** 2025-12-02T03:04:42.934515Z

### E-RKO-SOC-002: N32903K5DN SoC Identification and Architecture
- **RE-KB ID:** finding-0002
- **Status:** verified
- **Type:** behavior
- **Summary:** Device uses Nuvoton N32903K5DN (ARM926EJ-S, LQFP-128, K5DN variant with no external SDRAM). Marked as 'DWIN M5'. Confirmed via USB descriptors, CP15 instructions, GPIO pinout match, and MMIO fingerprint. Features include USB 1.1 host, USB 2.0 HS device, LCD controller, SD/MMC, and GPIO multiplexing.
- **Evidence:**
  - E1: USB descriptor contains UTF-16LE string 'W55FA93 USB Card Reader 1.00' and vendor string 'Nuvoton' at 0x00475140, uniquely identifying controller vendor; source_type=ghidra; function_address=0x475180; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E2: CP15 instructions (mrc p15,0,pc,c7,c14,3 for cache drain, mrc p15,0,rx,c1,c0,0 for SCTLR read) prove ARM926EJ-S / ARMv5TEJ core. ARM/Thumb interworking stubs and vector layout match N32903 series (Ghidra analysis); source_type=other [ghidra-v1]
  - E3: GPIO register writes to GPBFUN @ 0xB0000084 match published multiplexer layout. Hardware probing confirmed GPB[2-5] on pins 125-128 matching N32903U5DN LQFP-128 pinout.; source_type=ghidra; function_address=0x31f34; function_name=pin_mux_config; program_name=ZK-INKJET-NANO-APP.bin; domain_file_id=7f011b6c592307498348432 [ghidra-v1]
  - E4: No SDRAM initialization routine in BOOT.bin or APP.bin. All RAM references within 8KB SRAM at 0xFF000000, confirming K5DN 'no external SDRAM' variant (firmware-wide analysis); source_type=other [ghidra-v1]
  - E5: N32903 architecture, memory map, and peripheral specifications; source_type=pdf [ghidra-v1]
  - E6: MMIO fingerprint: Clock/power registers at 0xB0000204/208/18/14, GPIO mux at 0xB000008C/84, doorbell at 0xB800C000, display controller at 0xB100D000; source_type=other [ghidra-v1]
- **Tags:** soc, hardware, nuvoton, n32903k5dn, arm926ej-s, verified
- **Confidence:** None
- **Component:** None
- **Created:** 2025-11-27T00:12:43.881101Z
- **Updated:** 2025-12-02T03:04:49.282868Z

