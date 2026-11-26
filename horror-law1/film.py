"""horror-law1 — আইন ১: মনিবের চেয়ে বেশি জ্বলজ্বল করো না।

A two-minute Bangla horror parable on Robert Greene's first law, told with the five
character designs in img/cast.png. The design sheet is one illustration, so there are no
cut-out puppets: the picture is a *plate*, and the film is built from camera (crawls and
push-ins), grade (warm memory -> cold -> ash), light (a lamp that flickers), type, and a
procedural score.

Timing is probed from the voice takes, never hardcoded:
    NAR[k] = start of spoken line k
    BOUNDS = one cut per scene, 0.35 s before the line it carries
Re-record a line and the film re-times itself.

    python3 film.py --mix                      voices + bed -> audio/mix.wav
    python3 film.py --still 12.5               single frame, for QA
    python3 film.py --seg 0 900 /tmp/a.mp4     render frames [a,b)
    python3 film.py --join /tmp/a.mp4 ...      concat + mux -> OUT
"""
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

import deva  # noqa: E402
deva.FONT = os.path.join(HERE, "fonts", "NotoSansBengali.ttf")

W, H, FPS = 1080, 1920, 30
BG = (11, 12, 13)
INK = (236, 229, 216)
DIM = (138, 128, 120)
RED = (194, 69, 47)
BLOOD = (86, 26, 20)
TRACK = (38, 33, 31)

# panel frame: wide scenes sit inside it letterboxed, close-ups fill it
PX, PY, PFW, PFH = 60, 176, 960, 672
WIDE_H = 540
SRC_W, SRC_H = 1408, 768

TX = 72
TY_OVER = 908
TY_BODY = 972
BODY_ZONE = 528
BODY_MAXW = 936
METER_Y = 1602
FOOT_Y = 1798

TAKES = ["audio/v%d.mp3" % i for i in range(1, 11)]
START = 4.2
GAPS = [1.0, 1.0, 1.0, 1.1, 1.0, 1.6, 2.2, 2.4, 2.6]
TAIL = 12.4
MIX = "audio/mix.wav"
OUT = os.environ.get("OUT", "horror-law1-1080x1920.mp4")
FACES = [("তানিয়া", 250, 258), ("বাবা", 438, 176), ("রোকেয়া", 687, 200),
         ("মিঠু", 944, 176), ("মা", 1224, 205)]


def bn(n):
    return str(n).translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def f(a, b, t):
    t = clamp(t, 0.0, 1.0)
    return a + (b - a) * t


def expo(k):
    k = clamp(k, 0.0, 1.0)
    return 1 - (1 - k) ** 3


def sine_io(k):
    k = clamp(k, 0.0, 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * k)


def wob(t, seed, amp=1.0):
    return amp * (0.62 * math.sin(t * 0.83 + seed) + 0.38 * math.sin(t * 2.17 + seed * 3.1))


# ------------------------------------------------------------------ timeline
def _probe(path):
    import imageio_ffmpeg
    txt = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", txt)
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


DUR = [_probe(p) for p in TAKES]
NAR, _t = [], START
for k, d in enumerate(DUR):
    NAR.append(round(_t, 3))
    _t += d + (GAPS[k] if k < len(GAPS) else 0.0)
SPEECH_END = round(NAR[-1] + DUR[-1], 3)
BOUNDS = [0.0] + [round(NAR[k] - 0.35, 3) for k in range(1, 10)] + [round(SPEECH_END + 0.55, 3)]
TOTAL = round(BOUNDS[-1] + TAIL, 3)
NF = int(round(TOTAL * FPS))
NSC = len(BOUNDS)


# ------------------------------------------------------------------ grade
_SRC = Image.open("img/cast.png").convert("RGB")
_A = np.asarray(_SRC, np.float32) / 255.0


def _grade(desat, dark, tint, contrast):
    lum = (_A[:, :, 0] * 0.299 + _A[:, :, 1] * 0.587 + _A[:, :, 2] * 0.114)[:, :, None]
    a = _A * (1 - desat) + lum * desat
    a = (a - 0.5) * contrast + 0.5
    a = a * dark * np.array(tint, np.float32)
    return Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8))


GRADES = {
    "warm": _grade(0.10, 0.94, (1.04, 1.00, 0.93), 1.02),
    "cold": _grade(0.58, 0.58, (0.80, 0.94, 1.00), 1.12),
    "dark": _grade(0.74, 0.34, (1.00, 0.79, 0.78), 1.20),
    "ash":  _grade(0.88, 0.20, (0.95, 0.86, 0.86), 1.10),
}


