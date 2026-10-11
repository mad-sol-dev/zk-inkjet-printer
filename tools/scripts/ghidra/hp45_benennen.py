# Benennt die HP45-Treiberfunktionen aus der Druckhardware-Tabelle bei 0x120F28,
# belegt am Disassemblat am 2026-10-12 (CL-FIRMWARE-REC-107). Nur Standardnamen
# werden ersetzt; jede Funktion bekommt einen Plate-Kommentar mit dem Beleg.
#
# @category ZK-Inkjet
# @runtime Jython

from ghidra.program.model.listing import CodeUnit
from ghidra.program.model.symbol import SourceType

Q = " (CL-FIRMWARE-REC-107)"
TABELLE = [
    (0x000D874C, "hp45_gpio_init",
     "Tabelle 0x120F28 Eintrag 0. Schaltet ueber 0x89F34(Port, Bit, 5, 0) GPA0-7, GPA10-11, GPD5-8, GPC0-15, "
     "GPE0-1, GPB15 und GPD9-11 auf Ausgang; Ruhepegel: REG_GPIOA_DOUT=0xCFF, GPD5-8 high (Primitive inaktiv, "
     "also aktiv low), GPC=0, GPE0-1, GPB15, GPD9-11 low (Adressen inaktiv)."),
    (0x000D8AE8, "hp45_set_address",
     "Tabelle Eintrag 1. r0 Bits 0-15 -> GPC0-15 (ganzes REG_GPIOC_DOUT), 16-17 -> GPE0-1, 18 -> GPB15, "
     "19-21 -> GPD9-11: die 22 Adressleitungen, Bit fuer Bit wie CL-HP45-REC-007."),
    (0x000D8B44, "hp45_set_primitives",
     "Tabelle Eintrag 2. r0 Bits 0-7 -> GPA0-7, 8-9 -> GPA10-11, 10-13 -> GPD5-8: die 14 Primitivleitungen."),
    (0x0009EEC0, "delay_us",
     "Tabelle Eintrag 4. Timer-Vergleichswert n*24 (n<<4 + n<<3) an +0x30, starten, aktiv warten -- "
     "Pause in Mikrosekunden bei 24 MHz."),
]

fm = currentProgram.getFunctionManager()
lst = currentProgram.getListing()
for va, name, beleg in TABELLE:
    f = fm.getFunctionAt(toAddr(va))
    if f is None:
        println("0x%08X keine Funktion" % va)
        continue
    if f.getName() != name and f.getSymbol().getSource() == SourceType.DEFAULT:
        println("   0x%08X  %-14s -> %s" % (va, f.getName(), name))
        f.setName(name, SourceType.USER_DEFINED)
    lst.setComment(toAddr(va), CodeUnit.PLATE_COMMENT, name + ": " + beleg + Q)
println("OK")
