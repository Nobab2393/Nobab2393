#!/usr/bin/env python3
"""অন্ধকার পাঠ ০৩ · দুপুর (NOON) — a 3D-anime dark lesson in Bangla, told in daylight.

    python3 film.py --still 12.0        one frame
    python3 film.py --mix               build audio/mix.wav
    python3 film.py --seg A B out.mp4   render a frame range to a silent segment
    python3 film.py --join s1.mp4 ...   concat segments + mux the voice-over
    python3 film.py                     full render

The series is called DARK LESSON, so ep-03 happens at noon. The darkness is not in the light —
it is in the ten people standing in it. One graphic carries the film: everybody's shadow is
separate until somebody steps forward, and then two shadows become one.
"""
import math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import cel3d as C
import bg3
import cast3
import deva
from cel3d import Cam, place, T, S, R

W, H = 1080, 1920
SS = 1.15
FPS = 24
TTF = "/usr/local/lib/python3.11/dist-packages/matplotlib/mpl-data/fonts/ttf/"

# the daylight key: high, from the right and slightly in front, warm-white rim
C.L_KEY = C._normalize(np.array([0.46, 0.80, 0.34]))
C.RIM_COL = np.array([1.00, 0.97, 0.86])

INK = (26, 24, 22)
CREAM = (252, 246, 232)
TEAL = (18, 108, 118)
RUST = (172, 62, 36)
PAPER = (250, 244, 230)

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG = "ffmpeg"

VO_DIR = os.environ.get("VO_DIR", "audio")      # VO_DIR=audio-v15 to re-voice
MIX = os.path.join(VO_DIR, "mix.wav")
OUT = os.environ.get("OUT", "dark-lesson-03-1080x1920.mp4")
AUD = [os.path.join(VO_DIR, "v%d.mp3" % i) for i in range(1, 8)]


def probe(path):
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", err)
    if not m:
        return 7.0
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


LEAD, GAP, TAIL = 0.90, 0.45, 3.90
if all(os.path.exists(p) for p in AUD):
    DUR = [probe(p) for p in AUD]
else:
    DUR = [7.0] * 7
NAR = [LEAD]
for d in DUR[:-1]:
    NAR.append(round(NAR[-1] + d + GAP, 3))
END_AT = round(NAR[-1] + DUR[-1] + 0.60, 3)
TOTAL = round(END_AT + TAIL, 3)
BOUNDS = [0.0] + [round(n - 0.32, 3) for n in NAR[1:]] + [round(END_AT - 0.26, 3)]
NF = int(round(TOTAL * FPS))


# ---------------------------------------------------------------- helpers
def eio(k):
    k = min(1.0, max(0.0, k))
    return k * k * (3 - 2 * k)


def eout(k, p=3):
    k = min(1.0, max(0.0, k))
    return 1 - (1 - k) ** p


def segd(a, b, x):
    if b <= a:
        return 1.0 if x >= b else 0.0
    return min(1.0, max(0.0, (x - a) / (b - a)))


def lerp(a, b, k):
    return a + (b - a) * k


def cam_at(eye, target, fov):
    c = Cam(eye=eye, target=target, fov=fov, w=W, h=H)
    c._fov = fov
    return c


def compose_3d(img, pairs):
    for model, cam in pairs:
        tile, pos = C.render_model_tiled(model, cam, ss=SS, outline=INK, outline_px=6)
        img.alpha_composite(tile, pos)


def cut(img, model, cam):
    """A character, rendered once and reused inside one frame (avoids double work)."""
    tile, pos = C.render_model_tiled(model, cam, ss=SS, outline=INK, outline_px=6)
    img.alpha_composite(tile, pos)


# bushes at the field edge, for scale. The treeline itself is the band on the horizon.
TREES = [(-6.4, -17.0, 1.5, 0, 11), (-5.0, -22.0, 1.9, 1, 12), (-8.2, -26.0, 2.2, 0, 13),
         (6.8, -19.0, 1.7, 1, 14), (8.6, -24.0, 2.0, 0, 15), (-9.4, -14.0, 1.2, 1, 16),
         (9.2, -13.0, 1.3, 0, 17)]


