#!/usr/bin/env python3
"""Prueft Commits vor dem Push auf private Daten.

Exit 0 = nichts gefunden, 1 = Fund, 2 = Pruefung nicht moeglich. Gedacht als
pre-push-Hook (.githooks/pre-push) und fuer Handlaeufe:

    python3 tools/scripts/check_privat.py --bereich origin/master..HEAD
    python3 tools/scripts/check_privat.py --pre-push origin < zeilen

Hintergrund: Zweimal sind Login, Hostname, Vorname, absolute Heimatpfade und
eine WLAN-BSSID unbemerkt in Commits gelandet und erst vor dem Push aufgefallen
(Dezember 2025, Oktober 2026). Eine Datei, die im Arbeitsbaum nicht mehr steht,
steht trotzdem in der Historie -- deshalb prueft dieses Skript jedes neue
Objekt der ausgehenden Commits, nicht den Arbeitsbaum.

Geprueft werden alle Blobs, die die ausgehenden Commits neu mitbringen (auch
in zip/gz/xz/bz2 und in lokal vorhandenen LFS-Objekten), Dateipfade,
Commit-Nachrichten und Autor-/Committer-Adressen. Was schon auf dem Remote
liegt, wird nicht geprueft; das ist ohnehin oeffentlich.

Die Muster stehen bewusst nicht in dieser Datei, denn sie wird
veroeffentlicht:
  - Login, Hostname und Heimatverzeichnis werden zur Laufzeit ermittelt.
  - MAC-Adressen/BSSIDs (sechs Hexbytes mit ':' oder '-') sind ein festes
    Muster.
  - Weitere Muster (Vorname, Nachname, private Verzeichnisse) stehen lokal in
    .git/info/privat-muster, ein regulaerer Ausdruck je Zeile, '#' Kommentar.
    'erlaubt: <regex>' nimmt Treffer davon aus, 'email-erlaubt: <regex>'
    erlaubt weitere Autor-Adressen.

Umgehen (nur bewusst): CHECK_PRIVAT=aus git push ...
"""
import argparse, bz2, getpass, gzip, io, lzma, os, re, socket, subprocess, sys, zipfile

NULL = "0" * 40
EMAIL_ERLAUBT = [r"@users\.noreply\.github\.com$"]
# Platzhalter und Broadcast sind keine Geraeteadressen
MAC_ERLAUBT = [r"(?i)^(00[:-]){5}00$", r"(?i)^(ff[:-]){5}ff$"]
MAX_ENTPACKT = 256 * 1024 * 1024


def git(*args, eingabe=None, roh=False):
    r = subprocess.run(["git", *args], input=eingabe, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.decode("utf-8", "replace").strip()))
    return r.stdout if roh else r.stdout.decode("utf-8", "replace")


def muster_laden(extra):
    """Liefert (Liste (Name, regex-bytes), erlaubt-Liste, email-erlaubt-Liste)."""
    muster = []
    login = getpass.getuser()
    host = socket.gethostname().split(".")[0]
    heim = os.path.expanduser("~")
    for name, wert in (("Login", login), ("Hostname", host)):
        # sehr kurze Namen wuerden ueberall treffen
        if wert and len(wert) >= 4 and wert not in ("user", "root", "host", "localhost"):
            muster.append((name, re.compile(rb"(?i)" + re.escape(wert.encode()))))
            muster.append((name + " (UTF-16)", re.compile(re.escape(wert.encode("utf-16-le")))))
    if heim and heim not in ("/", "/root"):
        muster.append(("Heimatverzeichnis", re.compile(re.escape(heim.encode()))))
    muster.append(("MAC/BSSID", re.compile(
        rb"(?<![0-9A-Fa-f:-])(?:[0-9A-Fa-f]{2}([:-]))(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}(?![0-9A-Fa-f:-])")))
    erlaubt = [re.compile(x.encode()) for x in MAC_ERLAUBT]
    email_erlaubt = [re.compile(x) for x in EMAIL_ERLAUBT]

    pfad = os.path.join(git("rev-parse", "--git-common-dir").strip(), "info", "privat-muster")
    zeilen = list(extra)
    if os.path.exists(pfad):
        zeilen += [z.rstrip("\n") for z in open(pfad, encoding="utf-8")]
    for z in zeilen:
        z = z.strip()
        if not z or z.startswith("#"):
            continue
        try:
            if z.startswith("erlaubt:"):
                erlaubt.append(re.compile(z[8:].strip().encode()))
            elif z.startswith("email-erlaubt:"):
                email_erlaubt.append(re.compile(z[14:].strip()))
            else:
                muster.append(("lokales Muster", re.compile(z.encode())))
        except re.error as e:
            raise RuntimeError("ungueltiger Ausdruck in %s: %r (%s)" % (pfad, z, e))
    return muster, erlaubt, email_erlaubt


