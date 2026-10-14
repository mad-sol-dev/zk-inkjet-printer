#!/usr/bin/env python3
# /// script
# dependencies = ["pyserial"]
# ///
"""Zeilen des ESP32-I2C-Mitlesers lesen und als ATSHA204A-Verkehr deuten (CL-HARDWARE-REC-117).

Jede Transaktion wird mit Zeitstempel ausgegeben und, wo moeglich, gedeutet: Word-Address beim
Schreiben (0x00 Reset, 0x01 Sleep, 0x02 Idle, 0x03 Befehl), Befehlspakete mit Opcode-Name und
CRC-Pruefung, Antworten mit Count und CRC, Status-Antworten mit Namen. Rohzeilen und Deutung
gehen mit --log zusaetzlich in eine Datei (Rohzeile zuerst, damit die Datei wieder einlesbar ist).

  uv run tools/esp32_i2c_sniffer/sniff.py [--port /dev/ttyUSB0] [--log mitschnitt.txt]
  python3 tools/esp32_i2c_sniffer/sniff.py --datei mitschnitt.txt   # gespeicherte Rohzeilen neu deuten
"""
import argparse
import collections
import gzip
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from sr_i2c_atsha import crc_atsha  # noqa: E402

# Opcodes laut ATSHA204A-Datenblatt; genau diese 14 kennt die Firmware (CL-FIRMWARE-REC-120)
OPCODES = {0x01: "Pause", 0x02: "Read", 0x08: "MAC", 0x11: "HMAC", 0x12: "Write", 0x15: "GenDig",
           0x16: "Nonce", 0x17: "Lock", 0x1B: "Random", 0x1C: "DeriveKey", 0x20: "UpdateExtra",
           0x28: "CheckMac", 0x30: "DevRev", 0x47: "SHA"}
STATUS = {0x00: "ok", 0x01: "CheckMac-Fehlvergleich", 0x03: "Parse-Fehler", 0x0F: "Ausfuehrungsfehler",
          0x11: "nach Wake", 0xFF: "CRC-/Kommunikationsfehler"}
WORDADR = {0x00: "Reset", 0x01: "Sleep", 0x02: "Idle"}
WECKZEITEN = []  # Zeitpunkte der Weckpulse fuer die Abstandsstatistik
AKTIV = []  # Zeitstempel jeder Bus-Zeile, auch undeutbarer -- Herzschlag unabhaengig von der Dekodierung


def deuten(zeile, stat):
    """Rohzeile -> Deutung (oder None, wenn keine Transaktionszeile)."""
    teile = zeile.split()
    if len(teile) < 2 or not teile[0][0].isdigit():
        return None
    AKTIV.append(float(teile[0]))
    if teile[1] == "PEGEL":
        stat["pegelwechsel"] += 1
        return "Ruhepegel " + " ".join(teile[2:])
    if teile[1] == "WAKE":
        stat["wake"] += 1
        if int(teile[2]) >= 1000:
            WECKZEITEN.append(float(teile[0]))
        return "Weckpuls %.2f ms" % (int(teile[2]) / 1000)
    toks = [t for t in teile[1:] if t not in ("S", "Sr", "P", "...")]
    byts, nacks = [], []
    for t in toks:
        if t.startswith("b") or t == "?":
            return "unvollstaendige Bits: " + " ".join(teile[1:])
        nacks.append(t.endswith("-"))
        byts.append(int(t.rstrip("-"), 16))
    if not byts:
        return None
    adr, daten = byts[0], bytes(byts[1:])
    if nacks[0]:
        stat["adr_nack"] += 1
        return "Adresse 0x%02X %s -> NACK (Baustein beschaeftigt oder schlaeft)" % (adr >> 1, "R" if adr & 1 else "W")
    kopf = "0x%02X %s" % (adr >> 1, "R" if adr & 1 else "W")
    if adr & 1:  # Lesen
        if len(daten) >= 3 and daten[0] == len(daten):
            ok = crc_atsha(daten[:-2]) == daten[-2:]
            stat["antwort_ok" if ok else "antwort_crc_falsch"] += 1
            text = "%s Antwort %d Byte, CRC %s" % (kopf, daten[0], "OK" if ok else "FALSCH")
            if daten[0] == 4:
                text += ", Status 0x%02X (%s)" % (daten[1], STATUS.get(daten[1], "?"))
            return text
        return "%s %d Byte gelesen, kein ATSHA-Rahmen" % (kopf, len(daten))
    # Schreiben
    if len(daten) == 1 and daten[0] in WORDADR:
        stat[WORDADR[daten[0]]] += 1
        return "%s %s" % (kopf, WORDADR[daten[0]])
    if daten and daten[0] == 0x03 and len(daten) >= 2:
        pk = daten[1:]
        if len(pk) != pk[0] or len(pk) < 7:
            stat["befehl_unvollstaendig"] += 1
            return "%s Befehl unvollstaendig (Count %d, %d Byte)" % (kopf, pk[0], len(pk))
        op, p1, p2 = pk[1], pk[2], pk[3] | (pk[4] << 8)
        ok = crc_atsha(pk[:-2]) == pk[-2:]
        name = OPCODES.get(op, "unbekannt")
        stat["befehl %s CRC %s" % (name, "OK" if ok else "FALSCH")] += 1
        stat["%s Mode 0x%02X Slot %d" % (name, p1, p2)] += 1
        return "%s Befehl %s (0x%02X) Param1 0x%02X Param2 0x%04X, %d Datenbyte, CRC %s" % (
            kopf, name, op, p1, p2, len(pk) - 7, "OK" if ok else "FALSCH")
    return "%s %d Byte geschrieben" % (kopf, len(daten))


