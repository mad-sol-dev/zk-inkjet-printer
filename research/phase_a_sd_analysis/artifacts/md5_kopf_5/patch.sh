#!/bin/bash
set -e
# Erzeugt von patch_md5_kopf.py (CL-FIRMWARE-REC-119). NUR Testkarte.
# Quelle: Abbild research/phase_a_sd_analysis/artifacts/vbus_detect/APP.vbus_detect.bin
# Kopf Datei 0xC8F60: 9df147cdea1b0eaa9ada29226caa68c0 -> 905e542f9b7b28e611b7238a5c80b304
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
echo "Ziel: $DEV -- lese Imagebereich (5034 Sektoren ab 98304)"
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
case "$IST" in
  73a7d095cba57c4a1f3850c93a17cdfc99d5c349f0df031b5c9c0dbd91385400) echo "Kopf ist schon gesetzt -- nichts zu tun"; exit 0;;
  6f6ddb34f97a11626a51a378dc4cd923f8ed8a4427c5ce2f1581c790623c3fbf) ;;
  *) echo "Imagebereich weicht vom erwarteten Stand ab -- Abbruch, nichts geschrieben."
     echo "Karte lesen und mit patch_md5_kopf.py --image neu erzeugen."; exit 1;;
esac
read -p "Sicherung anlegen und 1 Sektor (Datei 0xC8E00) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_0c8e00.sicherung ] || dd if=$DEV of=sektor_0c8e00.sicherung bs=512 skip=99911 count=1 iflag=direct status=none
[ "$(sha256sum < sektor_0c8e00.sicherung | cut -d" " -f1)" = 848dc3f7970d5f5b646279321b60e536e12da3571a849757f8464c88a44d17cd ] || { echo "Sicherung unerwartet -- Abbruch"; exit 1; }
dd if=sektor_0c8e00.neu of=$DEV bs=512 seek=99911 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
[ "$IST" = 73a7d095cba57c4a1f3850c93a17cdfc99d5c349f0df031b5c9c0dbd91385400 ] || { echo "Ruecklesen weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, Imagebereich rueckgelesen -- erwartet Diagnose OK M0 A0; zurueck mit ./zurueck.sh"
