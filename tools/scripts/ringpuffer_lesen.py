#!/usr/bin/env python3
"""Liest und deutet den Ringpuffer aus patch_ringpuffer.py (CL-USB-REC-128).

Quelle ist das Geraet ueber das RAM-Fenster (ram_fenster_lesen.py, mit dessen
Positivkontrolle), ein voller RAM-Abzug oder eine schon gelesene Rohdatei.
Ausgabe: Kopf, dann A (erste Sekunde nach dem Abziehen, jeder 4. Tick) und B
(die letzten 256 Ticks vor dem Anstecken) in zeitlicher Reihenfolge, je
Eintrag PC, LR und SP des unterbrochenen Modus, Modus und I-Bit aus SPSR, die
Funktion um PC (naechstes push {..., lr} davor, Naeherung) und eine
Haeufigkeitsliste der PCs.

  sudo python3 tools/scripts/ringpuffer_lesen.py /dev/sdX [--roh ring.bin]
  python3 tools/scripts/ringpuffer_lesen.py --abzug ram.bin
  python3 tools/scripts/ringpuffer_lesen.py --datei ring.bin
"""
import argparse
import collections
import os
import struct
import sys

import patch_ringpuffer as rp
import ram_fenster_lesen as rf

LAENGE = rp.PUF_B + 256 * 16 - rp.KOPF
MODI = {0x10: "USR", 0x11: "FIQ", 0x12: "IRQ", 0x13: "SVC", 0x17: "ABT", 0x1B: "UND", 0x1F: "SYS"}
APP = open(rp.dauer.APP, "rb").read()


def funktion(pc):
    """Naechstes push {..., lr} vor pc im Original-APP (Naeherung fuer den Funktionsanfang)."""
    if not rp.dauer.VA0 <= pc < rp.dauer.VA0 + len(APP):
        return "-"
    for a in range(pc & ~3, max(rp.dauer.VA0, pc - 0x8000), -4):
        if (struct.unpack_from("<I", APP, a - rp.dauer.VA0)[0] & 0xFFFF4000) == 0xE92D4000:
            return "0x%X" % a
    return "?"


def eintraege(roh, off, anzahl):
    return [struct.unpack_from("<4I", roh, off + 16 * i) for i in range(anzahl)]


def zeile(nr, e):
    pc, lr, sp, spsr = e
    return "  %5s  PC %08X  LR %08X  SP %08X  %s%s  in %s" % (
        nr, pc, lr, sp, MODI.get(spsr & 0x1F, "%02X" % (spsr & 0x1F)), " I" if spsr & 0x80 else "  ", funktion(pc))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dev", nargs="?")
    ap.add_argument("--abzug", help="voller RAM-Abzug statt Geraet")
    ap.add_argument("--datei", help="schon gelesene Rohdatei (Kopf..Ende B)")
    ap.add_argument("--roh", help="gelesene Rohdaten zusaetzlich hier ablegen")
    a = ap.parse_args()
    if a.datei:
        roh = open(a.datei, "rb").read()
    elif a.abzug:
        roh = open(a.abzug, "rb").read()[rp.KOPF:rp.KOPF + LAENGE]
    elif a.dev:
        rf.kontrolle(a.dev)
        roh = rf.lesen(a.dev, rp.KOPF, LAENGE)
    else:
        sys.exit("Geraet, --abzug oder --datei angeben")
    if a.roh:
        open(a.roh, "wb").write(roh)
        print("Rohdaten -> %s" % a.roh)
    assert len(roh) == LAENGE, len(roh)

    magic, zustand, episoden, n, vbus_ticks, start, letzt, alle = struct.unpack_from("<8I", roh, 0)
    if magic != rp.MAGIC:
        sys.exit("kein Kopf (Magic 0x%08X statt 0x%08X) -- Ringpuffer-Patch nicht aktiv oder nie ein TMR1-Tick" % (magic, rp.MAGIC))
    print("Kopf 0x%X: Episoden %d, Ticks in der letzten Episode n = %d, VBUS jetzt %s" %
          (rp.KOPF, episoden, n, "weg" if zustand else "da"))
    print("  Tick 0xC18 bei Episodenbeginn %d, beim letzten Eintrag %d (Spanne %d ms)" % (start, letzt, letzt - start))
    print("  TMR1-Ticks gesamt %d, davon mit VBUS %d" % (alle, vbus_ticks))
    if n and letzt - start + 1 != n:
        print("  HINWEIS: n (%d) und Tickspanne (%d) weichen ab -- Ticks ohne Eintrag oder Tick-Zaehler steht"
              % (n, letzt - start + 1))

    off_a, off_b = rp.PUF_A - rp.KOPF, rp.PUF_B - rp.KOPF
    na = min((n + 3) // 4, 256)
    print("\nA -- erste Sekunde nach dem Abziehen (jeder 4. Tick, %d Eintraege):" % na)
    ea = eintraege(roh, off_a, na)
    for i, e in enumerate(ea):
        print(zeile("t%d" % (4 * i), e))

    nb = min(n, 256)
    erste = n - nb
    eb = [eintraege(roh, off_b + 16 * ((erste + i) & 0xFF), 1)[0] for i in range(nb)]
    print("\nB -- die letzten %d Ticks vor dem Anstecken (t%d..t%d):" % (nb, erste, n - 1))
    for i, e in enumerate(eb):
        print(zeile("t%d" % (erste + i), e))

    for name, liste in (("A", ea), ("B", eb)):
        if not liste:
            continue
        h = collections.Counter(e[0] for e in liste)
        print("\nHaeufigste PCs in %s:" % name)
        for pc, k in h.most_common(10):
            print("  %08X  %4d x  in %s" % (pc, k, funktion(pc)))


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
