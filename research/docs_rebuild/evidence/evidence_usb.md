# USB Evidence

Extracted evidence from chat transcripts. Format: Quote (1-2 lines) + Source + Date + Type + Tags.

---

## VID/PID & Device Identity

### E-USB-001: VID/PID Enumeration
- **Quote:** "idVendor=0416, idProduct=0093, bcdDevice=11.00"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** vid-pid, enumeration, identity

### E-USB-002: Manufacturer String
- **Quote:** "Manufacturer: nuvoTon"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** descriptor, string, manufacturer

### E-USB-003: Product String (Normal Mode)
- **Quote:** "Product: USB MSC"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** descriptor, string, product, msc

### E-USB-004: Serial Number
- **Quote:** "SerialNumber: 00000055FA93"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** descriptor, serial, identity

### E-USB-005: SCSI Device String
- **Quote:** "scsi 2:0:0:0: Direct-Access     W55FA93  SPI Disk         1.00 PQ: 0 ANSI: 0 CCS"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** scsi, device-string, w55fa93

### E-USB-006: VID/PID Ownership (Winbond/Nuvoton)
- **Quote:** "VID:PID 0416:0093 gehört zu Winbond/Nuvoton"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=12
- **Date:** 2025-09-29
- **Type:** OBSERVATION (analysis)
- **Tags:** vid-pid, vendor, identity

### E-USB-007: VID/PID Normal vs IBR-Boot
- **Quote:** "VID=0416(Nuvoton),PID=0093(MSC normal),PID=9396(IBR-Boot o.SD-Karte!)"
- **Source:** Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0
- **Date:** 2025-12-06
- **Type:** OBSERVATION (session summary)
- **Tags:** vid-pid, ibr-boot, mode-switch

### E-USB-008: IBR-Boot Product String
- **Quote:** "PID:9396,Product:\"WPMUSB\",Manuf:\"NUVOTON\",fake 1.1TB size"
- **Source:** Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0
- **Date:** 2025-12-06
- **Type:** OBSERVATION (IBR discovery)
- **Tags:** ibr-boot, wpmusb, product-string, recovery

---

## Device Class & Capacity

### E-USB-009: USB Mass Storage Class Detection
- **Quote:** "usb-storage 1-2.3:1.0: USB Mass Storage device detected"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** usb-storage, msc, class

### E-USB-010: SCSI Host Assignment
- **Quote:** "scsi host2: usb-storage 1-2.3:1.0"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** scsi, host, msc

### E-USB-011: Storage Capacity (Block Count)
- **Quote:** "sd 2:0:0:0: [sda] 131072 512-byte logical blocks: (67.1 MB/64.0 MiB)"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** capacity, blocks, 64mb

### E-USB-012: Partition Detection
- **Quote:** "sda: sda1"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** partition, sda1

### E-USB-013: Write Protection Status
- **Quote:** "sd 2:0:0:0: [sda] Write Protect is off"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** write-protect, mode

### E-USB-014: Write Cache Enabled
- **Quote:** "sd 2:0:0:0: [sda] Write cache: enabled, read cache: enabled, doesn't support DPO or FUA"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** cache, mode

---

## I/O Errors & Behavior

### E-USB-015: Read Error at Sector 2111
- **Quote:** "sd 2:0:0:0: [sda] tag#0 FAILED Result: hostbyte=DID_ERROR driverbyte=DRIVER_OK cmd_age=0s [...] I/O error, dev sda, sector 2111 op 0x0:(READ)"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg error)
- **Tags:** io-error, sector-2111, read-failure

### E-USB-016: USB Disconnect After Read Error
- **Quote:** "usb 1-2.3: USB disconnect, device number 9"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** disconnect, error-behavior

### E-USB-017: Buffer I/O Errors on Partition
- **Quote:** "Buffer I/O error on dev sda1, logical block 2048, async page read"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=2
- **Date:** 2025-09-29
- **Type:** LOG (dmesg)
- **Tags:** buffer-error, partition, sda1

### E-USB-018: Read Error Interpretation
- **Quote:** "Der READ(10)-Fehler + sofortiges USB-Reset spricht weniger für einen 'Defekt' als für FW-seitige Begrenzung/Abbruch beim Lesen bestimmter LBAs. Das passt zu Demo-/ISP-Firmwares, die nur einen Bereich exponieren und bei 'falschem' Zugriff resetten."
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=12
- **Date:** 2025-09-29
- **Type:** OBSERVATION (analysis)
- **Tags:** io-error, firmware-behavior, lba-protection

---

## Controller & Hardware

### E-USB-019: UDC Base Address
- **Quote:** "UDC-Base=0xB8007000(10 Refs in APP.bin)"
- **Source:** Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0
- **Date:** 2025-12-06
- **Type:** ARTIFACT (binary analysis)
- **Tags:** udc-base, mmio, controller

