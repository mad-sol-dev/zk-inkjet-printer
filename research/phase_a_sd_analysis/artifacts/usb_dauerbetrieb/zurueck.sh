#!/bin/bash
set -e
DEV=/dev/sdc
cd "$(dirname "$0")"
read -p "Sicherung zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1
dd if=sektor_012400.sicherung of=$DEV bs=512 seek=98450 count=1 conv=notrunc,fsync status=none
dd if=sektor_068e00.sicherung of=$DEV bs=512 seek=99143 count=1 conv=notrunc,fsync status=none
dd if=sektor_069000.sicherung of=$DEV bs=512 seek=99144 count=1 conv=notrunc,fsync status=none
dd if=sektor_06a600.sicherung of=$DEV bs=512 seek=99155 count=1 conv=notrunc,fsync status=none
dd if=sektor_275400.sicherung of=$DEV bs=512 seek=103338 count=1 conv=notrunc,fsync status=none
sync
echo "zurueck"
