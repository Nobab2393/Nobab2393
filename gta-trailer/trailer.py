"""trailer.py — GRAND THEFT AUTO: VICE CITY, a 50 s flat-vector trailer.

Every frame is a pure function of t. Seven beats, hard cuts, one neon accent family.
"""
import math
import os
import subprocess
import sys

import numpy as np

import craft
import night
from craft import (W, H, BG, CITY, CITY2, CREAM, MUTED, PINK, PINK_D, CYAN, AMBER, VIOLET,
                   Canvas, back, expo, seg, snap, lerp, mix)

FPS = 30
DUR = 50.0
NF = int(DUR * FPS)

BEATS = [0.0, 3.2, 8.0, 13.0, 15.0, 23.0, 33.0, 41.0, 50.0]   # 8 scenes


def cap(cv, y, s, size, k=1.0, col=CREAM, track=0.16, glow=None, alpha=1.0):
    if k <= 0.02:
        return
    yy = y + (1 - k) * 26
    if glow:
        cv.glow_text((W / 2, yy), s, size, col, glow, track, k=k * alpha)
    else:
        cv.text((W / 2, yy), s, size, col, track, alpha=k * alpha)


def kick_flash(cv, k, col=PINK, a=0.5):
    if k <= 0.01:
        return
    cv.rect([0, 0, W, H], col + (int(120 * k * a),))


# ---------------------------------------------------------------- 1 · cold open
def s1(cv, lt, dur):
    cv.rect([0, 0, W, H], BG)
    p = expo(seg(0.15, 1.15, lt))
    if p > 0.01:
        cv.rect([W / 2 - W * 0.44 * p, 958, W / 2 + W * 0.44 * p, 962], PINK)
    if p > 0.3:
        night.skyline(cv, 1190, lt * 2.2, seed=31, scale=0.7, near=False)
        cv.rect([0, 1190, W, H], BG)
    cap(cv, 1250, "A CITY THAT NEVER SLEEPS", 30, expo(seg(1.0, 1.5, lt)), MUTED, 0.34)
    cap(cv, 820, "VICE CITY", 64, expo(seg(1.35, 1.9, lt)), CREAM, 0.30)
    if lt > 2.3:
        cv.rect([0, 0, W, H], BG + (int(255 * seg(2.3, 2.9, lt)),))


# ---------------------------------------------------------------- 2 · the skyline
def s2(cv, lt, dur):
    hz = 1210
    night.sky(cv, hz)
    night.sun(cv, W * 0.62, 980, 120, k=back(seg(0.0, 0.7, lt)))
    night.skyline(cv, hz - 4, lt, seed=3, scale=1.0)
    night.skyline(cv, hz + 30, lt * 1.15, near=True, seed=8, scale=1.25)
    night.bay(cv, hz + 34, W * 0.62, seed=7)
    night.palm(cv, W * 0.90, H + 70, 1180, lean=-0.16, col=BG)
    k1 = expo(seg(1.2, 1.7, lt))
    cap(cv, 560, "IN A CITY WHERE THE SUN", 46, k1, CREAM, 0.20)
    cap(cv, 640, "NEVER SETS", 46, expo(seg(1.45, 1.95, lt)), CREAM, 0.20)
    cap(cv, 760, "AND THE NEON NEVER FADES", 34, expo(seg(1.9, 2.4, lt)), MUTED, 0.24)


# ---------------------------------------------------------------- 3 · the car
def s3(cv, lt, dur):
    hz = 1150
    night.sky(cv, hz, top=mix(BG, VIOLET, 0.25))
    night.skyline(cv, hz, 2.0, seed=5, scale=0.9)
    road = 1430
    cv.rect([0, road, W, H], (16, 13, 22))
    cv.rect([0, road, W, road + 5], mix(CYAN, BG, 0.35))
    for i in range(9):                                  # lane dashes sliding past
        x = ((i * 190) - lt * 620) % (W + 260) - 130
        cv.rect([x, road + 120, x + 96, road + 130], mix(CREAM, BG, 0.55))
    x = lerp(-380, 690, snap(seg(0.1, 3.2, lt)))
    night.car(cv, x, road + 40, 1.0, col=(38, 30, 54), bob=math.sin(lt * 9) * 2.5)
    for i in range(3):                                  # wet-road reflections
        cv.poly([(x + 120, road + 42), (x + 300, road + 60 + i * 26),
                 (x + 120, road + 70 + i * 22)], mix(CYAN, BG, 0.78 - 0.18 * i))
    night.rain(cv, lt, 110, seed=4)
    cap(cv, 470, "ONE MAN.", 78, expo(seg(0.9, 1.4, lt)), CREAM, 0.14)
    cap(cv, 570, "ONE MISSION.", 78, expo(seg(1.35, 1.85, lt)), PINK, 0.14)


