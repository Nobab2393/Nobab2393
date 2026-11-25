"""night.py — Vice City, drawn flat: skyline, palms, neon sun, one car, one explosion."""
import math
import random

import numpy as np

from craft import (W, H, BG, CITY, CITY2, CREAM, MUTED, PINK, PINK_D, CYAN, AMBER, VIOLET,
                   clamp, seg, back, snap, expo, lerp, mix)


def sky(cv, horizon, top=BG, low=VIOLET, band=0.30):
    """Three flat bands: night, the violet haze over the water, and the water itself."""
    cv.rect([0, 0, W, horizon * (1 - band)], top)
    cv.rect([0, horizon * (1 - band), W, horizon], mix(top, low, 0.55))
    cv.rect([0, horizon - 24, W, horizon], low)
    cv.rect([0, horizon, W, H], mix(BG, VIOLET, 0.35))


def sun(cv, x, y, r, k=1.0):
    """Flat concentric discs — a neon sun, no gradient anywhere."""
    if k <= 0.02:
        return
    r = r * k
    cv.circle(x, y, r * 1.55, mix(BG, PINK_D, 0.55))
    cv.circle(x, y, r * 1.22, mix(BG, PINK, 0.55))
    cv.circle(x, y, r, AMBER)
    for i in range(5):                       # the horizontal cutouts that make it read 80s
        yy = y + r * (0.15 + 0.17 * i)
        cv.rect([x - r, yy, x + r, yy + r * 0.055 + i * 1.5], mix(AMBER, PINK, 0.25))


def building(cv, x, w, top, base, col, windows=True, seed=0, lit=0.22):
    cv.rect([x, top, x + w, base], col)
    if not windows:
        return
    rng = np.random.default_rng(seed)
    step = 26
    for yy in range(int(top) + 26, int(base) - 20, step):
        for xx in range(int(x) + 14, int(x + w) - 12, 22):
            if rng.random() < lit:
                c = mix(col, CREAM, 0.75) if rng.random() > 0.25 else mix(col, CYAN, 0.7)
                cv.rect([xx, yy, xx + 8, yy + 12], c)


def skyline(cv, base, t, k=1.0, near=False, seed=3, scale=1.0):
    """A staggered skyline that rises out of the ground, the near row one tone up."""
    rng = np.random.default_rng(seed)
    col = CITY2 if near else CITY
    x = -60
    i = 0
    while x < W + 60:
        w = float(rng.uniform(60, 130)) * scale
        h = float(rng.uniform(90, 380)) * scale * (1.25 if near else 1.0)
        delay = (i % 9) * 0.045
        kk = back(seg(delay, delay + 0.55, t)) * k
        if kk > 0.01:
            top = base - h * kk
            building(cv, x, w, top, base, col, windows=not near, seed=seed * 100 + i,
                     lit=0.18 if near else 0.26)
        x += w + float(rng.uniform(6, 26))
        i += 1


def _leaf(cv, x, y, ang, length, droop, width, col):
    """One palm frond: a spine that arcs and droops, extruded to a tapered leaf."""
    up, dn = [], []
    for j in range(9):
        k = j / 8.0
        px = x + math.cos(ang) * length * k
        py = y + math.sin(ang) * length * k + droop * k * k
        tx = math.cos(ang) * length
        ty = math.sin(ang) * length + 2 * droop * k
        n = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / n, tx / n
        w = width * max(0.0, 1 - k) ** 0.55 * (0.55 + 0.45 * k)
        up.append((px + nx * w, py + ny * w))
        dn.append((px - nx * w, py - ny * w))
    cv.poly(up + dn[::-1], col)


def palm(cv, x, ground, h, lean=0.18, col=None, k=1.0):
    """A real palm silhouette: curved tapering trunk, seven filled fronds."""
    if k <= 0.02:
        return
    col = col or CITY2
    hh = h * k
    left, right = [], []
    for i in range(13):
        u = i / 12.0
        cx = x + lean * hh * (u ** 1.7)
        cy = ground - hh * u
        w = 17 * (1 - 0.58 * u)
        left.append((cx - w, cy))
        right.append((cx + w, cy))
    cv.poly(left + right[::-1], col)
    tipx = x + lean * hh
    tipy = ground - hh
    for i in range(7):
        ang = math.radians(-172 + i * 26)
        _leaf(cv, tipx, tipy, ang, hh * 0.46, hh * 0.34, hh * 0.040, col)
    cv.circle(tipx, tipy, hh * 0.028, col)


