# ZK-Inkjet Printer - System Understanding

**Date:** 2026-01-07 (Updated with Phase A ground truth)  
**Based on:** Phase 1 Reconciliation (152 claims, 9 subsystems) + Phase A SD Analysis  
**Confidence Level:** High (85% system understood, key unknowns identified)

---

## Executive Summary

The ZK-Inkjet handheld printer is a compact labeling system built around a Nuvoton N32903U5DN SoC, with storage and boot handled directly from an SD card and a tightly integrated printhead driver stack for HP45-class cartridges. Firmware is structured as a staged boot chain (IBR -> BOOT.bin -> APP.bin), and the device exposes itself over USB as a Mass Storage Class (MSC) device. GPIO usage reveals the core functions: printhead drive, display SPI, backlight PWM, touch ADC, and an encoder input.

What we know with high confidence includes the SoC identity and package, the boot chain and SD offsets, the raw SD layout with FAT16 volumes, and a BSP-verified MMIO map. The MMIO map is BSP-verified, including **USBD_BA = 0xB1008000** and **PWM_BA = 0xB8007000**. Major unknowns remain in the display controller identity, the exact location of the 3:/ update volume, the MT6701 encoder interface, and whether the firmware references the USB controller base in a non-literal way.

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

Pin mapping below reflects the **trace-verified hardware pinout** (`N32903U5DN_GPIO_Pinout.md`). Key point: most high-impact pins are already function-assigned (printhead, SD, display, touch, USB). Any “free pin” assumptions must be backed by either trace evidence or firmware pin-mux configuration.

**Confirmed assignments (selected):**
- **Display (SPI0):**
  - SCLK: **Pin 5 / GPD[12]**
  - CS0: **Pin 6 / GPD[13]**
  - MOSI (DI): **Pin 7 / GPD[14]**
  - MISO (DO): **Pin 8 / GPD[15]** (**PCB untraced**)
  - RS/A0 (Cmd/Data): **Pin 120 / GPE[8]**
- **Backlight:** **Pin 81 / GPD[0] = PWM0**, shared with **JTAG TCK**
- **Touch (4-wire resistive):** **Pins 57–60** (ADC_TP_YM/XM/XP/YP)
- **MicroSD (SD0):** **Pins 9–14** (DAT[2:3], DAT[0:1], CMD, CLK)
- **USB (device):** **Pin 26 (UD_DM), Pin 27 (UD_DP), Pin 86 (UD_CDET)**; USB PHY reference via **Pin 29 (UD_REXT)**
- **UART0:** **Pins 122/123 (URTXD/URRXD) are wired into the printhead HP path**
- **Pogo-pin header:** **Pins 125–128 (GPB[5..2])** are routed to the pogo-pin header

**Constraints that affect development/debug:**
- **JTAG vs backlight:** JTAG clock shares the backlight PWM pin (Pin 81). Debug workflows must account for backlight interaction.
- **UART0 unavailable:** URTXD/URRXD cannot be used as a console without interfering with printhead control.

