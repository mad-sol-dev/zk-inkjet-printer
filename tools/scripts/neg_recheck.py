#!/usr/bin/env python3
"""Re-check of negative findings from the old address base (Rule 6).

Until 2026-08-31 the register counted VA = file offset + 0x200000 (and in
2025-12 even VA = file offset); the correct load address is file + 0x58000
(CL-BOOT-REC-113, Ghidra database rebased 2026-10-11, CL-TOOL-REC-121). In the
wrong base every absolute pointer dangled, so "no caller", "no xref" and
"no reference" results from that time are suspect. This script repeats such
queries on the raw APP.bin, in the right base, in every search mode:

  lit    aligned 32-bit word in the file (literal pool or data); each hit is
         classified by whether an ARM ldr Rd,[pc,#imm] or a Thumb ldr Rd,[pc,#imm]
         loads it -- an unloaded word is data, not a code reference
  lit_u  the same value at any unaligned offset (count only)
  imm    one ARM data-processing immediate (8 bits rotated)
  adr    ADD/SUB Rd,PC,#imm (target computed)
  chain  MOV/MVN seed + up to 4 ORR/ADD/SUB/EOR on the same register
  bl     ARM B/BL (any condition), ARM BLX imm, Thumb BL/BLX pair
         (Thumb pairs only in file+0x10000-0x1FFFF, CL-BOOT-REC-016)

Function targets are searched as value and as value|1 (Thumb pointer).
Every mode is first run against a known case (positive control); a mode whose
control fails makes no negative statement. Read-only: nothing is written except
the report on stdout and, with --out DIR, report.txt and raw.json there.

    python3 tools/scripts/neg_recheck.py [--out DIR]
"""
import json, os, struct, sys
import capstone

APP = 'firmware/bin/ZK-INKJET-NANO-APP.bin'
D = open(APP, 'rb').read()
N = len(D)
BASE = 0x58000
END = BASE + N
THUMB = range(0x10000, 0x20000)
CODE_END_VA = 0x120000          # last Ghidra function ends at 0x11F6C3 (CL-TOOL-REC-126)

CS_ARM = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
CS_THUMB = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
# Without skipdata capstone stops silently at the first word it cannot decode:
# over VA 0x58000-0x120000 it returns 43 instructions instead of 204800.
CS_ARM.skipdata = True
CS_THUMB.skipdata = True


def w(o):
    return struct.unpack_from('<I', D, o)[0]


def h(o):
    return struct.unpack_from('<H', D, o)[0]


def ror(v, r):
    r &= 31
    return ((v >> r) | (v << (32 - r))) & 0xFFFFFFFF if r else v


def immdec(x):
    return ror(x & 0xFF, 2 * ((x >> 8) & 0xF))


def va(o):
    return BASE + o


def region(o):
    if o in THUMB:
        return 'thumb-range'
    return 'code' if va(o) < CODE_END_VA else 'data'


# ---------------------------------------------------------------- loaders
def _ldr_targets():
    arm, thb = {}, {}
    for q in range(0, N - 3, 4):
        x = w(q)
        if (x >> 28) != 0xF and (x >> 26) & 3 == 1 and (x >> 16) & 0xF == 15 \
                and (x >> 20) & 1 and (x >> 25) & 1 == 0 and (x >> 22) & 1 == 0:
            t = q + 8 + ((x & 0xFFF) if (x >> 23) & 1 else -(x & 0xFFF))
            if 0 <= t < N:
                arm.setdefault(t, []).append(q)
    for q in range(0x10000, 0x20000, 2):
        x = h(q)
        if x >> 11 == 0b01001:
            t = ((q + 4) & ~3) + ((x & 0xFF) << 2)
            thb.setdefault(t, []).append(q)
    return arm, thb


LDR_ARM, LDR_THUMB = _ldr_targets()
WORDS = [w(o) for o in range(0, N - 3, 4)]


