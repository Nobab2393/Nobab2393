"""film3.py — অন্ধকার পাঠ ০৩ · কেনা সম্মান (Bought Respect)

A code-drawn flat-vector short: 1080x1920, 24 fps, Bangla voice-over + Bangla on-screen text.

The colour rule carries the whole story:
    PAPER + INK everywhere. GOLD means exactly one thing — respect that was bought — and it
    is present in every scene until the flood. After the flood there is no gold left in the
    film at all. BLUE appears once: the glass of water given away for nothing.

    python3 film3.py --still 40
    python3 film3.py --seg 0 1300 --out seg-0.mp4
"""
import argparse
import functools
import math
import os
import re
import subprocess

from PIL import Image, ImageDraw

import deva
from fig3 import (BLUE, GOLD, GOLD_D, GOLD_L, INK, INK_D, INK_S, PAPER, PAPER_D,
                  PAPER_M, P, back, clamp, coin, ease, glass, lerp, medal, mic,
                  person, soft, steam)

W, H = 1080, 1920
SS = 1.25                      # supersample 1350x2400 -> 1080x1920
FPS = 24
GY = 1500                      # every body stands on this line
TYPE_Y = 210                   # meta line
CAP_Y = 312                    # the one-word caption
SUB_Y = 1742                   # subtitles never go higher than this

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "audio")

try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:                                            # pragma: no cover
    FF = "ffmpeg"


# ---------------------------------------------------------------- text
def T(base, xy, text, size, col, weight=700, anchor="lm"):
    deva.draw_text(base, xy, text, size, weight, col, anchor=anchor)


@functools.lru_cache(maxsize=600)
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


# ---------------------------------------------------------------- script
# One clip = one recording. Some clips carry two lines: they are the same voice in the
# same shot, and the subtitle splits itself across the take (see build_timeline).
CLIPS = [
    ("stall", [("narr", "গ্রামে রহিমকে সবাই সালাম দিত। কারণ চায়ের দোকানে সবার বিল রহিমই দিত।")]),
    ("stall", [("narr", "রহিম ভাবত — টাকা থাকলে সম্মানও থাকে।")]),
    ("stall", [("rahim", "খাও, খাও। আজ সবটাই আমার। দেখো, টাকায় সম্মান কেনা যায়।")]),
    ("stall", [("narr", "সালামের শব্দে পুরো দোকানটা ভরে যেত।")]),
    ("stage", [("narr", "তারপর সে আরও কিনল। সোনার মেডেল, মঞ্চ, আর মাইকে নিজের নাম।")]),
    ("stage", [("rahim", "এই গ্রামে যা কিছু ভালো, সব আমার টাকায়।")]),
    ("stage", [("narr", "হাততালি পড়ত ঠিক তখনই — যখন টাকার শব্দ হতো।")]),
    ("stage", [("rahim", "সবাই আমার নাম জানে। তুমি জানো না কেন?")]),
    ("oldman", [("narr", "শুধু একজন ছিল, যে তাঁর টাকা নিত না।")]),
    ("oldman", [("old", "আমি কারও টাকা নিই না। তাই কাউকে সালামও দিই না।")]),
    ("oldman", [("rahim", "আমার টাকায় পুরো গ্রাম চলে — তুমি কে?")]),
    ("oldman", [("old", "আমি সেই লোক, যে তোমার টাকা ছাড়াও বাঁচতে পারে।")]),
    ("flood", [("narr", "বর্ষায় নদী ফুলে উঠল। বাঁধ ভাঙল, আর রহিমের গুদাম ডুবে গেল।"),
               ("narr", "যে টাকা সম্মান কিনে এনেছিল, সেই টাকাই ভেসে গেল।")]),
    ("morning", [("narr", "সকালে সে চায়ের দোকানে গেল। কেউ সালাম দিল না।"),
                 ("narr", "কেউ বলল — ও এখন আমাদের মতোই।")]),
    ("morning", [("rahim", "…কেউ নেই?")]),
    ("water", [("narr", "তখন একজন এল। যে কখনো তাঁর টাকা নেয়নি।")]),
    ("water", [("old", "পানি খাবে?")]),
    ("water", [("rahim", "তুমি… কেন?")]),
    ("water", [("old", "সম্মান তো আমি বিক্রি করি না।")]),
    ("end", [("narr", "সম্মান কিনেছিলে, তাই ভাড়াটে ছিল। ভাড়া শেষ — সম্মানও শেষ।"),
             ("narr", "আর যে একটা গ্লাস পানি দিল, সে কিছুই বিক্রি করেনি।")]),
]

