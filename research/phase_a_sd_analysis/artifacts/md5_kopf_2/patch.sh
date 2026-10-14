#!/bin/bash
set -e
# Erzeugt von patch_md5_kopf.py (CL-FIRMWARE-REC-119). NUR Testkarte.
# Quelle: Abbild research/phase_a_sd_analysis/artifacts/reset_ruecklesen/APP.ruecklesen.bin
# Kopf Datei 0xC8F60: c67cd5c096080a3bf835dc0a656c6d64 -> 6e4353a5d2d6cc589faa67d10d402761
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
echo "Ziel: $DEV -- lese Imagebereich (5034 Sektoren ab 98304)"
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
case "$IST" in
  bb553d03a92c47f1cc882c6482f6620a80c3d6447b2b6dac3511ac2553d1bb6e) echo "Kopf ist schon gesetzt -- nichts zu tun"; exit 0;;
  e6e3d032ae14fb3aee3d010f8590501fc5e258631e0ef0a6ed8821539a3f785a) ;;
  *) echo "Imagebereich weicht vom erwarteten Stand ab -- Abbruch, nichts geschrieben."
     echo "Karte lesen und mit patch_md5_kopf.py --image neu erzeugen."; exit 1;;
esac
read -p "Sicherung anlegen und 1 Sektor (Datei 0xC8E00) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_0c8e00.sicherung ] || dd if=$DEV of=sektor_0c8e00.sicherung bs=512 skip=99911 count=1 iflag=direct status=none
[ "$(sha256sum < sektor_0c8e00.sicherung | cut -d" " -f1)" = f535892d694487d3a79f26565afc155d9572dd3eef657b985cfebc8d12d41ffd ] || { echo "Sicherung unerwartet -- Abbruch"; exit 1; }
dd if=sektor_0c8e00.neu of=$DEV bs=512 seek=99911 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
[ "$IST" = bb553d03a92c47f1cc882c6482f6620a80c3d6447b2b6dac3511ac2553d1bb6e ] || { echo "Ruecklesen weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, Imagebereich rueckgelesen -- erwartet Diagnose OK M0 A0; zurueck mit ./zurueck.sh"