# ---------------------------------------------------------------- modes
def m_lit(lo, hi):
    out = []
    for i, v in enumerate(WORDS):
        if lo <= v < hi:
            o = 4 * i
            kind = 'arm-ldr' if o in LDR_ARM else 'thumb-ldr' if o in LDR_THUMB else 'data'
            out.append({'file': o, 'va': va(o), 'value': v, 'kind': kind,
                        'loaded_by': [va(q) for q in LDR_ARM.get(o, []) + LDR_THUMB.get(o, [])]})
    return out


def m_lit_unaligned(lo, hi):
    n = 0
    for o in range(N - 3):
        if o & 3 and lo <= w(o) < hi:
            n += 1
    return n


def m_imm(lo, hi):
    out = []
    for o in range(0, N - 3, 4):
        x = w(o)
        if (x >> 28) == 0xF or (x >> 25) & 7 != 1:
            continue
        v = immdec(x)
        if lo <= v < hi:
            out.append({'file': o, 'va': va(o), 'value': v, 'word': x, 'region': region(o)})
    return out


def m_adr(lo, hi):
    out = []
    for o in range(0, N - 3, 4):
        x = w(o)
        if (x >> 28) == 0xF:
            continue
        m = x & 0x0FFF0000
        if m in (0x028F0000, 0x024F0000):
            t = va(o) + 8 + (immdec(x) if m == 0x028F0000 else -immdec(x))
            if lo <= t < hi:
                out.append({'file': o, 'va': va(o), 'value': t, 'region': region(o)})
    return out


def m_chain(lo, hi):
    out = []
    for o in range(0, N - 3, 4):
        x = w(o)
        if (x >> 28) == 0xF or (x >> 25) & 7 != 1:
            continue
        op = (x >> 21) & 0xF
        if op not in (13, 15):
            continue
        rd = (x >> 12) & 0xF
        v = immdec(x)
        if op == 15:
            v = ~v & 0xFFFFFFFF
        for k in range(1, 5):
            p = o + 4 * k
            if p + 4 > N:
                break
            y = w(p)
            if (y >> 28) == 0xF or (y >> 26) & 3 != 0:
                break
            if (y >> 12) & 0xF != rd:
                continue
            yop = (y >> 21) & 0xF
            if (y >> 25) & 1 and (y >> 16) & 0xF == rd and yop in (12, 4, 2, 1):
                u = immdec(y)
                v = {12: v | u, 4: (v + u) & 0xFFFFFFFF, 2: (v - u) & 0xFFFFFFFF, 1: v ^ u}[yop]
                if lo <= v < hi:
                    out.append({'file': o, 'va': va(o), 'value': v, 'end': va(p), 'region': region(o)})
            else:
                break
    return out


def _sx(v, bits):
    return v - (1 << bits) if v >> (bits - 1) else v


def m_bl(lo, hi):
    out = []
    for o in range(0, N - 3, 4):
        x = w(o)
        c = x >> 28
        if (x >> 25) & 7 != 5:
            continue
        off = _sx(x & 0xFFFFFF, 24) << 2
        if c == 0xF:
            t = va(o) + 8 + off + (((x >> 24) & 1) << 1)
            kind = 'arm-blx-imm'
        else:
            t = va(o) + 8 + off
            kind = ('arm-bl' if (x >> 24) & 1 else 'arm-b') + ('' if c == 0xE else '-cond%X' % c)
        if lo <= t < hi:
            out.append({'file': o, 'va': va(o), 'target': t, 'kind': kind, 'region': region(o)})
    for o in range(0x10000, 0x20000 - 2, 2):
        a, b = h(o), h(o + 2)
        if a >> 11 == 0b11110 and b >> 11 in (0b11111, 0b11101):
            off = (_sx(a & 0x7FF, 11) << 12) | ((b & 0x7FF) << 1)
            t = va(o) + 4 + off
            kind = 'thumb-bl'
            if b >> 11 == 0b11101:
                t &= ~3
                kind = 'thumb-blx'
            if lo <= t < hi:
                out.append({'file': o, 'va': va(o), 'target': t, 'kind': kind, 'region': 'thumb-range'})
    return out