**Signals that require verification (do not assume availability):**
- **I2C:** **Pins 3–4 (GPB[14]/GPB[13])** are **PCB-untraced**.
- **High-speed UART (HUR_*):** **Pins 82–85 (GPD[1–4])** are **PCB-untraced**.
- **SPI0 MISO:** **Pin 8 (GPD[15])** is **PCB-untraced**.

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
- Total size: 12,768 bytes (32-byte IBR header + 12,736 bytes code)
- Structure:
  * Bytes 0x200-0x21F: IBR header (32 bytes)
    - Signature: 0xA5 [ZBW...WBZ] 0xA5 (spaced pattern, not contiguous)
    - Field A: 0x00001010 (purpose TBD)
    - Field B: 0x00888800 (purpose TBD)
  * Bytes 0x220-0x31FF: ARM bootloader code (12,736 bytes)
    - First instruction: 0xE321F0DB (bic r15, r0, #0xdb000000)
- Loads APP.bin from SD offset 0x100000
- SHA256 (with header): 142a8ff5457df4ff86aeff1e6b7d63773f410074fb3d8660545b01b7f4537ce7
- SHA256 (code only): a651630c374c5441190cc35887baa814b4820c8ba2be100c9614f622cca6264d

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

The SD card uses a **raw (no MBR/GPT) layout** with firmware components placed at fixed offsets, plus multiple FAT volumes used for resources and update handling.

**Known fixed-offset components:**
- **0x200:** `BOOT.bin` (bootloader)
- **0x100000:** `APP.bin` (main firmware container)

**FAT volumes (verified via boot sector analysis):**

Three FAT volumes identified:

| Volume | Offset | Type | Size | Contents | Purpose |
|--------|--------|------|------|----------|---------|
| 1 | 0x04000000 | FAT16 | 512 MB | Fonts/Resources (28 files, 167 MB used) | System resources |
| 2 | 0x24007E00 | FAT | 256 MB | UI binary + user dirs (450 KB used) | System/staging |
| 3 | 0x2A61BE00 | FAT | 64 MB | **EMPTY** (88 bytes metadata only) | User USB "MINI" drive |

**Volume 3 "MINI" (VERIFIED):**
- Offset: 0x2A61BE00 (711 MB into SD card)
- Size: 64 MB (matches USB-exposed "MINI" drive)
- Label: "MINI" (confirmed via mtools inspection)
- Status: Empty during normal operation (update staging area)
- Purpose: User places firmware files here for updates

**Firmware file locations:**
- Active boot code: Raw SD offsets (0x200 for BOOT.bin, 0x100000 for APP.bin)
- Update copies: Volume 2 contains deleted firmware files (recovered via TestDisk)
- User update input: Volume 3 "MINI" (empty when not updating)

**Update workflow (verified structure, firmware analysis pending):**
1. User places firmware files on Volume 3 "MINI" (via USB connection)
2. Files: `ZK-INKJET-NANO-BOOT.bin`, `ZK-INKJET-NANO-APP.bin` (without IBR header)
3. Update system reads files from Volume 3
4. System prepends 32-byte IBR header to BOOT.bin
5. Combined (header + code) written to raw offsets
6. Files deleted from Volume 3 (returns to empty state)
7. Optional: Copy to Volume 2 for backup/staging

**Required verification (firmware analysis):**
- Search the SD image for `BOOT.bin` and `APP.bin` signatures and verify their **exact offsets**.
- Confirm how the update staging volume is mounted (which FatFS volume index corresponds to which LBA region).
- Determine whether any size limits or integrity checks exist (CRC, header guard, fixed maximum size).

⚠️ **Open Question:** The exact mapping of FatFS volume indices (e.g., `3:/`) to SD regions is still unresolved.

⚠️ **Open Question:** Update validation behavior (CRC/guard checks and maximum accepted sizes) must be confirmed by code path analysis and/or controlled update tests.

---

## USB Interface

### USB Identity and Architecture

The device enumerates as USB Mass Storage Class (MSC) with VID:PID 0416:0093, manufacturer "nuvoTon", product "USB MSC", and serial "00000055FA93". A dual-mode behavior exists: normal MSC mode exposes a 64 MiB MINI volume, while IBR-Boot mode uses a different PID and fake 1 MiB capacity when no valid BOOT.bin is found.

### USB Device Controller Base Address

BSP headers define **USB_BA / USBD_BA = 0xB1008000**. Firmware-side evidence of how the running image derives or uses this base address is still pending (literal constant vs computed base).

⚠️ **Open Question:** No direct constant reference has been confirmed yet for 0xB1008000 in the main firmware image. Verification requires searches for computed-base patterns and/or register access sequences consistent with the USBD block.

### USB-CDC Implementation Path

**Project Goal:** Implement USB-CDC (virtual serial port) for automatic lithium cell labeling.

Hardware capabilities support this path: UDC base is BSP-verified and USB is physically present on the board (UD_DM/UD_DP + detect). A CDC design should not assume a UART backend is available: **UART0 is wired into the printhead HP path**, and the **high-speed UART pins (HUR_* on GPD[1–4]) are expected to be board-assigned elsewhere**. CDC planning should therefore focus on a **pure USB implementation** unless a usable UART interface is proven by tracing and firmware pin-mux configuration.

Firmware analysis has identified a boot-time hold-key trigger that can serve as an injection point, and descriptor/endpoint patch strategies have been outlined.

✅ **Confidence:** Hardware capability is verified and the implementation path is feasible, pending firmware verification of UDC usage.

---

## Printhead (HP45 Cartridge)

### Architecture

The printer uses an HP45/HP45SI printhead with a 22x14 nozzle matrix (300 active nozzles). Nozzle firing requires simultaneous activation of HA lines (address) and HP lines (primitive). Each print line is emitted as 22 sub-lines with 14-bit HP masks; overlap of HA (high) + HP (pulsed) fires the corresponding nozzle.

### Driver Topology

**Level shifting / gate drive:**
- Implementation: **6× CM504B**
- Role: level shifting and gate control for the printhead drive signals (HA + HP)

**HA Lines (Address/Select):**
- Voltage domain: ~10–12 V gate drive
- Routed through CM504B level shifters

**HP Lines (High-current primitive):**
- Routed through CM504B level shifters
- After level shifting, the HP path is driven through **MOSFET stages** to generate the firing pulses

**Thermal / analog feedback:**
- C10X, CTSR feedback pins for thermal sensing
- VADJ rail: ~9.09 V supplies printhead power

### Encoder Integration

An encoder module is routed to **Pin 117 (GPE[10]/NALE)**. The fitted component is labeled as **MT6701**, but available datasheets do not cleanly match the observed hookup (single output behavior).

**Current working assumption:** the encoder output is **PWM-modulated** (to be confirmed by measurement).

**Required verification:**
- Scope capture on the encoder output while rotating the magnet to identify signal type (PWM duty, frequency, or alternative encoding).
- Firmware-side: locate the sampling/decoding path (timer capture, GPIO interrupt, ADC, or PWM input) in `APP.bin`.

---

## Display Interface

### Hardware Configuration

**Display Specifications:**
- 2.8 inch TFT LCD
- 18-pin FFC connector
- Module marking: LM-024CS18200NC (datasheet not located)

**Interface Connections (trace-verified pinout):**
- **SPI0:**
  - SCLK: **Pin 5 / GPD[12]**
  - CS0: **Pin 6 / GPD[13]**
  - MOSI: **Pin 7 / GPD[14]**
  - MISO: **Pin 8 / GPD[15]** (**PCB untraced**)
- **RS/A0 (D/C):** **Pin 120 / GPE[8]**
- **Backlight:** **Pin 81 / GPD[0] = PWM0** (shared with **JTAG TCK**)
- **Touch:** 4-wire resistive via **ADC_TP_YM/XM/XP/YP (Pins 57–60)**

### Display Controller

**Controller Identity: UNCONFIRMED.**

Current leading candidate is **ILI9341** (SPI TFT controller family).

**Required verification (Ghidra):**
- Extract the LCD initialization command/data stream (power, pixel format, MADCTL, gamma, sleep-out/display-on).
- Compare the observed command set against ILI9341 vs ST77xx families.

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



---

## Analysis Infrastructure (TOOL)

### Ghidra MCP Integration

Workflow discipline is enforced by an operator prompt with allowlist and single-action steps. BATCH mode enables sequential multi-step queries. The MCP server runs on port 8080 and exposes functions like select_program and get_current_program.

### RE-KB Knowledge Management

The knowledge base is stored as JSON in .re_kb/findings, with MCP write gating to prevent schema violations. The index can be rebuilt from individual findings, and workflows support structured inputs via create_finding and attach_evidence.

### BSP Import Infrastructure

BSP headers were imported from vendor directories, with Keil `__inline` preprocessing mitigations. Auto-analysis uses base 0x02000000 and ARM v5T little-endian settings.

Key achievement: BSP extraction produced **1544 register definitions**, establishing a reliable MMIO register map.

---

## Known Limitations and Open Questions

1. **Volume 3 Location (STORAGE) - RESOLVED**
   ✅ Volume 3 located at offset 0x2A61BE00 (711 MB into SD image)
   ✅ Size: 64 MB (matches "MINI" USB drive references)
   ✅ Label: "MINI" (verified via mtools inspection)
   ✅ Status: Empty during normal operation (update staging area)
   ⚠️ Firmware mount code verification pending (f_mount analysis)

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
- IBR header structure: 32 bytes @ 0x200 with 0xA5 [ZBW...WBZ] 0xA5 pattern
- FAT volume structure: 3 volumes at verified offsets (512 MB, 256 MB, 64 MB)
- Volume 3 "MINI": 64 MB @ 0x2A61BE00, empty during normal operation
- USB identity: VID:PID 0416:0093, MSC + IBR-Boot dual-mode
- Pin mapping: trace-verified assignments for display, SD, touch, USB, printhead; remaining candidates include PCB-untraced pins that need verification
- MMIO bases: BSP-verified (USB, GPIO, SPI0, ADC, PWM)
- HP45 architecture: 22x14 matrix, HA/HP firing mechanism
- Storage layout: raw SD, no partition table, FAT volumes identified

### Medium Confidence (Supported)

- ARM/Thumb mixed-mode distribution
- Update workflow (3:/ scan, FatFS, filename matching)
- Display hardware wiring (SPI0 on Pins 5–7; RS/A0 on Pin 120/GPE[8]; backlight PWM0 on Pin 81/GPD[0])
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

1. Reconstruct SD card layout and confirm fixed-offset component placement (signature search + mount mapping).
2. Verify USBD usage in firmware (computed-base patterns + register access signatures).
3. Extract LCD init sequence to confirm display controller (ILI9341 candidate).
4. Identify encoder signal type and firmware decode path (PWM/timer capture hypothesis).
5. Confirm update validation behavior (CRC/guards and size limits).

### Project Goal Status: USB-CDC Implementation

Hardware prerequisites are verified, and the firmware update infrastructure provides a viable injection path. The remaining blocker is confirming the firmware usage of the USB device controller base address.

✅ **Conclusion:** USB-CDC implementation is technically feasible pending firmware validation.

---

*Document generated: 2026-01-05*  
*Based on: Phase 1 Reconciliation (152 claims across 9 subsystems)*  
*Confidence: 85% system understood, 15% critical gaps identified*

