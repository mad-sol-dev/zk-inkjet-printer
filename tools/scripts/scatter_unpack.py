#!/usr/bin/env python3
"""Rollt die RW-Region eines armlink-Images aus und liest Worte daraus.

Der Entpacker ist eine Nachbildung von `__scatterload_decompress`, das in beiden
Binaerdateien dieses Geraets byteidentisch ab Dateioffset 0x9C liegt (Thumb,
hinter dem Veneer `add ip,pc,#1; bx ip`). Disassembliert, nicht geraten:

    token = *src++
    lit   = token & 7        ; 0 -> naechstes Byte
    run   = token >> 4       ; 0 -> naechstes Byte
    lit-1 Literalbytes kopieren
    Bit 3 gesetzt ? Rueckwaerts-Referenz: dist = *src++, run+2 Bytes ab dst-dist
                  : run Nullbytes
    bis dst das Ende erreicht

Gegenprobe ist BOOT.bin: dort rollt derselbe Eintrag 0x24 Bytes auf 0x180 aus,
klein genug, um das Ergebnis von Hand anzusehen. Laeuft die Kontrolle nicht
sauber durch, ist auch das APP-Ergebnis wertlos -- der Aufruf bricht dann ab.

    python3 tools/scripts/scatter_unpack.py firmware/bin/ZK-INKJET-NANO-BOOT.bin
    python3 tools/scripts/scatter_unpack.py firmware/bin/ZK-INKJET-NANO-APP.bin \
        --word 0x7D8 --word 0x890 --dump 0x7D0:0x40
"""
import argparse, struct, sys

HELFER = {0x9C: "decompress", 0xF8: "copy", 0x120: "zeroinit"}


def w32(d, off):
    return struct.unpack_from("<I", d, off)[0]


def entpacken(src, out_len):
    """__scatterload_decompress. Gibt (bytes, verbrauchte Quellbytes) zurueck."""
    dst = bytearray()
    i = 0
    while len(dst) < out_len:
        token = src[i]; i += 1
        lit = token & 7
        if lit == 0:
            lit = src[i]; i += 1
        run = token >> 4
        if run == 0:
            run = src[i]; i += 1
        for _ in range(lit - 1):
            dst.append(src[i]); i += 1
        if token & 8:
            dist = src[i]; i += 1
            p = len(dst) - dist
            if p < 0:
                sys.exit("Rueckwaerts-Referenz zeigt vor den Blockanfang -- Entpacker falsch")
            for _ in range(run + 2):
                dst.append(dst[p]); p += 1
        else:
            dst.extend(b"\x00" * run)
    return bytes(dst), i


def region(d, name):
    """Die RW-Region aus dem Scatter-Table: (basis_va, bytes) -- entpackt bzw. kopiert."""
    t0 = 0x94 + w32(d, 0x94)
    t1 = 0x94 + w32(d, 0x98)
    stuecke = []
    for off in range(t0, t1, 16):
        src, dst, size, fn = (w32(d, off + i * 4) for i in range(4))
        art = HELFER.get(fn & 0xFFF)
        basis = fn - (fn & 0xFFF)
        if art == "zeroinit":
            stuecke.append((dst, size, b"\x00" * size, 0))
        elif art == "copy":
            o = src - basis
            stuecke.append((dst, size, d[o:o + size], size))
        elif art == "decompress":
            o = src - basis
            roh, n = entpacken(d[o:], size)
            stuecke.append((dst, size, roh, n))
        else:
            sys.exit("unbekannte Scatter-Funktion 0x%08X" % fn)
    return stuecke


def kontrolle():
    d = open("firmware/bin/ZK-INKJET-NANO-BOOT.bin", "rb").read()
    for dst, size, roh, n in region(d, "BOOT"):
        if dst == 0x60:
            if len(roh) != size:
                sys.exit("Kontrolle: %d statt %d Bytes entpackt" % (len(roh), size))
            if n != 0x24:
                sys.exit("Kontrolle: %d statt 0x24 Quellbytes verbraucht" % n)
            return roh
    sys.exit("Kontrolle: BOOT.bin hat keinen RW-Eintrag bei 0x60")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--word", action="append", default=[], help="VA (hex) als 32-Bit-Wort lesen")
    ap.add_argument("--dump", action="append", default=[], help="VA:laenge (hex) als Hexdump")
    a = ap.parse_args()

    roh = kontrolle()
    print("Positivkontrolle BOOT.bin: 0x24 -> 0x180 Bytes, erste 32: %s" % roh[:32].hex())

    d = open(a.image, "rb").read()
    stuecke = region(d, a.image)
    print("\n%s -- ausgerollte Startregion:" % a.image)
    speicher = {}
    for dst, size, blob, n in stuecke:
        art = "zero" if not any(blob) and n == 0 else ("entpackt aus 0x%X" % n if n and n != size else "kopiert")
        print("  0x%08X-0x%08X  0x%06X Bytes  %s" % (dst, dst + size, size, art))
        for k, b in enumerate(blob):
            speicher[dst + k] = b

    def wort(va):
        if any(va + k not in speicher for k in range(4)):
            return None
        return speicher[va] | speicher[va + 1] << 8 | speicher[va + 2] << 16 | speicher[va + 3] << 24

    for hx in a.word:
        va = int(hx, 0)
        v = wort(va)
        print("  *(0x%08X) = %s" % (va, "nicht abgedeckt" if v is None else "0x%08X" % v))
    for spec in a.dump:
        va, _, ln = spec.partition(":")
        va, ln = int(va, 0), int(ln or "0x20", 0)
        for z in range(va, va + ln, 16):
            bs = [speicher.get(z + k) for k in range(16)]
            hexs = " ".join("--" if b is None else "%02x" % b for b in bs)
            print("  0x%08X  %s" % (z, hexs))


if __name__ == "__main__":
    main()
