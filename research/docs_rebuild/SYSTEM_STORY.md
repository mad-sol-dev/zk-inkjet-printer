# ZK-Inkjet Printer - System Understanding

**Date:** 2026-01-05
**Based on:** Phase 1 Reconciliation (152 claims, 9 subsystems)
**Confidence Level:** Mixed (32% verified, 53% supported, 13% hypothesis, 1% refuted)

---

## Executive Summary

The ZK-Inkjet handheld printer is a compact labeling system built around a Nuvoton N32903U5DN SoC, with storage and boot handled directly from an SD card and a tightly integrated printhead driver stack for HP45-class cartridges. Firmware is structured as a staged boot chain (IBR -> BOOT.bin -> APP.bin), and the device exposes itself over USB as a Mass Storage Class (MSC) device. GPIO usage reveals the core functions: printhead drive, display SPI, backlight PWM, touch ADC, and an encoder input.

What we know with high confidence includes the SoC identity and package, the boot chain and SD offsets, the raw SD layout with FAT16 volumes, and a BSP-verified MMIO map. The most impactful correction was the USB device controller base address, which moved from a pre-optimization claim (0xB8007000) to the BSP-confirmed base (0xB1008000). Major unknowns remain in the display controller identity, the exact location of the 3:/ update volume, the MT6701 encoder interface, and whether the firmware references the USB controller base in a non-literal way.

The project goal remains a USB-CDC implementation for automatic lithium cell labeling. Hardware availability and pin budget appear sufficient for CDC, but the firmware entry point and UDC usage need verification before a safe patch can be constructed.

---

## Hardware Foundation

### System-on-Chip (N32903U5DN)

The system is built around a Nuvoton N32903U5DN SoC in LQFP-128 package. This is the U-series variant (not K-series), confirmed through pin measurements and system readout. The chip is physically marked "M5 dwin.com.cn" which is DWIN Technology OEM branding, not the chip identity itself.

**Key Specifications:**
- Architecture: ARM926EJ-S @ 200 MHz class clock
- Memory: 8 MB DDR SDRAM @ 1.8V (MVDD) in MCP package
- Package: LQFP-128 (U-series pinout)
- GPIO: 72 pins with alternate functions documented

⚠️ **Open Question:** The USB descriptor string "W55FA93" appears in firmware. This is legacy Winbond naming from before Nuvoton's acquisition and refers to the same chip family.

### Memory Architecture

The system uses external DDR SDRAM within the MCP package. DDR rails are measured at 1.8V (MVDD/MVREF), and the memory controller behavior aligns with U-series N32903 variants. Internal ROM (IBR) and SRAM are present for early boot and staging, but the primary firmware runs from RAM at 0x03000000 after being loaded from SD.

### GPIO Allocation

Analysis shows 31 GPIOs actively used and 41 remaining free, with most active pins tied to printhead control, display SPI, backlight PWM, touch ADC, and encoder input.

**Used GPIO Functions:**
- Printhead control: ~30 pins (GPA/GPD via CM504B drivers)
- Display interface: SPI0 pins (GPE[0-3])
- Backlight control: PWM0/GPE[12]
- Touch interface: 4-wire resistive (ADC channels)
- Encoder feedback: Pin 117/GPE[10] -> MT6701 connection

**Available GPIO Candidates:**
- I2C: GPB[13-14] (potentially free, needs verification)
- High-speed UART: GPD[1-4] (documented as available)
- USB Device pins: 26-28, 86 (unused, UDC available)

⚠️ **Open Question:** GPB[2-5] are unconfigured in firmware but physical availability needs PCB trace verification.

---

## Boot Process and Storage

### Boot Sequence

The device boots from SD card in a three-stage process:

**Stage 1: IBR (Initial Boot ROM)**
- 16 KB ROM inside the SoC
- Reads SD card sector at offset 0x200
- No fallback; SD card is required for boot

**Stage 2: BOOT.bin (Bootloader)**
- Located at SD offset 0x200
- Size: 12.7 KB
- Signature: "ZBWp1WBZ" at start
- Loads APP.bin from SD offset 0x100000

**Stage 3: APP.bin (Main Firmware)**
- Located at SD offset 0x100000
- Size: ~2.6 MB proprietary resource container
- Contains ARM interrupt vector table
- Loaded to RAM address 0x03000000
- Execution starts from loaded image

Hardware supports SD, NAND, SPI, and USB boot modes, but this device only implements SD boot (no other mode detected in firmware).

### ARM/Thumb Mixed-Mode Code

