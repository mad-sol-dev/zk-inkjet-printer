#!/bin/bash
set -e
# Erzeugt von patch_vbus_taktprobe.py (CL-USB-REC-131). Messstand Taktprobe. NUR Testkarte.
# Ausgangsstand: Endstand vbus_waechter_end (Kopf 296b3c5b8d48ae5b76635eeb77731145). Geschrieben werden nur Datei 0x275800 und 0x275A00.
DEV=${1:-/dev/sdX}
cd "$(dirname "$0")"
echo "Ziel: $DEV -- lese Imagebereich (5034 Sektoren ab 98304)"
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
[ "$IST" = cfbd158ca02341469fcb743be84c5875e4c2a4e1f004c1424dd5da16fbf47eef ] || { echo "Imagebereich ist nicht der Endstand vbus_waechter_end -- Abbruch, nichts geschrieben."; exit 1; }
S=$(dd if=$DEV bs=512 skip=103339 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$S" = 076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560 ] || { echo "Sektor Datei 0x275600 nicht leer -- Abbruch, nichts geschrieben."; exit 1; }
FERTIG=0
S=$(dd if=$DEV bs=512 skip=103340 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$S" in
  b55c80abdf5f8bcdb17da6f172fabd423bcf502987bd32487d409628d873c0dc) FERTIG=$((FERTIG+1));;
  076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560) ;;
  *) echo "Sektor Datei 0x275800 weder Endstand noch Messstand -- Abbruch, nichts geschrieben."; exit 1;;
esac
S=$(dd if=$DEV bs=512 skip=103341 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
case "$S" in
  bc7427ce04ef971a6ead2883a2f883770b74f2fda1d1a47ef4102bbe5ac28f8e) FERTIG=$((FERTIG+1));;
  c904b602d70b8ff9be8f5c26b7f3d12034c19ed27c668d8269ad6dd79d175130) ;;
  *) echo "Sektor Datei 0x275A00 weder Endstand noch Messstand -- Abbruch, nichts geschrieben."; exit 1;;
esac
[ $FERTIG = 2 ] && { echo "Messstand Taktprobe ist schon drauf -- nichts zu tun"; exit 0; }
[ $FERTIG = 0 ] || { echo "Nur ein Teil des Messstands drauf -- erst ./zurueck.sh"; exit 1; }
read -p "Sicherung anlegen und 2 Sektoren (Datei 0x275800, 0x275A00) schreiben? [j/N] " x; [ "$x" = j ] || exit 1
mkdir -p sicherung
[ -e sicherung/sektor_275800 ] || dd if=$DEV of=sicherung/sektor_275800 bs=512 skip=103340 count=1 iflag=direct status=none
[ -e sicherung/sektor_275a00 ] || dd if=$DEV of=sicherung/sektor_275a00 bs=512 skip=103341 count=1 iflag=direct status=none
dd if=sektor_275800.neu of=$DEV bs=512 seek=103340 count=1 oflag=direct conv=notrunc,fsync status=none
dd if=sektor_275a00.neu of=$DEV bs=512 seek=103341 count=1 oflag=direct conv=notrunc,fsync status=none
sync
IST=$(dd if=$DEV bs=512 skip=98304 count=5034 iflag=direct status=none | head -c 2576940 | sha256sum | cut -d" " -f1)
[ "$IST" = cfbd158ca02341469fcb743be84c5875e4c2a4e1f004c1424dd5da16fbf47eef ] || { echo "Ruecklesen Imagebereich weicht ab -- ./zurueck.sh"; exit 1; }
S=$(dd if=$DEV bs=512 skip=103340 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$S" = b55c80abdf5f8bcdb17da6f172fabd423bcf502987bd32487d409628d873c0dc ] || { echo "Ruecklesen Sektor Datei 0x275800 weicht ab -- ./zurueck.sh"; exit 1; }
S=$(dd if=$DEV bs=512 skip=103341 count=1 iflag=direct status=none | sha256sum | cut -d" " -f1)
[ "$S" = bc7427ce04ef971a6ead2883a2f883770b74f2fda1d1a47ef4102bbe5ac28f8e ] || { echo "Ruecklesen Sektor Datei 0x275A00 weicht ab -- ./zurueck.sh"; exit 1; }
echo "fertig, rueckgelesen -- Messstand Taktprobe drauf; zurueck in den Endstand mit ./zurueck.sh"
