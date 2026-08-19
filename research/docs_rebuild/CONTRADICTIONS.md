# Contradictions Plan (research/CONTRADICTIONS.md)

Sessions are pointers; only chat transcripts are evidence. Each cluster lists competing claims with evidence and the single best decisive test.

---

## Cluster A: SoC identity vs marking
- Claim A: SoC is Nuvoton N32903U5DN (W55FA93 family).
  - Evidence: `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0`
- Claim B: SoC is marked "DWIN M5"; firmware contains "W55FA93 USB Card Reader 1.00" string.
  - Evidence: `Chats/856_GPT_Datenblatt_Anfrage_Nuvoton_W55FA93_25.10.2025.json#msg=4`
- Decisive test: Photograph the SoC marking and cross-check against N32903 pinout + live USB descriptor capture.

## Cluster B: Runtime load address vs analysis base
- Claim A: Boot flow loads APP.bin to 0x03000000.
  - Evidence: `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0`
- Claim B: Analysis base 0x00200000 is used (FLASH); mirror at 0x00000000 causes duplicates.
  - Evidence: `Chats/61_CL_ARM_firmware_memory_mirroring_and_duplicate_function_analysis_26.12.2025.json#msg=0`
  - Evidence: `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=14`
- Decisive test: Extract and decode MMU/TTBR setup in BOOT.bin, then map virtual to physical addresses.

## Cluster C: USB descriptor region and file offset mapping
- Claim A: Offset 0x275140 was patched as the descriptor region (brick).
  - Evidence: `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0`
- Claim B: String descriptors start at VA 0x00475148; config/interface data at 0x00475140.
  - Evidence: `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=14`
  - Evidence: `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=22`
- Decisive test: Extract APP.bin bytes at computed file offsets and parse with a USB descriptor parser.

## Cluster D: Volume mapping (USB MSC vs internal storage)
- Claim A: USB MSC exposes 0:/ (MINI); update copies from 0:/ to 3:/.
  - Evidence: `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0`
- Claim B: Firmware strings reference update paths on 3:/ (could imply 3:/ is the active staging volume).
  - Evidence: `Chats/28_GPT_Teilgespräch__GhidraMCP_und_Open-WebUI_18.10.2025.json#msg=147`
- Decisive test: Mount USB MSC volume and confirm which volume index maps to the exposed filesystem; cross-check with SD image offsets.

## Cluster E: Checksum/validator in APP load path
- Claim A: APP.bin padding test succeeded; implies no CRC/size check in that load path.
  - Evidence: `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0`
- Claim B: A separate validator might exist elsewhere in the update pipeline (not evidenced yet).
  - Evidence: none (hypothesis only)
- Decisive test: Trace the update chain in Ghidra and verify whether any checksum/length validator is invoked before flash/write.
