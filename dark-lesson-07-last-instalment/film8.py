"""film8.py — অন্ধকার পাঠ ০৭ · শেষ কিস্তি (কথ্য সংস্করণ).

Five generated Claude-2D characters, treated as paper puppets. The plates were cut out
in prep7.py, their mouths cleared in prep7b.py; here every frame pastes a scaled sprite,
redraws the mouth from the take's loudness envelope, blinks it, and moves it a little.

The sets are drawn, not photographed: flat vector courtyard, market and gate, baked once
per shot at 1.4x so the camera can drift and push inside them without re-rendering a wall.

    python3 film8.py --still 24.5 --out frames/x.png
    python3 film8.py --seg 0 1000 --out /tmp/a.mp4
"""
import functools
import json
import math
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw

import deva

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "audio")
CAST = os.path.join(HERE, "cast")

try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:                                            # pragma: no cover
    FF = "ffmpeg"

W, H = 1080, 1920
FPS = 24
OX, OY = 170, 150          # overscan so the camera can move
BAKE = 1.4

# ------------------------------------------------------------------ colour
PAPER = (240, 238, 230)
PAPER_D = (224, 219, 208)
PAPER_M = (206, 200, 188)
INK = (26, 23, 20)
INK_S = (92, 88, 80)
INK_D = (14, 13, 12)
MUST = (201, 154, 46)
MUST_D = (163, 120, 33)
MUST_L = (228, 193, 106)
CORAL = (217, 119, 87)
CORAL_D = (176, 86, 60)
OFF = (250, 247, 240)
SAND = (215, 179, 117)
SAND_D = (190, 152, 92)
OLIVE = (112, 124, 74)
OLIVE_D = (82, 94, 54)
LAMP = (247, 205, 120)
NIGHT = (23, 25, 30)
NIGHT_W = (48, 45, 46)
NIGHT_G = (40, 37, 36)

CREAM = (245, 241, 231)
RED = (176, 74, 52)


def lerp(a, b, q):
    return a + (b - a) * q


def clamp(v, a=0.0, b=1.0):
    return a if v < a else (b if v > b else v)


def soft(q):
    q = clamp(q)
    return q * q * (3 - 2 * q)


def ease(q):
    q = clamp(q)
    return 1 - (1 - q) ** 3


# ------------------------------------------------------------------ pen
class Pen:
    def __init__(self, img, ss=1.0, ox=0.0, oy=0.0):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.ss = ss
        self.ox = ox
        self.oy = oy

    def _p(self, pts):
        return [((x + self.ox) * self.ss, (y + self.oy) * self.ss) for x, y in pts]

    def poly(self, pts, col, outline=None, ow=5):
        if outline:
            self.d.polygon(self._p(pts), fill=col, outline=outline,
                           width=max(1, int(ow * self.ss)))
        else:
            self.d.polygon(self._p(pts), fill=col)

    def rect(self, x0, y0, x1, y1, col, outline=None, ow=5):
        box = [((x0 + self.ox) * self.ss, (y0 + self.oy) * self.ss),
               ((x1 + self.ox) * self.ss, (y1 + self.oy) * self.ss)]
        if outline:
            self.d.rectangle(box, fill=col, outline=outline, width=max(1, int(ow * self.ss)))
        else:
            self.d.rectangle(box, fill=col)

    def ell(self, x0, y0, x1, y1, col, outline=None, ow=5):
        box = [((x0 + self.ox) * self.ss, (y0 + self.oy) * self.ss),
               ((x1 + self.ox) * self.ss, (y1 + self.oy) * self.ss)]
        if outline:
            self.d.ellipse(box, fill=col, outline=outline, width=max(1, int(ow * self.ss)))
        else:
            self.d.ellipse(box, fill=col)

    def line(self, pts, col, w=5):
        self.d.line(self._p(pts), fill=col, width=max(1, int(w * self.ss)), joint="curve")