def field(img, cam, drift=0.0, sun=(0.72, 0.09), seed=3, near=0.92, heatk=0.0, t=0.0):
    bg3.sky(img, cam, sun=sun)
    bg3.far_ridge(img, cam, seed=5, drift=drift)
    bg3.treeline(img, cam, TREES, drift=drift)
    y0 = bg3.ground(img, cam, seed=seed)
    if heatk > 0.01:
        bg3.heat(img, t, y0, heatk)
    return y0


def shadow(img, cam, x, z, h=1.45, w=0.20, slope=0.52, alpha=104, blur=5):
    bg3.cast_shadow(img, cam, x, z, height=h, width=w, slope=slope, alpha=alpha, blur=blur)


def caption(img, y, text, size=40, col=INK, weight=700, halo=(255, 252, 240), blur=14):
    deva.draw_text(img, (540, y), text, size, weight, col, shadow=halo, shadow_blur=blur)


def kicker(img, k, y=286, col=INK):
    """The series mark, always in the same place, always the same size."""
    if k <= 0.02:
        return
    deva.draw_text(img, (540, y), "অন্ধকার পাঠ · ০৩", int(34 * k + 5), 700, col,
                   shadow=(255, 252, 240), shadow_blur=10)
    d = ImageDraw.Draw(img)
    d.line([(430, y + 34), (650, y + 34)], fill=(60, 56, 48, int(120 * k)), width=2)


# ---------------------------------------------------------------- the crowd
def crowd_ring(img, cam, t, people, drift=0.0, look_at=None):
    """Draw far-to-near; every one gets a shadow, because the shadows are the argument.
    If `look_at` is given, each body is turned toward it — a ring, not a row."""
    out = []
    for (x, z, tall, ph, turn, look, i) in sorted(people, key=lambda p: p[1]):
        m = cast3.crowd(i, t=t, tall=tall, phone=ph, turn=turn, look=look)
        yaw = 0.0
        if look_at is not None:
            dx, dz = look_at[0] - x, look_at[1] - z
            yaw = math.degrees(math.atan2(dx, dz))
        shadow(img, cam, x, z, h=1.55 * tall, w=0.34 * tall,
               slope=0.52, alpha=int(78 * max(0.3, 1.0 + z / 6.0)), blur=6)
        out.append((place(m, T(x, 0.0, z) @ R("y", yaw)), cam))
    return out


# ---------------------------------------------------------------- s1 · the street
def s1(img, lt, dur):
    """Noon. He walks in. Somebody is already standing in the way."""
    push = eio(segd(0, dur, lt))
    cx = lerp(-0.46, -0.06, eio(segd(0, dur * 0.9, lt)))
    cam = cam_at((cx, 1.48, 9.4 - 0.55 * push), (cx * 0.85 + 0.02, 1.00, 0.35), 32)
    field(img, cam, drift=-0.55 + 0.10 * push, t=lt, heatk=0.5)

    walkx = lerp(-1.38, -0.46, eout(segd(0.2, dur * 0.92, lt), 2))
    ayan_m, hands, hd = cast3.ayan(t=lt, walk=lt * 1.7, look=0.35, slump=0.25,
                                   bag=1.0, blink=1.0 - eout(segd(0.9, 1.4, lt)))
    shadow(img, cam, walkx, 0.55, h=1.44, slope=0.52)
    rafiq_m = cast3.rafiq(t=lt, look=-0.25, arm=0.05)
    shadow(img, cam, 0.56, 0.10, h=1.66, w=0.36, slope=0.52)

    crowd = [(2.15, -2.4, 1.02, 0.0, -0.5, -0.2, 0), (2.95, -3.6, 0.98, 0.0, -0.7, -0.1, 1),
             (-1.75, -3.4, 1.00, 0.0, 0.3, -0.1, 2), (1.10, -5.0, 1.05, 0.0, -0.4, -0.1, 3)]
    pairs = crowd_ring(img, cam, lt, crowd)
    pairs += [(place(ayan_m, T(walkx, 0.0, 0.55)), cam),
              (place(rafiq_m, T(0.56, 0.0, 0.10)), cam)]
    compose_3d(img, pairs)

    bg3.dust(img, lt, 70, seed=4, alpha=100, top=0.62)
    kicker(img, eout(segd(0.25, 1.0, lt)))
    if lt > 2.6:
        caption(img, 1620, "দুপুরের রোদে সব পরিষ্কার", 38)
    bg3.near_plane(img, 0.95)
    bg3.grade(img, tint=(255, 249, 238), sat=1.02)


