#!/bin/bash
set -e
# Erzeugt von patch_ram_fenster.py (CL-USB-REC-126). NUR Testkarte, Dauerbetrieb muss drauf sein.
DEV=/dev/sdc
cd "$(dirname "$0")"
IST=$(dd if=$DEV bs=512 skip=99266 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in 3fc86cff9aff0eb96eb5204bf4bc3f6d8391ffba97e250e05a92e83e2e7e1f04|a8e70a83103b186ec8092a87933796425ed1e2044b13b188a2c31bc13d88ddfe) ;; *) echo "Datei-Sektor 0x78400 unerwartet -- Abbruch"; exit 1;; esac
IST=$(dd if=$DEV bs=512 skip=103338 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in 2f2ade7ebf15aed7535f2530bc076d16b6588e7d943a97e9e2c6d41464eb2ed5|c645f3a2d7259e7bb9f364c13546be307198678775ce85068865715aee9c677a) ;; *) echo "Datei-Sektor 0x275400 unerwartet -- Abbruch"; exit 1;; esac
read -p "Sicherung anlegen und 2 Sektoren schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_078400.sicherung ] || dd if=$DEV of=sektor_078400.sicherung bs=512 skip=99266 count=1 iflag=direct status=none
[ -e sektor_275400.sicherung ] || dd if=$DEV of=sektor_275400.sicherung bs=512 skip=103338 count=1 iflag=direct status=none
dd if=sektor_078400.neu of=$DEV bs=512 seek=99266 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_275400.neu of=$DEV bs=512 seek=103338 count=1 oflag=direct conv=notrunc,fsync status=none
sync
echo "fertig -- zurueck mit ./zurueck.sh (stellt den Dauerbetrieb-Stand her)"
