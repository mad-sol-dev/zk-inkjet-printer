#!/usr/bin/env python3
"""vbus_detect beim Abziehen anlassen: Fix-Test fuer den VBUS-Interruptsturm (CL-USB-REC-128).

Befund (2026-10-15, usb_isr_ring/ring_1.bin): Nach dem Abziehen ruft der AIC
usbd_isr ~1,5e5-mal je Sekunde; anhaengig und freigegeben ist nur VBUS (0x100),
obwohl der Abzieh-Zweig ihn quittiert. PHY_CTL steht dabei auf 0x220
(vbus_detect Bit 8 aus). Kandidat: ohne vbus_detect wirkt die Quittung nicht.

Test: beide Abzieh-Stellen schreiben PHY_CTL = 0x320 statt 0x220 (Phy_suspend
und vbus_detect an, Design Guide A1 S. 539):
  0x109C60  mov r0, #0x220  (usbd_isr, VBUS-Zweig, Abziehen)       -> #0x320
  0x10A050  mov r0, #0x220  (usbd_isr, SUSPEND-Pfad, Abziehen)     -> #0x320
Unveraendert bleiben udcOpen 0x107AC8 (0x220 beim Start), udcInit 0x107984 und
die Einsteck-Zweige 0x109BC0/0x109FD8 (0x320) sowie 0x1077E4 (Bit 8 loeschen).
Jede Stelle wird gegen das erwartete Wort und den folgenden str nach PHY_CTL
geprueft. Vorhersage: der USB-ISR-Ring zaehlt nach dem Abziehen nur noch wenige
Eintritte, der TMR1-Tick laeuft weiter, Anstecken meldet das Geraet an.

Basis ist der Kartenstand nach md5_kopf_4 (Ruecklese-, TMR1- und USB-ISR-Ring drauf).
Danach den Kopf nachziehen:
  python3 tools/scripts/patch_md5_kopf.py --image <out>/APP.vbus_detect.bin --out <dir2>
Reihenfolge an der Karte: <out>/patch.sh, dann <dir2>/patch.sh; zurueck umgekehrt.

  python3 tools/scripts/patch_vbus_detect.py --out <dir> [--device /dev/sdX] [--basis ABBILD]
Es wird nichts auf ein Geraet geschrieben.
"""
import argparse
import hashlib
import os
import struct
import sys

import capstone

import image_pruefwert as pw
import patch_usb_dauerbetrieb as dauer
import patch_usb_isr_ring as ur

