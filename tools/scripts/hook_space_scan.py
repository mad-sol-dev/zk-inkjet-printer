#!/usr/bin/env python3
"""Vier-Modi-Suche nach Verweisen auf einen Adressbereich in APP.bin (Regel 6).

VA = Dateioffset + 0x58000. Thumb-Bereich file+0x10000-0x1FFFF wird fuer die
ARM-Decoder (Immediate, ADR, Kette) ausgespart und getrennt gemeldet.

Modi: lit (ausgerichtetes Poolwort, ueber die ganze Datei), imm (ein
ARM-Immediate allein), adr (ADD/SUB Rd,PC,#imm), kette (MOV/MVN-Seed + ORR/ADD/
SUB/EOR auf demselben Register, bis zu 4 Folgebefehle, Register darf nicht
zwischendurch neu geladen werden). Aufruf:
    hook_space_scan.py LO HI      |      hook_space_scan.py --bericht
"""
import struct, sys
D = open('firmware/bin/ZK-INKJET-NANO-APP.bin', 'rb').read()
BASE = 0x58000
THUMB = range(0x10000, 0x20000)
N = len(D)

def ror(v, r):
    r &= 31
    return ((v >> r) | (v << (32 - r))) & 0xFFFFFFFF if r else v

def w(o):
    return struct.unpack_from('<I', D, o)[0]

def immdec(x):
    return ror(x & 0xFF, 2 * ((x >> 8) & 0xF))

def modus_lit(lo, hi):
    return [(o, w(o)) for o in range(0, N - 3, 4) if lo <= w(o) < hi]

def modus_imm(lo, hi):
    """Data-Processing mit Immediate (I-Bit), Cond egal ausser 0xF: Wert im Bereich."""
    r = []
    for o in range(0, N - 3, 4):
        if o in THUMB: continue
        x = w(o)
        if (x >> 28) == 0xF or (x >> 25) & 7 != 1: continue
        op = (x >> 21) & 0xF
        if op in (8, 9, 10, 11): pass          # tst/teq/cmp/cmn: auch Operand
        v = immdec(x)
        if lo <= v < hi: r.append((o, v))
    return r

def modus_adr(lo, hi):
    r = []
    for o in range(0, N - 3, 4):
        if o in THUMB: continue
        x = w(o)
        if (x >> 28) == 0xF: continue
        m = x & 0x0FFF0000
        if m in (0x028F0000, 0x024F0000):
            t = BASE + o + 8 + (immdec(x) if m == 0x028F0000 else -immdec(x))
            if lo <= t < hi: r.append((o, t))
    return r

def modus_kette(lo, hi):
    r = []
    for o in range(0, N - 3, 4):
        if o in THUMB: continue
        x = w(o)
        if (x >> 28) == 0xF or (x >> 25) & 7 != 1: continue
        op = (x >> 21) & 0xF
        if op not in (13, 15): continue        # mov / mvn Seed
        rd = (x >> 12) & 0xF
        v = immdec(x)
        if op == 15: v = ~v & 0xFFFFFFFF
        for k in range(1, 5):
            p = o + 4 * k
            if p + 4 > N or p in THUMB: break
            y = w(p)
            if (y >> 28) == 0xF: break
            if (y >> 26) & 3 != 0: break
            if (y >> 12) & 0xF != rd: 
                # Rd anders: Kette endet, falls Rd gelesen/geschrieben egal -> nur Abbruch bei Neuladen
                continue
            yop = (y >> 21) & 0xF
            if (y >> 25) & 1 and (y >> 16) & 0xF == rd and yop in (12, 4, 2, 1):
                u = immdec(y)
                if yop == 12: v |= u
                elif yop == 4: v = (v + u) & 0xFFFFFFFF
                elif yop == 2: v = (v - u) & 0xFFFFFFFF
                elif yop == 1: v ^= u
                if lo <= v < hi: r.append((o, v))
            else:
                break
    return r

MODI = [('lit', modus_lit), ('imm', modus_imm), ('adr', modus_adr), ('kette', modus_kette)]

