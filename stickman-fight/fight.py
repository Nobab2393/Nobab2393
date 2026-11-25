#!/usr/bin/env python3
"""fight.py — অন্ধকার পাঠ ০৩ · লড়াই (DARK LESSON 03: FIGHT)

A daylight stickman fight in Bangla, 1080x1920, drawn with plain 2D line art on a PIL canvas.

    python3 fight.py --poses          a pose sheet (design aid)
    python3 fight.py --still 12.0     one frame
    python3 fight.py --mix            build audio/mix.wav (voice + procedural sfx)
    python3 fight.py --seg A B out.mp4
    python3 fight.py --join s1.mp4 ... s7.mp4
    python3 fight.py                  full render

Story: he trains alone in the sun. Last year Rafiq threw him down in front of everyone. He
never trained revenge — he trained the slip. In the rematch nothing lands: ten punches, three
kicks, and Rafiq falls to his own exhaustion. Then a hand is offered.
"""
import math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import stage as S
import deva
from stage import (W, H, SS, Cam, cam_for, sun_screen, ease, eout, ein, seg, lerp, clamp, mix, seq, pose, kf,
                   sky, sun, ground, skyline, draw_fig, shadow, dust, speedlines, arc, grade)

FPS = 24
FONT_EN = "/usr/local/lib/python3.11/dist-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf"
FONT_EN_B = "/usr/local/lib/python3.11/dist-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans-Bold.ttf"
INK = (22, 24, 30)
PAPER = (250, 247, 238)
ACCENT = (198, 74, 46)          # the one accent: a rust red, used only for the anger / impact
COOL = (58, 86, 120)

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG = "ffmpeg"

AUD = ["audio/v%d.mp3" % i for i in range(1, 8)]


