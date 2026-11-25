"""film.py — "কিসের তুলনায়?" / Compared to What?  ·  2 minutes, 16:9, 24 fps.

Six scenes, shot-timed to the narration. Every frame is a pure function of t.
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import cast
import deva
import studio as st

W, H = 1920, 1080        # output
RW, RH = 1600, 900       # rendered, then upscaled (the look wants a little softness)
FPS = 20
DUR = 121.5
NF = int(FPS * DUR)

INK = (58, 42, 32)
RUST = (150, 62, 40)
PAPER = (240, 230, 210)

# ---------------------------------------------------------------- voice-over map
VO = [
    ("vo1a", 2.4, 6.94),
    ("vo1b", 10.2, 9.34),
    ("vo2", 21.2, 16.30),
    ("vo3", 39.2, 12.50),
    ("vo4owl", 60.0, 1.70),
    ("vo4b", 64.2, 11.02),
    ("vo5", 78.6, 16.22),
    ("vo6", 98.5, 8.74),
]
END = 121.5


def ease(p):
    p = min(max(p, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * p)


def ramp(t, a, b):
    return min(max((t - a) / (b - a), 0.0), 1.0)


# ---------------------------------------------------------------- 2D cards
_CARDS = {}


def _paper(w, h, tone=PAPER, edge=(206, 190, 164)):
    im = Image.new("RGBA", (w, h), tone + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=edge + (255,), width=3)
    return im


def price_card(old, new, w=760, h=420, struck=True):
    key = ("p", old, new, struck)
    if key in _CARDS:
        return _CARDS[key]
    im = _paper(w, h)
    d = ImageDraw.Draw(im)
    deva.draw_text(im, (w * 0.30, h * 0.40), old, 120, 700, (120, 106, 90))
    if struck:
        d.line([(w * 0.10, h * 0.40), (w * 0.50, h * 0.40)], fill=RUST + (235,), width=13)
    deva.draw_text(im, (w * 0.72, h * 0.62), new, 190, 700, RUST)
    _CARDS[key] = im
    return im


def plain_card(num, w=520, h=380):
    key = ("n", num)
    if key in _CARDS:
        return _CARDS[key]
    im = _paper(w, h)
    deva.draw_text(im, (w / 2, h * 0.55), num, 170, 700, INK)
    _CARDS[key] = im
    return im


def receipt_card(num, w=260, h=340):
    key = ("r", num)
    if key in _CARDS:
        return _CARDS[key]
    im = _paper(w, h, tone=(247, 240, 226))
    deva.draw_text(im, (w / 2, h * 0.34), "বিক্রি", 42, 500, (120, 108, 92))
    deva.draw_text(im, (w / 2, h * 0.64), num, 96, 700, INK)
    _CARDS[key] = im
    return im


def warp_card(card, quad):
    """Perspective-map a flat card onto a screen-space quadrilateral."""
    w, h = card.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    A, b = [], []
    for (x, y), (u, v) in zip(quad, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        b.append(u * 1.0)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        b.append(v * 1.0)
    try:
        co = np.linalg.solve(np.array(A, float), np.array(b, float))
    except np.linalg.LinAlgError:
        return Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return card.transform((W, H), Image.PERSPECTIVE, tuple(co), Image.BICUBIC,
                          fillcolor=(0, 0, 0, 0))



def _text(img, xy, s, size, weight, rgb, alpha=1.0):
    """Bangla on top of the frame, with an alpha fade (deva draws at full alpha)."""
    if alpha <= 0.02:
        return
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    deva.draw_text(layer, xy, s, size, weight, tuple(rgb))
    if alpha < 0.999:
        layer.putalpha(layer.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(layer)


def quad_of(cam, corners):
    """Project to the render buffer, then scale to the output frame the card is warped on."""
    P = st.project(np.array(corners, float), cam, RW, RH)
    sx, sy = W / RW, H / RH
    return [(p[0] * sx, p[1] * sy) for p in P]


# ---------------------------------------------------------------- set
def town():
    """The square: four shops, a signpost, a tree or three. Built once, re-framed per shot."""
    o = []
    o += cast.shop((-0.6, 0, -9.4), w=6.8, d=4.2, h=4.15, wall=np.array([0.75, 0.66, 0.54]),
                   roof=np.array([0.50, 0.29, 0.26]), awning=np.array([0.48, 0.30, 0.28]))
    o += cast.shop((-8.4, 0, -8.2), w=5.6, d=4.0, h=3.85, ry=0.10,
                   wall=np.array([0.67, 0.61, 0.56]), roof=np.array([0.42, 0.36, 0.34]),
                   awning=np.array([0.34, 0.38, 0.36]))
    o += cast.shop((7.0, 0, -8.8), w=6.0, d=4.0, h=3.7, ry=-0.10,
                   wall=np.array([0.71, 0.60, 0.50]), roof=np.array([0.46, 0.32, 0.28]),
                   awning=np.array([0.52, 0.38, 0.30]))
    o += cast.shop((13.6, 0, -7.0), w=4.6, d=3.6, h=3.3, ry=-0.16,
                   wall=np.array([0.62, 0.56, 0.48]), roof=np.array([0.40, 0.30, 0.26]),
                   awning=np.array([0.58, 0.52, 0.44]), lit=False)
    o += cast.signpost((-4.2, 0, 0.6), h=2.55)
    o += cast.tree((4.2, 0, -8.0), 4.0, seed=3)
    o += cast.tree((-5.0, 0, -13.0), 3.6, seed=9)
    o += cast.tree((11.0, 0, -11.0), 3.4, seed=5)
    o += cast.tree((-12.0, 0, -3.0), 3.2, seed=11)
    o += cast.lamp((-1.8, 0, -2.4))
    o += cast.lamp((6.2, 0, -4.4), h=2.8)
    o += cast.barrel((2.9, 0, -6.9))
    o += cast.barrel((3.4, 0, -6.5), s=0.3)
    o += cast.crate((5.0, 0, -7.2), 0.5)
    o += cast.crate((5.4, 0, -6.9), 0.38, col=np.array([0.58, 0.44, 0.30]))
    o += cast.bicycle((1.85, 0.0, -6.6), ry=1.45, wheel_spin=0.4)
    # the shop's counter, and the receipt box that lives behind it
    o.append(cast._bx(np.array([0.55, 0.40, 0.28]), (1.05, 0.52, -3.9), (2.1, 1.04, 0.72)))
    o.append(cast._bx(np.array([0.66, 0.50, 0.36]), (1.05, 1.06, -3.9), (2.2, 0.07, 0.82)))
    o.append(cast._bx(np.array([0.47, 0.36, 0.27]), (0.45, 1.24, -4.05), (0.52, 0.30, 0.42)))
    return o


SET = town()

SIGN_C = (-0.6, 3.32, -7.15)
SIGN_W, SIGN_H = 2.5, 1.35


def sign_board():
    x, y, z = SIGN_C
    quad = [(x - SIGN_W / 2, y + SIGN_H / 2, z + 0.03), (x + SIGN_W / 2, y + SIGN_H / 2, z + 0.03),
            (x + SIGN_W / 2, y - SIGN_H / 2, z + 0.03), (x - SIGN_W / 2, y - SIGN_H / 2, z + 0.03)]
    frame = [cast._bx(np.array([0.74, 0.68, 0.57]), (x, y, z), (SIGN_W + 0.22, SIGN_H + 0.22, 0.10)),
             cast._bx(np.array([0.40, 0.32, 0.25]), (x, y + SIGN_H / 2 + 0.24, z + 0.06),
                      (SIGN_W + 0.34, 0.06, 0.20))]
    return frame, quad


def tag_quad(x, y, z, w=0.62, h=0.44):
    return [(x - w / 2, y + h / 2, z), (x + w / 2, y + h / 2, z),
            (x + w / 2, y - h / 2, z), (x - w / 2, y - h / 2, z)]


# ---------------------------------------------------------------- 1 · the sign
def s1(t):
    o = list(SET)
    frame, squad = sign_board()
    o += frame
    fill = 0.0
    if t < 3.4:
        p = ramp(t, 0.0, 3.4)
        cam = st.Cam((-1.5 + 0.7 * p, 2.60, 16.0 - 0.9 * p), (-0.5, 2.12, -9.0), fov=27)
        x = -7.0 + 3.7 * ease(ramp(t, 0.4, 3.4))
        o += cast.bruno((x, 2.2), ry=-1.42, hop=0.05 * abs(math.sin(t * 5.2)),
                        ears=0.15, look=0.3, pack=True, purse=True)
    elif t < 7.6:
        p = ramp(t, 3.4, 7.6)
        x = -3.2 + 2.0 * ease(p)
        cam = st.Cam((x - 1.5, 1.02, 4.45), (x + 0.30, 0.80, 2.2), fov=29)
        hop = 0.075 * abs(math.sin((t - 3.4) * 6.0))
        o += cast.bruno((x, 2.2), ry=-1.5, hop=hop, ears=0.25, purse=True,
                        held=(0.24, 0.38 + hop * 0.4, 0.22))
    elif t < 14.2:
        p = ramp(t, 7.6, 14.2)
        cam = st.Cam((0.15 + 0.3 * p, 1.28, 2.2), (-0.55, 2.48, -9.0), fov=40)
        o += cast.bruno((0.95 - 0.22 * ease(ramp(t, 8.4, 10.6)), 0.85),
                        ry=math.pi, hop=0.015, ears=0.0, look=0.9, purse=True)
    else:
        p = ramp(t, 14.2, 20.8)
        cam = st.Cam((0.57, 0.96, -0.55), (0.60, 0.86, 1.58), fov=23)
        fill = 0.30
        eyes = 1.0 + 1.15 * ease(ramp(t, 14.9, 17.2))
        o += cast.bruno((0.60, 1.58), ry=math.pi, hop=0.0, ears=0.55, look=0.7,
                        purse=True, pack=True, eyes=eyes)

    def post(img, cam):
        img.alpha_composite(warp_card(price_card("২০০", "৭৯"), quad_of(cam, squad)), (0, 0))
        k = ramp(t, 0.7, 1.5) * (1 - ramp(t, 2.9, 3.5))
        if k > 0:
            _text(img, (W / 2, H * 0.16), "কিসের তুলনায়?", 76, 700, (252, 242, 224), 0.94 * k)
            _text(img, (W / 2, H * 0.245), "একটি ছোট্ট গল্প", 32, 500, (234, 222, 202), 0.78 * k)
        return img
    return o, cam, post, fill


# ---------------------------------------------------------------- 2 · the watcher
def s2(t):
    fill = 0.0
    o = list(SET)
    o += sign_board()[0]
    if t < 27.4:
        cam = st.Cam((1.25, 1.45, 2.75), (-4.15, 3.05, 0.55), fov=27)
        eyes = 0.10 if 26.6 < t < 26.9 else 1.0
        head = math.sin(math.pi * ease(ramp(t, 21.6, 24.2))) * 1.6
        o += _lift(cast.olive((-4.2, 0.6), ry=-0.5, eyes=eyes, head=head), 2.52)
        fill = 0.20
    elif t < 34.0:
        p = ramp(t, 27.4, 34.0)
        x = 2.1 - 2.2 * ease(p)
        cam = st.Cam((-0.5, 1.06, 5.7), (0.8, 0.74, 1.6), fov=32)
        hop = 0.10 * abs(math.sin((t - 27.4) * 7.4))
        o += cast.bruno((x, 1.6), ry=1.75, hop=hop, ears=0.7, purse=True,
                        held=(0.26, 0.40 + hop, 0.26), eyes=1.3)
    else:
        cam = st.Cam((0.9, 1.62, 3.9), (-4.15, 3.02, 0.55), fov=23)
        eyes = 1.0 - 0.9 * ramp(t, 37.7, 38.2)
        o += _lift(cast.olive((-4.2, 0.6), ry=-0.5, eyes=eyes), 2.52)
        o += cast.bruno((0.4, 2.4), ry=1.75, hop=0.02, ears=0.3, purse=True)

    def post(img, cam):
        img.alpha_composite(warp_card(price_card("২০০", "৭৯"), quad_of(cam, squad := sign_board()[1])),
                            (0, 0))
        return img
    return o, cam, post, fill


def _lift(objs, dy):
    for ob in objs:
        ob.V = ob.V + np.array([0.0, dy, 0.0])
    return objs


# ---------------------------------------------------------------- 3 · the montage
def s3(t):
    o = list(SET)
    o += sign_board()[0]
    if t < 43.6:
        cam = st.Cam((4.5, 1.16, 2.6), (6.35, 1.32, -4.8), fov=34)
        o += cast.scooter((6.6, 0, -5.0), ry=2.75)
        o += cast.bruno((5.05, -2.3), ry=1.9, hop=0.03, ears=0.35, look=0.8, purse=True,
                        eyes=1.15)
    elif t < 48.6:
        cam = st.Cam((-5.20, 1.12, 1.50), (-7.60, 1.30, -5.00), fov=34)
        o += cast.pedestal((-8.2, 0, -5.2), 0.48)
        o += cast.helmet((-8.2, 0.48, -5.2))
        o += cast.bruno((-6.00, -1.40), ry=1.9, hop=0.03, ears=0.4, look=0.7, purse=True,
                        eyes=1.2)
    else:
        p = ramp(t, 48.6, 53.6)
        cam = st.Cam((-0.2 + 0.2 * p, 1.02, 4.4), (-0.4, 0.82, 0.0), fov=30)
        hop = 0.055 * abs(math.sin((t - 48.6) * 6.6))
        o += cast.bruno((-0.5, 1.6), ry=0.35, hop=hop, ears=0.55, purse=True,
                        held=(0.26, 0.40 + hop, 0.26), eyes=1.35)

    def post(img, cam):
        if t < 43.6:
            q = tag_quad(6.55, 2.62, -6.55, 1.55, 1.02)
            img.alpha_composite(warp_card(price_card("১৫০", "৫৯", 620, 400), quad_of(cam, q)), (0, 0))
        elif t < 48.6:
            q = tag_quad(-8.15, 2.38, -5.75, 1.45, 0.96)
            img.alpha_composite(warp_card(price_card("৬০", "২৫", 620, 400), quad_of(cam, q)), (0, 0))
        else:
            img.alpha_composite(warp_card(price_card("২০০", "৭৯"), quad_of(cam, sign_board()[1])),
                                (0, 0))
        return img
    return o, cam, post, 0.0


# ---------------------------------------------------------------- 4 · the question
def s4(t):
    o = list(SET)
    o += sign_board()[0]
    lt = t - 53.6
    push = ease(ramp(lt, 0.0, 19.4))
    cam = st.Cam((2.90 - 0.55 * push, 1.38, 3.90 - 0.95 * push),
                 (0.20, 1.50, -7.20), fov=34)
    o += cast.bruno((1.35, 0.55), ry=math.pi * 0.94, hop=0.012, ears=0.2, look=0.5,
                    purse=True, held=(0.30, 0.32, 0.22))
    # Olive comes down off the post and lands beside him
    glide = ease(ramp(lt, 3.4, 5.6))
    if glide > 0:
        ex = -4.2 + 6.15 * glide
        ez = 0.6 + 0.15 * glide
        ey = 2.52 * (1 - glide) + 0.05 * (1 - abs(2 * glide - 1))
        o += _lift(cast.olive((ex, ez), ry=-1.2, eyes=1.0,
                              wing_out=1.0 - glide, flap=math.sin(lt * 15) * (1 - glide)), ey)
    if glide >= 0.999:                              # she lifts one feather toward the crossed-out tag
        lift = ease(ramp(lt, 5.8, 6.6))
        o.append(cast._bx(np.array([0.88, 0.84, 0.76]),
                          (1.02, 1.52 + 0.46 * lift, 0.30), (0.09, 0.42, 0.05),
                          rot=(0, 0.3, -0.6 + 0.6 * lift)))

    def post(img, cam):
        quad = quad_of(cam, sign_board()[1])
        card = price_card("২০০", "৭৯")
        crack = ramp(t, 62.2, 63.6)
        if crack <= 0:
            img.alpha_composite(warp_card(card, quad), (0, 0))
        else:
            _shards(img, cam, card, quad, crack)
        for i in range(5):                          # the receipt box: every sale reads the same
            k = ramp(t, 65.4 + i * 0.5, 66.2 + i * 0.5)
            if k > 0:
                q = tag_quad(0.52 + i * 0.30, 1.24 + 0.30 * i + 0.26 * k, -3.55, 0.30, 0.40)
                layer = warp_card(receipt_card("৭৯"), quad_of(cam, q))
                a = layer.split()[3].point(lambda v: int(v * min(1.0, k * 1.5)))
                layer.putalpha(a)
                img.alpha_composite(layer, (0, 0))
        return img
    return o, cam, post, 0.16


def _shards(img, cam, card, quad, crack):
    """Break the price card into paper pieces that fall out of frame."""
    xs = [q[0] for q in quad]
    ys = [q[1] for q in quad]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    cols, rows = 5, 4
    cw, ch = card.width // cols, card.height // rows
    for i in range(cols):
        for j in range(rows):
            piece = card.crop((i * cw, j * ch, (i + 1) * cw, (j + 1) * ch))
            u0, u1 = i / cols, (i + 1) / cols
            v0, v1 = j / rows, (j + 1) / rows

            def lp(u, v):
                ax = quad[0][0] + (quad[1][0] - quad[0][0]) * u
                ay = quad[0][1] + (quad[1][1] - quad[0][1]) * u
                bx = quad[3][0] + (quad[2][0] - quad[3][0]) * u
                by = quad[3][1] + (quad[2][1] - quad[3][1]) * u
                return (ax + (bx - ax) * v, ay + (by - ay) * v)

            q = [lp(u0, v0), lp(u1, v0), lp(u1, v1), lp(u0, v1)]
            rng = np.random.RandomState(i * 7 + j * 13 + 5)
            k = min(max((crack - rng.uniform(0.0, 0.22)) / 0.66, 0.0), 1.0)
            dx = (float(q[0][0]) - cx) * 0.12 * k
            dy = 760 * k * k + 40 * k
            piece = piece.rotate(rng.uniform(-40, 40) * k, resample=Image.BICUBIC,
                                 fillcolor=(0, 0, 0, 0))
            layer = warp_card(piece, [(px + dx, py + dy) for px, py in q])
            fade = int(255 * max(0.0, (1 - max(0.0, (k - 0.72) / 0.28))))
            if fade > 3:
                layer.putalpha(layer.split()[3].point(lambda v: v * fade // 255))
                img.alpha_composite(layer, (0, 0))


# ---------------------------------------------------------------- 5 · the honest shop
def s5(t):
    o = list(SET)
    lt = t - 76.6
    cam = st.Cam((11.35 + 0.35 * ease(ramp(lt, 0.0, 14.0)), 1.22, 0.95),
                 (12.95, 1.14, -4.2), fov=34)
    bx = 11.5 + 1.15 * ease(ramp(lt, 0.4, 4.4))
    hop = 0.05 * abs(math.sin((t - 76.6) * 5.6)) * (1 - ramp(lt, 4.4, 5.2))
    o += cast.bruno((bx, -1.15), ry=math.pi * 0.92, hop=hop, ears=0.25, purse=True)
    o += cast.hedgehog((12.95, -2.95), ry=-2.3)
    if lt > 5.6:
        roll = ease(ramp(lt, 5.6, 10.5))
        o += cast.bicycle((12.95 - 0.35 * roll, 0.0, -3.2 + 0.9 * roll), ry=0.35, scale=1.1,
                          wheel_spin=2.2 * lt)
    if lt > 11.5:
        o += cast.crate((11.9, 0, -1.2), 0.42)

    def post(img, cam):
        q = tag_quad(13.62, 2.02, -5.35, 0.82, 0.58)
        layer = warp_card(plain_card("৬৫"), quad_of(cam, q))
        a = ramp(t, 79.4, 80.4)
        if a < 1:
            layer.putalpha(layer.split()[3].point(lambda v: int(v * a)))
        img.alpha_composite(layer, (0, 0))
        return img
    return o, cam, post, 0.0


# ---------------------------------------------------------------- 6 · the moral
def s6(t):
    o = list(SET)
    lt = t - 96.4
    cam = st.Cam((-3.4 + 1.5 * ease(ramp(lt, 0.0, 12.0)), 1.30,
                  5.6 - 1.0 * ease(ramp(lt, 0.0, 12.0))), (-1.2, 1.15, -9.0), fov=33)
    ride = 2.6 * ease(ramp(lt, 0.0, 9.5))
    bx = -3.1 + ride
    o += cast.bicycle((bx, 0.0, 2.6), ry=0.0, wheel_spin=2.4 * lt, scale=1.22)
    o += _lift(cast.bruno((bx - 0.16, 2.6), ry=0.10, ears=0.55, purse=False, pack=True,
                          hop=0.0), 0.22)
    o.append(cast._bx(np.array([0.80, 0.32, 0.30]), (bx - 0.12, 0.66, 2.62),
                      (0.22, 0.09, 0.24), rot=(0, 0, 0.3)))
    o.append(cast._bx(np.array([0.80, 0.32, 0.30]), (bx + 0.18, 0.72, 2.62),
                      (0.10, 0.30, 0.06), rot=(0.2, 0, -0.25)))
    if lt < 6.2:
        o += _lift(cast.olive((-1.8, -2.6), ry=0.4,
                              eyes=0.10 if 4.0 < lt < 4.35 else 1.0), 2.96)
    else:
        p = ease(ramp(lt, 6.2, 12.5))
        o += _lift(cast.olive((-1.8 + 4.2 * p, -2.6), ry=0.6, eyes=0.1, wing_out=1.0,
                              flap=math.sin(lt * 9) * 0.7), 2.96 + 2.6 * p)

    def post(img, cam):
        k = ramp(t, 101.2, 104.2)
        if k > 0:
            scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(scrim).rectangle([0, 0, W, H], fill=(24, 19, 15, int(104 * k)))
            img.alpha_composite(scrim)
            _text(img, (W / 2, H * 0.40), "জিজ্ঞেস করো:", 56, 500, (236, 224, 202), k)
            _text(img, (W / 2, H * 0.54), "কিসের তুলনায়?", 108, 700, (247, 236, 214), k)
            _text(img, (W / 2, H * 0.71), "কেউ বড় দাম কেটে দিলেই সেটা সস্তা হয়ে যায় না।",
                  38, 500, (222, 206, 182), 0.93 * k)
        fade = ramp(t, 118.6, 121.4)
        if fade > 0:
            img = Image.blend(img.convert("RGB"), Image.new("RGB", (W, H), (8, 7, 6)),
                              fade).convert("RGBA")
        return img
    return o, cam, post, 0.0


SCENES = [(0.0, s1), (20.8, s2), (38.8, s3), (53.6, s4), (76.6, s5), (96.4, s6)]


def draw(t):
    fn = SCENES[0][1]
    for t0, f in SCENES:
        if t >= t0:
            fn = f
    o, cam, post, fill = fn(t)
    rgb = st.render(o, cam, RW, RH, fill=fill)
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    img = img.resize((W, H), Image.BICUBIC).convert("RGBA")
    img = post(img, cam).convert("RGB")
    return img


# ---------------------------------------------------------------- audio bed
def voice_track(path="vo/track.wav"):
    """Lay the narration on one timeline with tiny breaths between lines."""
    import wave
    ff = _ffmpeg()
    n = int(END * 44100)
    acc = np.zeros(n, np.float32)
    for name, start, dur in VO:
        src = "vo/%s.mp3" % name
        if not os.path.exists(src):
            continue
        raw = subprocess.run([ff, "-v", "quiet", "-i", src, "-f", "s16le", "-ac", "1",
                              "-ar", "44100", "-"], capture_output=True).stdout
        a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
        i0 = int(start * 44100)
        i1 = min(n, i0 + len(a))
        acc[i0:i1] += a[:i1 - i0]
    acc *= 0.9
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes((np.clip(acc, -1, 1) * 32767).astype(np.int16).tobytes())
    return path


def _ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


# ---------------------------------------------------------------- render
def write_seg(a, b, out):
    ff = _ffmpeg()
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(a, b):
        img = draw(i / FPS)
        p.stdin.write(img.tobytes())
        if i % 60 == 0:
            print("  frame %d/%d" % (i, b), flush=True)
    p.stdin.close()
    p.wait()
    print("segdone", out, os.path.getsize(out), flush=True)


def join(segs, out="compared-to-what-1920x1080.mp4"):
    ff = _ffmpeg()
    with open("segs.txt", "w") as fh:
        for sp in segs:
            fh.write("file '%s'\n" % os.path.abspath(sp))
    args = [ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "segs.txt"]
    if os.path.exists("audio/mix.wav"):
        args += ["-i", "audio/mix.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                 "-shortest"]
    args += ["-movflags", "+faststart", out]
    subprocess.run(args, check=True)
    print("joined", os.path.getsize(out))


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    os.makedirs("frames", exist_ok=True)
    if a[0] == "--still":
        draw(float(a[1])).save("frames/still-%05.2f.png" % float(a[1]))
        print("ok")
    elif a[0] == "--seg":
        write_seg(int(a[1]), int(a[2]), a[3])
    elif a[0] == "--join":
        join(a[1:])


if __name__ == "__main__":
    main()
