#!/usr/bin/env python3
"""Ring im USB-Interrupt: welche UDC-Quelle haelt die CPU nach dem Abziehen fest? (CL-USB-REC-128)

Befund davor (2026-10-15): Waehrend des Stillstands kommen keine TMR1-Interrupts
(dem Tick fehlen 10,5 s bei 10 s ohne Kabel), und usbd_isr hat die hoehere
AIC-Prioritaet (sysInstallISR(1, 16, usbd_isr) bei 0x1078C8, TMR1 mit 2).
Kandidat: eine UDC-Quelle bleibt anhaengig, usbd_isr wird ununterbrochen gerufen.

Einhaengen wie patch_ringpuffer.py: usbd_isr 0x109AC4 steht als Poolwort nur
bei 0x10799C (Bytesuche), geladen nur bei 0x1078C0. Das Wort zeigt nach dem
Patch auf den Stub; der springt am Ende mit unveraendertem lr in usbd_isr.

Stub (VA 0x2CD800, Datei 0x275800, eigener Sektor), je Eintritt:
  Kopf beim ersten Mal anlegen (Magic 'USBR'), Eintritte gesamt +1
  VBUS da (PHY_CTL Bit 31): Zustand = 0, Eintritte mit VBUS +1
  VBUS weg: beim Uebergang neue Episode (Zaehler +1, n = 0); Eintrag mit 8 Worten
    PC (lr_irq - 4), IRQ_STAT_L (+0), IRQ_ENB_L (+8), USB_IRQ_STAT (+0x10),
    USB_IRQ_ENB (+0x14), PHY_CTL (+0x704), TISR (MMIO 0xB8002018: Bit 1 =
    TMR1 anhaengig), TDR1 (0xB8002014, Zaehlerstand im 1-ms-Takt)
    A: die ersten 256 Eintritte der Episode; B: Ring der letzten 256; n += 1
  dann b 0x109AC4
Alle Lesezugriffe sind reine Reads; die UDC-Statusregister loeschen per
Schreiben einer 1, nicht per Lesen.

Puffer (RAM): KOPF 0x2D2000 (+0 Magic, +4 Zustand, +8 Episoden, +0xC n,
+0x10 Eintritte gesamt, +0x14 mit VBUS), A 0x2D2100..0x2D4100,
B 0x2D4100..0x2D6100. Liegt im BOOT-Ladebereich: ein Neustart (Watchdog nach
22,4 s) loescht ihn -- also vor 20 s wieder stecken und lesen.
Lesen: tools/scripts/usb_isr_ring_lesen.py.

Basis ist der Kartenstand nach md5_kopf_3 (Ruecklese- und Ringpuffer-Patch drauf).
Danach den Kopf nachziehen:
  python3 tools/scripts/patch_md5_kopf.py --image <out>/APP.usb_isr_ring.bin --out <dir2>
Reihenfolge an der Karte: <out>/patch.sh, dann <dir2>/patch.sh; zurueck umgekehrt.

  python3 tools/scripts/patch_usb_isr_ring.py --out <dir> [--device /dev/sdX] [--basis ABBILD]
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
from patch_ringpuffer import Asm, ldr, str_, dp, regs

HIER = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HIER, "..", "..", "research", "phase_a_sd_analysis", "artifacts")
BASIS = os.path.join(ART, "md5_kopf_3", "APP.md5kopf.bin")

POOL, LADER = 0x10799C, 0x1078C0       # sysInstallISR(1, 0x10, [POOL])
HANDLER = 0x109AC4                     # usbd_isr (IRQ 16)
STUB = 0x2CD800                        # Datei 0x275800
KOPF, PUF_A, PUF_B = 0x2D2000, 0x2D2100, 0x2D4100
EINTRAG = 32
MAGIC = 0x52425355                     # 'USBR'
USBD_BA, PHY_CTL, TMR_BA = 0xB1008000, 0xB1008704, 0xB8002000
LR_OFF = rp.LR_OFF                     # gleicher Verteiler, gleicher push


def stub():
    a = Asm(STUB)
    a.w(0xE92D0000 | regs(0, 1, 2, 3, 4, 5, 6, 7, 8, 14), "push {r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}")
    a.ldr_lit(4, KOPF, "ldr r4, [pc, #")
    a.w(ldr(1, 4, 0), "ldr r1, [r4]")
    a.ldr_lit(2, MAGIC, "ldr r2, [pc, #")
    a.w(0xE1510002, "cmp r1, r2")
    a.b("eq", "init_ok", "beq")
    a.w(dp("mov", 3, 0, 0), "mov r3, #0")
    for o in range(4, 0x18, 4):
        a.w(str_(3, 4, o), "str r3, [r4, #%s]" % (o if o < 10 else "0x%x" % o))
    a.w(str_(2, 4, 0), "str r2, [r4]")
    a.lab("init_ok")
    a.w(ldr(1, 4, 0x10), "ldr r1, [r4, #0x10]")
    a.w(dp("add", 1, 1, 1), "add r1, r1, #1")
    a.w(str_(1, 4, 0x10), "str r1, [r4, #0x10]")
    a.ldr_lit(8, PHY_CTL, "ldr r8, [pc, #")
    a.w(ldr(5, 8, 0), "ldr r5, [r8]")
    a.w(dp("tst", 0, 5, 0x80000000), "tst r5, #0x80000000")
    a.b("eq", "vbus_aus", "beq")
    a.w(dp("mov", 1, 0, 0), "mov r1, #0")
    a.w(str_(1, 4, 4), "str r1, [r4, #4]")
    a.w(ldr(1, 4, 0x14), "ldr r1, [r4, #0x14]")
    a.w(dp("add", 1, 1, 1), "add r1, r1, #1")
    a.w(str_(1, 4, 0x14), "str r1, [r4, #0x14]")
    a.b("", "ende", "b")
    a.lab("vbus_aus")
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
    a.lab("lauf")
    a.w(ldr(6, 4, 0xC), "ldr r6, [r4, #0xc]")
    a.w(dp("add", 1, 6, 1), "add r1, r6, #1")
    a.w(str_(1, 4, 0xC), "str r1, [r4, #0xc]")
    # Eintrag in r0..r3 und r5..r8 sammeln (r5 = PHY_CTL schon geladen)
    a.ldr_lit(7, USBD_BA, "ldr r7, [pc, #")
    a.w(ldr(0, 13, LR_OFF), "ldr r0, [sp, #0x%x]" % LR_OFF)
    a.w(dp("sub", 0, 0, 4), "sub r0, r0, #4")
    a.w(ldr(1, 7, 0x00), "ldr r1, [r7]")
    a.w(ldr(2, 7, 0x08), "ldr r2, [r7, #8]")
    a.w(ldr(3, 7, 0x10), "ldr r3, [r7, #0x10]")
    a.w(ldr(7, 7, 0x14), "ldr r7, [r7, #0x14]")
    a.ldr_lit(8, TMR_BA, "ldr r8, [pc, #")
    a.w(ldr(12, 8, 0x18), "ldr ip, [r8, #0x18]")
    a.w(ldr(8, 8, 0x14), "ldr r8, [r8, #0x14]")
    # Reihenfolge im Speicher: PC, STAT_L, ENB_L, USB_STAT, USB_ENB, PHY_CTL, TISR, TDR1
    # stm schreibt aufsteigend nach Registernummer -> erst r0-r3, dann {r5, r7, ip, r8} einzeln
    a.w(dp("and", 14, 6, 0xFF), "and lr, r6, #0xff")
    a.ldr_lit(4, PUF_B, "ldr r4, [pc, #")
    a.w(0xE084428E, "add r4, r4, lr, lsl #5")
    a.w(0xE884000F, "stm r4, {r0, r1, r2, r3}")
    a.w(0xE5847010, "str r7, [r4, #0x10]")
    a.w(0xE5845014, "str r5, [r4, #0x14]")
    a.w(0xE584C018, "str ip, [r4, #0x18]")
    a.w(0xE584801C, "str r8, [r4, #0x1c]")
    a.w(dp("cmp", 0, 6, 0x100), "cmp r6, #0x100")
    a.b("hs", "ende", "bhs")
    a.ldr_lit(4, PUF_A, "ldr r4, [pc, #")
    a.w(0xE0844286, "add r4, r4, r6, lsl #5")
    a.w(0xE884000F, "stm r4, {r0, r1, r2, r3}")
    a.w(0xE5847010, "str r7, [r4, #0x10]")
    a.w(0xE5845014, "str r5, [r4, #0x14]")
    a.w(0xE584C018, "str ip, [r4, #0x18]")
    a.w(0xE584801C, "str r8, [r4, #0x1c]")
    a.lab("ende")
    a.w(0xE8BD0000 | regs(0, 1, 2, 3, 4, 5, 6, 7, 8, 14), "pop {r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}")
    a.b("", HANDLER, "b #0x%x" % HANDLER)
    return a.fertig()


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
    if struct.unpack_from("<I", b, rp.POOL - dauer.VA0)[0] != rp.STUB:
        sys.exit("Basis traegt den TMR1-Ringpuffer nicht -- erwartet ist der Stand md5_kopf_3")

    o = POOL - dauer.VA0
    if struct.unpack_from("<I", b, o)[0] != HANDLER:
        sys.exit("Poolwort 0x%X ist nicht 0x%X" % (POOL, HANDLER))
    w = struct.unpack_from("<I", b, LADER - dauer.VA0)[0]
    assert (w & 0xFFFFF000) == 0xE59F2000 and LADER + 8 + (w & 0xFFF) == POOL, hex(w)
    assert struct.unpack_from("<I", b, 0x1078C4 - dauer.VA0)[0] == 0xE3A01010      # mov r1, #0x10
    assert struct.unpack_from("<I", b, 0x1078C8 - dauer.VA0)[0] == 0xE3A00001      # mov r0, #1
    s = o // 512 * 512
    if b[s:s + 512] != orig[s:s + 512]:
        sys.exit("Sektor Datei 0x%X ist in der Basis schon veraendert" % s)

    code = stub()
    print("Stub 0x%X, %d Worte:" % (STUB, len(code)))
    rp.STUB, alt_stub = STUB, rp.STUB          # pruefen() rechnet Adressen relativ zu rp.STUB
    fehler = rp.pruefen(code)
    rp.STUB = alt_stub
    if fehler:
        sys.exit("Befehle stimmen nicht -- nichts erzeugt")
    stub_bytes = b"".join(struct.pack("<I", c[0]) for c in code)
    so = STUB - dauer.VA0
    assert so % 512 == 0 and so >= len(orig) and so + 512 <= dauer.APP_MAX and len(stub_bytes) <= 512
    assert STUB + len(stub_bytes) <= rp.KOPF                          # kollidiert nicht mit dem TMR1-Puffer
    assert rp.PUF_B + 256 * 16 <= KOPF and PUF_B + 256 * EINTRAG <= 0x2D8000

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
    open(os.path.join(a.out, "APP.usb_isr_ring.bin"), "wb").write(bild)
    leer = hashlib.sha256(b"\x00" * 512).hexdigest()
    sekt = [(s, b[s:s + 512], neu_pool), (so, None, neu_stub)]
    raw = lambda x: (dauer.RAW_APP >> 9) + x // 512
    lies = 'IST=$(dd if=$DEV bs=512 skip=%d count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)'
    z = ["#!/bin/bash", "set -e",
         "# Erzeugt von patch_usb_isr_ring.py (CL-USB-REC-128). NUR Testkarte.",
         "# Danach den MD5-Kopf mit dem patch.sh aus patch_md5_kopf.py --image APP.usb_isr_ring.bin nachziehen.",
         "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"', "FERTIG=0"]
    for x, alt, neu in sekt:
        alt_h = hashlib.sha256(alt).hexdigest() if alt else leer
        z += [lies % raw(x),
              'case "$IST" in',
              '  %s) FERTIG=$((FERTIG+1));;' % hashlib.sha256(neu).hexdigest(),
              '  %s) ;;' % alt_h,
              '  *) echo "Datei-Sektor 0x%X unerwartet -- Abbruch, nichts geschrieben."; exit 1;;' % x,
              'esac']
    z += ['[ $FERTIG = 2 ] && { echo "USB-ISR-Ring ist schon drauf -- nichts zu tun"; exit 0; }',
          'read -p "Sicherung anlegen und 2 Sektoren (Datei 0x%X, 0x%X) schreiben? [j/N] " x; [ "$x" = j ] || exit 1' % (s, so)]
    for x, _, _ in sekt:
        z.append('[ -e sektor_%06x.sicherung ] || dd if=$DEV of=sektor_%06x.sicherung bs=512 skip=%d count=1 iflag=direct status=none'
                 % (x, x, raw(x)))
    for x, _, neu in reversed(sekt):          # Stub zuerst, dann das Poolwort
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
    for x, _, _ in sekt:                      # Poolwort zuerst zurueck, dann der Stub
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
