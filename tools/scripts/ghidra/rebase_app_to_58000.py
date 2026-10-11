# Setzt die Speicherkarte von ZK-INKJET-NANO-APP.bin.orig auf die belegte Linkbasis
# und legt die drei Startregionen an, die die Scatter-Tabelle beschreibt.
#
# Belegt in CL-BOOT-REC-113: APP.bin ist nach 0x00058000 gelinkt. Die Datenbank
# stand auf 0x00200000, also war jede Adresse um 0x1A8000 zu hoch und jeder
# absolute Zeiger im Bild zeigte ins Leere.
#
# Ausfuehren in Ghidra: Script Manager -> dieses Skript. Laeuft in einer
# Transaktion, ist also mit Undo zurueckzunehmen, solange das Programm offen ist.
# Vorher trotzdem ein Projektarchiv anlegen.
#
# @category ZK-Inkjet
# @runtime Jython

from ghidra.program.model.address import AddressSet
from ghidra.program.model.listing import CodeUnit
from ghidra.program.model.symbol import SourceType
import re
from jarray import array

BASE_ALT   = 0x00200000
BASE_NEU   = 0x00058000
DATEIGROESSE = 0x27522C

# Scatter-Tabelle, gelesen bei Dateioffset 0x27487C (VA 0x2CC87C):
#   src           dst        size       fn
#   0x002CCB84    0x00000000 0x00000060 0x000580F8  copy
#   0x002CCBE4    0x00000060 0x00000C84 0x0005809C  decompress
#   0x002CD22C    0x00000CE4 0x000442DC 0x00058120  zeroinit
REGIONEN = [
    ("vectors", 0x00000000, 0x00000060, 0x002CCB84, "copy"),
    ("rw",      0x00000060, 0x00000C84, 0x002CCBE4, "decompress"),
    ("zi",      0x00000CE4, 0x000442DC, None,       "zero"),
]

mem = currentProgram.getMemory()


def hexs(v):
    return "0x%08X" % (v & 0xFFFFFFFF)


def entpacken(roh, groesse):
    """__scatterload_decompress, Thumb bei Dateioffset 0xA4 (VA 0x000580A4).

    token = *src++ ; lit = token & 7 (0 -> naechstes Byte)
                     run = token >> 4 (0 -> naechstes Byte)
    lit-1 Literalbytes; Bit 3 gesetzt -> Rueckwaertsreferenz dist = *src++,
    run+2 Bytes ab dst-dist; sonst run Nullbytes. Ende, wenn dst voll ist.
    """
    aus = []
    i = 0
    while len(aus) < groesse:
        tok = roh[i]; i += 1
        lit = tok & 7
        if lit == 0:
            lit = roh[i]; i += 1
        run = tok >> 4
        if run == 0:
            run = roh[i]; i += 1
        lit -= 1
        if lit:
            aus.extend(roh[i:i + lit]); i += lit
        if not (tok & 8):
            aus.extend([0] * run)
        else:
            dist = roh[i]; i += 1
            p = len(aus) - dist
            for _ in range(run + 2):
                aus.append(aus[p]); p += 1
    return aus, i


def lies(va, n):
    """n Bytes ab VA aus dem Programm, als Liste vorzeichenloser Werte."""
    puffer = array([0] * n, 'b')
    mem.getBytes(toAddr(va), puffer)
    return [b & 0xFF for b in puffer]


def schreibe(block_start, werte):
    mem.setBytes(toAddr(block_start),
                 array([(v - 256 if v > 127 else v) for v in werte], 'b'))


# Bestandsaufnahme, wie in inventory.py. Vor und nach dem Verschieben erhoben,
# damit belegt ist, dass Namen, Funktionen und Kommentare den Umzug ueberstehen.
# Adressen im alten Flash-Bereich werden auf ihre neue Lage umgerechnet, alles
# andere (MMIO-Labels usw.) muss an derselben Adresse bleiben.
KOMMENTARTYPEN = [(CodeUnit.EOL_COMMENT, "EOL"), (CodeUnit.PRE_COMMENT, "PRE"),
                  (CodeUnit.POST_COMMENT, "POST"), (CodeUnit.PLATE_COMMENT, "PLATE"),
                  (CodeUnit.REPEATABLE_COMMENT, "REPEAT")]