# ------------------------------------------------------------------ script
SHOTS = [
    dict(clip=1, who="kagojwala", scene="market", light="morning", cap="বাজার · সকাল",
         acts=[("kagojwala", 780, 730, 1252), ("dada", 390, 712, 1252)],
         cam=(1.00, 1.055, 540, 540, 900, 870), pre=0.0),
    dict(clip=2, who="dada", scene="yard", light="morning", cap="উঠোন · সকাল",
         acts=[("dada", 470, 735, 1252), ("bou", 800, 640, 1252)],
         cam=(1.02, 1.09, 540, 520, 880, 860), pre=0.55),
    dict(clip=3, who="bou", scene="yard", light="morning", cap="উঠোন · সকাল",
         acts=[("bou", 530, 1520, 1810)],
         cam=(1.03, 1.11, 520, 545, 830, 800), pre=0.4),
    dict(clip=4, who="chele", scene="yard", light="noon", cap="উঠোন · দুপুর",
         acts=[("chele", 520, 1500, 1800)],
         cam=(1.10, 1.02, 540, 525, 820, 840), pre=0.5),
    dict(clip=5, who="natni", scene="yard", light="noon", cap="উঠোন · দুপুর",
         acts=[("natni", 545, 1210, 1730)],
         cam=(1.02, 1.10, 540, 540, 800, 780), pre=0.55),
    dict(clip=6, who="dada", scene="yard", light="dusk", cap="উঠোন · সন্ধ্যা",
         acts=[("dada", 520, 1530, 1810)],
         cam=(1.04, 1.10, 530, 550, 820, 800), pre=0.7),
    dict(clip=7, who="chele", scene="yard", light="dusk", cap="উঠোন · সন্ধ্যা",
         acts=[("chele", 560, 1490, 1800)],
         cam=(1.09, 1.02, 545, 530, 830, 850), pre=0.4),
    dict(clip=8, who="kagojwala", scene="gate", light="dusk", cap="গেট · সন্ধ্যা",
         acts=[("kagojwala", 430, 706, 1252)],
         cam=(1.00, 1.07, 560, 520, 900, 870), pre=0.8),
    dict(clip=9, who="natni", scene="yard", light="night", cap="উঠোন · রাত",
         acts=[("natni", 545, 1230, 1740)],
         cam=(1.03, 1.11, 540, 540, 790, 770), pre=0.7),
    dict(clip=10, who="kagojwala", scene="yard", light="night", cap="উঠোন · রাত",
         acts=[("kagojwala", 530, 1520, 1810)],
         cam=(1.06, 1.13, 540, 545, 820, 795), pre=0.6),
]

TEXT = {
    1: "এই কাগজটা নাও, বাবা। খাতা বলছে, তোমাদের ঘরের ঋণ আজ শোধ। দাদার আঙুলের ছাপ, আমার সামনেই দেওয়া। কিন্তু কাগজের একটা দোষ আছে, সে কিছু ভোলে না।",
    2: "শুনো সবাই। এই কাগজটা আমার হাতে ধরিয়ে দিয়েছিল ও নিজেই। বলেছিল, দাদা, আপনার টাকা শেষ, আর কোনো ঋণ নেই। আমি সই করতে জানি না, তাই বুড়ো আঙুলের ছাপ দিয়েছি। এখন তোমরা বলছ, খাতায় অন্য কথা লেখা?",
    3: "আমি ছাপটা দেখেছি, দাদা। এটা আপনার আঙুলের ছাপ না, এটা কলম দিয়ে আঁকা। আর এই সইটা... সইটা আমার নিজের ছেলের হাতের লেখা। আমি চিনতে পারছি।",
    4: "আমি কিছু ভাঙিনি, আম্মা। একটা ফর্ম ছিল, সই ছাড়া স্কুলে ঢোকা যায় না। ভেবেছিলাম, দাদার নামটা লিখে দিলে কারও ক্ষতি হবে না। কেউ দেখবে না। কেউ দেখেনি।",
    5: "দাদু, আমি দেখেছিলাম। ভাইয়া কাগজটায় দাদুর নামে লিখছিল। ভাইয়া বলেছিল, এটা কাউকে বলিস না, দাদু কষ্ট পাবেন। তাই আমি চুপ করে ছিলাম।",
    6: "তুই চুপ করে ছিলি। আমি বুড়ো মানুষ, অক্ষর চিনি না, তাই আমিও চুপ। এই ঘরে সত্যি কথা বলার লোক একজনও নেই। তাহলে ঘরটা থাকবে কার নামে?",
    7: "আমি শুধু একটা ফোন চাইছিলাম, আম্মা। ভাবলাম, এই একটা ছোট্ট মিথ্যা। ওই ছোট্ট মিথ্যা আজ আমাদের ঘরটাকে খেয়ে ফেলছে।",
    8: "কাগজ কাউকে মিথ্যা বলে না, বাবা। কাগজ শুধু মনে রাখে কে কী লিখেছে। আমি কাগজ বেচি, লেখা বেচি না। লেখাটা তোমাদের ঘরের লোকের হাতের, তাই জবাবও তোমাদের ঘরের।",
    9: "দাদু, আমি আর কখনো চুপ করব না।",
    10: "মিথ্যা একবার লিখলে, কাগজ সেটা সারাজীবন বহন করে। আর কাগজের কোনো দোষ নেই, সে শুধু সত্যি বলে। তোমরা যা লিখেছ, তাই তোমরা।",
}

