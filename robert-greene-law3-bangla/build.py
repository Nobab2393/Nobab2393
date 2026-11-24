#!/usr/bin/env python3
"""
ROBERT GREENE — LAW III: CONCEAL YOUR INTENTIONS
Bangla narration, Claude 2D animation style (code-drawn flat vector), 1080x1920, 30 fps.

Rules followed (from ai-video-skills/.../claude-animation-style + animation-style-atlas):
  - flat vector, cream ground #F0EEE6, warm ink #191919, ONE accent (coral) with ONE meaning:
    coral = the hidden thing (the real intention)
  - every frame is a pure function of t; overshoot entrances, 2-4 frame staggers
  - transitions are carried by an element: a coral disc fills the frame and becomes the next ground
  - no fades, no gradients, no pure black/white, outlines 0 (flat shapes) at >= 3 px equivalents
  - text set whole, never letter by letter; kept out of the moving layer

Audio: 6 Bangla segments (voice-05), placed on a timeline with gaps, then muxed.
"""
import math, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

S = 2
W, H = 1080, 1920
WP, HP = W * S, H * S
FPS = 30

CREAM = (240, 238, 230)
CARD = (250, 249, 245)
INK = (25, 25, 25)
GREY = (196, 191, 181)
META = (118, 113, 103)
CORAL = (217, 119, 87)
CORAL_D = (189, 93, 58)

FFMPEG = os.environ.get("FFMPEG_BIN") or "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
if not os.path.exists(FFMPEG):
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_f = {}
def f_bold(px):
    if ("b", px) not in _f:
        _f[("b", px)] = ImageFont.truetype(BOLD, int(px * S))
    return _f[("b", px)]

def f_reg(px):
    if ("r", px) not in _f:
        _f[("r", px)] = ImageFont.truetype(REG, int(px * S))
    return _f[("r", px)]


# ------------------------------------------------------------------ easing
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


# ------------------------------------------------------------------ draw helpers
def txt(d, xy, s, px, fill, bold=True, anchor="mm"):
    d.text((xy[0] * S, xy[1] * S), s, font=(f_bold(px) if bold else f_reg(px)), fill=fill, anchor=anchor)

def disc(d, cx, cy, r, fill):
    if r <= 0.4:
        return
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=fill)

def rrect(d, cx, cy, w, h, r, fill, rot=0.0):
    """rounded rect centred at cx,cy, optionally rotated (radians)."""
    if w <= 0.5 or h <= 0.5:
        return
    if abs(rot) < 1e-4:
        d.rounded_rectangle([(cx - w / 2) * S, (cy - h / 2) * S, (cx + w / 2) * S, (cy + h / 2) * S],
                            radius=max(1, r) * S, fill=fill)
        return
    pts = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append(((cx + dx * math.cos(rot) - dy * math.sin(rot)) * S,
                    (cy + dx * math.sin(rot) + dy * math.cos(rot)) * S))
    d.polygon(pts, fill=fill)

def chip(img, cx, cy, label, fill, fg, px=30, padx=24, pady=14):
    d = ImageDraw.Draw(img)
    f = f_bold(px)
    bb = d.textbbox((0, 0), label, font=f)
    w = (bb[2] - bb[0]) / S + padx * 2
    h = (bb[3] - bb[1]) / S + pady * 2
    rrect(d, cx, cy, w, h, h / 2, fill)
    d.text((cx * S, cy * S), label, font=f, fill=fg, anchor="mm")
    return w

def dots(d, alpha_col=GREY):
    for gy in range(64, H, 64):
        for gx in range(64, W, 64):
            disc(d, gx, gy, 2.6, (231, 228, 218))



