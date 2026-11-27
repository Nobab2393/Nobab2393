"""Warm village environments for the lesson film — dusk palette, not horror.

Same hand-drawn language as the horror set, but lit for warmth: indigo sky, amber
lanterns, ochre dust, green banana groves. One cold scene (the forest) for contrast.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
_cache = {}


def _canvas(top, bottom, h=H, w=W):
    """Vertical sky gradient."""
    a = np.zeros((h, w, 3), dtype=np.float32)
    for i, (t, b) in enumerate(zip(top, bottom)):
        ramp = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        a[..., i] = t + (b - t) * ramp
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def _paper_grid(img, step=64, alpha=8):
    g = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for x in range(0, img.width, step):
        d.line([(x, 0), (x, img.height)], fill=(255, 255, 255, alpha))
    for y in range(0, img.height, step):
        d.line([(0, y), (img.width, y)], fill=(255, 255, 255, alpha))
    return Image.alpha_composite(img.convert("RGBA"), g).convert("RGB")


def _grain(img, amount=5.0, seed=1):
    rng = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.float32) + rng.normal(0, amount, (img.height, img.width, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def _vignette(img, s=0.5):
    w, h = img.size
    y, x = np.ogrid[:h, :w]
    r = np.sqrt(((x - w / 2) / (w * .62)) ** 2 + ((y - h / 2) / (h * .62)) ** 2)
    m = np.clip((r - .78) / (1.4 - .78), 0, 1) ** 1.4 * s
    a = np.asarray(img).astype(np.float32) * (1 - m)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def _glow(img, cx, cy, r, colour=(255, 190, 110), strength=0.7):
    """Soft radial light — a lantern, a fire, a shaft of sunlight."""
    w, h = img.size
    yy, xx = np.ogrid[:h, :w]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    m = (np.clip(1 - d, 0, 1) ** 2.2 * strength).astype(np.float32)
    a = np.asarray(img).astype(np.float32)
    for i in range(3):
        a[..., i] += m * colour[i]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def _hut(d, x, base, w, h, wall, roof, outline):
    d.rectangle([x, base - h, x + w, base], fill=wall, outline=outline, width=2)
    d.polygon([(x - w * .12, base - h), (x + w * .5, base - h - h * .55),
               (x + w * 1.12, base - h)], fill=roof, outline=outline)
    # door + one lit window
    d.rectangle([x + w * .42, base - h * .55, x + w * .58, base], fill=(38, 26, 22), outline=outline, width=2)
    d.rectangle([x + w * .12, base - h * .72, x + w * .3, base - h * .46],
                fill=(232, 176, 96), outline=outline, width=2)


def _palm(d, x, base, h, trunk=(62, 48, 34), leaf=(46, 92, 58), outline=(28, 34, 30)):
    d.line([(x, base), (x + h * 0.07, base - h)], fill=trunk, width=9)
    top = (x + h * 0.07, base - h)
    for ang in (-2.7, -2.2, -1.6, -1.0, -0.45, 0.15):
        ex = top[0] + math.cos(ang) * h * 0.34
        ey = top[1] + math.sin(ang) * h * 0.24
        d.line([top, (ex, ey)], fill=leaf, width=8)


def _fence(d, x0, x1, base, colour=(54, 42, 34), outline=(30, 24, 20)):
    d.line([(x0, base - 54), (x1, base - 54)], fill=colour, width=4)
    d.line([(x0, base - 26), (x1, base - 26)], fill=colour, width=4)
    for x in range(int(x0), int(x1), 56):
        d.line([(x, base - 70), (x, base)], fill=colour, width=5)


# ------------------------------------------------------------------ scenes
def porch():
    """Grandmother's porch at dusk: hut, lantern, low wall, first stars."""
    img = _canvas((44, 46, 92), (146, 104, 78))
    d = ImageDraw.Draw(img)
    rng = random.Random(3)
    # stars
    for _ in range(90):
        x, y = rng.randint(0, W), rng.randint(0, 420)
        v = rng.randint(150, 245)
        d.point((x, y), fill=(v, v, min(255, v + 20)))
    # far treeline
    for x in range(-60, W + 60, 70):
        d.ellipse([x, 500 + rng.randint(-40, 40), x + 150, 760], fill=(34, 40, 46))
    # ground — packed earth
    d.rectangle([0, 780, W, H], fill=(96, 72, 52))
    d.line([(0, 780), (W, 780)], fill=(60, 46, 34), width=3)
    for i in range(7):
        y = 820 + i * 38
        d.line([(0, y), (W, y)], fill=(86, 64, 46), width=2)
    # the hut, right
    _hut(d, 1180, 800, 520, 330, (108, 74, 52), (64, 44, 34), (36, 26, 20))
    # porch posts + roof beam, left
    d.rectangle([220, 470, 520, 800], fill=(88, 62, 44), outline=(36, 26, 20), width=3)
    d.polygon([(180, 480), (560, 480), (520, 400), (220, 400)], fill=(58, 40, 30), outline=(30, 22, 18))
    for px in (250, 500):
        d.rectangle([px - 10, 470, px + 10, 800], fill=(66, 46, 34), outline=(30, 22, 18), width=2)
    # hanging lantern
    d.line([(390, 400), (390, 452)], fill=(70, 60, 44), width=3)
    d.polygon([(366, 452), (414, 452), (406, 492), (374, 492)], fill=(240, 196, 120), outline=(120, 88, 40), width=2)
    # low wall, foreground
    d.rectangle([0, 800, 760, 840], fill=(86, 74, 62), outline=(48, 40, 34), width=2)
    _fence(d, 760, 1180, 800)
    img = _glow(img, 390, 472, 420, (255, 196, 118), 0.55)
    img = _glow(img, 1290, 660, 300, (255, 180, 96), 0.30)
    img = _paper_grid(img)
    img = _grain(img, 4, 11)
    return _vignette(img, 0.45)


