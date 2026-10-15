#!/usr/bin/env python3
"""Sucht die Erzeuger eines UI-Ereigniscodes in APP.bin (Sitzung 2026-10-15,
Frage 0x169 aus CL-STORAGE-REC-136). VA = Dateioffset + 0x58000.

Gelesen werden die vier Wege, auf denen ein Code in ui_main_loop ankommt:
  (1) Tastengeraete: alle Aufrufe von keydev_register 0x117560 (Lesefunktion,
      Filter, Tabelle aus 12-Byte-Eintraegen {Code, Intervall, Name} bis
      0x0FFFFFFF) samt Tabelleninhalt.
  (2) ui_event_post 0x117B7C: jede BL-Stelle mit dem Wert von r0.
  (3) Schaltflaechen: jede Aufrufstelle von FUN_00112a54/FUN_0011911c, dazu
      die Widgets FUN_000b5ffc (+0x28), FUN_00116bb0 (+0x3C), FUN_00117900
      (+0x34): letzte Speicherung in das Codefeld der Beschreibung auf dem
      Stapel und die Herkunft des gespeicherten Registers (mov/mvn/Poolwort
      oder Rechnung). 'kein Store' = Beschreibung nur per memcpy aus dem Image.
  (4) Optional --ram ABZUG: die Schaltflaechenliste 0x41378+0xC0 im RAM-Abzug.

  ereignis_erzeuger.py [--code 0x169] [--ram ABZUG]

Grenzen: Die Herkunftsverfolgung ist ein Rueckwaertsschritt ueber hoechstens
80 Befehle innerhalb des geraden Wegs; 'ret of' bei callee-gesicherten
Registern (r4-r11) ist unzuverlaessig und muss von Hand gelesen werden.
Ergebnis ist eine Liste zum Lesen, kein Urteil. Liest nur, schreibt nichts.
"""
import argparse, re, struct, sys
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / 'firmware/bin/ZK-INKJET-NANO-APP.bin'
BASE = 0x58000
B = IMG.read_bytes()
MD = Cs(CS_ARCH_ARM, CS_MODE_ARM)


def W(a):
    return struct.unpack_from('<I', B, a - BASE)[0]


def dis(a, n):
    return list(MD.disasm(B[a - BASE:a - BASE + 4 * n], a))


def callers(t):
    r = []
    for o in range(0, len(B) - 3, 4):
        w = struct.unpack_from('<I', B, o)[0]
        if (w >> 28) == 0xF:
            if (w >> 25) == 0x7D:
                off = w & 0xFFFFFF
                off -= (1 << 24) if off & 0x800000 else 0
                if BASE + o + 8 + off * 4 + ((w >> 24) & 1) * 2 == t:
                    r.append(BASE + o)
            continue
        if (w & 0x0F000000) == 0x0B000000:
            off = w & 0xFFFFFF
            off -= (1 << 24) if off & 0x800000 else 0
            if BASE + o + 8 + off * 4 == t:
                r.append(BASE + o)
    return r


def pointer_refs(v):
    return [BASE + o for o in range(0, len(B) - 3, 4)
            if struct.unpack_from('<I', B, o)[0] in (v, v | 1)]


def resolve(win, idx, reg, depth=0):
    for j in range(idx - 1, -1, -1):
        i = win[j]
        ops = [x.strip() for x in i.op_str.split(',')]
        if i.mnemonic in ('bl', 'blx'):
            return f'ret of {i.op_str}@{hex(i.address)}'
        if i.mnemonic.startswith(('str', 'cmp', 'cmn', 'tst', 'teq', 'push', 'b')) \
                and not i.mnemonic.startswith('bic'):
            continue
        if ops and ops[0] == reg:
            if i.mnemonic in ('mov', 'mvn') and ops[1].startswith('#'):
                v = int(ops[1][1:], 0)
                return hex(v if i.mnemonic == 'mov' else ~v & 0xFFFFFFFF)
            if i.mnemonic == 'ldr' and '[pc' in i.op_str:
                m = re.search(r'#(-?0x[0-9a-f]+|-?\d+)', i.op_str)
                return 'pool ' + hex(W(i.address + 8 + (int(m.group(1), 0) if m else 0)))
            s = f'{hex(i.address)} {i.mnemonic} {i.op_str}'
            if depth < 3 and len(ops) > 1 and re.match(r'r\d+$|sb$|sl$|fp$|ip$|lr$', ops[1]):
                s += ' <- ' + resolve(win, j, ops[1], depth + 1)
            return s
    return '?'


