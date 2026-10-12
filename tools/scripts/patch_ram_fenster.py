#!/usr/bin/env python3
"""RAM-Fenster: Diagnosepatch, der den Geraete-RAM ueber das USB-Laufwerk lesbar macht.

Zweck (CL-USB-REC-126): Im Stillstand nach Kabelstecken laufen Hauptschleife
und MSC-Pumpe weiter (der PC liest per dd), aber Uhr und Touch sind tot. Statt
am Dekompilat zu raten, wird der Zustand gelesen: Tick 0xC18, Uhr-Zeitstempel
0x550, Uhrpuffer 0xCE4, Ereignis-Warteschlange 0x41378+0x44 usw.

Mechanik: usb_lun_read_blocks (0x74998) hat genau zwei Aufrufer, beide in
mscdRd10_Command: 0xD0460 und 0xD04E4 (Xref). Beide bl werden auf ram_stub
umgelenkt:
    ram_stub(r0=lba, r1=blocks, r2=buf, r3):
      k = lba - MARKE; liegt k nicht in [0, RAM_BLOECKE) -> b 0x74998 (Karte)
      sonst: kopiere blocks*512 Byte ab RAM k*512 nach buf (wortweise, Ende bei
      RAM_ENDE gekappt), FUN_000f9aa4(8) (D-Cache clean+invalidate,
      I-Cache invalidate, Drain -- wie usb_lun_read_blocks selbst), return 0
mscdRd10_Command liest den Rueckgabewert nicht (0xD0464/0xD04E8 laden r0 neu).
Schreiben (usb_lun_write_blocks) bleibt unberuehrt. LBA 0x10000.. liegt hinter
der Dokumentablage (100 Slots * 0x4D000 enden bei LBA 0xF0A0) und unter der
gemeldeten Groesse 131072 Bloecke (CL-USB-REC-120).

Baut auf patch_usb_dauerbetrieb.py auf: der Stub liegt im selben Sektor
(Datei 0x275400) hinter dessen Stubs (0x2CD400..0x2CD463). Der neue Inhalt
dieses Sektors ist: Geraetesicherung des Sektors (Karteninhalt vor dem
Dauerbetrieb) + Dauerbetrieb-Stubs + RAM-Stub, also volle 512 Byte.

Positivkontrolle nach dem Aufbringen: RAM 0x9F8 = MSC_DeviceDescriptor
12 01 00 02 00 00 00 40 16 04 93 00 (CL-USB-REC-127); ram_fenster_lesen.py
prueft das bei jedem Aufruf mit --kontrolle.

  python3 tools/scripts/patch_ram_fenster.py --out <dir> --device /dev/sdX
Es wird nichts auf ein Geraet geschrieben; patch.sh/zurueck.sh erst nach Rueckfrage.
"""
import argparse
import hashlib
import os
import struct
import sys

import capstone

import patch_usb_dauerbetrieb as dauer

HIER = os.path.dirname(os.path.abspath(__file__))
SICHERUNG_275400 = os.path.join(HIER, "..", "..", "research", "phase_a_sd_analysis", "artifacts",
                                "usb_dauerbetrieb", "sektor_275400.sicherung")

VA0, RAW_APP = dauer.VA0, dauer.RAW_APP
LUN_LESEN = 0x74998
CACHE = 0xF9AA4                    # FUN_000f9aa4(8): clean+inv D, inv I, drain
AUFRUFE = (0xD0460, 0xD04E4)       # bl usb_lun_read_blocks in mscdRd10_Command
STUB_VA = 0x2CD480                 # hinter den Dauerbetrieb-Stubs, selber Sektor
MARKE = 0x10000                    # erste Host-LBA des Fensters
RAM_ENDE = 0x800000                # SDRAM 8 MiB, Stapel enden hier (CL-BOOT-REC-114)
RAM_BLOECKE = RAM_ENDE // 512      # 0x4000


