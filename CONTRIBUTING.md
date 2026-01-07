# Contributing to ZK-Inkjet RE

We welcome hackers, makers, and signal analysts!

## How to Help

### 1. The "Safety First" Rule
Do **not** submit PRs that contain raw vendor SDKs or copyrighted binaries.
*   ✅ Commit: Analysis scripts, Markdown notes, JSON findings.
*   ❌ Commit: `APP.bin`, Nuvoton tools.

### 2. Updating Findings
We use a structured Knowledge Base (`.re_kb`). If you verify a pinout or reverse a function:
1.  Don't just update the text files.
2.  Update the corresponding JSON in `.re_kb/findings/`.
3.  Run `python tools/generate_verification_summary.py` to sync the tables.

### 3. Beginners
Check `docs/guide/operations.md`. A good first task is decoding the remaining artifacts in the UI blob (`ZK-INKJET-UI-QVGA.bin`) or mapping the menu state machine.

### 4. Advanced
We are looking for a way to enable **USB CDC** (Virtual Serial).
*   Target: `0xB1008000` (USB Device Controller - USBD_BA, BSP-verified).
*   Goal: Inject a CDC descriptor and a handler hook to accept ASCII commands.
```
