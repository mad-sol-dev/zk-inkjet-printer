#!/bin/bash
set -e
DEV=/dev/sdc
cd "$(dirname "$0")"
read -p "Sicherung zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1
dd if=sektor_078400.sicherung of=$DEV bs=512 seek=99266 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_275400.sicherung of=$DEV bs=512 seek=103338 count=1 oflag=direct conv=notrunc,fsync status=none
sync
echo "zurueck"
