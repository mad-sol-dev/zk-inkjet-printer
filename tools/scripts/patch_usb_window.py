#!/usr/bin/env python3
"""Verschiebt das USB-Fenster (MSC-LUN) des ZK-Inkjet auf eine andere Rohadresse der Karte.

Grundlage CL-USB-REC-119: die Basis 0x2A614000 steht genau zweimal in APP.bin,
als Literal von usb_lun_read_blocks (VA 0x074998) bei Datei 0x1CA5C und von
usb_lun_write_blocks (VA 0x074A60) bei Datei 0x1CAAC. Beide Funktionen werden
nur aus den MSC-Datenphasen gerufen und rechnen Sektor = (Basis + LBA*512) >> 9.
Die gemeldete Kapazitaet (65536 KiB) haengt nicht an der Basis (CL-USB-REC-120).

Beide Literale liegen im selben Dateisektor 0x1CA00..0x1CBFF. Auf der Karte
liegt APP.bin roh ab 0x03000000 (CL-BOOT-REC-103); BOOT.bin laedt von dort fest
0x280000 Bytes ohne Pruefsumme (CL-FIRMWARE-REC-111). Der Patch auf der Karte
ist damit genau ein Sektor, die Ruecknahme ebenso.

Der Brick aus CL-USB-REC-016 (Datei 0x275140) lag im komprimierten RW-Block
0x274BE4..0x27522C, den __scatterload_decompress beim Start entpackt. Die
Literale hier liegen im RO-Code, der unveraendert geladen wird; das Skript
verweigert jeden Patch, der in den Scatter-Bereich faellt.

Erzeugt (nichts wird auf ein Geraet geschrieben):
  <out>/APP.usbfenster_<basis>.bin   gepatchte Kopie, nur fuer das Update-Menue
  <out>/sektor_<basis>.bin           der eine gepatchte Sektor
  <out>/sektor_original.bin          derselbe Sektor unveraendert
  <out>/patch.sh, <out>/zurueck.sh   dd-Skripte mit Rueckfrage, --device setzen

  python3 tools/scripts/patch_usb_window.py --out /tmp/usbfenster --device /dev/sdX
"""
import argparse, hashlib, os, struct, sys

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "firmware", "bin", "ZK-INKJET-NANO-APP.bin")
APP_SHA = "3be9028b01c0007aab9192877341918a0bc155beef55ac17e7e8f3bcc95151ea"
OLD_BASE = 0x2A614000
LITERALS = (0x1CA5C, 0x1CAAC)
RAW_APP = 0x03000000
SCATTER_RW = (0x274B84, 0x27522C)   # Vektorkopie + komprimierter RW-Block


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default=APP)
    ap.add_argument("--base", default="0x28800000", help="neue Rohadresse des Fensters, 512-Byte-ausgerichtet")
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="/dev/sdX")
    a = ap.parse_args()
    base = int(a.base, 0)

    d = bytearray(open(a.app, "rb").read())
    sha = hashlib.sha256(d).hexdigest()
    if sha != APP_SHA:
        sys.exit("APP.bin ist nicht die erwartete (%s statt %s...)" % (sha[:16], APP_SHA[:16]))
    if base & 0x1FF:
        sys.exit("Basis 0x%X ist nicht 512-Byte-ausgerichtet; usb_lun_*_blocks lehnen dann jeden Zugriff ab" % base)
    old = struct.pack("<I", OLD_BASE)
    found = [i for i in range(len(d) - 3) if d[i:i + 4] == old]
    if found != list(LITERALS):
        sys.exit("0x%X steht an %s, erwartet %s" % (OLD_BASE, [hex(i) for i in found], [hex(i) for i in LITERALS]))
    for off in LITERALS:
        if SCATTER_RW[0] <= off < SCATTER_RW[1]:
            sys.exit("0x%X liegt im Scatter-Bereich -- dort hat ein Patch schon einmal gebrickt (CL-USB-REC-016)" % off)

    orig = bytes(d)
    for off in LITERALS:
        struct.pack_into("<I", d, off, base)
    diff = [i for i in range(len(d)) if d[i] != orig[i]]
    sectors = sorted({i // 512 for i in diff})
    assert len(diff) <= 8 and all(diff[0] // 512 == s for s in sectors) and len(sectors) == 1, (diff, sectors)
    sec = sectors[0]
    raw_sector = (RAW_APP >> 9) + sec

    os.makedirs(a.out, exist_ok=True)
    tag = "%08x" % base
    p_app = os.path.join(a.out, "APP.usbfenster_%s.bin" % tag)
    p_new = os.path.join(a.out, "sektor_%s.bin" % tag)
    p_old = os.path.join(a.out, "sektor_original.bin")
    open(p_app, "wb").write(d)
    open(p_new, "wb").write(d[sec * 512:(sec + 1) * 512])
    open(p_old, "wb").write(orig[sec * 512:(sec + 1) * 512])

    def script(name, src, what):
        p = os.path.join(a.out, name)
        open(p, "w").write("\n".join([
            "#!/bin/bash", "set -e",
            "# Erzeugt von patch_usb_window.py -- %s" % what,
            "# Ein Sektor: Datei-Sektor 0x%X von APP.bin = Rohsektor %d (Rohadresse 0x%08X)." % (sec, raw_sector, raw_sector * 512),
            "# NUR auf die Testkarte anwenden, niemals auf die Originalkarte.",
            'DEV=%s' % a.device,
            'echo "Ziel: $DEV, Rohsektor %d"' % raw_sector,
            # Vorher pruefen, dass dort wirklich der erwartete Sektor steht
            'IST=$(dd if=$DEV bs=512 skip=%d count=1 status=none | sha256sum | cut -d" " -f1)' % raw_sector,
            'echo "vorher: $IST"',
            'case "$IST" in %s|%s) ;; *) echo "Unerwarteter Inhalt -- Abbruch"; exit 1;; esac' % (
                hashlib.sha256(orig[sec * 512:(sec + 1) * 512]).hexdigest(),
                hashlib.sha256(d[sec * 512:(sec + 1) * 512]).hexdigest()),
            'read -p "Fortfahren? [j/N] " x; [ "$x" = j ] || exit 1',
            "dd if=%s of=$DEV bs=512 count=1 seek=%d conv=notrunc,fsync status=none" % (src, raw_sector),
            'echo "nachher: $(dd if=$DEV bs=512 skip=%d count=1 status=none | sha256sum | cut -d" " -f1)"' % raw_sector,
            "sync", 'echo "fertig"', ""]))
        os.chmod(p, 0o755)
        return p

    s1 = script("patch.sh", p_new, "USB-Fenster nach 0x%08X" % base)
    s2 = script("zurueck.sh", p_old, "Originalzustand (0x%08X)" % OLD_BASE)

    print("APP.bin %s..., Literale bei %s: 0x%08X -> 0x%08X" % (APP_SHA[:12], ", ".join(hex(o) for o in LITERALS), OLD_BASE, base))
    print("geaenderte Bytes: %d, alle im Dateisektor 0x%X = Rohsektor %d (0x%08X)" % (len(diff), sec, raw_sector, raw_sector * 512))
    print("Fenster: 0x%08X..0x%08X (64 MiB bei unveraenderter Kapazitaet)" % (base, base + 0x4000000))
    print("gepatchte Kopie : %s  sha256 %s" % (p_app, hashlib.sha256(d).hexdigest()))
    print("Sektor neu/alt  : %s / %s" % (p_new, p_old))
    print("Skripte         : %s / %s" % (s1, s2))


if __name__ == "__main__":
    main()