LABEL = {"dada": "দাদা", "chele": "ছেলে", "bou": "বউ", "natni": "নাতনি",
         "kagojwala": "কাগজওয়ালা"}

LEAD = 2.4
TAIL_PAPER = 3.0
TAIL_CARD = 3.0


# ------------------------------------------------------------------ audio
def _dur(path):
    err = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", err)
    if not m:
        return 8.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


@functools.lru_cache(maxsize=16)
def envelope(clip):
    src = os.path.join(AUD, "d%02d.mp3" % clip)
    wav = os.path.join(AUD, "_env%02d.wav" % clip)
    if not os.path.exists(wav):
        subprocess.run([FF, "-y", "-v", "error", "-i", src, "-ar", "22050", "-ac", "1", wav],
                       check=True)
    import wave
    with wave.open(wav) as fh:
        a = np.frombuffer(fh.readframes(fh.getnframes()), dtype=np.int16).astype(np.float32)
    a /= 32768.0
    hop = 22050 // FPS
    n = len(a) // hop
    r = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1))
    r = np.convolve(r, np.array([0.18, 0.64, 0.18]), mode="same")
    top = np.percentile(r, 96) + 1e-9
    r = np.clip(r / top * 1.45, 0, 1) ** 0.70
    r[r < 0.09] = r[r < 0.09] * 0.25
    return tuple(float(v) for v in r)


def build_timeline():
    t, rows = LEAD, []
    for i, s in enumerate(SHOTS):
        t += s["pre"]
        d = _dur(os.path.join(AUD, "d%02d.mp3" % s["clip"]))
        rows.append(dict(s, t0=t, dur=d, idx=i, text=TEXT[s["clip"]]))
        t += d
    return rows, t


ENTRIES, LAST_END = build_timeline()
PAPER_A = LAST_END + 0.45
CARD_A = PAPER_A + TAIL_PAPER
TOTAL = CARD_A + TAIL_CARD

ACTIVE = {e["idx"]: (e["t0"], e["t0"] + e["dur"]) for e in ENTRIES}

SPRITES = json.load(open(os.path.join(CAST, "rigs.json")))
FILES = {"dada": "01-dada", "bou": "02-bou", "chele": "03-chele",
         "natni": "04-natni", "kagojwala": "05-kagojwala"}


def shot_at(t):
    for e in ENTRIES:
        if e["t0"] - 0.20 <= t < e["t0"] + e["dur"] + 0.30:
            return e
    if t < LEAD:
        return ENTRIES[0]
    return ENTRIES[-1]


@functools.lru_cache(maxsize=8)
def sprite(name):
    return Image.open(os.path.join(CAST, FILES[name] + "-rig.png")).convert("RGBA")


# ------------------------------------------------------------------ sets
def glow(p, x, y, R, col=LAMP, peak=64):
    """Smooth radial falloff, built small and scaled up — no visible rings."""
    n = 220
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2)
    a = np.clip(1 - d, 0, 1) ** 2.2 * peak
    lay = np.zeros((n, n, 4), np.uint8)
    lay[..., 0], lay[..., 1], lay[..., 2] = col
    lay[..., 3] = a.astype(np.uint8)
    img = Image.fromarray(lay, "RGBA").resize(
        (int(2 * R * p.ss), int(2 * R * p.ss)), Image.BILINEAR)
    p.img.alpha_composite(img, (int((x - R + p.ox) * p.ss), int((y - R + p.oy) * p.ss)))


def sun(p, x, y, r, col=LAMP):
    p.ell(x - r, y - r, x + r, y + r, col)


def far_buildings(p, base, col, edge=None):
    for x0, w, h in ((20, 190, 250), (230, 240, 190), (500, 150, 300), (700, 260, 210),
                     (980, 190, 260)):
        p.rect(x0, base - h, x0 + w, base, col, outline=edge or INK, ow=5)
    p.rect(-OX - 20, base - 6, W + OX + 20, base + 8, INK)


