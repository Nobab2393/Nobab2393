#!/usr/bin/env python3
"""ANGAAR AUR BAADAL — a 3D-anime style creature short in Hindi, 1080x1920.

    python3 film.py --still 12.0     one frame at t=12s
    python3 film.py --sheet          cast sheet
    python3 film.py                  full render + mux (needs audio/s1..s7.mp3)

Every frame is a pure function of t. The 3D is a software cel renderer (cel3d.py); the
painted sky, the FX and the type are 2D. Hindi type is shaped with harfbuzz (deva.py) because
this box has no libraqm.
"""
import math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import cel3d as C
import bg
import cast
import deva
from cel3d import Cam, place, render_model, T, S, R

W, H = 1080, 1920
SS = 1.7                                   # supersample factor for the 3D pass
FPS = 24
TTF = "/usr/local/lib/python3.11/dist-packages/matplotlib/mpl-data/fonts/ttf/"
F_INK = (12, 10, 13)
CREAM = (243, 238, 224)
EMBER_TXT = (247, 178, 92)
SLATE_TXT = (150, 176, 220)

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG = "ffmpeg"

AUD = ["audio/s%d.mp3" % i for i in range(1, 8)]


def probe(path):
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", err)
    if not m:
        return 10.0
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


COLD, GAP, TAIL = 1.30, 0.45, 6.20
if all(os.path.exists(p) for p in AUD):
    DUR = [probe(p) for p in AUD]
else:
    DUR = [9.5] * 7
NAR = [COLD]
for d in DUR[:-1]:
    NAR.append(round(NAR[-1] + d + GAP, 3))
END_AT = round(NAR[-1] + DUR[-1] + 0.6, 3)
TOTAL = round(END_AT + TAIL, 3)
BOUNDS = [0.0] + [round(n - 0.36, 3) for n in NAR[1:]] + [round(END_AT - 0.30, 3)]
NF = int(round(TOTAL * FPS))


# ---------------------------------------------------------------- helpers
def eio(k):
    k = min(1.0, max(0.0, k))
    return k * k * (3 - 2 * k)


def eout(k, p=3):
    k = min(1.0, max(0.0, k))
    return 1 - (1 - k) ** p


def seg(a, b, x):
    if b <= a:
        return 1.0 if x >= b else 0.0
    return min(1.0, max(0.0, (x - a) / (b - a)))


def lerp(a, b, k):
    return a + (b - a) * k


def vlerp(a, b, k):
    return tuple(lerp(a[i], b[i], k) for i in range(len(a)))


def shake(t, amp, seed=1.0):
    return (amp * math.sin(t * 47.3 + seed), amp * math.sin(t * 39.1 + seed * 2.3))


def compose_3d(img, cams, models, glow_models=()):
    """Render each model into its own supersampled tile and composite with outlines."""
    for model, cam in zip(models, cams):
        is_glow = model in glow_models if isinstance(glow_models, (list, tuple)) else False
        tile, pos = C.render_model_tiled(model, cam, ss=SS, outline=F_INK, glow=is_glow, outline_px=7)
        img.alpha_composite(tile, pos)


def ground_y(cam, z=0.40):
    """Where world y=0 projects to — the painted ground must meet the feet."""
    p = cam.project(cam.to_view(np.array([0.0, 0.0, z])))[0]
    return int(min(H - 1, max(10, p[1])))


def stage(img, cam, z=0.40, col=(26, 24, 31), name=None):
    """Paint the ground plane at the projected world line, with a falloff.

    A flat black band reads as a void (dark shoes vanish into it); a gradient
    from a lifted horizon to near-black at the bottom reads as ground.
    """
    gy = ground_y(cam, z)
    if name is not None and name in _FIT:
        gy = int(min(H - 4, max(10, gy + _FIT[name][3])))
    bg.ground(img, gy, col)
    n = H - gy
    if n > 8:
        arr = np.asarray(img).astype(np.float32)
        a = np.linspace(0.0, 0.80, n, dtype=np.float32)[:, None, None]
        deep = np.array([7, 7, 10], np.float32)[None, None, :]
        arr[gy:gy + n, :, :3] = arr[gy:gy + n, :, :3] * (1 - a) + deep * a
        img.paste(Image.fromarray(arr.clip(0, 255).astype(np.uint8)))