CAPTION = {"stall": "সালাম", "stage": "দাম", "oldman": "একজন বাদে",
           "flood": "ভাঙন", "morning": "সকাল", "water": "এক গ্লাস", "end": ""}
DARK = {"flood", "morning", "water", "end"}

OVERLAY = {
    "stage": [(540, 636, "রহিম", 74, INK, 700, "mm")],
}

LEAD = 2.4
TAIL = 6.6
GAP = 0.36


def _dur(path):
    if not os.path.exists(path):
        return None
    out = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if not m:
        return None
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def build_timeline():
    """Lay the clips out back to back. Returns (line entries, total, ...).

    Lines inside one clip share its measured duration in proportion to their length, so
    the subtitle turns over roughly where the reader expects it.
    """
    t, entries, ci = LEAD, [], 0
    for scene, lines in CLIPS:
        vo = os.path.join(AUD, "s%02d.mp3" % (ci + 1))
        d = _dur(vo)
        if d is None:
            d = 0.45 + sum(len(x[1]) for x in lines) / 15.5
            vo = None
        total_chars = sum(len(x[1]) for x in lines)
        acc = 0.0
        for j, (spk, text) in enumerate(lines):
            share = len(text) / total_chars
            entries.append({"i": len(entries), "scene": scene, "spk": spk, "text": text,
                            "t0": t + d * acc, "dur": d * share,
                            "vo": vo if j == 0 else None,
                            "vo_t0": t if j == 0 else None,
                            "clip": ci + 1})
            acc += share
        t += d + GAP
        ci += 1
    return entries, t - GAP + TAIL


def scene_spans(entries, total):
    spans, order = {}, []
    for e in entries:
        sc = e["scene"]
        if sc not in spans:
            spans[sc] = [e["t0"], e["t0"] + e["dur"]]
            order.append(sc)
        else:
            spans[sc][1] = e["t0"] + e["dur"]
    # a scene runs until the next one starts, not until its last line ends
    for i, sc in enumerate(order):
        if i + 1 < len(order):
            spans[sc][1] = max(spans[sc][1], spans[order[i + 1]][0])
    for sc in order:
        spans[sc][1] += GAP
    return {k: (a, b) for k, (a, b) in spans.items()}, order


# ---------------------------------------------------------------- sets
def band(p, y, col):
    p.poly([(-40, y), (W + 40, y), (W + 40, H + 60), (-40, H + 60)], col)


def sky(p, col):
    p.poly([(-40, -40), (W + 40, -40), (W + 40, H + 40), (-40, H + 40)], col)


def bunting(p, y, col=INK, sag=52, step=78, size=34):
    pts = [(x, y + sag * math.sin(math.pi * (x + 40) / (W + 80)))
           for x in range(-40, W + 90, 40)]
    p.line(pts, col, 4)
    for i, (px, py) in enumerate(pts):
        if i % 2 == 0:
            p.poly([(px - size * 0.55, py), (px + size * 0.55, py),
                    (px, py + size)], col)


