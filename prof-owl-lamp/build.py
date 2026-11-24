#!/usr/bin/env python3
"""
THE LAMP AND THE OWL — Prof. Owl fable.
Claude flat-vector style, code-drawn, 1080x1920, 30 fps.

Accent rule: CORAL is the flame and nothing else. Night ground is ink; the moral card flips to cream.

Modes:
  python3 build.py --sheet        character sheet (owl / crow / lamp) -> frames/sheet.png
  python3 build.py --test         three scene stills for approval
  python3 build.py                full render (needs audio/s1..s7.mp3)
"""
import math, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2
W, H = 1080, 1920
WP, HP = W * S, H * S
FPS = 30

CREAM = (240, 238, 230)
INK = (25, 25, 25)
NIGHT = (27, 26, 24)
NIGHT2 = (38, 36, 33)
GREY = (196, 191, 181)
META = (150, 144, 134)
CORAL = (217, 119, 87)
CORAL_HOT = (247, 190, 132)

FFMPEG = os.environ.get("FFMPEG_BIN") or "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
if not os.path.exists(FFMPEG):
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/local/share/fonts/DejaVuSans.ttf"
if not os.path.exists(REG):
    REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_f = {}
def fb(px):
    if ("b", px) not in _f:
        _f[("b", px)] = ImageFont.truetype(BOLD, int(px * S))
    return _f[("b", px)]

def fr(px):
    if ("r", px) not in _f:
        _f[("r", px)] = ImageFont.truetype(REG, int(px * S))
    return _f[("r", px)]


# ---------------------------------------------------------------- easing
def cl(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v

def seg(t0, t1, t):
    return cl((t - t0) / (t1 - t0))

def eio(t):
    t = cl(t)
    return 3 * t * t - 2 * t * t * t

def eout(t, p=4):
    t = cl(t)
    return 1 - (1 - t) ** p

def eback(t, s=1.70158):
    t = cl(t) - 1
    return t * t * ((s + 1) * t + s) + 1

def spr(t, freq=2.0, damp=6.0):
    t = cl(t)
    return 1 - math.exp(-damp * t) * math.cos(2 * math.pi * freq * t)


# ---------------------------------------------------------------- primitives
def ell(d, cx, cy, rx, ry, fill):
    if rx <= 0.3 or ry <= 0.3:
        return
    d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill)

def rr(d, cx, cy, w, h, r, fill, outline=None, ow=0):
    if w <= 0.4 or h <= 0.4:
        return
    box = [(cx - w / 2) * S, (cy - h / 2) * S, (cx + w / 2) * S, (cy + h / 2) * S]
    if outline:
        d.rounded_rectangle(box, radius=max(1, r) * S, fill=fill, outline=outline, width=int(ow * S))
    else:
        d.rounded_rectangle(box, radius=max(1, r) * S, fill=fill)


def poly(d, pts, fill):
    d.polygon([(x * S, y * S) for x, y in pts], fill=fill)

def txt(d, xy, s, px, fill, bold=True, anchor="mm"):
    d.text((xy[0] * S, xy[1] * S), s, font=(fb(px) if bold else fr(px)), fill=fill, anchor=anchor)



def fit(d, xy, text, px, fill, maxw=930, bold=True, gap=0.0):
    """Type that shrinks until it fits the phone frame."""
    f = fb(px) if bold else fr(px)
    while d.textlength(text, font=f) * (1 + gap) > maxw * S and px > 18:
        px -= 2
        f = fb(px) if bold else fr(px)
    d.text((xy[0] * S, xy[1] * S), text, font=f, fill=fill, anchor="mm")


