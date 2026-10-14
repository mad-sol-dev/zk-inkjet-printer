#!/usr/bin/env python3
# /// script
# dependencies = ["unicorn", "capstone"]
# ///
"""Emuliert den Stub aus patch_usb_isr_ring.py im Rahmen des AIC-Verteilers (CL-USB-REC-128).

Aufbau wie pruef_ringpuffer_emu.py: IRQ-Modus, Verteiler-Rahmen mit lr_irq bei
0x7FF7FC, sp 0x7FF7D0, lr 0xF9FD8; RAM aus einem Abzug, Code aus dem gepatchten
Abbild plus beiden Stub-Sektoren. MMIO der UDC (USBD_BA) und der Timer werden je
Eintritt mit Kennwerten belegt. Ende beim Sprung nach usbd_isr 0x109AC4.
r12 (ip) darf der Stub benutzen: der Verteiler sichert und stellt ihn selbst her.

  uv run tools/scripts/pruef_usb_isr_ring_emu.py --abzug <ram.bin> --dir <out von patch_usb_isr_ring.py> [--raus ring.bin]
"""
import argparse
import os
import struct
import sys

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_CPSR, UC_ARM_REG_SPSR, UC_ARM_REG_SP, UC_ARM_REG_LR,
                               UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4,
                               UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patch_usb_isr_ring as ur  # noqa: E402
import patch_ringpuffer as rp  # noqa: E402

REGS = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4,
        UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8]
FEHLER = []


def pruef(bed, text):
    print("  %s %s" % ("ok " if bed else "XX ", text))
    if not bed:
        FEHLER.append(text)


class Geraet:
    def __init__(self, ram, bild, stub):
        self.uc = uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        uc.mem_map(0, 0x800000)
        uc.mem_write(0, ram)
        uc.mem_write(ur.dauer.VA0, bild)
        uc.mem_write(ur.STUB, stub)
        uc.mem_write(ur.KOPF, b"\x00" * (0x2D8000 - ur.KOPF))
        uc.mem_map(0xB1008000, 0x1000)
        uc.mem_map(0xB8002000, 0x1000)
        self.ziel = None
        uc.hook_add(UC_HOOK_CODE, self._halt, begin=ur.HANDLER, end=ur.HANDLER)

    def _halt(self, uc, adr, size, _):
        self.ziel = adr
        uc.emu_stop()

    def eintritt(self, vbus, k, unterbrochen=0x000E2E40):
        uc = self.uc
        mm = {0xB1008000: 0x1000 + k, 0xB1008008: 0x2000 + k, 0xB1008010: 0x3000 + k, 0xB1008014: 0x10E,
              0xB1008704: (0x80000320 if vbus else 0x220) | (k << 12 & 0xF000), 0xB8002018: 2, 0xB8002014: 0x5000 + k}
        for adr, w in mm.items():
            uc.mem_write(adr, struct.pack("<I", w))
        c = uc.reg_read(UC_ARM_REG_CPSR)
        uc.reg_write(UC_ARM_REG_CPSR, (c & ~0x1F) | 0x12 | 0xC0)
        uc.reg_write(UC_ARM_REG_SPSR, 0x60000013)
        sp = 0x7FF800 - 36
        rahmen = [0x1110 + i for i in range(7)] + [0x11C0, unterbrochen + 4]
        uc.mem_write(sp, b"".join(struct.pack("<I", x) for x in rahmen))
        sp -= 0xC
        uc.reg_write(UC_ARM_REG_SP, sp)
        uc.reg_write(UC_ARM_REG_LR, 0xF9FD8)
        vorher = [0xA0 + i for i in range(9)]
        for r, v in zip(REGS, vorher):
            uc.reg_write(r, v)
        self.ziel = None
        uc.emu_start(ur.STUB, 0, count=400)
        return (self.ziel == ur.HANDLER and uc.reg_read(UC_ARM_REG_SP) == sp
                and uc.reg_read(UC_ARM_REG_LR) == 0xF9FD8 and [uc.reg_read(r) for r in REGS] == vorher
                and uc.reg_read(UC_ARM_REG_CPSR) & 0x1F == 0x12
                and uc.mem_read(0x7FF800 - 36, 36) == b"".join(struct.pack("<I", x) for x in rahmen)), mm

    def wort(self, va):
        return struct.unpack("<I", bytes(self.uc.mem_read(va, 4)))[0]

    def eintrag(self, puf, i):
        return [self.wort(puf + ur.EINTRAG * i + 4 * j) for j in range(8)]


