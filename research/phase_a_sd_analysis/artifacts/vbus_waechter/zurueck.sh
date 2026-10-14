#!/bin/bash
set -e
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
read -p "Sicherungen zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1
dd if=sektor_05c200.sicherung of=$DEV bs=512 seek=99041 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_0af800.sicherung of=$DEV bs=512 seek=99708 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_275a00.sicherung of=$DEV bs=512 seek=103341 count=1 oflag=direct conv=notrunc,fsync status=none
sync
echo "zurueck"
