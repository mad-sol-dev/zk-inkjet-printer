#!/usr/bin/env python3
"""I2C-Transaktionen eines PulseView-Mitschnitts (.sr) am Auth-Baustein dekodieren und ATSHA204A-Rahmen pruefen.

Gedacht fuer die Mitschnitte unter research/phase_a_sd_analysis/artifacts/i2c_mitschnitt/
(CL-HARDWARE-REC-117). Der Treiber der Firmware (CL-FIRMWARE-REC-120) ist ein Bit-Bang-Master:
SDA wechselt dicht an den SCL-Flanken. Deshalb wird jedes Bit in der Mitte der SCL-High-Phase
gelesen, und START/STOP gilt nur bei einem SDA-Wechsel im Inneren einer High-Phase.

ATSHA204A-Pruefung: Antwort = Count, Daten, CRC-16 (Polynom 0x8005, Bits LSB zuerst,
Low-Byte zuerst); Schreibpaket = Word-Address 0x03, dann Count, Opcode, Param1, Param2, Daten, CRC.
Eine Antwort, deren erstes Byte ihre Laenge ist, wird gegen die CRC geprueft.

Leerproben: der ESP32-Logikanalysator (ok-home/logic_analyzer, SUMP) schickte vor dem Patch der
SUMP-Flags 2 Byte je Probe, PulseView las 1 Byte -- jede zweite Probe ist dann 0 auf allen Kanaelen,
mit gelegentlichem Paritaetssprung. Solche Proben werden fensterweise verworfen. Die Zeitbasis ist
danach die eingestellte Rate: an einem 100-kHz-Referenzsignal gemessen (eigener SUMP-Client,
Periode 20 Proben bei 2 MHz und 10 bei 1 MHz). Mit --ref wird ein solches Referenzsignal mitgeprueft.

  python3 tools/scripts/sr_i2c_atsha.py MITSCHNITT.sr [--scl SCL] [--sda SDA] [--ref KANAL]
Liest nur.
"""
import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sr_phasen import lesen  # noqa: E402


def crc_atsha(daten):
    crc = 0
    for b in daten:
        for i in range(8):
            if ((b >> i) & 1) != ((crc >> 15) & 1):
                crc = ((crc << 1) & 0xFFFF) ^ 0x8005
            else:
                crc = (crc << 1) & 0xFFFF
    return bytes([crc & 0xFF, crc >> 8])


def leerproben_verwerfen(proben, fenster=64):
    """Jede zweite Probe 0 auf allen Kanaelen? Dann je Fenster die Paritaet mit den Nullen verwerfen."""
    anteil = sum(1 for x in proben if x == 0) / max(1, len(proben))
    if not 0.4 < anteil < 0.6:
        return proben, 0
    raus, spruenge, vorher = [], 0, None
    for s in range(0, len(proben) - len(proben) % 2, fenster):
        w = proben[s:s + fenster]
        p = 1 if sum(1 for x in w[0::2] if x == 0) > sum(1 for x in w[1::2] if x == 0) else 0
        if vorher is not None and p != vorher:
            spruenge += 1
        vorher = p
        raus += w[p::2]
    return raus, spruenge