# ---------------------------------------------------------------- 4 · the name
def s4(cv, lt, dur):
    cv.rect([0, 0, W, H], PINK_D)
    p = expo(seg(0.0, 0.5, lt))
    cv.rect([0, 940, W, 940 + 6 * p], CREAM)
    cap(cv, 860, "TOMMY", 130, expo(seg(0.05, 0.55, lt)), CREAM, 0.10, glow=PINK)
    cap(cv, 1040, "VERCETTI", 130, expo(seg(0.25, 0.8, lt)), CREAM, 0.10, glow=PINK)
    cap(cv, 1160, "RELEASED. DEPOSITED. UNDERESTIMATED.", 26, expo(seg(0.8, 1.3, lt)),
        CREAM, 0.26)


# ---------------------------------------------------------------- 5 · the rise
def s5(cv, lt, dur):
    hz = 1330
    night.sky(cv, hz, top=mix(BG, PINK_D, 0.10))
    night.sun(cv, W * 0.30, 1120, 96, k=1.0)
    night.skyline(cv, hz - 10, min(lt * 0.9 + 0.6, 2.2), seed=12, scale=1.15)
    cv.rect([0, hz, W, H], mix(BG, VIOLET, 0.40))
    # the empire, as a bar chart built out of blocks
    for i in range(9):
        k = back(seg(0.15 + i * 0.10, 0.75 + i * 0.10, lt))
        h = 40 + i * 46
        x = 130 + i * 92
        if k > 0.02:
            cv.rect([x, hz - h * k, x + 62, hz], mix(CREAM, PINK, 0.15 + 0.08 * i))
            cv.rect([x, hz - h * k, x + 62, hz - h * k + 6], CREAM)
    cap(cv, 450, "FROM NOTHING", 62, expo(seg(0.2, 0.7, lt)), CREAM, 0.18)
    cap(cv, 600, "AN EMPIRE", 90, expo(seg(0.9, 1.5, lt)), PINK, 0.16, glow=PINK)
    cap(cv, 730, "POWER. MONEY. RESPECT.", 30, expo(seg(2.2, 2.7, lt)), MUTED, 0.30)


# ---------------------------------------------------------------- 6 · the conflict
def s6(cv, lt, dur):
    """Eight hard cuts, one per 1.25 s: the city turning on him."""
    i = min(7, int(lt / 1.25))
    t = lt - i * 1.25
    hz = 1300
    night.sky(cv, hz, top=mix(BG, PINK_D, 0.16 if i % 2 else 0.0))

    if i in (0, 4):                                     # muzzle flash
        night.skyline(cv, hz, 2.0, seed=21, scale=0.85)
        night.burst(cv, 540, 980, 200 * back(seg(0, 0.25, t)), k=1.0 - seg(0.1, 0.4, t))
        night.figure(cv, 380, hz + 40, 520, gun=True)
        night.figure(cv, 760, hz + 30, 560, gun=True)
        kick_flash(cv, 1 - seg(0.0, 0.18, t), CREAM, 0.20)
    elif i in (1, 5):                                   # explosion
        night.skyline(cv, hz, 2.0, seed=22, scale=0.9)
        night.burst(cv, 520, 1050, 300 * back(seg(0, 0.35, t)), core=CREAM, edge=AMBER)
        for j in range(6):
            yy = 1000 + j * 74
            cv.rect([0, yy, W, yy + 5], mix(AMBER, PINK, 0.4))
    elif i in (2, 6):                                   # sirens
        night.skyline(cv, hz, 2.0, seed=23, scale=0.8)
        # a fan of light off a roof bar, not a row of barcode stripes
        for j in range(5):
            top = 40 + j * 250 + math.sin(t * 9 + j) * 26
            cc = PINK if (j + int(t * 8)) % 2 else CYAN
            cv.poly([(top, -120), (top + 170, -120), (588, 1420), (506, 1420)],
                    cc + (42,))
        night.car(cv, 540, 1450, 1.25, col=CITY2, beam=False)
        night.figure(cv, 320, hz + 60, 620, gun=True)
        night.figure(cv, 760, hz + 50, 660, gun=True)
    else:                                               # the mob, walking
        night.skyline(cv, hz, 2.0, seed=24, scale=0.95)
        for j, x in enumerate((250, 420, 610, 800)):
            night.figure(cv, x, hz + 30 + j * 6, 460 + j * 26)
    cap(cv, 330, ["TURF WARS.", "BETRAYAL.", "THE MOB.", "THE FEDS.",
                  "CORRUPT COPS.", "NO ALLIES.", "NO RULES.", "NO MERCY."][i],
        56, expo(seg(0.15, 0.5, t)), CREAM, 0.18)
    if t < 0.06:
        cv.rect([0, 0, W, H], CREAM + (60,))


