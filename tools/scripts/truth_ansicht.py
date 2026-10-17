#!/usr/bin/env python3
"""Die Ansicht des Registers: research/TRUTH.csv als eine HTML-Datei, nur lesend.

    python3 tools/truth_ansicht.py                 schreibt build/truth_ansicht.html
    python3 tools/truth_ansicht.py --oeffnen       ... und oeffnet sie im Browser
    python3 tools/truth_ansicht.py --out _site/index.html \\
            --commit-url 'https://github.com/OWNER/REPO/commit/{hash}'

Warum es das gibt: die CSV ist fuer Menschen unbequem -- lange Zellen,
Claim-IDs, die man einzeln nachschlagen muss, Abhaengigkeiten nur ueber
`truth.py deps`. Die Ansicht macht daraus eine Seite mit Front, einem Graphen
der Abhaengigkeiten, tragenden Zeilen, Registertabelle mit Filtern, Verweisen
in beide Richtungen und dem Laborjournal je Zeile.

Den Graphen ordnet Graphviz an (`dot`, Paket graphviz); er steht als SVG in der
Seite. Fehlt dot, entsteht die Seite trotzdem, nur ohne Graphen und mit einem
Hinweis. Ein anderes dot-Programm: Umgebungsvariable TRUTH_ANSICHT_DOT.

Was sie nicht ist: ein zweiter Stand. Sie fuehrt keinen eigenen Inhalt. Alles
kommt aus TRUTH.csv (ueber truth.lesen()), aus git log und aus dem Validator.
Gleiche Eingabe gibt eine byte-gleiche Datei; es gibt keinen Zeitstempel, der
Kopf nennt den Commit. Geschrieben wird nur die Ausgabedatei, atomar, nie
etwas unter research/.

Erzeugt wird sie nach jedem Commit vom Hook .githooks/post-commit (dazu
post-merge, post-checkout, post-rewrite). Die Oberflaeche ist englisch, weil
sie auch oeffentlich gelesen werden kann, etwa ueber GitHub Pages.

Projektspezifisches (optional, in truth_local.py):
  ANSICHT_TITEL   Seitentitel
  ANSICHT_ORACLE  {"O1": ("kurz", "lang"), ...} -- was die Pruefstufen hier heissen
"""
import argparse, html, importlib, os, re, shutil, subprocess, sys, tempfile, textwrap
import webbrowser

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import truth  # noqa: E402  -- lesen(), _ids(), ID_MUSTER, ROOT, P

REL = os.path.relpath(truth.P, truth.ROOT).replace(os.sep, "/")
AUSGABE = os.path.join(truth.ROOT, "build", "truth_ansicht.html")

ORACLE_VORGABE = {
    "O1": ("derived", "Derived from other rows, documents or plausibility. Nothing was measured."),
    "O2": ("reproducible", "A repeatable command over a file produces the statement."),
    "O3": ("observed", "The subject was observed to behave as the row predicts."),
}
DECKEL_VORGABE = {"O1": 0.60, "O2": 0.95, "O3": 1.00}
PRIO_TEXT = {
    "now": "Working front. Hand-picked, at most six rows.",
    "next": "Queued for the front. Came out of ongoing work.",
    "later": "Backlog. Not wrong, just cold.",
    "park": "About the tooling, not the subject.",
}
STATUS_ART = {"verified": "gut", "supported": "eher", "hypothesis": "vermutet",
              "open": "offen", "refuted": "falsch", "superseded": "alt"}
KERN = ["Claim_ID", "Subsystem", "Topic", "Statement", "Status", "Oracle", "Confidence",
        "Depends_On", "Decided", "Superseded_By", "Next_Test", "Prio", "Updated", "Source"]
LANG = 1400          # ab so vielen Zeichen wird eine Zelle eingeklappt
GV_FUELLUNG = {"O3": "#e3f3e8", "O2": "#e2f1f6", "O1": "#fbf0d9", "": "#f3f1ec"}
URTEIL_KURZ = 220    # Vorschau des Urteils in der Registerzeile


def esc(s):
    return html.escape(s or "", quote=True)


