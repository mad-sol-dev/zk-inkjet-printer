# Uebernimmt per Bytevergleich belegte BSP-Namen (CL-TOOL-REC-123/-125) aus einer
# CSV von tools/scripts/fid/bytevergleich.py. Argument: Dateiname in
# ghidra_projects/fid/ (Standard fid_belegt.csv, sonst z. B. norm_belegt.csv).
#
# - Fehlt an der Adresse eine Funktion, wird sie als ARM angelegt -- ausser die
#   Adresse liegt im Rumpf einer anderen Funktion; dann nur Meldung.
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
from ghidra.app.cmd.disassemble import ArmDisassembleCommand
from ghidra.app.cmd.function import CreateFunctionCmd

repo = os.path.normpath(os.path.join(getSourceFile().getParentFile().getAbsolutePath(),
                                     "..", "..", ".."))
args = getScriptArgs()
CSV = os.path.join(repo, "ghidra_projects", "fid", args[0] if args else "fid_belegt.csv")
if not os.path.exists(CSV):
    raise Exception("Keine %s -- erst tools/scripts/fid/bytevergleich.py" % CSV)

fm = currentProgram.getFunctionManager()
lst = currentProgram.getListing()
umbenannt = behalten = schon = angelegt = 0
fehlt = []

for z in csv.DictReader(open(CSV)):
    va = int(z["va"], 16)
    a = toAddr(va)
    f = fm.getFunctionAt(a)
    if f is None:
        drin = fm.getFunctionContaining(a)
        if drin is not None:
            fehlt.append("%s (in %s)" % (z["va"], drin.getName()))
            continue
        if lst.getInstructionAt(a) is None:
            ArmDisassembleCommand(a, None, False).applyTo(currentProgram, monitor)
        CreateFunctionCmd(a).applyTo(currentProgram, monitor)
        f = fm.getFunctionAt(a)
        if f is None:
            fehlt.append("%s (nicht anlegbar)" % z["va"])
            continue
        angelegt += 1
    art = "byte-identisch" if z["vergleich"] == "GLEICH" else "gleich bis auf Literalpool-Abstand"
    plate = ("BSP n32901: %s aus %s, %s (bytevergleich.py, %s)"
             % (z["name"], z["quelle"], art, os.path.basename(CSV)))
    if f.getName() == z["name"]:
        schon += 1
    elif f.isThunk():
        # Ein Thunk-Name kann auf die Zielfunktion durchschlagen -- nur kommentieren.
        fehlt.append("%s (Thunk auf %s, nur Kommentar)" % (z["va"], f.getThunkedFunction(False).getName()))
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

println("angelegt %d, umbenannt %d, vergebene Namen behalten %d, schon richtig %d, uebersprungen %d"
        % (angelegt, umbenannt, behalten, schon, len(fehlt)))
for x in fehlt:
    println("   uebersprungen: %s" % x)
