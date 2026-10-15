#!/usr/bin/env python3
# /// script
# dependencies = ["unicorn", "capstone"]
# ///
"""Emuliert den Endpatch VBUS-Waechter (patch_vbus_waechter_end.py, CL-USB-REC-128).

Wie pruef_vbus_waechter_emu.py, aber mit dem Endstand: W1 springt im Normalfall
direkt nach usbd_isr, W2 direkt in den TMR1-Handler; die Ring-Sektoren sind leer.

  uv run tools/scripts/pruef_vbus_waechter_end_emu.py --abzug <ram.bin>
"""
import argparse
import os
import struct
import sys

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pruef_vbus_waechter_emu as pe  # noqa: E402
import patch_vbus_waechter as vw  # noqa: E402
import patch_ringpuffer as rp  # noqa: E402
import patch_usb_isr_ring as ur  # noqa: E402

DIR = os.path.join(vw.ART, "vbus_waechter_end")


class EndGeraet(pe.Geraet):
    def __init__(self, ram):
        self.uc = uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        uc.mem_map(0, 0x800000)
        uc.mem_write(0, ram)
        uc.mem_write(vw.dauer.VA0, open(os.path.join(DIR, "APP.vbus_waechter_end.bin"), "rb").read())
        for s in (0x275600, 0x275800, 0x275A00):
            uc.mem_write(vw.dauer.VA0 + s, open(os.path.join(DIR, "sektor_%06x.neu" % s), "rb").read())
        uc.mem_write(rp.KOPF, b"\x00" * (0x2D8000 - rp.KOPF))
        for p in (0xB8000000, 0xB8002000, 0xB1008000):
            uc.mem_map(p, 0x1000)
        self.ziel, self.aic, self.ring_zugriff = None, [], []
        for z in pe.ZIELE:
            uc.hook_add(UC_HOOK_CODE, self._halt, begin=z, end=z)
        uc.hook_add(UC_HOOK_CODE, self._ring, begin=0x2CD600, end=0x2CD9FF)
        uc.hook_add(UC_HOOK_MEM_WRITE, self._aic, begin=0xB8000120, end=0xB8000127)

    def _ring(self, uc, adr, size, _):
        self.ring_zugriff.append(adr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--abzug", required=True)
    a = ap.parse_args()
    g = EndGeraet(open(a.abzug, "rb").read())
    pruef = pe.pruef
    bild = open(os.path.join(DIR, "APP.vbus_waechter_end.bin"), "rb").read()
    wort = lambda va: struct.unpack_from("<I", bild, va - vw.dauer.VA0)[0]
    print("Endstand:")
    pruef(wort(ur.POOL) == vw.W1 and wort(rp.POOL) == vw.W2, "Poolworte IRQ 16 -> 0x%X, IRQ 15 -> 0x%X" % (wort(ur.POOL), wort(rp.POOL)))
    pruef(wort(0x109C60) == 0xE3A00E22 and wort(0xCEFD0) == 0x1AFFFFFB, "vbus_detect- und Ruecklese-Patch nicht enthalten")

    print("W1 (vor usbd_isr):")
    g.setze(vbus=True, vbus_status=1, merker=0)
    z, s, aic = g.irq(vw.W1)
    pruef(z == "usbd_isr" and s and not aic, "Kabel da -> usbd_isr (%s)" % z)
    g.setze(vbus=False, vbus_status=1)
    z, s, aic = g.irq(vw.W1)
    pruef(z == "usbd_isr" and s and not aic, "erster Abzieh-Eintritt -> usbd_isr (%s)" % z)
    g.setze(vbus=False, vbus_status=0, usb_stat=0x011)
    z, s, aic = g.irq(vw.W1)
    pruef(z == "usbd_isr" and s and not aic, "VBUS nicht anhaengig -> usbd_isr (%s)" % z)
    g.setze(vbus=False, vbus_status=0, usb_stat=0x111, usb_enb=0x10E)
    z, s, aic = g.irq(vw.W1)
    pruef(z == "Verteiler" and s and aic == [(vw.AIC_MDCR, vw.IRQ_USB)], "Sturmfall -> MDCR = 1<<16, Ruecksprung (%s)" % z)
    pruef(g.wacht() == [1, 1, 0], "Merker 1, Sperren 1: %s" % g.wacht())

    print("W2 (vor dem TMR1-Handler):")
    g.setze(vbus=False, vbus_status=0)
    z, s, aic = g.irq(vw.W2)
    pruef(z == "TMR1-Handler" and s and not aic, "Kabel weg -> weiter (%s)" % z)
    g.setze(vbus=True, vbus_status=0)
    z, s, aic = g.irq(vw.W2)
    pruef(z == "TMR1-Handler" and s and aic == [(vw.AIC_MECR, vw.IRQ_USB)], "Kabel da -> MECR = 1<<16 (%s)" % z)
    pruef(g.wacht() == [0, 1, 1], "Merker 0, Sperren 1, Freigaben 1: %s" % g.wacht())
    pruef(not g.ring_zugriff, "kein Befehl aus den Ring-Sektoren ausgefuehrt")
    pruef(bytes(g.uc.mem_read(rp.KOPF, 0x8000)) == b"\x00" * 0x8000, "Ring-Puffer 0x2CE000..0x2D6000 unberuehrt")
    if pe.FEHLER:
        sys.exit("%d Pruefungen fehlgeschlagen" % len(pe.FEHLER))
    print("alle Pruefungen ok")


if __name__ == "__main__":
    main()