def ldr_ziele():
    """Pool-Adressen aller ARM-ldr Rd,[pc,#+-imm] und Thumb-ldr Rd,[pc,#imm]."""
    arm, thb = set(), set()
    for q in range(0, N - 3, 4):
        if q in THUMB: continue
        x = w(q)
        if (x >> 28) != 0xF and (x >> 26) & 3 == 1 and (x >> 16) & 0xF == 15 \
                and (x >> 20) & 1 and (x >> 25) & 1 == 0 and (x >> 22) & 1 == 0:
            arm.add(q + 8 + ((x & 0xFFF) if (x >> 23) & 1 else -(x & 0xFFF)))
    for q in range(0x10000, 0x20000, 2):
        x = struct.unpack_from('<H', D, q)[0]
        if x >> 11 == 0b01001: thb.add(((q + 4) & ~3) + ((x & 0xFF) << 2))
    return arm, thb

def bericht():
    print('hook_space_scan.py -- Rohzahlen fuer CL-FIRMWARE-REC-111 (VA = file + 0x58000)')
    print('APP.bin %d Bytes; Thumb-Bereich file+0x10000-0x1FFFF fuer ARM-Decoder ausgespart' % N)
    print('\n== Positivkontrollen (ganze Datei) ==')
    print('lit   0x0008A434 (CL-BOOT-REC-114/CL-STORAGE-REC-135 Callback):',
          len(modus_lit(0x8A434, 0x8A435)), 'Poolworte, soll >0')
    im = [o for o, v in modus_imm(0x28800000, 0x28800001) if w(o) >> 28 == 0xE]
    print('imm   0x28800000 cond=AL:', len(im), 'Stellen, davon file+0x65FE4:', 0x65FE4 in im,
          '(Ghidra search_scalars 2026-10-12: 8 Treffer, identische Menge)')
    a = modus_adr(0, 1 << 32)
    print('adr   Decoder:', len(a), 'ADD/SUB-PC-Befehle,',
          sum(1 for o, t in a if BASE <= t < BASE + N), 'davon mit Ziel im Image (Plausibilitaet)')
    k = modus_kette(0, 1 << 32)
    print('kette Decoder:', len(k), 'Ketten; Kontrolle file+0xC5CEC: ',
          dict(k).get(0xC5CEC) == 0x7FC00000,
          '(mov r0,#0x80000000; sub r0,r0,#0x400000 = 0x7FC00000, von Hand gelesen)')
    arm, thb = ldr_ziele()
    for name, lo, hi in (('A1 RAM-Luecke 0x00044FC0-0x00058000', 0x44FC0, 0x58000),
                         ('A2 hinter dem Image 0x002CD22C-0x002D8000', 0x2CD22C, 0x2D8000)):
        print('\n==', name, '==')
        l = modus_lit(lo, hi)
        la = [(o, v) for o, v in l if o in arm]
        lt = [(o, v) for o, v in l if o in thb]
        print('lit   %d ausgerichtete Worte im Bereich; %d von ARM-ldr geladen, %d von Thumb-ldr geladen,' % (len(l), len(la), len(lt)))
        print('      Rest %d sind Datenworte/Codebytes ohne ladenden Befehl' % (len(l) - len(la) - len(lt)))
        for o, v in la: print('      ARM-Pool file+0x%X = 0x%X ARM-ldr-geladen' % (o, v))
        for o, v in lt: print('      Thumb-Pool file+0x%X = 0x%X (Thumb-Bereich; Wert ist selbst Thumb-Code 0x%08X)' % (o, v, v))
        i = modus_imm(lo, hi)
        ic = [(o, v) for o, v in i if w(o) >> 28 == 0xE and o < 0x120000]
        print('imm   %d Dekodierungen in der ganzen Datei, %d davon cond=AL im Codebereich (file<0x120000)' % (len(i), len(ic)))
        for o, v in ic: print('      file+0x%X %08X -> 0x%X' % (o, w(o), v))
        print('adr   %d Treffer' % len(modus_adr(lo, hi)))
        print('kette %d Treffer' % len(modus_kette(lo, hi)))

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--bericht':
        bericht(); sys.exit()
    lo, hi = int(sys.argv[1], 0), int(sys.argv[2], 0)
    print(f'Bereich VA 0x{lo:X}-0x{hi:X} (HI exkl.), Datei {N} Bytes, Thumb 0x10000-0x1FFFF ausgespart')
    for n, f in MODI:
        h = f(lo, hi)
        print(f'{n}: {len(h)} Treffer', ' '.join(f'file+0x{o:X}->0x{v:X}' for o, v in h[:12]))
