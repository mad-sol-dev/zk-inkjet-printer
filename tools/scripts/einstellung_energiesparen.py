#!/usr/bin/env python3
"""Display-Abschaltung im Einstellungsblock der Karte ein- oder ausschalten (CL-FIRMWARE-REC-122).

Befund 2026-10-14: ui_event_wait (0x6A520) schaltet das Display ab, wenn seit der letzten Eingabe
mehr als [0xD00+0x170] Sekunden vergangen sind und [0xD00+0x16C] != 0 ist (Port 8 Pin 0 ueber
FUN_0008a2d4(0), dazu eine bildschirmfuellende Aufweck-Schaltflaeche 0x177). Die Struktur 0xD00 ist
der Einstellungsblock, den settings_load_validate_save (0xBA778) beim Start mit 400 Byte ab Karte
0x28000000 fuellt. Geprueft wird dort nur das Magic-Wort 0x01348D18 bei +0x188; stimmt es nicht,
setzt die Firmware Vorgaben und verlangt eine neue Touch-Kalibrierung. Kein Code schreibt +0x16C oder
+0x170, es gibt also keinen Menuepunkt. APP.bin bleibt unberuehrt, ein MD5-Kopf ist nicht noetig.

Geschrieben wird genau ein Sektor (Karte 0x28000000 = LBA 0x140000). Vorher wird er gesichert und
geprueft (Magic-Wort, Slot 0 bei 0x28800000 beginnt mit dem Dokumentkopf 22 20), danach
zurueckgelesen.

  sudo python3 tools/scripts/einstellung_energiesparen.py /dev/sdX --aus
  sudo python3 tools/scripts/einstellung_energiesparen.py /dev/sdX --sekunden 600
  sudo python3 tools/scripts/einstellung_energiesparen.py /dev/sdX --zeigen
  sudo python3 tools/scripts/einstellung_energiesparen.py /dev/sdX --zurueck SICHERUNG
"""
import argparse
import os
import struct
import sys

BLOCK = 0x28000000
SLOT0 = 0x28800000
MAGIC_OFF, MAGIC = 0x188, 0x01348D18
SCHALTER, SEKUNDEN = 0x16C, 0x170
SICHERUNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "research",
                         "phase_a_sd_analysis", "artifacts", "energiesparen", "sektor_28000000.sicherung")


def lesen(dev, off, n=512):
    try:
        fd = os.open(dev, os.O_RDONLY | getattr(os, "O_DIRECT", 0))
    except OSError:  # Dateisystem ohne O_DIRECT, z. B. beim Test an einer Abbilddatei
        fd = os.open(dev, os.O_RDONLY)
    try:
        import mmap
        buf = mmap.mmap(-1, n)
        os.preadv(fd, [buf], off)
        return bytes(buf)
    finally:
        os.close(fd)


def schreiben(dev, off, data):
    fd = os.open(dev, os.O_WRONLY | os.O_SYNC)
    try:
        os.pwrite(fd, data, off)
        os.fsync(fd)
    finally:
        os.close(fd)


def zeigen(s):
    print("Schalter +0x16C = %d, Sekunden +0x170 = %d, Magic +0x188 = %#x"
          % (struct.unpack_from("<i", s, SCHALTER)[0], struct.unpack_from("<i", s, SEKUNDEN)[0],
             struct.unpack_from("<I", s, MAGIC_OFF)[0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("device")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--aus", action="store_true", help="Display nie abschalten (+0x16C = 0)")
    g.add_argument("--ein", action="store_true", help="Abschaltung wieder an (+0x16C = 1)")
    g.add_argument("--sekunden", type=int, help="Abschaltung an, nach N Sekunden")
    g.add_argument("--zeigen", action="store_true")
    g.add_argument("--zurueck", metavar="SICHERUNG")
    a = ap.parse_args()

    alt = lesen(a.device, BLOCK)
    kopf = lesen(a.device, SLOT0)
    if struct.unpack_from("<I", alt, MAGIC_OFF)[0] != MAGIC or kopf[:2] != b"\x22\x20":
        sys.exit("Kein Einstellungsblock dieses Geraets auf %s (Magic oder Slot-0-Kopf fehlt) -- nichts geschrieben" % a.device)
    zeigen(alt)
    if a.zeigen:
        return

    if a.zurueck:
        neu = open(a.zurueck, "rb").read()
        if len(neu) != 512 or struct.unpack_from("<I", neu, MAGIC_OFF)[0] != MAGIC:
            sys.exit("Sicherung ungueltig -- nichts geschrieben")
    else:
        neu = bytearray(alt)
        if a.aus:
            struct.pack_into("<i", neu, SCHALTER, 0)
        elif a.ein:
            struct.pack_into("<i", neu, SCHALTER, 1)
        else:
            if not 5 <= a.sekunden <= 86400:
                sys.exit("--sekunden zwischen 5 und 86400")
            struct.pack_into("<i", neu, SCHALTER, 1)
            struct.pack_into("<i", neu, SEKUNDEN, a.sekunden)
        neu = bytes(neu)
        geaendert = [hex(i) for i in range(512) if neu[i] != alt[i]]
        if not geaendert:
            print("Schon so eingestellt -- nichts zu tun")
            return
        print("Aendert Bytes", geaendert)
        os.makedirs(os.path.dirname(SICHERUNG), exist_ok=True)
        if not os.path.exists(SICHERUNG):
            open(SICHERUNG, "wb").write(alt)
            print("Sicherung:", os.path.normpath(SICHERUNG))

    if input("1 Sektor bei Karte %#x schreiben? [j/N] " % BLOCK).strip() != "j":
        sys.exit("abgebrochen, nichts geschrieben")
    schreiben(a.device, BLOCK, neu)
    zurueck = lesen(a.device, BLOCK)
    if zurueck != neu:
        sys.exit("Ruecklesen weicht ab -- mit --zurueck %s wiederherstellen" % os.path.normpath(SICHERUNG))
    print("geschrieben und zurueckgelesen:")
    zeigen(zurueck)


if __name__ == "__main__":
    main()