MODES = [('lit', m_lit), ('imm', m_imm), ('adr', m_adr), ('chain', m_chain), ('bl', m_bl)]


# ---------------------------------------------------------------- argument recovery
REGS = {'r0': 0, 'r1': 1, 'r2': 2, 'r3': 3}


def call_args(o, regs=('r0', 'r1'), back=12):
    """Constant arguments before an ARM call at file offset o: walk back up to
    `back` instructions, the first write to each register decides. '?' if that
    write is not mov/mvn #imm, or if a branch or function start is crossed."""
    res = {r: None for r in regs}
    lo = max(0, o - 4 * back)
    ins = list(CS_ARM.disasm(D[lo:o], va(lo)))
    for i in reversed(ins):
        m = i.mnemonic
        if m.startswith(('b', 'pop', 'ldm')) and not m.startswith('bic') or 'pc' in i.op_str.split(',')[0]:
            break
        if m.startswith('push') or m.startswith('stmdb sp!'):
            break
        dst = i.op_str.split(',')[0].strip()
        if dst in res and res[dst] is None:
            if m in ('mov', 'movs') and '#' in i.op_str:
                res[dst] = int(i.op_str.split('#')[1], 0)
            elif m in ('mvn', 'mvns') and '#' in i.op_str:
                res[dst] = ~int(i.op_str.split('#')[1], 0) & 0xFFFFFFFF
            else:
                res[dst] = '%s %s' % (m, i.op_str)
        if all(v is not None for v in res.values()):
            break
    return {r: (hex(v) if isinstance(v, int) else (v or '?')) for r, v in res.items()}


def disasm_at(o, n=1):
    return ['0x%X: %s %s' % (i.address, i.mnemonic, i.op_str)
            for i in CS_ARM.disasm(D[o:o + 4 * n], va(o))]


# ---------------------------------------------------------------- driver
def query(lo, hi=None, thumb_ptr=False, modes=None):
    hi = lo + 1 if hi is None else hi
    res = {}
    for name, f in MODES:
        if modes and name not in modes:
            continue
        res[name] = f(lo, hi)
    res['lit_u'] = m_lit_unaligned(lo, hi)
    if thumb_ptr:
        res['lit_thumbptr'] = m_lit(lo | 1, hi | 1) if hi == lo + 1 else []
    return res


def counts(res):
    c = {k: (len(v) if isinstance(v, list) else v) for k, v in res.items()}
    if 'lit' in res:
        c['lit_loaded'] = sum(1 for e in res['lit'] if e['kind'] != 'data')
    return c


def controls():
    """Each mode against a case known from the register."""
    out = []
    lit = m_lit(0x8A434, 0x8A435)
    out.append(('lit', '0x0008A434 sd_raw primitive: 5 pool words (CL-FIRMWARE-REC-124/111)',
                len(lit), len(lit) == 5))
    imm = [e for e in m_imm(0x28800000, 0x28800001) if e['word'] >> 28 == 0xE]
    out.append(('imm', '0x28800000 cond=AL: 8 sites incl. file+0x65FE4 (Ghidra search_scalars 8)',
                len(imm), len(imm) == 8 and any(e['file'] == 0x65FE4 for e in imm)))
    adr = m_adr(0xB325C, 0xB325D)
    out.append(('adr', "'Please release the print key!' 0xB325C via adr at 0xB316C (CL-HARDWARE-REC-109)",
                [hex(e['va']) for e in adr], any(e['va'] == 0xB316C for e in adr)))
    ch = {e['file']: e['value'] for e in m_chain(0x7FC00000, 0x7FC00001)}
    out.append(('chain', 'file+0xC5CEC mov r0,#0x80000000; sub r0,r0,#0x400000 = 0x7FC00000 (CL-FIRMWARE-REC-111)',
                [hex(va(k)) for k in ch], 0xC5CEC in ch))
    bl = {e['va'] for e in m_bl(0xC7BF8, 0xC7BF9)}
    out.append(('bl', 'boot_init -> 0xC7BF8 at 0xB3120 and 0xB31CC (CL-HARDWARE-REC-109)',
                sorted(hex(x) for x in bl), {0xB3120, 0xB31CC} <= bl))
    tb = [e for e in m_bl(BASE, END) if e['kind'] == 'thumb-bl']
    out.append(('bl/thumb', 'Thumb BL pairs decoded in file+0x10000-0x1FFFF (plausibility, targets in image)',
                len(tb), len(tb) > 0))
    return out


