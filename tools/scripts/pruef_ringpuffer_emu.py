#!/usr/bin/env python3
# /// script
# dependencies = ["unicorn", "capstone"]
# ///
"""Emuliert den Stub aus patch_ringpuffer.py im Rahmen des AIC-Verteilers (CL-USB-REC-128).

Aufbau wie am Geraet (gelesen 2026-10-14): IRQ-Modus, IRQ-Stack-Spitze 0x7FF800,
Verteiler 0xF9F88 hat {r0-r6, ip, lr} gesichert (lr_irq = unterbrochene Stelle + 4
bei 0x7FF7FC) und sp um 0xC gesenkt, dann blx Handler mit lr = 0xF9FD8. RAM aus
einem Abzug, Code aus dem gepatchten Abbild plus Stub-Sektor. MMIO: Timer-Flag
0xB8002018 und PHY_CTL 0xB1008704 werden je Fall gesetzt. Die Emulation endet,
wenn der Stub in den Originalhandler 0xFBAAC springt; geprueft werden dann
Register (unveraendert), sp, lr und der Pufferinhalt.

  uv run tools/scripts/pruef_ringpuffer_emu.py --abzug <ram.bin> --dir <out von patch_ringpuffer.py> [--raus ring.bin]
"""
import argparse
import os
import struct
import sys

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_CPSR, UC_ARM_REG_SPSR, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC,
                               UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4,
                               UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patch_ringpuffer as rp  # noqa: E402

REGS = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4,
        UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8]
IRQ, SVC, SYS, USR = 0x12, 0x13, 0x1F, 0x10
FEHLER = []


def pruef(bed, text):
    print("  %s %s" % ("ok " if bed else "XX ", text))
    if not bed:
        FEHLER.append(text)


