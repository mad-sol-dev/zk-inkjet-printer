# RE-KB Archive Catalog

**Source:** research/findings/re_kb_archive/ (31 findings from historical analysis)
**Extraction Date:** 2026-01-03
**Tier:** E3-Old

---

## Summary

- **Total Findings:** 31
- **Subsystems:** 8 (USB, BOOT, STORAGE, SOC, HARDWARE, HP45, DISPLAY, MMIO)
- **Evidence Files:** 8 (re_kb_old_evidence_*.md)
- **Claims Files:** 8 (re_kb_old_claims_*.md)

## Subsystem Breakdown

| Subsystem | Findings | Evidence Entries | Claims | Status Distribution |
|-----------|----------|------------------|--------|---------------------|
| USB | 3 | 19 | 3 | 1V, 2S, 0H |
| BOOT | 5 | 21 | 5 | 3V, 1S, 1H |
| STORAGE | 2 | 7 | 2 | 1V, 1S, 0H |
| SOC | 2 | 8 | 2 | 2V, 0S, 0H |
| HARDWARE | 4 | 18 | 4 | 4V, 0S, 0H |
| HP45 | 6 | 10 | 6 | 3V, 3S, 0H |
| DISPLAY | 7 | 27 | 7 | 2V, 2S, 3H |
| MMIO | 4 | 13 | 4 | 4V, 0S, 0H |

## Key Findings by Subsystem

### USB (3 findings)
- finding-0013: USB File Scanning Trigger - Boot-Time Hold-Key Detection
- finding-0019: USB Stack Architecture for CDC Extension
- finding-0022: USB Descriptor Locations and CDC Patch Strategy

### BOOT (5 findings)
- finding-0009: Firmware Upgrade Orchestrator and Message Handler Table
- finding-0010: Upgrade UI Handler Functions (Queue Maintenance)
- finding-0011: Additional Firmware Functions Requiring Verification
- finding-0021: APP.bin load mechanism and size constraints
- finding-0023: SD Card Raw Binary Storage Layout and Firmware Update Workflow

### STORAGE (2 findings)
- finding-0020: SD Card Volume Management
- finding-0023: SD Card Raw Binary Storage Layout and Firmware Update Workflow

### SOC (2 findings)
- finding-0001: SoC Marking Discrepancy - DWIN M5 vs Nuvoton N32903K5DN
- finding-0002: N32903K5DN SoC Identification and Architecture

### HARDWARE (4 findings)
- finding-0003: GPIO Port B Configuration - Pins GPB[2-5] Unconfigured
- finding-0006: MMIO Display Controller (0xB100D000) and GPIO Base (0xB8001000)
- finding-0008: GPIO Helper Functions - Pin Configuration, Read, and Write
- finding-0031: ADC Architecture: Voltage Monitoring & Touch Screen Controller

### HP45 (6 findings)
- finding-0012: HP45 Cartridge Control - Complete Pin Mapping and Driver Architecture
- finding-0014: HP45 Cartridge Architecture - 22×14 Nozzle Matrix Control
- finding-0015: HP45 Address Lines (HA0-HA21) - Pin Mapping to Nuvoton SoC
- finding-0016: HP45 Primitive Lines (HP0-HP13) - Pin Mapping and High-Side MOSFET Drivers
- finding-0017: HP45 Driver Hardware Components - CM504B Level Shifters and Dual N-MOSFETs
- finding-0018: Firmware Analysis - HP45 Control Code Patterns and MMIO References

### DISPLAY (7 findings)
- finding-0024: SPI0 LCD command/data wrappers (ST7789V path)
- finding-0025: ST7789V display bring-up and backlight enable
- finding-0026: LCD rendering primitives (window set, blit, pixel read/write)
- finding-0027: ST7789V SPI Display Driver - Core Functions and Init Sequence
- finding-0028: ST7789V Display Rendering Primitives - Blitter and Fill Functions
- finding-0029: UI Architecture - Menu System and About Screen
- finding-0030: Display Backlight and PWM Control

### MMIO (4 findings)
- finding-0004: MMIO Global Control Registers (GCR_BA @ 0xB0000000)
- finding-0005: MMIO Doorbell/Parameter Block (0xB800C000)
- finding-0006: MMIO Display Controller (0xB100D000) and GPIO Base (0xB8001000)
- finding-0007: MMIO UART Controller (UA_BA @ 0xB8008000)

---

## Integration Notes

**Overlap with E1 Claims:**
- finding-0001: Potential overlap with CL-SOC-002
- finding-0002: Potential overlap with CL-SOC-001, CL-SOC-007
- finding-0003: Potential overlap with CL-HARDWARE-015, CL-HARDWARE-016
- finding-0006: Potential overlap with CL-HARDWARE-005, CL-HARDWARE-014
- finding-0009: Potential overlap with CL-BOOT-011, CL-BOOT-012
- finding-0010: Potential overlap with CL-BOOT-011
- finding-0012: Potential overlap with CL-HP45-005, CL-HP45-007
- finding-0013: Potential overlap with CL-USB-004, CL-BOOT-011
- finding-0014: Potential overlap with CL-HP45-002
- finding-0015: Potential overlap with CL-HP45-005, CL-HP45-008
- finding-0016: Potential overlap with CL-HP45-006, CL-HP45-010
- finding-0017: Potential overlap with CL-HP45-005, CL-HP45-006
- finding-0018: Potential overlap with CL-HP45-012, CL-HP45-015
- finding-0019: Potential overlap with CL-USB-010, CL-USB-017
- finding-0020: Potential overlap with CL-STORAGE-006, CL-STORAGE-009
- finding-0021: Potential overlap with CL-BOOT-008, CL-BOOT-016
- finding-0022: Potential overlap with CL-USB-015, CL-USB-014
- finding-0023: Potential overlap with CL-STORAGE-004, CL-BOOT-011
- finding-0024: Potential overlap with CL-HARDWARE-005, CL-HARDWARE-014
- finding-0025: Potential overlap with CL-HARDWARE-006
- finding-0027: Potential overlap with CL-HARDWARE-005, CL-HARDWARE-014
- finding-0028: Potential overlap with CL-HARDWARE-005
- finding-0029: Potential overlap with CL-HARDWARE-011
- finding-0030: Potential overlap with CL-HARDWARE-006
- finding-0031: Potential overlap with CL-HARDWARE-011, CL-HARDWARE-007

**Ghidra Version Tags:**
- All Ghidra-based evidence marked [ghidra-v1] (pre-optimization)

**Next Steps:**
- Map E3-Old claims to E1 claims (Phase 2C-3 reconciliation)
- Identify contradictions and evidence upgrades
- Update REKB_MAPPING.md with E3-Old integration