# claim -> list of (label, lo, hi, thumb_ptr, args_regs)
QUERIES = [
    ('CL-HARDWARE-REC-112', 'port pin reader FUN_00089EC4 (old FUN_00231EC4): callers', 0x89EC4, None, True, ('r0', 'r1')),
    ('CL-HARDWARE-REC-112', 'GPE9 wrapper FUN_000C7BF8 (old FUN_0026FBF8): callers/pointers', 0xC7BF8, None, True, ()),
    ('CL-HARDWARE-REC-005', 'pin config FUN_00089F34 (pin_mux_config, 2025-12 at 0x31F34): callers', 0x89F34, None, True, ('r0', 'r1', 'r2')),
    ('CL-HARDWARE-REC-005', 'REG_GPBFUN 0xB0000084', 0xB0000084, None, False, ()),
    ('CL-HARDWARE-REC-005', 'GCR_BA 0xB0000000 (base word)', 0xB0000000, None, False, ()),
    ('CL-HP45-REC-012', 'adc_read_channel 0x85F28 (2025-12 at 0x2DF28): callers', 0x85F28, None, True, ('r0', 'r1')),
    ('CL-HP45-REC-012', 'ADC_BA range 0xB800E000-0xB800E0FF', 0xB800E000, 0xB800E100, False, ()),
    ('CL-MMIO-REC-005', 'UART range 0xB8008000-0xB80081FF (UART0/UART1)', 0xB8008000, 0xB8008200, False, ()),
    ('CL-MMIO-REC-006', '0xB1006800-0xB10068FF', 0xB1006800, 0xB1006900, False, ()),
    ('CL-HARDWARE-REC-111', 'GPIOE 0xB8001040-0xB800104F (CFG/DIR/PUEN/DOUT/PIN)', 0xB8001040, 0xB8001050, False, ()),
    ('CL-DISPLAY-REC-108', "string 'Print' 0x248500 (old 0x3F0500)", 0x248500, None, False, ()),
    ('CL-DISPLAY-REC-108', "string 'Printing...' 0x24AB68 (old 0x3F2B68)", 0x24AB68, None, False, ()),
    ('CL-DISPLAY-REC-108', "string 'Drucken...' 0x2527A8 (old 0x3FA7A8)", 0x2527A8, None, False, ()),
    ('CL-STORAGE-REC-128', 'settings RAM mirror 0x00000D00', 0xD00, None, False, ()),
    ('CL-FIRMWARE-REC-103', 'Zint render FUN_000882EC (old FUN_002302EC): callers', 0x882EC, None, True, ()),
    ('CL-USB-REC-108', 'store exporter FUN_000BDB08 (old FUN_00265B08): callers', 0xBDB08, None, True, ()),
    ('CL-HARDWARE-REC-109', 'boot_init 0xB30C4 (old 0x25B0C4): callers', 0xB30C4, None, True, ()),
    ('CL-FIRMWARE-REC-113', 'hp45_set_address 0xD8AE8: callers', 0xD8AE8, None, True, ()),
    ('CL-FIRMWARE-REC-113', 'hp45_set_primitives 0xD8B44: callers', 0xD8B44, None, True, ()),
    ('CL-USB-REC-126', 'FUN_0008A2C0: callers', 0x8A2C0, None, True, ()),
    ('CL-USB-REC-126', 'FUN_001079AC: callers', 0x1079AC, None, True, ()),
    ('CL-FIRMWARE-REC-116', 'file import FUN_000C7150: callers', 0xC7150, None, True, ()),
    ('CL-FIRMWARE-REC-113', 'delay_us 0x9EEC0 (hp45 table +0x10, I2C table +0x1C): callers', 0x9EEC0, None, True, ()),
    ('CL-FIRMWARE-REC-113', 'hp45 ops table 0x120F28 (base)', 0x120F28, None, False, ()),
    ('CL-FIRMWARE-REC-113', 'I2C ops table 0x120F40 (base)', 0x120F40, None, False, ()),
    ('CL-FIRMWARE-REC-103', 'element renderer FUN_000824BC (jump table 0x82688, calls 0x882EC at 0x83868)', 0x824BC, None, True, ()),
    ('CL-MMIO-REC-005', 'UART1 putc FUN_000757F4 (ldr 0xB8008000, FSR +0x118, THR +0x100)', 0x757F4, None, True, ()),
]


