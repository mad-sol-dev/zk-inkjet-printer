#!/usr/bin/env python3
"""Prueft research/TRUTH.csv auf die Regeln aus research/TRUTH.md.

Exit 0 = in Ordnung, 1 = Verstoss. Gedacht fuer den Sitzungsanfang und als
pre-commit-Hook. Die Regeln stehen sonst nur in einem Chat -- und Chats enden.

Grundsatz fuer die Meldungen hier: wer das Skript laufen laesst, ist oft ein
Agent ohne Vorgeschichte. Ein Traceback oder ein nacktes "Verstoss" laesst ihn
ratlos zurueck. Jede Abbruchmeldung sagt deshalb, was passiert ist, was es
bedeutet und was als naechstes zu tun ist.
"""
import csv, glob, os, re, subprocess, sys

P = "research/TRUTH.csv"
COLS = ["Subsystem","Topic","Statement","Status","Confidence","Evidence_E0","Evidence_E3New",
        "Evidence_E1","Evidence_E3Old","Evidence_E4","Authority","Open_Question","Next_Test",
        "Claim_ID","Decided","Superseded_By","Updated","Source","Prio","Depends_On","Oracle"]

# Ab diesem Datum gelten Oracle-Pflicht und Konfidenzdeckel. Aeltere Zeilen
# bleiben unberuehrt -- sie werden beim naechsten Anfassen nachgezogen, nicht
# rueckwirkend umgeschrieben.
ORACLE_AB = "2026-08-22"
DECKEL = {"O1": 0.60, "O2": 0.95, "O3": 1.00}

# Ab diesem Datum gilt die Zellgrenze (Regel 9 in CLAUDE.md, Regel 8 in
# TRUTH.md). Im Januar wanderte die Arbeit aus der Matrix zurueck in
# Prosadokumente, im Oktober in die Zellen: CL-USB-REC-128 hatte 28 428
# Zeichen, 42 lebende Zeilen lagen ueber 2000. Eine Zelle ist ein Urteil;
# der Weg dorthin steht in den Commit-Nachrichten mit der Claim-ID.
# Altzeilen werden beim naechsten Anfassen gekuerzt, nicht rueckwirkend.
ZELLE_AB = "2026-10-16"

# Ab diesem Datum braucht eine O2/O3-Zeile ihren Beleg in Evidence_E0 (Kommando
# bzw. Vorgang am Geraet, Format 'Anzahl [Beleg]'). Der Skill verlangte das seit
# August, geprueft wurde es nicht: am 2026-10-15 standen fuenf O2/O3-Zeilen mit
# Evidence_E0 = 0 im Register. Aufgefallen durch den Selbsttest von truth.py.
EVIDENZ_AB = "2026-10-15"
ZELLGRENZE = {"Statement": 2000, "Next_Test": 1000}

# Ab diesem Datum muss der Beleg einer O2-Zeile einen wiederholbaren Aufruf
# nennen (Regel 11 in CLAUDE.md): ein Skript, ein Brueckenwerkzeug mit
# Argument, run_script mit Skriptnamen, einen Befehl wie pdftotext oder grep,
# oder ein Disassemblat an genannten Adressen. Die Auszaehlung der Sitzungen vom
# 2026-10-08 bis 2026-10-19 fand 1164 Inline-Python-Aufrufe und 201 Laeufe von
# Scratchpad-Skripten gegen 675 Brueckenaufrufe; mehrere O2-Zeilen nannten als
# Beleg nur Prosa ('python3 Bytesuche nach ...') oder ein Skript, das nie
# versioniert wurde (CL-BOOT-REC-115: pruef_boot115.py im Scratchpad).
# Erkannt wird nur, dass ein Aufruf genannt ist, nicht, dass er die Zahl
# geliefert hat. Ein genanntes Skript, das im Repository fehlt, ist nur ein
# Hinweis: Skripte aus Nachbar-Repositories und der Selbsttest der Vorlage
# (probe.py) nennen Dateien, die hier nicht liegen.
BELEG_AB = "2026-10-20"
BELEG_BRUECKE = ("analyze_function_complete|apply_label|collect|datatypes_create|"
                 "datatypes_update|disassemble_at|disassemble_batch|find_in_function|jt_scan|"
                 "jt_slot_check|jt_slot_process|list_functions_in_range|mmio_annotate_compact|"
                 "read_bytes|read_words|rename_function|search_exports|search_functions|"
                 "search_imports|search_scalars_with_context|search_scalars|search_strings|"
                 "search_xrefs_to|set_comment|string_xrefs_compact|strings_compact")
