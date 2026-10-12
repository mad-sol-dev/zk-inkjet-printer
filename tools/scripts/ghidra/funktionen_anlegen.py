# Legt an gemessenen ARM-Prologen Funktionen an, die die Auto-Analyse nicht
# selbst gefunden hat. Jede Adresse wird nur angefasst, wenn dort das erwartete
# Prologwort steht; sonst Abbruch ohne Aenderung. Idempotent.
#
# Herkunft der Adressen: CL-USB-REC-102 (USB-ISR) und CL-BOOT-REC-112/113
# (Callbacks), beide nach dem Rebase auf 0x58000 (CL-TOOL-REC-121).
#
# @category ZK-Inkjet
# @runtime Jython

from ghidra.app.cmd.disassemble import ArmDisassembleCommand
from ghidra.app.cmd.function import CreateFunctionCmd

ZIELE = [
    # Adresse,   Prologwort, Bedeutung
    (0x00109AC4, 0xE52DE004, "str lr,[sp,#-4]!  -- USB-ISR (CL-USB-REC-102)"),
    (0x000D9934, 0xE92D4FFF, "push {r0-r11,lr}  -- Callback (CL-BOOT-REC-112)"),
    (0x000A9184, 0xE92D4FF0, "push {r4-r11,lr}  -- SD-Konstruktor, Logik wie fmiInitSDDevice (CL-USB-REC-119)"),
    # Blattfunktionen ohne push: geprueft wird das erste Befehlswort.
    (0x000D8AE8, 0xE59F1050, "ldr r1,[pc,#0x50]  -- Druckhardware-Tabelle 0x120F28 Eintrag 1, Port C/E/B/D (CL-FIRMWARE-REC-107)"),
    (0x000D8B44, 0xE3A03B03, "mov r3,#0xC00      -- Druckhardware-Tabelle Eintrag 2, Port A/D (CL-FIRMWARE-REC-107)"),
    (0x0009EEC0, 0xE52D0004, "str r0,[sp,#-4]!   -- Druckhardware-Tabelle Eintrag 4 (CL-FIRMWARE-REC-107)"),
]

mem = currentProgram.getMemory()
fm = currentProgram.getFunctionManager()
lst = currentProgram.getListing()

# Aufruf mit Argumenten: <kandidatendatei> <stufe1|stufe2>. Dann kommen die Ziele
# aus einer Liste im Format von funktionen_kandidaten_*.txt (CL-TOOL-REC-126),
# gefiltert wie in kandidaten_pruefen.py:
#   stufe1  BL- oder Poolwort-Verweis, oder schon disassemblierter Prolog ohne Verweis
#   stufe2  Datenwort-Verweis (einzeln oder in dichter Folge), schon disassembliert
# Nie disassemblierte Kandidaten mit nur Datenwort- oder gar keinem Verweis
# bleiben ausgeschlossen.
import re
args = getScriptArgs()
if len(args) >= 2:
    ZEILE = re.compile(r'\(\s*(0x[0-9A-Fa-f]+)\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*"([^"]*)"\s*\)')

    def art(h):
        if h.startswith("BL von") or "; BL von" in h:
            return "BL"
        if h.startswith("Poolwort"):
            return "Pool"
        if h.startswith("Datenwort"):
            return "Daten"
        return "ohne"

    ZIELE = []
    for z in open(args[0]):
        m = ZEILE.search(z)
        if not m:
            continue
        va, w, h = int(m.group(1), 16), int(m.group(2), 16), m.group(3)
        code = lst.getInstructionAt(toAddr(va)) is not None
        a = art(h)
        if args[1] == "stufe1":
            nehmen = a in ("BL", "Pool") or (a == "ohne" and code)
        elif args[1] == "stufe2":
            nehmen = a == "Daten" and code
        else:
            raise Exception("Stufe %s unbekannt, erlaubt: stufe1, stufe2" % args[1])
        if nehmen:
            ZIELE.append((va, w, "%s %s | %s" % (a, "CODE" if code else "ROH", h)))
    println("%s: %d Ziele aus %s" % (args[1], len(ZIELE), args[0]))


def anzahl_befehle():
    n = 0
    it = lst.getInstructions(True)
    while it.hasNext():
        it.next()
        n += 1
    return n


fn_vorher = fm.getFunctionCount()
bf_vorher = anzahl_befehle()

for va, prolog, was in ZIELE:
    w = mem.getInt(toAddr(va)) & 0xFFFFFFFF
    if w != prolog:
        raise Exception("0x%08X: Wort 0x%08X statt 0x%08X. Abbruch." % (va, w, prolog))

