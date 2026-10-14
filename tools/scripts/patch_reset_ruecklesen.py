#!/usr/bin/env python3
"""Ruecklese-Schleife in mscdHighSpeedInit entfernen: Test fuer den Stillstand nach dem Abziehen (CL-USB-REC-128).

Befund (2026-10-14, Statement 11): usbd_isr ruft im Bus-Reset-Zweig bei
High-Speed (OPER Bit 2) ueber usbdInfo+0x68 mscdHighSpeedInit 0xCEF90 auf.
Die Funktion schreibt EPA_MPS = 0x200 und wartet ohne Zeitlimit, bis das
Register den Wert zurueckgibt (BSP UDC/src/MSC/mscd.c Z.2236):

  0xCEFC4  ldr r0,=0xB1008000
  0xCEFC8  ldr r0,[r0,#0x78]      ; EPA_MPS
  0xCEFCC  cmp r0,#0x200
  0xCEFD0  bne 0xCEFC4            ; <- wird zu mov r0,r0

Laeuft das im Interrupt und uebernimmt das Register ohne Kabel nicht, steht
die CPU bis zum Wiederanstecken. Die Funktion schreibt EPA_MPS bei 0xCEFEC
ohnehin ein zweites Mal; ohne das Warten geht nur die Bestaetigung verloren.
Vorhersage: kein Stillstand mehr nach dem Abziehen. Bleibt er, ist der
Kandidat widerlegt.

Der Sektor wird auf dem Kartenstand --basis gebaut (Vorgabe: der Stand nach
patch_md5_kopf.py vom 2026-10-13, md5_kopf/APP.md5kopf.bin). Zusaetzlich wird
das Abbild nach diesem Patch geschrieben (APP.ruecklesen.bin); damit danach

  python3 tools/scripts/patch_md5_kopf.py --image <out>/APP.ruecklesen.bin --out <dir2>

den Kopf nachzieht. Reihenfolge an der Karte: erst <out>/patch.sh, dann
<dir2>/patch.sh; zurueck umgekehrt.

  python3 tools/scripts/patch_reset_ruecklesen.py --out <dir> [--device /dev/sdX] [--basis ABBILD]
Es wird nichts auf ein Geraet geschrieben.
"""
import argparse
import hashlib
import os
import struct
import sys

import image_pruefwert as pw
import patch_usb_dauerbetrieb as dauer

HIER = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HIER, "..", "..", "research", "phase_a_sd_analysis", "artifacts")
BASIS = os.path.join(ART, "md5_kopf", "APP.md5kopf.bin")

