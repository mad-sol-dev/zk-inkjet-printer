#!/usr/bin/env python3
"""Die Bilder bei SD 0x03800000 und ihre maskierten Kopien auf der Karte.

Liest nur. Schreibt die drei Rohbilder als PNG, sucht zu jedem die maskierte
Kopie (XOR 0x4949 je Wort, Rot/Blau getauscht) ueber das ganze Abbild,
vergleicht Bild 1 mit Bild 2 und sucht die Marken in beiden Firmware-Fassungen.

    python3 tools/scripts/ui_rohbilder.py [--image firmware/image/sdcard.work.img]
            [--out research/phase_a_sd_analysis/artifacts/ui_roh_03800000]

Die Farben haengen an der Kanalreihenfolge und sind nicht festgestellt; die PNGs
lesen das niedrige Feld als Rot (wie decode_ui_qvga.py).
"""
import argparse, mmap, os, re, struct

ROH, W, H = 0x03800000, 320, 240
N = W * H * 2
APP = "firmware/bin/ZK-INKJET-NANO-APP.bin"
IMAGE_100000 = (0x100000, 3001262)          # CL-BOOT-REC-115
MARKEN = [b"DCJET", b"DC-MINI PRINTER", b"Leon", b"LEON", b"QINGSHAN", b"Qingshan", b"Sishui",
          "雷奥".encode("utf-8"), "雷奥".encode("gbk")]


def worte(b):
    return struct.unpack("<%dH" % (len(b) // 2), b)


def tausch(w):
    return ((w & 0x1F) << 11) | (w & 0x7E0) | (w >> 11)


def maskiert(b):
    return b"".join(struct.pack("<H", tausch(w) ^ 0x4949) for w in worte(b))


def png(ws, pfad):
    from PIL import Image
    px = bytearray()
    for x in ws:
        r5, g6, b5 = x & 0x1F, (x >> 5) & 0x3F, (x >> 11) & 0x1F
        px += bytes(((r5 << 3) | (r5 >> 2), (g6 << 2) | (g6 >> 4), (b5 << 3) | (b5 >> 2)))
    Image.frombytes("RGB", (W, H), bytes(px)).save(pfad)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--image", default="firmware/image/sdcard.work.img")
    ap.add_argument("--out", default="research/phase_a_sd_analysis/artifacts/ui_roh_03800000")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with open(a.image, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        bilder = [mm[ROH + k * N:ROH + (k + 1) * N] for k in range(3)]
        for k, b in enumerate(bilder):
            png(worte(b), os.path.join(a.out, "roh_bild%d.png" % k))
            # Probe: 32 Pixel mit den meisten verschiedenen Werten, dann ganzes Bild vergleichen
            beste = max(((len(set(worte(b[o:o + 64]))), o) for o in range(0, N - 64, 32 * 2)))[1]
            ziel, fund, i = maskiert(b), [], mm.find(maskiert(b[beste:beste + 64]))
            while i != -1:
                start = i - beste
                if start >= 0 and mm[start:start + N] == ziel:
                    fund.append("0x%08X" % start)
                i = mm.find(maskiert(b[beste:beste + 64]), i + 1)
            print("Bild %d bei 0x%08X: maskierte Kopie (ganzes Bild gleich) bei %s"
                  % (k, ROH + k * N, ", ".join(fund) or "nirgends"))
        a1, a2 = worte(bilder[1]), worte(bilder[2])
        diff = [(x, y) for x, y in zip(a1, a2) if x != y]
        groesst = max(max(abs((x >> s & m) - (y >> s & m)) for s, m in ((0, 31), (5, 63), (11, 31)))
                      for x, y in diff) if diff else 0
        eins = sum(1 for x, y in diff if all(abs((x >> s & m) - (y >> s & m)) <= 1
                                              for s, m in ((0, 31), (5, 63), (11, 31))))
        print("Bild 1 gegen 2: %d von %d Pixeln verschieden, davon %d um hoechstens eine Stufe je Kanal, "
              "groesste Abweichung %d" % (len(diff), W * H, eins, groesst))
        image = mm[IMAGE_100000[0]:IMAGE_100000[0] + IMAGE_100000[1]]
    app = open(APP, "rb").read()
    for m in MARKEN:
        print("%-22r APP.bin %d   Image 0x100000 %d" % (m, len(re.findall(re.escape(m), app)),
                                                     len(re.findall(re.escape(m), image))))
    print("PNGs in %s" % a.out)


if __name__ == "__main__":
    main()
