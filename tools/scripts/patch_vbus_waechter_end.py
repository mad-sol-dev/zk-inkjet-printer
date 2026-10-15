#!/usr/bin/env python3
"""Endpatch VBUS-Waechter: nur der Waechter, ohne Diagnose-Ringe und widerlegte Patches (CL-USB-REC-128).

Befund (2026-10-15): Nach einer Anmeldung und dem Abziehen bleibt das
VBUS-Ereignis im UDC anhaengig, usbd_isr wird ununterbrochen gerufen, TMR1 und
Hauptschleife verhungern, nach 22,4 s loest der Watchdog aus. Der Waechter aus
patch_vbus_waechter.py sperrt in diesem Fall IRQ 16 im AIC und gibt ihn beim
Anstecken im TMR1-Tick wieder frei -- am Geraet 10 s und 35 s ohne Kabel ohne
Stillstand bestaetigt.

ENDSTAND = Kartenstand vom 2026-10-13 (md5_kopf/APP.md5kopf.bin: USB-Fenster,
Dauerbetrieb, RAM-Fenster, MSC-Puffer) plus
  Poolwort 0x10799C (IRQ 16): 0x109AC4 -> W1 0x2CDA00, W1 springt sonst nach usbd_isr 0x109AC4
  Poolwort 0xB43E0  (IRQ 15): 0xFBAAC  -> W2 0x2CDB00, W2 springt danach nach 0xFBAAC
  Stub-Sektor Datei 0x275A00 (W1, W2), Daten WACHT 0x2D7000 (+0 Merker, +4 Sperren, +8 Freigaben)
  MD5-Kopf Datei 0xC8F60 passend zum Endstand ([0x558] = 0)
Die Diagnose-Stub-Sektoren 0x275600 (TMR1-Ring) und 0x275800 (USB-ISR-Ring)
werden geleert, der Ruecklese-Patch (0x76E00) und der vbus_detect-Patch
(0xB1C00, 0xB2000) auf den Originalinhalt zurueckgesetzt.

patch.sh akzeptiert genau zwei Ausgangsstaende und bricht sonst ab, bevor es
schreibt: (a) Stand md5_kopf_6 (alle Diagnose-Schichten vom 2026-10-14/15),
(b) Stand md5_kopf (2026-10-13). Geprueft wird der ganze Imagebereich (sha256
ueber Datei 0..0x27522C) und jeder Stub-Sektor. Danach wird der Imagebereich
erneut gelesen und gegen den Endstand geprueft. zurueck.sh schreibt die
Sicherungen zurueck, also in den Ausgangsstand, von dem aus gepatcht wurde.

  python3 tools/scripts/patch_vbus_waechter_end.py --out <dir> [--device /dev/sdX]
Es wird nichts auf ein Geraet geschrieben.
"""
import argparse
import hashlib
import os
import struct
import sys

import image_pruefwert as pw
import patch_ringpuffer as rp
import patch_usb_dauerbetrieb as dauer
import patch_usb_isr_ring as ur
import patch_vbus_waechter as vw

