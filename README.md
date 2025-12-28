# ZK-Inkjet Printer Reverse Engineering

**Status:** 🚧 Active Analysis | **Chip:** Nuvoton N32903U5DN | **Firmware:** Non-OS / Bare Metal

This repository documents the reverse engineering of the "ZK-1696" class handheld inkjet printers (often sold as **Luqeeg**, **Chiky Tech**, or generic **DP20**). These devices use HP45 thermal inkjet cartridges to print text, QR codes, and bitmaps on packaging.

Our goal is to understand the hardware and firmware well enough to enable **custom automation via USB** (e.g., printing serialized data sent from a PC without manual entry).

---

## 🧩 Project Status

| Component | Status | Notes |
| :--- | :---: | :--- |
| **SoC Identity** | ✅ Verified | **Nuvoton N32903U5DN** (ARM926EJ-S @ 200MHz, 8MB Stacked DDR). |
| **Boot Chain** | ✅ Verified | Proprietary IBR → `BOOT.bin` (RAW Sec 1) → `APP.bin` (RAW Sec 2048). |
| **Update System** | ✅ Verified | **Unsafe.** No CRC/Signature checks. Flashes raw data from SD card. |
| **Pinout** | ✅ Verified | GPIOs mapped. UART console is **blocked** by printhead usage. |
| **UI Decoding** | 🚧 In Progress | 480x480 framebuffer partially decoded (BGR565 scrambled). |
| **USB CDC** | 🔄 Planning | Goal: Replace Mass Storage Class with Virtual Serial Port. |

## 🚴 The "Nerd Cascade"

How we got here:
1.  **Goal:** Label lithium cells for an E-recumbent bike battery.
2.  **Tool:** Bought a cheap handheld inkjet printer.
3.  **Problem:** Manual data entry is tedious.
4.  **Solution:** Reverse engineer the firmware to inject data via USB.
5.  **Reality:** 'Wrote' a custom [Ghidra MCP Bridge](tools/mcp_bridge) and forced AI agents to read data sheets.
6.  *...the bike is still waiting.*

## 📂 Repository Layout

*   [**hardware/**](hardware/) - PCB analysis, Pinouts, and SoC datasheets.
*   [**firmware/**](firmware/) - Memory maps, Update protocols, and Binary analysis.
*   [**tools/**](tools/) - Custom Python scripts and MCP (Model Context Protocol) agents.
*   [**research/**](research/) - Raw session logs, findings database, and hypothesis tracking.

## ⚡ Quick Start

**Prerequisites:**
*   Python 3.10+
*   Ghidra 11.x (for binary analysis)

**Setup:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

**Key Commands:**
```bash
# Run unit tests on parsers
make test

# Generate current verification status tables
python tools/generate_verification_summary.py
```

## ⚠️ Safety Warning

**There are NO SAFETY GUARDS.**
The firmware update mechanism performs **zero** checksum or cryptographic verification. If you flash a corrupted `APP.bin`, the device will brick. Always keep a backup of your SD card image (specifically sectors 0-4096).

## License

*   **Code:** MIT
*   **Documentation/Images:** CC BY 4.0
