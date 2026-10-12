#!/bin/bash
set -e
# Erzeugt von patch_msc_puffer.py (CL-USB-REC-126). NUR Testkarte.
DEV=/dev/sdc
cd "$(dirname "$0")"
IST=$(dd if=$DEV bs=512 skip=99258 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$IST" in b7e5fe401f37dcdc56db7b388f543e834754fedec66e7f777b0ff7e81f34c5d0|db204e4663d2ad58b279da5389504b212abdfcd6b71fa41ce4e8beb76d9791c1) ;; *) echo "Datei-Sektor 0x77400 unerwartet -- Abbruch"; exit 1;; esac
read -p "Sicherung anlegen und 1 Sektor schreiben? [j/N] " x; [ "$x" = j ] || exit 1
[ -e sektor_077400.sicherung ] || dd if=$DEV of=sektor_077400.sicherung bs=512 skip=99258 count=1 iflag=direct status=none
dd if=sektor_077400.neu of=$DEV bs=512 seek=99258 count=1 oflag=direct conv=notrunc,fsync status=none
sync
echo "fertig -- zurueck mit ./zurueck.sh"
