#!/usr/bin/env python3
"""Re-check of the card negatives CL-STORAGE-REC-118, -119 and -120 with
positive controls (CL-TOOL-REC-130 Next_Test). Read-only; with --out DIR it
writes report.txt and raw.json there.

  A  CL-STORAGE-REC-118: hidden_sectors of volume 0 and the sector before it
     (card 0x03FFFE00) in every dump; the write measurement (minimal image
     against the dumps taken after using the device) with its control, i.e.
     that the same diff does show the firmware's own writes; and the sector
     number / byte address of that sector searched in APP.bin in all modes.
  B  CL-STORAGE-REC-119/-120: root directory of volume 0 (sdcard.work.img)
     with long names, live and deleted; cluster sharing; the bytes at cluster
     2580 against firmware/resources/ZK-INKJET-GUI-RES.zkml, and whether that
     file is one font or the clusters 2580.. carved in a row (font headers at
     cluster boundaries, each live file read through its FAT chain; control:
     ZK-INKJET-RES-HW.zkml against its chain); each live font name searched in
     APP.bin and in the resource files, ASCII and UTF-16, case-insensitive,
     with fonts the firmware does name as control; the font path table.

    python3 tools/scripts/card_recheck.py [--out DIR]
"""
import json, os, re, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import neg_recheck as n  # noqa: E402

IMG = 'firmware/image'
WORK = os.path.join(IMG, 'sdcard.work.img')
MINIMAL = os.path.join(IMG, 'sdcard.minimal.img')
AFTER = sorted(f for f in os.listdir(IMG) if f.startswith('sdcard.after') and f.endswith('-minimal.img'))
OTHER = ['sdcard.work.img', 'sdcard.clean_after_boot.img', 'sdcard.clean-raw.img', 'sdcard.minimal.img']
VOL0 = 0x04000000
BEFORE = VOL0 - 512
RES = ['firmware/resources/ZK-INKJET-GUI-RES.zkml', 'firmware/resources/ZK-INKJET-RES-HW.zkml',
       'firmware/resources/ZK-INKJET-UI-QVGA.bin', 'firmware/bin/ZK-INKJET-NANO-BOOT.bin']


def rd(path, off, ln):
    with open(path, 'rb') as f:
        f.seek(off)
        return f.read(ln)


def bpb(path):
    b = rd(path, VOL0, 512)
    if len(b) < 512 or b[510:512] != b'\x55\xaa':
        return None
    bps, spc, res, nf, rootn, _, _, fsz = struct.unpack_from('<HBHBHHBH', b, 11)
    hidden = struct.unpack_from('<I', b, 28)[0]
    return {'bps': bps, 'spc': spc, 'res': res, 'nfat': nf, 'root': rootn, 'fatsz': fsz, 'hidden': hidden}


def diff_runs(a, b, block=4096, chunk=1 << 22):
    """4 KiB blocks that differ between two images (over the shorter length)."""
    runs = []
    with open(a, 'rb') as fa, open(b, 'rb') as fb:
        off = 0
        while True:
            x, y = fa.read(chunk), fb.read(chunk)
            m = min(len(x), len(y))
            if m == 0:
                break
            if x[:m] != y[:m]:
                for k in range(0, m, block):
                    if x[k:k + block] != y[k:k + block]:
                        s = off + k
                        if runs and runs[-1][1] == s:
                            runs[-1][1] = s + block
                        else:
                            runs.append([s, s + block])
            off += m
            if m < chunk:
                break
    return runs