### E-USB-020: SoC Chip Identity (W55FA93 Family)
- **Quote:** "Die Geräte-Strings 'W55FA93 SPI Disk' / 'USB MSC' deuten sehr stark auf die ältere W55FA93-Familie (ARM9) hin"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=12
- **Date:** 2025-09-29
- **Type:** OBSERVATION (analysis)
- **Tags:** w55fa93, soc-family, arm9

### E-USB-021: SPI Flash as USB MSC
- **Quote:** "64,0 MiB Kapazität passt zu 'SPI-Flash als USB-Massenspeicher' — exakt so gibt es offizielle Nuvoton-Beispiele (NUC123/M451/M032 u. a.)"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=12
- **Date:** 2025-09-29
- **Type:** OBSERVATION (analysis)
- **Tags:** spi-flash, capacity, architecture

### E-USB-022: USB-ISP / TurboWriter Mode
- **Quote:** "Für diese (und die nahen N329/N9H2-Serien) ist dokumentiert, dass per USB-Schnittstelle Images in SPI/NAND/SD geschrieben werden können (TurboWriter/NuWriter / USB-ISP-Modus)"
- **Source:** Chats/833_GPT_Nuvoton_USB_MSC_Geräte_29.09.2025.json#msg=12
- **Date:** 2025-09-29
- **Type:** OBSERVATION (vendor documentation)
- **Tags:** usb-isp, turbowriter, nuwriter, update-mode

---

## CDC Template (BSP Reference)

### E-USB-023: N9H26 BSP VirtualCom CDC Template
- **Quote:** "N9H26-BSP-ANALYSE:docs/vendor/N9H26_NonOS_BSP/.VirtualCom-Beispiel=CDC-Template:EP1-IN-Bulk(0x81),EP2-OUT-Bulk(0x02),EP3-IN-Intr(0x83),MPS=64(FS)/512(HS).CDC-Desc~0x43B"
- **Source:** Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0
- **Date:** 2025-12-06
- **Type:** ARTIFACT (BSP analysis)
- **Tags:** cdc, endpoint-config, bsp-template

### E-USB-024: UDC Register Names (BSP)
- **Quote:** "UDC-Regs:EPA_CFG,EPB_CFG,EP*_MPS,EP*_START/END_ADDR"
- **Source:** Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0
- **Date:** 2025-12-06
- **Type:** ARTIFACT (BSP analysis)
- **Tags:** udc-registers, endpoint-config

---

## Test Results

### E-USB-025: Descriptor Patch Test (Failed)
- **Quote:** "TEST-B(Descriptor-Patch):Offset 0x275140 gepatcht(angenommen=USB-Desc)→BRICK!Offset war kritischer Code/Daten,nicht Descriptor.Recovery via Original-SD-Image.Ghidra-VA 0x00475140 mit falschem Base-Offset übersetzt."
- **Source:** Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0
- **Date:** 2025-12-06
- **Type:** OBSERVATION (test result)
- **Tags:** descriptor-patch, test-failure, recovery

### E-USB-026: MSC Functionality After Padding
- **Quote:** "TEST-A(Padding):APP.bin+4KB NOP+Tracer'ZKCD'@EOF→ERFOLG!Bootet,USB-MSC funktioniert."
- **Source:** Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0
- **Date:** 2025-12-06
- **Type:** OBSERVATION (test result)
- **Tags:** msc-functional, padding-test, extensibility

---

## Open Questions / Next Tests

### E-USB-027: Descriptor Offset Search Strategy
- **Quote:** "Echter File-Offset muss noch gefunden werden:strings -tx APP.bin|grep W55FA93"
- **Source:** Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0
- **Date:** 2025-12-06
- **Type:** OBSERVATION (next step)
- **Tags:** descriptor-offset, search-strategy

### E-USB-028: UDC Init Candidates
- **Quote:** "UDC-Init-Candidates:0x30ab8,0x46e48(Reset-Helper:base+0x08,+0x30,+0x38),0x8b03c,0xa3b08,0xb4068,0xb40fc.EP-Config-Writes noch nicht lokalisiert."
- **Source:** Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0
- **Date:** 2025-12-06
- **Type:** ARTIFACT (binary analysis)
- **Tags:** udc-init, candidates, ep-config

---

**Summary:**
- 28 evidence entries extracted
- Coverage: VID/PID, Device Class, Capacity, Errors, Controller Addresses, CDC Template, Test Results
- Primary sources: Chats 833 (dmesg logs), 51 (session summary with technical details)
- Key gaps: Full descriptor location, EP config writes, IBR mode details
