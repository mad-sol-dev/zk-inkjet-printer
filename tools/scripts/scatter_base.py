#!/usr/bin/env python3
"""Liest die Linkbasis eines armlink-Images aus seinem eigenen Scatter-Table.

Hintergrund: beide Binaerdateien dieses Geraets beginnen mit demselben
armlink-Startstub (`__scatterload_rt2`). Der Stub laedt bei +0x60 PC-relativ
zwei Offsets, die auf eine Tabelle am Dateiende zeigen; jeder Eintrag ist
(src, dst, size, fn) mit absoluten Adressen im *gelinkten* Adressraum. Daraus
faellt die Basis auf drei unabhaengige Weisen heraus:

  1. `fn` zeigt auf die Helfer __scatterload_decompress/_copy/_zeroinit, die im
     Stub bei +0x9C, +0xF8 und +0x120 liegen. Basis = fn - 0x9C bzw. -0xF8/-0x120.
  2. Der Zero-Init-Eintrag traegt als `src` das Ende des Images. Basis =
     src_zi - Dateigroesse.
  3. Der erste Eintrag kopiert 0x60 Bytes nach VA 0; das ist die ARM-Vektor-
     tabelle, und ihr Reset-Wort bei +0x20 ist die Basis selbst.

Gegenprobe ist BOOT.bin, dessen Basis 0x00700000 unabhaengig bekannt war
(CL-BOOT-REC-111): dort liefern alle drei Wege denselben Wert.

Zusaetzlich `--pooltest`: zaehlt, wie viele der von `ldr Rd,[pc,#imm]`
referenzierten Literalworte unter einer angenommenen Basis ueberhaupt ins Image
fallen und wie viele davon auf einen `push {...,lr}`-Funktionsanfang zeigen.
Eine falsche Basis erzeugt hier fast nur Nieten.

    python3 tools/scripts/scatter_base.py firmware/bin/ZK-INKJET-NANO-BOOT.bin
    python3 tools/scripts/scatter_base.py firmware/bin/ZK-INKJET-NANO-APP.bin \
        --pooltest 0x58000 --pooltest 0x200000
"""
import argparse, struct, sys

# Offsets der drei Scatter-Helfer im gemeinsamen armlink-Startstub.
HELFER = {0x9C: "__scatterload_decompress", 0xF8: "__scatterload_copy",
          0x120: "__scatterload_zeroinit"}


def w32(d, off):
    return struct.unpack_from("<I", d, off)[0]


def tabelle(d):
    """Fundort der Scatter-Tabelle als Dateioffset, aus dem PC-relativen Stub."""
    if w32(d, 0x60) != 0xE28F002C or w32(d, 0x64) != 0xE8900C00:
        sys.exit("kein armlink-Startstub bei +0x60 -- diese Datei passt nicht ins Muster")
    # add r0,pc,#0x2c -> r0 zeigt auf +0x94; ldm r0,{sl,fp} holt zwei Offsets.
    return 0x94 + w32(d, 0x94), 0x94 + w32(d, 0x98)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--pooltest", action="append", default=[],
                    help="Basis (hex), gegen die der Literalpool geprueft wird")
    a = ap.parse_args()
    d = open(a.image, "rb").read()
    n = len(d)
    t0, t1 = tabelle(d)
    print("%s  %d Bytes (0x%X)" % (a.image, n, n))
    print("Scatter-Tabelle bei Dateioffset 0x%X..0x%X  (%d Eintraege)"
          % (t0, t1, (t1 - t0) // 16))

    kandidaten = []
    for off in range(t0, t1, 16):
        src, dst, size, fn = (w32(d, off + i * 4) for i in range(4))
        name = HELFER.get(fn & 0xFFF, "?")
        print("  src=0x%08X dst=0x%08X size=0x%08X fn=0x%08X  %s"
              % (src, dst, size, fn, name))
        if (fn & 0xFFF) in HELFER:
            kandidaten.append(("fn %s" % name, fn - (fn & 0xFFF)))
        if name == "__scatterload_zeroinit":
            kandidaten.append(("Zero-Init-src minus Dateigroesse", src - n))

    print()
    for grund, basis in kandidaten:
        print("  Basis 0x%08X  aus %s" % (basis, grund))

    # Weg 3: die nach VA 0 kopierten 0x60 Bytes sind die Vektortabelle.
    basen = {b for _, b in kandidaten}
    for basis in sorted(basen):
        for off in range(t0, t1, 16):
            src, dst, size, fn = (w32(d, off + i * 4) for i in range(4))
            if dst == 0 and size == 0x60 and 0 <= src - basis < n:
                v = src - basis
                if all(w32(d, v + i * 4) == 0xE59FF018 for i in (0, 1, 2, 3)):
                    print("  Basis 0x%08X  aus dem Reset-Wort der Vektortabelle "
                          "(Dateioffset 0x%X + 0x20)" % (w32(d, v + 0x20), v))

    for hx in a.pooltest:
        basis = int(hx, 0)
        pool = set()
        for i in range(0, n - 4, 4):
            w = w32(d, i)
            if (w >> 28) == 0xE and ((w >> 16) & 0xFFF) == 0x59F:
                p = i + 8 + (w & 0xFFF)
                if 0 <= p < n - 4:
                    pool.add(p)
        drin = treffer = 0
        for p in pool:
            v = w32(d, p)
            if basis <= v < basis + n and not v & 3:
                drin += 1
                if w32(d, v - basis) & 0xFFFF4000 == 0xE92D4000:
                    treffer += 1
        print("  Pooltest Basis 0x%08X: %d Literalworte, davon %d im Image, "
              "davon %d auf push{..,lr}" % (basis, len(pool), drin, treffer))


if __name__ == "__main__":
    main()
