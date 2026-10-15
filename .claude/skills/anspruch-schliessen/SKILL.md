---
name: anspruch-schliessen
description: Schliesst eine Zeile in research/TRUTH.csv (Decided no -> yes) oder legt eine neue an. Verwenden bei jedem "das ist jetzt geklaert", "trag das ein", "Zeile schliessen", "neuer Befund", "CL-...-REC-... ist beantwortet" -- und immer dann, wenn eine Untersuchung im ZK-Inkjet-Projekt ein Ergebnis hat, das ins Register soll. Vergibt Oracle-Stufe und Konfidenz, prueft Abhaengige und reicht Abloesungen durch.
---

# Einen Anspruch schliessen

Der Moment, in dem eine Zeile von `Decided=no` auf `yes` geht, ist der einzige,
in dem in diesem Projekt Wissen entsteht. Historisch ist genau dort alles
schiefgegangen: nicht durch zu wenig Untersuchung, sondern durch zu grosszuegiges
Schliessen und durch Abloesungen, die niemand durchgereicht hat.

**TRUTH.md sagt, was erlaubt ist. Dieser Skill sagt, in welcher Reihenfolge es
getan wird.** Bei Widerspruch gewinnt TRUTH.md.

## Schritt 1 -- Oracle-Stufe vergeben, vor der Konfidenz

Nicht "wie sicher bin ich", sondern "was hat es geprueft". Die Stufe bestimmt
die Obergrenze der Konfidenz; innerhalb der Grenze wird geschaetzt.

| Stufe | Was dahintersteht | Deckel |
|---|---|---|
| **O1** | hergeleitet aus anderen Zeilen, aus Doku, aus Plausibilitaet. Nichts gemessen. | 0.60 |
| **O2** | ein wiederholbares Kommando ueber eine Datei auf der Platte erzeugt die Aussage. | 0.95 |
| **O3** | das Geraet hat sich beobachtbar so verhalten, wie die Zeile es vorhersagt. | 1.00 |

**Die schaerfste Regel steht hier:** O2 gilt nur, wenn die Aussage *das ist, was
das Kommando ausgibt*. Sobald die Zeile darueber hinausgeht -- Identitaet,
Zweck, Bedeutung, "das ist die aktive APP.bin", "das ist der Dispatcher" --
ist sie **O1**, egal wie sauber gemessen wurde.

Das ist keine Theorie. `CL-BOOT-REC-007` sagte "APP.bin liegt bei 0x100000 mit
ARM-IVT", Konfidenz 0.95, Autoritaet E0. Die IVT war gemessen, die Zuordnung
war geraten -- und falsch. Neun der bisher fuenfzehn abgeloesten Zeilen standen
auf E0, drei bei 0.95 und hoeher. Die gestuerzten Zeilen waren im Schnitt die
selbstsichersten.

## Schritt 2 -- Evidenz ist das Kommando, nicht seine Beschreibung

In `Evidence_E0` gehoert etwas, das jemand ausfuehren kann: der Aufruf und die
Datei. Nicht "Bytesuche zeigt zwei Treffer", sondern das, womit man auf zwei
Treffer kommt. Wer kein solches Kommando angeben kann, hat keine O2-Zeile.

Bei O3: welcher Vorgang am Geraet, welche Karte, welches Dump-Paar, welcher
Diff. Die Testkarte ist nicht die Originalkarte (`CL-TOOL-REC-106`) und die
laufende Firmware ist ein wiederhergestellter Build vom 9. Dezember 2022, nicht
belegt ab Werk (`CL-BOOT-REC-115`, `CL-STORAGE-REC-105`) -- beides gehoert in
die Zeile, wenn es die Aussage beruehrt.

## Schritt 3 -- Negativbefund braucht seine Positivkontrolle

Eine Zeile, die sagt "X kommt nicht vor" / "es gibt keinen Verweis auf Y",
nennt in derselben Zeile die Kontrolle, mit der dieselbe Methode etwas Bekanntes
gefunden hat. Ohne bestandene Kontrolle ist die Stufe **O1**, unabhaengig vom
Aufwand.

