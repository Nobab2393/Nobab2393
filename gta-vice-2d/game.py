"""game.py — GRAND THEFT AUTO: VICE CITY, 2D gameplay.

A top-down (GTA-2 style) gameplay clip: one continuous scripted drive through a
neon city, a drift, a police chase, a delivery. Landscape 1920x1080 @ 30 fps.

Every frame is a pure function of t. The drive is not animated by hand: the route
is a turtle-built polyline, a curvature-driven speed profile is integrated into an
arc-length table, and the camera, HUD, traffic and police all read from it. So the
speedometer, the minimap and the skid marks agree with the car by construction.

    python3 game.py --still 12.5            one frame, for QA
    python3 game.py --seg 0 450 /tmp/a.mp4  render frames [a,b)
    python3 game.py --join /tmp/a.mp4 ...   concat + mux -> OUT
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

W, H, FPS = 1920, 1080, 30
SS = 2
DUR = 30.0
NF = int(round(DUR * FPS))

# ---- palette: Vice City at night, flat planes only --------------------------------
BG = (11, 9, 19)
WATER = (14, 27, 56)
WATER2 = (26, 44, 80)
SAND = (72, 56, 64)
ASPH = (17, 14, 26)
ASPH2 = (24, 19, 34)
WALK = (56, 47, 78)
BLOCK = (40, 33, 58)
BLDG = [(66, 53, 90), (82, 64, 108), (54, 43, 72), (74, 58, 100)]
CREAM = (244, 239, 228)
MUTED = (150, 138, 160)
PINK = (255, 61, 139)
PINK_D = (172, 32, 92)
CYAN = (69, 216, 232)
AMBER = (255, 181, 74)
VIOLET = (122, 30, 92)
GREEN = (56, 112, 88)
GREEN_D = (38, 84, 66)

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

BLOCK_P = 520            # road pitch
ROAD_H = 95              # half road width
WATER_X = 2900           # sea starts here; the strip before it is sand
ZOOM = 1.15

MIX = "audio/mix.wav"
OUT = os.environ.get("OUT", "vice-city-2d-gameplay-1920x1080.mp4")


def clamp(v, a=0.0, b=1.0):
    return a if v < a else (b if v > b else v)


def seg(a, b, t):
    return clamp((t - a) / (b - a)) if b > a else 1.0


def expo(t):
    t = clamp(t)
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)


def snap(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def lerp(a, b, k):
    return a + (b - a) * k


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def bump(t, a, b, ramp=0.35):
    """0 before a, 1 between, 0 after b, with smooth shoulders"""
    return snap(seg(a, a + ramp, t)) * (1 - snap(seg(b - ramp, b, t)))


def hash2(a, b):
    h = (a * 73856093) ^ (b * 19349663) ^ 0x9E3779B9
    h = (h ^ (h >> 13)) * 1274126177
    return (h ^ (h >> 16)) & 0xFFFFFFFF


# ------------------------------------------------------------------ the route
def build_path():
    """turtle-built route; corners land exactly on the next road's centreline"""
    pts = []
    st = {"p": [-1040.0, 1560.0], "a": 0.0, "s": 0.0}
    corners = []          # (s_start, s_end, radius, turn)
    marks = {}

    def dirv(a):
        return (math.sin(a), -math.cos(a))

    def add(x, y):
        pts.append((x, y))

    def run(dist):
        dx, dy = dirv(st["a"])
        n = max(1, int(abs(dist) / 4))
        step = dist / n
        for _ in range(n):
            st["p"][0] += dx * step
            st["p"][1] += dy * step
            add(st["p"][0], st["p"][1])

    def to(axis, target):
        d = 1.0 if dirv(st["a"])[axis] >= 0 else -1.0
        run((target - st["p"][axis]) / d)

    def corner(sign, R, tag=None):
        """sign +1 = right, -1 = left. R is the radius."""
        a0 = st["a"]
        dx, dy = dirv(a0)
        nx, ny = ((-dy, dx) if sign > 0 else (dy, -dx))
        cxp, cyp = st["p"][0] + nx * R, st["p"][1] + ny * R
        ox, oy = -nx * R, -ny * R
        s0 = len(pts) * 4
        n = max(8, int(R * 1.6 / 4))
        for i in range(1, n + 1):
            th = (math.pi / 2) * i / n * sign
            c, s_ = math.cos(th), math.sin(th)
            st["p"][0] = cxp + ox * c - oy * s_
            st["p"][1] = cyp + ox * s_ + oy * c
            st["a"] = a0 + (math.pi / 2) * i / n * sign
            add(st["p"][0], st["p"][1])
        corners.append((s0, len(pts) * 4, R, sign))
        if tag:
            marks[tag] = (s0, len(pts) * 4)

    add(*st["p"])
    to(1, 720)                       # north up the first avenue
    corner(+1, 200)                  # right, onto the cross street
    to(0, 2260)                      # long east run
    marks["drift"] = (len(pts) * 4, len(pts) * 4)
    corner(-1, 340, "drift")         # sweeping left onto the shore road
    to(1, -900)                      # north along the beach

    L = len(pts) * 4.0
    P = np.array(pts, np.float32)
    dxy = np.diff(P, axis=0)
    dist = np.hypot(dxy[:, 0], dxy[:, 1]).astype(np.float32)
    dist[dist < 1e-3] = 4.0
    th = np.arctan2(dxy[:, 0], -dxy[:, 1]).astype(np.float32)
    dth = (np.diff(th) + math.pi) % (2 * math.pi) - math.pi
    k = np.zeros(len(P), np.float32)
    k[1:len(dth) + 1] = np.abs(dth) / dist[:len(dth)]
    ker = np.ones(21, np.float32)
    ker /= ker.sum()
    k = np.convolve(k, ker, mode="same")
    head = np.zeros(len(P), np.float32)
    for i in range(1, len(P)):
        head[i] = math.atan2(P[i][0] - P[i - 1][0], -(P[i][1] - P[i - 1][1]))
    return P, k, head, L, marks


P, KAP, HEAD, LEN, MARKS = build_path()
DRIFT_A, DRIFT_B = MARKS["drift"]