# ---------------------------------------------------------------- s2 · the bag
def s2(img, lt, dur):
    """The bag goes down. The books go everywhere. He reaches and does not get there."""
    cam = cam_at((0.30, 1.46, 6.6), (0.02, 0.95, 0.30), 34)
    field(img, cam, drift=-0.35, t=lt, heatk=0.4, sun=(0.74, 0.08))

    grab = eio(segd(0.45, 1.05, lt))
    fly = eio(segd(1.10, 1.55, lt))
    land = eio(segd(1.55, 1.75, lt))
    reach = eio(segd(2.2, 3.3, lt))

    ayan_m, hands, hd = cast3.ayan(t=lt, walk=0.0, look=0.55, slump=0.35 + 0.3 * land,
                                   reach=reach, blink=0.0, head=6 * land)
    rafiq_m = cast3.rafiq(t=lt, look=-0.1, arm=lerp(0.16, 0.03, fly))
    shadow(img, cam, -0.62, 0.62, h=1.44, slope=0.50)
    shadow(img, cam, 0.58, 0.25, h=1.66, w=0.36, slope=0.50)

    pairs = [(place(ayan_m, T(-0.62, 0.0, 0.62)), cam), (place(rafiq_m, T(0.58, 0.0, 0.25)), cam)]
    compose_3d(img, pairs)

    # the bag: in his hand, then in the air, then on the ground with the books out
    if fly < 0.995:
        bx = lerp(-0.30, 0.36, grab) if fly <= 0.0 else lerp(0.36, 0.22, fly)
        by = lerp(0.72, 0.68, grab) if fly <= 0.0 else lerp(0.68, 0.09, fly)
        bz = lerp(0.52, 0.34, grab) if fly <= 0.0 else lerp(0.34, 0.32, fly)
        bagm = cast3.bag_flat(t=lt, spilled=0.0)
        cut(img, place(bagm, T(bx, by, bz) @ R("y", -26 * grab) @ R("z", 76 * fly)
                       @ S(lerp(0.62, 0.52, fly))), cam)
    if land > 0.02:
        cut(img, place(cast3.bag_flat(t=lt, spilled=1.0), T(0.22, 0.0, 0.32) @ S(0.9)), cam)
    if 1.45 < lt < 2.5:                                    # dust at the impact
        k = (lt - 1.45) / 1.05
        r = 1.0
        for i in range(9):
            ang = i * 0.7 + 0.4
            px = 540 + math.cos(ang) * (60 + 90 * k)
            py = 1500 + math.sin(ang) * (16 + 30 * k) - 40 * k
            rr = 26 + 40 * k
            bg3._soft(img, lambda d, s, px=px, py=py, rr=rr, k=k:
                      d.ellipse([(px - rr) * s, (py - rr * 0.5) * s,
                                 (px + rr) * s, (py + rr * 0.5) * s],
                                fill=(214, 198, 168, int(70 * (1 - k)))), 12)

    bg3.dust(img, lt, 60, seed=9, alpha=95)
    if lt > 2.9:
        caption(img, 1620, "ব্যাগটা মাটিতে পড়ল", 38)
    bg3.near_plane(img, 0.9)
    bg3.grade(img, tint=(255, 249, 238))


