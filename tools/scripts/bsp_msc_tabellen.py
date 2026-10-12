#!/usr/bin/env python3
"""Vergleicht die Datentabellen aus BSP mscd.c byteweise mit der ausgerollten
RW-Region von APP.bin (CL-USB-REC-127).

Die Tabellen werden aus dem Quelltext gelesen, nicht abgeschrieben: die
UINT32-Felder als Worte, die UINT8-Felder als Bytes und Zeichen. Die Makros
(USB_VID/USB_PID in mscd.c, MSC_DEVICE_DSCPT_LEN in mass_storage_class.h)
werden aus beiden Dateien geholt. Die Laengenbytes der String-Deskriptoren setzt mscdInit zur Laufzeit
auf sizeof() -- im Quelltext stehen dieselben Werte als Vorbelegung.

Die Adressen in APP sind die Labels aus tools/scripts/ghidra/zuordnung/bsp_msc.csv.
Gibt pro Tabelle GLEICH oder die erste abweichende Position aus; Rueckgabewert
ist die Zahl der Abweichungen.

    python3 tools/scripts/bsp_msc_tabellen.py
"""
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scatter_unpack as su  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
APP = os.path.join(REPO, "firmware", "bin", "ZK-INKJET-NANO-APP.bin")
MSC = os.path.join(REPO, "vendor", "N32901-3_NonOS_BSP", "UDC", "src", "MSC", "mscd.c")
KOPF = os.path.join(REPO, "vendor", "N32901-3_NonOS_BSP", "UDC", "lib", "mass_storage_class.h")

# Tabelle -> VA in der RW-Region
ZIELE = [
    ("MSC_DeviceDescriptor", 0x9F8),
    ("MSC_QualifierDescriptor", 0xA0C),
    ("MSC_ConfigurationBlock", 0xA18),
    ("MSC_ConfigurationBlockFull", 0xA38),
    ("MSC_HOSConfigurationBlock", 0xA58),
    ("MSC_FOSConfigurationBlock", 0xA78),
    ("MSC_StringDescriptor1", 0xA9C),
    ("MSC_StringDescriptor2", 0xAAC),
    ("MSC_StringDescriptor3", 0xABC),
    ("InquiryID", 0xAF0),
]


def makros():
    m = {}
    for pfad in (KOPF, MSC):
        for z in open(pfad, encoding="latin-1"):
            t = re.match(r"\s*#define\s+(\w+)\s+(0x[0-9A-Fa-f]+|\d+)\b", z)
            if t:
                m[t.group(1)] = int(t.group(2), 0)
    return m


def wert(ausdruck, m):
    a = ausdruck.strip()
    if not a:
        return None
    if a.startswith("'"):
        return ord(a[1])
    for k, v in m.items():
        a = re.sub(r"\b%s\b" % k, str(v), a)
    return eval(a, {"__builtins__": {}}) & 0xFF


def tabelle(text, name, m):
    t = re.search(r"\b%s\s*\[[^\]]*\]\s*=\s*\{(.*?)\};" % re.escape(name), text, re.S)
    if not t:
        sys.exit("Tabelle %s nicht im Quelltext" % name)
    rumpf = re.sub(r"/\*.*?\*/|//[^\n]*", "", t.group(1), flags=re.S)
    kopf = text[max(0, t.start() - 80):t.start() + len(name)]
    teile = [x for x in rumpf.split(",") if x.strip()]
    if "UINT32" in kopf.splitlines()[-1]:
        return b"".join(struct.pack("<I", int(x.strip(), 0)) for x in teile)
    return bytes(wert(x, m) for x in teile)


def main():
    text = open(MSC, encoding="latin-1").read()
    m = makros()
    d = open(APP, "rb").read()
    rw = [s for s in su.region(d, "rw") if s[0] == 0x60][0]
    basis, roh = rw[0], rw[2]
    fehler = 0
    for name, va in ZIELE:
        soll = tabelle(text, name, m)
        ist = roh[va - basis:va - basis + len(soll)]
        if ist == soll:
            print("GLEICH      0x%04X  %-28s %3d Byte" % (va, name, len(soll)))
        else:
            i = next(k for k in range(len(soll)) if ist[k] != soll[k])
            print("ABWEICHUNG  0x%04X  %-28s ab +%d: soll %s ist %s"
                  % (va, name, i, soll[i:i + 8].hex(), ist[i:i + 8].hex()))
            fehler += 1
    return fehler


if __name__ == "__main__":
    sys.exit(main())
