#!/bin/bash
set -e
# Erzeugt von patch_md5_kopf.py (CL-FIRMWARE-REC-119). NUR Testkarte.
# Quelle: Abbild $HOME/workspace/zk-inkjet-printer/firmware/research/phase_a_sd_analysis/artifacts/vbus_waechter/APP.vbus_waechter.bin
# Kopf Datei 0xC8F60: 905e542f9b7b28e611b7238a5c80b304 -> 3a3dca16031fa16adaaad8af954461da
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
echo "Ziel: $DEV -- lese Imagebereich (5034 Sektoren ab 98304)"
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
case "$IST" in
  d9fb4230d2f9208fba7f95d577e848374d36c2658c813943ed092c12e9d8e1ee) echo "Kopf ist schon gesetzt -- nichts zu tun"; exit 0;;
  f9d0efe07ddc4fff7e44281ca8ffd2a8d63246845e54395de757af836081f364) ;;
  *) echo "Imagebereich weicht vom erwarteten Stand ab -- Abbruch, nichts geschrieben."
     echo "Karte lesen und mit patch_md5_kopf.py --image neu erzeugen."; exit 1;;
esac
read -p "Sicherung anlegen und 1 Sektor (Datei 0xC8E00) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_0c8e00.sicherung ] || dd if=$DEV of=sektor_0c8e00.sicherung bs=512 skip=99911 count=1 iflag=direct status=none
[ "$(sha256sum < sektor_0c8e00.sicherung | cut -d" " -f1)" = 47a2c5905edc496b3e9e67d3aaf2386c3cd663526e8212783986058f6617fa55 ] || { echo "Sicherung unerwartet -- Abbruch"; exit 1; }
dd if=sektor_0c8e00.neu of=$DEV bs=512 seek=99911 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
[ "$IST" = d9fb4230d2f9208fba7f95d577e848374d36c2658c813943ed092c12e9d8e1ee ] || { echo "Ruecklesen weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, Imagebereich rueckgelesen -- erwartet Diagnose OK M0 A0; zurueck mit ./zurueck.sh"
