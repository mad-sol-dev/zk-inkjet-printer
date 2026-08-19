# Master Timeline (research/MASTER_TIMELINE.md)

Two lanes:
- Lane A: Technical progress (claims created/updated/verified/refuted).
- Lane B: Tooling/methodology (only when it enables evidence capture).

Each event references sessions as pointers and the chat evidence.

| Date | Lane | Event | Session Pointer(s) | Evidence (chat) |
|---|---|---|---|---|
| 2025-10-18 | A | Firmware string list shows update paths under 3:/ (update candidate files). | `sessions/2025-10-10_session-notes.md` | `Chats/28_GPT_Teilgespräch__GhidraMCP_und_Open-WebUI_18.10.2025.json#msg=147` |
| 2025-10-25 | A | SoC marking reported as DWIN M5; firmware contains W55FA93 USB Card Reader string. | `sessions/2025-11-03_soc-identification.md` | `Chats/856_GPT_Datenblatt_Anfrage_Nuvoton_W55FA93_25.10.2025.json#msg=4` |
| 2025-12-02 | A | USB/SD/update summary: VID/PID pairs, SD volume layout, boot flow, update mechanism. | `sessions/2025-12-02_usb-cdc-patch.md` | `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0` |
| 2025-12-02 | B | Patch tests used to validate update checks (padding test success, descriptor patch brick). | `sessions/2025-12-02_usb-cdc-patch.md` | `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=0` |
| 2025-12-06 | A | USB descriptor region clarified: string descriptors at 0x00475148; SCSI product string at 0x00475180; config/interface data around 0x00475140. | `sessions/2025-12-02_usb-cdc-patch.md` | `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=14`; `Chats/51_CL_ZK-Inkjet-Drucker_USB-CDC_Reverse-Engineering_06.12.2025.json#msg=22` |
| 2025-12-20 | A | Touch panel mapping noted to use ADC_TP_* dedicated pins. | `sessions/2025-12-21_adc-encoder-analysis.md` | `Chats/58_CL_ZK-Inkjet_Projekt_Platine_analysieren_20.12.2025.json#msg=18` |
| 2025-12-26 | A | Memory mirror (LOW_MIRROR vs FLASH) identified as source of duplicate functions. | `sessions/2025-12-27_arm-thumb-analysis-mmio-extraction.md` | `Chats/61_CL_ARM_firmware_memory_mirroring_and_duplicate_function_analysis_26.12.2025.json#msg=0` |
| 2025-12-26 | B | Ghidra methodology adjustment: remove or disable LOW_MIRROR block to reduce false functions. | `sessions/2025-12-27_arm-thumb-analysis-mmio-extraction.md` | `Chats/61_CL_ARM_firmware_memory_mirroring_and_duplicate_function_analysis_26.12.2025.json#msg=0` |