APP.bin uses mixed ARM/Thumb instruction modes. Post-optimization analysis shows Thumb regions embedded within ARM code, with roughly 18% Thumb and 82% ARM. This corrected earlier over-detection from the 37k-function pre-optimization database.

### SD Card Layout

The SD card uses a raw binary layout with no MBR or GPT partition tables. The image is 4,026,531,840 bytes (3.75 GiB) with 512-byte sectors.

**Key Offsets (E0 verified from SD image):**
- 0x200: BOOT.bin (bootloader)
- 0x100000: APP.bin (main firmware)
- LBA 0x20000: FAT16 volume (fonts, resources)
- LBA 1,179,711: FAT16 volume (firmware update files)
- LBA 1,388,767: Small FAT volume (likely MINI/USB MSC)

**Update Mechanism:**
Firmware scans volume 3:/ for update files with hardcoded filename matching. The update orchestrator uses FatFS (f_open/f_read) to load new firmware.

⚠️ **Open Question:** "Volume 3" location is not definitively mapped. Firmware analysis of the mount function is required to resolve it.

⚠️ **Open Question:** Update validation mechanism is unclear; evidence conflicts on CRC or guard checks.

---

## USB Interface

### USB Identity and Architecture

The device enumerates as USB Mass Storage Class (MSC) with VID:PID 0416:0093, manufacturer "nuvoTon", product "USB MSC", and serial "00000055FA93". A dual-mode behavior exists: normal MSC mode exposes a 64 MiB MINI volume, while IBR-Boot mode uses a different PID and fake 1 MiB capacity when no valid BOOT.bin is found.

### USB Device Controller Base Address

**Critical Discovery:** Early firmware analysis identified UDC base as 0xB8007000 with 10 references in APP.bin. BSP headers definitively show USB_BA/USBD_BA = 0xB1008000 and PWM_BA = 0xB8007000. The earlier references were PWM accesses misidentified as USB.

⚠️ **Open Question:** No firmware references have been found yet for 0xB1008000. Pattern searches (MOV/MOVT, computed base + offset) are required to verify actual UDC usage.

### USB-CDC Implementation Path

**Project Goal:** Implement USB-CDC (virtual serial port) for automatic lithium cell labeling.

Hardware capabilities support this path: UDC base is BSP-verified, USB device pins are documented as unused, and a high-speed UART backend is available on GPD[1-4]. Firmware analysis has identified a boot-time hold-key trigger that can serve as an injection point, and descriptor/endpoint patch strategies have been outlined.

✅ **Confidence:** Hardware capability is verified and the implementation path is feasible, pending firmware verification of UDC usage.

---

## Printhead (HP45 Cartridge)

### Architecture

The printer uses an HP45/HP45SI printhead with a 22x14 nozzle matrix (300 active nozzles). Nozzle firing requires simultaneous activation of HA lines (address) and HP lines (primitive). Each print line is emitted as 22 sub-lines with 14-bit HP masks; overlap of HA (high) + HP (pulsed) fires the corresponding nozzle.

### Driver Topology

**HA Lines (Address/Level Shifting):**
- Voltage: 10-12V gate drive
- Implementation: 6x CM504B level shifter ICs
- GPIO: GPA/GPD pins (30 GPIOs total)

**HP Lines (High-Current Primitive):**
- Voltage: 9-13V
- Timing: 1.5-2 us pulses
- Implementation: Separate high-current MOSFET drivers

**Thermal Control:**
- C10X, CTSR feedback pins for thermal sensing
- VADJ rail: ~9.09V supplies printhead power

### Encoder Integration

An MT6701 magnetic encoder connects to Pin 117 (GPE[10]/NALE). The UI "About" screen reports an encoder status value, indicating live feedback.

⚠️ **Open Question:** The firmware driver path and protocol for the encoder are not yet identified.

---

## Display Interface

### Hardware Configuration

**Display Specifications:**
- 2.8 inch TFT LCD
- 18-pin FFC connector
- Module marking: LM-024CS18200NC (datasheet not located)

**Interface Connections:**
- SPI0: SCL/SDA/SDO + CS
- RS/A0 (D/C): Pin 120
- Backlight: PWM0/GPE[12]
- Touch: 4-wire resistive (XL, YU, XR, YD -> ADC channels)

### Display Controller

**Controller Identity: UNCONFIRMED.**

Earlier analysis suggested ST7789V, but a 2026 follow-up could not extract a clean initialization sequence. The firmware function `lcd_send_command()` appears as an endless loop in decompilation, which may indicate misidentified code paths or indirect calls.

⚠️ **Hypothesis Status:** Controller is either ST7789V or ILI9341, both plausible SPI TFT controllers. Definitive identification requires extracting the real init sequence.

