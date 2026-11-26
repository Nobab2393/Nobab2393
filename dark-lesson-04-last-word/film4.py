"""film4.py — অন্ধকার পাঠ ০৪ · শেষ কথা (The Last Word)

Two brothers, one shop, ten years of winning arguments.

The colour rule carries the film:
    PAPER + INK everywhere. CORAL means exactly one thing — a tally mark on the wall,
    one per argument won — and it never appears as anything else: not on a body, not on
    a caption glyph, not in the end card's type. BLUE appears twice: the cup the younger
    brother leaves behind, and the same cup in the last shot.

    python3 film4.py --still 40
    python3 film4.py --seg 0 1200 --out seg-0.mp4
"""
import argparse
import functools
import math
import os
import re
import subprocess

from PIL import Image, ImageDraw

import deva
from fig4 import (BLUE, INK, INK_D, INK_S, PAPER, PAPER_D, PAPER_M, P, back,
                  clamp, ease, glass, lerp, person, soft)

W, H = 1080, 1920
SS = 1.25
FPS = 24
GY = 1500
TYPE_Y = 210
CAP_Y = 348
SUB_Y = 1742

CORAL = (217, 119, 87)
CORAL_D = (146, 72, 50)
WALL = (219, 214, 202)
WALL_D = (46, 42, 37)
FLOOR = (205, 200, 189)

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "audio")

try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:                                             # pragma: no cover
    FF = "ffmpeg"


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
CLIPS = [
    ("shop", [("narr", "দুই ভাইয়ের একটাই দোকান ছিল। বড় ভাই বলত, ছোট ভাই শুনত।")]),
    ("shop", [("narr", "প্রথম দিন বড় ভাই জিতল। দেয়ালে একটা দাগ পড়ল।")]),
    ("wall", [("narr", "প্রতিটা তর্কে একটা দাগ। দশ বছরে দেয়ালটা প্রায় ভরে গেল।")]),
    ("wall", [("narr", "কেউ একবারও ভাবল না — জমছে কী?")]),
    ("leave", [("narr", "শেষ দিন ছোট ভাই আর তর্ক করল না।")]),
    ("leave", [("bro", "তুমি ঠিক। সবটাতেই তুমি ঠিক। দোকানটা তোমারই থাক।")]),
    ("years", [("narr", "বড় ভাই ভাবল, এইবার সে সত্যিই জিতেছে। দোকান বড় হলো, টাকা বাড়ল।")]),
    ("door", [("narr", "দশ বছর পর তার আর তর্ক করার কেউ নেই। সে ছোট ভাইয়ের বাড়িতে গেল।")]),
    ("door", [("narr", "ভেতরে হাসি, চায়ের শব্দ, অনেকগুলো কণ্ঠ। সে দরজায় হাত তুলল, আর নামিয়ে নিল।")]),
    ("chair", [("narr", "দেয়ালে সব দাগ এখনো আছে। শুধু তর্ক করার লোকটা নেই।")]),
]

CAPTION = {"shop": "দুই ভাই", "wall": "দাগ", "leave": "শেষ দিন",
           "years": "দশ বছর", "door": "দরজা", "chair": "একা", "end": ""}

DARK = {"door", "chair"}

LEAD = 3.2
TAIL = 9.5
GAP = 1.15


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
    for i, sc in enumerate(order):
        if i + 1 < len(order):
            spans[sc][1] = max(spans[sc][1], spans[order[i + 1]][0])
    for sc in order:
        spans[sc][1] += GAP
    return {k: (a, b) for k, (a, b) in spans.items()}, order


# ---------------------------------------------------------------- props
def band(p, y, col):
    p.poly([(-40, y), (W + 40, y), (W + 40, H + 60), (-40, H + 60)], col)


def sky(p, col):
    p.poly([(-40, -40), (W + 40, -40), (W + 40, H + 40), (-40, H + 40)], col)


def mark(p, x, y, s, k=1.0, seed=0, col=CORAL):
    """one tally stroke, hand-made: a stem and a base flick"""
    if k <= 0.03:
        return
    ang = ((seed * 37) % 9 - 4) * 0.026
    c, sn = math.cos(ang), math.sin(ang)

    def r(px, py):
        dx, dy = px - x, py - y
        return (x + dx * c - dy * sn, y + dx * sn + dy * c)

    a = r(x - s * 0.09, y + s * 0.52)
    b = r(x - s * 0.04, y - s * 0.50)
    p.line([a, (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)], col, max(2.0, s * 0.115))
    if k > 0.92:
        p.line([r(x + s * 0.26, y + s * 0.04), r(x - s * 0.14, y + s * 0.30)], col,
               max(2.0, s * 0.17))


