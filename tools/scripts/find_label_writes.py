#!/usr/bin/env python3
"""Sucht nach einem am Geraet eingegebenen Text auf der SD-Karte und ordnet
ihn den Sektoren zu, die sich gegenueber dem Referenzimage geaendert haben.

Idee: Ein Diff sagt, WO die Firmware geschrieben hat. Die Textsuche sagt, WAS
davon der eingegebene Label-Inhalt ist. Zusammen ergibt das die Adresse und die
Kodierung, in der Label-Inhalt abgelegt wird.

Usage:
  find_label_writes.py REFERENZ.img DUMP.img TEXT [TEXT ...]
"""
import argparse, sys, os

STORE_BASE, STORE_STRIDE, STORE_N = 0x28800000, 0x4D000, 100
SETTINGS = 0x28000000
VOL3_MBR, VOL3 = 0x2A614000, 0x2A61BE00

def encodings(t):
    out = [("ascii", t.encode("ascii", "ignore"))]
    out.append(("utf-16-le", t.encode("utf-16-le")))
    out.append(("utf-16-be", t.encode("utf-16-be")))
    try: out.append(("gb2312", t.encode("gb2312")))
    except Exception: pass
    out.append(("ascii-upper", t.upper().encode("ascii", "ignore")))
    out.append(("ascii-lower", t.lower().encode("ascii", "ignore")))
    seen, uniq = set(), []
    for n, b in out:
        if b and b not in seen:
            seen.add(b); uniq.append((n, b))
    return uniq

def scan(path, pats, chunk=1 << 24):
    hits = []
    maxlen = max(len(b) for _, b in pats)
    f = open(path, "rb"); off = 0; prev = b""
    while True:
        blk = f.read(chunk)
        if not blk: break
        buf = prev + blk
        base = off - len(prev)
        for name, pat in pats:
            s = 0
            while True:
                i = buf.find(pat, s)
                if i < 0: break
                hits.append((base + i, name)); s = i + 1
        prev = buf[-maxlen:]; off += len(blk)
    return sorted(hits)

def region_of(o):
    if SETTINGS <= o < SETTINGS + 512: return "Settings-Sektor"
    if STORE_BASE <= o < STORE_BASE + STORE_N * STORE_STRIDE:
        i, r = divmod(o - STORE_BASE, STORE_STRIDE)
        return f"Speichereintrag {i}, +0x{r:X}" + ("  (Header-Sektor)" if r < 512 else "")
    if VOL3_MBR <= o < VOL3_MBR + 512: return "MBR der USB-Platte"
    if o >= VOL3: return f"Volume 3 (MINI) +0x{o - VOL3:X}"
    if 0x04000000 <= o < 0x24000000: return "Volume 0 (Fonts/Resourcen)"
    if 0x03000000 <= o < 0x0327511C: return "APP.bin im RAW"
    return "sonstiger RAW-Bereich"

def diff_sectors(ref, dmp, block=512):
    a = open(ref, "rb"); b = open(dmp, "rb")
    n = min(os.path.getsize(ref), os.path.getsize(dmp))
    out, off = [], 0
    while off < n:
        x = a.read(min(block, n - off)); y = b.read(len(x))
        if x != y: out.append(off)
        off += len(x)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference"); ap.add_argument("dump"); ap.add_argument("texts", nargs="+")
    a = ap.parse_args()

    changed = diff_sectors(a.reference, a.dump)
    print(f"Geaenderte Sektoren gegenueber dem Referenzimage: {len(changed)}\n")
    for o in changed:
        print("  0x%010X  %s" % (o, region_of(o)))

    print()
    for t in a.texts:
        pats = encodings(t)
        print("=" * 70)
        print(f'Suche nach "{t}"  ({", ".join(n for n, _ in pats)})')
        hits = scan(a.dump, pats)
        if not hits:
            print("  KEIN Treffer im Dump.")
            continue
        print(f"  {len(hits)} Treffer:")
        for o, enc in hits[:60]:
            sect = o & ~511
            mark = "  <-- in geaendertem Sektor" if sect in set(changed) else ""
            print("    0x%010X  %-12s %s%s" % (o, enc, region_of(o), mark))
        if len(hits) > 60: print(f"    ... {len(hits)-60} weitere")

if __name__ == "__main__":
    main()
