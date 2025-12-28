# Firmware Update Mechanism

The update mechanism of this printer is notable for its complete lack of security or integrity verification.

## The Dual-Storage Architecture
The system uses a single SD card split into logical zones:

1.  **Reserved RAW Area (Sectors 0-2047):**
    *   Sector 1 (`0x200`): `NANO-BOOT.bin` (Stage 2 Loader)
    *   Sector 2048 (`0x100000`): `NANO-APP.bin` (Main Firmware)
    *   *Note:* The IBR (Internal Boot ROM) loads directly from these raw sectors.

2.  **FAT Partitions (Runtime):**
    *   Volume `0:/`: System/Staging (Hidden)
    *   Volume `3:/`: User/Update (Visible as "MINI" over USB)

## Update Workflow

1.  **Trigger:** User drops `ZK-INKJET-NANO-APP.bin` onto the USB drive (Volume `3:/`).
2.  **Detection:** Bootloader checks for specific filenames.
3.  **Staging:** File is copied from `3:/` (User) to `0:/` (System).
4.  **Flashing:** A RAW sector writer (`FUN_00094584`) writes the data from `0:/` directly to SD Sector 2048.
5.  **Cleanup:** The file on `3:/` is deleted.

## ⛔ Security Analysis

**There are NO CHECKSUMS.**

The update function (`FUN_0006ccf8`) performs **only** a file size check (`bytes_read == file_size`).
*   No CRC32.
*   No SHA-256.
*   No Magic Number validation (after the file extension check).

**Risk:** If a file transfer is interrupted or corrupted, the bootloader will flash garbage to the RAW sectors. Since the IBR loads blindly from Sector 1/2048, the device will fail to boot (Brick). Recovery requires an external SD card reader to restore the RAW sectors.