def probe(p):
    out = subprocess.run([FFMPEG, "-i", p], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0.0


LEAD = 0.9
GAP = 0.45
TAIL = 3.2
DUR = [probe(p) if os.path.exists(p) else 4.5 for p in AUD]
NAR, acc = [], LEAD
for d in DUR:
    NAR.append(round(acc, 3))
    acc += d + GAP
END_AT = round(NAR[-1] + DUR[-1] + 0.55, 3)
TOTAL = round(END_AT + TAIL, 3)
BOUNDS = [0.0] + [round(n - 0.30, 3) for n in NAR[1:]] + [round(END_AT - 0.25, 3)]
NF = int(round(TOTAL * FPS))

# ---------------------------------------------------------------- poses
STAND = pose(lean=2, l1=-13, l2=11, r1=13, r2=-10, a1=-10, a2=16, b1=10, b2=-14, head=-2)
GUARD = pose(lean=8, l1=-13, l2=11, r1=14, r2=-10, a1=16, a2=76, b1=48, b2=98, head=-3)
GUARD_L = pose(lean=8, l1=-12, l2=10, r1=13, r2=-9, a1=18, a2=80, b1=50, b2=102, head=-3)

WIND = pose(lean=-6, l1=-12, l2=10, r1=13, r2=-9, a1=34, a2=100, b1=18, b2=-128, head=2)
OUT = pose(lean=14, l1=-16, l2=12, r1=16, r2=-11, a1=36, a2=98, b1=88, b2=2, head=-4)
OUT_HI = pose(lean=10, l1=-16, l2=12, r1=16, r2=-11, a1=34, a2=100, b1=104, b2=-6, head=-6)

SLIP = pose(lean=-26, hipdy=0.04, l1=-18, l2=16, r1=20, r2=-14, a1=30, a2=104, b1=38, b2=98, head=-14)
SLIP_L = pose(lean=-20, hipdy=0.02, l1=-24, l2=20, r1=8, r2=-6, a1=30, a2=104, b1=38, b2=98, head=-12)
DUCK = pose(lean=22, hipdy=0.30, l1=-22, l2=34, r1=22, r2=-28, a1=28, a2=108, b1=36, b2=102, head=16)
WEAVE_R = pose(lean=24, hipdy=0.08, l1=-8, l2=8, r1=22, r2=-18, a1=32, a2=104, b1=40, b2=98, head=8)

KICK_W = pose(lean=-8, l1=-10, l2=8, r1=-40, r2=96, a1=30, a2=100, b1=36, b2=96, head=0)
KICK_OUT = pose(lean=-16, l1=-9, l2=7, r1=84, r2=-6, a1=-30, a2=96, b1=-20, b2=92, head=-4)

REACH = pose(lean=12, l1=-10, l2=8, r1=12, r2=-8, a1=-16, a2=10, b1=80, b2=-6, head=6)
TAKE = pose(lean=18, l1=-14, l2=14, r1=16, r2=-12, a1=16, a2=-20, b1=56, b2=-16, head=10)
FALL = pose(lean=-16, rot=-34, hipdy=0.34, l1=-40, l2=52, r1=34, r2=-40,
            a1=-58, a2=-30, b1=-42, b2=-24, head=-12)
DOWN = pose(lean=-2, rot=-86, hipdy=0.80, l1=-58, l2=60, r1=36, r2=-52,
            a1=-88, a2=-6, b1=-74, b2=-14, head=-2)
KNEEL = pose(lean=14, hipdy=0.40, l1=-56, l2=74, r1=36, r2=-50, a1=-30, a2=-18, b1=-22, b2=-30, head=12)
SIT = pose(lean=-12, hipdy=0.62, l1=96, l2=-70, r1=88, r2=-64, a1=-112, a2=40, b1=-102, b2=34, head=-6)
TIRED = pose(lean=26, hipdy=0.10, l1=-16, l2=16, r1=16, r2=-14, a1=-14, a2=26, b1=6, b2=-10, head=18)
BREATHE = pose(lean=4, l1=-10, l2=8, r1=10, r2=-8, a1=-12, a2=8, b1=12, b2=-8, head=-2)
BOW = pose(lean=34, head=22, l1=-12, l2=10, r1=12, r2=-10, a1=-24, a2=20, b1=-20, b2=16)


def step_cycle(t, amp=1.0):
    ph = t * 1.9
    s = math.sin(ph * math.tau)
    return pose(l1=-8 + 26 * s * amp, l2=6 + 18 * abs(s) * amp,
                r1=8 - 26 * s * amp, r2=-6 - 18 * abs(s) * amp,
                a1=-14 - 16 * s * amp, a2=10, b1=14 + 16 * s * amp, b2=-10)


# ---------------------------------------------------------------- strike engine
def strike(t, events, prep=0.26, hit=0.07, tail=0.34):
    """Return (weight_windup, weight_extend) for the nearest active strike."""
    for te in events:
        if te - prep <= t <= te + tail:
            if t < te - hit:
                return ease(seg(te - prep, te - hit, t)), 0.0
            if t < te + hit * 1.6:
                return 1.0, eout(seg(te - hit, te + hit * 0.9, t))
            return 1.0, 1.0 - ease(seg(te + hit * 1.6, te + tail, t))
    return 0.0, 0.0


def fighter(t, events, guard=GUARD, wind=WIND, out=OUT):
    ww, we = strike(t, events)
    p = mix(guard, wind, ww) if ww else dict(guard)
    if we:
        p = mix(p, out, we)
    return p


def shove_shake(t, te, amp=0.06, dur=0.5):
    if 0 <= t - te <= dur:
        k = (1 - (t - te) / dur) ** 2
        return (amp * k * math.sin((t - te) * 60), amp * 0.5 * k * math.cos((t - te) * 47))
    return (0.0, 0.0)


# ---------------------------------------------------------------- text helpers
def bengali(img, xy, text, size, weight=700, color=INK, shadow=PAPER, blur=14):
    deva.draw_text(S.ui(img.size), (xy[0] * SS, xy[1] * SS), text, size, weight, color,
                   shadow=shadow, shadow_blur=blur * SS)


def en(img, xy, text, size, color=(70, 78, 88), bold=False, alpha=255):
    f = ImageFont.truetype(FONT_EN_B if bold else FONT_EN, size)
    d = S.draw_on(img)
    c = tuple(color[:3]) + (alpha,)
    d.text((xy[0] * SS, xy[1] * SS), text, font=f, fill=c, anchor="mm")


def caption(img, text, k=1.0, y=1752):
    """One semantic line of Bangla, on a paper band just under the picture."""
    if k <= 0.02:
        return
    a = clamp(k)
    size = int(42 * SS)
    while size > int(24 * SS):
        tw = deva.text_image(text, size, 600, (26, 28, 34)).width
        if tw <= int(950 * SS):
            break
        size -= int(2 * SS)
    band = Image.new("RGBA", (int(W * SS), int(160 * SS)), (0, 0, 0, 0))
    d = ImageDraw.Draw(band, "RGBA")
    d.rounded_rectangle([int(58 * SS), int(6 * SS), int((W - 58) * SS), int(124 * SS)],
                        int(28 * SS), fill=(252, 250, 244, int(200 * a)))
    S.ui(img.size).alpha_composite(band, (0, int((y - 58) * SS)))
    bengali(img, (W / 2, y), text, size, 600, (26, 28, 34),
            shadow=(252, 250, 244), blur=9)


def brand(img, k=1.0):
    if k <= 0.02:
        return
    a = int(240 * clamp(k))
    bengali(img, (W / 2, 150), "অন্ধকার পাঠ · ০৩", int(34 * SS), 700, (34, 36, 42),
            shadow=(246, 242, 232), blur=10)
    d = S.draw_on(img)
    d.line([(int((W / 2 - 96) * SS), 190 * SS), (int((W / 2 + 96) * SS), 190 * SS)],
           fill=(40, 44, 52, int(110 * k)), width=int(2 * SS))
    en(img, (W / 2, 226), "D A R K   L E S S O N   0 3", int(19 * SS), (60, 66, 76, a))


# ---------------------------------------------------------------- scenes
def backdrop(cam, seed=1, sunpos=(0.78, 0.14), warm=1.0, cloudy=0.0):
    img = sky(cam, top=(126 - 18 * cloudy, 182 - 22 * cloudy, 226 - 18 * cloudy),
              bot=(238, 242, 242))
    sun_screen(img, fx=sunpos[0], fy=sunpos[1], r=0.072 + 0.012 * cloudy, warm=warm)
    skyline(img, cam, seed=seed, alpha=int(64 + 26 * cloudy))
    ground(img, cam)
    return img


def crowd(img, cam, n=4, alpha=54, rows=(1.05, 1.35)):
    """Bystanders, placed inside the visible width so they read as a crowd, not as furniture."""
    half = W * SS / (2 * cam.zoom)
    for row, dist in enumerate(rows):
        for i in range(n):
            k = (i + 0.5) / n
            x = (-1 + 2 * k) * (half * 1.02) * (1.0 if row == 0 else 0.86)
            x += 0.12 * (1 if row else -1)
            fig = dict(x=x, y=0.0, scale=0.52 - 0.05 * row, face=1 if x > 0 else -1,
                       col=(96, 108, 124, int(alpha * (1 - 0.35 * row))), w=S.LW * 0.86)
            draw_fig_bg(img, cam, fig)


def draw_fig_bg(img, cam, fig):
    d = S.draw_on(img)
    col = fig["col"]
    w = fig["w"] * cam.zoom
    p = pose()
    J = S.skeleton(fig, p)
    s = J["scale"]
    for a, b in ((J["hip"], J["kn_l"]), (J["kn_l"], J["ft_l"]), (J["hip"], J["kn_r"]),
                 (J["kn_r"], J["ft_r"]), (J["hip"], J["chest"]), (J["chest"], J["neck"]),
                 (J["sh_l"], J["el_l"]), (J["el_l"], J["hd_l"]), (J["sh_r"], J["el_r"]),
                 (J["el_r"], J["hd_r"])):
        d.line([cam.p(*a), cam.p(*b)], fill=col, width=int(max(2, w)))
    cx, cy = cam.p(*J["head"])
    rr = cam.z(0.135 * s)
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=col, width=int(max(2, w * 0.85)))
    return J


