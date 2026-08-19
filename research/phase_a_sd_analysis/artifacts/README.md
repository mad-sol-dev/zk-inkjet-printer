# Phase-A Artefakte

Textausgaben (`*.txt`), dekodierte Bilder (`*.png`) und Berichte werden versioniert.

**Binärdateien (`*.bin`) werden bewusst NICHT versioniert.** Jede davon ist ein
deterministischer Schnitt aus `firmware/image/sdcard.work.img` an einem
dokumentierten Offset — reproduzierbar, nicht kostbar. Zusammen wären es ~74 MB,
die das LFS-Kontingent ohne Erkenntnisgewinn belegen würden.

Reproduktion (Offsets siehe `../sd_memory_map_corrected_2026-01-14.md`):

| Datei | Offset | Größe |
|---|---|---|
| `boot_raw_0x220.bin` | 0x00000220 | 12 736 |
| `app_raw_0x03000000.bin` | 0x03000000 | 2 576 940 |
| `boot_vol2_0x24028000.bin` | 0x24028000 | 12 736 |
| `app_vol2_0x2402c000.bin` | 0x2402C000 | 2 576 940 |
| `ui_qvga_vol2_0x242a2000.bin` | 0x242A2000 | 460 800 |
| `unknown_0x00100000_stub.bin` | 0x00100000 | 3 002 368 |
| `gap_analysis/gap_b.bin` | 0x003DD000 | bis 0x03000000 |
| `gap_analysis/gap_c.bin` | 0x0327511C | bis 0x03800000 |
| `gap_analysis/gap_d.bin` | 0x03870800 | bis 0x04000000 |

```bash
dd if=firmware/image/sdcard.work.img of=<ziel> bs=1 skip=<offset> count=<groesse> \
   iflag=skip_bytes,count_bytes
```

`ui_qvga_old_vol3.bin` stammt nicht aus einem Rohschnitt, sondern aus
`tsk_recover -o 1388767 -e` auf dem FAT-Volume @ 0x2A61BE00 (siehe
`../../analysis_traceability.md`).
