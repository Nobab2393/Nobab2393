#!/usr/bin/env python3
"""অন্ধকার পাঠ ০২ · শোধ (THE DEBT) — a 3D-anime style dark lesson in Bangla, 1080x1920.

    python3 film.py --still 12.0        one frame
    python3 film.py --mix               build audio/mix.wav
    python3 film.py --seg A B out.mp4   render a frame range to a silent segment
    python3 film.py --join s1.mp4 ...   concat segments + mux the voice-over
    python3 film.py                     full render

One idea carries the whole film: a single glowing thread. It is born the moment he gives the
coat away, it thickens for every year he keeps the receipt, and it snaps the moment he gives
something without counting. Everything else — snow, brick, the coat's one warm colour — is
there to make that thread the only bright thing on screen.
"""
import math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import cel3d as C
import bg2
import cast
import deva
from cel3d import Cam, place, render_model, T, S, R

W, H = 1080, 1920
SS = 1.2
FPS = 24
TTF = "/usr/local/lib/python3.11/dist-packages/matplotlib/mpl-data/fonts/ttf/"
F_INK = (8, 7, 10)
CREAM = (242, 236, 220)
COLD = (150, 200, 255)
THREAD_COL = (128, 216, 255)
EMBER_TXT = (247, 168, 96)
GOLD_TXT = (240, 196, 128)

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG = "ffmpeg"

AUD = ["audio/v%d.mp3" % i for i in range(1, 8)]


def probe(path):
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", err)
    if not m:
        return 8.0
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


LEAD, GAP, TAIL = 1.10, 0.40, 4.40
if all(os.path.exists(p) for p in AUD):
    DUR = [probe(p) for p in AUD]
else:
    DUR = [8.0] * 7
NAR = [LEAD]
for d in DUR[:-1]:
    NAR.append(round(NAR[-1] + d + GAP, 3))
END_AT = round(NAR[-1] + DUR[-1] + 0.7, 3)
TOTAL = round(END_AT + TAIL, 3)
BOUNDS = [0.0] + [round(n - 0.34, 3) for n in NAR[1:]] + [round(END_AT - 0.30, 3)]
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


def compose_3d(img, cams, models, glow_models=()):
    for model, cam in zip(models, cams):
        is_glow = model in glow_models if isinstance(glow_models, (list, tuple)) else False
        tile, pos = C.render_model_tiled(model, cam, ss=SS, outline=F_INK, glow=is_glow, outline_px=6)
        img.alpha_composite(tile, pos)


def cam_at(eye, target, fov):
    c = Cam(eye=eye, target=target, fov=fov, w=W, h=H)
    c._fov = fov
    return c


def floor_y(cam, z=1.5):
    p = cam.project(cam.to_view(np.array([0.0, 0.0, z])))[0]
    return int(min(H - 1, max(10, p[1])))


def stage(img, cam, z=1.7, seed=3):
    y0 = floor_y(cam, z)
    bg2.wall(img, y0, seed=seed)
    bg2.floor(img, y0, col=(15, 15, 20), deep=(7, 7, 10))
    return y0


# ---- the thread: a 2D filament, drawn twice (a soft halo, then a crisp core)
def bez(p0, p1, sag=0.0, n=26, wave=0.0, phase=0.0):
    pts = []
    for i in range(n):
        k = i / (n - 1.0)
        x = lerp(p0[0], p1[0], k)
        y = lerp(p0[1], p1[1], k) + math.sin(k * math.pi) * sag
        if wave:
            y += math.sin(k * math.pi * 3 + phase) * wave * math.sin(k * math.pi)
        pts.append((x, y))
    return pts


def coil(cx, cy, rx, ry, turns=2.2, phase=0.0, n=40):
    pts = []
    for i in range(n):
        k = i / (n - 1.0)
        a = phase + k * turns * math.tau
        pts.append((cx + math.cos(a) * rx, cy + math.sin(a) * ry - k * 8))
    return pts