# ---------------------------------------------------------------- 7 · the payoff
def s7(cv, lt, dur):
    hz = 1290
    night.sky(cv, hz, top=mix(BG, VIOLET, 0.2))
    night.sun(cv, W * 0.5, 1080, 150, k=1.0)
    # the mansion: a wide low block with columns and two palms
    cv.poly([(180, hz), (200, 900), (420, 860), (660, 850), (900, 866), (900, hz)], CITY2)
    for i in range(6):
        cv.rect([250 + i * 110, 980, 290 + i * 110, hz], CITY)
    cv.rect([180, hz - 10, 900, hz], PINK)
    for i in range(9):
        cv.rect([250 + i * 80, 930, 300 + i * 80, 960], mix(CITY2, CREAM, 0.55))
    night.palm(cv, 90, hz + 120, 620, lean=0.20)
    night.palm(cv, 990, hz + 120, 640, lean=-0.18)
    cv.rect([0, hz, W, H], mix(BG, VIOLET, 0.35))
    k1 = expo(seg(0.4, 0.9, lt))
    cap(cv, 400, "THE QUESTION ISN'T", 38, k1, MUTED, 0.28)
    cap(cv, 470, "WHETHER HE SURVIVES —", 50, k1, CREAM, 0.18)
    cap(cv, 610, "IT'S HOW MUCH OF VICE CITY", 42, expo(seg(2.4, 2.9, lt)), CREAM, 0.20)
    cap(cv, 678, "HE'LL LEAVE STANDING.", 42, expo(seg(2.9, 3.4, lt)), PINK, 0.20)


# ---------------------------------------------------------------- 8 · endcard
def s8(cv, lt, dur):
    cv.rect([0, 0, W, H], BG)
    night.sun(cv, W / 2, 1180, 190, k=back(seg(0.0, 0.5, lt)))
    k = expo(seg(0.05, 0.55, lt))
    cap(cv, 560, "VICE", 150, k, CREAM, 0.12, glow=PINK)
    cap(cv, 720, "CITY", 150, expo(seg(0.25, 0.75, lt)), CREAM, 0.12, glow=PINK)
    if lt > 0.9:
        cv.rect([140, 812, 940, 817], PINK)
    cap(cv, 910, "COMING THIS SUMMER", 44, expo(seg(1.1, 1.6, lt)), CREAM, 0.24)
    cap(cv, 1450, "EVERYTHING SHINES.", 34, expo(seg(2.0, 2.5, lt)), MUTED, 0.26)
    cap(cv, 1512, "EVERYTHING HAS A PRICE.", 34, expo(seg(2.4, 2.9, lt)), MUTED, 0.26)
    # a last neon flicker on the title
    if 3.2 < lt < 3.55 and int(lt * 24) % 3 == 0:
        cv.rect([0, 480, W, 800], BG + (170,))


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8]


def draw(t):
    i = 0
    for k in range(len(BEATS) - 1):
        if t >= BEATS[k]:
            i = k
    i = min(i, len(SCENES) - 1)
    lo, hi = BEATS[i], BEATS[i + 1]
    lt, dur = t - lo, hi - lo
    cv = Canvas()
    crop = None
    if i == 6:                                   # one slow push on the payoff
        z = 1.0 + 0.06 * snap(seg(0, dur, lt))
        crop = (W / 2 - W / 2 / z, H / 2 - H / 2 / z, W / 2 + W / 2 / z, H / 2 + H / 2 / z)
    SCENES[i](cv, lt, dur)
    craft.scanlines(cv, alpha=14, gap=5)
    craft.vignette(cv, 0.7)
    return cv.finish(grain=3, crop=crop)


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

    out = "vice-city-trailer-1080x1920.mp4"
    print("beats", BEATS, "frames", NF, flush=True)

    if "--seg" in sys.argv:
        j = sys.argv.index("--seg")
        a, b, sp = int(sys.argv[j + 1]), int(sys.argv[j + 2]), sys.argv[j + 3]
        cmd = [ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", sp]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(a, b):
            proc.stdin.write(draw(i / FPS).tobytes())
            if (i - a) % 60 == 0:
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
                        "-i", "segs.txt", "-i", "audio/track.wav", "-c:v", "copy",
                        "-af", "volume=-2.5dB", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out],
                       check=True)
        print("joined", os.path.getsize(out))
        return


if __name__ == "__main__":
    main()
