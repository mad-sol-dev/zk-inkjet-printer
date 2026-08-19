# USB Claims

Propositional claims synthesized from USB evidence. Each claim represents a verifiable statement about the system.

---

## CL-USB-001: USB VID/PID Identity
- **Status:** verified
- **Confidence:** 0.95
- **Statement:** USB device enumerates as VID:PID 0416:0093, which is registered to Nuvoton/Winbond
- **Evidence:**
  - E1: E-USB-001 (dmesg enumeration log showing 0416:0093)
  - E1: E-USB-006 (analysis confirming Winbond/Nuvoton ownership)
  - E1: E-USB-007 (session summary confirming VID=0416)
- **Counter-Evidence:** None
- **Contradictions:** Related to Cluster-SOC-001 (W55FA93 vs N32903U5DN chip identity)
- **Revisions:** None
- **Next Test:** Cross-reference VID:PID with official Nuvoton USB device database
- **Tags:** vid-pid, identity, verified

---

## CL-USB-002: Device String Descriptors
- **Status:** verified
- **Confidence:** 0.95
- **Statement:** Device reports USB descriptor strings: Manufacturer="nuvoTon", Product="USB MSC", SerialNumber="00000055FA93"
- **Evidence:**
  - E1: E-USB-002 (dmesg manufacturer string)
  - E1: E-USB-003 (dmesg product string)
  - E1: E-USB-004 (dmesg serial number)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Dump full USB descriptors with `lsusb -vvv -d 0416:0093` to verify all descriptor fields
- **Tags:** descriptors, strings, verified

---

## CL-USB-003: SCSI Device Identification
- **Status:** verified
- **Confidence:** 0.95
- **Statement:** SCSI layer identifies device as "W55FA93 SPI Disk" (Direct-Access, PQ=0, ANSI=0 CCS)
- **Evidence:**
  - E1: E-USB-005 (dmesg SCSI device string)
- **Counter-Evidence:** None
- **Contradictions:** Related to Cluster-SOC-001 (chip name W55FA93 vs N32903U5DN)
- **Revisions:** None
- **Next Test:** Query SCSI device with `sg_inq /dev/sdX` to get full INQUIRY response
- **Tags:** scsi, device-string, w55fa93

---

## CL-USB-004: Dual-Mode Operation (MSC vs IBR-Boot)
- **Status:** supported
- **Confidence:** 0.85
- **Statement:** Device supports two operational modes: Normal MSC (PID 0093) and IBR-Boot recovery mode (PID 9396, triggered when SD card is absent)
- **Evidence:**
  - E1: E-USB-007 (session summary documenting PID 0093 vs 9396)
  - E1: E-USB-008 (IBR discovery with PID 9396, product "WPMUSB")
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Boot device without SD card and capture USB descriptors with PID 9396 to verify IBR-Boot mode activation
- **Tags:** dual-mode, ibr-boot, pid-9396, recovery

---

## CL-USB-005: IBR-Boot Mode Characteristics
- **Status:** supported
- **Confidence:** 0.80
- **Statement:** IBR-Boot mode (PID 9396) reports product string "WPMUSB", manufacturer "NUVOTON", and presents fake capacity of 1.1TB
- **Evidence:**
  - E1: E-USB-008 (IBR discovery showing WPMUSB and fake capacity)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Analyze IBR-Boot mode protocol to determine if it's USB-ISP/NuWriter/TurboWriter compatible
- **Tags:** ibr-boot, wpmusb, fake-capacity, recovery-mode

---

## CL-USB-006: USB Mass Storage Class Operation
- **Status:** verified
- **Confidence:** 0.95
- **Statement:** Device operates as USB Mass Storage Class (SCSI Direct-Access) with usb-storage driver
- **Evidence:**
  - E1: E-USB-009 (dmesg: "USB Mass Storage device detected")
  - E1: E-USB-010 (dmesg: SCSI host assignment)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Check if CDC descriptors exist but are inactive (multi-configuration device)