# ---------------------------------------------------------------- s3 · the ring
def s3(img, lt, dur):
    """Pull back. Ten people. Ten separate shadows. Nobody's shadow touches anybody's."""
    pull = eio(segd(0, dur, lt))
    cam = cam_at((0.12, 1.86 + 0.12 * pull, 6.6 + 0.5 * pull), (0.04, 0.86, 0.10), 34)
    field(img, cam, drift=-0.25, t=lt, sun=(0.78, 0.07), heatk=0.6)

    people = [(-2.10, -1.05, 1.00, 0.0, 0.0, 0.2, 0), (-1.30, -1.85, 1.03, 0.0, 0.0, 0.2, 1),
              (1.05, -1.15, 0.99, 1.0, 0.0, 0.1, 2), (1.85, -2.05, 1.05, 0.0, 0.0, 0.2, 3),
              (0.30, -2.55, 1.01, 0.0, 0.0, 0.1, 4), (-0.45, -3.10, 0.97, 1.0, 0.0, 0.1, 5),
              (2.55, -3.20, 1.02, 0.0, 0.0, 0.2, 1)]
    pairs = crowd_ring(img, cam, lt, people, look_at=(0.05, 0.20))
    ayan_m, hands, hd = cast3.ayan(t=lt, look=0.15, slump=1.0, crouch=0.72, blink=0.0, head=10)
    shadow(img, cam, 0.05, 0.20, h=1.05, w=0.26, slope=0.56, alpha=118)
    pairs.append((place(ayan_m, T(0.05, 0.0, 0.20)), cam))
    pairs.append((place(cast3.bag_flat(t=lt, spilled=1.0), T(0.42, 0.0, 0.10) @ S(0.9)), cam))
    compose_3d(img, pairs)

    bg3.dust(img, lt, 70, seed=11, alpha=90)
    if lt > 2.4:
        caption(img, 1620, "সবাই দেখছিল, কেউ এগোল না", 37)
    bg3.near_plane(img, 0.75)
    bg3.grade(img, tint=(255, 249, 238))


# ---------------------------------------------------------------- s4 · alone
def s4(img, lt, dur):
    """They leave. He picks his books up. The sun drops, and his own shadow comes at him."""
    push = eio(segd(0, dur, lt))
    cam = cam_at((0.18, 1.22, 4.9 - 0.35 * push), (0.0, 0.80, 0.30), 35)
    field(img, cam, drift=-0.20, t=lt, sun=(0.80, 0.11 + 0.05 * push), heatk=0.35)

    go = eout(segd(1.1, 5.2, lt), 1.7)
    down = eio(segd(0.8, 2.4, lt))
    rafiq_m = cast3.rafiq(t=lt, walk=lt * 1.5 * (1 - go * 0.4), look=-0.9, arm=0.0,
                          laugh=eout(segd(0.3, 0.9, lt)) * (1 - eout(segd(1.6, 2.4, lt))))
    ayan_m, hands, hd = cast3.ayan(t=lt, walk=0.0, look=0.2, slump=0.45 + 0.45 * down,
                                   crouch=0.80 * down, head=4 * down, blink=0.0,
                                   reach=0.55 * down)

    slope = lerp(0.52, 1.02, eio(segd(1.4, dur, lt)))
    shadow(img, cam, 2.05 + 2.6 * go, 0.20, h=1.66, w=0.36, slope=0.52,
           alpha=int(96 * (1 - go)))
    shadow(img, cam, -0.06, 0.34, h=1.35 - 0.28 * down, w=0.30, slope=slope,
           alpha=int(96 + 34 * down), blur=7)

    pairs = [(place(rafiq_m, T(2.6 + 2.1 * go, 0.0, 0.20)), cam),
             (place(ayan_m, T(-0.06, 0.0, 0.34)), cam),
             (place(cast3.bag_flat(t=lt, spilled=1.0), T(0.30, 0.0, 0.06) @ S(0.9)), cam)]
    compose_3d(img, pairs)

    for i in range(4):                                  # the books, still where they fell
        px = 0.44 + 0.16 * i
        cut(img, place(cast3.book(cast3.BOOKS[i % 4]), T(px + 0.06, 0.0, 0.30 + 0.09 * (i % 2))
                       @ R("y", -50 + i * 26) @ R("z", 4 - 3 * i)), cam)

    bg3.dust(img, lt, 55, seed=13, alpha=85)
    if lt > 3.4:
        caption(img, 1620, "সে কিছু বলল না", 38)
    bg3.near_plane(img, 0.85)
    bg3.grade(img, tint=(255, 248, 234))


