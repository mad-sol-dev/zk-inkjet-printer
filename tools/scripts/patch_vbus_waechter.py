#!/usr/bin/env python3
"""VBUS-Waechter: USB-Interrupt nach dem Abziehen im AIC sperren, beim Anstecken wieder freigeben (CL-USB-REC-128).

Befund (2026-10-15): Nach dem Abziehen bleibt das VBUS-Ereignis (USB_IRQ_STAT
0x100) trotz Quittung gesetzt -- mit vbus_detect aus (ring_1) und an (ring_2).
usbd_isr wird ~1,5e5-mal je Sekunde gerufen, TMR1 und Hauptschleife verhungern.

Weg: den Sturm nicht im UDC loeschen, sondern im AIC abstellen.
  W1 vor usbd_isr (IRQ 16, Poolwort 0x10799C, heute -> USB-ISR-Ring 0x2CD800):
     sperren, wenn PHY_CTL Bit 31 = 0 (Kabel weg) UND u32VbusStatus (Byte
     0x829E = usbdInfo+0x10E) = 0 (usbd_isr hat das Abziehen schon verarbeitet)
     UND USB_IRQ_STAT & USB_IRQ_ENB & 0x100 (VBUS haengt an):
       MDCR 0xB8000124 = 1 << 16, Merker = 1, Sperrzaehler +1, bx lr
     sonst b 0x2CD800 (Ring, dann usbd_isr) -- der erste Abzieh-Eintritt laeuft also normal.
  W2 vor dem TMR1-Handler (IRQ 15, Poolwort 0xB43E0, heute -> TMR1-Ring 0x2CD600):
     wenn Merker = 1 und PHY_CTL Bit 31 = 1 (Kabel wieder da):
       Merker = 0, Freigabezaehler +1, MECR 0xB8000120 = 1 << 16
     dann b 0x2CD600 (Ring, dann 0xFBAAC). Nach der Freigabe laeuft usbd_isr mit
     dem noch anhaengigen VBUS-Ereignis seinen Einsteck-Zweig (PHY_CTL 0x320, Quittung).
AIC-Register laut Firmware: MECR-Schreiber 0xF99EC/0xFA040, MDCR 0xFA04C.
Daten: WACHT 0x2D7000 (+0 Merker, +4 Sperren, +8 Freigaben), Laufzeit-RAM, beim Start 0.

Stubs W1 0x2CDA00 / W2 0x2CDB00 in einem Sektor (Datei 0x275A00). Die
Poolworte zeigen nachher auf W1/W2; die Ringe bleiben dahinter in der Kette.
Basis ist der Kartenstand nach md5_kopf_5. Danach den Kopf nachziehen:
  python3 tools/scripts/patch_md5_kopf.py --image <out>/APP.vbus_waechter.bin --out <dir2>
Reihenfolge an der Karte: <out>/patch.sh, dann <dir2>/patch.sh; zurueck umgekehrt.

  python3 tools/scripts/patch_vbus_waechter.py --out <dir> [--device /dev/sdX] [--basis ABBILD]
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
from patch_ringpuffer import Asm, ldr, str_, dp, regs

HIER = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HIER, "..", "..", "research", "phase_a_sd_analysis", "artifacts")
BASIS = os.path.join(ART, "md5_kopf_5", "APP.md5kopf.bin")

W1, W2 = 0x2CDA00, 0x2CDB00             # Datei 0x275A00
WACHT = 0x2D7000
VBUS_STATUS = 0x829E                    # usbdInfo 0x8190 + 0x10E (Byte)
USBD_BA, PHY_CTL = 0xB1008000, 0xB1008704
AIC_MECR, AIC_MDCR = 0xB8000120, 0xB8000124
IRQ_USB = 1 << 16


def w1(ziel=None):
    """ziel: wohin der Normalfall springt (Vorgabe: USB-ISR-Ring 0x2CD800)."""
    ziel = ur.STUB if ziel is None else ziel
    a = Asm(W1)
    a.w(0xE92D0000 | regs(0, 1, 2, 14), "push {r0, r1, r2, lr}")
    a.ldr_lit(0, PHY_CTL, "ldr r0, [pc, #")
    a.w(ldr(0, 0, 0), "ldr r0, [r0]")
    a.w(dp("tst", 0, 0, 0x80000000), "tst r0, #0x80000000")
    a.b("ne", "normal", "bne")
    a.ldr_lit(0, VBUS_STATUS, "ldr r0, [pc, #")
    a.w(0xE5D00000, "ldrb r0, [r0]")
    a.w(dp("cmp", 0, 0, 0), "cmp r0, #0")
    a.b("ne", "normal", "bne")
    a.ldr_lit(0, USBD_BA, "ldr r0, [pc, #")
    a.w(ldr(1, 0, 0x10), "ldr r1, [r0, #0x10]")
    a.w(ldr(2, 0, 0x14), "ldr r2, [r0, #0x14]")
    a.w(0xE0011002, "and r1, r1, r2")
    a.w(dp("tst", 0, 1, 0x100), "tst r1, #0x100")
    a.b("eq", "normal", "beq")
    a.ldr_lit(0, AIC_MDCR, "ldr r0, [pc, #")
    a.w(dp("mov", 1, 0, IRQ_USB), "mov r1, #0x10000")
    a.w(str_(1, 0, 0), "str r1, [r0]")
    a.ldr_lit(0, WACHT, "ldr r0, [pc, #")
    a.w(dp("mov", 1, 0, 1), "mov r1, #1")
    a.w(str_(1, 0, 0), "str r1, [r0]")
    a.w(ldr(1, 0, 4), "ldr r1, [r0, #4]")
    a.w(dp("add", 1, 1, 1), "add r1, r1, #1")
    a.w(str_(1, 0, 4), "str r1, [r0, #4]")
    a.w(0xE8BD0000 | regs(0, 1, 2, 14), "pop {r0, r1, r2, lr}")
    a.w(0xE12FFF1E, "bx lr")
    a.lab("normal")
    a.w(0xE8BD0000 | regs(0, 1, 2, 14), "pop {r0, r1, r2, lr}")
    a.b("", ziel, "b #0x%x" % ziel)
    return a.fertig()


def w2(ziel=None):
    """ziel: wohin W2 am Ende springt (Vorgabe: TMR1-Ring 0x2CD600)."""
    ziel = rp.STUB if ziel is None else ziel
    a = Asm(W2)
    a.w(0xE92D0000 | regs(0, 1, 14), "push {r0, r1, lr}")
    a.ldr_lit(0, WACHT, "ldr r0, [pc, #")
    a.w(ldr(1, 0, 0), "ldr r1, [r0]")
    a.w(dp("cmp", 0, 1, 0), "cmp r1, #0")
    a.b("eq", "weiter", "beq")
    a.ldr_lit(1, PHY_CTL, "ldr r1, [pc, #")
    a.w(ldr(1, 1, 0), "ldr r1, [r1]")
    a.w(dp("tst", 0, 1, 0x80000000), "tst r1, #0x80000000")
    a.b("eq", "weiter", "beq")
    a.w(dp("mov", 1, 0, 0), "mov r1, #0")
    a.w(str_(1, 0, 0), "str r1, [r0]")
    a.w(ldr(1, 0, 8), "ldr r1, [r0, #8]")
    a.w(dp("add", 1, 1, 1), "add r1, r1, #1")
    a.w(str_(1, 0, 8), "str r1, [r0, #8]")
    a.ldr_lit(0, AIC_MECR, "ldr r0, [pc, #")
    a.w(dp("mov", 1, 0, IRQ_USB), "mov r1, #0x10000")
    a.w(str_(1, 0, 0), "str r1, [r0]")
    a.lab("weiter")
    a.w(0xE8BD0000 | regs(0, 1, 14), "pop {r0, r1, lr}")
    a.b("", ziel, "b #0x%x" % ziel)
    return a.fertig()


def pruefen(code, basis):
    alt = rp.STUB
    rp.STUB = basis                  # rp.pruefen rechnet Adressen relativ zu rp.STUB
    try:
        return rp.pruefen(code)
    finally:
        rp.STUB = alt


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
    wort = lambda va: struct.unpack_from("<I", b, va - dauer.VA0)[0]
    # Erwarteter Stand: beide Poolworte zeigen auf die Ringe, vbus_detect-Patch drauf
    if wort(ur.POOL) != ur.STUB or wort(rp.POOL) != rp.STUB:
        sys.exit("Poolworte zeigen nicht auf die Ringe (0x%X, 0x%X) -- erwartet ist der Stand md5_kopf_5"
                 % (wort(ur.POOL), wort(rp.POOL)))
    if wort(0x109C60) != 0xE3A00E32:
        sys.exit("vbus_detect-Patch fehlt in der Basis -- erwartet ist der Stand md5_kopf_5")

    c1, c2 = w1(), w2()
    print("W1 0x%X, %d Worte:" % (W1, len(c1)))
    f = pruefen(c1, W1)
    print("W2 0x%X, %d Worte:" % (W2, len(c2)))
    f += pruefen(c2, W2)
    if f:
        sys.exit("Befehle stimmen nicht -- nichts erzeugt")
    b1 = b"".join(struct.pack("<I", c[0]) for c in c1)
    b2 = b"".join(struct.pack("<I", c[0]) for c in c2)
    assert W1 + len(b1) <= W2 and W2 + len(b2) <= W1 + 512
    so = W1 - dauer.VA0
    assert so % 512 == 0 and so >= len(orig) and so + 512 <= dauer.APP_MAX
    assert ur.STUB + 512 <= W1 and ur.PUF_B + 256 * ur.EINTRAG <= WACHT and WACHT + 12 <= 0x2D8000

    stub_sek = bytearray(512)
    stub_sek[0:len(b1)] = b1
    stub_sek[W2 - W1:W2 - W1 + len(b2)] = b2
    stub_sek = bytes(stub_sek)
    bild = bytearray(b)
    struct.pack_into("<I", bild, ur.POOL - dauer.VA0, W1)
    struct.pack_into("<I", bild, rp.POOL - dauer.VA0, W2)
    bild = bytes(bild)
    sekt = [((va - dauer.VA0) // 512 * 512) for va in (rp.POOL, ur.POOL)]
    assert sum(x != y for x, y in zip(b, bild)) <= 8

    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "APP.vbus_waechter.bin"), "wb").write(bild)
    open(os.path.join(a.out, "sektor_%06x.neu" % so), "wb").write(stub_sek)
    for s in sekt:
        open(os.path.join(a.out, "sektor_%06x.neu" % s), "wb").write(bild[s:s + 512])
    leer = hashlib.sha256(b"\x00" * 512).hexdigest()
    alle = [(s, hashlib.sha256(b[s:s + 512]).hexdigest(), bild[s:s + 512]) for s in sekt] + [(so, leer, stub_sek)]
    raw = lambda x: (dauer.RAW_APP >> 9) + x // 512
    lies = 'IST=$(dd if=$DEV bs=512 skip=%d count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)'
    z = ["#!/bin/bash", "set -e",
         "# Erzeugt von patch_vbus_waechter.py (CL-USB-REC-128). NUR Testkarte.",
         "# Danach den MD5-Kopf mit dem patch.sh aus patch_md5_kopf.py --image APP.vbus_waechter.bin nachziehen.",
         "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"', "FERTIG=0"]
    for s, alt_h, neu in alle:
        z += [lies % raw(s), 'case "$IST" in',
              '  %s) FERTIG=$((FERTIG+1));;' % hashlib.sha256(neu).hexdigest(),
              '  %s) ;;' % alt_h,
              '  *) echo "Datei-Sektor 0x%X unerwartet -- Abbruch, nichts geschrieben."; exit 1;;' % s, 'esac']
    z += ['[ $FERTIG = %d ] && { echo "VBUS-Waechter ist schon drauf -- nichts zu tun"; exit 0; }' % len(alle),
          'read -p "Sicherung anlegen und %d Sektoren (%s) schreiben? [j/N] " x; [ "$x" = j ] || exit 1'
          % (len(alle), ", ".join("Datei 0x%X" % s for s, _, _ in alle))]
    for s, _, _ in alle:
        z.append('[ -e sektor_%06x.sicherung ] || dd if=$DEV of=sektor_%06x.sicherung bs=512 skip=%d count=1 iflag=direct status=none'
                 % (s, s, raw(s)))
    for s, _, _ in reversed(alle):           # Stubs zuerst, dann die Poolworte
        z.append("dd if=sektor_%06x.neu of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none" % (s, raw(s)))
    z.append("sync")
    for s, _, neu in alle:
        z += [lies % raw(s), '[ "$IST" = %s ] || { echo "Ruecklesen Datei-Sektor 0x%X weicht ab -- ./zurueck.sh"; exit 1; }'
              % (hashlib.sha256(neu).hexdigest(), s)]
    z += ['echo "fertig, Sektoren rueckgelesen -- jetzt den MD5-Kopf nachziehen; zurueck mit ./zurueck.sh"', ""]
    p = os.path.join(a.out, "patch.sh")
    open(p, "w").write("\n".join(z)); os.chmod(p, 0o755)
    zz = ["#!/bin/bash", "set -e", "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"',
          'read -p "Sicherungen zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1']
    for s, _, _ in alle:                     # Poolworte zuerst zurueck, dann der Stub
        zz.append("dd if=sektor_%06x.sicherung of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none"
                  % (s, raw(s)))
    zz += ["sync", 'echo "zurueck"', ""]
    p = os.path.join(a.out, "zurueck.sh")
    open(p, "w").write("\n".join(zz)); os.chmod(p, 0o755)
    print("Poolworte 0x%X -> 0x%X (IRQ 16), 0x%X -> 0x%X (IRQ 15); Stubs Datei 0x%X = Karte %d; Pool-Sektoren %s"
          % (ur.POOL, W1, rp.POOL, W2, so, raw(so), ", ".join("Datei 0x%X = Karte %d" % (s, raw(s)) for s in sekt)))
    print("ohne neuen Kopf waere [0x558] = 0x%08X" % pw.pruefwert(bild)[0])


if __name__ == "__main__":
    main()
