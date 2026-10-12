# Zeigt fuer Aufrufstellen (bl/blx) die Werte von r0..r3, soweit sie im selben
# Grundblock direkt vor dem Aufruf per mov/mvn (Immediate) oder ldr [pc,#..]
# (Literalpool) gesetzt werden. Aendert nichts am Programm.
# Argumente: Adressen der Aufrufbefehle, hex. Mit "ziel=<adr>" statt Adressen
# werden alle Aufrufstellen dieser Funktion genommen.
# Nicht aufgeloest ("?") bleibt alles, was aus einem anderen Register, aus
# Speicher ohne PC-Bezug oder aus einem frueheren Block kommt.
#
# @category ZK-Inkjet
# @runtime Jython

from ghidra.program.model.symbol import RefType

lst = currentProgram.getListing()
fm = currentProgram.getFunctionManager()
mem = currentProgram.getMemory()
bbm = ghidra.program.model.block.BasicBlockModel(currentProgram)

stellen = []
for arg in getScriptArgs():
    if arg.startswith("ziel="):
        z = toAddr(int(arg[5:], 16))
        for r in currentProgram.getReferenceManager().getReferencesTo(z):
            if r.getReferenceType().isCall():
                stellen.append(r.getFromAddress())
    else:
        stellen.append(toAddr(int(arg, 16)))
stellen.sort()


def wert(ins):
    """Wert, den ins in sein Zielregister schreibt, oder None."""
    m = ins.getMnemonicString().lower()
    if m in ("mov", "mvn") and ins.getNumOperands() == 2:
        s = ins.getScalar(1)
        if s is None:
            return None
        v = s.getUnsignedValue() & 0xFFFFFFFF
        return (~v) & 0xFFFFFFFF if m == "mvn" else v
    if m == "ldr":
        for r in ins.getReferencesFrom():
            if r.getReferenceType().isData() or r.getReferenceType() == RefType.READ:
                try:
                    return mem.getInt(r.getToAddress()) & 0xFFFFFFFF
                except Exception:
                    return None
    if m == "adr" or (m == "add" and str(ins.getDefaultOperandRepresentation(1)) == "pc"):
        for r in ins.getReferencesFrom():
            return r.getToAddress().getOffset()
    return None


for a in stellen:
    ins = lst.getInstructionAt(a)
    f = fm.getFunctionContaining(a)
    blk = bbm.getFirstCodeBlockContaining(a, monitor)
    start = blk.getFirstStartAddress() if blk else a
    gesetzt = {}
    i = ins.getPrevious()
    while i is not None and i.getAddress().compareTo(start) >= 0 and len(gesetzt) < 4:
        res = i.getResultObjects()
        for o in res:
            n = str(o)
            if n in ("r0", "r1", "r2", "r3") and n not in gesetzt:
                v = wert(i)
                gesetzt[n] = ("0x%X" % v) if v is not None else "? (%s)" % i
        i = i.getPrevious()
    ziel = ins.getFlows()
    zn = ""
    if ziel:
        zf = fm.getFunctionAt(ziel[0])
        zn = zf.getName() if zf else str(ziel[0])
    println("%s  %-24s -> %-20s r0=%s r1=%s r2=%s r3=%s" % (
        a, f.getName() if f else "?", zn,
        gesetzt.get("r0", "-"), gesetzt.get("r1", "-"),
        gesetzt.get("r2", "-"), gesetzt.get("r3", "-")))
