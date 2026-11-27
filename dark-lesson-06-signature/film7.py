"""film7.py — অন্ধকার পাঠ ০৬ · সই (কথ্য সংস্করণ).

Five cards, five voices, ten turns. A family sits down to sign away the house the old man
was born in; the promise that he may stay is written into the deed and, as the paper man
says out loud before he signs, will not hold in any court.

The mouths are the audio: `envelope()` turns each take into a 24 fps loudness curve and the
speaker's mouth is drawn from that number. Everything else is a head, a lean and a table.

    python3 film7.py --still 40 --out frames/x.png
    python3 film7.py --seg 0 620 --out /tmp/a.mp4
"""
import functools
import math
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

import deva
import sprites7
from fig5 import PAPER, P, clamp, lerp, soft

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(HERE, "audio")

try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:                                            # pragma: no cover
    FF = "ffmpeg"

W, H = 1080, 1920
SS = 1.2
FPS = 24

TYPE_Y = 190
CAP_Y = 285
TABLE = 1420          # the strip the busts stand behind
BOT = 1490            # where every bust is cut off
LABEL_Y = 1540
SUB_Y = 1660

INK = (26, 23, 20)
INK_S = (92, 88, 80)
CREAM = (245, 241, 231)

SAND = (243, 227, 195)
SAND_D = (227, 207, 160)
SAGE = (215, 235, 208)
SAGE_D = (185, 217, 174)
SAGE_DD = (162, 198, 152)
PINK = (246, 217, 227)
PINK_D = (232, 185, 204)
PINK_DD = (214, 160, 182)
LAV = (230, 224, 243)
LAV_D = (207, 196, 232)
LAV_DD = (186, 174, 214)
SUN = (247, 215, 116)
RED = (200, 55, 45)
WOOD = (214, 168, 124)
WOOD_D = (188, 143, 101)
PAPER_W = (250, 248, 242)

SKIN = {"dada": (185, 130, 89), "chele": (165, 106, 68), "bou": (198, 138, 94),
        "natni": (198, 138, 94), "kagojwala": (208, 154, 110)}
PATCH = {"dada": (242, 242, 242), "chele": (165, 106, 68), "bou": (198, 138, 94),
         "natni": (198, 138, 94), "kagojwala": (208, 154, 110)}

LEAD = 5.0
TAIL = 13.0
LAST_END = 0.0          # filled in after the timeline is built
GAP = 1.55          # between turns, inside a scene
SCENE_GAP = 2.8


def T(base, xy, text, size, col, weight=700, anchor="lm"):
    deva.draw_text(base, xy, text, size, weight, col, anchor=anchor)


def TC(base, xy, text, size, col, weight=700, anchor="lm"):
    """Type on a supersampled card, in design units — P() scales, T() does not."""
    deva.draw_text(base, (xy[0] * SS, xy[1] * SS), text, size * SS, weight, col, anchor=anchor)


@functools.lru_cache(maxsize=400)
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
# (speaker, take, extra silence before this turn)
SCENES = [
    ("room", "ঘর", [("dada", 1, 0.0), ("chele", 2, 0.0), ("bou", 3, 0.4)]),
    ("yard", "উঠোন", [("natni", 4, 0.0), ("kagojwala", 5, 3.4), ("dada", 6, 1.2)]),
    ("dusk", "সন্ধ্যা", [("chele", 7, 0.0), ("natni", 8, 0.0), ("kagojwala", 9, 0.8)]),
    ("sign", "সই", [("dada", 10, 2.6)]),
]

LABEL = {"dada": "দাদা", "chele": "ছেলে", "bou": "বৌমা", "natni": "নাতনি",
         "kagojwala": "কাগজওয়ালা"}

