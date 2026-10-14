#!/bin/bash
set -e
# Erzeugt von patch_vbus_waechter.py (CL-USB-REC-128). NUR Testkarte.
# Danach den MD5-Kopf mit dem patch.sh aus patch_md5_kopf.py --image APP.vbus_waechter.bin nachziehen.
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
FERTIG=0
IST=$(dd if=$DEV bs=512 skip=99041 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in
  79baa3870549e6223612db0d0ecc424d8ca75a5e628cf234cb5db57d95ce1973) FERTIG=$((FERTIG+1));;
  db7755ca840613cac787ed482058da68c5c4a81bcc384d4656ec81288fa30dc0) ;;
  *) echo "Datei-Sektor 0x5C200 unerwartet -- Abbruch, nichts geschrieben."; exit 1;;
esac
IST=$(dd if=$DEV bs=512 skip=99708 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in
  f64617de70e0c820e0a0ce33e2c678a3ac42817b6f6e48c9ba47944f6778157f) FERTIG=$((FERTIG+1));;
  d9a2fefab7a3cafba7734d134d85aad6749badf6ef120ab09c23d9bccdce2edb) ;;
  *) echo "Datei-Sektor 0xAF800 unerwartet -- Abbruch, nichts geschrieben."; exit 1;;
esac
IST=$(dd if=$DEV bs=512 skip=103341 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in
  fd172084b175168395c208a345b5cb263a3c79c9092b97b213e85da46315b578) FERTIG=$((FERTIG+1));;
  076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560) ;;
  *) echo "Datei-Sektor 0x275A00 unerwartet -- Abbruch, nichts geschrieben."; exit 1;;
esac
[ $FERTIG = 3 ] && { echo "VBUS-Waechter ist schon drauf -- nichts zu tun"; exit 0; }
read -p "Sicherung anlegen und 3 Sektoren (Datei 0x5C200, Datei 0xAF800, Datei 0x275A00) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_05c200.sicherung ] || dd if=$DEV of=sektor_05c200.sicherung bs=512 skip=99041 count=1 iflag=direct status=none
[ -e sektor_0af800.sicherung ] || dd if=$DEV of=sektor_0af800.sicherung bs=512 skip=99708 count=1 iflag=direct status=none
[ -e sektor_275a00.sicherung ] || dd if=$DEV of=sektor_275a00.sicherung bs=512 skip=103341 count=1 iflag=direct status=none
dd if=sektor_275a00.neu of=$DEV bs=512 seek=103341 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_0af800.neu of=$DEV bs=512 seek=99708 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_05c200.neu of=$DEV bs=512 seek=99041 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=99041 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$IST" = 79baa3870549e6223612db0d0ecc424d8ca75a5e628cf234cb5db57d95ce1973 ] || { echo "Ruecklesen Datei-Sektor 0x5C200 weicht ab -- ./zurueck.sh"; exit 1; }
IST=$(dd if=$DEV bs=512 skip=99708 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$IST" = f64617de70e0c820e0a0ce33e2c678a3ac42817b6f6e48c9ba47944f6778157f ] || { echo "Ruecklesen Datei-Sektor 0xAF800 weicht ab -- ./zurueck.sh"; exit 1; }
IST=$(dd if=$DEV bs=512 skip=103341 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$IST" = fd172084b175168395c208a345b5cb263a3c79c9092b97b213e85da46315b578 ] || { echo "Ruecklesen Datei-Sektor 0x275A00 weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, Sektoren rueckgelesen -- jetzt den MD5-Kopf nachziehen; zurueck mit ./zurueck.sh"
