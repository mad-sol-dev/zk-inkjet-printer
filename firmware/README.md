# Firmware Files

Binary files and images for ZK-Inkjet printer reverse engineering.

## Directory Structure

### bin/
Firmware binary files:
- `ZK-INKJET-NANO-BOOT.bin` - Bootloader (12,736 bytes code + 32-byte IBR header)
- `ZK-INKJET-NANO-APP.bin` - Main application firmware (~2.6 MB)

### image/
SD card images:
- `sdcard.work.img.xz` - Compressed working SD card image (Git LFS tracked)
- `sdcard.work.img` - Uncompressed SD card image (Git ignored)
- `CHECKSUMS.txt` - SHA256 verification hashes for images

### Root Files
- `ZK-INKJET-UI-QVGA.bin` - UI blob
- `ZK-INKJET-GUI-RES.zkml` - Font resource (Leelawadee UI)
- `ZK-INKJET-RES-HW.zkml` - Hardware resource file

---

## File Verification (SHA256)

### Firmware Binaries (bin/)
```
a651630c374c5441190cc35887baa814b4820c8ba2be100c9614f622cca6264d  ZK-INKJET-NANO-BOOT.bin
cd9667d409abef2d029066fb1b05d9f7d12cdeaef7248541b74d372941612004  ZK-INKJET-NANO-APP.bin
```

### Root Files
```
81de4c19350c574c18c07b68fb33cfb65249111aa63767d58addd3a76db64b2a  ZK-INKJET-UI-QVGA.bin
4c374f83b69d0bfad1f5f4b2a419632d5fab36b20dba2e0a225e63596dad77d7  ZK-INKJET-GUI-RES.zkml
327593d8ae42634ef11ac09072b070c6a179aad04f5b4e0f96f5813281ad00f3  ZK-INKJET-RES-HW.zkml
```

### SD Card Images (image/)
```
6c19248aa79b6f990b45aa1d4f18c58c92d1317a23d0bd36c285d83cadb8b95b  sdcard.work.img
ff64f1bd8f80632162afc8106ad2ec1995215b8f331bfd8abd0475d507ee0510  sdcard.work.img.xz
```

**Verify:** `sha256sum -c` against these hashes or check `image/CHECKSUMS.txt`

---

## Documentation

**Technical documentation is in research/:**
- [research/system_understanding.md](../research/system_understanding.md) - Complete system reference
- [research/phase_a_sd_analysis/](../research/phase_a_sd_analysis/) - SD structure analysis
- [research/phase_a_sd_analysis/boot_header_structure.md](../research/phase_a_sd_analysis/boot_header_structure.md) - IBR header format

**Related documentation:**
- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture
- [hardware/](../hardware/) - Hardware documentation
