# HP45 Evidence

Raw facts extracted from chat transcripts. No interpretation, only concrete observations.

---

## Printhead Pinout & Connections

### E-HP45-001: HA and HP Line Definitions
- **Quote:** "**HA = Adressleitungen, HP = Primitive-Leitungen (Stromschienen).**"
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=1
- **Date:** 2025-11-29
- **Type:** ANALYSIS
- **Tags:** ha, hp, definitions, printhead

### E-HP45-002: Nozzle Requires HA and HP Together
- **Quote:** "Eine Düse feuert nur dann, wenn *beides* gleichzeitig aktiv ist."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=1
- **Date:** 2025-11-29
- **Type:** ANALYSIS
- **Tags:** nozzle, ha, hp, firing

### E-HP45-003: HP45/HP45SI Matrix Structure
- **Quote:** "Der HP45/HP45SI ist intern als **22×14-Matrix** verschaltet:"
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=1
- **Date:** 2025-11-29
- **Type:** DATASHEET
- **Tags:** hp45, hp45si, matrix, pinout

### E-HP45-004: Nozzle Count From Matrix
- **Quote:** "Die 300 Düsen entstehen aus dieser Matrix (22×14 = 308 mögliche Positionen, 8 bleiben unbenutzt)."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=1
- **Date:** 2025-11-29
- **Type:** DATASHEET
- **Tags:** nozzles, matrix, count, hp45

### E-HP45-005: Ground and Feedback Pins
- **Quote:** "dazu kommen 14 Masseleitungen und 2 Feedback-Pins (TSR, 10×)"
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=1
- **Date:** 2025-11-29
- **Type:** DATASHEET
- **Tags:** ground, feedback, tsr, 10x

### E-HP45-006: C10X and CTSR Listed as Separate Pins
- **Quote:** "C10X und CTSR sind sauber als separate Pins geführt – das passt perfekt zu Yvos Beschreibung des 10×-Resistors und des Temperature-Sense-Resistors."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=21
- **Date:** 2025-11-29
- **Type:** PCB_TRACE
- **Tags:** c10x, ctsr, sense, hp45

### E-HP45-007: HP45SI Connector Mapping (HGND/HP07/HA13)
- **Quote:** ",,HGND,,HP07,Q10:4 S1,HA13,IC5:B,,HGND,,HP8,Q11:6 S1,HA11,IC4:F,,,,,,,,,,,,,,,"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=8
- **Date:** 2025-12-19
- **Type:** PCB_TRACE
- **Tags:** hp45si, connector, hgnd, hp07

### E-HP45-008: HP45SI Connector Mapping (C10X/CTSR)
- **Quote:** ",,HA21,IC6:D,C10X,,,,,,,CTSR,x,HA00,IC3:A,,,,,,,,,,,,,,,"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=8
- **Date:** 2025-12-19
- **Type:** PCB_TRACE
- **Tags:** c10x, ctsr, ha00, connector

### E-HP45-009: FCC Connector HP/VDD Mapping
- **Quote:** "← FCC Connector,,,VDD,HP01,,HP02,VDD,HP03,,HP04,VDD,HP05,,HP06,VDD,HP07,,HP8,VDD,HP09,,HP10,VDD,HP11,,HP12,VDD,HP13,"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=8
- **Date:** 2025-12-19
- **Type:** PCB_TRACE
- **Tags:** fcc, vdd, hp01, hp13

---

## CM504B Driver ICs

### E-HP45-010: CM504B Carries HA Lines
- **Quote:** "Dass du an den CM504B-Bausteinen (CD4504B Level-Shiftern) nur **HA-Leitungen** findest, ist völlig logisch."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=21
- **Date:** 2025-11-29
- **Type:** ANALYSIS
- **Tags:** cm504b, level-shifter, ha, gpio

### E-HP45-011: HP Lines Use Separate High-Current Drivers
- **Quote:** "Die **HP-Leitungen** (Primitives) wirst du dort praktisch nie sehen – die müssen über **separate Hochstrom-Treiber** laufen."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=21
- **Date:** 2025-11-29
- **Type:** ANALYSIS
- **Tags:** hp, high-current, drivers, primitives

### E-HP45-012: CM504B Identified as 6-Channel Level Shifter
- **Quote:** "Der CD4504B (dein „CM504B“) ist ein **6-kanaliger Level-Shifter**:"
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=21
- **Date:** 2025-11-29
- **Type:** DATASHEET
- **Tags:** cm504b, cd4504b, level-shifter, channels

### E-HP45-013: CM504B Current Capability
- **Quote:** "Der kann bei 12–15 V **nur ein paar mA** treiben, also perfekt für:"
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=21
- **Date:** 2025-11-29
- **Type:** ANALYSIS
- **Tags:** cm504b, current, ha, level-shifter

### E-HP45-014: CM504B Count for Printhead Drive
- **Quote:** "- 6 ICs zur Ansteuerung der Druckköpfe"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=9
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** cm504b, driver-ic, count, printhead

### E-HP45-015: CM504B Pin Set
- **Quote:** "- Jedes IC hat Pins: VCC, AOUT, AIN, BOUT, BIN, COUT, CIN, VSS, DIN, DOUT, EIN, EOUT, FIN, FOUT, SELECT, VDD"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=9
- **Date:** 2025-12-19
- **Type:** DATASHEET
- **Tags:** cm504b, pins, vcc, vdd

