#!/usr/bin/env python3
"""Build the APP block for a live RAM boot over USB, and optionally run it.

The printer's BOOT.bin normally reads 0x280000 bytes from card raw 0x03000000
to RAM 0x58000: APP.bin (0x27522C bytes, CL-BOOT-REC-113) and the sectors
behind it, where patch stubs live (file 0x275400 and later). For a live boot
(n329-usbboot, README section "Running APP.bin from RAM") the host uploads
that block itself and starts a BOOT.bin whose two SD reads of APP.bin are
skipped. This script assembles the block exactly as the card would hold it:

  image       APP.bin or a patch stand image (VA = file offset + 0x58000)
  --patch     word patches inside the image, VA=OLD:NEW, OLD is checked
  MD5 head    recomputed after --patch so the image check value [0x558]
              stays 0 (CL-FIRMWARE-REC-119); without it the printer beeps
              continuously and shows 'NG' in its diagnostic line
  --sector    512-byte stub sectors behind the image, FILEOFFSET=FILE
  rest        zero up to 0x280000

  python3 tools/scripts/live_image.py [--stand NAME | --image FILE]
          [--sector 0x275400=FILE ...] [--patch 0xVA=OLD:NEW ...]
          [--out FILE] [--run]

--run uploads the block with n329usb (sibling checkout ../n329-usbboot):
BOOT.bin to 0x700000 with 0x702FC8 ldr r0,[r5] -> b 0x703028, the block to
0x58000, exec 0x700000. Power the board without the SD card first, insert
the card, then run. Nothing is written to the card.

Stands (--stand) are card states whose stub sectors come from several
artifact folders, because the patches build on each other:
  original            firmware/bin APP.bin, no stubs
  vbus_waechter_end   VBUS guard end stand (CL-USB-REC-130), 0x275400 from
                      ram_fenster, 0x275A00 from vbus_waechter_end; ran live
                      on 2026-10-18 (42 s cable pull without stall)
"""
import argparse
import hashlib
import os
import struct
import subprocess
import sys

import image_pruefwert as pw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ART = os.path.join(ROOT, "research", "phase_a_sd_analysis", "artifacts")
BIN = os.path.join(ROOT, "firmware", "bin")
APP = os.path.join(BIN, "ZK-INKJET-NANO-APP.bin")
BOOT = os.path.join(BIN, "ZK-INKJET-NANO-BOOT.bin")
N329USB = os.path.normpath(os.path.join(ROOT, "..", "n329-usbboot"))

VA0 = 0x58000
L = 0x27522C            # image length, header word at VA 0x120F70
BLOCK = 0x280000        # what BOOT.bin reads (0x1400 sectors)
FIRST_STUB = 0x275400   # first sector wholly behind the image

BOOT_EXEC = 0x700000
BOOT_SKIP_APP_READ = (0x702FC8, 0xE5950000, 0xEA000016)   # b 0x703028

STANDS = {
    "original": (APP, {}),
    "vbus_waechter_end": (
        os.path.join(ART, "vbus_waechter_end", "APP.vbus_waechter_end.bin"),
        {0x275400: os.path.join(ART, "ram_fenster", "sektor_275400.neu"),
         0x275A00: os.path.join(ART, "vbus_waechter_end", "sektor_275a00.neu")}),
}


def number(text):
    return int(text, 0)


def sector_arg(text):
    off, _, path = text.partition("=")
    if not path:
        raise argparse.ArgumentTypeError("expected FILEOFFSET=FILE")
    return number(off), path


def patch_arg(text):
    va, _, rest = text.partition("=")
    old, _, new = rest.partition(":")
    if not new:
        raise argparse.ArgumentTypeError("expected VA=OLD:NEW (hex words)")
    return number(va), int(old, 16), int(new, 16)


def show(path):
    rel = os.path.relpath(path, ROOT)
    return path if rel.startswith("..") else rel


