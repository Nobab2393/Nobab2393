"""film2d.py — "ধনী বাবা, গরিব বাবা · অধ্যায় ১: সম্পদ আর দায়"

Flat 2D, drawn with Pillow in cast2d's design space, rendered to 1920x1080 @ 20 fps.
World is 2400x1350; a per-scene camera crops a rect and resamples, so push-ins and
pans are free. All Bangla goes through deva.draw_text (no libraqm on this box).

    python3 film2d.py --still 42.0        # one PNG for QA
    python3 film2d.py --seg 0 1450        # frames [0,1450) -> seg-0.mp4
"""
import argparse
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import imageio_ffmpeg

import cast2d as C
import deva

HERE = os.path.dirname(os.path.abspath(__file__))
deva.FONT = os.path.join(HERE, "fonts/NotoSansBengali.ttf")

W, H = 1920, 1080
WW, WH = 2400, 1350
K = 1.5                      # world supersample
FPS = 20
GY = 1075.0                  # ground line, world coords
VO = os.path.join(HERE, "vo")
FF = imageio_ffmpeg.get_ffmpeg_exe()

INK = C.INK
CREAM = C.CREAM


# ----------------------------------------------------------------- timeline
SCRIPT = [
    # (scene, speaker, text)  — narration is "narr"
    ("sky", "narr",
     "পৃথিবীর সব ধনী মানুষ একই একটা প্রশ্নের উত্তর জেনে গেছে। আর সব গরিব মানুষ সারাজীবন সেই প্রশ্নটা করতেই ভুলে গেছে। প্রশ্নটা হলো — টাকা আসলে কীভাবে কাজ করে?"),
    ("bench", "rabbit",
     "স্যার, আমার বাবা বলেন — ভালো করে পড়ো, ভালো চাকরি করো, তাহলে টাকার অভাব হবে না।"),
    ("bench", "eagle",
     "উপদেশটা মিথ্যা নয়। কিন্তু অর্ধেক সত্য।"),
    ("bench", "rabbit", "অর্ধেক?"),
    ("bench", "eagle",
     "আমার জীবনে দুজন বাবা ছিলেন। একজন খুব পড়াশোনা করেছেন, ভালো চাকরি করেছেন — সারাজীবন টাকার অভাবে থেকেছেন। আরেকজন স্কুল শেষ করেননি, কিন্তু তাঁর টাকা তাঁর হয়ে কাজ করত।"),
    ("bench", "rabbit", "তাহলে পার্থক্যটা কোথায়?"),
    ("bench", "eagle", "শেখায়। একজন শিখেছিলেন টাকা কীভাবে আয় করতে হয়। আরেকজন শিখেছিলেন টাকা কী।"),
    ("board", "eagle",
     "পুরো বইটা যদি এক বাক্যে বলতে হয় — এই। এক জিনিস তোমার পকেটে টাকা ঢোকায়। আরেক জিনিস তোমার পকেট থেকে টাকা বের করে নেয়। প্রথমটার নাম সম্পদ। দ্বিতীয়টার নাম দায়।"),
    ("board", "rabbit", "সেটা তো সহজ!"),
    ("board", "eagle", "সহজ। কিন্তু শহরের অর্ধেক মানুষ প্রতিদিন এই দুটোকে গুলিয়ে ফেলে।"),
    ("shop", "fox", "আরে খরগোশ! একদম সময়মতো এসেছ। এই সাইকেলটা দেখো — মাসে মাত্র পাঁচশো। এটা তো সম্পদ!"),
    ("shop", "rabbit", "সম্পদ?"),
    ("shop", "fox", "অবশ্যই! সবার থাকে। তুমিও থাকো।"),
    ("shop", "rabbit", "স্যার… এটা কি সত্যিই সম্পদ?"),
    ("shop", "eagle", "আমাকে জিজ্ঞেস করো না। ওকে জিজ্ঞেস করো — কার পকেটে টাকা ঢুকছে, আর কার পকেট থেকে বেরোচ্ছে?"),
    ("shop", "rabbit", "সাইকেলটা কি আমার পকেটে টাকা ঢোকাবে?"),
    ("shop", "fox", "…ডে-ডে, ওভাবে দেখলে তো সব কিছুই…"),
    ("shop", "rabbit", "তাহলে এটা সম্পদ নয়। এটা দায়।"),
    ("shop", "fox", "তুমি খুব ছোট, তাই বুঝবে না।"),
    ("slope", "eagle",
     "বেতন বাড়ল? খরচও বাড়ল। এটাই ইঁদুরের দৌড় — যত জোরে দৌড়াবে, চাকাটাও তত জোরে ঘুরবে। বেরোনোর পথটা দৌড় নয়।"),
    ("turtle", "turtle",
     "টাকা তোমাকে ধনী বানায় না, ছোট্ট খরগোশ। টাকা কী — সেটা জানলেই ধনী হওয়া শুরু।"),
    ("walk", "eagle",
     "একটা অভ্যাস তৈরি করো। যা-ই কেনার আগে নিজেকে জিজ্ঞেস করো — এটা আমার পকেটে টাকা ঢোকাচ্ছে, না বের করছে? উত্তরটা জানলেই তুমি বাকি সবার থেকে এগিয়ে।"),
]
TITLE = "ধনী বাবা, গরিব বাবা"
SUBTITLE = "অধ্যায় ১ · সম্পদ আর দায়"
END1 = "যা টাকা ঢোকায়, তা সম্পদ।"
END2 = "যা টাকা বের করে, তা দায়।"
NEXT = "পরের অধ্যায় · কেন টাকার জন্য কাজ করবেন না"

