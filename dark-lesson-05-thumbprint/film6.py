"""film6.py — অন্ধকার পাঠ ০৫ · আঙুলের ছাপ (কথ্য সংস্করণ).

Five faces, five voices, ten turns of dialogue, no narrator. The thumbprint is the whole
film: one coral oval in a ledger, in a shop, and a man who cannot read what he signed.

The mouths follow the audio. `envelope()` turns each take into a 24 fps loudness curve and
the speaker's mouth is drawn from that number — pause, and it closes.

    python3 film6.py --still 40 --out frames/x.png
    python3 film6.py --seg 0 620 --out /tmp/a.mp4
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
import sprites6
from fig5 import INK, INK_D, INK_S, PAPER, P, clamp, lerp, soft

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
GY = 1560
TYPE_Y = 196
CAP_Y = 286
SUB_Y = 1748

WALL = (228, 224, 213)
WALL_D = (188, 182, 170)
CEIL = (206, 200, 187)
CEIL_D = (166, 160, 148)
MID = (142, 136, 124)
CORAL = (217, 119, 87)
CORAL_D = (168, 90, 62)
WHITE = (238, 235, 226)
FLOOR = (196, 190, 177)
FLOOR_D = (158, 152, 141)
WOOD = (150, 143, 130)
WOOD_D = (132, 126, 115)
LIP = (224, 219, 207)
NIGHT_W = (34, 31, 27)
NIGHT_F = (22, 20, 18)

SKIN = {who: sprites6.skin(who) for who in sprites6.FILE}
INK_MOUTH = (26, 23, 20)

LEAD = 3.6
TAIL = 10.2


def T(base, xy, text, size, col, weight=700, anchor="lm"):
    deva.draw_text(base, xy, text, size, weight, col, anchor=anchor)


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
SCENES = [
    ("shop", "দোকান", [("shopkeeper", 1), ("puller", 2), ("student", 3)]),
    ("deadline", "সাত মাস পর", [("puller", 4), ("shopkeeper", 5)]),
    ("street", "রাতের রাস্তা", [("student", 6), ("presenter", 7), ("uncle", 8)]),
    ("dark", "পরের সকাল", [("shopkeeper", 9), ("presenter", 10)]),
]

LABEL = {"shopkeeper": "দোকানদার", "puller": "রিকশাচালক", "student": "মেয়ে",
         "presenter": "ভিডিওওয়ালা", "uncle": "চাচা"}

TEXT = {
    1: "বাকিতে নিবি? তা হলে খাতায় আঙুলের ছাপ দে। চার মাসের বাকি, একসাথে শোধ দিবি। কথা এখন, টাকা পরে।",
    2: "আমি পড়তে জানি না, বৌ। তুই যা বলছিস, ঠিকই বলছিস। চার মাস পরে দেখব, আসলেই তো কম টাকা। আঙুলের ছাপ দিলাম।",
    3: "আব্বা, ওই কাগজটা আমাকে দেখাও। এখানে লেখা আছে, বাকি না দিলে রিকশাটা ওদের। তুমি শুধু কথাটা শুনেছ, লেখাটা পড়ো নি।",
    4: "রিকশা আমার জান, মা। ওটা ছাড়া আমি কিছু না। এইটুকু ভুলের দামে সাত বছরের রক্ত? না, আমি শোধ দিব, দিবই।",
    5: "সাত মাস হয়ে গেল। আজ মেয়াদ। কাগজে যেটা লেখা, সেটাই সত্যি। রিকশাটা নামিয়ে দে, আর খাতা থেকে নাম কাট।",
    6: "একটা ছাপ। শুধু একটা আঙুলের ছাপ। আমার বাবার সারাজীবনের জমানো, ওই একটা ছাপে বন্ধ হয়ে গেল।",
    7: "ভাই, একটু ক্যামেরার দিকে তাকান। এই খাতাটা ধরেন। এটা ভাইরাল হবে, বিশ্বাস করেন। আপনাদের কষ্টটা মানুষের কাছে পৌঁছাবে।",
    8: "বেটা, ক্যামেরাটা নামা। এই দোকানে আমি চল্লিশ বছর চা খাই। এই খাতায় বহু ছাপ দেখলাম। কিন্তু কেউ কখনো ছাপগুলো নিয়ে কথা বলে নি।",
    9: "আমি অন্যায় করি নাই। কাগজে লেখা আছে, ছাপ আছে, সাক্ষী আছে। আইন আমার পাশে। তোরা যা করিস, আমার কিছু যায় আসে না।",
    10: "ভিডিওটা দিলাম। দুই দিনে চল্লিশ লাখ মানুষ দেখল। রিকশাটা ফেরত পেল না, কেউ একটা টাকাও দিল না। সবাই শুধু শেয়ার করল।",
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
        for ti, (who, clip) in enumerate(turns):
            d = _dur(os.path.join(AUD, "d%02d.mp3" % clip)) or 9.0
            entries.append({"scene": scene, "cap": cap, "who": who, "clip": clip,
                            "text": TEXT[clip], "t0": t, "dur": d, "si": si})
            t += d
            last = (si == len(SCENES) - 1) and (ti == len(turns) - 1)
            t += 1.10 if (ti == len(turns) - 1 and not last) else 0.55
    return entries, t - 0.55 + TAIL


ENTRIES, TOTAL = build_timeline()
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


def scene_at(t):
    for scene, cap, turns in SCENES:
        a, b = SPAN[scene]
        if a - 0.2 <= t < b + 0.6:
            return scene, cap
    return "dark", "পরের সকাল"


# ---------------------------------------------------------------- people
HEIGHT = {"presenter": 742, "shopkeeper": 704, "puller": 762, "student": 700, "uncle": 716}
NIGHT = {"street": 0.74, "dark": 0.62}
SHADE = {"deadline": 0.90}


def actor(art, who, x, y, h=None, mouth=0.0, k=1.0, lean=0.0, sess=0.0, alpha=1.0):
    sp = sprites6.sprite(who)
    m = sprites6.MOUTH[who]
    h = h or HEIGHT[who]
    kk = h / sp.height
    w = max(1, int(round(sp.width * kk)))
    img = sp.resize((w, max(1, int(round(h * (1.0 + 0.004 * sess))))), Image.LANCZOS)
    sx = img.width / sp.width
    cx, cy = m["x"] * sx, (m["y"] + m.get("dy", 0)) * sx
    mw, mh = m["w"] * sx, m["h"] * sx

    d = ImageDraw.Draw(img)
    if mouth <= 0.04:
        # every one of these designs is drawn mid-sentence; a listener gets a closed mouth
        d.ellipse([cx - mw * 0.54, cy - mh * 0.40, cx + mw * 0.54, cy + mh * 0.50],
                  fill=SKIN[who] + (255,))
        d.arc([cx - mw * 0.40, cy - mh * 0.22, cx + mw * 0.40, cy + mh * 0.26],
              16, 164, fill=INK_MOUTH + (255,), width=max(2, int(round(mh * 0.11))))
    else:
        ow = max(3.0, mw * (0.58 + 0.26 * mouth))
        oh = max(2.0, mh * (0.14 + 0.66 * mouth))
        d.ellipse([cx - ow / 2, cy - oh * 0.38, cx + ow / 2, cy + oh * 0.62],
                  fill=INK_MOUTH + (255,))
    if k < 0.999:
        img = sprites6.tint(img, k)
    if lean:
        img = img.rotate(lean, resample=Image.BICUBIC,
                         center=(img.width / 2, img.height), expand=False)
    if alpha < 0.999:
        img.putalpha(img.split()[3].point(lambda v: int(v * alpha)))
    art.alpha_composite(img, (int(round(x - img.width / 2)), int(round(y - img.height))))


# ---------------------------------------------------------------- props
def bulb(p, x=548, y=380, on=False):
    p.line([(x, 0), (x, y - 30)], (110, 106, 98) if not on else (92, 88, 80), 4)
    if on:
        p.ell([x - 118, y - 118, x + 118, y + 118], (250, 244, 226))
        p.ell([x - 70, y - 70, x + 70, y + 70], (240, 230, 202))
    p.ell([x - 40, y - 40, x + 40, y + 40], (58, 54, 48))
    p.ell([x - 30, y - 30, x + 30, y + 30], (252, 246, 226) if on else (74, 70, 62))


def thumbprint(p, x, y, s=1.0, rot=0.0):
    """The whole film in one shape: a coral finger pressed on paper."""
    p.ell([x - 15 * s, y - 19 * s, x + 15 * s, y + 19 * s], CORAL)
    for r in (0.62, 0.36):
        p.ring([x - 15 * s * r, y - 19 * s * r, x + 15 * s * r, y + 19 * s * r],
               max(2, 3 * s), CORAL_D)
    for dy in (-0.42, 0.02, 0.44):
        p.line([(x - 11 * s, y + dy * 19 * s), (x + 11 * s, y + dy * 19 * s)], PAPER, max(2, 3 * s))
    _ = rot


def shelf(p, x0, y0, x1, y1, col_pkt, col_pkt2):
    for i in range(4):
        yy = y0 + (y1 - y0) * i / 4
        p.poly([(x0, yy), (x1, yy), (x1, yy + 9), (x0, yy + 9)], INK)
        for j in range(4):
            bx = x0 + 18 + j * ((x1 - x0 - 36) / 4)
            bh = 58 - (j % 3) * 7
            p.poly([(bx, yy - bh), (bx + 40, yy - bh), (bx + 40, yy - 3), (bx, yy - 3)],
                   col_pkt if (i + j) % 2 else col_pkt2)
            p.line([(bx, yy - bh), (bx + 40, yy - bh)], INK, 3)


def counter(p, top=1240, c1=WOOD, lip=LIP):
    p.poly([(120, top), (980, top - 8), (980, GY), (120, GY)], c1)
    p.poly([(120, top), (980, top - 8), (980, top + 30), (120, top + 38)], lip)
    p.line([(120, top), (980, top - 8)], INK, 4)
    p.line([(120, GY), (980, GY)], INK, 3)


def ledger(p, x, y, printed=False):
    """The khata, open, with one page you can press a finger onto."""
    p.poly([(x, y), (x + 150, y - 6), (x + 150, y + 52), (x, y + 58)], WHITE)
    p.line([(x, y), (x + 150, y - 6), (x + 150, y + 52), (x, y + 58), (x, y)], INK, 4)
    p.line([(x + 75, y - 3), (x + 75, y + 55)], INK, 3)
    for i in range(4):
        yy = y + 12 + i * 11
        p.line([(x + 10, yy), (x + 64, yy - 2)], MID, 3)
        p.line([(x + 86, yy), (x + 140, yy - 2)], MID, 3)
    if printed:
        thumbprint(p, x + 112, y + 26, 0.9)


def notice(p, x, y, w, h, stamped=False):
    p.poly([(x, y), (x + w, y - 8), (x + w, y + h), (x, y + h + 6)], (222, 218, 208))
    p.line([(x, y), (x + w, y - 8), (x + w, y + h), (x, y + h + 6), (x, y)], INK, 4)
    for i in range(4):
        yy = y + 24 + i * 26
        p.line([(x + 18, yy), (x + w - 26, yy - 4)], MID, 4)
    if stamped:
        thumbprint(p, x + w - 46, y + h - 46, 1.05)


def rickshaw(p, x, y, col=(46, 42, 36), col2=(58, 52, 44), r=64):
    """A cycle rickshaw, side on: two wheels, a seat, a canopy, and nowhere to sit."""
    p.line([(x - 96, y - 74), (x + 112, y - 74)], col, 12)
    for cx in (x - 96, x + 112):
        p.ring([cx - r, y - r, cx + r, y + r], 10, col)
        p.line([(cx - r + 6, y), (cx + r - 6, y)], col, 6)
        p.line([(cx, y - r + 6), (cx, y + r - 6)], col, 6)
    p.poly([(x - 44, y - 78), (x + 124, y - 78), (x + 124, y - 172), (x - 44, y - 172)], col2)
    p.poly([(x - 52, y - 172), (x - 12, y - 172), (x - 12, y - 244), (x - 52, y - 244)], col2)
    p.line([(x - 52, y - 78), (x - 52, y - 244)], col, 8)
    p.line([(x + 160, y - 246), (x + 160, y - 78)], col, 8)
    p.poly([(x - 64, y - 246), (x + 176, y - 246), (x + 196, y - 330), (x - 44, y - 330)], col2)
    p.line([(x - 64, y - 246), (x + 176, y - 246)], col, 6)
    p.line([(x + 124, y - 122), (x + 196, y - 158)], col, 9)


def set_shop(p, t, e, dusk=False):
    wall = WALL_D if dusk else WALL
    ceil = CEIL_D if dusk else CEIL
    floor = FLOOR_D if dusk else FLOOR
    p.poly([(0, 0), (W, 0), (W, H), (0, H)], floor)
    p.poly([(0, 0), (W, 0), (W, 300), (0, 312)], ceil)
    p.poly([(0, 300), (W, 286), (W, GY), (0, GY)], wall)
    p.line([(0, 312), (W, 300)], (176, 170, 158), 3)
    p.line([(0, GY), (W, GY)], INK, 3)

    # a door on the left, shut — and in the dusk scene it is the only light
    door = (250, 238, 206) if dusk else (214, 208, 194)
    p.poly([(44, 470), (252, 466), (252, GY), (44, GY)], door)
    p.line([(44, 470), (252, 466), (252, GY), (44, GY), (44, 470)], INK, 5)
    p.line([(122, 468), (122, GY)], (200, 194, 182), 3)
    p.ell([204, 998, 226, 1020], INK)

    # shelves on the right: the shop's stock, flat packets only
    shelf(p, 806, 640, 1010, 1074,
          (238, 235, 226), (176, 170, 158) if dusk else (198, 192, 180))
    counter(p, 1240, WOOD_D if dusk else WOOD,
            (196, 190, 178) if dusk else LIP)

    # the khata waits on the counter; the coral mark lands once he presses
    pressed = False
    if e:
        if e["clip"] >= 3:
            pressed = True
        elif e["clip"] == 2:
            pressed = (t - e["t0"]) > e["dur"] * 0.62
    ledger(p, 584, 1176, printed=pressed)
    p.poly([(764, 1192), (822, 1192), (822, 1230), (764, 1230)], (58, 54, 48))
    p.line([(764, 1192), (822, 1192)], INK, 4)


def set_deadline(p, t, e):
    set_shop(p, t, e, dusk=True)


def shutter(p, x0, y0, x1, y1, base=(38, 34, 29), slat=(26, 23, 20), rail=(52, 47, 40)):
    p.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], base)
    yy = y0 + 16
    while yy < y1 - 12:
        p.line([(x0 + 4, yy), (x1 - 4, yy)], slat, 6)
        yy += 34
    p.poly([(x0, y1 - 42), (x1, y1 - 42), (x1, y1), (x0, y1)], rail)
    p.poly([(x0, y0), (x1, y0), (x1, y0 + 22), (x0, y0 + 22)], rail)


def set_street(p, t, e):
    p.poly([(0, 0), (W, 0), (W, H), (0, H)], (22, 20, 18))
    p.poly([(0, 300), (W, 292), (W, 1400), (0, 1406)], NIGHT_W)
    p.line([(0, 300), (W, 292)], (48, 43, 36), 4)

    # the shop he walks past every day, shut for the night
    shutter(p, 618, 636, 1032, 1400)
    p.poly([(600, 560), (1050, 560), (1050, 640), (600, 640)], (52, 47, 40))
    p.line([(600, 560), (1050, 560), (1050, 640), (600, 640), (600, 560)], (76, 68, 56), 4)

    # poster wall, flat bills edged in ink so they read as paper on plaster
    for (x0, y0, x1, y1, band) in ((46, 546, 232, 800, True), (272, 600, 420, 776, False)):
        p.poly([(x0, y0), (x1, y0 - 6), (x1, y1), (x0, y1 + 6)], (52, 47, 40))
        p.line([(x0, y0), (x1, y0 - 6), (x1, y1), (x0, y1 + 6), (x0, y0)],
               (74, 66, 55), 3)
        if band:
            p.poly([(x0, y0), (x1, y0 - 6), (x1, y0 + 46), (x0, y0 + 52)], CORAL_D)

    # the street lamp
    p.poly([(104, 500), (136, 500), (136, 1406), (104, 1406)], (58, 54, 48))
    p.ell([84, 426, 156, 502], (58, 54, 48))
    p.ell([94, 436, 146, 490], (250, 244, 226))
    p.ell([103, 445, 137, 479], (240, 230, 202))

    # kerb, then pavement
    p.poly([(0, 1400), (W, 1394), (W, 1424), (0, 1430)], (46, 42, 35))
    p.line([(0, 1400), (W, 1394)], (12, 10, 9), 5)
    p.poly([(0, 1430), (W, 1424), (W, H), (0, H)], (22, 20, 18))

    # the rickshaw he no longer owns, parked against the wall
    rickshaw(p, 172, 1500, col=(66, 60, 50), col2=(76, 69, 57), r=56)


def set_dark(p, t, e):
    p.poly([(0, 0), (W, 0), (W, H), (0, H)], NIGHT_F)
    p.poly([(0, 300), (W, 288), (W, GY), (0, GY)], (30, 27, 24))
    p.line([(0, 300), (W, 288)], (58, 52, 44), 5)
    # shutter down over the whole shopfront
    shutter(p, 56, 470, 1024, 1400)
    notice(p, 742, 600, 214, 168, stamped=True)
    p.poly([(56, 1400), (1024, 1400), (1024, GY), (56, GY)], (26, 24, 21))
    bulb(p, 828, 430, on=False)


SETS = {"shop": set_shop, "deadline": set_deadline, "street": set_street, "dark": set_dark}


def stage(scene, t, e):
    who, mo = mouth_of(t)
    behind, front = [], []

    def lean_for(name, sign):
        if not e or who != name:
            return 0.0
        return sign * 1.1 * soft((t - e["t0"]) / 0.4)

    def sess(ph, amp=0.6):
        return amp * math.sin(t * 2.1 + ph)

    if scene in ("shop", "deadline"):
        behind.append(dict(who="shopkeeper", x=768, y=GY + 8,
                           mouth=mo if who == "shopkeeper" else 0.0,
                           lean=lean_for("shopkeeper", -1.0), sess=sess(0.3)))
        front.append(dict(who="puller", x=300, y=GY + 126,
                          mouth=mo if who == "puller" else 0.0,
                          lean=lean_for("puller", 1.0), sess=sess(1.1)))
        # the daughter arrives with the paper in her hand, and stays
        present = e and e["scene"] == "shop" and e["clip"] >= 3
        if present or scene == "deadline":
            cx, alpha = 520.0, 1.0
            if e and e["clip"] == 3:
                u = clamp((t - e["t0"] + 0.6) / 1.5)
                cx = lerp(116, 520, soft(u))
            front.append(dict(who="student", x=cx, y=GY + 148,
                              mouth=mo if who == "student" else 0.0,
                              lean=lean_for("student", 1.0), sess=sess(2.2),
                              alpha=alpha))
    elif scene == "street":
        behind.append(dict(who="uncle", x=560, y=GY + 44, h=620,
                           mouth=mo if who == "uncle" else 0.0,
                           lean=lean_for("uncle", -1.0), sess=sess(2.6)))
        front.append(dict(who="student", x=756, y=GY + 100, h=652,
                          mouth=mo if who == "student" else 0.0,
                          lean=lean_for("student", 1.0), sess=sess(0.8)))
        front.append(dict(who="presenter", x=902, y=GY + 118, h=764,
                          mouth=mo if who == "presenter" else 0.0,
                          lean=lean_for("presenter", -1.0), sess=sess(1.7)))
    elif scene == "dark":
        front.append(dict(who="shopkeeper", x=336, y=GY + 66,
                          mouth=mo if who == "shopkeeper" else 0.0,
                          lean=lean_for("shopkeeper", -1.0), sess=sess(0.2)))
        front.append(dict(who="presenter", x=800, y=GY + 92,
                          mouth=mo if who == "presenter" else 0.0,
                          lean=lean_for("presenter", 1.0), sess=sess(1.4)))
    return behind, front


# ---------------------------------------------------------------- cards
def title_card(t, q):
    art = Image.new("RGBA", (int(W * SS), int(H * SS)), PAPER + (255,))
    T(art, (96, 250), "অন্ধকার পাঠ", 34, INK_S, 500)
    T(art, (96, 300), "০৫", 34, INK_S, 700)
    T(art, (532, 700), "০৫", 800, WALL, 700, anchor="mm")
    T(art, (96, 1180), "আঙুলের ছাপ", 128, INK, 700)
    T(art, (100, 1268), "The Thumbprint", 46, INK_S, 500)
    T(art, (96, 1420), "কথ্য সংস্করণ · পাঁচ কণ্ঠ", 34, INK_S, 500)
    T(art, (96, 1492), "একটা ছাপ পড়ে।", 40, INK, 500)
    T(art, (96, 1548), "সারা জীবনের জমানো বন্ধ হয়ে যায়।", 40, INK, 500)
    _ = (t, q)
    return art.resize((W, H), Image.LANCZOS).convert("RGBA")


def end_card(t, q):
    art = Image.new("RGBA", (int(W * SS), int(H * SS)), INK_D + (255,))
    p = P(art, SS)
    T(art, (96, 470), "কেউ দেখল।", 112, PAPER, 700)
    T(art, (96, 592), "কেউ শেয়ার করল।", 112, PAPER, 700)
    T(art, (96, 736), "কেউ কিছু করল না।", 58, (170, 164, 152), 500)
    p.line([(96, 900), (984, 900)], (58, 54, 48), 4)
    thumbprint(p, 150, 1012, 2.4)
    T(art, (96, 1200), "একটা লাইকও তার রিকশা ফেরত দেয় না।", 44, (198, 192, 178), 500)
    T(art, (96, 1452), "তুমি দেখলে — এখন কী করবে?", 40, (198, 192, 178), 500)
    _ = (t, q)
    return art.resize((W, H), Image.LANCZOS).convert("RGBA")


def frame(t):
    if t < LEAD:
        return title_card(t, clamp(t / LEAD))
    if t >= TOTAL - TAIL:
        return end_card(t, clamp((t - (TOTAL - TAIL)) / TAIL))

    scene, cap = scene_at(t)
    e = active(t)
    k = NIGHT.get(scene, SHADE.get(scene, 1.0))

    art = Image.new("RGB", (int(W * SS), int(H * SS)), PAPER)
    p = P(art, SS)
    SETS[scene](p, t, e)
    art = art.resize((W, H), Image.LANCZOS).convert("RGBA")

    behind, front = stage(scene, t, e)
    for a_ in behind:
        actor(art, a_["who"], a_["x"], a_["y"], mouth=a_["mouth"], k=k,
              lean=a_.get("lean", 0.0), sess=a_.get("sess", 0.0),
              alpha=a_.get("alpha", 1.0))
    for a_ in front:
        actor(art, a_["who"], a_["x"], a_["y"], mouth=a_["mouth"], k=k,
              lean=a_.get("lean", 0.0), sess=a_.get("sess", 0.0),
              alpha=a_.get("alpha", 1.0))

    night = scene in ("street", "dark")
    light = (236, 232, 222) if night else INK
    faint = (162, 156, 144) if night else INK_S
    T(art, (92, TYPE_Y), "অন্ধকার পাঠ · ০৫", 26, faint, 500)
    T(art, (92, CAP_Y), cap, 104, light, 700)
    if e:
        lab = LABEL[e["who"]]
        lw = deva.layout(lab, 28)[1]
        chip = (24, 22, 19) if night else PAPER
        ImageDraw.Draw(art).rectangle([84, SUB_Y - 162, 84 + lw + 18, SUB_Y - 118],
                                      fill=chip + (255,))
        T(art, (93, SUB_Y - 140), lab, 28, (230, 138, 102) if night else CORAL, 700)
        lines = wrap(e["text"], 37, 912)
        yy = SUB_Y - 42 * (len(lines) - 1)
        for ln in lines:
            T(art, (92, yy), ln, 37, light, 500)
            yy += 44
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
    out = out or "dark-lesson-05-thumbprint-1080x1920.mp4"
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
