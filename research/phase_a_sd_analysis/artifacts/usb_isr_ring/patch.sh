#!/bin/bash
set -e
# Erzeugt von patch_usb_isr_ring.py (CL-USB-REC-128). NUR Testkarte.
# Danach den MD5-Kopf mit dem patch.sh aus patch_md5_kopf.py --image APP.usb_isr_ring.bin nachziehen.
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
FERTIG=0
IST=$(dd if=$DEV bs=512 skip=99708 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in
  d9a2fefab7a3cafba7734d134d85aad6749badf6ef120ab09c23d9bccdce2edb) FERTIG=$((FERTIG+1));;
  f2d4ec72c18f38812204d700f8e4398fc42e9ba8b315f7abf3358e63a7400d47) ;;
  *) echo "Datei-Sektor 0xAF800 unerwartet -- Abbruch, nichts geschrieben."; exit 1;;
esac
IST=$(dd if=$DEV bs=512 skip=103340 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in
  b9ac89a973a908ca742fc4f034bbb495368b1bcaa16236e4b6bd921f3e768be0) FERTIG=$((FERTIG+1));;
  076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560) ;;
  *) echo "Datei-Sektor 0x275800 unerwartet -- Abbruch, nichts geschrieben."; exit 1;;
esac
[ $FERTIG = 2 ] && { echo "USB-ISR-Ring ist schon drauf -- nichts zu tun"; exit 0; }
read -p "Sicherung anlegen und 2 Sektoren (Datei 0xAF800, 0x275800) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_0af800.sicherung ] || dd if=$DEV of=sektor_0af800.sicherung bs=512 skip=99708 count=1 iflag=direct status=none
[ -e sektor_275800.sicherung ] || dd if=$DEV of=sektor_275800.sicherung bs=512 skip=103340 count=1 iflag=direct status=none
dd if=sektor_275800.neu of=$DEV bs=512 seek=103340 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_0af800.neu of=$DEV bs=512 seek=99708 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=99708 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$IST" = d9a2fefab7a3cafba7734d134d85aad6749badf6ef120ab09c23d9bccdce2edb ] || { echo "Ruecklesen Datei-Sektor 0xAF800 weicht ab -- ./zurueck.sh"; exit 1; }
IST=$(dd if=$DEV bs=512 skip=103340 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$IST" = b9ac89a973a908ca742fc4f034bbb495368b1bcaa16236e4b6bd921f3e768be0 ] || { echo "Ruecklesen Datei-Sektor 0x275800 weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, beide Sektoren rueckgelesen -- jetzt den MD5-Kopf nachziehen; zurueck mit ./zurueck.sh"
