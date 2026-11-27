"""জমিদার বাড়ি — 2-minute Bengali conversational horror, stickman rig.

Five characters, five voices, per-line lip sync, five night environments.
No subtitles: on-screen Bengali exists only as diegetic story props (the title
on the gate, the carved names on the wall, the end card).
"""
import copy
import math
import os
import re
import subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import sys, os as _os
sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import bt
import hbg
from char import Pose, render
from rig import CHARACTERS, clamp01, lerp, smoothstep

W, H = 1920, 1080
FPS = 30
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
VO = os.path.join(HERE, "vo_fx")

# ----------------------------------------------------------------- cast
CHARACTERS = dict(CHARACTERS)
# Sujon without the office briefcase — he is here to knock a building down
_s = copy.deepcopy(CHARACTERS["boss"]); _s.briefcase = False; _s.tie = True
CHARACTERS["boss_nb"] = _s
CAST = {"malati": "mentor", "sujon": "boss", "rahul": "student", "kamal": "rival", "zamindar": "king"}

# ----------------------------------------------------------------- the dialogue
# (id, who, start, dur, text-is-property-only) — durations measured from vo_fx
LINES = [
    dict(n=1,  who="malati",   t0=9.0,   d=7.84),
    dict(n=2,  who="sujon",    t0=18.4,  d=6.80),
    dict(n=3,  who="malati",   t0=28.0,  d=7.72),
    dict(n=4,  who="sujon",    t0=37.2,  d=4.20),
    dict(n=5,  who="rahul",    t0=44.0,  d=6.20),
    dict(n=6,  who="kamal",    t0=51.6,  d=8.00),
    dict(n=7,  who="rahul",    t0=61.6,  d=6.64),
    dict(n=8,  who="sujon",    t0=71.2,  d=6.88),
    dict(n=9,  who="zamindar", t0=86.0,  d=8.64),
    dict(n=10, who="zamindar", t0=97.0,  d=4.84),
]
TOTAL = 120.0


def line_at(t):
    for L in LINES:
        if L["t0"] <= t <= L["t0"] + L["d"]:
            return L
    return None


def other_talking(t, who):
    """True while a different character is mid-line — used for listener reactions."""
    L = line_at(t)
    return bool(L and L["who"] != who)


def mouth(t, L):
    """Per-character mouth opening, driven by the measured line window."""
    if L is None:
        return 0.0, 0.0
    a = (t - L["t0"]) / max(0.001, L["d"])
    if a < 0 or a > 1:
        return 0.0, 0.0
    v = 0.5 + 0.5 * (0.62 * math.sin(t * 11.3) + 0.38 * math.sin(t * 6.9 + 1.7))
    env = smoothstep(0.0, 0.045, a) * (1 - smoothstep(0.94, 1.0, a))
    return clamp01(v) * env, a


# ----------------------------------------------------------------- lighting
def night_grade(im, tint=(150, 172, 255), lift=0.11, contrast=0.9, gain=1.5):
    """Cool moonlight: tint, lifted blacks, softened contrast."""
    arr = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb = arr[..., :3] / 255.0
    rgb = rgb * np.array([tint[0] / 255, tint[1] / 255, tint[2] / 255]) * gain
    rgb = (rgb - 0.5) * contrast + 0.5
    rgb = rgb + lift * (1 - np.clip(rgb, 0, 1))
    arr[..., :3] = np.clip(rgb, 0, 1) * 255
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


_POOL = {}
_SPR = {}


def cap_cache(cache, limit):
    """Bound a dict cache — keeps the 3.9 GB sandbox from OOMing mid-render."""
    while len(cache) > limit:
        cache.pop(next(iter(cache)))



def lamp_pool(frame, cx, cy, r, colour=(255, 196, 112), strength=0.55):
    """Additive pool of light — torch / lamp / candle. Mask is cached per position."""
    key = (frame.size, int(cx / 4), int(cy / 4), int(r / 4), colour, round(strength, 2))
    if key not in _POOL:
        w, h = frame.size
        yy, xx = np.ogrid[:h, :w]
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        m = (np.clip(1 - d, 0, 1) ** 2 * strength).astype(np.float32)
        # store ONE channel and scale per channel on use — a full RGB mask is
        # 24 MB at 1080p and this cache is keyed on a moving torch position.
        _POOL[key] = m
        cap_cache(_POOL, 4)
    m = _POOL[key]
    arr = np.asarray(frame).astype(np.float32)
    for i in range(3):
        arr[..., i] += m * colour[i]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), frame.mode)


