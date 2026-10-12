# Legt die Interrupt-Handler aus CL-FIRMWARE-REC-118 als Funktionen an und
# benennt sie. Vier der Einspruenge haben einen Vorspann VOR dem push (ldr, bei
# TMR1 dazu tst/bxeq); die Auto-Analyse hat die Funktion deshalb erst beim push
# angelegt (Einsprung + 4 bzw. + 16). Diese zu spaet beginnende Funktion -- die
# erste im Abstand 4..28 Bytes -- wird entfernt und am echten Einsprung neu
# angelegt, aber nur, wenn
#   - am Einsprung das erwartete erste Befehlswort steht und
#   - auf die alte Funktion kein Aufruf und kein Sprung zeigt (nur der
#     Durchlauf vom Einsprung).
# Sonst Meldung, keine Aenderung an dieser Stelle.
# Namen nennen den Pin, nicht die Bedeutung: welche Leitung Encoder und welche
# Lichtschranke ist, ist offen (CL-HARDWARE-REC-113); die Lesart der Firmware
# steht im Plate-Kommentar. Idempotent.
#
# @category ZK-Inkjet
# @runtime Jython

from ghidra.program.model.listing import CodeUnit
from ghidra.program.model.symbol import SourceType
from ghidra.app.cmd.disassemble import ArmDisassembleCommand
from ghidra.app.cmd.function import CreateFunctionCmd

Q = "CL-FIRMWARE-REC-118"
ZIELE = [
    # Einsprung, erstes Wort, Name, Kommentar
    (0x0010B754, 0xE59F1010, "isr_tmr0_druckspalte",
     "IRQ 14 TMR0, Level 1: quittiert TISR, ruft FUN_000d8cbc (Spaltenschritt). Ein/aus ueber FUN_0010b694 (%s)" % Q),
    (0x000FBAAC, 0xE59F004C, "isr_tmr1_systick",
     "IRQ 15 TMR1, Level 2: TISR Bit 1, Tick64 bei 0xC18++, Countdown [0x7DC+4] -> PWM POE Bit 1 aus (%s)" % Q),
    (0x0008247C, 0xE59F0014, "isr_extint0_gpe11",
     "IRQ 2 EXTINT0, Level 4, GPE11 beide Flanken: quittiert IRQTGSRC2 Bit 11, ruft gpe11_flanke. Firmware nennt den Zaehler 'Encoder' (%s, CL-HARDWARE-REC-113)" % Q),
    (0x0008249C, 0xE59F0014, "isr_extint1_gpe10",
     "IRQ 3 EXTINT1, Level 5, GPE10 eine Flanke: quittiert IRQTGSRC2 Bit 10, ruft gpe10_flanke. Firmware nennt den Zaehler 'External' = externe Lichtschranke (%s, CL-HARDWARE-REC-113)" % Q),
    (0x000B623C, 0xE59F0028, "gpe11_flanke",
     "Jede fuenfte Flanke [0x5B8+0x20]++ (Teiler in [0x5B8+0x34]); gibt im Nicht-Timer-Modus die Druckspalten frei (%s)" % Q),
    (0x000B65C8, 0xE59F000C, "gpe10_flanke",
     "[0x5B8+0x24]++ je Flanke; Startsignal 'Licht' in print_job_run wartet darauf, wenn [0xD00+0x128] gesetzt (%s)" % Q),
    (0x000FBA8C, 0xE59F1014, "systick64_inkrement",
     "64-Bit-Tick bei 0xC18 um 1 erhoehen (ldrd/adds/adc/strd), gerufen aus isr_tmr1_systick (%s)" % Q),
    (0x0010B694, None, "druck_timer0_schalten",
     "FUN_0010b694(an, frequenz): an -> TICR = 12000000/frequenz, TCSR0 periodisch, sysInstallISR(1, 14, isr_tmr0_druckspalte); aus -> TCSR0 = 0 (%s)" % Q),
]

mem = currentProgram.getMemory()
fm = currentProgram.getFunctionManager()
lst = currentProgram.getListing()
rm = currentProgram.getReferenceManager()


n = {"neu": 0, "verschoben": 0, "benannt": 0, "schon": 0}
meld = []

for va, wort, name, text in ZIELE:
    a = toAddr(va)
    if wort is not None and (mem.getInt(a) & 0xFFFFFFFF) != wort:
        meld.append("0x%X: erstes Wort 0x%08X statt 0x%08X, uebersprungen" % (va, mem.getInt(a) & 0xFFFFFFFF, wort))
        continue
    f = fm.getFunctionAt(a)
    if f is None:
        spaet = None
        for k in range(4, 32, 4):
            spaet = fm.getFunctionAt(a.add(k))
            if spaet is not None:
                break
        drin = fm.getFunctionContaining(a)
        if drin is not None:
            meld.append("0x%X liegt in %s, uebersprungen" % (va, drin.getName()))
            continue
        if spaet is not None:
            sa = spaet.getEntryPoint()
            fremd = [r for r in rm.getReferencesTo(sa)
                     if r.getReferenceType().isFlow()
                     and not (a.compareTo(r.getFromAddress()) <= 0 and r.getFromAddress().compareTo(sa) < 0)]
            if fremd:
                meld.append("0x%X: %s hat eigene Verweise (%s), nicht verschoben"
                            % (va, spaet.getName(), fremd[0].getFromAddress()))
                continue
            println("   0x%X  %s entfernt (begann %d Bytes zu spaet)"
                    % (va, spaet.getName(), sa.subtract(a)))
            fm.removeFunction(sa)
            n["verschoben"] += 1
        if lst.getInstructionAt(a) is None:
            lst.clearCodeUnits(a, a.add(3), False)
            ArmDisassembleCommand(a, None, False).applyTo(currentProgram, monitor)
        CreateFunctionCmd(a).applyTo(currentProgram, monitor)
        f = fm.getFunctionAt(a)
        if f is None:
            meld.append("0x%X nicht anlegbar" % va)
            continue
        n["neu"] += 1
        println("   0x%X  Funktion angelegt, %d Bytes" % (va, f.getBody().getNumAddresses()))
    if f.getName() == name:
        n["schon"] += 1
    elif f.getName().startswith("FUN_"):
        println("   0x%X  %s -> %s" % (va, f.getName(), name))
        f.setName(name, SourceType.ANALYSIS)
        n["benannt"] += 1
    else:
        meld.append("0x%X: vergebener Name %s bleibt" % (va, f.getName()))
    if lst.getComment(CodeUnit.PLATE_COMMENT, a) != text:
        lst.setComment(a, CodeUnit.PLATE_COMMENT, text)

println("neu %(neu)d, verschoben %(verschoben)d, benannt %(benannt)d, schon richtig %(schon)d" % n)
for m in meld:
    println("   Meldung: " + m)