NAME = {"eagle": "প্রফেসর ঈগল", "rabbit": "খরগোশ", "fox": "শিয়াল", "turtle": "কচ্ছপ"}


def _dur(path):
    out = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError("no duration for " + path)


def build_timeline():
    entries, t = [], 1.6                      # a breath of silent title first
    prev_scene = None
    for i, (scene, spk, text) in enumerate(SCRIPT):
        vid = os.path.join(VO, "s%02d.mp3" % (i + 1))
        d = _dur(vid) if os.path.exists(vid) else 3.5
        gap = 0.85 if scene != prev_scene else 0.45
        t0 = t + gap
        entries.append(dict(i=i, scene=scene, spk=spk, text=text, t0=t0, dur=d,
                            vo=vid if os.path.exists(vid) else None, fresh=scene != prev_scene))
        t = t0 + d
        prev_scene = scene
    # scene windows: cut a beat before the first line of each scene
    starts = {}
    for e in entries:
        if e["scene"] not in starts:
            starts[e["scene"]] = max(0.0, e["t0"] - 0.9)
    order = []
    for e in entries:
        if e["scene"] not in order:
            order.append(e["scene"])
    last = entries[-1]
    end_t0 = last["t0"] + last["dur"] + 0.6
    for k, sc in enumerate(order):
        ends = starts[order[k + 1]] if k + 1 < len(order) else end_t0
        for e in entries:
            if e["scene"] == sc:
                e["s0"], e["s1"] = starts[sc], ends
    order = order + ["end"]
    starts["end"] = end_t0
    return entries, order, end_t0 + 5.2


# ----------------------------------------------------------------- helpers
def ease(q):
    return q * q * (3 - 2 * q)


def lerp(a, b, q):
    return a + (b - a) * q


def bob(t, amp=6.0, rate=1.4, ph=0.0):
    return amp * math.sin(2 * math.pi * rate * t + ph)


def mouth_of(e, who, rate=4.6):
    if e["spk"] != who:
        return 0.0
    lt = e["t"] - e["line"]["t0"]
    if lt < 0 or lt > e["line"]["dur"]:
        return 0.0
    return 0.30 + 0.42 * abs(math.sin(math.pi * rate * lt))


def blink_of(t, ph=0.0, period=4.3):
    x = (t + ph) % period
    if x < 0.10:
        return min(1.0, x / 0.05, (0.10 - x) / 0.05)
    return 0.0


def cam_view(cx, cy, zoom):
    w, h = WW / zoom, WH / zoom
    x0 = min(max(cx - w / 2, 0.0), WW - w)
    y0 = min(max(cy - h / 2, 0.0), WH - h)
    return x0, y0, w, h


def proj(e, wx, wy):
    x0, y0, w, h = e["view"]
    k = W / w
    return ((wx - x0) * k, (wy - y0) * k, k)


# ----------------------------------------------------------------- skies
def sky_flat(p, col=(203, 221, 229)):
    p.poly([(-200, -500), (WW + 200, -500), (WW + 200, WH + 500), (-200, WH + 500)], col, 0)


def sky_bands(p, top=(203, 221, 227), mid=(228, 229, 213), low=CREAM, hz=GY - 230):
    """Kept for the aerial shot only: one flat sky plus a warm haze band at the horizon."""
    sky_flat(p, top)
    p.poly([(-200, hz - 120), (WW + 200, hz - 120), (WW + 200, WH), (-200, WH)],
           mid, 0)


def sun(p, x, y, r=120, col=(246, 216, 148), ring=(236, 198, 126)):
    p.ell([x - r * 1.22, y - r * 1.22, x + r * 1.22, y + r * 1.22], (250, 238, 208), 0)
    p.ell([x - r, y - r, x + r, y + r], col, 4.0, ring)


def cloud(p, x, y, s=1.0):
    for dx, dy, r in ((0, 0, 46), (52, -16, 54), (112, 4, 44), (56, 18, 44), (-40, 10, 34)):
        p.ell([x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s],
              (250, 248, 240), 3.2)


