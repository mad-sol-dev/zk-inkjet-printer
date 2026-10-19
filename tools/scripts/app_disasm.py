#!/usr/bin/env python3
"""Listing and callers for APP.bin on the raw file, as one repeatable command.

Sessions kept writing their own capstone helper for the same two questions
(dis.py in 2026-10-14 and again 2026-10-18, 62 runs in one session), because
the bridge's disassemble_at shows the pool address of a pc-relative load but
not the value. Rule 11 in CLAUDE.md wants such results from a versioned
command; this is that command.

    python3 tools/scripts/app_disasm.py dis 0xC54D8 [N] [--thumb | --arm]
    python3 tools/scripts/app_disasm.py callers 0x8A730 [--args r0,r1]
    python3 tools/scripts/app_disasm.py --selftest

dis      N instructions from VA (default 24). Mode: an odd VA or --thumb means
         Thumb, --arm forces ARM, otherwise Thumb inside the Thumb runs of
         Ghidra's listing (bridge_recheck.THUMB_RUNS, a lower bound) and ARM
         elsewhere. pc-relative ldr and adr/add/sub Rd,pc,#imm get the pool
         address and the value, each value is named: string in the image,
         address in the image, Thumb pointer, MMIO register (from
         research/findings/n32903_registers.json), RW/ZI global below the
         image (CL-BOOT-REC-114).
callers  every reference to VA in the file: ARM B/BL/BLX (any condition, whole
         file), Thumb BL/BLX inside the Thumb runs, pool words holding VA or
         VA|1 with the ldr sites that load them, ADR and MOV/ORR chains. Each
         branch site names the nearest preceding push {..., lr} and warns if
         an unconditional return lies in between (a heuristic for the
         function start, not Ghidra's function). --args r0,r1 recovers
         constant register arguments before ARM BL.

Decoders come from neg_recheck.py (positive controls there) and
bridge_recheck.py; --selftest checks both commands against cases from the
register. VA = file offset + 0x58000 (CL-BOOT-REC-113). Run from the
repository root. Read-only.
"""
import json, os, re, struct, sys

APP_PATH = 'firmware/bin/ZK-INKJET-NANO-APP.bin'     # neg_recheck opens it relative to the cwd
try:
    with open(APP_PATH, 'rb') as _fh:
        if _fh.read(24).startswith(b'version https://git-lfs'):
            raise SystemExit('%s is a Git LFS pointer, not the image: run git lfs checkout '
                             '(seen in worktrees, 2026-10-18)' % APP_PATH)
except FileNotFoundError:
    raise SystemExit('%s not found: run from the repository root (firmware/)' % APP_PATH)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import neg_recheck as n  # noqa: E402
import bridge_recheck as b  # noqa: E402

D, N, BASE, END = n.D, n.N, n.BASE, n.END
RW_ZI_END = 0x44FC0                     # RW/ZI region the image sets up (CL-BOOT-REC-114)
REG_MAP = 'research/findings/n32903_registers.json'


def _registers():
    try:
        d = json.load(open(REG_MAP, encoding='utf-8'))
    except (OSError, ValueError):
        return {}, []
    regs = {}
    for e in d.get('entries', []):
        regs.setdefault(int(e['address'], 16), e['register_name'])
    bases = sorted({(int(e['address'], 16), e['register_name']) for e in d.get('base_addresses', [])})
    return regs, bases


REGS, BASES = _registers()


def in_thumb_runs(a):
    return any(s <= a < e for s, e in b.THUMB_RUNS)


def string_at(a, limit=48):
    """ASCII text at VA a, if it looks like a C string (>= 4 printable bytes)."""
    o = a - BASE
    if not 0 <= o < N:
        return None
    s = bytearray()
    for c in D[o:o + limit]:
        if c == 0:
            break
        if not (32 <= c < 127 or c in (9, 10, 13)):
            return None
        s.append(c)
    if len(s) < 4:
        return None
    return s.decode('ascii') + ('...' if len(s) == limit else '')


