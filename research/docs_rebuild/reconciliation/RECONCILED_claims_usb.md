# USB Reconciled Claims (Phase 2C-3)

Authority order: E0 > E3-New > E1 > E3-Old > E4 (E2 = context only).

---

## CL-USB-REC-001: USB VID/PID Identity (0416:0093)

**Status:** verified
**Confidence:** 0.95
**Authority:** E1

**Statement:** The device enumerates as USB VID:PID 0416:0093.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-001 (dmesg enumeration shows 0416:0093), E-USB-006 (VID/PID ownership analysis)
- **E3-Old:** E-RKO-USB-003 (descriptor blob includes 0416:0093) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-USB-001
- E3-Old: CL-RKO-USB-003 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Cross-reference 0416:0093 with official Nuvoton/Winbond USB ID registry.

**Tags:** usb, vid-pid, identity

---

## CL-USB-REC-002: USB Descriptor Strings (Manufacturer/Product/Serial)

**Status:** verified
**Confidence:** 0.95
**Authority:** E1

**Statement:** USB descriptor strings report Manufacturer="nuvoTon", Product="USB MSC", SerialNumber="00000055FA93".

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-002 (manufacturer), E-USB-003 (product), E-USB-004 (serial)
- **E3-Old:** E-RKO-USB-003 (descriptor string table includes nuvoTon/USB MSC/serial) [ghidra-v1]
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-USB-002
- E3-Old: CL-RKO-USB-003 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Capture `lsusb -vvv -d 0416:0093` to confirm full string table and language IDs.

**Tags:** usb, descriptors, strings

---

## CL-USB-REC-003: Firmware Descriptor Block Contains W55FA93/Nuvoton Strings

**Status:** supported
**Confidence:** 0.85
**Authority:** E3-Old

**Statement:** Firmware embeds USB descriptor strings including "W55FA93 USB Card Reader 1.00" and vendor "Nuvoton" in the APP image.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-020 (analysis linking W55FA93 string family)
- **E3-Old:** E-RKO-USB-002 (descriptor blob at 0x00475140 contains W55FA93 string) [ghidra-v1]
- **E4:** E-OLD-USB-001 (descriptor block in app.bin contains W55FA93 + Nuvoton) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-USB-001
- E3-Old: CL-RKO-USB-002 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Verify string offsets in current APP.bin using `strings -tx` to avoid base-offset mismatches.

**Tags:** usb, descriptor, w55fa93

---

## CL-USB-REC-004: SCSI Device String Identifies "W55FA93 SPI Disk"

**Status:** verified
**Confidence:** 0.95
**Authority:** E1

**Statement:** The USB MSC layer presents as "W55FA93 SPI Disk" in the SCSI device string.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-005 (dmesg SCSI string)
- **E3-Old:** E-RKO-USB-003 (strings include W55FA93 USB Card Reader 1.00) [ghidra-v1]
- **E4:** E-OLD-USB-001 (firmware string) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E1: CL-USB-003

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Run `sg_inq /dev/sdX` to capture full INQUIRY response.

**Tags:** usb, scsi, device-string

---

## CL-USB-REC-005: USB Mass Storage Class Operation

**Status:** verified
**Confidence:** 0.95
**Authority:** E1

**Statement:** The device operates as a USB Mass Storage Class (MSC) device with usb-storage and SCSI Direct-Access.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-009 (usb-storage detected), E-USB-010 (SCSI host assignment)
- **E3-Old:** E-RKO-USB-001 (MSC device, not USB host) [ghidra-v1]
- **E4:** None
- **E2:** E2-USB-006 (MSC mode confirmed, not host)

**Source Claims:**
- E1: CL-USB-006
- E3-Old: CL-RKO-USB-001 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Check for additional USB configurations (CDC) by dumping descriptors during enumeration.

**Tags:** usb, msc, class

---

## CL-USB-REC-006: MSC Capacity (64 MiB)

**Status:** verified
**Confidence:** 0.95
**Authority:** E1