def cam_for(eye, target, fov, t=None, drift=0.0):
    c = Cam(eye=eye, target=target, fov=fov, w=W, h=H)
    c._fov = fov
    return c


def _bbox(models, cam):
    """Unclamped screen bbox of every point of every model."""
    xs, ys = [], []
    for m in models:
        for part in m.parts:
            v, _ = C.mesh(part.kind, part.subdiv)
            hom = np.concatenate([v, np.ones((len(v), 1))], 1) @ part.m.T
            uv, _z = cam.project(cam.to_view(hom[:, :3]))
            xs.append(uv[:, 0])
            ys.append(uv[:, 1])
    x = np.concatenate(xs)
    y = np.concatenate(ys)
    return float(x.min()), float(x.max()), float(y.min()), float(y.max())


def _solve_fit(models, eye, target, fov, top, bottom, side):
    """Find the (pan, zoom-out) that puts the models inside the safe area."""
    e = np.array(eye, float)
    g = np.array(target, float)
    dx = dy = 0.0
    s = 1.0
    for _ in range(6):
        c = cam_for(tuple(e), tuple(g), fov)
        x0, x1, y0, y1 = _bbox(models, c)
        need = max((x1 - x0) / (W - 2 * side), (y1 - y0) / (bottom - top))
        if need > s:
            s = min(2.3, need * 1.05)
            e = g + (np.array(eye, float) - g) * s + np.array([dx, dy, 0.0])
            continue
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        dist = float(np.linalg.norm(e - g))
        upp = 2 * math.tan(math.radians(fov) / 2) * dist / H
        ox = (cx - W / 2.0) * upp
        oy = -(cy - (top + bottom) / 2.0) * upp
        dx = float(np.clip(dx + ox, -1.5, 1.5))
        dy = float(np.clip(dy + oy, -1.5, 1.5))
        g = np.array(target, float) + np.array([dx, dy, 0.0])
        e = g + (np.array(eye, float) - np.array(target, float)) * s
        if abs(ox) < 3 and abs(oy) < 3:
            break
    return dx, dy, s


_FIT = {}
SCENE_NAME = None


def scene_cam(name, build, t_hero, eye, target, fov, top=230, bottom=1540, side=80):
    """One constant framing correction per scene, solved on a hero pose.

    Keeping it constant (instead of re-fitting every frame) stops the camera from
    breathing while characters move, and keeps the render deterministic.
    """
    if name not in _FIT:
        models, _glow = build(t_hero)
        dx, dy, s = _solve_fit(models, eye, target, fov, top, bottom, side)
        off = np.array([dx, dy, 0.0])
        g0 = np.array(target, float) + off
        c0 = cam_for(tuple(g0 + (np.array(eye, float) - np.array(target, float)) * s), tuple(g0), fov)
        feet = _bbox(models, c0)[3]
        _FIT[name] = (dx, dy, s, feet - ground_y(c0, 0.40))
    dx, dy, s, _dgy = _FIT[name]
    off = np.array([dx, dy, 0.0])
    g = np.array(target, float) + off
    e = g + (np.array(eye, float) - np.array(target, float)) * s
    return cam_for(tuple(e), tuple(g), fov)