def darkness(frame, amount):
    """How much of the frame survives — raises as the film goes on."""
    arr = np.asarray(frame).astype(np.float32) * (1 - amount)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), frame.mode)


_VIG = {}


def vignette(img, strength=0.9):
    key = (img.size, round(strength, 2))
    if key not in _VIG:
        w, h = img.size
        y, x = np.ogrid[:h, :w]
        r = np.sqrt(((x - w / 2) / (w * 0.62)) ** 2 + ((y - h / 2) / (h * 0.62)) ** 2)
        m = np.clip((r - 0.72) / (1.35 - 0.72), 0, 1) ** 1.5 * strength
        _VIG[key] = (1.0 - m)[..., None].astype(np.float32)
    arr = np.asarray(img).astype(np.float32) * _VIG[key]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), img.mode)


# ----------------------------------------------------------------- the world
class World:
    def __init__(self, base):
        self.img = base.convert("RGBA")

    def char(self, key, pose, hip_x, ground_y, scale=1.0, shadow=True, alpha=1.0,
             darken=0.0, silhouette=False):
        """Place a character with its FEET on ground_y.

        The sprite canvas is 1.16P x 1.22P with the hip at (0.5W, 0.53H); a
        standing figure's feet sit 0.462P below the hip, so the hip must be
        pushed up by exactly that much before pasting.
        """
        ch = CHARACTERS[key]
        P = ch.height
        ck = (key, hip_x, ground_y, scale, darken, silhouette, alpha, shadow,
              tuple(round(v, 3) for v in (pose.torso, pose.head, pose.mouth,
                                          pose.smile, pose.brow, pose.blink,
                                          pose.flip)))
        s = _SPR.get(ck)
        if s is None:
            s = render(ch, pose, scale=scale)
            _SPR[ck] = s
            cap_cache(_SPR, 48)
        if silhouette:
            # flat cut-out: keep the alpha, throw the palette away
            a = np.zeros((s.height, s.width, 4), dtype=np.uint8)
            a[..., 0], a[..., 1], a[..., 2] = 9, 10, 13
            a[..., 3] = np.asarray(s)[..., 3]
            s = Image.fromarray(a, "RGBA")
        elif darken > 0:
            dk = round(darken, 2)
            kd = ("dk", id(s) if False else ck, dk)
            s2 = _SPR.get(kd)
            if s2 is None:
                a = np.asarray(s).astype(np.float32)
                a[..., :3] *= (1 - dk)
                s2 = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
                _SPR[kd] = s2
                cap_cache(_SPR, 48)
            s = s2
        w, h = s.size
        hip_y = ground_y - 0.462 * P * scale
        px, py = int(hip_x - w / 2), int(hip_y - 0.53 * h)
        if shadow:
            sw, sh = int(w * 0.55), int(h * 0.055)
            sh_img = Image.new("RGBA", (sw + 60, sh + 60), (0, 0, 0, 0))
            ImageDraw.Draw(sh_img).ellipse([30, 30, 30 + sw, 30 + sh], fill=(0, 0, 0, 150))
            sh_img = sh_img.filter(ImageFilter.GaussianBlur(13))
            self.img.alpha_composite(sh_img, (int(hip_x - sh_img.width / 2), int(ground_y - sh_img.height * 0.42)))
        if alpha < 0.999:
            s = s.copy()
            s.putalpha(s.split()[3].point(lambda v: int(v * alpha)))
        self.img.alpha_composite(s, (px, py))
        return self

    def paste(self, im, x, y, alpha=1.0):
        if alpha < 0.999:
            im = im.copy()
            im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
        self.img.alpha_composite(im.convert("RGBA"), (int(x), int(y)))
        return self

    def out(self):
        return self.img.convert("RGB")


def camera(img, zoom=1.0, cx=0.5, cy=0.5):
    w, h = img.size
    cw, ch = int(w / zoom), int(h / zoom)
    x0 = int(clamp01(cx) * w - cw / 2)
    y0 = int(clamp01(cy) * h - ch / 2)
    x0 = max(0, min(w - cw, x0)); y0 = max(0, min(h - ch, y0))
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BILINEAR)


