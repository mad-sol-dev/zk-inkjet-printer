#!/usr/bin/env python3
"""Rechnet den Image-Pruefwert [0x558] nach, den die Systeminit FUN_000b7518
beim Start bildet (Nachtlauf 2026-10-13, CL-FIRMWARE-REC-119).

Ablauf in der Firmware (VA = Dateioffset + 0x58000):
  Kopf bei VA 0x120F60 (Datei 0xC8F60): 16 Byte gespeicherter MD5, Wort +0x10
  = Imagelaenge 0x27522C. MD5 (Startwerte 0x67452301/0xEFCDAB89 bei 0x72B34)
  ueber Datei[0:K] + Datei[K+0x14:K+0x28] + Datei[K+0x14:L] (K = 0xC8F60;
  die 0x14 Kopfbytes selbst sind ausgenommen). CRC-32 0x9DD20 (wortweise,
  MSB zuerst, Poly 0x04C11DB7, Start 0xFFFFFFFF, kein Endxor):
  c = CRC(gespeicherter MD5, 4 Worte); [0x558] = CRC(berechneter MD5 + c, 5 Worte).
  Gleich bei unveraendertem Image -> 0. ui_event_wait addiert [0x558] auf jedes
  Ereignis; die Diagnosezeile zeigt ihn als 'M%d'.

  image_pruefwert.py [IMAGE] [--patch DATEIOFFSET=WORT ...] [--ram ABZUG]
Ohne IMAGE: firmware/bin/ZK-INKJET-NANO-APP.bin. --ram nimmt das Image aus einem
RAM-Abzug (RAM-Adresse = Dateioffset im Abzug) und setzt das zur Laufzeit
beschriebene UI-String-Feld VA 0x124350..0x12B030 auf den Dateistand zurueck.
Liest nur, schreibt nichts.
"""
import argparse, hashlib, os, struct

BASE = 0x58000
K = 0x120F60 - BASE
FELD = (0x124350 - BASE, 0x12B030 - BASE)
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
APP = os.path.join(REPO, 'firmware', 'bin', 'ZK-INKJET-NANO-APP.bin')


def crc32w(worte):
    c = 0xFFFFFFFF
    for w in worte:
        for i in range(31, -1, -1):
            oben = c >> 31
            c = (c << 1) & 0xFFFFFFFF
            if oben: c ^= 0x04C11DB7
            if (w >> i) & 1: c ^= 0x04C11DB7
    return c


def md5_image(b):
    L = struct.unpack_from('<I', b, K + 0x10)[0]
    m = hashlib.md5()
    m.update(b[:K]); m.update(b[K + 0x14:K + 0x28]); m.update(b[K + 0x14:L])
    return m.digest(), L


def pruefwert(b):
    d, L = md5_image(b)
    c = crc32w(struct.unpack('<4I', b[K:K + 16]))
    return crc32w(list(struct.unpack('<4I', d)) + [c]), d, L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('image', nargs='?', default=APP)
    ap.add_argument('--ram')
    ap.add_argument('--patch', nargs='*', default=[])
    a = ap.parse_args()
    orig = open(APP, 'rb').read()
    v0 = pruefwert(orig)[0]
    print('Positivkontrolle APP.bin original: MD5==Kopf %s, [0x558]=%#010x (soll 0)'
          % (md5_image(orig)[0] == orig[K:K + 16], v0))
    if a.ram:
        b = bytearray(open(a.ram, 'rb').read()[BASE:BASE + len(orig)])
        b[FELD[0]:FELD[1]] = orig[FELD[0]:FELD[1]]
        quelle = a.ram + ' (String-Feld zurueckgesetzt)'
    else:
        b = bytearray(open(a.image, 'rb').read()); quelle = a.image
    for p in a.patch:
        o, w = (int(x, 0) for x in p.split('='))
        print('  patch Datei %#x: %#010x -> %#010x' % (o, struct.unpack_from('<I', b, o)[0], w))
        struct.pack_into('<I', b, o, w)
    abw = [o for o in range(0, len(orig) - 3, 4) if b[o:o + 4] != orig[o:o + 4]]
    v, d, L = pruefwert(bytes(b))
    s = v - (1 << 32) if v >> 31 else v
    e = (0x0FFFFFFF + v) & 0xFFFFFFFF
    print('%s: %d abweichende Worte, L=%#x' % (quelle, len(abw), L))
    print('  [0x558] = %#010x = %d (Diagnose M%d)' % (v, s, s))
    print('  kein Ereignis 0x0FFFFFFF + [0x558] = %#010x -> Klick in ui_event_wait: %s'
          % (e, (e >> 28) == 0 and e != 9))
    print('  MD5 dieses Images: %s (Kopf: %s)' % (d.hex(), bytes(b[K:K + 16]).hex()))


if __name__ == '__main__':
    main()
