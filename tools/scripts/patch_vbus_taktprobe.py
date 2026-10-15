#!/usr/bin/env python3
"""Messstand Taktprobe: steht der Transceiver-Takt, wenn VBUS_IS sich nicht loeschen laesst? (CL-USB-REC-131)

Frage: Nach dem Abziehen bleibt USB_IRQ_STAT Bit 8 (VBUS_IS) trotz Quittung
stehen (CL-USB-REC-129). Kandidat 2: ohne PHY-Takt uebernimmt der UDC das
Loeschen nicht. Kandidat 1/3: Pegelsteuerung oder Eigenheit bei laufendem Takt.
Nuvoton prueft den PHY-Takt per Schreiben und Ruecklesen von EPA_MPS
(W55FA93-Linux, NUC970, N9H30, M480); ohne Takt uebernimmt der Block den
Schreibzugriff nicht. Das wird hier einmalig und ohne Warteschleife gemacht.

Basis ist der Endstand vbus_waechter_end (patch_vbus_waechter_end.py, heute auf
der Testkarte). Imagebereich, Poolworte und MD5-Kopf bleiben unveraendert;
geaendert werden nur zwei Sektoren hinter dem Image:
  Datei 0x275A00: W1 0x2CDA00 / W2 0x2CDB00 -- der Waechter wie bisher, plus Probe
  Datei 0x275800: PROBE 0x2CD800 (im Endstand leer; frueher USB-ISR-Ring)

  W1 (vor usbd_isr): Sturmfall wie im Waechter -> MDCR = 1<<16, Merker, Sperren +1,
     Ticks seit Sperre = 0, dann PROBE(SPERRE, mit Quittung).
  W2 (vor dem TMR1-Handler, je Tick):
     gesperrt, Kabel weg: Ticks seit Sperre +1; beim 1000. PROBE(SPAET, mit Quittung)
     gesperrt, Kabel da:  PROBE(AN0, ohne Quittung) -- vor der Freigabe, also bevor
                          usbd_isr den Einsteck-Zweig (PHY_CTL 0x320) laufen laesst;
                          dann Merker 0, Freigaben +1, Countdown 10, MECR = 1<<16
     frei, Countdown > 0: -1; bei 0 PROBE(AN1, ohne Quittung) -- Positivkontrolle
                          10 ms nach der Freigabe, vor jeder Aufzaehlung durch den Host
  PROBE(r0 = Datensatz, r1 = 1: quittieren), Datensatz 16 Worte:
     +00 n          +04 Tick [0xC18]   +08 USB_IRQ_STAT   +0C USB_IRQ_ENB
     +10 PHY_CTL    +14 AHBCLK         +18 USB_OPER       +1C EPA_MPS alt
     +20 Probewert (0x20, bei alt 0x20: 0x40)  +24 EPA_MPS sofort nach dem Schreiben
     +28 EPA_MPS nach Wartezeit        +2C EPA_MPS nach Zurueckschreiben + Wartezeit
     +30 USB_IRQ_STAT sofort nach Schreiben 0x100   +34 dasselbe nach Wartezeit
     +38 Quittung versucht (1/0)       +3C Magic 'TKP1'
  Wartezeit: 0x200 Durchlaeufe subs/bne, einige Mikrosekunden -- weit mehr als die
  Synchronisierer-Latenz eines 30-MHz-UTMI-Takts. W2 schreibt USB_IRQ_STAT nur im
  SPAET-Fall; AN0/AN1 lesen nur, sonst verschluckte die Probe das Einsteck-Ereignis.

Daten ab WACHT 0x2D7000 (Laufzeit-RAM, BOOT-Ladebereich, nach jedem Start 0):
  +00 Merker  +04 Sperren  +08 Freigaben  +0C Ticks seit Sperre  +10 Countdown
  +20 SPERRE  +60 SPAET  +A0 AN0  +E0 AN1    (je 0x40, Ende 0x2D7120)
Lesen: tools/scripts/vbus_taktprobe_lesen.py (RAM-Fenster).

  python3 tools/scripts/patch_vbus_taktprobe.py --out <dir> [--device /dev/sdX]
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
from patch_ringpuffer import Asm, ldr, str_, dp, regs

HIER = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HIER, "..", "..", "research", "phase_a_sd_analysis", "artifacts")
END = os.path.join(ART, "vbus_waechter_end")
L = 0x27522C

PROBE = 0x2CD800                        # Datei 0x275800
W1, W2, WACHT = vw.W1, vw.W2, vw.WACHT  # 0x2CDA00, 0x2CDB00, 0x2D7000
TICKS, COUNTDOWN = 0x0C, 0x10           # Offsets in WACHT
SPERRE, SPAET, AN0, AN1 = 0x20, 0x60, 0xA0, 0xE0
SATZ = 0x40
SPAET_TICKS, AN1_TICKS = 1000, 10
MAGIC = 0x31504B54                      # 'TKP1'
AHBCLK = 0xB0000204
TICK = rp.TICK                          # 0xC18
EPA_MPS, USB_IRQ_STAT, USB_IRQ_ENB, USB_OPER = 0x78, 0x10, 0x14, 0x18
WARTE = 0x200

PUSH = 0xE92D0000 | regs(0, 1, 2, 3, 14)
POP = 0xE8BD0000 | regs(0, 1, 2, 3, 14)
T_PUSH, T_POP = "push {r0, r1, r2, r3, lr}", "pop {r0, r1, r2, r3, lr}"


def bl(a, ziel):
    d = ziel - (a.pc() + 8)
    assert d % 4 == 0 and -(1 << 25) <= d < (1 << 25)
    a.w(0xEB000000 | ((d >> 2) & 0xFFFFFF), "bl #0x%x" % ziel)


def warte(a, name):
    a.w(dp("mov", 3, 0, WARTE), "mov r3, #0x%x" % WARTE)
    a.lab(name)
    a.w(0xE2533001, "subs r3, r3, #1")
    a.b("ne", name, "bne")


def probe():
    a = Asm(PROBE)
    a.w(0xE92D0000 | regs(4, 5, 14), "push {r4, r5, lr}")
    a.ldr_lit(2, vw.USBD_BA, "ldr r2, [pc, #")
    a.w(ldr(3, 0, 0), "ldr r3, [r0]")
    a.w(dp("add", 3, 3, 1), "add r3, r3, #1")
    a.w(str_(3, 0, 0), "str r3, [r0]")
    a.ldr_lit(3, TICK, "ldr r3, [pc, #")
    a.w(ldr(3, 3, 0), "ldr r3, [r3]")
    a.w(str_(3, 0, 4), "str r3, [r0, #4]")
    a.w(ldr(3, 2, USB_IRQ_STAT), "ldr r3, [r2, #0x10]")
    a.w(str_(3, 0, 8), "str r3, [r0, #8]")
    a.w(ldr(3, 2, USB_IRQ_ENB), "ldr r3, [r2, #0x14]")
    a.w(str_(3, 0, 0xC), "str r3, [r0, #0xc]")
    a.ldr_lit(3, vw.PHY_CTL, "ldr r3, [pc, #")
    a.w(ldr(3, 3, 0), "ldr r3, [r3]")
    a.w(str_(3, 0, 0x10), "str r3, [r0, #0x10]")
    a.ldr_lit(3, AHBCLK, "ldr r3, [pc, #")
    a.w(ldr(3, 3, 0), "ldr r3, [r3]")
    a.w(str_(3, 0, 0x14), "str r3, [r0, #0x14]")
    a.w(ldr(3, 2, USB_OPER), "ldr r3, [r2, #0x18]")
    a.w(str_(3, 0, 0x18), "str r3, [r0, #0x18]")
    a.w(ldr(4, 2, EPA_MPS), "ldr r4, [r2, #0x78]")
    a.w(str_(4, 0, 0x1C), "str r4, [r0, #0x1c]")
    a.w(dp("cmp", 0, 4, 0x20), "cmp r4, #0x20")
    a.w(dp("mov", 5, 0, 0x40, "eq"), "moveq r5, #0x40")
    a.w(dp("mov", 5, 0, 0x20, "ne"), "movne r5, #0x20")
    a.w(str_(5, 0, 0x20), "str r5, [r0, #0x20]")
    a.w(str_(5, 2, EPA_MPS), "str r5, [r2, #0x78]")
    a.w(ldr(3, 2, EPA_MPS), "ldr r3, [r2, #0x78]")
    a.w(str_(3, 0, 0x24), "str r3, [r0, #0x24]")
    warte(a, "w1")
    a.w(ldr(3, 2, EPA_MPS), "ldr r3, [r2, #0x78]")
    a.w(str_(3, 0, 0x28), "str r3, [r0, #0x28]")
    a.w(str_(4, 2, EPA_MPS), "str r4, [r2, #0x78]")
    warte(a, "w2")
    a.w(ldr(3, 2, EPA_MPS), "ldr r3, [r2, #0x78]")
    a.w(str_(3, 0, 0x2C), "str r3, [r0, #0x2c]")
    a.w(str_(1, 0, 0x38), "str r1, [r0, #0x38]")
    a.w(dp("cmp", 0, 1, 0), "cmp r1, #0")
    a.b("eq", "ende", "beq")
    a.w(dp("mov", 3, 0, 0x100), "mov r3, #0x100")
    a.w(str_(3, 2, USB_IRQ_STAT), "str r3, [r2, #0x10]")
    a.w(ldr(3, 2, USB_IRQ_STAT), "ldr r3, [r2, #0x10]")
    a.w(str_(3, 0, 0x30), "str r3, [r0, #0x30]")
    warte(a, "w3")
    a.w(ldr(3, 2, USB_IRQ_STAT), "ldr r3, [r2, #0x10]")
    a.w(str_(3, 0, 0x34), "str r3, [r0, #0x34]")
    a.lab("ende")
    a.ldr_lit(3, MAGIC, "ldr r3, [pc, #")
    a.w(str_(3, 0, 0x3C), "str r3, [r0, #0x3c]")
    a.w(0xE8BD0000 | regs(4, 5, 15), "pop {r4, r5, pc}")
    return a.fertig()


def w1(ziel=ur.HANDLER):
    a = Asm(W1)
    a.w(PUSH, T_PUSH)
    a.ldr_lit(0, vw.PHY_CTL, "ldr r0, [pc, #")
    a.w(ldr(0, 0, 0), "ldr r0, [r0]")
    a.w(dp("tst", 0, 0, 0x80000000), "tst r0, #0x80000000")
    a.b("ne", "normal", "bne")
    a.ldr_lit(0, vw.VBUS_STATUS, "ldr r0, [pc, #")
    a.w(0xE5D00000, "ldrb r0, [r0]")
    a.w(dp("cmp", 0, 0, 0), "cmp r0, #0")
    a.b("ne", "normal", "bne")
    a.ldr_lit(0, vw.USBD_BA, "ldr r0, [pc, #")
    a.w(ldr(1, 0, 0x10), "ldr r1, [r0, #0x10]")
    a.w(ldr(2, 0, 0x14), "ldr r2, [r0, #0x14]")
    a.w(0xE0011002, "and r1, r1, r2")
    a.w(dp("tst", 0, 1, 0x100), "tst r1, #0x100")
    a.b("eq", "normal", "beq")
    a.ldr_lit(0, vw.AIC_MDCR, "ldr r0, [pc, #")
    a.w(dp("mov", 1, 0, vw.IRQ_USB), "mov r1, #0x10000")
    a.w(str_(1, 0, 0), "str r1, [r0]")
    a.ldr_lit(0, WACHT, "ldr r0, [pc, #")
    a.w(dp("mov", 1, 0, 1), "mov r1, #1")
    a.w(str_(1, 0, 0), "str r1, [r0]")
    a.w(ldr(1, 0, 4), "ldr r1, [r0, #4]")
    a.w(dp("add", 1, 1, 1), "add r1, r1, #1")
    a.w(str_(1, 0, 4), "str r1, [r0, #4]")
    a.w(dp("mov", 1, 0, 0), "mov r1, #0")
    a.w(str_(1, 0, TICKS), "str r1, [r0, #0xc]")
    a.w(dp("add", 0, 0, SPERRE), "add r0, r0, #0x%x" % SPERRE)
    a.w(dp("mov", 1, 0, 1), "mov r1, #1")
    bl(a, PROBE)
    a.w(POP, T_POP)
    a.w(0xE12FFF1E, "bx lr")
    a.lab("normal")
    a.w(POP, T_POP)
    a.b("", ziel, "b #0x%x" % ziel)
    return a.fertig()


def w2(ziel=rp.HANDLER):
    a = Asm(W2)
    a.w(PUSH, T_PUSH)
    a.ldr_lit(0, WACHT, "ldr r0, [pc, #")
    a.w(ldr(1, 0, 0), "ldr r1, [r0]")
    a.w(dp("cmp", 0, 1, 0), "cmp r1, #0")
    a.b("eq", "frei", "beq")
    a.ldr_lit(1, vw.PHY_CTL, "ldr r1, [pc, #")
    a.w(ldr(1, 1, 0), "ldr r1, [r1]")
    a.w(dp("tst", 0, 1, 0x80000000), "tst r1, #0x80000000")
    a.b("ne", "anstecken", "bne")
    # gesperrt, Kabel weg
    a.w(ldr(1, 0, TICKS), "ldr r1, [r0, #0xc]")
    a.w(dp("add", 1, 1, 1), "add r1, r1, #1")
    a.w(str_(1, 0, TICKS), "str r1, [r0, #0xc]")
    a.w(dp("cmp", 0, 1, SPAET_TICKS), "cmp r1, #0x%x" % SPAET_TICKS)
    a.b("ne", "weiter", "bne")
    a.w(dp("add", 0, 0, SPAET), "add r0, r0, #0x%x" % SPAET)
    a.w(dp("mov", 1, 0, 1), "mov r1, #1")
    bl(a, PROBE)
    a.b("", "weiter", "b")
    # gesperrt, Kabel wieder da
    a.lab("anstecken")
    a.w(dp("add", 0, 0, AN0), "add r0, r0, #0x%x" % AN0)
    a.w(dp("mov", 1, 0, 0), "mov r1, #0")
    bl(a, PROBE)
    a.ldr_lit(0, WACHT, "ldr r0, [pc, #")
    a.w(dp("mov", 1, 0, 0), "mov r1, #0")
    a.w(str_(1, 0, 0), "str r1, [r0]")
    a.w(ldr(1, 0, 8), "ldr r1, [r0, #8]")
    a.w(dp("add", 1, 1, 1), "add r1, r1, #1")
    a.w(str_(1, 0, 8), "str r1, [r0, #8]")
    a.w(dp("mov", 1, 0, AN1_TICKS), "mov r1, #0x%x" % AN1_TICKS)
    a.w(str_(1, 0, COUNTDOWN), "str r1, [r0, #0x10]")
    a.ldr_lit(0, vw.AIC_MECR, "ldr r0, [pc, #")
    a.w(dp("mov", 1, 0, vw.IRQ_USB), "mov r1, #0x10000")
    a.w(str_(1, 0, 0), "str r1, [r0]")
    a.b("", "weiter", "b")
    # frei: Countdown der Positivkontrolle
    a.lab("frei")
    a.w(ldr(1, 0, COUNTDOWN), "ldr r1, [r0, #0x10]")
    a.w(dp("cmp", 0, 1, 0), "cmp r1, #0")
    a.b("eq", "weiter", "beq")
    a.w(dp("sub", 1, 1, 1), "sub r1, r1, #1")
    a.w(str_(1, 0, COUNTDOWN), "str r1, [r0, #0x10]")
    a.w(dp("cmp", 0, 1, 0), "cmp r1, #0")
    a.b("ne", "weiter", "bne")
    a.w(dp("add", 0, 0, AN1), "add r0, r0, #0x%x" % AN1)
    a.w(dp("mov", 1, 0, 0), "mov r1, #0")
    bl(a, PROBE)
    a.lab("weiter")
    a.w(POP, T_POP)
    a.b("", ziel, "b #0x%x" % ziel)
    return a.fertig()


def sektoren():
    """-> (Sektor 0x275800, Sektor 0x275A00, Fehlerzahl der capstone-Pruefung)."""
    cp, c1, c2 = probe(), w1(), w2()
    f = 0
    for name, code, basis in (("PROBE", cp, PROBE), ("W1", c1, W1), ("W2", c2, W2)):
        print("%s 0x%X, %d Worte:" % (name, basis, len(code)))
        f += vw.pruefen(code, basis)
    bp, b1, b2 = (b"".join(struct.pack("<I", c[0]) for c in code) for code in (cp, c1, c2))
    assert len(bp) <= 512 and W1 + len(b1) <= W2 and W2 + len(b2) <= W1 + 512
    assert WACHT + AN1 + SATZ <= 0x2D8000
    s8 = bp + b"\x00" * (512 - len(bp))
    sa = bytearray(512)
    sa[0:len(b1)] = b1
    sa[W2 - W1:W2 - W1 + len(b2)] = b2
    return s8, bytes(sa), f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default=dauer.APP)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="/dev/sdX")
    a = ap.parse_args()

    orig = open(a.app, "rb").read()
    if hashlib.sha256(orig).hexdigest() != dauer.APP_SHA:
        sys.exit("APP.bin ist nicht die erwartete")
    end = open(os.path.join(END, "APP.vbus_waechter_end.bin"), "rb").read()
    v, md5, _ = pw.pruefwert(end)
    if len(end) != L or v != 0 or md5 != end[pw.K:pw.K + 16]:
        sys.exit("Endstand hat keinen passenden MD5-Kopf")
    wort = lambda va: struct.unpack_from("<I", end, va - dauer.VA0)[0]
    if wort(ur.POOL) != W1 or wort(rp.POOL) != W2:
        sys.exit("Poolworte des Endstands zeigen nicht auf W1/W2")
    alt = {s: open(os.path.join(END, "sektor_%06x.neu" % s), "rb").read() for s in (0x275600, 0x275800, 0x275A00)}
    leer = b"\x00" * 512
    assert alt[0x275600] == leer and alt[0x275800] == leer, "Ring-Sektoren im Endstand nicht leer"

    s8, sa, f = sektoren()
    if f:
        sys.exit("Befehle stimmen nicht -- nichts erzeugt")
    neu = {0x275800: s8, 0x275A00: sa}

    os.makedirs(a.out, exist_ok=True)
    for s, inhalt in neu.items():
        open(os.path.join(a.out, "sektor_%06x.neu" % s), "wb").write(inhalt)
    raw = lambda x: (dauer.RAW_APP >> 9) + x // 512
    h = lambda b: hashlib.sha256(b).hexdigest()
    n_sek = (L + 511) // 512
    bild_sha = ('dd if=$DEV bs=512 skip=%d count=%d iflag=direct status=none | head -c %d | sha256sum | cut -d" " -f1'
                % (dauer.RAW_APP >> 9, n_sek, L))
    lies = 'dd if=$DEV bs=512 skip=%d count=1 iflag=direct status=none | sha256sum | cut -d" " -f1'
    z = ["#!/bin/bash", "set -e",
         "# Erzeugt von patch_vbus_taktprobe.py (CL-USB-REC-131). Messstand Taktprobe. NUR Testkarte.",
         "# Ausgangsstand: Endstand vbus_waechter_end (Kopf %s). Geschrieben werden nur Datei 0x275800 und 0x275A00."
         % md5.hex(),
         "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"',
         'echo "Ziel: $DEV -- lese Imagebereich (%d Sektoren ab %d)"' % (n_sek, dauer.RAW_APP >> 9),
         "IST=$(%s)" % bild_sha,
         '[ "$IST" = %s ] || { echo "Imagebereich ist nicht der Endstand vbus_waechter_end -- Abbruch, nichts geschrieben."; exit 1; }'
         % h(end),
         'S=$(%s)' % (lies % raw(0x275600)),
         '[ "$S" = %s ] || { echo "Sektor Datei 0x275600 nicht leer -- Abbruch, nichts geschrieben."; exit 1; }' % h(leer),
         "FERTIG=0"]
    for s in sorted(neu):
        z += ['S=$(%s)' % (lies % raw(s)),
              'case "$S" in',
              '  %s) FERTIG=$((FERTIG+1));;' % h(neu[s]),
              '  %s) ;;' % h(alt[s]),
              '  *) echo "Sektor Datei 0x%X weder Endstand noch Messstand -- Abbruch, nichts geschrieben."; exit 1;;' % s,
              'esac']
    z += ['[ $FERTIG = %d ] && { echo "Messstand Taktprobe ist schon drauf -- nichts zu tun"; exit 0; }' % len(neu),
          '[ $FERTIG = 0 ] || { echo "Nur ein Teil des Messstands drauf -- erst ./zurueck.sh"; exit 1; }',
          'read -p "Sicherung anlegen und %d Sektoren (Datei 0x275800, 0x275A00) schreiben? [j/N] " x; [ "$x" = j ] || exit 1'
          % len(neu),
          'mkdir -p sicherung']
    for s in sorted(neu):
        z.append('[ -e sicherung/sektor_%06x ] || dd if=$DEV of=sicherung/sektor_%06x bs=512 skip=%d count=1 iflag=direct status=none'
                 % (s, s, raw(s)))
    for s in sorted(neu):                    # PROBE zuerst, dann W1/W2, die sie rufen
        z.append("dd if=sektor_%06x.neu of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none" % (s, raw(s)))
    z += ["sync", "IST=$(%s)" % bild_sha,
          '[ "$IST" = %s ] || { echo "Ruecklesen Imagebereich weicht ab -- ./zurueck.sh"; exit 1; }' % h(end)]
    for s in sorted(neu):
        z += ['S=$(%s)' % (lies % raw(s)),
              '[ "$S" = %s ] || { echo "Ruecklesen Sektor Datei 0x%X weicht ab -- ./zurueck.sh"; exit 1; }' % (h(neu[s]), s)]
    z += ['echo "fertig, rueckgelesen -- Messstand Taktprobe drauf; zurueck in den Endstand mit ./zurueck.sh"', ""]
    p = os.path.join(a.out, "patch.sh")
    open(p, "w").write("\n".join(z)); os.chmod(p, 0o755)
    zz = ["#!/bin/bash", "set -e", "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"',
          '[ -e sicherung/sektor_275a00 ] && [ -e sicherung/sektor_275800 ] || { echo "keine Sicherung vorhanden"; exit 1; }',
          'read -p "Sicherung zurueckschreiben (Endstand vbus_waechter_end)? [j/N] " x; [ "$x" = j ] || exit 1']
    for s in sorted(neu, reverse=True):      # W1/W2 zuerst zurueck, dann PROBE
        zz.append("dd if=sicherung/sektor_%06x of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none"
                  % (s, raw(s)))
    zz.append("sync")
    for s in sorted(neu):
        zz += ['S=$(%s)' % (lies % raw(s)),
               '[ "$S" = %s ] || { echo "Ruecklesen Sektor Datei 0x%X weicht vom Endstand ab"; exit 1; }' % (h(alt[s]), s)]
    zz += ['echo "zurueck im Endstand vbus_waechter_end"', ""]
    p = os.path.join(a.out, "zurueck.sh")
    open(p, "w").write("\n".join(zz)); os.chmod(p, 0o755)
    print("Sektoren: Datei 0x275800 = Karte %d (PROBE), Datei 0x275A00 = Karte %d (W1/W2); Imagebereich und Kopf %s unveraendert"
          % (raw(0x275800), raw(0x275A00), md5.hex()))


if __name__ == "__main__":
    main()
