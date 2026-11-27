"""film_stick.py — ফেরত · the one who came back. Character test, 1080x1920, 24 fps.

A stickman steps out of a screen, says nine seconds of Bangla, and steps back in.
The mouth is the take: `envelope()` turns the mp3 into a 24 fps loudness curve and the
mouth is drawn from that number, the way episodes 4–7 do it.

    python3 film_stick.py --still 6.0 --out frames/x.png
    python3 film_stick.py --seg 0 520 --out /tmp/s.mp4
"""
import functools
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw

import deva

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:                                            # pragma: no cover
    FF = "ffmpeg"

W, H = 1080, 1920
FPS = 24

PAPER = (240, 238, 230)
INK = (26, 23, 20)
INK_S = (120, 112, 100)
CORAL = (217, 119, 87)
MUST = (201, 154, 46)

LINE = os.path.join(HERE, "line.mp3")
SPOKEN = ["শহর থেকে ফিরে ভাবলাম, আমি অনেক বদলে গেছি।",
          "কিন্তু এই উঠোনে পা রাখতেই বুঝলাম, কিছুই বদলায়নি।",
          "শুধু আমি ছাড়া।",
          "এই ঘর আমাকে চিনতে পারছে না, আর আমিও ঘরটাকে চিনতে পারছি না।"]

LEAD = 1.5          # on the screen
POP = 1.4           # stepping out
TAIL = 1.5          # stepping back in
CARD = 2.4          # end card


def lerp(a, b, q):
    return a + (b - a) * q


def clamp(v, a=0.0, b=1.0):
    return a if v < a else (b if v > b else v)


def soft(q):
    q = clamp(q)
    return q * q * (3 - 2 * q)


def back(q, s=1.7):
    q = clamp(q) - 1
    return 1 + (s + 1) * q ** 3 + s * q ** 2


def _dur(path):
    err = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", err)
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


@functools.lru_cache(maxsize=2)
def envelope():
    wav = os.path.join(HERE, "_env.wav")
    if not os.path.exists(wav):
        subprocess.run([FF, "-y", "-v", "error", "-i", LINE, "-ar", "22050", "-ac", "1", wav],
                       check=True)
    with wave.open(wav) as fh:
        a = np.frombuffer(fh.readframes(fh.getnframes()), dtype=np.int16).astype(np.float32)
    a /= 32768.0
    hop = 22050 // FPS
    n = len(a) // hop
    r = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1))
    r = np.convolve(r, np.array([0.18, 0.64, 0.18]), mode="same")
    top = np.percentile(r, 96) + 1e-9
    r = np.clip(r / top * 1.5, 0, 1) ** 0.70
    r[r < 0.09] = r[r < 0.09] * 0.22
    return tuple(float(v) for v in r)


DUR = _dur(LINE) if os.path.exists(LINE) else 17.6
T_VO = LEAD + POP
T_BACK = T_VO + DUR + 0.35
T_CARD = T_BACK + TAIL
TOTAL = T_CARD + CARD


