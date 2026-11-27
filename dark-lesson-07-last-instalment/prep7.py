#!/usr/bin/env python3
"""prep7.py — cut the five Claude-2D plates out of their paper field.

The generated plates sit on near-flat paper. Clothes are the same off-white as the
paper, so a colour threshold would eat them: instead we flood-fill the background
region from the border (the ink outline stops it) and use *connectivity*, not colour,
to decide what is background.

Outputs
  cast/<name>.png        RGBA sprite, trimmed, 2 px padding
  cast/probe-faces.png   grid overlay for reading eye / mouth coordinates
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PLATES = os.path.join(HERE, "..", "character-style-preview", "cast-claude2d", "plates")
OUT = os.path.join(HERE, "cast")
PAPER = np.array([240, 238, 230], dtype=np.int16)
NAMES = ["01-dada", "02-bou", "03-chele", "04-natni", "05-kagojwala"]


def flatten(a, tol=22):
    """Replace the connected paper field with exact #F0EEE6; keep everything else."""
    h, w, _ = a.shape
    near = np.abs(a - PAPER).max(2) <= tol
    seen = np.zeros((h, w), bool)
    stack = []
    for x in range(w):
        stack += [(0, x), (h - 1, x)]
    for y in range(h):
        stack += [(y, 0), (y, w - 1)]
    while stack:
        y, x = stack.pop()
        if y < 0 or x < 0 or y >= h or x >= w or seen[y, x] or not near[y, x]:
            continue
        seen[y, x] = True
        stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    out = a.copy()
    out[seen] = PAPER
    return out, seen


def cut(name):
    src = os.path.join(PLATES, name + ".png")
    a = np.asarray(Image.open(src).convert("RGB")).astype(np.int16)
    flat, bg = flatten(a)
    rgb = flat.astype(np.uint8)

    alpha = np.where(bg, 0, 255).astype(np.uint8)
    # soften the one-pixel antialias seam: edge pixels blend toward paper
    d = np.abs(flat - PAPER).max(2)
    edge = (~bg) & (d < 26)
    alpha[edge] = np.clip((d[edge] - 4) * 34, 70, 255).astype(np.uint8)

    ys, xs = np.where(alpha > 8)
    y0, y1 = max(0, ys.min() - 2), min(a.shape[0], ys.max() + 3)
    x0, x1 = max(0, xs.min() - 2), min(a.shape[1], xs.max() + 3)
    rgba = np.dstack([rgb, alpha])[y0:y1, x0:x1]
    im = Image.fromarray(rgba, "RGBA")
    im.save(os.path.join(OUT, name + ".png"))
    return im


def probe(sprites):
    CW, CH, PAD = 430, 620, 12
    sheet = Image.new("RGB", (5 * (CW + PAD) + PAD, CH + 34), (26, 23, 20))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    for i, (name, im) in enumerate(sprites):
        head = im.crop((0, 0, im.width, round(im.height * 0.34)))
        k = min((CW - 20) / head.width, (CH - 40) / head.height)
        head = head.resize((round(head.width * k), round(head.height * k)), Image.LANCZOS)
        x = PAD + i * (CW + PAD)
        # paste on paper so the sprite's alpha is readable
        card = Image.new("RGB", (CW, CH), (240, 238, 230))
        card.paste(head, ((CW - head.width) // 2, 32), head)
        d2 = ImageDraw.Draw(card)
        for j in range(1, 10):
            gx = CW * j / 10
            gy = CH * j / 10
            d2.line([(gx, 32), (gx, CH)], fill=(200, 190, 175), width=1)
            d2.line([(10, gy), (CW - 10, gy)], fill=(200, 190, 175), width=1)
        for j in range(0, 11, 2):
            d2.text((CW * j / 10 + 2, CH - 24), f"{j/10:.1f}", font=f, fill=(150, 140, 126))
        sheet.paste(card, (x, 4))
        d.text((x + 4, 4), name, font=f, fill=(240, 230, 215))
    sheet.save(os.path.join(OUT, "probe-faces.png"))
    print("wrote probe-faces.png", sheet.size)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    sprites = [(n, cut(n)) for n in NAMES]
    for n, im in sprites:
        print(n, im.size)
    probe(sprites)
