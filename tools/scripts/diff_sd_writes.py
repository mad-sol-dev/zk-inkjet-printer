#!/usr/bin/env python3
"""Vergleicht einen SD-Dump gegen das geflashte Referenzimage.

Zweck: nach dem Flashen eines Minimalimages und Benutzung des Geraets zeigen,
welche Bereiche die Firmware selbst geschrieben hat. Jeder Unterschied ist ein
Schreibzugriff - es gibt keine andere Quelle.

Usage: diff_sd_writes.py REFERENZ.img DUMP.img [--block 4096] [--json OUT]
"""
import argparse, json, sys, os

def regions(ref_path, dump_path, block):
    ref = open(ref_path, "rb"); dmp = open(dump_path, "rb")
    rsize = os.path.getsize(ref_path); dsize = os.path.getsize(dump_path)
    n = min(rsize, dsize)
    off = 0; runs = []; cur = None
    while off < n:
        a = ref.read(min(block, n - off)); b = dmp.read(len(a))
        if a != b:
            kind = "zero->data" if not a.strip(b"\x00") else ("data->zero" if not b.strip(b"\x00") else "changed")
            if cur and cur["end"] == off and cur["kind"] == kind:
                cur["end"] = off + len(a)
            else:
                if cur: runs.append(cur)
                cur = {"start": off, "end": off + len(a), "kind": kind}
        else:
            if cur: runs.append(cur); cur = None
        off += len(a)
    if cur: runs.append(cur)
    return runs, rsize, dsize

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference"); ap.add_argument("dump")
    ap.add_argument("--block", type=int, default=4096)
    ap.add_argument("--json")
    a = ap.parse_args()
    runs, rsize, dsize = regions(a.reference, a.dump, a.block)
    print("Referenz %d Bytes, Dump %d Bytes, Vergleich ueber %d Bytes"
          % (rsize, dsize, min(rsize, dsize)))
    print("Abweichende Bereiche: %d, zusammen %d Bytes\n"
          % (len(runs), sum(r["end"] - r["start"] for r in runs)))
    print("%-12s %-12s %10s  %s" % ("Start", "Ende", "Groesse", "Art"))
    for r in runs:
        print("0x%010X 0x%010X %10d  %s" % (r["start"], r["end"], r["end"] - r["start"], r["kind"]))
    if dsize > rsize:
        dmp = open(a.dump, "rb"); dmp.seek(rsize)
        nz = 0; off = rsize
        while True:
            b = dmp.read(1 << 22)
            if not b: break
            if b.strip(b"\x00"): nz += sum(1 for x in b if x)
        print("\nJenseits des Referenzimages (0x%X .. 0x%X): %d Nicht-Null-Bytes"
              % (rsize, dsize, nz))
        print("Achtung: die Karte ist groesser als das Image. Alles dahinter kann Altbestand sein.")
    if a.json:
        json.dump(runs, open(a.json, "w"), indent=1)
        print("\nJSON: %s" % a.json)

if __name__ == "__main__":
    main()
