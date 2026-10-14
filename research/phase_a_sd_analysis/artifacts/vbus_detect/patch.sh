#!/bin/bash
set -e
# Erzeugt von patch_vbus_detect.py (CL-USB-REC-128). NUR Testkarte.
# Danach den MD5-Kopf mit dem patch.sh aus patch_md5_kopf.py --image APP.vbus_detect.bin nachziehen.
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
FERTIG=0
IST=$(dd if=$DEV bs=512 skip=99726 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in
  59e2bd5c85d0fec6d0171dee7a5cd5bcfb70a0b94860e3a56deaaa6c95908e6a) FERTIG=$((FERTIG+1));;
  83e841e9c1eae358169e2265d23fab33093c9c0610eb1271c6b7c4f86bc06bc2) ;;
  *) echo "Datei-Sektor 0xB1C00 unerwartet -- Abbruch, nichts geschrieben."; exit 1;;
esac
IST=$(dd if=$DEV bs=512 skip=99728 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in
  ad8db73ec096014b1b01fff4c5f6be156924501f16cddae6a71c5c3b9d3b167c) FERTIG=$((FERTIG+1));;
  380cd5def627e5892e783fe61a62d6a4f8c09d2c2b2450b7209f797a3f8b9b42) ;;
  *) echo "Datei-Sektor 0xB2000 unerwartet -- Abbruch, nichts geschrieben."; exit 1;;
esac
[ $FERTIG = 2 ] && { echo "vbus_detect-Patch ist schon drauf -- nichts zu tun"; exit 0; }
read -p "Sicherung anlegen und 2 Sektoren (Datei 0xB1C00, Datei 0xB2000) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_0b1c00.sicherung ] || dd if=$DEV of=sektor_0b1c00.sicherung bs=512 skip=99726 count=1 iflag=direct status=none
[ -e sektor_0b2000.sicherung ] || dd if=$DEV of=sektor_0b2000.sicherung bs=512 skip=99728 count=1 iflag=direct status=none
dd if=sektor_0b1c00.neu of=$DEV bs=512 seek=99726 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_0b2000.neu of=$DEV bs=512 seek=99728 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=99726 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$IST" = 59e2bd5c85d0fec6d0171dee7a5cd5bcfb70a0b94860e3a56deaaa6c95908e6a ] || { echo "Ruecklesen Datei-Sektor 0xB1C00 weicht ab -- ./zurueck.sh"; exit 1; }
IST=$(dd if=$DEV bs=512 skip=99728 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$IST" = ad8db73ec096014b1b01fff4c5f6be156924501f16cddae6a71c5c3b9d3b167c ] || { echo "Ruecklesen Datei-Sektor 0xB2000 weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, Sektoren rueckgelesen -- jetzt den MD5-Kopf nachziehen; zurueck mit ./zurueck.sh"