def s1(img, lt, dur):
    """Morning. He trains alone — and nobody knows why."""
    cam = cam_for(lerp(700, 770, ease(seg(0, dur, lt))), cx=0.06)
    base = backdrop(cam, seed=3, sunpos=(0.80, 0.115))
    img.alpha_composite(base)
    
    hero = dict(x=-0.25, y=0.62, scale=1.0, face=1)
    # three punches into the empty air, then breathing, then a slow guard reset
    combo = [1.15, 1.95, 2.75]
    p = fighter(lt, combo, guard=GUARD, wind=WIND, out=OUT)
    if lt < 0.9:
        p = mix(STAND, GUARD, ease(seg(0.15, 0.85, lt)))
    if lt > 3.55:
        p = mix(GUARD, BREATHE, ease(seg(3.55, 4.35, lt)))
    shadow(img, cam, S.skeleton(hero, p))
    J = draw_fig(img, cam, hero, p)

    d = S.draw_on(img)
    for i, te in enumerate(combo):
        ww, we = strike(lt, [te])
        if we > 0.05:
            hx, hy = J["hd_r"]
            speedlines(img, cam, hx, hy, math.radians(-8), 0.55 * we, a=int(110 * we), n=3)
    if abs(math.sin(lt * 3.1)) > 0.85:
        dust(img, cam, -0.25, 0.58, 0.20, a=10, n=2, seed=int(lt * 8))

    if lt < 1.4:
        k = eout(seg(0.15, 0.9, lt)) * (1 - eout(seg(1.0, 1.4, lt)) * 0.0)
        brand(img, k)
    caption(img, "মাঠে সে একা একা অনুশীলন করত। কেউ জানত না, কেন।", eout(seg(0.5, 1.1, lt)))
    return grade(img, tint=(252, 246, 232), amount=0.06, vignette=0.16)


