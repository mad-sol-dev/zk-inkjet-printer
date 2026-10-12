#!/usr/bin/env python3
"""Erzeugt ein Dokument in der Ablage des ZK-Inkjet aus einer gemessenen Vorlage.

Prinzip: NICHT von Grund auf konstruieren, sondern einen real vom Geraet
geschriebenen Datensatz als Vorlage nehmen und nur die verstandenen Felder
patchen. Alles Unverstandene bleibt so, wie das Geraet es hinterlassen hat.

Ablage: Eintrag i bei 0x28800000 + i*0x4D000, Datensatz 0x4D000 Bytes, davon
0x4CFC0 Nutzdaten (= der Job-Block *[0x560], CL-FIRMWARE-REC-116).

Zwei Betriebsarten:

1. Text/Barcode (wie bisher, CL-STORAGE-REC-222): patcht in sieben Sektoren
     +0x0004  Eintragsindex
     +0x0040  Dokumentname, ASCII, nullterminiert
     +0x0178  Textinhalt, ASCII, nullterminiert
     +0x67E8  Laenge der Barcode-Nutzdaten
     +0x6800  Barcode-Nutzdaten, ASCII, nullterminiert

2. Rohbild (--image, CL-FIRMWARE-REC-115/-116): ersetzt die Elementliste durch
   ein einziges Element vom Typ 7 und schreibt den ganzen Datensatz.
     Job+0x144            Zahl der Elemente = 1
     Element = Job+0x160, 0x6688 Bytes, vorher genullt wie in FUN_000c7150
     El+0x000 Typ 7, +0x004 Spalte x, +0x008 Hoehe y, +0x00C Drehung 0, +0x010 Spiegelung 0
     El+0x120 Breite, +0x124 Hoehe, +0x6680/+0x6684 dieselben Werte
     El+0x67D Bild zeilenweise, (Breite+7)/8 Bytes pro Zeile, MSB = linke Spalte,
              0-Bit = Tinte (FUN_000b692c); hoechstens 0x6000 Bytes, Hoehe <= 150

Folgezaehler (--seq): +0x0008, 64 Bit. Der Lader beim Start (FUN_000b7228 ->
FUN_000e2248) nimmt den Slot mit dem groessten Folgezaehler im Bereich 1..100.
--seq auto setzt Maximum+1 ueber alle Slots der Vorlage (bzw. von --into).

Usage:
  make_document.py --template DUMP.img --template-entry 2 \\
                   --entry 3 --name "TEST-003" --text "ABCDE" --barcode "87654321" \\
                   [--seq auto] [--into IMAGE.img] [--emit-dd SCRIPT.sh --device /dev/sdX]
  make_document.py --template DUMP.img --template-entry 1 \\
                   --entry 3 --name "BILD-003" --image bild.png [--x 25] [--y 0] \\
                   [--threshold 128] --seq auto [--into IMAGE.img] [--emit-dd ...]
"""
import argparse, os, struct, sys

STORE, STRIDE, RECLEN = 0x28800000, 0x4D000, 0x4CFC0
NSLOTS, MAGIC = 100, 0x2022
SETTINGS, DOCCOUNT = 0x28000000, 0x180
SECTORS = [0x00000, 0x00200, 0x00600, 0x06600, 0x06800, 0x06E00, 0x0CE00, 0x4CE00]

F_INDEX, F_SEQ, F_NAME, F_TEXT = 0x0004, 0x0008, 0x0040, 0x0178
F_BCLEN, F_BCDATA = 0x67E8, 0x6800
NAME_MAX, TEXT_MAX, BC_MAX = 0x40, 0x40, 0x40

J_COUNT, J_ELEM, E_SIZE, E_MAX = 0x144, 0x160, 0x6688, 12
E_TYPE, E_X, E_Y, E_ROT, E_MIRROR = 0x000, 0x004, 0x008, 0x00C, 0x010
E_W, E_H, E_PTR, E_VALID, E_DATA = 0x120, 0x124, 0x678, 0x67C, 0x67D
E_W2, E_H2, DATA_MAX, HEAD_PX = 0x6680, 0x6684, 0x6000, 150


def put_str(buf, off, s, maxlen, label):
    b = s.encode("ascii")
    if len(b) + 1 > maxlen:
        sys.exit("%s zu lang: %d Bytes, erlaubt sind %d" % (label, len(b), maxlen - 1))
    buf[off:off + maxlen] = b + b"\x00" * (maxlen - len(b))


