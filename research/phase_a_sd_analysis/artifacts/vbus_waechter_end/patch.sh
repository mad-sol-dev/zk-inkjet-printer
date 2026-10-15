#!/bin/bash
set -e
# Erzeugt von patch_vbus_waechter_end.py (CL-USB-REC-128). Endpatch VBUS-Waechter. NUR Testkarte.
# Ausgangsstand: md5_kopf_6 (Diagnose-Schichten) oder md5_kopf (2026-10-13). Endstand-Kopf 296b3c5b8d48ae5b76635eeb77731145
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
echo "Ziel: $DEV -- lese Imagebereich (5034 Sektoren ab 98304)"
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
case "$IST" in
  cfbd158ca02341469fcb743be84c5875e4c2a4e1f004c1424dd5da16fbf47eef) STAND=end;;
  d9fb4230d2f9208fba7f95d577e848374d36c2658c813943ed092c12e9d8e1ee) STAND=6;;
  2bde8f63094fc5086d89f887df099c08a643bd8fa1735c0d89b52c500e42b7f8) STAND=13;;
  *) echo "Imagebereich in keinem erwarteten Stand -- Abbruch, nichts geschrieben."; exit 1;;
esac
S=$(dd if=$DEV bs=512 skip=103339 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$STAND:$S" in
  end:076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560|6:c40091f0832ea0b17279992b9a3e46f0de76dbfc2a1ce0dca6a7edaac519dcc5|13:076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560) ;;
  *) echo "Stub-Sektor Datei 0x275600 passt nicht zum Stand $STAND -- Abbruch, nichts geschrieben."; exit 1;;
esac
S=$(dd if=$DEV bs=512 skip=103340 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$STAND:$S" in
  end:076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560|6:b9ac89a973a908ca742fc4f034bbb495368b1bcaa16236e4b6bd921f3e768be0|13:076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560) ;;
  *) echo "Stub-Sektor Datei 0x275800 passt nicht zum Stand $STAND -- Abbruch, nichts geschrieben."; exit 1;;
esac
S=$(dd if=$DEV bs=512 skip=103341 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$STAND:$S" in
  end:c904b602d70b8ff9be8f5c26b7f3d12034c19ed27c668d8269ad6dd79d175130|6:fd172084b175168395c208a345b5cb263a3c79c9092b97b213e85da46315b578|13:076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560) ;;
  *) echo "Stub-Sektor Datei 0x275A00 passt nicht zum Stand $STAND -- Abbruch, nichts geschrieben."; exit 1;;
esac
[ $STAND = end ] && { echo "Endstand ist schon drauf -- nichts zu tun"; exit 0; }
echo "Ausgangsstand erkannt: $STAND (6 = Diagnose-Schichten md5_kopf_6, 13 = md5_kopf vom 2026-10-13)"
read -p "Sicherung anlegen und 9 Sektoren schreiben? [j/N] " x; [ "$x" = j ] || exit 1
mkdir -p sicherung_$STAND
[ -e sicherung_$STAND/sektor_05c200 ] || dd if=$DEV of=sicherung_$STAND/sektor_05c200 bs=512 skip=99041 count=1 iflag=direct status=none
[ -e sicherung_$STAND/sektor_076e00 ] || dd if=$DEV of=sicherung_$STAND/sektor_076e00 bs=512 skip=99255 count=1 iflag=direct status=none
[ -e sicherung_$STAND/sektor_0af800 ] || dd if=$DEV of=sicherung_$STAND/sektor_0af800 bs=512 skip=99708 count=1 iflag=direct status=none
[ -e sicherung_$STAND/sektor_0b1c00 ] || dd if=$DEV of=sicherung_$STAND/sektor_0b1c00 bs=512 skip=99726 count=1 iflag=direct status=none
[ -e sicherung_$STAND/sektor_0b2000 ] || dd if=$DEV of=sicherung_$STAND/sektor_0b2000 bs=512 skip=99728 count=1 iflag=direct status=none
[ -e sicherung_$STAND/sektor_0c8e00 ] || dd if=$DEV of=sicherung_$STAND/sektor_0c8e00 bs=512 skip=99911 count=1 iflag=direct status=none
[ -e sicherung_$STAND/sektor_275600 ] || dd if=$DEV of=sicherung_$STAND/sektor_275600 bs=512 skip=103339 count=1 iflag=direct status=none
[ -e sicherung_$STAND/sektor_275800 ] || dd if=$DEV of=sicherung_$STAND/sektor_275800 bs=512 skip=103340 count=1 iflag=direct status=none
[ -e sicherung_$STAND/sektor_275a00 ] || dd if=$DEV of=sicherung_$STAND/sektor_275a00 bs=512 skip=103341 count=1 iflag=direct status=none
echo $STAND > letzter_stand
dd if=sektor_275600.neu of=$DEV bs=512 seek=103339 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_275800.neu of=$DEV bs=512 seek=103340 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_275a00.neu of=$DEV bs=512 seek=103341 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_05c200.neu of=$DEV bs=512 seek=99041 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_076e00.neu of=$DEV bs=512 seek=99255 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_0af800.neu of=$DEV bs=512 seek=99708 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_0b1c00.neu of=$DEV bs=512 seek=99726 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_0b2000.neu of=$DEV bs=512 seek=99728 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_0c8e00.neu of=$DEV bs=512 seek=99911 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
[ "$IST" = cfbd158ca02341469fcb743be84c5875e4c2a4e1f004c1424dd5da16fbf47eef ] || { echo "Ruecklesen Imagebereich weicht ab -- ./zurueck.sh"; exit 1; }
S=$(dd if=$DEV bs=512 skip=103339 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$S" = 076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560 ] || { echo "Ruecklesen Stub-Sektor 0x275600 weicht ab -- ./zurueck.sh"; exit 1; }
S=$(dd if=$DEV bs=512 skip=103340 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$S" = 076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560 ] || { echo "Ruecklesen Stub-Sektor 0x275800 weicht ab -- ./zurueck.sh"; exit 1; }
S=$(dd if=$DEV bs=512 skip=103341 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$S" = c904b602d70b8ff9be8f5c26b7f3d12034c19ed27c668d8269ad6dd79d175130 ] || { echo "Ruecklesen Stub-Sektor 0x275A00 weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, Imagebereich und Stub-Sektoren rueckgelesen -- erwartet Diagnose OK M0 A0; zurueck mit ./zurueck.sh"
