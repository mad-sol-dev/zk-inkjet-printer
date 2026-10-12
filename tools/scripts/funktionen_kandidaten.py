#!/usr/bin/env python3
"""Kandidaten fuer funktionen_anlegen.py: ARM-Prologe, auf die BL oder ein Poolwort
zeigt und an denen Ghidra keine Funktion definiert hat (Rohdatei-Methode).

Warum nicht als Ghidra-Skript: run_script war in der Sitzung 2026-10-12 abgeschaltet
(503). Statt der Funktionsmenge aus fm.getFunctionAt/getFunctionContaining dient die
Liste research/phase_a_sd_analysis/artifacts/ghidra_funktionsliste_2026-10-12.txt
(Eintritte und Koerperstuecke aus mcp list_functions_in_range).

Regeln (CL-TOOL-REC-126): VA = Dateioffset + 0x58000. Ziel 4-ausgerichtet, im Image
0x58000..0x2CD22B, Wort & 0xFFFF4000 == 0xE92D4000 (push {..,lr}) oder 0xE52DE004.
BL-Quellen: ARM-BL (Bedingung != 0xF) im Bereich file < 0xC8000 (VA < 0x120000), auch im
Bereich file+0x10000-0x1FFFF (dort liegt ARM-Code, z. B. VA 0x71888); Ziele dort werden
gesondert markiert. BLX-Immediate zielt auf Thumb und zaehlt nicht.
Poolwort-Quellen: ausgerichtete Worte der ganzen Datei, getrennt nach 'ldr' (ein
ARM-ldr Rd,[pc,#..] laedt das Wort), 'thumb' und 'daten' (kein ladender Befehl).

    funktionen_kandidaten.py            -> Bericht (Kontrolle, Zahlen, Tabelle)
    funktionen_kandidaten.py --tabelle  -> nur die ZIELE-Zeilen
"""
import struct, sys, bisect
D = open('firmware/bin/ZK-INKJET-NANO-APP.bin', 'rb').read()
BASE, N = 0x58000, len(D)
END = BASE + N
LISTE = 'research/phase_a_sd_analysis/artifacts/ghidra_funktionsliste_2026-10-12.txt'
THUMB = range(0x10000, 0x20000)
CODE_BIS = 0xC8000

def w(o): return struct.unpack_from('<I', D, o)[0]
def prolog(x): return x & 0xFFFF4000 == 0xE92D4000 or x == 0xE52DE004

def lade_funktionen():
    eintritte, teile = [], []
    for l in open(LISTE, encoding='utf-8'):
        if l.startswith('#') or not l.strip(): continue
        t = l.split(); a = int(t[0], 16)
        eintritte.append(a)
        if len(t) > 2 and t[2] == 'C':
            teile += [tuple(int(x, 16) for x in c.split('-')) for c in t[3:]]
        else:
            teile.append((a, a + int(t[1]) - 1))
    teile.sort()
    return set(eintritte), teile, [s for s, e in teile]

EIN, TEILE, STARTS = lade_funktionen()
def hat_funktion(a):
    if a in EIN: return True
    i = bisect.bisect_right(STARTS, a) - 1
    while i >= 0 and a - TEILE[i][0] < 0x40000:   # Koerper koennen weit streuen: alle pruefen
        if TEILE[i][0] <= a <= TEILE[i][1]: return True
        i -= 1
    return False

def sammle():
    q = {}
    def add(t, art, von):
        q.setdefault(t, {'BL': [], 'ldr': [], 'thumb': [], 'daten': [], 'ohne': []})[art].append(von)
    # ldr-Ziele
    arm, thb = set(), set()
    for o in range(0, N - 3, 4):
        x = w(o)
        if (x >> 28) != 0xF and (x >> 26) & 3 == 1 and (x >> 16) & 0xF == 15 and (x >> 20) & 1 \
                and (x >> 25) & 1 == 0 and (x >> 22) & 1 == 0:
            arm.add(o + 8 + ((x & 0xFFF) if (x >> 23) & 1 else -(x & 0xFFF)))
    for o in range(0x10000, 0x20000, 2):
        x = struct.unpack_from('<H', D, o)[0]
        if x >> 11 == 0b01001: thb.add(((o + 4) & ~3) + ((x & 0xFF) << 2))
    # BL
    for o in range(0, CODE_BIS, 4):
        x = w(o)
        if (x >> 28) != 0xF and (x >> 24) & 0xF == 0xB:
            imm = x & 0xFFFFFF
            if imm & 0x800000: imm -= 1 << 24
            t = BASE + o + 8 + imm * 4
            if BASE <= t < END and prolog(w(t - BASE)): add(t, 'BL', BASE + o)
    # Poolworte
    for o in range(0, N - 3, 4):
        v = w(o)
        if v & 3 or not BASE <= v < END or not prolog(w(v - BASE)): continue
        art = 'ldr' if o in arm else 'thumb' if o in thb else 'daten'
        add(v, art, BASE + o)
    # unreferenzierte Prologe im Codebereich (die Verweissuche allein besteht die Positivkontrolle nicht)
    for o in range(0, CODE_BIS, 4):
        if prolog(w(o)) and BASE + o not in q: add(BASE + o, 'ohne', BASE + o)
    return q

def dichte_tabelle(va_quelle):
    """Datenwort in einer dichten Zeigerfolge? (>=4 aufeinanderfolgende Worte im Imagebereich)"""
    o = va_quelle - BASE
    lauf = 1
    for d in (-4, 4):
        p = o + d
        while 0 <= p < N - 3 and BASE <= w(p) < END and lauf < 8:
            lauf += 1; p += d
    return lauf >= 4