class Geraet:
    def __init__(self, ram, bild, stub_sektor):
        self.uc = uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        uc.mem_map(0, 0x800000)
        uc.mem_write(0, ram)
        uc.mem_write(rp.dauer.VA0, bild)
        uc.mem_write(rp.STUB, stub_sektor)
        # Puffer leer wie im Abzug (dort 0)
        uc.mem_write(rp.KOPF, b"\x00" * (rp.PUF_B + 0x1000 - rp.KOPF))
        uc.mem_map(0xB8002000, 0x1000)
        uc.mem_map(0xB1008000, 0x1000)
        self.ziel = None
        uc.hook_add(UC_HOOK_CODE, self._halt, begin=rp.HANDLER, end=rp.HANDLER)

    def _halt(self, uc, adr, size, _):
        self.ziel = adr
        uc.emu_stop()

    def modus(self, m):
        c = self.uc.reg_read(UC_ARM_REG_CPSR)
        self.uc.reg_write(UC_ARM_REG_CPSR, (c & ~0x1F) | m | 0xC0)

    def tick(self, timer_flag=True, vbus=False, unterbrochen=0x000C43A4, int_modus=SVC, tickwert=1000):
        uc = self.uc
        uc.mem_write(0xB8002018, struct.pack("<I", 2 if timer_flag else 0))
        uc.mem_write(0xB1008704, struct.pack("<I", 0x80000220 if vbus else 0x220))
        uc.mem_write(rp.TICK, struct.pack("<Q", tickwert))
        # Register des unterbrochenen Modus
        self.modus(SYS if int_modus == USR else int_modus)
        uc.reg_write(UC_ARM_REG_SP, 0x7FE81C if int_modus == SVC else 0x7FFB00)
        uc.reg_write(UC_ARM_REG_LR, 0x0006A52C if int_modus == SVC else 0x00012345)
        # IRQ-Eintritt und Verteiler-Rahmen
        self.modus(IRQ)
        uc.reg_write(UC_ARM_REG_SPSR, 0x60000000 | int_modus)
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
        uc.emu_start(rp.STUB, 0, count=400)
        ok = (self.ziel == rp.HANDLER and uc.reg_read(UC_ARM_REG_SP) == sp
              and uc.reg_read(UC_ARM_REG_LR) == 0xF9FD8
              and [uc.reg_read(r) for r in REGS] == vorher
              and uc.reg_read(UC_ARM_REG_CPSR) & 0x1F == IRQ
              and uc.mem_read(0x7FF800 - 36, 36) == b"".join(struct.pack("<I", x) for x in rahmen))
        return ok

    def wort(self, va):
        return struct.unpack("<I", bytes(self.uc.mem_read(va, 4)))[0]

    def kopf(self):
        return [self.wort(rp.KOPF + 4 * i) for i in range(8)]

    def eintrag(self, puf, i):
        return [self.wort(puf + 16 * i + 4 * k) for k in range(4)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--abzug", required=True)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--raus", help="Pufferbereich nach den Faellen hier ablegen (Eingabe fuer ringpuffer_lesen.py --datei)")
    a = ap.parse_args()
    ram = open(a.abzug, "rb").read()
    bild = open(os.path.join(a.dir, "APP.ringpuffer.bin"), "rb").read()
    stub = open(os.path.join(a.dir, "sektor_%06x.neu" % (rp.STUB - rp.dauer.VA0)), "rb").read()
    g = Geraet(ram, bild, stub)

    print("Poolwort im Abbild:")
    pruef(struct.unpack_from("<I", bild, rp.POOL - rp.dauer.VA0)[0] == rp.STUB, "0x%X = 0x%X" % (rp.POOL, rp.STUB))

    print("Fall 1: Timer-Flag 0 (anderer Grund fuer IRQ 15)")
    pruef(g.tick(timer_flag=False), "Register/sp/lr/Rahmen unveraendert, Sprung in 0xFBAAC")
    pruef(g.kopf()[0] == 0, "Kopf nicht angelegt")

    print("Fall 2: 5 Ticks mit VBUS")
    pruef(all(g.tick(vbus=True) for _ in range(5)), "jeder Tick sauber zurueck in 0xFBAAC")
    k = g.kopf()
    pruef(k[0] == rp.MAGIC and k[1] == 0 and k[2] == 0 and k[4] == 5 and k[7] == 5,
          "Magic, Zustand 0, Episoden 0, VBUS-Ticks 5, alle 5: %s" % ["0x%X" % x for x in k])

    print("Fall 3: 1100 Ticks ohne VBUS, SVC unterbrochen bei 0xC43A4..")
    ok = True
    for n in range(1100):
        ok &= g.tick(vbus=False, unterbrochen=0xC0000 + 4 * n, tickwert=5000 + n)
    pruef(ok, "jeder Tick sauber zurueck")
    k = g.kopf()
    pruef(k[1] == 1 and k[2] == 1 and k[3] == 1100 and k[5] == 5000 and k[6] == 5000 + 1099 and k[7] == 1105,
          "Zustand 1, Episode 1, n 1100, Starttick 5000, letzter 6099, alle 1105: %s" % k)
    e = g.eintrag(rp.PUF_B, 1099 & 0xFF)
    pruef(e == [0xC0000 + 4 * 1099, 0x6A52C, 0x7FE81C, 0x60000013],
          "B[letzter] = PC, LR_svc, SP_svc, SPSR: %s" % ["0x%X" % x for x in e])
    e0 = g.eintrag(rp.PUF_A, 0)
    e255 = g.eintrag(rp.PUF_A, 255)
    pruef(e0[0] == 0xC0000 and e255[0] == 0xC0000 + 4 * 1020, "A[0] = Tick 0, A[255] = Tick 1020: 0x%X, 0x%X" % (e0[0], e255[0]))
    pruef(g.wort(rp.PUF_B + 0x1000) == 0 and g.wort(rp.PUF_A - 4) == 0, "nichts hinter B, nichts vor A geschrieben")

    print("Fall 4: USR unterbrochen (SYS-Register werden gelesen)")
    pruef(g.tick(vbus=False, unterbrochen=0x77770, int_modus=USR), "sauber zurueck")
    e = g.eintrag(rp.PUF_B, 1100 & 0xFF)
    pruef(e == [0x77770, 0x12345, 0x7FFB00, 0x60000010], "B = %s" % ["0x%X" % x for x in e])

    print("Fall 5: VBUS kommt zurueck, dann zweite Episode")
    g.tick(vbus=True)
    k = g.kopf()
    pruef(k[1] == 0 and k[3] == 1101 and k[4] == 6, "Zustand 0, n bleibt 1101, VBUS-Ticks 6: %s" % k)
    g.tick(vbus=False, tickwert=9000)
    k = g.kopf()
    pruef(k[2] == 2 and k[3] == 1 and k[5] == 9000, "Episode 2, n 1, Starttick 9000: %s" % k)

    print("Befehlszaehler: ein Tick ohne VBUS braucht ", end="")
    zaehl = []
    h = g.uc.hook_add(UC_HOOK_CODE, lambda uc, adr, size, _: zaehl.append(adr))
    g.tick(vbus=False)
    g.uc.hook_del(h)
    print("%d Befehle" % (len(zaehl) - 1))
    if a.raus:
        open(a.raus, "wb").write(bytes(g.uc.mem_read(rp.KOPF, rp.PUF_B + 256 * 16 - rp.KOPF)))
        print("Pufferbereich -> %s" % a.raus)
    if FEHLER:
        sys.exit("%d Pruefungen fehlgeschlagen" % len(FEHLER))
    print("alle Pruefungen ok")


if __name__ == "__main__":
    main()
