#!/bin/bash
set -e
# Erzeugt von patch_md5_kopf.py (CL-FIRMWARE-REC-119). NUR Testkarte.
# Quelle: Abbild research/phase_a_sd_analysis/artifacts/ringpuffer/APP.ringpuffer.bin
# Kopf Datei 0xC8F60: 6e4353a5d2d6cc589faa67d10d402761 -> e9e3747800158d46f1eb0613f5be17fa
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
echo "Ziel: $DEV -- lese Imagebereich (5034 Sektoren ab 98304)"
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
case "$IST" in
  648fdbf90fcb411a90d1be294adb8af67df0798c85881ed69d796a8734eeb99b) echo "Kopf ist schon gesetzt -- nichts zu tun"; exit 0;;
  be269860f4fe778ed47801e963066f3ca5e4c16e4f05cc89c60ca4524224942c) ;;
  *) echo "Imagebereich weicht vom erwarteten Stand ab -- Abbruch, nichts geschrieben."
     echo "Karte lesen und mit patch_md5_kopf.py --image neu erzeugen."; exit 1;;
esac
read -p "Sicherung anlegen und 1 Sektor (Datei 0xC8E00) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_0c8e00.sicherung ] || dd if=$DEV of=sektor_0c8e00.sicherung bs=512 skip=99911 count=1 iflag=direct status=none
[ "$(sha256sum < sektor_0c8e00.sicherung | cut -d" " -f1)" = 84e311622020ce54bdf47a01867b830691727874bbaa367d41ae51db0284f10b ] || { echo "Sicherung unerwartet -- Abbruch"; exit 1; }
dd if=sektor_0c8e00.neu of=$DEV bs=512 seek=99911 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
[ "$IST" = 648fdbf90fcb411a90d1be294adb8af67df0798c85881ed69d796a8734eeb99b ] || { echo "Ruecklesen weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, Imagebereich rueckgelesen -- erwartet Diagnose OK M0 A0; zurueck mit ./zurueck.sh"
