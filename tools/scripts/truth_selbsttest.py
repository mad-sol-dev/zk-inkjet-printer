#!/usr/bin/env python3
"""Positivkontrollen fuer truth.py und truth_mcp.py.

Spielt in einer Wegwerfkopie des Projekts (tools/ und research/TRUTH.csv,
eigenes Git-Repository) eine feste Folge von Aenderungen durch: erlaubte
muessen schreiben, verbotene muessen abgelehnt werden UND die Datei
unveraendert lassen. Danach dasselbe einmal ueber den MCP-Server.

    python3 tools/truth_selbsttest.py
"""
import csv, hashlib, json, os, shutil, subprocess, sys, tempfile

HIER = os.path.dirname(os.path.abspath(__file__))


def _wurzel():
    d = HIER
    while not os.path.exists(os.path.join(d, "research", "TRUTH.csv")):
        if os.path.dirname(d) == d:
            raise SystemExit("research/TRUTH.csv nicht gefunden")
        d = os.path.dirname(d)
    return d


QUELLE = _wurzel()
TOOLS_REL = os.path.relpath(HIER, QUELLE)


class Lauf:
    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="truth-cli-test-")
        shutil.copytree(HIER, os.path.join(self.root, TOOLS_REL),
                        ignore=shutil.ignore_patterns("__pycache__"))
        os.makedirs(os.path.join(self.root, "research"))
        shutil.copy(os.path.join(QUELLE, "research", "TRUTH.csv"),
                    os.path.join(self.root, "research", "TRUTH.csv"))
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "basis", "--no-verify")
        self.fehler = 0

    def git(self, *a):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t"] + list(a),
                              cwd=self.root, capture_output=True, text=True)

    def p(self):
        return os.path.join(self.root, "research", "TRUTH.csv")

    def zeilen(self):
        with open(self.p(), encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    def zeile(self, cid):
        return next(r for r in self.zeilen() if r["Claim_ID"] == cid)

    def hash(self):
        return hashlib.sha256(open(self.p(), "rb").read()).hexdigest()

    def cli(self, *a, stdin=None):
        p = subprocess.run([sys.executable, os.path.join(self.root, TOOLS_REL, "truth.py")] + list(a),
                           cwd=self.root, capture_output=True, text=True, input=stdin)
        return p.returncode, p.stdout + p.stderr

    def soll(self, name, ok, info=""):
        print("%-4s %s" % ("ok" if ok else "FEHL", name))
        if not ok:
            self.fehler += 1
            print("     " + info.strip().replace("\n", "\n     ")[:1500])

    def erlaubt(self, name, *a, stdin=None):
        vorher = self.hash()
        rc, out = self.cli(*a, stdin=stdin)
        self.soll(name, rc == 0 and self.hash() != vorher, out)
        return out

    def verboten(self, name, erwartet, *a):
        vorher = self.hash()
        rc, out = self.cli(*a)
        self.soll(name, rc == 1 and self.hash() == vorher and erwartet in out,
                  "rc=%d, Datei %s\n%s" % (rc, "gleich" if self.hash() == vorher else "VERAENDERT", out))
        return out


def main():
    t = Lauf()
    sub = "SELBSTTEST"
    alt = "T-SELBSTTEST-000"       # eigener Traeger, damit kein echter Altbestand beruehrt wird
    sys.path.insert(0, os.path.join(t.root, TOOLS_REL))
    import check_truth as ct
    zelle_ab = getattr(ct, "ZELLE_AB", "")
    evidenz_ab = getattr(ct, "EVIDENZ_AB", None)
    import datetime
    heute = datetime.date.today().isoformat()
    try:
        t.erlaubt("Traeger anlegen", "add", "--subsystem", sub, "--id", alt, "--topic", "Traeger",
                  "--statement", "Traeger gilt.", "--oracle", "O2", "--confidence", "0.9",
                  "--evidence", "python3 probe.py t.bin", "--entschieden")
        t.verboten("offene Zeile ohne Next_Test", "ohne --next-test",
                   "add", "--subsystem", sub, "--id", "T-SELBSTTEST-001", "--topic", "t",
                   "--statement", "s", "--oracle", "O1", "--confidence", "0.5")
        t.erlaubt("offene Zeile anlegen", "add", "--subsystem", sub, "--id", "T-SELBSTTEST-001",
                  "--topic", "Frage A", "--statement", "OFFEN. Ist A so?", "--oracle", "O1",
                  "--confidence", "0.5", "--next-test", "Kommando ausfuehren", "--prio", "next")
        r = t.zeile("T-SELBSTTEST-001")
        t.soll("Vorgaben gesetzt (Decided=no, Prio=next, Updated)",
               r["Decided"] == "no" and r["Prio"] == "next" and r["Updated"])
        t.erlaubt("entschiedene Zeile per JSON, haengt am Traeger", "add", "--json", "-",
                  stdin=json.dumps({"subsystem": sub, "id": "T-SELBSTTEST-002", "topic": "Befund B",
                                    "statement": "B ist so.", "oracle": "O2", "confidence": 0.9,
                                    "evidence": "python3 probe.py x.bin", "depends_on": alt,
                                    "entschieden": True}))
        vorher = t.hash()
        rc, out = t.cli("add", "--subsystem", sub, "--topic", "x", "--statement", "x", "--oracle",
                        "O1", "--confidence", "0.3", "--next-test", "t", "--dry-run")
        t.soll("Trockenlauf schreibt nicht und vergibt ID automatisch",
               rc == 0 and t.hash() == vorher and "T-SELBSTTEST-003" in out, out)
        out = t.verboten("Konfidenz ueber dem O1-Deckel", "Deckel",
                         "close", "T-SELBSTTEST-001", "--oracle", "O1", "--confidence", "0.9")
        t.soll("die Ablehnung nennt keinen Schein-Verstoss 'Kopien' (Pruefung der Wegwerfkopie)",
               "Kopien" not in out, out)
        t.verboten("--json mit fehlender Datei: Ablehnung statt Traceback", "--json",
                   "set", "T-SELBSTTEST-001", "--json", os.path.join(t.root, "fehlt.json"))
        if evidenz_ab is None or heute < evidenz_ab:
            print("--   O2 ohne Evidenz: uebersprungen, der Validator kennt die Regel %s"
                  % ("nicht (EVIDENZ_AB fehlt)" if evidenz_ab is None else "erst ab " + evidenz_ab))
        else:
            t.verboten("O2 ohne Evidenz", "Evidence",
                       "close", "T-SELBSTTEST-001", "--oracle", "O2", "--confidence", "0.95")
        t.erlaubt("Zeile schliessen", "close", "T-SELBSTTEST-001", "--oracle", "O2",
                  "--confidence", "0.95", "--evidence", "python3 probe.py a.bin",
                  "--urteil", "A ist so.")
        r = t.zeile("T-SELBSTTEST-001")
        t.soll("geschlossen: Decided=yes, Prio leer, Next_Test leer, Urteil vorn, OFFEN entfernt",
               r["Decided"] == "yes" and not r["Prio"] and not r["Next_Test"]
               and r["Statement"].startswith("ENTSCHIEDEN") and "OFFEN" not in r["Statement"], str(r))
        haengende = [x["Claim_ID"] for x in t.zeilen()
                     if alt in [d.strip() for d in x["Depends_On"].split(";")]]
        out = t.verboten("Abloesung ohne Entscheidung ueber die Abhaengigen", "NICHT GESCHRIEBEN",
                         "supersede", alt, "--by", "T-SELBSTTEST-001", "--notiz", "test")
        t.soll("die Ablehnung nennt jede abhaengige Zeile",
               all(h in out for h in haengende) and haengende, out)
        t.erlaubt("Abloesung mit Umhaengen", "supersede", alt, "--by", "T-SELBSTTEST-001",
                  "--notiz", "test", "--umhaengen", *haengende)
        t.soll("Abhaengige haengen an der Nachfolgerin",
               all("T-SELBSTTEST-001" in t.zeile(h)["Depends_On"] for h in haengende)
               and t.zeile(alt)["Superseded_By"] == "T-SELBSTTEST-001")
        rc, out = t.cli("check")
        t.soll("Validator danach sauber", rc == 0, out)
        # Ein Prozess, zwei Laeufe, dazwischen ein geaenderter Validator -- so wie im
        # langlebigen MCP-Server. Der zweite Lauf muss die Aenderung sehen.
        tools = os.path.join(t.root, TOOLS_REL)
        ct_pfad = os.path.join(tools, "check_truth.py")
        original = open(ct_pfad, encoding="utf-8").read()
        probe = ("import sys\nsys.path.insert(0, %r)\nimport truth\n"
                 "rc1, _ = truth.pruefen()\n"
                 "open(%r, 'a', encoding='utf-8').write("
                 "'\\n\\ndef main():\\n    print(\"  VERSTOSS: Selbsttest-Marke\")\\n    return 1\\n')\n"
                 "rc2, aus = truth.pruefen()\n"
                 "print(rc1, rc2, 'Selbsttest-Marke' in aus)\n") % (tools, ct_pfad)
        try:
            p = subprocess.run([sys.executable, "-c", probe], cwd=t.root, capture_output=True, text=True)
        finally:
            with open(ct_pfad, "w", encoding="utf-8") as fh:
                fh.write(original)
        t.soll("Validator wird je Lauf neu geladen (langlebiger MCP-Server)",
               p.stdout.split() == ["0", "1", "True"], p.stdout + p.stderr)
        t.verboten("Claim_ID aendern", "Claim_ID", "set", "T-SELBSTTEST-002", "Claim_ID=X-1")
        t.verboten("Prio an entschiedener Zeile", "Prio", "prio", "T-SELBSTTEST-002", "now")
        if zelle_ab and heute < zelle_ab:
            print("--   Zelle ueber der Grenze: uebersprungen, die Grenze gilt erst ab %s" % zelle_ab)
        else:
            t.verboten("Zelle ueber der Grenze", "Grenze", "set", "T-SELBSTTEST-002",
                       "Statement=" + "x" * 2001)
        t.verboten("Commit ohne Claim-ID", "keine Claim-ID", "commit", "irgendwas")
        rc, out = t.cli("commit", "T-SELBSTTEST-001: Weg zum Urteil")
        t.soll("Commit mit Claim-ID", rc == 0, out)
        rc, out = t.cli("journal", "T-SELBSTTEST-001")
        t.soll("Journal findet den Commit", rc == 0 and "Weg zum Urteil" in out, out)

        # MCP: gleiche Funktionen ueber JSON-RPC
        msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize",
                 "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                            "clientInfo": {"name": "selbsttest", "version": "1"}}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                 "params": {"name": "truth_show", "arguments": {"id": "T-SELBSTTEST-001",
                                                                "felder": ["Decided"]}}},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                 "params": {"name": "truth_close", "arguments": {"id": "T-SELBSTTEST-002",
                                                                 "oracle": "O9"}}}]
        vorher = t.hash()
        p = subprocess.run([sys.executable, os.path.join(t.root, TOOLS_REL, "truth_mcp.py")],
                           cwd=t.root, capture_output=True, text=True,
                           input="\n".join(json.dumps(m) for m in msgs) + "\n")
        antworten = {}
        for z in p.stdout.splitlines():
            try:
                m = json.loads(z)
                antworten[m.get("id")] = m
            except json.JSONDecodeError:
                antworten.setdefault("muell", []).append(z)
        t.soll("MCP: nur JSON auf stdout, eine Antwort je Anfrage, keine auf die Benachrichtigung",
               "muell" not in antworten and sorted(k for k in antworten if k) == [1, 2, 3, 4],
               p.stdout + p.stderr)
        tools = antworten.get(2, {}).get("result", {}).get("tools", [])
        t.soll("MCP: Werkzeugliste", len(tools) >= 10 and all("inputSchema" in x for x in tools))
        r3 = antworten.get(3, {}).get("result", {})
        t.soll("MCP: Lesen", not r3.get("isError") and "Decided: yes" in r3["content"][0]["text"], str(r3))
        r4 = antworten.get(4, {}).get("result", {})
        t.soll("MCP: verbotene Aenderung als isError, Datei unveraendert",
               r4.get("isError") is True and t.hash() == vorher, str(r4))
    finally:
        shutil.rmtree(t.root, ignore_errors=True)
    print("\n%s" % ("Alle Kontrollen bestanden." if not t.fehler
                    else "%d Kontrolle(n) fehlgeschlagen -- dem Werkzeug nicht trauen." % t.fehler))
    return 1 if t.fehler else 0


if __name__ == "__main__":
    sys.exit(main())