---

## Memory-Mapped I/O (MMIO)

All peripheral base addresses are BSP-verified from the N32901-3 NonOS BSP headers (1544 registers extracted).

**Verified Bases:**
- GCR_BA: 0xB0000000
- GPIO_BA: 0xB8001000
- USB_BA / USBD_BA: 0xB1008000
- SPI0_BA: 0xB800C000
- ADC_BA: 0xB800E000
- TMR_BA: 0xB8002000
- PWM_BA: 0xB8007000
- BLT_BA (Display engine): 0xB100D000

Historical [ghidra-v1] analysis misidentified 0xB800C000 as a doorbell block; BSP headers confirm it is SPI0_BA.

---

## Analysis Infrastructure (TOOL)

### Ghidra MCP Integration

Workflow discipline is enforced by an operator prompt with allowlist and single-action steps. BATCH mode enables sequential multi-step queries. The MCP server runs on port 8080 and exposes functions like select_program and get_current_program.

### RE-KB Knowledge Management

The knowledge base is stored as JSON in .re_kb/findings, with MCP write gating to prevent schema violations. The index can be rebuilt from individual findings, and workflows support structured inputs via create_finding and attach_evidence.

### BSP Import Infrastructure

BSP headers were imported from vendor directories, with Keil __inline preprocessing mitigations. Auto-analysis uses base 0x02000000 and ARM v5T little-endian settings. A headless wrapper (gh.sh) is documented but remains unverified in repo state.

Key achievement: BSP extraction produced 1544 register definitions, correcting multiple MMIO base errors.

---

## Known Limitations and Open Questions

1. **Volume 3 Location (STORAGE)**
   ⚠️ Firmware references 3:/ but its SD location is unresolved.

2. **USB Firmware Usage (USB)**
   ⚠️ USB_BA is BSP-verified but firmware references are unconfirmed.

3. **Display Controller Identity (DISPLAY)**
   ⚠️ ST7789V or ILI9341; init sequence extraction needed.

4. **MT6701 Encoder Interface (HARDWARE/SOC)**
   ⚠️ Pin 117 connection documented; firmware driver path unknown.

5. **Update Validation (BOOT/STORAGE)**
   ⚠️ Conflicting evidence on CRC/guard checks.

6. **Base Address Convention (TOOL)**
   ⚠️ Historical analyses used 0x200000 vs current 0x02000000 base.

---

## Confidence Assessment

### High Confidence (Verified)

- Chip identity: N32903U5DN (U-series, 8MB DDR)
- Boot chain: IBR -> BOOT.bin -> APP.bin -> RAM 0x03000000
- USB identity: VID:PID 0416:0093, MSC + IBR-Boot dual-mode
- GPIO allocation: 31 used, 41 free (detailed map)
- MMIO bases: BSP-verified (USB, GPIO, SPI0, ADC, PWM)
- HP45 architecture: 22x14 matrix, HA/HP firing mechanism
- Storage layout: raw SD, no partition table, FAT volumes identified

### Medium Confidence (Supported)

- ARM/Thumb mixed-mode distribution
- Update workflow (3:/ scan, FatFS, filename matching)
- Display hardware wiring (SPI0, Pin 120 RS/A0, PWM0 backlight)
- Touch interface (4-wire resistive via ADC)
- Encoder on Pin 117

### Low Confidence (Hypothesis)

- Display controller identity (ST7789V vs ILI9341)
- Volume 3 location
- UDC firmware usage
- Encoder protocol
- Update validation mechanism

### Refuted

- N32903K5DN identity (refuted)
- "No SDRAM" assumption (refuted)

---

## Summary and Next Steps

Phase 1 established a reconciled, multi-tier system understanding: 189 input claims condensed to 152 reconciled claims with clear authority. The system architecture is well understood, while a small set of critical unknowns remains.

### Phase 2 Priorities

1. Resolve Volume 3 mapping (mount function analysis).
2. Verify USB_BA usage via computed-base search.
3. Extract LCD init sequence to identify controller.
4. Locate MT6701 driver path.
5. Confirm update validation (CRC/guard checks).

### Project Goal Status: USB-CDC Implementation

Hardware prerequisites are verified, and the firmware update infrastructure provides a viable injection path. The remaining blocker is confirming the firmware usage of the USB device controller base address.

✅ **Conclusion:** USB-CDC implementation is technically feasible pending firmware validation.

---

*Document generated: 2026-01-05*
*Based on: Phase 1 Reconciliation (152 claims across 9 subsystems)*
*Confidence: 85% system understood, 15% critical gaps identified*