BELEG_SHELL = ("pdftotext|pdfgrep|grep|sha256sum|md5sum|cmp|xxd|hexdump|strings|"
               "arm-none-eabi-objdump|objdump|readelf|sigrok-cli|analyzeHeadless|binwalk")
BELEG_SKRIPT = re.compile(r"((?:[\w.~/-]*/)?[\w-]+\.py)\b")
BELEG_AUFRUF = [
    re.compile(r"\bpython3?\s+-m\s+[\w.]+"),
    re.compile(r"\brun_script\b[^;\]]{0,40}?[\w-]+\.py"),
    re.compile(r"\b(?:%s)\b[^;\]]{0,80}?(?:0x[0-9A-Fa-f]+|['\"]|\w+=)" % BELEG_BRUECKE),
    re.compile(r"(?<![\w./-])(?:%s)\s+(?:-|['\"]|[\w.~-]*/)" % BELEG_SHELL),
    re.compile(r"(?<![\w./-])dd\s+if="),
    re.compile(r"\bcapstone\b[^;\]]{0,80}?0x[0-9A-Fa-f]{3,}"),
]
BELEG_SCRATCH = re.compile(r"(?:/tmp/|scratchpad)[^\s;\]]*\.py")
BELEG_PROSA = re.compile(r"\bpython3?\s+(?!-[muc]\b)(?![\w.~/-]+\.py\b)[A-Za-z]|"
                         r"\b(?:Bytesuche|Stringsuche|Poolsuche|byte search|string search|"
                         r"re\.finditer|struct\.unpack|Regex)\b", re.I)

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

# Alte Adresszaehlweise. Bis 2026-08-31 galt VA = Dateioffset + 0x200000; die
# Linkbasis ist 0x00058000 (CL-BOOT-REC-113), die Ghidra-Datenbank steht seit
# 2026-10-11 dort (CL-TOOL-REC-121). Eine Zeile, die APP-Adressen der alten
# Zaehlweise nennt, braucht einen Vermerk -- sonst sucht der naechste Leser an
# der falschen Stelle. Am 2026-10-12 trugen 48 Zeilen solche Adressen ohne
# Vermerk, weil jede Sitzung nur die Zeilen nachzog, die sie ohnehin anfasste.
# Nur ein Hinweis: die Erkennung ist eine Heuristik, kein Beweis. VAs von
# 0x200000 bis 0x2CD22B sind auch in der neuen Zaehlweise gueltig (Dateioffset
# 0x1A8000 aufwaerts); eine neue Zeile, die solche Adressen nennt, sagt deshalb
# einmal, in welcher Zaehlweise sie schreibt, dann schweigt die Pruefung.
# FUN_-Namen werden aus demselben Grund nicht geprueft.
ALT_BASIS, APP_GROESSE = 0x200000, 0x27522C
ALT_HEX = re.compile(r"0x0*([0-9A-Fa-f]{5,8})\b")
ALT_DATEI = re.compile(r"(file offsets?|file|Datei(offset)?|Dateioffsets?)\s*[:=]?\s*$", re.I)
ALT_MARKE = re.compile(r"BASIS-VERMERK|CL-BOOT-REC-113|KORREKTUR 20|Zaehlweise|alte Adresse|"
                       r"Linkbasis|0x00058000|VA = (Dateioffset )?\+ ?0x58000", re.I)


def alte_adressen(rows):
    """Nicht abgeloeste Zeilen mit APP-Adressen der alten Zaehlweise und ohne Vermerk."""
    treffer = []
    for r in rows:
        if r.get("Superseded_By"):
            continue
        text = " ".join(r.get(c) or "" for c in ("Topic", "Statement", "Next_Test"))
        if ALT_MARKE.search(text):
            continue
        for m in ALT_HEX.finditer(text):
            v = int(m.group(1), 16)
            if (ALT_BASIS < v < ALT_BASIS + APP_GROESSE
                    and not ALT_DATEI.search(text[max(0, m.start() - 22):m.start()])):
                treffer.append(r["Claim_ID"])
                break
    return treffer


def _skript_da(pfad):
    """Liegt ein im Beleg genanntes Skript im Repository (Wurzel, tools/scripts, Artefakte)?"""
    if pfad.startswith(("/", "~")):
        return os.path.exists(os.path.expanduser(pfad))
    name = os.path.basename(pfad)
    if any(os.path.exists(k) for k in (pfad, os.path.join("tools/scripts", pfad),
                                       os.path.join("tools/scripts", name),
                                       os.path.join("tools/scripts/ghidra", name))):
        return True
    return bool(glob.glob("research/phase_a_sd_analysis/artifacts/**/" + name, recursive=True))