**Statement:** MSC exposes 131072 logical blocks of 512 bytes (64 MiB total).

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-011 (block count 131072)
- **E3-Old:** E-RKO-USB-001 (64MB MINI volume) [ghidra-v1]
- **E4:** None
- **E2:** E2-USB-006 (64MB MINI volume noted)

**Source Claims:**
- E1: CL-USB-007
- E3-Old: CL-RKO-USB-001 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** `sg_readcap -16 /dev/sdX` to confirm logical block count.

**Tags:** usb, capacity, msc

---

## CL-USB-REC-007: Single Partition Exposed (sda1)

**Status:** verified
**Confidence:** 0.90
**Authority:** E1

**Statement:** The device exposes a single partition (sda1) within the MSC volume.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-012 (sda1 detected)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-USB-008

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Inspect partition table with `fdisk -l /dev/sdX`.

**Tags:** usb, partition, msc

---

## CL-USB-REC-008: LBA Access Restriction Behavior

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** Reads beyond LBA 2111 trigger I/O errors and a USB disconnect, consistent with firmware-enforced access limits.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-015 (I/O error at sector 2111), E-USB-016 (USB disconnect), E-USB-017 (buffer errors), E-USB-018 (analysis: firmware-enforced limits)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-USB-009

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Probe LBA boundaries to map accessible range precisely.

**Tags:** usb, lba, errors

---

## CL-USB-REC-009: Dual-Mode Operation (MSC vs IBR-Boot)

**Status:** supported
**Confidence:** 0.85
**Authority:** E1

**Statement:** The device exposes normal MSC mode (PID 0093) and IBR-Boot recovery mode (PID 9396) depending on SD presence.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-007 (PID 0093 vs 9396), E-USB-008 (IBR discovery)
- **E3-Old:** E-RKO-USB-003 (IBR mode endpoints, PID 9396) [ghidra-v1]
- **E4:** None
- **E2:** E2-USB-011 (IBR mode PID 9396 noted)

**Source Claims:**
- E1: CL-USB-004
- E3-Old: CL-RKO-USB-003 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Capture descriptors in IBR mode and verify PID 9396 trigger with SD removed.

**Tags:** usb, ibr-boot, pid

---

## CL-USB-REC-010: IBR-Boot Mode Characteristics

**Status:** supported
**Confidence:** 0.80
**Authority:** E1

**Statement:** IBR-Boot mode reports product string "WPMUSB", manufacturer "NUVOTON", and a fake ~1.1 TB capacity.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-008 (WPMUSB, NUVOTON, fake 1.1TB)
- **E3-Old:** E-RKO-USB-003 (IBR mode endpoints) [ghidra-v1]
- **E4:** None
- **E2:** E2-USB-011 (IBR mode notes)

**Source Claims:**
- E1: CL-USB-005

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Record IBR mode `lsusb -vvv` output to verify descriptors and endpoint layout.

**Tags:** usb, ibr-boot, wpmusb

---

## CL-USB-REC-011: USB Device Controller Base Address (BSP)

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** BSP headers define USBD_BA/USB_BA as 0xB1008000 for the USB device controller.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (USBD_BA/USB_BA = 0xB1008000)
- **E3-New:** None
- **E1:** E-USB-019 (UDC base 0xB8007000, 10 refs) [superseded]
- **E3-Old:** E-RKO-USB-002 (UDC base 0xB8007000 from literals) [ghidra-v1] [superseded]
- **E4:** None
- **E2:** E2-USB-011 (documents 0xB8007000 error) [superseded]

**Source Claims:**
- E1: CL-USB-010
- E3-Old: CL-RKO-USB-002 (partial overlap)

**Superseded Evidence:**
- E-USB-019 (0xB8007000) superseded by BSP USBD_BA=0xB1008000.
- E-RKO-USB-002 (0xB8007000 literal mapping) superseded by BSP.

**Contradictions Resolved:** CONTRADICTION-USB-001

**Next Test:** Search for computed-address usage of 0xB1008000 (MOV/MOVT or base+offset patterns) in APP.bin.

**Tags:** usb, udc, mmio, bsp

---