# ---------------------------------------------------------------- s5 · one person
def s5(img, lt, dur):
    """One girl leaves the ring. She picks up one book. Two shadows become one."""
    cam = cam_at((0.16, 1.34, 6.6), (0.05, 0.78, 0.30), 34)
    field(img, cam, drift=-0.15, t=lt, sun=(0.78, 0.12))

    come = eout(segd(0.3, 2.6, lt), 2)
    kneel = eio(segd(2.3, 3.2, lt))
    give = eio(segd(3.3, 4.2, lt))

    mx = lerp(3.30, 0.30, come)
    mira_m, mhands, mhd = cast3.mira(t=lt, walk=lt * 1.9 * (1 - come), look=-0.55,
                                     crouch=0.52 * kneel, reach=0.45 * give,
                                     arm=lerp(0.0, 0.35, give), head=6 * kneel,
                                     blink=1.0 - eout(segd(2.0, 2.5, lt)))
    ayan_m, hands, hd = cast3.ayan(t=lt, look=lerp(0.1, 0.55, come), slump=0.9,
                                   crouch=0.86, head=8, blink=0.0)

    # once she is close, the two shadows overlap: that is the whole film in one shape
    # the two shadows run into each other as she kneels: one shape instead of two
    if give > 0.02:
        k = segd(0.02, 1.0, give)
        shadow(img, cam, lerp(-0.30, -0.10, k), 0.30, h=1.28, w=lerp(0.24, 0.66, k),
               slope=0.62, alpha=int(96 * k), blur=10)
    shadow(img, cam, -0.34, 0.36, h=1.16, w=0.32, slope=0.62, alpha=112, blur=7)
    shadow(img, cam, mx - 0.02 * give, 0.24, h=1.34 - 0.30 * kneel, w=0.26, slope=0.62,
           alpha=104, blur=7)


    people = [(2.35, -2.7, 1.0, 0.0, -0.9, 0.2, 3), (-1.45, -3.6, 1.03, 0.0, 0.5, 0.1, 0),
              (-2.35, -2.4, 0.98, 0.0, 0.8, 0.1, 1)]
    pairs = crowd_ring(img, cam, lt, people)
    pairs += [(place(ayan_m, T(-0.34, 0.0, 0.36) @ R("y", -10 * kneel)), cam),
              (place(mira_m, T(mx, 0.0, 0.24 + 0.04 * (1 - come)) @ R("y", 12 * kneel)), cam)]
    compose_3d(img, pairs)

    # the book passes between them
    if give > 0.02:
        bx = lerp(mx - 0.06, -0.10, give)
        by = 0.50 + 0.16 * math.sin(give * math.pi) - 0.10 * give
        cut(img, place(cast3.book(cast3.BOOKS[1]), T(bx, by, 0.46) @ R("y", 26 + 44 * give)
                       @ S(1.35)), cam)

    bg3.dust(img, lt, 60, seed=17, alpha=90)
    if lt > 3.6:
        caption(img, 1620, "একজন এগিয়ে এল", 38, TEAL)
    bg3.near_plane(img, 0.8)
    bg3.grade(img, tint=(255, 248, 234), sat=1.04)