def part_a(p, raw):
    out = raw['A'] = {}
    p('== A: CL-STORAGE-REC-118 -- volume 0 hidden_sectors and card sector 0x03FFFE00 ==')
    for f in OTHER + AFTER:
        path = os.path.join(IMG, f)
        if not os.path.exists(path):
            continue
        b = bpb(path)
        s = rd(path, BEFORE, 512)
        z = (len(s) == 512 and not any(s))
        out[f] = {'bpb': b, 'sector_0x3FFFE00_zero': z}
        p('  %-52s hidden=%s  0x03FFFE00 %s' % (f, b and b['hidden'], 'zero' if z else 'NOT ZERO'))
    p('\n  write measurement: %s against each dump (4 KiB blocks)' % os.path.basename(MINIMAL))
    p('  control: the same diff must show the firmware\'s own writes (settings, store slots)')
    out['diff'] = {}
    for f in AFTER:
        runs = diff_runs(MINIMAL, os.path.join(IMG, f))
        hit = [r for r in runs if r[0] <= BEFORE < r[1]]
        out['diff'][f] = {'runs': [(hex(s), hex(e)) for s, e in runs], 'touches_0x3FFFE00': bool(hit)}
        p('  %-52s %3d changed runs, first %s; 0x03FFFE00 %s'
          % (f, len(runs), ', '.join('%X-%X' % (s, e) for s, e in runs[:4]),
             'CHANGED' if hit else 'unchanged'))
    p('\n  APP.bin, all modes: sector 0x1FFFF and byte address 0x3FFFE00 of that sector;')
    p('  controls: 0x2A614000 (volume 3 MBR, literal at 0x74AAC, CL-USB-REC-117);')
    p('  0x4000000 / 0x20000 (volume 0 base) are common constants: counts only')
    out['code'] = {}
    for label, v in (('control vol3 MBR 0x2A614000', 0x2A614000), ('sector 0x1FFFF', 0x1FFFF),
                     ('byte 0x3FFFE00', 0x3FFFE00), ('vol0 base 0x4000000', 0x4000000),
                     ('vol0 sector 0x20000', 0x20000)):
        r = n.query(v)
        c = n.counts(r)
        out['code'][label] = {'counts': c,
                              'lit': [(hex(e['va']), e['kind']) for e in r['lit']],
                              'imm': [(hex(e['va']), e['region']) for e in r['imm']],
                              'chain': [(hex(e['va']), e['region']) for e in r['chain']]}
        p('  %-28s lit=%d (loaded %d) imm=%d adr=%d chain=%d'
          % (label, c['lit'], c['lit_loaded'], c['imm'], c['adr'], c['chain']))
        if label.startswith('vol0'):
            continue                      # common constants; counts only, no conclusion
        for e in r['lit']:
            p('      lit 0x%X %s %s' % (e['va'], e['kind'], ' '.join(hex(x) for x in e['loaded_by'])))
        for e in r['imm'] + r['chain']:
            if e['region'] == 'code':
                p('      %s 0x%X %s' % ('imm' if 'word' in e else 'chain', e['va'],
                                       (n.disasm_at(e['file']) or ['?'])[0]))


def root_dir(path):
    b = bpb(path)
    root = VOL0 + (b['res'] + b['nfat'] * b['fatsz']) * b['bps']
    data = root + b['root'] * 32
    cl = b['spc'] * b['bps']
    ents, lfn = [], []
    d = rd(path, root, b['root'] * 32)
    for i in range(b['root']):
        e = d[32 * i:32 * i + 32]
        if e[0] == 0:
            break
        if e[11] == 0x0F:
            lfn.insert(0, e)
            continue
        long = ''
        if lfn:
            s = b''.join(x[1:11] + x[14:26] + x[28:32] for x in lfn)
            long = s.decode('utf-16-le', 'replace').split('\x00')[0]
        lfn = []
        short = (e[0:8].decode('latin-1').rstrip() + '.' + e[8:11].decode('latin-1').rstrip()).rstrip('.')
        ents.append({'deleted': e[0] == 0xE5, 'dir': bool(e[11] & 0x10), 'short': short,
                     'long': long, 'cluster': struct.unpack_from('<H', e, 26)[0],
                     'size': struct.unpack_from('<I', e, 28)[0]})
    fat = rd(path, VOL0 + b['res'] * b['bps'], b['fatsz'] * b['bps'])
    return ents, data, cl, fat


