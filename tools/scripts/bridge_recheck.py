#!/usr/bin/env python3
"""Re-check of findings that rest on Ghidra MCP bridge output from before the
bridge rework (GhidraMCPd plugin 1.3.66, 2026-10-11; run_script reports Jython
errors only from 1.3.71, CL-TOOL-REC-124), and of the Thumb window used by
tools/scripts/neg_recheck.py.

Thumb ranges: neg_recheck.py decodes Thumb BL pairs and Thumb ldr only in
file+0x10000-0x1FFFF (CL-BOOT-REC-016). Ghidra's listing (tools/scripts/ghidra/
thumb_ranges.py, dry run 2026-10-17, 10691 Thumb instructions, 208 Thumb
function entries) has Thumb code elsewhere; THUMB_RUNS below is its output.
Part 1 repeats every neg_recheck.py query with Thumb decoding over those runs
and prints only what the old window missed.

Part 2 re-runs the bridge-era rows of this session, each with a positive
control. Read-only; with --out DIR it writes report.txt and raw.json there.

    python3 tools/scripts/bridge_recheck.py [--out DIR]
"""
import json, os, re, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import neg_recheck as n  # noqa: E402

D, N, BASE = n.D, n.N, n.BASE

# Ghidra TMode=1 runs (VA), gap > 256 bytes splits; thumb_ranges.py s256.
THUMB_RUNS = [
    (0x0005820C, 0x000582E4), (0x0006474C, 0x0006490A), (0x00064C7C, 0x00065DBC),
    (0x00066288, 0x0006676A), (0x00066A58, 0x00069B72), (0x0006A50C, 0x0006A520),
    (0x0007F550, 0x0007FA04), (0x00081310, 0x00081DDC), (0x00081F18, 0x00081F62),
    (0x00084658, 0x00084664), (0x00085C24, 0x00085C32), (0x000A8E24, 0x000A8E40),
    (0x000AB058, 0x000AB078), (0x0011BA18, 0x0011BFF8), (0x0011D958, 0x0011D964),
    (0x0011F70E, 0x0011F712),
]
OLD_WINDOW = (BASE + 0x10000, BASE + 0x20000)


def in_old_window(a):
    return OLD_WINDOW[0] <= a < OLD_WINDOW[1]


def thumb_bl(lo, hi):
    """Thumb BL/BLX pairs inside THUMB_RUNS whose target lies in [lo, hi)."""
    out = []
    for s, e in THUMB_RUNS:
        for a in range(s & ~1, e - 2, 2):
            o = a - BASE
            x, y = n.h(o), n.h(o + 2)
            if x >> 11 == 0b11110 and y >> 11 in (0b11111, 0b11101):
                off = (n._sx(x & 0x7FF, 11) << 12) | ((y & 0x7FF) << 1)
                t = a + 4 + off
                kind = 'thumb-bl'
                if y >> 11 == 0b11101:
                    t &= ~3
                    kind = 'thumb-blx'
                if lo <= t < hi:
                    out.append({'va': a, 'target': t, 'kind': kind, 'old_window': in_old_window(a)})
    return out


def thumb_ldr_targets():
    """file offset of pool word -> Thumb ldr sites (VA), over THUMB_RUNS."""
    res = {}
    for s, e in THUMB_RUNS:
        for a in range(s & ~1, e, 2):
            x = n.h(a - BASE)
            if x >> 11 == 0b01001:
                t = ((a + 4) & ~3) + ((x & 0xFF) << 2) - BASE
                res.setdefault(t, []).append(a)
    return res


LDR_THUMB_ALL = thumb_ldr_targets()


def part1_thumb(p, raw):
    p('== Part 1: neg_recheck.py queries with Thumb decoding over the Ghidra Thumb runs ==')
    p('  Thumb ldr pool loads: old window %d words, Ghidra runs %d words'
      % (len(n.LDR_THUMB), len(LDR_THUMB_ALL)))
    # positive control: Ghidra lists 0x6475C (Thumb, file+0xC75C) as the one call to FUN_00066aec
    ctrl = thumb_bl(0x66AEC, 0x66AED)
    ok = any(e['va'] == 0x6475C and not e['old_window'] for e in ctrl)
    p('  control  %s Thumb bl 0x6475C -> FUN_00066aec, outside the old window: %s'
      % ('PASS' if ok else 'FAIL', [(hex(e['va']), e['kind']) for e in ctrl]))
    raw['thumb_control'] = {'pass': ok, 'hits': ctrl}
    raw['thumb_delta'] = []
    for claim, label, lo, hi, tptr, _ in n.QUERIES:
        hi = lo + 1 if hi is None else hi
        new_bl = [e for e in thumb_bl(lo, hi) + (thumb_bl(lo | 1, (lo | 1) + 1) if tptr else [])
                  if not e['old_window']]
        lits = n.m_lit(lo, hi) + (n.m_lit(lo | 1, hi | 1) if tptr and hi == lo + 1 else [])
        new_ldr = [(e['va'], [hex(q) for q in LDR_THUMB_ALL[e['file']]]) for e in lits
                   if e['kind'] == 'data' and e['file'] in LDR_THUMB_ALL]
        raw['thumb_delta'].append({'claim': claim, 'label': label, 'bl': new_bl,
                                   'ldr': [(hex(a), q) for a, q in new_ldr]})
        if new_bl or new_ldr:
            p('  %s -- %s:' % (claim, label))
            for e in new_bl:
                p('    NEW %s at 0x%X -> 0x%X' % (e['kind'], e['va'], e['target']))
            for a, q in new_ldr:
                p('    NEW thumb ldr of pool word 0x%X at %s (was classified data)' % (a, ' '.join(q)))
    p('  queries without a new hit: %d of %d'
      % (sum(1 for d in raw['thumb_delta'] if not d['bl'] and not d['ldr']), len(n.QUERIES)))