def beleg_pruefen(text):
    """Regel 11: was nennt ein Beleg? -> (aufruf, scratch_pfade, prosa, fehlende_skripte)"""
    scratch = BELEG_SCRATCH.findall(text)
    rest = BELEG_SCRATCH.sub(" ", text)
    skripte = [m.group(1) for m in BELEG_SKRIPT.finditer(rest)]
    aufruf = bool(skripte) or any(p.search(rest) for p in BELEG_AUFRUF)
    return (aufruf, scratch, bool(BELEG_PROSA.search(text)),
            [s for s in skripte if not _skript_da(s)])


def beleg_selbsttest():
    """Positiv- und Negativkontrollen fuer beleg_pruefen; Aufruf mit --selbsttest-beleg."""
    faelle = [  # (Beleg, aufruf, scratch, prosa)
        ("1 [python3 tools/scripts/scatter_base.py firmware/bin/ZK-INKJET-NANO-APP.bin "
         "--pooltest 0x58000]", True, False, False),
        ("3 [Regex rb'(Jan|Feb) [ 0-9][0-9]' ueber firmware/bin/ZK-INKJET-NANO-APP.bin; "
         "Bytesuche DCJET in beiden]", False, False, True),
        ("1 [python3 /tmp/claude-1000/x/scratchpad/pruef_boot115.py]", False, True, False),
        ("6 [mcp disassemble_at 0xB2AC0 count=40; python3 Bytesuche nach 0x123B00]",
         True, False, True),
        ("1 [Ghidra search_xrefs_to 0x0010c06c (4)]", True, False, False),
        ("1 [mcp run_script dekompilieren.py 0xD7A7C]", True, False, False),
        ("1 [capstone ARM over firmware/bin/ZK-INKJET-NANO-APP.bin at VA 0xBB990-0xBB9C4]",
         True, False, False),
        ("1 [pdftotext -layout vendor/N3290X.PDF, grep 'USB1.1 Host']", True, False, False),
        ("1 [python3 -m n329usb --trace boot FA93_musb.bin]", True, False, False),
        ("1 [CL-BOOT-REC-118 (main 0x702F2C); CL-BOOT-REC-121]", False, False, False),
        ("1 [strings 0xBE9C4, 0xBE9BC in the image]", False, False, False),
        ("1 [python3 probe.py a.bin]", True, False, False),
    ]
    fehler = 0
    for text, a, s, p in faelle:
        ist = beleg_pruefen(text)
        ok = (ist[0], bool(ist[1]), ist[2]) == (a, s, p)
        fehler += not ok
        print("%s  %s" % ("ok  " if ok else "FEHL", text[:90]))
    fehlt = beleg_pruefen("1 [python3 probe_fehlt_hier.py a.bin]")[3]
    ok = fehlt == ["probe_fehlt_hier.py"] and not beleg_pruefen(
        "1 [python3 tools/scripts/neg_recheck.py]")[3]
    fehler += not ok
    print("%s  fehlendes Skript erkannt, vorhandenes nicht gemeldet" % ("ok  " if ok else "FEHL"))
    print("\n%s" % ("Alle Kontrollen bestanden." if not fehler
                    else "%d Kontrolle(n) fehlgeschlagen." % fehler))
    return 1 if fehler else 0