# ------------------------------------------------------------------ Quellen
def git(*args):
    try:
        p = subprocess.run(["git"] + list(args), cwd=truth.ROOT, capture_output=True,
                           text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout if p.returncode == 0 else None


def git_stand():
    kopf = (git("rev-parse", "HEAD") or "").strip()
    return {
        "hash": kopf,
        "datum": (git("log", "-1", "--format=%cd", "--date=short") or "").strip() if kopf else "",
        "schmutzig": bool((git("status", "--porcelain", "--", REL) or "").strip()),
        "flach": (git("rev-parse", "--is-shallow-repository") or "").strip() == "true",
    }


def journale(ids):
    """Je Claim-ID die Commits, deren Nachricht sie nennt -- dieselbe Auswahl wie
    `truth.py journal` (git log -F --grep), nur in einem Lauf statt einem je Zeile."""
    aus = git("log", "--date=short", "--format=%x1e%H%x1f%h%x1f%ad%x1f%s%x1f%B")
    treffer = {cid: [] for cid in ids}
    if aus is None:
        return treffer, False
    for satz in aus.split("\x1e")[1:]:
        teile = satz.split("\x1f", 4)
        if len(teile) < 5:
            continue
        voll, kurz, datum, betreff, nachricht = teile
        for cid in ids:
            if cid in nachricht:
                treffer[cid].append((datum, kurz, voll, betreff))
    return treffer, True


def validator():
    pfad = os.path.join(HIER, "check_truth.py")
    try:
        p = subprocess.run([sys.executable, pfad], cwd=truth.ROOT, capture_output=True,
                           text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return None, str(e)
    return p.returncode, (p.stdout + p.stderr).strip()


def deckel():
    try:
        return dict(importlib.import_module("check_truth").DECKEL)
    except Exception:
        return dict(DECKEL_VORGABE)


def dot_svg(quelle):
    """Graphviz rechnet die Anordnung. Ohne dot gibt es keinen Graphen, aber eine Seite."""
    prog = shutil.which(os.environ.get("TRUTH_ANSICHT_DOT", "dot"))
    if not prog:
        return None, ("Graphviz (dot) is not installed, so the graph is missing. "
                      "Install graphviz and generate the page again.")
    try:
        p = subprocess.run([prog, "-Tsvg"], input=quelle, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "Graphviz failed: %s" % e
    if p.returncode != 0 or "<svg" not in p.stdout:
        return None, "Graphviz failed: %s" % ((p.stderr or "").strip()[:300] or "exit %d" % p.returncode)
    svg = p.stdout[p.stdout.index("<svg"):]
    return re.sub(r"<!--.*?-->\s*", "", svg, flags=re.S).strip(), None


def dot_text(s):
    return (s or "").replace("\\", "\\\\").replace('"', '\\"')


def dot_label(cid, topic):
    zeilen = textwrap.wrap(" ".join((topic or "").split()), 30)
    if len(zeilen) > 3:
        zeilen = zeilen[:3]
        zeilen[2] = zeilen[2][:27].rstrip() + " ..."
    return "\\n".join(dot_text(z) for z in [cid] + zeilen)


# ------------------------------------------------------------------ Modell
class Register:
    def __init__(self, cols, rows):
        self.cols, self.rows = cols, rows
        self.topf = {r["Claim_ID"]: r for r in rows}
        self.ids = [r["Claim_ID"] for r in rows]
        self.oben = {c: truth._ids(self.topf[c].get("Depends_On")) for c in self.ids}
        self.unten = {c: [] for c in self.ids}
        for c in self.ids:
            for d in self.oben[c]:
                if d in self.unten:
                    self.unten[d].append(c)
        self.loest_ab = {c: [] for c in self.ids}
        for c in self.ids:
            n = (self.topf[c].get("Superseded_By") or "").strip()
            if n in self.loest_ab:
                self.loest_ab[n].append(c)

    def huelle(self, cid, kanten):
        seen, stack = set(), list(kanten.get(cid, ()))
        while stack:
            x = stack.pop()
            if x in seen or x == cid:
                continue
            seen.add(x)
            stack += [y for y in kanten.get(x, ()) if y in self.topf]
        return seen

    def abgeloest(self, cid):
        return bool((self.topf[cid].get("Superseded_By") or "").strip())

    def offen(self, cid):
        return self.topf[cid].get("Decided") == "no"


class Seite:
    def __init__(self, reg, journal, git_ok, stand, val, commit_url, titel, oracle, deckel_):
        self.reg, self.journal, self.git_ok = reg, journal, git_ok
        self.stand, self.val, self.commit_url = stand, val, commit_url
        self.titel, self.oracle, self.deckel = titel, oracle, deckel_
        try:
            self.evidenz = truth.evidenzspalte(reg.cols)
        except truth.Abgelehnt:
            self.evidenz = None
        self.pos = {c: i for i, c in enumerate(reg.ids)}
        self.n_oben = {c: len(reg.huelle(c, reg.oben)) for c in reg.ids}
        self.n_unten = {c: len(reg.huelle(c, reg.unten)) for c in reg.ids}
        self.graphen, self.graph_fehler, self.im_graph = self.graphen_bauen()

    # -------------------------------------------------------------- Bausteine
    def tooltip(self, cid):
        r = self.reg.topf[cid]
        teile = [r.get("Topic", ""), r.get("Status", "") or "-"]
        teile.append(r.get("Oracle") or "no check level")
        teile.append("c=" + (r.get("Confidence") or "?"))
        teile.append("open" if self.reg.offen(cid) else "decided")
        if self.reg.abgeloest(cid):
            teile.append("superseded by " + r["Superseded_By"])
        return " | ".join(teile)

    def link(self, cid, text=None):
        if cid not in self.reg.topf:
            return '<span class="fremd" title="not in the register">%s</span>' % esc(text or cid)
        cls = "id alt" if self.reg.abgeloest(cid) else "id"
        return '<a class="%s" href="#%s" title="%s">%s</a>' % (cls, esc(cid), esc(self.tooltip(cid)),
                                                              esc(text or cid))

    def verlinken(self, text):
        teile, pos = [], 0
        for m in truth.ID_MUSTER.finditer(text or ""):
            if m.group(0) not in self.reg.topf:
                continue
            teile.append(esc(text[pos:m.start()]))
            teile.append(self.link(m.group(0)))
            pos = m.end()
        teile.append(esc((text or "")[pos:]))
        return "".join(teile)

    def textblock(self, text):
        n = len(text or "")
        if n <= LANG:
            return '<div class="text">%s</div>' % self.verlinken(text)
        return ('<div class="text lang">%s</div><button type="button" class="mehr" '
                'data-n="%d">Show all %d characters</button>' % (self.verlinken(text), n, n))

    def chip_status(self, r):
        s = r.get("Status") or "-"
        if self.reg.abgeloest(r["Claim_ID"]):
            s = "superseded"
        return '<span class="chip st-%s">%s</span>' % (STATUS_ART.get(s, "anders"), esc(s))

    def chip_oracle(self, r, lang=False):
        o = (r.get("Oracle") or "").strip()
        if o in self.oracle:
            kurz, erkl = self.oracle[o]
            cap = self.deckel.get(o)
            titel = "%s: %s%s" % (o, erkl, " Confidence capped at %.2f." % cap if cap is not None else "")
            text = "%s %s" % (o, kurz)
            if lang and cap is not None:
                text += " (cap %.2f)" % cap
            return '<span class="chip or-%s" title="%s">%s</span>' % (o.lower(), esc(titel), esc(text))
        if o:
            return '<span class="chip or-x">%s</span>' % esc(o)
        return ('<span class="chip or-x" title="Older row without a check level.">'
                'not stated</span>')

    def chip_prio(self, r):
        p = r.get("Prio") or ""
        if not p:
            return ""
        return '<span class="chip pr-%s" title="%s">%s</span>' % (esc(p), esc(PRIO_TEXT.get(p, "")), esc(p))

    def schwach(self, cid):
        """Was an einem Glied der Kette schwach ist: ungeprueft, offen, abgeloest."""
        r = self.reg.topf[cid]
        grund = []
        o = (r.get("Oracle") or "").strip()
        if o not in ("O2", "O3"):
            grund.append(self.oracle[o][0] if o in self.oracle else "no check level")
        if self.reg.offen(cid):
            grund.append("open")
        if self.reg.abgeloest(cid):
            grund.append("superseded")
        if (r.get("Status") or "") == "refuted":
            grund.append("refuted")
        return grund

    def zeile_kurz(self, cid, extra=""):
        r = self.reg.topf[cid]
        cls = ' class="alt"' if self.reg.abgeloest(cid) else ""
        return '<li%s>%s %s %s <span class="topic">%s</span>%s</li>' % (
            cls, self.link(cid), self.chip_status(r), self.chip_oracle(r),
            esc(r.get("Topic", "")), extra)

    # -------------------------------------------------------------- Kopf
    def kopf(self):
        reg, st = self.reg, self.stand
        lebend = [c for c in reg.ids if not reg.abgeloest(c)]
        offen = [c for c in lebend if reg.offen(c)]
        prio = {p: sum(1 for c in offen if reg.topf[c].get("Prio") == p) for p in truth.PRIOS}
        if st["hash"]:
            k = st["hash"][:7]
            if self.commit_url:
                k = '<a href="%s"><code>%s</code></a>' % (esc(self.commit_url.format(hash=st["hash"])), k)
            else:
                k = '<code title="%s">%s</code>' % (esc(st["hash"]), k)
            stand = "at commit %s (%s)" % (k, esc(st["datum"]))
        else:
            stand = "outside a git repository"
        warn = []
        if st["schmutzig"]:
            warn.append("<code>%s</code> has uncommitted changes. This view shows the working copy, "
                        "not the commit." % esc(REL))
        if st["flach"]:
            warn.append("Shallow clone: the lab journals are incomplete.")
        if not self.git_ok:
            warn.append("No git history available: the lab journals are empty.")
        rc, aus = self.val
        if rc == 0:
            v = '<span class="chip st-gut">Validator: clean</span>'
        elif rc is None:
            v = '<span class="chip st-falsch">Validator did not run</span>'
        else:
            n = sum(1 for z in aus.splitlines() if "VERSTOSS" in z or "FATAL" in z)
            v = '<span class="chip st-falsch">Validator: %s</span>' % (
                "%d violation%s" % (n, "" if n == 1 else "s") if n else "failed (exit %d)" % rc)
        v += '<details class="vout"><summary>output</summary><pre>%s</pre></details>' % esc(aus)
        zahlen = [
            ("rows", len(reg.ids)), ("live", len(lebend)), ("decided", len(lebend) - len(offen)),
            ("open", len(offen)), ("superseded", len(reg.ids) - len(lebend)),
        ]
        kacheln = "".join('<div class="kachel"><b>%d</b><span>%s</span></div>' % (n, t) for t, n in zahlen)
        kacheln += '<div class="kachel prio"><span>open by priority</span><div>%s</div></div>' % " ".join(
            '<span class="chip pr-%s" title="%s">%s %d</span>' % (p, esc(PRIO_TEXT[p]), p, prio[p])
            for p in truth.PRIOS)
        return """<header class="kopf">
<h1>%s</h1>
<p class="stand">Generated from <code>%s</code> %s. A read-only view: the CSV is the only authority,
this page adds nothing of its own.</p>
%s
<div class="kacheln">%s</div>
<div class="val">%s</div>
<nav><a href="#front">Front</a><a href="#graph">Graph</a><a href="#tragend">Load-bearing</a><a href="#register">Register</a>
<a href="#legende">Legend</a></nav>
</header>""" % (esc(self.titel), esc(REL), stand,
                "".join('<p class="warn">%s</p>' % w for w in warn), kacheln, v)

    # -------------------------------------------------------------- Front
    def baum(self, cid, gesehen, tiefe=0):
        teile = []
        for d in self.reg.oben.get(cid, []):
            if d not in self.reg.topf:
                teile.append('<li>%s <span class="fremd">(not in the register)</span></li>' % esc(d))
                continue
            r = self.reg.topf[d]
            w = self.schwach(d)
            cls = "schwach" if w else ""
            marke = ' <span class="grund">%s</span>' % esc(", ".join(w)) if w else ""
            kopf = "%s %s %s <span class=\"topic\">%s</span>%s" % (
                self.link(d), self.chip_status(r), self.chip_oracle(r), esc(r.get("Topic", "")), marke)
            if d in gesehen:
                teile.append('<li class="%s">%s <span class="schon">listed above</span></li>' % (cls, kopf))
                continue
            gesehen.add(d)
            unter = self.baum(d, gesehen, tiefe + 1) if self.reg.oben.get(d) else ""
            if unter:
                teile.append('<li class="%s"><details%s><summary>%s</summary>%s</details></li>'
                             % (cls, " open" if tiefe == 0 else "", kopf, unter))
            else:
                teile.append('<li class="%s">%s</li>' % (cls, kopf))
        return "<ul>%s</ul>" % "".join(teile) if teile else ""

    def karte(self, cid):
        r = self.reg.topf[cid]
        alle = self.reg.huelle(cid, self.reg.oben)
        schwache = sorted(c for c in alle if self.schwach(c))
        nt = r.get("Next_Test") or ""
        stamm = ""
        if alle:
            stamm = ('<details class="stamm"><summary>Stands on %d row%s through Depends_On '
                     '(%d direct)%s</summary>%s</details>') % (
                len(alle), "" if len(alle) == 1 else "s", len(self.reg.oben[cid]),
                ", %d weak link%s" % (len(schwache), "" if len(schwache) == 1 else "s") if schwache else
                ", no weak links", self.baum(cid, set()))
            if schwache:
                stamm += '<p class="schwachliste">Weak links: %s</p>' % ", ".join(
                    "%s <span class=\"grund\">%s</span>" % (self.link(c), esc(", ".join(self.schwach(c))))
                    for c in schwache)
        else:
            stamm = '<p class="leer">Stands on no other row.</p>'
        return """<article class="karte">
<div class="kk">%s %s %s %s <span class="chip">c=%s</span> <span class="chip sub">%s</span></div>
<h3>%s</h3>
<h4>Statement</h4>%s
<h4>Next test</h4>%s
%s
</article>""" % (self.link(cid), self.chip_prio(r), self.chip_status(r), self.chip_oracle(r, True),
                 esc(r.get("Confidence")), esc(r.get("Subsystem")), esc(r.get("Topic")),
                 self.textblock(r.get("Statement")),
                 self.textblock(nt) if nt else '<p class="leer">none</p>', stamm)

    def front(self):
        reg = self.reg
        front = [c for c in reg.ids if reg.offen(c) and reg.topf[c].get("Prio") == "now"
                 and not reg.abgeloest(c)]
        nach = [c for c in reg.ids if reg.offen(c) and reg.topf[c].get("Prio") == "next"
                and not reg.abgeloest(c)]
        karten = "".join(self.karte(c) for c in front) or \
            '<p class="leer">The front is empty. Refill it from Prio = next.</p>'
        liste = "".join(self.zeile_kurz(c) for c in nach) or '<li class="leer">none</li>'
        return """<section id="front">
<h2>Front <small>Prio = now: what the work is on. Below each row: what it stands on, through
Depends_On. A weak link is one that was never checked by a file command or on the subject (O1 or no
check level), is still open, or was refuted.</small></h2>
<div class="karten">%s</div>
<h3>Queued <small>Prio = next, %d rows</small></h3>
<ul class="kurz">%s</ul>
</section>""" % (karten, len(nach), liste)

    # -------------------------------------------------------------- Graph
    def graph_ansichten(self):
        """Drei Ausschnitte, jeder fuer sich angeordnet: Front, offene Fragen, alles.
        Abgeloeste Zeilen und Zeilen ohne jede Kante kommen nicht vor."""
        reg = self.reg
        lebend = [c for c in reg.ids if not reg.abgeloest(c)]
        lset = set(lebend)
        kanten = [(d, c) for c in lebend for d in reg.oben[c] if d in lset]   # d traegt c
        mit_kante = {x for k in kanten for x in k}

        def mit_unterbau(start):
            menge, stack = set(start), list(start)
            while stack:
                for d in reg.oben.get(stack.pop(), []):
                    if d in lset and d not in menge:
                        menge.add(d)
                        stack.append(d)
            return menge
        front = [c for c in lebend if reg.offen(c) and reg.topf[c].get("Prio") == "now"]
        offen = [c for c in lebend if reg.offen(c)]
        offen_k = [c for c in offen if c in mit_kante]
        return kanten, [
            ("front", "Front", mit_unterbau(front),
             "The front (Prio = now) and everything it stands on."),
            ("offen", "Open questions", mit_unterbau(offen_k),
             "Every open row with a dependency, and everything those stand on. %d open row%s "
             "without any Depends_On link %s not shown." % (
                 len(offen) - len(offen_k), "" if len(offen) - len(offen_k) == 1 else "s",
                 "is" if len(offen) - len(offen_k) == 1 else "are")),
            ("alle", "Everything", mit_kante,
             "Every live row with at least one dependency. %d live row%s without any link %s not shown."
             % (len(lebend) - len(mit_kante), "" if len(lebend) - len(mit_kante) == 1 else "s",
                "is" if len(lebend) - len(mit_kante) == 1 else "are")),
        ]

    def dot_quelle(self, name, menge, kanten):
        reg = self.reg
        z = ['digraph "%s" {' % name,
             'graph [id="gv-%s", rankdir=BT, nodesep=0.22, ranksep=0.42, bgcolor="transparent", '
             'fontname="Helvetica"];' % name,
             'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, '
             'margin="0.10,0.05", color="#9aa0a6", fontcolor="#1f2328"];',
             'edge [arrowsize=0.6, color="#8a8f98"];']
        for c in reg.ids:                     # Registerreihenfolge: gleiche Eingabe, gleiches Bild
            if c not in menge:
                continue
            r = reg.topf[c]
            o = (r.get("Oracle") or "").strip()
            o = o if o in GV_FUELLUNG else ""
            kl = ["k", o.lower() if o else "ox"]
            rand = ""
            if reg.offen(c):
                kl.append("offen")
                if r.get("Prio") in ("now", "next"):
                    kl.append("p-" + r["Prio"])
                    rand = ', color="%s", penwidth=%s' % (
                        ("#b42318", "2.4") if r["Prio"] == "now" else ("#5a4fb3", "1.6"))
            schwach = bool(self.schwach(c))
            if schwach:
                kl.append("schwach")
            z.append('"%s" [id="gv-%s-%s", class="%s", style="%s", fillcolor="%s", label="%s"%s];' % (
                c, name, c, " ".join(kl), "rounded,filled,dashed" if schwach else "rounded,filled",
                GV_FUELLUNG[o], dot_label(c, r.get("Topic")), rand))
        i = 0
        for d, c in kanten:
            if d in menge and c in menge:
                z.append('"%s" -> "%s" [id="gv-%s-e%d"];' % (d, c, name, i))
                i += 1
        z.append("}")
        return "\n".join(z) + "\n"

    def graphen_bauen(self):
        kanten, ansichten = self.graph_ansichten()
        graphen, im_graph = [], set()
        for name, titel, menge, text in ansichten:
            if not menge:
                graphen.append((name, titel, 0, text, None))
                continue
            svg, fehler = dot_svg(self.dot_quelle(name, menge, kanten))
            if fehler:
                return [], fehler, set()
            graphen.append((name, titel, len(menge), text, svg))
            if name == "alle":
                im_graph = set(menge)
        return graphen, None, im_graph

    def graph(self):
        kopf = """<section id="graph">
<h2>Graph <small>Who stands on whom, through Depends_On. An arrow points from what a row stands on to
the row, so the foundations are at the bottom and the open questions near the top. Click a box to
light up everything it stands on and everything that stands on it; drag to move around.</small></h2>"""
        if self.graph_fehler:
            return kopf + '<p class="warn">%s</p></section>' % esc(self.graph_fehler)
        tabs = "".join('<button type="button" class="gv-tab" data-v="%s" aria-pressed="%s">%s <small>%d</small></button>'
                       % (n, "true" if i == 0 else "false", esc(t), k)
                       for i, (n, t, k, _, _) in enumerate(self.graphen))
        hinweise = "".join('<p class="gv-hinweis" data-v="%s"%s>%s</p>' % (n, "" if i == 0 else " hidden", esc(x))
                           for i, (n, _, _, x, _) in enumerate(self.graphen))
        boxen = "".join('<div class="gv" data-v="%s"%s>%s</div>' % (
            n, "" if i == 0 else " hidden", svg or '<p class="leer">No rows in this view.</p>')
            for i, (n, _, _, _, svg) in enumerate(self.graphen))
        muster = "".join('<span class="gv-muster %s">%s</span>' % (k, t) for k, t in (
            ("o3", "O3 " + esc(self.oracle["O3"][0])), ("o2", "O2 " + esc(self.oracle["O2"][0])),
            ("o1", "O1 " + esc(self.oracle["O1"][0])), ("ox", "no check level"),
            ("p-now", "front (now)"), ("p-next", "queued (next)"),
            ("schwach", "weak link: derived, no check level, open or refuted")))
        return """%s
<div class="gv-leiste">%s<span class="gv-zoom"><button type="button" data-z="-" aria-label="Zoom out">&minus;</button><button type="button" data-z="+" aria-label="Zoom in">+</button><button type="button" data-z="fit">Fit</button><button type="button" data-z="1">100%%</button></span></div>
%s
<div class="gv-info" id="gv-info"><span class="leer">Click a box to light up its chain.</span></div>
%s
<p class="gv-legende">%s</p>
</section>""" % (kopf, tabs, hinweise, boxen, muster)

    # -------------------------------------------------------------- Tragend
    def tragend(self):
        reg = self.reg
        traeger = [c for c in reg.ids if reg.unten[c]]
        meist = sorted(traeger, key=lambda c: (-len(reg.unten[c]), -self.n_unten[c], self.pos[c]))[:12]
        ungeprueft = [c for c in traeger if (reg.topf[c].get("Oracle") or "").strip() not in ("O2", "O3")]
        ungeprueft.sort(key=lambda c: (-self.n_unten[c], self.pos[c]))

        def li(c):
            return self.zeile_kurz(c, ' <span class="zahl">%d direct, %d in total</span>'
                                   % (len(reg.unten[c]), self.n_unten[c]))
        return """<section id="tragend">
<h2>Load-bearing <small>Rows that others stand on. If one of them is wrong, everything above it
falls with it.</small></h2>
<div class="zwei">
<div><h3>Most depended on</h3><ul class="kurz">%s</ul></div>
<div><h3>Load-bearing, never checked directly <small>not O2 or O3, %d rows. A file or subject check at
the top row covers the most rows above it.</small></h3><ul class="kurz">%s</ul></div>
</div>
</section>""" % ("".join(li(c) for c in meist) or '<li class="leer">none</li>', len(ungeprueft),
                 "".join(li(c) for c in ungeprueft) or '<li class="leer">none</li>')

    # -------------------------------------------------------------- Register
    def detail(self, cid):
        reg, r = self.reg, self.reg.topf[cid]
        teile = []
        if reg.abgeloest(cid):
            teile.append('<p class="abgeloest">Superseded by %s. This row is kept for the record '
                         'and no longer holds.</p>' % self.link(r["Superseded_By"].strip()))
        if reg.loest_ab[cid]:
            teile.append('<p class="loest">Supersedes %s.</p>' % ", ".join(self.link(c) for c in reg.loest_ab[cid]))
        felder = [("Status", self.chip_status(r)), ("Decided", esc(r.get("Decided"))),
                  ("Check level", self.chip_oracle(r, True)), ("Confidence", esc(r.get("Confidence"))),
                  ("Prio", self.chip_prio(r) or "-"), ("Updated", esc(r.get("Updated"))),
                  ("Subsystem", esc(r.get("Subsystem"))), ("Source", esc(r.get("Source")))]
        teile.append('<dl class="felder">%s</dl>' % "".join(
            "<div><dt>%s</dt><dd>%s</dd></div>" % (k, v) for k, v in felder))
        teile.append("<h4>Statement</h4>" + self.textblock(r.get("Statement")))
        ev = (r.get(self.evidenz) or "").strip() if self.evidenz else ""
        if ev not in ("", "0"):
            teile.append("<h4>Evidence <small>%s</small></h4>" % esc(self.evidenz) + self.textblock(ev))
        if (r.get("Next_Test") or "").strip():
            teile.append("<h4>Next test</h4>" + self.textblock(r.get("Next_Test")))
        ob, un = reg.oben[cid], reg.unten[cid]
        if cid in self.im_graph:
            teile.append('<button type="button" class="imgraph" data-id="%s">Show in graph</button>' % esc(cid))
        teile.append("""<div class="bez">
<div><h4>Stands on <small>%d direct, %d in total</small></h4><ul class="kurz">%s</ul></div>
<div><h4>Depended on by <small>%d direct, %d in total</small></h4><ul class="kurz">%s</ul></div>
</div>""" % (len(ob), self.n_oben[cid],
             "".join(self.zeile_kurz(d) if d in reg.topf else
                     '<li><span class="fremd">%s (not in the register)</span></li>' % esc(d) for d in ob)
             or '<li class="leer">nothing</li>',
             len(un), self.n_unten[cid], "".join(self.zeile_kurz(d) for d in un) or '<li class="leer">nothing</li>'))
        weitere = [(c, r.get(c, "")) for c in reg.cols if c not in KERN and c != self.evidenz
                   and (r.get(c) or "").strip() not in ("", "0")]
        if weitere:
            teile.append('<details class="weitere"><summary>Other fields (%d)</summary><dl>%s</dl></details>'
                         % (len(weitere), "".join('<dt>%s</dt><dd class="text">%s</dd>' % (esc(k), self.verlinken(v))
                                                  for k, v in weitere)))
        j = self.journal.get(cid, [])
        if j:
            def hashlink(voll, kurz):
                if self.commit_url:
                    return '<a href="%s"><code>%s</code></a>' % (esc(self.commit_url.format(hash=voll)), esc(kurz))
                return '<code title="%s">%s</code>' % (esc(voll), esc(kurz))
            teile.append('<h4>Lab journal <small>%d commit%s naming %s, newest first</small></h4>'
                         '<ol class="journal">%s</ol>' % (
                             len(j), "" if len(j) == 1 else "s", esc(cid), "".join(
                                 '<li data-hash="%s"><time>%s</time> %s <span>%s</span></li>'
                                 % (esc(k), esc(d), hashlink(v, k), self.verlinken(s)) for d, k, v, s in j)))
        else:
            teile.append('<h4>Lab journal</h4><p class="leer">No commit names %s.</p>' % esc(cid))
        return "\n".join(teile)

    def zeile(self, i, cid):
        reg, r = self.reg, self.reg.topf[cid]
        st = (r.get("Statement") or "").replace("\n", " ")
        if len(st) > URTEIL_KURZ:
            st = st[:URTEIL_KURZ].rsplit(" ", 1)[0] + " ..."
        attr = {
            "id": cid, "data-i": str(i), "data-sub": r.get("Subsystem", ""),
            "data-prio": r.get("Prio", "") or "-", "data-offen": "1" if reg.offen(cid) else "0",
            "data-oracle": (r.get("Oracle") or "").strip() or "-",
            "data-alt": "1" if reg.abgeloest(cid) else "0", "data-updated": r.get("Updated", ""),
            "data-c": r.get("Confidence", ""), "data-n": str(self.n_unten[cid]),
            "data-oben": " ".join(reg.oben[cid]), "data-unten": " ".join(reg.unten[cid]),
        }
        return """<details class="zeile%s" %s>
<summary><span class="c-id">%s</span><span class="c-sub">%s</span><span class="c-topic"><b>%s</b><i>%s</i></span><span class="c-st">%s</span><span class="c-or">%s</span><span class="c-c">%s</span><span class="c-pr">%s</span><span class="c-up">%s</span></summary>
<div class="detail">
%s
</div>
</details>""" % (" alt" if reg.abgeloest(cid) else "",
                 " ".join('%s="%s"' % (k, esc(v)) for k, v in attr.items()),
                 esc(cid), esc(r.get("Subsystem")), esc(r.get("Topic")), esc(st),
                 self.chip_status(r), self.chip_oracle(r), esc(r.get("Confidence")),
                 self.chip_prio(r), esc(r.get("Updated")), self.detail(cid))

    def register(self):
        reg = self.reg
        subs = sorted({reg.topf[c].get("Subsystem", "") for c in reg.ids})
        n_sub = {s: sum(1 for c in reg.ids if reg.topf[c].get("Subsystem") == s and not reg.abgeloest(c))
                 for s in subs}
        n_alt = sum(1 for c in reg.ids if reg.abgeloest(c))
        opt_sub = "".join('<option value="%s">%s (%d)</option>' % (esc(s), esc(s), n_sub[s]) for s in subs)
        opt_or = "".join('<option value="%s">%s %s</option>' % (o, o, esc(self.oracle[o][0]))
                         for o in sorted(self.oracle))
        return """<section id="register">
<h2>Register <small>Click a row to open it. Every ID is a link; hover it for its title.</small></h2>
<form class="filter" onsubmit="return false">
<input type="search" id="f-q" placeholder="Search ID, title, text ...  ( / )" aria-label="Search">
<select id="f-sub" aria-label="Subsystem"><option value="">All subsystems</option>%s</select>
<select id="f-offen" aria-label="State"><option value="">Open and decided</option><option value="1">Open</option><option value="0">Decided</option></select>
<select id="f-prio" aria-label="Priority"><option value="">Any priority</option><option>now</option><option>next</option><option>later</option><option>park</option><option value="-">none</option></select>
<select id="f-or" aria-label="Check level"><option value="">Any check level</option>%s<option value="-">not stated</option></select>
<select id="f-sort" aria-label="Sort"><option value="">Register order</option><option value="id">ID</option><option value="up">Recently updated</option><option value="c">Confidence, lowest first</option><option value="n">Most depended on</option></select>
<label><input type="checkbox" id="f-alt"> superseded (%d)</label>
<button type="button" id="f-reset">Reset</button>
<output id="f-n"></output>
</form>
<div class="liste" id="liste">
<div class="kz"><span>ID</span><span>Subsystem</span><span>Title and verdict</span><span>Status</span><span>Check</span><span>c</span><span>Prio</span><span>Updated</span></div>
%s
</div>
</section>""" % (opt_sub, opt_or, n_alt, "\n".join(self.zeile(i, c) for i, c in enumerate(reg.ids)))

    def legende(self):
        orr = "".join("<dt>%s</dt><dd>%s</dd>" % (self.chip_oracle({"Oracle": o, "Claim_ID": ""}, True),
                                                 esc(self.oracle[o][1])) for o in sorted(self.oracle))
        orr += "<dt>%s</dt><dd>Older row without a check level.</dd>" % self.chip_oracle({"Oracle": "", "Claim_ID": ""})
        pr = "".join('<dt><span class="chip pr-%s">%s</span></dt><dd>%s</dd>' % (p, p, esc(PRIO_TEXT[p]))
                     for p in truth.PRIOS)
        return """<section id="legende">
<h2>Legend</h2>
<div class="zwei">
<div><h3>Check level <small>what checked the statement; it caps the confidence</small></h3><dl class="leg">%s</dl></div>
<div><h3>Priority <small>open rows only</small></h3><dl class="leg">%s</dl></div>
</div>
<p class="fuss">Generated by <code>tools/truth_ansicht.py</code> from <code>%s</code>, <code>git log</code>
and the register validator. Same input, same file.</p>
</section>""" % (orr, pr, esc(REL))

    def html(self):
        return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="truth_ansicht.py">
<title>%s</title>
<style>%s</style>
<noscript><style>.text.lang{max-height:none;-webkit-mask-image:none;mask-image:none}.mehr,.filter,.gv-zoom,.imgraph{display:none}</style></noscript>
</head>
<body>
%s
<main>
%s
%s
%s
%s
%s
</main>
<script>%s</script>
</body>
</html>
""" % (esc(self.titel), CSS, self.kopf(), self.front(), self.graph(), self.tragend(), self.register(),
       self.legende(), JS)


CSS = r"""
:root{--bg:#fbfaf7;--fl:#ffffff;--fl2:#f3f1ec;--tx:#1f2328;--tx2:#5b6169;--rand:#e1ddd3;--akz:#2456b8;
--gut:#1d7a46;--gut-b:#e3f3e8;--eher:#1f6f8b;--eher-b:#e2f1f6;--verm:#94620b;--verm-b:#fbf0d9;
--falsch:#b42318;--falsch-b:#fde8e6;--alt:#7a7f87;--alt-b:#eeeeee;--offen:#5a4fb3;--offen-b:#ecebfa;
--now:#b42318;--now-b:#fde8e6;--mark:#fff3c4}
@media (prefers-color-scheme:dark){:root{--bg:#15171a;--fl:#1d2024;--fl2:#24282d;--tx:#e6e3dc;--tx2:#a2a8b0;
--rand:#33383e;--akz:#7fa7ff;--gut:#6fd39b;--gut-b:#183325;--eher:#7cc7e2;--eher-b:#16303a;--verm:#e9b55a;
--verm-b:#3a2c12;--falsch:#ff8a80;--falsch-b:#3d1c1a;--alt:#8d939b;--alt-b:#2a2d31;--offen:#b3abff;
--offen-b:#2b2846;--now:#ff8a80;--now-b:#3d1c1a;--mark:#4a3f12}}
*{box-sizing:border-box}
html{scroll-padding-top:12px}
body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main,.kopf{max-width:1240px;margin:0 auto;padding:0 16px}
code,.c-id,.id,pre{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.88em}
a{color:var(--akz)}
h1{font-size:1.6rem;margin:24px 0 4px}
h2{font-size:1.25rem;margin:40px 0 12px;padding-top:8px;border-top:1px solid var(--rand)}
h3{font-size:1.05rem;margin:18px 0 8px}
h4{font-size:.8rem;text-transform:uppercase;letter-spacing:.04em;color:var(--tx2);margin:16px 0 6px}
small{font-weight:400;color:var(--tx2);font-size:.82rem;text-transform:none;letter-spacing:0}
h2 small,h3 small{display:block;margin-top:2px;max-width:80ch}
.stand{color:var(--tx2);margin:0 0 10px;max-width:90ch}
.warn{background:var(--verm-b);color:var(--verm);padding:6px 10px;border-radius:6px;margin:6px 0}
.kacheln{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
.kachel{background:var(--fl);border:1px solid var(--rand);border-radius:8px;padding:8px 12px;display:flex;flex-direction:column;min-width:84px}
.kachel b{font-size:1.3rem;font-variant-numeric:tabular-nums}
.kachel span{color:var(--tx2);font-size:.8rem}
.kachel.prio div{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px}
.val{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.vout summary{cursor:pointer;color:var(--tx2);font-size:.85rem}
.vout pre{white-space:pre-wrap;background:var(--fl2);padding:8px;border-radius:6px;max-height:20em;overflow:auto}
nav{display:flex;gap:16px;margin:14px 0 0;padding:8px 0;flex-wrap:wrap}
.chip{display:inline-block;padding:0 7px;border-radius:999px;font-size:.78rem;line-height:1.6;white-space:nowrap;background:var(--fl2);color:var(--tx2);border:1px solid transparent;vertical-align:baseline}
.st-gut{background:var(--gut-b);color:var(--gut)}.st-eher{background:var(--eher-b);color:var(--eher)}
.st-vermutet{background:var(--verm-b);color:var(--verm)}.st-offen{background:var(--offen-b);color:var(--offen)}
.st-falsch{background:var(--falsch-b);color:var(--falsch)}.st-alt{background:var(--alt-b);color:var(--alt)}
.or-o3{background:var(--gut-b);color:var(--gut)}.or-o2{background:var(--eher-b);color:var(--eher)}
.or-o1{background:var(--verm-b);color:var(--verm)}.or-x{border-color:var(--rand);background:none}
.pr-now{background:var(--now-b);color:var(--now);font-weight:600}.pr-next{background:var(--offen-b);color:var(--offen)}
.pr-later,.pr-park{border-color:var(--rand);background:none}.pr-park{border-style:dashed}
.sub{border-color:var(--rand);background:none}
.text{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100ch}
.text.lang{max-height:18em;overflow:hidden;-webkit-mask-image:linear-gradient(#000 70%,transparent);mask-image:linear-gradient(#000 70%,transparent)}
.text.lang.auf{max-height:none;-webkit-mask-image:none;mask-image:none}
.mehr{margin:4px 0;font:inherit;font-size:.85rem;color:var(--akz);background:none;border:1px solid var(--rand);border-radius:6px;padding:2px 10px;cursor:pointer}
.leer{color:var(--tx2);font-style:italic}
.fremd{color:var(--tx2);text-decoration:line-through dotted}
.karten{display:grid;gap:14px}
.karte{background:var(--fl);border:1px solid var(--rand);border-left:4px solid var(--now);border-radius:8px;padding:12px 16px}
.karte h3{margin:6px 0 0}
.kk{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.stamm{margin-top:12px}
.stamm>summary{cursor:pointer;font-weight:600}
.stamm ul{list-style:none;margin:4px 0 4px 6px;padding-left:14px;border-left:1px solid var(--rand)}
.stamm li{margin:3px 0}
.stamm li>details>summary{cursor:pointer}
.schwach>.id,.schwach>details>summary>.id{background:var(--mark);border-radius:3px}
.grund{color:var(--verm);font-size:.8rem}
.schon{color:var(--tx2);font-size:.8rem;font-style:italic}
.schwachliste{font-size:.9rem}
ul.kurz{list-style:none;padding:0;margin:0}
ul.kurz li{padding:3px 0;border-bottom:1px dashed var(--rand)}
.topic{color:var(--tx)}
.zahl{color:var(--tx2);font-size:.8rem;white-space:nowrap}
li.alt,li.alt .topic{color:var(--alt)}
a.id.alt{color:var(--alt);text-decoration:line-through}
.zwei{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.filter{position:sticky;top:0;z-index:2;display:flex;flex-wrap:wrap;gap:6px;align-items:center;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--rand)}
.filter input[type=search]{flex:1 1 240px;min-width:0}
.filter input,.filter select,.filter button{font:inherit;font-size:.88rem;padding:4px 6px;border:1px solid var(--rand);border-radius:6px;background:var(--fl);color:var(--tx)}
.filter label{font-size:.88rem;color:var(--tx2);white-space:nowrap}
.filter output{margin-left:auto;color:var(--tx2);font-size:.88rem;white-space:nowrap}
.liste{margin-top:6px}
.kz,.zeile>summary{display:grid;grid-template-columns:150px 82px minmax(0,1fr) 96px 120px 44px 52px 92px;gap:10px;align-items:start;padding:7px 8px}
.kz{font-size:.75rem;text-transform:uppercase;letter-spacing:.04em;color:var(--tx2);border-bottom:1px solid var(--rand)}
.zeile{border-bottom:1px solid var(--rand);scroll-margin-top:var(--leiste,8px)}
.zeile>summary{cursor:pointer;list-style:none}
.zeile>summary::-webkit-details-marker{display:none}
.zeile>summary:hover{background:var(--fl2)}
.zeile[open]>summary{background:var(--fl2)}
.zeile.alt>summary{color:var(--alt)}
.zeile.alt .c-topic b{text-decoration:line-through}
.zeile.blitz>summary{animation:blitz 1.6s ease-out}
@keyframes blitz{from{background:var(--mark)}to{background:var(--fl2)}}
.c-id{font-size:.82rem;overflow-wrap:anywhere}
.c-sub,.c-up,.c-c{font-size:.85rem;color:var(--tx2);font-variant-numeric:tabular-nums}
.c-topic b{display:block;font-weight:600}
.c-topic i{display:block;font-style:normal;color:var(--tx2);font-size:.86rem;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.detail{padding:4px 12px 16px 16px;border-left:3px solid var(--akz);margin:0 0 10px 8px}
.felder{display:flex;flex-wrap:wrap;gap:6px 22px;margin:8px 0}
.felder div{display:flex;flex-direction:column}
.felder dt{font-size:.72rem;text-transform:uppercase;letter-spacing:.04em;color:var(--tx2)}
.felder dd{margin:0}
.abgeloest{background:var(--alt-b);color:var(--alt);padding:6px 10px;border-radius:6px}
.loest{color:var(--tx2)}
.bez{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.weitere{margin-top:12px}.weitere summary{cursor:pointer;color:var(--tx2)}
.weitere dt{font-family:ui-monospace,monospace;font-size:.8rem;color:var(--tx2);margin-top:6px}.weitere dd{margin:0}
.journal{list-style:none;padding:0;margin:0;font-size:.88rem}
.journal li{display:grid;grid-template-columns:88px 70px minmax(0,1fr);gap:8px;padding:3px 0;border-bottom:1px dashed var(--rand)}
.journal time{color:var(--tx2);font-variant-numeric:tabular-nums}
.journal span{overflow-wrap:anywhere}
.leg dt{margin-top:8px}.leg dd{margin:2px 0 0;color:var(--tx2)}
.fuss{color:var(--tx2);font-size:.85rem;margin:30px 0 40px}
.versteckt{display:none}
.gv-leiste{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:4px 0 6px}
.gv-leiste button{font:inherit;font-size:.88rem;padding:3px 10px;border:1px solid var(--rand);border-radius:6px;background:var(--fl);color:var(--tx);cursor:pointer}
.gv-tab[aria-pressed=true]{background:var(--akz);border-color:var(--akz);color:var(--bg)}
.gv-tab[aria-pressed=true] small{color:inherit}
.gv-zoom{margin-left:auto;display:flex;gap:4px}
.gv-hinweis{color:var(--tx2);font-size:.88rem;margin:4px 0}
.gv{overflow:auto;max-height:78vh;border:1px solid var(--rand);border-radius:8px;background:var(--fl);cursor:grab;user-select:none;-webkit-user-select:none}
.gv.zieht{cursor:grabbing}
.gv svg{display:block}
.gv .node{cursor:pointer}
.gv .node path,.gv .node polygon{fill:var(--fl2);stroke:var(--alt)}
.gv .node.o3 path,.gv .node.o3 polygon{fill:var(--gut-b)}
.gv .node.o2 path,.gv .node.o2 polygon{fill:var(--eher-b)}
.gv .node.o1 path,.gv .node.o1 polygon{fill:var(--verm-b)}
.gv .node.schwach path,.gv .node.schwach polygon{stroke:var(--verm)}
.gv .node.p-next path,.gv .node.p-next polygon{stroke:var(--offen);stroke-width:1.6}
.gv .node.p-now path,.gv .node.p-now polygon{stroke:var(--now);stroke-width:2.4}
.gv .node text{fill:var(--tx)}
.gv .edge path{stroke:var(--tx2);opacity:.7}
.gv .edge polygon{fill:var(--tx2);stroke:var(--tx2);opacity:.7}
.gv .blass{opacity:.13}
.gv .node.gewaehlt path,.gv .node.gewaehlt polygon{stroke:var(--akz);stroke-width:3}
.gv .edge.an path{stroke:var(--akz);stroke-width:1.8;opacity:1}
.gv .edge.an polygon{fill:var(--akz);stroke:var(--akz);opacity:1}
.gv-info{margin:6px 0;padding:6px 10px;border:1px solid var(--akz);border-radius:6px;background:var(--fl)}
.gv-info b{font-weight:600}
.gv-legende{display:flex;flex-wrap:wrap;gap:6px;font-size:.8rem;color:var(--tx2);margin:8px 0}
.gv-muster{padding:1px 8px;border:1px solid var(--alt);border-radius:5px;background:var(--fl2)}
.gv-muster.o3{background:var(--gut-b)}.gv-muster.o2{background:var(--eher-b)}.gv-muster.o1{background:var(--verm-b)}
.gv-muster.ox{background:var(--fl2)}
.gv-muster.p-now{border:2px solid var(--now);background:none}.gv-muster.p-next{border:2px solid var(--offen);background:none}
.gv-muster.schwach{border:1px dashed var(--verm);background:none}
.imgraph{margin:10px 0 0;font:inherit;font-size:.85rem;color:var(--akz);background:none;border:1px solid var(--rand);border-radius:6px;padding:2px 10px;cursor:pointer}
@media (max-width:820px){
.filter{position:static}
.zwei,.bez{grid-template-columns:1fr}
.kz{display:none}
.zeile>summary{grid-template-columns:auto auto 1fr;gap:4px 8px}
.c-topic{grid-column:1/-1;order:-1}
.c-c::before{content:"c="}
.detail{margin-left:0;padding-left:10px}
.journal li{grid-template-columns:80px 1fr}.journal li span{grid-column:1/-1}
}
"""

JS = r"""
(function(){
var liste=document.getElementById('liste'),zeilen=[].slice.call(liste.querySelectorAll('details.zeile'));
var kopfzeile=liste.querySelector('.kz'),text=new Map();
var f={q:$('f-q'),sub:$('f-sub'),offen:$('f-offen'),prio:$('f-prio'),or:$('f-or'),sort:$('f-sort'),alt:$('f-alt')};
function $(i){return document.getElementById(i)}
function suchtext(z){var t=text.get(z);if(t===undefined){t=z.textContent.toLowerCase();text.set(z,t)}return t}
function zustand(){var p=new URLSearchParams();
 if(f.q.value)p.set('q',f.q.value);['sub','offen','prio','or','sort'].forEach(function(k){if(f[k].value)p.set(k,f[k].value)});
 if(f.alt.checked)p.set('alt','1');return p.toString()}
function setzen(s){var p=new URLSearchParams(s);f.q.value=p.get('q')||'';
 ['sub','offen','prio','or','sort'].forEach(function(k){f[k].value=p.get(k)||''});f.alt.checked=p.get('alt')==='1'}
function anwenden(){var q=f.q.value.trim().toLowerCase().split(/\s+/).filter(Boolean),n=0;
 zeilen.forEach(function(z){var d=z.dataset,ok=(f.alt.checked||d.alt==='0')
  &&(!f.sub.value||d.sub===f.sub.value)&&(!f.offen.value||d.offen===f.offen.value)
  &&(!f.prio.value||d.prio===f.prio.value)&&(!f.or.value||d.oracle===f.or.value);
  if(ok&&q.length){var t=suchtext(z);ok=q.every(function(w){return t.indexOf(w)>=0})}
  z.classList.toggle('versteckt',!ok);z.classList.remove('gezeigt');if(ok)n++});
 var s=f.sort.value,arr=zeilen.slice();
 if(s==='id')arr.sort(function(a,b){return a.id<b.id?-1:a.id>b.id?1:0});
 else if(s==='up')arr.sort(function(a,b){return (b.dataset.updated).localeCompare(a.dataset.updated)||a.dataset.i-b.dataset.i});
 else if(s==='c')arr.sort(function(a,b){return (parseFloat(a.dataset.c)||0)-(parseFloat(b.dataset.c)||0)||a.dataset.i-b.dataset.i});
 else if(s==='n')arr.sort(function(a,b){return b.dataset.n-a.dataset.n||a.dataset.i-b.dataset.i});
 else arr.sort(function(a,b){return a.dataset.i-b.dataset.i});
 var frag=document.createDocumentFragment();arr.forEach(function(z){frag.appendChild(z)});liste.appendChild(frag);
 $('f-n').value=n+' of '+zeilen.length+' rows'}
var warten;
function geaendert(){clearTimeout(warten);warten=setTimeout(function(){anwenden();var s=zustand();
 history.replaceState(null,'',s?'#?'+s:location.pathname+location.search)},120)}
Object.keys(f).forEach(function(k){f[k].addEventListener(k==='q'?'input':'change',geaendert)});
$('f-reset').addEventListener('click',function(){setzen('');anwenden();history.replaceState(null,'',location.pathname+location.search)});
function zeigen(id){var z=document.getElementById(id);if(!z)return;
 if(z.classList.contains('zeile')){if(z.classList.contains('versteckt')){z.classList.remove('versteckt');z.classList.add('gezeigt')}
  z.open=true;z.classList.remove('blitz');void z.offsetWidth;z.classList.add('blitz')}
 z.scrollIntoView({block:'start'})}
function leiste(){var l=document.querySelector('.filter'),h=getComputedStyle(l).position==='sticky'?l.offsetHeight:0;
 document.documentElement.style.setProperty('--leiste',(h+8)+'px')}
window.addEventListener('resize',leiste);
function hash(){var h=decodeURIComponent(location.hash.slice(1));
 if(h.charAt(0)==='?'){setzen(h.slice(1));anwenden()}else if(h){zeigen(h)}}
window.addEventListener('hashchange',hash);
document.addEventListener('click',function(e){var b=e.target.closest('.mehr');if(!b)return;
 var t=b.previousElementSibling;t.classList.toggle('auf');
 b.textContent=t.classList.contains('auf')?'Show less':'Show all '+b.dataset.n+' characters'});
document.addEventListener('keydown',function(e){if(e.key==='/'&&!/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)){e.preventDefault();f.q.focus()}});
leiste();anwenden();
if(document.readyState==='complete')hash();else window.addEventListener('load',function(){setTimeout(hash,0)});
})();
(function(){
var sek=document.getElementById('graph'),boxen=sek?[].slice.call(sek.querySelectorAll('.gv')):[];
if(!boxen.some(function(b){return b.querySelector('svg')}))return;
var info=document.getElementById('gv-info'),leer=info.innerHTML,zoom={},aktiv=null;
function karte(box){if(box._k)return box._k;var k={knoten:{},oben:{},unten:{},kanten:[]};
 box.querySelectorAll('g.node').forEach(function(g){var n=g.querySelector('title').textContent;k.knoten[n]=g;k.oben[n]=[];k.unten[n]=[]});
 box.querySelectorAll('g.edge').forEach(function(g){var t=g.querySelector('title').textContent.split('->');g._von=t[0];g._zu=t[1];k.kanten.push(g);
  if(k.oben[t[1]])k.oben[t[1]].push(t[0]);if(k.unten[t[0]])k.unten[t[0]].push(t[1])});
 return box._k=k}
function huelle(start,nb){var s={},st=[start];while(st.length){(nb[st.pop()]||[]).forEach(function(y){if(!s[y]){s[y]=1;st.push(y)}})}return s}
function waehlen(box,id){var k=karte(box);if(!k.knoten[id])return;var auf=huelle(id,k.oben),ab=huelle(id,k.unten);
 function in_(m,x){return x===id||!!m[x]}
 Object.keys(k.knoten).forEach(function(n){var g=k.knoten[n];g.classList.toggle('blass',!(in_(auf,n)||in_(ab,n)));g.classList.toggle('gewaehlt',n===id)});
 k.kanten.forEach(function(e){var an=!!((in_(auf,e._von)&&in_(auf,e._zu))||(in_(ab,e._von)&&in_(ab,e._zu)));e.classList.toggle('blass',!an);e.classList.toggle('an',an)});
 infoZeigen(id,Object.keys(auf).length,Object.keys(ab).length)}
function loesen(box){var k=karte(box);Object.keys(k.knoten).forEach(function(n){k.knoten[n].classList.remove('blass','gewaehlt')});
 k.kanten.forEach(function(e){e.classList.remove('blass','an')});info.innerHTML=leer}
function infoZeigen(id,nAuf,nAb){var z=document.getElementById(id),s=z&&z.querySelector('summary');info.textContent='';
 var a=document.createElement('a');a.href='#'+id;a.className='id';a.textContent=id;info.appendChild(a);
 if(s){['.c-st','.c-or','.c-pr'].forEach(function(q){var x=s.querySelector(q);if(x&&x.innerHTML)info.insertAdjacentHTML('beforeend',' '+x.innerHTML)});
  var t=document.createElement('b');t.textContent=' '+s.querySelector('.c-topic b').textContent;info.appendChild(t)}
 var n=document.createElement('span');n.className='zahl';n.textContent=' Stands on '+nAuf+', carries '+nAb+' in this view. ';info.appendChild(n);
 var o=document.createElement('a');o.href='#'+id;o.textContent='Open in register';info.appendChild(o)}
function masse(box){var svg=box.querySelector('svg'),vb=svg.viewBox.baseVal;return{svg:svg,w:vb.width,h:vb.height}}
// Zoom 1 = natuerliche Groesse: Graphviz rechnet in pt, 1 pt = 4/3 px
function setzeZoom(box,z){var m=masse(box);z=Math.max(0.1,Math.min(3,z));zoom[box.dataset.v]=z;m.svg.style.width=(m.w*z*4/3)+'px';m.svg.style.height=(m.h*z*4/3)+'px'}
function passend(box){return Math.min(1,(box.clientWidth-2)/(masse(box).w*4/3))}
function zeige(v){boxen.forEach(function(b){var an=b.dataset.v===v;b.hidden=!an;if(an){aktiv=b;
  if(b.querySelector('svg')&&!(v in zoom))setzeZoom(b,Math.max(0.8,passend(b)))}});
 sek.querySelectorAll('.gv-tab').forEach(function(t){t.setAttribute('aria-pressed',String(t.dataset.v===v))});
 sek.querySelectorAll('.gv-hinweis').forEach(function(p){p.hidden=p.dataset.v!==v});info.innerHTML=leer}
sek.querySelectorAll('.gv-tab').forEach(function(t){t.addEventListener('click',function(){zeige(t.dataset.v)})});
sek.querySelectorAll('.gv-zoom button').forEach(function(b){b.addEventListener('click',function(){if(!aktiv||!aktiv.querySelector('svg'))return;
 var z=zoom[aktiv.dataset.v]||1,w=b.dataset.z;setzeZoom(aktiv,w==='+'?z*1.25:w==='-'?z/1.25:w==='fit'?passend(aktiv):1)})});
boxen.forEach(function(b){var start=null,bewegt=false;
 b.addEventListener('pointerdown',function(e){if(e.pointerType!=='mouse'||e.button!==0)return;start={x:e.clientX,y:e.clientY,l:b.scrollLeft,t:b.scrollTop};bewegt=false});
 b.addEventListener('pointermove',function(e){if(!start)return;var dx=e.clientX-start.x,dy=e.clientY-start.y;
  if(!bewegt&&Math.abs(dx)+Math.abs(dy)>4){bewegt=true;b.classList.add('zieht')}if(bewegt){b.scrollLeft=start.l-dx;b.scrollTop=start.t-dy}});
 window.addEventListener('pointerup',function(){start=null;b.classList.remove('zieht')});
 b.addEventListener('click',function(e){if(bewegt){bewegt=false;return}var g=e.target.closest('g.node');
  if(g)waehlen(b,g.querySelector('title').textContent);else loesen(b)})});
document.addEventListener('click',function(e){var knopf=e.target.closest('.imgraph');if(!knopf)return;
 zeige('alle');var box=aktiv,g=karte(box).knoten[knopf.dataset.id];if(!g)return;waehlen(box,knopf.dataset.id);
 sek.scrollIntoView({block:'start'});var r=g.getBoundingClientRect(),br=box.getBoundingClientRect();
 box.scrollLeft+=r.left-br.left-box.clientWidth/2+r.width/2;box.scrollTop+=r.top-br.top-box.clientHeight/2+r.height/2});
zeige(boxen[0].dataset.v);
})();
"""


# ------------------------------------------------------------------ Schreiben
def ziel_pruefen(out):
    out = os.path.abspath(out)
    research = os.path.realpath(os.path.join(truth.ROOT, "research"))
    echt = os.path.realpath(out)
    if echt == os.path.realpath(truth.P) or echt.startswith(research + os.sep):
        raise SystemExit("Abgelehnt: die Ansicht schreibt nie unter research/ (%s)." % out)
    if not out.endswith((".html", ".htm")):
        raise SystemExit("Abgelehnt: Ausgabe muss auf .html enden (%s)." % out)
    return out


def schreiben(out, inhalt):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".truth_ansicht-", suffix=".tmp", dir=os.path.dirname(out))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(inhalt)
        maske = os.umask(0)
        os.umask(maske)
        os.chmod(tmp, 0o666 & ~maske)   # mkstemp legt 0600 an; die Seite soll lesbar sein wie jede Datei
        os.replace(tmp, out)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def erzeugen(commit_url=None):
    cols, rows = truth.lesen()
    reg = Register(cols, rows)
    journal, git_ok = journale(reg.ids)
    oracle = dict(ORACLE_VORGABE)
    oracle.update(truth._konf("ANSICHT_ORACLE", {}) or {})
    seite = Seite(reg, journal, git_ok, git_stand(), validator(), commit_url,
                  truth._konf("ANSICHT_TITEL", "Truth register"), oracle, deckel())
    return seite.html()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Register als HTML-Ansicht, nur lesend.")
    ap.add_argument("--out", default=AUSGABE, help="Ausgabedatei (Vorgabe build/truth_ansicht.html)")
    ap.add_argument("--commit-url", help="Vorlage fuer Commit-Links, {hash} wird ersetzt")
    ap.add_argument("--oeffnen", action="store_true", help="danach im Browser oeffnen")
    ap.add_argument("--leise", action="store_true", help="nichts ausgeben (fuer Hooks)")
    a = ap.parse_args(argv)
    if a.commit_url and "{hash}" not in a.commit_url:
        raise SystemExit("--commit-url braucht den Platzhalter {hash}")
    out = ziel_pruefen(a.out)
    schreiben(out, erzeugen(a.commit_url))
    if not a.leise:
        print(out)
    if a.oeffnen:
        webbrowser.open("file://" + out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