def marks_grid(p, x0, y0, cols, rows, dx, dy, count, seed0, s=46, col=CORAL):
    n = int(count)
    for i in range(min(cols * rows, n + 1)):
        k = clamp(count - i)
        cx = x0 + (i % cols) * dx
        cy = y0 + (i // cols) * dy
        mark(p, cx, cy, s, k, seed0 + i, col)


def chair(p, x, y, h, col):
    sw = h * 0.42
    p.poly([(x - sw, y - h * 0.44), (x + sw, y - h * 0.44),
            (x + sw * 1.06, y - h * 0.40), (x - sw * 1.06, y - h * 0.40)], col)
    p.poly([(x - sw * 1.02, y - h * 0.40), (x + sw * 1.02, y - h * 0.40),
            (x + sw * 1.02, y - h * 0.30), (x - sw * 1.02, y - h * 0.30)], col)
    for s in (-1, 1):
        p.line([(x + s * sw * 0.86, y - h * 0.30), (x + s * sw * 0.98, y)], col, max(2.0, h * 0.045))
    p.poly([(x - sw * 0.98, y - h * 0.98), (x - sw * 0.62, y - h * 0.98),
            (x - sw * 0.66, y - h * 0.44), (x - sw * 0.98, y - h * 0.44)], col)


def bulb(p, x, y, on=True):
    p.line([(x, 0), (x, y - 40)], INK_S if on else (60, 55, 48), 4)
    if on:
        p.ell([x - 78, y - 92, x + 78, y + 74], (60, 55, 47))
        p.ell([x - 52, y - 62, x + 52, y + 44], (92, 84, 70))
    p.ell([x - 32, y - 40, x + 32, y + 24], (240, 236, 226) if on else (58, 53, 46))


# ---------------------------------------------------------------- sets
def shop(p, e):
    """The shop, before anything: two men, one counter, a wall that keeps score."""
    q = e["q"]
    sky(p, PAPER)
    p.poly([(0, 296), (W, 258), (W, GY), (0, GY)], WALL)
    p.poly([(0, 296), (W, 258), (W, 288), (0, 326)], (206, 200, 188))
    band(p, GY, FLOOR)

    # the window, and the light it lets in
    p.poly([(64, 500), (232, 490), (232, 796), (64, 806)], PAPER)
    p.line([(148, 495), (148, 801)], WALL, 7)
    p.line([(64, 648), (232, 643)], WALL, 7)

    cnt = clamp((q - 0.12) / 0.5) * 6.4
    marks_grid(p, 636, 452, 3, 3, 104, 96, max(0.0, cnt), 5)

    # the two of them, turned into each other
    person(p, 716, GY, 668, INK, shawl=(96, 90, 78), lean=-0.34,
           hand_r=(0.10, -0.14), hand_l=(-0.02, 0.26), feat=1.10)
    person(p, 392, GY, 628, INK, cap=True, lean=0.30,
           hand_r=(0.02, 0.22), hand_l=(-0.06, 0.24), feat=0.96)

    # the counter in front of both
    p.poly([(214, 1252), (872, 1234), (872, GY + 8), (214, GY + 8)], (198, 193, 181))
    p.poly([(214, 1252), (872, 1234), (872, 1270), (214, 1288)], (186, 181, 169))
    for i, gx in enumerate((300, 792)):
        glass(p, gx, 1252, 54, None, INK)


def wall(p, e):
    """Ten years later, close enough to read the wall."""
    q = e["q"]
    sky(p, WALL)
    p.poly([(0, 0), (W, 0), (W, GY + 40), (0, GY + 40)],
           (226, 221, 209))
    band(p, GY, FLOOR)
    cnt = 8 + clamp((q - 0.02) / 0.72) * 34
    marks_grid(p, 96, 372, 6, 7, 150, 138, cnt, 21, s=54)
    # the two of them, small, seen from behind at the bottom of the frame
    person(p, 250, GY + 96, 420, INK, hand_r=(0.04, 0.30), hand_l=(-0.04, 0.30))
    person(p, 812, GY + 96, 396, INK, cap=True, hand_r=(0.04, 0.30), hand_l=(-0.04, 0.30))


def leave(p, e):
    """He says the sentence that ends the arguments, then walks into the light."""
    t, q = e["t"], e["q"]
    sky(p, PAPER)
    p.poly([(0, 300), (W, 266), (W, GY), (0, GY)], WALL)
    band(p, GY, FLOOR)

    # the door, open, and the light lying on the floor
    p.poly([(676, 386), (1010, 356), (1010, GY), (676, GY)], (206, 200, 188))
    p.poly([(700, 402), (1010, 372), (1010, GY), (700, GY)], (247, 244, 236))
    p.poly([(700, 402), (1010, 372), (1010, 402), (700, 432)], (232, 228, 218))
    p.poly([(1010, GY), (700, GY), (700, 1560), (620, 1660), (1010, 1660)], (240, 237, 228))

    # the elder, still at the counter
    person(p, 258, GY, 648, INK, shawl=(96, 90, 78), lean=-0.06,
           hand_r=(0.02, 0.26), hand_l=(-0.02, 0.28), feat=1.10)

    # the younger, walking out
    wx = lerp(430, 838, ease(clamp(q * 1.05)))
    person(p, wx, GY, 610, INK, cap=True, walk=t * 2.6,
           hand_r=(0.04, 0.26), hand_l=(-0.04, 0.26), feat=0.96)

    # the counter, and the cup he leaves on it
    p.poly([(196, 1252), (660, 1238), (660, GY + 8), (196, GY + 8)], (198, 193, 181))
    p.poly([(196, 1252), (660, 1238), (660, 1274), (196, 1290)], (186, 181, 169))
    k = clamp((q - 0.62) / 0.18)
    if k > 0.02:
        glass(p, 560, 1240, 54, BLUE, INK)


def years(p, e):
    """The shop got bigger. The wall got fuller. The other chair stayed empty."""
    q = e["q"]
    sky(p, PAPER_M)
    p.poly([(0, 276), (W, 244), (W, GY), (0, GY)], (206, 201, 189))
    band(p, GY, (188, 183, 171))

    cnt = 40 + clamp((q - 0.05) / 0.6) * 14
    marks_grid(p, 70, 330, 8, 6, 124, 128, cnt, 41, s=44)

    # sacks in the corner: the shop has done well
    for i in range(3):
        x0, y0 = 760 + (i % 2) * 96, GY - 40 - i * 74
        p.poly([(x0, y0 - 96), (x0 + 168, y0 - 104), (x0 + 158, y0), (x0 - 6, y0 + 6)],
               (176, 171, 159))
        p.line([(x0 + 8, y0 - 62), (x0 + 150, y0 - 68)], (150, 145, 134), 5)

    # one chair, one man
    chair(p, 250, GY, 320, (176, 171, 159))
    person(p, 640, GY, 648, INK, shawl=(96, 90, 78), lean=0.10,
           hand_r=(0.02, 0.24), hand_l=(-0.02, 0.26), feat=1.10)

    p.poly([(520, 1252), (1010, 1238), (1010, GY + 8), (520, GY + 8)], (190, 185, 173))
    p.poly([(520, 1252), (1010, 1238), (1010, 1274), (520, 1290)], (178, 173, 161))
    glass(p, 940, 1238, 52, None, INK)


def door(p, e):
    """Outside his brother's house, ten years late."""
    t, q = e["t"], e["q"]
    sky(p, INK_D)
    band(p, GY, (18, 17, 15))

    # the lit doorway
    p.poly([(618, 452), (932, 420), (932, GY), (618, GY)], (34, 31, 27))
    p.poly([(646, 486), (906, 458), (906, GY), (646, GY)], (232, 228, 218))
    p.poly([(646, GY), (906, GY), (960, 1660), (600, 1660)], (44, 40, 34))

    # two small figures inside, and the sound of them
    person(p, 726, GY - 8, 300, (128, 122, 111), hand_r=(0.04, 0.28), hand_l=(-0.04, 0.28))
    person(p, 838, GY - 8, 262, (128, 122, 111), cap=True,
           hand_r=(0.04, 0.28), hand_l=(-0.04, 0.28))
    for i in range(4):
        ph = (q * 1.4 + i * 0.22) % 1.0
        r = 60 + ph * 150
        a = 0.55 - ph * 0.45
        col = (int(232 * a + 44 * (1 - a)), int(228 * a + 40 * (1 - a)), int(218 * a + 34 * (1 - a)))
        p.arc([742 - r, 700 - r * 0.7, 742 + r, 700 + r * 0.7], 300, 360, col, 5)

    # the elder, outside, one hand up and not knocking
    person(p, 360, GY, 640, (10, 9, 8), shawl=(30, 27, 24), lean=0.16,
           hand_r=(0.17, -0.17), hand_l=(-0.04, 0.26), feat=1.08)
    # his shadow, thrown away from the door
    p.poly([(300, GY), (250, GY), (140, GY + 40), (330, GY + 40)], (18, 17, 15))


def chair_shot(p, e):
    """Back home. The wall, the chair, the cup."""
    t, q = e["t"], e["q"]
    sky(p, INK_D)
    p.poly([(0, 300), (W, 274), (W, GY), (0, GY)], WALL_D)
    band(p, GY, (16, 15, 13))
    bulb(p, 540, 430, True)
    # the wall, still full of them, dim in this light
    marks_grid(p, 96, 480, 7, 6, 132, 132, 46, 61, s=44, col=(120, 62, 44))
    chair(p, 300, GY, 330, (58, 53, 46))
    person(p, 640, GY, 648, (10, 9, 8), sit=True, lean=0.06, hunch=0.5,
           hand_r=(0.02, 0.20), hand_l=(-0.02, 0.22), feat=1.06)
    p.poly([(520, 1258), (1010, 1244), (1010, GY), (520, GY)], (36, 33, 29))
    p.poly([(520, 1258), (1010, 1244), (1010, 1278), (520, 1292)], (52, 47, 41))
    glass(p, 940, 1246, 52, BLUE, (120, 114, 102))


SETS = {"shop": shop, "wall": wall, "leave": leave, "years": years,
        "door": door, "chair": chair_shot}


# ---------------------------------------------------------------- cards
def title_card(base, q):
    T(base, (96, TYPE_Y), "অন্ধকার পাঠ", 32, INK_S, 500)
    T(base, (96, TYPE_Y + 44), "০৪", 32, INK_S, 700)
    T(base, (532, 706), "০৪", 800, (210, 205, 193), 700, anchor="mm")
    T(base, (96, 1180), "শেষ কথা", 138, INK, 700, anchor="lm")
    T(base, (98, 1290), "The Last Word", 44, INK_S, 500, anchor="lm")
    T(base, (96, 1462), "তর্কে জিতলে একজন জেতে।", 40, INK, 500, anchor="lm")
    T(base, (96, 1524), "সম্পর্কে হারলে দুজন হারে।", 40, INK, 500, anchor="lm")
    bq = clamp((q - 0.5) / 0.4)
    if bq > 0:
        ImageDraw.Draw(base).rectangle([96, 1600, 96 + 108 * bq, 1606], fill=CORAL + (255,))


def end_card(base, q):
    T(base, (96, TYPE_Y), "অন্ধকার পাঠ · ০৪", 30, (128, 122, 111), 500)
    T(base, (96, 676), "দেয়ালে দাগ", 104, (238, 234, 224), 700, anchor="lm")
    T(base, (96, 796), "রয়ে গেল।", 104, (238, 234, 224), 700, anchor="lm")
    T(base, (96, 1002), "তর্ক করার লোকটা", 62, (198, 193, 181), 500, anchor="lm")
    T(base, (96, 1090), "রইল না।", 62, (198, 193, 181), 500, anchor="lm")
    # one last mark on the wall, and the cup
    mk = clamp((q - 0.30) / 0.25)
    if mk > 0:
        mark(P(base, 1.0), 96 + 34, 1284, 116, mk, 3)
    bq = clamp((q - 0.46) / 0.30)
    d = ImageDraw.Draw(base)
    if bq > 0:
        cy = 1430
        r = 15 * back(bq)
        d.ellipse([96 - r, cy - r, 96 + r, cy + r], fill=BLUE + (255,))
        d.line([(80, cy + 52), (96, cy + 80), (112, cy + 52)], fill=BLUE + (255,),
               width=5, joint="curve")
    T(base, (96, 1606), "তুমি দেখলে — এখন কী করবে?", 36, (150, 144, 132), 500, anchor="lm")


# ---------------------------------------------------------------- frame
def frame_at(t, entries, total, spans):
    if t < LEAD:
        base = Image.new("RGBA", (W, H), PAPER + (255,))
        title_card(base, t / LEAD)
        return base
    if t > total - TAIL + 0.15:
        base = Image.new("RGBA", (W, H), (24, 22, 19, 255))
        end_card(base, (t - (total - TAIL)) / TAIL)
        return base

    cur = entries[-1]
    for ent in entries:
        if ent["t0"] - 1e-6 <= t <= ent["t0"] + ent["dur"] + GAP:
            cur = ent
            break
    sc = cur["scene"]
    a, b = spans[sc]
    local = clamp((t - a) / max(0.45, b - a))

    art = Image.new("RGB", (int(W * SS), int(H * SS)), PAPER)
    p = P(art, SS)
    SETS[sc](p, {"t": t, "q": local, "spk": cur["spk"], "line": cur["i"], "scene": sc})
    art = art.resize((W, H), Image.LANCZOS).convert("RGBA")

    dark = sc in DARK
    cap = CAPTION.get(sc, "")
    ink_c = (236, 232, 222) if dark else INK
    if cap:
        T(art, (96, TYPE_Y), "অন্ধকার পাঠ · ০৪", 28,
          (150, 144, 132) if dark else INK_S, 500)
        T(art, (96, CAP_Y), cap, 126, ink_c, 700)

    if cur["spk"] != "narr":
        T(art, (96, SUB_Y - 62), "ছোট ভাই", 28, CORAL if not dark else (196, 108, 78), 700)
    lines = wrap(cur["text"], 38, 910)
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
    out = out or os.path.join(HERE, "film4.mp4")
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
