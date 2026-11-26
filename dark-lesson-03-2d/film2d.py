"""film2d.py — অন্ধকার পাঠ ০৩ · দুপুর, in the Claude animation style.

Flat vector motion graphics, built to the grammar in
`../ai-video-skills/library/.claude/skills/claude-animation-style/SKILL.md`:

  · warm paper ground #F0EEE6, ink #191919, ONE accent #D97757 (Ayan — the thing that matters),
    a single cool counterweight #6A9BCC (Mira, used exactly once in the film)
  · no gradients, no pure black, no pure white, outlines only where a shape needs an edge
  · every entrance is ease_out_back (overshoot, settles inside 12 frames), groups stagger 3 frames
  · scene changes are carried by an element that grows until it becomes the next ground
  · type is architecture: a giant ০৩, captions of 1–4 words, static, inside the safe area
  · every frame is a pure function of t
"""
import math
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

import deva
import flat
import rig2d
from flat import eio, eout, lerp, mix, seg, W, H

FPS = 30
VO_DIR = os.environ.get("VO_DIR", "audio")      # VO_DIR=audio-v15 to re-voice
MIX = os.path.join(VO_DIR, "mix.wav")
OUT = os.environ.get("OUT", "dark-lesson-03-2d-1080x1920.mp4")
AUD = os.path.join(VO_DIR, "v%d.mp3")
NAR_HARD = [0.90, 7.07, 14.19, 20.61, 29.66, 37.93, 44.54]
GAP_AFTER = 0.45        # breath between lines
TAIL = 4.5              # room after the last word for the CTA card


def _probe_dur(path):
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        exe = "ffmpeg"
    try:
        out = subprocess.run([exe, "-i", path], capture_output=True, text=True).stderr
    except Exception:
        return None
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if not m:
        return None
    h, mi, sec = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(sec)


def _timings():
    """Line starts follow the takes themselves, so a new voice-over stays in sync."""
    durs = [_probe_dur(AUD % (k)) for k in range(1, 8)]
    if any(d is None for d in durs):
        return list(NAR_HARD), 56.1
    nar = [NAR_HARD[0]]
    for d in durs[:-1]:
        nar.append(round(nar[-1] + d + GAP_AFTER, 3))
    total = round(nar[-1] + durs[-1] + TAIL, 3)
    return nar, total


def _bounds(nar, total):
    """Scene cuts sit a third of a second before the next line, like the original cut."""
    return [0.0] + [round(n - 0.32, 3) for n in nar[1:]] + [round(total - TAIL + 0.34, 3)]


NAR, TOTAL = _timings()
BOUNDS = _bounds(NAR, TOTAL)
NF = int(round(TOTAL * FPS))

# ---- palette -----------------------------------------------------------------------
GROUND = (240, 238, 230)      # #F0EEE6
CARD = (250, 249, 245)        # #FAF9F5
INK = (25, 25, 25)            # #191919
META = (92, 90, 85)           # #5C5A55
ACCENT = (217, 119, 87)       # #D97757
ACCENT_D = (189, 93, 58)      # #BD5D3A
COOL = (106, 155, 204)        # #6A9BCC — once
SHADE = (222, 219, 209)       # a flat plane of shadow, never an alpha

SAFE = (60, 250, 1020, 1600)  # 9:16 safe area for Instagram / TikTok


# ---- motion ------------------------------------------------------------------------
def back(t, s=1.70158):                 # cubic-bezier(0.34, 1.56, 0.64, 1)
    t = min(max(t, 0.0), 1.0) - 1.0
    return t * t * ((s + 1) * t + s) + 1.0


def snap(t):
    t = min(max(t, 0.0), 1.0)
    return 3 * t * t - 2 * t * t * t


def expo(t):
    t = min(max(t, 0.0), 1.0)
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)


def f(t0, t1, t):                        # local progress, in seconds
    return 0.0 if t <= t0 else 1.0 if t >= t1 else (t - t0) / (t1 - t0)


def frame(t0, t):                         # n frames later, at 30 fps
    return f(t0, t0 + 12 / FPS, t)


# ---- drawing helpers ---------------------------------------------------------------
def ground(cv, y, col, band=None):
    cv.rect([0, 0, W, y], GROUND)
    cv.rect([0, y, W, H], col)
    if band:
        cv.rect([0, y, W, y + band[1]], band[0])


def sun(cv, x, y, r, col=(214, 210, 198)):
    cv.circle(x, y, r, col)


