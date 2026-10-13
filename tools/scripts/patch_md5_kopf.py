#!/usr/bin/env python3
"""MD5-Kopf nachziehen: Image-Pruefwert [0x558] nach einem Patch wieder auf 0 (CL-FIRMWARE-REC-119).

Befund (Nachtlauf 2026-10-13): Die Systeminit FUN_000b7518 rechnet beim Start
MD5 ueber das geladene Image und vergleicht ueber eine CRC mit dem Kopf bei
VA 0x120F60 (Datei 0xC8F60: 16 Byte MD5, Wort +0x10 = Laenge 0x27522C).
Jeder Patch in Datei 0..0x27522C verschiebt [0x558]; ui_event_wait addiert den
Wert auf jedes Ereignis -> Dauerton, Diagnose 'NG M<wert>'. Steht der MD5 des
gepatchten Images im Kopf, ist [0x558] = 0 (erwartet: Diagnose 'OK M0 A0').

Gelesen 2026-10-13 an FUN_000b7518 0xB7574..0xB7600: r4 = 0x120F60 (Poolwort
0xB770C), MD5 ueber VA 0x58000..0x120F60, dann 0x14 Byte ab 0x120F74, dann
0x120F74..0x58000+L -- die 0x14 Byte hinter dem Kopf gehen zweimal ein, der
Kopf selbst nicht, Bytes hinter L (Stubs ab Datei 0x275400) auch nicht.
Einziger Leser des Kopfes: Vier-Modi-Suche (hook_space_scan) nach 0x120F60..
0x120F73: lit 1 (0xB770C), imm/adr/kette 0; Kontrolle 0x120F40: lit 7.
Ghidra-Xrefs: 0x120F60 nur 0xB75D8, 0x120F70 nur 0xB757C (r4+0x10).

Quelle des Kartenimages:
  ohne --image  Nachbau aus APP.bin + Patch-Stand STAND (Stand 2026-10-13:
                USB-Fenster, Dauerbetrieb, RAM-Fenster, MSC-Puffer). Kontrolle:
                der Nachbau muss den am Geraet abgelesenen Wert M ergeben.
  --image DATEI Abbild der Karte (fuer jeden anderen Stand), lesen mit
                dd if=/dev/sdX bs=512 skip=98304 count=5034 iflag=direct status=none \\
                   | head -c 2576940 > karte_app.bin
Nach jeder Aenderung am Patch-Stand (auch zurueck.sh eines anderen Patches)
stimmt der Kopf nicht mehr: dann neu erzeugen, immer als letzter Schritt.

patch.sh prueft vor dem Schreiben den ganzen Imagebereich der Karte (sha256
ueber Datei 0..L) gegen das Abbild -- weicht ein Byte ab, wird nichts
geschrieben. Geschrieben wird ein Sektor, Datei 0xC8E00; danach wird der
Imagebereich erneut gelesen und geprueft.

  python3 tools/scripts/patch_md5_kopf.py --out <dir> [--device /dev/sdX] [--image ABBILD] [--ram ABZUG]
Es wird nichts auf ein Geraet geschrieben; patch.sh/zurueck.sh erst nach Rueckfrage.
"""
import argparse
import hashlib
import os
import struct
import sys

import image_pruefwert as pw
import patch_usb_dauerbetrieb as dauer

HIER = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HIER, "..", "..", "research", "phase_a_sd_analysis", "artifacts")

VA0, RAW_APP = dauer.VA0, dauer.RAW_APP
K = pw.K                                   # Datei 0xC8F60, Kopf
L = 0x27522C                               # Laenge laut Kopf +0x10
SEKTOR = K // 512 * 512                    # Datei 0xC8E00
BILD_SEKTOREN = (L + 511) // 512           # 5034

# Patch-Stand der Testkarte 2026-10-13 (CL-USB-REC-126): (Datei-Sektor, .neu unter ART, Herkunft).
# Sektoren hinter L (0x275400, Stubs) gehen nicht in den MD5 ein und fehlen hier.
STAND = [
    (0x12400, "usb_dauerbetrieb/sektor_012400.neu", "patch_usb_dauerbetrieb.py"),
    (0x68E00, "usb_dauerbetrieb/sektor_068e00.neu", "patch_usb_dauerbetrieb.py"),
    (0x69000, "usb_dauerbetrieb/sektor_069000.neu", "patch_usb_dauerbetrieb.py"),
    (0x6A600, "usb_dauerbetrieb/sektor_06a600.neu", "patch_usb_dauerbetrieb.py"),
    (0x78400, "ram_fenster/sektor_078400.neu", "patch_ram_fenster.py"),
    (0x77400, "msc_puffer/sektor_077400.neu", "patch_msc_puffer.py"),
]
# Am Geraet abgelesen 2026-10-13 mit diesem Stand: Diagnose 'M -196828810' (CL-USB-REC-126)
M_GERAET = 0xF444A176


def worte_diff(a, b, basis=0):
    return [basis + o for o in range(0, min(len(a), len(b)) - 3, 4) if a[o:o + 4] != b[o:o + 4]]


