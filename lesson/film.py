"""সোনার হরিণ — 2-minute Bengali lesson fable, stickman rig.

Improves on the horror short in three ways:
  * lip sync is driven by the real amplitude envelope of each recorded line,
    not a synthetic sine wave;
  * speakers are blocked in a consistent left/right grammar so cross-cutting
    between them reads as a conversation;
  * every listener carries a reaction track (brow, chin, weight shift).
"""
import copy
import math
import os
import re
import subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import sys
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))

import bt
import lbg
from char import Pose, render
from rig import CHARACTERS, Palette, clamp01, lerp, smoothstep

W, H, FPS = 1920, 1080, 30
FF = imageio_ffmpeg.get_ffmpeg_exe()
VO = os.path.join(_HERE, "vo_fx")
TOTAL = 120.0
SR = 44100

# --------------------------------------------------------------- extra cast
CHARACTERS = dict(CHARACTERS)
_h = copy.deepcopy(CHARACTERS["king"])          # the headman: no crown, village cloth
_h.crown = False
_h.pal = Palette(skin=(196, 139, 94), skin_d=(162, 108, 70), hair=(58, 44, 40),
                 top=(146, 74, 42), top_d=(108, 52, 30), top_l=(176, 100, 60),
                 pants=(64, 52, 46), shoe=(52, 40, 30),
                 accent=(214, 178, 96), accent_d=(170, 138, 64))
CHARACTERS["headman"] = _h
_s = copy.deepcopy(CHARACTERS["boss"])          # Sujon, no office briefcase
_s.briefcase = False
CHARACTERS["sujon"] = _s

# ------------------------------------------------------------------ lines
LINES = [
    dict(n=1,  who="rahul",   t0=6.6,   d=4.48),
    dict(n=2,  who="malati",  t0=12.6,  d=5.72),
    dict(n=3,  who="sujon",   t0=21.0,  d=5.68),
    dict(n=4,  who="kamal",   t0=29.8,  d=6.64),
    dict(n=5,  who="rahul",   t0=39.4,  d=2.32),
    dict(n=6,  who="kamal",   t0=43.6,  d=8.56),
    dict(n=7,  who="headman", t0=55.4,  d=6.48),
    dict(n=8,  who="sujon",   t0=64.4,  d=5.44),
    dict(n=9,  who="malati",  t0=72.6,  d=5.08),
    dict(n=10, who="headman", t0=80.4,  d=8.00),
]


def line_at(t):
    for L in LINES:
        if L["t0"] <= t <= L["t0"] + L["d"]:
            return L
    return None


def other_talking(t, who):
    L = line_at(t)
    return bool(L and L["who"] != who)


