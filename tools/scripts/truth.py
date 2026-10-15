#!/usr/bin/env python3
"""Das Werkzeug fuer research/TRUTH.csv. Lesen und Aendern nur hierueber.

Warum es das gibt: jede Sitzung hat sich bisher ihr eigenes Python-Schnipsel
geschrieben, um das Register zu aendern -- mit denselben Fallstricken jedes
Mal (atomar schreiben, Zeilenzahl, CRLF, Pruefstufe), und ein solches
Schnipsel hat das Register in ZK-Inkjet einmal auf null Bytes gekuerzt.

Lesen:
  truth.py front                      Arbeitsfront mit naechstem Test
  truth.py find [--offen|--entschieden] [--prio P] [--subsystem S] [--oracle O] [--text REGEX] [--limit N]
  truth.py show ID [--felder F,F]     eine Zeile, volle Zellen
  truth.py deps ID                    worauf sie steht, was an ihr haengt
  truth.py journal ID                 Commits, die die ID nennen (das Laborjournal)
  truth.py check                      der Validator

Aendern (jeweils mit --dry-run zum Vorab-Ansehen):
  truth.py add --subsystem S --topic T --statement X --oracle O1 --confidence 0.5
               [--next-test X --prio next | --entschieden] [--evidence X] [--depends A;B]
               [--source X] [--status S] [--id ID]
  truth.py close ID --oracle O2 --confidence 0.95 --evidence X [--urteil X | --statement X] [--status refuted]
  truth.py supersede ALT --by NEU --notiz X [--umhaengen ID ...] [--mitabloesen ID ...]
  truth.py set ID Feld=Wert [Feld=Wert ...]
  truth.py prio ID now|next|later|park
  truth.py commit "CL-...: Nachricht"   committet nur research/TRUTH.csv
  Jede Aenderung nimmt Felder auch als JSON: --json datei.json (oder - fuer stdin).

Wie geschrieben wird: die geaenderte Fassung wird in einem Wegwerfverzeichnis
mit dem Validator des Projekts geprueft, die bisherige ebenso. Bringt die
Aenderung einen Verstoss, den es vorher nicht gab, wird nicht geschrieben.
Sonst atomar (Temporaerdatei, Rueckleseprobe, os.replace). Der Commit-Hook
bleibt die letzte Instanz.

Diese Datei ist in jedem Projekt dieselbe. Was ein Projekt anders hat (Name
der Evidenzspalte, Vorgaben fuer Altspalten), steht in truth_local.py daneben.
"""
import argparse, contextlib, csv, datetime, importlib, io, json, os, re, shutil
import subprocess, sys, tempfile

HIER = os.path.dirname(os.path.abspath(__file__))


def _wurzel():
    d = HIER
    while True:
        if os.path.exists(os.path.join(d, "research", "TRUTH.csv")):
            return d
        oben = os.path.dirname(d)
        if oben == d:
            raise SystemExit("research/TRUTH.csv nicht gefunden (gesucht ab %s aufwaerts)" % HIER)
        d = oben


ROOT = _wurzel()
P = os.path.join(ROOT, "research", "TRUTH.csv")
ID_MUSTER = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+\b")
PRIOS = ("now", "next", "later", "park")
ORACLES = ("O1", "O2", "O3")

try:
    sys.path.insert(0, HIER)
    import truth_local as _lokal
except ImportError:
    _lokal = None


def _konf(name, vorgabe):
    return getattr(_lokal, name, vorgabe) if _lokal else vorgabe


class Abgelehnt(Exception):
    """Die Aenderung wurde nicht geschrieben. Der Text sagt, warum."""


def heute():
    return datetime.date.today().isoformat()


