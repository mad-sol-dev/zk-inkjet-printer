# Setzt den Block "zi" (Zero-Init-Region der Scatter-Tabelle, CL-BOOT-REC-114)
# auf beschreibbar. rebase_app_to_58000.py hat ihn bis 2026-10-11 nur lesbar
# angelegt; der Decompiler behandelt nur lesbaren Speicher als konstant, fuer
# eine Region, die das Programm zur Laufzeit beschreibt, ist das falsch.
# Idempotent: steht das Recht schon, aendert sich nichts.
#
# @category ZK-Inkjet
# @runtime Jython

mem = currentProgram.getMemory()
blk = mem.getBlock("zi")
if blk is None:
    raise Exception("Kein Block 'zi'. Ist rebase_app_to_58000.py gelaufen?")
if blk.getStart().getOffset() != 0xCE4 or blk.getSize() != 0x442DC:
    raise Exception("Block 'zi' liegt nicht bei 0xCE4 + 0x442DC, sondern bei %s + 0x%X. Abbruch."
                    % (blk.getStart(), blk.getSize()))


def rechte(b):
    return "%s%s%s" % ("r" if b.isRead() else "-", "w" if b.isWrite() else "-",
                       "x" if b.isExecute() else "-")


println("zi vorher : %s .. %s  %s" % (blk.getStart(), blk.getEnd(), rechte(blk)))
blk.setRead(True)
blk.setWrite(True)
blk.setExecute(False)
println("zi nachher: %s .. %s  %s" % (blk.getStart(), blk.getEnd(), rechte(blk)))
if not (blk.isRead() and blk.isWrite() and not blk.isExecute()):
    raise Exception("Rechte nicht wie erwartet gesetzt.")
println("OK")
