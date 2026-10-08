#!/usr/bin/env python3
"""Prueft, ob Ghidra auf denselben Bytes arbeitet wie das Repo.

    python3 tools/scripts/ghidra_provenance.py

Jede Aussage, die aus Ghidra stammt, setzt stillschweigend voraus: das offene
Programm ist firmware/bin/ZK-INKJET-NANO-APP.bin, unveraendert. Das Skript
macht die Voraussetzung pruefbar. Es fragt das GhidraMCPd-Plugin direkt ab
(/projectInfo, kein MCP noetig) und vergleicht mit der Datei im Repo:

  1. Importhash des Programms gegen sha256 der Repo-Datei.
  2. patched: Bytes in der Datenbank gegenueber dem Import veraendert?
  3. Jeder dateigestuetzte Block: Hash des Blockinhalts gegen denselben
     Ausschnitt der Repo-Datei. Zeigt bei einem Patch, welcher Block betroffen ist.
  4. Wo liegt Dateioffset 0 in Ghidra, gemessen an der Linkbasis
     (CL-BOOT-REC-113). Ein Versatz verschiebt jede Adresse aus Ghidra.

Exitcode 0: stimmt oder ungeprueft (Ghidra nicht erreichbar, altes Plugin).
Exitcode 1: falsches Programm oder ein Block weicht ab, ohne dass die
Datenbank sich als gepatcht ausweist -- dann ist keine Ghidra-Adresse belastbar.

Braucht GhidraMCPd ab Commit c1119b5 (source_files, file_offset, sha256 je Block).
Aeltere Plugins liefern nur den Importhash; der wird trotzdem geprueft.
"""
import hashlib, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP = os.path.join(ROOT, "firmware", "bin", "ZK-INKJET-NANO-APP.bin")
URL = os.environ.get("GHIDRA_MCP_URL", "http://127.0.0.1:8080/").rstrip("/") + "/projectInfo"

# CL-BOOT-REC-113: APP.bin ist nach 0x00058000 gelinkt. Aendert sich die Zeile,
# hier nachziehen.
LINK_BASE = 0x00058000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fetch():
    try:
        with urllib.request.urlopen(URL, timeout=5) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return e


def check(app_path=APP, info=None, out=print):
    """Gibt (ok, zeilen) zurueck. ok=False heisst: Ghidra-Ergebnisse nicht belastbar."""
    lines = []
    say = lines.append
    if info is None:
        info = fetch()
    if isinstance(info, Exception) or not isinstance(info, dict):
        say("Ghidra nicht erreichbar (%s) -- Herkunft UNGEPRUEFT." % URL)
        return True, lines
    if "program_name" not in info:
        say("Plugin antwortet ohne Programm (%s) -- Herkunft UNGEPRUEFT." % str(info)[:80])
        return True, lines

    data = open(app_path, "rb").read()
    want = sha(data)
    ok = True
    name = info.get("program_name")
    got = (info.get("executable_sha256") or "").lower()
    if got == want:
        say("Programm %s = %s (%s...)" % (name, os.path.relpath(app_path, ROOT), want[:8]))
    else:
        ok = False
        say("ALARM: Programm %s ist NICHT %s" % (name, os.path.relpath(app_path, ROOT)))
        say("       Import %s... gegen Repo %s..." % (got[:8] or "?", want[:8]))

    files = info.get("source_files")
    if files is None:
        say("Plugin ohne Herkunftsfelder (vor GhidraMCPd c1119b5) -- nur Importhash geprueft.")
        return ok, lines

    patched = [f.get("name") for f in files if f.get("patched")]
    if patched:
        say("WARNUNG: Datenbank ist gepatcht (%s). Bytes aus Ghidra sind nicht die der Datei."
            % ", ".join(patched))

    for b in info.get("memory_blocks", []):
        off = b.get("file_offset")
        if off is None or b.get("source_file_index") is None:
            continue
        start = int(b["start"], 16)
        stueck = data[off:off + b["length"]]
        same = len(stueck) == b["length"] and sha(stueck) == b.get("sha256")
        mark = "gleich" if same else "WEICHT AB"
        say("Block %-8s %s <- Datei+0x%X, 0x%X Bytes, Inhalt %s"
            % (b.get("name"), b["start"], off, b["length"], mark))
        if not same and not patched:
            ok = False
            say("ALARM: Block %s weicht von der Datei ab, obwohl patched=false." % b.get("name"))
        if off == 0:
            delta = start - LINK_BASE
            if delta:
                say("Dateianfang liegt bei %s, Linkbasis ist 0x%08X (CL-BOOT-REC-113): "
                    "Ghidra-Adresse = Linkadresse %+#x. Offen in CL-TOOL-REC-121."
                    % (b["start"], LINK_BASE, delta))
            else:
                say("Dateianfang liegt auf der Linkbasis 0x%08X." % LINK_BASE)
    return ok, lines


def main(argv):
    app = argv[1] if len(argv) > 1 else APP
    ok, lines = check(app)
    for line in lines:
        print("  " + line)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