# ---------------------------------------------------------------- s6 · the field again
def s6(img, lt, dur):
    """Empty field, late light, one long shadow for two people. The lesson, plainly."""
    cam = cam_at((-0.10, 1.50, 6.2), (-0.30, 0.95, 0.10), 33)
    field(img, cam, drift=-0.10, t=lt, sun=(0.86, 0.20), heatk=0.25)

    # they walk away down the field; the camera holds, so they get smaller and the
    # two shadows keep overlapping — by now it is one shadow with two people in it
    go = eio(segd(0.3, dur * 0.96, lt))
    az = lerp(0.10, -3.10, go)
    ax, mx = lerp(-0.10, 0.24, go), lerp(0.13, 0.44, go)
    shadow(img, cam, ax + 0.02, az, h=1.40, w=0.34, slope=1.65, alpha=118, blur=8)
    shadow(img, cam, mx + 0.02, az - 0.02, h=1.30, w=0.30, slope=1.65, alpha=104, blur=8)
    ayan_m, hands, hd = cast3.ayan(t=lt, walk=lt * 1.9, look=0.0, slump=0.10)
    mira_m, mh, mhd = cast3.mira(t=lt, walk=lt * 1.9 + 0.4, look=0.0, blink=0.0)
    compose_3d(img, [(place(ayan_m, T(ax, 0.0, az) @ R("y", 180)), cam),
                     (place(mira_m, T(mx, 0.0, az - 0.02) @ R("y", 180)), cam)])

    k = eout(segd(0.8, 2.0, lt))
    if k > 0.03:
        deva.draw_text(img, (540, 396), "অন্ধকার আলোর অভাব নয়", int(48 * k + 6), 700, (28, 30, 34),
                       shadow=(255, 252, 240), shadow_blur=18)
        deva.draw_text(img, (540, 480), "যেখানে সবাই দেখেও দেখে না", int(48 * k + 6), 700, RUST,
                       shadow=(255, 252, 240), shadow_blur=18)

    bg3.dust(img, lt, 70, seed=19, alpha=110)
    bg3.near_plane(img, 0.9)
    bg3.grade(img, tint=(255, 244, 222), sat=1.06)


# ---------------------------------------------------------------- s7 · the card
_TILE = None
_TQ = -1.0


def s7(img, lt, dur):
    """The CTA, in daylight: the series has never ended on a black card until now."""
    arr = np.asarray(Image.new("RGB", (W, H), PAPER))
    ys = np.linspace(0, 1, H)[:, None, None]
    top = np.array([236, 232, 214], float)
    bot = np.array([250, 245, 231], float)
    arr = (top * (1 - ys) + bot * ys).astype(np.uint8).repeat(W, axis=1)
    img.paste(Image.fromarray(arr, "RGB"))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([-160, -260, W + 160, 520], fill=(212, 226, 232, 120))
    bg3._glow(img, W * 0.5, 120, 520, 300, (255, 250, 226), 120, 2.2)

    k1 = eout(segd(0.15, 0.75, lt))
    k2 = eout(segd(0.55, 1.15, lt))
    k3 = eout(segd(1.00, 1.65, lt))
    k4 = eout(segd(1.45, 2.10, lt))
    k5 = eout(segd(1.95, 2.55, lt))

    label = "অন্ধকার পাঠ · ০৩"
    deva.draw_text(img, (540, 300), label, 40, 700, (86, 78, 66),
                   shadow=(255, 255, 255), shadow_blur=10)
    d.line([(400, 344), (680, 344)], fill=(120, 108, 88, 150), width=2)

    if k1 > 0.03:
        deva.draw_text(img, (540, 470), "তুমি দেখেছিলে —", int(54 * k1 + 8), 700, INK,
                       shadow=(255, 255, 255), shadow_blur=14)
    if k2 > 0.03:
        deva.draw_text(img, (540, 566), "তারপর কী করলে?", int(58 * k2 + 8), 700, TEAL,
                       shadow=(255, 255, 255), shadow_blur=14)
    if k3 > 0.03:
        deva.draw_text(img, (540, 686), "দেখে চুপ থাকাটাও একটা বেছে নেওয়া।", 32, 600,
                       (72, 66, 56), shadow=(255, 255, 255), shadow_blur=10)
    if k4 > 0.03:
        deva.draw_text(img, (540, 900), "কমেন্ট করো: কী করেছিলে?", 42, 700, RUST,
                       shadow=(255, 255, 255), shadow_blur=12)
        pw = 620 * k4
        d.rounded_rectangle([540 - pw / 2, 1010, 540 + pw / 2, 1146], 38, fill=(24, 116, 128))
        if k4 > 0.9:
            deva.draw_text(img, (540, 1078), "ফলো করো", 48, 700, (250, 248, 238))
    if k5 > 0.03:
        deva.draw_text(img, (540, 1224), "প্রতি শুক্রবার · নতুন পাঠ", 34, 600, (96, 88, 74),
                       shadow=(255, 255, 255), shadow_blur=10)
        d.line([(340, 1272), (340 + 400 * k5, 1272)], fill=(24, 116, 128, 180), width=3)

    # a small daylight vignette: the two of them, walking out, at the bottom
    qt = round(lt * 4) / 4.0
    global _TILE, _TQ
    if _TILE is None or _TQ != qt:
        cam = cam_at((0.0, 1.35, 4.2), (0.05, 0.95, 0.15), 34)
        a_m, _, _ = cast3.ayan(t=qt, walk=qt * 2.0, look=0.1, slump=0.1)
        m_m, _, _ = cast3.mira(t=qt, walk=qt * 2.0 + 0.5, look=-0.1)
        sub = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        compose_3d(sub, [(place(a_m, T(-0.32, 0.0, 0.10)), cam), (place(m_m, T(0.02, 0.0, 0.16)), cam)])
        bbox = sub.getbbox()
        tile = sub.crop(bbox) if bbox else sub
        sc = min(400 / max(1, tile.width), 540 / max(1, tile.height))
        tile = tile.resize((int(tile.width * sc), int(tile.height * sc)), Image.LANCZOS)
        _TILE, _TQ = tile, qt
    img.alpha_composite(_TILE, (int(W / 2 - _TILE.width / 2 + 30),
                               H - 70 - _TILE.height))
    d.line([(120, 1330), (960, 1330)], fill=(150, 140, 118, 90), width=2)