def shadow(cv, x, gy, h, lean=-1.15, w=0.34, col=SHADE):
    """A flat plane of shadow lying on the ground — one tone for everyone, so two of them
    running into each other become one shape. That is the argument of the film."""
    rx = abs(lean) * h * 0.52
    cx = x + lean * h * 0.32
    cv.ellipse(cx, gy + 2, rx + w * h * 0.26, 0.075 * h, col)


def figure(cv, h, gy, x, pose=None, mono=INK, eye=None, flip=False, props=()):
    cv.mirror = x if flip else None
    rig2d.draw(cv, {}, h, gy, x, pose=pose or {}, mono=mono, eye=eye, props=props)
    cv.mirror = None


def card(cv, x, y, s, rot=0.0, col=INK):
    ca, sa = math.cos(rot), math.sin(rot)

    def T(px, py):
        return (x + px * ca - py * sa, y + px * sa + py * ca)
    cv.poly([T(-s, -s * 0.26), T(s, -s * 0.26), T(s, s * 0.26), T(-s, s * 0.26)], col)


def bag(cv, x, y, s, rot=0.0, col=ACCENT):
    ca, sa = math.cos(rot), math.sin(rot)

    def T(px, py):
        return (x + px * ca - py * sa, y + px * sa + py * ca)
    cv.poly([T(-s, -s * 0.60), T(s * 0.95, -s * 0.64), T(s * 1.04, s * 0.70),
             T(-s * 0.90, s * 0.74)], col)


# ---- type --------------------------------------------------------------------------
def meta(cv, txt, xy, size=26, col=META, anchor="mm"):
    cv.text(xy, txt, size, 600, col, anchor=anchor)


def caption(cv, y, txt, size=72, k=1.0, col=INK, cx=540):
    """Captions are drawn whole, never letter by letter, and they never move on their own."""
    if k <= 0.02:
        return
    cv.text((cx, y), txt, size, 800, col)


# ---------------------------------------------------------------- scenes
def s1(cv, lt, dur):
    """Noon. He walks in. Somebody is already standing in the way."""
    ground(cv, 1040, (233, 230, 220), band=(INK, 3))
    sun(cv, 830, 700, 92)

    g = back(f(0.05, 0.55, lt))                      # the giant number arrives first
    if g > 0.01:
        cv.text((330, 700), "০৩", int(430 * (0.72 + 0.28 * g)), 800, mix(GROUND, INK, 0.92))
    meta(cv, "অন্ধকার পাঠ", (SAFE[0], 300), 28, META, anchor="lm")
    meta(cv, "১ / ৭", (SAFE[2], 300), 28, META, anchor="rm")

    gy = 1500
    crowd = [(150, 1180, 300, 0), (930, 1180, 306, 3), (1030, 1260, 322, 6)]
    for i, (cx, gy2, hh, st) in enumerate(crowd):
        k = expo(f(0.10 + st / FPS, 0.50 + st / FPS, lt))
        if k < 0.02:
            continue
        yy = gy2 + (1 - k) * 80
        shadow(cv, cx, yy, hh, col=mix(GROUND, INK, 0.10))
        figure(cv, hh, yy, cx, pose=dict(walk=(0.15 + 0.2 * i) % 1.0), mono=mix(INK, GROUND, 0.55),
               eye=GROUND)

    kw = f(0.35, 1.05, lt)
    if kw > 0.01:
        wx = lerp(-180, 405, back(kw, 1.2))
        shadow(cv, wx, gy, 330)
        figure(cv, 330, gy, wx, pose=dict(walk=lt * 1.5, blink=0.0), mono=ACCENT, eye=GROUND,
           props=("bag",))

    kr = f(0.9, 1.4, lt)
    if kr > 0.01:
        ry = gy + (1 - back(kr)) * -60
        shadow(cv, 800, ry, 384)
        figure(cv, 384, ry, 800, pose=dict(walk=0.0, head=-3), mono=INK, eye=GROUND)

    caption(cv, 440, "দুপুরের রোদে সব পরিষ্কার", 76, expo(f(2.4, 2.9, lt)))
    return (ACCENT, (405, gy - 120))