def at(s):
    """position / heading / curvature at arc length s"""
    s = clamp(s, 0, LEN - 1)
    i = int(s / 4)
    i = min(i, len(P) - 2)
    f = (s - i * 4) / 4.0
    x = P[i][0] + (P[i + 1][0] - P[i][0]) * f
    y = P[i][1] + (P[i + 1][1] - P[i][1]) * f
    k = KAP[i] + (KAP[i + 1] - KAP[i]) * f
    h = HEAD[i] + (HEAD[i + 1] - HEAD[i]) * f
    return x, y, h, k


# ------------------------------------------------------------------ motion
def profile():
    """a unit speed profile: corners are limited by lateral grip, not by guesswork"""
    n = len(P)
    k = KAP.copy()
    vt = np.full(n, 1.0, np.float32)
    nz = k > 1e-5
    vt[nz] = np.minimum(1.0, np.sqrt(260.0 / k[nz]) / 470.0)
    # braking: v_i must allow slowing to v_j within (s_j - s_i)
    look = vt.copy()
    a_brake = 420.0
    for j in range(1, 120):
        shifted = np.concatenate([vt[j:], np.full(j, 1.0, np.float32)])
        allowed = np.sqrt(shifted ** 2 + 2 * a_brake * j * 4.0 / 470.0 ** 2)
        look = np.minimum(look, allowed)
    look = np.convolve(look, np.ones(5, np.float32) / 5, mode="same")
    return look


UNIT = profile()


def run_profile(mult, stop_at=None):
    v = UNIT * 470.0 * mult
    s, out, sp = 0.0, [], []
    n = len(P)
    for f in range(NF):
        i = min(int(s / 4), n - 2)
        vv = float(v[i])
        if stop_at is not None:
            vv *= clamp((stop_at - s) / 260.0, 0, 1)
        s = min(s + vv / FPS, stop_at if stop_at is not None else LEN - 8)
        out.append(s)
        sp.append(vv)
    return np.array(out), np.array(sp)


STOP_MARK = LEN - 6
ARRIVE = 26.0
_mult = 1.0
for _ in range(8):
    S, V = run_profile(_mult, STOP_MARK)
    hit = next((f / FPS for f in range(NF) if S[f] >= STOP_MARK - 1), None)
    if hit is None:
        _mult *= 1.25
        continue
    _mult *= hit / ARRIVE
    if abs(hit - ARRIVE) < 0.02:
        break
S, V = run_profile(_mult, STOP_MARK)


def t_at_s(sarc):
    return float(np.searchsorted(S, sarc)) / FPS


T_DRIFT_A = t_at_s(DRIFT_A)
T_DRIFT_B = t_at_s(DRIFT_B)
T_COPS = round(T_DRIFT_B + 0.5, 2)


def state(t):
    f = clamp(t * FPS, 0, NF - 1)
    i = int(f)
    j = min(i + 1, NF - 1)
    k = f - i
    s = S[i] + (S[j] - S[i]) * k
    v = V[i] + (V[j] - V[i]) * k
    x, y, h, kap = at(s)
    return x, y, h, kap, s, v


# ------------------------------------------------------------------ canvas
_fc = {}


def font(size, mono=False):
    key = (int(size * SS), mono)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(FONT_M if mono else FONT_B, key[0])
    return _fc[key]