def card_tile(w, h, fill, outline, pw=5, rad=18):
    tile = Image.new("RGBA", (int((w + 10) * S), int((h + 10) * S)), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    td.rounded_rectangle([5 * S, 5 * S, (w + 5) * S, (h + 5) * S], radius=rad * S,
                         fill=fill, outline=outline, width=int(pw * S))
    return tile


def paste_card(img, cx, cy, w, h, ang, fill, outline):
    tile = card_tile(w, h, fill, outline)
    tile = tile.rotate(math.degrees(ang), expand=True, resample=Image.BICUBIC)
    img.paste(tile, (int(cx * S - tile.width / 2), int(cy * S - tile.height / 2)), tile)


# ------------------------------------------------------------------ the seven scenes
def scene_hook(img, lt):
    """A giant III, and the coral intention the numeral keeps covering."""
    d = ImageDraw.Draw(img)
    dots(d)
    txt(d, (540, 430), "R O B E R T   G R E E N E", 30, META, bold=False, anchor="mm")
    # the coral dot travels across and goes behind the numeral (drawn first, on purpose)
    slide = eio(seg(0.55, 2.20, lt))
    dx = 150 + 700 * slide
    dy = 900 - 70 * math.sin(slide * math.pi)
    disc(d, dx, dy, 56, CORAL)
    # three bars = roman III, rising with a stagger, drawn over the dot
    for i, x in enumerate((410, 540, 670)):
        q = eback(seg(0.18 + i * 0.09, 0.86 + i * 0.09, lt))
        hh = 560 * q
        rrect(d, x, 1180 - hh / 2, 62, hh, 6, INK)
    if lt > 1.2:
        txt(d, (540, 1450), "L A W   T H R E E", 40, INK, anchor="mm")
    if lt > 1.9:
        txt(d, (540, 1540), "the intention stays behind the shape", 30, META, bold=False)


def scene_cards(img, lt):
    """Five cards fan open, and every one of them is face up."""
    d = ImageDraw.Draw(img)
    dots(d)
    open_p = eback(seg(0.10, 0.95, lt))
    for i in range(5):
        a = math.radians(-32 + 16 * i) * open_p
        cx = 540 + math.sin(a) * 430
        cy = 1390 - math.cos(a) * 430
        q = eback(seg(0.10 + i * 0.07, 0.72 + i * 0.07, lt))
        w, h = 210 * q, 320 * q
        if q > 0.03:
            paste_card(img, cx, cy, w, h, -a, CARD, INK)          # card
            rv = eio(seg(1.55 + i * 0.06, 1.95 + i * 0.06, lt))   # then its own pip,
            if rv > 0.02:                                         # so the next card covers it
                disc(d, cx, cy, 30 * rv, CORAL)
    if lt > 2.4:
        chip(img, 540, 590, "SHOW YOUR HAND — LOSE", INK, CREAM, px=34)
    if lt > 3.1:
        txt(d, (540, 690), "everyone can now read you", 29, META, bold=False)


def scene_mask(img, lt):
    """A mask slides up over a face; the coral eyes go dark behind it."""
    d = ImageDraw.Draw(img)
    dots(d)
    disc(d, 540, 1030, 272, CARD)                       # the face, wider than the mask
    eye = eio(seg(0.15, 0.55, lt)) * (1 - eio(seg(2.35, 2.75, lt)))
    disc(d, 450, 985, 38 * eye, CORAL)
    disc(d, 630, 985, 38 * eye, CORAL)
    up = eio(seg(0.95, 2.35, lt))                       # the mask rises from below
    my = 1500 - 620 * up
    rrect(d, 540, my, 412, 470, 96, INK)
    for ex in (450, 630):
        disc(d, ex, my - 34, 46, CREAM)
    if up > 0.88:                                        # eyes behind the mask: no light
        for ex in (450, 630):
            disc(d, ex, my - 34, 20, (64, 62, 58))
    txt(d, (540, 500), "W H A T   T H E Y   S E E", 30, META, bold=False)
    if lt > 2.9:
        chip(img, 540, 1660, "THE MASK IS THE MESSAGE", INK, CREAM, px=32)


def scene_hook_bait(img, lt):
    """A line, a hook, and a bait the fish never questions."""
    d = ImageDraw.Draw(img)
    dots(d)
    txt(d, (540, 300), "T H E   B A I T   I S   S H O W N", 30, META, bold=False)
    d.rectangle([0, 760 * S, WP, 764 * S], fill=GREY)    # the water line
    drop = eio(seg(0.05, 0.9, lt))
    ly = 420 + 400 * drop
    d.rectangle([540 * S, 420 * S, 546 * S, ly * S], fill=INK)
    d.arc([500 * S, (ly - 40) * S, 580 * S, (ly + 40) * S], start=0, end=200, fill=INK, width=9 * S)
    disc(d, 540, ly + 60, 40 * spr(seg(0.9, 1.4, lt)), CORAL)     # the bait: the only bright thing
    fx = -280 + 660 * eio(seg(1.3, 3.2, lt))                      # the fish, from the left
    fy = ly + 74
    d.ellipse([(fx - 92) * S, (fy - 52) * S, (fx + 92) * S, (fy + 52) * S], fill=INK)
    d.polygon([((fx - 86) * S, fy * S), ((fx - 162) * S, (fy - 46) * S),
               ((fx - 162) * S, (fy + 46) * S)], fill=INK)
    disc(d, fx + 46, fy - 12, 10, CREAM)
    if lt > 3.0:
        chip(img, 540, 1700, "THE HOOK STAYS HIDDEN", CORAL_D, CREAM, px=32)


def scene_two_people(img, lt):
    """One talks, one doesn't. The accent lives inside the quiet one."""
    d = ImageDraw.Draw(img)
    dots(d)
    for cx in (330, 750):
        disc(d, cx, 1120, 116, CARD)
        rrect(d, cx, 1420, 236, 320, 64, INK)
        disc(d, cx, 1500, 24, CREAM)
    # the talker's mouth opens with each bubble
    for i in range(4):
        q = eback(seg(0.25 + i * 0.30, 0.55 + i * 0.30, lt))
        if q > 0.02:
            mw = 10 + 16 * abs(math.sin(lt * 5.0 + i))
            rrect(d, 330, 1176, 46, 30 * q, 12, INK)
        if q > 0.02:
            bx = 236 - i * 52
            by = 980 - i * 108
            disc(d, bx, by, 44 * q, CORAL)
    if lt > 1.5:                                        # the quiet one: nothing out, one dot in
        disc(d, 750, 1420, 36 * spr(seg(1.5, 2.0, lt)), CORAL)
    txt(d, (330, 760), "T H E   T A L K E R", 28, META, bold=False)
    txt(d, (750, 760), "T H E   O P E R A T O R", 28, META, bold=False)
    if lt > 2.6:
        chip(img, 540, 1740, "SAY LESS, KEEP MORE", INK, CREAM, px=32)


def scene_box(img, lt):
    """A closed chest with a keyhole — and a gap that shows only once."""
    d = ImageDraw.Draw(img)
    dots(d)
    txt(d, (540, 620), "T H E   S H E L L   I S   P U B L I C", 28, META, bold=False)
    rrect(d, 540, 1180, 470, 380, 26, INK)              # the body
    peek = eio(seg(1.30, 1.75, lt)) * (1 - eio(seg(2.70, 3.05, lt)))
    if peek > 0.02:                                     # the kernel, seen for one beat only
        rrect(d, 540, 962, 92 * peek, 54 * peek, 10, CORAL)
    lift = peek
    rrect(d, 540, 946 - 16 * lift, 522, 88, 20, INK)    # the lid
    disc(d, 540, 1160, 46, CREAM)                       # keyhole
    d.polygon([(514 * S, 1160 * S), (566 * S, 1160 * S), (556 * S, 1252 * S), (524 * S, 1252 * S)], fill=CREAM)
    if lt > 3.0:
        chip(img, 540, 1700, "THE KERNEL IS NOT", CORAL_D, CREAM, px=32)


def scene_end(img, lt):
    d = ImageDraw.Draw(img)
    dots(d)
    p = eback(seg(0.0, 0.6, lt))
    txt(d, (540, 700), "L A W   T H R E E", 44, META, bold=False)
    for i in range(3):
        q = eback(seg(0.1 + i * 0.08, 0.7 + i * 0.08, lt))
        txt(d, (540, 860 + i * 96), ("CONCEAL", "YOUR", "INTENTIONS")[i], 84, INK)
    rrect(d, 540, 1240, 320 * eio(seg(0.5, 0.9, lt)), 10, 5, CORAL)
    txt(d, (540, 1380), "48 L A W S   O F   P O W E R", 30, META, bold=False)
    txt(d, (540, 1640), "Bangla voiceover · code-drawn", 28, META, bold=False)


# ------------------------------------------------------------------ timeline
def probe(path):
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", err)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


AUD = sorted([p for p in ("audio/s%d.mp3" % i for i in range(1, 7)) if os.path.exists(p)])
DUR = [probe(p) for p in AUD]
COLD, GAP, TAIL = 1.40, 0.80, 4.60
NAR = [COLD]
for d in DUR[:-1]:
    NAR.append(round(NAR[-1] + d + GAP, 3))
END_AT = round(NAR[-1] + DUR[-1] + 0.55, 3)
TOTAL = round(END_AT + TAIL, 3)

SCENES = [scene_hook, scene_cards, scene_mask, scene_hook_bait, scene_two_people, scene_box]
TRANS = 0.80            # element-carried disc transition, centred on each scene change
BOUNDS = [0.0] + [round(n - 0.40, 3) for n in NAR[1:]] + [END_AT]
NF = int(round(TOTAL * FPS))


def scene_index(t):
    for i in range(len(BOUNDS) - 1, -1, -1):
        if t >= BOUNDS[i]:
            return min(i, len(SCENES))
    return 0


def draw(t):
    i = scene_index(t)
    fn = SCENES[i] if i < len(SCENES) else scene_end
    img = Image.new("RGB", (WP, HP), CREAM)
    fn(img, t - BOUNDS[i])

    # element-carried transition: a coral disc covers the outgoing scene,
    # then shrinks and reveals the incoming one
    if i > 0:
        t0 = BOUNDS[i]
        r = 1180 * eio(seg(t0 - 0.34, t0, t)) if t < t0 else 1180 * (1 - eio(seg(t0, t0 + 0.46, t)))
        if r > 0.5:
            d = ImageDraw.Draw(img)
            d.ellipse([(540 - r) * S, (960 - r) * S, (540 + r) * S, (960 + r) * S], fill=CORAL)
    return img.resize((W, H), Image.LANCZOS)


def build_audio():
    inputs, filt, labels = [], [], []
    for k, (p, start) in enumerate(zip(AUD, NAR)):
        inputs += ["-i", p]
        ms = int(round(start * 1000))
        filt.append("[%d:a]adelay=%d|%d,volume=1.0[a%d]" % (k, ms, ms, k))
        labels.append("[a%d]" % k)
    fc = (";".join(filt) + ";" + "".join(labels)
          + "amix=inputs=%d:normalize=0:dropout_transition=0,apad[a]" % len(AUD))
    out = "audio/mix.wav"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error"] + inputs +
                   ["-filter_complex", fc, "-map", "[a]", "-ar", "44100", "-ac", "2",
                    "-t", "%.3f" % TOTAL, out], check=True)
    return out


def main():
    os.makedirs("frames", exist_ok=True)
    print("narration starts:", NAR)
    print("total duration: %.2fs  (%d frames)" % (TOTAL, NF))
    mix = build_audio()
    out = "robert-greene-law3-bangla-1080x1920.mp4"
    cmd = [FFMPEG, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-i", mix, "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    shots = {int(b * FPS) + 20 for b in BOUNDS if b > 0}
    for i in range(NF):
        t = i / FPS
        fr = draw(t)
        p.stdin.write(fr.tobytes())
        if i % 150 == 0 or i in shots:
            fr.save("frames/f%04d.png" % i)
        if i % 300 == 0:
            print("  %d/%d  t=%.1fs" % (i, NF, t), flush=True)
    p.stdin.close()
    p.wait()
    print("done:", out, os.path.getsize(out))


if __name__ == "__main__":
    main()