HIER = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HIER, "..", "..", "research", "phase_a_sd_analysis", "artifacts")
BASIS = os.path.join(ART, "md5_kopf_4", "APP.md5kopf.bin")
ALT, NEU = 0xE3A00E22, 0xE3A00E32          # mov r0, #0x220 -> mov r0, #0x320
STELLEN = (0x109C60, 0x10A050)
PHY_CTL = 0xB1008704


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default=dauer.APP)
    ap.add_argument("--basis", default=BASIS)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="/dev/sdX")
    a = ap.parse_args()

    orig = open(a.app, "rb").read()
    if hashlib.sha256(orig).hexdigest() != dauer.APP_SHA:
        sys.exit("APP.bin ist nicht die erwartete")
    b = open(a.basis, "rb").read()
    v, md5, _ = pw.pruefwert(b)
    if len(b) != len(orig) or v != 0 or md5 != b[pw.K:pw.K + 16]:
        sys.exit("Basis hat keinen passenden MD5-Kopf -- Stand unklar")
    if struct.unpack_from("<I", b, ur.POOL - dauer.VA0)[0] != ur.STUB:
        sys.exit("Basis traegt den USB-ISR-Ring nicht -- erwartet ist der Stand md5_kopf_4")

    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
    bild = bytearray(b)
    for va in STELLEN:
        o = va - dauer.VA0
        if struct.unpack_from("<I", b, o)[0] != ALT:
            sys.exit("0x%X: 0x%08X statt 0x%08X" % (va, struct.unpack_from("<I", b, o)[0], ALT))
        # folgt: ldr r1, [pc, #..] = PHY_CTL; str r0, [r1]
        w = struct.unpack_from("<I", b, o + 4)[0]
        assert (w & 0xFFFFF000) == 0xE59F1000, hex(w)
        assert struct.unpack_from("<I", b, va + 4 + 8 + (w & 0xFFF) - dauer.VA0)[0] == PHY_CTL
        assert struct.unpack_from("<I", b, o + 8)[0] == 0xE5810000          # str r0, [r1]
        if b[o // 512 * 512:o // 512 * 512 + 512] != orig[o // 512 * 512:o // 512 * 512 + 512]:
            sys.exit("Sektor Datei 0x%X ist in der Basis schon veraendert" % (o // 512 * 512))
        struct.pack_into("<I", bild, o, NEU)
        ins = list(md.disasm(struct.pack("<I", NEU), va))[0]
        print("  0x%X: 0x%08X -> 0x%08X  %s %s" % (va, ALT, NEU, ins.mnemonic, ins.op_str))
        assert (ins.mnemonic, ins.op_str) == ("mov", "r0, #0x320")
    bild = bytes(bild)
    sek = sorted({(va - dauer.VA0) // 512 * 512 for va in STELLEN})
    assert sum(x != y for x, y in zip(b, bild)) <= 2 * len(STELLEN)

    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "APP.vbus_detect.bin"), "wb").write(bild)
    raw = lambda x: (dauer.RAW_APP >> 9) + x // 512
    lies = 'IST=$(dd if=$DEV bs=512 skip=%d count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)'
    z = ["#!/bin/bash", "set -e",
         "# Erzeugt von patch_vbus_detect.py (CL-USB-REC-128). NUR Testkarte.",
         "# Danach den MD5-Kopf mit dem patch.sh aus patch_md5_kopf.py --image APP.vbus_detect.bin nachziehen.",
         "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"', "FERTIG=0"]
    for s in sek:
        open(os.path.join(a.out, "sektor_%06x.neu" % s), "wb").write(bild[s:s + 512])
        z += [lies % raw(s), 'case "$IST" in',
              '  %s) FERTIG=$((FERTIG+1));;' % hashlib.sha256(bild[s:s + 512]).hexdigest(),
              '  %s) ;;' % hashlib.sha256(b[s:s + 512]).hexdigest(),
              '  *) echo "Datei-Sektor 0x%X unerwartet -- Abbruch, nichts geschrieben."; exit 1;;' % s, 'esac']
    z += ['[ $FERTIG = %d ] && { echo "vbus_detect-Patch ist schon drauf -- nichts zu tun"; exit 0; }' % len(sek),
          'read -p "Sicherung anlegen und %d Sektoren (%s) schreiben? [j/N] " x; [ "$x" = j ] || exit 1'
          % (len(sek), ", ".join("Datei 0x%X" % s for s in sek))]
    for s in sek:
        z.append('[ -e sektor_%06x.sicherung ] || dd if=$DEV of=sektor_%06x.sicherung bs=512 skip=%d count=1 iflag=direct status=none'
                 % (s, s, raw(s)))
    for s in sek:
        z.append("dd if=sektor_%06x.neu of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none" % (s, raw(s)))
    z.append("sync")
    for s in sek:
        z += [lies % raw(s), '[ "$IST" = %s ] || { echo "Ruecklesen Datei-Sektor 0x%X weicht ab -- ./zurueck.sh"; exit 1; }'
              % (hashlib.sha256(bild[s:s + 512]).hexdigest(), s)]
    z += ['echo "fertig, Sektoren rueckgelesen -- jetzt den MD5-Kopf nachziehen; zurueck mit ./zurueck.sh"', ""]
    p = os.path.join(a.out, "patch.sh")
    open(p, "w").write("\n".join(z)); os.chmod(p, 0o755)
    zz = ["#!/bin/bash", "set -e", "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"',
          'read -p "Sicherungen zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1']
    for s in sek:
        zz.append("dd if=sektor_%06x.sicherung of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none"
                  % (s, raw(s)))
    zz += ["sync", 'echo "zurueck"', ""]
    p = os.path.join(a.out, "zurueck.sh")
    open(p, "w").write("\n".join(zz)); os.chmod(p, 0o755)
    print("Sektoren (Datei): %s = Karte %s; ohne neuen Kopf waere [0x558] = 0x%08X"
          % (", ".join("0x%X" % s for s in sek), ", ".join(str(raw(s)) for s in sek), pw.pruefwert(bild)[0]))


if __name__ == "__main__":
    main()