def s2(img, lt, dur):
    """Flashback — last year, in front of everyone."""
    cam = cam_for(500, cx=-0.10)
    base = backdrop(cam, seed=9, sunpos=(0.20, 0.13), warm=0.55, cloudy=0.62)
    img.alpha_composite(base)
    crowd(img, cam, n=3, alpha=40, rows=(1.0,))

    hero = dict(x=0.15, y=0.58, scale=0.98, face=-1)
    big = dict(x=-1.05, y=0.52, scale=1.10, face=1, w=S.LW * 1.18)
    push_t = 1.75
    # big walks in, shoves once; hero falls back and stays down
    walk = step_cycle(lt, 0.8) if lt < push_t else STAND
    bp = mix(walk, mix(STAND, GUARD, ease(seg(1.0, 1.5, lt))), ease(seg(0.85, 1.2, lt)))
    if push_t - 0.3 <= lt <= push_t + 0.42:
        ww, we = strike(lt, [push_t + 0.02], prep=0.30, hit=0.06, tail=0.30)
        bp = mix(mix(GUARD, WIND, ww), OUT, we)
    hp = mix(STAND, GUARD, ease(seg(0.5, 1.2, lt)))
    if lt >= push_t + 0.10:
        hp = mix(GUARD, FALL, ease(seg(push_t + 0.10, push_t + 0.52, lt)))
    if lt >= push_t + 0.52:
        hp = mix(FALL, DOWN, ease(seg(push_t + 0.52, push_t + 0.95, lt)))
    if lt >= push_t + 1.5:
        hp = mix(DOWN, DOWN, 1.0)
    hp["hipdy"] = hp["hipdy"]
    shake = shove_shake(lt, push_t + 0.10, 0.09, 0.55)
    cam.sx, cam.sy = shake

    # redraw ground after camera shake would be wrong; keep the plate steady and shake only figures
    cam_f = Cam(cam.cx, cam.cy, cam.zoom, shake)
    shadow(img, cam_f, S.skeleton(hero, hp))
    shadow(img, cam_f, S.skeleton(big, bp))
    draw_fig(img, cam_f, big, bp)
    J = draw_fig(img, cam_f, hero, hp)

    if lt > push_t + 0.35:                      # he is on the floor: ground contact must read
        k = ease(seg(push_t + 0.35, push_t + 0.9, lt))
        gx, gy = cam.p(hero["x"] + 0.10, hero["y"] - 0.02)
        rx, ry = cam.z(0.55 * k), cam.z(0.075 * k)
        S.draw_on(img).ellipse([gx - rx, gy - ry, gx + rx, gy + ry], fill=(84, 78, 66, 70))
    if push_t + 0.1 < lt < push_t + 1.1:
        k = 1 - seg(push_t + 0.1, push_t + 1.1, lt)
        dust(img, cam, 0.55, 0.0, 0.5 * (0.5 + k), a=int(46 * k), n=8, seed=7)

    # flashback grade: colder, lower contrast, a soft frame vignette
    g = grade(img, tint=(214, 224, 236), amount=0.22, vignette=0.34)
    d = S.draw_on(g)
    d.rectangle([0, 0, W * SS, H * SS], outline=(46, 56, 70, 60), width=int(26 * SS))
    caption(g, "গত বছর রফিক তাকে সবার সামনে মাটিতে ফেলে দিয়েছিল।", eout(seg(0.4, 1.0, lt)))
    return g


def s3(img, lt, dur):
    """Training: not revenge — the slip."""
    cam = cam_for(545, cx=0.05)
    base = backdrop(cam, seed=5, sunpos=(0.84, 0.10))
    img.alpha_composite(base)

    # a swinging sandbag on a frame: the drill partner
    d = S.draw_on(img)
    d.line([cam.p(-0.95, -3.05), cam.p(1.30, -3.05)], fill=(120, 112, 98, 210), width=int(0.045 * cam.zoom))
    d.line([cam.p(-0.95, -3.05), cam.p(-0.95, 0.58)], fill=(120, 112, 98, 210), width=int(0.045 * cam.zoom))
    d.line([cam.p(1.30, -3.05), cam.p(1.30, 0.58)], fill=(120, 112, 98, 210), width=int(0.045 * cam.zoom))

    swing = math.sin(lt * 2.35) * 0.52
    bx = 0.68 + swing
    by = -3.05 + math.cos(swing * 0.9) * 2.05
    d.line([cam.p(0.68, -3.05), cam.p(0.68 + swing * 1.6, by)], fill=(96, 92, 84, 230), width=int(0.022 * cam.zoom))
    r = 0.30
    d.ellipse([cam.p(bx - r, by - r)[0], cam.p(bx - r, by - r)[1],
               cam.p(bx + r, by + r)[0], cam.p(bx + r, by + r)[1]],
              fill=(122, 96, 70, 235), outline=(70, 56, 44, 255), width=int(0.018 * cam.zoom))

    hero = dict(x=-0.62, y=0.58, scale=1.0, face=1)
    # the bag reaches him four times; each time he slips
    passes = [1.05, 1.95, 2.85, 3.75]
    p = GUARD
    near = min(passes, key=lambda e: abs(lt - e))
    k = clamp(1 - abs(lt - near) / 0.55)
    if k > 0:
        p = mix(GUARD, SLIP if int(near * 2) % 2 == 0 else WEAVE_R, ease(k))
    if lt > 4.35:
        p = mix(GUARD, BOW, ease(seg(4.35, 5.0, lt)))
    shadow(img, cam, S.skeleton(hero, p))
    draw_fig(img, cam, hero, p)

    # footwork marks left in the dust
    for i, x in enumerate((-0.95, -0.7, -0.45, -0.2)):
        a = 60 if i < 3 else 30
        d.line([cam.p(x, 0.02), cam.p(x + 0.18, 0.02)], fill=(150, 140, 122, a), width=int(0.02 * cam.zoom))
    dust(img, cam, 0.6, -1.3, 0.34, a=22, n=4, seed=11)

    caption(img, "সে প্রতিশোধের মহড়া করেনি। সে শিখেছিল, কীভাবে সরে যেতে হয়।",
            eout(seg(0.5, 1.1, lt)))
    return grade(img, tint=(252, 248, 236), amount=0.05, vignette=0.16)


