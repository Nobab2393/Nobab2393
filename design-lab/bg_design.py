"""bg_design.py — a daylight field assembled in four layers at four different contrast levels.

The rule that fixes a flat background: decide the value structure first, then put each element in a
layer whose contrast sits *below* the characters'. Distance is not detail — distance is lower
contrast, cooler colour, fewer edges.

    L1 sky + sun + far range      ~8%  contrast, coolest, no interior lines
    L2 treeline + wall + hedge   ~18%
    L3 ground, path, stones      ~30%
    L4 branch + grass, blurred   ~70%  (near plane: frames the shot, never the subject)
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

INK = (26, 27, 31)

PAL = {
    "sky_top": (150, 186, 222),
    "sky_bot": (214, 227, 237),
    "haze": (244, 240, 228),
    "far": (166, 188, 206),
    "far2": (146, 168, 188),
    "mid": (146, 165, 156),
    "mid2": (128, 148, 138),
    "ground_far": (216, 207, 185),
    "ground_near": (188, 173, 145),
    "path": (228, 216, 190),
    "fg": (54, 58, 48),
}


def vgrad(size, top, bot):
    w, h = size
    ys = np.linspace(0, 1, h)[:, None]
    arr = np.array(top, float) * (1 - ys) + np.array(bot, float) * ys
    return np.repeat(arr[:, None, :], w, axis=1).astype(np.uint8)


def _glow(w, h, cx, cy, rx, ry, col, alpha, power=2.4):
    """One radial-gradient tile, resized. Stacked alpha circles band; this does not."""
    n = 256
    y, x = np.mgrid[0:n, 0:n]
    c = (n - 1) / 2.0
    d = np.sqrt(((x - c) / c) ** 2 + ((y - c) / c) ** 2)
    a = np.clip(1 - d, 0, 1) ** power
    arr = np.zeros((n, n, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = col
    arr[..., 3] = (a * alpha).astype(np.uint8)
    tile = Image.fromarray(arr, "RGBA").resize((int(rx * 2), int(ry * 2)), Image.BILINEAR)
    return tile, (int(cx - rx), int(cy - ry))


def sky(w, h, horizon):
    arr = vgrad((w, int(horizon)), PAL["sky_top"], PAL["sky_bot"])
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.paste(Image.fromarray(arr, "RGB"), (0, 0))
    # warm haze sitting on the horizon: this is what makes distance read as air
    t, pos = _glow(w, h, w * 0.5, horizon, w * 0.75, h * 0.10, PAL["haze"], 60, 2.6)
    img.alpha_composite(t, pos)
    # clouds: a few soft banks, drawn on their own layer and blurred, so no hard ellipse shows
    cl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cl, "RGBA")
    rng = np.random.default_rng(4)
    for i in range(3):
        cy = horizon * rng.uniform(0.10, 0.30)
        cx = rng.uniform(0.05, 0.85) * w
        rw = w * rng.uniform(0.26, 0.40)
        rh = rw * rng.uniform(0.09, 0.13)
        cd.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(255, 255, 255, 34))
        cd.ellipse([cx - rw * 0.5, cy - rh * 1.5, cx + rw * 0.4, cy + rh * 0.2],
                   fill=(255, 255, 255, 26))
    cl = cl.filter(ImageFilter.GaussianBlur(w * 0.02))
    img.alpha_composite(cl)
    return img


def sun(img, cx, cy, r):
    t, pos = _glow(img.width, img.height, cx, cy, r * 5.0, r * 5.0, (255, 246, 218), 120, 2.8)
    img.alpha_composite(t, pos)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 251, 238, 250))


def far_range(img, horizon, w, h):
    """L1: two ridges. Rounded tops, no interior line, dissolved by haze at the base."""
    rng = np.random.default_rng(11)
    d = ImageDraw.Draw(img, "RGBA")
    for depth, (col, alpha, amp, step) in enumerate(((PAL["far"], 165, 0.075, 0.13),
                                                    (PAL["far2"], 130, 0.045, 0.09))):
        base = horizon - h * 0.004 * depth
        pts = [(-10, base + 40)]
        x = -10
        while x < w + 40:
            x += w * step * rng.uniform(0.7, 1.3)
            pts.append((x, base - h * amp * rng.uniform(0.45, 1.0)))
        pts += [(w + 40, base + 40)]
        d.polygon(pts, fill=col + (alpha,))
    t, pos = _glow(w, h, w * 0.5, horizon, w * 0.9, h * 0.055, PAL["haze"], 95, 2.0)
    img.alpha_composite(t, pos)


def treeline(img, horizon, w, unit):
    """L2: varied crowns on uneven spacing — overlap and variety are what create depth."""
    d = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(7)
    x = -unit * 1.2
    while x < w + unit * 1.2:
        step = unit * rng.uniform(0.85, 1.7)
        cx = x + step * 0.5
        rr = unit * rng.uniform(0.30, 0.55)
        col = PAL["mid2"] if rng.random() < 0.45 else PAL["mid"]
        base = horizon + unit * 0.05
        top = horizon - unit * rng.uniform(0.35, 0.80)
        kind = rng.random()
        if kind < 0.22:                                   # conifer
            d.polygon([(cx, top - rr * 0.9), (cx + rr * 0.55, base), (cx - rr * 0.55, base)],
                      fill=col + (84,))
        else:
            d.line([(cx, base), (cx, top + rr * 0.7)], fill=col + (95,),
                   width=max(2, int(unit * 0.045)))
            n = 3 if kind < 0.7 else 2
            for k in range(n):
                ox = (k - (n - 1) / 2.0) * rr * 0.62
                oy = top + rr * (0.46 + 0.12 * abs(k - (n - 1) / 2.0))
                d.ellipse([cx + ox - rr * 0.66, oy - rr * 0.52, cx + ox + rr * 0.66, oy + rr * 0.56],
                          fill=col + (78,))
        x += step
    # a low hedge/wall: a man-made horizontal that doubles as a leading line
    d.rectangle([0, horizon - unit * 0.13, w, horizon + unit * 0.05], fill=(168, 170, 152, 66))
    d.line([(0, horizon - unit * 0.13), (w, horizon - unit * 0.13)], fill=(116, 124, 108, 90),
           width=max(2, int(unit * 0.018)))
    for i in range(6):                                  # posts: scale + a broken rhythm
        px = (i + 0.5) * w / 6 + unit * 0.4
        d.rectangle([px - unit * 0.016, horizon - unit * 0.30, px + unit * 0.016, horizon],
                    fill=(150, 146, 128, 95))


def ground(img, horizon, w, h, unit, path_x=None):
    """L3: the field, a track that converges on the subject, stone scale that follows depth."""
    g = vgrad((w, int(h - horizon)), PAL["ground_far"], PAL["ground_near"])
    img.paste(Image.fromarray(g, "RGB"), (0, int(horizon)))
    d = ImageDraw.Draw(img, "RGBA")
    path_x = path_x if path_x is not None else w * 0.36
    rng = np.random.default_rng(3)
    # the track: narrow at the horizon, gently bent, wide at the camera
    left = [(path_x - unit * 0.05, horizon), (path_x - w * 0.07, horizon + (h - horizon) * 0.45),
            (path_x - w * 0.19, h)]
    right = [(path_x + unit * 0.12, horizon), (path_x + w * 0.07, horizon + (h - horizon) * 0.45),
             (path_x + w * 0.16, h)]
    d.polygon(left + right[::-1], fill=PAL["path"] + (180,))
    # a second, fainter track branching off to the right: reads as a place, not a cone
    fork = [(path_x + w * 0.02, horizon + (h - horizon) * 0.42),
            (path_x + w * 0.30, horizon + (h - horizon) * 0.72), (path_x + w * 0.52, h)]
    d.line(fork, fill=(222, 210, 184, 120), width=int(unit * 0.14), joint="curve")
    edge = (176, 164, 136, 70)
    d.line(left, fill=edge, width=max(2, int(unit * 0.018)), joint="curve")
    d.line(right, fill=(176, 164, 136, 50), width=max(2, int(unit * 0.018)), joint="curve")
    for _ in range(90):
        px = rng.uniform(0, w)
        py = rng.uniform(horizon + 4, h)
        k = (py - horizon) / max(1.0, h - horizon)
        rr = unit * (0.004 + 0.020 * k * k)
        d.ellipse([px - rr, py - rr * 0.45, px + rr, py + rr * 0.45], fill=(146, 136, 116, 40))


def foreground(w, h, unit, blur, side="left"):
    """L4: the near plane. Highest contrast in frame that is not the character."""
    fg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(fg, "RGBA")
    c = PAL["fg"] + (205,)
    # one branch entering from the top-left corner, out of focus
    limb = [(-w * 0.06, unit * 0.46), (w * 0.08, unit * 0.24), (w * 0.26, unit * 0.06),
            (w * 0.40, -unit * 0.06)]
    d.line(limb, fill=c, width=int(unit * 0.085), joint="curve")
    for i, (bx, by) in enumerate(((w * 0.10, unit * 0.24), (w * 0.24, unit * 0.08))):
        d.line([(bx, by), (bx + unit * 0.16, by + unit * 0.30)], fill=c, width=int(unit * 0.030))
        for j in range(3):
            lx = bx + unit * (0.05 + 0.075 * j)
            ly = by + unit * (0.10 + 0.12 * j)
            w_, h_ = unit * 0.062, unit * 0.105
            leaf = Image.new("RGBA", (int(w_ * 2) + 4, int(h_ * 2) + 4), (0, 0, 0, 0))
            ImageDraw.Draw(leaf).ellipse([2, 2, w_ * 2, h_ * 2], fill=c)
            leaf = leaf.rotate(-42 + j * 30, expand=True, resample=Image.BICUBIC)
            fg.alpha_composite(leaf, (int(lx - leaf.width / 2), int(ly - leaf.height / 2)))
    rng = np.random.default_rng(21)
    for _ in range(26):
        x = rng.uniform(-w * 0.05, w * 1.05)
        base = h + rng.uniform(-unit * 0.02, unit * 0.07)
        hh = unit * rng.uniform(0.14, 0.34)
        for k in range(4):
            lean = rng.uniform(-0.45, 0.45)
            mid = (x + lean * hh * 0.35, base - hh * 0.55)
            d.line([(x, base), mid, (mid[0] + lean * hh * 0.55, base - hh * rng.uniform(0.7, 1.0))],
                   fill=PAL["fg"] + (185,), width=max(2, int(unit * 0.022)), joint="curve")
    fg = fg.filter(ImageFilter.GaussianBlur(blur))
    t, pos = _glow(w, h, w * 0.5, h * 1.10, w * 0.9, h * 0.24, PAL["fg"], 78, 1.6)
    fg.alpha_composite(t, pos)
    return fg


def contact_shadow(img, cx, cy, rx, alpha=70):
    """Without this the figure floats, however good the plate behind it is."""
    t, pos = _glow(img.width, img.height, cx, cy, rx, rx * 0.26, (70, 64, 50), alpha, 1.5)
    img.alpha_composite(t, pos)


def build(w, h, unit, horizon_frac=0.60, blur_fg=6, with_fg=True, path_x=None):
    """Painter order: sky -> far -> mid -> ground -> (character goes here) -> foreground."""
    horizon = h * horizon_frac
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    img.alpha_composite(sky(w, h, horizon))
    sun(img, w * 0.76, h * 0.115, w * 0.048)
    far_range(img, horizon, w, h)
    treeline(img, horizon, w, unit)
    ground(img, horizon, w, h, unit, path_x)
    if with_fg:
        img.alpha_composite(foreground(w, h, unit, blur_fg))
    return img
