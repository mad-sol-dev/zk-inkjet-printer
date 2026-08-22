#!/usr/bin/env python3
"""Prueft research/TRUTH.csv auf die Regeln aus research/TRUTH.md.

Exit 0 = in Ordnung, 1 = Verstoss. Gedacht fuer den Sitzungsanfang und als
pre-commit-Hook. Die Regeln stehen sonst nur in einem Chat -- und Chats enden.

Grundsatz fuer die Meldungen hier: wer das Skript laufen laesst, ist oft ein
Agent ohne Vorgeschichte. Ein Traceback oder ein nacktes "Verstoss" laesst ihn
ratlos zurueck. Jede Abbruchmeldung sagt deshalb, was passiert ist, was es
bedeutet und was als naechstes zu tun ist.
"""
import csv, glob, os, subprocess, sys

P = "research/TRUTH.csv"
COLS = ["Subsystem","Topic","Statement","Status","Confidence","Evidence_E0","Evidence_E3New",
        "Evidence_E1","Evidence_E3Old","Evidence_E4","Authority","Open_Question","Next_Test",
        "Claim_ID","Decided","Superseded_By","Updated","Source","Prio","Depends_On","Oracle"]

# Ab diesem Datum gelten Oracle-Pflicht und Konfidenzdeckel. Aeltere Zeilen
# bleiben unberuehrt -- sie werden beim naechsten Anfassen nachgezogen, nicht
# rueckwirkend umgeschrieben.
ORACLE_AB = "2026-08-22"
DECKEL = {"O1": 0.60, "O2": 0.95, "O3": 1.00}

ATOMAR = """Wie es nicht wieder passiert: TRUTH.csv nie in place schreiben.
  open(P,'w') kuerzt die Datei, bevor der Rest des Aufrufs geprueft wird --
  ein assert weiter unten im Skript kommt zu spaet. Stattdessen in eine
  Temporaerdatei schreiben, das Ergebnis pruefen, dann os.replace.
  Das Muster steht in CLAUDE.md unter "TRUTH.csv wird atomar geschrieben"."""

def fatal(titel, bedeutung, todo):
    print("FATAL: %s" % titel)
    print()
    print("  Was das heisst: %s" % bedeutung)
    print()
    print("  Was jetzt zu tun ist:")
    for zeile in todo.strip().splitlines():
        print("  %s" % zeile)
    print()
    sys.exit(1)

def zeilen_in_head():
    """Zeilenzahl der zuletzt committeten Fassung, oder None wenn nicht ermittelbar."""
    try:
        out = subprocess.run(["git", "show", "HEAD:" + P], capture_output=True, timeout=10)
        if out.returncode != 0:
            return None
        text = out.stdout.decode("utf-8", "replace")
        return len(list(csv.DictReader(text.splitlines())))
    except Exception:
        return None