def stub_worte():
    """(va, wort, soll-text) des RAM-Stubs; Rueckfall auf die Karte bei +0x50."""
    a = STUB_VA
    ruck = a + 0x50
    t = [
        (0x00, 0xE250C801, "subs ip, r0, #0x10000"),
        (0x04, dauer.b_cond(0x3, a + 0x04, ruck), "blo #0x%x" % ruck),
        (0x08, 0xE35C0901, "cmp ip, #0x4000"),
        (0x0C, dauer.b_cond(0x2, a + 0x0C, ruck), "bhs #0x%x" % ruck),
        (0x10, 0xE92D4010, "push {r4, lr}"),
        (0x14, 0xE1A0048C, "lsl r0, ip, #9"),
        (0x18, 0xE1A01481, "lsl r1, r1, #9"),
        (0x1C, 0xE0803001, "add r3, r0, r1"),
        (0x20, 0xE3530502, "cmp r3, #0x800000"),
        (0x24, 0x82601502, "rsbhi r1, r0, #0x800000"),
        (0x28, 0xE3510000, "cmp r1, #0"),
        (0x2C, 0xDA000003, "ble #0x%x" % (a + 0x40)),
        (0x30, 0xE4903004, "ldr r3, [r0], #4"),
        (0x34, 0xE4823004, "str r3, [r2], #4"),
        (0x38, 0xE2511004, "subs r1, r1, #4"),
        (0x3C, 0xCAFFFFFB, "bgt #0x%x" % (a + 0x30)),
        (0x40, 0xE3A00008, "mov r0, #8"),
        (0x44, dauer.bl(a + 0x44, CACHE), "bl #0x%x" % CACHE),
        (0x48, 0xE3A00000, "mov r0, #0"),
        (0x4C, 0xE8BD8010, "pop {r4, pc}"),
        (0x50, 0xEA000000 | (((LUN_LESEN - (ruck + 8)) >> 2) & 0xFFFFFF), "b #0x%x" % LUN_LESEN),
    ]
    return [(a + o, w, x) for o, w, x in t]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default=dauer.APP)
    ap.add_argument("--sicherung", default=SICHERUNG_275400,
                    help="Geraetesicherung des Sektors Datei 0x275400 vor dem Dauerbetrieb")
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="/dev/sdX")
    a = ap.parse_args()

    orig = open(a.app, "rb").read()
    if hashlib.sha256(orig).hexdigest() != dauer.APP_SHA:
        sys.exit("APP.bin ist nicht die erwartete")
    sicherung = open(a.sicherung, "rb").read()
    assert len(sicherung) == 512

    def off(va):
        return va - VA0

    # Sektor 0x275400 heute auf dem Geraet = Sicherung + Dauerbetrieb-Stubs (erste 100 Byte)
    w_dauer, merker, _ = dauer.stubs()
    s_basis = 0x275400
    heute = bytearray(sicherung)
    for va, wort, _ in w_dauer:
        struct.pack_into("<I", heute, off(va) - s_basis, wort)
    neu_stub = bytearray(heute)
    belegt = {off(va) - s_basis for va, _, _ in w_dauer}
    w_ram = stub_worte()
    for va, wort, _ in w_ram:
        o = off(va) - s_basis
        assert 0 <= o <= 508 and o not in belegt, hex(va)
        assert heute[o:o + 4] == sicherung[o:o + 4]
        struct.pack_into("<I", neu_stub, o, wort)
    assert STUB_VA > merker + 4

    # Aufrufstellen
    s_bl = off(AUFRUFE[0]) // 512 * 512
    assert all(off(v) // 512 * 512 == s_bl for v in AUFRUFE)
    alt_bl = orig[s_bl:s_bl + 512]
    neu_bl = bytearray(alt_bl)
    for v in AUFRUFE:
        ist = struct.unpack_from("<I", orig, off(v))[0]
        if ist != dauer.bl(v, LUN_LESEN):
            sys.exit("0x%X: 0x%08X statt bl 0x%X" % (v, ist, LUN_LESEN))
        struct.pack_into("<I", neu_bl, off(v) - s_bl, dauer.bl(v, STUB_VA))

    # Ruecklesen mit capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
    norm = lambda s: (s.replace("stmdb sp!, ", "push ").replace("ldm sp!, ", "pop ")
                      .replace("mov r0, ip, lsl #9", "lsl r0, ip, #9")
                      .replace("mov r1, r1, lsl #9", "lsl r1, r1, #9")
                      .replace("bcc ", "blo ").replace("bcs ", "bhs ")
                      .replace("lo #", "lo #").replace("r12", "ip"))
    fehler = 0
    pruef = [(v, dauer.bl(v, STUB_VA), "bl #0x%x" % STUB_VA) for v in AUFRUFE] + w_ram
    for va, w, soll in pruef:
        ins = list(md.disasm(struct.pack("<I", w), va))
        ist = ("%s %s" % (ins[0].mnemonic, ins[0].op_str)).strip() if ins else "?"
        ok = norm(ist) == norm(soll)
        print("  %s 0x%08X  %08X  %-28s %s" % ("ok " if ok else "XX ", va, w, ist, "" if ok else "soll: " + soll))
        fehler += not ok
    if fehler:
        sys.exit("%d Befehle stimmen nicht -- nichts erzeugt" % fehler)

    os.makedirs(a.out, exist_ok=True)
    sek = [(s_bl, bytes(alt_bl), bytes(neu_bl)), (s_basis, bytes(heute), bytes(neu_stub))]
    zeilen = ["#!/bin/bash", "set -e",
              "# Erzeugt von patch_ram_fenster.py (CL-USB-REC-126). NUR Testkarte, Dauerbetrieb muss drauf sein.",
              "DEV=%s" % a.device, 'cd "$(dirname "$0")"']
    for s, alt, neu in sek:
        raw = (RAW_APP >> 9) + s // 512
        open(os.path.join(a.out, "sektor_%06x.neu" % s), "wb").write(neu)
        zeilen.append('IST=$(dd if=$DEV bs=512 skip=%d count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)' % raw)
        zeilen.append('case "$IST" in %s|%s) ;; *) echo "Datei-Sektor 0x%X unerwartet -- Abbruch"; exit 1;; esac'
                      % (hashlib.sha256(alt).hexdigest(), hashlib.sha256(neu).hexdigest(), s))
    zeilen.append('read -p "Sicherung anlegen und %d Sektoren schreiben? [j/N] " x; [ "$x" = j ] || exit 1' % len(sek))
    for s, _, _ in sek:
        zeilen.append('[ -e sektor_%06x.sicherung ] || dd if=$DEV of=sektor_%06x.sicherung bs=512 skip=%d count=1 iflag=direct status=none'
                      % (s, s, (RAW_APP >> 9) + s // 512))
    for s, _, _ in sek:
        zeilen.append("dd if=sektor_%06x.neu of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none"
                      % (s, (RAW_APP >> 9) + s // 512))
    zeilen += ["sync", 'echo "fertig -- zurueck mit ./zurueck.sh (stellt den Dauerbetrieb-Stand her)"', ""]
    p = os.path.join(a.out, "patch.sh")
    open(p, "w").write("\n".join(zeilen)); os.chmod(p, 0o755)
    z = ["#!/bin/bash", "set -e", "DEV=%s" % a.device, 'cd "$(dirname "$0")"',
         'read -p "Sicherung zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1']
    for s, _, _ in sek:
        z.append("dd if=sektor_%06x.sicherung of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none"
                 % (s, (RAW_APP >> 9) + s // 512))
    z += ["sync", 'echo "zurueck"', ""]
    p = os.path.join(a.out, "zurueck.sh")
    open(p, "w").write("\n".join(z)); os.chmod(p, 0o755)
    print("RAM-Stub 0x%X..0x%X, Aufrufe %s -> Stub" % (STUB_VA, w_ram[-1][0] + 3, ", ".join("0x%X" % v for v in AUFRUFE)))
    print("Sektoren (Datei): %s" % ", ".join("0x%X" % s for s, _, _ in sek))
    print("Fenster: Host-LBA 0x%X + (RAM-Adresse / 512), %d Bloecke = RAM 0x0..0x%X" % (MARKE, RAM_BLOECKE, RAM_ENDE - 1))


if __name__ == "__main__":
    main()
