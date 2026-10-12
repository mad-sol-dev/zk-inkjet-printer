# Uebernimmt BSP-Namen, die durch Abgleich mit dem Quelltext zugeordnet sind
# (Oracle O1, nicht bytebelegt -- dafuer fid_benennen.py). Argument: CSV in
# tools/scripts/ghidra/zuordnung/ (versioniert, von Hand gepflegt) mit Spalten
# art,va,name,quelle; art = func | data | struct | zeiger.
# Optional als zweites Argument die Claim-ID fuer den Kommentar.
#
# - func: nur Standardnamen (FUN_...) werden umbenannt, Quelle ANALYSIS; vergebene
#   Namen bleiben, der BSP-Name steht dann nur im Plate-Kommentar. Fehlt an der
#   Adresse eine Funktion, wird sie als ARM angelegt -- nur wenn die Adresse in
#   keiner anderen Funktion und in keinen Daten mit echtem Typ liegt.
# - data: Label setzen (primaer), vorhandene Labels bleiben erhalten.
# - struct: usbdInfo = USBD_INFO_T aus UDC/lib/usbd.h, gepackt, BOOL = 1 Byte
#   (an den Offsets 0x68..0x10E gemessen, CL-USB-REC-102/-126). Ersetzt nur
#   undefinedN-Platzhalter; steht dort ein echter Typ oder Code, nur Meldung.
# - zeiger: jedes 32-Bit-Wort im Block flash mit dem Wert va, auf das ein Befehl
#   verweist (Literalpool), wird als Zeiger auf den Typ der Struktur an va
#   typisiert -- dann zeigt der Dekompiler Feldnamen. Worte ohne Befehlsverweis
#   bleiben unberuehrt und werden gemeldet. Die Zeile muss nach der struct-Zeile
#   derselben Adresse stehen.
# Idempotent: ein zweiter Lauf aendert nichts.
#
# @category ZK-Inkjet
# @runtime Jython

import csv
import os
from ghidra.program.model.listing import CodeUnit
from ghidra.program.model.symbol import SourceType
from ghidra.app.cmd.disassemble import ArmDisassembleCommand
from ghidra.app.cmd.function import CreateFunctionCmd
from ghidra.program.model.data import (PointerDataType as PDT,StructureDataType, CategoryPath, ByteDataType,
                                       WordDataType, DWordDataType, PointerDataType,
                                       ArrayDataType, DataTypeConflictHandler)

repo = os.path.normpath(os.path.join(getSourceFile().getParentFile().getAbsolutePath(),
                                     "..", "..", ".."))
args = getScriptArgs()
if not args:
    raise Exception("Argument: CSV-Name in tools/scripts/ghidra/zuordnung/")
CSV = os.path.join(repo, "tools", "scripts", "ghidra", "zuordnung", args[0])
CLAIM = args[1] if len(args) > 1 else "CL-USB-REC-102"

fm = currentProgram.getFunctionManager()
lst = currentProgram.getListing()
st = currentProgram.getSymbolTable()
dtm = currentProgram.getDataTypeManager()
n = {"angelegt": 0, "umbenannt": 0, "schon": 0, "behalten": 0, "label": 0, "struct": 0, "zeiger": 0}
meld = []

