# Prueft eine Kandidatenliste fuer funktionen_anlegen.py gegen die Datenbank.
# Liest nur. Erwartet als Argument den Pfad zu einer Textdatei mit Zeilen der Form
#     (0x00071888, 0xE92D4FFF, "Herkunft"),
# wie sie research/phase_a_sd_analysis/artifacts/funktionen_kandidaten_*.txt enthaelt.
#
# Je Kandidat eine Einstufung:
#   WORT     das erwartete erste Wort steht nicht dort (Liste fehlerhaft)
#   DA       an der Adresse beginnt schon eine Funktion (Liste veraltet)
#   DRIN     die Adresse liegt im Koerper einer anderen Funktion
#   DATEN    dort ist ein Datenobjekt definiert
#   FREI     nichts davon -- echter Kandidat; mit Vermerk, ob dort schon
#            Befehle disassembliert sind (CODE) oder nicht (ROH)
#
# @category ZK-Inkjet
# @runtime Jython

import re

args = getScriptArgs()
if len(args) < 1:
    raise Exception("Aufruf: kandidaten_pruefen.py <pfad zur Kandidatendatei>")

ZEILE = re.compile(r'\(\s*(0x[0-9A-Fa-f]+)\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*"([^"]*)"\s*\)')
kand = []
for z in open(args[0]):
    m = ZEILE.search(z)
    if m:
        kand.append((int(m.group(1), 16), int(m.group(2), 16), m.group(3)))
println("Kandidaten gelesen: %d" % len(kand))

mem = currentProgram.getMemory()
fm = currentProgram.getFunctionManager()
lst = currentProgram.getListing()

zaehler = {}
zeilen = []
for va, wort, herkunft in kand:
    a = toAddr(va)
    w = mem.getInt(a) & 0xFFFFFFFF
    if w != wort:
        stufe, info = "WORT", "steht 0x%08X" % w
    elif fm.getFunctionAt(a) is not None:
        stufe, info = "DA", fm.getFunctionAt(a).getName()
    elif fm.getFunctionContaining(a) is not None:
        f = fm.getFunctionContaining(a)
        stufe, info = "DRIN", "%s @ %s" % (f.getName(), f.getEntryPoint())
    elif lst.getDefinedDataContaining(a) is not None:
        d = lst.getDefinedDataContaining(a)
        stufe, info = "DATEN", "%s @ %s" % (d.getDataType().getName(), d.getMinAddress())
    else:
        stufe = "FREI"
        info = "CODE" if lst.getInstructionAt(a) is not None else "ROH"
    zaehler[stufe] = zaehler.get(stufe, 0) + 1
    zeilen.append("%s 0x%08X  %-28s | %s" % (stufe.ljust(5), va, info[:28], herkunft))

println("Einstufung: " + ", ".join("%s %d" % (k, zaehler[k]) for k in sorted(zaehler)))


def art(herkunft):
    # Staerkster Verweis zuerst: ein BL ist ein Aufruf, ein Poolwort ein geladener
    # Zeiger, ein Datenwort nur ein Wert in einer Tabelle.
    if herkunft.startswith("BL von") or "; BL von" in herkunft:
        return "BL"
    if herkunft.startswith("Poolwort"):
        return "Pool"
    if herkunft.startswith("Datenwort"):
        return "Daten-dicht" if "dichte Zeigerfolge" in herkunft else "Daten"
    return "ohne"


matrix = {}
for z in zeilen:
    teile = z.split("|", 1)
    kopf, herkunft = teile[0].split(), teile[1].strip()
    if kopf[0] != "FREI":
        continue
    schl = (art(herkunft), kopf[2])
    matrix[schl] = matrix.get(schl, 0) + 1
println("FREI nach Verweisart x Zustand (CODE = schon disassembliert, ROH = nie):")
for a in ("BL", "Pool", "Daten", "Daten-dicht", "ohne"):
    println("  %-11s CODE %3d  ROH %3d" % (a, matrix.get((a, "CODE"), 0), matrix.get((a, "ROH"), 0)))

if len(args) < 2 or args[1] != "kurz":
    for z in zeilen:
        println(z)
