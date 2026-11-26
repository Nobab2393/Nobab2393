"""horror-claude-law1 — নিয়ম ১ (Rule One).

A two-minute Bangla ghost story told with the five Claude-style characters from
../characters-bd-claude/. Their cut-outs are already transparent and trimmed, so
unlike horror-gona there is no keying step: the full body simply stands on the
floor at FEET and is lit from behind.

Unlike the card film, the frame itself follows the same flat-vector language:
flat ink ground, one flat moon, flat horizon, one coral lamp, no photographic
gradients. The only soft edges are the vignette and the light bloom behind the
speaker.

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

BG = (12, 13, 15)
DAWN = (34, 38, 44)
CREAM = (240, 238, 230)
GREY = (168, 162, 152)
DIMT = (128, 122, 114)
CORAL = (217, 119, 87)
CORAL_D = (122, 56, 38)
SAGE = (154, 165, 118)
SLATE = (124, 147, 168)

TX = 72
TY_TAG = 1372
TY_BODY = 1428
BODY_MAXW = 936
FOOT_Y = 1836

FEET = 1330          # every character stands here
BASE_H = 1150        # rafiq at scene scale 1.0
TAKES = ["audio/v%d.mp3" % i for i in range(1, 10)]
START = 5.6
GAPS = [1.5, 1.9, 1.6, 1.7, 1.6, 2.0, 1.4, 1.6]
TAIL = 12.4
MIX = "audio/mix.wav"
OUT = os.environ.get("OUT", "horror-claude-law1-1080x1920.mp4")

# name -> (file, height relative to rafiq)
CAST = {
    "rafiq": ("img/c1-rickshaw-cut.png", 1.00),
    "mim": ("img/c2-schoolgirl-cut.png", 0.86),
    "teacher": ("img/c3-teacher-cut.png", 0.97),
    "rohima": ("img/c4-vendor-cut.png", 0.93),
    "tutu": ("img/c5-boy-cut.png", 0.72),
}


def bn(n):
    return str(n).translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def f(a, b, t):
    return a + (b - a) * clamp(t, 0.0, 1.0)


def expo(k):
    return 1 - (1 - clamp(k, 0.0, 1.0)) ** 3


def overshoot(k):
    k = clamp(k, 0.0, 1.0)
    c = 1.70158
    return 1 + (c + 1) * (k - 1) ** 3 + c * (k - 1) ** 2


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
BOUNDS = [0.0] + [round(NAR[k] - 0.35, 3) for k in range(1, len(TAKES))] + \
         [round(SPEECH_END + 0.75, 3)]
TOTAL = round(BOUNDS[-1] + TAIL, 3)
NF = int(round(TOTAL * FPS))
NSC = len(BOUNDS)


# ------------------------------------------------------------------ sprites
_spr, _raw = {}, {}


def raw(name):
    if name not in _raw:
        _raw[name] = Image.open(CAST[name][0]).convert("RGBA")
    return _raw[name]


def sprite(name, h, ang=0.0, dim=1.0, alpha=1.0, tint=(1.0, 1.0, 1.0)):
    key = (name, int(round(h / 3.0)), int(round(ang * 2)), int(round(dim * 24)),
           int(round(alpha * 24)), tuple(int(c * 40) for c in tint))
    if key in _spr:
        return _spr[key]
    im = raw(name)
    nh = max(8, int(round(h)))
    nw = max(8, int(round(im.width * nh / im.height)))
    out = im.resize((nw, nh), Image.LANCZOS)
    if key[2]:
        out = out.rotate(key[2] / 2.0, resample=Image.BICUBIC, expand=True)
    if abs(dim - 1.0) > 0.02:
        a = out.getchannel("A")
        rgb = ImageEnhance.Brightness(out.convert("RGB")).enhance(clamp(dim, 0.04, 1.4))
        out = rgb.convert("RGBA")
        out.putalpha(a)
    if any(abs(c - 1.0) > 0.01 for c in tint):
        from PIL import ImageChops
        a = out.getchannel("A")
        lay = Image.new("RGB", out.size, tuple(int(clamp(c, 0, 1) * 255) for c in tint))
        out = ImageChops.multiply(out.convert("RGB"), lay).convert("RGBA")
        out.putalpha(a)
    if alpha < 0.99:
        out.putalpha(out.getchannel("A").point(lambda v: int(v * alpha)))
    if len(_spr) > 600:
        _spr.clear()
    _spr[key] = out
    return out


def puppet(cv, name, x, feet, h, ang=0.0, dim=1.0, alpha=1.0, tint=(1.0, 1.0, 1.0)):
    if alpha <= 0.02:
        return
    im = sprite(name, h, ang, dim, alpha, tint)
    cv.alpha_composite(im, (int(x - im.width / 2), int(feet - im.height)))


def height(name, scale):
    return BASE_H * CAST[name][1] * scale


def lifelike(t, seed, amp=1.0):
    """breath + lean, quantised by the sprite cache"""
    dy = amp * (2.0 * math.sin(t * 1.5 + seed) + 1.0 * math.sin(t * 2.8 + seed * 2))
    ang = amp * (0.9 * math.sin(t * 0.57 + seed * 1.7) + 0.3 * math.sin(t * 1.9 + seed))
    return dy, ang


# ------------------------------------------------------------------ layers
def _disc(r, col, a0=255):
    s = r * 2
    im = Image.new("RGBA", (s, s), col + (0,))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s - 1, s - 1], fill=col + (a0,))
    return im


def _bloom(r=340, col=(255, 172, 108)):
    s = r * 2
    y, x = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.sqrt((x - r) ** 2 + (y - r) ** 2) / r
    a = (np.clip(1 - d, 0, 1) ** 2.6 * 255).astype(np.uint8)
    im = Image.new("RGBA", (s, s), col + (0,))
    im.putalpha(Image.fromarray(a))
    return im


def _pool(w, h, col=(70, 66, 60), a0=90):
    im = Image.new("RGBA", (w, h), col + (0,))
    al = Image.new("L", (w, h), 0)
    ImageDraw.Draw(al).ellipse([0, 0, w - 1, h - 1], fill=a0)
    al = al.filter(ImageFilter.GaussianBlur(h * 0.28))
    im.putalpha(al)
    return im


def _vignette(w, h, strength=210, power=2.1):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (x - w / 2) / (w / 2)
    ny = (y - h / 2) / (h / 2)
    r = np.sqrt(nx ** 2 * 0.9 + ny ** 2) / 1.24
    a = (np.clip(r, 0, 1) ** power * strength).astype(np.uint8)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im.putalpha(Image.fromarray(a))
    return im


BLOOM_WARM = _bloom(340, (255, 172, 108))
BLOOM_COLD = _bloom(400, (150, 176, 208))
POOL = _pool(420, 92)
def _crescent(r=96, a0=52):
    s2 = r * 2
    im = Image.new("RGBA", (s2, s2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s2 - 1, s2 - 1], fill=CREAM + (a0,))
    cut = Image.new("RGBA", (s2, s2), (0, 0, 0, 0))
    ImageDraw.Draw(cut).ellipse([int(s2 * 0.26), -int(s2 * 0.10), s2 + int(s2 * 0.26), s2 - int(s2 * 0.10)],
                                fill=(0, 0, 0, 255))
    im.paste(cut, (0, 0), cut)
    return im


MOON = _crescent(96, 58)
MOON_RIM = _disc(126, CREAM, 6)
VIG = _vignette(W, H)

GRAIN = None


def grain():
    global GRAIN
    if GRAIN is None:
        rng = np.random.default_rng(5)
        n = rng.normal(0, 6.0, (H // 2, W // 2)).clip(-18, 18)
        n = np.repeat(np.repeat(n, 2, axis=0), 2, axis=1)[:H, :W]
        base = np.zeros((H, W, 3), np.uint8) + 128
        GRAIN = Image.fromarray((base + n[:, :, None]).clip(0, 255).astype(np.uint8))
    return GRAIN


DUST = None


def dust():
    global DUST
    if DUST is None:
        rng = np.random.default_rng(17)
        DUST = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(6, 22),
                 rng.uniform(0.4, 1.0), rng.uniform(0, 6.28), rng.uniform(8, 26))
                for _ in range(34)]
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
    lh = int(size * 1.46)
    wid = max(i.width for i in imgs)
    out = Image.new("RGBA", (wid + 6, lh * len(imgs) + 6), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        out.alpha_composite(im, (0, i * lh + (lh - im.height) // 2))
    _cap[key] = out
    return out


def blit(base, layer, x, y, alpha=1.0):
    if alpha <= 0.02:
        return
    if alpha < 0.99:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(layer, (int(x), int(y)))


def text_at(base, xy, s, size, weight=600, color=CREAM, anchor="lm", alpha=1.0):
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

    # drone: the bazaar at night
    sw = 0.55 + 0.45 * np.sin(2 * np.pi * 0.037 * t - 1.1)
    drone = (np.sin(2 * np.pi * 43.6 * t) * 0.55
             + np.sin(2 * np.pi * 65.4 * t + 0.7) * 0.30
             + np.sin(2 * np.pi * 87.2 * t + 2.1) * 0.14).astype(np.float32)
    drone *= (0.5 + 0.5 * sw)

    air = _lp(rng.normal(0, 1, n).astype(np.float32), 360)
    air /= (np.abs(air).max() + 1e-9)
    air *= (0.24 + 0.13 * np.sin(2 * np.pi * 0.061 * t + 0.3))

    # clock across the night scenes (lines 2-4)
    tick = np.zeros(n, np.float32)
    m = int(0.15 * SR)
    tk = np.arange(m) / SR
    click = ((np.sin(2 * np.pi * 2050 * tk) * np.exp(-tk * 95)).astype(np.float32) * 0.7
             + _lp(rng.normal(0, 1, m).astype(np.float32), 3000) * np.exp(-tk * 65) * 0.3)
    click /= (np.abs(click).max() + 1e-9)
    tt = NAR[1]
    k = 0
    while tt < min(NAR[4] + 1.5, total):
        i = int(tt * SR)
        seg = min(m, n - i)
        if seg > 0:
            tick[i:i + seg] += click[:seg] * (0.5 if k % 2 else 0.85)
        k += 1
        tt += 0.96

    # heartbeat under the boy's boast, faster at the answer
    hb = np.zeros(n, np.float32)
    b = np.arange(int(0.55 * SR)) / SR
    thump = (np.sin(2 * np.pi * 44 * b) * np.exp(-b * 15)).astype(np.float32)
    dub = (np.sin(2 * np.pi * 36 * b) * np.exp(-b * 20)).astype(np.float32) * 0.65
    tt, gap = NAR[3], 1.14
    while tt < total - 3:
        i = int(tt * SR)
        seg = min(len(thump), n - i)
        if seg > 0:
            hb[i:i + seg] += thump[:seg]
            j = i + int(0.25 * SR)
            s2 = min(len(dub), n - j)
            if s2 > 0:
                hb[j:j + s2] += dub[:s2]
        if tt > NAR[6]:                      # after he answers
            gap = 0.86
        tt += gap
    hb /= (np.abs(hb).max() + 1e-9)

    # riser into the answer
    ris = np.zeros(n, np.float32)
    r0, r1 = NAR[6] - 2.4, NAR[6] - 0.05
    i0, i1 = int(max(r0, 0) * SR), int(min(r1, total) * SR)
    if i1 > i0:
        m2 = i1 - i0
        tt_ = np.arange(m2) / SR
        fr = tt_ / max(tt_[-1], 1e-3)
        ns = _lp(rng.normal(0, 1, m2).astype(np.float32), 900)
        ns /= (np.abs(ns).max() + 1e-9)
        tone = np.sin(2 * np.pi * (50 + 470 * fr ** 2.2) * tt_).astype(np.float32)
        ris[i0:i1] = (ns * 0.65 + tone * 0.5) * (fr ** 2.4)

    stings = np.zeros(n, np.float32)

    def sting(at, gain=1.0, bright=0.0, long=2.0):
        m3 = int(long * SR)
        st = np.arange(m3) / SR
        low = (np.sin(2 * np.pi * 33 * st) * np.exp(-st * 3.0)).astype(np.float32)
        body = _lp(rng.normal(0, 1, m3).astype(np.float32), 240)
        body /= (np.abs(body).max() + 1e-9)
        body = (body * np.exp(-st * 5.5)).astype(np.float32)
        hi = (np.sin(2 * np.pi * 1180 * st) * np.exp(-st * 10)).astype(np.float32) * bright
        s = (low * 0.9 + body * 0.8 + hi) * gain
        i = int(max(at, 0) * SR)
        seg = min(m3, n - i)
        if seg > 0:
            stings[i:i + seg] += s[:seg]

    sting(NAR[6] - 0.02, 0.95, 0.20)          # he says yes
    sting(NAR[7] - 0.02, 0.55, 0.10)          # morning
    sting(NAR[8] - 0.02, 0.45, 0.06, 3.0)     # the five faces

    bed = drone * 0.50 + air * 0.38 + tick * 0.24 + hb * 0.25 + ris * 0.5 + stings
    duck = np.ones(n, np.float32)
    for k, st in enumerate(NAR):
        a, b_ = int(max(st - 0.45, 0) * SR), int(min(st + DUR[k] + 0.3, total) * SR)
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


def _ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def build_mix():
    ff = _ffmpeg()
    os.makedirs("/tmp/lwav", exist_ok=True)
    items = []
    for k, p in enumerate(TAKES):
        wp = "/tmp/lwav/v%d.wav" % (k + 1)
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", p, "-ar", str(SR), "-ac", "1", wp], check=True)
        with wave.open(wp) as fh:
            items.append(np.frombuffer(fh.readframes(fh.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0)
    n = int(TOTAL * SR)
    voice = np.zeros(n, np.float32)
    for k, a in enumerate(items):
        i = int(round(NAR[k] * SR))
        seg = min(len(a), n - i)
        voice[i:i + seg] += a[:seg] * 0.92
        rms = 20 * math.log10(float(np.sqrt((a ** 2).mean())) + 1e-9)
        print("  v%d at %6.2fs  %.2fs  rms %.1f dB" % (k + 1, NAR[k], len(a) / SR, rms), flush=True)
    bed = make_bed(TOTAL)
    m = min(len(bed), n)
    mix = np.tanh((voice[:m] + bed[:m] * 0.28) * 1.05) * 0.92
    st = np.stack([mix, mix], 1)
    with wave.open(MIX, "wb") as fh:
        fh.setnchannels(2)
        fh.setsampwidth(2)
        fh.setframerate(SR)
        fh.writeframes((st * 32767).clip(-32768, 32767).astype(np.int16).tobytes())
    peak = 20 * math.log10(float(np.abs(mix).max()) + 1e-9)
    print("mix ok %.2fs  peak %.1f dB  %d B" % (m / SR, peak, os.path.getsize(MIX)))


# ------------------------------------------------------------------ scenes
# cast: (name, x, scale, dim, seed)
SCN = [
    dict(slug="নিয়ম", moon=True, cast=[("teacher", 540, 1.00, 0.98, 1.0)]),
    dict(slug="রফিক", lamp=True, rails=True, cast=[("rafiq", 540, 0.99, 0.98, 2.0)]),
    dict(slug="দর্জি", stall=True, cast=[("rohima", 540, 1.00, 0.98, 3.0)]),
    dict(slug="টুটু", moon=True, cast=[("tutu", 540, 1.04, 1.00, 4.0)]),
    dict(slug="মিম", cast=[("mim", 404, 0.96, 0.98, 5.0),
                           ("tutu", 792, 0.80, 0.55, 6.0)]),
    dict(slug="মায়ের গলা", stall=True, cast=[("rohima", 540, 1.02, 0.98, 7.0)]),
    dict(slug="সাড়া", sting=True, dark=True, tint=(0.48, 0.53, 0.72),
         cast=[("tutu", 540, 0.94, 0.95, 8.0)]),
    dict(slug="সকাল", cold=True, tint=(1.0, 1.0, 1.0), cast=[("mim", 540, 0.98, 0.96, 9.0)]),
    dict(slug="পাঁচটা মুখ", row=True,
         cast=[("teacher", 168, 0.56, 0.92, 1.0), ("rohima", 350, 0.56, 0.92, 2.0),
               ("rafiq", 530, 0.56, 0.92, 3.0), ("mim", 706, 0.56, 0.92, 4.0),
               ("tutu", 866, 0.56, 0.42, 5.0)]),
    dict(slug=None, kind="end"),
]

SAY = [
    "এই বাজারে একটাই নিয়ম। রাত বারোটার পরে কেউ পেছন থেকে নাম ধরে ডাকলে ফিরে তাকাবে না, সাড়া দিবে না। কারণ যে ডাকে, তার নিজের কোনো মুখ নেই।",
    "রাত ঠিক বারোটা। রিকশা টানছি, পেছন থেকে কেউ ডাকল, রফিক। আমি ঘাড় ঘোরালাম না। আবার ডাকল, আরও কাছে। তৃতীয়বার ডাকল সামনে থেকে।",
    "আমার দোকানের পাশে এক দর্জি থাকত। এক রাতে সে সাড়া দিয়েছিল। সকালে তার মুখটা একদম মসৃণ, চোখ নেই, নাক নেই। তবু সে হাঁটে, আর সবাই তাকে অন্য নামে ডাকে।",
    "আমি ভয় পাই না, একদমই না। তোমরা সবাই ভীতু। আজ রাতে আমি একা বসব, আর যে ডাকবে, আমি সোজা সাড়া দিব।",
    "টুটু, শোনো। এটা মজার কিছু না। সাড়া দিলে ফেরার পথ থাকে না। ও তোমার মুখটা নিয়ে নেবে, আর তুমি থেকে যাবে একটা নামহীন শরীর।",
    "ও ডাকে তোমার মায়ের গলায়। হুবহু সেই কথাটা বলে, যেটা তুমি শেষবার বলেছিলে। তাই তুমি চিনতে পারবে না।",
    "মা? মা, তুমি এসেছ? আমি এখানে।",
    "সকালে টুটু উঠে বসল। মুখটা আমার দিকে ঘোরাল, তারপর আমার নিজের গলায় বলল, মিম, সাড়া দিও না।",
    "এখন বাজারে পাঁচটা মুখ। একটার বয়স বাড়ে না। আর একটা মুখ কারও না।",
    "",
]

TAG = ["মাস্টারমশাই", "রফিক", "রহিমা খালা", "টুটু", "মিম",
       "রহিমা খালা", "টুটু", "মিম", "মাস্টারমশাই", None]
ROLE = ["শিক্ষক", "রিকশাচালক", "সবজি বিক্রেতা", "ছোট ছেলে", "স্কুলছাত্রী",
        "", "", "", "", None]

CAPS = [plate(s, 50, 600, CREAM, BODY_MAXW) if s else None for s in SAY]


# ------------------------------------------------------------------ scenery
def horizon(cv, col, y=FEET + 14, a=1.0):
    ImageDraw.Draw(cv).line([(0, y), (W, y)], fill=col + (int(255 * a),), width=3)


def set_dress(cv, sc, t, i):
    """flat props — no gradients except the deliberate light bloom"""
    d = ImageDraw.Draw(cv)
    if sc.get("cold"):
        # dawn: flat band of sky, one low sun-less horizon
        d.rectangle([0, 0, W, FEET - 4], fill=(56, 62, 70, 255))
        d.rectangle([0, FEET - 4, W, H], fill=(30, 33, 38, 255))
        horizon(cv, (104, 110, 118), FEET - 4, 1.0)
        d.rectangle([0, 196, W, 200], fill=(74, 80, 88, 255))
        cv.alpha_composite(_disc(64, (246, 232, 208), 74), (742, 700))
        for (yy, ww) in ((520, 300), (570, 420)):
            d.rectangle([W - 60 - ww, yy, W - 60, yy + 9], fill=(70, 76, 84, 255))
        d.rectangle([0, FEET - 6, W, FEET - 2], fill=(112, 118, 126, 255))
    if sc.get("moon"):
        cv.alpha_composite(MOON_RIM, (798, 138))
        cv.alpha_composite(MOON, (828, 168))
    if sc.get("stall"):
        # the shop awning: one flat beam, one cloth, a scalloped hem
        d.rectangle([0, 226, W, 242], fill=(58, 52, 46, 255))
        d.rectangle([0, 242, W, 318], fill=(44, 40, 35, 255))
        for k in range(11):
            x = 24 + k * 100
            d.pieslice([x - 34, 318 - 34, x + 34, 318 + 34], 0, 180, fill=(44, 40, 35, 255))
        d.line([(0, 318), (W, 318)], fill=(30, 27, 24, 255), width=0)
    if sc.get("lamp"):
        d.rectangle([92, 430, 102, FEET + 6], fill=(54, 48, 43, 255))
        d.rectangle([70, 412, 132, 436], fill=(60, 54, 48, 255))
        cv.alpha_composite(_disc(15, CORAL, 235), (86, 430))
        blit(cv, BLOOM_WARM, 102 - 340, 444 - 340, 0.42 + 0.05 * math.sin(t * 7.3))
    if sc.get("rails"):
        # motion streaks: the road running past a moving rickshaw
        for k in range(7):
            y = 900 + k * 74
            ph = (t * (420 + k * 60)) % (W + 520)
            x0 = (W + 260) - ph
            d.rectangle([x0, y, x0 + 240, y + 4], fill=(34, 32, 30, 255))
    if sc.get("row"):
        d.rectangle([0, FEET + 14, W, FEET + 20], fill=(44, 40, 36, 255))


def draw_scene(i, sc, lt, dur, t):
    base = DAWN if sc.get("cold") else BG
    cv = Image.new("RGBA", (W, H), base + (255,))
    set_dress(cv, sc, t, i)

    # light from behind, breathing
    coast = clamp(lt / max(dur, 0.1), 0, 1)
    ga = 0.30 + 0.07 * math.sin(t * 0.63 + i)
    if sc.get("dark"):
        ga *= 0.55
    if sc.get("cold"):
        ga *= 0.7
    blit(cv, BLOOM_COLD if sc.get("cold") else BLOOM_WARM, W / 2 - 340, FEET - 900, ga)

    # dust
    d = ImageDraw.Draw(cv)
    for (dx, dy, sp, sz, ph, drift) in dust():
        y = (dy - t * sp) % H
        x = dx + math.sin(t * 0.5 + ph) * drift
        a = (22 + 20 * math.sin(t * 1.7 + ph)) * (0.6 if sc.get("dark") else 1.0)
        d.ellipse([x - sz / 2, y - sz / 2, x + sz / 2, y + sz / 2], fill=(206, 196, 180, int(max(a, 0))))

    # cast
    for k, (name, x, scale, dim, seed) in enumerate(sc["cast"]):
        h = height(name, scale)
        dy, ang = lifelike(t, seed, 1.0 if k == 0 else 0.65)
        enter = expo(clamp((lt - 0.05 * k) / 0.55, 0, 1))
        feet = FEET + dy + int((1 - enter) * 22)
        xo = x + (1 - enter) * (26 if x > W / 2 else -26) + wob(t, seed, 3)
        d2 = dim * (0.88 + 0.12 * enter) * (1.05 if k == 0 else 1.0)
        if sc.get("dark"):
            d2 *= 0.88
        tint = sc.get("tint", (0.90, 0.93, 1.0))
        if sc.get("sting"):
            sh = max(0.0, 1.0 - lt / 0.55) ** 2
            xo += sh * 16 * math.sin(lt * 61)
            feet += sh * 9 * math.cos(lt * 47)
        blit(cv, POOL, xo - 210, feet - 34, 0.55 * enter * (1.35 if k == 0 else 0.9))
        puppet(cv, name, xo, feet, h, ang, d2, enter, tint)
        if k == 0 and not sc.get("row"):
            la = 0.20 + 0.05 * math.sin(t * 2.1)
            blit(cv, BLOOM_COLD if sc.get("cold") else BLOOM_WARM, xo - 340, feet - h * 0.62 - 340, la)

    if sc.get("sting"):
        fl = max(0.0, 1.0 - lt / 0.28) ** 2
        if fl > 0.01:
            cv.alpha_composite(Image.new("RGBA", (W, H), (255, 132, 100, int(26 * fl))))
    return cv


def header(cv, i, t):
    text_at(cv, (TX, 84), "নিয়ম ১", 40, 700, CORAL, "lm")
    text_at(cv, (TX + 152, 86), "ভৌতিক পাঠ · ২", 28, 600, DIMT, "lm")
    text_at(cv, (W - TX, 86), "বাংলা ভৌতিক গল্প", 26, 500, DIMT, "rm")
    ImageDraw.Draw(cv).line([(TX, 124), (W - TX, 124)], fill=(44, 40, 37, 255), width=2)


def caption(cv, i, lt):
    if not CAPS[i]:
        return
    a = clamp((lt - 0.14) / 0.45, 0, 1)
    tg = TAG[i]
    if tg:
        text_at(cv, (TX, TY_TAG), tg, 34, 700, CORAL, "lm", a)
        wt = twidth(tg, 34, 700)
        ImageDraw.Draw(cv).line([(TX + wt + 20, TY_TAG + 2), (TX + wt + 44, TY_TAG + 2)],
                                fill=(int(126 * a), int(60 * a), 40, 255), width=2)
        if ROLE[i]:
            text_at(cv, (TX + wt + 58, TY_TAG + 2), ROLE[i], 26, 500, DIMT, "lm", a)
    blit(cv, CAPS[i], TX, TY_BODY + int((1 - expo(a)) * 12), a)


def footer(cv, i, t):
    d = ImageDraw.Draw(cv)
    d.line([(TX, FOOT_Y), (W - TX, FOOT_Y)], fill=(42, 38, 35, 255), width=2)
    for k in range(NSC):
        x = TX + k * 22
        d.rectangle([x, FOOT_Y + 16, x + 12, FOOT_Y + 22],
                    fill=(CORAL if k == i else (50, 44, 40)) + (255,))
    text_at(cv, (W - TX, FOOT_Y - 28), "সাড়া দিও না", 26, 600, DIMT, "rm")


def cold_open(cv, lt):
    """title over the first card, before the teacher speaks"""
    a = clamp((lt - 0.5) / 0.9, 0, 1) * (1 - clamp((lt - 4.6) / 0.7, 0, 1))
    if a <= 0.02:
        return
    im = timg("নিয়ম ১", 176, 700, CREAM)
    blit(cv, im, (W - im.width) / 2, 636, a)
    im2 = timg("রাত বারোটার পরে সাড়া দিও না", 42, 600, CORAL)
    blit(cv, im2, (W - im2.width) / 2, 852, a * clamp((lt - 1.2) / 0.6, 0, 1))


def end_card(cv, lt, t):
    a = clamp((lt - 0.35) / 0.7, 0, 1)
    im = timg("নিয়ম ১", 140, 700, CORAL)
    blit(cv, im, (W - im.width) / 2, 392, a)
    p = plate("কেউ পেছন থেকে নাম ধরে ডাকলে ফিরে তাকাবে না।", 48, 600, CREAM, 850)
    blit(cv, p, (W - p.width) / 2, 596, clamp((lt - 0.85) / 0.7, 0, 1))

    order = ["teacher", "rohima", "rafiq", "mim", "tutu"]
    for k, name in enumerate(order):
        st = overshoot(clamp((lt - 1.3 - k * 0.11) / 0.42, 0, 1))
        if st <= 0.02:
            continue
        hgt = 400 * (0.94 + 0.06 * st)
        im2 = raw(name)
        nwid = max(8, int(im2.width * hgt / im2.height))
        tile = im2.resize((nwid, int(hgt)), Image.LANCZOS)
        if name == "tutu":
            tile.putalpha(tile.getchannel("A").point(lambda v: int(v * 0.35)))
        x = 40 + k * 200 + (190 - nwid) // 2
        blit(cv, tile, x, 792, st)

    b = clamp((lt - 2.4) / 0.7, 0, 1)
    d = ImageDraw.Draw(cv)
    if b > 0.02:
        d.rounded_rectangle([W / 2 - 250, 1186, W / 2 + 250, 1286], 12,
                            outline=(int(CORAL[0] * b), int(CORAL[1] * b), int(CORAL[2] * b), 255), width=3)
    text_at(cv, (W / 2, 1236), "ফলো করো · প্রতি শুক্রবার নতুন গল্প", 31, 600, CREAM, "mm", b)
    text_at(cv, (W / 2, 1382), "ভৌতিক পাঠ · বাংলা সিরিজ", 28, 500, DIMT, "mm", clamp((lt - 3.0) / 0.7, 0, 1))
    fa = clamp((lt - 3.2) / 0.8, 0, 1)
    if fa > 0.02:
        d.line([(TX, 1704), (W - TX, 1704)], fill=(44, 40, 37, int(255 * fa)), width=2)
        text_at(cv, (TX, 1744), "নিয়ম ১ · ভৌতিক পাঠ ২", 26, 500, DIMT, "lm", fa)
        text_at(cv, (W - TX, 1744), "২:০০ মিনিট", 26, 500, DIMT, "rm", fa)


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
        blit(cv, BLOOM_WARM, W / 2 - 340, 150, 0.13)
        end_card(cv, lt, t)
        out = cv.convert("RGB")
    elif i == 0:
        cv = Image.new("RGBA", (W, H), BG + (255,))
        if t > NAR[0] - 1.4:
            sc2 = draw_scene(i, sc, max(0.0, lt - (NAR[0] - 1.4 - BOUNDS[0])), dur, t)
            blit(cv, sc2, 0, 0, clamp((t - (NAR[0] - 1.4)) / 0.7, 0, 1))
        cold_open(cv, lt)
        header(cv, i, t)
        if lt > 3.0:
            caption(cv, i, max(0.0, t - NAR[0] + 0.2))
        footer(cv, i, t)
        out = cv.convert("RGB")
    else:
        cv = draw_scene(i, sc, lt, dur, t)
        header(cv, i, t)
        caption(cv, i, lt)
        footer(cv, i, t)
        out = cv.convert("RGB")

    out = Image.blend(out, grain(), 0.075)
    out.paste((0, 0, 0), (0, 0), VIG)
    if i == 0 and lt < 0.5:
        k = clamp(lt / 0.5, 0, 1)
        out = ImageEnhance.Brightness(out).enhance(0.25 + 0.75 * k)
    if i == NSC - 1:
        k = clamp((lt - (TAIL - 2.2)) / 2.2, 0, 1)
        if k > 0:
            out = ImageEnhance.Brightness(out).enhance(1.0 - 0.85 * k)
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
