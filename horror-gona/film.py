"""horror-gona — গোনা (The Counting).

A two-minute Bangla ghost story built from the four portrait cards in img/: each card's
cream paper is flood-filled away (see key.py) and the bust is staged as a cut-out in the
dark, bottom-faded so it dissolves into black instead of standing on a floor.

Timing is probed from the voice takes:
    NAR[k] = start of spoken line k
    BOUNDS = one cut per scene, 0.35 s before the line it carries

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
BG = (8, 9, 10)
INK = (237, 230, 216)
DIM = (139, 130, 121)
AMBER = (180, 85, 58)
AMBER_D = (94, 40, 26)
BONE = (200, 190, 174)

TX = 72
TY_TAG = 1398
TY_BODY = 1454
BODY_MAXW = 936
FOOT_Y = 1836
BASE_Y = 1402          # where the busts stop (they fade out below this)
HEAD_CROP = 1560       # keep the head and shoulders, drop the chest

TAKES = ["audio/v%d.mp3" % i for i in range(1, 11)]
START = 5.4
GAPS = [1.4, 1.5, 1.6, 1.5, 1.8, 2.2, 2.6, 2.0, 2.2]
TAIL = 14.0
MIX = "audio/mix.wav"
OUT = os.environ.get("OUT", "horror-gona-1080x1920.mp4")

CUT = {"rahim": "img/rahim-cut.png", "fatema": "img/fatema-cut.png",
       "karim": "img/karim-cut.png", "bulbul": "img/bulbul-cut.png"}


def bn(n):
    return str(n).translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def f(a, b, t):
    return a + (b - a) * clamp(t, 0.0, 1.0)


def expo(k):
    return 1 - (1 - clamp(k, 0.0, 1.0)) ** 3


def sine_io(k):
    return 0.5 - 0.5 * math.cos(math.pi * clamp(k, 0.0, 1.0))


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
BOUNDS = [0.0] + [round(NAR[k] - 0.35, 3) for k in range(1, 10)] + [round(SPEECH_END + 0.75, 3)]
TOTAL = round(BOUNDS[-1] + TAIL, 3)
NF = int(round(TOTAL * FPS))
NSC = len(BOUNDS)


# ------------------------------------------------------------------ sprites
_cut, _spr, _tint = {}, {}, {}


FACE_TARGET = 880      # px from the top of the hair to the neck, at scale 1.0


def cut(name):
    """keyed bust, faded out from the neck down, cached with its neck line"""
    if name not in _cut:
        im = Image.open(CUT[name]).convert("RGBA")
        im = im.crop((0, 0, im.width, min(HEAD_CROP, im.height)))
        al = np.asarray(im.getchannel("A"), np.float32) / 255.0
        h, w = al.shape
        ws = (al > 0.5).sum(1).astype(np.float32)
        k = np.ones(9, np.float32) / 9
        ws = np.convolve(ws, k, mode="same")
        lo, hi = int(0.45 * h), int(0.88 * h)
        neck = lo + int(np.argmin(ws[lo:hi]))          # narrowest point between jaw and shoulders
        neck = max(neck, int(0.52 * h))
        y = np.arange(h, dtype=np.float32)[:, None]
        ramp = np.clip((neck + 0.06 * h - y) / (0.34 * h), 0, 1)
        a = (al * (ramp * ramp * (3 - 2 * ramp))).clip(0, 1)
        im.putalpha(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)))
        _cut[name] = (im, neck)
        print("  cut %s: %dx%d neck at %d (%.0f%%)" % (name, im.width, im.height, neck, 100.0 * neck / h))
    return _cut[name]


def natural(name):
    im, neck = cut(name)
    return int(im.height * FACE_TARGET / max(neck, 1))


def sprite(name, h, ang=0.0, dim=1.0, alpha=1.0):
    key = (name, int(round(h / 4.0)), int(round(ang * 2)), int(round(dim * 20)), int(round(alpha * 20)))
    if key in _spr:
        return _spr[key]
    im = cut(name)[0]
    nh = max(8, key[1] * 4)
    nw = max(8, int(im.width * nh / im.height))
    im = im.resize((nw, nh), Image.LANCZOS)
    if key[2]:
        im = im.rotate(-key[2] / 2.0, resample=Image.BICUBIC, expand=True)
    if abs(dim - 1.0) > 0.02:
        im = ImageEnhance.Brightness(im).enhance(clamp(dim, 0.05, 1.6))
    if alpha < 0.98:
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    if len(_spr) > 400:
        _spr.clear()
    _spr[key] = im
    return im


def puppet(cv, name, x, y, h, ang=0.0, dim=1.0, alpha=1.0):
    if alpha <= 0.02:
        return
    im = sprite(name, h, ang, dim, alpha)
    cv.alpha_composite(im, (int(x - im.width / 2), int(y - im.height)))


def lifelike(t, seed, amp=1.0):
    """breath + lean, quantised so the sprite cache actually hits"""
    dy = amp * (2.2 * math.sin(t * 1.55 + seed) + 1.1 * math.sin(t * 2.9 + seed * 2))
    ang = amp * (0.85 * math.sin(t * 0.62 + seed * 1.7) + 0.35 * math.sin(t * 1.9 + seed))
    return dy, ang


# ------------------------------------------------------------------ furniture
def _vignette(w, h, strength=200, power=2.2):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (x - w / 2) / (w / 2)
    ny = (y - h / 2) / (h / 2)
    r = np.sqrt(nx ** 2 * 0.9 + ny ** 2) / 1.24
    a = (np.clip(r, 0, 1) ** power * strength).astype(np.uint8)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im.putalpha(Image.fromarray(a))
    return im


VIG = _vignette(W, H, 205, 2.1)


def _glow(r=300, col=(255, 176, 104)):
    s = r * 2
    y, x = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.sqrt((x - r) ** 2 + (y - r) ** 2) / r
    a = (np.clip(1 - d, 0, 1) ** 2.4 * 255).astype(np.uint8)
    im = Image.new("RGBA", (s, s), col + (0,))
    im.putalpha(Image.fromarray(a))
    return im


GLOW = _glow(300, (255, 168, 96))
GLOW_COLD = _glow(360, (150, 176, 208))

GRAIN = None


def grain():
    global GRAIN
    if GRAIN is None:
        rng = np.random.default_rng(5)
        n = rng.normal(0, 7.0, (H // 2, W // 2)).clip(-20, 20)
        n = np.repeat(np.repeat(n, 2, axis=0), 2, axis=1)[:H, :W]
        base = np.zeros((H, W, 3), np.uint8) + 128
        GRAIN = Image.fromarray((base + n[:, :, None]).clip(0, 255).astype(np.uint8))
    return GRAIN


DUST = None


def dust():
    global DUST
    if DUST is None:
        rng = np.random.default_rng(17)
        DUST = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(6, 26),
                 rng.uniform(0.4, 1.0), rng.uniform(0, 6.28), rng.uniform(8, 30))
                for _ in range(46)]
    return DUST


# ------------------------------------------------------------------ type
_cap, _TIMG, _TW = {}, {}, {}


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


def plate(text, size, weight, color, maxw):
    key = (text, size, weight, color, maxw)
    if key in _cap:
        return _cap[key]
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
    lh = int(size * 1.42)
    wid = max(i.width for i in imgs)
    out = Image.new("RGBA", (wid + 6, lh * len(imgs) + 8), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        out.alpha_composite(im, (0, i * lh + (lh - im.height) // 2))
    _cap[key] = out
    return out


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


def _lp(x, fc):
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    X /= (1 + (fr / fc) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def make_bed(total):
    n = int(total * SR) + SR
    t = np.arange(n) / SR
    rng = np.random.default_rng(23)

    sw = 0.55 + 0.45 * np.sin(2 * np.pi * 0.041 * t - 1.1)
    drone = (np.sin(2 * np.pi * 40.8 * t) * 0.55
             + np.sin(2 * np.pi * 61.2 * t + 0.7) * 0.30
             + np.sin(2 * np.pi * 81.6 * t + 2.1) * 0.15).astype(np.float32)
    drone *= (0.5 + 0.5 * sw)

    air = _lp(rng.normal(0, 1, n).astype(np.float32), 380)
    air /= (np.abs(air).max() + 1e-9)
    air *= (0.26 + 0.14 * np.sin(2 * np.pi * 0.07 * t + 0.3))

    # clock ticks through the night scenes (lines 5-8)
    tick = np.zeros(n, np.float32)
    m = int(0.16 * SR)
    tk = np.arange(m) / SR
    click = ((np.sin(2 * np.pi * 2100 * tk) * np.exp(-tk * 90)).astype(np.float32) * 0.7
             + _lp(rng.normal(0, 1, m).astype(np.float32), 3000) * np.exp(-tk * 60) * 0.35)
    click /= (np.abs(click).max() + 1e-9)
    tt = NAR[4]
    k = 0
    while tt < min(NAR[7] + 2.0, total):
        i = int(tt * SR)
        seg = min(m, n - i)
        if seg > 0:
            tick[i:i + seg] += click[:seg] * (0.55 if k % 2 else 0.9)
        k += 1
        tt += 1.0

    # heartbeat from line 6 on
    hb = np.zeros(n, np.float32)
    b = np.arange(int(0.55 * SR)) / SR
    thump = (np.sin(2 * np.pi * 44 * b) * np.exp(-b * 15)).astype(np.float32)
    dub = (np.sin(2 * np.pi * 36 * b) * np.exp(-b * 20)).astype(np.float32) * 0.65
    tt = NAR[5]
    while tt < total - 3:
        i = int(tt * SR)
        seg = min(len(thump), n - i)
        if seg > 0:
            hb[i:i + seg] += thump[:seg]
            j = i + int(0.26 * SR)
            s2 = min(len(dub), n - j)
            if s2 > 0:
                hb[j:j + s2] += dub[:s2]
        tt += 1.18
    hb /= (np.abs(hb).max() + 1e-9)

    # riser into the count, sting on the ninth
    ris = np.zeros(n, np.float32)
    r0, r1 = NAR[5] - 2.2, NAR[5] - 0.05
    i0, i1 = int(max(r0, 0) * SR), int(min(r1, total) * SR)
    if i1 > i0:
        m2 = i1 - i0
        tt_ = np.arange(m2) / SR
        fr = tt_ / max(tt_[-1], 1e-3)
        ns = _lp(rng.normal(0, 1, m2).astype(np.float32), 950)
        ns /= (np.abs(ns).max() + 1e-9)
        tone = np.sin(2 * np.pi * (55 + 500 * fr ** 2.2) * tt_).astype(np.float32)
        ris[i0:i1] = (ns * 0.7 + tone * 0.5) * (fr ** 2.5)

    stings = np.zeros(n, np.float32)

    def sting(at, gain=1.0, bright=0.0):
        m3 = int(2.0 * SR)
        st = np.arange(m3) / SR
        low = (np.sin(2 * np.pi * 35 * st) * np.exp(-st * 3.2)).astype(np.float32)
        body = _lp(rng.normal(0, 1, m3).astype(np.float32), 250)
        body /= (np.abs(body).max() + 1e-9)
        body *= np.exp(-st * 6).astype(np.float32)
        hi = (np.sin(2 * np.pi * 1240 * st) * np.exp(-st * 11)).astype(np.float32) * bright
        s = (low * 0.9 + body * 0.75 + hi) * gain
        i = int(max(at, 0) * SR)
        seg = min(m3, n - i)
        if seg > 0:
            stings[i:i + seg] += s[:seg]

    sting(NAR[5] - 0.02, 0.95, 0.22)
    sting(NAR[8] - 0.02, 0.70, 0.14)
    sting(NAR[9] - 0.02, 0.45, 0.08)

    bed = drone * 0.52 + air * 0.40 + tick * 0.26 + hb * 0.26 + ris * 0.5 + stings
    duck = np.ones(n, np.float32)
    for k, st in enumerate(NAR):
        a, b_ = int(max(st - 0.45, 0) * SR), int(min(st + DUR[k] + 0.25, total) * SR)
        duck[a:b_] = 0.55
    kk = int(0.55 * SR)
    ker = np.hanning(kk).astype(np.float32)
    ker /= ker.sum()
    duck = np.convolve(duck, ker, mode="same").astype(np.float32)
    bed = bed[:int(total * SR)] * duck[:int(total * SR)]
    fi = int(0.9 * SR)
    bed[:fi] *= np.linspace(0, 1, fi)
    fo = int(2.6 * SR)
    if len(bed) > fo:
        bed[-fo:] *= np.linspace(1, 0, fo)
    return bed.astype(np.float32)


def build_mix():
    ff = _ffmpeg()
    os.makedirs("/tmp/gwav", exist_ok=True)
    items = []
    for k, p in enumerate(TAKES):
        wp = "/tmp/gwav/v%d.wav" % (k + 1)
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", p, "-ar", str(SR), "-ac", "1", wp], check=True)
        with wave.open(wp) as fh:
            items.append(np.frombuffer(fh.readframes(fh.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0)
    n = int(TOTAL * SR)
    voice = np.zeros(n, np.float32)
    for k, a in enumerate(items):
        i = int(round(NAR[k] * SR))
        seg = min(len(a), n - i)
        voice[i:i + seg] += a[:seg] * 0.92
        print("  v%d at %.2fs (%.2fs)" % (k + 1, NAR[k], len(a) / SR), flush=True)
    bed = make_bed(TOTAL)
    m = min(len(bed), n)
    mix = np.tanh((voice[:m] + bed[:m] * 0.28) * 1.05) * 0.92
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
# cast: (name, x, height, dim, seed)
SCN = [
    dict(slug="দাদির বাড়ি", nums=[], cast=[("rahim", 540, 1.05, 1.0, 1.0)]),
    dict(slug="চাচার সতর্কতা", nums=[], cast=[("karim", 360, 1.03, 1.0, 2.0),
                                            ("rahim", 856, 0.77, 0.42, 3.0)]),
    dict(slug="ফাতেমার কথা", nums=[], cast=[("fatema", 470, 1.04, 1.0, 4.0),
                                           ("rahim", 900, 0.75, 0.40, 5.0)]),
    dict(slug="বুলবুল", nums=[], cast=[("bulbul", 470, 1.00, 1.0, 6.0),
                                      ("fatema", 902, 0.76, 0.40, 7.0)]),
    dict(slug="দুই চল্লিশ", nums=[4, 5, 6], cast=[("rahim", 540, 1.02, 0.92, 8.0)]),
    dict(slug="সাত · আট · নয়", nums=[7, 8, 9], sting=True,
         cast=[("fatema", 540, 1.06, 1.0, 9.0)]),
    dict(slug="সাড়া দিও না", nums=[], cast=[("bulbul", 540, 1.00, 0.95, 10.0)]),
    dict(slug="সকাল", nums=[1, 2, 3], cold=True,
         cast=[("fatema", 540, 0.98, 0.85, 11.0)]),
    dict(slug="কেউ মনে করে না", nums=[], cast=[("karim", 540, 1.01, 0.9, 12.0)]),
    dict(slug="নাম", nums=[], cast=[("rahim", 540, 1.03, 0.95, 13.0)]),
    dict(slug=None, kind="end"),
]

SAY = [
    "দাদির বাড়িটা বিক্রি করতে ফিরে এসেছিলাম। প্রথম রাতে ঘর থেকে শব্দ এল। কেউ গুনছে। এক, দুই, তিন। আমি আলো জ্বালালাম। ঘরটা খালি।",
    "গোনাটা থামাবি না, আর সাড়াও দিবি না। নয় পেরোলে ও একটা নাম ডাকবে। তুই সাড়া দিলে গোনা শেষ, আর তুই ওই ঘরেই থেকে যাবি।",
    "চাচা, এসব ভূতের গল্প আমার জন্য না। আমি আজ রাতটা এই ঘরেই থাকব। দেখি, কে গোনে।",
    "দিদি, কাল রাতে আমিও গুনেছি। সাত পর্যন্ত গুনলাম। তারপর দেখলাম, আওয়াজটা আমার গলা থেকে আসছে। আমি থামাতে পারছি না।",
    "রাত দুটো চল্লিশে গোনা শুরু হলো। আমি শুনলাম, চার, পাঁচ, ছয়।",
    "সাত। আট। নয়। তারপর কেউ আমার নাম ধরে ডাকল। খুব মিষ্টি করে। দুবার।",
    "দিদি, সাড়া দিও না। প্লিজ, সাড়া দিও না।",
    "সকালে ঘরটা খালি ছিল। ফাতেমা জানালার পাশে বসে ছিল, চুল আঁচড়াচ্ছিল, আর গুনছিল। এক, দুই, তিন।",
    "এখন ও গোনে। ওর নাম ধরে ডাকলে ও ফিরে আসবে। কিন্তু আমরা কেউ ওর নাম মনে করতে পারি না।",
    "আজও আমি ভাবি, মেয়েটার নামটা কী ছিল? মনে পড়ে না।",
    "",
]

TAG = ["রহিম", "করিম চাচা", "ফাতেমা", "বুলবুল", "রহিম", "ফাতেমা", "বুলবুল", "রহিম",
       "করিম চাচা", "রহিম", None]
ROLE = ["ভাড়াটে নাতি", "প্রতিবেশী", "সাহসী", "ছোট ছেলে", "", "", "", "", "", "", None]

CAPS = [plate(s, 54, 600, INK, BODY_MAXW) if s else None for s in SAY]


def ghost_nums(cv, nums, lt, dur, alpha=0.085):
    """the count, as numerals barely there behind the figures"""
    if not nums:
        return
    for k, n in enumerate(nums):
        a = alpha * clamp((lt - 0.25 - k * 0.30) / 0.5, 0, 1)
        if a <= 0.01:
            continue
        im = timg(bn(n), 260, 700, (126, 50, 34))
        blit(cv, im, W / 2 - im.width / 2 + (k - 1) * 232, 250, a)


def draw_scene(i, sc, lt, dur, t):
    cv = Image.new("RGBA", (W, H), BG + (255,))
    # room light behind the cast
    coast = clamp((lt) / max(dur, 0.1), 0, 1)
    gl = GLOW_COLD if sc.get("cold") else GLOW
    ga = (0.34 + 0.10 * math.sin(t * 0.7 + i)) * (1.0 - 0.35 * coast if sc.get("cold") else 1.0)
    blit(cv, gl, W / 2 - 300, 380 - 300 + 40, ga)

    ghost_nums(cv, sc.get("nums", []), lt, dur)

    # dust
    for (dx, dy, sp, sz, ph, drift) in dust():
        y = (dy - t * sp) % H
        x = dx + math.sin(t * 0.5 + ph) * drift
        a = 30 + 26 * math.sin(t * 1.7 + ph)
        d = ImageDraw.Draw(cv)
        d.ellipse([x - sz / 2, y - sz / 2, x + sz / 2, y + sz / 2], fill=(196, 186, 170, int(a)))

    # cast
    for k, (name, x, hgt, dim, seed) in enumerate(sc["cast"]):
        hgt = int(natural(name) * hgt)
        dy, ang = lifelike(t, seed, 1.0 if k == 0 else 0.7)
        enter = expo(clamp((lt - 0.04 * k) / 0.5, 0, 1))
        y = BASE_Y + dy + int((1 - enter) * 26)
        xo = x + (1 - enter) * (34 if x > W / 2 else -34) + wob(t, seed, 4)
        d2 = dim * (0.86 + 0.14 * enter) * (1.10 if k == 0 else 1.0)
        if sc.get("sting"):
            sh = max(0.0, 1.0 - lt / 0.6) ** 2
            xo += sh * 14 * math.sin(lt * 57)
            y += sh * 10 * math.cos(lt * 43)
        puppet(cv, name, xo, y, hgt, ang, d2, enter)
        if k == 0:            # the speaker is lit
            la = 0.22 + 0.06 * math.sin(t * 2.3)
            blit(cv, GLOW if not sc.get("cold") else GLOW_COLD, xo - 300, y - hgt * 0.55 - 300, la)

    # flash on the ninth
    if sc.get("sting"):
        fl = max(0.0, 1.0 - lt / 0.30) ** 2
        if fl > 0.01:
            cv.alpha_composite(Image.new("RGBA", (W, H), (255, 126, 96, int(30 * fl))))

    return cv


def header(cv, i, t):
    text_at(cv, (TX, 84), "গোনা", 40, 700, AMBER, "lm")
    text_at(cv, (TX + 118, 86), "ভৌতিক পাঠ · ১", 28, 600, DIM, "lm")
    text_at(cv, (W - TX, 86), "বাংলা ভৌতিক গল্প", 26, 500, DIM, "rm")
    ImageDraw.Draw(cv).line([(TX, 124), (W - TX, 124)], fill=(46, 40, 37, 255), width=2)


def caption(cv, i, lt):
    if not CAPS[i]:
        return
    a = clamp((lt - 0.14) / 0.45, 0, 1)
    tg = TAG[i]
    if tg:
        text_at(cv, (TX, TY_TAG), tg, 36, 700, AMBER, "lm", a)
        wt = twidth(tg, 36, 700)
        ImageDraw.Draw(cv).line([(TX + wt + 20, TY_TAG + 2), (TX + wt + 42, TY_TAG + 2)],
                                fill=(int(110 * a), int(52 * a), 36, 255), width=2)
        if ROLE[i]:
            text_at(cv, (TX + wt + 56, TY_TAG + 2), ROLE[i], 26, 500, DIM, "lm", a)
    blit(cv, CAPS[i], TX, TY_BODY + int((1 - expo(a)) * 12), a)


def footer(cv, i, t):
    d = ImageDraw.Draw(cv)
    d.line([(TX, FOOT_Y), (W - TX, FOOT_Y)], fill=(44, 38, 35, 255), width=2)
    for k in range(NSC):
        x = TX + k * 22
        d.rectangle([x, FOOT_Y + 16, x + 12, FOOT_Y + 22], fill=(AMBER if k == i else (52, 44, 40)) + (255,))
    text_at(cv, (W - TX, FOOT_Y - 26), "ভৌতিক পাঠ · ১", 26, 600, DIM, "rm")


def cold_open(cv, lt):
    a = clamp((lt - 0.4) / 0.9, 0, 1) * (1 - clamp((lt - 3.5) / 0.6, 0, 1))
    if a <= 0.02:
        return
    im = timg("গোনা", 176, 700, INK)
    blit(cv, im, (W - im.width) / 2, 690, a)
    im2 = timg("একটা বাংলা ভৌতিক গল্প", 44, 600, AMBER)
    blit(cv, im2, (W - im2.width) / 2, 900, a)
    for k, n in enumerate((1, 2, 3)):
        na = a * clamp((lt - 1.3 - k * 0.45) / 0.4, 0, 1)
        if na > 0.01:
            im3 = timg(bn(n), 132, 700, (160, 66, 44))
            blit(cv, im3, W / 2 + (k - 1) * 190 - im3.width / 2, 1024, na * 0.92)


def end_card(cv, lt, t):
    a = clamp((lt - 0.4) / 0.7, 0, 1)
    im = timg("গোনা", 138, 700, AMBER)
    blit(cv, im, (W - im.width) / 2, 452, a)
    p = plate("কেউ নাম ধরে ডাকলে সাড়া দিও না।", 48, 600, INK, 860)
    blit(cv, p, (W - p.width) / 2, 664, clamp((lt - 0.9) / 0.7, 0, 1))

    for k, name in enumerate(("rahim", "fatema", "karim", "bulbul")):
        st = expo(clamp((lt - 1.4 - k * 0.12) / 0.45, 0, 1))
        if st <= 0.01:
            continue
        hgt = 360
        im2 = cut(name)[0]
        nwid = int(im2.width * hgt / im2.height)
        tile = im2.resize((nwid, hgt), Image.LANCZOS)
        x = 62 + k * 241 + (231 - nwid) // 2
        y = 850
        blit(cv, tile, x, y, st * 0.92)

    b = clamp((lt - 2.6) / 0.7, 0, 1)
    d = ImageDraw.Draw(cv)
    if b > 0.02:
        d.rounded_rectangle([W / 2 - 258, 1290, W / 2 + 258, 1394], 12,
                            outline=(int(AMBER[0] * b), int(AMBER[1] * b), int(AMBER[2] * b), 255), width=3)
    text_at(cv, (W / 2, 1342), "ফলো করো · প্রতি শুক্রবার নতুন গল্প", 32, 600, INK, "mm", b)
    text_at(cv, (W / 2, 1462), "ভৌতিক পাঠ · বাংলা সিরিজ", 28, 500, DIM, "mm", clamp((lt - 3.2) / 0.7, 0, 1))
    fa = clamp((lt - 3.4) / 0.8, 0, 1)
    if fa > 0.02:
        d.line([(TX, 1704), (W - TX, 1704)], fill=(46, 40, 37, int(255 * fa)), width=2)
        text_at(cv, (TX, 1744), "গোনা · ভৌতিক পাঠ ১", 26, 500, DIM, "lm", fa)
        text_at(cv, (W - TX, 1744), "৩:০০ মিনিট", 26, 500, DIM, "rm", fa)


def draw(t):
    i = 0
    for k in range(len(BOUNDS)):
        if t >= BOUNDS[k]:
            i = k
    lt = t - BOUNDS[i]
    dur = (BOUNDS[i + 1] if i + 1 < len(BOUNDS) else TOTAL) - BOUNDS[i]
    sc = SCN[i]

    if sc.get("kind") == "end":
        cv = Image.new("RGBA", (W, H), BG + (255,))
        blit(cv, GLOW, W / 2 - 300, 200, 0.16)
        end_card(cv, lt, t)
        out = cv.convert("RGB")
    elif i == 0:
        cv = Image.new("RGBA", (W, H), BG + (255,))
        if t > NAR[0] - 1.3:
            sc2 = draw_scene(i, sc, max(0.0, lt - (NAR[0] - 1.3 - BOUNDS[0])), dur, t)
            k = clamp((t - (NAR[0] - 1.3)) / 0.6, 0, 1)
            blit(cv, sc2, 0, 0, k)
        cold_open(cv, lt)
        header(cv, i, t)
        if lt > 3.2:
            caption(cv, i, max(0.0, t - NAR[0] + 0.2))
        footer(cv, i, t)
        out = cv.convert("RGB")
    else:
        cv = draw_scene(i, sc, lt, dur, t)
        header(cv, i, t)
        caption(cv, i, lt)
        footer(cv, i, t)
        out = cv.convert("RGB")

    # fade from black at the top of each cut, and a slow pulse on the last one
    out = Image.blend(out, grain(), 0.085)
    out.paste((0, 0, 0), (0, 0), VIG)
    if i == 0 and lt < 0.5:
        k = clamp(lt / 0.5, 0, 1)
        out = ImageEnhance.Brightness(out).enhance(0.2 + 0.8 * k)
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
