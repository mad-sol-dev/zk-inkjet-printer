# Sitzung 2026-08-22 — Abhängigkeitsgraph, Oracle-Stufen, Encoder aufgelöst

Nicht autoritativ. Autoritativ ist `research/TRUTH.csv`.
Commits: `8a0e1f0` bis `128824c` (9 Stück, nicht gepusht).

## Was am Register gebaut wurde

**`Depends_On`** — Claim-IDs, auf denen eine Zeile steht. Gesetzt für die 28
Zeilen der Schichten 1 und 2. Macht tragende Zeilen zählbar: `CL-BOOT-REC-111`
(Ladebasis 0x00200000) trägt sieben.

**`Oracle`** — O1 hergeleitet (Deckel c=0.60), O2 wiederholbares Kommando über
eine Datei (0.95), O3 beobachtetes Geräteverhalten (1.00). Die scharfe Kante
liegt zwischen O1 und O2: **geht die Zeile über das hinaus, was das Kommando
ausgibt — Identität, Zweck, Bedeutung — ist sie O1, auch bei sauberer Messung.**
Pflicht und Deckel gelten nur für Zeilen mit `Updated` ab 2026-08-22.

Anlass war eine Messung am eigenen Register: von den damals 15 abgelösten Zeilen
trugen **neun die Autoritätsstufe E0**, drei bei c≥0.95. Die gestürzten Zeilen
waren im Schnitt die selbstsichersten.

**Vier Validatorregeln** in `check_truth.py`, alle gegen künstlich verletzte
Kopien getestet: Depends_On zeigt auf existierende Zeilen, keine Selbstbezüge,
kein Zyklus, und — der eigentliche Punkt — **keine Zeile darf an einer abgelösten
hängen**. Wer `Superseded_By` setzt, muss die Abhängigen umhängen; das Umhängen
ist die Prüfung. Dazu: Zellen dürfen nicht auf `...` enden.

**Skill** `.claude/skills/anspruch-schliessen/SKILL.md` — der Ablauf beim
Schließen einer Zeile. `.gitignore` lässt `.claude/skills/` jetzt zu.

**Getrennte Zählung.** `TRUTH.csv | GERAET 227 (...) | WERKZEUG 38 (3 davon
tragend)`. Grund: `park` ist ein Wert von `Prio`, und `Prio` ist bei
entschiedenen Zeilen leer — eine Werkzeugzeile war nur so lange als
Nicht-Wissen erkennbar, wie sie offen war.

## Reparaturen

**51 abgeschnittene Zellen** wiederhergestellt. Die Januar-Reconciliation hatte
`Statement` bei exakt 120 und `Next_Test` bei exakt 80 Zeichen gekappt. Volltext
lag in `research/docs_rebuild/reconciliation/RECONCILED_claims_*.md`. Der erste
Durchgang erklärte 19 für nicht rekonstruierbar — falsch: die Matrix hatte beim
Import **Kommas durch Semikolons ersetzt**, weshalb kein Fragment wörtlich passte.
Mit Komma-Varianten waren alle 19 sofort auffindbar.