STANDARDADRESSE = re.compile(r"_([0-9a-fA-F]{8})\b")


def neu(off):
    if BASE_ALT <= off < BASE_ALT + DATEIGROESSE:
        return off - BASE_ALT + BASE_NEU
    return off


def bestand(umrechnen):
    fm = currentProgram.getFunctionManager()
    lst = currentProgram.getListing()
    st = currentProgram.getSymbolTable()
    abb = neu if umrechnen else (lambda o: o)
    b = {"fn_alle": 0, "fn_namen": {}, "fn_standard": {}, "symbole": 0, "daten": 0,
         "kommentare": {}}
    for f in fm.getFunctions(True):
        b["fn_alle"] += 1
        ep = abb(f.getEntryPoint().getOffset())
        if f.getSymbol().getSource() == SourceType.DEFAULT:
            # Standardnamen (FUN_, thunk_FUN_ ...) tragen die Adresse im Namen
            # und benennen sich beim Umzug selbst um. Verglichen wird daher der
            # Name mit umgerechneter Adresse.
            b["fn_standard"][ep] = STANDARDADRESSE.sub(
                lambda m: "_%08x" % abb(int(m.group(1), 16)), f.getName())
        else:
            b["fn_namen"][ep] = f.getName()
    for s in st.getAllSymbols(False):
        b["symbole"] += 1
    for d in lst.getDefinedData(True):
        b["daten"] += 1
    for typ, name in KOMMENTARTYPEN:
        it = lst.getCommentAddressIterator(typ, currentProgram.getMemory(), True)
        while it.hasNext():
            a = it.next()
            b["kommentare"][(abb(a.getOffset()), name)] = lst.getComment(typ, a)
    return b


def vergleiche(vor, nach):
    """Gibt die Zahl der Abweichungen zurueck und druckt sie."""
    abw = 0
    for schluessel, text in (("fn_alle", "Funktionen gesamt"), ("symbole", "Symbole gesamt"),
                             ("daten", "Datenobjekte")):
        ok = vor[schluessel] == nach[schluessel]
        abw += 0 if ok else 1
        println("   %-18s %6d -> %6d   %s" % (text, vor[schluessel], nach[schluessel],
                                             "OK" if ok else "FEHLER"))
    for titel, a, b in (("vergebene Namen", vor["fn_namen"], nach["fn_namen"]),
                        ("Standardnamen", vor["fn_standard"], nach["fn_standard"]),
                        ("Kommentare", vor["kommentare"], nach["kommentare"])):
        fehlt = [k for k in a if k not in b]
        anders = [k for k in a if k in b and a[k] != b[k]]
        neu_da = [k for k in b if k not in a]
        ok = not (fehlt or anders or neu_da)
        abw += 0 if ok else 1
        println("   %-18s %6d -> %6d   %s  (fehlt %d, geaendert %d, neu %d)"
                % (titel, len(a), len(b), "OK" if ok else "FEHLER",
                   len(fehlt), len(anders), len(neu_da)))
        for k in (fehlt + anders + neu_da)[:10]:
            println("      %r: %r -> %r" % (k, str(a.get(k))[:50], str(b.get(k))[:50]))
    return abw


# Zahlen im alten Flash-Bereich, die in Kommentartexten stehen, wandern beim
# Verschieben nicht mit. Sie werden umgerechnet; Schreibweise (Breite, Gross-/
# Kleinschreibung) bleibt erhalten. AUSNAHMEN sind Werte, die keine Adresse
# sind, sondern die alte Basis selbst nennen.
KOMMENTARZAHL = re.compile(r"0x([0-9A-Fa-f]{6,8})")
AUSNAHMEN = set([BASE_ALT])