def crop_plate(src, cx, cy, z, bw, bh, jx=0.0, jy=0.0):
    asp = bw / bh
    cw = SRC_W / z
    ch = cw / asp
    if ch > SRC_H:
        ch = SRC_H
        cw = ch * asp
    cx = clamp(cx + jx, cw / 2, SRC_W - cw / 2)
    cy = clamp(cy + jy, ch / 2, SRC_H - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    im = src.crop(tuple(int(round(v)) for v in box))
    return im.resize((bw, bh), Image.LANCZOS if cw < bw else Image.BICUBIC)


# ------------------------------------------------------------------ furniture
def rounded_mask(w, h, r=16):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    return m


MASK_FILL = rounded_mask(PFW, PFH)
MASK_WIDE = rounded_mask(PFW, WIDE_H)

_SHADOW = Image.new("RGBA", (PFW + 120, PFH + 120), (0, 0, 0, 0))
_d = ImageDraw.Draw(_SHADOW)
_d.rounded_rectangle([56, 64, 56 + PFW + 8, 64 + PFH + 16], 20, fill=(0, 0, 0, 210))
_SHADOW = _SHADOW.filter(ImageFilter.GaussianBlur(20))


def _vignette(w, h, strength=190, power=2.4):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (x - w / 2) / (w / 2)
    ny = (y - h / 2) / (h / 2)
    r = np.sqrt(nx ** 2 * 0.86 + ny ** 2) / 1.28
    a = (np.clip(r, 0, 1) ** power * strength).astype(np.uint8)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im.putalpha(Image.fromarray(a))
    return im


VIG_FILL = _vignette(PFW, PFH, 172, 2.2)
VIG_WIDE = _vignette(PFW, WIDE_H, 150, 2.2)
FRAME_VIG = _vignette(W, H, 150, 2.6)


def _glow(r=250, col=(255, 176, 92)):
    s = r * 2
    y, x = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.sqrt((x - r) ** 2 + (y - r) ** 2) / r
    a = (np.clip(1 - d, 0, 1) ** 2.6 * 255).astype(np.uint8)
    im = Image.new("RGBA", (s, s), col + (0,))
    im.putalpha(Image.fromarray(a))
    return im


GLOW = _glow(250)
_PLATE = Image.new("RGBA", (PFW, PFH), (0, 0, 0, 0))
_RAIN = None


def rain_layer():
    global _RAIN
    if _RAIN is None:
        rng = np.random.default_rng(7)
        im = Image.new("RGBA", (PFW * 2, PFH), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for _ in range(300):
            x = rng.uniform(0, PFW * 2)
            y = rng.uniform(0, PFH)
            ln = rng.uniform(28, 78)
            d.line([(x, y), (x - ln * 0.24, y + ln)],
                   fill=(196, 214, 230, int(rng.uniform(16, 46))), width=1)
        _RAIN = im
    return _RAIN


GRAIN = None


def grain():
    global GRAIN
    if GRAIN is None:
        rng = np.random.default_rng(5)
        n = rng.normal(0, 7.5, (H // 2, W // 2)).clip(-22, 22)
        n = np.repeat(np.repeat(n, 2, axis=0), 2, axis=1)[:H, :W]
        base = np.zeros((H, W, 3), np.uint8) + 128
        GRAIN = Image.fromarray((base + n[:, :, None]).clip(0, 255).astype(np.uint8))
    return GRAIN


class Surf:
    def __init__(self, w=None, h=None, col=BG):
        self.im = Image.new("RGBA", (w or W, h or H), tuple(col) + (255,))


# ------------------------------------------------------------------ type
_cap_cache, _TIMG, _TW = {}, {}, {}


def timg(s, size, weight, color):
    k = (s, size, weight, color)
    if k not in _TIMG:
        _TIMG[k] = deva.text_image(s, size, weight, color)
    return _TIMG[k]


def twidth(s, size, weight):
    k = (s, size, weight)
    if k not in _TW:
        _TW[k] = deva.layout(s, size, weight)[1]
    return _TW[k]


def plate_left(text, size, weight, color, maxw):
    key = (text, size, weight, color, maxw)
    if key in _cap_cache:
        return _cap_cache[key]
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if deva.layout(trial, size, weight)[1] <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    imgs = [timg(l, size, weight, color) for l in lines]
    lh = int(size * 1.44)
    wid = max(i.width for i in imgs)
    out = Image.new("RGBA", (wid + 6, lh * len(imgs) + 8), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        out.alpha_composite(im, (0, i * lh + (lh - im.height) // 2))
    _cap_cache[key] = out
    return out


def fit_caption(text):
    best = None
    for size in (58, 54, 50, 46, 42):
        im = plate_left(text, size, 600, INK, BODY_MAXW)
        if im.height <= 560:
            return im, size
        best = (im, size)
    return best


def blit(base, layer, x, y, alpha=1.0):
    if alpha <= 0.02:
        return
    if alpha < 0.98:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(layer, (int(x), int(y)))


def text_at(base, xy, s, size, weight=600, color=INK, anchor="lm", alpha=1.0):
    if alpha <= 0.02:
        return
    im = timg(s, size, weight, color)
    x, y = xy
    if anchor[0] == "m":
        x -= im.width / 2
    elif anchor[0] == "r":
        x -= im.width
    if anchor[1] == "m":
        y -= im.height / 2
    elif anchor[1] == "b":
        y -= im.height
    blit(base, im, x, y, alpha)


# ------------------------------------------------------------------ score
SR = 44100


def _fft_lp(x, fc):
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    X /= (1 + (fr / fc) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def make_bed(total):
    n = int(total * SR) + SR
    t = np.arange(n) / SR
    rng = np.random.default_rng(11)

    sw = 0.55 + 0.45 * np.sin(2 * np.pi * 0.045 * t - 1.2)
    drone = (np.sin(2 * np.pi * 43.65 * t) * 0.55
             + np.sin(2 * np.pi * 65.40 * t + 0.7) * 0.30
             + np.sin(2 * np.pi * 87.30 * t + 2.1) * 0.16).astype(np.float32)
    drone *= (0.55 + 0.45 * sw)

    air = _fft_lp(rng.normal(0, 1, n).astype(np.float32), 420)
    air /= (np.abs(air).max() + 1e-9)
    air *= (0.28 + 0.16 * np.sin(2 * np.pi * 0.09 * t + 0.4))

    hb = np.zeros(n, np.float32)
    beat = np.arange(int(0.55 * SR)) / SR
    thump = (np.sin(2 * np.pi * 46 * beat) * np.exp(-beat * 15)).astype(np.float32)
    dub = (np.sin(2 * np.pi * 38 * beat) * np.exp(-beat * 19)).astype(np.float32) * 0.7
    tt = NAR[3]
    while tt < total - 3:
        i = int(tt * SR)
        seg = min(len(thump), n - i)
        if seg > 0:
            hb[i:i + seg] += thump[:seg]
            j = i + int(0.26 * SR)
            seg2 = min(len(dub), n - j)
            if seg2 > 0:
                hb[j:j + seg2] += dub[:seg2]
        tt += 1.25
    hb /= (np.abs(hb).max() + 1e-9)

    ris = np.zeros(n, np.float32)
    r0, r1 = NAR[7] - 2.6, NAR[7] - 0.05
    i0, i1 = int(max(r0, 0) * SR), int(min(r1, total) * SR)
    if i1 > i0:
        m = i1 - i0
        tt_ = np.arange(m) / SR
        frac = tt_ / max(tt_[-1], 1e-3)
        ns = _fft_lp(rng.normal(0, 1, m).astype(np.float32), 900)
        ns /= (np.abs(ns).max() + 1e-9)
        tone = np.sin(2 * np.pi * (60 + 520 * frac ** 2.2) * tt_).astype(np.float32)
        ris[i0:i1] = (ns * 0.75 + tone * 0.5) * (frac ** 2.4)

    stings = np.zeros(n, np.float32)

    def sting(at, gain=1.0, bright=0.0):
        m = int(1.9 * SR)
        st = np.arange(m) / SR
        low = (np.sin(2 * np.pi * 37 * st) * np.exp(-st * 3.4)).astype(np.float32)
        body = _fft_lp(rng.normal(0, 1, m).astype(np.float32), 260)
        body /= (np.abs(body).max() + 1e-9)
        body *= np.exp(-st * 6).astype(np.float32)
        hi = (np.sin(2 * np.pi * 1180 * st) * np.exp(-st * 12)).astype(np.float32) * bright
        s = (low * 0.9 + body * 0.8 + hi) * gain
        i = int(max(at, 0) * SR)
        seg = min(m, n - i)
        if seg > 0:
            stings[i:i + seg] += s[:seg]

    sting(NAR[7] - 0.02, 0.95, 0.25)
    sting(NAR[8] - 0.02, 0.75, 0.18)
    sting(NAR[9] - 0.02, 0.55, 0.10)

    bed = drone * 0.55 + air * 0.42 + hb * 0.30 + ris * 0.55 + stings
    duck = np.ones(n, np.float32)
    for k, st in enumerate(NAR):
        a, b = int(max(st - 0.45, 0) * SR), int(min(st + DUR[k] + 0.25, total) * SR)
        duck[a:b] = 0.55
    k = int(0.55 * SR)
    ker = np.hanning(k).astype(np.float32)
    ker /= ker.sum()
    duck = np.convolve(duck, ker, mode="same").astype(np.float32)
    bed = bed[:int(total * SR)] * duck[:int(total * SR)]
    fi = int(1.2 * SR)
    bed[:fi] *= np.linspace(0, 1, fi)
    fo = int(2.4 * SR)
    if len(bed) > fo:
        bed[-fo:] *= np.linspace(1, 0, fo)
    return bed.astype(np.float32)


def build_mix():
    ff = _ffmpeg()
    os.makedirs("/tmp/hwav", exist_ok=True)
    items = []
    for k, p in enumerate(TAKES):
        wp = "/tmp/hwav/v%d.wav" % (k + 1)
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", p, "-ar", str(SR), "-ac", "1", wp],
                       check=True)
        with wave.open(wp) as fh:
            a = np.frombuffer(fh.readframes(fh.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        items.append(a)
    n = int(TOTAL * SR)
    voice = np.zeros(n, np.float32)
    for k, a in enumerate(items):
        i = int(round(NAR[k] * SR))
        seg = min(len(a), n - i)
        voice[i:i + seg] += a[:seg] * 0.92
        print("  v%d at %.2fs (%.2fs)" % (k + 1, NAR[k], len(a) / SR), flush=True)
    bed = make_bed(TOTAL)
    m = min(len(bed), n)
    mix = voice[:m] + bed[:m] * 0.30
    mix = np.tanh(mix * 1.05) * 0.92
    st = np.stack([mix, mix], 1)
    with wave.open(MIX, "wb") as fh:
        fh.setnchannels(2)
        fh.setsampwidth(2)
        fh.setframerate(SR)
        fh.writeframes((st * 32767).clip(-32768, 32767).astype(np.int16).tobytes())
    print("mix ok", round(m / SR, 2), "s", os.path.getsize(MIX))


def _ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


# ------------------------------------------------------------------ scenes
SCN = [
    dict(slug='শহর · রোকেয়া আপার দোকান', tag="মিঠু", role="কর্মচারী · বর্ণনাকারী", fit="wide", meter=(0.04, 0.12),
         cam=(700, 392, 1.07), cam1=(742, 372, 1.24), grade="warm", dk=(0.98, 0.86),
         flick=0.006, kind="title"),
    dict(slug='বাবার সতর্কতা', tag="বাবা", role="মিঠুর বাবা", fit="fill", meter=(0.12, 0.24),
         cam=(460, 292, 2.85), cam1=(452, 300, 3.06), grade="warm", dk=(0.82, 0.72),
         flick=0.010),
    dict(slug='প্রথম মাস', tag="মিঠু", role="কর্মচারী", fit="fill", meter=(0.24, 0.40),
         cam=(932, 284, 2.85), cam1=(906, 280, 3.06), grade="cold", dk=(0.92, 0.84),
         flick=0.014),
    dict(slug='তানিয়ার ভয়', tag="তানিয়া", role="মিঠুর বন্ধু", fit="fill", meter=(0.40, 0.50),
         cam=(268, 298, 2.85), cam1=(284, 304, 3.06), grade="cold", dk=(0.84, 0.78),
         flick=0.020),
    dict(slug='মায়ের কথা', tag="মা", role="মিঠুর মা", fit="fill", meter=(0.50, 0.60),
         cam=(1206, 298, 2.80), cam1=(1186, 304, 3.02), grade="cold", dk=(0.78, 0.70),
         flick=0.026),
    dict(slug='হাসি', tag="মিঠু", role="কর্মচারী", fit="fill", meter=(0.60, 0.68),
         cam=(944, 224, 3.00), cam1=(948, 220, 3.16), grade="cold", dk=(0.70, 0.62),
         flick=0.034),
    dict(slug='রাত · দোকানের পেছন', tag="মিঠু", role="কর্মচারী", fit="wide", meter=(0.68, 0.80),
         cam=(704, 378, 1.10), cam1=(689, 250, 2.30), grade="dark", dk=(0.62, 0.40),
         flick=0.055, lamp=True, rain=True),
    dict(slug='পেছনের ঘর', tag="রোকেয়া আপা", role="দোকানের মালিক", fit="fill", meter=(0.80, 0.92),
         cam=(700, 226, 2.86), cam1=(704, 234, 3.04), grade="dark", dk=(0.46, 0.58),
         flick=0.070, lamp=True, sting=True),
    dict(slug='প্রশ্ন', tag="রোকেয়া আপা", role="দোকানের মালিক", fit="fill", meter=(0.92, 0.99),
         cam=(687, 232, 2.94), cam1=(687, 240, 3.10), grade="ash", dk=(0.76, 0.52),
         flick=0.085, lamp=True),
    dict(slug='সকাল', tag="মিঠু", role="সকাল", fit="wide", meter=(0.99, 1.0),
         cam=(704, 384, 1.08), cam1=(704, 384, 1.17), grade="cold", dk=(0.72, 0.66),
         flick=0.010, law=True),
    dict(tag=None, kind="end"),
]

SAY = [
    "শহরের সবচেয়ে বড় দোকান রোকেয়া আপার। নতুন কর্মচারী ঢুকলেই উনি একটা কথা বলেন — এই দোকানে একটা বাতি জ্বলে। আর সেটা আমি।",
    "কাজ ভালো করো, বাবা। কিন্তু মনিবের সামনে নিজেকে বড় করে দেখিয়ো না। যে ছায়া আলোর চেয়ে লম্বা হয়, সে ছায়া থাকে না।",
    "প্রথম মাসেই আমি সবচেয়ে বেশি বিক্রি করলাম। ক্রেতারা আমার নাম ধরে ডাকতে লাগল। রোকেয়া আপা তখনো হাসতেন।",
    "মিঠু, মা গতকাল তোমার নাম শুনে কথা বলা বন্ধ করে দিলেন। উনি কিছু একটা করবেন। তুই দোকানে যাস না।",
    "ঘরে আলো জ্বালিয়ে রাখবি। রাতে দরজা খুলিস না। কেউ আমার গলায় ডাকলেও খুলিস না।",
    "আমি হেসে উঠলাম। আমি তো শুধু কাজ করেছি।",
    "সেই রাতে দোকানের পেছনের ঘরে একটা বাতি জ্বলছিল। আমি ভাবলাম, কেউ আলো নেভাতে ভুলে গেছে। আমি দরজা ঠেলে ঢুকলাম।",
    "তুমি খুব উজ্জ্বল, মিঠু। খুব উজ্জ্বল। এই দোকানে একটা বাতি জ্বলে। এত দিন ওটা আমি ছিলাম।",
    "এখন তুমি জ্বলছ। কিন্তু জ্বালানি কে দেবে?",
    "সকালে দোকান খোলা ছিল। রোকেয়া আপা হাসছিলেন। কাউন্টারে একটা নতুন ছেলে মাল সাজছিল। আমার চেয়ারে। আমার নামটা কেউ মনে করতে পারল না।",
    "",
]

CAPS, CAPSIZE = [], []
for _s in SAY:
    if _s:
        _im, _sz = fit_caption(_s)
    else:
        _im, _sz = None, 0
    CAPS.append(_im)
    CAPSIZE.append(_sz)


def panel_box(sc):
    if sc.get("fit") == "wide":
        return PX, PY + (PFH - WIDE_H) // 2, PFW, WIDE_H
    return PX, PY, PFW, PFH


def draw_panel(cv, sc, lt, dur, i, t):
    bw, bh = panel_box(sc)[2], panel_box(sc)[3]
    k = sine_io(lt / max(dur, 0.1) * 0.92 + 0.04)
    jx = wob(t, i * 1.7, 3.2)
    jy = wob(t, i * 2.9 + 1, 2.6)
    if sc.get("sting"):
        sh = max(0.0, 1.0 - lt / 0.75) ** 2
        jx += sh * 16 * math.sin(lt * 61)
        jy += sh * 13 * math.cos(lt * 47)
    cx = f(sc["cam"][0], sc["cam1"][0], k) + jx
    cy = f(sc["cam"][1], sc["cam1"][1], k) + jy
    z = f(sc["cam"][2], sc["cam1"][2], k) * (1 + 0.004 * math.sin(t * 1.3 + i))

    pan = crop_plate(GRADES[sc["grade"]], cx, cy, z, bw, bh)
    dk = f(sc["dk"][0], sc["dk"][1], clamp(lt / max(dur, 0.1), 0, 1))
    fl = sc.get("flick", 0.0)
    if fl:
        dk *= 1.0 + fl * (math.sin(lt * 23.0) * 0.5 + math.sin(lt * 7.3 + 2.0) * 0.5)
    if sc.get("sting"):
        dk *= 1.0 + 2.4 * max(0.0, 1.0 - lt / 0.35) ** 2
    pan = ImageEnhance.Brightness(pan).enhance(clamp(dk, 0.05, 2.2)).convert("RGBA")

    if sc.get("rain"):
        rl = rain_layer()
        ox = int((t * 210) % PFW)
        pan.alpha_composite(rl.crop((ox, 0, ox + bw, bh)))
        d = ImageDraw.Draw(pan)
        for n in range(5):
            x = (t * 130 + n * 197) % bw
            d.line([(x, 0), (x + 40, bh)], fill=(200, 214, 226, 26), width=1)
    if sc.get("lamp"):
        a = clamp(0.55 + 0.45 * math.sin(lt * 9.3) * math.sin(lt * 2.7 + 1.1), 0.12, 1.0)
        blit(pan, GLOW, bw * 0.60 - 250, bh * 0.42 - 250, 0.30 * a)

    pan.alpha_composite(VIG_WIDE if bh == WIDE_H else VIG_FILL)
    bx, by = panel_box(sc)[0], panel_box(sc)[1]
    cv.im.alpha_composite(_SHADOW, (bx - 60, by - 64))
    cv.im.paste(pan, (bx, by), MASK_WIDE if bh == WIDE_H else MASK_FILL)
    ImageDraw.Draw(cv.im).rounded_rectangle([bx, by, bx + bw - 1, by + bh - 1], 16,
                                            outline=(74, 58, 52, 255), width=2)


def header(cv, i, t):
    text_at(cv.im, (TX, 74), "আইন ১", 34, 700, RED, "lm")
    text_at(cv.im, (TX + 132, 76), "৪৮ আইন · বাংলা", 28, 600, DIM, "lm")
    text_at(cv.im, (W - TX, 76), "রবার্ট গ্রিন", 26, 500, DIM, "rm")
    ImageDraw.Draw(cv.im).line([(TX, 114), (W - TX, 114)], fill=(54, 46, 42, 255), width=2)


def speaker(cv, sc, a):
    if not sc.get("tag"):
        return
    text_at(cv.im, (TX, TY_OVER), sc["tag"], 42, 700, RED, "lm", a)
    wt = twidth(sc["tag"], 42, 700)
    d = ImageDraw.Draw(cv.im)
    d.line([(TX + wt + 24, TY_OVER + 2), (TX + wt + 50, TY_OVER + 2)],
           fill=(int(92 * a), int(64 * a), 56, 255), width=2)
    text_at(cv.im, (TX + wt + 64, TY_OVER + 2), sc["role"], 28, 500, DIM, "lm", a)


def caption(cv, i, lt):
    if not CAPS[i]:
        return
    a = clamp((lt - 0.16) / 0.5, 0, 1)
    dy = int((1 - expo(a)) * 14)
    blit(cv.im, CAPS[i], TX, TY_BODY + dy, a)


def lightmeter(cv, v, t, glow_boost=0.0):
    x0, x1 = TX + 96, W - TX
    y = METER_Y
    d = ImageDraw.Draw(cv.im)
    text_at(cv.im, (TX, y + 2), "আলো", 30, 600, DIM, "lm")
    d.line([(x0, y), (x1, y)], fill=(52, 44, 40, 255), width=8)
    fill = int((x1 - x0) * clamp(v, 0, 1))
    if fill > 2:
        fl = 1.0 + 0.05 * math.sin(t * 8.0)
        col = (int(clamp(RED[0] * fl, 0, 255)), int(RED[1] * fl), int(RED[2] * fl), 255)
        d.line([(x0, y), (x0 + fill, y)], fill=col, width=8)
        d.ellipse([x0 + fill - 7, y - 7, x0 + fill + 7, y + 7],
                  fill=(255, 210, 176, 255) if v > 0.5 else (240, 150, 120, 255))
    for k in range(11):
        tx = x0 + (x1 - x0) * k / 10.0
        d.line([(tx, y + 12), (tx, y + (20 if k % 5 == 0 else 16))], fill=(60, 50, 46, 255), width=2)
    text_at(cv.im, (W - TX, y + 40), "%s%%" % bn(int(round(clamp(v, 0, 1) * 100))), 26, 600, DIM, "rm")


SLUG_Y = 1494


def slug(cv, i, lt, text):
    a = clamp((lt - 0.55) / 0.6, 0, 1)
    if not text or a <= 0.02:
        return
    d = ImageDraw.Draw(cv.im)
    d.rectangle([TX, SLUG_Y - 9, TX + 9, SLUG_Y + 9], fill=(int(RED[0] * a), int(RED[1] * a),
                                                             int(RED[2] * a), 255))
    text_at(cv.im, (TX + 26, SLUG_Y + 1), text, 30, 600, DIM, "lm", a)


def footer(cv, i, t):
    d = ImageDraw.Draw(cv.im)
    d.line([(TX, FOOT_Y), (W - TX, FOOT_Y)], fill=(50, 42, 40, 255), width=2)
    for k in range(NSC):
        x = TX + k * 22
        d.rectangle([x, FOOT_Y + 16, x + 12, FOOT_Y + 22], fill=(RED if k == i else (58, 48, 44)) + (255,))
    text_at(cv.im, (W - TX, FOOT_Y - 26), "৪৮ আইন · পাঠ ১", 26, 600, DIM, "rm")


def cold_open(cv, lt):
    a = clamp((lt - 0.45) / 0.8, 0, 1) * (1 - clamp((lt - 3.15) / 0.55, 0, 1))
    if a > 0.02:
        im = timg("আইন ১", 190, 700, INK)
        blit(cv.im, im, (W - im.width) / 2, 620, a)
        im2 = timg("মনিবের চেয়ে বেশি জ্বলজ্বল করো না", 50, 600, RED)
        blit(cv.im, im2, (W - im2.width) / 2, 860, a)
        d = ImageDraw.Draw(cv.im)
        wl = int(260 * expo(clamp((lt - 1.1) / 0.9, 0, 1)))
        if wl:
            d.line([(W / 2 - wl / 2, 976), (W / 2 + wl / 2, 976)], fill=RED + (255,), width=3)
        text_at(cv.im, (W / 2, 1060), "একটা বাংলা ভৌতিক পাঠ", 30, 500, DIM, "mm", a * 0.9)


def law_card(cv, lt):
    a = clamp((lt - 0.15) / 0.55, 0, 1)
    text_at(cv.im, (W / 2, 668), "আইন ১", 148, 700, RED, "mm", a)
    im = plate_left("মনিবের চেয়ে বেশি জ্বলজ্বল করো না", 78, 700, INK, 880)
    blit(cv.im, im, (W - im.width) / 2, 826, clamp((lt - 0.5) / 0.7, 0, 1))
    d = ImageDraw.Draw(cv.im)
    wl = int(320 * expo(clamp((lt - 0.35) / 0.9, 0, 1)))
    if wl:
        d.line([(W / 2 - wl / 2, 1085), (W / 2 + wl / 2, 1085)], fill=RED + (255,), width=3)
    text_at(cv.im, (W / 2, 1160), "রবার্ট গ্রিন · ৪৮ Laws of Power — সারসংক্ষেপ", 28, 500, DIM, "mm",
            clamp((lt - 1.7) / 0.8, 0, 1))


def end_card(cv, lt, t):
    a = clamp((lt - 0.35) / 0.7, 0, 1)
    text_at(cv.im, (W / 2, 430), "আইন ১", 104, 700, RED, "mm", a)
    im = plate_left("মনের আলো নিভিয়ে দাও, নইলে মনিব তোমার আলো নিভিয়ে দেবে।", 48, 600, INK, 860)
    blit(cv.im, im, (W - im.width) / 2, 560, clamp((lt - 0.9) / 0.8, 0, 1))

    dia = 160
    gap = (W - 2 * 56 - 5 * dia) / 4
    for k, (nm, sx, sy) in enumerate(FACES):
        r = 92
        face = GRADES["cold"].crop((sx - r, sy - r, sx + r, sy + r)).resize((dia, dia), Image.LANCZOS)
        face = ImageEnhance.Brightness(face).enhance(1.55).convert("RGBA")
        m = rounded_mask(dia, dia, dia // 2)
        x = 56 + k * (dia + gap)
        y = 700
        st = expo(clamp((lt - 1.25 - k * 0.1) / 0.45, 0, 1))
        if st <= 0.01:
            continue
        cv.im.paste(face, (int(x), int(y)), m.point(lambda v: int(v * st)))
        ImageDraw.Draw(cv.im).ellipse([x - 2, y - 2, x + dia + 1, y + dia + 1],
                                      outline=(int(120 * st), 46, 34, 255), width=3)
        text_at(cv.im, (x + dia / 2, y + dia + 32), nm, 26, 600, (176, 162, 150), "mm", st)

    b = clamp((lt - 2.5) / 0.7, 0, 1)
    d = ImageDraw.Draw(cv.im)
    if b > 0.02:
        d.rounded_rectangle([W / 2 - 268, 1120, W / 2 + 268, 1224], 12,
                            outline=(int(RED[0] * b), int(RED[1] * b), int(RED[2] * b), 255), width=3)
    text_at(cv.im, (W / 2, 1172), "ফলো করো · প্রতি শুক্রবার নতুন আইন", 34, 600, INK, "mm", b)
    text_at(cv.im, (W / 2, 1300), "৪৮ আইন · বাংলা সিরিজ", 28, 500, DIM, "mm", clamp((lt - 3.1) / 0.7, 0, 1))
    if clamp((lt - 3.1) / 0.7, 0, 1) > 0.02:
        d.line([(TX, 1690), (W - TX, 1690)], fill=(46, 38, 36, 255), width=2)
        text_at(cv.im, (TX, 1730), "পাঠ ১ · ধনীরা নয়, আলো", 26, 500, DIM, "lm", clamp((lt - 3.3) / 0.7, 0, 1))
        text_at(cv.im, (W - TX, 1730), "৪৮ আইন", 26, 500, DIM, "rm", clamp((lt - 3.3) / 0.7, 0, 1))


def draw(t):
    i = 0
    for k in range(len(BOUNDS)):
        if t >= BOUNDS[k]:
            i = k
    lt = t - BOUNDS[i]
    dur = (BOUNDS[i + 1] if i + 1 < len(BOUNDS) else TOTAL) - BOUNDS[i]
    sc = SCN[i]
    cv = Surf()

    if sc.get("kind") == "title":
        if lt > 3.05:
            draw_panel(cv, sc, lt - 3.05, dur - 3.05, i, t)
        cold_open(cv, lt)
        header(cv, i, t)
        if lt > 3.4:
            speaker(cv, sc, clamp((lt - 3.4) / 0.45, 0, 1))
        if t >= NAR[0] - 0.6:
            caption(cv, i, t - NAR[0] + 0.2)
        slug(cv, i, lt, sc.get("slug"))
        lightmeter(cv, f(sc["meter"][0], sc["meter"][1], lt / max(dur, 0.1) * 1.3), t)
        footer(cv, i, t)
    elif sc.get("kind") == "end":
        end_card(cv, lt, t)
    else:
        draw_panel(cv, sc, lt, dur, i, t)
        header(cv, i, t)
        speaker(cv, sc, clamp(lt / 0.45, 0, 1))
        caption(cv, i, lt)
        slug(cv, i, lt, sc.get("slug"))
        lightmeter(cv, f(sc["meter"][0], sc["meter"][1], lt / max(dur, 0.1) * 1.25), t)
        footer(cv, i, t)
        if sc.get("law"):
            law_lt = lt - (dur - 5.0)
            if law_lt > 0:
                dark = clamp(law_lt / 0.45, 0, 1)
                veil = Image.new("RGBA", (W, H), BG + (int(255 * dark),))
                cv.im.alpha_composite(veil)
                law_card(cv, law_lt)

    out = cv.im.convert("RGB")
    out = Image.blend(out, grain(), 0.075)
    out.paste((0, 0, 0), (0, 0), FRAME_VIG)
    return out


def main():
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1])
        os.makedirs("frames", exist_ok=True)
        i = max(k for k, b in enumerate(BOUNDS) if t >= b)
        draw(t).save("frames/still-%06.2f.png" % t)
        print("still", t, "scene", i, "lt", round(t - BOUNDS[i], 2))
        return

    print("NAR", NAR)
    print("BOUNDS", BOUNDS)
    print("total", TOTAL, "frames", NF, "scenes", NSC, flush=True)
    print("caption sizes", CAPSIZE, flush=True)

    if "--mix" in sys.argv:
        build_mix()
        return

    if "--seg" in sys.argv:
        j = sys.argv.index("--seg")
        a, b, sp = int(sys.argv[j + 1]), int(sys.argv[j + 2]), sys.argv[j + 3]
        cmd = [_ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", sp]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(a, b):
            proc.stdin.write(draw(i / FPS).tobytes())
            if (i - a) % 150 == 0:
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
        subprocess.run([_ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", "segs.txt", "-i", MIX, "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT], check=True)
        print("joined", os.path.getsize(OUT))
        return


if __name__ == "__main__":
    main()
