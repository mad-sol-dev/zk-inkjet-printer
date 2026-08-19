# USB Evidence (Old Docs)

Extracted evidence from research/old_docs/ (E4 tier). Format: Content (1-3 lines) + Source + Date + Type + Provenance + Tags.

---

### E-OLD-USB-001: Firmware USB Descriptor Strings
- **Content:** USB descriptor block in app.bin contains UTF-16LE "W55FA93 USB Card Reader 1.00" and vendor string "Nuvoton".
- **Source:** old_docs/findings/chip_identification.md#USB-Descriptor-Block
- **Date:** 2025-11-03
- **Type:** FINDING
- **Provenance:** sessions/session-2025-11-03-soc-identification.md
- **Tags:** usb, descriptor, w55fa93, nuvoton
- **Note:** [ghidra-v1]

### E-OLD-USB-002: USB-C Data Lines And PHY Reference
- **Content:** USB D+ (UD_DP) and D- (UD_DM) connect to the USB-C connector; UD_REXT pin uses a 12k resistor indicating active USB PHY.
- **Source:** old_docs/hardware/zk-dp20/circuit/N32903U5DN_GPIO_Pinout.md#Master-Pinout-List-1-128
- **Date:** 2025-11-03
- **Type:** OBSERVATION
- **Provenance:** None
- **Tags:** usb, usb-c, phy, ud_dp, ud_dm

### E-OLD-USB-003: USB Detect Pin Routed
- **Content:** UD_CDET pin (USB detect) is wired on the PCB and noted as a USB detect signal.
- **Source:** old_docs/hardware/zk-dp20/circuit/N32903U5DN_GPIO_Pinout.md#Master-Pinout-List-1-128
- **Date:** 2025-11-03
- **Type:** OBSERVATION
- **Provenance:** None
- **Tags:** usb, detect, hardware
