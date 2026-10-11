#!/usr/bin/env python3
"""Toleranter Vergleich der BSP-Funktionen mit APP.bin (CL-TOOL-REC-125).

Function ID findet nur unveraenderten Code. Dieses Skript sucht jede ARM-Funktion
aus den BSP-Objekten (ghidra_projects/fid/src) im ganzen Image, auch dort, wo
Ghidra noch keine Funktion kennt, und misst, wie viele Befehle uebereinstimmen.

Normalform eines 32-Bit-Worts (in Objekt und Image gleich angewandt):
  B/BL                      -> nur Bedingung und Opcode (Ziel ausgeblendet)
  LDR/STR Rd,[pc,#imm]      -> Offset ausgeblendet (Literalpool anders platziert)
  ADD/SUB Rd,pc,#imm (ADR)  -> Immediate ausgeblendet
Relokationsstellen im Objekt sind Joker. Treffer = Startadresse im Image, an der
die ersten vier Normalworte gleich sind; Aehnlichkeit = Anteil gleicher Worte
ueber die ganze Funktion. Ausgegeben werden Treffer ab --min (Standard 0.80) und
mit mindestens --worte Worten (Standard 12), je Funktion der beste.

Liest nur. Schreibt ghidra_projects/fid/normvergleich.csv.

  python3 tools/scripts/fid/normvergleich.py [--min 0.8] [--worte 12]
"""
import argparse
import csv
import glob
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bytevergleich import APP, BASIS, FID, elf_lesen  # noqa: E402

JOKER = None


def norm(w):
    if (w & 0x0E000000) == 0x0A000000:              # B, BL
        return w & 0xFF000000
    if (w & 0x0E5F0000) == 0x041F0000:              # LDR/STR literal
        return w & 0xFFFFF000
    if (w & 0x0FEF0000) in (0x028F0000, 0x024F0000):  # ADD/SUB Rd,pc,#imm
        return w & 0xFFFFF000
    return w


def objekt_funktionen(pfad):
    d, sek, syms, relok = elf_lesen(pfad)
    for name, (shndx, wert, groesse) in syms.items():
        if groesse < 16 or wert % 4 or groesse % 4:
            continue                                    # zu kurz oder Thumb
        s = sek[shndx]
        roh = d[s["off"] + wert:s["off"] + wert + groesse]
        rel = relok.get(shndx, set())
        worte = []
        for k in range(0, groesse, 4):
            if any(r in rel for r in range(wert + k, wert + k + 4)):
                worte.append(JOKER)
            else:
                worte.append(norm(struct.unpack_from("<I", roh, k)[0]))
        yield name, worte


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=float, default=0.80)
    ap.add_argument("--worte", type=int, default=12)
    a = ap.parse_args()

    app = open(APP, "rb").read()
    n = len(app) // 4
    img = [norm(w) for w in struct.unpack_from("<%dI" % n, app, 0)]
    index = {}
    for i in range(n - 4):
        index.setdefault(tuple(img[i:i + 4]), []).append(i)

    beste = {}   # (lib, obj, name) -> (aehnlichkeit, va, worte)
    gesehen = {}  # gleicher Code in mehreren Bibliotheksvarianten nur einmal suchen
    for obj in sorted(glob.glob(os.path.join(FID, "src", "*", "*.o"))):
        lib = os.path.basename(os.path.dirname(obj))
        try:
            funktionen = list(objekt_funktionen(obj))
        except ValueError:
            continue
        for name, worte in funktionen:
            if len(worte) < a.worte or any(w is JOKER for w in worte[:4]):
                continue
            schluessel = (name, tuple(worte))
            if schluessel in gesehen:
                if gesehen[schluessel]:
                    beste[(lib, os.path.basename(obj), name)] = gesehen[schluessel]
                continue
            treffer = None
            for i in index.get(tuple(worte[:4]), ()):
                if i + len(worte) > n:
                    continue
                gleich = sum(1 for k, w in enumerate(worte) if w is JOKER or w == img[i + k])
                q = gleich / len(worte)
                if treffer is None or q > treffer[0]:
                    treffer = (q, BASIS + 4 * i, len(worte))
            if treffer and treffer[0] >= a.min:
                gesehen[schluessel] = treffer
                beste[(lib, os.path.basename(obj), name)] = treffer
            else:
                gesehen[schluessel] = None

    # je Image-Adresse die Varianten zusammenfassen
    je_va = {}
    for (lib, obj, name), (q, va, nw) in beste.items():
        e = je_va.setdefault(va, {"namen": set(), "libs": set(), "q": q, "nw": nw, "obj": obj})
        e["namen"].add(name)
        e["libs"].add(lib)
        e["q"] = max(e["q"], q)
    aus = os.path.join(FID, "normvergleich.csv")
    with open(aus, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["va", "namen", "aehnlichkeit", "worte", "objekt", "bibliotheken"])
        for va in sorted(je_va):
            e = je_va[va]
            w.writerow(["0x%08X" % va, "|".join(sorted(e["namen"])), "%.3f" % e["q"], e["nw"],
                        e["obj"], "|".join(sorted(e["libs"]))])
    stufen = [(1.0, "100%"), (0.95, ">=95%"), (0.9, ">=90%"), (a.min, ">=%d%%" % (a.min * 100))]
    for s, t in stufen:
        print("%-6s %4d Adressen" % (t, sum(1 for e in je_va.values() if e["q"] >= s)))
    je_lib = {}
    for e in je_va.values():
        for l in e["libs"]:
            je_lib[l.split("__")[0]] = je_lib.get(l.split("__")[0], 0) + 1
    for l in sorted(je_lib, key=lambda k: -je_lib[k])[:30]:
        print("   %-40s %d" % (l, je_lib[l]))
    print("CSV:", aus)


if __name__ == "__main__":
    main()