# ----------------------------------------------------------------- poses
def pose_stand(P=700, **kw):
    p = dict(hip=(0, 0), torso=0.02, head=0.0,
             foot_n=(0.105 * P, 0.462 * P), foot_f=(-0.115 * P, 0.462 * P),
             hand_n=(0.175 * P, 0.215 * P), hand_f=(-0.195 * P, 0.225 * P),
             coat=0.0, blink=1.0, mouth=0.0, smile=0.45, brow=0.0, look=0.0)
    p.update(kw)
    return Pose(**p)


def blink_at(t, seed=0.0, every=3.1, length=0.15):
    ph = (t + seed) % every
    if ph < length:
        return 1.0 - math.sin(ph / length * math.pi) * 0.95
    return 1.0


def shake(t, amp, freq=7.0, seed=0.0):
    return amp * math.sin(t * freq + seed) * math.sin(t * freq * 0.37 + 1.3)


# ----------------------------------------------------------------- scenes
def bg(name):
    return hbg.get(name)


# --- 1. exteriors / gate -------------------------------------------------
def shot_gate(t, dur):
    """0–18.4 : fog, gate, Malati waiting, Sujon's jeep lights arrive."""
    base = bg("gate")
    P = 700
    w = World(base)
    # camera: slow push toward the gate
    z = 1.0 + 0.05 * smoothstep(0, dur, t)
    cx = 0.5 + 0.02 * smoothstep(0, dur, t)

    # Malati stands at the gate from 4 s
    if t > 3.4:
        a = smoothstep(3.4, 4.6, t)
        mal_x = 1010 + 8 * math.sin(t * 0.7)
        L = line_at(t) if line_at(t) and line_at(t)["who"] == "malati" else None
        mo, _ = mouth(t, L)
        w.char("mentor", pose_stand(P,
                                    torso=0.03 + 0.02 * math.sin(t * 1.1),
                                    head=-0.05,
                                    hand_n=(0.24 * P, 0.10 * P),
                                    hand_f=(-0.20 * P, 0.20 * P),
                                    mouth=mo, smile=0.15, brow=0.35,
                                    blink=blink_at(t, 0.4)),
               mal_x, 862, scale=1.02, alpha=a)
    # Sujon walks in from the left at 12 s, torch up
    if t > 11.0:
        a = smoothstep(11.0, 12.2, t)
        x = lerp(-160, 620, smoothstep(11.0, 16.5, t))
        ph = t * 7.4
        L = line_at(t) if line_at(t) and line_at(t)["who"] == "sujon" else None
        mo, _ = mouth(t, L)
        moving = t < 16.3
        w.char("boss_nb", pose_stand(P,
                                  torso=0.05 if moving else 0.02,
                                  foot_n=(0.105 * P + (0.10 * P * math.sin(ph) if moving else 0),
                                          0.462 * P - (0.05 * P * max(0, math.cos(ph)) if moving else 0)),
                                  foot_f=(-0.115 * P + (-0.10 * P * math.sin(ph) if moving else 0),
                                          0.462 * P - (0.05 * P * max(0, -math.cos(ph)) if moving else 0)),
                                  hand_n=(0.21 * P, 0.12 * P),
                                  hand_f=(-0.24 * P, 0.06 * P),
                                  mouth=mo, smile=0.25, brow=0.5,
                                  blink=blink_at(t, 1.2)),
               x, 866, scale=1.04, alpha=a)
        # torch cone from his hand
        tx = x + 0.21 * P
        f = w.out()
        f = lamp_pool(f, tx, 830, 330, strength=0.30)
        w = World(f)
    f = camera(w.out(), zoom=z, cx=cx, cy=0.52)
    f = darkness(f, 0.10 + 0.06 * smoothstep(dur * 0.6, dur, t))
    return vignette(f, 0.92)


