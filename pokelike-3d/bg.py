"""Painted backgrounds + 2D anime FX. Everything is a pure function of (t, camera offset)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920

SKY_TOP = (10, 12, 26)
SKY_MID = (26, 22, 46)
SKY_LOW = (58, 30, 36)


def _lerp(a, b, k):
    return tuple(int(round(a[i] + (b[i] - a[i]) * k)) for i in range(3))


def sky(img, t=0.0, storm=0.0):
    """Three-stop vertical gradient; `storm` darkens and cools it."""
    d = ImageDraw.Draw(img)
    top = _lerp(SKY_TOP, (6, 7, 14), storm)
    mid = _lerp(SKY_MID, (14, 16, 30), storm)
    low = _lerp(SKY_LOW, (22, 22, 34), storm)
    for y in range(0, H, 4):
        k = y / H
        col = _lerp(top, mid, k / 0.62) if k < 0.62 else _lerp(mid, low, (k - 0.62) / 0.38)
        d.rectangle([0, y, W, y + 4], fill=col)


def stars(img, n=110, seed=7, t=0.0, fade=1.0):
    d = ImageDraw.Draw(img)
    x = seed
    for i in range(n):
        x = (x * 1103515245 + 12345) % 2147483648
        sx = (x % (W + 40)) - 20
        x = (x * 1103515245 + 12345) % 2147483648
        sy = 30 + (x % 1180)
        x = (x * 1103515245 + 12345) % 2147483648
        r = 0.9 + (x % 220) / 190.0
        tw = 0.55 + 0.45 * math.sin(t * 1.6 + i * 0.9)
        v = int(255 * min(1.0, fade) * tw)
        if v > 12:
            col = (v, v, int(v * 0.96)) if i % 7 else (v, int(v * 0.92), int(v * 0.8))
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col)


def moon(img, cx=760, cy=300, r=92, halo=1.0):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k in range(7):
        rr = r * (1.6 + k * 0.55)
        a = int(16 * halo * (1 - k / 7))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(206, 214, 240, a))
    layer = layer.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(layer)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 230, 218))
    d.ellipse([cx - r * 0.55, cy - r * 0.9, cx + r * 0.1, cy - r * 0.2], fill=(224, 221, 208))


def ridge(img, y, amp, seed=3, col=(18, 17, 24), step=90):
    """A jagged mountain band; higher y = closer."""
    d = ImageDraw.Draw(img)
    pts = [(0, H)]
    x = seed
    for px in range(-40, W + 120, step):
        x = (x * 1103515245 + 12345) % 2147483648
        h = amp * (0.45 + ((x % 1000) / 1000.0) * 0.85)
        pts.append((px, y - h))
    pts.append((W + 80, H))
    d.polygon(pts, fill=col)


def ground(img, y=1560, col=(15, 14, 18)):
    d = ImageDraw.Draw(img)
    d.rectangle([0, y, W, H], fill=col)
    d.rectangle([0, y, W, y + 6], fill=(26, 23, 26))


def vignette(img, strength=90):
    layer = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(layer)
    d.ellipse([-W * 0.35, -H * 0.2, W * 1.35, H * 1.2], fill=255)
    layer = layer.filter(ImageFilter.GaussianBlur(140))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, strength))
    dark.putalpha(layer.point(lambda v: int((255 - v) * strength / 255)))
    img.alpha_composite(dark)


# ---------------------------------------------------------------- anime FX
def speed_lines(img, t, n=26, cx=540, cy=980, inner=210, strength=1.0, seed=11):
    """Radial manga speed lines, drawn as thin wedges from the edges."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = seed
    for i in range(n):
        x = (x * 1103515245 + 12345) % 2147483648
        ang = (x % 6283) / 1000.0
        x = (x * 1103515245 + 12345) % 2147483648
        ln = 260 + (x % 520)
        w = 2 + (x % 9)
        x0 = cx + math.cos(ang) * inner
        y0 = cy + math.sin(ang) * inner
        x1 = cx + math.cos(ang) * (inner + ln * strength)
        y1 = cy + math.sin(ang) * (inner + ln * strength)
        a = int(60 + 120 * strength)
        d.line([(x0, y0), (x1, y1)], fill=(255, 252, 240, a), width=w)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1.2)))


