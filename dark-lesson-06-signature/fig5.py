"""fig3.py — the silhouette rig for অন্ধকার পাঠ ০৩ · কেনা সম্মান.

Everything here is flat: one colour per body, no outlines, no faces. Identity comes from
*shape and gesture* — Rahim is broad with a shawl, the old man is thin and hunched, the
village is a row of smaller bodies. Arms are driven by hand-targets so a gesture (salute,
offering a glass, a jab) is a number, not a pose library.

Every function is a pure function of its arguments; time reaches them only through the
values the film passes in.
"""
import math

# ---------------------------------------------------------------- colour
PAPER = (240, 238, 230)
PAPER_D = (222, 218, 208)
PAPER_M = (208, 203, 192)
INK = (26, 23, 20)
INK_S = (92, 90, 85)
INK_D = (16, 14, 12)
GOLD = (200, 150, 62)
GOLD_D = (150, 108, 44)
GOLD_L = (232, 194, 118)
BLUE = (106, 155, 204)


# ---------------------------------------------------------------- maths
def lerp(a, b, q):
    return a + (b - a) * q


def clamp(v, a=0.0, b=1.0):
    return a if v < a else (b if v > b else v)


def ease(q):
    q = clamp(q)
    return 1 - (1 - q) ** 3


def back(q, s=1.9):
    """ease-out-back: entrance overshoot, settles."""
    q = clamp(q) - 1
    return 1 + (s + 1) * q ** 3 + s * q ** 2


def soft(q):
    """slow-in slow-out, for premium moves."""
    q = clamp(q)
    return q * q * (3 - 2 * q)


def stag(q, i, n=3, step=0.07):
    """stagger a group: element i starts later."""
    return clamp((q - i * step) / max(1e-6, 1 - (n - 1) * step))


def rot(x, y, ox, oy, a):
    c, s = math.cos(a), math.sin(a)
    dx, dy = x - ox, y - oy
    return ox + dx * c - dy * s, oy + dx * s + dy * c


def wave(t, hz=0.5, ph=0.0):
    return math.sin(2 * math.pi * (hz * t + ph))


# ---------------------------------------------------------------- pen
class P:
    """Draw in 1080x1920 design units; the canvas may be supersampled."""

    def __init__(self, img, ss=1.0):
        from PIL import ImageDraw
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.ss = ss

    def poly(self, pts, col, w=0.0):
        s = self.ss
        self.d.polygon([(x * s, y * s) for x, y in pts], fill=col,
                       outline=col if w else None,
                       width=int(max(1, w * s)) if w else 1)

    def ell(self, box, col, w=0.0):
        s = self.ss
        self.d.ellipse([box[0] * s, box[1] * s, box[2] * s, box[3] * s],
                       fill=col, outline=col if w else None,
                       width=int(max(1, w * s)) if w else 1)

    def ring(self, box, w, col):
        s = self.ss
        self.d.ellipse([box[0] * s, box[1] * s, box[2] * s, box[3] * s],
                       outline=col, width=int(max(1, w * s)))

    def line(self, pts, col, w):
        s = self.ss
        self.d.line([(x * s, y * s) for x, y in pts], fill=col,
                    width=int(max(1, w * s)), joint="curve")

    def arc(self, box, a0, a1, col, w):
        s = self.ss
        self.d.arc([box[0] * s, box[1] * s, box[2] * s, box[3] * s], a0, a1,
                   fill=col, width=int(max(1, w * s)))

    def rrect(self, box, r, col, w=0.0):
        s = self.ss
        self.d.rounded_rectangle([box[0] * s, box[1] * s, box[2] * s, box[3] * s],
                                 radius=r * s, fill=col,
                                 outline=col if w else None,
                                 width=int(max(1, w * s)) if w else 1)

    def quad(self, pts, col):
        """curved blob through 4 points (p0,p1,p2,p3), single fill."""
        self.poly(pts, col)


def arm(p, sx, sy, hx, hy, w, col, cx_body):
    """Upper arm + forearm, elbow bowed away from the body: a gesture, not a baton."""
    L = math.hypot(hx - sx, hy - sy) or 1.0
    ux, uy = (hx - sx) / L, (hy - sy) / L
    nx, ny = -uy, ux
    if nx * (0.0 if sx >= cx_body else -1.0) < 0:      # keep the bow outward
        nx, ny = -nx, -ny
    ex = (sx + hx) / 2 + nx * L * 0.20
    ey = (sy + hy) / 2 + ny * L * 0.20
    capsule(p, sx, sy, ex, ey, w, col)
    capsule(p, ex, ey, hx, hy, w * 0.90, col)