## CL-USB-REC-012: UDC Register Names (BSP Ground Truth)

**Status:** verified
**Confidence:** 0.95
**Authority:** E0

**Statement:** BSP register map defines UDC endpoint registers such as EPA_CFG, EPB_CFG, EP*_MPS, and EP*_START/END_ADDR under USBD_BA.

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (EPA_CFG/EPB_CFG/EP*_MPS/EP*_START_ADDR/EP*_END_ADDR)
- **E3-New:** None
- **E1:** E-USB-024 (BSP register names) [superseded by E0]
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-USB-014

**Superseded Evidence:**
- E-USB-024 is superseded by the N32901-3 BSP headers in-repo.

**Contradictions Resolved:** None

**Next Test:** Map these offsets to firmware access patterns once UDC base usage is located.

**Tags:** usb, udc, registers, bsp

---

## CL-USB-REC-013: SPI Flash As MSC Backend (Inference)

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** The MSC backend is likely SPI flash, inferred from the "SPI Disk" SCSI string and 64 MiB capacity.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-005 (SCSI string "SPI Disk"), E-USB-021 (analysis linking 64 MiB to SPI flash)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-USB-011

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Identify the SPI flash part on PCB and compare capacity to 64 MiB.

**Tags:** usb, msc, spi-flash

---

## CL-USB-REC-014: USB-ISP/TurboWriter Support In SoC Family

**Status:** supported
**Confidence:** 0.75
**Authority:** E1

**Statement:** The W55FA93/N329/N9H2 family supports USB-ISP/TurboWriter modes for firmware programming.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-022 (vendor documentation note)
- **E3-Old:** None
- **E4:** None
- **E2:** None

**Source Claims:**
- E1: CL-USB-012

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Confirm N32903-specific documentation or BSP boot ROM notes for USB-ISP.

**Tags:** usb, isp, turbowriter

---

## CL-USB-REC-015: CDC Template Available In Related BSP

**Status:** supported
**Confidence:** 0.70
**Authority:** E1

**Statement:** A related BSP (N9H26) provides a CDC VirtualCom template with EP1 IN bulk, EP2 OUT bulk, and EP3 IN interrupt endpoints.

**Evidence (All Tiers):**
- **E0:** None (N9H26 BSP not present in repo)
- **E3-New:** None
- **E1:** E-USB-023 (CDC template endpoints, MPS details)
- **E3-Old:** None
- **E4:** None
- **E2:** E2-USB-011 (CDC strategy uses EP3)

**Source Claims:**
- E1: CL-USB-013

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Locate the N9H26 BSP source or use N32901-3 BSP examples to confirm CDC endpoint layouts.

**Tags:** usb, cdc, bsp

---

## CL-USB-REC-016: Descriptor Patch At 0x275140 Bricked Device

**Status:** verified
**Confidence:** 1.00
**Authority:** E1

**Statement:** Patching APP.bin at file offset 0x275140 bricked the device, indicating that location is not safely editable as a descriptor table.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-025 (descriptor patch test failure)
- **E3-Old:** E-RKO-USB-003 (earlier descriptor location claim) [ghidra-v1]
- **E4:** None
- **E2:** E2-USB-011 (risk assessment notes)

**Source Claims:**
- E1: CL-USB-015
- E3-Old: CL-RKO-USB-003 (partial overlap)

**Superseded Evidence:**
- E-RKO-USB-003 descriptor offset mapping is unreliable given the brick at 0x275140.

**Contradictions Resolved:** None

**Next Test:** Use `strings -tx APP.bin | rg -i "W55FA93|USB MSC|nuvoTon"` to find safe descriptor offsets.

**Tags:** usb, descriptors, patching

---

## CL-USB-REC-017: APP.bin Extension Preserves MSC

**Status:** verified
**Confidence:** 0.95
**Authority:** E1

**Statement:** Extending APP.bin by +4 KB does not break boot or USB MSC functionality.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-026 (padding test success)
- **E3-Old:** E-RKO-USB-002 (no trailing 0xFF padding noted) [ghidra-v1]
- **E4:** None
- **E2:** E2-USB-011 (extensibility noted)

