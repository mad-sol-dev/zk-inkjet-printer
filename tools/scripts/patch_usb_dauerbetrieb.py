#!/usr/bin/env python3
"""USB-MSC ohne Setup -> USB: Entwurf und Patch-Erzeugung fuer CL-USB-REC-126.

Zweck: Das Geraet soll nach dem Start dauerhaft als USB-Massenspeicher am PC
haengen, damit ein Etikett von aussen in die Dokumentablage geschrieben werden
kann, waehrend der Drucker normal bedienbar bleibt. Dafuer werden die drei
Bausteine, die heute nur der Menuepunkt Setup -> USB benutzt (CL-USB-REC-109),
an andere Stellen gehaengt:

  (1) Start einmal beim Hochfahren -- nach dem Dokument-Startlader:
      ui_main_loop 0xC27FC  bl 0xB7228  ->  bl start_stub
      start_stub: r = 0xB7228(); wenn Merker==0: Merker=1, 0x8A75C(); return r
      0xB7228 ist der Startlader (CL-FIRMWARE-REC-116), 0x8A75C der Starter
      (udcOpen, mscdInit, mscdFlashInit, udcInit, mscdBlcokModeEnable(0),
      mscdMassEvent(0); CL-USB-REC-124). Der Merker ist noetig, weil
      ui_main_loop zwei Aufrufer hat (boot_init 0xB3248, ui_system_menu 0xC4708)
      und mscdInit bei jedem Lauf neu Puffer anfordert.

  (2) Pumpe in jeder Warteschleife:
      ui_event_wait 0x6A528  bl 0x8A7BC  ->  bl pumpe_stub
      pumpe_stub: 0x8A7BC() (Watchdog, unveraendert zuerst); r0..r3 sichern;
      0x8A7A8() = mscdMassEvent(0); r0..r3 zurueck
      Ohne wartenden CBW kehrt mscdMassBulk nach drei Flag-Pruefungen zurueck
      (dwCBW_flag setzt MSC_EPB_CallBack aus dem ISR; CL-USB-REC-126).

  (3) Menuepunkt Setup -> USB entschaerfen (FUN_000c0ef0):
      0xC0F4C  bl 0x8A75C  ->  nop     (kein zweiter Start)
      0xC1044  bl 0x8A790  ->  nop     (kein Abschalten beim Verlassen)
      Die eigene Pumpe der Menueschleife (0xC0F58) bleibt; doppelt pumpen ist
      harmlos. Der Rueckgabewert beider Aufrufe wird dort nicht benutzt
      (0xC0F50 laedt r9, 0xC1048 ueberschreibt r0).

Die Stubs liegen hinter dem Image in der Luecke 0x2CD22C..0x2D8000, die BOOT
fest mitlaedt und auf die kein Code zeigt (CL-FIRMWARE-REC-111) -- ab dem
ersten vollen Sektor 0x2CD400 (Datei 0x275400), damit der Sektor mit dem Ende
des komprimierten RW-Blocks (bis Datei 0x27522C) unberuehrt bleibt.

VORBEDINGUNG: das USB-Fenster muss schon auf der Ablage 0x28800000 liegen
(CL-USB-REC-119, patch_usb_window.py). Ohne das exportiert MSC das FAT-Volume
MINI, das die Firmware selbst benutzt -- zwei Herren auf einer FAT
(CL-USB-REC-115). patch.sh prueft das am Geraet und bricht sonst ab.
Unbestaetigt ist ausserdem CL-FIRMWARE-REC-111: dass Code hinter dem Image
ausgefuehrt wird. Ein Fehlstart zeigt sich sofort beim Booten; zurueck.sh
stellt alle Sektoren aus der Sicherung wieder her.

Jede Befehlsstelle wird vor dem Patch gegen das erwartete Wort geprueft, jedes
neue Wort mit capstone zurueckdisassembliert. Es wird nichts auf ein Geraet
geschrieben; patch.sh/zurueck.sh tun das erst nach Rueckfrage.

  python3 tools/scripts/patch_usb_dauerbetrieb.py --out <dir> --device /dev/sdX
"""
import argparse
import hashlib
import os
import struct
import sys

