#!/usr/bin/env python3
import argparse
import os
import struct
import sys

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit("Pillow is required: pip install pillow") from exc


XOR_MASK = 0x4949


def bgr565_to_rgb888(value):
    value ^= XOR_MASK
    r5 = value & 0x1F
    g6 = (value >> 5) & 0x3F
    b5 = (value >> 11) & 0x1F
    r8 = (r5 << 3) | (r5 >> 2)
    g8 = (g6 << 2) | (g6 >> 4)
    b8 = (b5 << 3) | (b5 >> 2)
    return r8, g8, b8


def decode_linear(values, width, height):
    expected = width * height
    if len(values) < expected:
        raise ValueError("Not enough pixels for requested dimensions.")
    out = bytearray(expected * 3)
    for idx in range(expected):
        r8, g8, b8 = bgr565_to_rgb888(values[idx])
        base = idx * 3
        out[base:base + 3] = bytes((r8, g8, b8))
    return out


def decode_tiled(values, tile_size, tiles_x, tiles_y):
    width = tile_size * tiles_x
    height = tile_size * tiles_y
    expected = width * height
    if len(values) < expected:
        raise ValueError("Not enough pixels for requested tile layout.")
    out = bytearray(expected * 3)
    src = 0
    for ty in range(tiles_y):
        for tx in range(tiles_x):
            for y in range(tile_size):
                row_base = ((ty * tile_size + y) * width + tx * tile_size) * 3
                for x in range(tile_size):
                    r8, g8, b8 = bgr565_to_rgb888(values[src])
                    src += 1
                    base = row_base + x * 3
                    out[base:base + 3] = bytes((r8, g8, b8))
    return out, width, height


def write_png(rgb_bytes, width, height, output_path):
    image = Image.frombytes("RGB", (width, height), bytes(rgb_bytes))
    image.save(output_path)


def parse_args():
    parser = argparse.ArgumentParser(description="Decode ZK-INKJET-UI-QVGA.bin")
    parser.add_argument(
        "--input",
        default="firmware/resources/ZK-INKJET-UI-QVGA.bin",
        help="Path to UI blob",
    )
    parser.add_argument(
        "--output",
        default="UI_QVGA_DECODED_CORRECT.png",
        help="Output PNG path",
    )
    parser.add_argument("--width", type=int, help="Image width")
    parser.add_argument("--height", type=int, help="Image height")
    parser.add_argument(
        "--tile",
        type=int,
        metavar="SIZE",
        help="Decode as tiled layout (SIZE x SIZE tiles, 3x3 grid)",
    )
    return parser.parse_args()


def select_dimensions(data_len, width, height, tile_size):
    if width and height:
        return width, height
    if tile_size:
        return tile_size * 3, tile_size * 3
    candidates = [(480, 480), (320, 240), (320, 480), (480, 320)]
    for w, h in candidates:
        if data_len % (w * h * 2) == 0:
            return w, h
    return 480, 480


def main():
    args = parse_args()
    with open(args.input, "rb") as f:
        data = f.read()
    if len(data) % 2 != 0:
        raise SystemExit("Input size is not aligned to 16-bit pixels.")
    values = struct.unpack("<{}H".format(len(data) // 2), data)
    width, height = select_dimensions(len(data), args.width, args.height, args.tile)
    frame_bytes = width * height * 2
    frame_count = len(data) // frame_bytes
    if frame_count < 1:
        raise SystemExit("Input size does not match selected dimensions.")

    base_root, base_ext = os.path.splitext(args.output)
    for frame_idx in range(frame_count):
        start = frame_idx * frame_bytes // 2
        end = start + (frame_bytes // 2)
        frame_values = values[start:end]
        if args.tile:
            rgb_bytes, out_w, out_h = decode_tiled(frame_values, args.tile, 3, 3)
        else:
            rgb_bytes = decode_linear(frame_values, width, height)
            out_w, out_h = width, height
        if frame_count > 1:
            output_path = f"{base_root}_frame{frame_idx:02d}{base_ext}"
        else:
            output_path = args.output
        write_png(rgb_bytes, out_w, out_h, output_path)
        print(f"Wrote {output_path} ({out_w}x{out_h})")


if __name__ == "__main__":
    main()
