"""Law 5 explainer — Bangla voice-over, 2D rigged characters, no subtitles.

Per-shot: build a 1920x1080 world image, then apply a virtual camera
(crop + resize) and a screen-space text overlay.
"""
import math
import os
import re
import subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import bg
import bt
from char import Pose, render
from rig import CHARACTERS, clamp01, lerp, smoothstep, vlerp

W, H = 1920, 1080
FPS = 30
FF = imageio_ffmpeg.get_ffmpeg_exe()

AUDIO = [
    ("audio/01_intro.mp3", 0.50),
    ("audio/02_king.mp3", 0.50),
    ("audio/03_business.mp3", 0.50),
    ("audio/04_young.mp3", 0.50),
    ("audio/05_mentor.mp3", 0.50),
    ("audio/06_close.mp3", 0.75),
]


# ------------------------------------------------------------------ fonts
def F_HEAD(sz):
    return bt.font(bt.FONT_SANS, 800, sz)


def F_TITLE(sz):
    return bt.font(bt.FONT_SERIF, 800, sz)


def dur_of(path):
    """Exact clip duration in seconds, read from ffmpeg's Duration: line."""
    out = subprocess.run([FF, "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", out)
    if not m:
        raise RuntimeError(f"no duration for {path}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


# ------------------------------------------------------------------ sprite cache
CACHE_FRAMES = 240  # rendered-frame LRU: re-renders cost ~90 ms, keeping >240 blows memory


def sprite(key, tag, pose, scale):
    return render(CHARACTERS[key], pose, scale=scale)


FRAME_CACHE = {}
FRAME_ORDER = []


def render_frame_cached(t_global, timeline):
    sig = round(t_global * 2) / 2  # half-frame granularity is enough for stills/tests
    hit = FRAME_CACHE.get(sig)
    if hit is not None:
        return hit
    shot = timeline[-1]
    for s in timeline:
        if s["start"] <= t_global < s["start"] + s["dur"]:
            shot = s
            break
    img = SHOTS[shot["index"]](t_global - shot["start"], shot["dur"])
    if len(FRAME_CACHE) >= CACHE_FRAMES:
        for k in FRAME_ORDER[:60]:
            FRAME_CACHE.pop(k, None)
        del FRAME_ORDER[:60]
    FRAME_CACHE[sig] = img
    FRAME_ORDER.append(sig)
    return img


SHADOW = None


def shadow_sprite(w, h, alpha=110):
    key = (w // 10, h // 10, alpha)
    global SHADOW
    if SHADOW is None:
        SHADOW = {}
    if key in SHADOW:
        return SHADOW[key]
    blur = max(4, h // 2)
    im = Image.new("RGBA", (w + blur * 4, h + blur * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([blur * 2, blur * 2, blur * 2 + w, blur * 2 + h], fill=(10, 8, 14, alpha))
    im = im.filter(ImageFilter.GaussianBlur(blur))
    im = im.crop((blur, blur, blur + w + blur * 2, blur + h + blur * 2))
    SHADOW[key] = im
    return im


def std(P, **kw):
    p = dict(hip=(0.0, 0.0), torso=0.02, head=0.0,
             foot_n=(0.105 * P, 0.462 * P), foot_f=(-0.115 * P, 0.462 * P),
             hand_n=(0.175 * P, 0.215 * P), hand_f=(-0.195 * P, 0.225 * P),
             coat=0.0, blink=1.0, mouth=0.0, smile=0.55, brow=0.0, look=0.0)
    p.update(kw)
    return Pose(**p)


def blink_at(t, seed=0.0, every=2.7, length=0.14):
    ph = (t + seed) % every
    if ph < length:
        return 1.0 - math.sin(ph / length * math.pi) * 0.96
    return 1.0


def mouth_for(t, start, end, seed=0.0):
    if not (start <= t <= end):
        return 0.0
    a = math.sin((t - start) * 11.0 + seed)
    b = math.sin((t - start) * 6.7 + 1.7 + seed)
    v = 0.5 + 0.5 * (0.6 * a + 0.4 * b)
    return clamp01(v) * 0.6 * smoothstep(start, start + 0.22, t) * (1 - smoothstep(end - 0.25, end, t))


def walk_feet(P, phase, stride=0.19, lift=0.05):
    def step(ph):
        if ph < 0.5:
            u = ph / 0.5
            return (lerp(stride * 0.5, -stride * 0.5, u) * P, 0.462 * P)
        u = (ph - 0.5) / 0.5
        e = smoothstep(0, 1, u)
        return (lerp(-stride * 0.5, stride * 0.5, e) * P,
                (0.462 - math.sin(u * math.pi) * lift) * P)
    return step(phase % 1.0), step((phase + 0.5) % 1.0)


# ------------------------------------------------------------------ canvas
class World:
    def __init__(self, background):
        self.img = background.convert("RGBA").copy()

    def char(self, key, pose, scale, cx, ground_y, alpha=1.0, shadow=True, flip=False):
        ch = CHARACTERS[key]
        P = ch.height
        pose.flip = flip
        im = sprite(key, "s", pose, scale)
        hip_x = cx
        hip_y = ground_y - 0.462 * P * scale
        px = int(hip_x - im.width * 0.5)
        py = int(hip_y - im.height * 0.53)
        if shadow:
            sw = int(0.30 * P * scale * 2)
            sh = shadow_sprite(sw, max(10, int(sw * 0.26)), alpha=95)
            self.img.alpha_composite(sh, (int(cx - sw / 2), int(ground_y - sh.height * 0.55)))
        if alpha >= 0.995:
            self.img.alpha_composite(im, (px, py))
        else:
            tmp = im.copy()
            tmp.putalpha(tmp.split()[3].point(lambda v: int(v * alpha)))
            self.img.alpha_composite(tmp, (px, py))

    def paste(self, im, x, y):
        self.img.alpha_composite(im, (int(x), int(y)))

    def glow(self, cx, cy, r, color=(255, 200, 130), alpha=40):
        g = Image.new("RGBA", (int(r * 2), int(r * 2)), (0, 0, 0, 0))
        d = ImageDraw.Draw(g)
        d.ellipse([0, 0, r * 2 - 1, r * 2 - 1], fill=color + (alpha,))
        g = g.filter(ImageFilter.GaussianBlur(r * 0.45))
        self.img.alpha_composite(g, (int(cx - r), int(cy - r)))


def camera(world, zoom=1.0, cx=W / 2, cy=H / 2):
    if zoom <= 1.001:
        return world
    vw, vh = W / zoom, H / zoom
    x0 = min(max(0, cx - vw / 2), W - vw)
    y0 = min(max(0, cy - vh / 2), H - vh)
    box = (int(x0), int(y0), int(x0 + vw), int(y0 + vh))
    return world.crop(box).resize((W, H), Image.LANCZOS)


def overlay_text(base, lines, x, y, size=64, color=(255, 236, 200), font=None,
                 stroke=(12, 10, 18), align="left", alpha=1.0):
    if alpha <= 0.01:
        return base
    f = font or F_HEAD(size)
    img = f.block(lines, color=color, stroke=stroke, stroke_w=3, align=align)
    if alpha < 0.995:
        img.putalpha(img.split()[3].point(lambda v: int(v * alpha)))
    out = base.convert("RGBA")
    out.alpha_composite(img, (int(x), int(y)))
    return out


def chapter_chip(frame, t):
    """Small persistent 'Law 5' chapter label — a title, not a subtitle."""
    a = smoothstep(0.4, 1.2, t)
    if a <= 0.01:
        return frame
    out = frame.convert("RGBA")
    chip = Image.new("RGBA", (470, 86), (0, 0, 0, 0))
    d = ImageDraw.Draw(chip)
    d.rounded_rectangle([0, 0, 469, 85], radius=42, fill=(12, 14, 26, 168),
                        outline=(226, 176, 74, 150), width=3)
    out.alpha_composite(chip, (60, 52))
    img = F_HEAD(40).block(["সূত্র ৫ · সুনাম"], color=(255, 224, 170))
    img.putalpha(img.split()[3].point(lambda v: int(v * a)))
    out.alpha_composite(img, (98, 58))
    return out


def fade(img, k):
    k = clamp01(k)
    if k >= 0.999:
        return img
    black = Image.new("RGBA", img.size, (0, 0, 0, 255))
    return Image.blend(black, img, k)


# ------------------------------------------------------------------ shots
def shot_intro(t, dur):
    """King walks in, stops, points at the title."""
    world = World(bg.get("title"))
    P = CHARACTERS["king"].height
    enter = smoothstep(0.0, 1.9, t)
    x = lerp(420, 690, enter)
    if t < 1.9:
        fn, ff = walk_feet(P, t * 1.9)
        pose = std(P, foot_n=fn, foot_f=ff, torso=0.06,
                   hip=(0, -abs(math.sin(t * 1.9 * math.pi)) * 0.014 * P),
                   hand_n=(0.15 * P, 0.235 * P), hand_f=(-0.185 * P, 0.245 * P),
                   blink=blink_at(t, 0.4), mouth=0.0, smile=0.35, brow=0.2,
                   coat=0.008 * math.sin(t * 5))
    else:
        k = smoothstep(1.9, 2.6, t)
        pose = std(P, torso=lerp(0.06, -0.02, k),
                   hand_n=(lerp(0.15, 0.33, k) * P, lerp(0.235, -0.10, k) * P
                           + 0.010 * P * math.sin(t * 3.4) * k),
                   hand_f=(-0.19 * P, 0.24 * P), head=0.02 * math.sin(t * 1.6),
                   blink=blink_at(t, 0.4), mouth=mouth_for(t, 2.3, dur - 0.5),
                   smile=0.5, brow=0.3)
    world.char("king", pose, 1.10, x, 1005)
    world.glow(690, 640, 520, (255, 190, 120), 26)

    # title block fades in on the right
    a1 = smoothstep(0.7, 1.7, t)
    a2 = smoothstep(1.1, 2.1, t)
    a3 = smoothstep(1.5, 2.6, t)
    zoom = 1.0 + 0.05 * smoothstep(0, dur, t)
    frame = camera(world.img, zoom, 900, 540)
    frame = overlay_text(frame, ["রবার্ট গ্রিনের", "৪৮টি ক্ষমতার সূত্র"], 1030, 300, 62,
                         color=(255, 226, 174), font=F_TITLE(62), alpha=a1)
    frame = overlay_text(frame, ["সূত্র ৫"], 1032, 430, 176, color=(255, 176, 92), alpha=a2)
    frame = overlay_text(frame, ["সুনাম রক্ষা করুন"], 1028, 680, 92,
                         color=(255, 248, 228), font=F_TITLE(92), alpha=a3)
    if a3 > 0:
        d = ImageDraw.Draw(frame)
        sw = int(620 * smoothstep(1.9, 3.0, t))
        d.rectangle([1030, 662, 1030 + sw, 671], fill=(226, 176, 74, int(235 * a3)))
    return fade(frame, smoothstep(0, 0.5, t) * (1 - smoothstep(dur - 0.6, dur, t)))


def shot_king(t, dur):
    """The king explains reputation; a rival enters and recoils."""
    world = World(bg.get("hall"))
    P = CHARACTERS["king"].height
    Pr = CHARACTERS["rival"].height

    # rival walks in from the left, then bows / recoils
    renter = smoothstep(0.3, 2.3, t)
    rx = lerp(-320, 520, renter)
    if t < 2.3:
        rfn, rff = walk_feet(Pr, t * 1.6 + 0.2)
        rpose = std(Pr, foot_n=rfn, foot_f=rff, torso=0.05,
                    hip=(0, -abs(math.sin(t * 1.6 * math.pi)) * 0.012 * Pr),
                    smile=0.05, brow=-0.2, look=0.5, blink=blink_at(t, 1.3),
                    hand_n=(0.16 * Pr, 0.235 * Pr))
    else:
        bow = smoothstep(2.3, 3.1, t) * (1 - smoothstep(4.0, 4.8, t))
        rec = smoothstep(4.8, 5.6, t)
        rpose = std(Pr, torso=0.28 * bow - 0.05 * rec,
                    head=0.16 * bow - 0.06 * rec,
                    hand_n=(0.11 * Pr, 0.20 * Pr), hand_f=(-0.17 * Pr, 0.235 * Pr),
                    smile=-0.1 - 0.2 * rec, brow=-0.30 * bow - 0.15 * rec,
                    look=0.2 + 0.3 * rec, blink=blink_at(t, 1.3),
                    foot_n=(0.10 * Pr, 0.462 * Pr), foot_f=(-0.12 * Pr, 0.462 * Pr))
    world.char("rival", rpose, 1.00, rx, 1030)

    # king: settles, then declares with a raised, beating hand
    decl = smoothstep(3.0, 4.2, t)
    beat = 0.012 * P * math.sin((t - 3.0) * 5.2) * decl
    pose = std(P, torso=lerp(0.04, -0.03, decl),
               head=0.03 * math.sin(t * 1.4) - 0.02 * decl,
               hand_n=(lerp(0.175, 0.31, decl) * P, lerp(0.215, -0.075, decl) * P + beat),
               hand_f=(-0.205 * P, 0.245 * P),
               blink=blink_at(t, 0.6), mouth=mouth_for(t, 0.15, dur - 0.5),
               smile=lerp(0.45, 0.62, decl), brow=lerp(0.15, 0.4, decl),
               coat=0.006 * math.sin(t * 3.2))
    world.char("king", pose, 1.10, 1300, 1030)
    # warm light from the hall lamps
    world.glow(1260, 620, 560, (255, 186, 120), 22)
    world.glow(430, 520, 420, (210, 170, 255), 12)

    zoom = 1.0 + 0.06 * smoothstep(2.0, dur, t)
    frame = camera(world.img, zoom, lerp(1000, 1080, smoothstep(0, dur, t)), 540)
    frame = chapter_chip(frame, t)
    return fade(frame, smoothstep(0, 0.45, t) * (1 - smoothstep(dur - 0.55, dur, t)))


def shot_boss(t, dur):
    """Modern workplace: image is armour, crowds read you at a glance."""
    world = World(bg.get("city"))
    P = CHARACTERS["boss"].height
    # crowd of passers-by behind
    for i in range(8):
        speed = 70 + i * 11
        sx = ((t * speed + i * 300) % (W + 500)) - 250
        sc = 0.60 + (i % 3) * 0.05
        key = "student" if i % 2 == 0 else ("mentor" if i % 3 == 0 else "rival")
        pk = CHARACTERS[key].height
        fn, ff = walk_feet(pk, t * 1.7 + i * 0.3)
        pop = std(pk, foot_n=fn, foot_f=ff, torso=0.05,
                  hip=(0, -abs(math.sin((t * 1.7 + i * 0.3) * math.pi)) * 0.012 * pk),
                  smile=0.15, blink=1.0)
        world.char(key, pop, sc, sx, 1005, alpha=0.30, shadow=False)

    enter = smoothstep(0.0, 2.1, t)
    x = lerp(300, 700, enter)
    if t < 2.1:
        fn, ff = walk_feet(P, t * 1.8)
        pose = std(P, foot_n=fn, foot_f=ff, torso=0.05,
                   hip=(0, -abs(math.sin(t * 1.8 * math.pi)) * 0.014 * P),
                   hand_n=(0.16 * P, 0.235 * P), hand_f=(-0.19 * P, 0.245 * P),
                   blink=blink_at(t, 0.3), smile=0.4, brow=0.1)
    else:
        adj = smoothstep(2.1, 2.7, t) * (1 - smoothstep(3.2, 3.8, t))
        gest = smoothstep(3.4, 4.4, t)
        talk = math.sin(t * 5.6) * 0.5 + 0.5
        pose = std(P, hip=(0, -0.002 * P * abs(math.sin(t * 1.9))),
                   torso=lerp(0.03, -0.03, gest),
                   head=0.02 * math.sin(t * 1.5),
                   hand_n=((lerp(0.175, 0.145, adj) + 0.155 * gest) * P,
                           (lerp(0.215, 0.058, adj) - 0.055 * gest) * P
                           + 0.010 * P * talk * gest),
                   hand_f=(-0.205 * P, 0.245 * P),
                   blink=blink_at(t, 0.3), mouth=mouth_for(t, 2.2, dur - 0.5),
                   smile=lerp(0.45, 0.68, gest), brow=lerp(0.1, 0.28, gest))
    world.char("boss", pose, 1.16, x, 1030)
    world.glow(x, 620, 520, (255, 190, 140), 20)

    zoom = 1.0 + 0.05 * smoothstep(1.5, dur, t)
    frame = camera(world.img, zoom, 860, 540)
    frame = chapter_chip(frame, t)
    return fade(frame, smoothstep(0, 0.45, t) * (1 - smoothstep(dur - 0.55, dur, t)))


def shot_student(t, dur):
    """Built over years, broken in a moment — shield cracks."""
    world = World(bg.get("campus"))
    P = CHARACTERS["student"].height
    walk_end = 4.3
    if t < walk_end:
        fn, ff = walk_feet(P, t * 1.75)
        x = lerp(240, 760, smoothstep(0, walk_end, t))
        pose = std(P, foot_n=fn, foot_f=ff, torso=0.05,
                   hip=(0, -abs(math.sin(t * 1.75 * math.pi)) * 0.014 * P),
                   hand_n=(0.16 * P, 0.225 * P), hand_f=(-0.19 * P, 0.235 * P),
                   blink=blink_at(t, 0.6), smile=0.5, brow=0.1,
                   look=0.0)
    else:
        x = 760
        sad = smoothstep(walk_end, walk_end + 0.9, t)
        shock = smoothstep(6.0, 6.5, t)
        pose = std(P, torso=lerp(0.04, -0.02, sad) - 0.05 * shock,
                   head=lerp(0.0, -0.03, sad) - 0.05 * shock,
                   hand_n=(lerp(0.175, 0.115, sad) * P, 0.225 * P),
                   hand_f=(-0.19 * P, 0.235 * P),
                   blink=blink_at(t, 0.6), mouth=mouth_for(t, 0.2, dur - 0.6),
                   smile=lerp(0.5, -0.15, sad) + 0.1 * shock,
                   brow=lerp(0.1, -0.35, sad) + 0.5 * shock)
    world.char("student", pose, 1.14, x, 1015)
    world.glow(900, 700, 620, (255, 240, 200), 18)

    # shield of reputation, top right
    cx, cy = 1470, 400
    rad = 165
    a = smoothstep(0.9, 1.9, t)
    if a > 0:
        hold = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(hold)
        d.polygon([(cx - rad, cy - rad), (cx, cy - rad - 66), (cx + rad, cy - rad),
                   (cx + rad * 0.84, cy + rad * 0.52), (cx, cy + rad + 76),
                   (cx - rad * 0.84, cy + rad * 0.52)],
                  fill=(230, 190, 100, 46), outline=(255, 216, 136, 225), width=6)
        crack = smoothstep(5.6, 6.4, t)
        if crack > 0:
            pts = [(cx - 14, cy - 180), (cx + 14, cy - 78), (cx - 26, cy - 8),
                   (cx + 22, cy + 62), (cx - 4, cy + 158)]
            n = max(2, int(len(pts) * crack))
            d.line(pts[:n], fill=(255, 252, 244, 255), width=11)
            if crack > 0.5:
                d.line([(cx - 26, cy - 8), (cx - 116, cy + 44)], fill=(255, 252, 244, 235), width=8)
                d.line([(cx + 14, cy - 78), (cx + 104, cy - 40)], fill=(255, 252, 244, 235), width=8)
        hold.putalpha(hold.split()[3].point(lambda v: int(v * a)))
        world.paste(hold, 0, 0)

    zoom = 1.0 + 0.06 * smoothstep(1.0, dur, t)
    frame = camera(world.img, zoom, 900, 540)
    frame = chapter_chip(frame, t)
    return fade(frame, smoothstep(0, 0.45, t) * (1 - smoothstep(dur - 0.55, dur, t)))


def shot_mentor(t, dur):
    """Mentor advises the young man; both listen and nod."""
    world = World(bg.get("room"))
    Pm = CHARACTERS["mentor"].height
    Ps = CHARACTERS["student"].height

    gest = smoothstep(0.7, 2.0, t)
    beat = math.sin(t * 3.2) * 0.012 * Pm
    mpose = std(Pm, torso=0.02 + 0.012 * math.sin(t * 1.5),
                head=0.03 * math.sin(t * 1.1) - 0.03 * gest,
                hand_n=(lerp(0.175, 0.335, gest) * Pm, lerp(0.215, 0.005, gest) * Pm + beat * gest),
                hand_f=(-0.195 * Pm, 0.235 * Pm),
                blink=blink_at(t, 1.4), mouth=mouth_for(t, 0.15, dur - 0.7),
                smile=0.72, brow=0.25 + 0.1 * gest)
    world.char("mentor", mpose, 1.06, 600, 1030)

    nod = math.sin(t * 2.2)
    talk_beat = smoothstep(4.2, 5.0, t) * (1 - smoothstep(7.2, 8.0, t))
    spose = std(Ps, torso=0.02 + 0.02 * talk_beat * math.sin(t * 4.4),
                head=-0.05 + 0.035 * nod - 0.04 * talk_beat,
                hand_n=(lerp(0.16, 0.235, talk_beat) * Ps, lerp(0.235, 0.12, talk_beat) * Ps
                        + 0.01 * Ps * math.sin(t * 6.0)),
                hand_f=(-0.195 * Ps, 0.245 * Ps),
                blink=blink_at(t, 0.5), mouth=mouth_for(t, 4.3, 7.4, seed=2.1),
                smile=0.62 + 0.1 * talk_beat, brow=0.12 + 0.2 * talk_beat)
    world.char("student", spose, 1.00, 1320, 1030)
    world.glow(900, 700, 640, (255, 200, 140), 26)

    zoom = 1.0 + 0.06 * smoothstep(1.0, dur, t)
    frame = camera(world.img, zoom, lerp(880, 940, smoothstep(0, dur, t)), 540)
    frame = chapter_chip(frame, t)
    return fade(frame, smoothstep(0, 0.45, t) * (1 - smoothstep(dur - 0.55, dur, t)))


def shot_close(t, dur):
    """Final beat: the law, stated plainly."""
    world = World(bg.get("title"))
    P = CHARACTERS["king"].height
    k = smoothstep(0, 1.3, t)
    pose = std(P, torso=-0.02, head=-0.03,
               hand_n=(lerp(0.175, 0.255, k) * P, lerp(0.215, 0.02, k) * P
                       + 0.008 * P * math.sin(t * 2.6) * k),
               hand_f=(-0.205 * P, 0.245 * P),
               blink=blink_at(t, 1.0), mouth=mouth_for(t, 0.15, dur - 1.0),
               smile=0.78, brow=0.32)
    world.char("king", pose, 1.10, 640, 1010)
    world.glow(660, 640, 560, (255, 196, 128), 26)

    frame = camera(world.img, 1.0 + 0.08 * smoothstep(0, dur, t), 900, 540)
    frame = overlay_text(frame, ["সুনাম রক্ষা করুন —"], 1010, 380, 82,
                         color=(255, 231, 182), font=F_TITLE(82), alpha=smoothstep(0.4, 1.4, t))
    frame = overlay_text(frame, ["প্রাণ দিয়ে।"], 1010, 500, 126,
                         color=(255, 172, 100), font=F_TITLE(126), alpha=smoothstep(1.1, 2.2, t))
    frame = overlay_text(frame, ["রবার্ট গ্রিন · ৪৮টি ক্ষমতার সূত্র"], 1014, 690, 40,
                         color=(204, 212, 234), alpha=smoothstep(2.0, 3.0, t) * 0.9)
    return fade(frame, smoothstep(0, 0.45, t) * (1 - smoothstep(dur - 0.8, dur, t)))


SHOTS = [shot_intro, shot_king, shot_boss, shot_student, shot_mentor, shot_close]


# ------------------------------------------------------------------ timeline
def build_timeline():
    shots, t = [], 0.0
    for i, (path, pad) in enumerate(AUDIO):
        d = dur_of(path) + pad
        shots.append({"index": i, "start": t, "dur": d, "audio": path})
        t += d
    return shots


def render_frame(t_global, timeline):
    shot = timeline[-1]
    for s in timeline:
        if s["start"] <= t_global < s["start"] + s["dur"]:
            shot = s
            break
    return SHOTS[shot["index"]](t_global - shot["start"], shot["dur"])


def main():
    timeline = build_timeline()
    total = sum(s["dur"] for s in timeline)
    print(f"total {total:.2f}s / {int(round(total * FPS))} frames", flush=True)

    os.makedirs("build", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    # Build the soundtrack sample-accurately: each narration clip followed by
    # exactly enough silence to fill its shot. The concat demuxer's "duration"
    # directive does NOT pad, which silently slid every shot earlier.
    SR = 44100
    parts = []
    for s in timeline:
        dec = subprocess.run([FF, "-v", "error", "-i", s["audio"], "-f", "s16le",
                              "-ac", "2", "-ar", str(SR), "-"],
                             capture_output=True, check=True)
        clip = np.frombuffer(dec.stdout, dtype=np.int16)
        need = int(round(s["dur"] * SR)) * 2
        if clip.size > need:
            clip = clip[:need]
        parts.append(clip)
        parts.append(np.zeros(need - clip.size, dtype=np.int16))
    pcm = np.concatenate(parts)
    mix = "build/voice.wav"
    subprocess.run([FF, "-y", "-v", "error", "-f", "s16le", "-ar", str(SR),
                    "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", mix],
                   input=pcm.tobytes(), check=True)
    print(f"audio {pcm.size / 2 / SR:.2f}s -> {mix}", flush=True)

    out = "output/law5_bangla_2d_animation.mp4"
    cmd = [FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", mix,
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    n = int(round(total * FPS))
    for fi in range(n):
        frame = render_frame(fi / FPS, timeline)
        proc.stdin.write(np.asarray(frame.convert("RGB"), dtype=np.uint8).tobytes())
        if fi % 60 == 0:
            print(f"  {fi}/{n}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("done ->", out)


if __name__ == "__main__":
    main()
