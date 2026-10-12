#!/usr/bin/env python3
"""Liest Geraete-RAM ueber das RAM-Fenster (patch_ram_fenster.py, CL-USB-REC-126).

Host-LBA = 0x10000 + Adresse/512. Gelesen wird mit dd iflag=direct, damit der
Seitencache des PCs keine alten Inhalte liefert. Vor jeder Messung wird die
Positivkontrolle gelesen: RAM 0x9F8 muss der MSC-Geraetedeskriptor sein
(CL-USB-REC-127). Schlaegt sie fehl, wird nichts ausgegeben.

  sudo python3 tools/scripts/ram_fenster_lesen.py /dev/sdX --zustand [--abstand 3]
  sudo python3 tools/scripts/ram_fenster_lesen.py /dev/sdX --adr 0x41378 --len 0x60
  sudo python3 tools/scripts/ram_fenster_lesen.py /dev/sdX --abzug ram.bin   (8 MiB)
"""
import argparse
import struct
import subprocess
import sys
import time

MARKE = 0x10000
KONTROLLE = (0x9F8, bytes.fromhex("120100020000004016049300"))

# Name, Adresse, Laenge -- Quellen in CL-USB-REC-126 / -102 / -124 und den Dekompilaten
ZUSTAND = [
    ("Tick 0xC10..0xC1F (0xC18 = u64 Tick)", 0xC10, 0x10),
    ("Uhr: Auffrisch-Zeitstempel [0x550]", 0x550, 4),
    ("Uhr: Puffer 0xCE4 (J,M,T,h,m,s)", 0xCE4, 0x18),
    ("Statuszeile 0x52C (+0 letzte Zeichnung, +0xC Spannungstakt, +0x14 Batterietakt)", 0x52C, 0x18),
    ("0x59C: Ladeanimation +4,+8,+0xC Stufe,+0x10; ui_event_wait +0x14/+0x18 Energiesparen", 0x59C, 0x20),
    ("Einstellungen 0xD00 +0x16C..+0x178 (Zeitlimits Energiesparen)", 0xE6C, 0x10),
    ("Ereignis-Struktur 0x41378 +0x40 Tastenliste, +0x44..+0x50 Warteschlange", 0x413B8, 0x14),
    ("Touch-Struktur 0x41378 +0xA4..+0xCB", 0x4141C, 0x28),
    ("usbdInfo 0x8190 +0xC8 USBModeFlag, +0xC9 devstate", 0x8258, 4),
    ("usbdInfo +0x10E u32VbusStatus", 0x829E, 4),
    ("mscdInfo 0x82EC (+0x28 dwCBW_flag, +0x48 Bulk_First)", 0x82EC, 0x50),
    ("Blockmodus 0x9F4", 0x9F4, 4),
]


def lesen(dev, adr, n):
    lba0 = MARKE + adr // 512
    lba1 = MARKE + (adr + n + 511) // 512
    roh = subprocess.run(["dd", "if=" + dev, "bs=512", "skip=%d" % lba0, "count=%d" % (lba1 - lba0),
                          "iflag=direct", "status=none"], capture_output=True, check=True).stdout
    o = adr % 512
    return roh[o:o + n]


def hexzeilen(adr, b):
    for i in range(0, len(b), 16):
        teil = b[i:i + 16]
        worte = " ".join("%08x" % struct.unpack_from("<I", teil, j)[0] for j in range(0, len(teil) - 3, 4))
        print("    %08x: %-36s %s" % (adr + i, worte, teil.hex(" ")))


def kontrolle(dev):
    adr, soll = KONTROLLE
    ist = lesen(dev, adr, len(soll))
    if ist != soll:
        sys.exit("Positivkontrolle FEHLGESCHLAGEN: RAM 0x%X = %s, erwartet %s -- Fenster nicht aktiv"
                 % (adr, ist.hex(" "), soll.hex(" ")))
    print("Positivkontrolle ok: RAM 0x%X = MSC-Geraetedeskriptor" % adr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dev")
    ap.add_argument("--adr", type=lambda s: int(s, 0))
    ap.add_argument("--len", type=lambda s: int(s, 0), default=0x40)
    ap.add_argument("--zustand", action="store_true")
    ap.add_argument("--abstand", type=float, default=0, help="zweiten Zustand nach so vielen Sekunden lesen")
    ap.add_argument("--abzug", help="ganzen RAM (8 MiB) in diese Datei schreiben")
    a = ap.parse_args()
    kontrolle(a.dev)
    if a.abzug:
        open(a.abzug, "wb").write(lesen(a.dev, 0, 0x800000))
        print("RAM-Abzug -> %s" % a.abzug)
    if a.adr is not None:
        hexzeilen(a.adr, lesen(a.dev, a.adr, a.len))
    if a.zustand:
        runden = [0] + ([a.abstand] if a.abstand else [])
        for r, warte in enumerate(runden):
            time.sleep(warte)
            print("== Zustand %d (%s)" % (r + 1, time.strftime("%H:%M:%S")))
            for name, adr, n in ZUSTAND:
                print("  " + name)
                hexzeilen(adr, lesen(a.dev, adr, n))


if __name__ == "__main__":
    main()