Warum das hier so hart steht: `CONTRADICTION-USB-001` galt sieben Monate als
projektblockierend, weil Ghidras Scalar-Suche Poolworte nicht sieht und niemand
die Methode geprueft hat. Und Konstanten stehen in dieser Firmware in beiden
Formen -- `0x2A614000` nur als Literal, `0x28800000` nur als MOV-Immediate.
Wer einen Modus laufen laesst und nichts findet, hat nichts gemessen
(`CL-TOOL-REC-101`, `-108`, `-114`).

## Schritt 4 -- Depends_On setzen

Worauf steht diese Zeile? Nur echte Traeger: Adressbasen, Geometrien,
Methodenzeilen, Provenienz. Nicht "gleiches Subsystem".

Die Probe: **Wenn die genannte Zeile falsch waere -- faellt diese hier mit?**
Nur dann gehoert sie hinein.

## Schritt 5 -- Abloesung durchreichen (der Schritt, der uebersprungen wird)

Wenn diese Zeile eine andere abloest:

1. `Superseded_By` in der alten Zeile setzen. Zeilen werden nie geloescht.
2. **Alle Zeilen suchen, die auf die alte zeigen**, und einzeln pruefen, ob sie
   die Abloesung ueberleben:
   `grep -n 'CL-ALTE-ID' research/TRUTH.csv`
3. Depends_On auf die Nachfolgerin umhaengen. **Das Umhaengen ist die Pruefung** --
   wer umhaengt, ohne gelesen zu haben, verschiebt den Fehler nur.
4. Faellt eine abhaengige Zeile mit, wird sie ebenfalls abgeloest, nicht editiert.

`check_truth.py` erzwingt Schritt 3: eine Zeile darf nicht an einer abgeloesten
haengen. Der Validator merkt aber nicht, ob wirklich gelesen wurde.

## Schritt 6 -- Die Zelle auf das Urteil bringen

Die Zeile sagt, was gilt und worauf es steht: Urteil zuerst, dann die
tragenden Belege. Kandidaten, Fehlversuche und Zwischenstaende gehoeren in die
Commit-Nachricht mit der Claim-ID -- der Git-Log ist das Laborjournal dieses
Projekts. Ein Ergebnis, das fuer sich gilt, wird eine eigene Zeile, kein
weiterer Absatz.

Grenzen ab 2026-10-16: `Statement` 2000 Zeichen, `Next_Test` 1000. Wer eine
laengere Altzeile anfasst, kuerzt sie dabei auf das Urteil. Der Weg ist nicht
verloren: `git log --date=short --format='%ad %h %s' | grep <Claim-ID>`.

Warum: im Januar wanderte die Arbeit aus der Matrix in Prosadokumente, im
Oktober in die Zellen. CL-USB-REC-128 hatte 28 428 Zeichen -- die Antwort
stand im ersten Satz, der Rest war das Protokoll von 30 Commits.

## Schritt 7 -- Front nachziehen und schreiben

Geschlossene Zeile: `Decided=yes`, `Prio` leeren, `Updated` auf heute,
`Next_Test` leeren. Aus `next` nachruecken, hoechstens 6 auf `now`.

**TRUTH.csv wird atomar geschrieben** -- Temporaerdatei, Ergebnis pruefen,
`os.replace`. Nie `open(P,'w')`: das kuerzt die Datei, bevor irgendein assert
greift, und genau so war sie schon einmal null Bytes gross.

Danach `python3 tools/scripts/check_truth.py`. Sauber, dann committen.

## Wenn eine Zeile sich nicht schliessen laesst

Zwei Sitzungen ohne Fortschritt heissen: die Frage ist falsch gestellt, nicht
zu schwer. Dann nicht weiterbohren, sondern `Next_Test` neu schreiben oder die
Zeile in zwei Zeilen zerlegen. Auch das ist Fortschritt und gehoert ins Register.
