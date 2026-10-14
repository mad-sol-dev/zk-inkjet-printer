#!/usr/bin/env python3
# /// script
# dependencies = ["unicorn", "capstone"]
# ///
"""Emuliert die Kette VBUS-Waechter -> Ring -> Originalhandler (patch_vbus_waechter.py, CL-USB-REC-128).

Rahmen wie pruef_ringpuffer_emu.py: IRQ-Modus, Verteiler-Rahmen mit lr_irq bei
0x7FF7FC, sp 0x7FF7D0, lr 0xF9FD8. Geladen: gepatchtes Abbild, Stub-Sektoren
0x275600 (TMR1-Ring), 0x275800 (USB-ISR-Ring), 0x275A00 (Waechter). Das Ende ist
erreicht, wenn der Originalhandler (usbd_isr 0x109AC4 bzw. 0xFBAAC) oder die
Rueckkehr in den Verteiler (0xF9FD8) ausgefuehrt wuerde. Schreibzugriffe auf
AIC MECR/MDCR werden mitprotokolliert.

  uv run tools/scripts/pruef_vbus_waechter_emu.py --abzug <ram.bin>
"""
import argparse
import os
import struct
import sys

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import (UC_ARM_REG_CPSR, UC_ARM_REG_SPSR, UC_ARM_REG_SP, UC_ARM_REG_LR,
                               UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4,
                               UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patch_vbus_waechter as vw  # noqa: E402
import patch_ringpuffer as rp  # noqa: E402
import patch_usb_isr_ring as ur  # noqa: E402

ART = vw.ART
REGS = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4,
        UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8]
ZIELE = {ur.HANDLER: "usbd_isr", rp.HANDLER: "TMR1-Handler", 0xF9FD8: "Verteiler"}
FEHLER = []


def pruef(bed, text):
    print("  %s %s" % ("ok " if bed else "XX ", text))
    if not bed:
        FEHLER.append(text)