TEXT = {
    1: "এই টেবিলে আমার বাবা খেতেন। এই ঘরে তিন পুরুষ মানুষ হয়েছে। আজ তোরা কাগজ নিয়ে এসেছিস, চা নিয়ে আসিস নাই।",
    2: "বাবা, ঋণটা আমার নামে। ব্যাংক তিন মাস ধরে তাড়া দিচ্ছে। বাড়ি বেচে দিলে সব শোধ, তারপর শহরে নতুন ফ্ল্যাট।",
    3: "আমার কিছু চাই না। কিন্তু এই ঘরে আমি চৌদ্দ বছর আছি। সই করার আগে আমার নামটা অন্তত শোনো।",
    4: "দাদা, সই করলে তুমি থাকবে কোথায়? এই ঘরে তুমি থাকবে না, তাহলে কে থাকবে?",
    5: "দাদা, সইটা করুন। কাগজ সব ঠিক আছে, আমি নিজে দেখেছি। দেরি করলে দাম আরও কমবে, শুনে রাখুন।",
    6: "যেই ঘরে তোর দাদি শেষ নিঃশ্বাস নিয়েছে, আমি সেই ঘরেই থাকব। আমার আর কোথাও জল খাওয়ার জায়গা নাই।",
    7: "বাবা, আমার কিছু করার নাই। মেয়ের স্কুলের টাকা বাকি, বাড়িওয়ালা উঠোনে দাঁড়িয়ে। আমাকে বাঁচতে দে।",
    8: "তাহলে বেচো। কিন্তু কাগজে লেখো, দাদা এই ঘরে থাকবে। শেষ দিন পর্যন্ত, শেষ নিঃশ্বাস পর্যন্ত।",
    9: "এই শর্তটা কাগজে লেখা যাবে, কিন্তু আদালতে টিকবে না। দাদা, বুঝে সই করেন। আমার কথা রাখতে হবে না।",
    10: "তাহলে সই করি। আমার নামে ঘর থাকল না, কারও দয়ার ঘরে থাকব না। সই করলাম।",
}


def _dur(path):
    if not os.path.exists(path):
        return None
    err = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", err)
    if not m:
        return None
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
    r = np.convolve(r, np.array([0.15, 0.7, 0.15]), mode="same")
    top = np.percentile(r, 96) + 1e-9
    r = np.clip(r / top, 0, 1)
    r[r < 0.10] = r[r < 0.10] * 0.3
    return tuple(float(v) for v in r)


def build_timeline():
    t, entries = LEAD, []
    for si, (scene, cap, turns) in enumerate(SCENES):
        for ti, (who, clip, pre) in enumerate(turns):
            t += pre
            d = _dur(os.path.join(AUD, "d%02d.mp3" % clip)) or 8.0
            entries.append({"scene": scene, "cap": cap, "who": who, "clip": clip,
                            "text": TEXT[clip], "t0": t, "dur": d, "si": si})
            t += d
            last = (si == len(SCENES) - 1) and (ti == len(turns) - 1)
            t += (SCENE_GAP if ti == len(turns) - 1 else GAP) if not last else 0.0
    return entries, t + TAIL


ENTRIES, TOTAL = build_timeline()
LAST_END = ENTRIES[-1]["t0"] + ENTRIES[-1]["dur"]
PAPER_A = LAST_END + 0.7
CARD_A = PAPER_A + 4.4
SPAN = {}
for e in ENTRIES:
    a, b = SPAN.get(e["scene"], (e["t0"], e["t0"] + e["dur"]))
    SPAN[e["scene"]] = (min(a, e["t0"]), max(b, e["t0"] + e["dur"]))


def active(t):
    for e in ENTRIES:
        if e["t0"] - 0.15 <= t < e["t0"] + e["dur"] + 0.35:
            return e
    return None


def mouth_of(t):
    e = active(t)
    if not e:
        return None, 0.0
    i = int((t - e["t0"]) * FPS)
    env = envelope(e["clip"])
    if i < 0:
        return e["who"], 0.0
    return e["who"], env[min(i, len(env) - 1)]


