"""Was ZK-Inkjet anders hat als die Vorlage truth-register. Gelesen von truth.py.

Das Register stammt aus der Januar-Abgleichsrunde und traegt deren Spalten
weiter: Evidenz je Herkunftsstufe (E0, E3New, E1, E3Old, E4) als
'Anzahl [Beleg]', dazu Authority und Open_Question. truth.py selbst ist
dieselbe Datei wie in der Vorlage; Aenderungen am Werkzeug dort machen und
hierher kopieren.
"""

# Kommando oder Vorgang zu O2/O3 steht in Evidence_E0, im Format 'Anzahl [Beleg]'.
EVIDENZ_SPALTE = "Evidence_E0"
EVIDENZ_FORMAT = "1 [{}]"

# Vorgaben fuer neue Zeilen in den Altspalten.
NEUE_ZEILE = {
    "Evidence_E0": "0", "Evidence_E3New": "0", "Evidence_E1": "0",
    "Evidence_E3Old": "0", "Evidence_E4": "0", "Authority": "E0",
}

# Fuer die Ansicht (truth_ansicht.py): Seitentitel und was die Pruefstufen hier heissen.
ANSICHT_TITEL = "ZK-Inkjet truth register"
ANSICHT_ORACLE = {
    "O1": ("derived", "Derived from other rows, documents or plausibility. Nothing was measured."),
    "O2": ("file", "A repeatable command over a file (firmware image, card dump, capture) "
                   "produces the statement."),
    "O3": ("device", "Observed on the printer itself."),
}
