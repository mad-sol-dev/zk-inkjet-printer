#!/usr/bin/env python3
"""Abdeckungspruefung: welche Altdokumente sind in TRUTH.csv nicht vertreten?

Methode: Jedes Quelldokument wird auf technische Fingerabdruecke reduziert --
Hex-Adressen, FUN_-Namen, Registernamen. Dann wird geprueft, ob diese
Fingerabdruecke irgendwo ankommen:

  A  direkt in research/TRUTH.csv                     -> geerntet
  B  nur in der docs_rebuild-Reconciliation           -> mittelbar geerntet
  C  nirgends                                          -> UNGEERNTET

Dokumente ohne technische Fingerabdruecke koennen so nicht beurteilt werden
und werden getrennt ausgewiesen.
"""
import csv, glob, json, os, re, sys
from collections import defaultdict

ROOT = "."
TOKEN = re.compile(r'0x[0-9A-Fa-f]{4,8}|FUN_[0-9A-Fa-f]{6,8}|\b[A-Z]{2,6}_BA\b')

def norm(t):
    if t.lower().startswith("0x"):
        return "0x%X" % int(t, 16)
    if t.upper().startswith("FUN_"):
        return "0x%X" % int(t[4:], 16)
    return t.upper()

def toks(text):
    return {norm(t) for t in TOKEN.findall(text)}

def read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""

def sources():
    pats = ["research/docs_rebuild/old_docs/**/*.md",
            "research/sessions/*.md",
            "research/*.md",
            "research/phase_a_sd_analysis/*.md",
            "research/findings/re_kb_archive/findings/*.json",
            "research/findings/.re_kb/findings/*.json",
            "*.md", "hardware/*.md", "hardware/**/*.md", "firmware/*.md", "tools/*.md"]
    out = []
    for p in pats:
        out += glob.glob(p, recursive=True)
    skip = ("research/TRUTH.md",)
    return sorted({p for p in out if os.path.isfile(p) and p not in skip})

def main():
    truth = read("research/TRUTH.csv")
    T = toks(truth)
    harvest = ""
    for p in ("research/docs_rebuild/claims/*.md", "research/docs_rebuild/evidence/*.md",
              "research/docs_rebuild/reconciliation/*.md", "research/docs_rebuild/CONFIDENCE_MATRIX.csv",
              "research/docs_rebuild/CLAIM_BACKLOG.md", "research/docs_rebuild/CLAIMS.md"):
        for f in glob.glob(p):
            harvest += read(f)
    H = toks(harvest)
    print("Fingerabdruecke in TRUTH.csv: %d, in der Reconciliation: %d\n" % (len(T), len(H)))

    rows = []
    for p in sources():
        S = toks(read(p))
        if not S:
            rows.append((p, 0, 0, 0, "keine Fingerabdruecke")); continue
        a = len(S & T); b = len(S & H - T)
        c = len(S - T - H)
        rows.append((p, len(S), a, b, c))

    unrated = [r for r in rows if r[4] == "keine Fingerabdruecke"]
    rated = [r for r in rows if r[4] != "keine Fingerabdruecke"]
    C = [r for r in rated if r[2] == 0 and r[3] == 0]
    B = [r for r in rated if r[2] == 0 and r[3] > 0]
    A = [r for r in rated if r[2] > 0]

    print("=" * 78)
    print("C  UNGEERNTET -- weder in TRUTH.csv noch in der Reconciliation (%d)" % len(C))
    for p, n, a, b, c in sorted(C, key=lambda r: -r[1]):
        print("   %4d Marker  %s" % (n, p))
    print()
    print("=" * 78)
    print("B  nur mittelbar, kein Marker direkt in TRUTH.csv (%d)" % len(B))
    for p, n, a, b, c in sorted(B, key=lambda r: -r[1])[:25]:
        print("   %4d Marker, %3d in Reconciliation  %s" % (n, b, p))
    if len(B) > 25: print("   ... %d weitere" % (len(B) - 25))
    print()
    print("=" * 78)
    print("A  direkt vertreten (%d) -- die zehn mit dem groessten Rest" % len(A))
    for p, n, a, b, c in sorted(A, key=lambda r: -r[4])[:10]:
        print("   %4d Marker, %3d in TRUTH, %3d nur Reconciliation, %3d nirgends  %s" % (n, a, b, c, p))
    print()
    print("Nicht beurteilbar (keine technischen Marker): %d" % len(unrated))
    for p, *_ in unrated[:12]: print("   ", p)
    if len(unrated) > 12: print("   ... %d weitere" % (len(unrated) - 12))

if __name__ == "__main__":
    main()
