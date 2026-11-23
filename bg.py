"""Scene backgrounds, drawn as flat vector art (cached)."""
import math
import random

from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
SS = 1  # backgrounds drawn at final size


def _grad(w, h, top, bottom, vertical=True):
    img = Image.new("RGB", (1, h) if vertical else (w, 1), top)
    d = ImageDraw.Draw(img)
    n = h if vertical else w
    for i in range(n):
        t = i / max(1, n - 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        if vertical:
            d.line([(0, i), (1, i)], fill=c)
        else:
            d.line([(i, 0), (i, 1)], fill=c)
    return img.resize((w, h), Image.BILINEAR)


def _vignette(img, strength=90):
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([-w * 0.30, -h * 0.35, w * 1.30, h * 1.35], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(180))
    dark = Image.new("RGB", (w, h), (6, 8, 14))
    return Image.composite(img, dark, m.point(lambda v: 255 - int((255 - v) * strength / 255)))


def _grain(img, amount=6, seed=7):
    rng = random.Random(seed)
    import numpy as np
    a = np.asarray(img).astype(np.int16)
    noise = np.array([[rng.randint(-amount, amount) for _ in range(64)] for _ in range(64)], dtype=np.int16)
    tiled = np.tile(noise, (img.height // 64 + 1, img.width // 64 + 1))[:img.height, :img.width]
    a = np.clip(a + tiled[:, :, None], 0, 255).astype("uint8")
    return Image.fromarray(a)


# ------------------------------------------------------------------ scenes
def bg_hall():
    """Palace hall: arches, warm light shafts, marble floor."""
    img = _grad(W, H, (38, 26, 40), (18, 14, 24))
    d = ImageDraw.Draw(img, "RGBA")
    # far arches
    for i in range(5):
        cx = 190 + i * 400
        d.rounded_rectangle([cx - 150, 150, cx + 150, 860], radius=150,
                            fill=(52, 36, 52, 255), outline=(74, 52, 66, 255), width=6)
        d.rounded_rectangle([cx - 118, 190, cx + 118, 860], radius=118,
                            fill=(30, 22, 34, 255))
    # light shafts
    for i, cx in enumerate((330, 960, 1590)):
        poly = [(cx - 40, 0), (cx + 80, 0), (cx + 330, 900), (cx + 40, 900)]
        d.polygon(poly, fill=(255, 206, 138, 22))
    # floor
    d.rectangle([0, 860, W, H], fill=(26, 20, 28))
    for i in range(-4, 9):
        x0 = i * 250
        d.polygon([(x0, 860), (x0 + 250, 860), (x0 + 250 + 160, H), (x0 - 160, H)],
                  outline=(44, 34, 44, 255), width=3)
    d.line([(0, 862), (W, 862)], fill=(120, 86, 60), width=6)
    # hanging lamps
    for cx in (330, 1590):
        d.line([(cx, 0), (cx, 210)], fill=(60, 46, 50), width=4)
        d.ellipse([cx - 46, 200, cx + 46, 300], fill=(255, 190, 110, 235))
        d.ellipse([cx - 22, 220, cx + 22, 272], fill=(255, 236, 190, 255))
    return _grain(_vignette(img.convert("RGB"), 70))


def bg_city():
    """Modern skyline dusk."""
    img = _grad(W, H, (36, 52, 92), (78, 60, 92))
    d = ImageDraw.Draw(img, "RGBA")
    # sun disc
    d.ellipse([1380, 240, 1740, 600], fill=(255, 176, 120, 40))
    d.ellipse([1460, 320, 1660, 520], fill=(255, 206, 150, 120))
    rng = random.Random(4)
    # far skyline
    x = -40
    while x < W + 80:
        w = rng.randint(90, 190)
        h = rng.randint(240, 560)
        top = 900 - h
        d.rectangle([x, top, x + w, 900], fill=(26, 34, 58, 255))
        for wy in range(top + 24, 890, 46):
            for wx in range(x + 16, x + w - 16, 34):
                if rng.random() < 0.5:
                    d.rectangle([wx, wy, wx + 12, wy + 18], fill=(255, 214, 140, 150))
        x += w + rng.randint(8, 26)
    # near skyline
    x = -80
    while x < W + 120:
        w = rng.randint(140, 280)
        h = rng.randint(150, 380)
        top = 980 - h
        d.rectangle([x, top, x + w, 980], fill=(16, 20, 36, 255))
        for wy in range(top + 20, 970, 40):
            for wx in range(x + 18, x + w - 18, 40):
                if rng.random() < 0.38:
                    d.rectangle([wx, wy, wx + 16, wy + 16], fill=(255, 226, 168, 120))
        x += w + rng.randint(20, 60)
    # street
    d.rectangle([0, 980, W, H], fill=(22, 22, 30))
    for i in range(0, W, 260):
        d.rectangle([i + 40, 1024, i + 190, 1036], fill=(190, 180, 150, 90))
    return _grain(_vignette(img.convert("RGB"), 80))


def bg_campus():
    """Campus courtyard, day, greenery."""
    img = _grad(W, H, (120, 176, 214), (206, 226, 214))
    d = ImageDraw.Draw(img, "RGBA")
    # distant trees
    rng = random.Random(11)
    for i in range(16):
        cx = rng.randint(-60, W + 60)
        r = rng.randint(90, 170)
        d.ellipse([cx - r, 700 - r, cx + r, 700 + r], fill=(58, 118, 92, 190))
    # building
    d.rectangle([980, 300, 1900, 780], fill=(226, 222, 210, 255))
    for row in range(3):
        for col in range(6):
            d.rectangle([1030 + col * 140, 360 + row * 130, 1100 + col * 140, 440 + row * 130],
                        fill=(120, 150, 176, 255))
    d.rectangle([960, 280, 1920, 316], fill=(204, 198, 186, 255))
    # lawn + path
    d.rectangle([0, 780, W, H], fill=(96, 158, 96))
    d.polygon([(300, 1080), (760, 1080), (980, 800), (860, 800)], fill=(214, 200, 172))
    d.rectangle([0, 780, W, 792], fill=(72, 132, 82))
    # foreground tree
    d.rectangle([70, 520, 118, 900], fill=(96, 70, 52))
    for r, ox, oy in ((190, 90, 470), (150, -30, 520), (140, 210, 540)):
        d.ellipse([ox - r, oy - r, ox + r, oy + r], fill=(46, 112, 74, 235))
    return _grain(_vignette(img.convert("RGB"), 60))


def bg_room():
    """Warm study room with bookshelf."""
    img = _grad(W, H, (72, 52, 44), (38, 28, 26)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # bookshelf
    d.rectangle([1180, 150, 1850, 900], fill=(78, 52, 38))
    rng = random.Random(3)
    for row in range(5):
        y = 190 + row * 142
        d.rectangle([1180, y + 112, 1850, y + 126], fill=(56, 36, 26))
        x = 1200
        while x < 1830:
            w = rng.randint(18, 34)
            h = rng.randint(70, 104)
            col = rng.choice([(150, 60, 54), (60, 92, 120), (176, 140, 80), (86, 110, 76), (120, 70, 96)])
            d.rectangle([x, y + 112 - h, x + w, y + 112], fill=col)
            x += w + 6
    # window with warm light
    d.rectangle([140, 170, 620, 700], fill=(255, 206, 142))
    d.rectangle([140, 170, 620, 700], outline=(64, 44, 36), width=14)
    d.line([(380, 170), (380, 700)], fill=(64, 44, 36), width=12)
    d.line([(140, 430), (620, 430)], fill=(64, 44, 36), width=12)
    # desk
    d.rectangle([0, 880, W, H], fill=(46, 32, 28))
    d.rectangle([0, 876, W, 892], fill=(122, 86, 58))
    # lamp glow (soft, drawn straight onto the wall)
    glow = Image.new("RGBA", (620, 460), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([0, 0, 619, 459], fill=(255, 200, 130, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img.alpha_composite(glow, (640, 520))
    # plant in the corner
    d.rectangle([1046, 806, 1116, 906], fill=(96, 66, 48))
    for a in range(-3, 4):
        d.ellipse([1030 + a * 34, 700 + abs(a) * 16, 1100 + a * 34, 838 + abs(a) * 16],
                  fill=(48, 104, 70))
    return _grain(_vignette(img.convert("RGB"), 95))


def bg_title():
    """Deep navy stage with a radial spotlight for the title cards."""
    img = _grad(W, H, (16, 20, 38), (8, 10, 20))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(46):
        a = i / 46 * math.tau
        r0, r1 = 300, 1500
        cx, cy = W * 0.42, H * 0.46
        d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0),
                (cx + math.cos(a) * r1, cy + math.sin(a) * r1)],
               fill=(255, 206, 140, 7), width=70)
    d.ellipse([W * 0.42 - 520, H * 0.46 - 520, W * 0.42 + 520, H * 0.46 + 520],
              fill=(255, 200, 130, 14))
    d.rectangle([0, 940, W, H], fill=(10, 12, 22))
    d.line([(0, 942), (W, 942)], fill=(150, 116, 74), width=4)
    return _grain(_vignette(img.convert("RGB"), 120))


CACHE = {}


def get(name):
    if name not in CACHE:
        CACHE[name] = {
            "hall": bg_hall, "city": bg_city, "campus": bg_campus,
            "room": bg_room, "title": bg_title,
        }[name]()
    return CACHE[name]
