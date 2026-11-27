"""film9.py — অন্ধকার পাঠ ০৮ · জামিন (the surety). 1080x1920, 24 fps, Bangla.

One lane, one hour, ten turns and five voices. A wedding the bride did not choose, paid
for by a loan nobody can repay; an elder whose thumbprint is on the guarantee; a
moneylender who would rather the paper stayed on the wall than in his pocket.

Timing, for the whole film, comes from one clock: frame i is t = i / FPS, and the shot,
the camera, the mouth, the caption and the mix are all read off that same t. Nothing is
animated against a separate counter, so picture and sound cannot drift.
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
OX, OY = 170, 150
BAKE = 1.4

PAPER = (240, 238, 230)
PAPER_D = (224, 219, 208)
PAPER_M = (205, 199, 187)
INK = (26, 23, 20)
INK_S = (98, 92, 84)
INK_D = (14, 13, 12)
MUST = (201, 154, 46)
MUST_D = (163, 120, 33)
MUST_L = (228, 193, 106)
CORAL = (217, 119, 87)
CORAL_D = (176, 86, 60)
OFF = (250, 247, 240)
SAND = (216, 181, 121)
SAND_D = (192, 154, 94)
OLIVE = (112, 124, 74)
CREAM = (245, 241, 231)
RED = (172, 72, 50)

LABEL = {"elder": "মোড়ল", "shopkeeper": "দোকানদার", "moneylender": "মহাজন",
         "postman": "ডাকপিয়ন", "widow": "বিধবা", "bride": "নববধূ"}


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


class Pen:
    def __init__(self, img, ss=1.0, ox=0.0, oy=0.0):
        self.img, self.ss, self.ox, self.oy = img, ss, ox, oy
        self.d = ImageDraw.Draw(img)

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
# one hour, late afternoon: the light never changes, only the camera and the people
SHOTS = [
    dict(clip=1, who="shopkeeper", scene="stall", cap="দোকানের সামনে",
         acts=[("shopkeeper", 720, 986, 1262), ("elder", 300, 962, 1262)], bg=[],
         cam=(1.00, 1.05, 540, 528, 930, 946), pre=0.0),
    dict(clip=2, who="elder", scene="stall", cap="দোকানের সামনে",
         acts=[("elder", 540, 1000, 1262)], bg=[],
         cam=(1.06, 1.12, 534, 546, 949, 966), pre=0.9),
    dict(clip=3, who="moneylender", scene="lane", cap="উঠোনের গেট",
         acts=[("moneylender", 700, 1000, 1262), ("elder", 246, 958, 1262)], bg=[("tailor", 112, 786, 1258)],
         cam=(1.06, 1.00, 560, 528, 949, 930), pre=1.2),
    dict(clip=4, who="postman", scene="lane", cap="শামিয়ানার নিচে",
         acts=[("postman", 530, 1000, 1262)], bg=[("student", 124, 760, 1258), ("boatman", 940, 780, 1258)],
         cam=(1.02, 1.09, 520, 538, 937, 957), pre=1.0),
    dict(clip=5, who="widow", scene="lane", cap="শামিয়ানার নিচে",
         acts=[("widow", 560, 1000, 1262)], bg=[("bride", 186, 800, 1258)],
         cam=(1.08, 1.02, 545, 528, 955, 937), pre=0.9),
    dict(clip=6, who="shopkeeper", scene="stall", cap="দোকানের সামনে",
         acts=[("shopkeeper", 528, 1008, 1262)], bg=[("elder", 892, 796, 1258)],
         cam=(1.03, 1.10, 540, 552, 940, 960), pre=1.1),
    dict(clip=7, who="elder", scene="stall", cap="দোকানের সামনে",
         acts=[("elder", 520, 1000, 1262)], bg=[],
         cam=(1.06, 1.00, 528, 540, 949, 930), pre=0.9),
    dict(clip=8, who="moneylender", scene="lane", cap="গেটের পাশে",
         acts=[("moneylender", 540, 1008, 1262)], bg=[("teacher", 138, 790, 1258)],
         cam=(1.05, 1.11, 540, 550, 946, 963), pre=1.1),
    dict(clip=9, who="widow", scene="lane", cap="বিয়ের ঘর",
         acts=[("widow", 372, 956, 1262), ("bride", 776, 1000, 1262)], bg=[],
         cam=(1.02, 1.08, 560, 546, 937, 955), pre=1.0),
    dict(clip=10, who="elder", scene="lane", cap="বিয়ের ঘর",
         acts=[("elder", 512, 1000, 1262)], bg=[("bride", 872, 800, 1258)],
         cam=(1.03, 1.10, 530, 544, 940, 960), pre=1.1),
]

TEXT = {
    1: "মোড়ল মশাই, চাল-ডাল সব পাঠিয়ে দিয়েছি। টাকাটা তো এখনও দেখছি না। বলেছিলেন বিয়ের পরে দেবেন, কিন্তু বিয়েটাই এখন প্রশ্নের মুখে।",
    2: "টাকা যাবে না, ভাই। আমি নিজে জামিন হয়ে দাঁড়িয়েছি। আমার মুখে ভরসা রাখো, এই পাড়ায় আমি চারশো বিয়ে দেখেছি, একটাও ভাঙিনি।",
    3: "জামিনের কাগজে আপনার আঙুলের ছাপ আছে, মোড়ল মশাই। টাকাটা আমার ঘর থেকে গেছে, ফিরছে না। আজ রাতের মধ্যে না হলে, বিয়ের পরে আমার লোক বাড়িটা দেখতে আসবে।",
    4: "একটা চিঠি এসেছে, বরের বাড়ি থেকে। ওরা লিখেছে, বিয়ের সব খরচ মেয়ের পক্ষে, নইলে ছেলে দেখতে আসবে না। মানে, ওরা সব জেনে গেছে।",
    5: "আমি এই মেয়ের মাকে চিনতাম। ও বিয়ের দিন নিজের সোনা বিক্রি করেছিল, শুধু যেন লোকে না বলে মেয়ে খালি হাতে গেছে। আজ ওর মেয়েও সেই একই দাম দিচ্ছে।",
    6: "আমি আমার বিলটা ছিঁড়ে ফেললাম। যেটা যাবে, যাক। কিন্তু মোড়ল মশাই, কাগজে আপনার ছাপটা তো রয়ে গেল।",
    7: "দুশো টাকা দিয়েছিল, শুধু ছাপটা দিতে। আমি ভেবেছিলাম, কাগজটা কেউ দেখবে না। আজ সারা পাড়া দেখছে।",
    8: "দোষ কাগজের না। কাগজ শুধু জবাব দেয়। আপনার ছাপ, আপনার দায়। কাগজটা আমি নিচ্ছি না, ওই দেয়ালে টানানো থাকুক। যেদিন টাকা আসবে, সেদিন নামাব।",
    9: "তুই কারও কাছে কিছু চাস না, মা। আজ তুই শুধু ঠিক করে বল, তুই যেতে চাস কি না। বাকিটা আমরা দেখছি।",
    10: "তাহলে বিয়েটা আজ বন্ধ। আমার মুখ পাড়ায় থাকবে না, কিন্তু মেয়েটা বেঁচে যাবে। মা, তুই ভিতরে যা। তোর মায়ের নামে এটা আমি লিখে রাখলাম।",
}

LEAD = 3.0
TAIL_PAPER = 3.5
TAIL_CARD = 3.5


def _dur(path):
    err = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", err)
    if not m:
        return 9.0
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
    r = np.clip(r / top * 1.45, 0, 1) ** 0.72
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
PAPER_A = LAST_END + 0.5
CARD_A = PAPER_A + TAIL_PAPER
TOTAL = CARD_A + TAIL_CARD

RIGS = json.load(open(os.path.join(CAST, "rigs8.json")))


def shot_at(t):
    for e in ENTRIES:
        if e["t0"] - 0.20 <= t < e["t0"] + e["dur"] + 0.30:
            return e
    return ENTRIES[0] if t < LEAD else ENTRIES[-1]


@functools.lru_cache(maxsize=24)
def sprite(name):
    return Image.open(os.path.join(CAST, name + ".png")).convert("RGBA")


@functools.lru_cache(maxsize=24)
def rigged(name):
    return Image.open(os.path.join(CAST, name + "-rig.png")).convert("RGBA")


# ------------------------------------------------------------------ sets
def stalls(p):
    p.rect(-OX, -OY, W + OX, 1258, CREAM)

    # corrugated shutter, half up, dark inside
    p.rect(360, 430, 780, 1258, (58, 50, 44), outline=INK, ow=8)
    for x in range(380, 780, 26):
        p.line([(x, 430), (x, 900)], (78, 68, 58), 4)
    p.rect(360, 380, 780, 440, MUST_D, outline=INK, ow=7)
    for x in range(376, 780, 24):
        p.line([(x, 392), (x, 428)], INK_S, 3)

    # counter with sacks and jars
    p.rect(-OX, 940, 470, 1004, MUST_D, outline=INK, ow=6)
    p.rect(-OX, 1004, -40, 1258, MUST_D, outline=INK, ow=6)
    p.rect(420, 1004, 470, 1258, MUST_D, outline=INK, ow=6)
    for x, r in ((-120, 58), (-20, 50), (250, 46)):
        p.ell(x - r, 940 - 1.7 * r, x + r, 940, MUST, outline=INK, ow=5)
        p.line([(x - r * 0.4, 940 - 1.4 * r), (x + r * 0.3, 940 - 1.1 * r)], INK_S, 3)
    for x in (120, 190, 300):
        p.rect(x, 862, x + 58, 940, OFF, outline=INK, ow=4)
        p.rect(x + 8, 872, x + 50, 900, PAPER_M, outline=INK, ow=2)
    for x in (560, 640, 720):
        p.rect(x, 470, x + 52, 560, CORAL, outline=INK, ow=4)
        p.line([(x + 26, 470), (x + 26, 452)], INK, 3)

    p.rect(-OX, 1258, W + OX, H + OY, SAND)
    p.line([(-OX, 1258), (W + OX, 1258)], INK, 8)
    for x, y, r in ((180, 1360, 8), (700, 1420, 10), (940, 1330, 7)):
        p.ell(x - r, y - r * 0.6, x + r, y + r * 0.6, SAND_D)


def lane(p):
    p.poly([(-OX, -OY), (W + OX, -OY), (W + OX, 1258), (-OX, 1258)], PAPER_D)
    p.rect(-OX, 210, W + OX, 1258, CREAM, outline=INK, ow=7)

    # the bride's gate, left: two leaves of planking, a lintel, a latch
    p.rect(56, 440, 384, 1258, MUST_D, outline=INK, ow=9)
    p.rect(56, 440, 384, 500, MUST, outline=INK, ow=7)
    for leaf, x0 in ((0, 66), (1, 226)):
        p.rect(x0, 500, x0 + 148, 1258, MUST, outline=INK, ow=6)
        for i in range(1, 4):
            p.line([(x0 + i * 37, 500), (x0 + i * 37, 1258)], MUST_D, 3)
        p.line([(x0 + 12, 720), (x0 + 136, 720)], INK_D, 4)
        p.line([(x0 + 12, 1010), (x0 + 136, 1010)], INK_D, 4)
    p.rect(196, 830, 250, 866, INK_D)
    p.rect(206, 836, 240, 860, MUST_D)
    # a step of brick at the sill
    p.rect(40, 1258, 400, 1290, SAND_D, outline=INK, ow=4)
    # a shuttered window, right
    p.rect(830, 520, 1010, 700, PAPER_M, outline=INK, ow=6)
    for i in range(1, 3):
        p.line([(830 + i * 60, 520), (830 + i * 60, 700)], INK, 4)
    # the nail, and the paper it carries: the guarantee deed, on the wall for all to see
    p.ell(946, 760, 958, 772, INK)
    p.poly([(908, 774), (996, 766), (1000, 900), (912, 906)], OFF, outline=INK, ow=4)
    for i in range(4):
        y = 800 + i * 26
        p.line([(922, y), (986 - (i % 2) * 14, y - 2)], (176, 170, 158), 3)
    p.line([(934, 884), (958, 880)], (196, 86, 64), 5)

    # shamiana: cloth overhead, scalloped, with poles
    p.poly([(-OX, -OY), (W + OX, -OY), (W + OX, 250), (-OX, 250)], CORAL)
    for i in range(7):
        x = -170 + i * 182
        p.poly([(x, -OY), (x + 88, -OY), (x + 96, 250), (x + 8, 250)], OFF)
    p.poly([(-OX, 250), (W + OX, 250), (W + OX, 300), (-OX, 300)], CORAL_D)
    for i in range(11):
        x = -170 + i * 122
        p.ell(x, 300, x + 122, 360, CORAL_D, outline=INK, ow=3)
    p.rect(72, -OY, 108, 1258, MUST_D, outline=INK, ow=6)
    p.rect(972, -OY, 1008, 1258, MUST_D, outline=INK, ow=6)

    # garlands
    for gx in (250, 760):
        p.line([(gx, 300), (gx, 640)], INK_S, 3)
        for i in range(9):
            y = 320 + i * 36
            p.ell(gx - 13, y, gx + 13, y + 26, CORAL, outline=INK, ow=2)

    # chairs stacked for the guests who are not sitting down
    for i in range(3):
        y0 = 1060 - i * 64
        p.rect(586, y0, 700, y0 + 18, MUST_D, outline=INK, ow=4)          # seat
        p.rect(586, y0 - 58, 700, y0 - 50, MUST_D, outline=INK, ow=4)     # back rail
        p.rect(586, y0 - 58, 596, y0 + 18, MUST_D, outline=INK, ow=4)     # back post
        p.rect(690, y0 - 58, 700, y0 + 18, MUST_D, outline=INK, ow=4)
        for dx in (596, 682):
            p.line([(dx, y0 + 6), (dx, y0 + 34)], MUST_D, 4)

    p.rect(-OX, 1258, W + OX, H + OY, SAND)
    p.line([(-OX, 1258), (W + OX, 1258)], INK, 8)
    p.poly([(320, 1258), (840, 1258), (886, H + OY), (274, H + OY)], (233, 222, 201))
    p.line([(320, 1258), (840, 1258)], INK, 4)


def bake(idx):
    e = SHOTS[idx]
    size = (int((W + 2 * OX) * BAKE), int((H + 2 * OY) * BAKE))
    main = Image.new("RGBA", size, PAPER)
    fg = Image.new("RGBA", size, (0, 0, 0, 0))
    p = Pen(main, BAKE, OX, OY)
    (stalls if e["scene"] == "stall" else lane)(p)
    f = Pen(fg, BAKE, OX, OY)
    if e["scene"] == "lane":
        # a near garland strand, in front of everyone
        f.line([(1090, 60), (1060, 360), (1074, 620)], INK_S, 5)
        for i in range(5):
            y = 150 + i * 104
            f.ell(1042, y, 1076, y + 44, CORAL, outline=INK, ow=3)
    else:
        f.rect(-OX, -OY, -70, 1000, MUST_D, outline=INK, ow=8)
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
    return ((t + (seed % 11) * 0.37) % (3.1 + (seed % 7) * 0.21)) < 0.095


@functools.lru_cache(maxsize=96)
def scaled(name, h, rigged_ok=True):
    sp = rigged(name) if rigged_ok else sprite(name)
    k = h / sp.height
    return sp.resize((max(1, round(sp.width * k)), max(1, round(h))), Image.LANCZOS), k


def mouth_draw(work, name, k, m, eyes_closed):
    rig = RIGS[name]
    d = ImageDraw.Draw(work)
    lw = max(2, int(round(4.4 * k)))
    mx, my, hw, hh = rig["mouth"]
    cx, cy = mx * k, my * k
    hw, hh = hw * k, hh * k
    if m < 0.07:
        w = hw * 1.55
        d.line([(cx - w / 2, cy), (cx, cy + hh * 0.22), (cx + w / 2, cy)],
               fill=INK + (255,), width=lw, joint="curve")
    else:
        ow = hw * (1.52 + 0.42 * m)
        oh = max(ow * 0.52, hh * 1.2) * (0.55 + 0.45 * m)
        t0 = cy + hh * 0.55
        d.ellipse([cx - ow / 2, t0, cx + ow / 2, t0 + oh],
                  fill=(52, 30, 28, 255), outline=INK + (255,), width=max(2, int(lw * 0.72)))
        if m > 0.42:
            d.ellipse([cx - ow * 0.22, t0 + oh * 0.52, cx + ow * 0.22, t0 + oh * 0.94],
                      fill=(138, 58, 54, 255))
    if eyes_closed:
        for ex, ey, er in rig["eyes"]:
            ex, ey, er = ex * k, ey * k, er * k
            patch = Image.new("RGBA", (int(er * 4), int(er * 4)), (0, 0, 0, 0))
            pd = ImageDraw.Draw(patch)
            sample = work.crop((int(ex - er * 1.4), int(ey - er * 2.2),
                                int(ex + er * 1.4), int(ey - er * 0.6)))
            if sample.width > 2 and sample.height > 2:
                patch.paste(sample.resize((patch.width, patch.height), Image.BILINEAR), (0, 0))
                work.paste(patch, (int(ex - er * 2), int(ey - er * 2)), patch)
            d.line([(ex - er * 1.2, ey + er * 0.2), (ex + er * 1.2, ey + er * 0.2)],
                   fill=INK + (255,), width=max(2, int(round(3.2 * k))))


def grade(work):
    """One hour of light: everything sits in the same warm afternoon."""
    return work


def actor(art, name, x, feet, h, mouth=0.0, cam=None, t=0.0, sway=0.0, alive=True):
    z, cx, cy = cam
    hh = h * z
    sp, k = scaled(name, hh, alive)
    work = sp.copy()
    if alive:
        mouth_draw(work, name, k, mouth, blink_at(name, t))
    work = grade(work)
    sx = (x + sway - (cx - W / (2 * z))) * z
    sy = (feet - (cy - H / (2 * z))) * z
    sw = int(work.width * 0.58)
    sh = max(8, int(work.height * 0.020))
    shadow = Image.new("RGBA", (sw, sh * 2), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([0, 0, sw - 1, sh * 2 - 1], fill=(0, 0, 0, 52))
    art.alpha_composite(shadow, (int(sx - sw / 2), int(sy - sh)))
    art.alpha_composite(work, (int(sx - work.width / 2), int(sy - work.height)))
    return sx, sy


def neither(art, e, t, cam):
    """Silent neighbours: they breathe, they do not talk. They are the reason it is a street."""
    for name, x, h, feet in e.get("bg", []):
        sway = math.sin(t * 0.5 + x * 0.01) * 2.4
        actor(art, name, x, feet + math.sin(t * 0.7 + x) * 1.6, h, 0.0, cam, t, sway, alive=False)


def being(art, e, t, cam):
    z, cx, cy = cam
    mouth = 0.0
    if t >= e["t0"] - 0.02:
        env = envelope(e["clip"])
        i = int((t - e["t0"]) * FPS)
        if 0 <= i < len(env):
            mouth = env[i]
    neither(art, e, t, cam)
    for name, x, h, feet in e["acts"]:
        m = mouth if name == e["who"] else 0.0
        sway = math.sin(t * 0.55 + x * 0.013) * 3.6
        breath = 1.0 + 0.006 * math.sin(t * 1.4 + x * 0.01)
        bob = math.sin(t * 0.8 + x * 0.02) * 2.2 - 2.4 * m
        actor(art, name, x, feet + bob, h * breath, m, cam, t, sway, alive=True)


# ------------------------------------------------------------------ cards
def thumb(d, cx, cy, r, seed=0):
    """A finger pressed in ink: rings that do not quite agree with each other."""
    j = [(0.0, 0.0), (1.3, -1.1), (-1.1, 1.4), (0.7, 1.0)]
    a = [(1.0, 0.92), (0.74, 0.70), (0.48, 0.46), (0.22, 0.21)]
    for i in range(4):
        dx, dy = j[i]
        rx, ry = a[i]
        d.ellipse([cx - r * rx + dx, cy - r * ry + dy,
                   cx + r * rx + dx, cy + r * ry + dy],
                  outline=(176 + i * 6, 74))if False else None
    for i in range(4):
        dx, dy = j[i]
        rx, ry = a[i]
        d.ellipse([cx - r * rx + dx, cy - r * ry + dy,
                   cx + r * rx + dx, cy + r * ry + dy],
                  outline=(178, 76, 58, 235), width=max(2, int(r * 0.16)))


def paper_sheet(art, x, y, w, h, tilt=0.0, print_r=0.0, pin=False):
    layer = Image.new("RGBA", (int(w * 1.7), int(h * 1.7)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0 = layer.width * 0.2, layer.height * 0.2
    d.polygon([(x0, y0), (x0 + w, y0 - 8), (x0 + w, y0 + h - 8), (x0, y0 + h)],
              fill=OFF, outline=INK, width=6)
    for i in range(4):
        yy = y0 + h * 0.13 + i * h * 0.075
        d.line([(x0 + w * 0.09, yy), (x0 + w * (0.9 - 0.11 * (i % 2)), yy - 5)],
               fill=(176, 170, 158), width=4)
    if print_r > 0:
        cx, cy = x0 + w * 0.64, y0 + h * 0.74
        thumb(d, cx, cy, w * 0.062 * print_r)
    if pin:
        d.ellipse([x0 + w * 0.48, y0 - 12, x0 + w * 0.52, y0 - 2], fill=INK)
    if tilt:
        layer = layer.rotate(tilt, resample=Image.BICUBIC)
    art.alpha_composite(layer, (int(x - layer.width * 0.2), int(y - layer.height * 0.2)))


def title_card(t):
    art = Image.new("RGBA", (W, H), (24, 22, 20))
    u = ease(clamp(t / 1.1))
    paper_sheet(art, 150, 470 - 40 * (1 - u), 780, 540, tilt=-1.4)
    v = clamp((t - 1.0) / 0.5)
    if v > 0:
        d = ImageDraw.Draw(art)
        r = 52 * (1.22 - 0.22 * ease(v))
        a = int(255 * min(1.0, v * 2))
        cx, cy = 742, 822
        lay = Image.new("RGBA", (int(r * 3), int(r * 3)), (0, 0, 0, 0))
        thumb(ImageDraw.Draw(lay), lay.width / 2, lay.height / 2, r)
        art.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))
    deva.draw_text(art, (150, 1150), "জামিন", 128, 700, CREAM, anchor="lm")
    deva.draw_text(art, (154, 1260), "অন্ধকার পাঠ · ০৮", 40, 500, (176, 168, 156), anchor="lm")
    deva.draw_text(art, (154, 1346), "যে বিয়েতে কেউ মেয়েটাকে জিজ্ঞেস করেনি", 34, 500,
                   (214, 146, 116), anchor="lm")
    d = ImageDraw.Draw(art)
    d.line([(154, 1660), (560, 1660)], fill=(72, 66, 60), width=2)
    deva.draw_text(art, (154, 1704), "এক বিকেল · এক পাড়া · একটা কাগজ", 30, 500,
                   (150, 142, 132), anchor="lm")
    return art


def paper_card(t):
    art = Image.new("RGBA", (W, H), (26, 24, 22))
    paper_sheet(art, 120, 500, 840, 700, tilt=0.9, print_r=ease(clamp(t / 1.2)), pin=True)
    if t > 0.8:
        deva.draw_text(art, (540, 812), "জামিননামা", 54, 700, (28, 26, 24), anchor="mm")
        deva.draw_text(art, (540, 884), "আঙুলের ছাপ — মোড়ল", 36, 500, (176, 74, 52),
                       anchor="mm")
        deva.draw_text(art, (540, 942), "দুশো টাকা · ফিরবে কি, ফিরবে না", 30, 500,
                       (128, 120, 108), anchor="mm")
    if t > 1.3:
        deva.draw_text(art, (540, 1436), "কাগজটা কার, সেটা কাগজ জানে না।", 32, 500,
                       (150, 142, 130), anchor="mm")
    return art


def end_card(t):
    art = Image.new("RGBA", (W, H), PAPER)
    d = ImageDraw.Draw(art)
    d.rectangle([0, 0, W, 24], fill=INK)
    d.rectangle([0, H - 24, W, H], fill=INK)
    deva.draw_text(art, (90, 780), "বিয়েটা বন্ধ হলো।", 84, 700, INK, anchor="lm")
    deva.draw_text(art, (92, 890), "মেয়েটা বেঁচে গেল। নাকি শুধু কালকের জন্য?", 42, 500,
                   (120, 112, 100), anchor="lm")
    if t > 0.9:
        deva.draw_text(art, (92, 1050), "কাগজে একটা ছাপ, ঘরে একটা নাম।", 40, 500, (176, 74, 52),
                       anchor="lm")
    paper_sheet(art, 596, 1240, 380, 250, tilt=-3.2, print_r=1.0, pin=True)
    deva.draw_text(art, (92, 1758), "অন্ধকার পাঠ · ০৮", 30, 500, (150, 142, 130), anchor="lm")
    return art


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
    d.rectangle([0, 1596, W, H], fill=PAPER)
    d.line([(0, 1596), (W, 1596)], fill=INK, width=6)
    lab = LABEL[e["who"]]
    lw = deva.layout(lab, 30)[1]
    d.rectangle([74, 1638, 74 + lw + 34, 1694], fill=RED)
    deva.draw_text(art, (92, 1668), lab, 30, 700, CREAM, anchor="lm")
    cap_w = deva.layout(e["cap"], 28)[1]
    deva.draw_text(art, (W - 76 - cap_w, 1664), e["cap"], 28, 500, (128, 120, 108), anchor="lm")
    lines = wrap(e["text"], 35, 918)
    y = 1746 if len(lines) < 3 else 1732
    for ln in lines[:3]:
        deva.draw_text(art, (74, y), ln, 35, 500, (32, 29, 26), anchor="lm")
        y += 48


def header(art):
    d = ImageDraw.Draw(art)
    pill = Image.new("RGBA", (344, 62), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([0, 0, 343, 61], 31, fill=PAPER + (232,))
    art.alpha_composite(pill, (56, 52))
    deva.draw_text(art, (78, 84), "অন্ধকার পাঠ · ০৮", 26, 600, (74, 68, 62), anchor="lm")


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
    header(art)
    return art


def render(still=None, seg=None, out=None):
    n = int(round(TOTAL * FPS))
    print("timeline %.2fs · %d frames · %d turns" % (TOTAL, n, len(ENTRIES)), flush=True)
    if still is not None:
        path = out or "frames/s.png"
        frame(float(still)).convert("RGB").save(path)
        print("wrote", path)
        return
    a, b = seg if seg else (0, n)
    out = out or "dark-lesson-08-wedding-1080x1920.mp4"
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
    os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
    render(still=still, seg=seg, out=out)