# ---------------------------------------------------------------- characters
def owl(img, cx, cy, s=1.0, blink=0.0, tilt=0.0, look=0.0):
    """Prof. Owl: ink egg, cream eyes, round glasses, small grey scarf."""
    d = ImageDraw.Draw(img)
    # ear tufts
    poly(d, [(cx - 62 * s, cy - 92 * s), (cx - 34 * s, cy - 136 * s), (cx - 18 * s, cy - 84 * s)], INK)
    poly(d, [(cx + 62 * s, cy - 92 * s), (cx + 34 * s, cy - 136 * s), (cx + 18 * s, cy - 84 * s)], INK)
    # body
    ell(d, cx, cy, 92 * s, 124 * s, INK)
    # eyes (smaller discs so the glasses have air around them)
    for ex in (-38, 38):
        exx = cx + ex * s
        eyy = cy - 26 * s
        ell(d, exx, eyy, 32 * s, 32 * s, CREAM)
        ell(d, exx + look * 9 * s, eyy + look * 2 * s, 12 * s, 12 * s, INK)
        if blink > 0.02:                       # eyelid slides down over the eye
            top = eyy - 33 * s
            d.rectangle([(exx - 33 * s) * S, top * S, (exx + 33 * s) * S,
                         (top + 66 * s * cl(blink)) * S], fill=INK)
        # glasses ring, drawn last so it survives the blink
        d.ellipse([(exx - 41 * s) * S, (eyy - 41 * s) * S, (exx + 41 * s) * S, (eyy + 41 * s) * S],
                  outline=CREAM, width=int(4 * s * S))
    # bridge
    d.line([((cx - 8 * s) * S, (cy - 26 * s) * S), ((cx + 8 * s) * S, (cy - 26 * s) * S)],
           fill=CREAM, width=int(4 * s * S))
    # temples: two short arms so it reads as spectacles, not goggles
    for sg in (-1, 1):
        d.line([((cx + sg * 51 * s) * S, (cy - 26 * s) * S),
                ((cx + sg * 68 * s) * S, (cy - 35 * s) * S)],
               fill=CREAM, width=int(3.5 * s * S))
    # beak
    poly(d, [(cx - 11 * s, cy + 6 * s), (cx + 11 * s, cy + 6 * s), (cx, cy + 30 * s)], GREY)
    # scarf: band at the throat + a small knot on one side
    rr(d, cx, cy + 50 * s, 78 * s, 14 * s, 7 * s, (150, 145, 135))
    poly(d, [(cx - 22 * s, cy + 54 * s), (cx + 22 * s, cy + 54 * s),
             (cx + 6 * s, cy + 86 * s)], (166, 161, 151))
    # feet: two flat grey paddles
    for fx in (-26, 26):
        rr(d, cx + fx * s, cy + 120 * s, 36 * s, 13 * s, 6 * s, GREY)


def crow(img, cx, cy, s=1.0, wing=0.0, beak_open=0.0):
    """The young crow: leaner, greyer, one bright eye."""
    d = ImageDraw.Draw(img)
    dark = (62, 58, 53)
    darker = (48, 45, 41)
    # tail
    poly(d, [(cx - 34 * s, cy + 26 * s), (cx - 88 * s, cy + 62 * s), (cx - 30 * s, cy + 66 * s)], darker)
    # body
    ell(d, cx, cy, 58 * s, 72 * s, dark)
    # wing: a leaf shape lifted by `wing`
    wx = cx - 22 * s - 6 * s * wing
    wy = cy + 10 * s + 16 * s * wing
    ell(d, wx, wy, 30 * s, 44 * s, darker)
    poly(d, [(cx + 4 * s, cy - 14 * s), (cx - 30 * s, cy + 26 * s + 20 * s * wing),
             (cx - 16 * s, cy + 48 * s)], darker)
    # head
    ell(d, cx + 24 * s, cy - 58 * s, 36 * s, 34 * s, dark)
    # beak
    poly(d, [(cx + 56 * s, cy - 64 * s), (cx + 100 * s, cy - 54 * s), (cx + 54 * s, cy - 44 * s)], GREY)
    if beak_open > 0.05:
        poly(d, [(cx + 56 * s, cy - 58 * s), (cx + 96 * s, cy - 38 * s), (cx + 54 * s, cy - 40 * s)],
             (140, 134, 124))
    # eye
    ell(d, cx + 34 * s, cy - 68 * s, 6.5 * s, 6.5 * s, CREAM)