def stall(p, e):
    """Evening. The counter everyone's tea is paid at."""
    t = e["t"]
    dark = e["scene"] in DARK
    ground = INK_D if dark else PAPER
    sky(p, ground)
    band(p, GY, (28, 26, 23) if dark else (206, 201, 190))

    ink = PAPER if dark else INK
    mass = (30, 27, 24) if dark else (44, 40, 35)
    mass2 = (22, 20, 18) if dark else (26, 23, 20)

    # the shop: a tall dark block with one lit hatch in it
    p.poly([(620, 470), (W + 40, 452), (W + 40, GY), (620, GY)], mass)
    p.poly([(580, 440), (W + 40, 420), (W + 40, 502), (580, 522)], mass)
    for i in range(3):
        y0 = 444 + i * 20
        p.poly([(588, y0), (W + 40, y0 - 20), (W + 40, y0 - 10), (588, y0 + 10)], mass2)
    hatch = (236, 232, 222) if not dark else (44, 40, 35)
    p.poly([(722, 646), (1024, 632), (1024, 1186), (722, 1200)], hatch)
    p.poly([(722, 646), (1024, 632), (1024, 654), (722, 668)], (196, 190, 178) if not dark else (56, 51, 45))
    # the tea man inside it
    person(p, 884, 1200, 356, INK if not dark else PAPER,
           hand_r=(-0.20, 0.04), hand_l=(0.16, 0.12), feat=0.92)

    # counter, in front of everything the shop owns
    p.poly([(596, 1210), (W + 40, 1194), (W + 40, GY), (596, GY)],
           (186, 180, 168) if not dark else (40, 37, 32))
    p.poly([(596, 1210), (W + 40, 1194), (W + 40, 1230), (596, 1246)],
           (188, 182, 170) if not dark else (56, 51, 45))
    if not dark:
        # kettle and glasses on the counter, well clear of his reaching hand
        p.ell([944, 1130, 1020, 1202], INK_S)
        p.poly([(1016, 1148), (1066, 1158), (1060, 1180), (1012, 1174)], INK_S)
        p.ell([962, 1124, 1002, 1140], (196, 190, 178))
        steam(p, 982, 1122, 150, (188, 182, 170), t, n=4)
        for i in range(2):
            glass(p, 1044 + i * 40, 1196, 50, None, INK)

    # the bulb hangs in the dark of the street: gold, because it is all paid for
    if not dark:
        p.line([(420, 442), (420, 592)], INK_S, 4)
        p.ell([388, 592, 452, 656], GOLD)
        p.ell([402, 606, 438, 642], GOLD_L)

    # the regulars
    for i, x0 in enumerate((140, 268, 378)):
        person(p, x0, GY + 6, 352 + (i % 2) * 26, ink,
               hand_r=(0.06, 0.31), hand_l=(-0.06, 0.32), lean=0.30 if i == 1 else 0.0,
               aw=0.056)

    # Rahim, in front of the counter: broad, collared, gold sash
    rah = person(p, 470, GY + 8, 600, ink, hand_r=(0.30, 0.14), hand_l=(-0.09, 0.30),
                 shawl=(64, 59, 51) if not dark else (58, 53, 46),
                 sash=GOLD if not dark else None, feat=1.10)
    e["anch"] = rah
    if not dark:
        hx, hy = rah["hand_r"]
        for k in range(3):
            ph = (t * 0.55 + k * 0.33) % 1.0
            coin(p, lerp(hx, 872, ph), lerp(hy, 1198, ph) - math.sin(ph * math.pi) * 92,
                 19 - 5 * ph, tilt=ph * 2)
    e["ink"], e["ground"] = ink, ground