def s4(img, lt, dur):
    """The rematch. First punch goes through air."""
    cam = cam_for(lerp(505, 470, ease(seg(0, dur, lt))), cx=0.10)
    base = backdrop(cam, seed=13, sunpos=(0.78, 0.12))
    img.alpha_composite(base)
    crowd(img, cam, n=3, alpha=38, rows=(1.0,))

    hero = dict(x=0.42, y=0.60, scale=1.0, face=-1)
    big = dict(x=-0.48, y=0.54, scale=1.12, face=1, w=S.LW * 1.16)

    te = 2.65
    bp = fighter(lt, [te], guard=GUARD, wind=WIND, out=OUT)
    if lt < 1.0:
        bp = mix(STAND, GUARD, ease(seg(0.2, 0.95, lt)))
    # the hero slips exactly when the fist arrives
    hp = GUARD
    if lt > te - 0.30:
        k = ease(seg(te - 0.30, te + 0.06, lt)) * (1 - ease(seg(te + 0.35, te + 0.95, lt)))
        hp = mix(GUARD, SLIP_L, k)
    if lt < 0.9:
        hp = mix(STAND, GUARD, ease(seg(0.15, 0.8, lt)))

    shadow(img, cam, S.skeleton(big, bp))
    shadow(img, cam, S.skeleton(hero, hp))
    Jb = draw_fig(img, cam, big, bp)
    Jh = draw_fig(img, cam, hero, hp)

    ww, we = strike(lt, [te])
    if we > 0.35:
        hx, hy = Jb["hd_r"]
        speedlines(img, cam, hx, hy, 0.0, 0.62 * we, a=int(140 * we), n=4)
        arc(img, cam, Jb["sh_r"][0], Jb["sh_r"][1], 0.55, -70, 20, col=ACCENT + (120,), w=0.02)
    if 0.5 < we < 1.0:
        # slow-motion dust at the miss
        dust(img, cam, 0.55, -1.15, 0.26, a=int(40 * we), n=4, seed=17)

    caption(img, "আবার সামনে এসে দাঁড়াল। রফিকের প্রথম ঘুষটা গেল বাতাসে।",
            eout(seg(0.6, 1.2, lt)))
    return grade(img, tint=(253, 247, 234), amount=0.05, vignette=0.16)


def s5(img, lt, dur):
    """Ten punches, three kicks, nothing lands — and Rafiq sits down in his own exhaustion."""
    cam = cam_for(480, cx=0.05)
    base = backdrop(cam, seed=21, sunpos=(0.82, 0.11))
    img.alpha_composite(base)
    crowd(img, cam, n=3, alpha=40, rows=(1.0,))

    hero = dict(x=0.44, y=0.60, scale=1.0, face=-1)
    big = dict(x=-0.50, y=0.54, scale=1.12, face=1, w=S.LW * 1.16)

    atk = [0.55, 1.15, 1.75, 2.35, 2.95, 3.55, 4.15]
    kicks = [4.75, 5.35]
    collapse = 5.85

    bp = fighter(lt, atk, guard=GUARD, wind=WIND, out=OUT)
    kw, ko = strike(lt, kicks, prep=0.30, hit=0.08, tail=0.32)
    if kw or ko:
        kp = mix(GUARD, KICK_W, kw)
        if ko:
            kp = mix(kp, KICK_OUT, ko)
        bp = kp
    # fatigue: the guard sags as the barrage goes on
    fat = ease(seg(0.4, 5.4, lt))
    bp = mix(bp, mix(bp, TIRED, 0.55), fat)
    if lt > collapse:
        bp = mix(mix(bp, KNEEL, ease(seg(collapse, collapse + 0.45, lt))),
                 SIT, ease(seg(collapse + 0.45, collapse + 0.95, lt)))

    dodges = [a + 0.02 for a in atk] + [k + 0.04 for k in kicks]
    hp = GUARD
    near = min(dodges, key=lambda e: abs(lt - e)) if dodges else 0
    kk = clamp(1 - abs(lt - near) / 0.42)
    if kk > 0:
        alt = (SLIP if int(near * 3) % 3 == 0 else DUCK if int(near * 3) % 3 == 1 else WEAVE_R)
        hp = mix(GUARD, alt, ease(kk))
    # he keeps his hands up and never throws one
    hp = mix(hp, mix(hp, GUARD_L, 0.5), ease(seg(0.3, 1.2, lt)))

    shake = (0.0, 0.0)
    if lt > collapse:
        shake = shove_shake(lt, collapse + 0.9, 0.05, 0.5)
    camf = Cam(cam.cx, cam.cy, cam.zoom, shake)
    shadow(img, cam, S.skeleton(big, bp))
    shadow(img, cam, S.skeleton(hero, hp))
    Jb = draw_fig(img, camf, big, bp)
    Jh = draw_fig(img, camf, hero, hp)

    for te in atk + kicks:
        _, we = strike(lt, [te])
        if we > 0.55:
            hx, hy = Jb["hd_r"] if te in atk else Jb["ft_r"]
            speedlines(img, cam, hx, hy, -0.2, 0.55 * we, a=int(90 * we), n=2)
    if lt > collapse + 0.85:
        dust(img, cam, -0.72, 0.0, 0.55, a=int(50 * ease(seg(collapse + 0.85, collapse + 1.5, lt))),
             n=9, seed=23)

    caption(img, "দশটা ঘুষ, তিনটা লাথি। একটাও গায়ে লাগল না।", eout(seg(0.5, 1.1, lt)))
    return grade(img, tint=(253, 246, 232), amount=0.05, vignette=0.17)


