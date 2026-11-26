"""sprites.py — the five cast designs as animated sprites.

The characters were designed as flat-vector art; this file cuts them out of their paper,
finds each mouth so it can be opened by the audio envelope, and hands film5.py a paste
routine. Detection results are cached in cast-mouths.json so every render is identical and
you can read (and correct) the numbers without guessing.

    python3 sprites.py            # detect + print, writes cast-mouths.json
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
CAST = os.path.join(os.path.dirname(HERE), "dark-lesson-04-last-word", "cast")
CACHE = os.path.join(HERE, "cast-mouths.json")

FILES = {
    "elder": "c1-elder-brother.png",
    "younger": "c2-younger-brother.png",
    "boudi": "c3-boudi.png",
    "customer": "c5-old-customer.png",
    "niece": "c4-niece.png",
}
SKIN = np.array([201, 139, 98])
PAPER = np.array([240, 238, 230], np.uint8)


def find_mouth(path):
    """Head from the skin profile, mouth from the lowest dark band inside it."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    skin = np.abs(a - SKIN).sum(2) < 110
    rows = np.where(skin.sum(1) > 8)[0]
    top = int(rows.min())
    widths = skin.sum(1)
    widest = widths[top: top + 220].max()
    bottom = top
    for y in range(top, min(top + 240, im.height)):
        bottom = y
        if widths[y] < widest * 0.34 and y > top + 40:
            break
    head_h = bottom - top
    probe = int(top + head_h * 0.80)
    dark = (a.mean(2) < 95)
    best = None
    for y in range(probe - int(head_h * 0.20), min(probe + int(head_h * 0.16), bottom)):
        xs = np.where(dark[y])[0]
        if len(xs) < 6:
            continue
        cx = int(np.median(xs))
        w = int(xs.max() - xs.min())
        if best is None or w > best[2]:
            best = (y, cx, w)
    y, cx, w = best if best else (probe, int(skin[y].mean()), 26)
    return {"head_top": top, "head_bottom": int(bottom),
            "x": int(cx), "y": int(y), "w": max(14, int(w * 0.62))}


# The detector is a first guess; these are the mouths as read off the art (source px).
# x,y = centre of the mouth line, w = its width, h = how far the jaw can drop from there.
MANUAL = {
    "elder":    dict(x=630, y=176, w=34, h=26),
    "younger":  dict(x=703, y=181, w=26, h=20),
    "boudi":    dict(x=672, y=172, w=22, h=16),
    "customer": dict(x=687, y=173, w=24, h=17),
    "niece":    dict(x=651, y=222, w=40, h=26),
}


def build(force=False):
    if os.path.exists(CACHE) and not force:
        return json.load(open(CACHE))
    out = {}
    for who, fn in FILES.items():
        g = find_mouth(os.path.join(CAST, fn))
        m = dict(MANUAL[who])
        m.update({"detected": g})
        out[who] = m
    json.dump(out, open(CACHE, "w"), indent=1)
    return out


CUT = {}


# the younger brother's file also holds the shop counter and the blue cup — cut to the man
WINDOW = {"elder": (515, 0, 930, 768), "younger": (565, 0, 862, 768),
          "boudi": (495, 0, 850, 768), "customer": (555, 0, 850, 768),
          "niece": (515, 0, 905, 768)}


def _exterior(bg, rounds=8):
    """Paper connected to the frame edge, by repeated scanline propagation (no scipy)."""
    ext = np.zeros_like(bg)
    ext[0, :] = bg[0, :]
    ext[-1, :] = bg[-1, :]
    ext[:, 0] |= bg[:, 0]
    ext[:, -1] |= bg[:, -1]
    for _ in range(rounds):
        l = np.maximum.accumulate(ext, axis=1)
        r = np.maximum.accumulate(ext[:, ::-1], axis=1)[:, ::-1]
        ext = ext | (bg & (l | r))
        d = np.maximum.accumulate(ext, axis=0)
        u = np.maximum.accumulate(ext[::-1], axis=0)[::-1]
        ext = ext | (bg & (d | u))
    return ext


def cut(who, night=False):
    """RGBA sprite with the paper removed. Written to cast-cut/ once, then cached."""
    cache = os.path.join(HERE, "cast-cut")
    os.makedirs(cache, exist_ok=True)
    fn = os.path.join(cache, "%s%s.png" % (who, "-night" if night else ""))
    idx = os.path.join(cache, "origins.json")
    if os.path.exists(idx):
        ORIGIN.update(json.load(open(idx)))
    if os.path.exists(fn) and who in ORIGIN:
        return Image.open(fn).convert("RGBA"), tuple(ORIGIN[who])
    raw = Image.open(os.path.join(CAST, FILES[who])).convert("RGB")
    xw = WINDOW[who]
    im = raw.crop(xw)
    a = np.asarray(im).astype(np.int16)
    bg = np.abs(a - PAPER.astype(np.int16)).sum(2) < 16
    alpha = np.where(_exterior(bg), 0, 255).astype(np.uint8)
    ys, xs = np.where(alpha > 0)
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    sp = im.crop(box).convert("RGBA")
    sp.putalpha(Image.fromarray(alpha[box[1]:box[3], box[0]:box[2]], "L"))
    ORIGIN[who] = (xw[0] + box[0], xw[1] + box[1])
    if night:
        arr = np.asarray(sp).astype(np.float32)
        arr[..., :3] *= np.array([0.46, 0.46, 0.52])
        sp = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
    sp.save(fn)
    json.dump(ORIGIN, open(idx, "w"), indent=1)
    return sp, ORIGIN[who]


ORIGIN = {}


if __name__ == "__main__":
    m = build(force=True)
    for k, v in m.items():
        g = v["detected"]
        print("%-9s mouth (%4d,%4d) w %2d h %2d   detector said (%4d,%4d) w %d, head %d-%d"
              % (k, v["x"], v["y"], v["w"], v["h"], g["x"], g["y"], g["w"],
                 g["head_top"], g["head_bottom"]))
