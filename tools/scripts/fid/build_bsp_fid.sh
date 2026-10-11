#!/usr/bin/env bash
# Baut ghidra_projects/fid/n32901_bsp.fidb aus den Bibliotheken des Nuvoton-BSP
# (CL-TOOL-REC-123). Deterministisch und wiederholbar: jeder Lauf beginnt leer.
#
#   1. jede inhaltlich verschiedene .lib aus vendor/N32901-3_NonOS_BSP nach
#      ghidra_projects/fid/src/<lib>/ entpacken (ar x)
#   2. alle Objekte headless in das Projekt ghidra_projects/fid/bsp importieren
#      und analysieren (ARM:LE:32:v5t, wie APP.bin)
#   3. BuildBspFid.java baut daraus die .fidb
#
# Aufruf aus dem Repository-Wurzelverzeichnis:  tools/scripts/fid/build_bsp_fid.sh
set -euo pipefail

GHIDRA="${GHIDRA_HOME:-$HOME/tools/ghidra_11.4.2_PUBLIC}"
HEADLESS="$GHIDRA/support/analyzeHeadless"
BSP="vendor/N32901-3_NonOS_BSP"
ZIEL="ghidra_projects/fid"
SRC="$ZIEL/src"
FIDB="$ZIEL/n32901_bsp.fidb"
LOG="$ZIEL/build.log"

[ -x "$HEADLESS" ] || { echo "analyzeHeadless fehlt: $HEADLESS" >&2; exit 1; }
[ -d "$BSP" ] || { echo "BSP fehlt: $BSP (Aufruf aus dem Repo-Wurzelverzeichnis?)" >&2; exit 1; }

rm -rf "$SRC" "$ZIEL/bsp.gpr" "$ZIEL/bsp.rep" "$FIDB" "$LOG"
mkdir -p "$SRC"

# 1. Entpacken -- gleiche Inhalte nur einmal, der erste Pfad in Sortierreihenfolge gewinnt
declare -A gesehen
n_lib=0; n_obj=0
while IFS= read -r lib; do
    h=$(md5sum "$lib" | cut -d' ' -f1)
    [ -n "${gesehen[$h]:-}" ] && continue
    gesehen[$h]=1
    name=$(basename "$lib" .lib)
    d="$SRC/$name"
    [ -e "$d" ] && d="$SRC/${name}__$(echo "$lib" | md5sum | cut -c1-6)"
    mkdir -p "$d"
    (cd "$d" && ar x "$OLDPWD/$lib")
    n_lib=$((n_lib + 1)); n_obj=$((n_obj + $(ls "$d" | wc -l)))
done < <(find "$BSP" -iname '*.lib' | sort)
echo "entpackt: $n_lib Bibliotheken, $n_obj Objekte" | tee -a "$LOG"

# 2. Import und Analyse
"$HEADLESS" "$ZIEL" bsp -import "$SRC" -recursive \
    -processor ARM:LE:32:v5t -cspec default \
    -max-cpu 4 >> "$LOG" 2>&1
echo "importiert: $(grep -c 'IMPORTING:' "$LOG" || true) Dateien, Fehler: $(grep -c -i 'ERROR' "$LOG" || true)" | tee -a "$LOG"

# 3. FID-Datenbank. Das Skript braucht ein Programm als Kontext; irgendeines genuegt.
# Projektordner und Dateiname des ersten Objekts: bsp/src/<lib> und <obj>.
erstes=$(cd "$SRC" && find . -type f | sort | head -1 | sed 's|^\./||')
"$HEADLESS" "$ZIEL" "bsp/src/$(dirname "$erstes")" -process "$(basename "$erstes")" -noanalysis -readOnly \
    -scriptPath tools/scripts/ghidra \
    -postScript BuildBspFid.java "$PWD/$FIDB" src N32901-3_NonOS_BSP armcc4.1 >> "$LOG" 2>&1

grep -E 'BuildBspFid.java>|SUMME' "$LOG" | sed 's/^.*BuildBspFid.java> //' || true
[ -f "$FIDB" ] && echo "fertig: $FIDB ($(du -h "$FIDB" | cut -f1))" || { echo "keine .fidb erzeugt, siehe $LOG" >&2; exit 1; }