# ---------------------------------------------------------------- scenes
def s1(img, lt, dur):
    """The ember on the ridge. Title."""
    global SCENE_NAME
    SCENE_NAME = "s1"
    p = eio(seg(0, dur, lt))
    bg.sky(img, lt, 0.0)
    bg.stars(img, 130, 7, lt, fade=1.0)
    bg.moon(img, 902 - 22 * p, 264, 84, halo=1.0)
    bg.ridge(img, 1320, 240, seed=5, col=(20, 19, 28))
    bg.ridge(img, 1430, 160, seed=11, col=(15, 14, 19))

    def build(t):
        rock = place(cast.rock(0, 0, 0.85), T(-0.55, 0.06, 0.0))
        pup = place(cast.angaar(t=t, bounce=-0.14, flame=0.55, ear=0.7, tail=t),
                    T(-0.55, 0.30, 0.15) @ S(0.92))
        return [rock, pup], [pup]

    models, glow = build(lt)
    cam = scene_cam("s1", build, dur * 0.5, (2.05, 1.05 + 0.10 * p, 8.6 - 1.3 * p),
                    (0.0, 1.16, 0.0), 30, top=600, bottom=1740)
    stage(img, cam, 0.40, (26, 24, 31), name=SCENE_NAME)
    compose_3d(img, [cam] * len(models), models, glow_models=glow)

    bg.sparks(img, lt, 430, 1080, n=16, spread=180, rise=520, col=(255, 168, 92))
    bg.vignette(img, 110)

    if lt > 1.1:
        k = eout(seg(1.1, 2.0, lt))
        deva.draw_text(img, (540, 360), "अंगार और बादल", int(74 + 6 * k), 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=16)
        d = ImageDraw.Draw(img)
        d.text((540, 432), "A N G A A R   A U R   B A A D A L", font=ImageFont.truetype(TTF + "DejaVuSans.ttf", 27),
               fill=(168, 160, 150, int(255 * k)), anchor="mm")
    if lt > 2.6:
        k = eout(seg(2.6, 3.4, lt))
        deva.draw_text(img, (540, 512), "एक छोटी सी आग, एक बड़ा तूफ़ान", 38, 500,
                       (210, 200, 190) if k > 0.3 else CREAM, shadow=(0, 0, 0), shadow_blur=12)


def s2(img, lt, dur):
    """Ravi finds him."""
    global SCENE_NAME
    SCENE_NAME = "s2"
    bg.sky(img, lt, 0.05)
    bg.stars(img, 120, 7, lt)
    bg.moon(img, 810, 320, 84)
    bg.ridge(img, 1320, 240, seed=5, col=(20, 19, 28))
    bg.ridge(img, 1430, 160, seed=11, col=(15, 14, 19))

    walk = eio(seg(0.0, 3.2, lt))

    def build(t):
        w = eio(seg(0.0, 3.2, t))
        rock = place(cast.rock(0, 0, 0.8), T(0.85, 0.05, -0.2))
        pup = place(cast.angaar(t=t, bounce=-0.10, ear=0.3 + 0.6 * eio(seg(2.6, 3.2, t)),
                               flame=0.6 + 0.25 * eio(seg(3.4, 4.2, t)),
                               blink=1.0 - eio(seg(2.5, 2.75, t)), tail=t),
                    T(0.85, 0.30, -0.05) @ S(0.92))
        rav = place(cast.ravi(t=t, walk=t if w < 0.98 else 0, arm=eio(seg(3.3, 3.9, t)) * 0.85,
                              look=0.7),
                    T(lerp(-2.7, -1.15, w), 0, 0.45) @ S(1.02))
        return [rock, pup, rav], [pup]

    models, glow = build(lt)
    cam = scene_cam("s2", build, 3.9, (1.10 + 0.30 * walk, 0.95, 8.4), (0.10, 1.02, 0.0), 30)
    stage(img, cam, 0.40, (26, 24, 31), name=SCENE_NAME)
    compose_3d(img, [cam] * len(models), models, glow_models=glow)

    sneeze = seg(3.9, 4.15, lt) * (1 - seg(4.5, 4.9, lt))
    if sneeze > 0:
        bg.sparks(img, lt, 470, 900, n=30, spread=340, rise=380)
        bg.impact(img, lt, 0.22 * sneeze, cx=470, cy=900)
    bg.vignette(img, 105)
    if lt > 4.6:
        deva.draw_text(img, (540, 1660), "रवि को मिला एक छोटा सा अंगार", 40, 600, CREAM,
                       shadow=(0, 0, 0), shadow_blur=14)


