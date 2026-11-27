"""sprites7.py — the five episode-6 busts.

These cards are drawn in a much simpler language than the last cast: one heavy contour,
flat fills, a pastel sky, a sun and a cloud. The characters are head-and-chest only, cut
off flat at the bottom, so the film hides that edge behind a table.

Everything here is measured, not guessed:
    * `skin()` reads the face colour from a patch beside the mouth
    * `MOUTH` is the mouth centre and size in cut-image pixels
    * `dy` nudges the mouth down for the two moustached men so an open shape never
      merges with the tash

    python3 sprites7.py
"""
import functools
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CAST = os.path.join(HERE, "cast")

FILE = {
    "dada": "dada.png",
    "chele": "chele.png",
    "bou": "bou.png",
    "natni": "natni.png",
    "kagojwala": "kagojwala.png",
}

MOUTH = {
    "dada": dict(x=145, y=224, w=52, h=26, dy=0),
    "chele": dict(x=140, y=230, w=46, h=22, dy=0),
    "bou": dict(x=157, y=276, w=54, h=24),
    "natni": dict(x=180, y=200, w=64, h=28),
    "kagojwala": dict(x=145, y=236, w=58, h=24),
}


@functools.lru_cache(maxsize=16)
def sprite(who):
    return Image.open(os.path.join(CAST, FILE[who])).convert("RGBA")


@functools.lru_cache(maxsize=16)
def skin(who):
    im = np.asarray(sprite(who).convert("RGB")).astype(np.int16)
    m = MOUTH[who]
    x0, x1 = int(m["x"] - m["w"] * 1.6), int(m["x"] + m["w"] * 1.6)
    y0, y1 = int(m["y"] + m["h"] * 0.6), int(m["y"] + m["h"] * 2.4)
    patch = im[max(0, y0):y1, max(0, x0):x1].reshape(-1, 3)
    warm = patch[(patch.sum(1) > 240) & (patch[:, 0] > patch[:, 2] + 30)
                 & (patch[:, 0] < 228) & (patch[:, 1] < 190)]
    if len(warm) < 30:                                   # the mouth sits in a white beard
        warm = patch[(patch.sum(1) > 240) & (patch[:, 0] < 228) & (patch[:, 1] < 190)]
    med = np.median(warm, axis=0)
    return tuple(int(v) for v in med)


def tint(im, k):
    rgba = im.convert("RGBA")
    out = rgba.convert("RGB").point(lambda v: int(v * k))
    out.putalpha(rgba.split()[3])
    return out


if __name__ == "__main__":
    for who in FILE:
        im = sprite(who)
        print(f"{who:10s} {im.width}x{im.height}  mouth {MOUTH[who]}  skin {skin(who)}")