Der teuerste Einzelfall: `CL-USB-REC-011` verlor genau den Teil seines Tests, der
die Zweimodus-Suche verlangt — *„(MOV/MOVT or base+offset patt…"*. Die Auflösung
von CONTRADICTION-USB-001 stand als Handlungsanweisung im Register, unlesbar.

## Inhaltliche Befunde

**CL-USB-REC-013 widerlegt** — kein SPI-Flash auf der Platine. Zwei Fotos:
APM4958A (Dual-MOSFET) und ein QFN-10 „30502/E09XAA". Der SCSI-String
„W55FA93 SPI Disk" ist der Vorgabewert der Nuvoton-MSC-Bibliothek
(`UDC/src/MSC/mscd.c`, `w55fa93_MSC_SPI.lib`), keine Hardwarebeschreibung.

**CL-SOC-REC-002 geschlossen (O3)** — das LQFP-128 trägt
„M5 / dwin.com.cn / 2728M0142 / 1728" und ist der Hauptprozessor. Warum ein
Nuvoton-Die DWIN-Branding trägt, bleibt offen; die Zeile dokumentiert, erklärt
nicht. Der DWIN/T5L-Faden wurde im Dezember 2025 nach Plausibilität aufgegeben,
nicht widerlegt — steht als Notiz in `CL-BOOT-REC-022`.

**0xB8003000 ist RTC_BA, nicht GPIO** (`CL-SOC-REC-021`). Derselbe Zahlendreher
steht in **drei** Findings vom 2025-12-20 (0024, 0025, 0027), jeweils als
`verified` mit Konfidenz 1.0. Gemessene D/C-Basis ist GPIO_BA+0x38 =
REG_GPIOD_DOUT, Bit 13, also GPD[13]. Jede CL-DISPLAY-Zeile, die von diesen
Findings abstammt, braucht eine Nachprüfung ihrer MMIO-Basen.

**Der Encoder hängt am Interrupt** (`CL-HARDWARE-REC-112`, O2). VA 0x231F30
gehört zu FUN_00231EC4, einem portgenerischen Pinleser; die Maske entsteht als
`1<<param_2`. Genau ein Aufrufer übergibt Port E: FUN_0026FBF8 mit **Bit 9**.
GPE[10] (Pin 117, MT6701) wird bei 0x25C3A0 mit Modus 0x23 konfiguriert und
nimmt den IRQ-Zweig — `1<<irq` nach AIC_BA+0x120. Pin 117 hat keine
Capture-Hardware, der MT6701 sendet PWM, also wertet die Firmware ihn per
Flankeninterrupt plus dem 64-Bit-Tick bei 0xC18 aus. Der Handler ist noch nicht
identifiziert (`CL-SOC-REC-022`, offen).

**Die Drucktaste hat einen Codepfad** (`CL-HARDWARE-REC-109`, O1→O2, c=0.85).
Der Block um VA 0x25B16C referenziert „Please release the print key!" (0x25B25C,
per `adr`) und ruft FUN_0026FBF8 **zweimal** — 0x25B120 und 0x25B1CC. Warten auf
Druck, Meldung, Warten auf Loslassen. Derselbe Block ruft `settings_load_validate_save`
(0x262778) und den Menü-Dispatcher (0x26A7F8). **VA 0x25B0C0–0x25B250 ist der
konkreteste Kandidat für die Druckaktion.**

## Werkzeug

Zwei billige Modelle an einem Kalibriertest gescheitert (`research/probes/`):
Devstral mit kaputtem Immediate-Dekoder ohne Alignment-Filter, Mistral Large mit
korrekter Fehlerdiagnose und anschließendem *„Let's fix the decoder and hardcode
the controls"*. Nicht Wissenslücke, sondern Zielfunktion: die Kontrolle stand dem
fertigen Bericht im Weg. Konfigurationen liegen unter `~/.aider-desk/agents/`.

Der Claude-Code-Auftrag `research/probes/_auftraege/A1-encoder-gpio.md` hat
dagegen funktioniert — er hat eine falsche Annahme von mir korrigiert (Maske
0x400), den base+offset-Vorbehalt in beide Richtungen aufgelöst, die Findingzahl
von zwei auf drei erhöht und nicht umbenannt, weil keine Identität aus Header
oder String folgte.

`CL-TOOL-REC-117`: VA 0x280AE8–0x280B7B ist in Ghidra nicht disassembliert.

## Fehler dieser Sitzung, zum Lernen

Dreimal derselbe: Negativbefund aus ungeprüfter Methode. „19 nicht
rekonstruierbar" (Semikolon-Tausch übersehen), „42 % nennen kein Orakel"
(Klassifikator zu eng — real sind es 3), „Pin 117 nie durchgeklingelt" (Archiv
sagt das Gegenteil). Der letzte hat über den Oracle-Deckel eine korrekte Zeile
auf c=0.60 gedrückt. **Ein Deckel schützt gegen zu hohe Konfidenz, nicht gegen
eine falsch eingeordnete Evidenzstufe.**