def hills(p, base=GY - 180, amp=150, col=(214, 196, 166), col2=(198, 178, 144)):
    def ridge(b, a, ph, colr, step=40):
        pts = [(x, b - a * (0.5 + 0.32 * math.sin(x / 360.0 + ph)
                            + 0.18 * math.sin(x / 150.0 + ph * 2.1)))
               for x in range(-120, WW + 240, step)]
        p.poly(pts + [(WW + 240, base + 500), (-120, base + 500)], colr, 0)
    ridge(base - 60, amp * 1.15, 1.1, col)
    ridge(base + 70, amp * 0.85, 3.7, col2)


def tree(p, x, y, s=1.0, col=(122, 138, 88)):
    p.poly([(x - 12 * s, y), (x + 12 * s, y), (x + 8 * s, y - 120 * s), (x - 8 * s, y - 120 * s)],
           (139, 90, 43), 4.0)
    for dx, dy, r in ((0, -170, 62), (-46, -140, 44), (48, -142, 46)):
        p.ell([x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s],
              col, 4.2)


def ground_band(p, y=GY, col=(238, 221, 192), line=True):
    p.poly([(-200, y), (WW + 200, y), (WW + 200, WH + 400), (-200, WH + 400)], col, 0)
    if line:
        p.line([(-200, y), (WW + 200, y)], (198, 172, 134), 4.0)


def cobbles(p, y=GY, rows=6):
    for r in range(rows):
        yy = y + 26 + r * 46
        wgt = max(1.0, 4.0 - r * 0.5)
        for i in range(-2, 26):
            xx = i * 104 + (52 if r % 2 else 0)
            p.arc([xx, yy - 16, xx + 96, yy + 30], 200, 340, (206, 182, 148), wgt)


# ----------------------------------------------------------------- world pieces
def street(p, e, lamp_x=560, houses=((300, 1.0), (1980, 1.15)), bench_x=None):
    sky_flat(p)
    hills(p, base=GY - 150, amp=150)
    ground_band(p, y=GY - 30)
    cobbles(p, y=GY - 38)
    for hx, hs in houses:
        C.house(p, hx, GY - 6, w=300 * hs, h=210 * hs)
    C.lamp(p, lamp_x, GY - 4, h=470)
    if bench_x is not None:
        C.bench(p, bench_x, GY - 2, w=340)


def shopfront(p, e):
    sky_flat(p, (200, 219, 228))
    hills(p, base=GY - 150, amp=150)
    tree(p, 240, GY - 40, 1.1)
    tree(p, 700, GY - 30, 0.8)
    ground_band(p, y=GY - 30)
    cobbles(p, y=GY - 38)
    x0, x1, top = 1180, 2090, GY - 540
    # wall + roof slab
    p.rrect([x0, top, x1, GY], 6, (226, 201, 166), 4.8)
    p.rrect([x0 - 34, top - 104, x1 + 34, top], 6, C.ROOF, 4.8)
    p.rrect([x0 - 34, top - 104, x1 + 34, top - 80], 3, C.ROOF_D, 0)
    # window: three panes over a sill
    wx0, wx1, wy0, wy1 = x0 + 60, x0 + 510, top + 262, GY - 80
    p.rrect([wx0 - 14, wy0 - 14, wx1 + 14, wy1 + 14], 6, (150, 108, 74), 4.4)
    for k in range(3):
        xa = wx0 + k * (wx1 - wx0) / 3 + 8
        p.rrect([xa, wy0, xa + (wx1 - wx0) / 3 - 16, wy1], 3, (250, 236, 198), 3.4)
    # door on the right
    dx0, dx1 = x0 + 560, x0 + 760
    p.rrect([dx0, GY - 268, dx1, GY], 6, (146, 96, 66), 4.6)
    p.rrect([dx0 + 24, GY - 236, dx1 - 24, GY - 150], 4, (250, 232, 186), 3.4)
    p.ell([dx1 - 34, GY - 150, dx1 - 18, GY - 134], C.GOLD, 3.0)
    # awning, scalloped, over the window
    ay0, ay1 = top + 190, top + 278
    span = 500.0
    for i in range(6):
        xa = x0 + 30 + i * (span / 6.0)
        p.poly([(xa, ay0), (xa + span / 6.0, ay0), (xa + span / 6.0, ay1),
                (xa, ay1)], (238, 232, 214) if i % 2 == 0 else (196, 92, 72), 3.6)
    for i in range(6):
        xa = x0 + 30 + i * (span / 6.0)
        p.arc([xa, ay1 - 26, xa + span / 6.0, ay1 + 26], 0, 180,
              (238, 232, 214) if i % 2 == 0 else (196, 92, 72), 4.0)
    # a price ticket hanging off the awning
    tx = x0 + 130
    p.line([(tx, ay1), (tx, ay1 + 54)], INK, 3.4)
    p.rrect([tx - 84, ay1 + 50, tx + 84, ay1 + 136], 6, (250, 244, 226), 3.8)
    e["tag"] = (tx, ay1 + 93)
    C.lamp(p, 470, GY - 4, h=440)


