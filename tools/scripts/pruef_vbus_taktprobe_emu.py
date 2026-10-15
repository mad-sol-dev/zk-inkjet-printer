#!/usr/bin/env python3
# /// script
# dependencies = ["unicorn", "capstone"]
# ///
"""Emuliert den Messstand Taktprobe (patch_vbus_taktprobe.py, CL-USB-REC-131) gegen drei UDC-Modelle.

Rahmen wie pruef_vbus_waechter_emu.py (IRQ-Modus, Verteiler-Rahmen, Ziel ist
usbd_isr 0x109AC4, der TMR1-Handler 0xFBAAC oder die Rueckkehr 0xF9FD8).
Geladen: RAM-Abzug, Endstand vbus_waechter_end, Sektor 0x275600 leer und die
neuen Sektoren 0x275800 (PROBE) und 0x275A00 (W1/W2). Der UDC ist ein
MMIO-Modell mit drei Schaltern:
  takt   -- ohne Takt nimmt der Block Schreibzugriffe auf USB_IRQ_STAT und EPA_MPS nicht an
  pegel  -- VBUS_IS wird ohne VBUS sofort neu gesetzt (Kandidat 1)
  taub   -- EPA_MPS nimmt nie etwas an (eine untaugliche Probe)
Je Modell: Abziehen (Sturmfall in W1), 1000 Ticks ohne Kabel, Anstecken, der
Einsteck-Zweig von usbd_isr als Modellschritt, 10 Ticks bis AN1, dann das
Urteil von vbus_taktprobe_lesen.py ueber die emulierten Bytes.

  uv run tools/scripts/pruef_vbus_taktprobe_emu.py --abzug <ram.bin>
"""
import argparse
import os
import struct
import sys

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pruef_vbus_waechter_emu as pe  # noqa: E402
import patch_vbus_taktprobe as tp  # noqa: E402
import patch_vbus_waechter as vw  # noqa: E402
import vbus_taktprobe_lesen as lesen  # noqa: E402
from pruef_vbus_waechter_emu import REGS, ZIELE, pruef  # noqa: E402
from unicorn.arm_const import UC_ARM_REG_CPSR, UC_ARM_REG_SPSR, UC_ARM_REG_SP, UC_ARM_REG_LR  # noqa: E402

USBD, AIC, TIMER, CLK = 0xB1008000, 0xB8000000, 0xB8002000, 0xB0000000


class Udc:
    def __init__(self, takt_ohne_kabel, pegel=False, taub=False):
        self.takt_ohne_kabel, self.pegel, self.taub = takt_ohne_kabel, pegel, taub
        self.takt = True
        self.vbus, self.stat, self.enb, self.mps, self.phy = True, 0x011, 0x10E, 0x200, 0x320
        self.schreib = []

    def lies(self, uc, off, size, _):
        if off == 0x704:
            return (0x80000000 if self.vbus else 0) | self.phy
        return {0x10: self.stat, 0x14: self.enb, 0x18: 0x6, 0x78: self.mps, 0x00: 1, 0x08: 0x3F}.get(off, 0)

    def schreibe(self, uc, off, size, wert, _):
        self.schreib.append((USBD + off, wert))
        if off == 0x10 and self.takt:
            self.stat &= ~wert
        elif off == 0x78 and self.takt and not self.taub:
            self.mps = wert & 0x7FF
        elif off == 0x704:
            self.phy = wert & 0x7FFFFFFF
        if self.pegel and not self.vbus:
            self.stat |= 0x100


class Geraet:
    def __init__(self, ram, udc):
        self.uc = uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        self.udc = udc
        uc.mem_map(0, 0x800000)
        uc.mem_write(0, ram)
        uc.mem_write(vw.dauer.VA0, open(os.path.join(tp.END, "APP.vbus_waechter_end.bin"), "rb").read())
        s8, sa, f = tp.sektoren()
        assert not f
        uc.mem_write(vw.dauer.VA0 + 0x275600, b"\x00" * 512)
        uc.mem_write(tp.PROBE, s8)
        uc.mem_write(tp.W1, sa)
        uc.mem_write(tp.WACHT, b"\x00" * 0x1000)
        uc.mmio_map(USBD, 0x1000, udc.lies, None, udc.schreibe, None)
        self.aic = []
        uc.mmio_map(AIC, 0x1000, lambda *a: 0, None, lambda u, o, s, w, d: self.aic.append((AIC + o, w)), None)
        uc.mmio_map(TIMER, 0x1000, lambda u, o, s, d: {0x18: 2}.get(o, 0), None, lambda *a: None, None)
        uc.mmio_map(CLK, 0x1000, lambda u, o, s, d: {0x204: 0x0005011F}.get(o, 0), None, lambda *a: None, None)
        self.ziel = None
        for z in ZIELE:
            uc.hook_add(UC_HOOK_CODE, self._halt, begin=z, end=z)

    def _halt(self, uc, adr, size, _):
        self.ziel = adr
        uc.emu_stop()

    def irq(self, start):
        uc = self.uc
        c = uc.reg_read(UC_ARM_REG_CPSR)
        uc.reg_write(UC_ARM_REG_CPSR, (c & ~0x1F) | 0x12 | 0xC0)
        uc.reg_write(UC_ARM_REG_SPSR, 0x60000013)
        sp = 0x7FF800 - 36 - 0xC
        uc.reg_write(UC_ARM_REG_SP, sp)
        uc.reg_write(UC_ARM_REG_LR, 0xF9FD8)
        vorher = [0xA0 + i for i in range(9)]
        for r, v in zip(REGS, vorher):
            uc.reg_write(r, v)
        self.ziel, self.aic, self.udc.schreib = None, [], []
        uc.emu_start(start, 0, count=20000)
        sauber = (uc.reg_read(UC_ARM_REG_SP) == sp and uc.reg_read(UC_ARM_REG_LR) == 0xF9FD8
                  and [uc.reg_read(r) for r in REGS] == vorher and uc.reg_read(UC_ARM_REG_CPSR) & 0x1F == 0x12)
        return ZIELE.get(self.ziel, hex(self.ziel or 0)), sauber, self.aic, self.udc.schreib

    def wacht(self):
        return bytes(self.uc.mem_read(tp.WACHT, lesen.LAENGE))

    def vbus_status(self, v):
        self.uc.mem_write(vw.VBUS_STATUS, bytes([v]))