**Source Claims:**
- E1: CL-USB-016
- E3-Old: CL-RKO-USB-002 (partial overlap)

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Determine maximum safe extension size without breaking memory layout.

**Tags:** usb, msc, extensibility

---

## CL-USB-REC-018: UDC Init Candidates Require Revalidation

**Status:** hypothesis
**Confidence:** 0.60
**Authority:** E1

**Statement:** Candidate USB initialization functions (0x30ab8, 0x46e48, 0x8b03c, 0xa3b08, 0xb4068, 0xb40fc) are unverified and must be rechecked against the corrected UDC base (0xB1008000).

**Evidence (All Tiers):**
- **E0:** `research/old_docs/vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/w55fa93_reg.h` (UDC base 0xB1008000)
- **E3-New:** None
- **E1:** E-USB-028 (candidate UDC init functions)
- **E3-Old:** E-RKO-USB-002 (UDC init map at 0xB8007000) [ghidra-v1]
- **E4:** None
- **E2:** E2-USB-011 (base address corrected)

**Source Claims:**
- E1: CL-USB-017
- E3-Old: CL-RKO-USB-002 (partial overlap)

**Superseded Evidence:**
- E-RKO-USB-002 register map tied to 0xB8007000 is superseded by BSP base 0xB1008000.

**Contradictions Resolved:** CONTRADICTION-USB-001

**Next Test:** Re-run Ghidra searches for EP*_CFG/EP*_MPS offsets relative to 0xB1008000.

**Tags:** usb, udc, init, hypothesis

---

## CL-USB-REC-019: Descriptor Location Mapping (Refuted)

**Status:** refuted
**Confidence:** 0.80
**Authority:** E1

**Statement:** The prior mapping of USB descriptors at VA 0x475101/0x475118/0x475140 (file offsets 0x275101/0x275118/0x275140) is unreliable and should not be used without revalidation.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** E-USB-025 (patching 0x275140 bricked device)
- **E3-Old:** E-RKO-USB-003 (descriptor location mapping) [ghidra-v1]
- **E4:** None
- **E2:** E2-USB-011 (base offset mismatch noted)

**Source Claims:**
- E3-Old: CL-RKO-USB-003

**Superseded Evidence:**
- E-RKO-USB-003 descriptor offsets superseded by E1 test failure.

**Contradictions Resolved:** None

**Next Test:** Locate descriptors by searching for USB string constants and verifying pointer tables.

**Tags:** usb, descriptors, refuted

---

## CL-USB-REC-020: USB Update Workflow (MINI Volume + Hold-Key)

**Status:** supported
**Confidence:** 0.70
**Authority:** E3-Old

**Statement:** USB update workflow uses a boot-time hold-key trigger and runtime update menus, exposing a 64 MB "MINI" MSC volume for file transfer before copying into internal storage.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** E-RKO-USB-001 (hold-key trigger, update menus, MINI volume flow) [ghidra-v1]
- **E4:** None
- **E2:** E2-USB-006 (strategy notes align with MINI workflow)

**Source Claims:**
- E3-Old: CL-RKO-USB-001

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Validate the MINI volume flow against current firmware with USB menu and update actions.

**Tags:** usb, update, workflow

---

## CL-USB-REC-021: USB-C Wiring And Detect Pin

**Status:** supported
**Confidence:** 0.75
**Authority:** E4

**Statement:** USB D+/D- and UD_REXT are wired to the USB-C connector, and UD_CDET is routed for USB detect.

**Evidence (All Tiers):**
- **E0:** None
- **E3-New:** None
- **E1:** None
- **E3-Old:** None
- **E4:** E-OLD-USB-002 (USB-C data/PHY wiring), E-OLD-USB-003 (USB detect pin) [ghidra-v1]
- **E2:** None

**Source Claims:**
- E4: CL-OLD-USB-002

**Superseded Evidence:** None

**Contradictions Resolved:** None

**Next Test:** Confirm UD_CDET toggles on plug/unplug with a scope.

**Tags:** usb, hardware, usb-c