def s3(img, lt, dur):
    """The storm takes the flame."""
    global SCENE_NAME
    SCENE_NAME = "s3"
    storm = eio(seg(0.0, 2.2, lt))
    bg.sky(img, lt, 0.55 * storm)
    bg.stars(img, 90, 7, lt, fade=1 - 0.7 * storm)
    bg.moon(img, 196, 306, 86, halo=1 - 0.5 * storm)
    bg.ridge(img, 1320, 240, seed=5, col=(20, 19, 28))
    bg.ridge(img, 1430, 160, seed=11, col=(15, 14, 19))
    bg.wind(img, lt, 0.5 + 0.5 * storm)

    k = eio(seg(0.6, 3.6, lt))

    def build(t):
        kk = eio(seg(0.6, 3.6, t))
        hx = lerp(3.0, -0.35, kk)
        hy = lerp(2.90, 1.30, kk) - 0.45 * math.sin(math.pi * kk)
        flame_out = 1.0 - eio(seg(3.4, 3.8, t))
        rock = place(cast.rock(0, 0, 0.75), T(-0.75, 0.05, -0.1))
        pup = place(cast.angaar(t=t, bounce=-0.05, ear=0.9, flame=0.8 * flame_out,
                                look=-0.6, tail=t),
                    T(-0.75, 0.30, 0.0) @ S(0.9))
        haw = place(cast.baadal(t=t, flap=0.5 + 0.5 * math.sin(t * 9.0), dive=0.55 * kk, y=0.0),
                    T(hx, hy, 0.15) @ S(0.95))
        return [rock, pup, haw], [pup]

    models, glow = build(lt)
    # anchor the framing on the pup; the hawk flies in from off-frame by design
    anchors = models[:2]
    cam = scene_cam("s3", lambda t: (build(t)[0][:2], None), 2.6,
                    (0.35, 1.45 + 0.30 * storm, 8.6 - 0.6 * k), (0.0, 1.50, 0.0), 32,
                    top=260, bottom=1500)
    stage(img, cam, 0.40, (26, 24, 31), name=SCENE_NAME)
    compose_3d(img, [cam] * len(models), models, glow_models=glow)

    if lt > 3.6:
        bg.sparks(img, lt, 500, 780, n=10, spread=260, rise=420)
    bg.vignette(img, 120)
    if lt > 3.9:
        deva.draw_text(img, (540, 1660), "आसमान से उतरा बादल — और आग ले गया", 38, 600, CREAM,
                       shadow=(0, 0, 0), shadow_blur=14)