def main():
    err, warn = [], []

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

    # --- Abgeschnittene Zellen ---
    # Die Januar-Reconciliation hat Statement bei 120 und Next_Test bei 80
    # Zeichen hart gekappt: 51 Zellen in 42 Zeilen, mit "..." am Ende. Der
    # Validator konnte das nicht sehen, weil das Feld ja gefuellt war -- und
    # CL-USB-REC-011 verlor dabei genau den Teil seines Next_Test, der die
    # Zweimodus-Suche verlangt. Ein halber Satz ist kein Arbeitspaket.
    gekappt = [(r["Claim_ID"], c) for r in rows for c in ("Statement", "Next_Test")
               if (r.get(c) or "").strip().endswith(("...", "\u2026"))]
    if gekappt:
        err.append("Zelle endet auf '...': %s -- fast immer ein Importschnitt, kein "
                   "Auslassungszeichen. Volltext steht meist in "
                   "research/docs_rebuild/reconciliation/RECONCILED_claims_*.md; ist er "
                   "nicht auffindbar, die Luecke sichtbar machen statt sie stehen zu "
                   "lassen" % gekappt[:8])

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

    # --- Evidenzpflicht fuer O2/O3 ---
    def ohne_beleg(r):
        return (r.get("Oracle", "") in ("O2", "O3") and not r["Superseded_By"]
                and (r.get("Evidence_E0") or "").strip() in ("", "0"))
    x = [r["Claim_ID"] for r in rows if ohne_beleg(r) and r.get("Updated", "") >= EVIDENZ_AB]
    if x:
        err.append("O2/O3 ohne Evidence (Evidence_E0 leer oder 0): %s -- O2 nennt das Kommando "
                   "und die Datei, O3 den Vorgang am Geraet; wer das nicht kann, hat O1" % x[:12])
    x = [r["Claim_ID"] for r in rows if ohne_beleg(r) and r.get("Updated", "") < EVIDENZ_AB]
    if x:
        warn.append("%d Altzeile(n) auf O2/O3 ohne Beleg in Evidence_E0: %s -- beim Anfassen "
                    "Beleg nachtragen oder auf O1 senken" % (len(x), ", ".join(x)))

    # --- Beleg einer O2-Zeile nennt einen wiederholbaren Aufruf (Regel 11) ---
    def o2_mit_beleg(r):
        return (r.get("Oracle", "") == "O2" and not r["Superseded_By"]
                and (r.get("Evidence_E0") or "").strip() not in ("", "0"))
    ohne_aufruf, im_scratch, prosa, fehlt = [], [], [], []
    alt_ohne = []
    for r in rows:
        if not o2_mit_beleg(r):
            continue
        aufruf, scratch, pr, fe = beleg_pruefen(r["Evidence_E0"])
        if r.get("Updated", "") < BELEG_AB:
            if not aufruf:
                alt_ohne.append(r["Claim_ID"])
            continue
        if not aufruf:
            ohne_aufruf.append(r["Claim_ID"])
        if scratch:
            im_scratch.append((r["Claim_ID"], scratch[0]))
        if pr:
            prosa.append(r["Claim_ID"])
        if fe:
            fehlt.append((r["Claim_ID"], fe[0]))
    if ohne_aufruf:
        err.append("O2-Beleg ohne wiederholbaren Aufruf: %s -- Evidence_E0 nennt das Skript "
                   "(tools/scripts/ oder neben der Ausgabe im Artefaktordner), das "
                   "Brueckenwerkzeug mit Argument, run_script mit Skriptnamen oder den Befehl "
                   "(pdftotext, grep ...). Ein Verweis auf andere Zeilen reicht nicht: deren "
                   "Aufruf hierher uebernehmen, sonst ist die Zeile O1 (Regel 11)" % ohne_aufruf[:12])
    if im_scratch:
        err.append("O2-Beleg nennt ein Skript im Scratchpad: %s -- das Skript verschwindet mit "
                   "der Sitzung. Nach tools/scripts/ oder neben seine Ausgabe in "
                   "research/phase_a_sd_analysis/artifacts/ legen, committen und diesen Pfad "
                   "nennen (Regel 11)" % im_scratch[:8])
    if prosa:
        warn.append("%d O2-Zeile(n) beschreiben einen Rechenschritt in Worten statt mit Skript "
                    "(etwa 'python3 Bytesuche nach ...'): %s -- liefert dieser Schritt eine Zahl, "
                    "Zaehlung oder einen Negativbefund, gehoert er in ein versioniertes Skript "
                    "(Regel 11)" % (len(prosa), ", ".join(prosa[:12])))
    if fehlt:
        warn.append("O2-Beleg nennt ein Skript, das im Repository nicht liegt: %s -- "
                    "versionieren oder den Pfad korrigieren (Regel 11)" % fehlt[:8])
    if alt_ohne:
        warn.append("%d Altzeile(n) auf O2 nennen keinen wiederholbaren Aufruf in Evidence_E0: "
                    "%s -- beim Anfassen den Aufruf nachtragen oder auf O1 senken (Regel 11)"
                    % (len(alt_ohne), ", ".join(alt_ohne[:12]) + (" ..." if len(alt_ohne) > 12 else "")))

    # --- Zellgrenze ---
    lebend = [r for r in rows if not r["Superseded_By"]]
    zu_lang = [(r["Claim_ID"], c, len(r.get(c) or "")) for r in lebend
               if r.get("Updated", "") >= ZELLE_AB
               for c, n in ZELLGRENZE.items() if len(r.get(c) or "") > n]
    if zu_lang:
        err.append("Zelle ueber der Grenze: %s -- eine Zelle ist ein Urteil, kein "
                   "Laborjournal. Urteil und tragende Belege stehen lassen, den Weg "
                   "dorthin in die Commit-Nachricht; ein eigenstaendiges Ergebnis wird "
                   "eine eigene Zeile. Grenzen: %s" % (zu_lang[:8], ZELLGRENZE))
    alt_lang = [r["Claim_ID"] for r in lebend if r.get("Updated", "") < ZELLE_AB
                and any(len(r.get(c) or "") > n for c, n in ZELLGRENZE.items())]
    if alt_lang:
        warn.append("%d Altzeile(n) ueber der Zellgrenze %s. Wer eine davon anfasst, "
                    "kuerzt sie auf das Urteil; der Weg bleibt im Git-Log "
                    "(git log --format='%%ad %%h %%s' --date=short | grep <Claim-ID>)."
                    % (len(alt_lang), ZELLGRENZE))

    reste = [f for f in glob.glob(P + "*") if f.endswith((".tmp", ".part", ".bak"))]
    if reste:
        err.append("Reste eines abgebrochenen Schreibvorgangs: %s -- pruefen und "
                   "loeschen; die eigentliche Datei scheint in Ordnung" % reste)
    copies = [f for f in glob.glob("research/TRUTH.csv*")
              if f != P and not f.endswith(".md") and f not in reste]
    if copies:
        err.append("Kopien neben der autoritativen Datei: %s -- Regel 3: Git ist die "
                   "Historie, vor groesseren Aenderungen committen statt kopieren" % copies)
    # Bewusst nur ein Hinweis, kein Verstoss: die Datei anzusehen ist der
    # Normalfall und soll nichts blockieren. Eine Regel, die man routinemaessig
    # mit --no-verify umgeht, ist schlechter als eine, die nur informiert.
    # Gefaehrlich ist nicht das Offenhaben, sondern das Speichern aus einer
    # veralteten Ansicht heraus -- und das wuerde ein blockierter Commit
    # ohnehin nicht verhindern.
    alt = alte_adressen(rows)
    if alt:
        warn.append("%d Zeile(n) nennen Adressen der alten Zaehlweise Dateioffset + 0x200000 "
                    "ohne Vermerk: %s -- richtig ist Dateioffset + 0x58000 (CL-BOOT-REC-113), "
                    "also alt minus 0x1A8000. Einen BASIS-VERMERK mit den umgerechneten "
                    "Adressen anhaengen, oder die Zaehlweise in der Zeile selbst nennen. "
                    "Dateioffsets direkt nach 'file'/'Datei' zaehlen nicht."
                    % (len(alt), ", ".join(alt[:12]) + (" ..." if len(alt) > 12 else "")))

    locks = glob.glob("research/.~lock.*")
    if locks:
        warn.append("TRUTH.csv ist in LibreOffice geoeffnet (%s). Ansehen ist in "
                    "Ordnung. Nicht von dort speichern: die Ansicht kann aelter sein "
                    "als die Datei, und LibreOffice schreibt zusaetzlich CRLF und "
                    "eigene Quoting-Regeln, was den naechsten Diff unbrauchbar macht."
                    % ", ".join(os.path.basename(l) for l in locks))

    # Getrennt zaehlen: diese Datei ist der Stand des GERAETS. Subsystem=TOOL
    # sind Methoden- und Werkzeugzeilen -- notwendig, aber kein Geraetewissen.
    # Prio=park markiert das nur bei offenen Zeilen; entschiedene Werkzeugzeilen
    # trugen bis 2026-08-22 gar keine Kennzeichnung und standen gleichrangig
    # neben Befunden ueber den Drucker.
    ger = [r for r in rows if r["Subsystem"] != "TOOL"]
    wzg = [r for r in rows if r["Subsystem"] == "TOOL"]
    traegt = {d.strip() for r in rows for d in r.get("Depends_On", "").split(";") if d.strip()}
    print("TRUTH.csv | GERAET %d (%d entschieden, %d offen, %d abgeloest) | "
          "WERKZEUG %d (%d davon tragend) | Front %d"
          % (len(ger), sum(1 for r in ger if r["Decided"] == "yes"),
             sum(1 for r in ger if r["Decided"] == "no" and not r["Superseded_By"]),
             sum(1 for r in ger if r["Superseded_By"]),
             len(wzg), sum(1 for r in wzg if r["Claim_ID"] in traegt), len(front)))
    for w in warn:
        print("  HINWEIS:  %s" % w)
    for e in err:
        print("  VERSTOSS: %s" % e)
    return 1 if err else 0

if __name__ == "__main__":
    sys.exit(beleg_selbsttest() if "--selbsttest-beleg" in sys.argv[1:] else main())
