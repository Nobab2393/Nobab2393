#!/usr/bin/env python3
"""
2D + 2.5D demo — 12 s, 1080x1920, 30 fps.

Act 1  0.0-3.4   the 2D principles: anticipation, stretch, arc, impact squash, spring settle
Act 2  3.4-4.8   the layer split: FAR / MID / FG pulled apart on Y, then back together
Act 3  4.8-10.0  one dolly-in at three speeds (parallax: far 1.05, mid 1.09, fg 1.14)
Act 4  10.0-12.0 stat chips (waterfall entry) + closing caption

Every frame is a pure function of t. Renderer: PIL @2x supersample -> ffmpeg.
"""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

S = 2
W, H = 1080, 1920
WP, HP = W * S, H * S
FPS = 30
DUR = 12.0
N = int(FPS * DUR)

CREAM = (240, 238, 230)
INK = (25, 25, 25)
GREY = (188, 183, 172)
META = (118, 113, 103)
CORAL = (217, 119, 87)          # the one reserved accent
SKY = (243, 222, 196)
FAR = (201, 164, 136)
MID = (140, 107, 82)
FG = (62, 44, 34)
FGD = (40, 27, 20)

FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
if not os.path.exists(FFMPEG):
    FFMPEG = "ffmpeg"

for b, r in [("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]:
    if os.path.exists(b):
        BOLD, REG = b, r
        break

_f = {}
def font(px, bold=True):
    k = (px, bold)
    if k not in _f:
        _f[k] = ImageFont.truetype(BOLD if bold else REG, int(px * S))
    return _f[k]


# ---------------- easing ----------------
def cl(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v

def seg(t0, t1, t):
    return cl((t - t0) / (t1 - t0))

def eio(t):
    t = cl(t); return 3 * t * t - 2 * t * t * t

def eout(t, p=4):
    t = cl(t); return 1 - (1 - t) ** p

def ein(t, p=3):
    t = cl(t); return t ** p

def spr(t, freq=2.0, damp=6.0):
    t = cl(t); return 1 - math.exp(-damp * t) * math.cos(2 * math.pi * freq * t)


# ---------------- canvas helpers ----------------
def txt(d, xy, s, px, fill, bold=True, anchor="mm"):
    d.text((xy[0] * S, xy[1] * S), s, font=font(px, bold), fill=fill, anchor=anchor)

def chip(img, cx, cy, label, fill=INK, fg=CREAM, px=34, padx=26, pady=16):
    d = ImageDraw.Draw(img)
    f = font(px)
    bb = d.textbbox((0, 0), label, font=f)
    w, h = (bb[2] - bb[0]) / S + padx * 2, (bb[3] - bb[1]) / S + pady * 2
    d.rounded_rectangle([(cx - w / 2) * S, (cy - h / 2) * S, (cx + w / 2) * S, (cy + h / 2) * S],
                        radius=h / 2 * S, fill=fill)
    d.text((cx * S, cy * S), label, font=f, fill=fg, anchor="mm")
    return w


# ---------------- 2D act: the ball ----------------
def ball_state(t):
    """Returns (x, y, sx, sy) for the ball centre and its squash."""
    ground = 1408
    r = 92

    if t < 0.55:                                    # anticipation: sink + squash
        p = eio(seg(0.0, 0.55, t))
        return 380, ground + 40 * p, 1 + 0.25 * p, 1 - 0.25 * p

    if t < 0.80:                                    # launch: stretch along the path
        p = seg(0.55, 0.80, t)
        return 380 + 24 * p, (ground + 40) - 90 * p, 1.25 - 0.45 * eout(p), 0.75 + 0.55 * eout(p)

    if t < 1.72:                                    # rise: decelerating, arc to the right
        p = seg(0.80, 1.72, t)
        y = 1318 - 620 * eout(p)
        x = 404 + 226 * p + 26 * math.sin(math.pi * p)      # the arc's bow
        return x, y, 0.86, 1.24

    if t < 1.92:                                    # apex: a moving hold, never frozen
        p = seg(1.72, 1.92, t)
        y = 698 - 10 * math.sin(math.pi * p)
        return 630 + 6 * p, y, 1.0 + 0.02 * math.sin(math.pi * p), 1.0

    if t < 2.62:                                    # fall: accelerating (gravity)
        p = seg(1.92, 2.62, t)
        y = 698 + 710 * ein(p, 2)
        x = 636 + 124 * p
        return x, y, 0.90, 1.18

    p = seg(2.62, 3.40, t)                          # impact + spring settle
    k = (1 - spr(p * 1.15)) * (1 - p)               # damped follow-through, dies out
    return 760, ground + 30 * (1 - spr(p * 1.15)), 1 + 0.30 * k, 1 - 0.30 * k


def draw_act1(img, t):
    d = ImageDraw.Draw(img)
    # ground: dot-grid paper, one hairline rule
    for gy in range(60, H, 60):
        for gx in range(60, W, 60):
            d.ellipse([(gx - 3) * S, (gy - 3) * S, (gx + 3) * S, (gy + 3) * S], fill=(229, 226, 216))
    d.rectangle([90 * S, 1500 * S, 990 * S, 1504 * S], fill=GREY)

    x, y, sx, sy = ball_state(t)
    r = 92
    # contact shadow: smaller and fainter when the ball is high
    lift = cl((1500 - y) / 800.0)
    sw = r * (1.35 - 0.7 * lift)
    d.ellipse([(x - sw) * S, 1470 * S, (x + sw) * S, 1502 * S], fill=(214, 209, 198))

    rx, ry = r * sx, r * sy
    d.ellipse([(x - rx) * S, (y - ry) * S, (x + rx) * S, (y + ry) * S], fill=CORAL)

    # caption, set once, then held with a breath (never frozen)
    if t > 0.45:
        br = 1.5 * math.sin(t * 2.1)
        txt(d, (540, 1700 + br), "SQUASH · STRETCH · FOLLOW-THROUGH", 44, INK)
        txt(d, (540, 1780), "the ball is one shape and one accent", 34, META, bold=False)


# ---------------- 2.5D act: the multiplane landscape ----------------
PLANES = [("FAR", 0.10), ("MID", 0.18), ("FG", 0.29)]


def proj(x, y, w, s, panx, off_y):
    return ((540 + (x - 540) * s + panx * 6 * w) * S,
            (960 + (y - 960) * s + 0.35 * panx * 6 * w + off_y) * S)


def draw_landscape(img, t):
    """Layers, each transformed by its own depth weight."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, WP, HP], fill=SKY)

    split = 0.0
    dolly = ease = 0.0
    panx = 0.0
    if 3.40 <= t < 4.80:                              # act 2: show the split
        up = eout(seg(3.42, 3.78, t), 4)
        down = 1 - eio(seg(4.32, 4.78, t))
        split = up * down
    if t >= 4.85:                                     # act 3: one dolly-in
        ease = eio(seg(4.95, 9.95, t))
        dolly = 0.5 * ease
        panx = 40 * ease

    def lay(w, y_shift):
        return 1 + dolly * w, panx, y_shift

    # --- far plane: sun + distant range
    s, px, oy = lay(0.10, -120 * split)
    d.ellipse([((540 + (720 - 540) - 150) * S), ((960 + (640 - 960) * s + oy) - 150 * s) * S,
               ((540 + 180 + 150) * S), ((960 + (640 - 960) * s + oy) + 150 * s) * S], fill=CORAL)
    far_pts = []
    for i, x in enumerate(range(-460, 1520, 20)):
        y = 980 + 90 * math.sin(i * 0.42) + 55 * math.sin(i * 1.31) + 40 * math.cos(i * 0.17)
        far_pts.append(proj(x, y, 0.10, s, px, oy))
    far_pts += [proj(1520, 1500, 0.10, s, px, oy), proj(-460, 1500, 0.10, s, px, oy)]
    d.polygon(far_pts, fill=FAR)

    # --- mid plane: ridge + small pines
    s, px, oy = lay(0.18, 0)
    mid_pts = []
    for i, x in enumerate(range(-460, 1520, 20)):
        y = 1180 + 46 * math.sin(i * 0.23 + 1.2) + 26 * math.sin(i * 0.61)
        mid_pts.append(proj(x, y, 0.18, s, px, oy))
    mid_pts += [proj(1520, 1700, 0.18, s, px, oy), proj(-460, 1700, 0.18, s, px, oy)]
    d.polygon(mid_pts, fill=MID)
    for i, x in enumerate(range(-320, 1420, 62)):
        h = 54 + 26 * ((i * 7) % 5) / 4
        xi = (x + 460) / 20.0          # same index math as the ridge polygon, so trees sit on it
        base = 1180 + 46 * math.sin(xi * 0.23 + 1.2) + 26 * math.sin(xi * 0.61)
        for tri, sc in ((0, 1.0),):
            p1 = proj(x, base - h, 0.18, s, px, oy)
            p2 = proj(x - h * 0.34, base, 0.18, s, px, oy)
            p3 = proj(x + h * 0.34, base, 0.18, s, px, oy)
            d.polygon([p1, p2, p3], fill=(112, 84, 64))

    # --- foreground: ground mass, rocks, two big pines
    s, px, oy = lay(0.29, 120 * split)
    fg_pts = []
    for i, x in enumerate(range(-460, 1520, 24)):
        y = 1450 + 26 * math.sin(i * 0.19 + 0.4) + 16 * math.sin(i * 0.53)
        fg_pts.append(proj(x, y, 0.29, s, px, oy))
    fg_pts += [proj(1520, 2200, 0.29, s, px, oy), proj(-460, 2200, 0.29, s, px, oy)]
    d.polygon(fg_pts, fill=FG)
    for (bx, bh, bw) in ((150, 470, 150), (1010, 400, 132)):
        for k in range(3):
            yy = 1470 - bh * (0.30 + 0.24 * k)
            ww = bw * (1.0 - 0.22 * k) / 2
            d.polygon([proj(bx, 1470 - bh * (0.72 + 0.14 * k), 0.29, s, px, oy),
                       proj(bx - ww, yy, 0.29, s, px, oy),
                       proj(bx + ww, yy, 0.29, s, px, oy)], fill=FGD)


def draw_act2_overlay(img, t):
    """FAR / MID / FG chips that name the planes while they are apart."""
    if not (3.55 <= t < 4.70):
        return
    a = cl((t - 3.55) / 0.25) * (1 - cl((t - 4.45) / 0.25))
    if a <= 0.02:
        return
    layer = Image.new("RGBA", (WP, HP), (0, 0, 0, 0))
    for i, (name, _) in enumerate(PLANES):
        y = 640 + i * 430
        chip(layer, 190, y, name, fill=INK + (int(255 * a),), fg=CREAM + (int(255 * a),))
    img.paste(layer, (0, 0), layer)


def draw_act4(img, t):
    if t < 10.0:
        return
    # waterfall entry: from below, staggered, power4.out, binary opacity
    items = [("3 LAYERS", 10.05), ("1 CAMERA", 10.16), ("10% PUSH", 10.27)]
    for i, (label, t0) in enumerate(items):
        if t < t0:
            continue
        p = eout(seg(t0, t0 + 0.20, t), 4)
        y = 1470 + (1 - p) * 70
        chip(img, 540 + (i - 1) * 300, y, label, fill=INK, fg=CREAM, px=30)
    if t >= 10.55:
        p = eout(seg(10.55, 10.85, t), 4)
        d = ImageDraw.Draw(img)
        d.rectangle([0, (1660 + (1 - p) * 40) * S, WP, (1830 + (1 - p) * 40) * S], fill=CREAM)
        txt(d, (540, 1710 + (1 - p) * 40), "ONE CAMERA · THREE DEPTHS", 52, INK)
        txt(d, (540, 1790 + (1 - p) * 40), "2D principles + a multiplane rig", 32, META, bold=False)


# ---------------- film ----------------
def render(t):
    img = Image.new("RGB", (WP, HP), CREAM)
    if t < 3.40:
        draw_act1(img, t)
    else:
        draw_landscape(img, t)
        draw_act2_overlay(img, t)
        draw_act4(img, t)
    return img.resize((W, H), Image.LANCZOS)


def main():
    os.makedirs("frames", exist_ok=True)
    out = "2d-2point5d-demo-1080x1920.mp4"
    cmd = [FFMPEG, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    marks = (0, 45, 80, 112, 130, 200, 290, 350)
    for i in range(N):
        t = i / FPS
        fr = render(t)
        p.stdin.write(fr.tobytes())
        if i in marks:
            fr.save("frames/f%03d.png" % i)
        if i % 60 == 0:
            print("  %d/%d  t=%.2fs" % (i, N, t), flush=True)
    p.stdin.close()
    p.wait()
    print("done:", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