def s4(img, lt, dur):
    """The clash."""
    global SCENE_NAME
    SCENE_NAME = "s4"
    bg.sky(img, lt, 0.75)
    bg.stars(img, 70, 7, lt, fade=0.35)
    bg.ridge(img, 1320, 240, seed=5, col=(18, 17, 25))
    bg.ridge(img, 1430, 160, seed=11, col=(14, 13, 18))
    bg.wind(img, lt, 1.0)

    air = math.sin(math.pi * seg(0.5, 2.4, lt))
    hit = seg(1.9, 2.35, lt)
    sh = shake(lt, 26 * (1 - hit) * air)

    def build(t):
        a = math.sin(math.pi * seg(0.5, 2.4, t))
        h = seg(1.9, 2.35, t)
        pup = place(cast.angaar(t=t, bounce=0.10 + 0.95 * a, lean=0.9 * a, ear=1.0,
                               flame=1.0 + 0.5 * a, look=0.8, tail=t),
                    T(-0.52, 0.10 * a, 0.35) @ S(0.95))
        haw = place(cast.baadal(t=t, flap=0.85, dive=0.35 + 0.45 * h, bank=-20 * (1 - h)),
                    T(0.92 - 1.15 * h, 1.30 + 0.18 * a - 0.42 * h, 0.1) @ S(1.0))
        return [pup, haw], [pup]

    models, glow = build(lt)
    cam = scene_cam("s4", build, 2.65, (0.2 + sh[0] / 300, 1.15 + air * 0.30 + sh[1] / 300,
                                       8.0 - 0.5 * air), (0.0, 1.34 + air * 0.30, 0.0), 33,
                    top=300, bottom=1470)
    stage(img, cam, 0.40, (24, 22, 29), name=SCENE_NAME)
    rav = place(cast.ravi(t=lt, arm=0.7, look=0.6), T(-3.30, 0, 0.15) @ S(0.92))
    compose_3d(img, [cam] * len(models) + [cam], models + [rav], glow_models=glow)

    if air > 0.35:
        bg.speed_lines(img, lt, n=30, cx=540, cy=950, inner=230, strength=air)
    if 1.85 < lt < 2.9:
        k = math.sin(math.pi * seg(1.85, 2.55, lt))
        bg.impact(img, lt, k, cx=560, cy=880)
        bg.sparks(img, lt, 560, 880, n=34, spread=520, rise=520)
    bg.vignette(img, 120)
    if lt > 2.7:
        deva.draw_text(img, (540, 1660), "आग और तूफ़ान — आमने-सामने", 42, 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=14)


def s5(img, lt, dur):
    """The choice: he lights the way instead of burning."""
    global SCENE_NAME
    SCENE_NAME = "s5"
    bg.sky(img, lt, 0.45)
    bg.stars(img, 80, 7, lt, fade=0.5)
    bg.moon(img, 168, 318, 68, halo=0.7)
    bg.ridge(img, 1330, 250, seed=5, col=(19, 18, 26))
    bg.ridge(img, 1440, 150, seed=11, col=(14, 13, 18))
    calm = eio(seg(0.4, 1.8, lt))

    def build(t):
        haw = place(cast.baadal(t=t, flap=0.22, dive=0.10, y=-0.48, bank=14),
                    T(0.62, 0.06, -0.10) @ S(0.95))
        pup = place(cast.angaar(t=t, bounce=0.02, ear=0.55, flame=0.85, look=0.5, tail=t),
                    T(-0.55, 0.08, 0.15) @ S(0.92))
        return [haw, pup], [pup]

    models, glow = build(lt)
    cam = scene_cam("s5", build, 2.2, (1.15, 0.95, 8.9 - 0.5 * calm), (0.05, 1.00, 0.0), 30)
    stage(img, cam, 0.40, (24, 22, 29), name=SCENE_NAME)
    rav = place(cast.ravi(t=lt, arm=0.35, look=0.3), T(-2.15, 0, -0.15) @ S(0.9))
    compose_3d(img, [cam] * len(models) + [cam], models + [rav], glow_models=glow)

    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(320, 1560), (680, 1560), (880, 1920), (160, 1920)], fill=(255, 170, 90, 34))
    lay = lay.filter(ImageFilter.GaussianBlur(64))
    img.alpha_composite(lay)
    bg.sparks(img, lt, 380, 900, n=12, spread=200, rise=380)
    bg.vignette(img, 110)
    if lt > 2.0:
        deva.draw_text(img, (540, 1650), "अंगार ने जलाया नहीं — रास्ता दिखाया", 40, 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=14)


