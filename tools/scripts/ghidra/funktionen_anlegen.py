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
]

mem = currentProgram.getMemory()
fm = currentProgram.getFunctionManager()
lst = currentProgram.getListing()

for va, prolog, was in ZIELE:
    w = mem.getInt(toAddr(va)) & 0xFFFFFFFF
    if w != prolog:
        raise Exception("0x%08X: Wort 0x%08X statt 0x%08X. Abbruch." % (va, w, prolog))

fehler = 0
for va, prolog, was in ZIELE:
    a = toAddr(va)
    f = fm.getFunctionAt(a)
    if f is not None:
        println("0x%08X: Funktion %s existiert schon -- nichts zu tun" % (va, f.getName()))
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
    println("0x%08X: %s angelegt, %d Bytes, %s .. %s  | %s"
            % (va, f.getName(), body.getNumAddresses(), body.getMinAddress(),
               body.getMaxAddress(), was))

println("FEHLER: %d" % fehler if fehler else "OK")
