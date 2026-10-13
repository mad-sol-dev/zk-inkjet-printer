#!/usr/bin/env python3
"""Grobe Phasen eines I2C-Mitschnitts (sigrok/PulseView .sr) am Auth-Baustein (CL-HARDWARE-REC-116).

Fuer Mitschnitte, die zu langsam fuer den PulseView-I2C-Decoder sind: es werden
keine Bits dekodiert, sondern die Abschnitte gezeigt, die der Treiber
FUN_000ebcfc/FUN_000ec248 erzeugt -- Weckpuls (SDA low bei SCL high), Ruhe
(beide high) und Verkehr dazwischen -- samt Abstand von Weckpuls zu Weckpuls.

Erwartung aus der Firmware: Weckpuls = delay(2000), Warten danach =
delay(0x1388). delay(n) (0x9EEC0) laedt n*24 in CNR3, das nur 16 Bit breit
ist (Design Guide A1, PWM Counter Register): delay(2000) = 48000 Takte,
delay(5000) = 120000 & 0xFFFF = 54464 Takte.

Der ESP32-Logikanalysator (sigrok 0.5.2) liefert jede zweite Probe als 0 auf
allen Kanaelen; eine solche Phase wird erkannt und verworfen (effektive Rate
halbiert, wird gemeldet).

  python3 tools/scripts/sr_phasen.py MITSCHNITT.sr [--scl SCL] [--sda SDA] [--min-ms 0.5]
Liest nur.
"""
import argparse
import configparser
import re
import zipfile


def lesen(pfad):
    z = zipfile.ZipFile(pfad)
    meta = configparser.ConfigParser()
    meta.read_string(z.read("metadata").decode())
    dev = meta["device 1"]
    rate = dev["samplerate"].split()
    rate = float(rate[0]) * {"Hz": 1, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9}[rate[1]]
    kanaele = {v: int(k[5:]) - 1 for k, v in dev.items() if re.fullmatch(r"probe\d+", k)}
    einheit = int(dev["unitsize"])
    datei = dev["capturefile"]
    teile = sorted((n for n in z.namelist() if n.startswith(datei + "-")), key=lambda n: int(n.rsplit("-", 1)[1]))
    roh = b"".join(z.read(n) for n in teile)
    proben = [int.from_bytes(roh[i:i + einheit], "little") for i in range(0, len(roh) - einheit + 1, einheit)]
    return rate, kanaele, proben


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sr")
    ap.add_argument("--scl", default="SCL")
    ap.add_argument("--sda", default="SDA")
    ap.add_argument("--min-ms", type=float, default=0.5, help="Mindestlaenge fuer Weckpuls und Ruhe")
    a = ap.parse_args()
    rate, kanaele, proben = lesen(a.sr)
    bc, bd = kanaele[a.scl], kanaele[a.sda]
    zust = [((x >> bc) & 1, (x >> bd) & 1) for x in proben]
    print("%s: %d Proben, %.0f Hz, %.2f ms; SCL Bit %d, SDA Bit %d" % (a.sr, len(zust), rate, len(zust) / rate * 1e3, bc, bd))

    # Leerproben-Phase des ESP32 erkennen: eine Paritaet fast nur (0,0), die andere nicht
    null = [sum(1 for z in zust[p::2] if z == (0, 0)) / max(1, len(zust[p::2])) for p in (0, 1)]
    leer = [p for p in (0, 1) if null[p] > 0.95 and null[1 - p] < 0.5]
    if leer:
        p = leer[0]
        zust = zust[1 - p::2]
        rate /= 2
        print("Phase %d ist zu %.1f %% (0,0) und wird verworfen -> effektiv %.0f Hz, %.0f us je Probe"
              % (p, 100 * null[p], rate, 1e6 / rate))

    # Startartefakt: fuehrende (0,0)-Proben (am Anfang sind die Phasen kurz vertauscht) sind kein Bus-Zustand
    s0 = 0
    while s0 < len(zust) and zust[s0] == (0, 0):
        s0 += 1
    if s0:
        print("Anfang: %d Proben (0,0) als Startartefakt uebersprungen, der folgende Abschnitt ist angeschnitten" % s0)

    n_min = max(1, int(a.min_ms * 1e-3 * rate))
    abschnitte, i = [], s0
    while i < len(zust):
        j = i
        while j < len(zust) and zust[j] == zust[i]:
            j += 1
        art = {(1, 0): "Weckpuls", (1, 1): "Ruhe"}.get(zust[i]) if j - i >= n_min else None
        if art:
            abschnitte.append((i, j, art))
        else:
            if abschnitte and abschnitte[-1][2] == "Verkehr":
                abschnitte[-1] = (abschnitte[-1][0], j, "Verkehr")
            else:
                abschnitte.append((i, j, "Verkehr"))
        i = j
    ms = lambda k: k / rate * 1e3
    for i, j, art in abschnitte:
        rand = "  (Rand)" if i == s0 or j == len(zust) else ""
        print("  %8.2f - %8.2f ms  %-9s %6.2f ms%s" % (ms(i), ms(j), art, ms(j - i), rand))
    weck = [(i, j) for i, j, art in abschnitte if art == "Weckpuls"]
    enden = [j for i, j in weck if j < len(zust)]
    print("Weckpulse: %d; Laengen (ohne Rand) %s ms" % (len(weck), ", ".join("%.2f" % ms(j - i) for i, j in weck if i > s0 and j < len(zust))))
    if len(enden) > 1:
        print("Abstand Weckpuls-Ende zu Weckpuls-Ende: %s ms" % ", ".join("%.2f" % ms(b - a_) for a_, b in zip(enden, enden[1:])))


if __name__ == "__main__":
    main()
