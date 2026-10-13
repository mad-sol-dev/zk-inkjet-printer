#!/bin/bash
set -e
# Erzeugt von patch_md5_kopf.py (CL-FIRMWARE-REC-119). NUR Testkarte.
# Quelle: Nachbau Patch-Stand 2026-10-13 (USB-Fenster, Dauerbetrieb, RAM-Fenster, MSC-Puffer)
# Kopf Datei 0xC8F60: e4784d6e7524f24a168ce179980a70ee -> c67cd5c096080a3bf835dc0a656c6d64
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
echo "Ziel: $DEV -- lese Imagebereich (5034 Sektoren ab 98304)"
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
case "$IST" in
  2bde8f63094fc5086d89f887df099c08a643bd8fa1735c0d89b52c500e42b7f8) echo "Kopf ist schon gesetzt -- nichts zu tun"; exit 0;;
  75fcca056846e687c146aab66582c3aee18b3d5e252a725c3362e4433b9c5404) ;;
  *) echo "Imagebereich weicht vom erwarteten Stand ab -- Abbruch, nichts geschrieben."
     echo "Karte lesen und mit patch_md5_kopf.py --image neu erzeugen."; exit 1;;
esac
read -p "Sicherung anlegen und 1 Sektor (Datei 0xC8E00) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_0c8e00.sicherung ] || dd if=$DEV of=sektor_0c8e00.sicherung bs=512 skip=99911 count=1 iflag=direct status=none
[ "$(sha256sum < sektor_0c8e00.sicherung | cut -d" " -f1)" = 663a13d29768d8d63565aa59d03ee2401303539cc21b7f01f16edb6b9c971b2d ] || { echo "Sicherung unerwartet -- Abbruch"; exit 1; }
dd if=sektor_0c8e00.neu of=$DEV bs=512 seek=99911 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
[ "$IST" = 2bde8f63094fc5086d89f887df099c08a643bd8fa1735c0d89b52c500e42b7f8 ] || { echo "Ruecklesen weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, Imagebereich rueckgelesen -- erwartet Diagnose OK M0 A0; zurueck mit ./zurueck.sh"
