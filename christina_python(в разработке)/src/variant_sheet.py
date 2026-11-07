"""Контактный лист вариантов отрисовки сцен 11–18.

Собирает PNG: строки — сцены, столбцы — 8 вариантов каждой сцены.
Запуск: python variant_sheet.py [--frame 25] [--scale 3] [--out файл.png]
"""

import argparse
import struct
import sys
import zlib

import numpy as np

import christina as ch


def write_png(path, rgb):
    height, width, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[row].tobytes() for row in range(height))

    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as handle:
        handle.write(png)


def build_sheet(scenes, frame_index, scale):
    cells = len(scenes) * ch.SCENE_VARIANTS
    sheet = np.zeros(
        (len(scenes) * ch.HEIGHT * scale, ch.SCENE_VARIANTS * ch.WIDTH * scale, 3),
        dtype=np.uint8,
    )
    for row, scene_idx in enumerate(scenes):
        for variant in range(ch.SCENE_VARIANTS):
            frame = ch.build_scene_frame(scene_idx, variant, frame_index)
            big = np.repeat(np.repeat(frame, scale, axis=0), scale, axis=1)
            row_start = row * ch.HEIGHT * scale
            col_start = variant * ch.WIDTH * scale
            sheet[
                row_start : row_start + ch.HEIGHT * scale,
                col_start : col_start + ch.WIDTH * scale,
            ] = big
            sheet[row_start, :] = 255
            sheet[:, col_start] = 255
    return sheet, cells


def main(argv=None):
    parser = argparse.ArgumentParser(description="Контактный лист вариантов сцен 11–18")
    parser.add_argument(
        "--frame", type=int, default=25, help="номер кадра внутри сцены"
    )
    parser.add_argument("--scale", type=int, default=3, help="увеличение пикселя")
    parser.add_argument(
        "--out", default="scenes_11_18_variants.png", help="куда писать PNG"
    )
    args = parser.parse_args(argv)

    scenes = sorted(ch.SCENE_PAINTERS)
    sheet, cells = build_sheet(scenes, args.frame, args.scale)
    write_png(args.out, sheet)
    print(
        f"Готово: {args.out} — сцен {len(scenes)}, "
        f"вариантов {ch.SCENE_VARIANTS}, ячеек {cells}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