# ----------------------------------------------------------------- scenes
SCENES = {}


def scene(key):
    def wrap(fn):
        SCENES[key] = fn
        return fn
    return wrap


def ridge_y(x):
    return 930.0 - 46.0 * math.sin(x / 620.0) - 18.0 * math.sin(x / 210.0 + 2.0)


@scene("sky")
def s_sky(p, e):
    q, t = e["q"], e["t"]
    sky_flat(p, (197, 218, 229))
    sun(p, 1960, 236, r=118)
    for cx, cy, cs, sp in ((320, 250, 1.2, 11), (900, 150, 0.9, 7),
                           (1540, 320, 1.05, 9), (2180, 176, 0.75, 6)):
        cloud(p, cx + sp * t, cy + 6 * math.sin(t * 0.4 + cx), cs)
    # the town, far below, along a rolling ridge
    pts = [(x, ridge_y(x)) for x in range(-120, WW + 240, 40)]
    p.poly(pts + [(WW + 240, WH + 400), (-120, WH + 400)], (208, 191, 162), 0)
    pts2 = [(x, ridge_y(x) + 96) for x in range(-120, WW + 240, 40)]
    p.poly(pts2 + [(WW + 240, WH + 400), (-120, WH + 400)], (190, 172, 142), 0)
    for hx, hs in ((240, 0.52), (470, 0.42), (760, 0.55), (1010, 0.44),
                   (1300, 0.5), (1620, 0.4), (1900, 0.52), (2210, 0.44)):
        C.house(p, hx, ridge_y(hx) + 26, w=230 * hs, h=170 * hs, roof=C.ROOF_D)
    for tx in (620, 1150, 1780, 2060):
        tree(p, tx, ridge_y(tx) + 20, 0.45)
    for yy, cc in ((1120, (200, 182, 152)), (1215, (194, 176, 146))):
        p.poly([(-120, yy), (WW + 240, yy - 22), (WW + 240, yy + 30), (-120, yy + 52)], cc, 0)
    # the eagle glides down
    ex = lerp(360, 760, ease(min(1.0, q * 1.4)))
    ey = 1000 - 40 * q + bob(t, 10, 0.3)
    C.eagle(p, ex, ey, 0.74, wings=0.52 + 0.12 * math.sin(2 * math.pi * 0.4 * t),
            blink=blink_of(t, 1.1), mouth=mouth_of(e, "eagle"), look=(0.2, 0.5), legs=False)
    if q < 0.40:
        a = 1.0 if q < 0.28 else max(0.0, (0.40 - q) / 0.12)
        e["card"] = (TITLE, SUBTITLE, None, a)


@scene("bench")
def s_bench(p, e):
    t, q = e["t"], e["q"]
    street(p, e, lamp_x=470, houses=((250, 1.0), (2140, 1.1)), bench_x=1250)
    zoom = lerp(1.02, 1.12, ease(min(1, q * 1.6)))
    C.rabbit(p, 1000, GY - 4, 1.34, ears=0.10 * math.sin(2 * math.pi * 0.5 * t),
             blink=blink_of(t, 0.4), mouth=mouth_of(e, "rabbit"), look=(0.35, 0),
             arm=0.4 if e["spk"] == "rabbit" else 0.0)
    C.eagle(p, 1440, GY - 2, 1.42, wings=0.0,
            blink=blink_of(t, 2.2), mouth=mouth_of(e, "eagle"), look=(-0.5, 0), tilt=-4)
    e["zoom"] = zoom


@scene("board")
def s_board(p, e):
    t, q = e["t"], e["q"]
    sky_flat(p, (202, 220, 228))
    hills(p, base=GY - 170, amp=160)
    ground_band(p, y=GY - 30)
    # the board
    bx, by = 1560, GY - 300
    p.line([(bx - 190, GY), (bx - 120, by + 130)], (150, 106, 70), 12)
    p.line([(bx + 190, GY), (bx + 120, by + 130)], (150, 106, 70), 12)
    p.rrect([bx - 360, by - 240, bx + 360, by + 200], 12, (250, 244, 226), 6.0)
    p.rrect([bx - 344, by - 224, bx + 344, by + 184], 8, (245, 238, 217), 0)
    p.line([(bx, by - 224), (bx, by + 184)], (216, 198, 168), 3.4)
    # left: a purse that fills · right: a pocket with a hole
    purse(p, bx - 180, by + 20, 1.05 + 0.05 * math.sin(t * 1.6))
    pocket(p, bx + 180, by + 40, 1.05)
    coins_into(p, bx - 180, by + 10, t)
    coins_out(p, bx + 180, by + 110, t)
    C.eagle(p, 830, GY - 2, 1.34, wings=0.0,
            blink=blink_of(t, 0.9), mouth=mouth_of(e, "eagle"), look=(0.6, 0), tilt=6)
    C.rabbit(p, 470, GY - 4, 1.16, blink=blink_of(t, 2.6), mouth=mouth_of(e, "rabbit"),
             look=(0.6, 0), arm=0.5)