def s2(cv, lt, dur):
    """The bag goes down. The books go everywhere."""
    ground(cv, 980, CARD, band=(INK, 3))
    meta(cv, "২ / ৭", (SAFE[2], 300), 30, META)

    gy = 1500
    reach = snap(f(1.4, 2.4, lt))
    fly = snap(f(0.85, 1.25, lt))
    land = snap(f(1.25, 1.45, lt))

    figure(cv, 660, gy, 800, pose=dict(walk=0.0, head=-8), mono=INK, eye=CARD, flip=True)
    shadow(cv, 800, gy, 660, lean=1.15)

    if fly < 0.995:
        by = lerp(gy - 210, gy - 40, fly * fly)
        bag(cv, lerp(300, 560, snap(f(0.3, 0.8, lt))) if fly <= 0 else lerp(560, 545, fly), by, 74,
            0.1 + 1.8 * fly)
    if land > 0.02:
        bag(cv, 548, gy - 30, 76, 0.25)
        cv.line([(430, gy - 18), (690, gy - 10)], mix(CARD, INK, 0.25), 6.0, caps=False)

    for i in range(5):
        k = snap(f(0.9 + i * 0.04, 1.45 + i * 0.04, lt))
        if k <= 0.02:
            continue
        x = lerp(560, 660 + i * 54 - 24 * (i % 2), k)
        y = lerp(gy - 90, gy - 14 + 8 * (i % 3), k) - 110 * math.sin(k * math.pi)
        card(cv, x, y, 40, (1 - k) * 2.4 + i * 0.3, col=mix(INK, GROUND, 0.15 * i))

    shadow(cv, 330, gy + 10, 650)
    figure(cv, 650, gy + 10, 330, pose=dict(walk=0.0, reach=0.35 + 0.5 * reach, head=4),
           mono=ACCENT, eye=CARD, props=("bag",))

    caption(cv, 400, "ব্যাগটা মাটিতে পড়ল", 76, expo(f(2.1, 2.6, lt)))
    return (ACCENT, (500, gy - 40))


def s3(cv, lt, dur):
    """The ring. Everyone has their own shadow. Nobody's touches anybody's."""
    ground(cv, 1000, (233, 230, 220), band=(INK, 3))
    meta(cv, "৩ / ৭", (SAFE[2], 300), 30, META)

    gy = 1400
    ring = [(120, 1276, 350), (300, 1210, 330), (770, 1200, 332), (930, 1276, 354),
            (1010, 1196, 324)]
    for i, (cx, yy, hh) in enumerate(ring):
        k = expo(f(0.05 + 3 * i / FPS, 0.45 + 3 * i / FPS, lt))
        if k < 0.02:
            continue
        yo = yy + (1 - k) * 60
        shadow(cv, cx, yo, hh, col=mix(GROUND, INK, 0.10))
        figure(cv, hh, yo, cx, pose=dict(walk=0.0, head=-6), mono=mix(INK, GROUND, 0.55),
               eye=GROUND, flip=cx > 540)

    shadow(cv, 520, gy, 420)
    figure(cv, 420, gy, 520, pose=dict(kneel=0.9, reach=0.4, head=6), mono=ACCENT, eye=GROUND,
           props=("bag",))
    for i in range(4):
        card(cv, 610 + i * 44, gy - 14 + 8 * (i % 2), 30, i * 0.5, col=INK)

    caption(cv, 400, "সবাই দেখছিল, কেউ এগোল না", 62, expo(f(1.5, 2.0, lt)))
    return (ACCENT, (520, gy - 220))


def s4(cv, lt, dur):
    """They leave. He picks his books up. His own shadow comes at him."""
    ground(cv, 980, (232, 229, 219), band=(INK, 3))
    meta(cv, "৪ / ৭", (SAFE[2], 300), 30, META)

    gy = 1780
    go = snap(f(0.2, 1.6, lt))
    if go < 0.99:
        x = lerp(760, 1180, go)
        shadow(cv, x, gy, 560, col=mix(GROUND, INK, 0.10))
        figure(cv, 760, gy, x, pose=dict(walk=lt * 1.4), mono=INK, eye=GROUND)

    down = snap(f(0.5, 1.4, lt))
    shadow(cv, 400, gy, 760, w=0.5, lean=-1.4)
    figure(cv, 760, gy, 400, pose=dict(kneel=0.95 * down, reach=0.35 + 0.55 * down,
                                       head=5 * down), mono=ACCENT, eye=GROUND, props=("bag",))
    for i in range(4):
        k = snap(f(1.2 + i * 0.05, 1.6 + i * 0.05, lt))
        if k < 0.5:
            continue
        card(cv, 566 + i * 78, gy - 12 + 8 * (i % 2), 38, -0.2 + i * 0.24, col=INK)

    caption(cv, 400, "সে কিছু বলল না", 76, expo(f(2.6, 3.1, lt)))
    return (ACCENT, (400, gy - 60))


