#!/bin/bash
set -e
DEV=${1:-/dev/sdc}
cd "$(dirname "$0")"
read -p "Sicherung zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1
dd if=sektor_0c8e00.sicherung of=$DEV bs=512 seek=99911 count=1 oflag=direct conv=notrunc,fsync status=none
sync
echo "zurueck"