def purse(p, x, y, s=1.0):
    p.rrect([x - 92 * s, y - 60 * s, x + 92 * s, y + 78 * s], 18, (139, 94, 80), 5.0)
    p.rrect([x - 92 * s, y - 60 * s, x + 92 * s, y - 12 * s], 16, (112, 73, 62), 4.6)
    p.ell([x - 14 * s, y + 6 * s, x + 14 * s, y + 34 * s], C.GOLD, 3.4)


def pocket(p, x, y, s=1.0):
    p.rrect([x - 92 * s, y - 60 * s, x + 92 * s, y + 80 * s], 12, (94, 122, 74), 5.0)
    p.ell([x - 26 * s, y + 60 * s, x + 26 * s, y + 96 * s], (70, 81, 42), 4.2)


def coins_into(p, x, y, t):
    for i in range(5):
        ph = (t * 0.75 + i * 0.2) % 1.0
        cy = y - 150 + 210 * ph
        if cy < y + 60:
            C.coin(p, x + 30 * math.sin(ph * 6 + i), cy, 13, tilt=0.4 + 0.6 * abs(math.cos(ph * 9)))


def coins_out(p, x, y, t):
    for i in range(5):
        ph = (t * 0.85 + i * 0.2) % 1.0
        cy = y + 120 * ph
        C.coin(p, x - 40 * math.sin(ph * 4 + i), cy, 13, tilt=0.3)


@scene("shop")
def s_shop(p, e):
    t, q = e["t"], e["q"]
    shopfront(p, e)
    C.bicycle(p, 1300, GY - 6, 1.35 + 0.02 * math.sin(t * 1.2))
    C.fox(p, 1810, GY - 2, 1.28, blink=0.35 if e["spk"] != "fox" else 0.18,
          mouth=mouth_of(e, "fox", 5.4), look=(-0.6, 0),
          hands=0.0 if e["spk"] == "fox" else 1.0)
    C.rabbit(p, 1055, GY - 4, 1.3, ears=0.08 * math.sin(2 * math.pi * 0.6 * t),
             blink=blink_of(t, 1.7), mouth=mouth_of(e, "rabbit"), look=(0.6, 0),
             arm=0.5)
    C.eagle(p, 760, GY - 2, 1.34, wings=0.0, blink=blink_of(t, 3.1),
            mouth=mouth_of(e, "eagle"), look=(0.5, 0), tilt=2)
    e["zoom"] = lerp(1.06, 1.0, ease(min(1, q * 1.2)))


def slope_y(x):
    return 1035.0 - (x + 200) * 390.0 / 2800.0


@scene("slope")
def s_slope(p, e):
    t, q = e["t"], e["q"]
    sky_flat(p, (212, 220, 224))
    # a long hill running up to the right, with a worn path
    p.poly([(-200, WH + 200), (-200, slope_y(-200)), (WW + 200, slope_y(WW + 200)),
            (WW + 200, WH + 200)], (231, 211, 179), 0)
    p.poly([(-200, slope_y(-200) + 60), (WW + 200, slope_y(WW + 200) + 60),
            (WW + 200, WH + 200), (-200, WH + 200)], (208, 188, 156), 0)
    p.line([(-200, slope_y(-200)), (WW + 200, slope_y(WW + 200))], (198, 178, 146), 3.4)
    for i in range(26):
        xx = -100 + i * 100
        p.line([(xx, slope_y(xx) + 92), (xx + 62, slope_y(xx) - 30)], (196, 176, 144), 3.0)
    # the wheel of the rat race, standing on the hill
    wx = 1760
    wy = slope_y(wx) - 168
    wr = 168
    for sx in (-1, 1):
        p.line([(wx + sx * 96, wy + 120), (wx + sx * 120, slope_y(wx) - 6)], (150, 110, 74), 12)
    p.line([(wx - 120, slope_y(wx) - 10), (wx + 120, slope_y(wx) - 10)], (150, 110, 74), 12)
    C.Pen.ring(p, [wx - wr, wy - wr, wx + wr, wy + wr], 14.0, (150, 116, 78))
    C.Pen.ring(p, [wx - wr + 16, wy - wr + 16, wx + wr - 16, wy + wr - 16], 4.0, (176, 144, 104))
    for i in range(8):
        a = 2 * math.pi * (i / 8.0 + t * 0.55)
        p.line([(wx, wy), (wx + wr * math.cos(a), wy + wr * math.sin(a))], (168, 132, 92), 6)
    p.ell([wx - 24, wy - 24, wx + 24, wy + 24], (150, 116, 78), 4.0)
    p.arc([wx - wr - 24, wy - wr - 24, wx + wr + 24, wy + wr + 24], 200, 250,
          (150, 116, 78), 5.0)
    # the rabbit, climbing with the load
    rx = 940 - 70 * q
    ry = slope_y(rx) + 4 + 3 * abs(math.sin(2 * math.pi * 1.5 * t))
    p.ell([rx - 104, ry - 8, rx + 104, ry + 18], (200, 181, 150), 0)
    C.rabbit(p, rx, ry, 1.22, ears=0.12 * math.sin(2 * math.pi * 1.5 * t),
             blink=blink_of(t, 0.8), mouth=mouth_of(e, "rabbit"), look=(0.3, -0.2),
             arm=0.85)
    for i, col in enumerate(((176, 116, 82), (150, 106, 62), (176, 116, 82))):
        yy = ry - 132 - i * 60
        p.poly([(rx - 62 + 5 * i, yy - 56), (rx + 74 - 5 * i, yy - 62),
                (rx + 74 - 5 * i, yy), (rx - 62 + 5 * i, yy + 8)], col, 4.6)
        p.line([(rx - 60 + 5 * i, yy - 26), (rx + 72 - 5 * i, yy - 32)], INK, 3.0)
    # coins slipping out of the satchel behind him
    for i in range(7):
        ph = (t * 1.4 + i * 0.14) % 1.0
        C.coin(p, rx - 96 - 16 * i + 20 * math.sin(ph * 5 + i), ry - 40 + 120 * ph,
               12, tilt=0.5)
    # dust puffs at his heels
    for i in range(3):
        ph = (t * 1.1 + i * 0.33) % 1.0
        r = 10 + 26 * ph
        p.ell([rx - 60 - r, ry - 6 - r * 0.6, rx - 60 + r, ry - 6 + r * 0.6],
              (232, 216, 190), 2.4)