def village_square():
    """Sujon's entrance: the square, well, shop, warm evening dust."""
    img = _canvas((38, 42, 84), (132, 96, 74))
    d = ImageDraw.Draw(img)
    rng = random.Random(9)
    for _ in range(70):
        x, y = rng.randint(0, W), rng.randint(0, 340)
        v = rng.randint(140, 230)
        d.point((x, y), fill=(v, v, min(255, v + 18)))
    for x in range(-80, W + 80, 88):
        d.ellipse([x, 460 + rng.randint(-30, 30), x + 170, 740], fill=(32, 38, 44))
    d.rectangle([0, 740, W, H], fill=(102, 76, 54))
    d.line([(0, 740), (W, 740)], fill=(62, 46, 34), width=3)
    _hut(d, 90, 760, 380, 250, (104, 72, 50), (62, 42, 32), (34, 24, 18))
    _hut(d, 1380, 768, 420, 270, (112, 78, 54), (68, 46, 34), (34, 24, 18))
    # shop awning
    d.polygon([(560, 660), (980, 660), (940, 600), (600, 600)], fill=(150, 62, 48), outline=(60, 26, 22))
    d.rectangle([600, 660, 940, 770], fill=(78, 56, 42), outline=(34, 24, 18), width=3)
    # the well
    d.ellipse([1030, 760, 1300, 850], fill=(70, 66, 62), outline=(34, 32, 30), width=3)
    d.ellipse([1062, 772, 1268, 828], fill=(28, 28, 30), outline=(46, 44, 40), width=2)
    d.line([(1050, 800), (1050, 640)], fill=(58, 44, 34), width=6)
    d.line([(1280, 800), (1280, 640)], fill=(58, 44, 34), width=6)
    d.line([(1050, 640), (1280, 640)], fill=(58, 44, 34), width=5)
    # dust haze
    for _ in range(120):
        x, y = rng.randint(0, W), rng.randint(560, 900)
        d.point((x, y), fill=(120, 96, 72))
    img = _glow(img, 770, 690, 330, (255, 186, 110), 0.40)
    img = _glow(img, 1360, 700, 280, (255, 176, 104), 0.26)
    img = _paper_grid(img)
    img = _grain(img, 4, 12)
    return _vignette(img, 0.45)


def fireside():
    """Kamal by the fire at the edge of the grove."""
    img = _canvas((30, 30, 58), (78, 62, 52))
    d = ImageDraw.Draw(img)
    rng = random.Random(17)
    for _ in range(60):
        x, y = rng.randint(0, W), rng.randint(0, 300)
        v = rng.randint(120, 210)
        d.point((x, y), fill=(v, v, min(255, v + 16)))
    for x in range(-100, W + 100, 100):
        d.ellipse([x, 420 + rng.randint(-40, 40), x + 190, 720], fill=(26, 30, 30))
    for x in (180, 420, 1500, 1740):
        _palm(d, x, 820, 460, trunk=(52, 40, 30), leaf=(34, 62, 44))
    d.rectangle([0, 800, W, H], fill=(74, 56, 42))
    d.line([(0, 800), (W, 800)], fill=(42, 32, 24), width=3)
    # fire ring
    d.ellipse([820, 840, 1100, 920], fill=(48, 38, 30), outline=(28, 22, 18), width=3)
    for i, (cx, hh) in enumerate([(900, 46), (960, 70), (1020, 54)]):
        d.polygon([(cx - 22, 862), (cx, 862 - hh), (cx + 22, 862)], fill=(246, 168, 62))
        d.polygon([(cx - 12, 862), (cx, 862 - hh * 0.6), (cx + 12, 862)], fill=(255, 224, 140))
    # log
    d.rectangle([700, 856, 880, 884], fill=(52, 38, 28), outline=(28, 20, 16), width=2)
    img = _glow(img, 960, 850, 520, (255, 154, 70), 0.62)
    img = _paper_grid(img)
    img = _grain(img, 4, 13)
    return _vignette(img, 0.55)