import capstone

HIER = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HIER, "..", "..", "firmware", "bin", "ZK-INKJET-NANO-APP.bin")
APP_SHA = "3be9028b01c0007aab9192877341918a0bc155beef55ac17e7e8f3bcc95151ea"
VA0 = 0x58000                      # Linkbasis (CL-BOOT-REC-113)
RAW_APP = 0x03000000               # APP.bin roh auf der Karte (CL-BOOT-REC-103)
APP_MAX = 0x280000                 # BOOT laedt fest so viel (CL-FIRMWARE-REC-111)
SCATTER_RW = (0x274B84, 0x27522C)  # Vektorkopie + komprimierter RW-Block (Datei)

# Fenster-Vorbedingung (CL-USB-REC-119)
FENSTER_ALT, FENSTER_NEU = 0x2A614000, 0x28800000
FENSTER_LITERALE = (0x1CA5C, 0x1CAAC)

# Ziele (VA)
STARTLADER = 0xB7228
STARTER = 0x8A75C
STOPPER = 0x8A790
WATCHDOG = 0x8A7BC
PUMPE = 0x8A7A8

STUB_VA = 0x2CD400                 # Datei 0x275400, erster voller Sektor der Luecke

NOP = 0xE1A00000                   # mov r0,r0


def bl(von, nach):
    d = nach - (von + 8)
    assert d % 4 == 0 and -(1 << 25) <= d < (1 << 25), (hex(von), hex(nach))
    return 0xEB000000 | ((d >> 2) & 0xFFFFFF)


def b_cond(cond, von, nach):
    d = nach - (von + 8)
    assert d % 4 == 0 and -(1 << 25) <= d < (1 << 25)
    return (cond << 28) | 0x0A000000 | ((d >> 2) & 0xFFFFFF)