- **Tags:** usb-storage, msc, scsi, verified

---

## CL-USB-007: Storage Capacity
- **Status:** verified
- **Confidence:** 0.95
- **Statement:** USB MSC exposes 131072 × 512-byte logical blocks (64 MiB total capacity)
- **Evidence:**
  - E1: E-USB-011 (dmesg block count)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Verify actual readable capacity with `sg_readcap -16 /dev/sdX`
- **Tags:** capacity, 64mb, blocks, verified

---

## CL-USB-008: Single Partition Exposure
- **Status:** verified
- **Confidence:** 0.90
- **Statement:** Device exposes single partition (sda1) within the 64 MiB capacity
- **Evidence:**
  - E1: E-USB-012 (dmesg partition detection: "sda: sda1")
- **Counter-Evidence:** None
- **Contradictions:** Related to STORAGE claims about volume 0:/ (MINI partition)
- **Revisions:** None
- **Next Test:** Examine partition table with `fdisk -l /dev/sdX` or `parted /dev/sdX print`
- **Tags:** partition, sda1, verified

---

## CL-USB-009: LBA Access Restrictions
- **Status:** supported
- **Confidence:** 0.80
- **Statement:** Read attempts at sector 2111 and beyond trigger firmware-enforced I/O errors followed by USB disconnect, indicating LBA-based access restrictions rather than hardware defects
- **Evidence:**
  - E1: E-USB-015 (dmesg I/O error at sector 2111)
  - E1: E-USB-016 (USB disconnect after error)
  - E1: E-USB-017 (buffer errors on partition)
  - E1: E-USB-018 (analysis: FW-enforced LBA protection)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Systematically probe LBA range boundaries to map accessible vs restricted sectors
- **Tags:** lba-protection, io-error, firmware-behavior

---

## CL-USB-010: USB Device Controller Base Address
- **Status:** supported
- **Confidence:** 0.85
- **Statement:** USB Device Controller (UDC) registers are mapped at MMIO base address 0xB8007000, with 10 references found in APP.bin
- **Evidence:**
  - E1: E-USB-019 (binary analysis showing UDC-Base=0xB8007000 with 10 refs)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Disassemble UDC register access patterns in APP.bin to identify EP configuration writes
- **Tags:** udc-base, mmio, controller, 0xb8007000

---

## CL-USB-011: SPI Flash as USB MSC Backend
- **Status:** supported
- **Confidence:** 0.85
- **Statement:** Device architecture uses SPI Flash as storage backend, exposed to host as USB Mass Storage device (64 MiB capacity matches typical SPI Flash sizes)
- **Evidence:**
  - E1: E-USB-005 (SCSI string "SPI Disk")
  - E1: E-USB-021 (analysis: 64 MiB matches SPI Flash as MSC pattern)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Identify SPI Flash chip on PCB and verify capacity/model
- **Tags:** spi-flash, architecture, storage-backend

---

## CL-USB-012: SoC Family USB Capabilities (W55FA93/N329/N9H2)
- **Status:** supported
- **Confidence:** 0.75
- **Statement:** SoC belongs to W55FA93/N329/N9H2 family which supports USB-ISP/TurboWriter/NuWriter modes for firmware update via USB
- **Evidence:**
  - E1: E-USB-020 (analysis: W55FA93 family identification)
  - E1: E-USB-022 (vendor documentation: USB-ISP/TurboWriter support)
- **Counter-Evidence:**
  - Chip marking shows N32903U5DN (not W55FA93) - see SOC claims
- **Contradictions:** Cluster-SOC-001 (chip name discrepancy)
- **Revisions:** None
- **Next Test:** Check N32903U5DN datasheet for USB-ISP mode support (may be W55FA93 successor)
- **Tags:** soc-family, usb-isp, turbowriter, w55fa93

---

