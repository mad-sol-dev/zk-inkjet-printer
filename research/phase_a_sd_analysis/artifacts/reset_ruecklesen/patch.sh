#!/bin/bash
set -e
# Erzeugt von patch_reset_ruecklesen.py (CL-USB-REC-128). NUR Testkarte.
# Danach den MD5-Kopf mit dem patch.sh aus patch_md5_kopf.py --image APP.ruecklesen.bin nachziehen.
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
IST=$(dd if=$DEV bs=512 skip=99255 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in
  2a8dc2975a8e7329cc741b4bd5252628e5efc965fcc5103001ce4012161a9af2) echo "Sektor ist schon gepatcht -- nichts zu tun"; exit 0;;
  976f66f66d4d422a928686ecc8b278d8f83f36e8b10daab35f1ab9b23028e0d8) ;;
  *) echo "Datei-Sektor 0x76E00 unerwartet -- Abbruch, nichts geschrieben."; exit 1;;
esac
read -p "Sicherung anlegen und 1 Sektor (Datei 0x76E00) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_076e00.sicherung ] || dd if=$DEV of=sektor_076e00.sicherung bs=512 skip=99255 count=1 iflag=direct status=none
[ "$(sha256sum < sektor_076e00.sicherung | cut -d" " -f1)" = 976f66f66d4d422a928686ecc8b278d8f83f36e8b10daab35f1ab9b23028e0d8 ] || { echo "Sicherung unerwartet -- Abbruch"; exit 1; }
dd if=sektor_076e00.neu of=$DEV bs=512 seek=99255 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=99255 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$IST" = 2a8dc2975a8e7329cc741b4bd5252628e5efc965fcc5103001ce4012161a9af2 ] || { echo "Ruecklesen weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, Sektor rueckgelesen -- jetzt den MD5-Kopf nachziehen; zurueck mit ./zurueck.sh"