def market(p, light):
    if light == "morning":
        sky, ground, wood, paper_c, wall = PAPER, SAND, MUST_D, OFF, CREAM
    else:
        sky, ground, wood, paper_c, wall = PAPER_D, SAND_D, MUST_D, PAPER, OFF
    p.poly([(-OX, -OY), (W + OX, -OY), (W + OX, 1252), (-OX, 1252)], sky)

    # the row of shopfronts behind
    p.rect(-OX, 470, W + OX, 1252, wall, outline=INK, ow=7)
    for x0, x1, shut in ((40, 300, CORAL_D), (330, 590, MUST_D), (620, 880, CORAL_D),
                         (900, 1180, MUST_D)):
        p.rect(x0, 560, x1, 780, shut, outline=INK, ow=5)
        for i in range(1, 3):
            p.line([(x0 + i * (x1 - x0) / 3, 560), (x0 + i * (x1 - x0) / 3, 780)], INK, 3)
        p.rect(x0 + 10, 800, x1 - 10, 830, PAPER_M, outline=INK, ow=3)
    p.line([(-OX, 470), (W + OX, 470)], INK, 7)

    # awning over the left counter
    p.poly([(-OX, 250), (640, 250), (650, 430), (-OX, 430)], CORAL)
    for i in range(5):
        x = -180 + i * 168
        p.poly([(x, 250), (x + 82, 250), (x + 90, 430), (x + 8, 430)], OFF)
    p.line([(-OX, 250), (640, 250)], INK, 8)
    p.rect(584, 430, 616, 1252, wood, outline=INK, ow=6)

    # counter
    p.rect(-OX, 1010, 330, 1070, wood, outline=INK, ow=6)
    p.rect(276, 1070, 330, 1252, wood, outline=INK, ow=6)
    p.rect(-OX, 1070, -30, 1252, wood, outline=INK, ow=6)
    for x, y, wd, ht in ((-140, 962, 190, 48), (-120, 916, 160, 46), (40, 966, 176, 44),
                         (60, 920, 140, 44)):
        p.rect(x, y, x + wd, y + ht, paper_c, outline=INK, ow=5)
        p.line([(x + 10, y + ht // 2), (x + wd - 12, y + ht // 2)], INK_S, 3)
    p.ell(-40, 1042, 60, 1104, MUST_L, outline=INK, ow=5)
    p.line([(10, 1042), (10, 990)], INK, 6)
    p.ell(-8, 970, 28, 1006, MUST, outline=INK, ow=5)

    # ground
    p.rect(-OX, 1252, W + OX, H + OY, ground)
    p.line([(-OX, 1252), (W + OX, 1252)], INK, 8)

    # two men at the counter, back turned, waiting
    for x, s_ in ((150, 1.0), (250, 1.08)):
        p.ell(x - 26 * s_, 1252 - 196 * s_, x + 26 * s_, 1252 - 128 * s_, INK_S)
        p.poly([(x - 46 * s_, 1252), (x + 46 * s_, 1252), (x + 36 * s_, 1252 - 136 * s_),
                (x - 36 * s_, 1252 - 136 * s_)], INK_S)
    if light == "morning":
        sun(p, 890, 150, 60)
        for bx, by in ((300, 130), (352, 108)):
            p.line([(bx - 18, by - 8), (bx, by + 2), (bx + 18, by - 8)], INK_S, 4)


def yard(p, light):
    if light == "morning":
        sky, wall, ground, door, leaf = PAPER, CREAM, SAND, MUST, OLIVE
    elif light == "noon":
        sky, wall, ground, door, leaf = PAPER, OFF, SAND, MUST, OLIVE
    elif light == "dusk":
        sky, wall, ground, door, leaf = (233, 197, 164), (238, 219, 198), (203, 163, 112), MUST_D, OLIVE_D
    else:
        sky, wall, ground, door, leaf = NIGHT, NIGHT_W, NIGHT_G, (56, 48, 40), (34, 38, 34)

    p.poly([(-OX, -OY), (W + OX, -OY), (W + OX, 760), (-OX, 760)], sky)
    p.rect(-OX, 240, W + OX, 1268, wall, outline=INK, ow=8)
    p.line([(-OX, 300), (W + OX, 300)], PAPER_M if light != "night" else (60, 56, 54), 4)
    for x in (330, 700, 980):
        p.line([(x, 900), (x + 14, 1010), (x - 6, 1130)],
               (206, 200, 188) if light != "night" else (62, 58, 56), 3)

    # door
    p.rect(96, 470, 430, 1268, door, outline=INK, ow=9)
    p.line([(263, 470), (263, 1268)], INK_D, 6)
    p.rect(180, 820, 214, 860, INK_D)
    p.rect(340, 820, 374, 860, INK_D)

    for x in (180, 345):
        p.line([(x, 480), (x, 1262)], INK_D, 3)

    # jali window
    p.rect(640, 620, 800, 790, sky, outline=INK, ow=6)
    for i in range(1, 4):
        p.line([(640 + i * 40, 620), (640 + i * 40, 790)], INK, 3)
        p.line([(640, 620 + i * 42), (800, 620 + i * 42)], INK, 3)

    # line + cloth


    # tree
    p.rect(944, 700, 1002, 1268, MUST_D if light != "night" else (52, 44, 38), outline=INK, ow=6)
    for cx, cy, r in ((880, 706, 92), (975, 660, 116), (1052, 724, 84)):
        p.ell(cx - r, cy - r, cx + r, cy + r, leaf, outline=INK, ow=6)

    p.rect(-OX, 1226, W + OX, 1268, PAPER_M if light != "night" else (52, 48, 46))

    # ground, steps, pot
    p.rect(-OX, 1268, W + OX, H + OY, ground)
    p.line([(-OX, 1268), (W + OX, 1268)], INK, 8)
    p.rect(-OX, 1268, 250, 1318, SAND_D if light != "night" else (34, 32, 31), outline=INK, ow=6)
    for x, y, r in ((360, 1360, 9), (700, 1420, 7), (960, 1330, 11), (180, 1450, 8)):
        p.ell(x - r, y - r * 0.6, x + r, y + r * 0.6,
              SAND_D if light != "night" else (34, 32, 31))
    p.ell(1000, 1170, 1088, 1268,
          (188, 108, 74) if light != "night" else (58, 44, 40), outline=INK, ow=6)
    p.ell(1016, 1190, 1072, 1236, (150, 80, 54) if light != "night" else (44, 34, 32))

    if light == "morning":
        sun(p, 900, 170, 60)
    elif light == "dusk":
        sun(p, 880, 520, 74, (238, 138, 96))
    else:
        p.ell(636, 138, 732, 234, OFF)          # moon
        p.ell(662, 164, 758, 260, NIGHT)
        # lamp on a bracket
        p.line([(300, 610), (300, 736)], INK, 6)
        p.ell(292, 700, 308, 748, OFF)
        p.poly([(266, 1120), (334, 1120), (318, 1180), (282, 1180)], MUST_D, outline=INK, ow=5)


def gate(p, light):
    p.poly([(-OX, -OY), (W + OX, -OY), (W + OX, 760), (-OX, 760)], (233, 197, 164))
    sun(p, 872, 190, 64, (238, 138, 96))

    p.rect(-OX, 300, 620, 1268, (238, 219, 198), outline=INK, ow=8)
    for x in (150, 400):
        p.line([(x, 560), (x, 1260)], (206, 196, 182), 4)

    # the gate: a dark opening with a lit house beyond it
    p.rect(620, 420, 840, 1268, (62, 50, 42), outline=INK, ow=9)
    p.line([(620, 452), (840, 452)], INK, 8)
    p.rect(660, 760, 800, 1268, (78, 62, 50))
    p.rect(704, 800, 756, 860, LAMP, outline=INK, ow=4)
    p.ell(652, 420, 664, 1268, (96, 78, 62))

    p.rect(840, 300, W + OX, 1268, (232, 210, 186), outline=INK, ow=8)
    p.rect(900, 610, 1058, 780, (233, 197, 164), outline=INK, ow=6)
    p.line([(300, 372), (300, 452)], INK, 6)
    p.ell(258, 452, 342, 506, LAMP, outline=INK, ow=6)

    p.rect(-OX, 1268, W + OX, H + OY, (203, 163, 112))
    p.line([(-OX, 1268), (W + OX, 1268)], INK, 8)
    p.poly([(628, 1268), (832, 1268), (930, H + OY), (520, H + OY)], (191, 156, 120))
    for x, y, r in ((180, 1360, 9), (980, 1400, 8)):
        p.ell(x - r, y - r * 0.6, x + r, y + r * 0.6, (176, 142, 106))


def bake(idx):
    """Bake one shot's set at BAKE scale; returns (main, fg)."""
    e = SHOTS[idx]
    size = (int((W + 2 * OX) * BAKE), int((H + 2 * OY) * BAKE))
    main = Image.new("RGBA", size, PAPER)
    fg = Image.new("RGBA", size, (0, 0, 0, 0))
    p = Pen(main, BAKE, OX, OY)
    {"market": market, "yard": yard, "gate": gate}[e["scene"]](p, e["light"])
    f = Pen(fg, BAKE, OX, OY)
    if e["light"] == "night":
        glow(f, 300, 780, 470, LAMP, 52)
        glow(f, 300, 780, 200, LAMP, 34)
    if e["scene"] == "yard":
        # a near branch, kept in the top-right corner and out of type's way
        f.line([(1200, -20), (1040, 26), (930, 8)], INK_D, 14)
        for x, y, r in ((1046, 52, 30), (972, 74, 24), (900, 34, 22), (1128, -14, 26)):
            f.ell(x - r, y - r, x + r, y + r, INK_D)
    elif e["scene"] == "market":
        f.rect(-OX - 30, -OY, -60, 900, MUST_D, outline=INK, ow=8)
    else:
        f.rect(1064, 210, 1130, 1268, (214, 190, 166), outline=INK, ow=8)
    return main, fg


@functools.lru_cache(maxsize=1)
def baked(idx):
    return bake(idx)


def cam_at(e, u):
    z0, z1, x0, x1, y0, y1 = e["cam"]
    q = soft(u)
    return lerp(z0, z1, q), lerp(x0, x1, q), lerp(y0, y1, q)


def crop_layer(layer, z, cx, cy):
    cw, chh = W / z, H / z
    box = ((cx - cw / 2 + OX) * BAKE, (cy - chh / 2 + OY) * BAKE,
           (cx + cw / 2 + OX) * BAKE, (cy + chh / 2 + OY) * BAKE)
    return layer.crop(tuple(int(round(v)) for v in box)).resize((W, H), Image.BILINEAR)


# ------------------------------------------------------------------ people
def blink_at(name, t):
    seed = sum(ord(c) for c in name)
    period = 3.1 + (seed % 7) * 0.21
    ph = (t + (seed % 11) * 0.37) % period
    return ph < 0.095


@functools.lru_cache(maxsize=64)
def scaled(name, h):
    sp = sprite(name)
    k = h / sp.height
    return sp.resize((max(1, round(sp.width * k)), max(1, round(h))), Image.LANCZOS), k


def mouth_draw(work, name, k, m, eyes_closed):
    rig = SPRITES[FILES[name]]
    d = ImageDraw.Draw(work)
    lw = max(2, int(round(5 * k)))
    mx, my, hw, hh = rig["mouth"]
    cx, cy = mx * k, my * k
    hw, hh = hw * k, hh * k
    if m < 0.07:
        w = hw * 1.55
        d.line([(cx - w / 2, cy), (cx, cy + hh * 0.16), (cx + w / 2, cy)],
               fill=INK + (255,), width=lw, joint="curve")
    else:
        ow = hw * (1.48 + 0.26 * m)
        oh = hh * (0.58 + 2.10 * m)
        d.ellipse([cx - ow / 2, cy - oh * 0.46, cx + ow / 2, cy + oh * 0.66],
                  fill=(44, 27, 25, 255), outline=INK + (255,), width=lw)
        if m > 0.34:
            d.ellipse([cx - ow * 0.30, cy + oh * 0.10, cx + ow * 0.30, cy + oh * 0.54],
                      fill=(160, 68, 62, 255),
                      outline=None)
    if eyes_closed:
        skin = tuple(rig["skin"]) + (255,)
        for ex, ey, er in rig["eyes"]:
            ex, ey, er = ex * k, ey * k, er * k
            d.ellipse([ex - er * 1.25, ey - er * 1.15, ex + er * 1.25, ey + er * 1.35],
                      fill=skin)
            d.line([(ex - er * 1.15, ey + er * 0.15), (ex, ey - er * 0.30), (ex + er * 1.15, ey + er * 0.15)],
                   fill=INK + (255,), width=max(2, int(round(3.4 * k))))


def grade(work, light):
    """Put the puppet in the light it is standing in."""
    if light in ("morning", "noon"):
        return work
    k = (255, 216, 190) if light == "dusk" else (152, 136, 140)
    rgb = ImageChops.multiply(work.convert("RGB"), Image.new("RGB", work.size, k))
    out = rgb.convert("RGBA")
    out.putalpha(work.split()[3])
    return out


def actor(art, name, x, y, h, mouth=0.0, z=1.0, cam=None, t=0.0, drift=0.0, light="morning"):
    hh = h * z
    sp, k = scaled(name, hh)
    work = sp.copy()
    mouth_draw(work, name, k, mouth, blink_at(name, t))
    work = grade(work, light)
    sx = (x + drift - (cam[1] - W / (2 * cam[0]))) * cam[0]
    sy = (y - (cam[2] - H / (2 * cam[0]))) * cam[0]
    sw = int(work.width * 0.56)
    sh = max(8, int(work.height * 0.022))
    sh_img = Image.new("RGBA", (sw, sh * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh_img).ellipse([0, 0, sw - 1, sh * 2 - 1], fill=(0, 0, 0, 58))
    art.alpha_composite(sh_img, (int(round(sx - sw / 2)), int(round(sy - sh))))
    art.alpha_composite(work, (int(round(sx - work.width / 2)), int(round(sy - work.height))))


def being(art, e, t, cam):
    """Every visible character in this shot, breathing, swaying and (if speaking) talking."""
    z, cx, cy = cam
    u = clamp((t - e["t0"]) / max(1e-6, e["dur"]))
    mouth = 0.0
    if e["who"] and t >= e["t0"] - 0.02:
        env = envelope(e["clip"])
        i = int((t - e["t0"]) * FPS)
        if 0 <= i < len(env):
            mouth = env[i]
    for name, x, h, feet in e["acts"]:
        sway = math.sin(t * 0.62 + x * 0.013) * 4.2
        breath = 1.0 + 0.006 * math.sin(t * 1.45 + x * 0.01)
        bob = math.sin(t * 0.83 + x * 0.02) * 2.4 - 2.6 * (mouth if name == e["who"] else 0.0)
        m = mouth if name == e["who"] else 0.0
        actor(art, name, x, feet + bob, h * breath, mouth=m, z=z, cam=(z, cx, cy),
              t=t, drift=sway, light=e["light"])


# ------------------------------------------------------------------ cards
def paper_sheet(art, x, y, w, h, tilt=0.0, signed=False):
    layer = Image.new("RGBA", (int(w * 1.6), int(h * 1.6)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0 = layer.width * 0.2, layer.height * 0.2
    d.polygon([(x0, y0), (x0 + w, y0 - 10), (x0 + w, y0 + h - 10), (x0, y0 + h)],
              fill=OFF, outline=INK, width=6)
    for i in range(5):
        yy = y0 + h * 0.18 + i * h * 0.12
        d.line([(x0 + w * 0.10, yy), (x0 + w * (0.86 - 0.10 * (i % 2)), yy - 6)],
               fill=(178, 172, 160), width=5)
    if signed:
        d.ellipse([x0 + w * 0.62, y0 + h * 0.66, x0 + w * 0.74, y0 + h * 0.80],
                  fill=(196, 86, 64))
        d.line([(x0 + w * 0.58, y0 + h * 0.72), (x0 + w * 0.78, y0 + h * 0.71)],
               fill=INK, width=5)
    if tilt:
        layer = layer.rotate(tilt, resample=Image.BICUBIC)
    art.alpha_composite(layer, (int(x - layer.width * 0.2), int(y - layer.height * 0.2)))


def title_card(t):
    art = Image.new("RGBA", (W, H), INK)
    u = ease(clamp(t / 1.2))
    paper_sheet(art, 150, 420 - 40 * (1 - u), 780, 520, tilt=-1.6)
    # the thumbprint lands last, and hard
    v = clamp((t - 1.15) / 0.5)
    if v > 0:
        d = ImageDraw.Draw(art)
        r = 54 * (1.25 - 0.25 * ease(v))
        cx, cy = 700, 800
        a = int(255 * min(1.0, v * 2))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(196, 86, 64, a))
        d.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55],
                  fill=(240, 238, 230, a))
        d.ellipse([cx - r * 0.34, cy - r * 0.34, cx + r * 0.34, cy + r * 0.34],
                  fill=(196, 86, 64, a))
    deva.draw_text(art, (150, 1090), "শেষ কিস্তি", 118, 700, CREAM, anchor="lm")
    deva.draw_text(art, (154, 1200), "অন্ধকার পাঠ · ০৭", 40, 500, (176, 168, 156), anchor="lm")
    deva.draw_text(art, (154, 1290), "একটা ছোট মিথ্যা, একটা বড় দাম", 34, 500,
                   (214, 146, 116), anchor="lm")
    return art


def paper_card(t):
    art = Image.new("RGBA", (W, H), (28, 26, 24))
    u = ease(clamp(t / 1.0))
    paper_sheet(art, 120, 560, 840, 620, tilt=0.8)
    a = int(255 * clamp((t - 0.7) / 0.8))
    if a > 0:
        deva.draw_text(art, (540, 790), "আঙুলের ছাপ", 52, 700, (28, 26, 24), anchor="mm")
        deva.draw_text(art, (540, 880), "কলম দিয়ে আঁকা", 46, 500, (176, 74, 52), anchor="mm")
    return art


def end_card(t):
    art = Image.new("RGBA", (W, H), PAPER)
    d = ImageDraw.Draw(art)
    d.rectangle([0, 0, W, 26], fill=INK)
    d.rectangle([0, H - 26, W, H], fill=INK)
    u = clamp(t / 1.4)
    deva.draw_text(art, (90, 700), "কাগজ ভোলে না।", 86, 700, INK, anchor="lm")
    deva.draw_text(art, (92, 810), "যা লেখা হয়, তা থেকে যায়।", 44, 500, (120, 112, 100),
                   anchor="lm")
    a = clamp((t - 1.0) / 1.2)
    if a > 0:
        deva.draw_text(art, (92, 1000), "কেউ দেখেনি বলে কিছু হয় না, তা নয়।", 40, 500,
                       (176, 74, 52), anchor="lm")
    paper_sheet(art, 640, 1180, 320, 200, tilt=-3.0, signed=True)
    deva.draw_text(art, (92, 1760), "অন্ধকার পাঠ · ০৭", 30, 500, (150, 142, 130), anchor="lm")
    return art


# ------------------------------------------------------------------ caption band
@functools.lru_cache(maxsize=64)
def wrap(text, size, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        try:
            width = deva.layout(trial, size)[1]
        except Exception:
            width = len(trial) * size * 0.55
        if width > maxw and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return tuple(lines)


def caption(art, e):
    d = ImageDraw.Draw(art)
    d.rectangle([0, 1592, W, H], fill=PAPER)
    d.line([(0, 1592), (W, 1592)], fill=INK, width=6)
    lab = LABEL[e["who"]]
    lw = deva.layout(lab, 30)[1]
    d.rectangle([74, 1636, 74 + lw + 34, 1692], fill=RED)
    deva.draw_text(art, (92, 1666), lab, 30, 700, CREAM, anchor="lm")
    cap_w = deva.layout(e["cap"], 28)[1]
    deva.draw_text(art, (W - 76 - cap_w, 1662), e["cap"], 28, 500, (128, 120, 108),
                   anchor="lm")
    lines = wrap(e["text"], 35, 918)
    y = 1742 if len(lines) < 3 else 1730
    for ln in lines[:3]:
        deva.draw_text(art, (74, y), ln, 35, 500, (32, 29, 26), anchor="lm")
        y += 48


def header(art, e):
    dark = e["light"] == "night"
    deva.draw_text(art, (74, 84), "অন্ধকার পাঠ · ০৭", 26, 500,
                   (188, 178, 164) if dark else (120, 112, 100), anchor="lm")


# ------------------------------------------------------------------ frame
def frame(t):
    if t < LEAD:
        return title_card(t)
    if t >= CARD_A:
        return end_card(t - CARD_A)
    if t >= PAPER_A:
        return paper_card(t - PAPER_A)

    e = shot_at(t)
    u = clamp((t - e["t0"]) / max(1e-6, e["dur"]))
    cam = cam_at(e, u)
    main, fg = baked(e["idx"])
    art = crop_layer(main, *cam)
    being(art, e, t, cam)
    art.alpha_composite(crop_layer(fg, *cam))
    caption(art, e)
    header(art, e)
    return art


def render(still=None, seg=None, out=None):
    n = int(round(TOTAL * FPS))
    print("timeline %.2fs · %d frames · %d lines" % (TOTAL, n, len(ENTRIES)), flush=True)
    if still is not None:
        path = out or "frames/still.png"
        frame(float(still)).convert("RGB").save(path)
        print("wrote", path)
        return
    a, b = seg if seg else (0, n)
    out = out or "dark-lesson-07-last-instalment-1080x1920.mp4"
    ff = subprocess.Popen(
        [FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-g", "48", out], stdin=subprocess.PIPE)
    for i in range(a, b):
        ff.stdin.write(frame(i / FPS).convert("RGB").tobytes())
        if i % 120 == 0:
            print("  %d/%d  %.1fs" % (i - a, b - a, i / FPS), flush=True)
    ff.stdin.close()
    ff.wait()
    print("wrote", out)


if __name__ == "__main__":
    args = sys.argv[1:]
    still = seg = out = None
    if "--still" in args:
        still = float(args[args.index("--still") + 1])
    if "--seg" in args:
        i = args.index("--seg")
        seg = (int(args[i + 1]), int(args[i + 2]))
    if "--out" in args:
        out = args[args.index("--out") + 1]
    render(still=still, seg=seg, out=out)
