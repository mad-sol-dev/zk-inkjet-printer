#!/bin/bash
set -e
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
read -p "Sicherungen zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1
dd if=sektor_0b1c00.sicherung of=$DEV bs=512 seek=99726 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_0b2000.sicherung of=$DEV bs=512 seek=99728 count=1 oflag=direct conv=notrunc,fsync status=none
sync
echo "zurueck"