def s6(img, lt, dur):
    """A hand offered — and the fight turns out to have been Rafiq's own."""
    cam = cam_for(lerp(520, 470, ease(seg(0, dur, lt))), cx=-0.25)
    base = backdrop(cam, seed=27, sunpos=(0.70, 0.10), warm=1.25)
    img.alpha_composite(base)

    walk = eout(seg(0.35, 1.55, lt))
    hero = dict(x=lerp(-0.05, -0.78, walk), y=0.60, scale=1.0, face=1)
    big = dict(x=-1.52, y=0.54, scale=1.10, face=1, w=S.LW * 1.14)

    # he walks to Rafiq, offers the hand at 1.5 s, Rafiq takes it at 2.4 s, both stand at 3.3 s
    hp = mix(step_cycle(lt, 0.7), REACH, ease(seg(1.15, 1.75, lt)))
    hp = mix(hp, mix(REACH, STAND, ease(seg(3.05, 3.6, lt))), 0.0)
    if lt > 2.3:
        hp = mix(hp, mix(REACH, pose(lean=6, b1=52, b2=-10, a1=-14, a2=12), ease(seg(2.3, 2.9, lt))), 1.0)
    if lt > 3.3:
        hp = mix(hp, STAND, ease(seg(3.3, 3.9, lt)))

    bp = mix(SIT, KNEEL, ease(seg(1.2, 2.0, lt)))
    bp = mix(bp, TAKE, ease(seg(2.25, 2.85, lt)))
    if lt > 3.35:
        bp = mix(bp, mix(TIRED, STAND, ease(seg(3.35, 4.1, lt))), 1.0)
    bp["hipdy"] *= (1 - ease(seg(3.35, 4.2, lt)))

    shadow(img, cam, S.skeleton(big, bp))
    shadow(img, cam, S.skeleton(hero, hp))
    draw_fig(img, cam, big, bp)
    Jh = draw_fig(img, cam, hero, hp)

    if 1.4 < lt < 3.2:
        # a soft light between the two hands
        k = math.sin(clamp(seg(1.4, 3.2, lt)) * math.pi)
        gx, gy = cam.p((Jh["hd_r"][0] - 0.03), Jh["hd_r"][1])
        d = S.draw_on(img)
        rr = cam.z(0.22 + 0.06 * k)
        d.ellipse([gx - rr, gy - rr, gx + rr, gy + rr], fill=(255, 244, 214, int(70 * k)))

    caption(img, "লড়াইটা আসলে রফিকের নিজের সঙ্গে ছিল।", eout(seg(0.5, 1.1, lt)))
    return grade(img, tint=(255, 246, 226), amount=0.10, vignette=0.15)


def s7(img, lt, dur):
    """Lesson card — paper, ink, one line."""
    img.alpha_composite(Image.new("RGBA", img.size, (247, 244, 236, 255)))
    d = S.draw_on(img)
    cx = W * SS / 2
    # faint grid
    for x in range(0, int(W * SS), int(64 * SS)):
        d.line([(x, 0), (x, H * SS)], fill=(76, 90, 105, 9), width=1)
    for y in range(0, int(H * SS), int(64 * SS)):
        d.line([(0, y), (W * SS, y)], fill=(76, 90, 105, 9), width=1)

    k1 = eout(seg(0.15, 0.75, lt))
    k2 = eout(seg(0.6, 1.3, lt))
    k3 = eout(seg(1.2, 1.9, lt))
    k4 = eout(seg(2.2, 2.9, lt))

    bengali(img, (W / 2, 220), "অন্ধকার পাঠ · ০৩", int(34 * SS), 700, (96, 100, 108), shadow=None)
    en(img, (W / 2, 286), "L E S S O N   0 3", int(20 * SS), (128, 132, 138, int(230 * k1)))

    # the hand-drawn line, in the order the viewer needs it
    if k2 > 0.02:
        bengali(img, (W / 2, 640), "যে লড়াই শুধু জেতার জন্য,", int(50 * SS), 700, (28, 30, 36), shadow=None)
    if k3 > 0.02:
        bengali(img, (W / 2, 760), "তার প্রথম শত্রু", int(50 * SS), 700, (28, 30, 36), shadow=None)
        bengali(img, (W / 2, 910), "নিজের রাগ।", int(74 * SS), 700, (176, 62, 40), shadow=None)
        d.line([(int(W / 2 - 175 * SS), 1000 * SS),
                (int(W / 2 - 175 * SS + 350 * SS * k3), 1000 * SS)],
               fill=(176, 62, 40, int(215 * k3)), width=int(5 * SS))

    if k4 > 0.02:
        bengali(img, (W / 2, 1180), "কেউ তোমাকে চ্যালেঞ্জ করলে —", int(36 * SS), 500, (74, 78, 86),
                shadow=None)
        bengali(img, (W / 2, 1262), "প্রথমে নিজের রাগটাকে হারাও।", int(36 * SS), 600, (40, 44, 52),
                shadow=None)
        d.line([(int(W / 2 - 120 * SS), 1352 * SS), (int(W / 2 + 120 * SS), 1352 * SS)],
               fill=(60, 64, 72, int(70 * k4)), width=int(2 * SS))
        bengali(img, (W / 2, 1444), "ফলো করো · প্রতি শুক্রবার নতুন পাঠ", int(32 * SS), 600,
                (146, 92, 58), shadow=None)

    # a tiny walker in the corner keeps the frame alive
    fig = dict(x=-1.75 + 3.5 * ((lt * 0.42) % 1.0), y=0.62, scale=0.30, face=1, col=(72, 76, 84))
    cam = Cam(0.0, 0.10, 300)
    draw_fig(img, cam, fig, step_cycle(lt, 0.7))

    return grade(img, tint=(252, 246, 232), amount=0.04, vignette=0.10)