B, W, D, P = ByteDataType.dataType, WordDataType.dataType, DWordDataType.dataType, PointerDataType.dataType
USBD_INFO_T = (
    [("pu32DevDescriptor", P), ("pu32QulDescriptor", P), ("pu32HSConfDescriptor", P),
     ("pu32FSConfDescriptor", P), ("pu32HOSConfDescriptor", P), ("pu32FOSConfDescriptor", P),
     ("pu32HIDDescriptor", P), ("pu32HIDRPTDescriptor", P),
     ("pu32StringDescriptor", ArrayDataType(P, 5, 4))] +
    [(x, D) for x in ("u32DevDescriptorLen", "u32QulDescriptorLen", "u32HSConfDescriptorLen",
                      "u32FSConfDescriptorLen", "u32HOSConfDescriptorLen", "u32FOSConfDescriptorLen",
                      "u32HIDDescriptorLen", "u32HIDRPTDescriptorLen")] +
    [("u32StringDescriptorLen", ArrayDataType(D, 5, 4))] +
    [(x, P) for x in ("pfnHighSpeedInit", "pfnFullSpeedInit")] +
    [(x, D) for x in ("i32EPA_Num", "i32EPB_Num", "i32EPC_Num", "i32EPD_Num")] +
    [(x, P) for x in ("pfnEPACallBack", "pfnEPBCallBack", "pfnEPCCallBack", "pfnEPDCallBack",
                      "pfnClassDataINCallBack", "pfnClassDataOUTCallBack", "pfnDMACompletion",
                      "pfnReset", "pfnSOF", "pfnPlug", "pfnUnplug")] +
    [("_usbd_remlen", D), ("_usbd_remlen_flag", B), ("_usbd_ptr", P)] +
    [(x, B) for x in ("GET_DEV_Flag", "GET_CFG_Flag", "GET_QUL_Flag", "GET_OSCFG_Flag",
                      "GET_STR_Flag", "GET_VEN_Flag", "GET_VENO_Flag", "GET_HID_Flag",
                      "GET_HID_RPT_Flag", "CLASS_CMD_Flag", "CLASS_CMD_Iflag", "CLASS_CMD_Oflag")] +
    [("usbdMaxPacketSize", D)] +
    [(x, B) for x in ("_usbd_DMA_Flag", "_usbd_DMA_In", "_usbd_resume", "USBModeFlag")] +
    [(x, D) for x in ("_usbd_devstate", "_usbd_address", "_usbd_speedset")] +
    [(x, W) for x in ("_usbd_confsel", "_usbd_intfsel", "_usbd_altsel")] +
    [(x, D) for x in ("_usbd_feature", "_usbd_haltep", "_usbd_unhaltep", "remotewakeup",
                      "testmode", "enableremotewakeup", "enabletestmode", "disableremotewakeup",
                      "disabletestmode", "testselector", "usbdGetStatusData")] +
    [(x, B) for x in ("usbdGetConfig", "usbdGetInterface", "usbdGetStatus")] +
    [(x, D) for x in ("AlternateFlag", "u32VbusStatus", "AlternateFlag_Audio", "u32UVC",
                      "USBStartFlag")])
# Messpunkte aus CL-USB-REC-102/-126: Feld -> erwarteter Offset
PRUEF = {"pfnHighSpeedInit": 0x68, "pfnEPACallBack": 0x80, "pfnUnplug": 0xA8,
         "_usbd_remlen_flag": 0xB0, "GET_DEV_Flag": 0xB5, "CLASS_CMD_Iflag": 0xBF,
         "_usbd_DMA_Flag": 0xC5, "USBModeFlag": 0xC8, "_usbd_devstate": 0xC9,
         "_usbd_speedset": 0xD1, "_usbd_haltep": 0xDF, "AlternateFlag": 0x10A,
         "u32VbusStatus": 0x10E}


def baue_struct():
    s = StructureDataType(CategoryPath("/ZK-Inkjet"), "USBD_INFO_T", 0)
    s.setPackingEnabled(False)
    for name, dt in USBD_INFO_T:
        s.add(dt, dt.getLength(), name, None)
    for c in s.getComponents():
        if c.getFieldName() in PRUEF and c.getOffset() != PRUEF[c.getFieldName()]:
            raise Exception("USBD_INFO_T: %s bei 0x%X, gemessen 0x%X"
                            % (c.getFieldName(), c.getOffset(), PRUEF[c.getFieldName()]))
    return dtm.addDataType(s, DataTypeConflictHandler.REPLACE_HANDLER)


def echt_belegt(a, laenge):
    # Zaehlt Befehle und definierte Daten mit echtem Typ im Bereich;
    # undefinedN-Platzhalter der Analyse zaehlen nicht.
    rng = currentProgram.getAddressFactory().getAddressSet(a, a.add(laenge - 1))
    k = 0
    it = lst.getDefinedData(rng, True)
    while it.hasNext():
        if not it.next().getDataType().getName().startswith("undefined"):
            k += 1
    if lst.getInstructions(rng, True).hasNext():
        k += 1
    return k


def setze_label(a, name):
    for s in st.getSymbols(a):
        if s.getName() == name:
            if not s.isPrimary():
                s.setPrimary()
            return False
    st.createLabel(a, name, SourceType.ANALYSIS).setPrimary()
    return True