def main():
    err = []

    if not os.path.exists(P):
        fatal("%s existiert nicht." % P,
              "ohne diese Datei hat das Projekt keinen Stand -- sie ist die einzige "
              "autoritative Quelle.",
              "Pruefen, ob das Arbeitsverzeichnis stimmt: der Aufruf erwartet die\n"
              "  Wurzel des firmware-Repositories. Sonst aus Git holen:\n"
              "      git checkout -- %s" % P)

    if os.path.getsize(P) == 0:
        fatal("%s ist 0 Bytes gross." % P,
              "die Datei wurde in place geschrieben und der Schreibvorgang ist "
              "abgebrochen. Der Inhalt ist weg, aber nicht verloren, solange committet war.",
              "    git checkout -- %s\n\n%s" % (P, ATOMAR))

    try:
        with open(P, encoding="utf-8", errors="replace", newline="") as fh:
            rows = list(csv.DictReader(fh))
    except Exception as exc:
        fatal("%s laesst sich nicht als CSV lesen (%s)." % (P, exc.__class__.__name__),
              "die Datei ist beschaedigt oder halb geschrieben. Meldung: %s" % exc,
              "    git checkout -- %s\n\n%s" % (P, ATOMAR))

    if not rows:
        fatal("%s enthaelt keine einzige Datenzeile." % P,
              "die Kopfzeile ist da oder auch nicht, aber Inhalt fehlt. Das ist fast "
              "immer ein abgebrochener Schreibvorgang, kein absichtlicher Zustand -- "
              "Regel 5 verbietet das Loeschen von Zeilen.",
              "    git checkout -- %s\n\n%s" % (P, ATOMAR))

    if list(rows[0].keys()) != COLS:
        fehlend = [c for c in COLS if c not in rows[0]]
        zuviel = [c for c in rows[0] if c not in COLS]
        err.append("Spalten weichen ab -- fehlend: %s, unerwartet: %s" % (fehlend or "keine", zuviel or "keine"))

    vorher = zeilen_in_head()
    if vorher is not None and len(rows) < vorher:
        fatal("Zeilenzahl ist gesunken: %d in HEAD, %d im Arbeitsbaum (%d fehlen)."
              % (vorher, len(rows), vorher - len(rows)),
              "Regel 5 sagt, dass Zeilen nie geloescht werden, sondern nur per "
              "Superseded_By abgeloest. Eine sinkende Zeilenzahl ist deshalb immer "
              "ein Fehler und nie eine Absicht.",
              "Zuerst ansehen, was verschwunden ist:\n"
              "      git diff -- %s | grep '^-' | head -20\n"
              "  War es ein Versehen, dann verwerfen:\n"
              "      git checkout -- %s\n\n%s" % (P, P, ATOMAR))

    ids = [r["Claim_ID"] for r in rows]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        err.append("doppelte Claim_IDs: %s -- jede ID darf nur einmal vorkommen" % dup)
    open_rows = [r for r in rows if r["Decided"] == "no" and not r["Superseded_By"]]
    no_test = [r["Claim_ID"] for r in open_rows if not r["Next_Test"].strip()]
    if no_test:
        err.append("offene Zeilen ohne Next_Test: %s -- Regel 4: eine Frage ohne "
                   "definiertes Experiment ist kein Arbeitspaket" % no_test)
    bad_dec = [r["Claim_ID"] for r in rows if r["Decided"] not in ("yes", "no")]
    if bad_dec:
        err.append("Decided weder yes noch no: %s" % bad_dec)
    sup = {r["Claim_ID"] for r in rows}
    dangling = [(r["Claim_ID"], r["Superseded_By"]) for r in rows
                if r["Superseded_By"] and r["Superseded_By"] not in sup]
    if dangling:
        err.append("Superseded_By zeigt ins Leere: %s -- die genannte Zeile gibt es "
                   "nicht; oft ein verrutschtes Feld beim Anlegen" % dangling)
    PRIO = ("now", "next", "later", "park")
    bad_prio = [r["Claim_ID"] for r in rows
                if (r["Decided"] == "no" and r.get("Prio") not in PRIO)
                or (r["Decided"] == "yes" and r.get("Prio", "").strip())]
    if bad_prio:
        err.append("Prio fehlt bei offener Zeile oder steht bei entschiedener: %s "
                   "-- offen braucht now/next/later/park, entschieden braucht leer" % bad_prio[:12])
    front = [r["Claim_ID"] for r in rows if r["Decided"] == "no" and r.get("Prio") == "now"]
    if len(front) > 6:
        err.append("Arbeitsfront hat %d Zeilen, erlaubt sind hoechstens 6: %s -- eine "
                   "erledigte now-Zeile schliessen, bevor eine neue nachrueckt" % (len(front), front))

    # --- Abhaengigkeiten (Depends_On) ---
    deps = {r["Claim_ID"]: [d.strip() for d in r.get("Depends_On", "").split(";") if d.strip()]
            for r in rows}
    tot = {r["Claim_ID"]: r["Superseded_By"] for r in rows}
    ins_leere = [(cid, d) for cid, ds in deps.items() for d in ds if d not in ids]
    if ins_leere:
        err.append("Depends_On zeigt ins Leere: %s -- die genannte Zeile gibt es nicht"
                   % ins_leere[:8])
    selbst = [cid for cid, ds in deps.items() if cid in ds]
    if selbst:
        err.append("Depends_On zeigt auf sich selbst: %s" % selbst)
    veraltet = [(cid, d) for cid, ds in deps.items() for d in ds if tot.get(d)]
    if veraltet:
        err.append("Zeile haengt an einer abgeloesten Zeile: %s -- die Ablösung ist "
                   "noch nicht durchgereicht. Jede dieser Zeilen gegen die Nachfolgerin "
                   "pruefen und Depends_On umhaengen; das Umhaengen IST die Pruefung. "
                   "Genau dieses Nicht-Durchreichen hat CONTRADICTION-USB-001 sieben "
                   "Monate am Leben gehalten." % veraltet[:8])

    def zyklus():
        weiss, grau = set(ids), set()
        def geh(n, pfad):
            if n in grau:
                return pfad[pfad.index(n):] + [n]
            if n not in weiss:
                return None
            weiss.discard(n); grau.add(n)
            for m in deps.get(n, []):
                if m in ids:
                    z = geh(m, pfad + [n])
                    if z:
                        return z
            grau.discard(n)
            return None
        for n in list(ids):
            z = geh(n, [])
            if z:
                return z
        return None
    z = zyklus()
    if z:
        err.append("Depends_On enthaelt einen Zyklus: %s -- Abhaengigkeiten muessen "
                   "ein azyklischer Graph sein, sonst traegt keine Zeile die andere"
                   % " -> ".join(z))

    # --- Oracle-Stufe und Konfidenzdeckel ---
    bad_or = [r["Claim_ID"] for r in rows if r.get("Oracle", "") not in ("", "O1", "O2", "O3")]
    if bad_or:
        err.append("Oracle weder leer noch O1/O2/O3: %s" % bad_or)
    neu = [r for r in rows if r.get("Updated", "") >= ORACLE_AB]
    ohne = [r["Claim_ID"] for r in neu if not r.get("Oracle", "").strip()]
    if ohne:
        err.append("ab %s geaenderte Zeile ohne Oracle-Stufe: %s -- O1 hergeleitet, "
                   "O2 ein wiederholbares Kommando ueber eine Datei, O3 beobachtetes "
                   "Geraeteverhalten" % (ORACLE_AB, ohne[:12]))
    ueber = []
    for r in neu:
        o = r.get("Oracle", "").strip()
        if o in DECKEL:
            try:
                c = float(r["Confidence"])
            except ValueError:
                continue
            if c > DECKEL[o] + 1e-9:
                ueber.append((r["Claim_ID"], o, c, DECKEL[o]))
    if ueber:
        err.append("Konfidenz ueber dem Deckel der Oracle-Stufe: %s -- entweder die "
                   "Zahl senken oder die Aussage auf eine hoehere Stufe heben. Neun der "
                   "bisher fuenfzehn abgeloesten Zeilen standen auf E0, drei bei 0.95 "
                   "und hoeher: Ueberzeugung ist kein Beleg." % ueber[:8])

    reste = [f for f in glob.glob(P + "*") if f.endswith((".tmp", ".part", ".bak"))]
    if reste:
        err.append("Reste eines abgebrochenen Schreibvorgangs: %s -- pruefen und "
                   "loeschen; die eigentliche Datei scheint in Ordnung" % reste)
    copies = [f for f in glob.glob("research/TRUTH.csv*")
              if f != P and not f.endswith(".md") and f not in reste]
    if copies:
        err.append("Kopien neben der autoritativen Datei: %s -- Regel 3: Git ist die "
                   "Historie, vor groesseren Aenderungen committen statt kopieren" % copies)
    locks = glob.glob("research/.~lock.*")
    if locks:
        err.append("Office-Lockdatei offen -- die Datei ist gerade in einem Editor "
                   "geoeffnet, Schreibzugriffe kollidieren: %s" % locks)

    print("TRUTH.csv: %d Zeilen, %d entschieden, %d offen, %d abgeloest | Front %d"
          % (len(rows), sum(1 for r in rows if r["Decided"] == "yes"),
             len(open_rows), sum(1 for r in rows if r["Superseded_By"]), len(front)))
    for e in err:
        print("  VERSTOSS: %s" % e)
    return 1 if err else 0

if __name__ == "__main__":
    sys.exit(main())