# Zahlen, die an dieser Stelle einen gesuchten WERT nennen, keinen Ort. Sie
# umzurechnen hiesse, ein nie gemessenes Suchergebnis zu behaupten. Schluessel
# ist die alte Kommentaradresse.
AUSNAHMEN_STELLE = set([
    (0x00265B08, 0x00265B08),   # "aligned words holding 0x00265B08"
    (0x0025C3A0, 0x0028249C),   # Argument "unter der Ladebasis 0x200000"
])
NACHTRAG = {
    0x0025C3A0: "[2026-10-11, Rebase auf 0x58000] Die Argumentation oben stand auf "
                "der falschen Basis 0x200000. Mit der Linkbasis 0x58000 "
                "(CL-BOOT-REC-113) liegen 0x0008249C und 0x0008247C im Image, "
                "Dateioffset 0x2A49C/0x2A47C -- neu pruefen. 0x28249C ist absichtlich "
                "nicht umgerechnet.",
    0x00265B08: "[2026-10-11, Rebase auf 0x58000] Die Wortsuche oben galt dem Wert "
                "0x00265B08, also einem Zeiger in der alten Zaehlweise. Ein Zeiger auf "
                "diese Funktion lautet bei Linkbasis 0x58000 0x000BDB08 -- die Suche "
                "nach Aufrufern ist mit diesem Wert zu wiederholen.",
}


def kommentare_umrechnen():
    lst = currentProgram.getListing()
    n_kommentare = 0
    n_zahlen = 0
    for typ, name in KOMMENTARTYPEN:
        it = lst.getCommentAddressIterator(typ, currentProgram.getMemory(), True)
        stellen = []
        while it.hasNext():
            stellen.append(it.next())
        for a in stellen:
            alt = lst.getComment(typ, a)
            treffer = [0]
            alte_stelle = a.getOffset() - BASE_NEU + BASE_ALT

            def ersetze(m):
                v = int(m.group(1), 16)
                if not (BASE_ALT <= v < BASE_ALT + DATEIGROESSE) or v in AUSNAHMEN:
                    return m.group(0)
                if (alte_stelle, v) in AUSNAHMEN_STELLE:
                    return m.group(0)
                treffer[0] += 1
                ziffern = m.group(1)
                breite = len(ziffern)
                fmt = "%0" + str(breite) + ("X" if ziffern.upper() == ziffern else "x")
                return "0x" + (fmt % neu(v))

            neu_text = KOMMENTARZAHL.sub(ersetze, alt)
            if typ == CodeUnit.PRE_COMMENT and alte_stelle in NACHTRAG:
                neu_text = neu_text + "\n" + NACHTRAG[alte_stelle]
                println("   %s [%s] Nachtrag angehaengt" % (a, name))
            if treffer[0] or neu_text != alt:
                lst.setComment(a, typ, neu_text)
                n_kommentare += 1
                n_zahlen += treffer[0]
                println("   %s [%s] %d Zahl(en)" % (a, name, treffer[0]))
                for z_alt, z_neu in zip(KOMMENTARZAHL.findall(alt),
                                        KOMMENTARZAHL.findall(neu_text)):
                    if z_alt != z_neu:
                        println("      0x%s -> 0x%s" % (z_alt, z_neu))
    return n_kommentare, n_zahlen


# --- 1. Zustand pruefen ---------------------------------------------------
bloecke = list(mem.getBlocks())
println("Bloecke vorher:")
for b in bloecke:
    println("   %-10s %s .. %s  %s" % (b.getName(), b.getStart(), b.getEnd(),
                                     "init" if b.isInitialized() else "uninit"))

flash = None
for b in bloecke:
    if b.getStart().getOffset() == BASE_ALT and b.getSize() == DATEIGROESSE:
        flash = b
if flash is None:
    for b in bloecke:
        if b.getStart().getOffset() == BASE_NEU and b.getSize() == DATEIGROESSE:
            println("\nBlock liegt bereits auf %s -- Verschieben wird uebersprungen."
                  % hexs(BASE_NEU))
            flash = b
    if flash is None:
        raise Exception("Kein Block mit Start %s und Groesse %s gefunden. "
                        "Falsches Programm? Abbruch ohne Aenderung."
                        % (hexs(BASE_ALT), hexs(DATEIGROESSE)))
    verschieben = False
else:
    verschieben = True

vorhanden = set([b.getName() for b in bloecke])
for name, dst, size, src, art in REGIONEN:
    if name in vorhanden:
        raise Exception("Block '%s' existiert schon. Abbruch, damit nichts "
                        "doppelt angelegt wird." % name)

vorher = bestand(verschieben)

# --- 2. Block verschieben -------------------------------------------------
if verschieben:
    println("\nVerschiebe '%s' von %s nach %s ..."
          % (flash.getName(), flash.getStart(), hexs(BASE_NEU)))
    mem.moveBlock(flash, toAddr(BASE_NEU), monitor)
    println("   fertig. Namen, Kommentare und Funktionen bleiben erhalten.")

