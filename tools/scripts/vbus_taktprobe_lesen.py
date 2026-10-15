#!/usr/bin/env python3
"""Liest und wertet den Messstand Taktprobe aus (patch_vbus_taktprobe.py, CL-USB-REC-131).

Gelesen wird WACHT 0x2D7000..0x2D7120 ueber das RAM-Fenster (mit dessen
Positivkontrolle) oder aus einer gespeicherten Datei. Auswertung wie im
Next_Test von CL-USB-REC-131:
  Takt je Datensatz: EPA_MPS nach Wartezeit == Probewert und nach dem
    Zurueckschreiben wieder alt -> laeuft; beide Lesungen == alt -> steht.
  SPERRE steht und AN1 laeuft -> Kandidat 2 (TCLKOK_IS in AN1 bestaetigt den Neustart)
  SPERRE laeuft und VBUS_IS bleibt nach der Quittung -> Kandidat 1 oder 3
  AN1 steht -> Positivkontrolle fehlgeschlagen, die Probe ist untauglich, kein Urteil

  sudo python3 tools/scripts/vbus_taktprobe_lesen.py /dev/sdX [--speichern datei.bin]
  python3 tools/scripts/vbus_taktprobe_lesen.py --datei datei.bin
"""
import argparse
import struct
import sys

WACHT, LAENGE = 0x2D7000, 0x120
MAGIC = 0x31504B54
SAETZE = [("SPERRE", 0x20, "W1, Moment des Sperrens, mit Quittung"),
          ("SPAET", 0x60, "W2, 1000 Ticks nach dem Sperren, Kabel weg, mit Quittung"),
          ("AN0", 0xA0, "W2, erster Tick mit Kabel, vor der Freigabe, ohne Quittung"),
          ("AN1", 0xE0, "W2, 10 Ticks nach der Freigabe, ohne Quittung (Positivkontrolle)")]
FELDER = ["n", "tick", "stat", "enb", "phy", "ahbclk", "oper", "mps_alt", "probe", "mps_sofort",
          "mps_spaet", "mps_zurueck", "stat_q_sofort", "stat_q_spaet", "quittiert", "magic"]
STAT_BITS = [(8, "VBUS"), (7, "RUM_NOCLK"), (6, "TCLKOK"), (5, "DMACOM"), (4, "HISPD"), (3, "SUS"),
             (2, "RUM"), (1, "RST"), (0, "SOF")]


def bits(w):
    return "|".join(n for b, n in STAT_BITS if w >> b & 1) or "-"


def zerlegen(roh):
    kopf = dict(zip(["merker", "sperren", "freigaben", "ticks", "countdown"], struct.unpack_from("<5I", roh, 0)))
    saetze = {}
    for name, off, _ in SAETZE:
        s = dict(zip(FELDER, struct.unpack_from("<16I", roh, off)))
        saetze[name] = s if s["magic"] == MAGIC else None
    return kopf, saetze


def takt(s):
    if s is None:
        return "fehlt"
    if s["mps_spaet"] == s["probe"] and s["mps_zurueck"] == s["mps_alt"]:
        return "laeuft"
    if s["mps_sofort"] == s["mps_alt"] and s["mps_spaet"] == s["mps_alt"]:
        return "steht"
    return "unklar"


def urteil(saetze):
    sp, an1 = saetze["SPERRE"], saetze["AN1"]
    if sp is None or an1 is None:
        return "kein Urteil: Datensatz %s fehlt" % ("SPERRE" if sp is None else "AN1")
    t_sp, t_an1 = takt(sp), takt(an1)
    if t_an1 != "laeuft":
        return "kein Urteil: Positivkontrolle AN1 '%s' -- die Probe ist so nicht tauglich" % t_an1
    bleibt = bool(sp["stat_q_spaet"] & 0x100)
    if t_sp == "steht" and bleibt:
        return "Kandidat 2: ohne Kabel steht der Takt, VBUS_IS bleibt; mit Kabel laeuft er%s" % (
            " (TCLKOK_IS in AN1 gesetzt: Neustart bestaetigt)" if an1["stat"] & 0x40 else
            " (TCLKOK_IS in AN1 nicht gesetzt)")
    if t_sp == "laeuft" and bleibt:
        return "Kandidat 1 oder 3: Takt laeuft beim Sperren, VBUS_IS bleibt trotzdem"
    if not bleibt:
        return "unerwartet: VBUS_IS liess sich beim Sperren loeschen (Takt %s)" % t_sp
    return "unklar: Takt beim Sperren '%s'" % t_sp


def bericht(roh):
    kopf, saetze = zerlegen(roh)
    print("WACHT 0x%X: Merker %d, Sperren %d, Freigaben %d, Ticks seit Sperre %d, Countdown %d"
          % (WACHT, kopf["merker"], kopf["sperren"], kopf["freigaben"], kopf["ticks"], kopf["countdown"]))
    for name, off, text in SAETZE:
        s = saetze[name]
        print("== %s @0x%X -- %s" % (name, WACHT + off, text))
        if s is None:
            print("   nicht geschrieben")
            continue
        print("   n %d, Tick %d" % (s["n"], s["tick"]))
        print("   USB_IRQ_STAT 0x%03X (%s), USB_IRQ_ENB 0x%03X" % (s["stat"], bits(s["stat"]), s["enb"]))
        print("   PHY_CTL 0x%08X (Vbus_status %d, Phy_suspend %d, vbus_detect %d), AHBCLK 0x%08X (USBD_CKE %d), USB_OPER 0x%X (CUR_SPD %d)"
              % (s["phy"], s["phy"] >> 31, s["phy"] >> 9 & 1, s["phy"] >> 8 & 1, s["ahbclk"], s["ahbclk"] >> 18 & 1,
                 s["oper"], s["oper"] >> 2 & 1))
        print("   EPA_MPS alt 0x%X, Probewert 0x%X -> sofort 0x%X, nach Wartezeit 0x%X; zurueckgeschrieben 0x%X  => Takt %s"
              % (s["mps_alt"], s["probe"], s["mps_sofort"], s["mps_spaet"], s["mps_zurueck"], takt(s)))
        if s["quittiert"]:
            print("   Quittung 0x100: USB_IRQ_STAT sofort 0x%03X (%s), nach Wartezeit 0x%03X (%s)"
                  % (s["stat_q_sofort"], bits(s["stat_q_sofort"]), s["stat_q_spaet"], bits(s["stat_q_spaet"])))
    u = urteil(saetze)
    print("URTEIL: " + u)
    return u


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dev", nargs="?")
    ap.add_argument("--datei", help="gespeicherten Abzug 0x2D7000..0x2D7120 auswerten")
    ap.add_argument("--speichern", help="gelesene Bytes zusaetzlich in diese Datei schreiben")
    a = ap.parse_args()
    if a.datei:
        roh = open(a.datei, "rb").read()
    elif a.dev:
        import ram_fenster_lesen as rf
        rf.kontrolle(a.dev)
        roh = rf.lesen(a.dev, WACHT, LAENGE)
        if a.speichern:
            open(a.speichern, "wb").write(roh)
            print("gespeichert: %s" % a.speichern)
    else:
        sys.exit("Geraet oder --datei angeben")
    if len(roh) != LAENGE:
        sys.exit("Laenge %d statt %d" % (len(roh), LAENGE))
    bericht(roh)


if __name__ == "__main__":
    main()
