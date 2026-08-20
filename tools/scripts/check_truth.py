#!/usr/bin/env python3
"""Prueft research/TRUTH.csv auf die Regeln aus research/TRUTH.md.

Exit 0 = in Ordnung, 1 = Verstoss. Gedacht fuer den Sitzungsanfang und als
pre-commit-Hook. Die Regeln stehen sonst nur in einem Chat -- und Chats enden.
"""
import csv, glob, os, sys

P = "research/TRUTH.csv"
COLS = ["Subsystem","Topic","Statement","Status","Confidence","Evidence_E0","Evidence_E3New",
        "Evidence_E1","Evidence_E3Old","Evidence_E4","Authority","Open_Question","Next_Test",
        "Claim_ID","Decided","Superseded_By","Updated","Source","Prio"]

def main():
    err = []
    if not os.path.exists(P):
        sys.exit("FEHLT: %s" % P)
    rows = list(csv.DictReader(open(P, encoding="utf-8", errors="replace")))
    if list(rows[0].keys()) != COLS:
        err.append("Spalten weichen ab: %s" % list(rows[0].keys()))
    ids = [r["Claim_ID"] for r in rows]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        err.append("doppelte Claim_IDs: %s" % dup)
    open_rows = [r for r in rows if r["Decided"] == "no" and not r["Superseded_By"]]
    no_test = [r["Claim_ID"] for r in open_rows if not r["Next_Test"].strip()]
    if no_test:
        err.append("offene Zeilen ohne Next_Test: %s" % no_test)
    bad_dec = [r["Claim_ID"] for r in rows if r["Decided"] not in ("yes", "no")]
    if bad_dec:
        err.append("Decided weder yes noch no: %s" % bad_dec)
    sup = {r["Claim_ID"] for r in rows}
    dangling = [r["Claim_ID"] for r in rows if r["Superseded_By"] and r["Superseded_By"] not in sup]
    if dangling:
        err.append("Superseded_By zeigt ins Leere: %s" % dangling)
    PRIO = ("now", "next", "later", "park")
    bad_prio = [r["Claim_ID"] for r in rows
                if (r["Decided"] == "no" and r.get("Prio") not in PRIO)
                or (r["Decided"] == "yes" and r.get("Prio", "").strip())]
    if bad_prio:
        err.append("Prio fehlt bei offener Zeile oder steht bei entschiedener: %s" % bad_prio[:12])
    front = [r["Claim_ID"] for r in rows if r["Decided"] == "no" and r.get("Prio") == "now"]
    if len(front) > 6:
        err.append("Arbeitsfront hat %d Zeilen, erlaubt sind hoechstens 6: %s" % (len(front), front))

    copies = [f for f in glob.glob("research/TRUTH.csv*") if f != P and not f.endswith(".md")]
    if copies:
        err.append("Kopien neben der autoritativen Datei (Git ist die Historie): %s" % copies)
    locks = glob.glob("research/.~lock.*")
    if locks:
        err.append("Office-Lockdatei offen -- Datei ist in Bearbeitung: %s" % locks)

    print("TRUTH.csv: %d Zeilen, %d entschieden, %d offen, %d abgeloest | Front %d"
          % (len(rows), sum(1 for r in rows if r["Decided"] == "yes"),
             len(open_rows), sum(1 for r in rows if r["Superseded_By"]), len(front)))
    for e in err:
        print("  VERSTOSS: %s" % e)
    return 1 if err else 0

if __name__ == "__main__":
    sys.exit(main())
