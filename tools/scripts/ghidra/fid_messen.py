# Misst, was die BSP-FID-Datenbank (CL-TOOL-REC-123) in APP.bin erkennt. Aendert
# NICHTS am Programm: es fragt nur ab und schreibt eine CSV neben die .fidb.
# Benennen ist ein eigener, spaeterer Schritt.
#
# Eindeutig  = alle Treffer einer Funktion tragen denselben Namen (oft dieselbe
#              Funktion in mehreren Bibliotheksvarianten, z. B. 36 MSC-Bauarten).
# Mehrdeutig = verschiedene Namen; die zaehlen nicht als Erkennung.
#
# @category ZK-Inkjet
# @runtime Jython

import os
from java.io import File
from ghidra.feature.fid.db import FidFileManager
from ghidra.feature.fid.service import FidService
from ghidra.program.model.symbol import SourceType

import traceback
try:
    repo = os.path.normpath(os.path.join(getSourceFile().getParentFile().getAbsolutePath(),
                                         "..", "..", ".."))
    FIDB = os.path.join(repo, "ghidra_projects", "fid", "n32901_bsp.fidb")
    CSV = os.path.join(repo, "ghidra_projects", "fid", "fid_treffer_app.csv")
    if not os.path.exists(FIDB):
        raise Exception("Keine .fidb: %s -- erst tools/scripts/fid/build_bsp_fid.sh" % FIDB)

    fm = FidFileManager.getInstance()
    eigene = [f for f in fm.getFidFiles() if File(str(f.getPath())).getAbsolutePath() == File(FIDB).getAbsolutePath()]
    ff = eigene[0] if eigene else fm.addUserFidFile(File(FIDB))
    ff.setActive(True)

    svc = FidService()
    schwelle = svc.getDefaultScoreThreshold()
    q = svc.openFidQueryService(currentProgram.getLanguage(), False)
    ergebnisse = svc.processProgram(currentProgram, q, schwelle, monitor)
    # Die Treffer lesen ihre Namen aus der offenen Datenbank -- erst am Ende schliessen.

    eindeutig = []
    mehrdeutig = []
    je_lib = {}
    for r in ergebnisse:
        if not r.matches:
            continue
        namen = sorted(set([m.getFunctionRecord().getName() for m in r.matches]))
        libs = sorted(set([m.getLibraryRecord().getLibraryFamilyName() for m in r.matches]))
        score = max([m.getOverallScore() for m in r.matches])
        f = r.function
        alt = f.getName()
        vergeben = f.getSymbol().getSource() != SourceType.DEFAULT
        zeile = (f.getEntryPoint().getOffset(), alt, vergeben, namen, libs, score)
        if len(namen) == 1:
            eindeutig.append(zeile)
            for l in libs:
                je_lib[l] = je_lib.get(l, 0) + 1
        else:
            mehrdeutig.append(zeile)

    with open(CSV, "w") as fh:
        fh.write("va,name_jetzt,vergeben,fid_namen,bibliotheken,score,eindeutig\n")
        for z, e in [(z, 1) for z in eindeutig] + [(z, 0) for z in mehrdeutig]:
            fh.write('0x%08X,%s,%d,"%s","%s",%.1f,%d\n'
                     % (z[0], z[1], 1 if z[2] else 0, "|".join(z[3]), "|".join(z[4]), z[5], e))

    println("Schwelle %.1f, Funktionen im Programm %d" % (schwelle, currentProgram.getFunctionManager().getFunctionCount()))
    println("eindeutig erkannt : %d" % len(eindeutig))
    println("mehrdeutig        : %d" % len(mehrdeutig))
    println("Treffer je Bibliothek (eindeutig, eine Funktion zaehlt in jeder Variante):")
    for l in sorted(je_lib, key=lambda k: -je_lib[k])[:40]:
        println("   %-40s %d" % (l, je_lib[l]))
    println("Eindeutige Treffer an schon benannten Funktionen (Gegenprobe):")
    for z in eindeutig:
        if z[2]:
            println("   0x%08X  jetzt %-34s FID %s" % (z[0], z[1], z[3][0]))
    println("Eindeutige Treffer (Auszug, nach Adresse):")
    for z in sorted(eindeutig)[:400]:
        println("   0x%08X  %-36s %.1f  %s" % (z[0], z[3][0], z[5], z[4][0] + (" +%d" % (len(z[4]) - 1) if len(z[4]) > 1 else "")))
    println("CSV: %s" % CSV)

except:
    println("FEHLER:\n" + traceback.format_exc())
    raise
finally:
    try:
        q.close()
    except NameError:
        pass