SCENES = [s1, s2, s3, s4, s5, s6, s7]


# ---------------------------------------------------------------- draw(t)
def scene_at(t):
    i = 0
    for k in range(len(BOUNDS) - 1):
        if t >= BOUNDS[k]:
            i = k
    lo, hi = BOUNDS[i], BOUNDS[i + 1]
    return i, max(0.0, t - lo), max(0.001, hi - lo)


def draw(t):
    i, lt, dur = scene_at(t)
    S.ink_reset()
    S.ui_reset()
    img = Image.new("RGBA", (int(W * SS), int(H * SS)), (0, 0, 0, 255))
    img = SCENES[i](img, lt, dur)
    return S.down(img)


# ---------------------------------------------------------------- audio
def build_sfx():
    """Procedural fight sound: whooshes, impacts, scuffs, footsteps, wind bed."""
    os.makedirs("audio/sfx", exist_ok=True)
    sr = 44100
    rng = np.random.default_rng(5)

    def write(name, sig):
        s = np.clip(sig / max(1e-6, np.abs(sig).max()) * 0.7, -1, 1)
        import wave
        with wave.open("audio/sfx/%s.wav" % name, "wb") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
            f.writeframes((s * 32000).astype("<i2").tobytes())

    def bp(x, lo, hi):
        X = np.fft.rfft(x)
        fr = np.fft.rfftfreq(len(x), 1 / sr)
        m = (fr >= lo) & (fr <= hi)
        X = X * m
        return np.fft.irfft(X, len(x))

    # whoosh: band-passed noise, fast rise, slow fall
    n = int(0.34 * sr)
    wsig = bp(rng.normal(0, 1, n), 600, 3200)
    env = np.linspace(0, 1, n) ** 0.5 * np.exp(-np.linspace(0, 4.2, n))
    write("whoosh", wsig * env)

    # impact: low sine thump + noise click
    n = int(0.28 * sr)
    tt = np.arange(n) / sr
    thump = np.sin(2 * math.pi * 78 * tt) * np.exp(-tt * 24)
    click = bp(rng.normal(0, 1, n), 900, 5200) * np.exp(-tt * 55)
    write("impact", thump * 0.9 + click * 0.5)

    # soft body fall
    n = int(0.5 * sr)
    tt = np.arange(n) / sr
    write("fall", np.sin(2 * math.pi * 60 * tt) * np.exp(-tt * 12) * 0.9 +
          bp(rng.normal(0, 1, n), 200, 1400) * np.exp(-tt * 9) * 0.5)

    # scuff / step in dust
    n = int(0.14 * sr)
    tt = np.arange(n) / sr
    write("scuff", bp(rng.normal(0, 1, n), 1200, 6500) * np.exp(-tt * 40))

    # breathing
    n = int(1.2 * sr)
    tt = np.arange(n) / sr
    write("breath", bp(rng.normal(0, 1, n), 300, 1600) * np.sin(np.pi * tt / 1.2) ** 2 * 0.5)

    # wind bed, 46 s
    n = int(TOTAL * sr)
    tt = np.arange(n) / sr
    wind = bp(rng.normal(0, 1, n), 90, 900)
    lfo = 0.55 + 0.45 * np.sin(2 * math.pi * 0.06 * tt)
    write("wind", wind * lfo * 0.35)