def ereignisse(scl, sda):
    """(Probe, 'S'|'P'|0|1) je SCL-High-Phase. Phasen ueber dem Dreifachen des Medians sind Busruhe:
    dort nur START/STOP, kein Datenbit."""
    phasen, i, n = [], 1, len(scl)
    while i < n:
        if scl[i] and not scl[i - 1]:
            j = i
            while j < n and scl[j]:
                j += 1
            phasen.append((i, j))
            i = j
        else:
            i += 1
    if not phasen:
        return []
    laengen = sorted(j - i for i, j in phasen)
    ruhe = 3 * laengen[len(laengen) // 2]
    ev = []
    for i, j in phasen:
        seg = sda[i + 1:j - 1] if j - i > 4 else sda[i:j]
        wechsel = [k for k in range(1, len(seg)) if seg[k] != seg[k - 1]]
        if not wechsel and j - i <= ruhe:
            ev.append((i, seg[0] if seg else sda[i]))
        for k in wechsel:
            ev.append((i + 1 + k, 'S' if seg[k] == 0 else 'P'))
    return ev


def transaktionen(ev):
    tr, cur, bits = [], None, []
    for t, e in ev:
        if e == 'S':
            if cur:
                tr.append(cur)
            cur, bits = {'t': t, 'bytes': [], 'rest': None, 'stop': False}, []
        elif e == 'P':
            if cur:
                cur['rest'] = bits or None
                cur['stop'] = True
                tr.append(cur)
            cur, bits = None, []
        elif cur is not None:
            bits.append(e)
            if len(bits) == 9:
                cur['bytes'].append((int(''.join(map(str, bits[:8])), 2), bits[8] == 0))
                bits = []
    if cur:
        cur['rest'] = bits or None
        tr.append(cur)
    return tr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sr")
    ap.add_argument("--scl", default="SCL")
    ap.add_argument("--sda", default="SDA")
    ap.add_argument("--ref", help="Kanal mit 100-kHz-Referenz (z. B. 2)")
    a = ap.parse_args()
    rate, kanaele, proben = lesen(a.sr)
    n_roh = len(proben)
    proben, spruenge = leerproben_verwerfen(proben)
    print("%s: %d Proben, %.0f Hz" % (a.sr, n_roh, rate))
    if len(proben) != n_roh:
        print("Leerproben verworfen: %d -> %d Proben, %d Paritaetsspruenge (Bytes dort unsicher)"
              % (n_roh, len(proben), spruenge))
    print("Dauer %.2f ms" % (len(proben) / rate * 1e3))
    bc, bd = kanaele[a.scl], kanaele[a.sda]
    scl = [(x >> bc) & 1 for x in proben]
    sda = [(x >> bd) & 1 for x in proben]

    if a.ref:
        br = kanaele[a.ref]
        ref = [(x >> br) & 1 for x in proben]
        st = [i for i in range(1, len(ref)) if ref[i] and not ref[i - 1]]
        abst = collections.Counter(st[i + 1] - st[i] for i in range(len(st) - 1))
        if abst:
            haeufig = abst.most_common(1)[0][0]
            print("Referenz %s: %d Perioden, Abstaende %s -> %.1f kHz bei Dateirate"
                  % (a.ref, len(st) - 1, abst.most_common(3), rate / haeufig / 1e3))

    for t in transaktionen(ereignisse(scl, sda)):
        b = t['bytes']
        zeile = "%9.1f us: S" % (t['t'] / rate * 1e6)
        if b:
            adr, ack = b[0]
            lesend = adr & 1
            zeile += " [%02X %s %s]" % (adr >> 1, 'R' if lesend else 'W', 'A' if ack else 'N')
            zeile += "".join(" %02X%s" % (x, '' if k else '/N') for x, k in b[1:])
        if t['rest']:
            zeile += " +%d Bit" % len(t['rest'])
        zeile += " P" if t['stop'] else " ..."
        print(zeile)
        daten = bytes(x for x, _ in b[1:])
        if b and lesend and len(daten) >= 3 and daten[0] == len(daten):
            print("            Antwort Count %d, CRC %s, berechnet %s -> %s"
                  % (daten[0], daten[-2:].hex(' '), crc_atsha(daten[:-2]).hex(' '),
                     'OK' if crc_atsha(daten[:-2]) == daten[-2:] else 'FALSCH'))
        if b and not lesend and len(daten) >= 4 and daten[0] == 0x03:
            pk = daten[1:]
            if len(pk) == pk[0]:
                print("            Befehl Opcode 0x%02X, CRC %s -> %s" % (
                    pk[1], pk[-2:].hex(' '), 'OK' if crc_atsha(pk[:-2]) == pk[-2:] else 'FALSCH'))
            else:
                print("            Befehl Opcode 0x%02X, Count %d, aber %d Byte mitgeschnitten -- CRC nicht pruefbar"
                      % (pk[1], pk[0], len(pk)))


if __name__ == "__main__":
    main()