def stubs():
    """Liefert (Liste (va, wort, soll-text), merker_va, pumpe_va)."""
    a = STUB_VA
    merker = a + 0x60
    pumpe = a + 0x40
    w = []

    def put(va, wort, text):
        w.append((va, wort, text))

    # start_stub
    put(a + 0x00, 0xE92D4010, "push {r4, lr}")
    put(a + 0x04, bl(a + 0x04, STARTLADER), "bl #0x%x" % STARTLADER)
    put(a + 0x08, 0xE1A04000, "mov r4, r0")
    put(a + 0x0C, 0xE59F1000 | (a + 0x30 - (a + 0x0C + 8)), "ldr r1, [pc, #0x1c]")
    put(a + 0x10, 0xE5910000, "ldr r0, [r1]")
    put(a + 0x14, 0xE3500000, "cmp r0, #0")
    put(a + 0x18, b_cond(0x1, a + 0x18, a + 0x28), "bne #0x%x" % (a + 0x28))
    put(a + 0x1C, 0xE3A00001, "mov r0, #1")
    put(a + 0x20, 0xE5810000, "str r0, [r1]")
    put(a + 0x24, bl(a + 0x24, STARTER), "bl #0x%x" % STARTER)
    put(a + 0x28, 0xE1A00004, "mov r0, r4")
    put(a + 0x2C, 0xE8BD8010, "pop {r4, pc}")
    put(a + 0x30, merker, None)                      # Literal: Adresse des Merkers
    # pumpe_stub
    put(pumpe + 0x00, 0xE92D4010, "push {r4, lr}")
    put(pumpe + 0x04, bl(pumpe + 0x04, WATCHDOG), "bl #0x%x" % WATCHDOG)
    put(pumpe + 0x08, 0xE92D000F, "push {r0, r1, r2, r3}")
    put(pumpe + 0x0C, bl(pumpe + 0x0C, PUMPE), "bl #0x%x" % PUMPE)
    put(pumpe + 0x10, 0xE8BD000F, "pop {r0, r1, r2, r3}")
    put(pumpe + 0x14, 0xE8BD8010, "pop {r4, pc}")
    put(merker, 0x00000000, None)                    # Merker, beim Laden 0
    return w, merker, pumpe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default=APP)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="/dev/sdX")
    a = ap.parse_args()

    d = bytearray(open(a.app, "rb").read())
    if hashlib.sha256(d).hexdigest() != APP_SHA:
        sys.exit("APP.bin ist nicht die erwartete")
    orig = bytes(d)

    def off(va):
        return va - VA0

    def wort(buf, va):
        return struct.unpack_from("<I", buf, off(va))[0]

    w_stub, merker, pumpe_va = stubs()

    # Patchstellen: (va, erwartetes Wort, neues Wort, soll-text)
    stellen = [
        (0xC27FC, bl(0xC27FC, STARTLADER), bl(0xC27FC, STUB_VA), "bl #0x%x" % STUB_VA),
        (0x6A528, bl(0x6A528, WATCHDOG), bl(0x6A528, pumpe_va), "bl #0x%x" % pumpe_va),
        (0xC0F4C, bl(0xC0F4C, STARTER), NOP, "mov r0, r0"),
        (0xC1044, bl(0xC1044, STOPPER), NOP, "mov r0, r0"),
    ]
    for va, alt, neu, _ in stellen:
        if wort(d, va) != alt:
            sys.exit("0x%X: 0x%08X statt erwartet 0x%08X" % (va, wort(d, va), alt))

    # Stub-Bereich: hinter dem Image, ausserhalb Scatter, innerhalb der Ladelaenge
    lo, hi = off(STUB_VA), off(merker) + 4
    assert lo >= len(d) and hi <= APP_MAX and lo % 512 == 0, (hex(lo), hex(hi))
    assert not (SCATTER_RW[0] <= lo < SCATTER_RW[1])

    # Fenster-Vorbedingung offline nachbauen (fuer Kopie und Hash im Skript)
    for o in FENSTER_LITERALE:
        assert struct.unpack_from("<I", d, o)[0] == FENSTER_ALT
        struct.pack_into("<I", d, o, FENSTER_NEU)
    fenster_sektor = FENSTER_LITERALE[0] // 512
    fenster_hash = hashlib.sha256(d[fenster_sektor * 512:(fenster_sektor + 1) * 512]).hexdigest()

    # Patchen
    for va, _, neu, _ in stellen:
        struct.pack_into("<I", d, off(va), neu)
    d.extend(b"\x00" * (hi - len(d)))
    for va, w, _ in w_stub:
        struct.pack_into("<I", d, off(va), w)

    # Ruecklesen mit capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
    fehler = 0
    pruef = [(va, neu, t) for va, _, neu, t in stellen] + [(va, w, t) for va, w, t in w_stub if t]
    for va, w, soll in pruef:
        ins = list(md.disasm(struct.pack("<I", w), va))
        ist = ("%s %s" % (ins[0].mnemonic, ins[0].op_str)).strip() if ins else "?"
        norm = lambda s: s.replace("stmdb sp!, ", "push ").replace("ldm sp!, ", "pop ").replace("pop.w", "pop")
        ok = norm(ist) == norm(soll) or (soll.startswith("ldr r1, [pc") and ist.startswith("ldr r1, [pc"))
        print("  %s 0x%08X  %08X  %-28s %s" % ("ok " if ok else "XX ", va, w, ist, "" if ok else "soll: " + soll))
        fehler += not ok
    if fehler:
        sys.exit("%d Befehle stimmen nicht -- nichts erzeugt" % fehler)

    # Sektoren: alle geaenderten Dateisektoren innerhalb von APP_MAX
    alt_pad = orig + b"\x00" * (len(d) - len(orig))
    sek = sorted({i // 512 for i in range(len(d)) if d[i] != alt_pad[i]} - {fenster_sektor})
    for s in sek:
        assert not (SCATTER_RW[0] // 512 <= s <= (SCATTER_RW[1] - 1) // 512), hex(s * 512)

    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "APP.usb_dauerbetrieb.bin"), "wb").write(d)
    zeilen = ["#!/bin/bash", "set -e",
              "# Erzeugt von patch_usb_dauerbetrieb.py (CL-USB-REC-126). NUR Testkarte.",
              "DEV=%s" % a.device, 'cd "$(dirname "$0")"',
              "# Vorbedingung: USB-Fenster schon auf 0x%08X (CL-USB-REC-119)" % FENSTER_NEU,
              'IST=$(dd if=$DEV bs=512 skip=%d count=1 status=none | sha256sum | cut -d" " -f1)'
              % ((RAW_APP >> 9) + fenster_sektor),
              '[ "$IST" = %s ] || { echo "USB-Fenster nicht gepatcht -- erst patch_usb_window.py"; exit 1; }' % fenster_hash]
    for s in sek:
        raw = (RAW_APP >> 9) + s
        neu = d[s * 512:(s + 1) * 512]
        open(os.path.join(a.out, "sektor_%06x.neu" % (s * 512)), "wb").write(neu)
        if s * 512 < len(orig):
            erwartet = hashlib.sha256(orig[s * 512:(s + 1) * 512]).hexdigest()
            zeilen.append('IST=$(dd if=$DEV bs=512 skip=%d count=1 status=none | sha256sum | cut -d" " -f1)' % raw)
            zeilen.append('case "$IST" in %s|%s) ;; *) echo "Datei-Sektor 0x%X unerwartet -- Abbruch"; exit 1;; esac'
                          % (erwartet, hashlib.sha256(neu).hexdigest(), s * 512))
    zeilen.append('read -p "Sicherung anlegen und %d Sektoren schreiben? [j/N] " x; [ "$x" = j ] || exit 1' % len(sek))
    for s in sek:
        raw = (RAW_APP >> 9) + s
        zeilen.append('[ -e sektor_%06x.sicherung ] || dd if=$DEV of=sektor_%06x.sicherung bs=512 skip=%d count=1 status=none'
                      % (s * 512, s * 512, raw))
    for s in sek:
        raw = (RAW_APP >> 9) + s
        zeilen.append("dd if=sektor_%06x.neu of=$DEV bs=512 seek=%d count=1 conv=notrunc,fsync status=none" % (s * 512, raw))
    zeilen += ["sync", 'echo "fertig -- zurueck mit ./zurueck.sh"', ""]
    p = os.path.join(a.out, "patch.sh")
    open(p, "w").write("\n".join(zeilen)); os.chmod(p, 0o755)
    z = ["#!/bin/bash", "set -e", "DEV=%s" % a.device, 'cd "$(dirname "$0")"',
         'read -p "Sicherung zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1']
    for s in sek:
        z.append("dd if=sektor_%06x.sicherung of=$DEV bs=512 seek=%d count=1 conv=notrunc,fsync status=none"
                 % (s * 512, (RAW_APP >> 9) + s))
    z += ["sync", 'echo "zurueck"', ""]
    p = os.path.join(a.out, "zurueck.sh")
    open(p, "w").write("\n".join(z)); os.chmod(p, 0o755)

    print("Stubs: start 0x%X, pumpe 0x%X, Merker 0x%X (Datei 0x%X..0x%X)"
          % (STUB_VA, pumpe_va, merker, lo, hi))
    print("Sektoren (Datei): %s, Fenster-Sektor 0x%X als Vorbedingung"
          % (", ".join("0x%X" % (s * 512) for s in sek), fenster_sektor * 512))
    print("Kopie inkl. Fenster: %s  sha256 %s"
          % (os.path.join(a.out, "APP.usb_dauerbetrieb.bin"), hashlib.sha256(d).hexdigest()[:16]))


if __name__ == "__main__":
    main()