def bay(cv, hz, sun_x, seed=7, sun_col=AMBER):
    """Foreground water at dusk: the sun's column, broken streaks, a dim far shore."""
    rnd = random.Random(seed)
    cv.rect([0, hz, W, H], mix(BG, (21, 14, 28), 0.9))
    for i in range(16):                                  # far shore, mirrored dark
        w = rnd.randint(46, 116)
        x = rnd.randint(-40, W - 20)
        cv.rect([x, hz, x + w, hz + rnd.randint(26, 88)], CITY + (120,))
    cv.rect([0, hz, W, hz + 3], mix(sun_col, CREAM, 0.25) + (110,))
    for i in range(30):                                  # the sun's column
        d = i / 29.0
        y = hz + 6 + d * (H - hz - 60)
        w = (1 - 0.5 * d) * (150 + rnd.uniform(-40, 40))
        x = sun_x + math.sin(d * 6.0 + seed) * 14 + rnd.uniform(-8, 8)
        cv.rect([x - w, y, x + w, y + 4 + 7 * (1 - d)], sun_col + (int(200 * (1 - d) ** 1.3),))
    for i in range(9):                                   # a little cyan on the right
        d = i / 8.0
        y = hz + 50 + d * 320
        w = 60 + rnd.uniform(0, 70)
        x = W * 0.76 + rnd.uniform(-46, 46)
        cv.rect([x - w, y, x + w, y + 3], CYAN + (int(80 * (1 - d)),))


def car(cv, x, ground, s=1.0, col=None, beam=True, bob=0.0):
    """A 1980s wedge, side-on, flat."""
    col = col or (18, 14, 26)
    y = ground + bob
    cv.poly([(x - 150 * s, y), (x - 128 * s, y - 52 * s), (x - 62 * s, y - 62 * s),
             (x - 20 * s, y - 92 * s), (x + 52 * s, y - 90 * s), (x + 104 * s, y - 60 * s),
             (x + 156 * s, y - 48 * s), (x + 164 * s, y)], col)
    cv.poly([(x - 24 * s, y - 86 * s), (x + 48 * s, y - 84 * s), (x + 96 * s, y - 58 * s),
             (x - 46 * s, y - 60 * s)], mix(col, CYAN, 0.22))
    cv.line([(x - 128 * s, y - 54 * s), (x - 60 * s, y - 64 * s), (x - 18 * s, y - 94 * s),
             (x + 54 * s, y - 92 * s), (x + 106 * s, y - 62 * s)], mix(CREAM, PINK, 0.25),
            4 * s)
    for wx in (x - 92 * s, x + 108 * s):
        cv.circle(wx, y + 2, 30 * s, (10, 8, 14))
        cv.circle(wx, y + 2, 13 * s, CITY2)
    if beam:
        cv.poly([(x + 160 * s, y - 40 * s), (x + 420 * s, y - 92 * s),
                 (x + 420 * s, y + 16 * s)], mix(BG, CREAM, 0.10))
        cv.circle(x + 158 * s, y - 40 * s, 9 * s, CREAM)


def rain(cv, t, n=90, seed=5, slant=0.42, col=None, alpha=70):
    rng = np.random.default_rng(seed)
    col = col or (190, 200, 230)
    for i in range(n):
        x = float(rng.uniform(0, W)) + (t * 260) % W
        y = float(rng.uniform(0, H)) + (t * 900) % H
        L = float(rng.uniform(26, 64))
        cv.line([(x % W, y % H), ((x % W) + L * slant, (y % H) + L)], col + (alpha,), 3,
                caps=False)


def burst(cv, x, y, r, k=1.0, core=AMBER, edge=PINK):
    """An explosion as a flat star: one polygon, two tones."""
    if k <= 0.02:
        return
    r *= k
    pts = []
    for i in range(18):
        a = i * math.pi * 2 / 18
        rr = r * (1.0 if i % 2 == 0 else 0.58)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.86))
    cv.poly(pts, edge)
    pts = []
    for i in range(14):
        a = i * math.pi * 2 / 14 + 0.2
        rr = r * 0.56 * (1.0 if i % 2 == 0 else 0.62)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.86))
    cv.poly(pts, core)
    cv.circle(x, y, r * 0.22, CREAM)


def figure(cv, x, ground, h, col=None, gun=False):
    """A silhouette, because faces are not what a trailer sells."""
    col = col or (8, 6, 12)
    hd = h * 0.14
    cv.circle(x, ground - h + hd, hd * 0.52, col)
    cv.poly([(x - h * 0.10, ground - h + hd * 1.1), (x + h * 0.10, ground - h + hd * 1.1),
             (x + h * 0.13, ground - h * 0.42), (x - h * 0.13, ground - h * 0.42)], col)
    cv.poly([(x - h * 0.13, ground - h * 0.42), (x - h * 0.02, ground - h * 0.42),
             (x - h * 0.04, ground), (x - h * 0.14, ground)], col)
    cv.poly([(x + h * 0.02, ground - h * 0.42), (x + h * 0.13, ground - h * 0.42),
             (x + h * 0.14, ground), (x + h * 0.04, ground)], col)
    if gun:                                  # raised arm + barrel, not a bar through the ribs
        ax, ay = x + h * 0.10, ground - h * 0.62
        hx, hy = x + h * 0.30, ground - h * 0.74
        cv.line([(ax, ay), (hx, hy)], col, w=max(3, h * 0.055))
        cv.rect([hx - h * 0.012, hy - h * 0.035, hx + h * 0.15, hy - h * 0.012], col)
