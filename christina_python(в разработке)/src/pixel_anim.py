"""Кристина — отдельная пиксельная анимация 32x32 (numpy).

Задний вид Plymouth Fury 1958 ночью на мокром шоссе: пульсирующие
стоп-сигналы, дым из выхлопа, ливень и редкие красные глаза в темноте.
Запуск: python pixel_anim.py [--html out.html] [--fps 12] [--loops 1]
"""

import argparse
import sys
import time

import numpy as np

WIDTH = 32
HEIGHT = 32
FRAMES = 96

SKY = 0
SKY_LOW = 1
HORIZON = 2
ROAD = 3
ROAD_LIGHT = 4
LINE = 5
BODY_DARK = 6
BODY = 7
BODY_LIGHT = 8
CHROME = 9
CHROME_DARK = 10
TAIL = 11
TAIL_GLOW = 12
SMOKE = 13
SMOKE_LIGHT = 14
GLASS = 15
BEAM = 16
RAIN = 17
EYE = 18
BLACK = 19
BODY_SHADE = 20

PALETTE = np.array(
    [
        (6, 8, 20),
        (13, 17, 40),
        (46, 28, 54),
        (24, 24, 30),
        (42, 42, 52),
        (198, 198, 208),
        (104, 12, 18),
        (170, 20, 30),
        (214, 54, 60),
        (188, 194, 204),
        (116, 122, 136),
        (255, 40, 60),
        (255, 128, 128),
        (118, 118, 128),
        (174, 174, 184),
        (18, 24, 40),
        (255, 240, 190),
        (116, 156, 220),
        (255, 64, 52),
        (0, 0, 0),
        (86, 8, 12),
    ],
    dtype=np.uint8,
)


def noise(seed, salt):
    value = (seed * 2654435761 + salt * 40503) & 0xFFFFFFFF
    return value / 0xFFFFFFFF


def fill(canvas, index, top, left, bottom, right):
    canvas[max(top, 0) : min(bottom, HEIGHT), max(left, 0) : min(right, WIDTH)] = index


def disc(canvas, index, cy, cx, radius):
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            inside = 0 <= y < HEIGHT and 0 <= x < WIDTH
            if inside and (y - cy) ** 2 + (x - cx) ** 2 <= radius * radius:
                canvas[y, x] = index


def sky(canvas, phase):
    fill(canvas, SKY, 0, 0, HEIGHT, WIDTH)
    fill(canvas, SKY_LOW, 6, 0, 13, WIDTH)
    fill(canvas, HORIZON, 12, 0, 14, WIDTH)
    horizon_shift = int(2 * np.sin(phase * 2 * np.pi))
    fill(canvas, HORIZON, 11 + horizon_shift, 0, 12 + horizon_shift, WIDTH)


def road(canvas, phase):
    fill(canvas, ROAD, 14, 0, HEIGHT, WIDTH)
    offset = int(phase * 16) % 4
    for x in range(-4 + offset, WIDTH, 8):
        fill(canvas, LINE, 30, x, 32, x + 4)
        fill(canvas, ROAD_LIGHT, 28, x + 1, 29, x + 3)
    for x in range(0, WIDTH, 3):
        y = 24 + int(3 * noise(x, 7))
        canvas[y, x] = ROAD_LIGHT


def car(canvas, phase, bob):
    left, right = 7, 25
    top = 14 - bob
    fill(canvas, BODY_DARK, top, 11, top + 1, 21)
    fill(canvas, GLASS, top + 1, 11, top + 4, 21)
    fill(canvas, BODY_SHADE, top + 1, 10, top + 5, 11)
    fill(canvas, BODY_SHADE, top + 1, 21, top + 5, 22)
    fill(canvas, BODY, top + 4, left, top + 10, right)
    fill(canvas, BODY_LIGHT, top + 4, left + 1, top + 5, right - 1)
    fill(canvas, BODY_DARK, top + 9, left, top + 11, right)
    fill(canvas, CHROME, top + 1, left, top + 8, left + 1)
    fill(canvas, CHROME, top + 1, right - 1, top + 8, right)
    fill(canvas, CHROME, top + 8, left, top + 9, right)

    pulse = 0.5 + 0.5 * np.sin(phase * 2 * np.pi * 3)
    glow = TAIL_GLOW if pulse > 0.62 else TAIL
    fill(canvas, glow, top + 5, left + 1, top + 7, left + 4)
    fill(canvas, glow, top + 5, right - 4, top + 7, right - 1)
    if pulse > 0.8:
        disc(canvas, TAIL_GLOW, top + 6, left + 2, 1)
        disc(canvas, TAIL_GLOW, top + 6, right - 2, 1)

    fill(canvas, BLACK, top + 10, left + 1, top + 12, left + 4)
    fill(canvas, BLACK, top + 10, right - 4, top + 12, right - 1)
    fill(canvas, CHROME_DARK, top + 10, left + 4, top + 11, right - 4)


def exhaust(canvas, phase):
    for i in range(8):
        age = (phase + i / 8.0) % 1.0
        y = 27 - int(age * 7)
        x = 6 - int(age * 6)
        level = SMOKE_LIGHT if age < 0.35 else SMOKE
        disc(canvas, level, y, x, 1 + int(age * 2))


