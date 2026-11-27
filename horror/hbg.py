"""Horror environment set for the stickman short — B1 paper world, night palette.

Same paper + faint grid language as the B1 reference, but lit for horror: cold moon
instead of warm daylight, motivated light sources (torch, dying lamp, window shaft),
and fog layered between depth planes.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080

PAPER = (24, 25, 29)          # night paper — near-black with a blue cast
INK = (232, 233, 236)         # chalk-white "ink" lines on night paper
GRID = (255, 255, 255, 7)

_cache = {}


# ------------------------------------------------------------------ helpers
def _paper(w, h, step=64, base=None):
    img = Image.new("RGB", (w, h), base or PAPER)
    g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=GRID, width=1)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=GRID, width=1)
    return Image.alpha_composite(img.convert("RGBA"), g).convert("RGB")


def _vignette(img, strength=0.85, radius=0.78):
    w, h = img.size
    y, x = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    r = np.sqrt(((x - cx) / (w * 0.62)) ** 2 + ((y - cy) / (h * 0.62)) ** 2)
    m = np.clip((r - radius) / (1.35 - radius), 0, 1) ** 1.6 * strength
    a = np.asarray(img).astype(np.float32)
    a *= (1 - m)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _grain(img, amount=7.0, seed=1):
    rng = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.float32)
    n = rng.normal(0, amount, (a.shape[0], a.shape[1], 1))
    a = a + n
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _fog(img, y0, y1, colour=(150, 158, 178), peak=70, seed=3):
    """Horizontal fog band, feathered — the cheapest way to get depth."""
    w, h = img.size
    rng = random.Random(seed)
    band = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(band)
    for i in range(90):
        cx = rng.uniform(-0.1, 1.1) * w
        cy = rng.uniform(y0, y1)
        rx = rng.uniform(0.08, 0.30) * w
        ry = rng.uniform(0.02, 0.07) * h
        a = rng.uniform(0.25, 1.0)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=int(255 * a))
    band = band.filter(ImageFilter.GaussianBlur(48))
    band = band.point(lambda v: int(v / 255 * peak))
    layer = Image.new("RGB", (w, h), colour)
    return Image.composite(layer, img, band)


def _moon(img, cx, cy, r, col=(226, 231, 222)):
    d = ImageDraw.Draw(img)
    # halo
    glow = Image.new("RGB", img.size, (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(9, 0, -1):
        rr = r * (1 + i * 0.42)
        v = int(30 - i * 3)
        gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(v, v + 2, v + 6))
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    img = Image.fromarray(np.clip(np.asarray(img).astype(np.int16) +
                                  np.asarray(glow).astype(np.int16), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # a few craters, hand-drawn style
    for (ox, oy, rr) in [(-0.3, -0.25, 0.16), (0.22, 0.1, 0.12), (-0.05, 0.42, 0.09)]:
        rr2 = r * rr
        d.ellipse([cx + ox * r - rr2, cy + oy * r - rr2, cx + ox * r + rr2, cy + oy * r + rr2],
                  fill=(203, 208, 200))
    return img


def _dead_tree(d, x, ground, h, colour, rng, depth=0):
    """Recursive bare tree — the classic horror silhouette."""
    def branch(x0, y0, ang, ln, w, lvl):
        x1 = x0 + math.cos(ang) * ln
        y1 = y0 - math.sin(ang) * ln
        d.line([(x0, y0), (x1, y1)], fill=colour, width=max(1, int(w)))
        if lvl <= 0 or ln < 16:
            return
        for sign in (-1, 1):
            branch(x1, y1, ang + sign * rng.uniform(0.22, 0.55),
                   ln * rng.uniform(0.62, 0.78), w * 0.62, lvl - 1)
    branch(x, ground, math.pi / 2, h * 0.42, 9, depth)


def _house_block(d, x0, x1, base_y, top_y, colour, outline, rng):
    """Facade with windows — some lit, most dead."""
    d.rectangle([x0, top_y, x1, base_y], fill=colour, outline=outline, width=2)
    cols = max(2, int((x1 - x0) // 120))
    rows = max(2, int((base_y - top_y) // 130))
    for r in range(rows):
        for c in range(cols):
            wx = x0 + 40 + c * (x1 - x0 - 60) / cols
            wy = top_y + 40 + r * (base_y - top_y - 60) / rows
            ww, wh = 34, 52
            lit = rng.random() < 0.12
            d.rectangle([wx, wy, wx + ww, wy + wh],
                        fill=(196, 150, 78) if lit else (12, 13, 16), outline=outline, width=1)


# ------------------------------------------------------------------ scenes
def gate():
    """Exterior: the barred gate, dead tree, moon, broken wall."""
    img = _paper(W, H)
    rng = random.Random(11)
    d = ImageDraw.Draw(img)
    # ground
    d.rectangle([0, 880, W, H], fill=(16, 17, 20))
    d.line([(0, 880), (W, 880)], fill=(58, 62, 70), width=3)
    # moon behind the house
    img = _moon(img, 1430, 250, 78)
    d = ImageDraw.Draw(img)
    # the house mass, far
    d.polygon([(520, 880), (520, 470), (760, 300), (1180, 300), (1420, 470), (1420, 880)],
              fill=(19, 20, 24), outline=(70, 74, 84))
    d.polygon([(700, 300), (760, 300), (760, 210), (700, 210)], fill=(19, 20, 24),
              outline=(70, 74, 84))
    # two lit windows upstairs — warm, wrong
    for (wx, wy) in [(640, 500), (940, 500)]:
        d.rectangle([wx, wy, wx + 90, wy + 130], fill=(206, 152, 70), outline=(90, 70, 40), width=2)
        d.line([(wx + 45, wy), (wx + 45, wy + 130)], fill=(90, 70, 40), width=2)
        d.line([(wx, wy + 65), (wx + 90, wy + 65)], fill=(90, 70, 40), width=2)
    # boundary wall + iron gate
    d.rectangle([0, 760, W, 880], fill=(22, 23, 27), outline=(72, 76, 86), width=2)
    for x in range(60, W, 74):
        d.line([(x, 700), (x, 880)], fill=(86, 90, 100), width=5)
        d.line([(x, 700), (x + 3, 640)], fill=(86, 90, 100), width=3)   # spear tips
    d.line([(0, 706), (W, 706)], fill=(86, 90, 100), width=5)
    d.line([(0, 800), (W, 800)], fill=(86, 90, 100), width=4)
    # gate opening (the way in) — a dark arch
    d.rectangle([900, 700, 1080, 880], fill=(8, 9, 11))
    # dead tree left
    _dead_tree(d, 300, 900, 520, (34, 36, 42), rng, depth=5)
    # crows on the wall
    for cx in (1250, 1300):
        d.ellipse([cx, 700, cx + 26, 718], fill=(10, 10, 12))
        d.line([(cx + 22, 706), (cx + 34, 702)], fill=(10, 10, 12), width=2)
    img = _fog(img, 640, 940, peak=46)
    img = _vignette(img, 0.9)
    img = _grain(img, 6)
    return img


def courtyard():
    """Inside the gate: the well, hanging lamp, courtyard, wet stone."""
    img = _paper(W, H)
    rng = random.Random(23)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 840, W, H], fill=(15, 16, 19))
    # house wall behind, with the door
    d.rectangle([0, 150, W, 840], fill=(20, 21, 25))
    d.rectangle([760, 380, 1160, 840], fill=(11, 12, 14), outline=(62, 66, 76), width=3)
    d.arc([760, 300, 1160, 460], 180, 360, fill=(62, 66, 76), width=3)
    # door panels
    d.line([(960, 400), (960, 840)], fill=(46, 50, 58), width=2)
    # pillars
    for px in (300, 1620):
        d.rectangle([px - 46, 260, px + 46, 840], fill=(24, 25, 30), outline=(58, 62, 72), width=2)
        d.rectangle([px - 60, 232, px + 60, 268], fill=(30, 31, 37), outline=(58, 62, 72), width=2)
    # hanging lamp
    d.line([(1340, 0), (1340, 360)], fill=(70, 74, 84), width=3)
    d.polygon([(1300, 360), (1380, 360), (1360, 430), (1320, 430)], fill=(38, 34, 26),
              outline=(150, 122, 70), width=2)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(10, 0, -1):
        rr = i * 46
        gd.ellipse([1340 - rr, 400 - rr, 1340 + rr, 400 + rr], fill=(14, 11, 6))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.fromarray(np.clip(np.asarray(img).astype(np.int16) +
                                  np.asarray(glow).astype(np.int16), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.ellipse([1322, 372, 1358, 408], fill=(255, 214, 132))
    # the well, right foreground
    d.ellipse([1460, 800, 1800, 900], fill=(13, 14, 17), outline=(62, 66, 76), width=3)
    d.ellipse([1496, 812, 1764, 880], fill=(6, 6, 7), outline=(48, 52, 60), width=2)
    # stone slabs
    for i in range(6):
        y = 860 + i * 38
        d.line([(0, y), (W, y)], fill=(26, 28, 33), width=2)
    img = _fog(img, 700, 1000, peak=30)
    img = _vignette(img, 0.9)
    img = _grain(img, 6, seed=4)
    return img


def corridor():
    """Inner corridor: arches receding, torchlight cone, name wall."""
    img = _paper(W, H)
    rng = random.Random(31)
    d = ImageDraw.Draw(img)
    # perspective floor + ceiling
    d.polygon([(0, 0), (W, 0), (W, 120), (0, 120)], fill=(14, 15, 18))
    d.polygon([(0, H), (W, H), (W, 900), (0, 900)], fill=(16, 17, 20))
    d.polygon([(0, 120), (W, 120), (1400, 520), (520, 520)], fill=(19, 20, 24))
    d.polygon([(0, 900), (W, 900), (1400, 620), (520, 620)], fill=(18, 19, 23))
    d.polygon([(480, 120), (520, 620), (1400, 620), (1440, 120)], fill=(9, 10, 12))
    # receding arches
    for i, (x0, x1, top, bot) in enumerate([(150, 1770, 60, 980), (330, 1590, 150, 900),
                                           (470, 1450, 230, 820), (570, 1350, 290, 760)]):
        d.arc([x0, top, x1, top + (bot - top) * 0.9], 180, 360,
              fill=(52 + i * 6, 56 + i * 6, 66 + i * 6), width=4)
        d.line([(x0, top + (bot - top) * 0.45), (x0, bot)], fill=(40 + i * 5, 44 + i * 5, 52 + i * 5), width=4)
        d.line([(x1, top + (bot - top) * 0.45), (x1, bot)], fill=(40 + i * 5, 44 + i * 5, 52 + i * 5), width=4)
    # the name wall, left
    d.rectangle([110, 300, 470, 860], fill=(21, 22, 26), outline=(56, 60, 70), width=3)
    for r in range(7):
        for c in range(3):
            x = 150 + c * 108
            y = 350 + r * 68
            for k in range(rng.randint(3, 6)):
                d.line([(x, y + k * 8), (x + rng.randint(40, 80), y + k * 8)],
                       fill=(96 + rng.randint(-14, 14), 100, 108), width=2)
    # torch cone from the right
    cone = Image.new("RGB", (W, H), (0, 0, 0))
    cd = ImageDraw.Draw(cone)
    cd.polygon([(1880, 300), (760, 520), (760, 900), (1880, 760)], fill=(40, 33, 20))
    cone = cone.filter(ImageFilter.GaussianBlur(70))
    img = Image.fromarray(np.clip(np.asarray(img).astype(np.int16) +
                                  np.asarray(cone).astype(np.int16), 0, 255).astype(np.uint8))
    img = _fog(img, 600, 1000, peak=34, seed=7)
    img = _vignette(img, 0.94)
    img = _grain(img, 7, seed=9)
    return img


def window_room():
    """Side room: one barred window, moonlight shaft, an empty chair."""
    img = _paper(W, H, base=(20, 21, 25))
    rng = random.Random(41)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 860, W, H], fill=(15, 16, 19))
    # window
    d.rectangle([1180, 240, 1620, 640], fill=(30, 38, 52), outline=(74, 80, 92), width=4)
    for x in (1290, 1400, 1510):
        d.line([(x, 240), (x, 640)], fill=(74, 80, 92), width=4)
    for y in (380, 510):
        d.line([(1180, y), (1620, y)], fill=(74, 80, 92), width=4)
    # moonlight shaft falling left across the floor
    shaft = Image.new("RGB", (W, H), (0, 0, 0))
    sd = ImageDraw.Draw(shaft)
    sd.polygon([(1180, 240), (1620, 240), (1620, 640), (1180, 640)], fill=(26, 30, 40))
    sd.polygon([(1180, 240), (1620, 640), (980, 1080), (300, 1080)], fill=(20, 24, 32))
    shaft = shaft.filter(ImageFilter.GaussianBlur(40))
    img = Image.fromarray(np.clip(np.asarray(img).astype(np.int16) +
                                  np.asarray(shaft).astype(np.int16), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    # a chair, turned to face the corner
    d.line([(700, 780), (700, 930)], fill=(60, 64, 74), width=6)
    d.line([(820, 780), (820, 930)], fill=(60, 64, 74), width=6)
    d.line([(660, 790), (860, 790)], fill=(60, 64, 74), width=7)
    d.line([(660, 700), (860, 700)], fill=(60, 64, 74), width=7)
    d.line([(660, 700), (660, 790)], fill=(60, 64, 74), width=6)
    d.line([(860, 700), (860, 790)], fill=(60, 64, 74), width=6)
    # cracks on the plaster
    for _ in range(14):
        x, y = rng.randint(80, 1100), rng.randint(160, 800)
        pts = [(x, y)]
        for _ in range(rng.randint(2, 5)):
            x += rng.randint(-60, 60); y += rng.randint(20, 90)
            pts.append((x, y))
        ImageDraw.Draw(img).line(pts, fill=(34, 36, 42), width=2)
    img = _fog(img, 620, 1040, peak=30, seed=12)
    img = _vignette(img, 0.95)
    img = _grain(img, 7, seed=13)
    return img


def throne():
    """The hall: the landlord's chair, tall windows, dust, the dark at the back."""
    img = _paper(W, H, base=(17, 18, 21))
    rng = random.Random(51)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 880, W, H], fill=(13, 14, 17))
    # three tall windows behind
    for i, x in enumerate((260, 830, 1400)):
        d.rectangle([x, 140, x + 260, 880], fill=(26, 33, 46), outline=(62, 68, 80), width=4)
        d.line([(x + 130, 140), (x + 130, 880)], fill=(62, 68, 80), width=4)
        for y in (330, 520, 710):
            d.line([(x, y), (x + 260, y)], fill=(62, 68, 80), width=3)
    # dais + chair
    d.polygon([(700, 880), (1220, 880), (1150, 800), (770, 800)], fill=(22, 23, 28), outline=(54, 58, 68))
    d.rectangle([850, 520, 1070, 810], fill=(15, 16, 19), outline=(70, 76, 88), width=4)
    d.polygon([(850, 520), (960, 420), (1070, 520)], fill=(15, 16, 19), outline=(70, 76, 88))
    for x in (880, 960, 1040):
        d.line([(x, 440), (x, 520)], fill=(70, 76, 88), width=3)
    # dust motes
    for _ in range(200):
        x, y = rng.randint(0, W), rng.randint(100, H)
        v = rng.randint(40, 90)
        d.point((x, y), fill=(v, v, v + 8))
    img = _fog(img, 760, 1080, peak=26, seed=21)
    img = _vignette(img, 0.96)
    img = _grain(img, 7, seed=22)
    return img


def black():
    return Image.new("RGB", (W, H), (7, 7, 9))


def get(name):
    if name not in _cache:
        _cache[name] = {"gate": gate, "courtyard": courtyard, "corridor": corridor,
                        "window": window_room, "throne": throne, "black": black}[name]()
    return _cache[name]