def stage(p, e):
    """The price: a podium, a medal, his own name in gold."""
    t, q = e["t"], e["q"]
    ink, ground = INK, PAPER
    sky(p, ground)
    band(p, GY, (206, 201, 190))
    bunting(p, 470)
    bunting(p, 600, sag=44)

    # the banner with his name (the word itself is an overlay)
    bq = clamp((q - 0.10) / 0.34)
    if bq > 0:
        bw = 320 * back(bq)
        p.poly([(540 - bw, 560), (540 + bw, 560), (540 + bw, 712), (540 - bw, 712)], GOLD_D)
        p.poly([(540 - bw, 560), (540 + bw, 560), (540 + bw, 578), (540 - bw, 578)], GOLD)

    # the podium
    p.poly([(300, 1424), (700, 1424), (716, GY), (284, GY)], (52, 48, 42))
    p.poly([(300, 1424), (700, 1424), (700, 1450), (300, 1450)], GOLD if q > 0.28 else (52, 48, 42))

    # the crowd, backs to us, arms up, clapping
    for i in range(6):
        x = 60 + i * 190 + (i % 2) * 12
        hh = 336 + (i % 3) * 22
        clap = abs(math.sin(t * 5.0 + i * 0.9))
        up = 0.26 + 0.08 * clap
        spread = 0.30 + 0.05 * clap
        person(p, x, GY + 10, hh, (34, 31, 27) if i % 2 else (52, 48, 42),
               hand_r=(spread, -up), hand_l=(-spread, -up), aw=0.060)

    # Rahim on the podium, in front of them
    rah = person(p, 400, 1424, 566, ink, hand_r=(0.22, -0.26), hand_l=(-0.10, 0.28),
                 shawl=(64, 59, 51), sash=GOLD, feat=1.12)
    e["anch"] = rah
    # the medal drops onto his chest
    mq = clamp((q - 0.30) / 0.20)
    if mq > 0:
        my = lerp(rah["head"][1] - 300, rah["head"][1] + rah["hr"] * 3.4, back(mq))
        medal(p, rah["head"][0] + 6, my, 19)
    # the microphone, planted later
    if q > 0.52:
        mh = 260 * back(clamp((q - 0.52) / 0.26))
        mic(p, 640, 1424, mh)

    # coin confetti — the price, falling
    if q > 0.24:
        for i in range(11):
            ph = (t * 0.40 + i * 0.19) % 1.0
            coin(p, 60 + (i * 149) % 960 + 18 * math.sin(ph * 7 + i),
                 440 + ph * 900, 12, tilt=ph * 5)
    e["ink"], e["ground"] = ink, ground


def oldman(p, e):
    """One man who takes nothing — and the man who cannot believe it."""
    t = e["t"]
    ink, ground = INK, (233, 229, 219)
    sky(p, ground)
    band(p, GY, (208, 203, 192))
    # a bare tree: the winter of the story
    p.line([(44, GY + 6), (66, 900)], (70, 66, 59), 15)
    for a, ln in ((-0.95, 168), (-0.35, 200), (0.55, 178), (1.10, 128)):
        p.line([(66, 900), (66 + ln * math.sin(a), 900 - ln * math.cos(a))], (70, 66, 59), 9)

    # the old man on a stool, perfectly still
    p.rrect([150, 1338, 356, 1364], 8, (86, 81, 72))
    p.line([(178, 1364), (178, GY + 6)], (86, 81, 72), 10)
    p.line([(330, 1364), (330, GY + 6)], (86, 81, 72), 10)
    old = person(p, 252, GY, 452, (112, 104, 90), sit=True, crouch=1.0, beard=1.0, hunch=0.75,
                 hand_r=(0.22, 0.30), hand_l=(-0.15, 0.30), stick=True)
    glass(p, 386, 1352, 38, None, INK)

    # villagers, ringing him
    for i, x0 in enumerate((842, 962, 1046)):
        person(p, x0, GY + 8, 348 + (i % 2) * 24, (150, 143, 130),
               hand_l=(-0.08, 0.30), hand_r=(0.08, 0.30), aw=0.058)

    # Rahim, leaning in, gold and enormous
    jab = 0.5 + 0.5 * math.sin(t * 2.0)
    rah = person(p, 492, GY + 8, 616, INK,
                 hand_r=(-0.24 - 0.03 * jab, 0.20 - 0.05 * jab),
                 hand_l=(0.10, 0.30),
                 lean=0.55, shawl=(64, 59, 51), sash=GOLD, feat=1.12)
    e["anch"] = rah
    e["ink"], e["ground"] = ink, ground