def s5(cv, lt, dur):
    """One girl walks out of the ring. Two shadows become one shape."""
    ground(cv, 980, CARD, band=(INK, 3))
    meta(cv, "৫ / ৭", (SAFE[2], 300), 30, META)

    gy = 1780
    come = snap(f(0.15, 1.7, lt))
    kneel = snap(f(1.5, 2.3, lt))
    give = snap(f(2.6, 3.4, lt))
    mx = lerp(1240, 790, come)

    # his shadow, then hers — same tone, no gap: the merge is the argument
    shadow(cv, 400, gy, 760, w=0.52, lean=-1.4)
    shadow(cv, mx, gy, 760 - 330 * kneel, w=0.42, lean=-1.4)
    figure(cv, 760, gy, 400, pose=dict(kneel=0.95, reach=0.5 + 0.35 * give, head=4),
           mono=ACCENT, eye=CARD, props=("bag",))
    figure(cv, 770, gy, mx, pose=dict(walk=(lt * 1.7) % 1.0 * (1 - come), kneel=0.9 * kneel,
                                      reach=0.7 * give, head=3), mono=COOL, eye=CARD, flip=True,
           props=("hood", "scarf"))

    if give > 0.05:
        bx = lerp(mx - 90, 470, give)
        by = lerp(gy - 250, gy - 120, give) - 50 * math.sin(give * math.pi)
        card(cv, bx, by, 44, 0.6 - give * 1.1, col=COOL)

    caption(cv, 400, "একজন এগিয়ে এল", 76, expo(f(2.8, 3.3, lt)))
    return (COOL, (mx - 40, gy - 60))


def s6(cv, lt, dur):
    """The field again. Two people leaving, one long shadow."""
    w = snap(fast := f(0.0, dur, lt))
    ground(cv, 1000 - 40 * w, (236, 233, 223), band=(INK, 3))
    meta(cv, "৬ / ৭", (SAFE[2], 300), 30, META)

    gy = 1400
    go = snap(f(0.3, 4.6, lt))
    x = lerp(640, 250, go)
    h = lerp(380, 300, go)
    yy = gy + 40 * go
    shadow(cv, x + 60, yy, h * 1.3, lean=-1.75, w=0.9)
    figure(cv, h, yy, x, pose=dict(walk=lt * 1.5), mono=ACCENT, eye=GROUND, flip=True,
           props=("bag",))
    figure(cv, h * 0.96, yy + 4, x + 92, pose=dict(walk=lt * 1.5 + 0.4), mono=COOL,
           eye=GROUND, flip=True, props=("hood", "scarf"))

    k = expo(f(1.0, 1.7, lt))
    if k > 0.02:
        cv.text((540, 380), "অন্ধকার আলোর অভাব নয়", 70, 800, mix(GROUND, INK, k))
        cv.text((540, 500), "যেখানে সবাই দেখেও দেখে না", 70, 800, mix(GROUND, ACCENT_D, k))
    return (ACCENT, (540, 900))


def s7(cv, lt, dur):
    """The endcard: paper, ink, one coral button. Daylight, not black."""
    cv.rect([0, 0, W, H], CARD)
    cv.circle(540, 250, 300, GROUND)

    k1 = expo(f(0.05, 0.45, lt))
    k2 = expo(f(0.30, 0.70, lt))
    k3 = expo(f(0.55, 0.95, lt))
    k4 = expo(f(0.85, 1.30, lt))
    k5 = expo(f(1.15, 1.55, lt))

    meta(cv, "অন্ধকার পাঠ · ০৩", (540, 470), 34, META)
    cv.text((540, 590), "তুমি দেখেছিলে —", 78, 800, mix(CARD, INK, k1))
    cv.text((540, 700), "তারপর কী করলে?", 82, 800, mix(CARD, ACCENT_D, k2))
    cv.text((540, 830), "দেখে চুপ থাকাটাও একটা বেছে নেওয়া।", 40, 600, mix(CARD, META, k3))

    if k4 > 0.02:
        cv.text((540, 1010), "কমেন্ট করো: কী করেছিলে?", 50, 800, mix(CARD, ACCENT_D, k4))
        pw = 500 * back(k4, 1.2)
        cv.rect([540 - pw / 2, 1080, 540 + pw / 2, 1210], ACCENT, None, 0, r=30)
        if k4 > 0.93:
            cv.text((540, 1145), "ফলো করো", 54, 800, CARD)
    if k5 > 0.02:
        cv.text((540, 1310), "প্রতি শুক্রবার · নতুন পাঠ", 40, 600, mix(CARD, META, k5))

    kv = expo(f(1.3, 1.9, lt))
    if kv > 0.02:
        y = 1720 + (1 - kv) * 90
        figure(cv, 300, y, 470, pose=dict(walk=0.0), mono=ACCENT, eye=CARD, props=("bag",))
        figure(cv, 272, y, 610, pose=dict(walk=0.0), mono=COOL, eye=CARD,
               props=("hood", "scarf"))
    return None


