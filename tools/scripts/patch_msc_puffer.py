#!/usr/bin/env python3
"""MSC-Datenpuffer auf 128 KiB: behebt den Heap-Ueberlauf hinter dem USB-Stillstand (CL-USB-REC-126).

Befund (RAM-Fenster, 2026-10-13): mscdInit holt den Datenpuffer mit
malloc(65567) (BSP UDC/src/MSC/mscd.c Z.2775, Variante ohne __ARRAY_BUFFER__),
mscdRd10_Command liest aber in Stuecken von MSC_BUFFER_SECTOR = 256 Sektoren
= 128 KiB in diesen Puffer (mscd.c Z.1476ff; USBD_DMA_LEN = 0x20000), der
Schreibpfad ebenso. Jede Host-Uebertragung ueber 64 KiB schreibt hinter den
Puffer in den Heap; gemessen wurde ein Nullbereich bis exakt Puffer+0x1D000
und eine zerstoerte Freiliste (einziger Knoten 0x38925C, Groesse 0). Danach
liefert jedes malloc NULL: Glyphen (FUN_00116f08) und Touch-Schaltflaechen
fallen aus, Rechteckfuellungen (Batteriesymbol) nicht.

Fix: Poolwort 0xCF518 (Datei 0x77518), geladen nur von 0xCF4C4
(ldr r0 -> blx malloc), von 0x1001F auf 0x2001F. Das ist die Groesse, die
das BSP-Array MSC_DATA_BUFFER meint, plus 31 fuer die Ausrichtung.

  python3 tools/scripts/patch_msc_puffer.py --out <dir> --device /dev/sdX
"""
import argparse
import hashlib
import os
import struct
import sys

import patch_usb_dauerbetrieb as dauer

POOL = 0xCF518
LADER = 0xCF4C4
ALT, NEU = 0x1001F, 0x2001F


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default=dauer.APP)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="/dev/sdX")
    a = ap.parse_args()
    d = open(a.app, "rb").read()
    if hashlib.sha256(d).hexdigest() != dauer.APP_SHA:
        sys.exit("APP.bin ist nicht die erwartete")
    o = POOL - dauer.VA0
    if struct.unpack_from("<I", d, o)[0] != ALT:
        sys.exit("Poolwort 0x%X ist nicht 0x%X" % (POOL, ALT))
    # der einzige Lader: ldr r0,[pc,#imm] bei 0xCF4C4 muss genau dieses Wort treffen
    w = struct.unpack_from("<I", d, LADER - dauer.VA0)[0]
    assert (w & 0xFFFFF000) == 0xE59F0000 and LADER + 8 + (w & 0xFFF) == POOL, hex(w)
    s = o // 512 * 512
    alt = d[s:s + 512]
    neu = bytearray(alt)
    struct.pack_into("<I", neu, o - s, NEU)
    neu = bytes(neu)
    assert sum(x != y for x, y in zip(alt, neu)) <= 4
    raw = (dauer.RAW_APP >> 9) + s // 512
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "sektor_%06x.neu" % s), "wb").write(neu)
    zeilen = ["#!/bin/bash", "set -e",
              "# Erzeugt von patch_msc_puffer.py (CL-USB-REC-126). NUR Testkarte.",
              "DEV=%s" % a.device, 'cd "$(dirname "$0")"',
              'IST=$(dd if=$DEV bs=512 skip=%d count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)' % raw,
              'case "$IST" in %s|%s) ;; *) echo "Datei-Sektor 0x%X unerwartet -- Abbruch"; exit 1;; esac'
              % (hashlib.sha256(alt).hexdigest(), hashlib.sha256(neu).hexdigest(), s),
              'read -p "Sicherung anlegen und 1 Sektor schreiben? [j/N] " x; [ "$x" = j ] || exit 1',
              '[ -e sektor_%06x.sicherung ] || dd if=$DEV of=sektor_%06x.sicherung bs=512 skip=%d count=1 iflag=direct status=none'
              % (s, s, raw),
              "dd if=sektor_%06x.neu of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none" % (s, raw),
              "sync", 'echo "fertig -- zurueck mit ./zurueck.sh"', ""]
    p = os.path.join(a.out, "patch.sh")
    open(p, "w").write("\n".join(zeilen)); os.chmod(p, 0o755)
    z = ["#!/bin/bash", "set -e", "DEV=%s" % a.device, 'cd "$(dirname "$0")"',
         'read -p "Sicherung zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1',
         "dd if=sektor_%06x.sicherung of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none" % (s, raw),
         "sync", 'echo "zurueck"', ""]
    p = os.path.join(a.out, "zurueck.sh")
    open(p, "w").write("\n".join(z)); os.chmod(p, 0o755)
    print("Poolwort 0x%X (Datei 0x%X): 0x%X -> 0x%X, Sektor Datei 0x%X = Karte %d" % (POOL, o, ALT, NEU, s, raw))


if __name__ == "__main__":
    main()
