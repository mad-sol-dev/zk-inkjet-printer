#!/usr/bin/env python3
"""MCP-Server fuer research/TRUTH.csv -- ein duenner Wrapper um truth.py.

Kein eigener Speicher, keine eigene Regellogik: jedes Werkzeug ruft dieselbe
Funktion wie die Kommandozeile, und geschrieben wird nur, wenn der Validator
des Projekts danach nicht mehr Verstoesse meldet als vorher.

Ohne Abhaengigkeiten (kein mcp-Paket noetig): JSON-RPC 2.0 ueber stdio, eine
Nachricht je Zeile. Start durch den Client, z. B. Claude Code ueber .mcp.json:

    {"mcpServers": {"truth": {"command": "python3", "args": ["tools/truth_mcp.py"]}}}

Selbsttest von Hand:
    printf '%s\\n' '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 tools/truth_mcp.py
"""
import json, os, sys, traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import truth  # noqa: E402

VERSION = "1.0"
S, I, N, B, A, O = "string", "integer", "number", "boolean", "array", "object"


def _schema(pflicht, **felder):
    props = {}
    for name, (typ, text) in felder.items():
        props[name] = {"type": typ, "description": text}
        if typ == A:
            props[name]["items"] = {"type": S}
    return {"type": "object", "properties": props, "required": list(pflicht)}


DRY = (B, "nur zeigen, was sich aendern wuerde; nichts schreiben")

WERKZEUGE = {
    "truth_front": (
        "Arbeitsfront (Prio=now) mit dem naechsten Test je Zeile. Am Sitzungsanfang nach next.py.",
        _schema([]),
        lambda a: truth.front()),
    "truth_find": (
        "Zeilen suchen. Liefert ID, entschieden/offen, Prio, Stufe, Konfidenz, Titel.",
        _schema([], offen=(B, "true nur offene, false nur entschiedene, weglassen fuer alle"),
                prio=(S, "now|next|later|park"), subsystem=(S, "Subsystem"),
                oracle=(S, "O1|O2|O3"), text=(S, "regulaerer Ausdruck ueber Titel und Aussage"),
                limit=(I, "hoechstens so viele Treffer, Vorgabe 50")),
        lambda a: truth.finden(a.get("offen"), a.get("prio"), a.get("subsystem"), a.get("oracle"),
                               a.get("text"), int(a.get("limit", 50)))),
    "truth_show": (
        "Eine Zeile mit vollen Zellen. Mit felder nur bestimmte Spalten -- spart Kontext bei langen Zellen.",
        _schema(["id"], id=(S, "Claim-ID"), felder=(A, "Spaltennamen, z. B. Statement, Next_Test")),
        lambda a: truth.zeigen(a["id"], a.get("felder"))),
    "truth_deps": (
        "Worauf eine Zeile steht und welche Zeilen direkt an ihr haengen.",
        _schema(["id"], id=(S, "Claim-ID")),
        lambda a: truth.abhaengigkeiten(a["id"])),
    "truth_journal": (
        "Commits, die die Claim-ID nennen -- das Laborjournal einer Zeile (Kandidaten, Fehlversuche).",
        _schema(["id"], id=(S, "Claim-ID")),
        lambda a: truth.journal(a["id"])),
    "truth_check": (
        "Den Validator des Projekts laufen lassen.",
        _schema([]),
        lambda a: "rc=%d\n%s" % truth.pruefen()),
    "truth_add": (
        "Neue Zeile anlegen. Pruefstufe vor Konfidenz: O1 hergeleitet (max 0.60), O2 wiederholbares "
        "Kommando ueber eine Datei (max 0.95), O3 am Gegenstand beobachtet. Geht die Aussage ueber die "
        "Ausgabe hinaus (Identitaet, Zweck, Herkunft), ist sie O1. Statement: Urteil zuerst, dann die "
        "tragenden Belege, hoechstens 2000 Zeichen; der Weg dorthin gehoert in die Commit-Nachricht. "
        "Offene Zeilen brauchen next_test. Die ID wird automatisch vergeben, wenn id fehlt.",
        _schema(["subsystem", "topic", "statement", "oracle", "confidence"],
                subsystem=(S, "Subsystem"), topic=(S, "Titel, eine Zeile"),
                statement=(S, "Urteil zuerst, dann tragende Belege"), oracle=(S, "O1|O2|O3"),
                confidence=(N, "0..1, gedeckelt durch die Stufe"),
                next_test=(S, "bei offener Zeile Pflicht: das Experiment, das sie entscheidet"),
                prio=(S, "now|next|later|park, Vorgabe next"),
                evidence=(S, "O2: Kommando und Datei; O3: Vorgang am Gegenstand"),
                depends_on=(S, "Claim-IDs mit ; getrennt -- nur echte Traeger"),
                source=(S, "Herkunft, Vorgabe Sitzung-<Datum>"), status=(S, "Status"),
                id=(S, "Claim-ID, sonst automatisch"),
                entschieden=(B, "gleich als entschieden anlegen"), dry_run=DRY),
        lambda a: truth.anlegen(a["subsystem"], a["topic"], a["statement"], a["oracle"],
                                a["confidence"], a.get("next_test", ""), a.get("prio"),
                                a.get("evidence", ""), a.get("depends_on", ""), a.get("source", ""),
                                a.get("status"), a.get("id"), bool(a.get("entschieden")),
                                bool(a.get("dry_run")))),
    "truth_close": (
        "Offene Zeile schliessen (Decided=yes, Prio und Next_Test leer). urteil wird mit Datum vor die "
        "Aussage gesetzt; statement ersetzt sie ganz. O2 verlangt in evidence das Kommando.",
        _schema(["id"], id=(S, "Claim-ID"), status=(S, "verified|refuted, Vorgabe verified"),
                oracle=(S, "O1|O2|O3"), confidence=(N, "0..1"), evidence=(S, "Kommando oder Vorgang"),
                urteil=(S, "das Ergebnis in einem Satz"), statement=(S, "ersetzt die Aussage ganz"),
                dry_run=DRY),
        lambda a: truth.schliessen(a["id"], a.get("status") or "verified", a.get("oracle"),
                                   a.get("confidence"), a.get("evidence"), a.get("urteil"),
                                   a.get("statement"), bool(a.get("dry_run")))),
    "truth_supersede": (
        "Zeile abloesen und die Abloesung durchreichen. Haengen andere Zeilen an der alten, wird "
        "nichts geschrieben, bevor jede davon gelesen und entschieden ist: umhaengen (ueberlebt, "
        "haengt kuenftig an der Nachfolgerin) oder mitabloesen (faellt mit). Der erste Aufruf ohne "
        "diese Listen zeigt die betroffenen Zeilen mit Text.",
        _schema(["alt", "neu", "notiz"], alt=(S, "abzuloesende Claim-ID"),
                neu=(S, "Nachfolgerin, muss existieren"), notiz=(S, "warum, ein Satz"),
                umhaengen=(A, "Claim-IDs, die ueberleben"), mitabloesen=(A, "Claim-IDs, die mitfallen"),
                dry_run=DRY),
        lambda a: truth.abloesen(a["alt"], a["neu"], a["notiz"], a.get("umhaengen", []),
                                 a.get("mitabloesen", []), bool(a.get("dry_run")))),
    "truth_set": (
        "Einzelne Felder einer Zeile setzen (Korrekturen). Updated wird automatisch gesetzt. "
        "Claim_ID aendert sich nie -- dafuer neue Zeile und abloesen.",
        _schema(["id", "felder"], id=(S, "Claim-ID"),
                felder=(O, "Spalte -> Wert, z. B. {\"Oracle\": \"O1\", \"Confidence\": \"0.60\"}"),
                dry_run=DRY),
        lambda a: truth.setzen(a["id"], a["felder"], bool(a.get("dry_run")))),
    "truth_prio": (
        "Prio einer offenen Zeile setzen. Front (now) hoechstens 6.",
        _schema(["id", "prio"], id=(S, "Claim-ID"), prio=(S, "now|next|later|park"), dry_run=DRY),
        lambda a: truth.prio(a["id"], a["prio"], bool(a.get("dry_run")))),
    "truth_commit": (
        "Nur research/TRUTH.csv committen. Die Nachricht muss eine Claim-ID nennen und beschreibt "
        "den Weg: Kandidaten, Fehlversuche, warum so entschieden -- das ist das Laborjournal.",
        _schema(["nachricht"], nachricht=(S, "Commit-Nachricht mit Claim-ID")),
        lambda a: truth.commit(a["nachricht"])),
}