for z in csv.DictReader(open(CSV)):
    a = toAddr(int(z["va"], 16))
    plate = "BSP n32901: %s aus %s, Zuordnung durch Quelltextabgleich (O1, %s)" % (
        z["name"], z["quelle"], CLAIM)
    if z["art"] == "func":
        f = fm.getFunctionAt(a)
        if f is None:
            drin = fm.getFunctionContaining(a)
            if drin is not None:
                meld.append("%s liegt in %s, nicht angelegt" % (z["va"], drin.getName()))
                continue
            if echt_belegt(a, 4) and lst.getInstructionAt(a) is None:
                meld.append("%s mit Daten belegt, nicht angelegt" % z["va"])
                continue
            if lst.getInstructionAt(a) is None:
                lst.clearCodeUnits(a, a.add(3), False)
                ArmDisassembleCommand(a, None, False).applyTo(currentProgram, monitor)
            CreateFunctionCmd(a).applyTo(currentProgram, monitor)
            f = fm.getFunctionAt(a)
            if f is None:
                meld.append("%s nicht anlegbar" % z["va"])
                continue
            n["angelegt"] += 1
            println("   %s  Funktion angelegt, %d Bytes" % (z["va"], f.getBody().getNumAddresses()))
        if f.getName() == z["name"]:
            n["schon"] += 1
        elif f.getSymbol().getSource() == SourceType.DEFAULT:
            println("   %s  %-14s -> %s" % (z["va"], f.getName(), z["name"]))
            f.setName(z["name"], SourceType.ANALYSIS)
            n["umbenannt"] += 1
        else:
            n["behalten"] += 1
            println("   %s  vergeben %-28s bleibt, BSP sagt %s" % (z["va"], f.getName(), z["name"]))
    elif z["art"] == "zeiger":
        d0 = lst.getDataAt(a)
        if d0 is None or d0.getDataType().getName().startswith("undefined"):
            meld.append("%s: keine Struktur an der Adresse, zeiger uebersprungen" % z["va"])
            continue
        zt = PDT(d0.getDataType(), 4)
        mem = currentProgram.getMemory()
        blk = mem.getBlock("flash")
        wert = int(z["va"], 16)
        x = blk.getStart()
        rm = currentProgram.getReferenceManager()
        while x.compareTo(blk.getEnd()) < 0:
            if mem.getInt(x) == wert:
                von = [r.getFromAddress() for r in rm.getReferencesTo(x)
                       if lst.getInstructionAt(r.getFromAddress()) is not None]
                d = lst.getDataAt(x)
                if not von:
                    meld.append("%s: Wort 0x%X ohne Befehlsverweis, bleibt" % (x, wert))
                elif d is not None and d.getDataType().getName() == zt.getName():
                    pass
                elif echt_belegt(x, 4) == 0 or (d is not None and d.getDataType().getName()
                                                 in ("int", "uint", "dword", "pointer")):
                    lst.clearCodeUnits(x, x.add(3), False)
                    lst.createData(x, zt)
                    n["zeiger"] += 1
                    println("   %s  -> %s (Verweis von %s)" % (x, zt.getName(), von[0]))
                else:
                    meld.append("%s: belegt mit %s, bleibt" % (x, d.getDataType().getName()
                                                              if d else "Code"))
            x = x.add(4)
        continue
    else:
        if setze_label(a, z["name"]):
            n["label"] += 1
            println("   %s  Label %s" % (z["va"], z["name"]))
        if z["art"] == "struct":
            dt = baue_struct()
            d = lst.getDataAt(a)
            if d is not None and d.getDataType().getName() == dt.getName():
                pass
            elif echt_belegt(a, dt.getLength()) == 0:
                lst.clearCodeUnits(a, a.add(dt.getLength() - 1), False)
                lst.createData(a, dt)
                n["struct"] += 1
                println("   %s  %s angelegt, %d Bytes" % (z["va"], dt.getName(), dt.getLength()))
            else:
                vor = []
                it = lst.getDefinedData(currentProgram.getAddressFactory().getAddressSet(
                    a, a.add(dt.getLength() - 1)), True)
                while it.hasNext():
                    x = it.next()
                    if not x.getDataType().getName().startswith("undefined"):
                        vor.append("%s %s" % (x.getAddress(), x.getDataType().getName()))
                meld.append("%s schon definierte Daten, Struktur nicht angelegt: %s"
                            % (z["va"], ", ".join(vor[:12])))
    if lst.getComment(CodeUnit.PLATE_COMMENT, a) != plate:
        lst.setComment(a, CodeUnit.PLATE_COMMENT, plate)

println("angelegt %(angelegt)d, umbenannt %(umbenannt)d, schon richtig %(schon)d, vergebene behalten %(behalten)d, "
        "Labels %(label)d, Strukturen %(struct)d, Zeiger %(zeiger)d" % n)
for x in meld:
    println("   Meldung: %s" % x)
