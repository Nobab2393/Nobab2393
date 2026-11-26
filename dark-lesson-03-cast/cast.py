"""dark-lesson-03-cast — the illustrated cut of কেনা সম্মান.

The five designs in ../characters-bd are used as cut-out puppets: each PNG is keyed off its
cream ground, then staged on a drawn set with a small vocabulary of puppet motion
(bob / sway / slide / walk / tilt / dim). Timing is probed from the voice takes, never
hardcoded, so re-recording a line re-times the whole thing.

	NAR    = start of each spoken line
	BOUNDS = the eleven cuts, 0.30 s before the line they belong to

Usage:
	python3 cast.py --mix                      build audio/mix.wav from audio/v1..v10.mp3
	python3 cast.py --still 12.5               one frame, for QA
	python3 cast.py --seg 0 900 /tmp/a.mp4     render frames [a,b)
	python3 cast.py --join /tmp/a.mp4 ...      concat + mux -> OUT
"""
import math
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

import deva  # noqa: E402  (needs cwd for its font path; overridden right after)
deva.FONT = os.path.join(HERE, "fonts", "NotoSansBengali.ttf")

W, H, FPS = 1080, 1920, 30
GROUND = (240, 238, 230)
CARD = (250, 249, 245)
INK = (25, 25, 25)
META = (122, 118, 110)
ACCENT = (217, 119, 87)
COOL = (138, 162, 178)
WATER = (196, 208, 214)
SHADE = (228, 225, 215)

TAU = math.pi * 2
SAFE = 64
GY = 1340                      # the line everybody stands on

TAKES = ["audio/v%d.mp3" % i for i in range(1, 11)]
GAP, START, TAIL = 0.55, 1.6, 9.0
MIX = "audio/mix.wav"
OUT = os.environ.get("OUT", "dark-lesson-03-cast-1080x1920.mp4")


# ---------------------------------------------------------------- numbers

def bn(n):
    return str(n).translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))


# ---------------------------------------------------------------- easing

def f(a, b, t):
    if b <= a:
        return 1.0 if t >= b else 0.0
    return min(1.0, max(0.0, (t - a) / (b - a)))


def expo(k):
    return 0.0 if k <= 0 else (1.0 if k >= 1 else 1 - 2 ** (-9 * k))


def snap(k):
    return k * k * (3 - 2 * k)


def bob(t, seed, amp=1.0):
    return math.sin(TAU * (0.42 * t + seed)) * amp


def sway(t, seed):
    """±1 slow drift — the thing that stops a cut-out reading as a photocopy."""
    return math.sin(TAU * (0.19 * t + seed))


def lifelike(t, seed, amp=1.0):
    """(dy, degrees) shared by every puppet: a breath and a lean."""
    return (-2.6 * amp * (0.5 + 0.5 * bob(t, seed)), 1.15 * amp * sway(t * 1.7, seed + 0.31))


# ---------------------------------------------------------------- sprites

SPRITES = {
    "patron": "../characters-bd/c1-patron.png",
    "boy": "../characters-bd/c2-boy.png",
    "elder": "../characters-bd/c3-elder.png",
    "rickshaw": "../characters-bd/c4-rickshaw.png",
    "stall": "../characters-bd/c5-teastall.png",
}
_raw = {}
_cache = {}


