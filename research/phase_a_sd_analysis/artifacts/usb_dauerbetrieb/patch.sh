#!/bin/bash
set -e
# Erzeugt von patch_usb_dauerbetrieb.py (CL-USB-REC-126). NUR Testkarte.
DEV=/dev/sdc
cd "$(dirname "$0")"
# Vorbedingung: USB-Fenster schon auf 0x28800000 (CL-USB-REC-119)
IST=$(dd if=$DEV bs=512 skip=98533 count=1 status=none | sha256sum | cut -d" " -f1)
[ "$IST" = 08e414c305b5a97e60d98ff8ba867e2314d75617bbfa8899343132f7e9f98213 ] || { echo "USB-Fenster nicht gepatcht -- erst patch_usb_window.py"; exit 1; }
IST=$(dd if=$DEV bs=512 skip=98450 count=1 status=none | sha256sum | cut -d" " -f1)
case "$IST" in 18b1246d67f8cd72de85f5e682219d6c2efda70090045ee1962e907f33c7c1de|f62e876817b6e7f73cefd1849b8605b21c099fe930b3f36b2124a04867af5c68) ;; *) echo "Datei-Sektor 0x12400 unerwartet -- Abbruch"; exit 1;; esac
IST=$(dd if=$DEV bs=512 skip=99143 count=1 status=none | sha256sum | cut -d" " -f1)
case "$IST" in 932bd9b58a42daa9346b12a1aeb9a487476ce849d7d67695f9de57d7733cf401|163c46a877f00acfe67fba1384ad6368052fa419f968ac8776d49396d3ddd4f0) ;; *) echo "Datei-Sektor 0x68E00 unerwartet -- Abbruch"; exit 1;; esac
IST=$(dd if=$DEV bs=512 skip=99144 count=1 status=none | sha256sum | cut -d" " -f1)
case "$IST" in 2ab5f6e05d841b416ef303b7db0e269203d2390d3537673ee47eeb688fe73910|5822bf7c695019c0909fd2241d32b7331626a17a01cc9ec0a90f73307876c9ff) ;; *) echo "Datei-Sektor 0x69000 unerwartet -- Abbruch"; exit 1;; esac
IST=$(dd if=$DEV bs=512 skip=99155 count=1 status=none | sha256sum | cut -d" " -f1)
case "$IST" in b9a0339f5fc8fde96494023472ce1c338c12fa9d5c7414b84432f7b56ddca85f|fdf6320cec03701a183b56990a28b66dcdc2efa56206983532655096b71db291) ;; *) echo "Datei-Sektor 0x6A600 unerwartet -- Abbruch"; exit 1;; esac
read -p "Sicherung anlegen und 5 Sektoren schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_012400.sicherung ] || dd if=$DEV of=sektor_012400.sicherung bs=512 skip=98450 count=1 status=none
[ -e sektor_068e00.sicherung ] || dd if=$DEV of=sektor_068e00.sicherung bs=512 skip=99143 count=1 status=none
[ -e sektor_069000.sicherung ] || dd if=$DEV of=sektor_069000.sicherung bs=512 skip=99144 count=1 status=none
[ -e sektor_06a600.sicherung ] || dd if=$DEV of=sektor_06a600.sicherung bs=512 skip=99155 count=1 status=none
[ -e sektor_275400.sicherung ] || dd if=$DEV of=sektor_275400.sicherung bs=512 skip=103338 count=1 status=none
dd if=sektor_012400.neu of=$DEV bs=512 seek=98450 count=1 conv=notrunc,fsync status=none
dd if=sektor_068e00.neu of=$DEV bs=512 seek=99143 count=1 conv=notrunc,fsync status=none
dd if=sektor_069000.neu of=$DEV bs=512 seek=99144 count=1 conv=notrunc,fsync status=none
dd if=sektor_06a600.neu of=$DEV bs=512 seek=99155 count=1 conv=notrunc,fsync status=none
dd if=sektor_275400.neu of=$DEV bs=512 seek=103338 count=1 conv=notrunc,fsync status=none
sync
echo "fertig -- zurueck mit ./zurueck.sh"