def mix_audio():
    build_sfx()
    sr = 44100
    total_n = int((TOTAL + 0.5) * sr)
    bed = np.zeros(total_n, dtype=np.float32)

    import wave
    def load(name):
        with wave.open("audio/sfx/%s.wav" % name, "rb") as f:
            a = np.frombuffer(f.readframes(f.getnframes()), "<i2").astype(np.float32) / 32000
        return a

    def place(name, t0, gain=1.0):
        a = load(name) * gain
        i = int(t0 * sr)
        j = min(total_n, i + len(a))
        if 0 <= i < total_n:
            bed[i:j] += a[: j - i]

    place("wind", 0.0, 0.30)
    # whooshes / scuffs / impacts, timed to the beats drawn in the scenes
    for t0 in (NAR[0] + 1.15, NAR[0] + 1.95, NAR[0] + 2.75):
        place("whoosh", t0 - 0.06, 0.45)
    place("fall", NAR[1] + 1.85, 0.55)
    place("impact", NAR[1] + 1.86, 0.35)
    place("scuff", NAR[1] + 2.30, 0.40)
    for t0 in (NAR[2] + 1.05, NAR[2] + 1.95, NAR[2] + 2.85, NAR[2] + 3.75):
        place("whoosh", t0 - 0.02, 0.34)
        place("scuff", t0 + 0.18, 0.30)
    place("whoosh", NAR[3] + 2.61, 0.55)
    for a in (0.55, 1.15, 1.75, 2.35, 2.95, 3.55, 4.15):
        place("whoosh", NAR[4] + a - 0.05, 0.42)
    for a in (4.75, 5.35):
        place("whoosh", NAR[4] + a - 0.05, 0.50)
    place("fall", NAR[4] + 5.85 + 0.75, 0.50)
    place("breath", NAR[4] + 6.2, 0.30)

    # voice
    import subprocess as sp
    mix = [p for p in AUD]
    from PIL import Image  # noqa: F401  (keep import cost out of the audio path)

    # decode voice to raw via ffmpeg, then sum in numpy
    for p, start in zip(mix, NAR):
        raw = sp.run([FFMPEG, "-loglevel", "error", "-i", p, "-f", "s16le", "-ac", "1",
                      "-ar", str(sr), "-"], capture_output=True).stdout
        a = np.frombuffer(raw, "<i2").astype(np.float32) / 32000
        i = int(start * sr)
        j = min(total_n, i + len(a))
        if 0 <= i < total_n:
            bed[i:j] += a[: j - i] * 1.15

    bed = np.clip(bed, -1, 1)
    st = np.stack([bed, bed], axis=1)
    import wave
    os.makedirs("audio", exist_ok=True)
    with wave.open("audio/mix.wav", "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes((st * 32000).astype("<i2").tobytes())
    print("mix ok", os.path.getsize("audio/mix.wav"))


# ---------------------------------------------------------------- cli
def pose_sheet():
    names = [("STAND", STAND), ("GUARD", GUARD), ("WIND", WIND), ("OUT", OUT), ("SLIP", SLIP),
             ("DUCK", DUCK), ("KICK_W", KICK_W), ("KICK_OUT", KICK_OUT), ("FALL", FALL),
             ("DOWN", DOWN), ("KNEEL", KNEEL), ("SIT", SIT), ("REACH", REACH), ("TIRED", TIRED)]
    cw, ch = 270, 480
    sheet = Image.new("RGB", (cw * 7, ch * 2), (238, 236, 228))
    for i, (nm, p) in enumerate(names):
        im = Image.new("RGBA", (int(W * SS), int(H * SS)), (240, 238, 230, 255))
        cam = Cam(0.0, -1.15, 470)
        ground(im, cam)
        draw_fig(im, cam, dict(x=0.0, y=0.0, scale=1.0, face=1), p)
        tile = S.down(im).resize((cw, ch), Image.LANCZOS)
        d = ImageDraw.Draw(tile)
        d.text((8, 8), nm, font=ImageFont.truetype(FONT_EN_B, 20), fill=(20, 20, 24))
        sheet.paste(tile, ((i % 7) * cw, (i // 7) * ch))
    sheet.save("frames/pose-sheet.png")
    print("frames/pose-sheet.png")


def main():
    if "--poses" in sys.argv:
        os.makedirs("frames", exist_ok=True)
        pose_sheet(); return
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1])
        os.makedirs("frames", exist_ok=True)
        draw(t).save("frames/still-%05.2f.png" % t)
        print("still", t); return

    print("timeline", NAR, "end", END_AT, "total", TOTAL, "frames", NF, flush=True)

    if "--mix" in sys.argv:
        mix_audio(); return

    if "--seg" in sys.argv:
        j = sys.argv.index("--seg")
        a, b = int(sys.argv[j + 1]), int(sys.argv[j + 2])
        sp = sys.argv[j + 3]
        cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "19",
               "-pix_fmt", "yuv420p", sp]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(a, b):
            proc.stdin.write(draw(i / FPS).tobytes())
            if (i - a) % 60 == 0:
                print("  seg %d/%d" % (i - a, b - a), flush=True)
        proc.stdin.close(); proc.wait()
        print("segdone", sp, os.path.getsize(sp), flush=True)
        return

    if "--join" in sys.argv:
        segs = sys.argv[sys.argv.index("--join") + 1:]
        with open("segs.txt", "w") as f:
            for sp in segs:
                f.write("file '%s'\n" % os.path.abspath(sp))
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", "segs.txt", "-i", "audio/mix.wav", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                        "-shortest", "stickman-fight-1080x1920.mp4"], check=True)
        print("joined", os.path.getsize("stickman-fight-1080x1920.mp4"))
        return

    print("nothing to do — pass --still/--poses/--mix/--seg/--join")


if __name__ == "__main__":
    main()