def flood(p, e):
    """The money leaves the frame. After this, no gold anywhere in the film."""
    t = e["t"]
    sky(p, (16, 15, 13))
    for i in range(80):
        x = (i * 173 + t * 380) % (W + 140) - 70
        y = (i * 271 + t * 1560) % (H + 260) - 130
        p.line([(x, y), (x - 8, y + 50)], (52, 49, 44), 3)

    # the godown, half under
    p.poly([(566, 900), (1010, 866), (1010, 1300), (566, 1300)], (40, 37, 32))
    p.poly([(544, 900), (1032, 862), (1022, 826), (554, 864)], (54, 50, 44))
    p.poly([(700, 918), (792, 910), (792, 1046), (700, 1054)], (26, 24, 21))
    p.poly([(860, 906), (952, 898), (952, 1034), (860, 1042)], (26, 24, 21))

    wl = 1290
    band(p, wl, (34, 36, 40))
    for i in range(8):
        y = wl + 8 + i * 30
        amp = 5 + i * 1.7
        pts = [(x, y + amp * math.sin(x * 0.011 + t * 1.5 + i)) for x in range(-40, W + 60, 26)]
        p.line(pts, (58, 60, 64), 3)

    # sacks floating away
    for i in range(3):
        ph = (t * 0.14 + i * 0.3) % 1.0
        sx = 110 + 300 * ph + i * 40
        sy = wl + 40 + 30 * math.sin(t * 0.9 + i)
        p.ell([sx - 46, sy - 26, sx + 46, sy + 30], (198, 190, 174))
        p.poly([(sx - 18, sy - 22), (sx + 18, sy - 22), (sx + 10, sy - 44), (sx - 10, sy - 44)],
               (198, 190, 174))
        p.line([(sx - 8, sy - 42), (sx + 14, sy - 58)], (168, 160, 145), 5)

    # a plank riding the water
    p.poly([(596, wl + 92), (1000, wl + 50), (1004, wl + 82), (600, wl + 124)], (150, 142, 128))

    # the coins going down
    for i in range(10):
        ph = (t * 0.28 + i * 0.10) % 1.0
        fade = 1.0 - ph
        col = (int(lerp(34, 148, fade)), int(lerp(36, 108, fade)), int(lerp(40, 46, fade)))
        coin(p, 180 + (i * 191) % 760, wl + 36 + ph * 470, 15 - 6 * ph,
             tilt=0.4 + ph * 2, col=col, col2=(28, 28, 30))

    # Rahim, waist deep, no sash any more
    person(p, 268, GY + 8, 540, (216, 210, 196), hand_r=(0.14, 0.20),
           hand_l=(-0.14, 0.22), hunch=0.55, aw=0.056)
    e["ink"], e["ground"] = (216, 210, 196), (16, 15, 13)


def morning(p, e):
    """The stall is shut. Nobody turns around. No gold anywhere."""
    t = e["t"]
    sky(p, (21, 19, 17))
    band(p, GY, (31, 28, 25))
    # the stall, shut, its bulb dark
    p.poly([(620, 900), (W + 40, 878), (W + 40, GY), (620, GY)], (38, 35, 30))
    p.poly([(596, 872), (W + 40, 848), (W + 40, 900), (596, 924)], (48, 44, 38))
    p.poly([(620, 1218), (W + 40, 1200), (W + 40, GY), (620, GY)], (44, 40, 34))
    p.line([(700, 872), (700, 916)], (66, 60, 52), 4)
    p.ell([684, 916, 716, 948], (72, 66, 58))
    # an upturned stool
    p.poly([(700, 1300), (836, 1300), (836, 1318), (700, 1318)], (62, 56, 49))
    p.line([(716, 1318), (716, GY + 4)], (62, 56, 49), 8)
    p.line([(820, 1318), (820, GY + 4)], (62, 56, 49), 8)

    # the village, leaving, backs turned
    for i in range(3):
        person(p, 236 + i * 104 + (t * 9) % 24, GY + 8, 330 + (i % 2) * 20, (84, 78, 68),
               walk=t * 2.4 + i * 1.2, hand_r=(0.05, 0.32), hand_l=(-0.05, 0.32), aw=0.058)

    # he stands where he used to hold court
    rah = person(p, 764, GY + 8, 520, (198, 192, 178), hand_r=(0.07, 0.33),
                 hand_l=(-0.07, 0.33), hunch=0.6, aw=0.056)
    e["anch"] = rah
    e["ink"], e["ground"] = (216, 210, 196), (21, 19, 17)