def code_field(c, off):
    win = dis(c - 4 * 80, 81)
    k = len(win) - 1
    for j in range(k - 1, -1, -1):
        i = win[j]
        if i.op_str.startswith('r0,') and not i.mnemonic.startswith(('str', 'cmp', 'tst', 'cmn')):
            break
    else:
        return '?'
    if i.op_str == 'r0, sp' and i.mnemonic.startswith('mov'):
        X = 0
    else:
        m = re.match(r'r0, sp, #(0x[0-9a-f]+|\d+)$', i.op_str)
        if not (m and i.mnemonic.startswith('add')):
            return f'Beschreibung ueber {i.mnemonic} {i.op_str} = {resolve(win, j + 1, "r0")}'
        X = int(m.group(1), 0)
    t = X + off
    pat = rf'\[sp, #{hex(t)}\]$' if t else r'\[sp\]$'
    st = [(n, s) for n, s in enumerate(win[:k])
          if s.mnemonic.startswith('str') and re.search(pat, s.op_str)]
    if not st:
        return f'sp+{hex(X)}: kein Store (memcpy aus dem Image)'
    n, s = st[-1]
    reg = s.op_str.split(',')[0]
    return f'sp+{hex(X)}: {hex(s.address)} {reg} = {resolve(win, n, reg)}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--code', default='0x169')
    ap.add_argument('--ram')
    a = ap.parse_args()
    code = int(a.code, 0)

    print('== (1) Tastengeraete: keydev_register 0x117560')
    print('   Zeigerverweise:', [hex(x) for x in pointer_refs(0x117560)])
    for c in callers(0x117560):
        win = dis(c - 4 * 6, 7)
        regs = {}
        for i in win:
            m = re.match(r'(r[012]), \[pc, #(0x[0-9a-f]+)\]', i.op_str)
            if i.mnemonic == 'ldr' and m:
                regs[m.group(1)] = W(i.address + 8 + int(m.group(2), 16))
        print(f'   {hex(c)}: Lesefunktion {hex(regs.get("r0", 0))} Filter {hex(regs.get("r1", 0))} '
              f'Tabelle {hex(regs.get("r2", 0))}')
        t = regs.get('r2')
        while t:
            e = W(t)
            print(f'      {{{hex(e)}, {W(t + 4)}, {hex(W(t + 8))}}}')
            if e == 0x0FFFFFFF:
                break
            t += 12

    print('== (2) ui_event_post 0x117B7C, r0 an jeder BL-Stelle')
    print('   Zeigerverweise:', [hex(x) for x in pointer_refs(0x117B7C)])
    for c in callers(0x117B7C):
        win = dis(c - 4 * 40, 41)
        print(f'   {hex(c)}: r0 = {resolve(win, len(win) - 1, "r0")}')

    print('== (3) Schaltflaechen und Widgets: Codefeld der Beschreibung')
    for f, off, name in ((0x112A54, 0, 'FUN_00112a54'), (0x11911C, 0, 'FUN_0011911c'),
                         (0xB5FFC, 0x28, 'FUN_000b5ffc'), (0x116BB0, 0x3C, 'FUN_00116bb0'),
                         (0x117900, 0x34, 'FUN_00117900')):
        cs = callers(f)
        print(f'   -- {name} (+{hex(off)}), {len(cs)} Aufrufstellen, Zeigerverweise '
              f'{[hex(x) for x in pointer_refs(f)]}')
        for c in cs:
            print(f'   {hex(c)}: {code_field(c, off)}')

    print(f'== Wort {hex(code)} im Image:',
          [hex(BASE + o) for o in range(0, len(B) - 3, 4) if struct.unpack_from('<I', B, o)[0] == code])

    if a.ram:
        R = Path(a.ram).read_bytes()
        p = struct.unpack_from('<I', R, 0x41378 + 0xC0)[0]
        print(f'== (4) Schaltflaechenliste im RAM-Abzug {a.ram}, [0x558] = '
              f'{hex(struct.unpack_from("<I", R, 0x558)[0])}')
        n = 0
        while p and p + 0x68 <= len(R) and n < 256:
            d = struct.unpack_from('<26I', R, p)
            lab = d[9]
            s = R[lab:R.find(b'\0', lab)][:40].decode('utf-8', 'replace') if 0 < lab < len(R) else ''
            print(f'   {hex(p)}: Code {hex(d[0])} Pos {d[1]},{d[2]} Groesse {d[3]}x{d[4]} {s!r}')
            p = d[25]
            n += 1


if __name__ == '__main__':
    sys.exit(main())