def rain(canvas, phase):
    for i in range(34):
        x = int(noise(i, 1) * WIDTH)
        y = int((noise(i, 2) * HEIGHT + phase * 20) % HEIGHT)
        canvas[max(y - 1, 0), x] = RAIN


def eyes(canvas, phase):
    window = (phase - 0.72) % 1.0
    if window > 0.16:
        return
    blink = 1.0 - abs((window / 0.16) * 2 - 1)
    if blink > 0.15:
        canvas[7, 9] = EYE
        canvas[7, 10] = EYE
        canvas[7, 22] = EYE
        canvas[7, 23] = EYE


def build_frame(index):
    phase = (index % FRAMES) / float(FRAMES)
    canvas = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    bob = 1 if (index // 6) % 2 else 0
    sky(canvas, phase)
    road(canvas, phase)
    car(canvas, phase, bob)
    exhaust(canvas, phase)
    rain(canvas, phase)
    eyes(canvas, phase)
    return PALETTE[canvas]


def build_frames(count=FRAMES):
    return [build_frame(index) for index in range(count)]


def render_terminal(frames, fps, loops):
    out = sys.stdout
    out.write("\x1b[2J\x1b[?25l")
    try:
        for _ in range(loops):
            for frame in frames:
                rows = ["\x1b[H"]
                for row in frame:
                    rows.append(
                        "".join(
                            f"\x1b[48;2;{int(px[0])};{int(px[1])};{int(px[2])}m  "
                            for px in row
                        )
                        + "\x1b[0m"
                    )
                out.write("\n".join(rows) + "\n")
                out.flush()
                time.sleep(1.0 / fps)
    except KeyboardInterrupt:
        pass
    finally:
        out.write("\x1b[0m\x1b[?25h\n")


def render_ascii(frames):
    letters = " .:-=+*#%"
    for frame in frames:
        for row in frame:
            line = "".join(
                letters[
                    int((int(px[0]) + int(px[1]) + int(px[2])) / 3 / 26) % len(letters)
                ]
                for px in row
            )
            print(line)
        print("-" * WIDTH)


def render_html(frames, fps, path):
    encoded = []
    for frame in frames:
        data = frame.reshape(-1, 3)
        encoded.append(
            "".join(
                "{:02x}{:02x}{:02x}".format(*tuple(int(v) for v in px)) for px in data
            )
        )
    payload = ",\n".join(f'"{chunk}"' for chunk in encoded)
    template = """<!doctype html>
<html lang="ru">
<meta charset="utf-8">
<title>Кристина — пиксельная анимация 32x32</title>
<style>
  html, body {{ margin: 0; height: 100%; background: #05060a; }}
  body {{ display: grid; place-items: center; }}
  #frame {{ image-rendering: pixelated; background: #000;
            width: min(86vmin, 640px); height: min(86vmin, 640px);
            box-shadow: 0 0 60px rgba(255, 40, 60, .28),
                        0 0 0 2px #1b1f2e; }}
  #scan {{ position: fixed; inset: 0; pointer-events: none;
           background: repeating-linear-gradient(
             180deg, rgba(0,0,0,.28) 0 1px, rgba(0,0,0,0) 1px 3px); }}
</style>
<canvas id="frame" width="32" height="32"></canvas>
<div id="scan"></div>
<script>
const FRAMES = [
{payload}
];
const canvas = document.getElementById('frame');
const ctx = canvas.getContext('2d');
const image = ctx.createImageData(32, 32);
let index = 0;
function paint() {{
  const hex = FRAMES[index];
  for (let p = 0; p < 1024; p += 1) {{
    image.data[p * 4] = parseInt(hex.substr(p * 6, 2), 16);
    image.data[p * 4 + 1] = parseInt(hex.substr(p * 6 + 2, 2), 16);
    image.data[p * 4 + 2] = parseInt(hex.substr(p * 6 + 4, 2), 16);
    image.data[p * 4 + 3] = 255;
  }}
  ctx.putImageData(image, 0, 0);
  index = (index + 1) % FRAMES.length;
}}
paint();
setInterval(paint, 1000 / {fps});
</script>
</html>
"""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(template.format(payload=payload, fps=fps))
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Пиксельная анимация «Кристина» 32x32")
    parser.add_argument("--fps", type=float, default=12.0, help="кадров в секунду")
    parser.add_argument(
        "--loops", type=int, default=1, help="сколько раз проиграть цикл"
    )
    parser.add_argument("--html", help="сохранить самодостаточную HTML-страницу")
    parser.add_argument("--ascii", action="store_true", help="показать кадры текстом")
    parser.add_argument("--preview", type=int, help="напечатать один кадр как ASCII")
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    if args.preview is not None:
        render_ascii([build_frame(args.preview)])
    else:
        frames = build_frames()
        if args.html:
            path = render_html(frames, args.fps, args.html)
            print(f"Готово: {path} (кадров: {len(frames)}, {args.fps:.1f} fps)")
        elif args.ascii:
            render_ascii(frames[:2])
        else:
            render_terminal(frames, args.fps, args.loops)
    return 0


if __name__ == "__main__":
    sys.exit(main())