def indirect_calls_via(offset):
    """ldr rX,[rY,#offset] followed within 6 instructions by blx rX, code range."""
    ins = list(CS_ARM.disasm(D[0:CODE_END_VA - BASE], BASE))
    out = []
    for k, i in enumerate(ins):
        if i.mnemonic.startswith('blx') and i.op_str.startswith('r'):
            for p in ins[max(0, k - 6):k]:
                if p.mnemonic.startswith('ldr') and p.op_str.startswith(i.op_str + ', [') \
                        and p.op_str.endswith(']') and '#' in p.op_str \
                        and int(p.op_str.rsplit('#', 1)[1][:-1], 0) == offset:
                    out.append((p.address, i.address))
    return sorted(set(out))


def gcr_offsets():
    """Loads/stores relative to a register set by mov rX,#0xB0000000 (GCR_BA),
    up to 48 instructions or until rX is redefined."""
    ins = list(CS_ARM.disasm(D[0:CODE_END_VA - BASE], BASE))
    out = []
    for k, i in enumerate(ins):
        if i.mnemonic in ('mov', 'movs') and i.op_str.endswith('#0xb0000000'):
            r = i.op_str.split(',')[0]
            offs = []
            for p in ins[k + 1:k + 48]:
                if p.mnemonic.startswith(('ldr', 'str')) and ('[%s,' % r in p.op_str or '[%s]' % r in p.op_str):
                    offs.append('%s@0x%X:%s' % (p.mnemonic, p.address, p.op_str.split('[', 1)[1].rstrip(']')))
                d = p.op_str.split(',')[0]
                if d == r and not p.mnemonic.startswith(('str', 'cmp', 'tst', 'teq', 'cmn')):
                    break
                if (p.mnemonic == 'pop' and 'pc' in p.op_str) or (p.mnemonic == 'bx' and p.op_str == 'lr'):
                    break                 # unconditional return only; popeq/bxeq do not end the path
            out.append((i.address, r, offs))
    return out


def tool120_stats():
    """CL-TOOL-REC-120 counted words of VA 0x1D4000-0x1F2000 (old 0x37C000-0x39A000)
    against the old code range 0x200000-0x2D0000; here the same words against both."""
    lo, hi = 0x1D4000, 0x1F2000
    ws = [w(a - BASE) for a in range(lo, hi, 4)]
    def cnt(a, b):
        return sum(1 for v in ws if a <= v < b)
    return {'span': '0x1D4000-0x1F2000', 'words': len(ws),
            'in_old_code_range_0x200000_0x2D0000': cnt(0x200000, 0x2D0000),
            'in_new_code_range_0x58000_0x120000': cnt(0x58000, CODE_END_VA),
            'aligned_new_code_addresses_hit': len({v for v in ws if BASE <= v < CODE_END_VA and v % 4 == 0}),
            'in_whole_image': cnt(BASE, END),
            'run_0x1F17A0': [hex(w(a - BASE)) for a in range(0x1F17A0, 0x1F17C8, 4)],
            'bytes_at_0x28A198_utf8': D[0x28A198 - BASE:0x28A198 - BASE + 24].decode('utf-8', 'replace').replace('\x00', '.'),
            'run_0x1DEFC0': [hex(w(a - BASE)) for a in range(0x1DEFC0, 0x1DEFE8, 4)]}