def callers(t, thumb_ptr=True):
    r = n.query(t, thumb_ptr=thumb_ptr)
    tb = [e for e in thumb_bl(t, t + 1) if not e['old_window']]
    return r, tb


def show_callers(p, label, t, argregs=()):
    r, tb = callers(t)
    c = n.counts(r)
    p('  %s: bl=%d (+%d Thumb outside the old window), lit=%d, lit_thumbptr=%d, adr=%d'
      % (label, c['bl'], len(tb), c['lit'], c.get('lit_thumbptr', 0), c['adr']))
    for e in r['bl']:
        a = n.call_args(e['file'], argregs) if argregs and e['kind'].startswith('arm-bl') else {}
        p('    %s 0x%X %s' % (e['kind'], e['va'], ' '.join('%s=%s' % kv for kv in a.items())))
    for e in tb:
        p('    %s 0x%X' % (e['kind'], e['va']))
    for e in r['lit'] + r.get('lit_thumbptr', []):
        p('    lit 0x%X %s %s' % (e['va'], e['kind'], ' '.join(hex(x) for x in e['loaded_by'])))
    return {'counts': c, 'bl': [(hex(e['va']), e['kind']) for e in r['bl']] + [(hex(e['va']), e['kind']) for e in tb]}


def part2(p, raw):
    out = raw['part2'] = {}
    p('\n== Part 2: bridge-era rows ==')
    p('  controls of neg_recheck.py: %s' % ', '.join('%s=%s' % (m, 'PASS' if ok else 'FAIL')
                                                      for m, _, _, ok in n.controls()))

    p('\n-- CL-USB-REC-117 (2026-08-20, old base): WRITE path --')
    p('  control: the three known dispatch sites 0xCF86C/0xCF888/0xCF8B0 must appear')
    out['USB-117'] = {
        'data_phase_0xD0BB0': show_callers(p, 'mscdWt10_Command 0xD0BB0 (old msc_write_data_phase_278bb0)', 0xD0BB0),
        'lun_write_0x74A60': show_callers(p, 'usb_lun_write_blocks 0x74A60', 0x74A60),
        'literal_0x74AAC': hex(n.w(0x74AAC - BASE)),
        'signature_0xCFEC8': hex(n.w(0xCFEC8 - BASE)),
    }
    p('  literal 0x74AAC = %s, CBW signature 0xCFEC8 = %s'
      % (out['USB-117']['literal_0x74AAC'], out['USB-117']['signature_0xCFEC8']))
    pads = {}
    for lo, ln in ((0xCF5D0, 2276), (0xD0BB0, 300), (0x74A60, 76)):
        pads[hex(lo)] = [hex(a) for a in range(lo, lo + ln, 4)
                         if n.w(a - BASE) in (0, 0xE1A00000, 0xE320F000, 0xFFFFFFFF)]
    out['USB-117']['nop_or_zero_words'] = pads
    p('  nop/zero words inside dispatcher, data phase, lun_write: %s' % pads)

    p('\n-- CL-FIRMWARE-REC-118 (2026-10-12, aufrufer.py = Ghidra xrefs, a lower bound) --')
    out['FIRMWARE-118'] = {
        'sysInstallISR': show_callers(p, 'sysInstallISR 0xF9E88', 0xF9E88, ('r0', 'r1')),
        'sysEnableInterrupt': show_callers(p, 'sysEnableInterrupt 0xF99D0', 0xF99D0, ('r0',)),
        'gpio_cfg': show_callers(p, 'FUN_00089F34 GPIO config', 0x89F34, ('r0', 'r1', 'r2')),
    }
    p('  the b at 0xB2BAC (in 0xB2B94-0xB2BBF, no Ghidra function):')
    for line in n.disasm_at(0xB2B94 - BASE, 7):
        p('    ' + line)

    p('\n-- CL-DISPLAY-REC-004 (2026-08-31): call sites of the SPI0 display primitives --')
    p('  the row counted BL with condition AL (0xEB) only; here every condition, B and Thumb')
    out['DISPLAY-004'] = {
        'cmd_0xC7D90': show_callers(p, 'FUN_000c7d90 (old 0x26FD90)', 0xC7D90),
        'data_0xC7DD4': show_callers(p, 'FUN_000c7dd4 (old 0x26FDD4)', 0xC7DD4),
        'dc_0xC7D70': show_callers(p, 'FUN_000c7d70 (old 0x26FD70)', 0xC7D70),
    }

    p('\n-- CL-STORAGE-REC-103 (RE-KB 2026-01): only 0:/ and 3:/ --')
    st = {}
    for s in ('0:/', '3:/', '1:/', '2:/', '4:/', '0:\\', '1:\\', '2:\\', '3:\\', '%d:/', '%c:/', '%s:/'):
        for enc in ('ascii', 'utf-16-le'):
            st['%s %s' % (s, enc)] = len(re.findall(re.escape(s.encode(enc)), D))
    out['STORAGE-103'] = st
    drive_ok = ('0:/ ascii', '3:/ ascii', '3:\\ ascii')
    p('  controls 0:/ and 3:/ (ascii) must be > 0: %s' % {k: v for k, v in st.items() if v})
    p('  3:\\ is "3:\\inkjet-lite-vadj-sample.csv" (drive 3 as well)')
    p('  all other patterns: %s' % ('0' if all(v == 0 for k, v in st.items() if k not in drive_ok)
                                    else 'HITS'))

    p('\n-- CL-BOOT-REC-017/-018 (ghidra-v1, 2025): "287-entry handler table" at 0x22BE00 (old 0x3D3E00) --')
    o = 0x22BE00 - BASE

    def rec(i):
        return struct.unpack_from('<III', D, o + 12 * i)

    def ok(r):
        return BASE <= r[0] < n.END and BASE <= r[1] < n.END and r[2] < 16

    fwd = 0
    while ok(rec(fwd)):
        fwd += 1
    back = 0
    while ok(rec(-back - 1)):
        back += 1
    recs = [rec(i) for i in range(-back, fwd)]

    def cstr(va):
        b = D[va - BASE:va - BASE + 32]
        return b.split(b'\0', 1)[0].decode('ascii', 'replace')
    asc = sum(1 for a, _, _ in recs if re.fullmatch(r'[a-z]{1,24}', cstr(a)))
    code_a = sum(1 for a, _, _ in recs if a < n.CODE_END_VA)
    p('  0x22BE00 starts a run of %d (pointer, pointer, count<16) records forward and %d before it'
      % (fwd, back))
    p('  first fields: %d of %d point at a lowercase ASCII word (pinyin), %d into code'
      % (asc, len(recs), code_a))
    p('  run 0x%X-0x%X, first word "%s", last "%s"'
      % (0x22BE00 - 12 * back, 0x22BE00 + 12 * fwd, cstr(recs[0][0]), cstr(recs[-1][0])))
    for a, b, c in recs[back:back + 4]:
        q = n.w(b - BASE)
        p('    0x%X "%s"  0x%X -> 0x%X "%s"  %d' % (a, cstr(a), b, q,
          D[q - BASE:q - BASE + 24].split(b'\0', 1)[0].decode('utf-8', 'replace'), c))
    p('  old view (VA = file + 0x200000): first field 0x%X was file+0x%X, i.e. code at today\'s 0x%X'
      % (recs[back][0], recs[back][0] - 0x200000, recs[back][0] - 0x200000 + BASE))
    ctrl = [n.w(0x120F40 - BASE + 4 * i) for i in range(8)]
    p('  control, a real function table (I2C ops 0x120F40, CL-FIRMWARE-REC-127): %s'
      % ' '.join(hex(x) for x in ctrl))
    out['BOOT-017'] = {'forward': fwd, 'before': back, 'pinyin_first_field': asc, 'into_code': code_a,
                       'sample': [(hex(a), cstr(a), hex(b), c) for a, b, c in recs[back:back + 4]],
                       'control_0x120F40': [hex(x) for x in ctrl]}
    show = out['BOOT-017']['orchestrator'] = show_callers(p, 'old "upgrade orchestrator" 0x66AEC (Thumb)', 0x66AEC)
    del show


def main():
    out_dir = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    lines, raw = [], {'app': n.APP, 'thumb_runs': [(hex(a), hex(b)) for a, b in THUMB_RUNS]}
    p = lines.append
    p('bridge_recheck.py -- bridge-era findings and the Thumb window, VA = file + 0x58000')
    part1_thumb(p, raw)
    part2(p, raw)
    txt = '\n'.join(lines)
    print(txt)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        open(os.path.join(out_dir, 'report.txt'), 'w').write(txt + '\n')
        json.dump(raw, open(os.path.join(out_dir, 'raw.json'), 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