def slot_headers(path):
    """Kopf jedes Slots: (magic, index, folgezaehler)."""
    out = []
    with open(path, "rb") as f:
        for k in range(NSLOTS):
            f.seek(STORE + k * STRIDE)
            m, idx, lo, hi = struct.unpack("<4I", f.read(16))
            out.append((m, idx, lo | hi << 32))
    return out


def next_seq(path):
    """Folgezaehler, den der Lader als neuesten waehlt (FUN_000e2248, 0xE2324-0xE2394)."""
    valid = [s for m, idx, s in slot_headers(path) if m == MAGIC and idx < NSLOTS and 1 <= s <= NSLOTS]
    seq = max(valid, default=0) + 1
    if seq > NSLOTS:
        sys.exit("Folgezaehler waere %d > %d -- der Lader wuerde den Slot ignorieren" % (seq, NSLOTS))
    return seq


def image_rows(path, threshold):
    """Bild -> (Breite, Hoehe, Bytes): zeilenweise, MSB links, 0-Bit = Tinte."""
    from PIL import Image
    im = Image.open(path).convert("L")
    w, h = im.size
    if h > HEAD_PX:
        sys.exit("Bild ist %d Pixel hoch, der Kopf hat %d" % (h, HEAD_PX))
    rb = (w + 7) // 8
    if rb * h > DATA_MAX:
        sys.exit("Bild braucht %d Bytes, im Element ist Platz fuer %d (bei Hoehe %d hoechstens %d Pixel breit)"
                 % (rb * h, DATA_MAX, h, (DATA_MAX // h) * 8))
    px = im.load()
    out = bytearray(b"\xff" * (rb * h))
    for y in range(h):
        for x in range(w):
            if px[x, y] < threshold:
                out[y * rb + (x >> 3)] &= ~(0x80 >> (x & 7)) & 0xFF
    return w, h, bytes(out)


def build_image_record(rec, a):
    w, h, data = image_rows(a.image, a.threshold)
    if a.x + w > 18000:
        sys.exit("x + Breite = %d > 18000 Spalten" % (a.x + w))
    struct.pack_into("<I", rec, J_COUNT, 1)
    rec[J_ELEM:J_ELEM + E_MAX * E_SIZE] = bytes(E_MAX * E_SIZE)
    e = J_ELEM
    for off, val in ((E_TYPE, 7), (E_X, a.x), (E_Y, a.y), (E_ROT, 0), (E_MIRROR, 0),
                     (E_W, w), (E_H, h), (E_PTR, 0), (E_W2, w), (E_H2, h)):
        struct.pack_into("<I", rec, e + off, val)
    rec[e + E_VALID] = 0
    rec[e + E_DATA:e + E_DATA + len(data)] = data
    ink = sum(8 - bin(b).count("1") for b in data) - (len(data) * 8 - w * h)
    print("  Bild    : %s, %d x %d Pixel, %d Bytes, %d Pixel Tinte, Spalten %d..%d"
          % (a.image, w, h, len(data), ink, a.x, a.x + w - 1))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True, help="Kartendump mit einem echten Dokument")
    ap.add_argument("--template-entry", type=int, default=2)
    ap.add_argument("--entry", type=int, required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--text")
    ap.add_argument("--barcode")
    ap.add_argument("--image", help="Rohbild als einziges Element vom Typ 7")
    ap.add_argument("--x", type=int, default=25, help="Startspalte des Bildes")
    ap.add_argument("--y", type=int, default=0, help="Hoehe des Bildes am Kopf (0..149)")
    ap.add_argument("--threshold", type=int, default=128, help="Grauwert unter dem ein Pixel Tinte ist")
    ap.add_argument("--seq", help="Folgezaehler: Zahl 1..100 oder 'auto' (Maximum+1)")
    ap.add_argument("--into", help="Imagedatei, in die geschrieben wird")
    ap.add_argument("--doc-count", type=int, help="settings+0x180 auf diesen Wert setzen")
    ap.add_argument("--emit-dd", help="Shellskript mit dd-Befehlen erzeugen")
    ap.add_argument("--device", default="/dev/sdX")
    ap.add_argument("--outdir", default="/tmp/zkdoc")
    a = ap.parse_args()
    if not a.image and (a.text is None or a.barcode is None):
        sys.exit("ohne --image sind --text und --barcode noetig")
    if not 0 <= a.entry < NSLOTS:
        sys.exit("--entry muss 0..99 sein")

    src = STORE + a.template_entry * STRIDE
    dst = STORE + a.entry * STRIDE

    seq = None
    if a.seq == "auto":
        seq = next_seq(a.into or a.template)
    elif a.seq is not None:
        seq = int(a.seq, 0)
        if not 1 <= seq <= NSLOTS:
            sys.exit("--seq muss 1..100 sein, sonst ignoriert der Lader den Slot")

    with open(a.template, "rb") as f:
        f.seek(SETTINGS); settings = bytearray(f.read(512))
        if a.image:
            f.seek(src); rec = bytearray(f.read(RECLEN))
        else:
            tpl = {}
            for rel in SECTORS:
                f.seek(src + rel); tpl[rel] = bytearray(f.read(512))

    print("Eintrag %d bei 0x%08X, Vorlage Eintrag %d" % (a.entry, dst, a.template_entry))
    if a.image:
        if struct.unpack_from("<I", rec, 0)[0] != MAGIC:
            sys.exit("Vorlage Eintrag %d hat kein Magic 0x2022" % a.template_entry)
        head = rec
        build_image_record(rec, a)
    else:
        head = tpl[0x00000]
        put_str(head, F_TEXT, a.text, TEXT_MAX, "Text")
        struct.pack_into("<I", tpl[0x06600], F_BCLEN - 0x06600, len(a.barcode))
        put_str(tpl[0x06800], F_BCDATA - 0x06800, a.barcode, BC_MAX, "Barcode")
        print("  Text    : %r" % a.text)
        print("  Barcode : %r  (Laenge %d)" % (a.barcode, len(a.barcode)))
    struct.pack_into("<I", head, F_INDEX, a.entry)
    put_str(head, F_NAME, a.name, NAME_MAX, "Name")
    print("  Name    : %r" % a.name)
    if seq is not None:
        struct.pack_into("<Q", head, F_SEQ, seq)
        print("  Folgez. : %d" % seq)
    else:
        print("  Folgez. : %d (aus der Vorlage -- der Lader nimmt den Slot beim Start nur, wenn das das Maximum ist)"
              % struct.unpack_from("<Q", head, F_SEQ)[0])

    # Bloecke erst nach allen Patches schneiden: rec[...] kopiert
    if a.image:
        blocks = [(rel, rec[rel:rel + 512]) for rel in range(0, RECLEN, 512)]
    else:
        blocks = [(rel, tpl[rel]) for rel in SECTORS]

    if a.doc_count is not None:
        struct.pack_into("<I", settings, DOCCOUNT, a.doc_count)
        print("  settings+0x180 = %d" % a.doc_count)

    if a.into:
        with open(a.into, "r+b") as f:
            for rel, b in blocks:
                f.seek(dst + rel); f.write(b)
            if a.doc_count is not None:
                f.seek(SETTINGS); f.write(settings)
        print("geschrieben in %s (%d Sektoren)" % (a.into, len(blocks)))

    if a.emit_dd:
        os.makedirs(a.outdir, exist_ok=True)
        lines = ["#!/bin/bash", "set -e",
                 "# Erzeugt von make_document.py -- schreibt Eintrag %d (%d Sektoren%s) auf %s" % (
                     a.entry, len(blocks), " + Settings" if a.doc_count is not None else "", a.device),
                 "# NUR auf die Testkarte anwenden, niemals auf die Originalkarte.",
                 'echo "Ziel: %s"; read -p "Fortfahren? [j/N] " x; [ "$x" = j ] || exit 1' % a.device]
        if a.image:
            p = os.path.join(a.outdir, "doc%d.bin" % a.entry)
            open(p, "wb").write(b"".join(b for _, b in blocks))
            lines.append("dd if=%s of=%s bs=512 count=%d seek=%d conv=notrunc,fsync status=none"
                         % (p, a.device, len(blocks), dst // 512))
        else:
            for rel, b in blocks:
                p = os.path.join(a.outdir, "doc%d_%05x.bin" % (a.entry, rel))
                open(p, "wb").write(b)
                lines.append("dd if=%s of=%s bs=512 count=1 seek=%d conv=notrunc,fsync status=none"
                             % (p, a.device, (dst + rel) // 512))
        if a.doc_count is not None:
            p = os.path.join(a.outdir, "settings.bin")
            open(p, "wb").write(settings)
            lines.append("dd if=%s of=%s bs=512 count=1 seek=%d conv=notrunc,fsync status=none"
                         % (p, a.device, SETTINGS // 512))
        lines.append('echo "fertig"')
        open(a.emit_dd, "w").write("\n".join(lines) + "\n")
        os.chmod(a.emit_dd, 0o755)
        print("dd-Skript: %s   Sektordaten in %s" % (a.emit_dd, a.outdir))


if __name__ == "__main__":
    main()
