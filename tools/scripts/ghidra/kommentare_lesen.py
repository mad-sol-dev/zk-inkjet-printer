# Gibt alle Kommentare (PRE, EOL, PLATE, POST) an den angegebenen Adressen aus. Aendert nichts.
# Argumente: Adressen, hex.
# @category ZK-Inkjet
# @runtime Jython
from ghidra.program.model.listing import CodeUnit
lst = currentProgram.getListing()
for arg in getScriptArgs():
    a = toAddr(int(arg, 16))
    for typ, name in ((CodeUnit.PLATE_COMMENT, "PLATE"), (CodeUnit.PRE_COMMENT, "PRE"),
                      (CodeUnit.EOL_COMMENT, "EOL"), (CodeUnit.POST_COMMENT, "POST")):
        c = lst.getComment(typ, a)
        if c:
            println("%s [%s]\n%s\n" % (arg, name, c))