# --- 2. courtyard --------------------------------------------------------
def shot_yard(t, dur):
    """18.4–37.2 : the courtyard, the lamp, the argument."""
    base = bg("courtyard")
    P = 700
    w = World(base)
    z = 1.02 + 0.05 * smoothstep(0, dur, t)
    cx = 0.5 - 0.01 * smoothstep(0, dur, t)

    # Sujon left third, facing right; Malati right third, facing left
    L = line_at(t)
    mo_s = mouth(t, L) if L and L["who"] == "sujon" else (0.0, 0.0)
    mo_m = mouth(t, L) if L and L["who"] == "malati" else (0.0, 0.0)

    suj_x = 700 + shake(t, 3.0)
    w.char("boss_nb", pose_stand(P,
                              torso=0.05, head=-0.03,
                              hand_n=(0.30 * P, 0.05 * P + 0.02 * P * math.sin(t * 2.2)),
                              hand_f=(-0.22 * P, 0.12 * P),
                              mouth=mo_s[0], smile=0.15, brow=0.7,
                              blink=blink_at(t, 2.1)),
           suj_x, 888, scale=1.06)
    listening = 1.0 if other_talking(t, "malati") else 0.0
    w.char("mentor", pose_stand(P,
                                torso=0.00, head=0.06 - 0.04 * listening,
                                hand_n=(0.25 * P, 0.06 * P),
                                hand_f=(-0.19 * P, 0.18 * P),
                                mouth=mo_m[0], smile=0.10 - 0.06 * listening,
                                brow=0.45 + 0.30 * listening,
                                blink=blink_at(t, 0.9),
                                flip=True),
           1180, 888, scale=1.02)

    f = camera(w.out(), zoom=z, cx=cx, cy=0.55)
    f = lamp_pool(f, 1340, 400, 420, strength=0.22)
    f = darkness(f, 0.12 + 0.05 * smoothstep(0, dur, t))
    return vignette(f, 0.93)


# --- 3. corridor: the names ---------------------------------------------
def shot_names(t, dur):
    """37.2–51.6 : corridor + the carved names + the window."""
    base = bg("corridor")
    P = 700
    w = World(base)
    z = 1.04 + 0.06 * smoothstep(0, dur, t)
    cx = 0.44 + 0.05 * smoothstep(0, dur, t)

    L = line_at(t)
    mo_r = mouth(t, L) if L and L["who"] == "rahul" else (0.0, 0.0)
    mo_s = mouth(t, L) if L and L["who"] == "sujon" else (0.0, 0.0)

    # Rahul at the name wall, torch up on it
    recoil = 1.0 if other_talking(t, "rahul") else 0.0
    w.char("student", pose_stand(672,
                                 torso=0.06 + 0.06 * recoil, head=-0.10 - 0.06 * recoil,
                                 hand_n=(0.26 * 672, (0.05 + 0.03 * recoil) * 672),
                                 hand_f=(-0.21 * 672, 0.16 * 672),
                                 mouth=mo_r[0], smile=0.10 - 0.06 * recoil, brow=0.85 + 0.10 * recoil,
                                 blink=blink_at(t, 1.7)),
           470, 930, scale=1.10)
    # Sujon further back, arms out
    if t > 6.0:
        w.char("boss_nb", pose_stand(P,
                                  torso=0.08, head=-0.02,
                                  hand_n=(0.32 * P, 0.03 * P),
                                  hand_f=(-0.32 * P, 0.05 * P),
                                  mouth=mo_s[0], smile=0.10, brow=0.8,
                                  blink=blink_at(t, 0.3)),
               900, 930, scale=1.02, darken=0.25)

    f = camera(w.out(), zoom=z, cx=cx, cy=0.5)
    f = lamp_pool(f, 760, 700, 380, strength=0.26)
    f = lamp_pool(f, 1580, 560, 420, strength=0.18)
    f = darkness(f, 0.16 + 0.06 * smoothstep(dur * 0.5, dur, t))
    return vignette(f, 0.94)


