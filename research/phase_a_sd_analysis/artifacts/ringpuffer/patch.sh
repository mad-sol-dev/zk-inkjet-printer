#!/bin/bash
set -e
# Erzeugt von patch_ringpuffer.py (CL-USB-REC-128). NUR Testkarte.
# Danach den MD5-Kopf mit dem patch.sh aus patch_md5_kopf.py --image APP.ringpuffer.bin nachziehen.
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
FERTIG=0
IST=$(dd if=$DEV bs=512 skip=99041 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in
  db7755ca840613cac787ed482058da68c5c4a81bcc384d4656ec81288fa30dc0) FERTIG=$((FERTIG+1));;
  822b419793a3b01db3bd2bd055249d90589d52dbd80c01dd8c9fcf406d4dee16) ;;
  *) echo "Datei-Sektor 0x5C200 unerwartet -- Abbruch, nichts geschrieben."; exit 1;;
esac
IST=$(dd if=$DEV bs=512 skip=103339 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in
  c40091f0832ea0b17279992b9a3e46f0de76dbfc2a1ce0dca6a7edaac519dcc5) FERTIG=$((FERTIG+1));;
  076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560) ;;
  *) echo "Datei-Sektor 0x275600 unerwartet -- Abbruch, nichts geschrieben."; exit 1;;
esac
[ $FERTIG = 2 ] && { echo "Ringpuffer ist schon drauf -- nichts zu tun"; exit 0; }
read -p "Sicherung anlegen und 2 Sektoren (Datei 0x5C200, 0x275600) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_05c200.sicherung ] || dd if=$DEV of=sektor_05c200.sicherung bs=512 skip=99041 count=1 iflag=direct status=none
[ -e sektor_275600.sicherung ] || dd if=$DEV of=sektor_275600.sicherung bs=512 skip=103339 count=1 iflag=direct status=none
dd if=sektor_275600.neu of=$DEV bs=512 seek=103339 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_05c200.neu of=$DEV bs=512 seek=99041 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=99041 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$IST" = db7755ca840613cac787ed482058da68c5c4a81bcc384d4656ec81288fa30dc0 ] || { echo "Ruecklesen Datei-Sektor 0x5C200 weicht ab -- ./zurueck.sh"; exit 1; }
IST=$(dd if=$DEV bs=512 skip=103339 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$IST" = c40091f0832ea0b17279992b9a3e46f0de76dbfc2a1ce0dca6a7edaac519dcc5 ] || { echo "Ruecklesen Datei-Sektor 0x275600 weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, beide Sektoren rueckgelesen -- jetzt den MD5-Kopf nachziehen; zurueck mit ./zurueck.sh"