@scene("turtle")
def s_turtle(p, e):
    t, q = e["t"], e["q"]
    street(p, e, lamp_x=430, houses=((230, 1.05), (2180, 1.0)), bench_x=620)
    C.rabbit(p, 860, GY - 4, 1.32, ears=0.06 * math.sin(2 * math.pi * 0.4 * t),
             blink=blink_of(t, 2.0), mouth=mouth_of(e, "rabbit"), look=(0.5, 0),
             arm=0.3)
    sway = 3.0 * math.sin(2 * math.pi * 0.25 * t)
    C.turtle(p, 1280, GY - 2, 1.5, blink=blink_of(t, 0.3, 6.0),
             mouth=mouth_of(e, "turtle", 3.4), tilt=sway)
    C.eagle(p, 1600, GY - 2, 1.3, wings=0.0, blink=blink_of(t, 1.4),
            mouth=mouth_of(e, "eagle"), look=(-0.4, 0), tilt=-2)
    e["zoom"] = lerp(1.1, 1.02, ease(min(1, q * 1.1)))


@scene("walk")
def s_walk(p, e):
    t, q = e["t"], e["q"]
    sky_flat(p, (243, 216, 186))
    sun(p, 1700 + 24 * q, GY - 470, r=185, col=(246, 200, 132), ring=(232, 176, 108))
    hills(p, base=GY - 170, amp=120, col=(216, 172, 138), col2=(200, 156, 124))
    for tx, ts in ((300, 0.9), (560, 0.62), (2060, 0.8), (2280, 0.6)):
        tree(p, tx, GY - 150, ts, col=(170, 150, 96))
    ground_band(p, col=(238, 210, 172))
    p.poly([(-200, GY + 4), (WW + 200, GY - 26), (WW + 200, GY + 60), (-200, GY + 96)],
           (246, 224, 190), 0)
    for i in range(16):
        xx = -150 + i * 180
        p.line([(xx, GY + 44), (xx + 78, GY + 30)], (222, 194, 160), 4.0)
    for xx in (400, 900, 1500, 2000):
        p.line([(xx, GY + 120), (xx, GY + 70)], (196, 176, 140), 3.0)
        for k in (-1, 0, 1):
            p.line([(xx, GY + 74), (xx + 10 * k, GY + 52)], (196, 176, 140), 3.0)
    wx = 760 + 26 * q
    C.rabbit(p, wx, GY - 4 + 4 * abs(math.sin(2 * math.pi * 1.1 * t)), 1.28,
             ears=0.1 * math.sin(2 * math.pi * 1.1 * t), blink=blink_of(t, 0.6),
             mouth=mouth_of(e, "rabbit"), look=(0.5, 0), arm=0.2)
    C.eagle(p, wx + 205, GY - 2 + 4 * abs(math.sin(2 * math.pi * 1.1 * t + 0.6)), 1.36,
            wings=0.0, blink=blink_of(t, 2.4), mouth=mouth_of(e, "eagle"), look=(-0.5, 0))



