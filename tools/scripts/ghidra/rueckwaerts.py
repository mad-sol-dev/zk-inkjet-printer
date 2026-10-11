# Geht von einer Adresse aus im Kontrollfluss rueckwaerts: Grundblock, seine
# Vorgaenger, deren Vorgaenger ... bis zur Tiefe T. Zu jedem Block die letzten
# Befehle (Vergleich und Sprung). Aendert nichts.
#
# Argumente: "<adresse> [tTiefe]", z. B. "0xC3068 t6".
#
# @category ZK-Inkjet
# @runtime Jython

from ghidra.program.model.block import BasicBlockModel

a = getScriptArgs()
start = toAddr(int(a[0], 16))
tiefe = int(a[1][1:]) if len(a) > 1 else 5
modell = BasicBlockModel(currentProgram)
lst = currentProgram.getListing()


def ende(block, n=4):
    zeilen = []
    ins = lst.getInstructionContaining(block.getMaxAddress())
    while ins is not None and len(zeilen) < n and block.contains(ins.getAddress()):
        zeilen.insert(0, "%s: %s" % (ins.getAddress(), ins))
        ins = ins.getPrevious()
    return zeilen


gesehen = set()
schicht = [(modell.getFirstCodeBlockContaining(start, monitor), None)]
for t in range(tiefe + 1):
    naechste = []
    for b, nach in schicht:
        if b is None or b.getFirstStartAddress() in gesehen:
            continue
        gesehen.add(b.getFirstStartAddress())
        println("%sBlock %s..%s%s" % ("  " * t, b.getFirstStartAddress(), b.getMaxAddress(),
                                      "" if nach is None else "  -> " + str(nach)))
        for z in ende(b):
            println("%s    %s" % ("  " * t, z))
        it = b.getSources(monitor)
        while it.hasNext():
            r = it.next()
            naechste.append((r.getSourceBlock(), b.getFirstStartAddress()))
    schicht = naechste