def main():
    out_dir = None
    if '--out' in sys.argv:
        out_dir = sys.argv[sys.argv.index('--out') + 1]
    lines, raw = [], {'app': APP, 'size': N, 'base': hex(BASE), 'controls': [], 'queries': []}
    p = lines.append
    p('neg_recheck.py -- negative findings from the old base, re-run in VA = file + 0x58000')
    p('APP.bin %d bytes; ARM ldr pool loads %d words, Thumb ldr %d' % (N, len(LDR_ARM), len(LDR_THUMB)))
    p('\n== Positive controls ==')
    ok_all = True
    for mode, what, got, ok in controls():
        p('  %-9s %-4s %s -> %s' % (mode, 'PASS' if ok else 'FAIL', what, got))
        raw['controls'].append({'mode': mode, 'case': what, 'got': got, 'pass': ok})
        ok_all &= ok
    p('  all controls pass: %s' % ok_all)
    for claim, label, lo, hi, tptr, argregs in QUERIES:
        res = query(lo, hi, thumb_ptr=tptr)
        c = counts(res)
        p('\n== %s -- %s ==' % (claim, label))
        p('  counts: ' + ', '.join('%s=%s' % kv for kv in c.items()))
        for e in res['lit'] + res.get('lit_thumbptr', []):
            p('  lit   file+0x%X va 0x%X = 0x%X  %s %s' % (e['file'], e['va'], e['value'], e['kind'],
              ' '.join('0x%X' % x for x in e['loaded_by'])))
        for e in res['imm']:
            p('  imm   va 0x%X %08X -> 0x%X [%s] %s' % (e['va'], e['word'], e['value'], e['region'],
              (disasm_at(e['file']) or ['?'])[0]))
        for e in res['adr']:
            p('  adr   va 0x%X -> 0x%X [%s]' % (e['va'], e['value'], e['region']))
        for e in res['chain']:
            p('  chain va 0x%X..0x%X -> 0x%X [%s]' % (e['va'], e['end'], e['value'], e['region']))
        for e in res['bl']:
            args = call_args(e['file'], argregs) if argregs and e['kind'].startswith('arm-bl') else {}
            e['args'] = args
            p('  bl    va 0x%X %s [%s] %s' % (e['va'], e['kind'], e['region'],
              ' '.join('%s=%s' % kv for kv in args.items())))
        raw['queries'].append({'claim': claim, 'label': label, 'lo': hex(lo),
                               'hi': hex(hi if hi else lo + 1), 'counts': c, 'hits': res})
    p('\n== CL-FIRMWARE-REC-113 -- indirect calls through a table slot (ldr rX,[rY,#off]; blx rX) ==')
    raw['indirect'] = {}
    for off in (4, 8, 0x10, 0x1C):
        ic = indirect_calls_via(off)
        raw['indirect'][hex(off)] = [(hex(a), hex(b)) for a, b in ic]
        la = sorted({a for a, b in ic})
        p('  #%s: %d ldr sites feeding %d blx %s' % (hex(off), len(la), len(ic), ' '.join('0x%X' % a for a in la)))
    p('\n== CL-HARDWARE-REC-005 -- accesses relative to mov rX,#0xB0000000 (GCR_BA; GPBFUN = +0x84) ==')
    raw['gcr'] = []
    for a, r, offs in gcr_offsets():
        raw['gcr'].append({'mov': hex(a), 'reg': r, 'accesses': offs})
        p('  0x%X %s: %s' % (a, r, ' '.join(offs)))
    p('\n== CL-TOOL-REC-120 -- pool-word statistics in the right base ==')
    raw['tool120'] = tool120_stats()
    for k, v in raw['tool120'].items():
        p('  %s: %s' % (k, v))
    txt = '\n'.join(lines)
    print(txt)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        open(os.path.join(out_dir, 'report.txt'), 'w').write(txt + '\n')
        json.dump(raw, open(os.path.join(out_dir, 'raw.json'), 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