def name_value(v):
    """Short note on what a 32-bit value points at."""
    if 0xB0000000 <= v <= 0xBFFFFFFF:
        exact = [nm for a, nm in BASES if a == v]
        if exact:
            return 'MMIO %s%s' % (exact[0], (' = %s' % REGS[v]) if v in REGS else '')
        if v in REGS:
            return 'MMIO %s' % REGS[v]
        base = [(a, nm) for a, nm in BASES if a <= v < a + 0x1000]
        return 'MMIO %s+0x%X' % (base[-1][1], v - base[-1][0]) if base else 'MMIO'
    if BASE <= v < END:
        s = string_at(v)
        if s:
            return 'string "%s"' % s.replace('\n', '\\n').replace('\r', '\\r')
        if v & 1 and in_thumb_runs(v - 1):
            return 'Thumb pointer 0x%X' % (v - 1)
        return 'image file+0x%X' % (v - BASE)
    if v < RW_ZI_END:
        return 'RW/ZI address or constant'
    f = struct.unpack('<f', struct.pack('<I', v))[0]
    if 1e-3 <= abs(f) <= 1e6 and len(('%g' % f).replace('-', '').replace('.', '')) <= 4:
        return 'float %g' % f
    return ''


PC_LOAD = re.compile(r'\[pc(?:, #(-?0x[0-9a-f]+|-?\d+))?\]')
SIZES = {'ldr': 4, 'ldrh': 2, 'ldrsh': 2, 'ldrb': 1, 'ldrsb': 1}


def annotate(i, thumb):
    mn, ops = i.mnemonic, i.op_str
    pc = ((i.address + 4) & ~3) if thumb else i.address + 8
    m = PC_LOAD.search(ops)
    base_mn = re.sub(r'(eq|ne|cs|hs|cc|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le|al)$', '', mn.split('.')[0])
    if m and base_mn in SIZES:
        pool = pc + (int(m.group(1), 0) if m.group(1) else 0)
        o, size = pool - BASE, SIZES[base_mn]
        if not 0 <= o <= N - size:
            return '[0x%X] outside the image' % pool
        v = int.from_bytes(D[o:o + size], 'little')
        note = name_value(v) if size == 4 else ''
        return '[0x%X] = 0x%0*X%s' % (pool, 2 * size, v, ('  ' + note) if note else '')
    am = re.match(r'(\w+), (?:pc, )?#(-?0x[0-9a-f]+|-?\d+)$', ops)
    if am and (mn.startswith('adr') or (mn.startswith(('add', 'sub')) and ', pc, #' in ops)):
        imm = int(am.group(2), 0)
        t = pc + (-imm if mn.startswith('sub') else imm)
        note = name_value(t)
        return '-> 0x%X%s' % (t, ('  ' + note) if note else '')
    return ''


def dis(a, count=24, mode=None):
    """Lines of the listing from VA a; mode None/'arm'/'thumb'."""
    thumb = bool(a & 1) or mode == 'thumb' or (mode is None and in_thumb_runs(a & ~1))
    if mode == 'arm':
        thumb = False
    a &= ~1
    o = a - BASE
    if not 0 <= o < N:
        raise SystemExit('VA 0x%X is outside APP.bin (0x%X-0x%X)' % (a, BASE, END))
    cs = n.CS_THUMB if thumb else n.CS_ARM
    why = ('Thumb run of the listing' if in_thumb_runs(a) else 'forced') if thumb else \
          ('ARM outside the Thumb runs' if mode is None else 'forced')
    out = ['%s at VA 0x%X (file+0x%X), %s' % ('Thumb' if thumb else 'ARM', a, o, why)]
    for k, i in enumerate(cs.disasm(D[o:o + 4 * count + 4], a)):
        if k >= count:
            break
        raw = D[i.address - BASE:i.address - BASE + i.size]
        word = (' '.join(raw[k:k + 2][::-1].hex().upper() for k in range(0, len(raw), 2))
                if thumb else raw[::-1].hex().upper())
        note = annotate(i, thumb)
        out.append('0x%08X: %-8s %-7s %-28s%s' % (i.address, word, i.mnemonic, i.op_str,
                                                  ('  ; ' + note) if note else ''))
    return out