def forest():
    """The memory: cold, tall, the light thinning. Deliberately wrong colour."""
    img = _canvas((16, 30, 28), (44, 62, 46))
    d = ImageDraw.Draw(img)
    rng = random.Random(29)
    # receding trunks
    for depth, (col, wid, n) in enumerate([((30, 44, 34), 16, 9), ((22, 34, 26), 26, 6),
                                          ((14, 22, 18), 44, 4)]):
        for i in range(n):
            x = rng.randint(-40, W + 40)
            top = rng.randint(-100, 120) + depth * 40
            d.rectangle([x, top, x + wid, 900], fill=col)
    d.rectangle([0, 860, W, H], fill=(36, 40, 30))
    # light shafts from above
    shafts = Image.new("RGB", (W, H), (0, 0, 0))
    sd = ImageDraw.Draw(shafts)
    for i in range(4):
        x = 300 + i * 420
        sd.polygon([(x, 0), (x + 150, 0), (x + 400, H), (x + 180, H)], fill=(30, 36, 20))
    # one warm shaft down the middle: the only way out, and it is not where he looks
    sd.polygon([(760, 0), (940, 0), (1180, H), (900, H)], fill=(64, 58, 34))
    shafts = shafts.filter(ImageFilter.GaussianBlur(60))
    img = Image.fromarray(np.clip(np.asarray(img).astype(np.int16) +
                                  np.asarray(shafts).astype(np.int16), 0, 255).astype(np.uint8))
    # ground mist
    mist = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mist)
    for _ in range(60):
        cx, cy = rng.randint(0, W), rng.randint(760, 1040)
        rx, ry = rng.randint(160, 460), rng.randint(30, 90)
        md.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=rng.randint(40, 90))
    mist = mist.filter(ImageFilter.GaussianBlur(50)).point(lambda v: int(v * 0.55))
    img = Image.composite(Image.new("RGB", (W, H), (150, 168, 140)), img, mist)
    # thicket: dark undergrowth either side, framing a corridor
    under = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ud = ImageDraw.Draw(under)
    for side in (-1, 1):
        x0 = 0 if side < 0 else W
        for _ in range(46):
            cx = x0 + side * rng.randint(0, 430)
            cy = rng.randint(740, 980)
            rx, ry = rng.randint(60, 150), rng.randint(50, 120)
            ud.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                       fill=(10, 18, 14, rng.randint(150, 230)))
    under = under.filter(ImageFilter.GaussianBlur(26))
    img = Image.alpha_composite(img.convert("RGBA"), under).convert("RGB")
    img = _glow(img, 1000, 240, 640, (150, 170, 120), 0.22)
    img = _paper_grid(img, alpha=7)
    img = _grain(img, 5, 14)
    return _vignette(img, 0.62)


def banyan():
    """The headman under the banyan: broad canopy, roots, last light."""
    img = _canvas((52, 44, 78), (168, 116, 78))
    d = ImageDraw.Draw(img)
    rng = random.Random(41)
    d.rectangle([0, 800, W, H], fill=(104, 82, 58))
    d.line([(0, 800), (W, 800)], fill=(62, 46, 34), width=3)
    # canopy
    for i in range(26):
        cx = rng.randint(-100, W + 100)
        cy = rng.randint(40, 300)
        rw, rh = rng.randint(190, 330), rng.randint(90, 170)
        d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(38, 62, 42))
    # trunk + aerial roots
    d.rectangle([880, 300, 1040, 820], fill=(60, 44, 32), outline=(30, 22, 16), width=3)
    for i in range(11):
        x = 700 + i * 52
        d.line([(x, 340 + rng.randint(0, 60)), (x - 30 + rng.randint(0, 60), 820)],
               fill=(48, 36, 26), width=max(3, 9 - i % 4))
    # a stone platform
    d.rectangle([760, 820, 1180, 872], fill=(96, 92, 84), outline=(46, 44, 40), width=3)
    img = _glow(img, 1420, 720, 420, (255, 178, 96), 0.34)
    img = _paper_grid(img)
    img = _grain(img, 4, 15)
    return _vignette(img, 0.5)


def black():
    return Image.new("RGB", (W, H), (12, 12, 14))


def get(name):
    if name not in _cache:
        _cache[name] = {"porch": porch, "square": village_square, "fire": fireside,
                        "forest": forest, "banyan": banyan, "black": black}[name]()
    return _cache[name]
