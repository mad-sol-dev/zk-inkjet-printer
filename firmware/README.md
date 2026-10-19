# Firmware Files

> Text written by Claude from `research/TRUTH.csv` on 2026-10-18; read and fact-checked by the maintainer. The claim IDs point into that register, which is authoritative where this page disagrees.

The firmware binaries, resource files and SD card images the analysis works on. The binaries and resource files come from the device's original 4 GB SD card; the images are dumps of that card and of a test card. `bin/` and `image/` are not edited in place.

## bin/

| File | Size | What it is |
| :--- | ---: | :--- |
| `ZK-INKJET-NANO-BOOT.bin` | 12,736 bytes | Bootloader. On the card at raw offset 0x220, behind the IBR header at 0x200 ([boot_header_structure.md](../research/phase_a_sd_analysis/boot_header_structure.md)). Linked to 0x00700000 (CL-BOOT-REC-113). |
| `ZK-INKJET-NANO-APP.bin` | 2,576,940 bytes | Main application, from raw card offset 0x03000000. Linked to 0x00058000, so VA = file offset + 0x58000 (CL-BOOT-REC-113). The maintained Ghidra database is `ZK-INKJET-NANO-APP.bin.orig` (CL-TOOL-REC-102, CL-TOOL-REC-121). |

A second, younger build of the application lies at raw card offset 0x00100000 and is not extracted here (CL-BOOT-REC-115).

## resources/

As I understood it from the maintainer, these three files were recovered from the original card with a recovery tool (TestDisk, as far as he remembers). Only one of them is what its name suggests.

| File | Size | What it is |
| :--- | ---: | :--- |
| `ZK-INKJET-UI-QVGA.bin` | 460,800 bytes | Three 320 x 240 RGB565 frames in the masked update form (XOR 0x4949 per 16-bit word, red and blue swapped), found at card offset 0x242A2000: two "Starting System..." frames without a brand and the "Thanks for using / Goodbye" screen. The device displays unmasked frames stored at raw offset 0x03800000, which mix this set with a Leon-branded start logo (CL-DISPLAY-REC-102, CL-DISPLAY-REC-120). |
| `ZK-INKJET-GUI-RES.zkml` | 3,934,892 bytes | Not the vendor's GUI resource. Recovered from the deleted directory entry of that name, i.e. clusters 2580-2640 of volume 0 read in a row after fonts had reused them: three complete Windows fonts back to back (Leelawadee UI, Nirmala UI, Segoe UI). A font viewer therefore shows "Leelawadee UI". The original content is overwritten, and APP.bin never names the file (CL-STORAGE-REC-137). |
| `ZK-INKJET-RES-HW.zkml` | 1,994,504 bytes | Handwriting model, not hardware data. APP.bin labels it "Handwriting Resources"; after a short header it holds 6763 records, one per GB2312 Chinese character. Identical to the live file on volume 0; a deleted entry `simple-handwriting-zh_CN.mod` with the same clusters and size shows its earlier name (CL-FIRMWARE-REC-130). |

## image/

The card images themselves are not in Git (`*.img` and `*.img.xz` are ignored). The compressed original is published as the release [Cloned sd-card image](https://github.com/mad-sol-dev/zk-inkjet-printer/releases/tag/SD-Card-clone). Locally, the folder holds:

| File | What it is |
| :--- | :--- |
| `sdcard.work.img`, `sdcard.work.img.xz` | Dump of the original card (4,026,531,840 bytes), the basis of all card findings. A fresh image of the same card taken on 2026-10-17 differs only where use leaves traces: settings block, header of store slot 0, MINI volume (CL-TOOL-REC-132). |
| `sdcard.minimal.img` | Rebuilt from the work image with only the regions needed to boot and all gaps zeroed. Flashed to a test card to see what the firmware writes (CL-TOOL-REC-105). |
| `sdcard.after*-minimal.img` | Dumps of that test card after boot, language change, saving a document and copying a file to MINI. The test card is a different, larger card (CL-TOOL-REC-106). |
| `sdcard.clean-raw.img` | Reproducible rebuild from the work image (CL-TOOL-REC-104). |
| `sdcard.clean_after_boot.img`, `sdcard.clean.BROKEN-truncated.img` | January 2026 artefacts; the truncated one does not match its manifest (CL-STORAGE-REC-107). |

Tracked in Git:

| File | What it is |
| :--- | :--- |
| `CHECKSUMS.txt` | SHA-256 of the images. |
| `*.layout.txt`, `*.manifest.txt` | Region lists of the rebuilt images. |
| `sdcard.work.img.xz.sha256` | Checksum of the release file. `firmware-v1.4.2.img.xz.sha256` holds the same line under an old name. |
| `APP.header.bin` | The first 4 KiB of the second application image at raw offset 0x00100000 (CL-BOOT-REC-115). |

The card was used before it went into the printer: between the ZK regions lie remnants of a 2015 Linux system, which recovery tools report as a 7.94 GB ext4 file system on a 4 GB card (CL-STORAGE-REC-138). They say nothing about the printer.

## Checksums (SHA-256)

`bin/` and `resources/`, re-checked 2026-10-18:

```
a651630c374c5441190cc35887baa814b4820c8ba2be100c9614f622cca6264d  bin/ZK-INKJET-NANO-BOOT.bin
3be9028b01c0007aab9192877341918a0bc155beef55ac17e7e8f3bcc95151ea  bin/ZK-INKJET-NANO-APP.bin
81de4c19350c574c18c07b68fb33cfb65249111aa63767d58addd3a76db64b2a  resources/ZK-INKJET-UI-QVGA.bin
4c374f83b69d0bfad1f5f4b2a419632d5fab36b20dba2e0a225e63596dad77d7  resources/ZK-INKJET-GUI-RES.zkml
327593d8ae42634ef11ac09072b070c6a179aad04f5b4e0f96f5813281ad00f3  resources/ZK-INKJET-RES-HW.zkml
```

Images: see `image/CHECKSUMS.txt`. For reference, the two most used:

```
6c19248aa79b6f990b45aa1d4f18c58c92d1317a23d0bd36c285d83cadb8b95b  sdcard.work.img
7d0b2466b71955b710b8e4ac17ca66a52f87ee03f16723d30fd1b0aee52cf747  sdcard.work.img.xz
```

Verify with `sha256sum -c` against these lines.

## Documentation

- [research/TRUTH.csv](../research/TRUTH.csv) is the only authoritative record; the rules are in [research/TRUTH.md](../research/TRUTH.md). A browsable view of the register: https://mad-sol-dev.github.io/zk-inkjet-printer/
- [research/phase_a_sd_analysis/](../research/phase_a_sd_analysis/) holds the raw artefacts of the card analysis, including [boot_header_structure.md](../research/phase_a_sd_analysis/boot_header_structure.md).
- [hardware/](../hardware/) holds the hardware documentation.