def prev_push(a, thumb):
    """Heuristic function start before VA a: the nearest push {..., lr} (also the
    one-register form str lr,[sp,#-4]!). Returns (push VA, VA of the last
    unconditional return between push and a, or None) -- a return in between
    means either an early exit or that a leaf function without push lies in
    between; the caller has to look. None if no push within reach."""
    o = a - BASE
    ret = None
    if thumb:
        for q in range(o - 2, max(0, o - 0x2000), -2):
            x = n.h(q)
            if x & 0xFF00 == 0xB500:
                return BASE + q, ret
            if ret is None and (x & 0xFF00 == 0xBD00 or x == 0x4770):
                ret = BASE + q
    else:
        for q in range(o - 4, max(0, o - 0x8000), -4):
            x = n.w(q)
            if x & 0xFFFF4000 == 0xE92D4000 or x == 0xE52DE004:    # stmdb sp!,{..lr} / str lr,[sp,#-4]!
                return BASE + q, ret
            if ret is None and (x & 0xFFFF8000 == 0xE8BD8000 or x in (0xE12FFF1E, 0xE49DF004)):
                ret = BASE + q
    return None


def callers(t, arg_regs=()):
    """All references to VA t; returns a dict of lists (VAs and kinds)."""
    t &= ~1
    res = {'arm_branch': [], 'thumb_branch': [], 'pool': [], 'adr': [], 'chain': []}
    for e in n.m_bl(t, t + 1):
        if e['kind'].startswith('arm'):
            e2 = {'va': e['va'], 'kind': e['kind'], 'push': prev_push(e['va'], False)}
            if arg_regs and e['kind'].startswith('arm-bl'):
                e2['args'] = n.call_args(e['file'], arg_regs)
            res['arm_branch'].append(e2)
    for e in b.thumb_bl(t, t + 1):
        res['thumb_branch'].append({'va': e['va'], 'kind': e['kind'], 'push': prev_push(e['va'], True)})
    for v in (t, t | 1):
        for e in n.m_lit(v, v + 1):
            loaders = [BASE + q for q in n.LDR_ARM.get(e['file'], [])] + b.LDR_THUMB_ALL.get(e['file'], [])
            res['pool'].append({'va': e['va'], 'value': v, 'loaded_by': sorted(loaders)})
    res['adr'] = [{'va': e['va']} for e in n.m_adr(t, t + 1)]
    res['chain'] = [{'va': e['va'], 'end': e['end']} for e in n.m_chain(t, t + 1)]
    return res


def callers_text(t, arg_regs=()):
    r = callers(t, arg_regs)
    out = ['references to VA 0x%X (file+0x%X): %d ARM branch, %d Thumb branch, %d pool word, '
           '%d adr, %d chain' % (t & ~1, (t & ~1) - BASE, len(r['arm_branch']), len(r['thumb_branch']),
                                 len(r['pool']), len(r['adr']), len(r['chain']))]
    for e in r['arm_branch'] + r['thumb_branch']:
        push = ''
        if e['push']:
            push = '  after push at 0x%X' % e['push'][0]
            if e['push'][1]:
                push += ' (return at 0x%X in between)' % e['push'][1]
        args = ('  ' + ' '.join('%s=%s' % kv for kv in e['args'].items())) if e.get('args') else ''
        out.append('  %-14s 0x%08X%s%s' % (e['kind'], e['va'], push, args))
    for e in r['pool']:
        out.append('  %-14s 0x%08X = 0x%X  loaded by %s' % ('pool', e['va'], e['value'],
                   ' '.join('0x%X' % x for x in e['loaded_by']) or 'nothing (data)'))
    for e in r['adr']:
        out.append('  %-14s 0x%08X' % ('adr', e['va']))
    for e in r['chain']:
        out.append('  %-14s 0x%08X..0x%X' % ('chain', e['va'], e['end']))
    return out