def antwort(mid, ergebnis=None, fehler=None):
    m = {"jsonrpc": "2.0", "id": mid}
    if fehler:
        m["error"] = fehler
    else:
        m["result"] = ergebnis
    sys.stdout.write(json.dumps(m, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def behandeln(nachricht):
    mid, methode = nachricht.get("id"), nachricht.get("method")
    if methode == "initialize":
        version = (nachricht.get("params") or {}).get("protocolVersion") or "2025-06-18"
        return antwort(mid, {"protocolVersion": version, "capabilities": {"tools": {}},
                             "serverInfo": {"name": "truth", "version": VERSION}})
    if mid is None:          # Benachrichtigungen (notifications/initialized u. a.): keine Antwort
        return
    if methode == "ping":
        return antwort(mid, {})
    if methode == "tools/list":
        return antwort(mid, {"tools": [{"name": n, "description": d, "inputSchema": s}
                                       for n, (d, s, _) in WERKZEUGE.items()]})
    if methode == "tools/call":
        p = nachricht.get("params") or {}
        name, args = p.get("name"), p.get("arguments") or {}
        if name not in WERKZEUGE:
            return antwort(mid, fehler={"code": -32602, "message": "unbekanntes Werkzeug %s" % name})
        try:
            text, fehlerhaft = str(WERKZEUGE[name][2](args)), False
        except truth.Abgelehnt as e:
            text, fehlerhaft = str(e), True
        except Exception:
            text, fehlerhaft = "Interner Fehler:\n" + traceback.format_exc(), True
        return antwort(mid, {"content": [{"type": "text", "text": text}], "isError": fehlerhaft})
    return antwort(mid, fehler={"code": -32601, "message": "unbekannte Methode %s" % methode})


def main():
    for zeile in sys.stdin:
        zeile = zeile.strip()
        if not zeile:
            continue
        try:
            nachricht = json.loads(zeile)
        except json.JSONDecodeError:
            antwort(None, fehler={"code": -32700, "message": "kein JSON"})
            continue
        behandeln(nachricht)


if __name__ == "__main__":
    main()