# --- 3. Startregionen anlegen --------------------------------------------
println("\nLege die Startregionen der Scatter-Tabelle an:")
for name, dst, size, src, art in REGIONEN:
    if art == "zero":
        mem.createUninitializedBlock(name, toAddr(dst), size, False)
        mem.getBlock(toAddr(dst)).setWrite(True)   # Laufzeitdaten, nicht konstant
        println("   %-8s %s + %s  uninitialisiert (ZI)" % (name, hexs(dst), hexs(size)))
        continue

    mem.createInitializedBlock(name, toAddr(dst), size, 0, monitor, False)
    if art == "copy":
        werte = lies(src, size)
    else:
        roh = lies(src, DATEIGROESSE + BASE_NEU - src)   # bis Bildende
        werte, verbraucht = entpacken(roh, size)
        println("   %-8s entpackt aus %s Quellbytes" % ("", hexs(verbraucht)))
    schreibe(dst, werte)
    blk = mem.getBlock(toAddr(dst))
    blk.setWrite(True)
    blk.setExecute(name == "vectors")
    println("   %-8s %s + %s  aus %s (%s)" % (name, hexs(dst), hexs(size), hexs(src), art))


# --- 4. Selbstpruefung ----------------------------------------------------
# Drei Werte, die nur bei richtiger Basis stimmen koennen. Schlaegt einer fehl,
# ist etwas anderes schiefgegangen als erwartet -- dann Undo statt Weiterarbeiten.
println("\nSelbstpruefung:")
fehler = 0

# a) *(0x7D8) muss 0x718 sein (entpackte RW-Region)
w = mem.getInt(toAddr(0x7D8)) & 0xFFFFFFFF
ok = (w == 0x718)
fehler += 0 if ok else 1
println("   *(0x000007D8) = %s   erwartet 0x00000718   %s" % (hexs(w), "OK" if ok else "FEHLER"))

# b) *(0x718+0x98) muss 65536 sein -- die LUN-Kapazitaet in KiB (CL-USB-REC-119)
w = mem.getInt(toAddr(0x718 + 0x98)) & 0xFFFFFFFF
ok = (w == 0x10000)
fehler += 0 if ok else 1
println("   *(0x000007B0) = %s   erwartet 0x00010000   %s" % (hexs(w), "OK" if ok else "FEHLER"))

# c) 0x0008A434 muss auf einen Prolog zeigen (push {r4-r10,lr})
w = mem.getInt(toAddr(0x8A434)) & 0xFFFFFFFF
ok = (w == 0xE92D47F0)
fehler += 0 if ok else 1
println("   *(0x0008A434) = %s   erwartet 0xE92D47F0   %s" % (hexs(w), "OK" if ok else "FEHLER"))

println("\nBestand vorher -> nachher (alte Flash-Adressen umgerechnet):")
fehler += vergleiche(vorher, bestand(False))

println("\nKommentartexte auf die neue Basis umrechnen:")
n_k, n_z = kommentare_umrechnen()
println("   %d Zahlen in %d Kommentaren umgerechnet" % (n_z, n_k))

println("\nBloecke nachher:")
for b in mem.getBlocks():
    println("   %-10s %s .. %s  %s" % (b.getName(), b.getStart(), b.getEnd(),
                                     "init" if b.isInitialized() else "uninit"))

if fehler:
    println("\n%d Pruefung(en) fehlgeschlagen. NICHT speichern -- Undo (Strg+Z) "
          "und nachsehen, was abweicht." % fehler)
else:
    println("\nAlle Pruefungen bestanden.")
    println("Naechste Schritte von Hand, weil sie Analyse ausloesen und dauern:")
    println("  1. Auto-Analyse ueber die neuen Bloecke laufen lassen")
    println("     (Analysis -> Auto Analyze, nur die neuen Adressbereiche).")
    println("  2. An 0x0008A434, 0x0008A500, 0x000D9934, 0x00109AC4 Funktionen")
    println("     anlegen (F), falls die Analyse sie nicht selbst findet.")
    println("  3. Speichern, dann in der Sitzung gegenpruefen:")
    println("     search_xrefs_to 0x0008A434 -> vier Ladestellen")
    println("     read_words 0x000007D8      -> 0x718")
    println("     get_current_program        -> Block flash ab 0x00058000")
