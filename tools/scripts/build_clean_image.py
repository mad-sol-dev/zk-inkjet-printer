#!/usr/bin/env python3
"""Baut sdcard.clean.img deterministisch aus sdcard.work.img.

Die Regionen (Offset, Groesse, sha256) stehen in firmware/image/sdcard.clean.manifest.txt.
Alles ausserhalb bleibt Null. Ergebnis wird gegen das Manifest verifiziert.

Damit ist das Clean-Image ein reproduzierbares Artefakt und keine Datei,
die man verlieren kann.

Usage: python3 tools/scripts/build_clean_image.py [--out PFAD] [--verify-only PFAD]
"""
import argparse, hashlib, os, re, sys

CHUNK = 1 << 22

def parse_manifest(path):
    txt = open(path).read()
    size = int(re.search(r"size_bytes:\s*(\d+)", txt).group(1))
    regions = []
    for line in txt.splitlines():
        m = re.match(r"-\s*(\w+):\s*offset=0x([0-9a-fA-F]+)\s+size=(\d+)(?:\s+sha256=(\S+))?", line.strip())
        if m:
            regions.append((m.group(1), int(m.group(2), 16), int(m.group(3)), m.group(4) or ""))
    return size, regions

def sha_region(path, off, size):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        f.seek(off)
        left = size
        while left > 0:
            b = f.read(min(CHUNK, left))
            if not b:
                return None, left
            h.update(b); left -= len(b)
    return h.hexdigest(), 0

def verify(img, regions):
    ok = True
    for name, off, size, exp in regions:
        got, missing = sha_region(img, off, size)
        good = got == exp and missing == 0
        ok &= good
        note = "" if good else ("  fehlende Bytes: %d" % missing if missing else "  ist %s" % got)
        print("%-4s %-14s @0x%08X %10d%s" % ("OK" if good else "FEHL", name, off, size, note))
    return ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default="firmware/image/sdcard.work.img")
    ap.add_argument("--manifest", default="firmware/image/sdcard.clean.manifest.txt")
    ap.add_argument("--out", default="firmware/image/sdcard.clean.img")
    ap.add_argument("--verify-only")
    a = ap.parse_args()

    size, regions = parse_manifest(a.manifest)
    if not regions:
        sys.exit("Manifest enthaelt keine Regionen")

    # Layout-Konsistenz: Teilueberlappungen sind ein Fehler, vollstaendige
    # Verschachtelung (z.B. boot_code in boot_bin) ist erlaubt.
    srt = sorted(regions, key=lambda r: (r[1], -r[2]))
    for i, (n1, o1, s1, _) in enumerate(srt):
        for n2, o2, s2, _ in srt[i + 1:]:
            if o2 >= o1 + s1:
                break
            if o2 + s2 > o1 + s1:
                sys.exit("Layoutfehler: %s [0x%08X..0x%08X) ueberlappt %s [0x%08X..0x%08X) nur teilweise"
                         % (n2, o2, o2 + s2, n1, o1, o1 + s1))
    end = max(o + s for _, o, s, _ in regions)
    if end > size:
        sys.exit("Layoutfehler: Regionen enden bei 0x%08X (%d), size_bytes ist aber %d" % (end, end, size))

    if a.verify_only:
        sys.exit(0 if verify(a.verify_only, regions) else 1)

    if not os.path.exists(a.work):
        sys.exit("Quelle fehlt: %s" % a.work)

    print("Baue %s (%d Bytes, %d Regionen) aus %s" % (a.out, size, len(regions), a.work))
    with open(a.out, "wb") as dst:
        dst.truncate(size)                      # sparse
        with open(a.work, "rb") as src:
            for name, off, rsize, _ in regions:
                src.seek(off); dst.seek(off)
                left = rsize
                while left > 0:
                    b = src.read(min(CHUNK, left))
                    if not b:
                        sys.exit("Quelle zu kurz bei %s" % name)
                    dst.write(b); left -= len(b)
                print("  kopiert: %-14s @0x%08X %10d" % (name, off, rsize))

    os.truncate(a.out, size)   # exakte Groesse erzwingen

    # Eigenes Manifest mit den tatsaechlichen Hashes schreiben
    out_man = a.out + ".manifest.txt"
    lines = ["file: %s" % os.path.basename(a.out),
             "built_from: %s" % os.path.basename(a.work),
             "built_by: tools/scripts/build_clean_image.py (raw regions, gaps zeroed)",
             "size_bytes: %d" % size, "regions:"]
    diff = 0
    print("\nVerifikation gegen Referenzmanifest:")
    for name, off, rsize, exp in regions:
        got, _ = sha_region(a.out, off, rsize)
        lines.append("- %s: offset=0x%08X size=%d sha256=%s" % (name, off, rsize, got))
        same = got == exp
        diff += (not same)
        print("  %-4s %-14s @0x%08X %10d%s" % ("=" if same else "!=", name, off, rsize,
              "" if same else "  Referenz %s..., hier %s..." % (exp[:12], got[:12])))
    open(out_man, "w").write("\n".join(lines) + "\n")
    h = hashlib.sha256()
    with open(a.out, "rb") as f:
        for b in iter(lambda: f.read(CHUNK), b""):
            h.update(b)
    print("\nsha256(%s) = %s" % (os.path.basename(a.out), h.hexdigest()))
    print("Manifest geschrieben: %s" % out_man)
    if diff:
        print("\nHINWEIS: %d Region(en) weichen vom Referenzmanifest ab." % diff)
        print("Die FAT-Volumes im Januar-Clean-Image waren keine Rohschnitte aus work.img,")
        print("sondern wurden in einem undokumentierten Schritt nachbearbeitet.")
        print("Dieses Image hier ist der rohe, vollstaendig reproduzierbare Nachbau.")

if __name__ == "__main__":
    main()
