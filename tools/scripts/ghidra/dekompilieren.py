# Dekompiliert eine Funktion und schreibt den C-Text nach ghidra_projects/dekompiliert/<adresse>.c.
# Aendert nichts am Programm. Argumente: eine oder mehrere Adressen, hex.
#
# @category ZK-Inkjet
# @runtime Jython

import os
from ghidra.app.decompiler import DecompInterface

repo = os.path.normpath(os.path.join(getSourceFile().getParentFile().getAbsolutePath(), "..", "..", ".."))
ziel = os.path.join(repo, "ghidra_projects", "dekompiliert")
if not os.path.isdir(ziel):
    os.makedirs(ziel)
d = DecompInterface()
d.openProgram(currentProgram)
for arg in getScriptArgs():
    a = toAddr(int(arg, 16))
    f = currentProgram.getFunctionManager().getFunctionContaining(a)
    if f is None:
        println("%s: keine Funktion" % arg)
        continue
    r = d.decompileFunction(f, 300, monitor)
    if not r.decompileCompleted():
        raise Exception("Dekompilieren fehlgeschlagen: %s" % r.getErrorMessage())
    pfad = os.path.join(ziel, "%08x_%s.c" % (f.getEntryPoint().getOffset(), f.getName()))
    open(pfad, "w").write(r.getDecompiledFunction().getC())
    println("%s, %d Zeilen -> %s" % (f.getName(), r.getDecompiledFunction().getC().count("\n"), pfad))
