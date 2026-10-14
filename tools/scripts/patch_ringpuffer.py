#!/usr/bin/env python3
"""Ringpuffer im TMR1-Interrupt: das Geraet zeichnet selbst auf, wo es nach dem Abziehen steht (CL-USB-REC-128).

Warum: Das RAM-Fenster braucht das Kabel, und mit Kabel laeuft das Geraet
weiter -- den Zustand dazwischen sieht es nie (Abzug ram_nach_wiederanstecken.bin).
Also schreibt das Geraet ihn selbst mit, solange VBUS fehlt, und man liest
ihn nach dem Anstecken.

Einhaengen (gelesen 2026-10-14): Der IRQ-Vektor zeigt auf den AIC-Verteiler
0xF9F88 (push {r0-r6, ip, lr}; sub sp,#0xC; blx [0x810 + 4*IRQ]). Der
TMR1-Handler 0xFBAAC steht dort als IRQ 15; eingetragen wird er an genau
einer Stelle, sysInstallISR(2, 15, h) bei 0xB4290 mit dem Poolwort 0xB43E0.
Dieses Wort zeigt nach dem Patch auf den Stub; der Stub springt am Ende mit
unveraendertem lr in den Originalhandler (Endaufruf).

Stub (VA 0x2CD600, Datei 0x275600, eigener Sektor hinter den Stubs von
patch_usb_dauerbetrieb/patch_ram_fenster; ausserhalb des MD5-Bereichs, aber
innerhalb der 0x280000 Byte, die BOOT laedt):
  nur wenn TMR1-Flag (MMIO 0xB8002018 Bit 1) gesetzt:
    Kopf beim ersten Mal anlegen (Magic 'RING'), Zaehler 'alle Ticks' +1
    VBUS da (MMIO 0xB1008704 Bit 31): Zustand = 0, Zaehler 'Ticks mit VBUS' +1
    VBUS weg: beim Uebergang neue Episode (Zaehler +1, n = 0, Starttick);
      Eintrag {PC, LR, SP, SPSR} der unterbrochenen Stelle:
        PC = lr_irq - 4 vom Verteiler-Rahmen ([sp+84] nach eigenem push)
        LR/SP = Register des unterbrochenen Modus (aus SPSR, USR -> SYS)
      B: Ring, jeder Tick, 256 Eintraege  -> die letzten 256 ms vor dem Anstecken
      A: jeder 4. Tick fuer n < 1024       -> die erste Sekunde nach dem Abziehen
      n += 1, letzter Tick
  dann b 0xFBAAC
Steht der TMR1-Interrupt (CPU mit gesperrten IRQs), bleibt n stehen und der
letzte Eintrag in B zeigt, wo. Laeuft er, zeigt B die Schleife des Stillstands.

Puffer (RAM, Laufzeit, nicht auf der Karte; im Abzug vom 2026-10-14 ist
0x2CD600..0x2D8000 durchweg 0, also unbenutzt; Heap ab 0x2D8000):
  KOPF 0x2CE000: +0 Magic, +4 Zustand, +8 Episoden, +0xC n, +0x10 Ticks mit
                 VBUS, +0x14 Starttick, +0x18 letzter Tick, +0x1C alle Ticks
  A    0x2CE100..0x2CF100, B 0x2CF100..0x2D0100 (je 256 x 16 Byte)
Lesen: tools/scripts/ringpuffer_lesen.py.

Basis ist der Kartenstand nach md5_kopf_2 (Ruecklese-Patch drauf). Danach
den Kopf nachziehen:
  python3 tools/scripts/patch_md5_kopf.py --image <out>/APP.ringpuffer.bin --out <dir2>
Reihenfolge an der Karte: <out>/patch.sh, dann <dir2>/patch.sh; zurueck umgekehrt.

  python3 tools/scripts/patch_ringpuffer.py --out <dir> [--device /dev/sdX] [--basis ABBILD]
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

HIER = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HIER, "..", "..", "research", "phase_a_sd_analysis", "artifacts")
BASIS = os.path.join(ART, "md5_kopf_2", "APP.md5kopf.bin")

POOL, LADER = 0xB43E0, 0xB4290          # sysInstallISR(2, 15, [POOL])
HANDLER = 0xFBAAC                        # TMR1-Handler (IRQ 15)
STUB = 0x2CD600                          # Datei 0x275600
KOPF, PUF_A, PUF_B = 0x2CE000, 0x2CE100, 0x2CF100
MAGIC = 0x474E4952                       # 'RING'
TIMER_BA, PHY_CTL, TICK = 0xB8002000, 0xB1008704, 0xC18
LR_OFF = 84                              # lr_irq relativ zu sp nach push {r0-r8, lr}

COND = {"": 0xE, "eq": 0x0, "ne": 0x1, "hs": 0x2, "lo": 0x3}


def imm12(v):
    """ARM-Immediate (8 Bit rotiert) oder AssertionError."""
    for rot in range(16):
        w = ((v << (2 * rot)) | (v >> (32 - 2 * rot))) & 0xFFFFFFFF if rot else v
        if w < 256:
            return (rot << 8) | w
    raise AssertionError("kein Immediate: 0x%X" % v)


def regs(*r):
    return sum(1 << x for x in r)


class Asm:
    def __init__(self, basis):
        self.basis, self.code, self.labels, self.pool, self.fix = basis, [], {}, [], []

    def pc(self):
        return self.basis + 4 * len(self.code)

    def lab(self, n):
        self.labels[n] = self.pc()

    def w(self, word, text):
        self.code.append([word, text])

    def ldr_lit(self, rd, wert, text):
        self.fix.append(("lit", len(self.code), rd, wert))
        self.w(0, text)

    def b(self, cond, ziel, text):
        self.fix.append(("b", len(self.code), cond, ziel))
        self.w(0, text)

    def fertig(self):
        # Literalpool hinter dem Code, jeder Wert einmal
        werte = []
        for f in self.fix:
            if f[0] == "lit" and f[3] not in werte:
                werte.append(f[3])
        pool_va = {v: self.pc() + 4 * i for i, v in enumerate(werte)}
        for kind, i, a, b in self.fix:
            va = self.basis + 4 * i
            if kind == "lit":
                off = pool_va[b] - (va + 8)
                assert 0 <= off < 4096
                self.code[i][0] = 0xE59F0000 | (a << 12) | off
            else:
                ziel = self.labels[b] if isinstance(b, str) else b
                d = ziel - (va + 8)
                assert d % 4 == 0 and -(1 << 25) <= d < (1 << 25)
                self.code[i][0] = (COND[a] << 28) | 0x0A000000 | ((d >> 2) & 0xFFFFFF)
        for v in werte:
            self.w(v, None)
        return self.code


def ldr(rd, rn, off):
    return 0xE5900000 | (rn << 16) | (rd << 12) | off


def str_(rd, rn, off):
    return 0xE5800000 | (rn << 16) | (rd << 12) | off


def dp(op, rd, rn, imm, cond=""):
    """Datenverarbeitung mit Immediate: op in and/sub/add/orr/mov/bic/tst/cmp."""
    code = {"and": 0x0, "sub": 0x2, "add": 0x4, "tst": 0x8, "cmp": 0xA, "orr": 0xC, "mov": 0xD, "bic": 0xE}[op]
    s = 1 if op in ("tst", "cmp") else 0
    return (COND[cond] << 28) | 0x02000000 | (code << 21) | (s << 20) | (rn << 16) | (rd << 12) | imm12(imm)


def stub():
    a = Asm(STUB)
    a.w(0xE92D0000 | regs(0, 1, 2, 3, 4, 5, 6, 7, 8, 14), "push {r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}")
    a.ldr_lit(0, TIMER_BA, "ldr r0, [pc, #")
    a.w(ldr(1, 0, 0x18), "ldr r1, [r0, #0x18]")
    a.w(dp("tst", 0, 1, 2), "tst r1, #2")
    a.b("eq", "ende", "beq")
    a.ldr_lit(4, KOPF, "ldr r4, [pc, #")
    a.w(ldr(1, 4, 0), "ldr r1, [r4]")
    a.ldr_lit(2, MAGIC, "ldr r2, [pc, #")
    a.w(0xE1510002, "cmp r1, r2")
    a.b("eq", "init_ok", "beq")
    a.w(dp("mov", 3, 0, 0), "mov r3, #0")
    for o in range(4, 0x20, 4):
        a.w(str_(3, 4, o), "str r3, [r4, #%s]" % (o if o < 10 else "0x%x" % o))
    a.w(str_(2, 4, 0), "str r2, [r4]")
    a.lab("init_ok")
    a.w(ldr(1, 4, 0x1C), "ldr r1, [r4, #0x1c]")
    a.w(dp("add", 1, 1, 1), "add r1, r1, #1")
    a.w(str_(1, 4, 0x1C), "str r1, [r4, #0x1c]")
    a.ldr_lit(0, PHY_CTL, "ldr r0, [pc, #")
    a.w(ldr(0, 0, 0), "ldr r0, [r0]")
    a.w(dp("tst", 0, 0, 0x80000000), "tst r0, #0x80000000")
    a.b("eq", "vbus_aus", "beq")
    a.w(dp("mov", 1, 0, 0), "mov r1, #0")
    a.w(str_(1, 4, 4), "str r1, [r4, #4]")
    a.w(ldr(1, 4, 0x10), "ldr r1, [r4, #0x10]")
    a.w(dp("add", 1, 1, 1), "add r1, r1, #1")
    a.w(str_(1, 4, 0x10), "str r1, [r4, #0x10]")
    a.b("", "ende", "b")
    a.lab("vbus_aus")
    a.ldr_lit(6, TICK, "ldr r6, [pc, #")
    a.w(ldr(6, 6, 0), "ldr r6, [r6]")
    a.w(ldr(1, 4, 4), "ldr r1, [r4, #4]")
    a.w(dp("cmp", 0, 1, 0), "cmp r1, #0")
    a.b("ne", "lauf", "bne")
    a.w(dp("mov", 1, 0, 1), "mov r1, #1")
    a.w(str_(1, 4, 4), "str r1, [r4, #4]")
    a.w(ldr(1, 4, 8), "ldr r1, [r4, #8]")
    a.w(dp("add", 1, 1, 1), "add r1, r1, #1")
    a.w(str_(1, 4, 8), "str r1, [r4, #8]")
    a.w(dp("mov", 1, 0, 0), "mov r1, #0")
    a.w(str_(1, 4, 0xC), "str r1, [r4, #0xc]")
    a.w(str_(6, 4, 0x14), "str r6, [r4, #0x14]")
    a.lab("lauf")
    a.w(str_(6, 4, 0x18), "str r6, [r4, #0x18]")
    a.w(ldr(5, 4, 0xC), "ldr r5, [r4, #0xc]")
    a.w(dp("add", 1, 5, 1), "add r1, r5, #1")
    a.w(str_(1, 4, 0xC), "str r1, [r4, #0xc]")
    a.w(ldr(0, 13, LR_OFF), "ldr r0, [sp, #0x%x]" % LR_OFF)
    a.w(dp("sub", 0, 0, 4), "sub r0, r0, #4")
    a.w(0xE14F3000, "mrs r3, spsr")
    a.w(dp("and", 7, 3, 0x1F), "and r7, r3, #0x1f")
    a.w(dp("cmp", 0, 7, 0x10), "cmp r7, #0x10")
    a.w(dp("mov", 7, 0, 0x1F, "eq"), "moveq r7, #0x1f")
    a.w(0xE10F8000, "mrs r8, apsr")
    a.w(dp("bic", 1, 8, 0x1F), "bic r1, r8, #0x1f")
    a.w(0xE1811007, "orr r1, r1, r7")
    a.w(0xE121F001, "msr cpsr_c, r1")
    a.w(0xE1A0200D, "mov r2, sp")
    a.w(0xE1A0100E, "mov r1, lr")
    a.w(0xE121F008, "msr cpsr_c, r8")
    a.w(dp("and", 7, 5, 0xFF), "and r7, r5, #0xff")
    a.ldr_lit(6, PUF_B, "ldr r6, [pc, #")
    a.w(0xE0866207, "add r6, r6, r7, lsl #4")
    a.w(0xE886000F, "stm r6, {r0, r1, r2, r3}")
    a.w(dp("cmp", 0, 5, 0x400), "cmp r5, #0x400")
    a.b("hs", "ende", "bhs")
    a.w(dp("tst", 0, 5, 3), "tst r5, #3")
    a.b("ne", "ende", "bne")
    a.ldr_lit(6, PUF_A, "ldr r6, [pc, #")
    a.w(0xE0866105, "add r6, r6, r5, lsl #2")
    a.w(0xE886000F, "stm r6, {r0, r1, r2, r3}")
    a.lab("ende")
    a.w(0xE8BD0000 | regs(0, 1, 2, 3, 4, 5, 6, 7, 8, 14), "pop {r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}")
    a.b("", HANDLER, "b #0x%x" % HANDLER)
    return a.fertig()


def pruefen(code):
    """Jeden Befehl mit capstone zurueckdisassemblieren und mit dem Soll vergleichen."""
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
    fehler = 0
    for i, (wort, soll) in enumerate(code):
        if soll is None:
            continue
        va = STUB + 4 * i
        ins = list(md.disasm(struct.pack("<I", wort), va))
        ist = ("%s %s" % (ins[0].mnemonic, ins[0].op_str)).strip() if ins else "?"
        ok = ist == soll or (soll.endswith("#") and ist.startswith(soll)) or \
            (soll in ("beq", "bne", "bhs", "b") and ist.split()[0] == soll)
        print("  %s 0x%08X  %08X  %s" % ("ok " if ok else "XX ", va, wort, ist + ("" if ok else "   soll: " + soll)))
        fehler += not ok
    return fehler


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

    # Einhaengestelle: einziger Lader des Poolworts, Wert = Handler
    o = POOL - dauer.VA0
    if struct.unpack_from("<I", b, o)[0] != HANDLER:
        sys.exit("Poolwort 0x%X ist nicht 0x%X" % (POOL, HANDLER))
    w = struct.unpack_from("<I", b, LADER - dauer.VA0)[0]
    assert (w & 0xFFFFF000) == 0xE59F2000 and LADER + 8 + (w & 0xFFF) == POOL, hex(w)
    assert struct.unpack_from("<I", b, 0xB4294 - dauer.VA0)[0] == 0xE3A0100F      # mov r1, #0xf
    s = o // 512 * 512
    if b[s:s + 512] != orig[s:s + 512]:
        sys.exit("Sektor Datei 0x%X ist in der Basis schon veraendert" % s)

    code = stub()
    print("Stub 0x%X, %d Worte:" % (STUB, len(code)))
    if pruefen(code):
        sys.exit("Befehle stimmen nicht -- nichts erzeugt")
    stub_bytes = b"".join(struct.pack("<I", c[0]) for c in code)
    so = STUB - dauer.VA0
    assert so % 512 == 0 and so >= len(orig) and so + 512 <= dauer.APP_MAX and len(stub_bytes) <= 512
    assert STUB + len(stub_bytes) <= KOPF and PUF_B + 256 * 16 <= 0x2D8000

    neu_pool = bytearray(b[s:s + 512])
    struct.pack_into("<I", neu_pool, o - s, STUB)
    neu_pool = bytes(neu_pool)
    neu_stub = stub_bytes + b"\x00" * (512 - len(stub_bytes))
    bild = bytearray(b)
    bild[s:s + 512] = neu_pool
    bild = bytes(bild)

    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "sektor_%06x.neu" % s), "wb").write(neu_pool)
    open(os.path.join(a.out, "sektor_%06x.neu" % so), "wb").write(neu_stub)
    open(os.path.join(a.out, "APP.ringpuffer.bin"), "wb").write(bild)
    leer = hashlib.sha256(b"\x00" * 512).hexdigest()
    sekt = [(s, b[s:s + 512], neu_pool), (so, None, neu_stub)]
    raw = lambda x: (dauer.RAW_APP >> 9) + x // 512
    lies = 'IST=$(dd if=$DEV bs=512 skip=%d count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)'
    z = ["#!/bin/bash", "set -e",
         "# Erzeugt von patch_ringpuffer.py (CL-USB-REC-128). NUR Testkarte.",
         "# Danach den MD5-Kopf mit dem patch.sh aus patch_md5_kopf.py --image APP.ringpuffer.bin nachziehen.",
         "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"', "FERTIG=0"]
    for x, alt, neu in sekt:
        alt_h = hashlib.sha256(alt).hexdigest() if alt else leer
        z += [lies % raw(x),
              'case "$IST" in',
              '  %s) FERTIG=$((FERTIG+1));;' % hashlib.sha256(neu).hexdigest(),
              '  %s) ;;' % alt_h,
              '  *) echo "Datei-Sektor 0x%X unerwartet -- Abbruch, nichts geschrieben."; exit 1;;' % x,
              'esac']
    z += ['[ $FERTIG = 2 ] && { echo "Ringpuffer ist schon drauf -- nichts zu tun"; exit 0; }',
          'read -p "Sicherung anlegen und 2 Sektoren (Datei 0x%X, 0x%X) schreiben? [j/N] " x; [ "$x" = j ] || exit 1' % (s, so)]
    for x, _, _ in sekt:
        z.append('[ -e sektor_%06x.sicherung ] || dd if=$DEV of=sektor_%06x.sicherung bs=512 skip=%d count=1 iflag=direct status=none'
                 % (x, x, raw(x)))
    # Stub zuerst, dann das Poolwort: ein Abbruch dazwischen laesst den Stub ungenutzt
    for x, _, neu in reversed(sekt):
        z.append("dd if=sektor_%06x.neu of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none" % (x, raw(x)))
    z.append("sync")
    for x, _, neu in sekt:
        z += [lies % raw(x),
              '[ "$IST" = %s ] || { echo "Ruecklesen Datei-Sektor 0x%X weicht ab -- ./zurueck.sh"; exit 1; }'
              % (hashlib.sha256(neu).hexdigest(), x)]
    z += ['echo "fertig, beide Sektoren rueckgelesen -- jetzt den MD5-Kopf nachziehen; zurueck mit ./zurueck.sh"', ""]
    p = os.path.join(a.out, "patch.sh")
    open(p, "w").write("\n".join(z)); os.chmod(p, 0o755)
    zz = ["#!/bin/bash", "set -e", "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"',
          'read -p "Sicherungen zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1']
    for x, _, _ in sekt:      # Poolwort zuerst zurueck, dann der Stub
        zz.append("dd if=sektor_%06x.sicherung of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none"
                  % (x, raw(x)))
    zz += ["sync", 'echo "zurueck"', ""]
    p = os.path.join(a.out, "zurueck.sh")
    open(p, "w").write("\n".join(zz)); os.chmod(p, 0o755)
    v1, _, _ = pw.pruefwert(bild)
    print("Poolwort 0x%X (Datei 0x%X): 0x%X -> 0x%X; Stub Datei 0x%X = Karte %d; Pool-Sektor Karte %d"
          % (POOL, o, HANDLER, STUB, so, raw(so), raw(s)))
    print("ohne neuen Kopf waere [0x558] = 0x%08X" % v1)


if __name__ == "__main__":
    main()
