# Liest einen Datenbereich als Folge von 32-Bit-Worten und fasst zusammenhaengende
# Laeufe von Codezeigern zu Tabellen zusammen. Liest nur.
#
# Aufruf: zeigertabellen_lesen.py <von> <bis> [kandidatendatei]
#   von, bis   Adressen mit 0x-Praefix
#
# Je Wort eine Klasse:
#   F  zeigt auf einen Funktionsanfang (bekannt)
#   K  zeigt auf einen Kandidaten aus der Kandidatendatei, der noch keine Funktion ist
#   I  zeigt in den Koerper einer Funktion, nicht auf ihren Anfang
#   C  zeigt in den Codeblock, aber weder F noch K noch I
#   -  alles andere (kein Zeiger in den Codeblock)
# Ein Lauf ist eine Folge von Worten der Klassen F/K/I/C ohne Unterbrechung.
# Fuer jeden Lauf: Laenge und Anteil bekannter Anfaenge. Ein Lauf, der ueberwiegend
# auf bekannte Anfaenge zeigt, ist eine Funktionstabelle -- seine K-Eintraege sind
# dann mit hoher Wahrscheinlichkeit ebenfalls Anfaenge.
#
# @category ZK-Inkjet
# @runtime Jython

import re

args = getScriptArgs()
von, bis = int(args[0], 16), int(args[1], 16)
kand = set()
if len(args) >= 3:
    for z in open(args[2]):
        m = re.search(r'\(\s*(0x[0-9A-Fa-f]+)\s*,', z)
        if m:
            kand.add(int(m.group(1), 16))

mem = currentProgram.getMemory()
fm = currentProgram.getFunctionManager()
code_lo, code_hi = 0x00058000, 0x002CD22C


def klasse(v):
    if not (code_lo <= v < code_hi) or (v & 3):
        return "-"
    a = toAddr(v)
    if fm.getFunctionAt(a) is not None:
        return "F"
    if v in kand:
        return "K"
    if fm.getFunctionContaining(a) is not None:
        return "I"
    return "C"


laeufe = []
lauf = None
for va in range(von, bis, 4):
    v = mem.getInt(toAddr(va)) & 0xFFFFFFFF
    k = klasse(v)
    if k == "-":
        if lauf:
            laeufe.append(lauf)
            lauf = None
        continue
    if lauf is None:
        lauf = {"start": va, "eintraege": []}
    lauf["eintraege"].append((va, v, k))
if lauf:
    laeufe.append(lauf)

println("Bereich 0x%08X..0x%08X, %d Laeufe" % (von, bis, len(laeufe)))
k_tabelle, k_sonst = [], []
for l in laeufe:
    e = l["eintraege"]
    n = len(e)
    zaehl = dict((c, sum(1 for x in e if x[2] == c)) for c in "FKIC")
    anteil_f = float(zaehl["F"]) / n
    tabelle = n >= 4 and anteil_f >= 0.5
    if n >= 4 or zaehl["K"]:
        println("  Lauf 0x%08X..0x%08X  n=%3d  F=%3d K=%3d I=%3d C=%3d  %s"
                % (l["start"], e[-1][0] + 4, n, zaehl["F"], zaehl["K"], zaehl["I"], zaehl["C"],
                   "TABELLE" if tabelle else ""))
    for va, v, k in e:
        if k == "K":
            (k_tabelle if tabelle else k_sonst).append((v, va, l["start"]))

println("Kandidaten in Tabellen (ueberwiegend bekannte Anfaenge): %d" % len(k_tabelle))
println("Kandidaten in anderen Laeufen: %d" % len(k_sonst))
for v, va, s in sorted(k_tabelle):
    println("  T 0x%08X  aus 0x%08X (Lauf ab 0x%08X)" % (v, va, s))
for v, va, s in sorted(k_sonst):
    println("  S 0x%08X  aus 0x%08X (Lauf ab 0x%08X)" % (v, va, s))