fehler = 0
groessen = []
neu_angelegt = set()
mehrteilig = []
kurz = len(args) >= 3 and args[2] == "kurz"
verschluckt = []   # (Kandidat, Einstiegsadresse der Funktion, die ihn enthaelt)
for va, prolog, was in ZIELE:
    a = toAddr(va)
    f = fm.getFunctionAt(a)
    if f is not None:
        println("0x%08X: Funktion %s existiert schon -- nichts zu tun" % (va, f.getName()))
        continue
    if fm.getFunctionContaining(a) is not None:
        # Kann entstehen, wenn ein vorher angelegtes Ziel dieses Laufs den
        # Koerper bis hierher ausgedehnt hat. Nicht anlegen, sondern melden.
        g = fm.getFunctionContaining(a)
        println("0x%08X: liegt jetzt in %s @ %s -- uebersprungen" % (va, g.getName(), g.getEntryPoint()))
        verschluckt.append((va, g.getEntryPoint().getOffset()))
        continue
    if lst.getInstructionAt(a) is None:
        cmd = ArmDisassembleCommand(a, None, False)   # False = ARM, nicht Thumb
        cmd.applyTo(currentProgram, monitor)
    ok = CreateFunctionCmd(a).applyTo(currentProgram, monitor)
    f = fm.getFunctionAt(a)
    if f is None:
        fehler += 1
        println("0x%08X: FEHLER, keine Funktion angelegt (%s)" % (va, was))
        continue
    body = f.getBody()
    neu_angelegt.add(va)
    groessen.append((body.getNumAddresses(), va))
    stuecke = body.getNumAddressRanges()
    if stuecke > 1:
        mehrteilig.append(va)
    if not kurz or stuecke > 1:
        println("0x%08X: %s angelegt, %d Bytes in %d Stueck(en), %s .. %s  | %s"
                % (va, f.getName(), body.getNumAddresses(), stuecke, body.getMinAddress(),
                   body.getMaxAddress(), was))

# Nachlauf: Ein Kandidat, den eine in DIESEM Lauf angelegte Funktion ueber einen
# Endsprung (b ohne Rueckkehr) in ihren Koerper gezogen hat, ist selbst ein
# Funktionsanfang. Die schluckende Funktion wird entfernt, der Kandidat zuerst
# angelegt, dann die Funktion neu -- ihr Koerper endet jetzt am Kandidaten.
# Funktionen, die schon vor dem Lauf bestanden, werden nie angefasst.
for va, gross in verschluckt:
    if gross not in neu_angelegt:
        println("0x%08X: steckt in einer vorbestehenden Funktion @ 0x%08X -- nicht angefasst" % (va, gross))
        continue
    fm.removeFunction(toAddr(gross))
    CreateFunctionCmd(toAddr(va)).applyTo(currentProgram, monitor)
    CreateFunctionCmd(toAddr(gross)).applyTo(currentProgram, monitor)
    f1, f2 = fm.getFunctionAt(toAddr(va)), fm.getFunctionAt(toAddr(gross))
    if f1 is None or f2 is None:
        fehler += 1
        println("0x%08X / 0x%08X: FEHLER im Nachlauf" % (va, gross))
        continue
    groessen.append((f1.getBody().getNumAddresses(), va))
    println("0x%08X: im Nachlauf angelegt, %d Bytes, %s .. %s; 0x%08X jetzt %d Bytes, %s .. %s"
            % (va, f1.getBody().getNumAddresses(), f1.getBody().getMinAddress(),
               f1.getBody().getMaxAddress(), gross, f2.getBody().getNumAddresses(),
               f2.getBody().getMinAddress(), f2.getBody().getMaxAddress()))

println("Koerper aus mehreren Stuecken: %d %s" % (len(mehrteilig), ", ".join("0x%08X" % v for v in mehrteilig)))
fn_nachher = fm.getFunctionCount()
bf_nachher = anzahl_befehle()
println("Funktionen: %d -> %d (+%d)" % (fn_vorher, fn_nachher, fn_nachher - fn_vorher))
println("Befehle:    %d -> %d (+%d)" % (bf_vorher, bf_nachher, bf_nachher - bf_vorher))
if groessen:
    groessen.sort()
    println("Koerpergroessen: min %d, Median %d, max %d Bytes"
            % (groessen[0][0], groessen[len(groessen) // 2][0], groessen[-1][0]))
    println("Groesste: " + ", ".join("0x%08X=%d" % (v, g) for g, v in groessen[-5:]))
println("FEHLER: %d" % fehler if fehler else "OK")