SCENES = [s1, s2, s3, s4, s5, s6, s7]


def draw(t):
    img = Image.new("RGBA", (W, H), (236, 232, 214, 255))
    i = 0
    for k in range(len(BOUNDS) - 1):
        if t >= BOUNDS[k]:
            i = k
    lo, hi = BOUNDS[i], BOUNDS[i + 1]
    SCENES[min(i, 6)](img, t - lo, hi - lo)
    return img.convert("RGB")


def main():
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1])
        os.makedirs("frames", exist_ok=True)
        draw(t).save("frames/still-%05.2f.png" % t)
        print("still", t)
        return

    print("timeline", NAR, "end", END_AT, "total", TOTAL, "frames", NF, flush=True)

    if "--seg" in sys.argv:
        j = sys.argv.index("--seg")
        a, b, sp = int(sys.argv[j + 1]), int(sys.argv[j + 2]), sys.argv[j + 3]
        cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", sp]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(a, b):
            proc.stdin.write(draw(i / FPS).tobytes())
            if (i - a) % 60 == 0:
                print("  seg %d/%d" % (i - a, b - a), flush=True)
        proc.stdin.close()
        proc.wait()
        print("segdone", sp, os.path.getsize(sp), flush=True)
        return

    if "--mix" in sys.argv:
        inputs, filt, labels = [], [], []
        for k, (p, start) in enumerate(zip(AUD, NAR)):
            inputs += ["-i", p]
            ms = int(round(start * 1000))
            filt.append("[%d:a]adelay=%d|%d[a%d]" % (k, ms, ms, k))
            labels.append("[a%d]" % k)
        fc = ";".join(filt) + ";" + "".join(labels) + "amix=inputs=7:normalize=0,apad[a]"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error"] + inputs +
                       ["-filter_complex", fc, "-map", "[a]", "-ar", "44100", "-ac", "2",
                        "-t", "%.3f" % TOTAL, MIX], check=True)
        print("mix ok", os.path.getsize(MIX))
        return

    if "--join" in sys.argv:
        segs = sys.argv[sys.argv.index("--join") + 1:]
        with open("segs.txt", "w") as f:
            for sp in segs:
                f.write("file '%s'\n" % os.path.abspath(sp))
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", "segs.txt", "-i", MIX, "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "144k", "-movflags", "+faststart",
                        OUT], check=True)
        print("joined", os.path.getsize(OUT))
        return

    out = OUT
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-i", MIX,
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "144k", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(NF):
        proc.stdin.write(draw(i / FPS).tobytes())
        if i % 240 == 0:
            print("  %d/%d" % (i, NF), flush=True)
    proc.stdin.close()
    proc.wait()
    print("done", out, os.path.getsize(out))


if __name__ == "__main__":
    main()
