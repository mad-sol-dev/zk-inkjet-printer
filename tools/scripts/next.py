#!/usr/bin/env python3
"""Der Einstiegsbefehl. Erste Handlung jeder neuen Sitzung:

    python3 tools/scripts/next.py

Druckt: Pruefergebnis, Arbeitsfront, Restmenge. Nichts sonst. Wer das gelesen
hat, weiss wo das Projekt steht, ohne eine einzige Beschreibungsdatei zu oeffnen.

Prio-Werte und ihre Bedeutung:
  now    Arbeitsfront -- was diese Sitzung anfasst. Handverlesen, hoechstens 6.
  next   Kandidaten fuer die naechste Front. Aus laufender Arbeit entstanden.
  later  Altlast aus Phase-1-Reconciliation (Januar). Nicht falsch, nur kalt.
  park   Betrifft unser Werkzeug, nicht das Geraet. Zaehlt nicht als Wissen.
  (leer) entschieden oder abgeloest.
"""
import csv, os, subprocess, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "research", "TRUTH.csv")


def sh(cmd):
    try:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                              timeout=20).stdout.strip()
    except Exception:
        return ""


def main():
    print("=" * 72)
    print("ZK-INKJET -- Stand")
    print("=" * 72)

    rc = subprocess.run([sys.executable, "tools/scripts/check_truth.py"], cwd=ROOT)
    if rc.returncode:
        print("\n>> Erst die Verstoesse beheben. Alles andere wartet.\n")
        return 1

    rows = list(csv.DictReader(open(P, encoding="utf-8")))
    open_rows = [r for r in rows if r["Decided"] == "no"]
    prio = Counter(r.get("Prio", "") for r in open_rows)

    print("\nARBEITSFRONT (Prio=now) -- hier weiterarbeiten:")
    front = [r for r in open_rows if r.get("Prio") == "now"]
    if not front:
        print("  leer. Front aus Prio=next nachfuellen, hoechstens 6 Zeilen.")
    for r in front:
        print("\n  %s  [%s]  %s" % (r["Claim_ID"], r["Confidence"], r["Topic"]))
        print("    %s" % r["Statement"][:200].replace("\n", " "))
        print("    NAECHSTER TEST: %s" % r["Next_Test"][:260].replace("\n", " "))

    print("\nRESTMENGE")
    print("  offen gesamt %d   davon now %d | next %d | later %d | park %d"
          % (len(open_rows), prio["now"], prio["next"], prio["later"], prio["park"]))
    real = [r for r in open_rows if r.get("Prio") in ("now", "next", "later")]
    print("  echte Geraetefragen: %d (park zaehlt nicht mit)" % len(real))
    sub = Counter(r["Subsystem"] for r in real)
    print("  nach Subsystem: " + "  ".join("%s %d" % (k, v) for k, v in sub.most_common()))

    print("\nTRAGENDE ZEILEN -- was am meisten Gewicht haelt:")
    traeger = Counter(d.strip() for r in rows
                      for d in r.get("Depends_On", "").split(";") if d.strip())
    topf = {r["Claim_ID"]: r for r in rows}
    if not traeger:
        print("  keine Depends_On gesetzt.")
    for cid, n in traeger.most_common(5):
        r = topf.get(cid, {})
        print("  %-22s %d Abhaengige  [%s/%s]  %s"
              % (cid, n, r.get("Oracle") or "--", r.get("Confidence", "?"),
                 r.get("Topic", "?")[:44]))

    print("\nGIT")
    print("  " + (sh(["git", "log", "--oneline", "-3"]).replace("\n", "\n  ") or "?"))
    dirty = sh(["git", "status", "--porcelain"])
    print("  Arbeitsbaum: " + ("SAUBER" if not dirty else "%d geaenderte Dateien" % len(dirty.splitlines())))

    print("\nREGELN: research/TRUTH.md  (Kurzfassung oben in CLAUDE.md / AGENTS.md)")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