def _keyed(name):
    """Cut the cream ground away by flooding in from the corners of the sheet.

    Flood fill (not a colour distance) is what keeps white clothing intact: the patron's
    pajama and the elder's kurta are only ~14 levels away from the paper, so a global
    colour key punched holes in them. Fill can't reach an enclosed interior.
    """
    if name in _raw:
        return _raw[name]
    im = Image.open(SPRITES[name]).convert("RGB")
    work = im.copy()
    w, h = work.size
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
                 (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        ImageDraw.floodfill(work, seed, (255, 0, 255), thresh=10)
    a = np.asarray(work).astype(np.int16)
    keyed = (a[:, :, 0] > 248) & (a[:, :, 1] < 8) & (a[:, :, 2] > 248)
    alpha = Image.fromarray(np.where(keyed, 0, 255).astype(np.uint8))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    arr = np.array(alpha)
    arr[:2, :] = arr[-2:, :] = 0
    arr[:, :2] = arr[:, -2:] = 0
    out = Image.fromarray(np.dstack([np.asarray(im), arr]), "RGBA")
    out = out.crop(out.split()[3].getbbox())
    _raw[name] = out
    return out


def sprite(name, height, ang=0.0, flip=False, alpha=1.0, grey=0.0):
    key = (name, int(height) // 4, int(round(ang * 2)), flip, round(alpha, 2), round(grey, 2))
    hit = _cache.get(key)
    if hit is not None:
        return hit
    base = _keyed(name)
    h = max(40, int(height))
    w = max(20, int(base.width * h / base.height))
    im = base.resize((w, h), Image.LANCZOS)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if grey > 0.01:
        flat = ImageOps.grayscale(im.convert("RGB")).convert("RGB")
        flat = Image.blend(flat, Image.new("RGB", im.size, GROUND), grey)
        keep = im.split()[3]
        im = flat.convert("RGBA")
        im.putalpha(keep)
    if abs(ang) > 0.05:
        im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    _cache[key] = im
    return im


# ---------------------------------------------------------------- caption plates

_wrap_cache = {}


def _measure(s, size, weight):
    k = (s, size, weight)
    if k not in _wrap_cache:
        _wrap_cache[k] = deva.layout(s, size, weight)[1]
    return _wrap_cache[k]


def wrap(text, size, weight, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if _measure(trial, size, weight) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


_plate_cache = {}


def plate(text, size, weight, color, maxw):
    key = (text, size, weight, color, maxw)
    if key in _plate_cache:
        return _plate_cache[key]
    lines = wrap(text, size, weight, maxw)
    imgs = [deva.text_image(l, size, weight, color) for l in lines]
    wmax = max(i.width for i in imgs)
    lh = int(size * 1.42)
    plate_ = Image.new("RGBA", (wmax, lh * len(imgs)), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        plate_.alpha_composite(im, ((wmax - im.width) // 2, i * lh + (lh - im.height) // 2))
    _plate_cache[key] = plate_
    return plate_


# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, col=GROUND):
        self.im = Image.new("RGBA", (W, H), col + (255,))
        self.d = ImageDraw.Draw(self.im)

    def rect(self, box, col):
        self.d.rectangle(box, fill=col + ((255,) if len(col) == 3 else ()))

    def line(self, pts, col, w=3):
        self.d.line(pts, fill=col + ((255,) if len(col) == 3 else ()), width=w, joint="curve")

    def circle(self, c, r, col):
        self.d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r],
                       fill=col + ((255,) if len(col) == 3 else ()))

    def poly(self, pts, col):
        self.d.polygon(pts, fill=col + ((255,) if len(col) == 3 else ()))

    def puppet(self, name, x, y, h, ang=0.0, flip=False, alpha=1.0, grey=0.0):
        im = sprite(name, h, ang, flip, alpha, grey)
        self.im.alpha_composite(im, (int(x - im.width / 2), int(y - im.height)))

    def text(self, xy, s, size, weight=700, color=INK, anchor="mm"):
        deva.draw_text(self.im, xy, s, size, weight, color, anchor)

    def plate(self, xy, text, size, weight, color, maxw, anchor="top"):
        im = plate(text, size, weight, color, maxw)
        y = int(xy[1] - im.height / 2) if anchor == "mm" else int(xy[1])
        self.im.alpha_composite(im, (int(xy[0] - im.width / 2), y))
        return im.height


# ---------------------------------------------------------------- set dressing

def header(cv, n):
    cv.text((SAFE, 118), "অন্ধকার পাঠ · ০৩", 36, 600, INK, anchor="lm")
    cv.text((W - SAFE - 52, 118), "%s / %s" % (bn(n), bn(10)), 34, 600, META, anchor="mm")


def paper(cv):
    cv.rect((0, 0, W, H), GROUND)


def horizon(cv, y=GY, col=INK, band=None):
    if band:
        cv.rect((0, y, W, H), band)
    cv.line([(0, y), (W, y)], col, 3)


def steam(cv, x, y, t, n=2, h=90, col=META):
    for k in range(n):
        ph = t * 1.5 + k * 0.9
        for i in range(4):
            yy = y - i * h / 4.0 - (ph * 18) % (h / 4.0)
            cv.circle((x + 7 * math.sin(ph + i), yy), 3.2, col)


def notes(cv, x, y, ang, n=3, col=ACCENT):
    """A fan of banknotes. Small, paper-coloured, accent edge."""
    for k in range(n):
        cx = x + k * 26 - (n - 1) * 13
        cy = y - k * 5
        ca, sa = math.cos(ang + k * 0.12), math.sin(ang + k * 0.12)
        pts = []
        for dx, dy in ((-34, -14), (34, -14), (34, 14), (-34, 14)):
            pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
        cv.poly(pts, CARD)
        cv.line(pts + [pts[0]], ACCENT, 3)


def chevrons(cv, x, y, k, col=ACCENT):
    """Little 'respect rising' marks: two carets climbing out of a head."""
    for i in range(2):
        a = max(0.0, min(1.0, k - i * 0.22))
        if a <= 0.02:
            continue
        yy = y - 34 - i * 40 - 14 * a
        w = 13 * (0.7 + 0.3 * a)
        cv.line([(x - w, yy + w), (x, yy - w * 0.4), (x + w, yy + w)], col, 4)


def rain(cv, t, k):
    if k <= 0.02:
        return
    for i in range(26):
        seed = i * 0.618
        x = (int(seed * W) + int(seed * 977)) % W
        y = (t * (900 + 500 * (seed - 0.5)) + i * 137) % (H + 200) - 100
        cv.line([(x, y), (x - 12, y + 46)], COOL, 3)


def water_top(cv, y, t, col=WATER):
    """A rising river with a live surface — a flat rect reads as a wall, this doesn't."""
    pts = [(0, y)]
    for i in range(13):
        x = i * W / 12.0
        pts.append((x, y + 7 * math.sin(TAU * (x / 420.0 + t * 0.42)) + 4 * math.sin(TAU * (x / 170.0 - t * 0.7))))
    pts += [(W, H + 10), (0, H + 10)]
    cv.poly(pts, col)


# ---------------------------------------------------------------- scenes
# Every caption is a subtitle, not the full narration: one idea per frame, big type.
CAPS = {
    0: dict(tag="দোকানদার", line="আজ সবাই রফিক সাহেবের মেহমান"),
    1: dict(tag="রফিক", line="টাকা থাকলে সম্মানও থাকে"),
    2: dict(tag=None, line="মঞ্চ, মাইকে নাম, বুকে রুপোর পদক"),
    3: dict(tag="বুড়ো", line="এই টাকা আমার দরকার নেই"),
    4: dict(tag="রফিক", line="আমার টাকায় পুরো গ্রাম চলে — তুমি কে?",
             extra=("বুড়ো", "যে সম্মান কিনতে হয়, সে সম্মান নয় — ভাড়া")),
    5: dict(tag=None, line="নদী ফুলে উঠল, খাতা শূন্য"),
    6: dict(tag=None, line="তারা আজ চোখ ফিরিয়ে নিল"),
    7: dict(tag="দোকানদার", line="বাকিতে দিই না",
             extra=("রিকশাওয়ালা", "আজ আপনার ভাড়া নেব না")),
    8: dict(tag="বুড়ো", line="কিছু না বলে এক গ্লাস পানি"),
}


def s1(cv, lt, dur):
    """The tea stall, and a bill nobody pays."""
    paper(cv)
    cv.line([(340, 1230), (1040, 1230)], INK, 4)          # the counter plank
    cv.line([(340, 1230), (340, 1430)], META, 2)
    horizon(cv, 1430, META)

    # the tab, a slip of paper that grows as the morning goes on
    sk = expo(f(2.2, 3.2, lt))
    if sk > 0.02:
        cv.rect((430, 1194, 430 + 132 * sk, 1226), CARD)
        cv.line([(430, 1194), (430 + 132 * sk, 1194)], ACCENT, 3)

    # glasses on the counter, steam drifting off them
    for i in range(3):
        gx = 610 + i * 76
        lift = 22 * max(0.0, math.sin(lt * 1.1 + i * 1.7))
        cv.rect((gx, 1168 - lift, gx + 28, 1228 - lift), CARD)
        cv.rect((gx, 1168 - lift, gx + 28, 1228 - lift), WATER)
        cv.line([(gx, 1168 - lift), (gx + 28, 1168 - lift)], ACCENT, 4)
        cv.line([(gx, 1168 - lift), (gx, 1228 - lift)], META, 2)
        cv.line([(gx + 28, 1168 - lift), (gx + 28, 1228 - lift)], META, 2)
        steam(cv, gx + 14, 1160 - lift, lt + i * 0.4, n=1, h=70)

    # the man pouring, and two customers who will not pay
    dy, dg = lifelike(lt, 0.11)
    cv.puppet("stall", 880, 1440 + dy, 740, ang=dg * 0.7)
    c1, a1 = lifelike(lt, 0.6)
    cv.puppet("boy", 175, 1452 + c1, 470, ang=a1, flip=True, grey=0.42)
    c2, a2 = lifelike(lt, 1.9)
    cv.puppet("rickshaw", 330, 1468 + c2, 515, ang=a2 * 0.8, flip=True, grey=0.5)

    header(cv, 1)


def s2(cv, lt, dur):
    """He pays. The village bows."""
    paper(cv)
    horizon(cv, 1400, META)

    k = snap(f(0.25, 1.25, lt))
    x = 1290 - 520 * k
    dy, dg = lifelike(lt, 0.4)
    tilt = dg + 2.0 * (1 - k) - 1.4 * expo(f(3.0, 3.9, lt))
    cv.puppet("patron", x, 1420 + dy, 800, ang=tilt)

    # the notes leave his hand and land on the counter
    for i in range(3):
        t0 = 1.55 + i * 0.22
        kk = snap(f(t0, t0 + 0.55, lt))
        if kk > 0.01:
            nx = x - 40 - 190 * kk
            ny = 1050 - 90 * math.sin(kk * math.pi) + 120 * kk * kk
            notes(cv, nx, ny, -0.5 + 0.9 * kk, n=2)

    # the crowd, greyed and turned, bowing in a stagger
    for i, (cx, hh) in enumerate(((180, 500), (300, 540), (1010, 520))):
        b = snap(f(3.3 + i * 0.18, 4.0 + i * 0.18, lt))
        cy, cg = lifelike(lt, 1.1 + i * 0.7)
        cv.puppet("boy" if i == 0 else ("rickshaw" if i == 1 else "stall"), cx, 1440 + cy,
                  hh, ang=cg - 3.5 * b, flip=(i != 2), grey=0.62)
        chevrons(cv, cx, 1440 + cy - hh * 0.93, snap(f(4.3 + i * 0.2, 5.0 + i * 0.2, lt)))

    header(cv, 2)


def s3(cv, lt, dur):
    """He buys the stage, the microphone, the medal."""
    paper(cv)
    # a stage edge and a name banner
    cv.rect((0, 1252, W, 1278), INK)                     # the edge of the stage
    bk = expo(f(0.2, 0.9, lt))
    if bk > 0.02:
        cv.rect((70, 392, 70 + 430 * bk, 520), CARD)
        cv.line([(70, 392), (70 + 430 * bk, 392)], INK, 4)
        cv.line([(70, 520), (70 + 430 * bk, 520)], INK, 4)
        if bk > 0.55:
            cv.text((70 + 215 * bk, 456), "রফিক", 66, 700, ACCENT)

    horizon(cv, 1400, META)

    # mic stand
    mk = expo(f(1.2, 1.9, lt))
    if mk > 0.02:
        mx = 985
        cv.line([(mx - 46, 1400), (mx + 46, 1400)], INK, 6)      # a foot, not a lollipop
        cv.line([(mx, 1400), (mx, 1400 - 240 * mk)], INK, 5)
        cv.circle((mx, 1400 - 240 * mk - 12), 13, INK)

    dy, dg = lifelike(lt, 0.75)
    cv.puppet("patron", 600, 1410 + dy, 800, ang=dg * 1.3)

    # the medal arrives on his chest
    mk2 = snap(f(4.2, 5.4, lt))
    if mk2 > 0.02:
        my = 930 + 70 * (1 - mk2)
        cv.poly([(610, my - 74), (646, my - 74), (628, my - 8)], ACCENT)
        cv.circle((628, my), 27 * mk2, CARD)
        cv.circle((628, my), 27 * mk2, INK)
        cv.circle((628, my), 22 * mk2, CARD)
        cv.circle((628, my), 8 * mk2, ACCENT)

    # applause
    for i, (cx, hh, fy) in enumerate(((150, 470, 1452), (330, 445, 1462))):
        cy, cg = lifelike(lt, 2.2 + i * 0.5)
        cv.puppet("stall" if i == 0 else "boy", cx, fy + cy, hh, ang=cg,
                  flip=True, grey=0.66)
        ap = 1 - f(5.0, 9.6, lt)
        if ap > 0.05:                                  # clap marks, over the head not on it
            for k in range(3):
                off = 7 * math.sin(TAU * 2.4 * lt + k * 0.8)
                cv.circle((cx + (k - 1) * 30, fy + cy - hh - 34 - off), 6, ACCENT)

    header(cv, 3)


def s4(cv, lt, dur):
    """One man hands the money back."""
    paper(cv)
    horizon(cv, 1400, META)

    ey, eg = lifelike(lt, 0.2)
    cv.puppet("elder", 320, 1400 + ey, 770, ang=eg * 0.8)

    k = snap(f(0.3, 1.2, lt))
    py, pg = lifelike(lt, 1.4)
    cv.puppet("patron", 820, 1415 + py, 800, ang=pg - 1.0 * k)

    # the offer goes out, then comes back
    out_k = snap(f(1.5, 2.3, lt))
    back = snap(f(3.0, 4.1, lt))
    if out_k > 0.02:
        nx = 700 - 300 * out_k + 330 * back
        ny = 1080 + 40 * (1 - out_k) - 120 * math.sin(back * math.pi) + 150 * back
        notes(cv, nx, ny, -0.35 + 1.1 * back, n=3)

    # his palm stays up
    pk = snap(f(2.6, 3.3, lt))
    if pk > 0.02:
        cv.line([(392, 1140), (400 + 30 * pk, 1090 - 40 * pk)], META, 3)

    header(cv, 4)


def s5(cv, lt, dur):
    """'তুমি কে?' — the only question that matters."""
    paper(cv)
    horizon(cv, 1400, META)

    ey, eg = lifelike(lt, 0.9)
    cv.puppet("elder", 330, 1400 + ey, 720, ang=eg * 0.6)

    lean = 1 - 0.55 * expo(f(9.0, 10.6, lt))
    py, pg = lifelike(lt, 0.3)
    cv.puppet("patron", 700 + 40 * expo(f(0.4, 2.2, lt)), 1440 + py, 880, ang=pg - 2.6 * lean)

    # the notes are on the floor now
    for i, (gx, gy) in enumerate(((600, 1412), (700, 1420), (790, 1408))):
        cv.poly([(gx - 40, gy - 8), (gx + 40, gy - 12), (gx + 40, gy + 10), (gx - 40, gy + 14)], CARD)
        cv.line([(gx - 38, gy - 8), (gx + 38, gy - 12)], ACCENT, 3)

    header(cv, 5)


def s6(cv, lt, dur):
    """The night the river took it all."""
    paper(cv)
    k = snap(f(1.2, 7.4, lt))
    if k > 0.01:                                          # the light goes out of the day
        cv.rect((0, 0, W, 1430), (
            int(GROUND[0] + (226 - GROUND[0]) * k),
            int(GROUND[1] + (231 - GROUND[1]) * k),
            int(GROUND[2] + (234 - GROUND[2]) * k)))
    rain(cv, lt, snap(f(0.6, 2.0, lt)) * (1 - 0.55 * f(7.0, 9.4, lt)))

    # the river climbs the frame behind him, up to the ground line but never into the type
    wy = 1430 - 300 * snap(f(2.0, 7.6, lt))
    pts = [(0, wy)]
    for i in range(13):
        x = i * W / 12.0
        pts.append((x, wy + 7 * math.sin(TAU * (x / 420.0 + lt * 0.42))
                    + 4 * math.sin(TAU * (x / 170.0 - lt * 0.7))))
    pts += [(W, 1430), (0, 1430)]
    cv.poly(pts, WATER)
    horizon(cv, 1430, META)

    dy, dg = lifelike(lt, 0.5, 0.6)
    sink = 44 * snap(f(6.6, 9.4, lt))
    cv.puppet("patron", 640, 1440 + dy, 740, ang=dg + 2.4 * f(6.6, 9.4, lt),
              grey=0.5 * f(6.6, 9.2, lt))

    # the ledger, adrift
    if k > 0.02:
        lx = 210 + 16 * math.sin(TAU * 0.3 * lt)
        ly = 1250 + 10 * math.sin(TAU * 0.4 * lt + 1.0)
        cv.rect((lx, ly, lx + 150, ly + 94), CARD)
        cv.line([(lx, ly), (lx + 150, ly)], INK, 3)
        for i in range(3):
            cv.line([(lx + 16, ly + 26 + i * 21), (lx + 128, ly + 26 + i * 21)], META, 2)

    header(cv, 6)


def s7(cv, lt, dur):
    """The morning after: nobody meets his eye."""
    paper(cv)
    horizon(cv, 1400, META)

    dy, dg = lifelike(lt, 0.2, 1.4)
    cv.puppet("patron", 380 + 30 * snap(f(0.5, 3.0, lt)), 1440 + dy, 660,
              ang=dg + 3.0 * f(1.0, 4.0, lt), grey=0.18)

    for i, (cx, hh, nm, fy) in enumerate(((660, 470, "boy", 1450), (810, 510, "rickshaw", 1464),
                                          (950, 480, "stall", 1452))):
        turn = snap(f(2.2 + i * 0.3, 3.2 + i * 0.3, lt))
        cy, cg = lifelike(lt, 1.3 + i * 0.6)
        cv.puppet(nm, cx + 26 * turn, fy + cy, hh, ang=cg + 2.0 * turn,
                  flip=True, grey=0.5)

    header(cv, 7)


def s8(cv, lt, dur):
    """'বাকিতে দিই না.'"""
    paper(cv)
    cv.line([(560, 1230), (1040, 1230)], INK, 4)
    cv.line([(560, 1230), (560, 1430)], META, 2)
    horizon(cv, 1420, META)

    sy, sg = lifelike(lt, 0.4)
    cv.puppet("stall", 745, 1440 + sy, 720, ang=sg * 0.8, flip=True)

    ay, ag = lifelike(lt, 1.8)
    cv.puppet("patron", 300, 1450 + ay, 660, ang=ag + 2.0 * f(0.4, 2.2, lt), grey=0.3)

    ry, rg = lifelike(lt, 2.9)
    cv.puppet("rickshaw", 1000, 1450 + ry, 660, ang=rg, flip=True, grey=0.45)

    # the cup is pushed back across the counter
    pk = snap(f(3.4, 4.3, lt))
    if pk > 0.02:
        cx = 700 - 210 * pk
        cv.rect((cx, 1198, cx + 34, 1232), WATER)
        cv.line([(cx, 1198), (cx + 34, 1198)], ACCENT, 4)
        cv.line([(cx, 1198), (cx, 1232)], META, 2)
        cv.line([(cx + 34, 1198), (cx + 34, 1232)], META, 2)

    header(cv, 8)


def s9(cv, lt, dur):
    """A glass of water, and no words."""
    paper(cv)
    horizon(cv, 1420, META)

    ey, eg = lifelike(lt, 0.3)
    cv.puppet("elder", 760, 1420 + ey, 780, ang=eg * 0.7)

    lift = snap(f(5.2, 7.4, lt))
    py, pg = lifelike(lt, 1.2)
    cv.puppet("patron", 300, 1490 + py, 600, ang=pg + 4.0 * (1 - lift) - 1.0 * lift, grey=0.12)

    # the glass comes across
    gk = snap(f(1.4, 2.8, lt))
    gx = 745 - 265 * gk
    if gk > 0.02:
        gy0 = 1150
        cv.rect((gx, gy0, gx + 48, gy0 + 84), CARD)
        cv.rect((gx + 5, gy0 + 16, gx + 43, gy0 + 79), WATER)
        cv.line([(gx, gy0), (gx + 48, gy0)], ACCENT, 4)
        cv.line([(gx, gy0), (gx, gy0 + 84)], INK, 3)
        cv.line([(gx + 48, gy0), (gx + 48, gy0 + 84)], INK, 3)
        cv.line([(gx, gy0 + 84), (gx + 48, gy0 + 84)], INK, 3)
        steam(cv, gx + 24, gy0 - 8, lt * 0.6, n=1, h=40, col=(168, 188, 198))

    header(cv, 9)


LESSON = [("সম্মান কিনেছিলে,", 0.5), ("তাই ভাড়াটে ছিল।", 2.2), ("ভাড়া শেষ — সম্মানও শেষ।", 4.4)]


def s10(cv, lt, dur):
    """The lesson, set as type."""
    paper(cv)
    cv.puppet("patron", 250, 1730, 470, ang=1.4, grey=0.55)
    cv.puppet("elder", 830, 1730, 470, ang=-1.0, grey=0.3)

    cv.text((SAFE, 240), "অন্ধকার পাঠ · ০৩", 36, 600, META, anchor="lm")
    cv.line([(SAFE, 300), (W - SAFE, 300)], META, 2)

    y = 470
    for i, (line, t0) in enumerate(LESSON):
        k = expo(f(t0, t0 + 0.9, lt))
        if k <= 0.02:
            continue
        col = ACCENT if i == 2 else INK
        cv.plate((W / 2, y + (1 - k) * 24), line, 84 if i < 2 else 78, 700, col, 940)
        y += 210


def s11(cv, lt, dur):
    """End card: does respect actually have a price?"""
    paper(cv)
    ck = snap(f(0.1, 0.9, lt))
    cv.circle((W / 2, 560), 300 * ck, (247, 246, 241))

    cv.text((W / 2, 210), "অন্ধকার পাঠ · ০৩", 38, 600, META)
    cv.plate((W / 2, 470), "সম্মান কি সত্যিই", 92, 700, INK, 920)
    cv.plate((W / 2, 640), "কেনা যায়?", 92, 700, ACCENT, 920)

    # drawn arrow — the font has no 👇, and tofu is worse than a shape
    ak = expo(f(1.4, 2.2, lt))
    if ak > 0.02:
        ay = 830 + 12 * math.sin(TAU * 0.5 * lt)
        cv.line([(W / 2, ay), (W / 2, ay + 70 * ak)], ACCENT, 8)
        cv.poly([(W / 2 - 26, ay + 62 * ak), (W / 2 + 26, ay + 62 * ak), (W / 2, ay + 106 * ak)], ACCENT)

    pk = expo(f(2.4, 3.2, lt))
    if pk > 0.02:
        cv.rect((330, 1130, 750, 1226), ACCENT)
        cv.text((540, 1178), "ফলো করো", 52, 700, CARD)
    cv.text((540, 1300), "প্রতি শুক্রবার · নতুন পাঠ", 38, 600, META)

    cv.puppet("patron", 392, 1878, 452, ang=1.2, grey=0.5)
    cv.puppet("elder", 700, 1878, 452, ang=-0.8, grey=0.25)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11]
END_AT = len(SCENES) - 1


# ---------------------------------------------------------------- captions

def captions(cv, i, lt, dur):
    cap = CAPS.get(i)          # the lesson and the end card set their own type
    if cap is None:
        return
    k = expo(f(0.25, 0.95, lt))
    fade = 1.0 - expo(f(dur - 0.55, dur - 0.1, lt))
    if k <= 0.02 or fade <= 0.02:
        return
    y = 1560 + (1 - k) * 18
    if cap.get("tag"):
        cv.text((SAFE, y - 66), cap["tag"], 38, 700, ACCENT, anchor="lm")
    cv.plate((W / 2, y), cap["line"], 62, 700, INK, 940)
    extra = cap.get("extra")
    if extra:
        ek = expo(f(4.6, 5.4, lt))
        if ek > 0.02:
            cv.text((SAFE, 1790), extra[0], 34, 700, ACCENT, anchor="lm")
            cv.plate((W / 2, 1840), extra[1], 50, 600, META, 940)


# ---------------------------------------------------------------- timeline

def _probe(path):
    import imageio_ffmpeg
    txt = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", txt)
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


DUR = [_probe(p) for p in TAKES]
NAR, _t = [], START
for d in DUR:
    NAR.append(round(_t, 3))
    _t += d + GAP
BOUNDS = [0.0] + [round(n - 0.30, 3) for n in NAR[1:]] + [round(NAR[-1] + DUR[-1] + 0.60, 3)]
TOTAL = round(BOUNDS[-1] + TAIL, 3)
NF = int(round(TOTAL * FPS))

GRAIN = None


def grain():
    global GRAIN
    if GRAIN is None:
        rng = np.random.default_rng(3)
        n = rng.normal(0, 5.0, (H // 2, W // 2)).clip(-14, 14)
        n = np.repeat(np.repeat(n, 2, axis=0), 2, axis=1)[:H, :W]
        base = np.zeros((H, W, 3), np.uint8) + 128
        img = Image.fromarray((base + n[:, :, None]).clip(0, 255).astype(np.uint8))
        GRAIN = img
    return GRAIN


def draw(t):
    i = 0
    for k in range(len(BOUNDS)):
        if t >= BOUNDS[k]:
            i = k
    i = min(i, END_AT)
    lt = t - BOUNDS[i]
    dur = (BOUNDS[i + 1] if i + 1 < len(BOUNDS) else TOTAL) - BOUNDS[i]
    cv = Canvas()
    SCENES[i](cv, lt, dur)
    captions(cv, i, lt, dur)
    out = cv.im.convert("RGB")
    return Image.blend(out, grain(), 0.055)


# ---------------------------------------------------------------- encoder

def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def main():
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1])
        os.makedirs("frames", exist_ok=True)
        draw(t).save("frames/still-%06.2f.png" % t)
        print("still", t, "scene", [k for k, b in enumerate(BOUNDS) if t >= b][-1])
        return

    print("timeline", NAR, "total", TOTAL, "frames", NF, flush=True)

    if "--mix" in sys.argv:
        inputs, filt, labels = [], [], []
        for k, start in enumerate(NAR):
            inputs += ["-i", TAKES[k]]
            ms = int(round(start * 1000))
            filt.append("[%d:a]adelay=%d|%d[a%d]" % (k, ms, ms, k))
            labels.append("[a%d]" % k)
        fc = ";".join(filt) + ";" + "".join(labels) + "amix=inputs=%d:normalize=0,apad[a]" % len(NAR)
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error"] + inputs +
                       ["-filter_complex", fc, "-map", "[a]", "-ar", "44100", "-ac", "2",
                        "-t", "%.3f" % TOTAL, MIX], check=True)
        print("mix ok")
        return

    if "--seg" in sys.argv:
        j = sys.argv.index("--seg")
        a, b, sp = int(sys.argv[j + 1]), int(sys.argv[j + 2]), sys.argv[j + 3]
        cmd = [ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", sp]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(a, b):
            proc.stdin.write(draw(i / FPS).tobytes())
            if (i - a) % 120 == 0:
                print("  seg %d/%d" % (i - a, b - a), flush=True)
        proc.stdin.close()
        proc.wait()
        print("segdone", sp, os.path.getsize(sp), flush=True)
        return

    if "--join" in sys.argv:
        segs = sys.argv[sys.argv.index("--join") + 1:]
        with open("segs.txt", "w") as fh:
            for sp in segs:
                fh.write("file '%s'\n" % os.path.abspath(sp))
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", "segs.txt", "-i", MIX, "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "144k", "-movflags", "+faststart", OUT], check=True)
        print("joined", os.path.getsize(OUT))
        return


if __name__ == "__main__":
    main()