### E-HP45-016: IC1 Mapping (GPA0)
- **Quote:** "- Pin 3 (AIN): SoC 79 (GPA0)"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=9
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** ic1, gpa0, mapping, gpio

### E-HP45-017: IC2 Mapping (GPA6/GPA7/GPA11/GPA10/GPD6)
- **Quote:** "- Pin 3 (AIN): SoC 73 (GPA[6])"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=9
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** ic2, gpa6, mapping, gpio

### E-HP45-018: IC2 HP Order
- **Quote:** "Also wenn man sich IC2 anschaut, dann ist es logisch, dass in dieser Reihenfolge eben, also HP06, HP07, HP08, HP09 kommt."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=80
- **Date:** 2025-11-29
- **Type:** ANALYSIS
- **Tags:** ic2, hp06, hp07, hp09

---

## Nozzle Control & Timing

### E-HP45-019: HA Drive Voltage
- **Quote:** "1. **Eine Adresse (HAᵢ)** wird auf ca. 10–12 V gelegt → Gate des FETs für alle Düsen dieser „Zeile“ öffnet."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=1
- **Date:** 2025-11-29
- **Type:** DATASHEET
- **Tags:** ha, voltage, 10-12v, timing

### E-HP45-020: HP Pulse Width
- **Quote:** "2. **Ein oder mehrere Primitive (HPⱼ)** werden für ~2 µs auf 10–12 V gelegt → durch die ausgewählten Düsen fließt der Heizstrom."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=1
- **Date:** 2025-11-29
- **Type:** DATASHEET
- **Tags:** hp, pulse, 2us, voltage

### E-HP45-021: Primitive/Address Ordering
- **Quote:** "Alles andere kann FET oder Düse zerstören."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=1
- **Date:** 2025-11-29
- **Type:** ANALYSIS
- **Tags:** order, primitive, address, timing

### E-HP45-022: HP Pulse Timing Range
- **Quote:** "2. Nach ~1 µs die passende HP-Primitive für ~1,5–2 µs auf 9–13 V schalten (High-Side-Treiber, viel Strom)."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=21
- **Date:** 2025-11-29
- **Type:** ANALYSIS
- **Tags:** pulse, 1.5-2us, 9-13v, timing

### E-HP45-023: Current Demand Difference
- **Quote:** "Die **Adressen** brauchen fast keinen Strom (nur FET-Gate), die **Primitives** dagegen mehrere 100 mA pro aktivem Strang."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=21
- **Date:** 2025-11-29
- **Type:** ANALYSIS
- **Tags:** current, primitives, addresses, power

### E-HP45-024: 22 Sub-Lines per Print Line
- **Quote:** "**jede Druckzeile** wird als Folge von 22 „Subzeilen“ ausgegeben, und in jeder Subzeile ist ein 14-Bit-Muster aktiv."
- **Source:** Chats/48_GPT_HP45_Drucker_Pinout_Erklärung_29.11.2025.json#msg=1
- **Date:** 2025-11-29
- **Type:** ANALYSIS
- **Tags:** sublines, 22, 14-bit, firing

---

## ADC & Encoder Integration

### E-HP45-025: VADJ as Printhead Voltage
- **Quote:** "VIN: 7,97V -1
und VADJ: 9,09V (Druckkopf/Düsenspannung)."
- **Source:** Chats/58_CL_ZK-Inkjet_Projekt_Platine_analysieren_20.12.2025.json#msg=34
- **Date:** 2025-12-20
- **Type:** PCB_TRACE
- **Tags:** vadj, vin, voltage, adc

### E-HP45-026: ADC Channels 0/1 Unused
- **Quote:** "Sehr interessant! Codex hat bestätigt, dass es nur 3 Aufrufe von adc_read_channel gibt, und KEINER davon verwendet Channel 0 oder 1."
- **Source:** Chats/58_CL_ZK-Inkjet_Projekt_Platine_analysieren_20.12.2025.json#msg=41
- **Date:** 2025-12-20
- **Type:** ANALYSIS
- **Tags:** adc, channels, ain0, ain1

### E-HP45-027: Encoder SoC Pin Reference
- **Quote:** "Der magnetische Encoder wird über Pin 6 mit SoC 117 verbunden, was die Gesamtkomplexität der Pinbelegung unterstreicht."
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=9
- **Date:** 2025-12-19
- **Type:** ANALYSIS
- **Tags:** encoder, mt6701, soc117, gpe10

### E-HP45-028: MT6701 Connection Line
- **Quote:** ",,3 (A_Out),,(A / SDA) 6,117 (NALE_ / GPE[10],,,,,,,,,,,,,,,,,,,,,,,,"
- **Source:** Chats/57_CL_N32903N5DN_Pinout_GPIO-Übersicht_19.12.2025.json#msg=8
- **Date:** 2025-12-19
- **Type:** PCB_TRACE
- **Tags:** mt6701, gpe10, nale, encoder

### E-HP45-029: Encoder Reading on About Screen
- **Quote:** "ZU schnell!! INK: 1667820 pl (pico Lieter?!) - Encoder OK | 66602 (<- Encoder Wert) Und lass Codex arbeiten!"
- **Source:** Chats/58_CL_ZK-Inkjet_Projekt_Platine_analysieren_20.12.2025.json#msg=48
- **Date:** 2025-12-20
- **Type:** OBSERVATION
- **Tags:** encoder, about-screen, value, ink