def capsule(p, x1, y1, x2, y2, w, col):
    p.line([(x1, y1), (x2, y2)], col, w)
    r = w / 2.0
    p.ell([x1 - r, y1 - r, x1 + r, y1 + r], col)
    p.ell([x2 - r, y2 - r, x2 + r, y2 + r], col)


# ---------------------------------------------------------------- people
def person(p, x, y, h, col, hand_r=None, hand_l=None, lean=0.0, hunch=0.0,
           walk=None, cap=False, beard=0.0, stick=False, sash=None, shawl=None,
           feat=1.0, crouch=0.0, sit=False, aw=0.052):
    """A flat body standing on (x, y) with total height h.

    hand_r / hand_l: (dx, dy) offset of the hand from the shoulder, in units of h.
                     dx is forward (+ = right), dy is down.
    walk: phase in radians (legs swing) or None for a standing figure.
    Returns the absolute anchor points so props can be hung on them.
    """
    hr = 0.076 * h                      # head radius
    hip = y - (0.47 - crouch * 0.16) * h
    shy = y - (0.80 - crouch * 0.14) * h + hunch * 0.05 * h
    fx = lean * 0.055 * h                # the whole upper body leans forward
    shw = 0.150 * h * feat              # shoulder half-width
    ww = 0.098 * h
    up = 0.020 * h

    # legs
    if sit:
        for s in (-1, 1):
            kx = x + 0.19 * h + s * 0.030 * h
            ky = hip + 0.06 * h
            capsule(p, x + s * ww * 0.5, hip, kx, ky, 0.086 * h, col)
            capsule(p, kx, ky, kx + 0.02 * h, y - 0.010 * h, 0.080 * h, col)
    elif walk is None:
        for s in (-1, 1):
            capsule(p, x + s * ww * 0.55, hip, x + s * 0.075 * h, y - 0.012 * h,
                    0.085 * h, col)
    else:
        for s, ph in ((-1, 0.0), (1, math.pi)):
            sw = math.sin(walk + ph)
            capsule(p, x + s * ww * 0.55, hip,
                    x + s * 0.075 * h + sw * 0.085 * h,
                    y - 0.012 * h - max(0.0, sw) * 0.03 * h, 0.082 * h, col)
    # torso: one flat shape, shoulders rounded into it
    p.poly([(x + fx - shw, shy + up), (x + fx + shw, shy + up),
            (x + ww, hip + 0.02 * h), (x - ww, hip + 0.02 * h)], col)
    p.ell([x + fx - shw, shy - 0.045 * h, x + fx + shw, shy + 0.085 * h], col)
    # neck + head
    nx = x + fx + hunch * 0.075 * h
    capsule(p, nx, shy - 0.01 * h, nx, shy - 0.075 * h, 0.055 * h, col)
    hx, hy = nx, shy - 0.075 * h - hr * 0.92
    p.ell([hx - hr, hy - hr, hx + hr, hy + hr], col)
    if beard > 0.0:
        bw = hr * 1.06
        p.poly([(hx - bw, hy + 0.05 * hr), (hx + bw, hy + 0.05 * hr),
                (hx + bw * 0.55, hy + hr * (1.0 + 1.5 * beard)),
                (hx - bw * 0.55, hy + hr * (1.0 + 1.5 * beard))], col)
        p.ell([hx - bw, hy + hr * (0.75 + 1.45 * beard), hx + bw,
               hy + hr * (1.35 + 1.75 * beard)], col)
    if cap:
        p.poly([(hx - hr * 1.02, hy - hr * 0.32), (hx + hr * 1.02, hy - hr * 0.32),
                (hx + hr * 0.92, hy - hr * 0.62), (hx - hr * 0.92, hy - hr * 0.62)], col)
        p.ell([hx - hr * 0.60, hy - hr * 1.42, hx + hr * 0.60, hy - hr * 0.55], col)

    # arms
    sxr, syr = x + fx + shw * 0.88, shy + 0.012 * h
    sxl, syl = x + fx - shw * 0.88, shy + 0.012 * h
    aw = aw * h
    if hand_r is None:
        hand_r = (0.075, 0.34)
    if hand_l is None:
        hand_l = (-0.075, 0.34)
    rx, ry = sxr + hand_r[0] * h, syr + hand_r[1] * h
    lx, ly = sxl + hand_l[0] * h, syl + hand_l[1] * h
    arm(p, sxr, syr, rx, ry, aw, col, x + fx)
    arm(p, sxl, syl, lx, ly, aw, col, x + fx)

    # the one thing that is bought: a gold band across the body
    if sash:
        ang, th = -0.34, 0.052 * h
        dx, dy = math.cos(ang), math.sin(ang)
        nx, ny = -dy, dx
        mx = x + fx
        my = (shy + hip) / 2 - 0.01 * h
        half = shw * 1.10
        p.poly([(mx - dx * half - nx * th, my - dy * half - ny * th),
                (mx + dx * half - nx * th, my + dy * half - ny * th),
                (mx + dx * half + nx * th, my + dy * half + ny * th),
                (mx - dx * half + nx * th, my - dy * half + ny * th)], sash)
    if shawl:
        ax = x + fx
        p.poly([(ax - shw * 1.16, shy + 0.16 * h), (ax + shw * 0.10, shy + 0.06 * h),
                (ax + shw * 0.04, shy - 0.03 * h), (ax - shw * 1.10, shy + 0.05 * h)], shawl)
        p.poly([(ax - shw * 1.16, shy + 0.16 * h), (ax - shw * 0.62, shy + 0.14 * h),
                (ax - shw * 0.74, shy + 0.60 * h), (ax - shw * 1.30, shy + 0.54 * h)], shawl)
    if stick:
        p.line([(lx, ly), (lx + 0.02 * h, y)], INK_S, 0.020 * h)

    return {"head": (hx, hy), "hr": hr, "hand_r": (rx, ry), "hand_l": (lx, ly),
            "shoulder": (sxr, syr), "hip": hip}