# --- 4. window room: Kamal sees the shape --------------------------------
def shot_window(t, dur):
    """51.6–61.6 : the side room, the shape at the window."""
    base = bg("window")
    P = 700
    w = World(base)
    z = 1.05 + 0.07 * smoothstep(0, dur, t)
    cx = 0.52

    L = line_at(t)
    mo_k = mouth(t, L) if L and L["who"] == "kamal" else (0.0, 0.0)
    mo_r = mouth(t, L) if L and L["who"] == "rahul" else (0.0, 0.0)

    # the figure at the window — a silhouette with no face, appears 3.6s
    if t > 3.6:
        a = smoothstep(3.6, 4.6, t) * 0.92
        w.char("king", pose_stand(P,
                                  torso=0.00, head=0.02,
                                  hand_n=(0.17 * P, 0.24 * P),
                                  hand_f=(-0.19 * P, 0.24 * P),
                                  smile=0.0, brow=0.0, blink=1.0),
               1400, 900, scale=1.10, alpha=a, shadow=False, silhouette=True)
    k_listen = 1.0 if other_talking(t, "kamal") else 0.0
    w.char("rival", pose_stand(P,
                               torso=0.10 + 0.04 * k_listen, head=-0.06 - 0.05 * k_listen,
                               hand_n=(0.20 * P, (0.05 + 0.04 * k_listen) * P),
                               hand_f=(-0.24 * P, 0.02 * P),
                               mouth=mo_k[0], smile=0.05 - 0.05 * k_listen, brow=0.9 + 0.05 * k_listen,
                               blink=blink_at(t, 0.4)),
           780, 946, scale=1.04)
    w.char("student", pose_stand(672,
                                 torso=0.10, head=-0.12,
                                 hand_n=(0.22 * 672, 0.16 * 672),
                                 hand_f=(-0.22 * 672, 0.16 * 672),
                                 mouth=mo_r[0], smile=0.10, brow=0.8,
                                 blink=blink_at(t, 2.3)),
           1140, 946, scale=1.0, darken=0.18)

    f = camera(w.out(), zoom=z, cx=cx, cy=0.5)
    f = lamp_pool(f, 900, 700, 300, strength=0.10, colour=(180, 200, 255))
    f = darkness(f, 0.20 + 0.08 * smoothstep(dur * 0.4, dur, t))
    return vignette(f, 0.95)


# --- 5. the throne room: the landlord -----------------------------------
def shot_landlord(t, dur):
    """61.6–120 : Sujon shouting into the dark, then the landlord speaks."""
    base = bg("throne")
    P = 700
    w = World(base)
    z = 1.03 + 0.10 * smoothstep(0, dur, t)
    cx = 0.5

    L = line_at(t)
    mo_s = mouth(t, L) if L and L["who"] == "sujon" else (0.0, 0.0)
    mo_r = mouth(t, L) if L and L["who"] == "rahul" else (0.0, 0.0)
    mo_z = mouth(t, L) if L and L["who"] == "zamindar" else (0.0, 0.0)

    # the landlord: only his outline in the chair until 12 s, then he stands
    # he resolves out of the dark only once he starts speaking (t = 20.4)
    rising = smoothstep(18.0, 21.0, t)
    alpha = 0.34 + 0.60 * rising
    w.char("king", pose_stand(P,
                              torso=0.02 + 0.03 * math.sin(t * 0.8),
                              head=0.04,
                              hand_n=(0.30 * P, 0.02 * P),
                              hand_f=(-0.30 * P, 0.02 * P),
                              mouth=mo_z[0], smile=0.0, brow=0.2,
                              blink=1.0),
           960, 1022, scale=1.34, alpha=alpha, shadow=False,
           silhouette=(rising < 0.99), darken=0.45 * (1 - rising))

    # at 110.5 the doors come down: everything except the landlord goes dark
    if t > 48.9:                      # global 110.5
        k = smoothstep(48.9, 49.6, t)
        f = camera(w.out(), zoom=z, cx=cx, cy=0.5)
        f = darkness(f, 0.24 + 0.10 * smoothstep(0, dur, t) + 0.62 * k)
        f = vignette(f, 0.96)
        if t > 51.0:                  # global 112.6
            k2 = smoothstep(51.0, 52.0, t)
            black = np.asarray(f).astype(np.float32) * (1.0 - k2)
            f = Image.fromarray(np.clip(black, 0, 255).astype(np.uint8), "RGB")
        return f

    # the two humans, small, foreground left and right
    w.char("boss_nb", pose_stand(P,
                              torso=0.06, head=-0.06,
                              hand_n=(0.30 * P, 0.02 * P),
                              hand_f=(-0.28 * P, 0.06 * P),
                              mouth=mo_s[0], smile=0.10, brow=0.85,
                              blink=blink_at(t, 1.1)),
           420, 1010, scale=0.94, darken=0.42)
    w.char("student", pose_stand(672,
                                 torso=0.10, head=-0.10,
                                 hand_n=(0.22 * 672, 0.14 * 672),
                                 hand_f=(-0.22 * 672, 0.14 * 672),
                                 mouth=mo_r[0], smile=0.05, brow=0.9,
                                 blink=blink_at(t, 2.6)),
           1500, 1010, scale=0.90, darken=0.46)

    f = camera(w.out(), zoom=z, cx=cx, cy=0.5)
    # a dying cold light from the windows, and the landlord's own dark glow
    f = lamp_pool(f, 960, 640, 520, strength=0.10, colour=(120, 150, 230))
    f = darkness(f, 0.24 + 0.10 * smoothstep(0, dur, t))
    # heartbeat pulse under the last lines
    if t > 30:
        amp = 0.03 + 0.02 * math.sin(t * 3.4)
        f = darkness(f, amp)
    return vignette(f, 0.96)


