"""Night interiors for অন্ধকার পাঠ — the alley, the room, and the light that gets borrowed."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920


def _rng(seed):
    x = seed

    def nxt():
        nonlocal x
        x = (x * 1103515245 + 12345) % 2147483648
        return x / 2147483648.0

    return nxt


def wall(img, y0=1500, seed=3, col=(17, 16, 21), brick=(21, 20, 26), fade=1.0):
    """A flat wall with courses of brick, sitting on a floor at y0."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, y0], fill=col)
    r = _rng(seed)
    bh = 74
    for row, by in enumerate(range(-bh, y0, bh)):
        off = (row % 2) * 62
        for bx in range(-140 + off, W + 140, 124):
            jitter = int((r() - 0.5) * 8)
            d.rectangle([bx + 4, by + 4, bx + 116, by + bh - 6 - abs(jitter)],
                        fill=(brick[0], brick[1], brick[2]))
            d.line([bx + 6, by + bh - 8, bx + 114, by + bh - 8], fill=(14, 13, 17), width=3)
    # damp patches
    for i in range(7):
        cx, cy = r() * W, y0 - 240 * r()
        rr = 90 + 180 * r()
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse([cx - rr, cy - rr * 0.6, cx + rr, cy + rr * 0.6],
                                    fill=(9, 9, 12, 70))
        img.paste(Image.alpha_composite(img.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(26))).convert("RGB"))


def floor(img, y0=1500, col=(12, 11, 15), deep=(7, 7, 9)):
    """Floor from the wall base down, darkening toward the camera."""
    arr = np.asarray(img).astype(np.float32)
    n = H - y0
    if n > 4:
        a = np.linspace(0.0, 0.86, n, dtype=np.float32)[:, None, None]
        deepc = np.array(deep, np.float32)[None, None, :]
        arr[y0:y0 + n, :, :3] = arr[y0:y0 + n, :, :3] * (1 - a) + deepc * a
    img.paste(Image.fromarray(arr.clip(0, 255).astype(np.uint8)))


def _soft(img, draw_fn, blur, k=4):
    """Draw at 1/k resolution, blur, upscale — a 60px blur costs 1/16 as much."""
    lay = Image.new("RGBA", (W // k, H // k), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay), 1.0 / k)
    lay = lay.filter(ImageFilter.GaussianBlur(blur / k)).resize((W, H), Image.BILINEAR)
    if img.mode == "RGBA":
        img.alpha_composite(lay)
    else:
        img.paste(Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB"))


def pool(img, cx, cy, r, col=(96, 150, 255), a=70, blur=60):
    """A soft pool of light on the wall/floor — the lantern's spill."""
    def draw(d, k):
        d.ellipse([(cx - r) * k, (cy - r * 0.62) * k, (cx + r) * k, (cy + r * 0.62) * k],
                  fill=col + (a,))
    _soft(img, draw, blur)


def glow(img, cx, cy, r, col=(120, 170, 255), a=120, blur=40):
    def draw(d, k):
        d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=col + (a,))
    _soft(img, draw, blur)


def window(img, x0, y0, x1, y1, shaft=0.0, col=(60, 92, 150)):
    """A barred window, and a shaft of cold light falling from it."""
    d = ImageDraw.Draw(img)
    d.rectangle([x0 - 10, y0 - 10, x1 + 10, y1 + 10], fill=(9, 9, 12))
    d.rectangle([x0, y0, x1, y1], fill=col)
    for i in range(1, 4):
        bx = x0 + (x1 - x0) * i / 4
        d.line([bx, y0, bx, y1], fill=(11, 11, 15), width=9)
    d.line([x0, (y0 + y1) / 2, x1, (y0 + y1) / 2], fill=(11, 11, 15), width=9)
    if shaft > 0.02:
        def draw(d, k):
            d.polygon([x0 * k, y0 * k, x1 * k, y0 * k, (x1 + 250 * shaft) * k, H * k,
                       (x0 - 250 * shaft) * k, H * k], fill=(120, 160, 230, int(30 * shaft)))
        _soft(img, draw, 40)


def fog(img, t, strength=0.5, seed=7):
    """Slow drifting haze — cheap depth cue in a dark room."""
    lay = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = _rng(seed)
    for i in range(14):
        cx = (r() * W / 4 + t * 6 * (0.4 + r())) % (W / 4)
        cy = (H / 4) * (0.45 + 0.5 * r())
        rr = 40 + 60 * r()
        d.ellipse([cx - rr, cy - rr * 0.5, cx + rr, cy + rr * 0.5], fill=(120, 130, 170, int(16 * strength)))
    lay = lay.filter(ImageFilter.GaussianBlur(18)).resize((W, H), Image.BILINEAR)
    if img.mode == "RGBA":
        img.alpha_composite(lay)
    else:
        img.paste(Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB"))


def coins(img, t, x=540, y=0, n=18, spread=300, seed=5, col=(232, 190, 96), speed=380):
    """Coins falling through frame."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = _rng(seed)
    for i in range(n):
        sx = x + (r() - 0.5) * spread
        ph = r()
        yy = ((ph + t * speed / H) % 1.0) * (H + 200) - 100
        spin = abs(math.sin(t * 6 + i))
        w = 12 + 10 * spin
        d.ellipse([sx - w, yy - 14, sx + w, yy + 14], fill=col + (210,))
        d.ellipse([sx - w * 0.45, yy - 6, sx + w * 0.45, yy + 6], fill=(180, 140, 60, 220))
    lay = lay.filter(ImageFilter.GaussianBlur(1.2))
    if img.mode == "RGBA":
        img.alpha_composite(lay)
    else:
        img.paste(Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB"))


def vignette(img, strength=110):
    lay = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lay)
    for i in range(9):
        k = i / 8.0
        d.ellipse([-W * 0.5 + k * 240, -H * 0.35 + k * 200,
                   W * 1.5 - k * 240, H * 1.3 - k * 200], fill=int(255 * (1 - k * 0.92)))
    mask = lay.filter(ImageFilter.GaussianBlur(90)).point(lambda v: int(v * strength / 255))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(img, black, Image.eval(mask, lambda v: 255 - v).point(lambda v: 255)) if False else img


def grade(img, lift=0.0, tint=(255, 255, 255)):
    """Final letterbox-safe grade: pull the blacks down, keep the highlights soft."""
    arr = np.asarray(img).astype(np.float32) / 255.0
    arr = np.clip((arr - 0.02) * 1.06, 0, 1)
    arr[..., 0] *= tint[0] / 255.0 * 0.98 + 0.02
    arr[..., 1] *= tint[1] / 255.0 * 0.98 + 0.02
    arr[..., 2] *= tint[2] / 255.0 * 0.98 + 0.02
    img.paste(Image.fromarray((arr * 255).clip(0, 255).astype(np.uint8)))
