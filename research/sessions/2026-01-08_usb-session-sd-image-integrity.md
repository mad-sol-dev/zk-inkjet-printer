# Session Log: USB Analysis + SD Image Integrity

**Date:** 2026-01-08  
**Project:** ZK inkjet printer RE  
**Scope:** USB init/IRQ mapping (APP.bin) + SD image carving + checksum hygiene

## Goals
- Confirm USBD init path and IRQ registration in APP.bin.
- Trace unknown RAM pointers used during USBD init.
- Validate SD image locations for BOOT/APP binaries.
- Normalize APP.bin checksum in `firmware/bin/`.

## Key Discoveries
- `usbd_init_phy_cep` (0x002af9c0) writes USBD PHY/CEP registers and toggles USBD clocks.
- `usbd_irq_setup` (0x002af80c) registers IRQ ID 0x10 and handler pointer `0x00109ac4` via `irq_register_handler` (0x002a1e88).
- RAM pointers `0x00008190` and `0x000082B0` are used as state/flag bases during USBD init; they are not USBD register offsets.
- Raw SD image contains APP at `0x03000000` and BOOT code at `0x00000220`; volume 2 stores deleted copies at `0x24028000` (BOOT) and `0x2402C000` (APP).
- The APP image in `firmware/bin/` was not identical to the raw SD APP and was replaced with the clean `.orig` copy.

## Technical Notes

### USBD init/IRQ
- **Function renamed:** `usbd_init_phy_cep` @ `0x002af9c0`
  - Writes `USBD_BA+0x704` (USB_PHY_CTL) = `0x220`
  - Writes `USBD_BA+0x58` (CEP_END_ADDR) = `0x7f` with readback loop
  - Sets `REG_AHBCLK` (`0xB0000204`) bits `0x50000` (USBD + HCLK3)
  - Uses RAM pointers: `0x00008190` (bytes `+0x10e..+0x111`) and `0x000082B0` (`+0x4`) based on PHY_CTL bit31
- **Function renamed:** `usbd_irq_setup` @ `0x002af80c`
  - Calls `irq_register_handler` with `(type=1, irq_id=0x10, handler_ptr=0x00109ac4)`
  - IRQ handler table base `0x00000890` used by dispatcher (`0x002a1a00`)
- **Function renamed:** `irq_register_handler` @ `0x002a1e88`

### BSP Register Map Check
- `vendor/N32901-3_NonOS_BSP/SYSLIB/Lib/W55FA93_reg.h` defines USBD offsets up to `+0x178` then `+0x700/+0x704`.
- No USBD register offsets at `+0x190` or `+0x2B0` → confirms RAM usage for `0x00008190/0x000082B0`.

### SD Image Carving
Raw SD image: `$HOME/workspace/zk-inkjet-printer/firmware/image/sdcard.work.img`

Carved artifacts (stored in `research/phase_a_sd_analysis/artifacts/`):
- `boot_raw_0x220.bin` (BOOT code, 12,736 bytes)
- `boot_vol2_0x24028000.bin` (deleted BOOT copy from volume 2)
- `app_raw_0x03000000.bin` (APP from raw SD)
- `app_vol2_0x2402c000.bin` (deleted APP copy from volume 2)
- `unknown_0x00100000_0x20000.bin` (vector table + strings; likely UI/logging stub)

Hashes:
- BOOT code (raw + vol2 + extracted): `a651630c374c5441190cc35887baa814b4820c8ba2be100c9614f622cca6264d`
- APP raw SD / volume 2 / `.orig`: `3be9028b01c0007aab9192877341918a0bc155beef55ac17e7e8f3bcc95151ea`
- `firmware/bin/ZK-INKJET-NANO-APP.bin` was replaced to match the `.orig` hash above.

### Documentation Updates
- Updated `firmware/README.md` to reflect correct APP hash.
- Clarified BOOT.bin description (code-only; IBR header lives in raw SD @ `0x200`).

## RE-KB References
- `finding-0003`: USB IRQ setup in APP.bin (handler pointer at `0x00109ac4`, table base `0x00000890`).
- `finding-0004`: BSP USBD register map has no offsets `+0x190/+0x2B0`.
- `finding-0005`: USBD init routine at `0x002af9c0` (PHY/CEP + RAM flags).

## Next Steps / Open Questions
- Map SDRAM in Ghidra to resolve RAM pointers (`0x00008190`, `0x000082B0`) and handler table.
- Load any missing firmware segments to resolve ISR `0x00109ac4`.
- Extend carve around `0x00100000` to identify full binary boundaries and classify that stub.