def soll(mm, pc):
    return [pc, mm[0xB1008000], mm[0xB1008008], mm[0xB1008010], mm[0xB1008014], mm[0xB1008704], mm[0xB8002018], mm[0xB8002014]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--abzug", required=True)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--raus")
    a = ap.parse_args()
    ram = open(a.abzug, "rb").read()
    bild = open(os.path.join(a.dir, "APP.usb_isr_ring.bin"), "rb").read()
    stub = open(os.path.join(a.dir, "sektor_%06x.neu" % (ur.STUB - ur.dauer.VA0)), "rb").read()
    g = Geraet(ram, bild, stub)
    tmr1_vorher = bytes(g.uc.mem_read(rp.KOPF, 0x2000))

    print("Poolwort im Abbild:")
    pruef(struct.unpack_from("<I", bild, ur.POOL - ur.dauer.VA0)[0] == ur.STUB, "0x%X = 0x%X" % (ur.POOL, ur.STUB))
    pruef(struct.unpack_from("<I", bild, rp.POOL - ur.dauer.VA0)[0] == rp.STUB, "TMR1-Poolwort weiter 0x%X" % rp.STUB)

    print("Fall 1: 3 Eintritte mit VBUS")
    pruef(all(g.eintritt(True, k)[0] for k in range(3)), "Register/sp/lr/Rahmen unveraendert, Sprung in usbd_isr")
    k = [g.wort(ur.KOPF + 4 * i) for i in range(6)]
    pruef(k == [ur.MAGIC, 0, 0, 0, 3, 3], "Kopf %s" % ["0x%X" % x for x in k])

    print("Fall 2: 300 Eintritte ohne VBUS")
    ok, letzte = True, None
    erste = None
    for n in range(300):
        r, mm = g.eintritt(False, n, unterbrochen=0xE0000 + 4 * n)
        ok &= r
        if n == 0:
            erste = soll(mm, 0xE0000)
        letzte = soll(mm, 0xE0000 + 4 * n)
    pruef(ok, "jeder Eintritt sauber zurueck")
    k = [g.wort(ur.KOPF + 4 * i) for i in range(6)]
    pruef(k == [ur.MAGIC, 1, 1, 300, 303, 3], "Kopf: Zustand 1, Episode 1, n 300, gesamt 303, mit VBUS 3: %s" % k)
    pruef(g.eintrag(ur.PUF_A, 0) == erste, "A[0] = erster Eintritt: %s" % ["0x%X" % x for x in g.eintrag(ur.PUF_A, 0)])
    pruef(g.eintrag(ur.PUF_A, 255)[0] == 0xE0000 + 4 * 255, "A[255] = Eintritt 255")
    pruef(g.eintrag(ur.PUF_B, 299 & 0xFF) == letzte, "B[letzter] = %s" % ["0x%X" % x for x in g.eintrag(ur.PUF_B, 299 & 0xFF)])
    pruef(g.wort(ur.PUF_B + 256 * ur.EINTRAG) == 0 and g.wort(ur.PUF_A + 256 * ur.EINTRAG - 4) != 0, "Grenzen von A und B eingehalten")
    pruef(bytes(g.uc.mem_read(rp.KOPF, 0x2000)) == tmr1_vorher, "TMR1-Puffer 0x2CE000..0x2D0000 unberuehrt")

    print("Fall 3: VBUS zurueck, neue Episode")
    g.eintritt(True, 7)
    g.eintritt(False, 8)
    k = [g.wort(ur.KOPF + 4 * i) for i in range(6)]
    pruef(k[1] == 1 and k[2] == 2 and k[3] == 1, "Episode 2, n 1: %s" % k)

    zaehl = []
    h = g.uc.hook_add(UC_HOOK_CODE, lambda uc, adr, size, _: zaehl.append(adr))
    g.eintritt(False, 9)
    g.uc.hook_del(h)
    print("ein Eintritt ohne VBUS: %d Befehle" % (len(zaehl) - 1))
    if a.raus:
        open(a.raus, "wb").write(bytes(g.uc.mem_read(ur.KOPF, ur.PUF_B + 256 * ur.EINTRAG - ur.KOPF)))
    if FEHLER:
        sys.exit("%d Pruefungen fehlgeschlagen" % len(FEHLER))
    print("alle Pruefungen ok")


if __name__ == "__main__":
    main()