def treffer(daten, muster, erlaubt):
    gefunden = []
    for name, rx in muster:
        for m in rx.finditer(daten):
            s = m.group(0)
            if any(e.search(s) for e in erlaubt):
                continue
            gefunden.append((name, s.decode("utf-8", "replace")))
    return gefunden


def entpacken(daten, tiefe=0):
    """Liefert (Bezeichnung, Inhalt) fuer komprimierte Inhalte, rekursiv."""
    if tiefe > 3:
        return []
    aus = []
    try:
        if daten[:4] == b"PK\x03\x04":
            z = zipfile.ZipFile(io.BytesIO(daten))
            for info in z.infolist():
                if info.file_size > MAX_ENTPACKT:
                    continue
                inhalt = z.read(info.filename)
                aus.append(("zip:" + info.filename, info.filename.encode() + b"\n" + inhalt))
                aus += [("zip:" + info.filename + "!" + b, d) for b, d in entpacken(inhalt, tiefe + 1)]
        else:
            inhalt = None
            if daten[:2] == b"\x1f\x8b":
                inhalt = gzip.decompress(daten)
            elif daten[:6] == b"\xfd7zXZ\x00":
                inhalt = lzma.decompress(daten)
            elif daten[:3] == b"BZh":
                inhalt = bz2.decompress(daten)
            if inhalt is not None:
                aus.append(("entpackt", inhalt))
                aus += [("entpackt!" + b, d) for b, d in entpacken(inhalt, tiefe + 1)]
    except Exception:
        pass  # kein gueltiges Archiv; der Rohinhalt wird ohnehin geprueft
    return aus


def bereiche_aus_pre_push(remote, zeilen):
    """Aus den stdin-Zeilen des pre-push-Hooks: (Spitzen, Ausschluesse).

    Ausgeschlossen wird, was der Remote schon hat: sein bisheriger Stand des
    Refs und alle Remote-Tracking-Refs dieses Remotes."""
    spitzen, aus = [], ["--remotes=" + remote] if remote else []
    for z in zeilen:
        teile = z.split()
        if len(teile) != 4:
            continue
        lokal_sha, remote_sha = teile[1], teile[3]
        if lokal_sha == NULL:
            continue  # Loeschen eines Refs bringt nichts Neues
        spitzen.append(lokal_sha)
        if remote_sha != NULL and subprocess.run(["git", "cat-file", "-e", remote_sha + "^{commit}"],
                                                 capture_output=True).returncode == 0:
            aus.append(remote_sha)
    return spitzen, aus


def pruefen(spitzen, aus, muster, erlaubt, email_erlaubt):
    funde = []  # (Ort, Name, Treffer)
    if not spitzen:
        return funde
    objekte = git("rev-list", "--objects", *spitzen, "--not", *aus)
    pfade = {}
    for z in objekte.splitlines():
        sha, _, pfad = z.partition(" ")
        if pfad:
            pfade.setdefault(sha, pfad)
            for name, s in treffer(pfad.encode(), muster, erlaubt):
                funde.append(("Pfadname " + pfad, name, s))
    if pfade:
        typen = git("cat-file", "--batch-check", eingabe="\n".join(pfade).encode())
        blobs = [z.split()[0] for z in typen.splitlines() if z.split()[1] == "blob"]
    else:
        blobs = []
    lfs_dir = os.path.join(git("rev-parse", "--git-common-dir").strip(), "lfs", "objects")
    proc = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for sha in blobs:
        proc.stdin.write((sha + "\n").encode())
        proc.stdin.flush()
        groesse = int(proc.stdout.readline().split()[2])
        daten = proc.stdout.read(groesse)
        proc.stdout.read(1)
        teile = [("", daten)] + entpacken(daten)
        if daten.startswith(b"version https://git-lfs"):
            m = re.search(rb"oid sha256:([0-9a-f]{64})", daten)
            if m:
                oid = m.group(1).decode()
                p = os.path.join(lfs_dir, oid[:2], oid[2:4], oid)
                if os.path.exists(p):
                    lfs = open(p, "rb").read()
                    teile += [("LFS", lfs)] + [("LFS!" + b, d) for b, d in entpacken(lfs)]
        for bez, inhalt in teile:
            for name, s in treffer(inhalt, muster, erlaubt):
                funde.append(("Blob %s %s%s" % (sha[:10], pfade[sha], " [" + bez + "]" if bez else ""), name, s))
    proc.stdin.close()
    proc.wait()

    log = git("log", "--format=%H%x00%an <%ae>%x00%cn <%ce>%x00%B%x01", *spitzen, "--not", *aus)
    for satz in log.split("\x01"):
        satz = satz.strip("\n")
        if not satz:
            continue
        h, autor, committer, text = satz.split("\x00", 3)
        for rolle, wer in (("Autor", autor), ("Committer", committer)):
            adresse = wer[wer.rfind("<") + 1:-1]
            if not any(e.search(adresse) for e in email_erlaubt):
                funde.append(("Commit %s" % h[:10], rolle + "-Adresse", adresse))
            for name, s in treffer(wer.encode(), muster, erlaubt):
                funde.append(("Commit %s %s" % (h[:10], rolle), name, s))
        for name, s in treffer(text.encode(), muster, erlaubt):
            funde.append(("Commit-Nachricht %s" % h[:10], name, s))
    return funde