# ------------------------------------------------- envelope-driven lip sync
class Env:
    """Per-line loudness envelope, normalised, with a fast-open / slow-close gate."""

    def __init__(self, path, hop=1 / 60.0):
        r = subprocess.run([FF, "-v", "error", "-i", path, "-f", "s16le",
                            "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True)
        x = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768
        win = int(SR * hop)
        n = max(1, len(x) // win)
        e = np.sqrt((x[: n * win].reshape(n, win) ** 2).mean(axis=1))
        lo, hi = np.percentile(e, 12), np.percentile(e, 96)
        e = np.clip((e - lo) / max(1e-5, hi - lo), 0, 1)
        # smooth, then open fast / close slower so mouths don't chatter
        k = np.array([0.25, 0.5, 0.25])
        e = np.convolve(np.pad(e, 1, mode="edge"), k, "valid")
        self.e, self.hop = e, hop

    def at(self, t_local):
        i = int(round(t_local / self.hop))
        return float(self.e[min(len(self.e) - 1, max(0, i))])


ENVS = {L["n"]: Env(os.path.join(VO, f"{L['n']:02d}_{L['who']}.wav")) for L in LINES}


def mouth(t, who):
    """Mouth value 0..1 for the character speaking at time t (0 if silent)."""
    L = line_at(t)
    if not L or L["who"] != who:
        return 0.0
    a = (t - L["t0"]) / max(1e-3, L["d"])
    v = ENVS[L["n"]].at(t - L["t0"])
    gate = smoothstep(0.0, 0.04, a) * (1 - smoothstep(0.95, 1.0, a))
    return clamp01(v * 1.15) * gate


# ------------------------------------------------------------------ posing
def stand(P=700, **kw):
    p = dict(hip=(0, 0), torso=0.02, head=0.0,
             foot_n=(0.105 * P, 0.462 * P), foot_f=(-0.115 * P, 0.462 * P),
             hand_n=(0.175 * P, 0.215 * P), hand_f=(-0.195 * P, 0.225 * P),
             coat=0.0, blink=1.0, mouth=0.0, smile=0.45, brow=0.0, look=0.0)
    p.update(kw)
    return Pose(**p)


def blink_at(t, seed=0.0, every=3.2, length=0.15):
    ph = (t + seed) % every
    if ph < length:
        return 1.0 - math.sin(ph / length * math.pi) * 0.95
    return 1.0


def breathe(t, amp=0.012, speed=1.1, seed=0.0):
    return amp * math.sin(t * speed * 2 * math.pi / 3.0 + seed)


_DEER = {}


def deer_sprite(scale=1.0):
    """A golden deer drawn with the same hand as the cast: soft body, tall antlers."""
    key = round(scale, 2)
    if key in _DEER:
        return _DEER[key]
    w_, h_ = int(420 * scale), int(400 * scale)
    im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    gold = (232, 186, 92, 255)
    gold_d = (196, 150, 66, 255)
    edge = (150, 112, 46, 255)
    S = scale

    def P(*pts):
        return [(x * S, y * S) for x, y in pts]

    # body + neck + head
    d.ellipse(P((60, 190), (300, 300)), fill=gold, outline=edge, width=int(3 * S))
    d.polygon(P((250, 210), (286, 244), (330, 170), (306, 150)), fill=gold, outline=edge)
    d.line(P((286, 244), (330, 170)), fill=edge, width=int(3 * S))
    d.ellipse(P((300, 108), (386, 180)), fill=gold, outline=edge, width=int(3 * S))
    # muzzle
    d.polygon(P((372, 132), (404, 140), (404, 158), (368, 160)), fill=gold, outline=edge)
    # ear
    d.polygon(P((330, 106), (344, 78), (360, 110)), fill=gold_d, outline=edge)
    # antlers
    for base, tip, mid in (((340, 108), (312, 26), (330, 60)),
                           ((356, 104), (392, 20), (372, 58))):
        d.line(P(base, mid), fill=edge, width=int(5 * S))
        d.line(P(mid, tip), fill=edge, width=int(4 * S))
        d.line(P(mid, (mid[0] + 22, mid[1] - 26)), fill=edge, width=int(3 * S))
    # legs
    for x0 in (110, 158, 246, 286):
        d.line(P((x0, 286), (x0 - 6, 372)), fill=gold_d, width=int(9 * S))
        d.line(P((x0 - 6, 372), (x0 + 4, 376)), fill=edge, width=int(5 * S))
    # tail
    d.line(P((70, 214), (40, 196)), fill=gold_d, width=int(7 * S))
    # spots — the thing that makes it read as a deer at a glance
    for (sx, sy) in ((140, 224), (186, 216), (228, 232), (168, 258), (212, 264)):
        d.ellipse(P((sx - 7, sy - 7), (sx + 7, sy + 7)), fill=(250, 224, 160, 255))
    # eye
    d.ellipse(P((352, 136), (364, 148)), fill=(40, 30, 22, 255))
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    _DEER[key] = im
    return im


# --------------------------------------------------------------- blocking
GROUND = 900          # the line everybody stands on at depth 0


def place(depth, x):
    """Screen position + scale for a character at `depth` (0 = near, 1 = far)."""
    scale = lerp(1.10, 0.62, depth)
    ground = lerp(GROUND, 706, depth)
    return x, ground, scale


# ---------------------------------------------------------------- lighting
def warmth(im, gain=1.06, lift=0.03):
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb = a[..., :3] / 255.0 * gain
    rgb = rgb + lift * (1 - np.clip(rgb, 0, 1))
    a[..., :3] = np.clip(rgb, 0, 1) * 255
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def cold(im, tint=(176, 210, 182), gain=1.0, toe=0.05):
    """Cold grade that keeps the picture legible: desaturate toward green, lift the
    shadows a little, and don't touch overall level."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb = a[..., :3] / 255.0
    lum = rgb @ np.array([0.30, 0.59, 0.11])
    cold_ = np.stack([lum] * 3, -1) * np.array([t / 255 for t in tint]) * 1.28
    rgb = rgb * 0.42 + cold_ * 0.58
    rgb = rgb * gain
    rgb = rgb * (1 - toe) + toe * np.array([0.06, 0.10, 0.07])
    a[..., :3] = np.clip(rgb, 0, 1) * 255
    return Image.fromarray(a.astype(np.uint8), "RGBA")


_VIG, _SPR, _POOL = {}, {}, {}


def cap(d, n):
    while len(d) > n:
        d.pop(next(iter(d)))


def vignette(img, s=0.5):
    key = (img.size, round(s, 2))
    if key not in _VIG:
        w, h = img.size
        y, x = np.ogrid[:h, :w]
        r = np.sqrt(((x - w / 2) / (w * .62)) ** 2 + ((y - h / 2) / (h * .62)) ** 2)
        m = np.clip((r - .78) / (1.4 - .78), 0, 1) ** 1.4 * s
        _VIG[key] = (1.0 - m)[..., None].astype(np.float32)
    a = np.asarray(img).astype(np.float32) * _VIG[key]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), img.mode)


def glow(frame, cx, cy, r, colour=(255, 190, 120), strength=0.5):
    key = (frame.size, int(cx / 6), int(cy / 6), int(r / 6), round(strength, 2))
    m = _POOL.get(key)
    if m is None:
        w, h = frame.size
        yy, xx = np.ogrid[:h, :w]
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        m = (np.clip(1 - d, 0, 1) ** 2.2 * strength).astype(np.float32)
        _POOL[key] = m
        cap(_POOL, 4)
    a = np.asarray(frame).astype(np.float32)
    for i in range(3):
        a[..., i] += m * colour[i]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), frame.mode)


def camera(img, zoom=1.0, cx=0.5, cy=0.5):
    w, h = img.size
    cw, ch = int(w / zoom), int(h / zoom)
    x0 = int(clamp01(cx) * w - cw / 2); y0 = int(clamp01(cy) * h - ch / 2)
    x0 = max(0, min(w - cw, x0)); y0 = max(0, min(h - ch, y0))
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BILINEAR)


# ------------------------------------------------------------------ world
class World:
    def __init__(self, base):
        self.img = base.convert("RGBA")

    def char(self, key, pose, x, ground, scale=1.0, darken=0.0, shadow=True):
        ch = CHARACTERS[key]
        P = ch.height
        ck = (key, round(x, 1), ground, scale, round(darken, 2), shadow,
              tuple(round(v, 3) for v in (pose.torso, pose.head, pose.mouth, pose.smile,
                                          pose.brow, pose.blink, pose.flip, pose.look)))
        s = _SPR.get(ck)
        if s is None:
            s = render(ch, pose, scale=scale)
            if darken > 0:
                a = np.asarray(s).astype(np.float32)
                a[..., :3] *= (1 - darken)
                s = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
            _SPR[ck] = s
            cap(_SPR, 40)
        w, h = s.size
        hip_y = ground - 0.462 * P * scale
        px, py = int(x - w / 2), int(hip_y - 0.53 * h)
        if shadow:
            sw, sh = int(w * 0.52), int(h * 0.05)
            im = Image.new("RGBA", (sw + 60, sh + 60), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse([30, 30, 30 + sw, 30 + sh], fill=(30, 20, 12, 120))
            im = im.filter(ImageFilter.GaussianBlur(12))
            self.img.alpha_composite(im, (int(x - im.width / 2), int(ground - im.height * 0.45)))
        self.img.alpha_composite(s, (px, py))
        return self

    def paste(self, im, x, y):
        self.img.alpha_composite(im, (int(x), int(y)))
        return self

    def out(self):
        return self.img.convert("RGB")


# ------------------------------------------------------------- text props
def _block(lines, size, colour, serif=True, stroke_w=3):
    f = bt.font(bt.FONT_SERIF if serif else bt.FONT_SANS, 800, size)
    return f.block(lines, color=colour, stroke=(18, 12, 8), stroke_w=stroke_w)


def card(img, lines, size, colour, y=None, alpha=1.0, serif=True):
    b = _block(lines, size, colour, serif)
    if alpha < 0.999:
        b.putalpha(b.split()[3].point(lambda v: int(v * alpha)))
    out = img.convert("RGBA")
    yy = (img.height - b.height) // 2 if y is None else y
    out.alpha_composite(b, ((img.width - b.width) // 2, yy))
    return out.convert("RGB")


# ------------------------------------------------------------------ shots
def shot_porch(t, dur):
    """Dusk porch: the boy asks, the grandmother answers. She is near, he is nearer."""
    mo_r = mouth(t, "rahul")
    mo_m = mouth(t, "malati")
    lis_r = 1.0 if other_talking(t, "rahul") else 0.0
    lis_m = 1.0 if other_talking(t, "malati") else 0.0

    w = World(lbg.get("porch"))
    # a bench under the beam, so they sit rather than stand in a field
    w.char("mentor", stand(672,
                           torso=0.07, head=0.06 - 0.05 * lis_m,
                           foot_n=(0.15 * 672, 0.430 * 672), foot_f=(-0.15 * 672, 0.430 * 672),
                           hand_n=(0.20 * 672, 0.17 * 672),
                           hand_f=(-0.18 * 672, (0.20 + 0.02 * lis_m) * 672),
                           mouth=mo_m, smile=0.58 - 0.12 * lis_m, brow=0.12 + 0.34 * lis_m,
                           blink=blink_at(t, 0.6)), 700, 905, scale=1.16)
    w.char("student", stand(672,
                            torso=0.05, head=-0.02 + 0.06 * lis_r,
                            foot_n=(0.12 * 672, 0.430 * 672), foot_f=(-0.12 * 672, 0.430 * 672),
                            hand_n=(0.23 * 672, (0.13 + 0.03 * lis_r) * 672),
                            hand_f=(-0.19 * 672, 0.20 * 672),
                            mouth=mo_r, smile=0.30 + 0.22 * lis_r, brow=0.22 + 0.38 * lis_r,
                            blink=blink_at(t, 1.8), flip=True), 1150, 918, scale=1.22)

    z = 1.0 + 0.06 * smoothstep(0, dur, t)
    f = camera(w.out(), zoom=z, cx=0.5, cy=0.58)
    f = glow(f, 400, 500, 480, (255, 190, 112), 0.16)
    return vignette(f, 0.45)


def shot_square(t, dur):
    """Evening square: Sujon comes back loud, the others are further away."""
    w = World(lbg.get("square"))
    # the grandmother and the boy, up on the porch edge (far)
    xm, gm, sm = place(0.55, 1500)
    xb, gb, sb = place(0.58, 1660)
    lis = 1.0 if other_talking(t, "malati") else 0.0
    w.char("mentor", stand(672, torso=0.03, head=0.02,
                           hand_n=(0.19 * 672, 0.20 * 672), hand_f=(-0.19 * 672, 0.20 * 672),
                           mouth=0.0, smile=0.36 - 0.10 * lis, brow=0.2 + 0.3 * lis,
                           blink=blink_at(t, 0.9)), xm, gm, scale=sm)
    w.char("student", stand(672, torso=0.05, head=-0.03,
                            hand_n=(0.21 * 672, 0.15 * 672), hand_f=(-0.20 * 672, 0.21 * 672),
                            mouth=mouth(t, "rahul"), smile=0.3, brow=0.4,
                            blink=blink_at(t, 2.2), flip=True), xb, gb, scale=sb)

    # Sujon, near, walking in
    walk = smoothstep(0.0, 3.8, t)
    x = lerp(-40, 620, walk)
    moving = t < 3.8
    ph = t * 7.0
    mo_s = mouth(t, "sujon")
    xs, gs, ss = place(0.02, x)
    w.char("sujon", stand(700,
                          torso=0.05 if moving else 0.03,
                          head=-0.02,
                          foot_n=(0.105 * 700 + (0.09 * 700 * math.sin(ph) if moving else 0),
                                  0.462 * 700 - (0.05 * 700 * max(0, math.cos(ph)) if moving else 0)),
                          foot_f=(-0.115 * 700 + (-0.09 * 700 * math.sin(ph) if moving else 0),
                                  0.462 * 700 - (0.05 * 700 * max(0, -math.cos(ph)) if moving else 0)),
                          hand_n=(0.27 * 700, (0.10 + 0.05 * math.sin(t * 2.4)) * 700),
                          hand_f=(-0.24 * 700, 0.14 * 700),
                          mouth=mo_s, smile=0.30, brow=0.55,
                          blink=blink_at(t, 1.1)), xs, gs, scale=ss)

    z = 1.02 + 0.06 * smoothstep(0, dur, t)
    f = camera(w.out(), zoom=z, cx=0.46, cy=0.56)
    f = glow(f, 770, 700, 380, (255, 186, 110), 0.14)
    return vignette(f, 0.45)


def shot_fire(t, dur):
    """Kamal by the fire; the boy sits across it, smaller, further back."""
    w = World(lbg.get("fire"))
    mo_k = mouth(t, "kamal")
    mo_r = mouth(t, "rahul")
    lis = 1.0 if other_talking(t, "kamal") else 0.0

    xk, gk, sk = place(0.05, 700)
    w.char("rival", stand(700,
                          torso=0.04, head=-0.02,
                          hand_n=(0.26 * 700, (0.10 + 0.03 * math.sin(t * 1.7)) * 700),
                          hand_f=(-0.21 * 700, 0.18 * 700),
                          mouth=mo_k, smile=0.15, brow=0.5 + 0.2 * lis,
                          blink=blink_at(t, 0.5)), xk, gk, scale=sk)
    xr, gr, sr = place(0.42, 1330)
    w.char("student", stand(672, torso=0.06, head=0.03,
                            hand_n=(0.22 * 672, 0.16 * 672), hand_f=(-0.20 * 672, 0.21 * 672),
                            mouth=mo_r, smile=0.28, brow=0.4,
                            blink=blink_at(t, 2.4), flip=True), xr, gr, scale=sr)

    z = 1.03 + 0.06 * smoothstep(0, dur, t)
    f = camera(w.out(), zoom=z, cx=0.5, cy=0.55)
    f = glow(f, 960, 850, 560, (255, 150, 66), 0.20)
    return vignette(f, 0.55)


def shot_forest(t, dur):
    """The memory: Kamal walked in years ago. Cold, open, and too quiet."""
    w = World(lbg.get("forest"))
    mo_k = mouth(t, "kamal")
    # slow push-in behind him — we are following, not watching
    z = 1.04 + 0.10 * smoothstep(0, dur, t)
    # he stops walking halfway through L6, when the deer turns
    walk = 1.0 - smoothstep(4.2, 5.4, t)
    ph = t * 5.4
    xk, gk, sk = place(0.10, 830)
    w.char("rival", stand(700,
                          torso=0.04 + 0.02 * walk,
                          head=-0.04 - 0.05 * smoothstep(5.0, 7.0, t),
                          foot_n=(0.10 * 700 + 0.085 * 700 * math.sin(ph) * walk,
                                  0.462 * 700 - 0.05 * 700 * max(0, math.cos(ph)) * walk),
                          foot_f=(-0.11 * 700 - 0.085 * 700 * math.sin(ph) * walk,
                                  0.462 * 700 - 0.05 * 700 * max(0, -math.cos(ph)) * walk),
                          hand_n=(0.24 * 700, (0.12 + 0.02 * math.sin(t * 1.9)) * 700),
                          hand_f=(-0.22 * 700, 0.18 * 700),
                          mouth=mo_k, smile=0.10, brow=0.45 + 0.2 * smoothstep(5.0, 7.0, t),
                          blink=blink_at(t, 0.7)), xk, gk, scale=sk)

    # the deer: gold, half-seen, standing still between the trunks
    if t > 3.6:
        a = smoothstep(3.6, 5.0, t)
        # it comes a little closer as it is noticed
        g = 1.02 + 0.10 * smoothstep(4.6, dur, t)
        deer = deer_sprite(round(g, 2))
        if a < 0.999:
            deer.putalpha(deer.split()[3].point(lambda v: int(v * a)))
        dx, dy = 1060, 470
        w.paste(deer, dx, dy)
        f = w.out()
        f = glow(f, dx + 200, dy + 200, 420, (255, 216, 130), 0.40 * a)
        # rim light so the gold separates from the green
        f = glow(f, dx + 40, dy + 190, 260, (255, 230, 170), 0.20 * a)
        return vignette(camera(f, zoom=z, cx=0.5, cy=0.52), 0.60)

    f = camera(w.out(), zoom=z, cx=0.5, cy=0.52)
    f = glow(f, 900, 300, 700, (150, 175, 120), 0.18)
    # a cool rim behind him: the forest is behind, not on top of, the man
    f = glow(f, xk + 30 * sk, gk - 320 * sk, 330 * sk, (196, 224, 190), 0.26)
    # light drains as the shot runs
    arr = np.asarray(f).astype(np.float32) * (1 - 0.12 * smoothstep(0, dur, t))
    return vignette(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB"), 0.58)


def _last_setup():
    """Grandmother on the porch, headman beside her, the boy's absence in the gap."""
    return World(lbg.get("porch"))


def shot_last_a(t, dur):
    """Wide: L10 begins. The camera is far back and closes in slowly."""
    w = _last_setup()
    mo_h = mouth(t, "headman")
    mo_m = mouth(t, "malati")
    lis = 1.0 if other_talking(t, "headman") else 0.0
    w.char("mentor", stand(672,
                           torso=0.04, head=0.03 - 0.05 * lis,
                           foot_n=(0.14 * 672, 0.430 * 672), foot_f=(-0.14 * 672, 0.430 * 672),
                           hand_n=(0.19 * 672, (0.18 + 0.03 * lis) * 672),
                           hand_f=(-0.18 * 672, 0.21 * 672),
                           mouth=mo_m, smile=0.40 - 0.14 * lis, brow=0.16 + 0.34 * lis,
                           blink=blink_at(t, 0.5)), 700, 912, scale=1.02)
    w.char("headman", stand(700, torso=0.02, head=0.03,
                            hand_n=(0.25 * 700, (0.11 + 0.04 * math.sin(t * 1.5)) * 700),
                            hand_f=(-0.22 * 700, 0.18 * 700),
                            mouth=mo_h, smile=0.14, brow=0.22,
                            blink=blink_at(t, 1.4), flip=True), 1350, 900, scale=0.99)
    z = 1.0 + 0.13 * smoothstep(0, dur, t)
    f = camera(w.out(), zoom=z, cx=0.44, cy=0.60)
    f = glow(f, 380, 500, 470, (255, 172, 92), 0.13)
    arr = np.asarray(f).astype(np.float32) * (1 - 0.10 * smoothstep(0, dur, t))
    return vignette(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB"), 0.5)


def shot_last_b(t, dur):
    """Close on the headman. He is the one saying the hard thing."""
    w = _last_setup()
    mo_h = mouth(t, "headman")
    x, g, sc = place(0.18, 620)
    w.char("headman", stand(760, torso=0.03, head=0.02,
                            hand_n=(0.24 * 760, (0.13 + 0.03 * math.sin(t * 1.6)) * 760),
                            hand_f=(-0.23 * 760, 0.19 * 760),
                            mouth=mo_h, smile=0.12, brow=0.30 + 0.18 * abs(math.sin(t * 0.9)),
                            blink=blink_at(t, 0.9)), x, g - 60, scale=sc * 1.14)
    z = 1.06 + 0.07 * smoothstep(0, dur, t)
    f = camera(w.out(), zoom=z, cx=0.32, cy=0.34)
    f = glow(f, 360, 470, 430, (255, 168, 88), 0.12)
    arr = np.asarray(f).astype(np.float32) * (1 - 0.20 * smoothstep(0, dur, t))
    return vignette(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB"), 0.52)


def shot_last_c(t, dur):
    """The empty side of the porch, and the light going out of it."""
    w = _last_setup()
    mo_m = mouth(t, "malati")
    x, g, sc = place(0.18, 760)
    w.char("mentor", stand(672,
                           torso=0.05, head=0.05,
                           foot_n=(0.14 * 672, 0.430 * 672), foot_f=(-0.14 * 672, 0.430 * 672),
                           hand_n=(0.19 * 672, (0.18 + 0.02 * math.sin(t * 1.2)) * 672),
                           hand_f=(-0.18 * 672, 0.21 * 672),
                           mouth=mo_m, smile=0.30, brow=0.22,
                           blink=blink_at(t, 1.2)), x, g - 60, scale=sc * 1.10)
    z = 1.04 + 0.10 * smoothstep(0, dur, t)
    f = camera(w.out(), zoom=z, cx=0.56, cy=0.36)
    f = glow(f, 380, 500, 470, (255, 166, 86), 0.13)
    arr = np.asarray(f).astype(np.float32) * (1 - 0.40 * smoothstep(0, dur, t))
    return vignette(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB"), 0.55)


def shot_banyan(t, dur):
    """The headman under the banyan: the moral."""
    P = 700
    w = World(lbg.get("banyan"))
    z = 1.02 + 0.07 * smoothstep(0, dur, t)
    mo_h = mouth(t, "headman")
    mo_s = mouth(t, "sujon")
    lis = 1.0 if other_talking(t, "headman") else 0.0

    w.char("headman", stand(P,
                            torso=0.02, head=0.02,
                            hand_n=(0.23 * P, (0.14 + 0.03 * math.sin(t * 1.3)) * P),
                            hand_f=(-0.22 * P, 0.19 * P),
                            mouth=mo_h, smile=0.20, brow=0.25,
                            blink=blink_at(t, 0.8)), 980, 880, scale=1.0)
    # nobody else here: the headman speaks to the village, and to the boy
    w.char("student", stand(672, torso=0.05, head=0.02,
                            hand_n=(0.21 * 672, 0.15 * 672), hand_f=(-0.20 * 672, 0.21 * 672),
                            mouth=mouth(t, "rahul"), smile=0.3, brow=0.45,
                            blink=blink_at(t, 2.7)), 440, 906, scale=1.02)

    f = camera(w.out(), zoom=z, cx=0.5, cy=0.55)
    f = glow(f, 1420, 740, 440, (255, 178, 96), 0.16)
    return vignette(f, 0.5)


# ----------------------------------------------------------------- frames
def render_frame(t):
    if t < 21.0:
        f = shot_porch(t, 21.0)
        if t < 5.6:
            a = smoothstep(0.3, 1.8, t) * (1 - smoothstep(4.2, 5.6, t))
            # a soft band in the sky so the type never fights a silhouette
            band = Image.new("RGBA", f.size, (0, 0, 0, 0))
            bd = ImageDraw.Draw(band)
            bd.rectangle([0, 40, f.width, 300], fill=(8, 8, 16, int(150 * a)))
            band = band.filter(ImageFilter.GaussianBlur(70))
            f = Image.alpha_composite(f.convert("RGBA"), band).convert("RGB")
            f = card(f, ["সোনার হরিণ"], 116, (252, 234, 198), y=64, alpha=a)
            f = card(f, ["ভাগ ১ — লোভের পাঠ"], 44, (255, 206, 138), y=214, alpha=a * 0.95)
        return f
    if t < 39.0:
        return shot_square(t - 21.0, 18.0)
    if t < 55.4:
        return shot_fire(t - 39.0, 6.4) if t < 45.4 else shot_forest(t - 45.4, 10.0)
    if t < 63.0:
        return shot_banyan(t - 55.4, 7.6)
    if t < 71.0:
        return shot_square(t - 63.0, 8.0)
    if t < 80.4:
        return shot_banyan(t - 71.0, 9.4)
    if t < 92.0:
        f = shot_last_a(t - 80.4, 11.6)
    elif t < 104.0:
        f = shot_last_b(t - 92.0, 12.0)
    else:
        f = shot_last_c(t - 104.0, TOTAL - 104.0)
    if t > 112.0:
        a = smoothstep(112.0, 113.4, t)
        arr = np.asarray(f).astype(np.float32) * (1 - 0.55 * a)
        f = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    if t > 113.6:
        a = smoothstep(113.6, 114.8, t)
        f = card(f, ["লোভে পাপ, পাপে মৃত্যু"], 86, (250, 226, 178), alpha=a)
    return f


# ----------------------------------------------------------------- audio
def build_audio(out_path):
    n = int((TOTAL + 1) * SR)
    tr = np.zeros(n, dtype=np.float32)

    def add(path, at):
        r = subprocess.run([FF, "-v", "error", "-i", path, "-f", "s16le", "-ac", "1",
                            "-ar", str(SR), "-"], capture_output=True, check=True)
        x = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768
        i = int(at * SR); j = min(n, i + len(x))
        tr[i:j] += x[: j - i]

    for L in LINES:
        add(os.path.join(VO, f"{L['n']:02d}_{L['who']}.wav"), L["t0"])

    t = np.arange(n) / SR
    prog = np.clip(t / TOTAL, 0, 1)
    # warm drone + a slow plucked motif (a village evening, not a horror bed)
    bed = (0.035 * np.sin(2 * np.pi * 73.4 * t) +
           0.026 * np.sin(2 * np.pi * 110.0 * t + 0.6) +
           0.018 * np.sin(2 * np.pi * 146.8 * t + 1.2))
    bed *= 0.55 + 0.45 * np.sin(2 * np.pi * 0.045 * t)
    bed *= 0.5 + 0.5 * (1 - prog)
    tr += bed.astype(np.float32)

    # soft "tanpura" plucks every 4 s, fading with the film
    for k in range(int(TOTAL / 4)):
        i = int(k * 4.0 * SR); ln = int(2.4 * SR)
        if i >= n: break
        tt = np.arange(ln) / SR
        f0 = 146.8 if k % 2 == 0 else 110.0
        x = (np.sin(2 * np.pi * f0 * tt) * 0.5 + np.sin(2 * np.pi * f0 * 2 * tt) * 0.2)
        x *= np.exp(-tt * 2.4) * 0.035
        j = min(n, i + ln); tr[i:j] += x[: j - i].astype(np.float32)

    # wind / leaves
    rng = np.random.default_rng(5)
    nz = rng.normal(0, 1, n).astype(np.float32)
    acc = 0.0
    for i in range(n):
        acc += 0.02 * (nz[i] - acc)
        nz[i] = acc
    nz /= (np.sqrt((nz ** 2).mean()) or 1)
    tr += (nz * 0.018).astype(np.float32)

    # gentle musical sting under each cut, low in the mix
    for at in (21.0, 39.0, 45.4, 55.4, 63.0, 71.0, 80.4):
        i = int(at * SR); ln = int(1.8 * SR)
        if i >= n: break
        tt = np.arange(ln) / SR
        x = np.sin(2 * np.pi * 98 * tt) * np.exp(-tt * 2.0) * 0.10
        j = min(n, i + ln); tr[i:j] += x[: j - i].astype(np.float32)

    env = np.ones(n)
    k0, k1 = int(114.0 * SR), int(TOTAL * SR)
    env[k0:k1] = np.linspace(1, 0.0, k1 - k0) ** 1.4
    env[k1:] = 0
    tr *= env
    tr *= min(1.0, 0.90 / (np.abs(tr).max() or 1))

    st = np.stack([tr, tr], axis=1)
    pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()
    subprocess.run([FF, "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", "-t", f"{TOTAL:.3f}", "-c:a", "pcm_s16le", out_path],
                   input=pcm, check=True)
    print(f"audio {TOTAL:.2f}s -> {out_path}", flush=True)


def main():
    mix = os.path.join(_HERE, "..", "build", "lesson_mix.wav")
    os.makedirs(os.path.dirname(mix), exist_ok=True)
    out = os.path.join(_HERE, "..", "output", "sonar_horin_bangla_lesson.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build_audio(mix)
    cmd = [FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", mix,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
           "-threads", "2", "-x264-params", "rc-lookahead=10:ref=1:bframes=2",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    n = int(round(TOTAL * FPS))
    for fi in range(n):
        frame = render_frame(fi / FPS)
        proc.stdin.write(np.asarray(frame.convert("RGB"), dtype=np.uint8).tobytes())
        if fi % 60 == 0:
            print(f"  {fi}/{n}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("done ->", out, flush=True)


if __name__ == "__main__":
    main()