@scene("end")
def s_end(p, e):
    q, t = e["q"], e["t"]
    sky_flat(p, (244, 208, 176))
    p.poly([(-200, 906), (WW + 200, 906), (WW + 200, WH + 400), (-200, WH + 400)],
           (240, 198, 162), 0)
    sun(p, 1810, 868, r=206, col=(248, 198, 130), ring=(234, 172, 104))
    hills(p, base=904, amp=86, col=(216, 166, 132), col2=(198, 148, 118))
    for tx, ts in ((150, 0.85), (420, 0.55), (2180, 0.75)):
        tree(p, tx, 900, ts, col=(168, 148, 94))
    p.poly([(-200, 1012), (WW + 200, 1012), (WW + 200, WH + 400), (-200, WH + 400)],
           (228, 176, 142), 0)
    # a road widening toward us
    p.poly([(1290, 1014), (1452, 1014), (2260, WH + 300), (520, WH + 300)],
           (242, 200, 166), 0)
    for i in range(9):
        yy = 1046 + i * 34
        w = 16 + i * 13
        p.line([(1372 - w / 2, yy), (1372 + w / 2, yy)], (232, 190, 156), 5.0)
    # two small figures walking away up the road
    wx = 1310 + 30 * q
    wy = 1014 - 4 * q
    C.rabbit(p, wx, wy, 0.52, blink=0.0, look=(0.5, 0),
             ears=0.08 * math.sin(2 * math.pi * 1.2 * t))
    C.eagle(p, wx + 74, wy, 0.54, wings=0.0, blink=0.0, look=(-0.5, 0))
    for gx in (240, 380, 1900, 2080, 2230):
        p.line([(gx, WH + 60), (gx + 4, WH - 30)], (206, 158, 126), 4.0)
        for k in (-2, 0, 2):
            p.line([(gx, WH - 10), (gx + 16 * k, WH - 68)], (206, 158, 126), 3.4)
    a = min(1.0, q / 0.16)
    e["card"] = (END1, END2, NEXT, a)


# ----------------------------------------------------------------- text
def _text_img(s, size, weight, color):
    return deva._cached_text(s, size, weight, color)


def wrap(s, size, maxw, weight=600):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if _text_img(trial, size, weight, (0, 0, 0)).width <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def world_text(p, e, s, wx, wy, size, weight=700, col=INK):
    """Text positioned in world space, sized by the camera zoom."""
    x, y, k = proj(e, wx, wy)
    if not (0 <= x <= W and 0 <= y <= H):
        return
    deva.draw_text(p, (x, y), s, max(8, int(size * k)), weight, col, "mm")


def card_text(p, line1, line2, sub3=None, alpha=1.0):
    """Big centred storybook card, screen space, on a soft paper panel."""
    size = 92 if len(line1) < 30 else 72
    w1 = _text_img(line1, size, 700, (0, 0, 0)).width
    w2 = _text_img(line2, 54, 600, (0, 0, 0)).width
    pw = min(W - 120, max(w1, w2) + 150)
    ph = 150 + 96 + (70 if sub3 else 0)
    cy = H * 0.26
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(panel)
    d.rounded_rectangle([W / 2 - pw / 2, cy - ph / 2, W / 2 + pw / 2, cy + ph / 2], 28,
                        fill=(250, 244, 228, 238), outline=INK + (255,), width=5)
    p.alpha_composite(panel)
    deva.draw_text(p, (W / 2, cy - 62), line1, size, 700, INK, "mm")
    deva.draw_text(p, (W / 2, cy + 26), line2, 54, 600, (118, 78, 52), "mm")
    if sub3:
        deva.draw_text(p, (W / 2, cy + 96), sub3, 36, 500, (150, 110, 74), "mm")


def subtitle(p, e):
    if e["scene"] == "end":
        return
    ln = e["line"]
    if ln["spk"] == "narr":
        return
    size, lead = 38, 52
    lines = wrap(ln["text"], size, 1620, 600)
    bh = 26 + lead * len(lines)
    y1 = H - 18
    y0 = y1 - bh
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    bw = max(_text_img(l, size, 600, (0, 0, 0)).width for l in lines) + 68
    d.rounded_rectangle([W / 2 - bw / 2, y0, W / 2 + bw / 2, y1], 20,
                        fill=(250, 244, 228, 232), outline=INK + (255,), width=4)
    p.alpha_composite(box)
    for i, l in enumerate(lines):
        deva.draw_text(p, (W / 2, y0 + 13 + lead * (i + 0.5)), l, size, 600, (46, 33, 24), "mm")
    who = NAME.get(ln["spk"])
    if who:
        wimg = _text_img(who, 25, 700, (0, 0, 0))
        tw = wimg.width + 32
        tag = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(tag).rounded_rectangle(
            [W / 2 - tw / 2, y0 - 42, W / 2 + tw / 2, y0 - 8], 13, fill=INK + (255,))
        p.alpha_composite(tag)
        deva.draw_text(p, (W / 2, y0 - 25), who, 25, 700, (250, 244, 228), "mm")