def s6(img, lt, dur):
    """Together."""
    global SCENE_NAME
    SCENE_NAME = "s6"
    bg.sky(img, lt, 0.12)
    bg.stars(img, 140, 3, lt)
    bg.moon(img, 860, 300, 96)
    bg.ridge(img, 1310, 235, seed=5, col=(20, 19, 28))
    bg.ridge(img, 1430, 150, seed=11, col=(15, 14, 19))
    k = eio(seg(0.0, dur, lt))

    def build(t):
        rock = place(cast.rock(0, 0, 0.9), T(-0.92, 0.05, -0.6))
        pup = place(cast.angaar(t=t, bounce=-0.02, ear=0.5, flame=0.9, tail=t),
                    T(-0.34, 0.14, 0.25) @ S(0.9))
        rav = place(cast.ravi(t=t, arm=0.2), T(0.20, 0, 0.30) @ S(0.95))
        haw = place(cast.baadal(t=t, flap=0.0, y=-0.64, dive=0.0), T(0.66, 0.10, -0.15) @ S(0.86))
        return [rock, pup, rav, haw], [pup]

    models, glow = build(lt)
    cam = scene_cam("s6", build, dur * 0.6, (0.10, 0.84, 6.6 - 0.7 * k), (0.00, 0.90, 0.0), 30,
                    top=560, bottom=1640, side=30)
    stage(img, cam, 0.40, (26, 24, 31), name=SCENE_NAME)
    compose_3d(img, [cam] * len(models), models, glow_models=glow)

    bg.sparks(img, lt, 520, 780, n=14, spread=520, rise=520)
    bg.vignette(img, 110)
    if lt > 1.4:
        deva.draw_text(img, (540, 1640), "अब वो तीनों साथ हैं", 42, 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=14)