def selftest():
    """Both commands against cases from the register."""
    fails = 0

    def check(what, ok, got):
        nonlocal fails
        fails += not ok
        print('%s  %s -> %s' % ('PASS' if ok else 'FAIL', what, got))

    r = callers(0xC7BF8)
    got = {e['va'] for e in r['arm_branch'] if e['kind'] == 'arm-bl'}
    check('callers 0xC7BF8: bl at 0xB3120 and 0xB31CC (CL-HARDWARE-REC-109)',
          {0xB3120, 0xB31CC} <= got, sorted(hex(x) for x in got))
    r = callers(0x66AEC)
    got = {e['va'] for e in r['thumb_branch']}
    check('callers 0x66AEC: Thumb bl at 0x6475C (bridge_recheck control)', 0x6475C in got,
          sorted(hex(x) for x in got))
    r = callers(0x8A730)
    got = {e['va'] for e in r['arm_branch']}
    check('callers 0x8A730: four branches incl. 0xB5F90, 0xC52B4, 0xBC090 (CL-FIRMWARE-REC-124)',
          len(got) == 4 and {0xB5F90, 0xC52B4, 0xBC090} <= got, sorted(hex(x) for x in got))
    r = callers(0x8A7BC)
    got = {e['va'] for e in r['arm_branch'] if e['kind'].startswith('arm-bl')}
    check('callers 0x8A7BC: bl from 0x6A528, 0xB44B4, 0xBDFD0, 0xBDFD8, 0xC5390 (CL-FIRMWARE-REC-124)',
          got == {0x6A528, 0xB44B4, 0xBDFD0, 0xBDFD8, 0xC5390}, sorted(hex(x) for x in got))
    r = callers(0xB325C)
    check("callers 0xB325C: adr at 0xB316C (CL-HARDWARE-REC-109)", any(e['va'] == 0xB316C for e in r['adr']),
          [hex(e['va']) for e in r['adr']])
    r = callers(0x8A434)
    check('callers 0x8A434: 5 pool words (neg_recheck control)', len(r['pool']) == 5, len(r['pool']))
    lines = dis(0xB316C, 1)
    check("dis 0xB316C: adr names 'Please release the print key!'",
          'Please release the print key!' in lines[1], lines[1].strip())
    lines = dis(0x757F4, 16)
    hit = [l for l in lines if '= 0xB8008000' in l]
    check('dis 0x757F4: pool load of 0xB8008000 named as MMIO (CL-MMIO-REC-005)',
          bool(hit) and 'MMIO' in hit[0], hit[0].strip() if hit else lines[1:4])
    r = {e['va']: e['push'] for e in callers(0x8A730)['arm_branch']}
    check('callers 0x8A730: 0xC0870 in power-off 0xC0808 (str lr,[sp,#-4]!), 0xC52B4 in 0xC4CF8 '
          '(CL-FIRMWARE-REC-124, CL-BOOT-REC-123)',
          r.get(0xC0870, (0,))[0] == 0xC0808 and r.get(0xC52B4, (0,))[0] == 0xC4CF8,
          {hex(k): v and hex(v[0]) for k, v in r.items()})
    args = {e['va']: e['args'] for e in callers(0x8A7BC, ('r0',))['arm_branch'] if 'args' in e}
    check('callers 0x8A7BC --args r0: bl 0xBDFD0 has r0 = 0x78 (mov at 0xBDFC4, then only stores; '
          'before 2026-10-19 "str r0, [r4, #0x178]")', args.get(0xBDFD0, {}).get('r0') == '0x78',
          args.get(0xBDFD0))
    for mode, what, got, ok in n.call_args_controls():
        check('neg_recheck.call_args, ' + what, ok, got)
    lines = dis(0xC54D8, 1)
    check('dis 0xC54D8: pool value 0x40E00000 named float 7 (CL-FIRMWARE-REC-132)',
          'float 7' in lines[1], lines[1].strip())
    lines = dis(0x6475C, 2)
    check('dis 0x6475C: chosen as Thumb from the listing runs, BL shown as F002 F9C6',
          lines[0].startswith('Thumb') and 'F002 F9C6' in lines[1], lines[1].strip())
    print('\n%s' % ('All controls pass.' if not fails else '%d control(s) failed -- do not trust the output.'
                    % fails))
    return 1 if fails else 0


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0
    if argv[0] == '--selftest':
        return selftest()
    cmd, rest = argv[0], argv[1:]
    flags = [x for x in rest if x.startswith('--')]
    pos = [x for x in rest if not x.startswith('--')]
    if cmd == 'dis' and pos:
        mode = 'thumb' if '--thumb' in flags else 'arm' if '--arm' in flags else None
        count = int(pos[1], 0) if len(pos) > 1 else 24
        print('\n'.join(dis(int(pos[0], 16), count, mode)))
        return 0
    if cmd == 'callers' and pos:
        regs = ()
        if '--args' in rest:
            i = rest.index('--args')
            regs = tuple(rest[i + 1].split(',')) if i + 1 < len(rest) else ('r0', 'r1')
            pos = [x for x in pos if x != rest[i + 1]] if i + 1 < len(rest) else pos
        print('\n'.join(callers_text(int(pos[0], 16), regs)))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
