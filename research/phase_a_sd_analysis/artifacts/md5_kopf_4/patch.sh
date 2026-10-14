#!/bin/bash
set -e
# Erzeugt von patch_md5_kopf.py (CL-FIRMWARE-REC-119). NUR Testkarte.
# Quelle: Abbild research/phase_a_sd_analysis/artifacts/usb_isr_ring/APP.usb_isr_ring.bin
# Kopf Datei 0xC8F60: e9e3747800158d46f1eb0613f5be17fa -> 9df147cdea1b0eaa9ada29226caa68c0
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
echo "Ziel: $DEV -- lese Imagebereich (5034 Sektoren ab 98304)"
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
case "$IST" in
  876bdc7a2800f0ba0a3d13d1b69bdb2ab55b6cea4403e904cff75222435092f4) echo "Kopf ist schon gesetzt -- nichts zu tun"; exit 0;;
  580a2eecfab750b1d178cc333a0562f7e3f07bdbbfc5f96089b25571c2eb1bf8) ;;
  *) echo "Imagebereich weicht vom erwarteten Stand ab -- Abbruch, nichts geschrieben."
     echo "Karte lesen und mit patch_md5_kopf.py --image neu erzeugen."; exit 1;;
esac
read -p "Sicherung anlegen und 1 Sektor (Datei 0xC8E00) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_0c8e00.sicherung ] || dd if=$DEV of=sektor_0c8e00.sicherung bs=512 skip=99911 count=1 iflag=direct status=none
[ "$(sha256sum < sektor_0c8e00.sicherung | cut -d" " -f1)" = 2e4d0c4d2446588ca583e560927c2f15eba1cbb8f81d883c9a509462c173afa6 ] || { echo "Sicherung unerwartet -- Abbruch"; exit 1; }
dd if=sektor_0c8e00.neu of=$DEV bs=512 seek=99911 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
[ "$IST" = 876bdc7a2800f0ba0a3d13d1b69bdb2ab55b6cea4403e904cff75222435092f4 ] || { echo "Ruecklesen weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, Imagebereich rueckgelesen -- erwartet Diagnose OK M0 A0; zurueck mit ./zurueck.sh"