def caption_at(t):
    """Which line belongs on screen right now — including the beats between turns."""
    prev = None
    for e in ENTRIES:
        if t < e["t0"] - 0.10:
            return prev
        prev = e
    return prev


def scene_at(t):
    for scene, cap, turns in SCENES:
        a, b = SPAN[scene]
        if a - 0.4 <= t < b + 0.9:
            return scene, cap
    return "sign", "সই"


# ---------------------------------------------------------------- people
HEIGHT = {"dada": 900, "chele": 880, "bou": 860, "natni": 840,
          "kagojwala": 850}


def actor(art, who, x, y, h=None, mouth=0.0, k=1.0, lean=0.0, sess=0.0, alpha=1.0):
    sp = sprites7.sprite(who)
    m = sprites7.MOUTH[who]
    h = h or HEIGHT[who]
    kk = h / sp.height
    w = max(1, int(round(sp.width * kk)))
    img = sp.resize((w, max(1, int(round(h * (1.0 + 0.006 * sess))))), Image.LANCZOS)
    sx = img.width / sp.width
    cx, cy = m["x"] * sx, (m["y"] + m.get("dy", 0)) * sx
    mw, mh = m["w"] * sx, m["h"] * sx

    if mouth > 0.05:
        d = ImageDraw.Draw(img)
        # cover the smile that is drawn into the card, then open a mouth on top of it
        d.ellipse([cx - mw * 0.52, cy - mh * 0.62, cx + mw * 0.52, cy + mh * 0.66],
                  fill=PATCH[who] + (255,))
        ow = max(4.0, mw * (0.50 + 0.36 * mouth))
        oh = max(3.0, mh * (0.12 + 0.66 * mouth))
        d.ellipse([cx - ow / 2, cy - oh * 0.40, cx + ow / 2, cy + oh * 0.60],
                  fill=INK + (255,))
        if mouth > 0.30:                       # a tongue-tip, only when it is really open
            d.ellipse([cx - ow * 0.22, cy + oh * 0.16, cx + ow * 0.22, cy + oh * 0.48],
                      fill=(150, 60, 58, 255))
    if k < 0.999:
        img = sprites7.tint(img, k)
    if lean:
        img = img.rotate(lean, resample=Image.BICUBIC,
                         center=(img.width / 2, img.height), expand=False)
    if alpha < 0.999:
        img.putalpha(img.split()[3].point(lambda v: int(v * alpha)))
    art.alpha_composite(img, (int(round(x - img.width / 2)), int(round(y - img.height))))


# ---------------------------------------------------------------- landscape
def sky(p, col):
    p.poly([(0, 0), (W, 0), (W, H), (0, H)], col)


def sun(p, x, y, r, col=SUN):
    p.ell([x - r, y - r, x + r, y + r], col)


def cloud(p, x, y, s=1.0, col=(255, 255, 255)):
    p.ell([x - 92 * s, y - 30 * s, x + 60 * s, y + 26 * s], col)
    p.ell([x - 20 * s, y - 46 * s, x + 118 * s, y + 22 * s], col)


def hills(p, y, c1, c2):
    p.poly([(0, y + 90), (0, y), (240, y - 96), (520, y - 26), (760, y - 92),
            (1010, y - 18), (W, y - 40), (W, H), (0, H)], c1)
    p.poly([(0, y + 210), (0, y + 150), (300, y + 62), (620, y + 140),
            (900, y + 80), (W, y + 130), (W, H), (0, H)], c2)


def floorline(p, col):
    p.poly([(0, TABLE), (W, TABLE), (W, H), (0, H)], col)


def edge(p, col):
    """The strip the busts are tucked behind — a table edge, or a courtyard wall."""
    p.poly([(0, TABLE - 22), (W, TABLE - 22), (W, TABLE + 70), (0, TABLE + 70)], col)
    p.line([(0, TABLE - 22), (W, TABLE - 22)], INK, 5)


