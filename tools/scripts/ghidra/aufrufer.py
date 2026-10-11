# Uebersicht zu Adressen: Funktion, Groesse, aufrufende Funktionen (mit Zahl der
# Aufrufstellen). Aendert nichts.
#
# Argumente: Adressen, hex, durch Leerzeichen getrennt, z. B. "0xC7D90 0x750C0".
#
# @category ZK-Inkjet
# @runtime Jython

from ghidra.program.model.symbol import RefType

fm = currentProgram.getFunctionManager()
rm = currentProgram.getReferenceManager()

for arg in getScriptArgs():
    a = toAddr(int(arg, 16))
    f = fm.getFunctionAt(a)
    if f is None:
        drin = fm.getFunctionContaining(a)
        println("%s  KEINE Funktion%s" % (arg, (" (liegt in %s)" % drin.getName()) if drin else ""))
        continue
    aufrufer = {}
    sonst = 0
    for r in rm.getReferencesTo(a):
        if r.getReferenceType().isCall():
            g = fm.getFunctionContaining(r.getFromAddress())
            n = "%s@%s" % (g.getName(), g.getEntryPoint()) if g else "ohne-Funktion@%s" % r.getFromAddress()
            aufrufer[n] = aufrufer.get(n, 0) + 1
        else:
            sonst += 1
    println("%s  %-28s %5d Bytes  %3d Aufrufstellen in %2d Funktionen, %d andere Refs"
            % (arg, f.getName(), f.getBody().getNumAddresses(), sum(aufrufer.values()), len(aufrufer), sonst))
    for n in sorted(aufrufer, key=lambda k: -aufrufer[k]):
        println("      %3d x %s" % (aufrufer[n], n))