def gap_cuts():
    """Four sentences, three of the longest silences — captions follow the breath."""
    env = envelope()
    quiet = [i for i, v in enumerate(env) if v < 0.10]
    runs, cur = [], []
    for i in quiet:
        if cur and i != cur[-1] + 1:
            runs.append(cur)
            cur = []
        cur.append(i)
    if cur:
        runs.append(cur)
    cands = [r for r in runs if len(r) > 4]
    cands.sort(key=len, reverse=True)
    cuts = sorted(r[len(r) // 2] / FPS for r in cands[:len(SPOKEN) - 1])
    return cuts


CUTS = gap_cuts()


def caption_at(t):
    if t < T_VO:
        return None
    i = t - T_VO
    idx = 0
    for k, c in enumerate(CUTS):
        if i >= c:
            idx = k + 1
    return SPOKEN[min(idx, len(SPOKEN) - 1)]


@functools.lru_cache(maxsize=1)
def sprite():
    return Image.open(os.path.join(HERE, "rig.png")).convert("RGBA")


import json
RIG = json.load(open(os.path.join(HERE, "rig.json")))


@functools.lru_cache(maxsize=1)
def face_col():
    im = np.asarray(sprite())
    x, y = RIG["eyes"][0][0], RIG["eyes"][0][1]
    box = im[y + 26:y + 56, x + 10:x + 90, :3].reshape(-1, 3)
    return tuple(int(v) for v in np.median(box, axis=0))


@functools.lru_cache(maxsize=96)
def scaled(h):
    sp = sprite()
    k = h / sp.height
    return sp.resize((max(1, round(sp.width * k)), max(1, round(h))), Image.LANCZOS), k


@functools.lru_cache(maxsize=96)
def turned(h, deg):
    img, _ = scaled(h)
    return img.rotate(deg, resample=Image.BICUBIC, center=(img.width // 2, img.height // 2))


def draw_face(work, k, m, blink):
    d = ImageDraw.Draw(work)
    mx, my, mw, mh = RIG["mouth"]
    cx, cy = mx * k, my * k
    mw, mh = mw * k, mh * k
    lw = max(3, int(round(7 * k)))
    if m < 0.08:
        d.line([(cx - mw * 0.85, cy), (cx + mw * 0.85, cy)], fill=INK + (255,), width=lw)
    else:
        ow = mw * (1.30 + 0.55 * m)
        oh = mh * (1.6 + 6.2 * m)
        d.ellipse([cx - ow, cy - oh * 0.55, cx + ow, cy + oh * 0.75],
                  fill=INK + (255,))
        if m > 0.55:
            d.ellipse([cx - ow * 0.42, cy + oh * 0.18, cx + ow * 0.42, cy + oh * 0.62],
                      fill=(176, 84, 70, 255))
    if blink:
        col = face_col() + (255,)
        for ex, ey, er in RIG["eyes"]:
            ex, ey, er = ex * k, ey * k, er * k
            d.ellipse([ex - er * 1.5, ey - er * 1.5, ex + er * 1.5, ey + er * 1.5], fill=col)
            d.line([(ex - er * 1.15, ey + er * 0.1), (ex + er * 1.15, ey + er * 0.1)],
                   fill=INK + (255,), width=max(2, int(round(5 * k))))


def blink_at(t):
    return (t % 3.4) < 0.10 or (t % 7.1) < 0.08


def stage(art, t):
    """Paper, a sun, a ground line, and the screen he walks out of."""
    d = ImageDraw.Draw(art)
    art.paste(PAPER, (0, 0, W, H))
    drift = 18 * math.sin(t * 0.11)
    d.ellipse([W * 0.5 - 300 + drift, 250, W * 0.5 + 300 + drift, 850], fill=CORAL)
    d.rectangle([0, 1790, W, H], fill=(226, 219, 205))
    d.line([(0, 1790), (W, 1790)], fill=INK, width=6)


def screen_frame(art, t, s, alpha):
    """The device he is stuck inside — it opens for him, then waits behind him."""
    if alpha <= 0.01:
        return
    w, h = 500 * s, 800 * s
    x0, y0 = W / 2 - w / 2, 880 - h / 2
    lay = Image.new("RGBA", (int(w) + 40, int(h) + 40), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    dd.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=int(34 * s),
                         fill=(250, 247, 240, int(235 * alpha)),
                         outline=INK + (int(255 * alpha),), width=int(9 * s))
    dd.rounded_rectangle([20 + w * 0.42, 20 + 12 * s, 20 + w * 0.58, 20 + 20 * s],
                         radius=int(4 * s), fill=INK + (int(160 * alpha),))
    art.alpha_composite(lay, (int(x0 - 20), int(y0 - 20)))


def frame(t):
    art = Image.new("RGBA", (W, H), PAPER)
    stage(art, t)
    env = envelope()

    if t >= T_CARD:
        u = clamp((t - T_CARD) / 0.8)
        art.paste(PAPER, (0, 0, W, H))
        ImageDraw.Draw(art).rectangle([0, 0, W, 22], fill=INK)
        ImageDraw.Draw(art).rectangle([0, H - 22, W, H], fill=INK)
        deva.draw_text(art, (92, 720), "ফেরত", 132, 700, INK, anchor="lm")
        deva.draw_text(art, (96, 850), "যে ফিরে আসে", 46, 500, (140, 132, 120), anchor="lm")
        a = int(255 * clamp((t - T_CARD - 0.6) / 1.0))
        if a > 0:
            deva.draw_text(art, (96, 1000), "কিছুই বদলায় না, শুধু আমরা।", 44, 500,
                           CORAL, anchor="lm")
        deva.draw_text(art, (96, 1770), "অন্ধকার পাঠ · নতুন চরিত্র", 30, 500, INK_S, anchor="lm")
        return art

    # ---- where he is in the gag
    if t < LEAD:                                     # inside the screen, small
        h = 560
        feet = 1258
        alpha_s = 1.0
        s_screen = 1.0
        m = 0.0
        z = 1.0
    elif t < T_VO:                                   # stepping out, overshoot
        u = (t - LEAD) / POP
        e = back(u, 1.5)
        h = lerp(560, 1520, e)
        feet = lerp(1258, 1790, e)
        alpha_s = 1.0 - clamp(u * 1.25)
        s_screen = 1.0 - 0.25 * soft(u)
        m = 0.0
        z = 1.0
    elif t < T_BACK:                                 # he talks
        h = 1520
        feet = 1790
        alpha_s = 0.0
        s_screen = 0.0
        i = int((t - T_VO) * FPS)
        m = env[min(i, len(env) - 1)] if i >= 0 else 0.0
        z = 1.0 + 0.05 * soft(clamp((t - T_VO) / (T_BACK - T_VO))) \
            + 0.07 * soft(clamp((t - (T_VO + DUR * 0.74)) / 1.2))
    else:                                            # stepping back inside
        u = clamp((t - T_BACK) / TAIL)
        e = soft(u)
        h = lerp(1520, 560, e)
        feet = lerp(1790, 1258, e)
        alpha_s = clamp((u - 0.35) / 0.5)
        s_screen = 1.0 - 0.0 * u
        m = 0.0
        z = 1.14 - 0.14 * e

    screen_frame(art, t, s_screen, alpha_s)

    # ---- the puppet
    deg = 0.7 * math.sin(t * 0.9) + (1.4 if (T_VO + DUR * 0.74) < t < T_BACK else 0.0)
    img = turned(round(h / 8) * 8, round(deg * 2) / 2)
    k = img.height / sprite().height
    work = img.copy()
    draw_face(work, k, m, blink_at(t))

    bob = 2.6 * math.sin(t * 1.7) - 9.0 * m
    cx = W / 2 + 5 * math.sin(t * 0.7)
    feet = feet + bob

    sh_w = work.width * 0.62
    sh = max(10, int(work.height * 0.018))
    shadow = Image.new("RGBA", (int(sh_w), sh * 2), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([0, 0, sh_w - 1, sh * 2 - 1], fill=(26, 23, 20, 46))
    art.alpha_composite(shadow, (int(cx - sh_w / 2), int(feet - sh)))

    # camera: scale about the ground line
    if z != 1.0:
        grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sw = int(work.width * z)
        shh = int(work.height * z)
        work = work.resize((sw, shh), Image.LANCZOS)
        nx = W / 2 + (cx - W / 2) * z
        ny = 1790 + (feet - 1790) * z
        grid.alpha_composite(work, (int(nx - sw / 2), int(ny - shh)))
        art.alpha_composite(grid)
    else:
        art.alpha_composite(work, (int(cx - work.width / 2), int(feet - work.height)))

    # ---- type
    deva.draw_text(art, (86, 96), "অন্ধকার পাঠ", 28, 500, INK_S, anchor="lm")
    cap = caption_at(t)
    rise = soft((t - (T_VO - 0.5)) / 0.5)
    band_top = lerp(H + 40, 1596, rise)
    d = ImageDraw.Draw(art)
    if band_top < H:
        d.rectangle([0, int(band_top), W, H], fill=PAPER)
        d.line([(0, int(band_top)), (W, int(band_top))], fill=INK, width=6)
    if cap and band_top < 1620:
        lines = wrap(cap, 40, 900)
        y = 1690 if len(lines) < 3 else 1672
        for ln in lines:
            deva.draw_text(art, (86, y), ln, 40, 600, (28, 25, 22), anchor="lm")
            y += 54
        deva.draw_text(art, (W - 86 - deva.layout("ফেরত", 26)[1], 1840), "ফেরত", 26, 700,
                       CORAL, anchor="lm")
    return art


@functools.lru_cache(maxsize=64)
def wrap(text, size, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        try:
            width = deva.layout(trial, size)[1]
        except Exception:
            width = len(trial) * size * 0.55
        if width > maxw and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return tuple(lines)


def render(still=None, seg=None, out=None):
    n = int(round(TOTAL * FPS))
    print("total %.2fs · %d frames · cuts %s" % (TOTAL, n,
                                                 [round(c, 2) for c in CUTS]), flush=True)
    if still is not None:
        frame(float(still)).convert("RGB").save(out or "frames/s.png")
        print("wrote", out or "frames/s.png")
        return
    a, b = seg if seg else (0, n)
    out = out or "stickman-test.mp4"
    ff = subprocess.Popen(
        [FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-g", "48", out], stdin=subprocess.PIPE)
    for i in range(a, b):
        ff.stdin.write(frame(i / FPS).convert("RGB").tobytes())
        if i % 120 == 0:
            print("  %d/%d" % (i - a, b - a), flush=True)
    ff.stdin.close()
    ff.wait()
    print("wrote", out)


if __name__ == "__main__":
    args = sys.argv[1:]
    still = seg = out = None
    if "--still" in args:
        still = float(args[args.index("--still") + 1])
    if "--seg" in args:
        i = args.index("--seg")
        seg = (int(args[i + 1]), int(args[i + 2]))
    if "--out" in args:
        out = args[args.index("--out") + 1]
    os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
    render(still=still, seg=seg, out=out)
