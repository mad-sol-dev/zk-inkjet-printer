#!/bin/bash
set -e
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
[ -e letzter_stand ] || { echo "keine Sicherung vorhanden"; exit 1; }
STAND=$(cat letzter_stand)
read -p "Sicherung sicherung_$STAND zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1
dd if=sicherung_$STAND/sektor_05c200 of=$DEV bs=512 seek=99041 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sicherung_$STAND/sektor_076e00 of=$DEV bs=512 seek=99255 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sicherung_$STAND/sektor_0af800 of=$DEV bs=512 seek=99708 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sicherung_$STAND/sektor_0b1c00 of=$DEV bs=512 seek=99726 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sicherung_$STAND/sektor_0b2000 of=$DEV bs=512 seek=99728 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sicherung_$STAND/sektor_0c8e00 of=$DEV bs=512 seek=99911 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sicherung_$STAND/sektor_275600 of=$DEV bs=512 seek=103339 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sicherung_$STAND/sektor_275800 of=$DEV bs=512 seek=103340 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sicherung_$STAND/sektor_275a00 of=$DEV bs=512 seek=103341 count=1 oflag=direct conv=notrunc,fsync status=none
sync
echo "zurueck in Stand $STAND"
