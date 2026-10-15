#!/bin/bash
set -e
DEV=${1:-/dev/sdX}
cd "$(dirname "$0")"
[ -e sicherung/sektor_275a00 ] && [ -e sicherung/sektor_275800 ] || { echo "keine Sicherung vorhanden"; exit 1; }
read -p "Sicherung zurueckschreiben (Endstand vbus_waechter_end)? [j/N] " x; [ "$x" = j ] || exit 1
dd if=sicherung/sektor_275a00 of=$DEV bs=512 seek=103341 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sicherung/sektor_275800 of=$DEV bs=512 seek=103340 count=1 oflag=direct conv=notrunc,fsync status=none
sync
S=$(dd if=$DEV bs=512 skip=103340 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$S" = 076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560 ] || { echo "Ruecklesen Sektor Datei 0x275800 weicht vom Endstand ab"; exit 1; }
S=$(dd if=$DEV bs=512 skip=103341 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$S" = c904b602d70b8ff9be8f5c26b7f3d12034c19ed27c668d8269ad6dd79d175130 ] || { echo "Ruecklesen Sektor Datei 0x275A00 weicht vom Endstand ab"; exit 1; }
echo "zurueck im Endstand vbus_waechter_end"