def build(image, sectors, patches):
    """Return (block, check value) or exit with a message."""
    if len(image) != L:
        sys.exit(f"image is {len(image):#x} bytes, expected {L:#x}")
    img = bytearray(image)
    for va, old, new in patches:
        off = va - VA0
        if not 0 <= off <= L - 4 or off & 3:
            sys.exit(f"patch {va:#x} is not a word inside the image")
        if pw.K <= off < pw.K + 0x14:
            sys.exit(f"patch {va:#x} hits the MD5 head; it is recomputed anyway")
        found = struct.unpack_from("<I", img, off)[0]
        if found != old:
            sys.exit(f"word at {va:#x} is {found:08x}, expected {old:08x} -- nothing built")
        struct.pack_into("<I", img, off, new)
    if patches:
        _, md5, _ = pw.pruefwert(bytes(img))
        img[pw.K:pw.K + 16] = md5
    value, _, _ = pw.pruefwert(bytes(img))

    block = bytearray(BLOCK)
    block[:L] = img
    for off, data in sorted(sectors.items()):
        if off % 512 or not FIRST_STUB <= off <= BLOCK - 512:
            sys.exit(f"sector {off:#x} is not a sector behind the image")
        if len(data) != 512:
            sys.exit(f"sector {off:#x}: {len(data)} bytes, expected 512")
        block[off:off + 512] = data
    return bytes(block), value


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--stand", choices=sorted(STANDS))
    src.add_argument("--image", help="image file of length 0x27522C")
    ap.add_argument("--sector", type=sector_arg, action="append", default=[],
                    metavar="OFF=FILE", help="stub sector behind the image; repeatable")
    ap.add_argument("--patch", type=patch_arg, action="append", default=[],
                    metavar="VA=OLD:NEW", help="word patch inside the image; repeatable")
    ap.add_argument("--out", default=os.path.join(ROOT, "build", "live", "APP.live.bin"))
    ap.add_argument("--allow-check-value", action="store_true",
                    help="build even if the image check value is not 0")
    ap.add_argument("--run", action="store_true", help="upload and start with n329usb")
    ap.add_argument("--n329usb", default=N329USB, help="n329-usbboot checkout")
    a = ap.parse_args()

    path, stand_sectors = STANDS[a.stand or "original"] if not a.image else (a.image, {})
    image = open(path, "rb").read()
    sectors = {off: open(p, "rb").read() for off, p in stand_sectors.items()}
    for off, p in a.sector:
        sectors[off] = open(p, "rb").read()
    block, value = build(image, sectors, a.patch)

    print(f"image   {show(path)}")
    for va, old, new in a.patch:
        print(f"patch   VA {va:#09x}: {old:08x} -> {new:08x}")
    if a.patch:
        print("MD5 head recomputed")
    for off in sorted(sectors):
        print(f"sector  file {off:#08x} (VA {off + VA0:#09x})")
    print(f"check value [0x558] = {value:#x}")
    if value and not a.allow_check_value:
        sys.exit("check value is not 0 -- the printer would beep and show NG; nothing written")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "wb") as f:
        f.write(block)
    print(f"block   {show(os.path.abspath(a.out))}, {len(block):#x} bytes, "
          f"sha256 {hashlib.sha256(block).hexdigest()[:16]}")

    va, old, new = BOOT_SKIP_APP_READ
    cmd = [sys.executable, "-m", "n329usb", "run",
           "--load", f"{BOOT_EXEC:#x}:{BOOT}",
           "--load", f"{VA0:#x}:{os.path.abspath(a.out)}",
           "--patch", f"{va:#x}:{old:08x}:{new:08x}",
           "--exec", f"{BOOT_EXEC:#x}"]
    if not a.run:
        print("run with --run, or:  cd " + a.n329usb + " && python3 " + " ".join(cmd[1:]))
        return
    env = dict(os.environ, PYTHONPATH=a.n329usb)
    sys.exit(subprocess.call(cmd, cwd=a.n329usb, env=env))


if __name__ == "__main__":
    main()
