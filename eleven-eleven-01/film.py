"""Render এগারোটা এগারো — part 1 of 3. One narrator, one phone, one locked drawer.

The rooms are painted plates (cel-shaded, cold blue night); the people in them are drawn here,
frame by frame, by `rig.py`, so they can act: hold a phone to an ear, turn from a window, walk into
a park, stand still while someone comes up behind them. The camera moves on the plate, and every
cut lands in a measured pause (see `plan.py`).

    python3 film.py                      # whole film -> build/video.mp4
    python3 film.py --stills 4,20,52     # review frames into build/still-*.png
"""

import argparse
import bisect
import json
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import deva
import lines as L
import rig

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "scene")
RAW = os.path.join(HERE, "raw")
BUILD = os.path.join(HERE, "build")
W, H = 1080, 1920
FPS = 24
M = 1.40                      # the plate is kept 40 % larger than frame so a push-in stays sharp

INK = (12, 12, 16)
NIGHT = (10, 14, 24)

_plates = {}


# --------------------------------------------------------------------------- the rooms
def background(name, flip=False):
    key = (name, flip)
    if key not in _plates:
        im = Image.open(os.path.join(SC, "bg-%s.png" % name)).convert("RGB")
        # crop to 9:16 around the centre, then up to master size
        want = 9 / 16
        if im.width / im.height > want:
            nw = int(im.height * want)
            im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
        else:
            nh = int(im.width / want)
            im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
        im = im.resize((int(W * M), int(H * M)), Image.LANCZOS)
        _plates[key] = im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
    return _plates[key]


def camera(shot, u):
    """(cx, cy, z) — fractions of the plate, and a zoom. Linear, eased at both ends."""
    c0, c1 = shot["cam"]
    k = u * u * (3 - 2 * u)
    return (c0[0] + (c1[0] - c0[0]) * k,
            c0[1] + (c1[1] - c0[1]) * k,
            c0[2] + (c1[2] - c0[2]) * k)


def view(shot, u):
    """The cropped frame, plus the mapping from plate fractions to screen pixels."""
    plate = background(shot["bg"], shot.get("flip", False))
    pw, ph = plate.size
    cx, cy, z = camera(shot, u)
    cw, ch = pw / z, ph / z
    x0 = min(max(cx * pw - cw / 2, 0), pw - cw)
    y0 = min(max(cy * ph - ch / 2, 0), ph - ch)
    im = plate.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
    return im, (x0, y0, W / cw, pw, ph)


# --------------------------------------------------------------------------- the actors
def actor_screen(a, mapping):
    x0, y0, k, pw, ph = mapping
    return dict(who=a["who"], view=a.get("view", "front"), flip=a.get("flip", False),
                seed=a.get("seed", 0.0), walk=a.get("walk"),
                x=(a["fx"] * pw - x0) * k,
                feet=(a["fy"] * ph - y0) * k,
                h=a["fh"] * ph * k,
                keys=a.get("keys", []))


def draw_actors(im, shot, t_local):
    mapping = shot["_map"]
    for a in shot.get("actors", []):
        spec = actor_screen(a, mapping)
        rig.draw(im, spec, t_local, ink_width=shot.get("ink", 1.0))


# --------------------------------------------------------------------------- overlays
def scrim(im, y0, y1, strength=0.55, colour=(6, 8, 14)):
    lay = Image.new("RGBA", (W, y1 - y0), colour + (int(255 * strength),))
    im.alpha_composite(lay, (0, y0))