def lamp(img, cx, cy, s=1.0, flame=1.0, glow=0.0, post_h=300):
    """Street lamp: ink post, glass box, coral flame inside. The flame is the only accent."""
    d = ImageDraw.Draw(img)
    if glow > 0.02 and flame > 0.02:
        lay = Image.new("RGBA", (WP, HP), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        base_r = 165 * s * (0.7 + 0.6 * min(flame, 2.0))
        for k in range(7):
            rr_ = base_r * (1 - k * 0.12)
            a = int((7 + k * 3) * min(1.0, glow))
            ld.ellipse([(cx - rr_) * S, (cy + 20 * s - rr_ * 1.15) * S,
                        (cx + rr_) * S, (cy + 20 * s + rr_ * 1.15) * S], fill=CORAL + (a,))
        lay = lay.filter(ImageFilter.GaussianBlur(26 * S / 2))
        img.paste(lay, (0, 0), lay)
        d = ImageDraw.Draw(img)
    # post
    rr(d, cx, cy + post_h * s / 2, 20 * s, post_h * s, 6 * s, INK)
    # glass box (dark interior), drawn before the flame so the flame reads inside it
    rr(d, cx, cy + 34 * s, 118 * s, 108 * s, 10 * s, (44, 40, 36))
    if flame > 0.02:
        fh = 86 * s * flame
        fw = 34 * s * (0.60 + 0.40 * min(flame, 2.0))
        by = cy + 86 * s
        poly(d, [(cx, by - fh), (cx + fw * 0.5, by - fh * 0.4), (cx + fw, by - fh * 0.1),
                 (cx + fw * 0.45, by), (cx - fw * 0.45, by), (cx - fw, by - fh * 0.1),
                 (cx - fw * 0.5, by - fh * 0.4)], CORAL)
        if flame > 1.15:
            poly(d, [(cx, by - fh * 0.8), (cx + fw * 0.3, by - fh * 0.26),
                     (cx + fw * 0.2, by - fh * 0.03), (cx - fw * 0.2, by - fh * 0.03),
                     (cx - fw * 0.3, by - fh * 0.26)], CORAL_HOT)
    # frame: side bars, rails, cap and a small finial
    for bx in (cx - 55 * s, cx + 55 * s):
        rr(d, bx, cy + 34 * s, 9 * s, 108 * s, 4 * s, INK)
    rr(d, cx, cy - 20 * s, 128 * s, 12 * s, 5 * s, INK)
    rr(d, cx, cy + 88 * s, 128 * s, 12 * s, 5 * s, INK)
    poly(d, [(cx - 76 * s, cy - 20 * s), (cx + 76 * s, cy - 20 * s),
             (cx + 44 * s, cy - 48 * s), (cx - 44 * s, cy - 48 * s)], INK)
    ell(d, cx, cy - 56 * s, 9 * s, 9 * s, INK)

def stars(d, n=70, seed=3):
    rnd = []
    x = seed
    for i in range(n):
        x = (x * 1103515245 + 12345) % 2147483648
        sx = 30 + (x % (W - 60))
        x = (x * 1103515245 + 12345) % 2147483648
        sy = 40 + (x % 900)
        x = (x * 1103515245 + 12345) % 2147483648
        r = 1.4 + (x % 300) / 160.0
        rnd.append((sx, sy, r))
    for sx, sy, r in rnd:
        ell(d, sx, sy, r, r, (120, 114, 104))


def houses(d, count=7, y=1240, lit=0.0, base_col=(52, 48, 43)):
    """A village silhouette: wall, roof, and one warm window when the lamp is alive."""
    xs = [110, 245, 380, 520, 660, 800, 940]
    for i, hx in enumerate(xs[:count]):
        hw = 78 + 14 * ((i * 3) % 3)
        hh = 130 + 34 * ((i * 5) % 3)
        d.rectangle([(hx - hw) * S, (y - hh) * S, (hx + hw) * S, y * S], fill=base_col)
        poly(d, [(hx - hw - 12, y - hh), (hx + hw + 12, y - hh), (hx, y - hh - 74)], fill=base_col)
        if lit > 0.02:
            ell(d, hx - 26, y - hh * 0.55, 13 * lit, 15 * lit, CORAL)
            ell(d, hx + 26, y - hh * 0.55, 13 * lit, 15 * lit, CORAL)
    d.rectangle([0, y * S, WP, (y + 12) * S], fill=(46, 42, 38))


def road(d, y=1244):
    poly(d, [(180, H), (900, H), (760, y), (320, y)], fill=(38, 35, 31))


# ---------------------------------------------------------------- scenes
def s1(img, lt):
    """One lamp on one road."""
    d = ImageDraw.Draw(img)
    stars(d)
    houses(d, 7, 1230, 0.0)
    road(d)
    appear = eio(seg(0.0, 0.8, lt))
    lamp(img, 620, 900, 1.0, flame=0.75 + 0.1 * math.sin(lt * 6.0), glow=appear)
    oy = 1255 + 4 * math.sin(lt * 1.6)                       # a slow breath
    owl(img, 772, oy, 1.55, blink=(0.6 if 2.4 < lt < 2.55 else 0.0),
        look=-0.5 if lt > 1.4 else -0.1)
    if lt > 0.9:
        txt(d, (540, 300), "O N E   L A M P   ·   O N E   R O A D", 30, META, bold=False)


def s2(img, lt):
    """The crow's offer."""
    d = ImageDraw.Draw(img)
    stars(d)
    houses(d, 7, 1230, 0.0)
    road(d)
    lamp(img, 620, 900, 1.0, flame=0.75, glow=1.0)
    owl(img, 806, 1270 + 4 * math.sin(lt * 1.7), 1.45, look=-0.75 if lt > 1.0 else -0.2)
    land = eout(seg(0.15, 1.35, lt), 3)
    cy = -180 + (1371 + 180) * land
    hop = 10 * abs(math.sin((lt - 1.35) * 7.0)) if lt > 1.35 else 0.0
    crow(img, 345, cy - hop, 1.2, wing=abs(math.sin(lt * 5.0)) * (1 - land),
         beak_open=0.9 if lt > 1.95 else 0.0)
    if lt > 1.6:
        txt(d, (540, 300), "T H E   C R O W ' S   O F F E R", 30, META, bold=False)


def s3(img, lt):
    """Too much light."""
    d = ImageDraw.Draw(img)
    stars(d, 40)
    grow = eio(seg(0.25, 1.7, lt))
    houses(d, 7, 1230, cl(grow * 1.2))
    road(d)
    fl = 0.75 + 0.58 * grow
    lamp(img, 620, 900, 1.0, flame=fl, glow=1.0 + 2.0 * grow)
    owl(img, 802, 1268 + 3 * math.sin(lt * 2.0), 1.42, look=-0.85)
    crow(img, 330, 1372, 1.18, wing=0.35, beak_open=0.6)
    # rays: the lamp is overworking (three short ticks, growing with the flare)
    for k, (dx, dy) in enumerate(((-1.0, -0.35), (0.0, -1.0), (1.0, -0.35))):
        a = eio(seg(1.4 + k * 0.08, 1.8 + k * 0.08, lt))
        if a > 0.05:
            x1, y1 = 620 + dx * 140, 860 + dy * 140
            x2, y2 = 620 + dx * (140 + 130 * a), 860 + dy * (140 + 130 * a)
            d.line([(x1 * S, y1 * S), (x2 * S, y2 * S)], fill=CORAL_HOT, width=int(6 * S))
    if lt > 1.2:
        txt(d, (540, 300), "T O O   M U C H   L I G H T", 30, CORAL_HOT, bold=False)


def s4(img, lt):
    """The wind answers."""
    d = ImageDraw.Draw(img)
    stars(d, 30)
    houses(d, 7, 1230, 0.0)
    road(d)
    die = eio(seg(1.1, 2.3, lt))
    fl = 1.33 * (1 - die) * (1 - 0.35 * abs(math.sin(lt * 9.0)) * (1 - die))
    lamp(img, 620, 900, 1.0, flame=max(0.0, fl), glow=max(0.0, 1 - die * 0.95))
    # wind streaks
    for i in range(4):
        q = eio(seg(0.1 + i * 0.12, 0.9 + i * 0.12, lt))
        if 0.02 < q < 0.98:
            yy = 760 + i * 70
            x0 = 120 + 780 * q
            d.rectangle([x0 * S, yy * S, (x0 + 120) * S, (yy + 6) * S], fill=(120, 114, 104))
    # smoke
    if die > 0.4:
        for i in range(3):
            ell(d, 620 + 14 * math.sin(lt * 2 + i), 940 - 60 * (lt - 1.1) * 30 - i * 34,
                10 - i * 2, 10 - i * 2, (96, 90, 82))
    owl(img, 802, 1268, 1.42, look=-0.85, blink=0.5 if lt > 2.2 else 0.0)
    crow(img, 330, 1388, 1.14, wing=0.05)
    if lt > 1.5:
        txt(d, (540, 300), "T H E   W I N D   A N S W E R S", 30, META, bold=False)


def s5(img, lt):
    """The relight."""
    d = ImageDraw.Draw(img)
    stars(d, 50)
    houses(d, 7, 1230, 0.0)
    road(d)
    relight = spr(seg(0.9, 1.5, lt)) if lt > 0.9 else 0.0
    lamp(img, 620, 900, 1.0, flame=max(0.05, 0.75 * relight), glow=max(0.0, relight))
    step = eout(seg(0.15, 1.25, lt))
    owl(img, 815 - 95 * step, 1262 + 3 * math.sin(lt * 1.5), 1.5, look=-0.55)
    if lt > 1.5:
        txt(d, (540, 300), "T H E   R E L I G H T", 30, META, bold=False)


def s6(img, lt):
    """The road remembers."""
    d = ImageDraw.Draw(img)
    stars(d, 60)
    houses(d, 7, 1230, 1.0)
    road(d)
    lamp(img, 620, 900, 1.0, flame=0.78, glow=1.0)
    # travellers walking home, in silhouette, legs actually stepping
    for i in range(3):
        q = eio(seg(0.35 + i * 0.38, 2.7 + i * 0.38, lt))
        if q <= 0.0 or q >= 0.999:
            continue
        tx = 1010 - 780 * q
        ty = 1470 + i * 30
        k = 1.0 + i * 0.06
        col = (72, 67, 60)
        step = math.sin(q * 26.0 + i * 2.0)
        ell(d, tx, ty - 96 * k, 20 * k, 21 * k, col)                  # head
        poly(d, [(tx - 24 * k, ty - 76 * k), (tx + 24 * k, ty - 76 * k),
                 (tx + 17 * k, ty - 4 * k), (tx - 17 * k, ty - 4 * k)], col)   # torso
        for sg in (-1, 1):                                            # legs
            d.line([(tx * S, (ty - 8 * k) * S),
                    ((tx + sg * 15 * k * (0.5 + 0.5 * step * sg)) * S, ty * S)],
                   fill=col, width=int(9 * k * S))
        d.line([(tx * S, (ty - 70 * k) * S), ((tx + 26 * k * step) * S, (ty - 30 * k) * S)],
               fill=col, width=int(7 * k * S))                        # arm
    owl(img, 845, 1282, 1.35, look=-0.6)
    if lt > 1.2:
        txt(d, (540, 300), "T H E   R O A D   R E M E M B E R S", 30, META, bold=False)


def s7(img, lt):
    """Moral card — the film flips to cream, the flame stays."""
    d = ImageDraw.Draw(img)
    p = eback(seg(0.0, 0.7, lt))
    txt(d, (540, 470), "T H E   M O R A L", 32, META, bold=False)
    lines = ("THE LIGHT THAT", "SHOWS OFF", "GOES OUT.", "", "THE LIGHT THAT", "SHOWS THE WAY", "STAYS LIT.")
    for i, line in enumerate(lines):
        if not line:
            continue
        q = eback(seg(0.15 + i * 0.10, 0.80 + i * 0.10, lt))
        if q > 0.02:
            big = i < 3
            fit(d, (540, 600 + i * 92), line, 74 if big else 74, INK if big else CORAL, maxw=880)
    rr(d, 540, 1300, 300 * eio(seg(0.7, 1.1, lt)), 8, 5, CORAL)
    if lt > 1.2:
        txt(d, (540, 1400), "T H E   L A M P   A N D   T H E   O W L", 28, META, bold=False)
    if lt > 1.5:
        owl(img, 540, 1660, 0.78, look=0.0)


def s_sheet(img):
    """Character sheet for approval."""
    d = ImageDraw.Draw(img)
    txt(d, (540, 120), "P R O F .   O W L   —   C H A R A C T E R   S H E E T", 32, INK, bold=False)

    owl(img, 300, 560, 1.15, look=0.3)
    txt(d, (300, 810), "PROF. OWL", 30, INK)
    txt(d, (300, 858), "ink egg · cream eyes · glasses · grey scarf", 22, META, bold=False)

    crow(img, 800, 560, 1.2)
    txt(d, (800, 810), "THE CROW", 30, INK)
    txt(d, (800, 858), "leaner, greyer, one bright eye", 22, META, bold=False)

    # lamp study, on its own night panel (glow off: no alpha spill on cream)
    rr(d, 540, 1120, 940, 320, 26, (58, 53, 48))
    lamp(img, 250, 1090, 0.9, flame=0.7, glow=0.0, post_h=150)
    lamp(img, 540, 1090, 0.9, flame=2.2, glow=0.0, post_h=150)
    lamp(img, 830, 1090, 0.9, flame=0.0, glow=0.0, post_h=150)
    txt(d, (250, 1332), "small / steady", 24, META, bold=False)
    txt(d, (540, 1332), "flared", 24, META, bold=False)
    txt(d, (830, 1332), "out", 24, META, bold=False)

    txt(d, (540, 1440), "C O R A L   =   T H E   F L A M E   (nothing else)", 30, INK, bold=False)
    rr(d, 540, 1540, 700, 110, 18, CORAL)
    txt(d, (540, 1540), "FLAME  /  ACCENT  /  #D97757", 26, CREAM)
    txt(d, (540, 1690), "palette: cream #F0EEE6 · ink #191919 · night #1B1A18 · grey #C4BFB5", 21, META, bold=False)


SCENES = [s1, s2, s3, s4, s5, s6, s7]
GROUNDS = [NIGHT, NIGHT, NIGHT, NIGHT, NIGHT, NIGHT, CREAM]


def scene(t):
    """Timeline: 7 blocks. Filled from audio durations at render time."""
    i = 0
    for k, b in enumerate(BOUNDS[1:], start=1):
        if t >= b:
            i = k
    return min(i, len(SCENES) - 1)


def draw(t):
    i = scene(t)
    img = Image.new("RGB", (WP, HP), GROUNDS[i])
    SCENES[i](img, t - BOUNDS[i])
    if i > 0:                      # element-carried transition: a coral disc wipes the frame
        t0 = BOUNDS[i]
        r = 1180 * eio(seg(t0 - 0.32, t0, t)) if t < t0 else 1180 * (1 - eio(seg(t0, t0 + 0.44, t)))
        if r > 0.5:
            d = ImageDraw.Draw(img)
            d.ellipse([(540 - r) * S, (960 - r) * S, (540 + r) * S, (960 + r) * S], fill=CORAL)
    return img.resize((W, H), Image.LANCZOS)


# ---------------------------------------------------------------- timeline (needs audio)
AUD = ["audio/s%d.mp3" % i for i in range(1, 8)]

def probe(path):
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", err)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))

COLD, GAP, TAIL = 1.40, 0.80, 4.20
if all(os.path.exists(p) for p in AUD):
    DUR = [probe(p) for p in AUD]
else:
    DUR = [12.0] * 7
NAR = [COLD]
for d_ in DUR[:-1]:
    NAR.append(round(NAR[-1] + d_ + GAP, 3))
END_AT = round(NAR[-1] + DUR[-1] + 0.55, 3)
TOTAL = round(END_AT + TAIL, 3)
BOUNDS = [0.0] + [round(n - 0.40, 3) for n in NAR[1:]] + [END_AT]
if len(BOUNDS) < 8:
    BOUNDS.append(END_AT)
NF = int(round(TOTAL * FPS))


if __name__ == "__main__":
    os.makedirs("frames", exist_ok=True)
    if "--sheet" in sys.argv:
        img = Image.new("RGB", (WP, HP), CREAM)
        s_sheet(img)
        img.resize((W, H), Image.LANCZOS).save("frames/sheet.png")
        print("sheet written")
    elif "--test" in sys.argv:
        for name, t in (("scene1", 3.0), ("scene3", BOUNDS[2] + 3.2), ("scene7", BOUNDS[6] + 2.2)):
            draw(t).save("frames/%s.png" % name)
        print("test stills written for t=", 3.0, BOUNDS[2] + 3.2, BOUNDS[6] + 2.2)
    else:
        print("timeline", NAR, "end", END_AT, "total", TOTAL, "frames", NF)
        # audio mix
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
        out = "prof-owl-lamp-1080x1920.mp4"
        cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-i", "audio/mix.wav",
               "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(NF):
            fr_ = draw(i / FPS)
            p.stdin.write(fr_.tobytes())
            if i % 150 == 0:
                fr_.save("frames/f%04d.png" % i)
            if i % 300 == 0:
                print("  %d/%d" % (i, NF), flush=True)
        p.stdin.close()
        p.wait()
        print("done", out, os.path.getsize(out))