# ----------------------------------------------------------------- frame
starts_end = [1e9, 1e9]


def frame(i, entries, order):
    t = i / FPS
    cur = None
    for e in entries:
        if e["t0"] - 0.9 <= t:
            cur = e
    if cur is None:
        cur = entries[0]
    sc = cur["scene"]
    s0, s1 = cur["s0"], cur["s1"]
    q = min(1.0, max(0.0, (t - s0) / max(0.001, s1 - s0)))
    if t >= starts_end[0]:
        sc = "end"
        s0, s1 = starts_end[0], starts_end[1]
        q = min(1.0, (t - s0) / max(0.001, s1 - s0))
    # talking line = the one whose audio covers t (or the next one, pre-roll)
    line = cur
    for e in entries:
        if e["t0"] - 0.15 <= t:
            line = e
    e = dict(t=t, q=q, spk=line["spk"], line=line, scene=sc)
    e["zoom"] = None
    img = Image.new("RGB", (int(WW * K), int(WH * K)), CREAM)
    p = C.Pen(img, K)
    SCENES[sc](p, e)
    zoom = e["zoom"] or 1.0
    cx, cy = WW / 2, WH / 2
    if sc == "sky":
        cx, cy = 1180, lerp(640, 830, ease(q))
        zoom = lerp(1.0, 1.12, ease(q))
    elif sc == "board":
        cx, cy = lerp(1200, 1400, ease(q)), WH / 2
    elif sc == "turtle":
        cx, cy = lerp(1120, 1330, ease(q)), WH / 2 - 20
    elif sc == "walk":
        cx, cy = lerp(1080, 1320, ease(q)), WH / 2 + 30
    elif sc == "shop":
        cx, cy = lerp(1330, 1460, ease(q)), WH / 2
        zoom = max(zoom, 1.16)
    elif sc == "bench":
        cx, cy = lerp(1210, 1240, ease(q)), WH / 2
        zoom = max(zoom, 1.14)
    elif sc == "board":
        zoom = max(zoom, 1.06)
    elif sc == "turtle":
        zoom = max(zoom, 1.1)
    elif sc == "walk":
        zoom = max(zoom, 1.08)
    elif sc == "end":
        cx, cy = 1400, 700
        zoom = 1.0
    elif sc == "slope":
        cx, cy = lerp(1120, 1300, ease(q)), lerp(700, 740, ease(q))
        zoom = 1.04
    if sc in ("bench", "shop", "board", "turtle", "walk"):
        cy = GY + 34 - 924.0 / (0.8 * zoom)
    v = cam_view(cx, cy, zoom)
    e["view"] = v
    x0, y0, w, h = v
    crop = img.crop((int(x0 * K), int(y0 * K), int((x0 + w) * K), int((y0 + h) * K)))
    out = crop.resize((W, H), Image.LANCZOS).convert("RGBA")
    # redraw the camera-dependent text now that we know the view
    if sc == "board":
        world_text(out, e, "সম্পদ", 1380, 600, 48, 700, (46, 33, 24))
        world_text(out, e, "দায়", 1740, 600, 48, 700, (46, 33, 24))
    if sc == "shop" and e.get("tag"):
        tx, ty = e["tag"]
        world_text(out, e, "মাসে ৫০০", tx, ty, 30, 700, (46, 33, 24))
    if sc == "slope":
        world_text(out, e, "ইঁদুরের দৌড়", 1760, 392, 44, 700, (46, 33, 24))
    if e.get("card"):
        card_text(out, *e["card"])
    subtitle(out, e)
    return out.convert("RGB")


# ----------------------------------------------------------------- render
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=float, default=None)
    ap.add_argument("--seg", nargs=2, type=int, default=None)
    ap.add_argument("--out", default="seg.mp4")
    a = ap.parse_args()
    entries, order, total = build_timeline()
    starts_end[0] = entries[-1]["t0"] + entries[-1]["dur"] + 0.6
    starts_end[1] = total
    n = int(total * FPS)
    print("timeline: %.1fs  %d frames  %d lines" % (total, n, len(entries)))
    if a.still is not None:
        im = frame(int(a.still * FPS), entries, order)
        im.save("/tmp/still-%05.1f.png" % a.still)
        print("wrote /tmp/still-%05.1f.png" % a.still)
        return
    i0, i1 = (0, n) if not a.seg else (a.seg[0], min(a.seg[1], n))
    cmd = [FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium",
           "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    for i in range(i0, i1):
        pr.stdin.write(frame(i, entries, order).tobytes())
        if i % 60 == 0:
            print("  frame %d/%d" % (i, i1), flush=True)
    pr.stdin.close()
    pr.wait()
    print("done", a.out)


if __name__ == "__main__":
    main()