## CL-USB-013: CDC Template Available (BSP Reference)
- **Status:** verified
- **Confidence:** 0.90
- **Statement:** N9H26 BSP (related SoC family) provides CDC VirtualCom example with endpoint configuration: EP1-IN-Bulk(0x81), EP2-OUT-Bulk(0x02), EP3-IN-Intr(0x83), MPS=64(FS)/512(HS)
- **Evidence:**
  - E1: E-USB-023 (BSP analysis: VirtualCom CDC template details)
  - E0: vendor/N9H26_NonOS_BSP/ (artifact)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Compare N9H26 BSP memory map with N32903U5DN to assess template portability
- **Tags:** cdc, bsp-template, endpoint-config, reference

---

## CL-USB-014: UDC Register Names (BSP)
- **Status:** verified
- **Confidence:** 0.90
- **Statement:** USB Device Controller registers include EPA_CFG, EPB_CFG, EP*_MPS, EP*_START/END_ADDR (documented in N9H26 BSP)
- **Evidence:**
  - E1: E-USB-024 (BSP analysis: UDC register names)
  - E0: vendor/N9H26_NonOS_BSP/ (artifact)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Map BSP register offsets to UDC base 0xB8007000 and verify against binary references
- **Tags:** udc-registers, bsp-reference, endpoint-config

---

## CL-USB-015: Descriptor Patch Test Failure
- **Status:** verified
- **Confidence:** 1.0
- **Statement:** USB descriptor patch attempt at file offset 0x275140 in APP.bin caused system brick, indicating offset was critical code/data rather than descriptor table (Ghidra VA 0x00475140 translated with incorrect base offset)
- **Evidence:**
  - E1: E-USB-025 (test result: descriptor patch → brick → recovery)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Search for USB descriptor strings in APP.bin with `strings -tx APP.bin | grep -i "W55FA93\|USB MSC\|nuvoTon"` to locate correct descriptor offset
- **Tags:** descriptor-offset, test-failure, recovery

---

## CL-USB-016: MSC Functionality After Binary Extension
- **Status:** verified
- **Confidence:** 0.95
- **Statement:** APP.bin can be extended with 4KB padding + tracer without breaking boot or USB MSC functionality, indicating no strict size validation
- **Evidence:**
  - E1: E-USB-026 (test result: padding test successful, USB MSC works)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Determine maximum safe extension size before hitting memory constraints
- **Tags:** extensibility, padding-test, msc-functional

---

## CL-USB-017: UDC Initialization Candidate Functions
- **Status:** hypothesis
- **Confidence:** 0.60
- **Statement:** USB Device Controller initialization occurs in one of the following candidate functions in APP.bin: 0x30ab8, 0x46e48, 0x8b03c, 0xa3b08, 0xb4068, 0xb40fc (EP-Config writes not yet located)
- **Evidence:**
  - E1: E-USB-028 (binary analysis: UDC init candidates)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Disassemble each candidate function and search for writes to UDC_BASE+EPA_CFG (0xB8007028) and related EP registers
- **Tags:** udc-init, candidates, ep-config, hypothesis

---

## Summary

**Verified Claims:** 9 (CL-USB-001, 002, 003, 006, 007, 008, 015, 016, plus BSP refs 013, 014)
**Supported Claims:** 7 (CL-USB-004, 005, 009, 010, 011, 012)
**Hypothesis Claims:** 1 (CL-USB-017)

**Key Strengths:**
- Strong VID/PID and device identity evidence from multiple sources
- Verified MSC operation and capacity
- Dual-mode operation (MSC vs IBR-Boot) documented
- UDC base address located in binary

**Key Gaps:**
- USB descriptor file offset in APP.bin not yet found
- UDC endpoint configuration writes not located
- IBR-Boot mode protocol not reverse-engineered
- CDC capability not verified (may require descriptor analysis or multi-config check)

**Critical Contradictions:**
- Cluster-SOC-001: Device strings reference "W55FA93" but chip marking shows "N32903U5DN"
- Requires resolution to understand SoC family compatibility and feature set
