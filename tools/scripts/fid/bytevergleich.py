#!/usr/bin/env python3
"""Bytevergleich der FID-Treffer gegen die BSP-Objekte (CL-TOOL-REC-123).

Fuer jeden eindeutigen Treffer aus ghidra_projects/fid/fid_treffer_app.csv:
Funktion per Symboltabelle im Objekt der genannten Bibliothek suchen, ihre Bytes
lesen und gegen APP.bin an Dateioffset = VA - 0x58000 vergleichen. Jede Stelle,
die eine Relokation im Objekt traegt, wird mit 4 Bytes maskiert -- dort steht im
Objekt ein Platzhalter, im Image die gelinkte Adresse.

Ergebnis je Funktion: GLEICH (alle unmaskierten Bytes identisch), POOL (nur das
Offset von ldr Rd,[pc,#imm] weicht ab -- derselbe Code, Literalpool anders
platziert), ABWEICHEND (erste Stelle genannt), NULLGROESSE (Symbol ohne Laenge,
etwa Assembler) oder NICHT GEFUNDEN. Liest nur; schreibt die belegten Treffer
(GLEICH und POOL) nach ghidra_projects/fid/fid_belegt.csv.

  python3 tools/scripts/fid/bytevergleich.py [--alle]
"""
import csv
import glob
import os
import struct
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
APP = os.path.join(REPO, "firmware", "bin", "ZK-INKJET-NANO-APP.bin")
FID = os.path.join(REPO, "ghidra_projects", "fid")
BASIS = 0x00058000

SHT_SYMTAB, SHT_REL = 2, 9


def elf_lesen(pfad):
    d = open(pfad, "rb").read()
    if d[:4] != b"\x7fELF" or d[4] != 1 or d[5] != 1:
        raise ValueError("kein ELF32 LE: %s" % pfad)
    e_shoff, = struct.unpack_from("<I", d, 0x20)
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", d, 0x2E)
    sek = []
    for i in range(e_shnum):
        (name, typ, flags, addr, off, size, link, info, align,
         entsize) = struct.unpack_from("<10I", d, e_shoff + i * e_shentsize)
        sek.append(dict(name=name, typ=typ, off=off, size=size, link=link, info=info,
                        entsize=entsize))
    syms = {}
    for s in sek:
        if s["typ"] != SHT_SYMTAB:
            continue
        strt = sek[s["link"]]
        for j in range(s["size"] // 16):
            nm, val, gr, inf, oth, shndx = struct.unpack_from("<IIIBBH", d, s["off"] + j * 16)
            if (inf & 0xF) != 2 or shndx == 0 or shndx >= 0xFF00:   # nur STT_FUNC
                continue
            ende = d.index(b"\0", strt["off"] + nm)
            syms[d[strt["off"] + nm:ende].decode("latin1")] = (shndx, val & ~1, gr)
    relok = {}   # Sektionsindex -> Menge der relozierten Offsets
    for s in sek:
        if s["typ"] != SHT_REL:
            continue
        ziel = s["info"]
        for j in range(s["size"] // 8):
            r_off, r_info = struct.unpack_from("<II", d, s["off"] + j * 8)
            relok.setdefault(ziel, set()).add(r_off)
    return d, sek, syms, relok


def vergleichen(app, va, objpfad, name):
    d, sek, syms, relok = elf_lesen(objpfad)
    if name not in syms:
        return None
    shndx, wert, groesse = syms[name]
    if groesse == 0:
        return ("NULLGROESSE", 0, 0, None)
    s = sek[shndx]
    obj = d[s["off"] + wert:s["off"] + wert + groesse]
    img = app[va - BASIS:va - BASIS + groesse]
    maske = set()
    for r in relok.get(shndx, ()):
        if wert <= r < wert + groesse:
            maske.update(range(r - wert, r - wert + 4))
    abw = [i for i in range(groesse) if i not in maske and obj[i] != img[i]]
    if not abw:
        return ("GLEICH", groesse, len(maske), None)
    # Weichen nur ldr Rd,[pc,#imm]-Befehle ab, und dort nur das 12-Bit-Offset, liegt
    # derselbe Code mit anders platziertem Literalpool vor.
    nur_pool = True
    for k in sorted(set(i - i % 4 for i in abw)):
        a, = struct.unpack_from("<I", obj, k)
        b, = struct.unpack_from("<I", img, k)
        if not ((a & 0x0E5F0000) == 0x041F0000 and (a & 0xFFFFF000) == (b & 0xFFFFF000)):
            nur_pool = False
            break
    return ("POOL" if nur_pool else "ABWEICHEND", groesse, len(maske), abw[0])


def main():
    app = open(APP, "rb").read()
    zeilen = list(csv.DictReader(open(os.path.join(FID, "fid_treffer_app.csv"))))
    zeilen = [z for z in zeilen if z["eindeutig"] == "1"]
    gleich = pool = abw = fehlt = 0
    belegt = []
    for z in zeilen:
        va = int(z["va"], 16)
        name = z["fid_namen"]
        ergebnis = None
        for lib in z["bibliotheken"].split("|"):
            for obj in sorted(glob.glob(os.path.join(FID, "src", lib, "*.o"))):
                ergebnis = vergleichen(app, va, obj, name)
                if ergebnis:
                    quelle = "%s/%s" % (lib, os.path.basename(obj))
                    break
            if ergebnis:
                break
        if not ergebnis:
            fehlt += 1
            print("0x%08X  %-32s NICHT GEFUNDEN" % (va, name))
            continue
        art, groesse, maskiert, erste = ergebnis
        if art == "GLEICH":
            gleich += 1
        elif art == "POOL":
            pool += 1
        else:
            abw += 1
        if art in ("GLEICH", "POOL"):
            belegt.append((va, name, art, quelle))
        print("0x%08X  %-32s %-10s %5d Bytes, %4d maskiert%s  %s"
              % (va, name, art, groesse, maskiert,
                 "" if erste is None else ", erste Abweichung +0x%X" % erste, quelle))
    with open(os.path.join(FID, "fid_belegt.csv"), "w") as fh:
        fh.write("va,name,vergleich,quelle\n")
        for va, name, art, quelle in belegt:
            fh.write("0x%08X,%s,%s,%s\n" % (va, name, art, quelle))
    print("SUMME: %d gleich, %d gleich bis auf Poolabstand, %d abweichend oder ohne Groesse, "
          "%d nicht gefunden, von %d -> %d belegt in fid_belegt.csv"
          % (gleich, pool, abw, fehlt, len(zeilen), len(belegt)))
    return 0 if abw == 0 and fehlt == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
