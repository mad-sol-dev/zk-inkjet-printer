# Report: Analyse 2,8" TFT/LCD (18‑Pin FFC) – vermuteter Controller

## 1) Ausgangslage
- Gesucht: Wahrscheinlicher Display‑Controller für ein 2,8" TFT/LCD mit **18‑Pin FFC** (u. a. Bezeichnung „LM-024CS18200NC“ genannt), **Datenblatt nicht auffindbar**.
- Ausgangspunkt war ein **Pinout**, das als „ST7789V‑Display“ beschrieben war und sich **so auf der Ziel‑Platine wiederfindet**.

## 2) Verdrahtung/Beobachtungen aus dem Gerät
- Leitungen **SCL / SDA / SDO + CS** gehen an **SPI0** des **N32903N5DN**.
- **RS/A0** (Daten/Befehl‑Umschaltung, oft „D/C“) geht an **Pin 120** des Mikrocontrollers.
- Touch‑Leitungen **XL, YU, XR, YD** sind vorhanden → typisch **4‑draht resistiver Touch** (häufig ohne separaten Touch‑Controller auf dem Flex, stattdessen Messung über µC‑Eingänge).

## 3) Erste Hypothesen (aus Pinout)
- Die Kombination **SPI + CS + RS/A0 + /RESET** ist **nicht exklusiv** für einen Controller.
- Als „wahrscheinlich“ wurden zunächst die üblichen Kandidaten genannt:
  - **ST7789V/ST7789** (sehr verbreitet)
  - **ILI9341** (ebenfalls sehr verbreitet)
- Kernaussage: **Pinout allein** ist oft zu unspezifisch; verlässlicher ist die **Initialisierungs‑Sequenz** (Startbefehle) in der Firmware.

## 4) Firmware‑Fund: vermutete Init‑Sequenz
Du hast folgenden (dekompilierten) Codeausschnitt gezeigt, u. a. mit Werten:
- `0x10`, `0x11`, `0x1A`, `0x3B`, `0x34`, `0x4E`, `0x3A`, `0x17`, `0x16`, `0x21`, `0x22`
- plus explizit: `lcd_send_command(0x3A)`, danach Daten `0x55`; `lcd_send_command(0x36)` danach Daten `0xB4`; `lcd_send_command(0x29)`

### Interpretation (vorläufig)
- Einzelne Werte (**0x21/0x22**) wirken **ähnlich** zu älteren Register‑basierten Controllern (z. B. **ILI932x‑Familie**), bei denen `0x22` oft als „GRAM write“ (Pixelspeicher schreiben) auftaucht.
- Gleichzeitig gilt: Bei modernen ST77xx/ILI9341‑artigen Controllern wäre ein häufiger Einstieg ins Pixel‑Schreiben eher **0x2C** („RAM write“).

**Wichtig:** Diese Interpretation ist **noch nicht belastbar**, weil der nächste Punkt die Aussagekraft stark einschränkt.

## 5) Kritischer Befund: `lcd_send_command()` sieht „tot“ aus
Du hast gezeigt:

- `lcd_send_command()` dekompiliert als **Endlosschleife** (hängt für immer).

### Konsequenz
- Wenn das im echten Laufpfad so wäre, würde die Firmware beim ersten Aufruf hängen – das passt **nicht** zu einem funktionierenden Gerät.
- Sehr wahrscheinlich ist daher mindestens eines dieser Szenarien zutreffend:
  1) **Falsch zugeordnete Funktion**: Ghidra hat einer Adresse den Namen `lcd_send_command` gegeben, die in Wahrheit eine **Fehlerfalle/Assert/Panik‑Routine** ist.
  2) **Falscher Disassemblier‑Kontext** (falscher Modus, falsche Segmentierung/Mapping), wodurch echter Code als „Unsinn“ erscheint.
  3) **Indirekter Aufruf/Funktionszeiger**: Der Decompiler macht daraus einen direkten Call auf die falsche Stelle.
  4) Der gezeigte Init‑Code könnte **toter Code** sein (nicht ausgeführt; alternative Display‑Variante).

**Ergebnis:** Aus den gezeigten Befehlswerten kann man den Controller **noch nicht sicher** bestimmen.

## 6) Was wir damit tatsächlich herausgefunden haben
- Die Hardware‑Anbindung entspricht sehr klar einem **SPI‑TFT mit D/C (RS/A0)** und **4‑draht resistivem Touch**.
- Als Kandidaten bleiben weiterhin realistisch **ST7789‑Varianten** und **ILI9341‑Varianten** (und ggf. andere kompatible), **aber**:
- Der aktuelle Firmware‑Ausschnitt ist **forensisch unsicher**, weil die zentrale Sendefunktion („Command senden“) im Decompiler als Endlosschleife erscheint.

## 7) Empfohlene nächsten Schritte (praktisch, zielgerichtet)
1) **Echten Command/Data‑Pfad finden**
   - In Ghidra nach GPIO‑Zugriffen suchen, die **RS/A0 (Pin 120)** schalten, direkt vor SPI‑Transfers.
   - Den Code suchen, der **SPI0** beschickt (TX‑Register/Status‑Flags) und damit die Display‑Bytes wirklich rausschiebt.

2) **Nach typischen Fenster-/Pixelbefehlen suchen**
   - Treffer für **0x2A / 0x2B / 0x2C** → spricht stark für ST77xx/ILI9341‑artige Controller.
   - Häufung von **0x20/0x21/0x22** plus Fensterregister (häufig im Bereich **0x50–0x53**) → eher Register‑basierte ILI932x‑Art.

3) **Init‑Sequenz als Rohliste rekonstruieren**
   - Idealerweise: Liste „Command → Datenbytes → Delay“.
   - Das liefert einen sehr zuverlässigen Fingerabdruck.

4) Optional (falls SDO wirklich aktiv): **ID‑Lesen**
   - Kann funktionieren, ist bei manchen Modulen aber hardwareseitig deaktiviert/unkomplett.

## 8) Kurzes Begriffs‑Glossar
- **SPI (Serial Peripheral Interface):** Serielle Schnittstelle mit Takt (SCL) und Daten (SDA/MOSI, SDO/MISO).
- **RS/A0 (D/C):** Umschaltung „Befehl“ vs. „Daten“ fürs Display.
- **GRAM:** Bildspeicher im Display‑Controller.

---
**Kurzfazit:** Die Verdrahtung passt zu gängigen SPI‑TFT‑Controllern (ST7789/ILI9341‑Klasse). Der aktuell gezeigte Firmware‑Ausschnitt liefert erst dann eine belastbare Controller‑Aussage, wenn der **tatsächlich ausgeführte** SPI‑Sendepfad (inkl. RS/A0‑Schaltung) gefunden und daraus die **reale Init‑Sequenz** extrahiert ist.