def impact(img, t, k, cx=540, cy=980):
    """A flash + a 12-point star, `k` 0..1 intensity."""
    if k <= 0.02:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = 120 + 620 * k
    for i in range(12):
        a = i * math.pi / 6 + 0.2
        L = r * (0.55 + 0.45 * ((i * 37) % 11) / 11.0)
        d.polygon([(cx + math.cos(a - 0.07) * r * 0.18, cy + math.sin(a - 0.07) * r * 0.18),
                   (cx + math.cos(a) * L, cy + math.sin(a) * L),
                   (cx + math.cos(a + 0.07) * r * 0.18, cy + math.sin(a + 0.07) * r * 0.18)],
                  fill=(255, 236, 196, int(210 * k)))
    layer = layer.filter(ImageFilter.GaussianBlur(3))
    img.alpha_composite(layer)
    if k > 0.78:
        flash = Image.new("RGBA", (W, H), (255, 245, 225, int(86 * (k - 0.78) / 0.22)))
        img.alpha_composite(flash)


def sparks(img, t, cx, cy, n=22, spread=260, seed=5, rise=340, col=(255, 176, 96)):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = seed
    for i in range(n):
        x = (x * 1103515245 + 12345) % 2147483648
        dx = ((x % 1000) / 1000.0 - 0.5) * spread
        x = (x * 1103515245 + 12345) % 2147483648
        sp = 0.4 + (x % 500) / 500.0
        life = (t * sp * 1.4 + i * 0.31) % 1.0
        px = cx + dx * (0.4 + life * 0.9)
        py = cy - rise * life + 60 * life * life
        r = 2.6 * (1 - life) + 0.8
        a = int(220 * (1 - life))
        d.ellipse([px - r, py - r, px + r, py + r], fill=col + (a,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1.0)))


def dust(img, t, cx, cy, k, n=16, seed=9):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = seed
    for i in range(n):
        x = (x * 1103515245 + 12345) % 2147483648
        ang = (x % 628) / 100.0
        x = (x * 1103515245 + 12345) % 2147483648
        r = (60 + x % 160) * k
        px = cx + math.cos(ang) * r
        py = cy + math.sin(ang) * r * 0.35
        rr = 26 * k + 6
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(120, 108, 96, int(70 * (1 - k))))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(12)))


def wind(img, t, k=1.0, seed=4, n=14):
    """Horizontal streaks for wing beats / gales."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = seed
    for i in range(n):
        x = (x * 1103515245 + 12345) % 2147483648
        yy = 260 + (x % 1300)
        x = (x * 1103515245 + 12345) % 2147483648
        ph = (x % 1000) / 1000.0
        px = ((t * 1.9 + ph + i * 0.07) % 1.4 - 0.2) * W
        ln = 90 + (x % 220)
        a = int(90 * k)
        d.line([(px, yy), (px + ln, yy - 6)], fill=(226, 236, 255, a), width=2)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1.4)))


def letterbox_grade(img):
    """A cool shadow lift + warm highlight push, the cheapest way to look 'shot'."""
    a = np.array(img.convert("RGB"), float) / 255.0
    a[..., 2] = np.clip(a[..., 2] * 1.06 + 0.012, 0, 1)      # cool shadows
    a[..., 0] = np.clip(a[..., 0] * 1.03, 0, 1)              # warm lights
    lum = a.mean(axis=2, keepdims=True)
    a = np.clip(a * (1 - 0.10) + lum * 0.10, 0, 1)           # tiny desat
    return Image.fromarray((a * 255).astype(np.uint8), "RGB")