def water(p, e):
    """The one blue in the film, given away for nothing."""
    t, q = e["t"], e["q"]
    sky(p, (18, 17, 15))
    band(p, GY, (27, 25, 22))
    # a wall and a doorframe: shelter, not a stage
    p.poly([(700, 470), (W + 40, 470), (W + 40, GY), (700, GY)], (33, 30, 26))
    p.poly([(880, 620), (W + 40, 620), (W + 40, GY), (880, GY)], (20, 19, 17))
    p.line([(700, 470), (W + 40, 470)], (52, 48, 42), 6)

    # Rahim on the ground, head down, against the wall
    person(p, 690, GY + 10, 486, (196, 190, 176), sit=True, crouch=1.0, hunch=1.0,
           lean=0.30, hand_r=(0.12, 0.26), hand_l=(-0.02, 0.34), aw=0.055)

    # the old man, standing over him, the glass held out and down
    gq = clamp((q - 0.12) / 0.20)
    old = person(p, 268, GY + 8, 566, (228, 222, 208),
                 hand_r=(0.44, 0.06 - 0.02 * back(gq)),
                 hand_l=(-0.10, 0.30), beard=1.0, hunch=0.55, lean=0.5)
    hx, hy = old["hand_r"]
    if gq > 0:
        gy = hy + 34 * (1 - gq) + 40
        glass(p, hx + 28, gy, 96, fill=BLUE, col=(236, 232, 220))
        p.line([(hx + 10, gy - 84), (hx + 48, gy - 88)], (156, 194, 228), 4)
    e["anch"] = old
    e["ink"], e["ground"] = (228, 222, 208), (18, 17, 15)


def end(p, e):
    """The last image: dusk, two men walking, one small blue light on a sill."""
    t, q = e["t"], e["q"]
    sky(p, (26, 24, 21))
    band(p, 1290, (18, 17, 15))
    for i in range(5):                          # the village, low
        x = -40 + i * 250
        p.poly([(x, 1080 - (i % 3) * 40), (x + 210, 1070 - (i % 3) * 40),
                (x + 210, 1290), (x, 1290)], (34, 31, 27))
        p.poly([(x + 20, 1160), (x + 70, 1158), (x + 70, 1210), (x + 20, 1212)], (24, 22, 19))
    p.poly([(-40, 1290), (W + 40, 1290), (W + 40, H + 40), (-40, H + 40)], (24, 22, 19))
    # the long road
    p.poly([(360, 1290), (700, 1290), (1000, H + 40), (60, H + 40)], (30, 28, 24))

    # two men walking away, together
    for i, (x, hh, col) in enumerate(((520, 300, (176, 170, 156)), (614, 268, (206, 200, 186)))):
        person(p, x + (t * 8) % 20, 1560 + i * 6, hh, col, walk=t * 2.2 + i * 1.6,
               hunch=0.55 if i else 0.35, hand_r=(0.05, 0.32), hand_l=(-0.05, 0.32), aw=0.058)

    # the one thing that was not for sale
    if q > 0.18:
        bq = back(clamp((q - 0.18) / 0.22))
        p.rrect([276, 1102, 276 + 48 * bq, 1102 + 60 * bq], 3, BLUE)
    e["ink"], e["ground"] = (206, 200, 186), (26, 24, 21)


SETS = {"stall": stall, "stage": stage, "oldman": oldman, "flood": flood,
        "morning": morning, "water": water, "end": end}


# ---------------------------------------------------------------- cards
def title_card(base, q):
    T(base, (96, TYPE_Y), "অন্ধকার পাঠ", 32, INK_S, 500)
    T(base, (96, TYPE_Y + 44), "০৩", 32, INK_S, 700)
    # the number as architecture
    T(base, (540, 650), "০৩", 840, (210, 205, 193), 700, anchor="mm")
    T(base, (96, 1180), "কেনা সম্মান", 132, INK, 700, anchor="lm")
    T(base, (98, 1284), "Bought Respect", 44, INK_S, 500, anchor="lm")
    T(base, (96, 1466), "সম্মান কেনা যায়, ভাড়া করা যায় —", 40, INK, 500, anchor="lm")
    T(base, (96, 1528), "কিন্তু মালিকানা নয়।", 40, INK, 500, anchor="lm")
    r = 0
    d = ImageDraw.Draw(base)
    bq = clamp((q - 0.5) / 0.4)
    if bq > 0:
        d.rectangle([96, 1600, 96 + 108 * bq, 1606], fill=INK + (255,))