def band(p, dark=INK):
    p.poly([(0, BOT), (W, BOT), (W, H), (0, H)], dark)


def window(p, x0, y0, x1, y1, col, sunx=None):
    p.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], col)
    if sunx:
        p.ell([sunx - 46, y0 + 60, sunx + 46, y0 + 152], SUN)
    p.line([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], INK, 7)
    p.line([(x0, (y0 + y1) // 2), (x1, (y0 + y1) // 2)], INK, 6)
    p.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], INK, 6)


def paper(p, x, y, w=340, h=190, signed=0.0):
    """The deed: one sheet, four clauses, and a line at the bottom for a name."""
    p.poly([(x, y), (x + w, y - 10), (x + w, y + h - 10), (x, y + h)], PAPER_W)
    p.line([(x, y), (x + w, y - 10), (x + w, y + h - 10), (x, y + h), (x, y)], INK, 5)
    step = max(24, int(h * 0.13))
    for i in range(4):
        yy = y + int(h * 0.18) + i * step
        p.line([(x + 26, yy), (x + w - 40 - (i % 2) * 40, yy - 6)], (150, 146, 136), 5)
    p.line([(x + 26, y + h - int(h * 0.16)), (x + 150, y + h - int(h * 0.18))],
           (150, 146, 136), 5)
    if signed > 0:
        # a signature: a looping pen nib that settles into a long underline
        base = y + h - int(h * 0.13)
        n = max(2, int(26 * min(1.0, signed * 1.4)))
        pts = []
        for i in range(n):
            u = i / 26.0
            px = x + int(w * (0.07 + u * 0.42))
            py = base + int(h * (0.030 * math.sin(u * 19.0) - 0.012 * math.sin(u * 7.0)))
            pts.append((px, py))
        for i in range(len(pts) - 1):
            p.line([pts[i], pts[i + 1]], INK, 7)
        if signed > 0.75:
            p.line([(x + int(w * 0.09), base + int(h * 0.06)),
                    (x + int(w * 0.56), base + int(h * 0.055))], INK, 5)
        if signed > 0.55:
            # the notary's red seal
            sx, sy, sw = x + int(w * 0.74), y + int(h * 0.66), int(w * 0.14)
            p.poly([(sx, sy), (sx + sw, sy - 4), (sx + sw, sy + sw), (sx, sy + sw + 4)], RED)
            p.ring([sx + sw * 0.18, sy + sw * 0.18, sx + sw * 0.82, sy + sw * 0.82], 4, PAPER_W)


def lamp(p, x, y, top=330):
    p.line([(x, top), (x, y - 40)], INK, 5)
    p.ell([x - 9, top - 9, x + 9, top + 9], INK)
    p.poly([(x - 54, y - 44), (x + 54, y - 44), (x + 34, y - 10), (x - 34, y - 10)], INK)
    p.ell([x - 20, y - 22, x + 20, y + 14], (255, 236, 176))


# ---------------------------------------------------------------- sets
def set_room(p, t, e):
    sky(p, SAND)
    floorline(p, SAND_D)
    p.line([(0, TABLE - 22), (W, TABLE - 22)], INK, 0)
    window(p, 96, 430, 396, 900, SAGE, sunx=330)
    lamp(p, 700, 560)
    edge(p, WOOD)
    band(p)


def set_yard(p, t, e):
    sky(p, SAGE)
    sun(p, 930, 300, 96)
    cloud(p, 236, 500, 0.95)
    hills(p, 1120, SAGE_D, SAGE_DD)
    p.poly([(0, TABLE - 96), (W, TABLE - 96), (W, TABLE - 22), (0, TABLE - 22)], SAGE_DD)
    edge(p, SAGE_DD)
    band(p)


def set_dusk(p, t, e):
    sky(p, PINK)
    sun(p, 540, 1180, 150, (247, 190, 120))
    cloud(p, 210, 470, 1.1, (255, 250, 252))
    hills(p, 1250, PINK_D, PINK_DD)
    edge(p, WOOD_D)
    band(p)


def set_sign(p, t, e):
    sky(p, LAV)
    sun(p, 830, 1240, 140, (247, 196, 130))
    cloud(p, 240, 520, 1.2, (252, 250, 255))
    hills(p, 1290, LAV_D, LAV_DD)
    edge(p, WOOD_D)
    band(p)


SETS = {"room": set_room, "yard": set_yard, "dusk": set_dusk, "sign": set_sign}


def stage(scene, t, e):
    who, mo = mouth_of(t)
    out = []

    def put(name, x, h, alpha=1.0, lean_sign=-1.0):
        lean = 0.0
        if e and who == name:
            lean = lean_sign * 1.2 * soft((t - e["t0"]) / 0.5)
        out.append(dict(who=name, x=x, h=h, mouth=mo if who == name else 0.0,
                        lean=lean, sess=0.7 * math.sin(t * 1.9 + h * 0.01),
                        alpha=alpha))

    if scene == "room":
        put("dada", 330, 900)
        put("chele", 782, 880, lean_sign=1.0)
        if e and e["clip"] >= 3:
            u = clamp((t - (e["t0"] - 0.9)) / 1.5)
            put("bou", lerp(1260, 1006, soft(u)), 860, lean_sign=-1.0)
    elif scene == "yard":
        put("natni", 400, 830, lean_sign=1.0)
        if e:
            if e["clip"] >= 5:
                u = clamp((t - (e["t0"] - 1.2)) / 1.6)
                put("kagojwala", lerp(1300, 880, soft(u)), 850)
            if e["clip"] >= 6:
                u = clamp((t - (e["t0"] - 1.2)) / 1.6)
                put("dada", lerp(-300, 206, soft(u)), 870, lean_sign=1.0)
    elif scene == "dusk":
        put("chele", 320, 870)
        put("natni", 676, 830, lean_sign=1.0)
        put("kagojwala", 1000, 850)
    elif scene == "sign":
        put("dada", 540, 1120, lean_sign=-1.0)
    return out


# ---------------------------------------------------------------- cards
def title_card(t, q):
    art = Image.new("RGBA", (int(W * SS), int(H * SS)), SAND + (255,))
    p = P(art, SS)
    sun(p, 900, 520, 150)
    cloud(p, 230, 470, 1.0)
    hills(p, 1560, SAND_D, (216, 194, 146))
    TC(art, (96, 250), "অন্ধকার পাঠ", 34, INK_S, 500)
    TC(art, (96, 300), "০৬", 34, INK, 700)
    TC(art, (540, 900), "০৬", 620, (230, 212, 172), 700, anchor="mm")
    TC(art, (96, 1180), "সই", 176, INK, 700)
    TC(art, (100, 1290), "The Signature", 46, INK_S, 500)
    TC(art, (96, 1430), "কথ্য সংস্করণ · পাঁচ কণ্ঠ", 34, INK_S, 500)
    TC(art, (96, 1500), "কাগজে সব ঠিক লেখা ছিল।", 40, INK, 500)
    TC(art, (96, 1556), "মানুষটার জায়গাটা লেখা ছিল না।", 40, INK, 500)
    _ = (t, q)
    return art.resize((W, H), Image.LANCZOS).convert("RGBA")


def end_card(t, q):
    art = Image.new("RGBA", (int(W * SS), int(H * SS)), INK + (255,))
    p = P(art, SS)
    TC(art, (96, 380), "বাড়ি বেচা হলো।", 92, CREAM, 700)
    TC(art, (96, 500), "ঋণ শোধ হলো।", 92, CREAM, 700)
    TC(art, (96, 640), "শর্তটা কাগজে লেখা হলো।", 52, (176, 170, 158), 500)
    TC(art, (96, 704), "আইনে টিকল না।", 52, (176, 170, 158), 500)
    p.line([(96, 830), (984, 830)], (58, 54, 48), 4)
    paper(p, 96, 900, 380, 210, signed=1.0)
    # the red shawl, folded on the table
    p.poly([(760, 906), (868, 898), (878, 1122), (770, 1130)], RED)
    p.line([(792, 906), (800, 1126)], (245, 241, 231), 5)
    TC(art, (96, 1270), "যে ঘরে মানুষ বড় হয়,", 44, (198, 192, 178), 500)
    TC(art, (96, 1334), "সেই ঘর কোন কাগজে থাকে না।", 44, (198, 192, 178), 500)
    TC(art, (96, 1560), "তুমি কোন কাগজে সই করবে?", 46, CREAM, 700)
    _ = (t, q)
    return art.resize((W, H), Image.LANCZOS).convert("RGBA")


def paper_card(t):
    """The deed, alone, while the signature is drawn on it."""
    art = Image.new("RGB", (W, H), INK)
    p = P(art, 1.0)
    u = clamp((t - PAPER_A - 0.5) / 2.4)
    paper(p, 96, 620, 888, 500, signed=u)
    if 0.02 < u < 1.0:                       # the nib, still on the page
        x = 150 + 770 * u
        p.line([(x + 26, 1062), (x + 56, 1096)], INK, 12)
    return art.convert("RGBA")


def frame(t):
    if t < LEAD:
        return title_card(t, clamp(t / LEAD))
    if t >= CARD_A:
        return end_card(t, clamp((t - CARD_A) / max(1e-6, TOTAL - CARD_A)))
    if t >= PAPER_A:
        return paper_card(t)

    scene, cap = scene_at(t)
    e = active(t)

    art = Image.new("RGB", (int(W * SS), int(H * SS)), SAND)
    p = P(art, SS)
    SETS[scene](p, t, e)
    art = art.resize((W, H), Image.LANCZOS).convert("RGBA")

    for a_ in stage(scene, t, e):
        actor(art, a_["who"], a_["x"], BOT, h=a_["h"], mouth=a_["mouth"],
              lean=a_["lean"], sess=a_["sess"], alpha=a_["alpha"])

    fp = P(art, 1.0)
    if scene == "sign" and e and e["clip"] == 10:
        # his hand comes down on the table as he decides — nothing else needed
        u = clamp((t - (e["t0"] + e["dur"] - 2.6)) / 1.2)
        fp.poly([(0, 1820), (W, 1820), (W, 1920), (0, 1920)], (18, 16, 14)) if u > 1 else None

    T(art, (92, TYPE_Y), "অন্ধকার পাঠ · ০৬", 26, INK_S, 500)
    T(art, (92, CAP_Y), cap, 104, INK, 700)
    e = caption_at(t) or e
    if e:
        lab = LABEL[e["who"]]
        lw = deva.layout(lab, 28)[1]
        ImageDraw.Draw(art).rectangle([84, LABEL_Y - 20, 84 + lw + 22, LABEL_Y + 24],
                                      fill=RED + (255,))
        T(art, (95, LABEL_Y + 2), lab, 28, CREAM, 700)
        lines = wrap(e["text"], 37, 916)
        yy = SUB_Y - 40 * (len(lines) - 1)
        for ln in lines:
            T(art, (92, yy), ln, 37, (236, 232, 222), 500)
            yy += 46
    return art


def render(still=None, seg=None, out=None):
    n = int(round(TOTAL * FPS))
    print("timeline: %.2fs  %d frames  %d turns" % (TOTAL, n, len(ENTRIES)))
    if still is not None:
        path = out or "frames/still.png"
        frame(float(still)).convert("RGB").save(path)
        print("wrote", path)
        return
    a, b = seg if seg else (0, n)
    out = out or "dark-lesson-06-signature-1080x1920.mp4"
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
