#!/bin/bash
set -e
# Erzeugt von patch_usb_window.py -- USB-Fenster nach 0x28800000
# Ein Sektor: Datei-Sektor 0xE5 von APP.bin = Rohsektor 98533 (Rohadresse 0x0301CA00).
# NUR auf die Testkarte anwenden, niemals auf die Originalkarte.
DEV=/dev/sdc
echo "Ziel: $DEV, Rohsektor 98533"
IST=$(dd if=$DEV bs=512 skip=98533 count=1 status=none | sha256sum | cut -d" " -f1)
echo "vorher: $IST"
case "$IST" in f16d21b62513694f03cb20b5b562ac27c47d26f1e7b56e9ee6b3cca7db4d59a7|08e414c305b5a97e60d98ff8ba867e2314d75617bbfa8899343132f7e9f98213) ;; *) echo "Unerwarteter Inhalt -- Abbruch"; exit 1;; esac
read -p "Fortfahren? [j/N] " x; [ "$x" = j ] || exit 1
dd if=$HOME/workspace/zk-inkjet-printer/firmware/research/phase_a_sd_analysis/artifacts/usbfenster_28800000/sektor_28800000.bin of=$DEV bs=512 count=1 seek=98533 conv=notrunc,fsync status=none
echo "nachher: $(dd if=$DEV bs=512 skip=98533 count=1 status=none | sha256sum | cut -d" " -f1)"
sync
echo "fertig"