# ------------------------------------------------------------------ Datei
def lesen():
    with open(P, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise Abgelehnt("%s hat keine Datenzeilen -- git checkout -- research/TRUTH.csv" % P)
    return list(rows[0].keys()), rows


def _csv_schreiben(pfad, cols, rows):
    with open(pfad, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def evidenzspalte(cols):
    s = _konf("EVIDENZ_SPALTE", None)
    if s:
        return s
    for c in ("Evidence", "Evidence_E0"):
        if c in cols:
            return c
    raise Abgelehnt("keine Evidenzspalte gefunden; EVIDENZ_SPALTE in truth_local.py setzen")


def _evidenz(text):
    return _konf("EVIDENZ_FORMAT", "{}").format(text)


# ------------------------------------------------------------------ Validator
def _validator_lauf(pfad):
    """Projekteigenen Validator gegen pfad laufen lassen. Liefert (rc, Ausgabe)."""
    ct = importlib.import_module("check_truth")
    alt_p, alt_cwd = ct.P, os.getcwd()
    puffer = io.StringIO()
    rc = 0
    try:
        os.chdir(ROOT)
        # Die echte Datei mit dem eigenen P des Validators pruefen -- manche Validatoren
        # vergleichen Pfade relativ, und ein absoluter Pfad saehe dort wie eine Kopie aus.
        if os.path.abspath(pfad) != os.path.abspath(P):
            ct.P = pfad
        with contextlib.redirect_stdout(puffer):
            try:
                rc = ct.main() or 0
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else 1
    finally:
        ct.P = alt_p
        os.chdir(alt_cwd)
    return rc, puffer.getvalue()


def _schluessel(ausgabe):
    """Verstoesse als Menge (Kategorie, ID). So zaehlt eine kuerzere Liste nicht als neu."""
    s = set()
    for z in ausgabe.splitlines():
        z = z.strip()
        if z.startswith("FATAL:"):
            s.add(("FATAL", z[6:].strip()[:60]))
        elif z.startswith("VERSTOSS:"):
            text = z[9:].strip()
            kat = re.split(r"[:(]| -- ", text, maxsplit=1)[0].strip()[:60]
            ids = ID_MUSTER.findall(text)
            if ids:
                s.update((kat, i) for i in ids)
            else:
                s.add((kat, None))
    return s


def _diff(alt, neu, cols):
    alt_by = {r["Claim_ID"]: r for r in alt}
    teile = []
    for r in neu:
        a = alt_by.get(r["Claim_ID"])
        if a is None:
            teile.append("NEU %s\n" % r["Claim_ID"] + "".join(
                "  %s: %s\n" % (c, _kurz(r[c])) for c in cols if r[c]))
            continue
        geaendert = [c for c in cols if a[c] != r[c]]
        if geaendert:
            teile.append("GEAENDERT %s\n" % r["Claim_ID"] + "".join(
                "  %s: %s\n    -> %s\n" % (c, _kurz(a[c]), _kurz(r[c])) for c in geaendert))
    return "".join(teile) or "keine Aenderung\n"


def _kurz(s, n=220):
    s = (s or "").replace("\n", " ")
    return s if len(s) <= n else s[:n] + " [... %d Zeichen]" % len(s)


def schreiben(cols, rows, dry=False):
    """Pruefen und atomar schreiben. Gibt den Bericht zurueck oder wirft Abgelehnt."""
    alt_cols, alt = lesen()
    if cols != alt_cols:
        raise Abgelehnt("Spalten wurden veraendert -- das macht dieses Werkzeug nicht")
    if len(rows) < len(alt):
        raise Abgelehnt("Zeilenzahl wuerde sinken (%d -> %d). Zeilen werden nie geloescht, "
                        "nur abgeloest." % (len(alt), len(rows)))
    bericht = _diff(alt, rows, cols)
    tmp = tempfile.mkdtemp(prefix="truth-pruef-")
    try:
        vorher, nachher = os.path.join(tmp, "vorher.csv"), os.path.join(tmp, "nachher.csv")
        shutil.copyfile(P, vorher)
        _csv_schreiben(nachher, cols, rows)
        _, aus_v = _validator_lauf(vorher)
        _, aus_n = _validator_lauf(nachher)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    neu = _schluessel(aus_n) - _schluessel(aus_v)
    if neu:
        zeilen = [z for z in aus_n.splitlines() if "VERSTOSS" in z or "FATAL" in z]
        raise Abgelehnt("NICHT GESCHRIEBEN -- die Aenderung bringt neue Verstoesse:\n  "
                        + "\n  ".join(sorted("%s: %s" % (k, i or "") for k, i in neu))
                        + "\n\nValidator:\n" + "\n".join(zeilen) + "\n\nGeplant war:\n" + bericht)
    rest = {k for k in _schluessel(aus_n) if not k[0].startswith("Kopien")}
    zustand = ("Validator danach sauber" if not rest else
               "Validator danach: %d Verstoss-Eintraege, alle schon vorher vorhanden" % len(rest))
    if dry:
        return "TROCKENLAUF -- nichts geschrieben. %s.\n\n%s" % (zustand, bericht)
    ziel_tmp = P + ".tmp"
    _csv_schreiben(ziel_tmp, cols, rows)
    with open(ziel_tmp, encoding="utf-8", newline="") as fh:
        probe = list(csv.DictReader(fh))
    if len(probe) != len(rows) or list(probe[0].keys()) != cols:
        os.remove(ziel_tmp)
        raise Abgelehnt("Rueckleseprobe fehlgeschlagen, Original unveraendert")
    os.replace(ziel_tmp, P)
    _, aus_echt = _validator_lauf(P)
    status = (aus_echt.strip().splitlines() or ["?"])[0]
    return "GESCHRIEBEN. %s\n%s.\n\n%s" % (status, zustand, bericht)


# ------------------------------------------------------------------ Hilfen
def _zeile(rows, cid):
    for r in rows:
        if r["Claim_ID"] == cid:
            return r
    raise Abgelehnt("keine Zeile %s" % cid)


def _ids(feld):
    return [d.strip() for d in (feld or "").split(";") if d.strip()]


def naechste_id(rows, subsystem):
    zahlen = {}
    for r in rows:
        if r["Subsystem"] == subsystem:
            m = re.match(r"^(.*?)(\d+)$", r["Claim_ID"])
            if m:
                zahlen.setdefault(m.group(1), []).append(m.group(2))
    if not zahlen:
        raise Abgelehnt("noch keine Zeile im Subsystem %s -- erste ID mit --id angeben" % subsystem)
    praefix = max(zahlen, key=lambda p: (len(zahlen[p]), max(int(z) for z in zahlen[p])))
    hoechste = max(zahlen[praefix], key=int)
    return "%s%0*d" % (praefix, len(hoechste), int(hoechste) + 1)


def _setze(r, cols, **felder):
    for k, v in felder.items():
        if k not in cols:
            continue
        r[k] = v


def _abhaengige(rows, ziele):
    """Alle Zeilen, die an einem Ziel haengen -- auch abgeloeste, weil manche Validatoren
    auch deren Depends_On pruefen."""
    return [r for r in rows if r["Claim_ID"] not in ziele and set(_ids(r["Depends_On"])) & ziele]


# ------------------------------------------------------------------ Lesen
def front():
    _, rows = lesen()
    out = []
    for r in rows:
        if r["Decided"] == "no" and r.get("Prio") == "now":
            out.append("%s  [%s/%s]  %s\n  NAECHSTER TEST: %s" % (
                r["Claim_ID"], r.get("Oracle") or "--", r["Confidence"], r["Topic"],
                _kurz(r["Next_Test"], 400)))
    return "\n\n".join(out) or "Front leer -- aus Prio=next nachfuellen."


def finden(offen=None, prio=None, subsystem=None, oracle=None, text=None, limit=50):
    _, rows = lesen()
    rx = re.compile(text, re.I) if text else None
    treffer = []
    for r in rows:
        if offen is True and r["Decided"] != "no":
            continue
        if offen is False and r["Decided"] != "yes":
            continue
        if prio and r.get("Prio") != prio:
            continue
        if subsystem and r["Subsystem"] != subsystem:
            continue
        if oracle and (r.get("Oracle") or "") != oracle:
            continue
        if rx and not rx.search(r["Topic"] + " " + r["Statement"]):
            continue
        treffer.append(r)
    zeilen = ["%-22s %-3s %-5s %-4s %-5s %s" % (
        r["Claim_ID"], "ja" if r["Decided"] == "yes" else "of", r.get("Prio") or "",
        r.get("Oracle") or "--", r["Confidence"],
        ("[abgeloest -> %s] " % r["Superseded_By"] if r["Superseded_By"] else "") + r["Topic"][:70])
        for r in treffer[:limit]]
    kopf = "%d Treffer%s" % (len(treffer), " (erste %d)" % limit if len(treffer) > limit else "")
    return kopf + "\n" + "\n".join(zeilen)


def zeigen(cid, felder=None):
    cols, rows = lesen()
    r = _zeile(rows, cid)
    felder = felder or cols
    return "\n".join("%s: %s" % (c, r.get(c, "(keine Spalte)")) for c in felder)


def abhaengigkeiten(cid):
    _, rows = lesen()
    topf = {r["Claim_ID"]: r for r in rows}
    r = _zeile(rows, cid)
    out = ["%s steht auf:" % cid]
    for d in _ids(r["Depends_On"]) or []:
        x = topf.get(d)
        out.append("  %s %s" % (d, ("[%s/%s, %s%s] %s" % (
            x.get("Oracle") or "--", x["Confidence"], "entschieden" if x["Decided"] == "yes" else "offen",
            ", ABGELOEST -> " + x["Superseded_By"] if x["Superseded_By"] else "", x["Topic"][:60]))
            if x else "(gibt es nicht)"))
    if not _ids(r["Depends_On"]):
        out.append("  nichts")
    kinder = [x for x in rows if cid in _ids(x["Depends_On"])]
    out.append("An %s haengen direkt %d Zeilen:" % (cid, len(kinder)))
    for x in kinder:
        out.append("  %s [%s] %s" % (x["Claim_ID"], "abgeloest" if x["Superseded_By"] else
                                     ("entschieden" if x["Decided"] == "yes" else "offen"), x["Topic"][:60]))
    return "\n".join(out)


def journal(cid):
    aus = subprocess.run(["git", "log", "--date=short", "--format=%ad %h %s", "-F", "--grep=" + cid],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return aus or "keine Commits, die %s nennen" % cid


def pruefen():
    rc, aus = _validator_lauf(P)
    return rc, aus


# ------------------------------------------------------------------ Aendern
def anlegen(subsystem, topic, statement, oracle, confidence, next_test="", prio=None,
            evidence="", depends="", source="", status=None, claim_id=None,
            entschieden=False, dry=False):
    cols, rows = lesen()
    fehlt = [n for n, v in (("subsystem", subsystem), ("topic", topic), ("statement", statement),
                            ("oracle", oracle), ("confidence", confidence)) if v in (None, "")]
    if fehlt:
        raise Abgelehnt("Pflichtangaben fehlen: %s" % ", ".join(fehlt))
    if oracle not in ORACLES:
        raise Abgelehnt("--oracle muss O1, O2 oder O3 sein")
    if not entschieden and not next_test:
        raise Abgelehnt("offene Zeile ohne --next-test: eine Frage ohne Experiment ist ein Thema, "
                        "kein Arbeitspaket (oder --entschieden)")
    cid = claim_id or naechste_id(rows, subsystem)
    if any(r["Claim_ID"] == cid for r in rows):
        raise Abgelehnt("ID %s gibt es schon" % cid)
    r = {c: "" for c in cols}
    _setze(r, cols, **_konf("NEUE_ZEILE", {}))
    ev = evidenzspalte(cols)
    _setze(r, cols, Claim_ID=cid, Subsystem=subsystem, Topic=topic, Statement=statement,
           Oracle=oracle, Confidence=str(confidence), Depends_On=depends,
           Decided="yes" if entschieden else "no",
           Status=status or ("verified" if entschieden else "hypothesis"),
           Next_Test="" if entschieden else next_test,
           Prio="" if entschieden else (prio or "next"),
           Open_Question="NO" if entschieden else "YES",
           Updated=heute(), Source=source or "Sitzung-%s" % heute())
    if evidence:
        r[ev] = _evidenz(evidence)
    rows.append(r)
    return schreiben(cols, rows, dry)


def schliessen(cid, status="verified", oracle=None, confidence=None, evidence=None,
               urteil=None, statement=None, dry=False):
    cols, rows = lesen()
    r = _zeile(rows, cid)
    if r["Superseded_By"]:
        raise Abgelehnt("%s ist abgeloest durch %s" % (cid, r["Superseded_By"]))
    if oracle and oracle not in ORACLES:
        raise Abgelehnt("--oracle muss O1, O2 oder O3 sein")
    if not (oracle or r.get("Oracle")):
        raise Abgelehnt("%s hat keine Pruefstufe -- --oracle angeben" % cid)
    if statement:
        r["Statement"] = statement
    elif urteil:
        rest = re.sub(r"^\s*OFFEN[,.:]?\s*", "", r["Statement"])
        r["Statement"] = "ENTSCHIEDEN %s: %s %s" % (heute(), urteil.strip(), rest)
    else:
        r["Statement"] = re.sub(r"^\s*OFFEN[,.:]?\s*", "", r["Statement"])
    _setze(r, cols, Decided="yes", Status=status, Prio="", Next_Test="", Open_Question="NO",
           Updated=heute())
    if oracle:
        r["Oracle"] = oracle
    if confidence is not None:
        r["Confidence"] = str(confidence)
    if evidence:
        r[evidenzspalte(cols)] = _evidenz(evidence)
    return schreiben(cols, rows, dry)


def abloesen(alt, neu, notiz, umhaengen=(), mitabloesen=(), dry=False):
    """Abloesung mit Durchreichen. Jede lebende Zeile, die an einer abgeloesten haengt,
    muss ausdruecklich umgehaengt oder mit abgeloest werden -- sonst wird nichts geschrieben."""
    cols, rows = lesen()
    topf = {r["Claim_ID"]: r for r in rows}
    if neu not in topf:
        raise Abgelehnt("Nachfolgerin %s gibt es nicht -- erst anlegen" % neu)
    if topf[neu]["Superseded_By"]:
        raise Abgelehnt("Nachfolgerin %s ist selbst abgeloest" % neu)
    for c in [alt] + list(umhaengen) + list(mitabloesen):
        _zeile(rows, c)
    for c in [alt] + list(mitabloesen):
        if topf[c]["Superseded_By"]:
            raise Abgelehnt("%s ist schon abgeloest durch %s" % (c, topf[c]["Superseded_By"]))
    ziele = {alt} | set(mitabloesen)
    entschieden = ziele | set(umhaengen)
    offen = [r for r in _abhaengige(rows, ziele) if r["Claim_ID"] not in entschieden]
    if offen:
        raise Abgelehnt(
            "NICHT GESCHRIEBEN -- an den abzuloesenden Zeilen haengen Zeilen, ueber die nicht "
            "entschieden ist. Jede lesen, dann je ID --umhaengen (ueberlebt, haengt kuenftig an %s) "
            "oder --mitabloesen (faellt mit):\n\n" % neu
            + "\n\n".join("%s [%s] %s\n  haengt an: %s\n  %s" % (
                r["Claim_ID"], "abgeloest, nur --umhaengen" if r["Superseded_By"] else
                ("entschieden" if r["Decided"] == "yes" else "offen"), r["Topic"],
                ";".join(sorted(set(_ids(r["Depends_On"])) & ziele)), _kurz(r["Statement"], 700))
                for r in offen))
    hinweise = []
    for c in ziele:
        r = topf[c]
        if not r.get("Oracle"):
            r["Oracle"] = "O1"
            hinweise.append("%s hatte keine Pruefstufe: O1 gesetzt" % c)
        try:
            if r.get("Oracle") == "O1" and float(r["Confidence"]) > 0.60:
                r["Confidence"] = "0.60"
                hinweise.append("%s: Konfidenz auf den O1-Deckel 0.60" % c)
        except ValueError:
            pass
        r["Statement"] = r["Statement"].rstrip(". ") + ". ABGELOEST %s durch %s: %s" % (heute(), neu, notiz)
        _setze(r, cols, Superseded_By=neu, Decided="yes", Prio="", Next_Test="",
               Open_Question="NO", Updated=heute())
    for c in umhaengen:
        r = topf[c]
        neu_deps = []
        for d in _ids(r["Depends_On"]):
            d = neu if d in ziele else d
            if d not in neu_deps and d != c:
                neu_deps.append(d)
        r["Depends_On"] = ";".join(neu_deps)
        if not r["Superseded_By"]:      # Archivzeilen: nur Buchhaltung, kein neuer Stand
            r["Updated"] = heute()
    bericht = schreiben(cols, rows, dry)
    return ("\n".join(hinweise) + "\n\n" if hinweise else "") + bericht


def setzen(cid, felder, dry=False):
    cols, rows = lesen()
    r = _zeile(rows, cid)
    unbekannt = [k for k in felder if k not in cols]
    if unbekannt:
        raise Abgelehnt("unbekannte Spalten: %s" % unbekannt)
    if "Claim_ID" in felder:
        raise Abgelehnt("Claim_ID wird nicht geaendert -- neue Zeile anlegen und abloesen")
    r.update({k: str(v) for k, v in felder.items()})
    if "Updated" not in felder:
        r["Updated"] = heute()
    return schreiben(cols, rows, dry)


def prio(cid, wert, dry=False):
    if wert not in PRIOS:
        raise Abgelehnt("Prio muss eine von %s sein" % (PRIOS,))
    return setzen(cid, {"Prio": wert}, dry)


def commit(nachricht):
    _, rows = lesen()
    ids = {r["Claim_ID"] for r in rows}
    if not set(ID_MUSTER.findall(nachricht)) & ids:
        raise Abgelehnt("die Commit-Nachricht nennt keine Claim-ID -- der Git-Log ist das Laborjournal")
    rel = os.path.relpath(P, ROOT)
    subprocess.run(["git", "add", rel], cwd=ROOT, check=True, capture_output=True)
    p = subprocess.run(["git", "commit", "-m", nachricht, "--", rel], cwd=ROOT,
                       capture_output=True, text=True)
    if p.returncode:
        raise Abgelehnt("git commit gescheitert:\n" + p.stdout + p.stderr)
    return subprocess.run(["git", "log", "--oneline", "-1"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


# ------------------------------------------------------------------ Kommandozeile
def _json_felder(quelle):
    if not quelle:
        return {}
    text = sys.stdin.read() if quelle == "-" else open(quelle, encoding="utf-8").read()
    d = json.loads(text)
    if not isinstance(d, dict):
        raise Abgelehnt("--json erwartet ein Objekt")
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(prog="truth.py", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("front")
    s = sub.add_parser("find")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--offen", action="store_true")
    g.add_argument("--entschieden", action="store_true")
    s.add_argument("--prio")
    s.add_argument("--subsystem")
    s.add_argument("--oracle")
    s.add_argument("--text")
    s.add_argument("--limit", type=int, default=50)
    s = sub.add_parser("show")
    s.add_argument("id")
    s.add_argument("--felder")
    sub.add_parser("deps").add_argument("id")
    sub.add_parser("journal").add_argument("id")
    sub.add_parser("check")

    def mit_dry(p):
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--json", help="Felder aus JSON-Datei, - fuer stdin")
        return p
    s = mit_dry(sub.add_parser("add"))
    for f in ("subsystem", "topic", "statement", "oracle", "confidence", "next-test", "prio",
              "evidence", "depends", "source", "status", "id"):
        s.add_argument("--" + f)
    s.add_argument("--entschieden", action="store_true")
    s = mit_dry(sub.add_parser("close"))
    s.add_argument("id")
    for f in ("status", "oracle", "confidence", "evidence", "urteil", "statement"):
        s.add_argument("--" + f)
    s = mit_dry(sub.add_parser("supersede"))
    s.add_argument("alt")
    s.add_argument("--by", required=True)
    s.add_argument("--notiz", required=True)
    s.add_argument("--umhaengen", nargs="*", default=[])
    s.add_argument("--mitabloesen", nargs="*", default=[])
    s = mit_dry(sub.add_parser("set"))
    s.add_argument("id")
    s.add_argument("zuweisungen", nargs="*", help="Feld=Wert")
    s = mit_dry(sub.add_parser("prio"))
    s.add_argument("id")
    s.add_argument("wert")
    sub.add_parser("commit").add_argument("nachricht")

    a = ap.parse_args(argv)
    try:
        if a.cmd == "front":
            print(front())
        elif a.cmd == "find":
            print(finden(True if a.offen else (False if a.entschieden else None),
                         a.prio, a.subsystem, a.oracle, a.text, a.limit))
        elif a.cmd == "show":
            print(zeigen(a.id, a.felder.split(",") if a.felder else None))
        elif a.cmd == "deps":
            print(abhaengigkeiten(a.id))
        elif a.cmd == "journal":
            print(journal(a.id))
        elif a.cmd == "check":
            rc, aus = pruefen()
            print(aus.rstrip())
            return rc
        elif a.cmd == "add":
            j = _json_felder(a.json)
            g = lambda k, attr: j.get(k, getattr(a, attr))  # noqa: E731
            print(anlegen(g("subsystem", "subsystem"), g("topic", "topic"), g("statement", "statement"),
                          g("oracle", "oracle"), g("confidence", "confidence"),
                          g("next_test", "next_test") or "", g("prio", "prio"),
                          g("evidence", "evidence") or "",
                          j.get("depends_on", g("depends", "depends")) or "",
                          g("source", "source") or "", g("status", "status"), g("id", "id"),
                          bool(j.get("entschieden", a.entschieden)), a.dry_run))
        elif a.cmd == "close":
            j = _json_felder(a.json)
            g = lambda k: j.get(k, getattr(a, k))  # noqa: E731
            print(schliessen(a.id, g("status") or "verified", g("oracle"), g("confidence"),
                             g("evidence"), g("urteil"), g("statement"), a.dry_run))
        elif a.cmd == "supersede":
            print(abloesen(a.alt, a.by, a.notiz, a.umhaengen, a.mitabloesen, a.dry_run))
        elif a.cmd == "set":
            felder = _json_felder(a.json)
            for z in a.zuweisungen:
                if "=" not in z:
                    raise Abgelehnt("erwartet Feld=Wert, nicht %r" % z)
                k, v = z.split("=", 1)
                felder[k] = v
            print(setzen(a.id, felder, a.dry_run))
        elif a.cmd == "prio":
            print(prio(a.id, a.wert, a.dry_run))
        elif a.cmd == "commit":
            print(commit(a.nachricht))
    except Abgelehnt as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