def crowd_row(p, y, h, n, col, spread=0.86, x0=None, x1=None, phase=0.0, walk=False,
              t=0.0, skip=()):
    """A row of smaller bodies standing on a line, evenly spaced."""
    x0 = 1080 * (1 - spread) / 2 if x0 is None else x0
    x1 = 1080 * (1 + spread) / 2 if x1 is None else x1
    out = []
    for i in range(n):
        if i in skip:
            continue
        q = i / max(1, n - 1)
        x = lerp(x0, x1, q)
        hh = h * (0.92 + 0.16 * ((i * 37) % 5) / 4.0)
        ph = phase + i * 0.9
        out.append(person(p, x, y, hh, col,
                          walk=(t * 3.0 + ph) if walk else None,
                          hand_r=(0.06, 0.33), hand_l=(-0.06, 0.33)))
    return out


# ---------------------------------------------------------------- props
def coin(p, x, y, r, tilt=0.0, col=GOLD, col2=GOLD_D):
    rx = max(2.0, r * (1.0 - 0.62 * abs(tilt)))
    p.ell([x - rx, y - r, x + rx, y + r], col)
    if rx > r * 0.42:
        p.ring([x - rx * 0.55, y - r * 0.55, x + rx * 0.55, y + r * 0.55], max(2.0, r * 0.16), col2)


def glass(p, x, y, h, fill=None, col=PAPER, w=0.0):
    """A tumbler standing on y, h tall, ~0.62h wide."""
    wd = h * 0.60
    p.poly([(x - wd * 0.46, y - h), (x + wd * 0.46, y - h),
            (x + wd * 0.38, y), (x - wd * 0.38, y)], col)
    if fill:
        p.poly([(x - wd * 0.43, y - h * 0.86), (x + wd * 0.43, y - h * 0.86),
                (x + wd * 0.38, y), (x - wd * 0.38, y)], fill)
    p.line([(x - wd * 0.46, y - h), (x + wd * 0.46, y - h)], col, max(2.0, h * 0.05))
    return (x, y - h * 0.7)


def medal(p, x, y, r):
    p.poly([(x - r * 0.62, y - r * 2.6), (x - r * 0.12, y - r * 2.6),
            (x + r * 0.16, y - r * 0.3), (x - r * 0.46, y - r * 0.3)], GOLD_D)
    p.poly([(x + r * 0.02, y - r * 2.6), (x + r * 0.52, y - r * 2.6),
            (x + r * 0.50, y - r * 0.3), (x + r * 0.10, y - r * 0.3)], GOLD)
    p.ell([x - r, y - r, x + r, y + r], GOLD)
    p.ring([x - r * 0.62, y - r * 0.62, x + r * 0.62, y + r * 0.62], max(2.0, r * 0.2), GOLD_D)


def mic(p, x, y, h):
    p.line([(x, y), (x, y - h)], INK, max(3.0, h * 0.018))
    p.ell([x - h * 0.035, y - h - h * 0.075, x + h * 0.035, y - h + h * 0.075], INK)
    p.poly([(x - h * 0.05, y - h * 0.02), (x + h * 0.05, y - h * 0.02),
            (x + h * 0.032, y), (x - h * 0.032, y)], INK)


def steam(p, x, y, h, col, t, n=3):
    for i in range(n):
        ph = (t * 0.55 + i * 0.33) % 1.0
        yy = y - ph * h
        a = 0.55 * (1 - ph)
        xx = x + math.sin(ph * 6.0 + i) * h * 0.10
        p.ell([xx - h * 0.05 * a - 3, yy - 3, xx + h * 0.05 * a + 3, yy + 3], col)
