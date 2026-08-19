# USB Claims (Old Docs)

Propositional claims synthesized from old_docs (E4 tier).

---

## CL-OLD-USB-001: Firmware Descriptor Strings Reference W55FA93/Nuvoton
- **Status:** verified
- **Confidence:** 0.90
- **Statement:** Firmware embeds USB descriptor strings referencing "W55FA93 USB Card Reader 1.00" and vendor "Nuvoton".
- **Evidence:**
  - E4: E-OLD-USB-001 (descriptor strings in firmware)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Compare firmware descriptor strings against live USB enumeration logs.
- **Tags:** usb, descriptor, w55fa93, nuvoton
- **Cross-Reference:** E1 CL-USB-003 (partial overlap), E1 CL-SOC-003 (partial overlap)

## CL-OLD-USB-002: USB-C Data Lines And Detect Wiring
- **Status:** supported
- **Confidence:** 0.75
- **Statement:** USB D+/D- and UD_REXT connect to the USB-C connector, with UD_CDET routed for USB detect.
- **Evidence:**
  - E4: E-OLD-USB-002 (USB-C data/PHY wiring)
  - E4: E-OLD-USB-003 (USB detect pin)
- **Counter-Evidence:** None
- **Contradictions:** None
- **Revisions:** None
- **Next Test:** Verify USB detect behavior by monitoring UD_CDET during plug/unplug.
- **Tags:** usb, hardware, usb-c, detect
- **Cross-Reference:** None (unique)