def nachbau(orig):
    """Kartenstand aus APP.bin + STAND; prueft jeden Sektor gegen Original und Geraetesicherung."""
    d = bytearray(orig)
    # USB-Fenster als Literale wie in patch_usb_dauerbetrieb.py (die .bin-Kopie ist gitignored)
    for o in dauer.FENSTER_LITERALE:
        assert struct.unpack_from("<I", d, o)[0] == dauer.FENSTER_ALT, hex(o)
        struct.pack_into("<I", d, o, dauer.FENSTER_NEU)
    print("  USB-Fenster  Datei %s: 0x%08X -> 0x%08X (patch_usb_window.py)"
          % ("/".join("0x%X" % o for o in dauer.FENSTER_LITERALE), dauer.FENSTER_ALT, dauer.FENSTER_NEU))
    kopie = os.path.join(ART, "usbfenster_28800000", "sektor_28800000.bin")
    if os.path.exists(kopie):
        s = dauer.FENSTER_LITERALE[0] // 512 * 512
        assert open(kopie, "rb").read() == bytes(d[s:s + 512]), "Fenster-Sektor weicht von der Kopie ab"
    for s, pfad, her in STAND:
        assert s % 512 == 0 and s + 512 <= L and s != SEKTOR, hex(s)
        neu = open(os.path.join(ART, pfad), "rb").read()
        assert len(neu) == 512, pfad
        sich = os.path.join(ART, pfad.replace(".neu", ".sicherung"))
        if os.path.exists(sich):
            # Geraetesicherung = Karteninhalt vor dem Patch; muss das Original sein
            if open(sich, "rb").read() != orig[s:s + 512]:
                sys.exit("Sicherung %s ist nicht der Originalsektor -- Stand unklar" % sich)
            gesichert = "Sicherung = Original"
        else:
            gesichert = "keine Sicherung"
        diff = worte_diff(orig[s:s + 512], neu, s)
        print("  Datei 0x%06X  %d Worte (%s)  %s, %s"
              % (s, len(diff), " ".join("0x%X" % o for o in diff), her, gesichert))
        d[s:s + 512] = neu
    return bytes(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default=dauer.APP)
    ap.add_argument("--image", help="Abbild der Karte ab Rohadresse 0x3000000 (mind. 0x%X Byte)" % L)
    ap.add_argument("--ram", help="RAM-Abzug zum Gegenlesen (Image bei RAM 0x%X)" % VA0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="/dev/sdX")
    a = ap.parse_args()

    orig = open(a.app, "rb").read()
    if hashlib.sha256(orig).hexdigest() != dauer.APP_SHA:
        sys.exit("APP.bin ist nicht die erwartete")
    assert len(orig) == L and struct.unpack_from("<I", orig, K + 0x10)[0] == L
    # Positivkontrolle der Rechnung: Original-Kopf = MD5 des Originals, [0x558] = 0
    v0, md5_0, _ = pw.pruefwert(orig)
    print("Positivkontrolle APP.bin original: MD5 %s == Kopf %s, [0x558] = 0x%08X"
          % (md5_0.hex(), orig[K:K + 16].hex(), v0))
    if md5_0 != orig[K:K + 16] or v0 != 0:
        sys.exit("Rechnung stimmt am Original nicht -- nichts erzeugt")

    if a.image:
        bild = open(a.image, "rb").read()
        if len(bild) < L:
            sys.exit("Abbild kuerzer als 0x%X" % L)
        bild = bild[:L]
        if struct.unpack_from("<I", bild, K + 0x10)[0] != L:
            sys.exit("Laengenwort im Kopf des Abbilds ist nicht 0x%X" % L)
        quelle = "Abbild %s" % a.image
        sek = sorted({o // 512 * 512 for o in worte_diff(orig, bild)})
        print("Abbild: %d Sektoren weichen vom Original ab: %s"
              % (len(sek), " ".join("0x%X" % s for s in sek)))
    else:
        quelle = "Nachbau Patch-Stand 2026-10-13 (USB-Fenster, Dauerbetrieb, RAM-Fenster, MSC-Puffer)"
        print("Nachbau des Kartenstands:")
        bild = nachbau(orig)

    v1, md5_1, _ = pw.pruefwert(bild)
    print("Kartenstand vorher: [0x558] = 0x%08X = %d (Diagnose M%d)"
          % (v1, v1 - (1 << 32) if v1 >> 31 else v1, v1 - (1 << 32) if v1 >> 31 else v1))
    if not a.image:
        if v1 != M_GERAET:
            sys.exit("Nachbau ergibt nicht den am Geraet abgelesenen Wert 0x%08X -- Stand unklar" % M_GERAET)
        print("  = am Geraet abgelesener Wert (Positivkontrolle des Nachbaus)")
    if a.ram:
        r = bytearray(open(a.ram, "rb").read()[VA0:VA0 + L])
        r[pw.FELD[0]:pw.FELD[1]] = orig[pw.FELD[0]:pw.FELD[1]]
        diff = worte_diff(bytes(r), bild)
        print("RAM-Abzug %s (String-Feld auf Dateistand): %d Worte weichen ab: %s"
              % (a.ram, len(diff), " ".join("0x%X" % o for o in diff)))

    if bild[K:K + 16] == md5_1:
        sys.exit("Kopf passt schon zum Abbild ([0x558] = 0) -- nichts zu tun")

    neu = bytearray(bild)
    neu[K:K + 16] = md5_1
    neu = bytes(neu)
    v2, md5_2, _ = pw.pruefwert(neu)
    print("Kopf Datei 0x%X: %s -> %s" % (K, bild[K:K + 16].hex(), md5_1.hex()))
    print("Kartenstand nachher: [0x558] = 0x%08X, MD5 unveraendert %s" % (v2, md5_2 == md5_1))
    if v2 != 0 or md5_2 != md5_1:
        sys.exit("Pruefwert nach dem Patch nicht 0 -- nichts erzeugt")
    abw = [i for i in range(L) if neu[i] != bild[i]]
    assert abw and K <= min(abw) and max(abw) < K + 16, "Patch reicht ueber den Kopf hinaus"

    alt_s, neu_s = bild[SEKTOR:SEKTOR + 512], neu[SEKTOR:SEKTOR + 512]
    raw = (RAW_APP >> 9) + SEKTOR // 512
    sha_alt, sha_neu = hashlib.sha256(bild).hexdigest(), hashlib.sha256(neu).hexdigest()

    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "sektor_%06x.neu" % SEKTOR), "wb").write(neu_s)
    open(os.path.join(a.out, "APP.md5kopf.bin"), "wb").write(neu)
    bild_sha = ('dd if=$DEV bs=512 skip=%d count=%d iflag=direct status=none | head -c %d | sha256sum | cut -d" " -f1'
                % (RAW_APP >> 9, BILD_SEKTOREN, L))
    zeilen = ["#!/bin/bash", "set -e",
              "# Erzeugt von patch_md5_kopf.py (CL-FIRMWARE-REC-119). NUR Testkarte.",
              "# Quelle: %s" % quelle,
              "# Kopf Datei 0x%X: %s -> %s" % (K, bild[K:K + 16].hex(), md5_1.hex()),
              "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"',
              'echo "Ziel: $DEV -- lese Imagebereich (%d Sektoren ab %d)"' % (BILD_SEKTOREN, RAW_APP >> 9),
              "IST=$(%s)" % bild_sha,
              'case "$IST" in',
              '  %s) echo "Kopf ist schon gesetzt -- nichts zu tun"; exit 0;;' % sha_neu,
              '  %s) ;;' % sha_alt,
              '  *) echo "Imagebereich weicht vom erwarteten Stand ab -- Abbruch, nichts geschrieben."',
              '     echo "Karte lesen und mit patch_md5_kopf.py --image neu erzeugen."; exit 1;;',
              'esac',
              'read -p "Sicherung anlegen und 1 Sektor (Datei 0x%X) schreiben? [j/N] " x; [ "$x" = j ] || exit 1' % SEKTOR,
              '[ -e sektor_%06x.sicherung ] || dd if=$DEV of=sektor_%06x.sicherung bs=512 skip=%d count=1 iflag=direct status=none'
              % (SEKTOR, SEKTOR, raw),
              '[ "$(sha256sum < sektor_%06x.sicherung | cut -d" " -f1)" = %s ] || { echo "Sicherung unerwartet -- Abbruch"; exit 1; }'
              % (SEKTOR, hashlib.sha256(alt_s).hexdigest()),
              "dd if=sektor_%06x.neu of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none" % (SEKTOR, raw),
              "sync",
              "IST=$(%s)" % bild_sha,
              '[ "$IST" = %s ] || { echo "Ruecklesen weicht ab -- ./zurueck.sh"; exit 1; }' % sha_neu,
              'echo "fertig, Imagebereich rueckgelesen -- erwartet Diagnose OK M0 A0; zurueck mit ./zurueck.sh"', ""]
    p = os.path.join(a.out, "patch.sh")
    open(p, "w").write("\n".join(zeilen)); os.chmod(p, 0o755)
    z = ["#!/bin/bash", "set -e", "DEV=${1:-%s}" % a.device, 'cd "$(dirname "$0")"',
         'read -p "Sicherung zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1',
         "dd if=sektor_%06x.sicherung of=$DEV bs=512 seek=%d count=1 oflag=direct conv=notrunc,fsync status=none"
         % (SEKTOR, raw),
         "sync", 'echo "zurueck"', ""]
    p = os.path.join(a.out, "zurueck.sh")
    open(p, "w").write("\n".join(z)); os.chmod(p, 0o755)
    print("Sektor Datei 0x%X = Karte %d; Imagebereich sha256 vorher %s.., nachher %s.."
          % (SEKTOR, raw, sha_alt[:16], sha_neu[:16]))


if __name__ == "__main__":
    main()