def ttf_extent(b):
    """Tables in a TrueType header and where the last one ends."""
    nt = struct.unpack_from('>H', b, 4)[0]
    end = 0
    for i in range(nt):
        _, _, off, ln = struct.unpack_from('>4sIII', b, 12 + 16 * i)
        end = max(end, off + ln)
    return nt, end


def chain(fat, c, limit=100000):
    out = []
    while 2 <= c < 0xFFF8 and len(out) < limit:
        out.append(c)
        c = struct.unpack_from('<H', fat, 2 * c)[0]
    return out


def part_b(p, raw):
    out = raw['B'] = {}
    p('\n== B: CL-STORAGE-REC-119/-120 -- volume 0 root directory (sdcard.work.img) ==')
    ents, data, cl, fat = root_dir(WORK)
    out['entries'] = ents
    for e in ents:
        p('  %-4s %-14s %-34s cl %5d  %9d' % ('DEL' if e['deleted'] else 'live', e['short'],
                                              e['long'], e['cluster'], e['size']))
    p('\n  clusters named by a live and a deleted entry, with the first 4 bytes found there:')
    live = {e['cluster']: e for e in ents if not e['deleted'] and not e['dir']}
    out['shared'] = []
    for e in ents:
        if e['deleted'] and e['cluster'] in live:
            le = live[e['cluster']]
            head = rd(WORK, data + (e['cluster'] - 2) * cl, 4)
            ch = chain(fat, le['cluster'])
            need = -(-le['size'] // cl)
            out['shared'].append({'cluster': e['cluster'], 'live': le['long'] or le['short'],
                                  'deleted': e['long'] or e['short'], 'head': head.hex(),
                                  'live_chain_len': len(ch), 'live_needs': need})
            p('    cl %5d live %-22s deleted %-24s head %s  live chain %d of %d clusters'
              % (e['cluster'], le['long'] or le['short'], e['long'] or e['short'], head.hex(),
                 len(ch), need))
    p('    (a TrueType/OpenType file starts with 00010000, 74727565, 4f54544f or 74746366)')
    g = open('firmware/resources/ZK-INKJET-GUI-RES.zkml', 'rb').read()
    at = rd(WORK, data + (2580 - 2) * cl, len(g))
    eq = at == g
    out['gui_res_at_2580'] = {'card': hex(data + (2580 - 2) * cl), 'len': len(g), 'equal': eq}
    p('\n  cluster 2580 = card 0x%X: %d bytes %s firmware/resources/ZK-INKJET-GUI-RES.zkml'
      % (data + (2580 - 2) * cl, len(g), '==' if eq else '!='))
    p('  is that file one font, or the clusters 2580.. carved in a row? (control: a font\'s own')
    p('  table directory says where it ends; each live file read through its FAT chain)')
    nt, end = ttf_extent(g)
    magic = [k for k in range(0, len(g), cl) if g[k:k + 4] in (b'\0\1\0\0', b'OTTO', b'true', b'ttcf')]
    p('    the file\'s table directory: %d tables, last table ends at %d of %d bytes'
      % (nt, end, len(g)))
    p('    font headers at cluster boundaries: %s'
      % ', '.join('+0x%X (cluster %d)' % (k, 2580 + k // cl) for k in magic))
    out['gui_res_carve'] = {'tables_end': end, 'font_headers': [hex(k) for k in magic], 'files': []}
    for e in ents:
        if e['deleted'] or e['dir'] or not (2580 <= e['cluster'] < 2580 + -(-len(g) // cl)):
            continue
        ch = chain(fat, e['cluster'])
        b = b''.join(rd(WORK, data + (c - 2) * cl, cl) for c in ch)[:e['size']]
        off = (e['cluster'] - 2580) * cl
        same = g[off:off + e['size']] == b
        ont, oend = ttf_extent(b)
        out['gui_res_carve']['files'].append({'name': e['long'] or e['short'], 'offset': hex(off),
                                              'equal': same, 'tables_end': oend, 'size': e['size']})
        p('    live %-14s cluster %d = file+0x%06X, %d bytes: %s, its own tables end at %d'
          % (e['long'] or e['short'], e['cluster'], off, e['size'],
             'identical' if same else 'DIFFERENT', oend))
    r = open('firmware/resources/ZK-INKJET-RES-HW.zkml', 'rb').read()
    ch = chain(fat, 2549)
    rb = b''.join(rd(WORK, data + (c - 2) * cl, cl) for c in ch)[:len(r)]
    out['res_hw'] = {'chain': [ch[0], ch[-1], len(ch)], 'equal': rb == r}
    p('    control: firmware/resources/ZK-INKJET-RES-HW.zkml == live file through its FAT chain'
      ' (%d..%d, %d clusters): %s' % (ch[0], ch[-1], len(ch), rb == r))

    p('\n  font names in APP.bin and in the resource files (ASCII + UTF-16LE, case-insensitive)')
    app = n.D
    blobs = {'APP.bin': app}
    for r in RES:
        blobs[os.path.basename(r)] = open(r, 'rb').read()

    def hits(blob, stem):
        c = 0
        for enc in ('ascii', 'utf-16-le'):
            c += len(re.findall(re.escape(stem.encode(enc)), blob, re.I))
        return c
    out['names'] = {}
    for e in ents:
        if e['deleted'] or e['dir']:
            continue
        name = e['long'] or e['short']
        stem = name.rsplit('.', 1)[0]
        row = {k: hits(v, stem) for k, v in blobs.items()}
        sh = e['short'].rsplit('.', 1)[0]
        row['APP.bin short'] = hits(app, sh) if sh.lower() != stem.lower() else None
        out['names'][name] = row
        p('    %-28s %s' % (name, '  '.join('%s=%s' % (k, v) for k, v in row.items() if v is not None)))
    enum = {}
    for pat in ('*.ttf', '*.ttc', '*.otf', '*.*', '.ttf', '.ttc', '.otf', 'ttf', '0:/', '0:/user/font',
                'user/font', '%s.ttf'):
        enum[pat] = hits(app, pat)
    out['enumeration_patterns'] = enum
    p('\n  enumeration patterns in APP.bin: %s' % ', '.join('%s=%d' % kv for kv in enum.items()))
    i = app.find(b'\0Calibri\0') + 1
    lst = app[i - 8:i + 56].split(b'\0')
    p('  "Calibri" in APP.bin: VA 0x%X, in the list %s' % (i + n.BASE, [x.decode() for x in lst if x]))
    pt = []
    a = 0x12B094
    while True:
        v = n.w(a - n.BASE)
        if not (n.BASE <= v < n.END) or not app[v - n.BASE:v - n.BASE + 3] == b'0:/':
            break
        pt.append(app[v - n.BASE:v - n.BASE + 40].split(b'\0')[0].decode())
        a += 4
    out['calibri'] = {'label_va': hex(i + n.BASE), 'path_table_0x12B094': pt}
    p('  font path table 0x12B094 (ldr at 0xB501C, 0xB708C, 0xB71E0, 0xB96FC), %d entries: %s'
      % (len(pt), ', '.join(pt)))


def main():
    out_dir = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    lines, raw = [], {}
    p = lines.append
    p('card_recheck.py -- CL-STORAGE-REC-118/-119/-120, read-only, card addresses are image offsets')
    part_a(p, raw)
    part_b(p, raw)
    txt = '\n'.join(lines)
    print(txt)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        open(os.path.join(out_dir, 'report.txt'), 'w').write(txt + '\n')
        json.dump(raw, open(os.path.join(out_dir, 'raw.json'), 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
