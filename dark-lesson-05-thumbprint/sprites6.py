"""sprites6.py — the five episode-5 faces as cut sprites with mouths.

The art comes from ../bangla-reel-cast/cut/ (already flattened to exact #F0EEE6 and cut on
its own alpha in that folder). This module does three jobs:

    * loads each cut once, and remembers its skin colour, sampled from the cheek
    * exposes MOUTH, the mouth position in cut-image pixels, so film6 can open it
    * tints a sprite for night scenes by multiplying — flat art stays flat when you
      multiply, so no shading appears

    python3 sprites6.py        # prints the mouth map, for eyeballing
"""
import functools
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CAST = os.path.join(HERE, "cast")

FILE = {
    "presenter": "c1-presenter.png",
    "shopkeeper": "c2-shopkeeper.png",
    "puller": "c3-rickshaw-puller.png",
    "student": "c4-student.png",
    "uncle": "c5-elder.png",
}

# mouth centre (x, y) and size (w, h) in cut-image pixels
MOUTH = {
    "presenter": dict(x=134, y=101, w=26, h=14),
    "shopkeeper": dict(x=143, y=79, w=22, h=12),
    "puller": dict(x=148, y=96, w=26, h=13, dy=4),
    "student": dict(x=130, y=91, w=28, h=15),
    "uncle": dict(x=153, y=113, w=30, h=14, dy=4),
}


@functools.lru_cache(maxsize=16)
def sprite(who):
    return Image.open(os.path.join(CAST, FILE[who])).convert("RGBA")


@functools.lru_cache(maxsize=16)
def skin(who):
    """The colour of this face: the median of the skin around the mouth.

    Sampling one pixel is not safe — a cheek edge, a moustache hair or an outline will
    poison it. So take a patch around the mouth and keep only the warm, bright pixels.
    """
    im = np.asarray(sprite(who).convert("RGB")).astype(np.int16)
    m = MOUTH[who]
    x0, x1 = int(m["x"] - m["w"] * 1.5), int(m["x"] + m["w"] * 1.5)
    y0, y1 = int(m["y"] - m["h"] * 2.2), int(m["y"] + m["h"] * 1.8)
    patch = im[max(0, y0):y1, max(0, x0):x1].reshape(-1, 3)
    warm = patch[(patch.sum(1) > 300) & (patch[:, 0] > patch[:, 2] + 40)]
    if len(warm) < 40:
        return (201, 139, 98)
    med = np.median(warm, axis=0)
    return tuple(int(v) for v in med)


def tint(im, k):
    """Multiply toward the dark — a night version of the same flat art."""
    rgba = im.convert("RGBA")
    out = rgba.convert("RGB").point(lambda v: int(v * k))
    out.putalpha(rgba.split()[3])
    return out


if __name__ == "__main__":
    for who in FILE:
        im = sprite(who)
        m = MOUTH[who]
        print(f"{who:11s} sprite {im.width}x{im.height}  mouth {m}  skin {skin(who)}")