def kandidaten():
    q = sammle()
    k = {t: v for t, v in q.items() if not hat_funktion(t)}
    return q, k

def art_text(v):
    teile = []
    if v['BL']: teile.append('BL von %s (%d Stelle%s)' % (', '.join('0x%X' % a for a in v['BL'][:2]), len(v['BL']), 'n' if len(v['BL']) != 1 else ''))
    if v['ohne']: teile.append('Prolog ohne jeden BL-/Poolwort-Verweis')
    for art, name in (('ldr', 'Poolwort per ldr'), ('thumb', 'Poolwort per Thumb-ldr'), ('daten', 'Datenwort')):
        if v[art]: teile.append('%s bei %s (%d)' % (name, ', '.join('0x%X' % a for a in v[art][:2]), len(v[art])))
    return '; '.join(teile)

def zeilen(k):
    out = []
    for t in sorted(k):
        out.append('    (0x%08X, 0x%08X, "%s"),' % (t, w(t - BASE), art_text(k[t])))
    return out

if __name__ == '__main__':
    q, k = kandidaten()
    if len(sys.argv) > 1 and sys.argv[1] == '--tabelle':
        print('\n'.join(zeilen(k))); sys.exit()
    print('funktionen_kandidaten.py -- Ghidra-Funktionen aus', LISTE, ':', len(EIN), 'Eintritte,', len(TEILE), 'Koerperstuecke')
    print('Prologe mit Verweis oder im Codebereich gesamt:', len(q), '; davon mit Ghidra-Funktion:', len(q) - len(k), '; ohne:', len(k))
    # Positivkontrolle: 10 bekannte Aufrufstellen von 0x8A434 ohne Funktion
    sites = [0x71930, 0x719E8, 0x71B70, 0x71BE0, 0xBDBA0, 0xBDBE0, 0xBDC24, 0xBDC9C, 0x114DAC, 0x114DF8]
    print('\n== Positivkontrolle: Aufrufstellen von 0x0008A434 ohne umgebende Funktion (mcp search_xrefs_to, 10 von 21) ==')
    gef = 0
    ks = sorted(k)
    for s in sites:
        assert not hat_funktion(s), hex(s)
        i = bisect.bisect_right(ks, s) - 1
        c = ks[i] if i >= 0 else None
        ok = False
        if c is not None:
            # zwischen Kandidat und Stelle darf keine Ghidra-Funktion beginnen
            ok = not any(c <= e <= s for e in EIN) and s - c < 0x2000
        gef += ok
        print('  Stelle 0x%X: naechster Kandidat davor %s (Abstand %s) -> %s' % (s, hex(c) if c else '-', hex(s - c) if c else '-', 'GEFUNDEN' if ok else 'NICHT gefunden'))
    print('  Kontrolle: %d von %d' % (gef, len(sites)))
    n = {'BL': 0, 'ldr': 0, 'thumb': 0, 'daten': 0, 'ohne': 0}
    for v in k.values():
        for a in n:
            if v[a]: n[a] += 1
    nur = lambda a: sum(1 for v in k.values() if v[a] and not any(v[b] for b in n if b != a))
    kv = sorted(t for t, v in k.items() if any(v[a] for a in ('BL', 'ldr', 'thumb', 'daten')))
    gv = 0
    for s in sites:
        i = bisect.bisect_right(kv, s) - 1
        gv += bool(i >= 0 and not any(kv[i] <= e <= s for e in EIN) and s - kv[i] < 0x2000)
    print('  Gegenprobe: nur Kandidaten MIT Verweis (BL/Poolwort/Datenwort): %d von %d. Die drei Anfaenge 0x71888, 0xBDB1C, 0x114CC0 tragen' % (gv, len(sites)))
    print('  weder BL noch Poolwort; die reine Verweissuche haette die Kontrolle nicht bestanden, deshalb gehoeren die Prologe ohne Verweis dazu.')
    print('\n== Kandidaten gesamt: %d ==' % len(k))
    print('mit mindestens einem Verweis dieses Typs: BL %d, Poolwort-ldr %d, Poolwort-Thumb %d, Datenwort %d, ohne Verweis %d' % (n['BL'], n['ldr'], n['thumb'], n['daten'], n['ohne']))
    print('ausschliesslich dieser Typ:            BL %d, Poolwort-ldr %d, Poolwort-Thumb %d, Datenwort %d, ohne Verweis %d' % (nur('BL'), nur('ldr'), nur('thumb'), nur('daten'), nur('ohne')))
    dt = [t for t, v in k.items() if v['daten'] and not (v['BL'] or v['ldr'] or v['thumb'] or v['ohne']) and all(dichte_tabelle(a) for a in v['daten'])]
    print('reine Datenwort-Kandidaten in dichter Zeigerfolge (Scheintreffer-Risiko, CL-TOOL-REC-120): %d' % len(dt))
    thumbziel = [t for t in k if (t - BASE) in THUMB]
    print('Kandidaten im Thumb-Bereich file+0x10000-0x1FFFF (gesondert markieren): %d' % len(thumbziel))
    print('\n== Tabelle (Adresse, erstes Wort, Herkunft) ==')
    for t in sorted(k):
        mark = ''
        if (t - BASE) in THUMB: mark = ' [THUMB-BEREICH]'
        if t in dt: mark += ' [dichte Zeigerfolge]'
        print('    (0x%08X, 0x%08X, "%s%s"),' % (t, w(t - BASE), art_text(k[t]), mark))
