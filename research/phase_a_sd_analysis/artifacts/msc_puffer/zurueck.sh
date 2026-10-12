#!/bin/bash
set -e
DEV=/dev/sdc
cd "$(dirname "$0")"
read -p "Sicherung zurueckschreiben? [j/N] " x; [ "$x" = j ] || exit 1
dd if=sektor_077400.sicherung of=$DEV bs=512 seek=99258 count=1 oflag=direct conv=notrunc,fsync status=none
sync
echo "zurueck"