SCENES = [s1, s2, s3, s4, s5, s6, s7]
# each cut is carried by an element that grows into the next ground
CARRY = [None,
         dict(col=CARD, at=(548, 1330), t0=0.18, t1=1.05),      # the bag
         dict(col=(233, 230, 220), at=(520, 1180), t0=0.16, t1=1.00),   # a shadow
         dict(col=(232, 229, 219), at=(400, 1410), t0=0.16, t1=1.00),   # the boy
         dict(col=CARD, at=(690, 1410), t0=0.16, t1=1.00),      # the book
         dict(col=(236, 233, 223), at=(600, 1300), t0=0.18, t1=1.05),   # the long shadow
         dict(col=CARD, at=(540, 1210), t0=0.20, t1=1.10)]      # the button


def _scene(i, lt):
    cv = flat.Canvas()
    ret = SCENES[i](cv, lt, BOUNDS[i + 1] - BOUNDS[i])
    crop = None
    if i == 5:                                    # the one slow move of the piece
        z = 1.0 + 0.055 * snap(f(0, BOUNDS[6] - BOUNDS[5], lt))
        crop = (540 - 540 / z, 960 - 960 / z, 540 + 540 / z, 960 + 960 / z)
    return cv.finish(card=(i == 6), crop=crop), ret


def draw(t):
    i = 0
    for k in range(len(BOUNDS) - 1):
        if t >= BOUNDS[k]:
            i = k
    if i > 0:
        tr = CARRY[i]
        k = f(BOUNDS[i] - tr["t0"], BOUNDS[i] + tr["t1"], t)
        if 0.0 < k < 1.0:
            prev, _ = _scene(i - 1, min(t, BOUNDS[i]) - BOUNDS[i - 1])
            nxt, _ = _scene(i, max(0.0, t - BOUNDS[i]))
            r = expo(k) * 2300
            cx, cy = tr["at"]
            mask = Image.new("L", (W, H), 0)
            ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
            out = Image.composite(nxt, prev, mask)
            return out
    img, _ = _scene(i, t - BOUNDS[i])
    return img


FFMPEG = None


def ffmpeg():
    global FFMPEG
    if FFMPEG is None:
        import imageio_ffmpeg
        FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    return FFMPEG


def main():
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1])
        os.makedirs("frames", exist_ok=True)
        draw(t).save("frames/still-%05.2f.png" % t)
        print("still", t)
        return

    out = OUT
    print("timeline", NAR, "total", TOTAL, "frames", NF, flush=True)

    if "--mix" in sys.argv:
        inputs, filt, labels = [], [], []
        for k, start in enumerate(NAR):
            inputs += ["-i", AUD % (k + 1)]
            ms = int(round(start * 1000))
            filt.append("[%d:a]adelay=%d|%d[a%d]" % (k, ms, ms, k))
            labels.append("[a%d]" % k)
        fc = ";".join(filt) + ";" + "".join(labels) + "amix=inputs=7:normalize=0,apad[a]"
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error"] + inputs +
                       ["-filter_complex", fc, "-map", "[a]", "-ar", "44100", "-ac", "2",
                        "-t", "%.3f" % TOTAL, MIX], check=True)
        print("mix ok")
        return

    if "--seg" in sys.argv:
        j = sys.argv.index("--seg")
        a, b, sp = int(sys.argv[j + 1]), int(sys.argv[j + 2]), sys.argv[j + 3]
        cmd = [ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", sp]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(a, b):
            proc.stdin.write(draw(i / FPS).tobytes())
            if (i - a) % 90 == 0:
                print("  seg %d/%d" % (i - a, b - a), flush=True)
        proc.stdin.close()
        proc.wait()
        print("segdone", sp, os.path.getsize(sp), flush=True)
        return

    if "--join" in sys.argv:
        segs = sys.argv[sys.argv.index("--join") + 1:]
        with open("segs.txt", "w") as fh:
            for sp in segs:
                fh.write("file '%s'\n" % os.path.abspath(sp))
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", "segs.txt", "-i", MIX, "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "144k", "-movflags", "+faststart", out], check=True)
        print("joined", os.path.getsize(out))
        return


if __name__ == "__main__":
    main()