# --- card helpers --------------------------------------------------------
def title_card(img, alpha=1.0):
    """The film title, chalk on the gate."""
    f = bt.font(bt.FONT_SERIF, 800, 132)
    block = f.block(["জমিদার বাড়ি"], color=(236, 232, 226), stroke=(6, 6, 8), stroke_w=4)
    if alpha < 0.999:
        block.putalpha(block.split()[3].point(lambda v: int(v * alpha)))
    x = (img.width - block.width) // 2
    y = 210
    out = img.convert("RGBA")
    out.alpha_composite(block, (int(x), int(y)))
    return out.convert("RGB")


def end_card(img, alpha=1.0):
    """Final card on black — two measured lines, no overlap."""
    out = img.convert("RGBA")
    f1 = bt.font(bt.FONT_SERIF, 800, 96)
    f2 = bt.font(bt.FONT_SANS, 800, 62)
    b1 = f1.block(["তোমরাও থাকবে।"], color=(228, 224, 216), stroke=(5, 5, 7), stroke_w=3)
    b2 = f2.block(["চিরকাল। আমার সাথে।"], color=(168, 34, 40), stroke=(5, 5, 7), stroke_w=3)
    if alpha < 0.999:
        for b in (b1, b2):
            b.putalpha(b.split()[3].point(lambda v: int(v * alpha)))
    gap = 46
    total = b1.height + gap + b2.height
    y0 = (img.height - total) // 2 - 30
    out.alpha_composite(b1, ((img.width - b1.width) // 2, y0))
    out.alpha_composite(b2, ((img.width - b2.width) // 2, y0 + b1.height + gap))
    return out.convert("RGB")


def overlay_prop(base, lines, x, y, size, color, align="left", alpha=1.0, serif=True, stroke_w=2):
    f = bt.font(bt.FONT_SERIF if serif else bt.FONT_SANS, 800, size)
    img = f.block(lines, color=color, stroke=(8, 8, 10), stroke_w=stroke_w, align=align)
    if alpha < 0.999:
        img.putalpha(img.split()[3].point(lambda v: int(v * alpha)))
    out = base.convert("RGBA")
    out.alpha_composite(img, (int(x), int(y)))
    return out.convert("RGB")


# ----------------------------------------------------------------- frames
def render_frame(t):
    # --- 0.0–18.4 gate
    if t < 18.4:
        f = shot_gate(t, 18.4)
        if t < 6.2:
            a = smoothstep(0.6, 2.4, t) * (1 - smoothstep(4.8, 6.2, t))
            f = title_card(f, a)
        return f
    # --- 18.4–37.2 courtyard
    if t < 37.2:
        return shot_yard(t - 18.4, 18.8)
    # --- 37.2–51.6 corridor
    if t < 51.6:
        return shot_names(t - 37.2, 14.4)
    # --- 51.6–61.6 window room
    if t < 61.6:
        return shot_window(t - 51.6, 10.0)
    # --- 61.6–120 throne room
    f = shot_landlord(t - 61.6, TOTAL - 61.6)
    if t > 113.6:
        f = end_card(f, smoothstep(113.6, 114.8, t))
    return f


# ----------------------------------------------------------------- audio
def build_audio():
    SR = 44100
    n = int(TOTAL * SR)
    track = np.zeros(n + SR, dtype=np.float32)

    def add(path, at):
        dec = subprocess.run([FF, "-v", "error", "-i", path, "-f", "s16le",
                              "-ac", "1", "-ar", str(SR), "-"],
                             capture_output=True, check=True)
        x = np.frombuffer(dec.stdout, dtype=np.int16).astype(np.float32) / 32768
        i = int(at * SR)
        j = min(len(track), i + len(x))
        track[i:j] += x[: j - i]

    for L in LINES:
        add(os.path.join(VO, f"{L['n']:02d}_{L['who']}.wav"), L["t0"])

    # --- drone: two detuned low sines + filtered noise, swelling over the film
    t = np.arange(len(track)) / SR
    prog = np.clip(t / TOTAL, 0, 1)
    drone = (0.055 * np.sin(2 * np.pi * 55 * t) +
             0.040 * np.sin(2 * np.pi * 55.6 * t + 0.7) +
             0.030 * np.sin(2 * np.pi * 82.5 * t + 1.9))
    drone *= (0.25 + 0.75 * prog)                 # grows
    # slow amplitude breathing
    drone *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.07 * t)
    track += drone.astype(np.float32)

    # --- noise bed (wind / room air), shaped with a moving low-pass
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 1, len(track)).astype(np.float32)
    # cheap one-pole low-pass with a slowly moving cutoff
    a = 0.02 + 0.05 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.03 * t))
    out = np.empty_like(noise)
    acc = 0.0
    for i in range(0, len(noise), 1):
        acc += a[i] * (noise[i] - acc)
        out[i] = acc
    rms = np.sqrt((out ** 2).mean()) or 1.0
    track += (out / rms * 0.035).astype(np.float32)

    # --- hits and stingers
    def hit(at, f0=48, dur=1.6, amp=0.28):
        i = int(at * SR); ln = int(dur * SR)
        if i >= len(track): return
        tt = np.arange(ln) / SR
        x = np.sin(2 * np.pi * f0 * tt * np.exp(-tt * 1.2)) * np.exp(-tt * 2.2) * amp
        j = min(len(track), i + ln)
        track[i:j] += x[: j - i].astype(np.float32)

    def sting(at, amp=0.16):
        i = int(at * SR); ln = int(2.2 * SR)
        if i >= len(track): return
        tt = np.arange(ln) / SR
        x = (np.sin(2 * np.pi * 1400 * tt) * 0.5 +
             np.sin(2 * np.pi * 1870 * tt) * 0.3 +
             np.sin(2 * np.pi * 2610 * tt) * 0.2) * np.exp(-tt * 2.6) * amp
        j = min(len(track), i + ln)
        track[i:j] += x[: j - i].astype(np.float32)

    hit(0.4, 40, 3.0, 0.22)          # cold open
    hit(18.4, 46, 2.0, 0.20)         # into the courtyard
    hit(37.2, 44, 2.2, 0.24)         # corridor
    hit(51.6, 52, 2.0, 0.20)
    hit(61.6, 42, 2.6, 0.26)
    sting(86.0, 0.20)                # the landlord speaks
    sting(97.0, 0.18)
    hit(110.6, 36, 4.0, 0.30)        # doors slam
    hit(112.2, 33, 4.0, 0.24)

    # --- the door slam + final silence
    def slam(at, amp=0.5):
        i = int(at * SR); ln = int(1.4 * SR)
        if i >= len(track): return
        tt = np.arange(ln) / SR
        x = rng.normal(0, 1, ln).astype(np.float32) * np.exp(-tt * 9) * 0.5
        x += np.sin(2 * np.pi * 42 * tt) * np.exp(-tt * 7) * 0.8
        j = min(len(track), i + ln)
        track[i:j] += (x[: j - i] * amp).astype(np.float32)

    slam(110.6)
    slam(112.1, 0.35)

    # --- final fade to silence after 115 s
    env = np.ones_like(track)
    k0, k1 = int(113.0 * SR), int(TOTAL * SR)
    env[k0:k1] = np.linspace(1.0, 0.0, k1 - k0) ** 1.6
    env[k1:] = 0.0
    track *= env

    # --- normalise, then keep peaks sane
    peak = np.abs(track).max() or 1.0
    track *= min(1.0, 0.92 / peak)

    st = np.stack([track, track], axis=1)
    pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()
    mix = os.path.join(HERE, "..", "build", "horror_mix.wav")
    os.makedirs(os.path.dirname(mix), exist_ok=True)
    subprocess.run([FF, "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", "-t", f"{TOTAL:.3f}", "-c:a", "pcm_s16le", mix],
                   input=pcm, check=True)
    print(f"audio {TOTAL:.2f}s -> {mix}", flush=True)
    return mix


# ----------------------------------------------------------------- main
def main():
    os.makedirs("../output", exist_ok=True)
    mix = build_audio()
    out = "../output/zamindar_bari_bangla_horror.mp4"
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