class Canvas:
    def __init__(self, bg=BG):
        self.img = Image.new("RGB", (W * SS, H * SS), bg)
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self.cx = self.cy = 0.0
        self.z = 1.0

    # -- transform ------------------------------------------------------------
    def cam(self, cx, cy, z=ZOOM):
        self.cx, self.cy, self.z = cx, cy, z

    def screen(self):
        self.cx, self.cy, self.z = W / 2.0, H / 2.0, 1.0

    def _p(self, x, y):
        return ((x - self.cx) * self.z + W / 2) * SS, ((y - self.cy) * self.z + H / 2) * SS

    # -- primitives (world coordinates unless screen() is active) -------------
    def rect(self, box, fill, r=0):
        x0, y0 = self._p(box[0], box[1])
        x1, y1 = self._p(box[2], box[3])
        if x1 < 0 or y1 < 0 or x0 > W * SS or y0 > H * SS:
            return
        if r:
            self.d.rounded_rectangle([x0, y0, x1, y1], max(1, r * self.z * SS), fill=fill)
        else:
            self.d.rectangle([x0, y0, x1, y1], fill=fill)

    def poly(self, pts, fill):
        if len(pts) < 3:
            return
        self.d.polygon([self._p(x, y) for x, y in pts], fill=fill)

    def circle(self, x, y, r, fill):
        a, b = self._p(x, y)
        rr = max(0.6, r * self.z * SS)
        if a < -rr or b < -rr or a > W * SS + rr or b > H * SS + rr:
            return
        self.d.ellipse([a - rr, b - rr, a + rr, b + rr], fill=fill)

    def ring(self, x, y, r, w, fill):
        a, b = self._p(x, y)
        rr = max(0.6, r * self.z * SS)
        self.d.ellipse([a - rr, b - rr, a + rr, b + rr], outline=fill,
                       width=max(1, int(w * self.z * SS)))

    def line(self, pts, fill, w=4):
        self.d.line([self._p(x, y) for x, y in pts], fill=fill,
                    width=max(1, int(w * self.z * SS)), joint="curve")

    def arc(self, x, y, r, a0, a1, w, fill):
        a, b = self._p(x, y)
        rr = max(1.0, r * self.z * SS)
        self.d.arc([a - rr, b - rr, a + rr, b + rr], a0, a1, fill=fill,
                   width=max(1, int(w * self.z * SS)))

    # -- type (screen space, letter-spaced caps) ------------------------------
    def text(self, xy, s, size, fill, tracking=0.0, anchor="lm", mono=False, alpha=1.0):
        if alpha <= 0.02 or not s:
            return 0
        f = font(size, mono)
        track = tracking * size * SS
        ws = [f.getlength(ch) for ch in s]
        total = sum(ws) + track * (len(s) - 1)
        x, y = xy[0] * SS, xy[1] * SS
        if anchor[0] == "m":
            x -= total / 2
        elif anchor[0] == "r":
            x -= total
        if anchor[1] == "m":
            y -= size * SS * 0.36
        base = fill[:3]
        a0 = fill[3] / 255.0 if len(fill) == 4 else 1.0
        col = base + (int(255 * clamp(alpha) * a0),)
        for ch, w in zip(s, ws):
            self.d.text((x, y), ch, font=f, fill=col, anchor="lm")
            x += w + track
        return total / SS

    def glow_text(self, xy, s, size, fill, halo=PINK, tracking=0.0, k=1.0):
        if k <= 0.02:
            return
        for r, a in ((6, 0.09), (4, 0.13), (2, 0.18)):
            for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
                self.text((xy[0] + dx / SS, xy[1] + dy / SS), s, size, halo, tracking,
                          "lm", False, a * k)
        self.text(xy, s, size, fill, tracking, "lm", False, k)

    def finish(self, grain=3):
        im = self.img.resize((W, H), Image.LANCZOS)
        if grain:
            if not hasattr(self, "_g"):
                rng = np.random.default_rng(5)
                n = rng.normal(0, grain, (H // 2, W // 2)).astype(np.float32)
                g = Image.fromarray(np.clip(n + 128, 0, 255).astype(np.uint8)).resize(
                    (W, H), Image.BILINEAR)
                Canvas._g = (np.asarray(g, np.float32) - 128.0)[..., None]
            im = Image.fromarray(np.clip(np.asarray(im, np.float32) + Canvas._g,
                                         0, 255).astype(np.uint8))
        return im


# ------------------------------------------------------------------ geometry
def rot(u, v, a):
    return (u * math.sin(a) + v * math.cos(a), -u * math.cos(a) + v * math.sin(a))


def car_poly(x, y, a, L, Wd, cham=10):
    pts = []
    hl, hw, c = L / 2, Wd / 2, cham
    loc = [(hl, -hw + c), (hl - c, -hw), (-hl + c, -hw), (-hl, -hw + c),
           (-hl, hw - c), (-hl + c, hw), (hl - c, hw), (hl, hw - c)]
    for u, v in loc:
        dx, dy = rot(u, v, a)
        pts.append((x + dx, y + dy))
    return pts


def quad(x, y, a, u0, u1, v0, v1):
    out = []
    for u, v in ((u1, v0), (u1, v1), (u0, v1), (u0, v0)):
        dx, dy = rot(u, v, a)
        out.append((x + dx, y + dy))
    return out


def car(cv, x, y, a, kind="traffic", col=None, brake=False, alpha=1.0, siren=0.0):
    """top-down car; u is forward, v is the car's right"""
    shadow = (0, 0, 0, int(120 * alpha))
    dx, dy = rot(5, 8, a)
    cv.poly(car_poly(x + dx, y + dy, a, 108, 50, 11), shadow)

    if kind == "player":
        body, stripe, glass = PINK, CYAN, (26, 40, 58)
    elif kind == "police":
        body, stripe, glass = (232, 228, 240), (28, 26, 44), (30, 34, 52)
    else:
        body, stripe, glass = (col or AMBER), None, (26, 40, 58)

    body = body + (int(255 * alpha),)
    cv.poly(car_poly(x, y, a, 108, 50, 11), body)
    # windscreen + rear glass
    cv.poly(quad(x, y, a, 12, 30, -19, 19), glass + (int(230 * alpha),))
    cv.poly(quad(x, y, a, -32, -20, -17, 17), (18, 26, 40, int(200 * alpha)))
    if stripe:
        cv.poly(quad(x, y, a, -46, 46, -5, 5), stripe + (int(235 * alpha),))
    if kind == "player":
        cv.poly(quad(x, y, a, 30, 46, -16, 16), (44, 30, 48, int(255 * alpha)))
        cv.poly(quad(x, y, a, -46, -34, -16, 16), (52, 32, 48, int(255 * alpha)))
    if kind == "police":
        cv.poly(quad(x, y, a, -10, 8, -22, 22), (24, 24, 40, int(240 * alpha)))
        # light bar
        for i, cc in enumerate(((255, 54, 68), (58, 132, 255))):
            lit = siren if i == int(siren * 8) % 2 else 0.0
            base = 0.55 + 0.45 * lit
            cv.poly(quad(x, y, a, -4, 6, (-19 if i == 0 else 6), (-6 if i == 0 else 19)),
                    cc + (int(255 * base * alpha),))
        if siren > 0:
            g = (255, 54, 68) if int(siren * 8) % 2 == 0 else (58, 132, 255)
            for r, aa in ((132, 16), (94, 22), (62, 30), (36, 44)):
                cv.circle(x, y, r, g + (int(aa * siren * alpha),))
    # headlights
    for v in (-16, 16):
        dx, dy = rot(46, v, a)
        cv.circle(x + dx, y + dy, 5, (255, 246, 214, int(240 * alpha)))
    if brake:
        for v in (-16, 16):
            dx, dy = rot(-48, v, a)
            cv.circle(x + dx, y + dy, 6, (255, 72, 92, int(240 * alpha)))
    # wheels
    for u in (30, -30):
        for v in (-25, 19):
            cv.poly(quad(x, y, a, u - 9, u + 9, v, v + 6), (14, 12, 20, int(235 * alpha)))


def ped(cv, x, y, a, col, phase, alpha=1.0):
    cv.circle(x + 3, y + 4, 7, (0, 0, 0, int(90 * alpha)))
    cv.circle(x, y, 7, col + (int(255 * alpha),))
    cv.circle(x, y - 1, 4.2, (214, 176, 150, int(255 * alpha)))
    dx, dy = rot(9 * math.sin(phase), 0, a)
    cv.line([(x, y), (x + dx, y + dy)], col + (int(180 * alpha),), 3)


def palm(cv, x, y, seed, alpha=1.0):
    cv.circle(x + 12, y + 14, 20, (0, 0, 0, int(48 * alpha)))
    cv.circle(x, y, 6, (36, 30, 26, int(255 * alpha)))
    for i in range(7):
        a = seed + i * (2 * math.pi / 7)
        ln = 34 + 8 * math.sin(seed * 2 + i)
        mid = (x + math.cos(a) * ln * 0.55, y + math.sin(a) * ln * 0.55)
        tip = (x + math.cos(a) * ln, y + math.sin(a) * ln)
        perp = (-math.sin(a) * 9, math.cos(a) * 9)
        cv.poly([(x, y), (mid[0] + perp[0], mid[1] + perp[1]), tip,
                 (mid[0] - perp[0], mid[1] - perp[1])],
                (GREEN if i % 2 else GREEN_D) + (int(240 * alpha),))


# ------------------------------------------------------------------ world
def draw_world(cv, t, px, py):
    x_lo, x_hi = px - 1500, px + 1500
    y_lo, y_hi = py - 1000, py + 1000
    bx0, bx1 = int(x_lo // BLOCK_P) - 1, int(x_hi // BLOCK_P) + 1
    by0, by1 = int(y_lo // BLOCK_P) - 1, int(y_hi // BLOCK_P) + 1

    # ---- sea and sand: they take the place of every block past WATER_X
    if x_hi > WATER_X - 320:
        cv.rect([WATER_X - 210, y_lo, x_hi, y_hi], SAND + (255,))
        cv.rect([WATER_X - 210, y_lo, WATER_X - 196, y_hi], (102, 84, 92, 255))
        cv.rect([WATER_X - 34, y_lo, WATER_X - 26, y_hi], (126, 108, 116, 255))
        cv.rect([WATER_X - 22, y_lo, x_hi, y_hi], WATER + (255,))
        for i in range(14):
            yy = y_lo + ((i * 150 + t * 22) % 2100)
            cv.rect([WATER_X + 30, yy, x_hi, yy + 8], WATER2 + (190,))
            cv.rect([WATER_X + 120, yy + 96, x_hi, yy + 102], (30, 44, 74, 150))
        for i in range(7):
            palm(cv, WATER_X - 130, y_lo + 120 + i * 300, 1.3 + i * 0.7)

    # ---- streets: a band per road line
    for k in range(bx0, bx1 + 1):
        x = k * BLOCK_P
        if x > WATER_X - 60:
            continue
        cv.rect([x - ROAD_H, y_lo, x + ROAD_H, y_hi], ASPH2 + (255,))
        cv.rect([x - ROAD_H, y_lo, x - ROAD_H + 4, y_hi], ASPH + (255,))
        cv.rect([x + ROAD_H - 4, y_lo, x + ROAD_H, y_hi], ASPH + (255,))
    for k in range(by0, by1 + 1):
        y = k * BLOCK_P
        cv.rect([x_lo, y - ROAD_H, x_hi, y + ROAD_H], ASPH2 + (255,))
        cv.rect([x_lo, y - ROAD_H, x_hi, y - ROAD_H + 4], ASPH + (255,))
        cv.rect([x_lo, y + ROAD_H - 4, x_hi, y + ROAD_H], ASPH + (255,))

    # ---- lane markings
    for k in range(bx0, bx1 + 1):
        x = k * BLOCK_P
        if x > WATER_X - 60:
            continue
        for j in range(by0, by1 + 1):
            y = j * BLOCK_P
            for yy in (y - ROAD_H - 8, y + ROAD_H + 2):
                for i in range(5):
                    cv.rect([x - 46 + i * 20, yy, x - 38 + i * 20, yy + 6], (152, 140, 172, 170))
                    cv.rect([x + 38 - i * 20, yy, x + 46 - i * 20, yy + 6], (152, 140, 172, 170))
            cv.rect([x - 3, y - ROAD_H + 16, x + 3, y - 24], (120, 108, 140, 200))
            cv.rect([x - 3, y + 24, x + 3, y + ROAD_H - 16], (120, 108, 140, 200))
    for k in range(by0, by1 + 1):
        y = k * BLOCK_P
        for j in range(bx0, bx1 + 1):
            x = j * BLOCK_P
            if x > WATER_X - 60:
                continue
            cv.rect([x - ROAD_H + 16, y - 3, x - 24, y + 3], (120, 108, 140, 200))
            cv.rect([x + 24, y - 3, x + ROAD_H - 16, y + 3], (120, 108, 140, 200))

    # ---- blocks
    for by in range(by0, by1 + 1):
        for bx in range(bx0, bx1 + 1):
            x0 = bx * BLOCK_P + ROAD_H + 20
            y0 = by * BLOCK_P + ROAD_H + 20
            x1 = (bx + 1) * BLOCK_P - ROAD_H - 20
            y1 = (by + 1) * BLOCK_P - ROAD_H - 20
            if x1 > WATER_X - 20:
                continue
            cv.rect([x0 - 20, y0 - 20, x1 + 20, y1 + 20], WALK + (255,))
            cv.rect([x0 - 20, y0 - 20, x1 + 20, y1 + 20], None) if False else None
            cv.rect([x0, y0, x1, y1], BLOCK + (255,))
            h = hash2(bx, by)
            k = h % 4
            w, hgt = x1 - x0, y1 - y0
            # one billboard on some blocks
            if (h >> 7) % 3 == 0:
                bw, bh2 = 132, 62
                bxx = x0 + (14 if (h >> 9) % 2 else w - bw - 14)
                byy = y0 + (14 if (h >> 11) % 2 else hgt - bh2 - 14)
                col = PINK if (h >> 13) % 2 else CYAN
                cv.rect([bxx - 14, byy - 14, bxx + bw + 14, byy + bh2 + 14], col + (16,))
                cv.rect([bxx, byy, bxx + bw, byy + bh2], (20, 16, 32, 255))
                for j, v in enumerate((0.95, 0.55, 0.3)):
                    cv.rect([bxx + 12, byy + 12 + j * 16, bxx + 12 + (bw - 24) * v,
                             byy + 22 + j * 16], (col if j == 0 else CREAM) + (210,))
            if k == 0:
                cv.rect([x0 + 22, y0 + 22, x1 - 22, y1 - 22], BLDG[0] + (255,))
                cv.rect([x0 + 22, y0 + 22, x1 - 22, y0 + 44], BLDG[2] + (255,))
                cv.rect([x0 + 22, y1 - 44, x1 - 22, y1 - 22], BLDG[2] + (255,))
                cv.rect([x0 + 46, y0 + 66, x0 + 120, y0 + 128], BLDG[1] + (255,))
                cv.rect([x1 - 130, y1 - 118, x1 - 56, y1 - 58], BLDG[1] + (255,))
                for i in range(4):
                    for j in range(3):
                        wx = x0 + 40 + i * 34
                        wy = y0 + 60 + j * 46
                        cv.rect([wx, wy, wx + 16, wy + 26], (206, 196, 224, 26))
                neon(cv, [(x0 + 22, y1 - 12), (x1 - 22, y1 - 12)], h)
            elif k == 1:
                cv.rect([x0 + 18, y0 + 18, x0 + w * 0.54, y1 - 18], BLDG[1] + (255,))
                cv.rect([x0 + 18, y0 + 18, x0 + w * 0.54, y0 + 40], BLDG[2] + (255,))
                cv.rect([x0 + w * 0.58, y0 + 18, x1 - 18, y0 + hgt * 0.48], BLDG[3] + (255,))
                cv.rect([x0 + w * 0.58, y0 + hgt * 0.52, x1 - 18, y1 - 18], (34, 28, 48, 255))
                for i in range(2):
                    cv.rect([x0 + w * 0.62 + i * 66, y0 + hgt * 0.56,
                             x0 + w * 0.62 + i * 66 + 50, y0 + hgt * 0.56 + 76],
                            (52, 44, 68, 255))
                neon(cv, [(x0 + 18, y0 + 18), (x0 + w * 0.54, y0 + 18)], h)
            elif k == 2:
                cv.rect([x0 + 28, y0 + 28, x1 - 28, y1 - 28], (44, 36, 62, 255))
                cv.rect([x0 + 76, y0 + 86, x1 - 76, y1 - 86], (28, 62, 76, 255))
                cv.rect([x0 + 88, y0 + 98, x1 - 88, y1 - 98], CYAN + (34,))
                cv.circle((x0 + x1) / 2, (y0 + y1) / 2, 150, CYAN + (10,))
                cv.rect([x0 + 88, y0 + 98, x1 - 88, y1 - 98], None) if False else None
                for i in range(3):
                    palm(cv, x0 + 50 + i * (w - 100) / 2, y0 + 46, h * 0.001 + i)
                palm(cv, x0 + 50, y1 - 50, h * 0.002)
                palm(cv, x1 - 50, y1 - 50, h * 0.003)
            else:
                for i in range(3):
                    ww = w / 3
                    cv.rect([x0 + i * ww + 8, y0 + 26, x0 + (i + 1) * ww - 8, y1 - 58],
                            BLDG[(h + i) % 4] + (255,))
                    neon(cv, [(x0 + i * ww + 16, y1 - 52), (x0 + (i + 1) * ww - 16, y1 - 52)],
                         h + i * 7)
                cv.rect([x0, y1 - 42, x1, y1 - 16], WALK + (255,))

    # ---- street lights
    for bx in range(bx0, bx1 + 1):
        for by in range(by0, by1 + 1):
            if (bx + by) % 2 and bx * BLOCK_P < WATER_X - 60:
                x = bx * BLOCK_P + ROAD_H + 22
                y = by * BLOCK_P + ROAD_H + 22
                cv.circle(x, y, 78, (255, 181, 74, 14))
                cv.circle(x, y, 38, (255, 181, 74, 20))
                cv.circle(x, y, 6, (255, 236, 196, 235))


def neon(cv, span, h):
    col = PINK if (h >> 3) % 3 else CYAN
    cv.rect([span[0][0], span[0][1] - 26, span[1][0], span[1][1] + 26], col + (12,))
    cv.rect([span[0][0], span[0][1] - 14, span[1][0], span[1][1] + 14], col + (24,))
    cv.rect([span[0][0], span[0][1] - 6, span[1][0], span[1][1] + 6], col + (60,))
    cv.rect([span[0][0], span[0][1] - 3, span[1][0], span[1][1] + 3], col + (235,))
    if (h >> 5) % 2:
        for i in range(3):
            cx = span[0][0] + 30 + i * (span[1][0] - span[0][0] - 60) / 2
            cv.circle(cx, span[0][1], 4, (255, 255, 255, 120))


# ------------------------------------------------------------------ traffic
TRAFFIC = [
    # (axis, road line, lane offset, speed, phase, colour)  axis 1 = east-west road
    (1, 520, +48, 235, 0.00, (58, 92, 150)),
    (1, 520, +48, 235, 0.55, (196, 92, 70)),
    (1, 520, -48, -245, 0.30, (150, 140, 170)),
    (1, 520, -48, -245, 0.80, (86, 150, 140)),
    (1, 0, +48, 230, 0.15, (120, 110, 150)),
    (1, 0, -48, -235, 0.62, (196, 150, 80)),
    (0, 2600, +48, 210, 0.10, (140, 92, 160)),
    (0, 2600, -48, -215, 0.70, (200, 150, 70)),
    (1, 520, +48, 250, 0.24, (86, 170, 190)),
    (1, 520, -48, -225, 0.06, (206, 120, 150)),
    (1, 0, +48, 240, 0.34, (150, 120, 190)),
    (1, 0, -48, -240, 0.90, (196, 196, 210)),
    (0, 2600, +48, 226, 0.36, (86, 120, 180)),
    (0, 2600, -48, -206, 0.14, (210, 130, 90)),
]

PEDS = [
    # (axis, road line, side offset, walk dir, phase, colour)
    (1, 520, +132, +1, 0.00, (196, 88, 120)),
    (1, 520, +132, +1, 0.40, (90, 150, 190)),
    (1, 520, -132, -1, 0.65, (200, 170, 90)),
    (1, 520, -132, -1, 0.18, (140, 200, 180)),
    (0, 2600, +132, +1, 0.25, (150, 120, 200)),
    (0, 2600, -132, -1, 0.55, (210, 120, 90)),
    (1, 0, +132, +1, 0.85, (120, 190, 150)),
    (1, 0, -132, -1, 0.35, (200, 140, 190)),
    (0, 2600, +132, +1, 0.72, (196, 150, 90)),
    (0, 2600, -132, -1, 0.08, (110, 150, 210)),
    (1, 520, +132, +1, 0.55, (170, 110, 180)),
    (1, 520, -132, -1, 0.28, (120, 200, 190)),
]

SPAN_X, OFF_X = 4000.0, -1300.0      # east-west wrap window
SPAN_Y, OFF_Y = 3000.0, -1250.0      # north-south wrap window


PATH_TRAFFIC = [
    # (start arc length, speed along the route, lane offset, colour)
    (620, 176, -50, (86, 120, 190)),
    (1500, 208, +50, (200, 96, 96)),
    (2400, 196, -50, (170, 150, 200)),
    (3300, 186, +50, (96, 176, 160)),
    (4200, 214, -50, (210, 150, 80)),
    (5100, 190, +50, (150, 130, 190)),
    (5800, 200, -50, (196, 190, 210)),
]


def path_traffic(t):
    out = []
    span = LEN - 120
    for (s0, v, lane, col) in PATH_TRAFFIC:
        s = (s0 + v * t) % span
        x, y, h, k = at(s)
        ox, oy = rot(0, lane, h)
        out.append((x + ox, y + oy, h, col))
    return out


def traffic_state(t, px=0.0, py=0.0):
    out = []
    for (axis, line, lane, spd, ph, col) in TRAFFIC:
        if axis == 1:
            x = ((ph * SPAN_X + spd * t) % SPAN_X) + OFF_X
            y = line + lane
            a = math.pi / 2 if spd > 0 else -math.pi / 2
        else:
            x = line + lane
            y = ((ph * SPAN_Y + spd * t) % SPAN_Y) + OFF_Y
            a = 0.0 if spd > 0 else math.pi
        out.append((x, y, a, col))
    out.extend(path_traffic(t))
    return out


def ped_state(t):
    out = []
    for (axis, line, off, dr, ph, col) in PEDS:
        if axis == 1:
            x = ((ph * SPAN_X + dr * 46 * t) % SPAN_X) + OFF_X
            y = line + off
            a = math.pi / 2 if dr > 0 else -math.pi / 2
        else:
            x = line + off
            y = ((ph * SPAN_Y + dr * 46 * t) % SPAN_Y) + OFF_Y
            a = 0.0 if dr > 0 else math.pi
        out.append((x, y, a, col, t * 6 + ph * 9))
    return out


# ------------------------------------------------------------------ HUD
def stars(cv, n, t, alpha=1.0):
    for i in range(5):
        x = W - 62 - i * 46
        y = 64
        filled = i < n
        if not filled:
            cv.ring(x, y, 17, 2, (92, 80, 104, int(200 * alpha)))
            continue
        blink = 1.0 if n < 3 else (0.55 + 0.45 * (math.sin(t * 9 + i) > -0.2))
        col = AMBER if i < n else (92, 80, 104)
        star_poly = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rr = 18 if k % 2 == 0 else 8
            star_poly.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
        cv.poly(star_poly, col + (int(255 * blink * alpha),))


def hud(cv, t, st, money, wanted, kmh, t_left, msg, msg_a=1.0):
    px, py, h, kap, s, v = st
    cv.screen()

    # ---- top left: cash + bars
    cv.rect([36, 34, 396, 152], (9, 8, 16, 205), 10)
    cv.text((58, 62), "CASH", 20, MUTED, 0.16)
    cv.text((58, 104), "$" + "{:,}".format(int(money)), 46, CREAM, 0.02, mono=True)
    cv.rect([36 + 244, 52, 36 + 244 + 112, 70], (30, 24, 42, 210), 4)
    cv.rect([36 + 246, 54, 36 + 246 + int(108 * 1.0), 68], PINK + (235,), 3)
    cv.rect([36 + 244, 78, 36 + 244 + 112, 96], (30, 24, 42, 210), 4)
    cv.rect([36 + 246, 80, 36 + 246 + int(108 * 0.62), 94], CYAN + (235,), 3)
    cv.text((36 + 244, 108), "HEALTH · ARMOUR", 15, MUTED, 0.18)

    # ---- top right: wanted
    stars(cv, wanted, t * 1.4)

    # ---- top centre: mission
    if msg_a > 0.01:
        wpx = 780
        cv.rect([W / 2 - wpx / 2, 30, W / 2 + wpx / 2, 116], (9, 8, 16, int(210 * msg_a)), 10)
        cv.rect([W / 2 - wpx / 2, 30, W / 2 - wpx / 2 + 5, 116], PINK + (int(230 * msg_a),), 2)
        cv.text((W / 2 - wpx / 2 + 26, 58), "MISSION", 18, AMBER, 0.2, alpha=msg_a)
        cv.text((W / 2 - wpx / 2 + 26, 88), msg, 25, CREAM, 0.03, alpha=msg_a)
        mm, ss_ = divmod(max(0, int(t_left)), 60)
        cv.text((W / 2 + wpx / 2 - 24, 74), "%d:%02d" % (mm, ss_), 34, CREAM, 0.02,
                anchor="rm", mono=True, alpha=msg_a)

    # ---- bottom left: speedo
    cx, cy = 190, 924
    cv.circle(cx, cy, 96, (9, 8, 16, 140))
    cv.arc(cx, cy, 74, 140, 400, 8, (48, 40, 60, 230))
    frac = clamp(kmh / 200.0)
    cv.arc(cx, cy, 74, 140, 140 + 260 * frac, 8,
           (PINK if frac < 0.8 else (255, 110, 120)) + (240,))
    ang = math.radians(140 + 260 * frac)
    cv.line([(cx, cy), (cx + math.cos(ang) * 62, cy + math.sin(ang) * 62)], CREAM + (240,), 3)
    cv.circle(cx, cy, 7, CREAM + (255,))
    cv.text((cx, cy + 34), "%d" % int(kmh), 40, CREAM, 0.02, anchor="mm", mono=True)
    cv.text((cx, cy + 64), "KM/H", 16, MUTED, 0.24, anchor="mm")

    # ---- bottom right: minimap
    mx, my, mr = W - 168, 918, 118
    cv.circle(mx, my, mr + 8, (9, 8, 16, 155))
    clip_roads(cv, mx, my, mr, px, py, wanted, h, s)
    cv.ring(mx, my, mr, 3, (216, 208, 226, 210))
    cv.circle(mx, my, 6, CREAM + (240,))

    # ---- footer
    cv.text((W / 2, H - 26), "FAN-MADE 2D HOMAGE · EVERY FRAME DRAWN IN CODE", 15,
            (120, 110, 132, 190), 0.22, anchor="mm")


def clip_circle(mx, my, mr, x0, y0, x1, y1):
    """segment clipped to the minimap disc"""
    dx, dy = x1 - x0, y1 - y0
    fx, fy = x0 - mx, y0 - my
    a = dx * dx + dy * dy
    if a < 1e-6:
        return None
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - mr * mr
    disc = b * b - 4 * a * c
    if disc <= 0:
        return None
    r = math.sqrt(disc)
    t0, t1 = (-b - r) / (2 * a), (-b + r) / (2 * a)
    t0, t1 = max(t0, 0.0), min(t1, 1.0)
    if t1 <= t0:
        return None
    return ((x0 + dx * t0, y0 + dy * t0), (x0 + dx * t1, y0 + dy * t1))


def clip_roads(cv, mx, my, mr, px, py, wanted, h, s_now):
    mz = 0.085
    # sea first, as rows clipped to the disc
    sx = mx + (WATER_X - px) * mz
    if sx < mx + mr:
        for j in range(26):
            y = my - mr + j * (2 * mr / 26.0)
            got = clip_circle(mx, my, mr, sx, y, mx + mr * 2, y)
            if got:
                x0 = max(got[0][0], sx)
                if got[1][0] > x0:
                    cv.rect([x0, y, got[1][0], y + 2 * mr / 26.0 + 1], (24, 40, 72, 210))
    for k in range(-16, 17):
        wx = k * BLOCK_P
        if wx <= WATER_X:
            sxk = mx + (wx - px) * mz
            got = clip_circle(mx, my, mr, sxk, my - mr * 2, sxk, my + mr * 2)
            if got:
                cv.line([got[0], got[1]], (124, 114, 148, 235), 3)
        wy = k * BLOCK_P
        sy = my + (wy - py) * mz
        got = clip_circle(mx, my, mr, mx - mr * 2, sy, mx + mr * 2, sy)
        if got:
            cv.line([got[0], got[1]], (124, 114, 148, 235), 3)
    for (x, y, a, col) in traffic_state(cv_t):
        ddx, ddy = (x - px) * mz, (y - py) * mz
        if ddx * ddx + ddy * ddy < (mr - 8) ** 2:
            cv.circle(mx + ddx, my + ddy, 3.4, (196, 186, 210, 210))
    if wanted:
        for k in range(2):
            x2, y2, h2, k2 = at(max(0.0, s_now - 210 - k * 182))
            ddx, ddy = (x2 - px) * mz, (y2 - py) * mz
            if ddx * ddx + ddy * ddy < (mr - 8) ** 2:
                cv.circle(mx + ddx, my + ddy, 4.4,
                          ((255, 54, 68) if k == 0 else (58, 132, 255)) + (240,))
    mxp = mx + (2600 - px) * mz
    myp = my + (-900 - py) * mz
    ddx, ddy = mxp - mx, myp - my
    if ddx * ddx + ddy * ddy < (mr - 10) ** 2:
        cv.ring(mxp, myp, 7, 2, CYAN + (240,))
        cv.circle(mxp, myp, 2.5, CYAN + (240,))
    # the player, a pink arrow at the centre
    cv.poly([(mx + math.cos(h) * 13, my + math.sin(h) * 13),
             (mx + math.cos(h + 2.5) * 9, my + math.sin(h + 2.5) * 9),
             (mx + math.cos(h - 2.5) * 9, my + math.sin(h - 2.5) * 9)], PINK + (255,))


cv_t = 0.0
cv_s = 0.0


# ------------------------------------------------------------------ frame
def draw(t):
    global cv_t, cv_s
    cv_t, cv_s = t, 0.0
    st = state(t)
    px, py, h, kap, s, v = st
    cv_s = s

    # camera: look ahead a little, eased
    ax, ay = px + math.sin(h) * 90, py - math.cos(h) * 90
    cv = Canvas(BG)
    cv.cam(ax, ay, ZOOM)

    draw_world(cv, t, px, py)

    # skid marks laid down during the drift
    if t > DRIFT_A / 470.0 - 4:
        draw_skids(cv, t)

    # traffic + peds
    for (x, y, a, col) in traffic_state(t, px, py):
        if abs(x - px) < 1300 and abs(y - py) < 900:
            car(cv, x, y, a, "traffic", col)
    for (x, y, a, col, ph) in ped_state(t):
        if abs(x - px) < 1300 and abs(y - py) < 900:
            ped(cv, x, y, a, col, ph)

    # mission marker
    mk = bump(t, 0.5, DUR)
    if mk > 0.02:
        ring_pulse(cv, 2600, -900, t, mk)

    # police
    wanted = wanted_level(t)
    if wanted > 0:
        for k, (lag, off) in enumerate(((210, 54), (392, -54))):
            s2 = max(0.0, s - lag)
            x2, y2, h2, k2 = at(s2)
            ox, oy = rot(0, off, h2)
            a_fade = snap(seg(T_COPS + k * 0.35, T_COPS + 1.2 + k * 0.35, t))
            if a_fade > 0.02:
                car(cv, x2 + ox, y2 + oy, h2, "police", alpha=a_fade,
                    siren=(1.0 if wanted >= 1 else 0.0) * a_fade)

    # the player
    brake = v < 90 or (t > ARRIVE - 0.6)
    slip = clamp(v * v * kap / 1400.0, 0, 0.26)
    slip += 0.16 * bump(t, T_DRIFT_A, T_DRIFT_B + 0.3, 0.45)
    car(cv, px, py, h + slip, "player", brake=brake)

    # headlight wash in front of the car
    for vv in (-16, 16):
        bx0, by0 = rot(44, vv, h)
        fx1, fy1 = rot(240, vv * 2.4 - 30, h)
        fx2, fy2 = rot(240, vv * 2.4 + 30, h)
        cv.poly([(px + bx0, py + by0), (px + fx1, py + fy1), (px + fx2, py + fy2)],
                (255, 240, 200, 9))

    # ---- HUD
    money = 12480 + int(4200 * snap(seg(25.6, 28.2, t)))
    kmh = v * 0.40
    t_left = 180 - t
    msg = "OCEAN DRIVE · DELIVER THE PACKAGE"
    msg_a = 1.0
    if t < 1.6:
        msg_a = snap(seg(0.5, 1.3, t))
    if t > 25.4:
        msg = "PACKAGE DELIVERED"
        msg_a = 1.0
    hud(cv, t, st, money, wanted, kmh, t_left, msg, msg_a)

    # mission passed banner
    if t > 26.4:
        k = snap(seg(26.4, 27.0, t))
        cv.screen()
        cv.rect([0, 402, W, 640], (9, 8, 16, int(150 * k)))
        cv.glow_text((W / 2, 462), "MISSION PASSED!", 76, CREAM, CYAN, 0.10, k)
        cv.text((W / 2 - 96, 546), "+ $4,200", 54, PINK, 0.06, mono=True, alpha=k)
        cv.text((W / 2 - 96, 604), "COPS LOST · RESPECT +", 24, MUTED, 0.2, alpha=k)

    # busted flash when the stars light up
    if T_COPS < t < T_COPS + 0.9:
        k = 1 - snap(seg(T_COPS, T_COPS + 0.9, t))
        cv.screen()
        cv.rect([0, 0, W, H], (255, 54, 68, int(46 * k)))

    # intro title
    if t < 1.9:
        k = snap(seg(0.15, 0.8, t)) * (1 - snap(seg(1.35, 1.9, t)))
        cv.screen()
        cv.rect([0, 0, W, H], (8, 7, 14, int(120 * k)))
        cv.glow_text((W / 2, H / 2 - 40), "VICE CITY", 108, CREAM, PINK, 0.14, k)
        cv.text((W / 2, H / 2 + 44), "2D", 64, PINK, 0.30, alpha=k)
        cv.text((W / 2, H / 2 + 116), "TOP-DOWN GAMEPLAY", 24, MUTED, 0.32, alpha=k)

    out = cv.finish()
    out = crt(out)
    if t > DUR - 0.6:
        f = int(255 * snap(seg(DUR - 0.6, DUR, t)))
        out = Image.blend(out, Image.new("RGB", out.size, (0, 0, 0)), f / 255.0)
    return out


def wanted_level(t):
    if t < T_COPS:
        return 0
    if t < 24.4:
        return 3
    if t < 25.2:
        return 2
    if t < 25.9:
        return 1
    return 0


def ring_pulse(cv, x, y, t, k):
    for i in range(3):
        ph = (t * 0.8 + i / 3.0) % 1.0
        cv.ring(x, y, 34 + ph * 46, 5 * (1 - ph) + 1, CYAN + (int(120 * (1 - ph) * k),))
    cv.circle(x, y, 16, CYAN + (int(70 * k),))
    cv.ring(x, y, 22, 3, CYAN + (int(220 * k),))
    cv.poly([(x, y - 26), (x + 14, y - 6), (x - 14, y - 6)], CYAN + (int(220 * k),))


SK = None


def draw_skids(cv, t):
    global SK
    if SK is None:
        SK = []
        for f in range(NF):
            tt = f / FPS
            s0 = S[min(f, len(S) - 1)]
            if DRIFT_A - 120 < s0 < DRIFT_B + 160:
                x, y, h, kap = at(s0)
                sl = 0.26 * bump(tt, 14.6, 16.4, 0.5) + 0.12
                for v_off in (-20, 20):
                    ox, oy = rot(-34, v_off, h + sl)
                    SK.append((x + ox, y + oy, f))
    cur = t * FPS
    for (x, y, f) in SK:
        if 0 <= cur - f < FPS * 8:
            a = int(155 * (1 - (cur - f) / (FPS * 8)))
            cv.circle(x, y, 6, (54, 46, 66, int(a * 0.8)))


def crt(im):
    a = np.asarray(im, np.float32)
    a[::4] *= 0.86
    h, w = a.shape[:2]
    yy = np.linspace(-1, 1, h)[:, None]
    xx = np.linspace(-1, 1, w)[None, :]
    r = np.sqrt(xx * xx * 0.7 + yy * yy)
    vig = (1 - 0.30 * np.clip(r - 0.35, 0, 1) ** 1.5)[..., None]
    a *= vig
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def main():
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1])
        os.makedirs("frames", exist_ok=True)
        draw(t).save("frames/still-%06.2f.png" % t)
        print("still", t)
        return
    if "--seg" in sys.argv:
        j = sys.argv.index("--seg")
        a, b, sp = int(sys.argv[j + 1]), int(sys.argv[j + 2]), sys.argv[j + 3]
        import imageio_ffmpeg
        cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
               "-crf", "19", "-pix_fmt", "yuv420p", sp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(a, b):
            p.stdin.write(draw(i / FPS).tobytes())
            if (i - a) % 120 == 0:
                print("  seg %d/%d" % (i - a, b - a), flush=True)
        p.stdin.close()
        p.wait()
        print("segdone", sp, os.path.getsize(sp), flush=True)
        return
    if "--join" in sys.argv:
        import imageio_ffmpeg
        segs = sys.argv[sys.argv.index("--join") + 1:]
        with open("segs.txt", "w") as fh:
            for s in segs:
                fh.write("file '%s'\n" % os.path.abspath(s))
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", "segs.txt", "-i", MIX,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", OUT], check=True)
        print("joined", os.path.getsize(OUT))
        return


if __name__ == "__main__":
    main()