def zyklus(g, modell, nr=1):
    """Abziehen -> Sturm -> 1000 Ticks -> Anstecken -> Einsteck-Zweig -> 10 Ticks -> Urteil."""
    u = g.udc
    n_vor = lambda s: (s or {}).get("n", 0)
    STAT, MPS = (USBD + 0x10, USBD + 0x78)
    print("[%s] W1 Normalfaelle:" % modell)
    vorher = g.wacht()
    for text, vbus, vs, stat, enb in (("Kabel da", True, 1, 0x111, 0x10E), ("erster Abzieh-Eintritt", False, 1, 0x111, 0x10E),
                                      ("VBUS nicht anhaengig", False, 0, 0x011, 0x10E),
                                      ("VBUS anhaengig, nicht frei", False, 0, 0x111, 0x00E)):
        u.vbus, u.stat, u.enb = vbus, stat, enb
        g.vbus_status(vs)
        z, s, aic, sw = g.irq(tp.W1)
        pruef(z == "usbd_isr" and s and not aic and not sw and g.wacht() == vorher,
              "%s -> usbd_isr, kein Schreibzugriff (%s)" % (text, z))

    print("[%s] W1 Sturmfall:" % modell)
    u.vbus, u.stat, u.enb, u.takt, u.phy = False, 0x111, 0x10E, u.takt_ohne_kabel, 0x220   # Abzieh-Zweig: PHY_CTL 0x220
    g.vbus_status(0)
    z, s, aic, sw = g.irq(tp.W1)
    k, sa = lesen.zerlegen(g.wacht())
    sp = sa["SPERRE"]
    pruef(z == "Verteiler" and s and aic == [(vw.AIC_MDCR, vw.IRQ_USB)], "Ruecksprung, MDCR = 1<<16, Register sauber (%s)" % z)
    pruef(sw == [(MPS, 0x20), (MPS, 0x200), (STAT, 0x100)],
          "Schreibzugriffe EPA_MPS 0x20, 0x200, USB_IRQ_STAT 0x100: %s" % [(hex(a), hex(w)) for a, w in sw])
    pruef(k["merker"] == 1 and k["sperren"] == nr and k["ticks"] == 0, "Merker 1, Sperren %d, Ticks 0" % k["sperren"])
    pruef(sp is not None and sp["n"] == nr and sp["stat"] == 0x111 and sp["quittiert"] == 1 and sp["probe"] == 0x20 and sp["mps_alt"] == 0x200,
          "SPERRE: STAT 0x111, Probewert 0x20, alt 0x200, quittiert")
    pruef(lesen.takt(sp) == ("laeuft" if u.takt and not u.taub else "steht"), "SPERRE Takt %s" % lesen.takt(sp))
    pruef(bool(sp["stat_q_spaet"] & 0x100), "VBUS_IS bleibt nach der Quittung (0x%X)" % sp["stat_q_spaet"])
    pruef(all(n_vor(sa[x]) == nr - 1 for x in ("SPAET", "AN0", "AN1")), "SPAET, AN0, AN1 noch beim Stand %d" % (nr - 1))

    print("[%s] W2 ohne Kabel, 1000 Ticks:" % modell)
    fehl, n_schreib = [], 0
    for t in range(1, 1002):
        z, s, aic, sw = g.irq(tp.W2)
        k, sa = lesen.zerlegen(g.wacht())
        if not (z == "TMR1-Handler" and s and not aic and k["ticks"] == t):
            fehl.append(t)
        erwartet = nr if t >= 1000 else nr - 1
        if n_vor(sa["SPAET"]) != erwartet:
            fehl.append(("SPAET", t))
        n_schreib += len(sw)
    pruef(not fehl, "jeder Tick -> TMR1-Handler, sauber, Ticks gezaehlt, SPAET genau beim 1000. (%s)" % fehl[:3])
    pruef(n_schreib == 3, "nur der 1000. Tick schreibt den UDC (3 Zugriffe), gesamt %d" % n_schreib)
    sp2 = sa["SPAET"]
    pruef(sp2["quittiert"] == 1 and lesen.takt(sp2) == lesen.takt(sa["SPERRE"]), "SPAET quittiert, Takt %s" % lesen.takt(sp2))

    print("[%s] Anstecken:" % modell)
    u.vbus = True
    z, s, aic, sw = g.irq(tp.W2)
    k, sa = lesen.zerlegen(g.wacht())
    pruef(z == "TMR1-Handler" and s and aic == [(vw.AIC_MECR, vw.IRQ_USB)], "MECR = 1<<16, weiter (%s)" % z)
    pruef(STAT not in [a for a, _ in sw], "AN0 schreibt USB_IRQ_STAT nicht (Einsteck-Ereignis bleibt)")
    pruef(k["merker"] == 0 and k["freigaben"] == nr and k["countdown"] == 10, "Merker 0, Freigaben %d, Countdown 10" % k["freigaben"])
    pruef(n_vor(sa["AN0"]) == nr and sa["AN0"]["quittiert"] == 0 and sa["AN0"]["stat"] & 0x100,
          "AN0 geschrieben, ohne Quittung, VBUS_IS gesetzt (Takt %s)" % lesen.takt(sa["AN0"]))

    # Einsteck-Zweig von usbd_isr als Modellschritt: PHY_CTL 0x320, Quittung, Takt wieder da
    u.takt = True
    u.phy = 0x320
    if u.takt:
        u.stat = (u.stat & ~0x100) | 0x40
    g.vbus_status(1)
    print("[%s] 10 Ticks bis AN1:" % modell)
    fehl, schreib_stat = [], 0
    for t in range(1, 13):
        z, s, aic, sw = g.irq(tp.W2)
        k, sa = lesen.zerlegen(g.wacht())
        if not (z == "TMR1-Handler" and s and not aic and n_vor(sa["AN1"]) == (nr if t >= 10 else nr - 1)):
            fehl.append(t)
        schreib_stat += sum(1 for a, _ in sw if a == STAT)
    pruef(not fehl and k["countdown"] == 0, "AN1 genau beim 10. Tick, danach nichts mehr (%s)" % fehl[:3])
    pruef(schreib_stat == 0, "W2 schreibt USB_IRQ_STAT nach der Freigabe nie")
    return lesen.urteil(sa), sa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--abzug", required=True)
    a = ap.parse_args()
    ram = open(a.abzug, "rb").read()
    faelle = [("Kandidat 2", dict(takt_ohne_kabel=False), "Kandidat 2"),
              ("Kandidat 1", dict(takt_ohne_kabel=True, pegel=True), "Kandidat 1 oder 3"),
              ("untaugliche Probe", dict(takt_ohne_kabel=False, taub=True), "kein Urteil: Positivkontrolle")]
    for name, kw, soll in faelle:
        u = Udc(**kw)
        g = Geraet(ram, u)
        u_text, sa = zyklus(g, name)
        pruef(u_text.startswith(soll), "[%s] Urteil: %s" % (name, u_text))
        if name == "Kandidat 2":
            pruef("TCLKOK_IS in AN1 gesetzt" in u_text, "[%s] TCLKOK_IS in AN1 erkannt" % name)
            print("[%s] zweiter Zyklus:" % name)
            _, sa2 = zyklus(g, name + " #2", nr=2)
            k, _ = lesen.zerlegen(g.wacht())
            pruef(sa2["SPERRE"]["n"] == 2 and k["sperren"] == 2 and k["freigaben"] == 2 and sa2["AN1"]["n"] == 2,
                  "zweiter Zyklus: SPERRE n 2, Sperren 2, Freigaben 2, AN1 n 2")
            print()
            lesen.bericht(g.wacht())
            print()
    print("[alt = 0x20]:")
    u = Udc(takt_ohne_kabel=True)
    u.mps = 0x20
    g = Geraet(ram, u)
    u.vbus, u.stat, u.enb = False, 0x111, 0x10E
    g.vbus_status(0)
    z, s, aic, sw = g.irq(tp.W1)
    sp = lesen.zerlegen(g.wacht())[1]["SPERRE"]
    pruef(sp["probe"] == 0x40 and sp["mps_spaet"] == 0x40 and sp["mps_zurueck"] == 0x20, "Probewert 0x40, zurueck 0x20")
    if pe.FEHLER:
        sys.exit("%d Pruefungen fehlgeschlagen" % len(pe.FEHLER))
    print("alle Pruefungen ok")


if __name__ == "__main__":
    main()
