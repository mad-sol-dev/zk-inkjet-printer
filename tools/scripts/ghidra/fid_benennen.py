# Uebernimmt die per Bytevergleich belegten FID-Namen (CL-TOOL-REC-123) aus
# ghidra_projects/fid/fid_belegt.csv, erzeugt von tools/scripts/fid/bytevergleich.py.
#
# - Nur Funktionen mit Standardnamen (FUN_...) werden umbenannt; Quelle IMPORTED,
#   damit sie von Hand vergebenen Namen unterscheidbar bleiben.
# - Vergebene Namen werden nie ueberschrieben; dort steht der FID-Name nur im Kommentar.
# - Jede Funktion bekommt einen Plate-Kommentar mit Herkunft und Vergleichsart.
# Idempotent: ein zweiter Lauf aendert nichts.
#
# @category ZK-Inkjet
# @runtime Jython

import csv
import os
from ghidra.program.model.listing import CodeUnit
from ghidra.program.model.symbol import SourceType

repo = os.path.normpath(os.path.join(getSourceFile().getParentFile().getAbsolutePath(),
                                     "..", "..", ".."))
CSV = os.path.join(repo, "ghidra_projects", "fid", "fid_belegt.csv")
if not os.path.exists(CSV):
    raise Exception("Keine %s -- erst tools/scripts/fid/bytevergleich.py" % CSV)

fm = currentProgram.getFunctionManager()
lst = currentProgram.getListing()
umbenannt = behalten = schon = 0
fehlt = []

for z in csv.DictReader(open(CSV)):
    va = int(z["va"], 16)
    f = fm.getFunctionAt(toAddr(va))
    if f is None:
        fehlt.append(z["va"])
        continue
    art = "byte-identisch" if z["vergleich"] == "GLEICH" else "gleich bis auf Literalpool-Abstand"
    plate = ("FID n32901_bsp: %s aus %s, %s (bytevergleich.py, CL-TOOL-REC-123)"
             % (z["name"], z["quelle"], art))
    if f.getName() == z["name"]:
        schon += 1
    elif f.getSymbol().getSource() == SourceType.DEFAULT:
        alt = f.getName()
        f.setName(z["name"], SourceType.IMPORTED)
        umbenannt += 1
        println("   %s  %-14s -> %s" % (z["va"], alt, z["name"]))
    else:
        behalten += 1
        println("   %s  vergeben %-30s bleibt, FID sagt %s" % (z["va"], f.getName(), z["name"]))
    if lst.getComment(CodeUnit.PLATE_COMMENT, toAddr(va)) != plate:
        lst.setComment(toAddr(va), CodeUnit.PLATE_COMMENT, plate)

println("umbenannt %d, vergebene Namen behalten %d, schon richtig %d, keine Funktion %d"
        % (umbenannt, behalten, schon, len(fehlt)))
if fehlt:
    raise Exception("Keine Funktion an: %s" % ", ".join(fehlt))