def commits_zu_blob(sha, spitzen, aus):
    try:
        r = git("log", "--format=%h", "--find-object=" + sha, *spitzen, "--not", *aus)
        return r.split()
    except RuntimeError:
        return []


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--bereich", help="Commit-Bereich, z. B. origin/master..HEAD")
    g.add_argument("--pre-push", metavar="REMOTE", help="Ref-Zeilen des pre-push-Hooks von stdin lesen")
    ap.add_argument("--muster", action="append", default=[],
                    help="zusaetzlicher Ausdruck (wie eine Zeile in .git/info/privat-muster)")
    a = ap.parse_args()

    if os.environ.get("CHECK_PRIVAT", "").lower() in ("aus", "0", "off"):
        print("check_privat: per CHECK_PRIVAT=aus uebersprungen.", file=sys.stderr)
        return 0
    try:
        muster, erlaubt, email_erlaubt = muster_laden(a.muster)
        if a.bereich:
            if ".." in a.bereich:
                basis, spitze = a.bereich.split("..", 1)
                spitzen, aus = [spitze or "HEAD"], [basis or "HEAD"]
            else:
                spitzen, aus = [a.bereich], []
        else:
            spitzen, aus = bereiche_aus_pre_push(a.pre_push, sys.stdin.read().splitlines())
        funde = pruefen(spitzen, aus, muster, erlaubt, email_erlaubt)
    except RuntimeError as e:
        print("check_privat: Pruefung nicht moeglich -- %s" % e, file=sys.stderr)
        print("Der Push wird vorsichtshalber angehalten. Umgehen nur bewusst: CHECK_PRIVAT=aus git push ...",
              file=sys.stderr)
        return 2

    if not funde:
        return 0
    print("\ncheck_privat: %d Fund(e) mit privaten Daten in den ausgehenden Commits:\n" % len(funde),
          file=sys.stderr)
    gesehen = set()
    for ort, name, s in funde:
        if (ort, name, s) in gesehen:
            continue
        gesehen.add((ort, name, s))
        zusatz = ""
        if ort.startswith("Blob "):
            c = commits_zu_blob(ort.split()[1], spitzen, aus)
            # --find-object nennt auch Commits, die den Blob wieder entfernen;
            # der aelteste ist der, der ihn eingefuehrt hat
            zusatz = "  (erstmals in %s)" % c[-1] if c else ""
        print("  %-14s %-40s in %s%s" % (name, repr(s)[:40], ort, zusatz), file=sys.stderr)
    print("""
Was das bedeutet: Diese Daten wuerden mit der Historie veroeffentlicht, auch
wenn sie im Arbeitsbaum laengst nicht mehr stehen.
Was zu tun ist: In ungepushten Commits mit git filter-repo --replace-text
bereinigen (Konvention: research/sessions/README.md, Abschnitt Anonymization
Rules), nicht mit einem Folgecommit. Ist ein Treffer harmlos, eine Zeile
'erlaubt: <regex>' in .git/info/privat-muster eintragen.""", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