STELLE = 0xCEFD0
ALT, NEU = 0x1AFFFFFB, 0xE1A00000          # bne 0xCEFC4 -> mov r0,r0
# Umgebung, die die Stelle eindeutig macht: ldr r0,[pc,#..]; ldr r0,[r0,#0x78]; cmp r0,#0x200
UMGEBUNG = {0xCEFC8: 0xE5900078, 0xCEFCC: 0xE3500C02}
POOL_LADER = 0xCEFC4                       # ldr r0,[pc,#0x74] -> =0xB1008000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default=dauer.APP)
    ap.add_argument("--basis", default=BASIS, help="Kartenstand, auf dem gebaut wird")
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="/dev/sdX")
    a = ap.parse_args()

    orig = open(a.app, "rb").read()
    if hashlib.sha256(orig).hexdigest() != dauer.APP_SHA:
        sys.exit("APP.bin ist nicht die erwartete")
    b = open(a.basis, "rb").read()
    if len(b) != len(orig):
        sys.exit("Basis hat nicht die Laenge von APP.bin")
    v, md5, _ = pw.pruefwert(b)
    if v != 0 or md5 != b[pw.K:pw.K + 16]:
        sys.exit("Basis hat keinen passenden MD5-Kopf ([0x558] = 0x%08X) -- Stand unklar" % v)

    o = STELLE - dauer.VA0
    s = o // 512 * 512
    for va, w in list(UMGEBUNG.items()) + [(STELLE, ALT)]:
        ist = struct.unpack_from("<I", b, va - dauer.VA0)[0]
        if ist != w:
            sys.exit("VA 0x%X: 0x%08X statt 0x%08X" % (va, ist, w))
    w = struct.unpack_from("<I", b, POOL_LADER - dauer.VA0)[0]
    assert (w & 0xFFFFF000) == 0xE59F0000, hex(w)
    assert struct.unpack_from("<I", b, POOL_LADER + 8 + (w & 0xFFF) - dauer.VA0)[0] == 0xB1008000
    # Sprungziel des bne ist 0xCEFC4 (Offset -5 Worte)
    assert STELLE + 8 + ((ALT & 0xFFFFFF) - (1 << 24)) * 4 == POOL_LADER
    if b[s:s + 512] != orig[s:s + 512]:
        sys.exit("Sektor Datei 0x%X ist in der Basis schon veraendert" % s)

    alt = b[s:s + 512]
    neu = bytearray(alt)
    struct.pack_into("<I", neu, o - s, NEU)
    neu = bytes(neu)
    assert sum(x != y for x, y in zip(alt, neu)) <= 4
    bild = bytearray(b)
    bild[s:s + 512] = neu
    bild = bytes(bild)
    v1, _, _ = pw.pruefwert(bild)
    raw = (dauer.RAW_APP >> 9) + s // 512

    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "sektor_%06x.neu" % s), "wb").write(neu)
    open(os.path.join(a.out, "APP.ruecklesen.bin"), "wb").write(bild)
    zeilen = ["#!/bin/bash", "set -e",
              "# Erzeugt von patch_reset_ruecklesen.py (CL-USB-REC-128). NUR Testkarte.",
              "# Danach den MD5-Kopf mit dem patch.sh aus patch_md5_kopf.py --image APP.ruecklesen.bin nachziehen.",
              "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"',
              'IST=$(dd if=$DEV bs=512 skip=%d count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)' % raw,
              'case "$IST" in',
              '  %s) echo "Sektor ist schon gepatcht -- nichts zu tun"; exit 0;;' % hashlib.sha256(neu).hexdigest(),
              '  %s) ;;' % hashlib.sha256(alt).hexdigest(),
              '  *) echo "Datei-Sektor 0x%X unerwartet -- Abbruch, nichts geschrieben."; exit 1;;' % s,
              'esac',
              'read -p "Sicherung anlegen und 1 Sektor (Datei 0x%X) schreiben? [j/N] " x; [ "$x" = j ] || exit 1' % s,
              '[ -e sektor_%06x.sicherung ] || dd if=$DEV of=sektor_%06x.sicherung bs=512 skip=%d count=1 iflag=direct status=none'
              % (s, s, raw),
              '[ "$(sha256sum < sektor_%06x.sicherung | cut -d" " -f1)" = %s ] || { echo "Sicherung unerwartet -- Abbruch"; exit 1; }'
              % (s, hashlib.sha256(alt).hexdigest()),
              "dd if=sektor_%06x.neu of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none" % (s, raw),
              "sync",
              'IST=$(dd if=$DEV bs=512 skip=%d count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)' % raw,
              '[ "$IST" = %s ] || { echo "Ruecklesen weicht ab -- ./zurueck.sh"; exit 1; }' % hashlib.sha256(neu).hexdigest(),
              'echo "fertig, Sektor rueckgelesen -- jetzt den MD5-Kopf nachziehen; zurueck mit ./zurueck.sh"', ""]
    p = os.path.join(a.out, "patch.sh")
    open(p, "w").write("\n".join(zeilen)); os.chmod(p, 0o755)
    z = ["#!/bin/bash", "set -e", "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"',
         'read -p "Sicherung zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1',
         "dd if=sektor_%06x.sicherung of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none" % (s, raw),
         "sync", 'echo "zurueck"', ""]
    p = os.path.join(a.out, "zurueck.sh")
    open(p, "w").write("\n".join(z)); os.chmod(p, 0o755)
    print("VA 0x%X (Datei 0x%X): 0x%08X -> 0x%08X, Sektor Datei 0x%X = Karte %d"
          % (STELLE, o, ALT, NEU, s, raw))
    print("Basis %s: [0x558] = 0; nach dem Patch ohne neuen Kopf [0x558] = 0x%08X" % (a.basis, v1))


if __name__ == "__main__":
    main()