def s7(img, lt, dur):
    """CTA card — the part that has to work."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(11, 11, 16))
    # ember glow behind the type
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(lay)
    gd.ellipse([140, 780, 940, 1300], fill=(255, 146, 74, 40))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(110)))
    bg.stars(img, 60, 21, lt, fade=0.5)

    k1 = eout(seg(0.15, 0.8, lt))
    k2 = eout(seg(0.55, 1.2, lt))
    k3 = eout(seg(0.95, 1.6, lt))
    k4 = eout(seg(1.4, 2.0, lt))

    if k1 > 0.05:
        deva.draw_text(img, (540, 560), "कहानी पसंद आई?", int(58 * k1 + 8), 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=18)
    if k2 > 0.05:
        deva.draw_text(img, (540, 690), "अगली कड़ी में अंगार को मिलेगा नया दोस्त", 36, 500,
                       (206, 198, 188), shadow=(0, 0, 0), shadow_blur=12)
    if k3 > 0.05:
        # comment bait first (cheapest engagement), then the follow pill
        deva.draw_text(img, (540, 900), "कमेंट करो: ANGAAR", 44, 700, EMBER_TXT,
                       shadow=(0, 0, 0), shadow_blur=14)
        pw = 560 * k3
        d.rounded_rectangle([540 - pw / 2, 1010, 540 + pw / 2, 1140], 34, fill=(247, 178, 92))
        if k3 > 0.85:
            deva.draw_text(img, (540, 1072), "फॉलो करें", 46, 700, (18, 14, 12))
    if k4 > 0.05:
        deva.draw_text(img, (540, 1230), "हर शुक्रवार नई कड़ी", 34, 500, (190, 184, 176))
        d.line([(340, 1290), (340 + 400 * k4, 1290)], fill=(247, 178, 92, 200), width=3)

    # Angaar peeking in from the bottom corner, flame lit
    qt = round(lt * 4) / 4.0
    global _CTA_TILE, _CTA_QT
    if _CTA_TILE is None or _CTA_QT != qt:
        cam = cam_for((0.55, 0.85, 3.1), (0.0, 0.62, 0.0), 30)
        pup = place(cast.angaar(t=qt, ear=0.75, flame=1.0, look=0.4, tail=qt), T(0, 0, 0) @ S(1.0))
        tile, _ = C.render_model_tiled(pup, cam, ss=SS, outline=F_INK, glow=True, outline_px=7)
        scale = 286 / max(1, tile.width)
        tile = tile.resize((int(tile.width * scale), int(tile.height * scale)), Image.LANCZOS)
        _CTA_TILE, _CTA_QT = tile, qt
    img.alpha_composite(_CTA_TILE, (int(W / 2 - _CTA_TILE.width / 2),
                                    min(1300, 1836 - _CTA_TILE.height)))


_CTA_TILE = None
_CTA_QT = -1.0

SCENES = [s1, s2, s3, s4, s5, s6, s7]
GROUNDS = [(12, 13, 22)] * 6 + [(11, 11, 16)]


def scene_index(t):
    for i in range(len(BOUNDS) - 1):
        if t < BOUNDS[i + 1]:
            return i
    return len(BOUNDS) - 2


def draw(t):
    i = min(scene_index(t), len(SCENES) - 1)
    img = Image.new("RGBA", (W, H), GROUNDS[i] + (255,))
    lt = t - BOUNDS[i]
    dur = max(0.5, BOUNDS[i + 1] - BOUNDS[i])
    SCENES[i](img, lt, dur)
    return bg.letterbox_grade(img)


def main():
    os.makedirs("frames", exist_ok=True)
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1])
        out = draw(t)
        path = "frames/still-%05.2f.png" % t
        out.save(path)
        print("still", path)
        return
    if "--sheet" in sys.argv:
        os.system("python3 sheet.py")
        return

    print("timeline", NAR, "end", END_AT, "total", TOTAL, "frames", NF, flush=True)

    if "--seg" in sys.argv:
        j = sys.argv.index("--seg")
        a, b, seg = int(sys.argv[j + 1]), int(sys.argv[j + 2]), sys.argv[j + 3]
        cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-pix_fmt", "yuv420p", seg]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(a, b):
            proc.stdin.write(draw(i / FPS).tobytes())
            if (i - a) % 60 == 0:
                print("  seg %d/%d" % (i - a, b - a), flush=True)
        proc.stdin.close()
        proc.wait()
        print("segdone", seg, os.path.getsize(seg), flush=True)
        return

    if "--join" in sys.argv:
        segs = sys.argv[sys.argv.index("--join") + 1:]
        with open("segs.txt", "w") as f:
            for sp in segs:
                f.write("file '%s'\n" % os.path.abspath(sp))
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", "segs.txt", "-i", "audio/mix.wav", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                        "angaar-baadal-1080x1920.mp4"], check=True)
        print("joined -> angaar-baadal-1080x1920.mp4",
              os.path.getsize("angaar-baadal-1080x1920.mp4"))
        return
    # audio
    inputs, filt, labels = [], [], []
    for k, (p, start) in enumerate(zip(AUD, NAR)):
        inputs += ["-i", p]
        ms = int(round(start * 1000))
        filt.append("[%d:a]adelay=%d|%d[a%d]" % (k, ms, ms, k))
        labels.append("[a%d]" % k)
    fc = ";".join(filt) + ";" + "".join(labels) + "amix=inputs=7:normalize=0,apad[a]"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error"] + inputs +
                   ["-filter_complex", fc, "-map", "[a]", "-ar", "44100", "-ac", "2",
                    "-t", "%.3f" % TOTAL, "audio/mix.wav"], check=True)

    out = "angaar-baadal-1080x1920.mp4"
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-i", "audio/mix.wav",
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(NF):
        fr = draw(i / FPS)
        proc.stdin.write(fr.tobytes())
        if i % 150 == 0:
            fr.save("frames/f%04d.png" % i)
        if i % 300 == 0:
            print("  %d/%d" % (i, NF), flush=True)
    proc.stdin.close()
    proc.wait()
    print("done", out, os.path.getsize(out))


if __name__ == "__main__":
    main()
