#!/usr/bin/env python3
"""Positiv- und Negativkontrollen fuer check_privat.py.

Baut ein Wegwerf-Repository mit einem nackten "Remote", legt nacheinander
saubere und verunreinigte Commits an und prueft, dass check_privat.py genau
die verunreinigten anhaelt -- ueber --bereich und ueber die stdin-Zeilen des
pre-push-Hooks. Login, Hostname und Heimatverzeichnis werden wie im Skript zur
Laufzeit ermittelt; private Zeichenketten stehen deshalb nirgends in dieser
Datei.

    python3 tools/scripts/check_privat_selbsttest.py
"""
import getpass, gzip, io, os, socket, subprocess, sys, tempfile, zipfile

HIER = os.path.dirname(os.path.abspath(__file__))
SKRIPT = os.path.join(HIER, "check_privat.py")
NULL = "0" * 40
NOREPLY = "test@users.noreply.github.com"
# Beispieladresse zur Laufzeit zusammengesetzt, sonst haelt der Hook diese Datei an
MAC = ":".join(["02", "1a", "2b", "3c", "4d", "5e"])


def git(cwd, *args, eingabe=None):
    r = subprocess.run(["git", *args], cwd=cwd, input=eingabe, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("git %s: %s" % (" ".join(args), r.stderr))
    return r.stdout.strip()


class Lauf:
    def __init__(self):
        self.fehler = 0
        self.n = 0
        self.tmp = tempfile.mkdtemp(prefix="check_privat_")
        self.remote = os.path.join(self.tmp, "remote.git")
        self.repo = os.path.join(self.tmp, "repo")
        git(self.tmp, "init", "-q", "--bare", self.remote)
        git(self.tmp, "init", "-q", self.repo)
        for k, v in (("user.name", "Test"), ("user.email", NOREPLY), ("commit.gpgsign", "false"),
                     ("core.hooksPath", "/dev/null")):
            git(self.repo, "config", k, v)
        git(self.repo, "remote", "add", "origin", self.remote)
        self.commit({"liesmich.txt": b"sauber\n"}, "start")
        git(self.repo, "push", "-q", "origin", "HEAD:refs/heads/master")
        git(self.repo, "fetch", "-q", "origin")
        self.basis = git(self.repo, "rev-parse", "HEAD")

    def commit(self, dateien, nachricht, autor=None):
        for pfad, inhalt in dateien.items():
            p = os.path.join(self.repo, pfad)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb").write(inhalt)
            git(self.repo, "add", pfad)
        env = ["-c", "user.email=" + autor] if autor else []
        git(self.repo, *env, "commit", "-q", "-m", nachricht)
        return git(self.repo, "rev-parse", "HEAD")

    def zurueck(self):
        git(self.repo, "reset", "-q", "--hard", self.basis)

    def pruefe(self, was, erwartet, *args, eingabe=None, env=None):
        self.n += 1
        e = dict(os.environ, **(env or {}))
        r = subprocess.run([sys.executable, SKRIPT, *args], cwd=self.repo, input=eingabe,
                           capture_output=True, text=True, env=e)
        ok = r.returncode == erwartet
        print("  %s %-62s exit %d (erwartet %d)" % ("ok  " if ok else "FEHL", was, r.returncode, erwartet))
        if not ok:
            self.fehler += 1
            print("      " + (r.stderr.strip().replace("\n", "\n      ") or "(keine Ausgabe)"))

    def fall(self, was, erwartet, dateien=None, nachricht="aenderung", autor=None, muster=()):
        """Ein Commit auf der Basis, geprueft per --bereich und per pre-push."""
        self.zurueck()
        spitze = self.commit(dateien or {"x.txt": b"neutral %d\n" % self.n}, nachricht, autor)
        extra = [a for m in muster for a in ("--muster", m)]
        self.pruefe(was + " [--bereich]", erwartet, "--bereich", self.basis + "..HEAD", *extra)
        zeile = "refs/heads/master %s refs/heads/master %s\n" % (spitze, self.basis)
        self.pruefe(was + " [pre-push]", erwartet, "--pre-push", "origin", *extra, eingabe=zeile)


def zip_mit(name, inhalt):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr(name, inhalt)
    return b.getvalue()


def main():
    login = getpass.getuser()
    host = socket.gethostname().split(".")[0]
    heim = os.path.expanduser("~")
    print("Muster aus der Umgebung: Login (%d Zeichen), Hostname (%d Zeichen), Heimatverzeichnis"
          % (len(login), len(host)))
    L = Lauf()
    try:
        print("Negativkontrollen (muessen durchgehen):")
        L.fall("sauberer Commit", 0)
        L.fall("Platzhalter $HOME/, user@host, xx:xx:...", 0,
               {"a.md": b"$HOME/workspace/x user@host:~ xx:xx:xx:xx:xx:xx\n"})
        L.fall("Null- und Broadcast-MAC", 0, {"a.md": b"00:00:00:00:00:00 ff:ff:ff:ff:ff:ff\n"})
        L.fall("Hexdump mit mehr als sechs Bytes", 0, {"a.md": b"01:02:03:04:05:06:07:08\n"})
        L.fall("GitHub-Webcommit (noreply@github.com)", 0, autor="noreply@github.com")
        L.fall("Lokales Muster mit erlaubt-Ausnahme", 0, {"a.md": b"Geheimwort-ok\n"},
               muster=("Geheimwort", "erlaubt: ^Geheimwort$"))
        print("Positivkontrollen (muessen anhalten):")
        L.fall("Login im Text", 1, {"a.md": ("Pfad: /srv/%s/x\n" % login).encode()})
        L.fall("Hostname im Text", 1, {"a.md": ("prompt %s:~$\n" % host.upper()).encode()})
        L.fall("Heimatverzeichnis", 1, {"a.sh": ("dd if=%s/x.bin\n" % heim).encode()})
        L.fall("BSSID in dmesg-Zeile", 1, {"a.md": b"wlan0: RX AssocResp from " + MAC.encode() + b"\n"})
        L.fall("MAC mit Bindestrichen", 1, {"a.md": MAC.upper().replace(":", "-").encode() + b"\n"})
        L.fall("Login in gzip", 1, {"a.txt.gz": gzip.compress(login.encode())})
        L.fall("Hostname in zip", 1, {"a.zip": zip_mit("log.txt", host.encode())})
        L.fall("Login in UTF-16", 1, {"a.bin": login.encode("utf-16-le")})
        L.fall("Login im Dateinamen", 1, {"daten/%s.txt" % login: b"x\n"})
        L.fall("Login in der Commit-Nachricht", 1, nachricht="Notiz fuer %s" % login)
        L.fall("private Autor-Adresse", 1, autor="jemand@example.org")
        L.fall("lokales Muster (--muster)", 1, {"a.md": b"Geheimwort\n"}, muster=("Geheimwort",))

        print("Sonderfaelle:")
        L.zurueck()
        spitze = L.commit({"a.md": ("%s\n" % login).encode()}, "x")
        L.pruefe("Ref-Loeschung bringt nichts Neues", 0, "--pre-push", "origin",
                 eingabe="refs/heads/x %s refs/heads/x %s\n" % (NULL, spitze))
        L.pruefe("Umgehung CHECK_PRIVAT=aus", 0, "--pre-push", "origin",
                 eingabe="refs/heads/master %s refs/heads/master %s\n" % (spitze, L.basis),
                 env={"CHECK_PRIVAT": "aus"})
        L.pruefe("neuer Branch (Remote-SHA null) wird geprueft", 1, "--pre-push", "origin",
                 eingabe="refs/heads/neu %s refs/heads/neu %s\n" % (spitze, NULL))
        # Was schon auf dem Remote liegt, ist oeffentlich und wird nicht erneut gemeldet
        git(L.repo, "push", "-q", "origin", "HEAD:refs/heads/alt")
        git(L.repo, "fetch", "-q", "origin")
        sauber = L.commit({"b.md": b"sauber\n"}, "sauber")
        L.pruefe("Altlast auf dem Remote, neuer Commit sauber", 0, "--pre-push", "origin",
                 eingabe="refs/heads/alt %s refs/heads/alt %s\n" % (sauber, spitze))
        info = os.path.join(git(L.repo, "rev-parse", "--git-common-dir"), "info")
        os.makedirs(os.path.join(L.repo, info), exist_ok=True)
        open(os.path.join(L.repo, info, "privat-muster"), "w").write("# Kommentar\n(?i)geheimwort\n")
        L.zurueck()
        s = L.commit({"a.md": b"GEHEIMWORT\n"}, "x")
        L.pruefe("Muster aus .git/info/privat-muster", 1, "--bereich", L.basis + "..HEAD")
        open(os.path.join(L.repo, info, "privat-muster"), "a").write("erlaubt: ^GEHEIMWORT$\n")
        L.pruefe("... und per erlaubt-Zeile ausgenommen", 0, "--bereich", L.basis + "..HEAD")
        open(os.path.join(L.repo, info, "privat-muster"), "a").write("(kaputt\n")
        L.pruefe("ungueltiger Ausdruck haelt an (exit 2)", 2, "--bereich", L.basis + "..HEAD")
        os.remove(os.path.join(L.repo, info, "privat-muster"))

        print("Hook durchgehend (git push an das Wegwerf-Remote, mit git lfs pre-push):")
        hooks = os.path.join(L.repo, ".githooks")
        os.makedirs(hooks)
        os.makedirs(os.path.join(L.repo, "tools", "scripts"))
        open(os.path.join(hooks, "pre-push"), "w").write(
            open(os.path.join(HIER, "..", "..", ".githooks", "pre-push")).read())
        os.chmod(os.path.join(hooks, "pre-push"), 0o755)
        open(os.path.join(L.repo, "tools", "scripts", "check_privat.py"), "w").write(open(SKRIPT).read())
        git(L.repo, "config", "core.hooksPath", ".githooks")
        for was, inhalt, erwartet in (("verunreinigter Push wird abgewiesen", login, False),
                                      ("sauberer Push geht durch", "sauber", True)):
            L.n += 1
            L.zurueck()
            spitze = L.commit({"h.md": ("%s\n" % inhalt).encode()}, "hook")
            r = subprocess.run(["git", "push", "-q", "origin", "HEAD:refs/heads/master"], cwd=L.repo,
                               capture_output=True, text=True)
            angekommen = git(L.remote, "rev-parse", "refs/heads/master") == spitze
            ok = (r.returncode == 0) == erwartet and angekommen == erwartet
            print("  %s %-62s push exit %d, Remote %s" % ("ok  " if ok else "FEHL", was, r.returncode,
                                                         "aktualisiert" if angekommen else "unveraendert"))
            if not ok:
                L.fehler += 1
                print("      " + r.stderr.strip().replace("\n", "\n      "))
            if angekommen:
                git(L.repo, "fetch", "-q", "origin")
                L.basis = spitze
    finally:
        subprocess.run(["rm", "-rf", L.tmp])
    print()
    if L.fehler:
        print("%d von %d Kontrollen FEHLGESCHLAGEN" % (L.fehler, L.n))
        return 1
    print("Alle Kontrollen bestanden (%d)." % L.n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