def card_frame(im, text, alpha):
    """A hook line, set on a dark rail — big, one line if it can be, always legible on a phone."""
    if alpha <= 0.01:
        return
    base = Image.new("RGBA", im.size, (0, 0, 0, 0))
    rail = Image.new("RGBA", (W, 210), (8, 10, 18, 215))
    base.alpha_composite(rail, (0, 96))
    deva.draw_text(base, (W // 2, 200), text, 62, 700, (244, 240, 232))
    if alpha < 0.999:
        base.putalpha(base.split()[3].point(lambda v: int(v * alpha)))
    im.alpha_composite(base)


def rain_layer(im, t, amount=1.0, seed=0.0):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(7)
    n = int(150 * amount)
    xs = rng.uniform(0, W, n)
    ys = rng.uniform(0, H, n)
    sp = rng.uniform(1500, 2600, n)
    ln = rng.uniform(28, 90, n)
    al = rng.integers(26, 78, n)
    for x, y, s_, l_, a_ in zip(xs, ys, sp, ln, al):
        yy = (y + s_ * (t + seed)) % (H + l_)
        d.line([(x, yy), (x - 6, yy + l_)], fill=(198, 220, 236, int(a_)), width=2)
    return Image.alpha_composite(im, lay)


def grain_and_vignette(im, dark=1.0, warm=0.0, vig=0.55, gr=2.4):
    a = np.asarray(im).astype(np.float32)
    if dark < 0.999:
        a[..., :3] *= dark
    lum = a[..., :3].mean(axis=2, keepdims=True) / 255.0
    # cold in the shadows, a little amber where the lamps are
    a[..., 2] += ((1.0 - lum) * 9.0)[..., 0]
    a[..., 0] += (lum * (3.0 + 5.0 * warm))[..., 0]
    a[..., :3] = a[..., :3] * 1.015 + 1.5
    if vig > 0.0:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        a[..., :3] *= (1.0 - vig * np.clip(r - 0.55, 0, 2) * 0.55)[..., None]
    if gr > 0:
        a[..., :3] += np.random.default_rng(int(a[0, 0, 0]) + 3).normal(0, gr, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


# --------------------------------------------------------------------------- the phones
def _phone_base():
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    a = (np.array([10, 13, 22], np.float32) * (1 - g) + np.array([20, 26, 40], np.float32) * g)
    return Image.fromarray(np.repeat(a, W, axis=1).astype(np.uint8), "RGB")


def phone_screen(kind, t_local, dur):
    """Full-bleed handset screens — the only crisp UI in the film, because the plot lives there."""
    im = _phone_base().convert("RGBA")
    d = ImageDraw.Draw(im)
    pulse = 0.5 + 0.5 * math.sin(2 * math.pi * 1.1 * t_local)

    if kind == "call":
        deva.draw_text(im, (W // 2, 150), "১১:১১", 40, 500, (176, 190, 206))
        deva.draw_text(im, (W // 2, 236), "শুক্রবার, ১৪ ফেব্রুয়ারি", 30, 400, (126, 140, 158))
        d.ellipse((W // 2 - 90, 520, W // 2 + 90, 700), outline=(120, 150, 176), width=3)
        deva.draw_text(im, (W // 2, 610), "?", 92, 700, (168, 190, 210))
        deva.draw_text(im, (W // 2, 800), "অজানা নম্বর", 78, 700, (238, 236, 230))
        deva.draw_text(im, (W // 2, 890), "মোবাইল · ঢাকা", 34, 400, (140, 154, 172))
        deva.draw_text(im, (W // 2, 1030), "কল আসছে…", int(40 + 4 * pulse), 500,
                       (150, 200, 210))
        for i in range(3):
            r = 1.0 + 0.25 * math.sin(2 * math.pi * 0.9 * t_local - i * 0.9)
            d.ellipse((W // 2 - 150 - i * 46 * r, 1104 - 16 * r,
                       W // 2 - 118 + i * 46 * r, 1136 + 16 * r),
                      outline=(96, 170, 190), width=2)
        d.ellipse((W // 2 - 250, 1520, W // 2 - 110, 1660), fill=(178, 52, 56))
        d.ellipse((W // 2 + 110, 1520, W // 2 + 250, 1660), fill=(44, 148, 92))
        deva.draw_text(im, (W // 2 - 180, 1720), "কেটে দিন", 30, 500, (150, 160, 176))
        deva.draw_text(im, (W // 2 + 180, 1720), "ধরুন", 30, 500, (150, 160, 176))

    elif kind == "old":
        wall = Image.open(os.path.join(RAW, "anika-01.png")).convert("RGB")
        wall = wall.crop((int(wall.width * 0.30), int(wall.height * 0.06),
                          int(wall.width * 0.72), int(wall.height * 0.46)))
        wall = wall.resize((W, int(W * wall.height / wall.width)), Image.LANCZOS)
        wall = wall.filter(ImageFilter.GaussianBlur(4))
        wall = Image.fromarray((np.asarray(wall).astype(np.float32) * 0.72).astype(np.uint8))
        im.paste(wall.convert("RGBA"), (0, 0))
        scrim(im, 560, 1060, 0.62, (6, 8, 14))
        deva.draw_text(im, (W // 2, 130), "১১:১১", 38, 500, (196, 206, 220))
        deva.draw_text(im, (W // 2, 660), "আনিকা ♥", 96, 700, (240, 236, 230))
        deva.draw_text(im, (W // 2, 760), "পুরোনো ফোন · ৪৭ %", 32, 400, (150, 162, 180))
        deva.draw_text(im, (W // 2, 900), "কল আসছে…", 40, 500, (150, 200, 210))
        d.ellipse((W // 2 - 250, 1520, W // 2 - 110, 1660), fill=(178, 52, 56))
        d.ellipse((W // 2 + 110, 1520, W // 2 + 250, 1660), fill=(44, 148, 92))

    elif kind == "live":
        deva.draw_text(im, (W // 2, 150), "১১:১১", 40, 500, (176, 190, 206))
        deva.draw_text(im, (W // 2, 760), "অজানা নম্বর", 84, 700, (238, 236, 230))
        mm, ss = divmod(int(t_local) + 3, 60)
        deva.draw_text(im, (W // 2, 880), "%02d:%02d" % (mm, ss), 44, 500, (146, 196, 206))
        deva.draw_text(im, (W // 2, 1000), "সংযুক্ত", 34, 400, (140, 154, 172))
        rng = np.random.default_rng(int(t_local * 24))
        for i in range(26):
            hh = rng.integers(18, 150)
            d.rounded_rectangle((90 + i * 35, 1240 - hh // 2, 116 + i * 35, 1240 + hh // 2),
                                radius=12, fill=(96, 170, 190))
        d.ellipse((W // 2 - 70, 1560, W // 2 + 70, 1700), fill=(178, 52, 56))
    return im


def end_card():
    im = Image.new("RGBA", (W, H), (7, 8, 13, 255))
    d = ImageDraw.Draw(im)
    for i in range(3):
        y = 470 + i * 300
        d.line([(150, y), (W - 150, y)], fill=(120, 40, 44), width=2)
    deva.draw_text(im, (W // 2, 620), "রায়ান কে?", 118, 700, (242, 238, 230))
    deva.draw_text(im, (W // 2, 800), "পার্ট ২ আসছে", 52, 600, (214, 120, 112))
    deva.draw_text(im, (W // 2, 1010), "।", 8, 400, (40, 44, 54))
    deva.draw_text(im, (W // 2, 1140), "এগারোটা এগারো", 44, 700, (150, 162, 180))
    deva.draw_text(im, (W // 2, 1210), "ভুল নম্বর · পার্ট ১", 30, 400, (110, 122, 140))
    deva.draw_text(im, (W // 2, 1460), "ফলো করে রাখুন", 34, 500, (128, 140, 158))
    return im


def title_card(alpha):
    im = Image.new("RGBA", (W, H), (6, 7, 12, 255))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    deva.draw_text(lay, (W // 2, 880), "এগারোটা এগারো", 92, 700, (236, 232, 224))
    deva.draw_text(lay, (W // 2, 985), "ভুল নম্বর", 40, 500, (150, 160, 178))
    deva.draw_text(lay, (W // 2, 1058), "পার্ট ১", 30, 400, (120, 130, 148))
    lay.putalpha(lay.split()[3].point(lambda v: int(v * alpha)))
    im.alpha_composite(lay)
    return im


# --------------------------------------------------------------------------- the shots
def A(who, fx, fy, fh, keys, **kw):
    d = dict(who=who, fx=fx, fy=fy, fh=fh, keys=keys)
    d.update(kw)
    return d


EAR = dict(ik1=1, hx1=70, hy1=-780, phone=1)      # phone up at her ear
CHEST = dict(ik1=1, hx1=112, hy1=-556, phone=1)    # phone low, held in both eyes' line
DOWN = dict(ik1=0)


def K(t, **kw):
    return (t, kw)


SHOTS = {
    # 1 — the hook: she is by the window, and the phone is already too important
    "h01": dict(bg="window-rain", cam=((0.50, 0.46, 1.02), (0.47, 0.44, 1.12)), dark=0.94, rain=0.8,
                actors=[A("anika", 0.36, 0.955, 0.62, [
                    (0.0, dict(CHEST, head=-6, eye=0.95, brow=0.4, mouth=-0.2)),
                    (4.0, dict(CHEST, head=8, eye=0.75, brow=0.8, mouth=-0.4)),
                    (8.0, dict(CHEST, head=-2, eye=0.9, brow=0.6, mouth=-0.2))])]),
    "h02": dict(bg="window-rain", cam=((0.36, 0.63, 1.30), (0.36, 0.65, 1.42)), dark=0.92, rain=0.5,
                actors=[A("anika", 0.36, 0.955, 0.62, [
                    (0.0, dict(EAR, head=4, eye=0.85, brow=0.8, mouth=-0.4)),
                    (4.5, dict(EAR, head=-4, eye=0.6, brow=1.0, mouth=-0.6))])]),

    # 2 — the wrong number
    "w01": dict(phone="call", dark=0.9),
    "w02": dict(bg="bed-phone", cam=((0.52, 0.50, 1.02), (0.50, 0.47, 1.12)), dark=0.9,
                actors=[A("anika", 0.34, 0.965, 0.60, [
                    (0.0, dict(EAR, head=-4, eye=0.95, brow=0.7, mouth=-0.2)),
                    (5.0, dict(EAR, head=6, eye=0.8, brow=0.95, mouth=-0.5))])]),
    "w03": dict(bg="window-rain", cam=((0.34, 0.66, 1.28), (0.34, 0.68, 1.40)), dark=0.9, rain=0.4,
                actors=[A("anika", 0.34, 0.955, 0.62, [
                    (0.0, dict(EAR, head=-2, eye=0.75, brow=1.0, mouth=-0.6)),
                    (4.0, dict(EAR, head=3, eye=0.95, brow=0.7, mouth=-0.3))])]),
    "w04": dict(bg="study", cam=((0.58, 0.50, 1.04), (0.56, 0.48, 1.12)), dark=0.88,
                actors=[A("sabbir", 0.56, 0.965, 0.58, [
                    (0.0, dict(EAR, head=-8, brow=-0.2, mouth=-0.6, eye=0.9)),
                    (4.0, dict(EAR, head=6, brow=0.0, mouth=-0.7, eye=0.85))], view="back")]),

    # 3 — every night at 11:11
    "d01": dict(bg="bed-phone", cam=((0.50, 0.46, 1.02), (0.47, 0.42, 1.22)), dark=0.88),
    "d02": dict(bg="window-rain", cam=((0.46, 0.48, 1.02), (0.44, 0.46, 1.14)), dark=0.9, rain=0.9,
                actors=[A("anika", 0.42, 0.955, 0.60, [
                    (0.0, dict(CHEST, head=6, eye=0.6, brow=0.4, mouth=0.4)),
                    (4.0, dict(CHEST, head=-2, eye=0.75, brow=0.5, mouth=0.6))])]),

    # 4 — he knew things he could not know
    "k01": dict(bg="window-rain", cam=((0.60, 0.40, 1.16), (0.58, 0.38, 1.30)), dark=0.92, rain=1.0),
    "k02": dict(bg="blanket", cam=((0.50, 0.50, 1.02), (0.48, 0.47, 1.18)), dark=0.95, warm=1.0),
    "k03": dict(bg="blanket", cam=((0.44, 0.56, 1.22), (0.42, 0.58, 1.36)), dark=0.95, warm=1.0),
    "k04": dict(bg="window-rain", cam=((0.36, 0.63, 1.24), (0.34, 0.65, 1.38)), dark=0.94, rain=0.5,
                actors=[A("anika", 0.36, 0.955, 0.62, [
                    (0.0, dict(ik1=1, hx1=16, hy1=-700, head=-2, eye=0.9, brow=0.2, mouth=0.8)),
                    (4.0, dict(ik1=1, hx1=16, hy1=-694, head=6, eye=0.75, brow=0.3, mouth=0.9))])]),

    # 5 — in love with the silence
    "l01": dict(bg="window-rain", cam=((0.50, 0.50, 1.02), (0.48, 0.47, 1.14)), dark=0.93, rain=0.7,
                actors=[A("anika", 0.38, 0.955, 0.60, [
                    (0.0, dict(la=22, lb=16, head=-8, eye=0.8, brow=0.3, mouth=0.6)),
                    (4.0, dict(la=20, lb=18, head=4, eye=0.7, brow=0.4, mouth=0.8))])]),
    "l02": dict(bg="window-rain", cam=((0.36, 0.64, 1.34), (0.36, 0.66, 1.46)), dark=0.92, rain=0.4,
                actors=[A("anika", 0.36, 0.955, 0.62, [
                    (0.0, dict(la=20, lb=18, head=4, eye=0.6, brow=0.3, mouth=0.8)),
                    (4.0, dict(la=18, lb=20, head=-4, eye=0.15, brow=0.4, mouth=0.6))])]),

    # 6 — five o'clock, under the krishnachura
    "m01": dict(bg="park", cam=((0.50, 0.50, 1.02), (0.47, 0.47, 1.12)), dark=0.96,
                actors=[A("anika", 0.36, 0.965, 0.52, [
                    (0.0, dict(scarf=1, la=14, ra=14, head=-8, eye=0.9, brow=0.4, mouth=0.4)),
                    (6.0, dict(scarf=1, la=12, ra=12, head=2, eye=0.85, brow=0.5, mouth=0.5))],
                    walk=(13.0, 0.85))]),
    "m02": dict(bg="park", cam=((0.58, 0.52, 1.16), (0.60, 0.54, 1.28)), dark=0.95,
                actors=[A("anika", 0.52, 0.965, 0.56, [
                    (0.0, dict(scarf=1, la=10, ra=12, head=-14, eye=0.9,
                               brow=0.5, mouth=0.3)),
                    (5.0, dict(scarf=1, la=8, ra=10, head=-4, eye=0.8,
                               brow=0.7, mouth=0.1))])]),

    # 7 — nobody came
    "n01": dict(bg="park", cam=((0.58, 0.54, 1.06), (0.62, 0.56, 1.20)), dark=0.97),
    "n02": dict(bg="park", cam=((0.70, 0.60, 1.28), (0.73, 0.62, 1.44)), dark=1.0),
    "n03": dict(bg="park", cam=((0.42, 0.52, 1.10), (0.40, 0.50, 1.22)), dark=0.95,
                actors=[A("anika", 0.40, 0.965, 0.56, [
                    (0.0, dict(scarf=1, la=14, ra=16, head=6, eye=0.55, brow=0.9, mouth=-0.6)),
                    (5.0, dict(scarf=1, la=10, ra=10, head=-6, eye=0.4, brow=1.0, mouth=-0.9))])]),

    # 8 — the drawer
    "r01": dict(bg="study", cam=((0.42, 0.50, 1.02), (0.46, 0.48, 1.12)), dark=0.9,
                actors=[A("anika", 0.36, 0.965, 0.58, [
                    (0.0, dict(scarf=1, la=16, ra=16, head=-4, eye=0.9, brow=0.5, mouth=-0.2)),
                    (5.0, dict(scarf=1, ik1=1, hx1=164, hy1=-430, head=10, eye=0.7, brow=0.8,
                               mouth=-0.5))])]),
    "r02": dict(bg="drawer", cam=((0.50, 0.50, 1.02), (0.46, 0.46, 1.20)), dark=0.95),
    "r03": dict(phone="old", dark=0.95),
    "r04": dict(bg="study", cam=((0.44, 0.54, 1.20), (0.42, 0.56, 1.32)), dark=0.92,
                actors=[A("anika", 0.40, 0.965, 0.60, [
                    (0.0, dict(CHEST, head=-2, eye=1.1, brow=1.0, mouth=-0.4)),
                    (4.0, dict(CHEST, head=-8, eye=1.15, brow=1.1, mouth=-0.6))])]),

    # 9 — behind her
    "s01": dict(bg="doorway", cam=((0.46, 0.46, 1.02), (0.50, 0.48, 1.10)), dark=0.86),
    "s02": dict(bg="study", cam=((0.50, 0.52, 1.06), (0.52, 0.54, 1.16)), dark=0.84,
                actors=[A("anika", 0.34, 0.965, 0.54, [
                    (0.0, dict(EAR, head=-16, eye=1.05, brow=1.0, mouth=-0.5)),
                    (5.0, dict(EAR, head=-10, eye=1.0, brow=1.1, mouth=-0.6))]),
                        A("sabbir", 0.62, 0.965, 0.60, [
                    (0.0, dict(la=6, ra=6, head=-6, brow=0.0, mouth=-0.6, eye=0.85)),
                    (5.0, dict(la=4, ra=4, head=2, brow=0.0, mouth=-0.7, eye=0.8))])]),

    # 10 — and then the voice on the other end
    "c01": dict(bg="study", cam=((0.40, 0.60, 1.28), (0.38, 0.62, 1.42)), dark=0.9,
                actors=[A("anika", 0.36, 0.965, 0.60, [
                    (0.0, dict(EAR, head=2, eye=1.15, brow=1.0, mouth=-0.3)),
                    (4.0, dict(EAR, head=-4, eye=1.2, brow=1.2, mouth=-0.6))])]),
    "c02": dict(phone="live", dark=0.92),
    "c03": dict(bg="study", cam=((0.36, 0.66, 1.38), (0.36, 0.68, 1.52)), dark=0.86,
                actors=[A("anika", 0.34, 0.965, 0.60, [
                    (0.0, dict(EAR, head=-2, eye=1.1, brow=1.2, mouth=-0.7)),
                    (3.0, dict(EAR, head=0, eye=0.9, brow=1.2, mouth=-0.8))])]),
}


# --------------------------------------------------------------------------- the frame
def frame_at(t, tl):
    beats = tl["beats"]
    shots = tl["shots"]
    card_at = tl["card_at"]
    black_at = tl["black_at"]

    if t >= card_at:
        im = end_card().copy()
        a = min(1.0, (t - card_at) / 0.9)
        return Image.fromarray(
            (np.asarray(im.convert("RGB")).astype(np.float32) * a).astype(np.uint8))

    if t >= black_at:
        return Image.new("RGB", (W, H), (4, 4, 6))

    if t < shots[0]["t0"]:
        a = min(1.0, max(0.0, (t - 0.15) / 0.9))
        b = max(0.0, min(1.0, (shots[0]["t0"] - t) / 0.5))
        im = title_card(min(a, b))
        return rain_layer(im, t, 0.5).convert("RGB")

    i = max(0, bisect.bisect_right([s["t0"] for s in shots], t) - 1)
    s = shots[i]
    shot = SHOTS[s["id"]]
    dur = max(0.2, s["t1"] - s["t0"])
    u = (t - s["t0"]) / dur

    if shot.get("phone"):
        im = phone_screen(shot["phone"], t - s["t0"], dur)
        out = grain_and_vignette(im.convert("RGB"), dark=shot.get("dark", 1.0), vig=0.4)
        return out

    im, mapping = view(shot, u)
    shot["_map"] = mapping
    im = im.convert("RGBA")
    draw_actors(im, shot, t - s["t0"])

    # the hook line, only while the beat that carries it is speaking
    for b in beats:
        if b.get("card") and b["at"] + 0.55 <= t <= b["at"] + b["dur"] + 0.15:
            a_in = min(1.0, (t - b["at"] - 0.55) / 0.45)
            a_out = min(1.0, max(0.0, (b["at"] + b["dur"] + 0.15 - t) / 0.35))
            card_frame(im, b["card"], min(a_in, a_out))
            break

    if shot.get("rain"):
        im = rain_layer(im, t, shot["rain"])
    dark0, dark1 = (shot["dark"], shot["dark"]) if isinstance(shot["dark"], float) \
        else shot["dark"]
    dark = dark0 + (dark1 - dark0) * u
    return grain_and_vignette(im.convert("RGB"), dark=dark, warm=shot.get("warm", 0.0))


def render(tl, out_path, crf=23, stills=None):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    total = int(round(tl["total"] * FPS))
    if stills:
        os.makedirs(BUILD, exist_ok=True)
        for sec in stills:
            f = int(round(float(sec) * FPS))
            frame_at(f / FPS, tl).save(os.path.join(BUILD, "still-%05.1f.png" % float(sec)))
            print("still %.1f s" % float(sec))
        return

    cmd = [ff, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(total):
        proc.stdin.write(frame_at(f / FPS, tl).tobytes())
        if f % 240 == 0:
            print("  %d / %d frames (%.1f s)" % (f, total, f / FPS), flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote %s  (%.2f s, %d frames)" % (out_path, total / FPS, total))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--crf", type=int, default=23)
    ap.add_argument("--out", default=os.path.join(BUILD, "video.mp4"))
    a = ap.parse_args()
    tl = json.load(open(os.path.join(BUILD, "timeline.json")))
    stills = [x for x in a.stills.split(",") if x.strip()] if a.stills else None
    render(tl, a.out, a.crf, stills)