def zeilen_seriell(port, baud):
    import serial
    s = serial.Serial()
    s.port, s.baudrate, s.timeout = port, baud, 1
    s.dtr = s.rts = False  # Oeffnen soll den ESP32 nicht zuruecksetzen
    s.open()
    puffer = b""
    while True:
        puffer += s.read(4096)
        while b"\n" in puffer:
            z, puffer = puffer.split(b"\n", 1)
            yield z.decode(errors="replace").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="/dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=921600)
    ap.add_argument("--log", help="Rohzeilen und Deutung zusaetzlich in diese Datei")
    ap.add_argument("--datei", help="gespeicherte Rohzeilen deuten statt seriell lesen")
    a = ap.parse_args()
    stat = collections.Counter()
    log = open(a.log, "a", encoding="utf-8") if a.log else None
    if a.datei:
        oeffnen = gzip.open if a.datei.endswith(".gz") else open
        quelle = (z.strip() for z in oeffnen(a.datei, "rt", encoding="utf-8"))
    else:
        quelle = zeilen_seriell(a.port, a.baud)
    try:
        for z in quelle:
            if not z or z.startswith("=") or z.startswith("    "):
                continue
            if z.startswith("#") or z.startswith("!"):
                print(z)
                if log:
                    log.write(z + "\n")
                continue
            d = deuten(z, stat)
            if d is None:
                continue
            print("%-60s  %s" % (z if len(z) <= 60 else z[:57] + "...", d))
            if log:
                log.write(z + "\n    = " + d + "\n")
                log.flush()
    except KeyboardInterrupt:
        pass
    print("\n# Zusammenfassung: " + ", ".join("%s %d" % kv for kv in sorted(stat.items())))
    if len(WECKZEITEN) > 1:
        abst = sorted(round((b - a) * 1000, 1) for a, b in zip(WECKZEITEN, WECKZEITEN[1:]))
        print("# Weckpuls-Abstand ms: Median %.1f, 10 %% %.1f, 90 %% %.1f, Maximum %.1f, ueber 100 ms: %d von %d"
              % (abst[len(abst) // 2], abst[len(abst) // 10], abst[len(abst) * 9 // 10], abst[-1],
                 sum(1 for x in abst if x > 100), len(abst)))
    if AKTIV:
        # Buendel = Aktivitaet mit weniger als 100 ms Abstand; Pausen ueber 2 s einzeln melden
        start = [AKTIV[0]] + [b for a, b in zip(AKTIV, AKTIV[1:]) if b - a > 0.1]
        pausen = ["%.2f..%.2f s" % (a, b) for a, b in zip(start, start[1:]) if b - a > 2]
        print("# Aktivitaet: %d Buendel von %.2f bis %.2f s, Pausen ueber 2 s: %s"
              % (len(start), AKTIV[0], AKTIV[-1], ", ".join(pausen) or "keine"))
    if log:
        log.write("# Zusammenfassung %s: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),
                                                   ", ".join("%s %d" % kv for kv in sorted(stat.items()))))


if __name__ == "__main__":
    main()