HIER = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HIER, "..", "..", "research", "phase_a_sd_analysis", "artifacts")
STAND_13 = os.path.join(ART, "md5_kopf", "APP.md5kopf.bin")
STAND_6 = os.path.join(ART, "md5_kopf_6", "APP.md5kopf.bin")
L = 0x27522C
STUB_SEKTOREN = {                      # Datei-Sektor -> Inhalt im Stand md5_kopf_6
    0x275600: os.path.join(ART, "ringpuffer", "sektor_275600.neu"),
    0x275800: os.path.join(ART, "usb_isr_ring", "sektor_275800.neu"),
    0x275A00: os.path.join(ART, "vbus_waechter", "sektor_275a00.neu"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default=dauer.APP)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="/dev/sdX")
    a = ap.parse_args()

    orig = open(a.app, "rb").read()
    if hashlib.sha256(orig).hexdigest() != dauer.APP_SHA:
        sys.exit("APP.bin ist nicht die erwartete")
    s13, s6 = open(STAND_13, "rb").read(), open(STAND_6, "rb").read()
    for name, st in (("md5_kopf", s13), ("md5_kopf_6", s6)):
        v, md5, _ = pw.pruefwert(st)
        if len(st) != L or v != 0 or md5 != st[pw.K:pw.K + 16]:
            sys.exit("Stand %s hat keinen passenden MD5-Kopf" % name)
    wort = lambda b, va: struct.unpack_from("<I", b, va - dauer.VA0)[0]
    assert wort(s13, ur.POOL) == ur.HANDLER and wort(s13, rp.POOL) == rp.HANDLER
    assert wort(s6, ur.POOL) == vw.W1 and wort(s6, rp.POOL) == vw.W2

    # Stubs: Normalfall direkt in die Originalhandler
    c1, c2 = vw.w1(ziel=ur.HANDLER), vw.w2(ziel=rp.HANDLER)
    print("W1 0x%X, %d Worte:" % (vw.W1, len(c1)))
    f = vw.pruefen(c1, vw.W1)
    print("W2 0x%X, %d Worte:" % (vw.W2, len(c2)))
    f += vw.pruefen(c2, vw.W2)
    if f:
        sys.exit("Befehle stimmen nicht -- nichts erzeugt")
    b1 = b"".join(struct.pack("<I", c[0]) for c in c1)
    b2 = b"".join(struct.pack("<I", c[0]) for c in c2)
    assert vw.W1 + len(b1) <= vw.W2 and vw.W2 + len(b2) <= vw.W1 + 512
    stub = bytearray(512)
    stub[0:len(b1)] = b1
    stub[vw.W2 - vw.W1:vw.W2 - vw.W1 + len(b2)] = b2
    stub = bytes(stub)

    # Endstand: Stand vom 2026-10-13 + Poolworte + neuer Kopf
    end = bytearray(s13)
    struct.pack_into("<I", end, ur.POOL - dauer.VA0, vw.W1)
    struct.pack_into("<I", end, rp.POOL - dauer.VA0, vw.W2)
    v, md5, _ = pw.pruefwert(bytes(end))
    end[pw.K:pw.K + 16] = md5
    end = bytes(end)
    v2, md5_2, _ = pw.pruefwert(end)
    if v2 != 0 or md5_2 != md5:
        sys.exit("Pruefwert des Endstands nicht 0 -- nichts erzeugt")
    abw = sorted({i // 512 * 512 for i in range(L) if end[i] != s13[i]})
    assert abw == sorted({(rp.POOL - dauer.VA0) // 512 * 512, (ur.POOL - dauer.VA0) // 512 * 512, pw.K // 512 * 512}), abw
    print("Endstand: gegen md5_kopf geaendert %s, Kopf %s -> %s"
          % (", ".join("0x%X" % s for s in abw), s13[pw.K:pw.K + 16].hex(), md5.hex()))

    # Ziel je Sektor: Imagebereich-Sektoren, die sich zwischen einem Ausgangsstand und dem Endstand unterscheiden,
    # plus die drei Stub-Sektoren
    def sektoren(st):
        return {i // 512 * 512 for i in range(L) if st[i] != end[i]}
    bild_sek = sorted(sektoren(s13) | sektoren(s6))
    leer = b"\x00" * 512
    ziel = {s: end[s:s + 512] + b"\x00" * (512 - len(end[s:s + 512])) for s in bild_sek}
    ziel.update({0x275600: leer, 0x275800: leer, 0x275A00: stub})
    stub6 = {s: open(p, "rb").read() for s, p in STUB_SEKTOREN.items()}
    print("zu schreibende Sektoren (Datei): %s" % ", ".join("0x%X" % s for s in sorted(ziel)))

    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "APP.vbus_waechter_end.bin"), "wb").write(end)
    for s, inhalt in ziel.items():
        open(os.path.join(a.out, "sektor_%06x.neu" % s), "wb").write(inhalt)
    raw = lambda x: (dauer.RAW_APP >> 9) + x // 512
    h = lambda b: hashlib.sha256(b).hexdigest()
    n_sek = (L + 511) // 512
    bild_sha = ('dd if=$DEV bs=512 skip=%d count=%d iflag=direct status=none | head -c %d | sha256sum | cut -d" " -f1'
                % (dauer.RAW_APP >> 9, n_sek, L))
    lies = 'dd if=$DEV bs=512 skip=%d count=1 iflag=direct status=none | sha256sum | cut -d" " -f1'
    z = ["#!/bin/bash", "set -e",
         "# Erzeugt von patch_vbus_waechter_end.py (CL-USB-REC-128). Endpatch VBUS-Waechter. NUR Testkarte.",
         "# Ausgangsstand: md5_kopf_6 (Diagnose-Schichten) oder md5_kopf (2026-10-13). Endstand-Kopf %s" % md5.hex(),
         "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"',
         'echo "Ziel: $DEV -- lese Imagebereich (%d Sektoren ab %d)"' % (n_sek, dauer.RAW_APP >> 9),
         "IST=$(%s)" % bild_sha,
         'case "$IST" in',
         '  %s) STAND=end;;' % h(end),
         '  %s) STAND=6;;' % h(s6),
         '  %s) STAND=13;;' % h(s13),
         '  *) echo "Imagebereich in keinem erwarteten Stand -- Abbruch, nichts geschrieben."; exit 1;;',
         'esac']
    # Stub-Sektoren je Ausgangsstand pruefen
    for s in sorted(stub6):
        z += ['S=$(%s)' % (lies % raw(s)),
              'case "$STAND:$S" in',
              '  end:%s|6:%s|13:%s) ;;' % (h(ziel[s]), h(stub6[s]), h(leer)),
              '  *) echo "Stub-Sektor Datei 0x%X passt nicht zum Stand $STAND -- Abbruch, nichts geschrieben."; exit 1;;' % s,
              'esac']
    z += ['[ $STAND = end ] && { echo "Endstand ist schon drauf -- nichts zu tun"; exit 0; }',
          'echo "Ausgangsstand erkannt: $STAND (6 = Diagnose-Schichten md5_kopf_6, 13 = md5_kopf vom 2026-10-13)"',
          'read -p "Sicherung anlegen und %d Sektoren schreiben? [j/N] " x; [ "$x" = j ] || exit 1' % len(ziel),
          'mkdir -p sicherung_$STAND']
    for s in sorted(ziel):
        z.append('[ -e sicherung_$STAND/sektor_%06x ] || dd if=$DEV of=sicherung_$STAND/sektor_%06x bs=512 skip=%d count=1 iflag=direct status=none'
                 % (s, s, raw(s)))
    z.append('echo $STAND > letzter_stand')
    # Stub-Sektor zuerst, dann der Imagebereich (Poolworte zuletzt wirksam erst mit dem Kopf)
    for s in sorted(ziel, key=lambda x: (x < 0x275000, x)):
        z.append("dd if=sektor_%06x.neu of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none" % (s, raw(s)))
    z += ["sync", "IST=$(%s)" % bild_sha,
          '[ "$IST" = %s ] || { echo "Ruecklesen Imagebereich weicht ab -- ./zurueck.sh"; exit 1; }' % h(end)]
    for s in sorted(stub6):
        z += ['S=$(%s)' % (lies % raw(s)),
              '[ "$S" = %s ] || { echo "Ruecklesen Stub-Sektor 0x%X weicht ab -- ./zurueck.sh"; exit 1; }' % (h(ziel[s]), s)]
    z += ['echo "fertig, Imagebereich und Stub-Sektoren rueckgelesen -- erwartet Diagnose OK M0 A0; zurueck mit ./zurueck.sh"', ""]
    p = os.path.join(a.out, "patch.sh")
    open(p, "w").write("\n".join(z)); os.chmod(p, 0o755)
    zz = ["#!/bin/bash", "set -e", "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"',
          '[ -e letzter_stand ] || { echo "keine Sicherung vorhanden"; exit 1; }',
          'STAND=$(cat letzter_stand)',
          'read -p "Sicherung sicherung_$STAND zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1']
    for s in sorted(ziel, key=lambda x: (x >= 0x275000, x)):     # Imagebereich zuerst, Stubs zuletzt
        zz.append("dd if=sicherung_$STAND/sektor_%06x of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none"
                  % (s, raw(s)))
    zz += ["sync", 'echo "zurueck in Stand $STAND"', ""]
    p = os.path.join(a.out, "zurueck.sh")
    open(p, "w").write("\n".join(zz)); os.chmod(p, 0o755)


if __name__ == "__main__":
    main()