def draw_thread(img, pts, w=3, alpha=180, glow=1.0, col=THREAD_COL):
    if len(pts) < 2:
        return
    k = 2
    lay = Image.new("RGBA", (W // k, H // k), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.line([(x / k, y / k) for x, y in pts], fill=col + (int(alpha * 0.8),),
           width=max(2, int(w * 1.6 / k * 6)), joint="curve")
    halo = lay.filter(ImageFilter.GaussianBlur(9 * glow)).resize((W, H), Image.BILINEAR)
    img.alpha_composite(halo)
    d2 = ImageDraw.Draw(img)
    d2.line(pts, fill=col + (min(255, int(alpha + 50)),), width=w, joint="curve")
    d2.line(pts, fill=(235, 250, 255, min(255, int(alpha + 60))), width=max(1, w - 2), joint="curve")


def proj(cam, x, y, z):
    p = cam.project(cam.to_view(np.array([float(x), float(y), float(z)])))[0]
    return (int(p[0]), int(p[1]))


def caption(img, y, text, size=38, col=CREAM, weight=600):
    deva.draw_text(img, (540, y), text, size, weight, col, shadow=(0, 0, 0), shadow_blur=16)


# ---------------------------------------------------------------- scenes
def s1(img, lt, dur):
    """Winter alley. He gives the coat away — and keeps the receipt."""
    cam = cam_at((0.55, 1.12, 6.0), (0.0, 1.00, 0.30), 34)
    stage(img, cam, 1.9, seed=3)
    bg2.frost(img, 0.35)

    give = eio(seg(2.3, 3.7, lt))
    ayan = place(cast.ayan(t=lt, walk=0.0, arm=0.55 - 0.15 * give, candle=0.0,
                           slump=0.75 - 0.25 * give, look=0.35), T(-0.62 + 0.10 * give, 0, 0.55))
    fr = place(cast.passer(t=lt, hood=1.0, warm=0.0, look=-0.3, shrug=0.25 * (1 - give)),
               T(0.55 + 0.06 * give, 0, 0.35) @ S(0.98))
    co = place(cast.coat(t=lt, fold=lerp(1.0, 0.55, give)),
               T(lerp(-0.74, -0.14, give), lerp(0.84, 0.94, give), lerp(0.64, 0.72, give))
               @ R("y", -22 * give) @ S(lerp(0.50, 0.56, give)))
    compose_3d(img, [cam] * 3, [ayan, fr, co])
    bg2.snow(img, lt, 110, seed=4)

    bg2.pool(img, 520, 1420, 320, col=(96, 150, 220), a=30, blur=120)
    if give > 0.02:                                   # the thread is born with the gift
        p0 = proj(cam, lerp(-0.34, 0.42, give), 0.95, 0.62)
        p1 = proj(cam, lerp(0.34, -0.30, give), 0.92, 0.60)
        draw_thread(img, bez(p0, p1, sag=40 + 30 * math.sin(lt * 2.0), wave=4), w=2,
                    alpha=int(150 * give))

    k = eout(seg(0.3, 1.2, lt))
    if k > 0.02:
        deva.draw_text(img, (540, 300), "অন্ধকার পাঠ", int(64 * k + 6), 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=18)
        d = ImageDraw.Draw(img)
        d.text((540, 366), "D A R K   L E S S O N   ·   0 2", font=ImageFont.truetype(TTF + "DejaVuSans.ttf", 24),
               fill=(150, 148, 144, int(230 * k)), anchor="mm")
        d.line([(400, 420), (680, 420)], fill=(120, 130, 160, int(150 * k)), width=2)
    if lt > 4.4:
        caption(img, 1772, "শীতে কাঁপতে থাকা বন্ধুকে সে চাদরটা দিল", 36)
    bg2.grade(img, tint=(232, 240, 255))


def s2(img, lt, dur):
    """Years later. The coat is gone; the sentence stayed."""
    cam = cam_at((0.55, 1.18, 6.2), (0.0, 1.05, 0.25), 34)
    stage(img, cam, 2.0, seed=5)
    bg2.frost(img, 0.5)

    walk = eio(seg(0.4, 3.4, lt))
    ayan = place(cast.ayan(t=lt, walk=0.0, arm=0.0, candle=0.0, slump=0.9, look=0.5),
                 T(-0.78, 0, 0.55))
    fr = place(cast.passer(t=lt, hood=0.0, warm=1.0, walk=walk,
                           look=-0.6 * walk, turn=0.35 * walk),
               T(lerp(-0.20, 0.95, walk), 0, lerp(0.15, -0.15, walk)) @ S(0.98))
    compose_3d(img, [cam] * 2, [ayan, fr])
    bg2.snow(img, lt, 130, seed=6, wind=0.5)

    # the thread has thickened: it now runs from his wrist to the man walking away
    p0 = proj(cam, -0.56, 0.86, 0.52)
    p1 = proj(cam, lerp(-0.20, 0.95, walk), 0.90, lerp(0.15, -0.15, walk))
    draw_thread(img, bez(p0, p1, sag=90 + 14 * math.sin(lt * 3.0), wave=6), w=3, alpha=200)

    if lt > 4.2:
        caption(img, 1772, "বছর পেরোল, কথা রইল", 38)
    bg2.grade(img, tint=(226, 236, 255))


def s3(img, lt, dur):
    """The sentence gets heavier, one day at a time."""
    cam = cam_at((0.40, 1.18, 4.5), (0.0, 1.05, 0.15), 32)
    stage(img, cam, 1.7, seed=7)
    bg2.frost(img, 0.55)

    ayan = place(cast.ayan(t=lt, walk=0.0, arm=0.25, candle=0.0, slump=1.0,
                           look=-0.15, blink=1.0 - eout(seg(0.2, 0.8, lt))), T(0.05, 0, 0.45))
    compose_3d(img, [cam], [ayan])
    bg2.snow(img, lt, 90, seed=8, alpha=110)

    # the thread curls around his forearm, then his neck
    ax, ay = proj(cam, 0.28, 0.86, 0.50)
    nx, ny = proj(cam, 0.05, 1.20, 0.46)
    arm = coil(ax, ay, 62, 22, turns=2.6, phase=lt * 0.7)
    neck = coil(nx, ny, 78, 26, turns=1.5, phase=-lt * 0.5 + 1.0)
    draw_thread(img, arm, w=3, alpha=210)
    draw_thread(img, neck, w=3, alpha=190)
    bg2.glow(img, nx, ny + 90, 190, col=(90, 170, 255), a=26, blur=90)

    if lt > 3.0:
        caption(img, 1772, "প্রতিদিন কথাটা একটু ভারী হলো", 36)
    bg2.grade(img, tint=(224, 234, 255))


def s4(img, lt, dur):
    """He asks for it back. He gets a goodbye."""
    cam = cam_at((0.50, 1.15, 6.1), (0.0, 1.05, 0.25), 34)
    stage(img, cam, 1.9, seed=9)
    bg2.frost(img, 0.45)

    ask = eio(seg(0.5, 1.8, lt))
    no = eio(seg(3.2, 4.4, lt))
    ayan = place(cast.ayan(t=lt, walk=0.0, arm=0.75 * ask, candle=0.0, slump=0.5,
                           look=0.6 - 0.3 * no), T(-0.70, 0, 0.55))
    fr = place(cast.passer(t=lt, hood=0.0, warm=1.0, turn=0.9 * no, shrug=no,
                           look=-0.2 - 0.5 * no), T(0.52, 0, 0.30) @ S(0.98))
    compose_3d(img, [cam] * 2, [ayan, fr])
    bg2.snow(img, lt, 120, seed=10)

    # taut: the thread is a straight, vibrating line between them, then it whips away
    taut = 1.0 - 0.6 * no
    p0 = proj(cam, -0.34, 0.98, 0.60)
    p1 = proj(cam, lerp(0.42, 0.62, no), lerp(0.95, 1.10, no), 0.34)
    draw_thread(img, bez(p0, p1, sag=lerp(90, 8, taut), wave=lerp(6, 16, no), phase=lt * 9), w=3,
                alpha=210)
    if no > 0.4:
        bg2.glow(img, 700, 1120, 150, col=(90, 170, 255), a=int(30 * no), blur=80)

    if lt > 4.6:
        caption(img, 1772, "ফেরত চাইলে বন্ধুত্ব শেষ", 38, EMBER_TXT, 700)
    bg2.grade(img, tint=(228, 236, 255))


def s5(img, lt, dur):
    """The lesson, said plainly."""
    cam = cam_at((0.30, 1.15, 6.4), (0.0, 1.00, 0.25), 33)
    stage(img, cam, 2.2, seed=11)
    bg2.frost(img, 0.4)

    ayan = place(cast.ayan(t=lt, walk=0.0, arm=0.0, candle=0.0, slump=0.95, look=0.1),
                 T(0.10, 0, 0.55) @ S(0.95))
    compose_3d(img, [cam], [ayan])
    bg2.snow(img, lt, 80, seed=12, alpha=95)

    # the thread hangs slack, still glowing — the debt outlives the friendship
    pts = bez(proj(cam, 0.30, 0.80, 0.55), proj(cam, 0.85, 0.02, 0.80), sag=90, wave=5, phase=lt * 1.5)
    draw_thread(img, pts, w=2, alpha=140)

    k = eout(seg(0.6, 1.7, lt))
    if k > 0.03:
        deva.draw_text(img, (540, 470), "যে দান ফেরত চায়", int(54 * k + 6), 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=18)
        deva.draw_text(img, (540, 566), "সেটা দান নয় — ঋণ", int(54 * k + 6), 700, THREAD_COL,
                       shadow=(0, 0, 0), shadow_blur=18)
    if lt > 2.6:
        caption(img, 1772, "আর ঋণের সুদ সবচেয়ে চড়া", 36, GOLD_TXT, 600)
    bg2.grade(img, tint=(230, 238, 255))


def s6(img, lt, dur):
    """The correction: give again, and keep no receipt. The thread goes."""
    cam = cam_at((0.45, 1.12, 5.9), (0.0, 1.02, 0.28), 34)
    stage(img, cam, 1.9, seed=13)
    bg2.frost(img, 0.30)

    give = eio(seg(0.8, 2.4, lt))
    snap = eout(seg(4.4, 5.2, lt))
    ayan = place(cast.ayan(t=lt, walk=0.0, arm=0.45 - 0.10 * give, candle=0.0,
                           slump=lerp(0.7, 0.25, give), look=0.3), T(-0.55 + 0.08 * give, 0, 0.55))
    str_ = place(cast.passer(t=lt, hood=1.0, warm=0.0, shrug=0.35 * (1 - give), look=-0.4),
                 T(0.58, 0, 0.32) @ S(0.96))
    co = place(cast.coat(t=lt, fold=lerp(1.0, 0.6, give)),
               T(lerp(-0.66, -0.10, give), lerp(0.86, 0.94, give), lerp(0.64, 0.72, give))
               @ R("y", 16 * give) @ S(lerp(0.50, 0.56, give)))
    compose_3d(img, [cam] * 3, [ayan, str_, co])
    bg2.snow(img, lt, 115, seed=14)

    # the thread: slack, then breaking into drifting pieces
    p0 = proj(cam, -0.30, 0.92, 0.62)
    p1 = proj(cam, 0.44, 0.90, 0.60)
    if snap < 0.98:
        pts = bez(p0, p1, sag=110 + 10 * math.sin(lt * 2.4), wave=5)
        draw_thread(img, pts[: max(2, int(len(pts) * (1 - snap)))], w=2,
                    alpha=int(150 * (1 - snap)))
    else:
        for i in range(7):
            ph = (lt * 0.5 + i * 0.17) % 1.0
            cx = p0[0] + 30 + i * 42 + 14 * math.sin(lt * 1.7 + i)
            cy = p0[1] + 20 + ph * 420
            draw_thread(img, [(cx, cy), (cx + 16, cy + 10)], w=2, alpha=int(120 * (1 - ph)))

    if give > 0.3:
        bg2.pool(img, 560, 1300, 300, col=(255, 190, 120), a=int(26 * give), blur=120)
    if lt > 5.2:
        caption(img, 1772, "এইবার সে কোনো হিসাব রাখল না", 36, GOLD_TXT, 600)
    bg2.grade(img, tint=(246, 240, 232))


_CTA_TILE = None
_CTA_QT = -1.0


def s7(img, lt, dur):
    """The card."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(9, 9, 13))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(lay)
    gd.ellipse([110, 720, 970, 1300], fill=(255, 168, 92, 30))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(120)))

    k1 = eout(seg(0.10, 0.75, lt))
    k2 = eout(seg(0.50, 1.15, lt))
    k3 = eout(seg(0.90, 1.60, lt))
    k4 = eout(seg(1.35, 2.00, lt))

    if k1 > 0.03:
        deva.draw_text(img, (540, 280), "অন্ধকার পাঠ · ০২", 42, 700, (196, 190, 182),
                       shadow=(0, 0, 0), shadow_blur=14)
        deva.draw_text(img, (540, 462), "কাকে কিছু দিয়ে", int(58 * k1 + 8), 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=18)
        deva.draw_text(img, (540, 562), "ফেরত চেয়েছ?", int(58 * k1 + 8), 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=18)
    if k2 > 0.03:
        deva.draw_text(img, (540, 682), "দান যেখানে হিসাব রাখে, বন্ধুত্ব সেখানে মরে।", 33, 500,
                       COLD, shadow=(0, 0, 0), shadow_blur=12)
    if k3 > 0.03:
        deva.draw_text(img, (540, 892), "কমেন্ট করো: একটা নাম", 44, 700, EMBER_TXT,
                       shadow=(0, 0, 0), shadow_blur=14)
        pw = 600 * k3
        d.rounded_rectangle([540 - pw / 2, 1004, 540 + pw / 2, 1140], 36, fill=(247, 172, 92))
        if k3 > 0.85:
            deva.draw_text(img, (540, 1072), "ফলো করো", 48, 700, (16, 12, 11))
    if k4 > 0.03:
        deva.draw_text(img, (540, 1230), "প্রতি শুক্রবার · নতুন পাঠ", 34, 500, (188, 182, 176))
        d.line([(340, 1290), (340 + 400 * k4, 1290)], fill=(247, 172, 92, 200), width=3)

    qt = round(lt * 4) / 4.0
    global _CTA_TILE, _CTA_QT
    if _CTA_TILE is None or _CTA_QT != qt:
        cam = cam_at((0.45, 1.10, 3.9), (0.0, 0.95, 0.15), 34)
        ayan = place(cast.ayan(t=qt, walk=0.0, arm=0.55, candle=0.0), T(-0.18, 0, 0))
        co = place(cast.coat(t=qt), T(0.22, 0.92, 0.34) @ S(0.58))
        img2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        compose_3d(img2, [cam, cam], [ayan, co])
        bbox = img2.getbbox()
        tile = img2.crop(bbox) if bbox else img2
        scale = min(430 / max(1, tile.width), 560 / max(1, tile.height))
        tile = tile.resize((int(tile.width * scale), int(tile.height * scale)), Image.LANCZOS)
        _CTA_TILE, _CTA_QT = tile, qt
    img.alpha_composite(_CTA_TILE, (int(W / 2 - _CTA_TILE.width / 2),
                                    max(1320, 1888 - _CTA_TILE.height)))
    bg2.pool(img, 540, 1710, 250, col=(255, 180, 104), a=34, blur=110)


SCENES = [s1, s2, s3, s4, s5, s6, s7]


def draw(t):
    img = Image.new("RGBA", (W, H), (9, 9, 12, 255))
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
        out = draw(t)
        path = "frames/still-%05.2f.png" % t
        out.save(path)
        print("still", path)
        return

    print("timeline", NAR, "end", END_AT, "total", TOTAL, "frames", NF, flush=True)

    if "--seg" in sys.argv:
        j = sys.argv.index("--seg")
        aandb = int(sys.argv[j + 1]), int(sys.argv[j + 2])
        sp = sys.argv[j + 3]
        cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-pix_fmt", "yuv420p", sp]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(aandb[0], aandb[1]):
            proc.stdin.write(draw(i / FPS).tobytes())
            if (i - aandb[0]) % 60 == 0:
                print("  seg %d/%d" % (i - aandb[0], aandb[1] - aandb[0]), flush=True)
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
                        "-t", "%.3f" % TOTAL, "audio/mix.wav"], check=True)
        print("mix ok", os.path.getsize("audio/mix.wav"))
        return

    if "--join" in sys.argv:
        segs = sys.argv[sys.argv.index("--join") + 1:]
        with open("segs.txt", "w") as f:
            for sp in segs:
                f.write("file '%s'\n" % os.path.abspath(sp))
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", "segs.txt", "-i", "audio/mix.wav", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                        "dark-lesson-02-1080x1920.mp4"], check=True)
        print("joined -> dark-lesson-02-1080x1920.mp4", os.path.getsize("dark-lesson-02-1080x1920.mp4"))
        return

    out = "dark-lesson-02-1080x1920.mp4"
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-i", "audio/mix.wav",
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(NF):
        proc.stdin.write(draw(i / FPS).tobytes())
        if i % 300 == 0:
            print("  %d/%d" % (i, NF), flush=True)
    proc.stdin.close()
    proc.wait()
    print("done", out, os.path.getsize(out))


if __name__ == "__main__":
    main()