def end_card(base, q):
    T(base, (96, TYPE_Y), "অন্ধকার পাঠ · ০৩", 30, (128, 122, 111), 500)
    T(base, (96, 700), "ভাড়া শেষ —", 104, (238, 234, 224), 700, anchor="lm")
    T(base, (96, 828), "সম্মানও শেষ।", 104, (238, 234, 224), 700, anchor="lm")
    T(base, (96, 1080), "সম্মান কি সত্যিই", 62, (198, 193, 181), 500, anchor="lm")
    T(base, (96, 1168), "কেনা যায়?", 62, (198, 193, 181), 500, anchor="lm")
    bq = clamp((q - 0.40) / 0.30)
    d = ImageDraw.Draw(base)
    if bq > 0:
        cy = 1316
        r = 15 * back(bq)
        d.ellipse([96 - r, cy - r, 96 + r, cy + r], fill=BLUE + (255,))
        d.line([(80, cy + 52), (96, cy + 80), (112, cy + 52)], fill=BLUE + (255,),
               width=5, joint="curve")



# ---------------------------------------------------------------- frame
def frame_at(t, entries, total, spans):
    if t < LEAD:
        base = Image.new("RGBA", (W, H), PAPER + (255,))
        title_card(base, t / LEAD)
        return base
    if t > total - TAIL + 0.15:
        base = Image.new("RGBA", (W, H), (26, 24, 21, 255))
        end_card(base, (t - (total - TAIL)) / TAIL)
        return base

    cur = entries[-1]
    for e in entries:
        if e["t0"] - 1e-6 <= t <= e["t0"] + e["dur"] + GAP:
            cur = e
            break
    sc = cur["scene"]
    a, b = spans[sc]
    local = clamp((t - a) / max(0.45, b - a))

    art = Image.new("RGB", (int(W * SS), int(H * SS)), PAPER)
    p = P(art, SS)
    env = {"t": t, "q": local, "spk": cur["spk"], "line": cur["i"], "scene": sc}
    SETS[sc](p, env)
    art = art.resize((W, H), Image.LANCZOS).convert("RGBA")

    for (x, y, tx, size, col, wt, an) in OVERLAY.get(sc, ()):
        T(art, (x, y), tx, size, col, wt, anchor=an)

    dark = sc in DARK
    cap = CAPTION.get(sc, "")
    ink_c = (236, 232, 222) if dark else INK
    if cap:
        T(art, (96, TYPE_Y), "অন্ধকার পাঠ · ০৩", 28, (150, 144, 132) if dark else INK_S, 500)
        T(art, (96, CAP_Y), cap, 126, ink_c, 700)

    # the spoken line
    if cur["spk"] != "narr":
        T(art, (96, SUB_Y - 62), {"rahim": "রহিম", "old": "বুড়ো",
                                  "villager": "কেউ একজন"}[cur["spk"]],
          28, (172, 160, 138) if dark else GOLD_D, 700)
    lines = wrap(cur["text"], 38, 880)
    yy = SUB_Y - 48 * (len(lines) - 1)
    for ln in lines:
        T(art, (96, yy), ln, 38, ink_c, 500, anchor="lm")
        yy += 48
    return art


def render(still=None, seg=None, out=None):
    entries, total = build_timeline()
    spans, order = scene_spans(entries, total)
    n = int(round(total * FPS))
    print("timeline: %.2fs  %d frames  %d lines" % (total, n, len(entries)))

    if still is not None:
        img = frame_at(float(still), entries, total, spans).convert("RGB")
        path = out or os.path.join(HERE, "frames", "still-%06.1f.png" % float(still))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)
        print("wrote", path)
        return

    a, b = (0, n) if seg is None else seg
    out = out or os.path.join(HERE, "film3.mp4")
    cmd = [FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(a, b):
        img = frame_at(i / FPS, entries, total, spans).convert("RGB")
        proc.stdin.write(img.tobytes())
        if (i - a) % 120 == 0:
            print("  %d/%d  %.1fs" % (i, b, i / FPS), flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=float, default=None)
    ap.add_argument("--seg", type=int, nargs=2, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    render(a.still, a.seg, a.out)
