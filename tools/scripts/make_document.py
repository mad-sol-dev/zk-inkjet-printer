#!/usr/bin/env python3
"""Erzeugt ein Dokument in der Ablage des ZK-Inkjet aus einer gemessenen Vorlage.

Prinzip: NICHT von Grund auf konstruieren, sondern einen real vom Geraet
geschriebenen Datensatz als Vorlage nehmen und nur die verstandenen Felder
patchen. Alles Unverstandene bleibt so, wie das Geraet es hinterlassen hat.

Ablage: Eintrag i bei 0x28800000 + i*0x4D000, Datensatz 0x4D000 Bytes.
Belegt sind davon sieben Sektoren; nur die werden geschrieben.

Gepatchte Felder (siehe research/phase_a_sd_analysis/document_store.md):
  +0x0004  Eintragsindex
  +0x0040  Dokumentname, ASCII, nullterminiert
  +0x0178  Textinhalt, ASCII, nullterminiert
  +0x67E8  Laenge der Barcode-Nutzdaten
  +0x6800  Barcode-Nutzdaten, ASCII, nullterminiert

Usage:
  make_document.py --template DUMP.img --template-entry 2 \
                   --entry 3 --name "TEST-003" --text "ABCDE" --barcode "87654321" \
                   [--into IMAGE.img] [--emit-dd SCRIPT.sh --device /dev/sdX]
"""
import argparse, os, struct, sys

STORE, STRIDE = 0x28800000, 0x4D000
SETTINGS, DOCCOUNT = 0x28000000, 0x180
SECTORS = [0x00000, 0x00200, 0x00600, 0x06600, 0x06800, 0x06E00, 0x0CE00, 0x4CE00]

F_INDEX, F_NAME, F_TEXT = 0x0004, 0x0040, 0x0178
F_BCLEN, F_BCDATA = 0x67E8, 0x6800
NAME_MAX, TEXT_MAX, BC_MAX = 0x40, 0x40, 0x40


def put_str(buf, off, s, maxlen, label):
    b = s.encode("ascii")
    if len(b) + 1 > maxlen:
        sys.exit("%s zu lang: %d Bytes, erlaubt sind %d" % (label, len(b), maxlen - 1))
    buf[off:off + maxlen] = b + b"\x00" * (maxlen - len(b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True, help="Kartendump mit einem echten Dokument")
    ap.add_argument("--template-entry", type=int, default=2)
    ap.add_argument("--entry", type=int, required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--barcode", required=True)
    ap.add_argument("--into", help="Imagedatei, in die geschrieben wird")
    ap.add_argument("--doc-count", type=int, help="settings+0x180 auf diesen Wert setzen")
    ap.add_argument("--emit-dd", help="Shellskript mit dd-Befehlen erzeugen")
    ap.add_argument("--device", default="/dev/sdX")
    ap.add_argument("--outdir", default="/tmp/zkdoc")
    a = ap.parse_args()

    src = STORE + a.template_entry * STRIDE
    dst = STORE + a.entry * STRIDE

    # Vorlage laden: nur die belegten Sektoren
    tpl = {}
    with open(a.template, "rb") as f:
        for rel in SECTORS:
            f.seek(src + rel); tpl[rel] = bytearray(f.read(512))
        f.seek(SETTINGS); settings = bytearray(f.read(512))

    h = tpl[0x00000]
    struct.pack_into("<I", h, F_INDEX, a.entry)
    put_str(h, F_NAME, a.name, NAME_MAX, "Name")
    put_str(h, F_TEXT, a.text, TEXT_MAX, "Text")

    struct.pack_into("<I", tpl[0x06600], F_BCLEN - 0x06600, len(a.barcode))
    put_str(tpl[0x06800], F_BCDATA - 0x06800, a.barcode, BC_MAX, "Barcode")
    print("Eintrag %d bei 0x%08X, Vorlage Eintrag %d" % (a.entry, dst, a.template_entry))
    print("  Name    : %r" % a.name)
    print("  Text    : %r" % a.text)
    print("  Barcode : %r  (Laenge %d)" % (a.barcode, len(a.barcode)))

    if a.doc_count is not None:
        struct.pack_into("<I", settings, DOCCOUNT, a.doc_count)
        print("  settings+0x180 = %d" % a.doc_count)

    if a.into:
        with open(a.into, "r+b") as f:
            for rel in SECTORS:
                f.seek(dst + rel); f.write(tpl[rel])
            if a.doc_count is not None:
                f.seek(SETTINGS); f.write(settings)
        print("geschrieben in %s" % a.into)

    if a.emit_dd:
        os.makedirs(a.outdir, exist_ok=True)
        lines = ["#!/bin/bash", "set -e",
                 "# Erzeugt von make_document.py -- schreibt %d Sektoren auf %s" % (
                     len(SECTORS) + (1 if a.doc_count is not None else 0), a.device),
                 "# NUR auf die Testkarte anwenden, niemals auf die Originalkarte.",
                 'echo "Ziel: %s"; read -p "Fortfahren? [j/N] " x; [ "$x" = j ] || exit 1' % a.device]
        for rel in SECTORS:
            p = os.path.join(a.outdir, "doc%d_%05x.bin" % (a.entry, rel))
            open(p, "wb").write(tpl[rel])
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