class Geraet:
    def __init__(self, ram):
        self.uc = uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        uc.mem_map(0, 0x800000)
        uc.mem_write(0, ram)
        uc.mem_write(vw.dauer.VA0, open(os.path.join(ART, "vbus_waechter", "APP.vbus_waechter.bin"), "rb").read())
        for s, d in ((0x275600, "ringpuffer"), (0x275800, "usb_isr_ring"), (0x275A00, "vbus_waechter")):
            uc.mem_write(vw.dauer.VA0 + s, open(os.path.join(ART, d, "sektor_%06x.neu" % s), "rb").read())
        uc.mem_write(rp.KOPF, b"\x00" * (0x2D8000 - rp.KOPF))
        for p in (0xB8000000, 0xB8002000, 0xB1008000):
            uc.mem_map(p, 0x1000)
        self.ziel, self.aic = None, []
        for z in ZIELE:
            uc.hook_add(UC_HOOK_CODE, self._halt, begin=z, end=z)
        uc.hook_add(UC_HOOK_MEM_WRITE, self._aic, begin=0xB8000120, end=0xB8000127)

    def _halt(self, uc, adr, size, _):
        self.ziel = adr
        uc.emu_stop()

    def _aic(self, uc, zugriff, adr, size, wert, _):
        self.aic.append((adr, wert))

    def setze(self, vbus, vbus_status, usb_stat=0x111, usb_enb=0x10E, merker=None):
        uc = self.uc
        for adr, w in ((0xB1008704, 0x80000320 if vbus else 0x320), (0xB1008010, usb_stat), (0xB1008014, usb_enb),
                       (0xB1008000, 1), (0xB1008008, 0x3F), (0xB8002018, 2), (0xB8002014, 0)):
            uc.mem_write(adr, struct.pack("<I", w))
        uc.mem_write(vw.VBUS_STATUS, bytes([vbus_status]))
        if merker is not None:
            uc.mem_write(vw.WACHT, struct.pack("<I", merker))

    def irq(self, start):
        uc = self.uc
        c = uc.reg_read(UC_ARM_REG_CPSR)
        uc.reg_write(UC_ARM_REG_CPSR, (c & ~0x1F) | 0x12 | 0xC0)
        uc.reg_write(UC_ARM_REG_SPSR, 0x60000013)
        sp = 0x7FF800 - 36
        rahmen = [0x1110 + i for i in range(7)] + [0x11C0, 0xE2E44]
        uc.mem_write(sp, b"".join(struct.pack("<I", x) for x in rahmen))
        sp -= 0xC
        uc.reg_write(UC_ARM_REG_SP, sp)
        uc.reg_write(UC_ARM_REG_LR, 0xF9FD8)
        vorher = [0xA0 + i for i in range(9)]
        for r, v in zip(REGS, vorher):
            uc.reg_write(r, v)
        self.ziel, self.aic = None, []
        uc.emu_start(start, 0, count=600)
        sauber = (uc.reg_read(UC_ARM_REG_SP) == sp and uc.reg_read(UC_ARM_REG_LR) == 0xF9FD8
                  and [uc.reg_read(r) for r in REGS] == vorher and uc.reg_read(UC_ARM_REG_CPSR) & 0x1F == 0x12)
        return ZIELE.get(self.ziel, hex(self.ziel or 0)), sauber, self.aic

    def wacht(self):
        return list(struct.unpack("<3I", bytes(self.uc.mem_read(vw.WACHT, 12))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--abzug", required=True)
    a = ap.parse_args()
    g = Geraet(open(a.abzug, "rb").read())
    bild = open(os.path.join(ART, "vbus_waechter", "APP.vbus_waechter.bin"), "rb").read()
    wort = lambda va: struct.unpack_from("<I", bild, va - vw.dauer.VA0)[0]
    print("Poolworte:")
    pruef(wort(ur.POOL) == vw.W1 and wort(rp.POOL) == vw.W2, "IRQ 16 -> W1 0x%X, IRQ 15 -> W2 0x%X" % (wort(ur.POOL), wort(rp.POOL)))

    print("W1 (vor usbd_isr):")
    g.setze(vbus=True, vbus_status=1, merker=0)
    z, s, aic = g.irq(vw.W1)
    pruef(z == "usbd_isr" and s and not aic, "Kabel da -> usbd_isr, Register sauber, kein AIC-Zugriff (%s)" % z)
    g.setze(vbus=False, vbus_status=1)
    z, s, aic = g.irq(vw.W1)
    pruef(z == "usbd_isr" and s and not aic, "erster Abzieh-Eintritt (VbusStatus 1) -> usbd_isr (%s)" % z)
    g.setze(vbus=False, vbus_status=0, usb_stat=0x011)
    z, s, aic = g.irq(vw.W1)
    pruef(z == "usbd_isr" and s and not aic, "Kabel weg, VBUS nicht anhaengig -> usbd_isr (%s)" % z)
    g.setze(vbus=False, vbus_status=0, usb_stat=0x111, usb_enb=0x00E)
    z, s, aic = g.irq(vw.W1)
    pruef(z == "usbd_isr" and s and not aic, "Kabel weg, VBUS anhaengig aber nicht freigegeben -> usbd_isr (%s)" % z)
    g.setze(vbus=False, vbus_status=0, usb_stat=0x111, usb_enb=0x10E)
    usb_ring_vorher = bytes(g.uc.mem_read(ur.KOPF, 0x20))
    z, s, aic = g.irq(vw.W1)
    pruef(z == "Verteiler" and s and aic == [(vw.AIC_MDCR, vw.IRQ_USB)],
          "Sturmfall -> Ruecksprung in den Verteiler, MDCR = 1<<16 (%s, %s)" % (z, [(hex(x), hex(y)) for x, y in aic]))
    pruef(g.wacht() == [1, 1, 0], "Merker 1, Sperren 1, Freigaben 0: %s" % g.wacht())
    pruef(bytes(g.uc.mem_read(ur.KOPF, 0x20)) == usb_ring_vorher, "USB-Ring im Sturmfall nicht beruehrt")

    print("W2 (vor dem TMR1-Handler):")
    g.setze(vbus=False, vbus_status=0)
    z, s, aic = g.irq(vw.W2)
    pruef(z == "TMR1-Handler" and s and not aic and g.wacht()[0] == 1, "Merker 1, Kabel weg -> nur weiter (%s)" % z)
    g.setze(vbus=True, vbus_status=0)
    z, s, aic = g.irq(vw.W2)
    pruef(z == "TMR1-Handler" and s and aic == [(vw.AIC_MECR, vw.IRQ_USB)],
          "Merker 1, Kabel da -> MECR = 1<<16, weiter (%s, %s)" % (z, [(hex(x), hex(y)) for x, y in aic]))
    pruef(g.wacht() == [0, 1, 1], "Merker 0, Sperren 1, Freigaben 1: %s" % g.wacht())
    z, s, aic = g.irq(vw.W2)
    pruef(z == "TMR1-Handler" and s and not aic, "Merker 0 -> keine zweite Freigabe")
    k = list(struct.unpack("<8I", bytes(g.uc.mem_read(rp.KOPF, 32))))
    pruef(k[0] == rp.MAGIC and k[7] == 3, "TMR1-Ring dahinter lief dreimal: alle Ticks %d" % k[7])
    if FEHLER:
        sys.exit("%d Pruefungen fehlgeschlagen" % len(FEHLER))
    print("alle Pruefungen ok")


if __name__ == "__main__":
    main()
