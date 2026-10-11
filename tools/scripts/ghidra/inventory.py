# Zaehlt, was in der Datenbank steht. Aendert nichts.
# Vor und nach dem Verschieben laufen lassen und die Ausgaben vergleichen.
# println statt print: so kommt die Ausgabe auch ueber run_script (GhidraMCPd) zurueck;
# Jythons print geht nur in Ghidras Konsole.
#
# @category ZK-Inkjet
# @runtime Jython

from ghidra.program.model.listing import CodeUnit
import re

ALT_VON, ALT_BIS = 0x00200000, 0x0047522C
VERSATZ = 0x1A8000

fm = currentProgram.getFunctionManager()
st = currentProgram.getSymbolTable()
lst = currentProgram.getListing()

println("Programm: %s" % currentProgram.getName())
for b in currentProgram.getMemory().getBlocks():
    println("  Block %-10s %s .. %s" % (b.getName(), b.getStart(), b.getEnd()))

fn_alle = 0
fn_benannt = 0
for f in fm.getFunctions(True):
    fn_alle += 1
    if not f.getName().startswith("FUN_"):
        fn_benannt += 1
println("\nFunktionen gesamt : %d" % fn_alle)
println("davon benannt     : %d" % fn_benannt)

sym = 0
for s in st.getAllSymbols(False):
    sym += 1
println("Symbole gesamt    : %d" % sym)

daten = 0
for d in lst.getDefinedData(True):
    daten += 1
println("Datenobjekte      : %d" % daten)

TYPEN = [(CodeUnit.EOL_COMMENT, "EOL"), (CodeUnit.PRE_COMMENT, "PRE"),
         (CodeUnit.POST_COMMENT, "POST"), (CodeUnit.PLATE_COMMENT, "PLATE"),
         (CodeUnit.REPEATABLE_COMMENT, "REPEAT")]
muster = re.compile(r"0x([0-9A-Fa-f]{6,8})")
gesamt = 0
verdaechtig = []
for typ, name in TYPEN:
    n = 0
    it = lst.getCommentAddressIterator(typ, currentProgram.getMemory(), True)
    while it.hasNext():
        a = it.next()
        n += 1
        txt = lst.getComment(typ, a)
        if txt:
            for h in muster.findall(txt):
                v = int(h, 16)
                if ALT_VON <= v <= ALT_BIS:
                    verdaechtig.append((str(a), name, v, txt.strip()[:70]))
    println("Kommentare %-7s: %d" % (name, n))
    gesamt += n
println("Kommentare gesamt : %d" % gesamt)

println("\nKommentare mit einer Hexzahl im alten Bereich %s..%s: %d"
      % (hex(ALT_VON), hex(ALT_BIS), len(verdaechtig)))
println("(Diese Zahlen wandern beim Verschieben NICHT mit und waeren danach"
      " um %s zu hoch.)" % hex(VERSATZ))
for a, t, v, txt in verdaechtig:
    println("  %s [%s] 0x%08X -> 0x%08X | %s" % (a, t, v, v - VERSATZ, txt))
