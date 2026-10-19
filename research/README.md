# Research

Written by Claude (Opus 5.5); not yet reviewed by the maintainer,
@mad-sol-dev. A guide to this folder, not a summary of findings.

## What counts

[`TRUTH.csv`](TRUTH.csv) is the register and the project's only authority.
Each row is one statement about the printer or about the tools, with its
verdict, evidence, test level, the rows it depends on and, while open, the
next experiment. It is easier to read as a
[web page](https://mad-sol-dev.github.io/zk-inkjet-printer/). The rules for
it are in [`TRUTH.md`](TRUTH.md) (German). Rows are changed only through
`tools/scripts/truth.py`, never by hand.

Everything else in this folder is evidence, a source or an archive. Where a
file and the register disagree, the register is right.

## What is here

| Path | Content | State |
|---|---|---|
| `phase_a_sd_analysis/artifacts/` | Raw output of measurements and patches, one folder per topic: patch sectors with backups and apply and revert scripts, logic-analyser captures, counts. This is what register rows cite as evidence | in use |
| `phase_a_sd_analysis/write_trace/` | Which card sectors a plain boot and a language change write (August 2026) | evidence |
| `phase_a_sd_analysis/*.md` | The SD card analysis of January 2026 | frozen; the current layout is the [card map](https://mad-sol-dev.github.io/zk-inkjet-printer/card_map.html) |
| `sessions/` | Session logs. The newer ones are written when the maintainer asks for one; the [README](sessions/README.md) there gives the format | logs, not authority |
| `probes/` | Task files and reports of the probes delegated in August 2026 | finished |
| `findings/` | The two JSON knowledge bases of 2025 and early 2026 | frozen; their IDs collide (CL-TOOL-REC-103) |
| `docs_rebuild/` | The reconciliation of January 2026 that seeded the register | frozen |
| `reference/n32903_registers.json` | MMIO register map extracted from the Nuvoton BSP | reference |
| `system_understanding.md` | A summary of January 2026 | outdated |
| `report_analyse_2_8_tft_lcd_18_pin_ffc_vermuteter_controller.md` | Report on the display controller, German | its conclusion, ST7789V, is in CL-DISPLAY-REC-002 |
| `_dis.py` | A small disassembler for APP.bin, cited as evidence in the register | kept; uses the old base 0x200000 |

Many of the older files are in German. Addresses written before 11 October
2026 may be 0x1A8000 too high; correct is VA = file offset + 0x58000, and the
register marks the rows that use the old base. [METHOD.md](../METHOD.md)
explains how that happened.
