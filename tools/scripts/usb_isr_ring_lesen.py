#!/usr/bin/env python3
"""Liest und deutet den USB-Interrupt-Ring aus patch_usb_isr_ring.py (CL-USB-REC-128).

Quelle: Geraet ueber das RAM-Fenster (mit Positivkontrolle), voller RAM-Abzug
oder schon gelesene Rohdatei. Ausgabe: Kopf, Zusammenfassung der anhaengigen
und freigegebenen Quellen (Status & Freigabe) ueber alle Eintraege, dann die
ersten Eintraege aus A und die letzten aus B mit Bitnamen.
Bitnamen nach BSP UDC/lib/usbd.h und dem ISR-Vergleich in CL-USB-REC-128.

  sudo python3 tools/scripts/usb_isr_ring_lesen.py /dev/sdX [--roh ring.bin] [--alle]
  python3 tools/scripts/usb_isr_ring_lesen.py --abzug ram.bin
  python3 tools/scripts/usb_isr_ring_lesen.py --datei ring.bin
"""
import argparse
import collections
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patch_usb_isr_ring as ur  # noqa: E402
import ram_fenster_lesen as rf  # noqa: E402

LAENGE = ur.PUF_B + 256 * ur.EINTRAG - ur.KOPF
USB_BITS = {0x1: "SOF", 0x2: "RST", 0x4: "RESUME", 0x8: "SUSPEND", 0x10: "HISPD", 0x20: "DMA", 0x40: "TCLKOK", 0x100: "VBUS"}
L_BITS = {0x1: "USB", 0x2: "CEP", 0x4: "EPA", 0x8: "EPB", 0x10: "EPC", 0x20: "EPD"}


def namen(v, tab):
    n = [tab[b] for b in sorted(tab) if v & b]
    rest = v & ~sum(tab)
    if rest:
        n.append("0x%X" % rest)
    return "|".join(n) or "-"


def zeile(nr, e):
    pc, st_l, en_l, st, en, phy, tisr, tdr1 = e
    return ("  %6s PC %08X  L %s/%s -> %-8s  USB %03X/%03X -> %-16s PHY %08X VBUS %d  TMR1 %s  TDR1 %5d"
            % (nr, pc, "%02X" % st_l, "%02X" % en_l, namen(st_l & en_l, L_BITS), st, en, namen(st & en, USB_BITS),
               phy, phy >> 31, "anh." if tisr & 2 else "-   ", tdr1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dev", nargs="?")
    ap.add_argument("--abzug")
    ap.add_argument("--datei")
    ap.add_argument("--roh")
    ap.add_argument("--alle", action="store_true", help="alle Eintraege statt je 16 aus A und B")
    a = ap.parse_args()
    if a.datei:
        roh = open(a.datei, "rb").read()
    elif a.abzug:
        roh = open(a.abzug, "rb").read()[ur.KOPF:ur.KOPF + LAENGE]
    elif a.dev:
        rf.kontrolle(a.dev)
        roh = rf.lesen(a.dev, ur.KOPF, LAENGE)
    else:
        sys.exit("Geraet, --abzug oder --datei angeben")
    if a.roh:
        open(a.roh, "wb").write(roh)
        print("Rohdaten -> %s" % a.roh)
    assert len(roh) == LAENGE, len(roh)
    magic, zustand, episoden, n, gesamt, mit_vbus = struct.unpack_from("<6I", roh, 0)
    if magic != ur.MAGIC:
        sys.exit("kein Kopf (Magic 0x%08X statt 0x%08X) -- Patch nicht aktiv oder nie ein USB-Interrupt" % (magic, ur.MAGIC))
    print("Kopf 0x%X: Episoden %d, Eintritte in der letzten Episode n = %d, VBUS jetzt %s" %
          (ur.KOPF, episoden, n, "weg" if zustand else "da"))
    print("  usbd_isr-Eintritte gesamt %d, davon mit VBUS %d, ohne VBUS %d" % (gesamt, mit_vbus, gesamt - mit_vbus))

    ea = [struct.unpack_from("<8I", roh, ur.PUF_A - ur.KOPF + ur.EINTRAG * i) for i in range(min(n, 256))]
    nb = min(n, 256)
    eb = [struct.unpack_from("<8I", roh, ur.PUF_B - ur.KOPF + ur.EINTRAG * ((n - nb + i) & 0xFF)) for i in range(nb)]
    alle = ea + eb
    if not alle:
        return
    print("\nAnhaengig und freigegeben (ueber A und B, %d Eintraege):" % len(alle))
    h = collections.Counter((e[1] & e[2], e[3] & e[4]) for e in alle)
    for (l, u), k in h.most_common(8):
        print("  %5d x  L %-10s USB %s" % (k, namen(l, L_BITS), namen(u, USB_BITS)))
    print("  nichts anhaengig und freigegeben (ISR kehrt sofort zurueck): %d x" % sum(1 for e in alle if not e[1] & e[2]))
    print("  TMR1 anhaengig waehrend des Eintritts: %d von %d" % (sum(1 for e in alle if e[6] & 2), len(alle)))
    pcs = collections.Counter(e[0] for e in alle)
    print("  unterbrochene Stellen: %s" % ", ".join("%08X x%d" % (p, k) for p, k in pcs.most_common(6)))

    zeig = len(ea) if a.alle else min(16, len(ea))
    print("\nA -- erste Eintritte nach dem Abziehen (%d von %d):" % (zeig, len(ea)))
    for i, e in enumerate(ea[:zeig]):
        print(zeile("a%d" % i, e))
    zeig = nb if a.alle else min(16, nb)
    print("\nB -- letzte Eintritte vor dem Anstecken (%d von %d):" % (zeig, nb))
    for i, e in enumerate(eb[nb - zeig:]):
        print(zeile("n%d" % (n - zeig + i), e))


if __name__ == "__main__":
    main()
