#!/usr/bin/env python3
"""অন্ধকার পাঠ · DARK LESSON — a 3D-anime style short in Bangla, 1080x1920.

    python3 film.py --still 12.0     one frame at t=12s
    python3 film.py --seg A B out.mp4  render frames A..B-1 to a silent segment
    python3 film.py --join s1.mp4 ...  concat segments + mux the voice-over
    python3 film.py                  full render (needs audio/s1..s7.mp3)

Every frame is a pure function of t: a software cel renderer (cel3d.py) for the 3D,
2D paint for the room and the light, harfbuzz for the Bengali type (deva.py),
because this box has no libraqm.
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
SS = 1.35
FPS = 24
TTF = "/usr/local/lib/python3.11/dist-packages/matplotlib/mpl-data/fonts/ttf/"
F_INK = (8, 7, 10)
CREAM = (242, 236, 220)
COLD = (150, 190, 255)
EMBER_TXT = (247, 168, 96)
DIM = (176, 172, 168)

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


LEAD, GAP, TAIL = 1.20, 0.40, 4.60
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


def shake(t, amp, seed=1.0):
    return (amp * math.sin(t * 47.3 + seed), amp * math.sin(t * 39.1 + seed * 2.3))


def compose_3d(img, cams, models, glow_models=()):
    for model, cam in zip(models, cams):
        is_glow = model in glow_models if isinstance(glow_models, (list, tuple)) else False
        tile, pos = C.render_model_tiled(model, cam, ss=SS, outline=F_INK, glow=is_glow, outline_px=6)
        img.alpha_composite(tile, pos)


def cam_at(eye, target, fov):
    c = Cam(eye=eye, target=target, fov=fov, w=W, h=H)
    c._fov = fov
    return c


def floor_y(cam, z=1.4):
    """Screen y where the wall meets the floor (a plane at depth z)."""
    p = cam.project(cam.to_view(np.array([0.0, 0.0, z])))[0]
    return int(min(H - 1, max(10, p[1])))


def stage(img, cam, z=1.5, seed=3, base=None, floor_col=(11, 10, 14)):
    y0 = floor_y(cam, z)
    bg2.wall(img, y0, seed=seed)
    bg2.floor(img, y0, col=(16, 15, 19), deep=floor_col)
    return y0


# ---------------------------------------------------------------- scenes
def s1(img, lt, dur):
    """The alley: the lantern in the mud, still dark. Slow push-in."""
    p = eio(seg(0.0, dur, lt))
    cam = cam_at((0.42 - 0.06 * p, 0.98 - 0.08 * p, 4.30 - 0.55 * p), (0.0, 0.52, 0.75), 36)
    y0 = stage(img, cam, 1.7, seed=3)
    bg2.fog(img, lt, 0.5)
    lit = 0.52 + 0.16 * math.sin(lt * 2.2)
    lan = place(cast.lantern(t=lt, lit=lit, tilt=7, float_=0.35),
                T(-0.16, 0.02, 0.85) @ S(0.80))
    compose_3d(img, [cam], [lan], glow_models=[lan])
    bg2.pool(img, 470, 1370, 280, col=(88, 136, 255), a=44, blur=110)
    bg2.glow(img, 470, 1330, 76, col=(150, 190, 255), a=105, blur=42)

    k = eout(seg(0.4, 1.4, lt))
    if k > 0.02:
        deva.draw_text(img, (540, 300), "অন্ধকার পাঠ", int(72 * k + 6), 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=20)
        d = ImageDraw.Draw(img)
        d.text((540, 372), "D A R K   L E S S O N   ·   0 1", font=ImageFont.truetype(TTF + "DejaVuSans.ttf", 24),
               fill=(152, 148, 142, int(235 * k)), anchor="mm")
        d.line([(400, 428), (680, 428)], fill=(120, 130, 160, int(150 * k)), width=2)
    if lt > 2.0:
        deva.draw_text(img, (540, 486), "ধার করা আলো", 36, 500, COLD,
                       shadow=(0, 0, 0), shadow_blur=14)
    bg2.grade(img)


def s2(img, lt, dur):
    """He lifts it. The shade stands up behind him."""
    rise = eio(seg(0.6, 3.4, lt))
    cam = cam_at((0.70, 1.15, 4.4), (0.0, 0.95, 0.2), 34)
    y0 = stage(img, cam, 1.7, seed=5)
    bg2.fog(img, lt, 0.7)

    sh = place(cast.shade(t=lt, high=0.15 + 0.95 * rise, reach=0.35 * rise,
                          eyes=eout(seg(1.6, 2.4, lt))),
               T(-0.80, 0, -0.95) @ S(0.82))
    ayan = place(cast.ayan(t=lt, walk=0.0, arm=0.35 + 0.45 * rise, candle=0.0,
                           look=0.2 * rise, slump=0.6 * (1 - rise)), T(0.16, 0, 0.55))
    lan = place(cast.lantern(t=lt, lit=0.9 + 0.5 * rise, float_=1.0),
                T(0.46 + 0.10 * rise, 0.80 + 0.22 * rise, 0.62) @ S(0.62))
    compose_3d(img, [cam] * 3, [sh, ayan, lan], glow_models=[lan])
    bg2.pool(img, 700, 1150, 300, col=(88, 136, 255), a=int(40 + 60 * rise), blur=110)
    bg2.glow(img, 690, 980, 70 + 30 * rise, col=(150, 190, 255), a=int(70 + 60 * rise), blur=40)

    if lt > 2.2:
        deva.draw_text(img, (540, 1772), "ছায়া বলল: যা চাস, আমি দেব", 38, 600, CREAM,
                       shadow=(0, 0, 0), shadow_blur=16)
    bg2.grade(img, tint=(236, 242, 255))


def s3(img, lt, dur):
    """The bargain: coins for a memory."""
    cam = cam_at((0.55, 1.20, 4.2), (0.0, 1.00, 0.15), 35)
    y0 = stage(img, cam, 1.7, seed=7)
    bg2.fog(img, lt, 0.4)

    ayan = place(cast.ayan(t=lt, walk=0.0, arm=0.55, candle=0.0, look=0.35,
                           blink=0.0), T(0.0, 0, 0.45))
    sh = place(cast.shade(t=lt, high=1.0, reach=0.85, eyes=1.0), T(-1.15, 0, -0.95) @ S(0.95))
    lan = place(cast.lantern(t=lt, lit=1.8, float_=1.0), T(-0.70, 0.10, 0.95) @ S(0.72))
    compose_3d(img, [cam] * 3, [sh, ayan, lan], glow_models=[lan])

    bg2.coins(img, lt, x=560, y=0, n=16, spread=420, seed=11)
    bg2.pool(img, 540, 1500, 380, col=(255, 210, 120), a=34, blur=120)
    bg2.pool(img, 300, 1160, 260, col=(90, 140, 255), a=52, blur=100)
    if lt > 2.0:
        deva.draw_text(img, (540, 1772), "ভাড়া: একটা স্মৃতি", 42, 700, EMBER_TXT,
                       shadow=(0, 0, 0), shadow_blur=16)
    bg2.grade(img, tint=(255, 240, 224))


def s4(img, lt, dur):
    """The price: the photographs go blank one by one."""
    cam = cam_at((0.45, 1.25, 4.0), (0.0, 1.10, 0.10), 35)
    y0 = stage(img, cam, 1.7, seed=9)
    bg2.fog(img, lt, 0.8)

    ayan = place(cast.ayan(t=lt, walk=0.0, arm=0.15, candle=0.0, look=-0.3,
                           blink=1.0 - eout(seg(0.2, 0.6, lt)), slump=1.0), T(0.05, 0, 0.55))
    sh = place(cast.shade(t=lt, high=1.0, reach=0.15, eyes=0.85, sway=1.0),
               T(-1.05, 0, -0.95) @ S(0.95))
    compose_3d(img, [cam] * 2, [sh, ayan])

    # three photographs, each losing its picture at a different moment
    fades = [1 - eio(seg(0.9, 1.9, lt)), 1 - eio(seg(2.3, 3.2, lt)), 1 - eio(seg(3.5, 4.4, lt))]
    for i, f in enumerate(fades):
        ph = place(cast.photo(t=lt, fade=max(0.0, f)),
                   T(-0.92 + i * 0.92, 1.58 + 0.04 * math.sin(lt * 1.3 + i), 1.55)
                   @ R("z", (i - 1) * 5) @ S(0.82))
        compose_3d(img, [cam], [ph])
    bg2.pool(img, 540, 1080, 300, col=(88, 136, 255), a=40, blur=110)
    if lt > 2.6:
        deva.draw_text(img, (540, 1772), "প্রথমে ভুলে গেল বন্ধুর নাম", 38, 600, CREAM,
                       shadow=(0, 0, 0), shadow_blur=16)
    bg2.grade(img)


def s5(img, lt, dur):
    """Alone with all of it."""
    push = eio(seg(0.0, dur, lt))
    cam = cam_at((0.25 + 0.1 * push, 1.28, 5.6 - 0.4 * push), (0.0, 1.02, 0.10), 33)
    y0 = stage(img, cam, 2.0, seed=13)
    bg2.window(img, 120, 300, 380, 900, shaft=0.8)
    bg2.fog(img, lt, 1.0)

    ayan = place(cast.ayan(t=lt, walk=0.0, arm=0.0, candle=0.0, look=0.0, slump=0.85),
                 T(0.20, 0, 0.60))
    sh = place(cast.shade(t=lt, high=1.15, reach=0.0, eyes=0.7, sway=1.0),
               T(-1.05, 0, -0.85) @ S(1.0))
    compose_3d(img, [cam] * 2, [sh, ayan])
    # the coins he got, on the floor, no longer worth anything
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(22):
        cx = 300 + (i * 137) % 520
        cy = 1500 + (i * 71) % 220
        rx = 16 + (i % 4) * 3
        d.ellipse([cx - rx, cy - rx * 0.42, cx + rx, cy + rx * 0.42], fill=(206, 168, 84, 150))
    img.paste(Image.alpha_composite(img.convert("RGBA"),
                                    lay.filter(ImageFilter.GaussianBlur(2.0))).convert("RGB"))
    if lt > 2.0:
        deva.draw_text(img, (540, 1772), "হাতে সব — পাশে কেউ নেই", 40, 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=18)
    bg2.grade(img)


def s6(img, lt, dur):
    """He lights his own candle. The borrowed light goes out."""
    out = eio(seg(0.3, 1.4, lt))
    own = eio(seg(1.6, 2.6, lt))
    cam = cam_at((0.45, 1.10, 3.9), (0.0, 0.95, 0.15), 35)
    y0 = stage(img, cam, 1.7, seed=15)
    bg2.fog(img, lt * 0.6, 0.6, seed=3)

    sh = place(cast.shade(t=lt, high=1.05 - 0.95 * own, reach=0.1 - 0.1 * own,
                          eyes=0.9 * (1 - 0.75 * own)),
               T(-1.15 - 0.35 * own, 0, -0.75) @ S(lerp(1.1, 0.85, own)))
    ayan = place(cast.ayan(t=lt, walk=0.0, arm=0.62 + 0.38 * own, candle=own,
                           look=0.15, slump=0.5 * (1 - own)), T(0.10, 0, 0.55))
    lan = place(cast.lantern(t=lt, lit=max(0.0, 1.6 * (1 - out))), T(-0.66, 0.02, 1.15) @ S(0.75))
    compose_3d(img, [cam] * 3, [sh, ayan, lan], glow_models=[lan])

    if own > 0.02:
        bg2.pool(img, 610, 1180, int(150 + 160 * own), col=(255, 176, 96), a=int(50 * own), blur=120)
        bg2.glow(img, 640, 1105, int(40 + 26 * own), col=(255, 196, 120), a=int(90 * own), blur=34)
    if out < 0.98:
        bg2.pool(img, 300, 1250, 220, col=(90, 140, 255), a=int(55 * (1 - out)), blur=100)
    if lt > 2.4:
        deva.draw_text(img, (540, 1772), "ধার করা আলো তোমাকে চেনে না", 38, 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=16)
    bg2.grade(img, tint=(255, 246, 236) if own > 0.4 else (240, 244, 255))


_CTA_TILE = None
_CTA_QT = -1.0


def s7(img, lt, dur):
    """The card. Four things to do, cheapest last."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(9, 9, 13))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(lay)
    gd.ellipse([110, 700, 970, 1280], fill=(255, 150, 70, 34))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(120)))

    k1 = eout(seg(0.10, 0.75, lt))
    k2 = eout(seg(0.50, 1.15, lt))
    k3 = eout(seg(0.90, 1.60, lt))
    k4 = eout(seg(1.35, 2.00, lt))

    if k1 > 0.03:
        deva.draw_text(img, (540, 286), "অন্ধকার পাঠ", 46, 700, (198, 192, 184),
                       shadow=(0, 0, 0), shadow_blur=14)
        deva.draw_text(img, (540, 470), "কোন স্মৃতি তুমি", int(58 * k1 + 8), 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=18)
        deva.draw_text(img, (540, 570), "কখনো বেচবে না?", int(58 * k1 + 8), 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=18)
    if k2 > 0.03:
        deva.draw_text(img, (540, 690), "যে আলো ধার করা, সে তোমাকে চেনে না।", 34, 500,
                       (150, 186, 244), shadow=(0, 0, 0), shadow_blur=12)
    if k3 > 0.03:
        deva.draw_text(img, (540, 900), "কমেন্ট করো: একটা স্মৃতি", 44, 700, EMBER_TXT,
                       shadow=(0, 0, 0), shadow_blur=14)
        pw = 600 * k3
        d.rounded_rectangle([540 - pw / 2, 1010, 540 + pw / 2, 1146], 36, fill=(247, 172, 92))
        if k3 > 0.85:
            deva.draw_text(img, (540, 1078), "ফলো করো", 48, 700, (16, 12, 11))
    if k4 > 0.03:
        deva.draw_text(img, (540, 1236), "প্রতি শুক্রবার · নতুন পাঠ", 34, 500, (188, 182, 176))
        d.line([(340, 1296), (340 + 400 * k4, 1296)], fill=(247, 172, 92, 200), width=3)

    qt = round(lt * 4) / 4.0
    global _CTA_TILE, _CTA_QT
    if _CTA_TILE is None or _CTA_QT != qt:
        cam = cam_at((0.5, 1.05, 3.7), (0.0, 0.92, 0.1), 34)
        ayan = place(cast.ayan(t=qt, walk=0.0, arm=0.95, candle=1.0, look=0.1), T(0, 0, 0))
        tile, _ = C.render_model_tiled(ayan, cam, ss=SS, outline=F_INK, glow=True, outline_px=6)
        scale = 400 / max(1, tile.width)
        tile = tile.resize((int(tile.width * scale), int(tile.height * scale)), Image.LANCZOS)
        _CTA_TILE, _CTA_QT = tile, qt
    img.alpha_composite(_CTA_TILE, (int(W / 2 - _CTA_TILE.width / 2),
                                    min(1330, 1876 - _CTA_TILE.height)))
    bg2.pool(img, 540, 1700, 240, col=(255, 168, 92), a=40, blur=110)


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
        a, b, sp = int(sys.argv[j + 1]), int(sys.argv[j + 2]), sys.argv[j + 3]
        cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-pix_fmt", "yuv420p", sp]
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
                        "dark-lesson-1080x1920.mp4"], check=True)
        print("joined -> dark-lesson-1080x1920.mp4", os.path.getsize("dark-lesson-1080x1920.mp4"))
        return

    out = "dark-lesson-1080x1920.mp4"
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
