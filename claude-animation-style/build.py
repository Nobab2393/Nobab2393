#!/usr/bin/env python3
"""
Claude-animation-style demo — flat vector, element-carried transition, deterministic frames.
Every frame is a pure function of t (no randomness, no state, no fades).
Renderer: PIL @2x supersample -> ffmpeg (no browser needed).
"""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

# ---------- canvas ----------
S       = 2                 # supersample factor (the vector-look guarantee)
W, H    = 1080, 1920
WP, HP  = W * S, H * S
FPS     = 30
DUR     = 6.0
N       = int(FPS * DUR)

CREAM  = (240, 238, 230)
INK    = (25, 25, 25)
GREY   = (184, 180, 170)
META   = (92, 90, 85)
CORAL  = (217, 119, 87)
DOT    = (229, 226, 216)

FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
if not os.path.exists(FFMPEG):
    FFMPEG = "ffmpeg"

FONT_CANDIDATES = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
     "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
]
BOLD_PATH = REG_PATH = None
for b, r in FONT_CANDIDATES:
    if os.path.exists(b):
        BOLD_PATH, REG_PATH = b, r
        break
if BOLD_PATH is None:
    sys.exit("no font found")

_fc = {}
def fb(px):
    k = ("b", px)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(BOLD_PATH, int(px * S))
    return _fc[k]

def fr(px):
    k = ("r", px)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(REG_PATH, int(px * S))
    return _fc[k]

# ---------- easing (references/motion-grammar.md) ----------
def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v

def seg(t0, t1, t):
    return clamp((t - t0) / (t1 - t0))

def ease_out_back(t, s=1.70158):
    t = clamp(t) - 1.0
    return t * t * ((s + 1) * t + s) + 1.0

def ease_in_out(t):
    t = clamp(t)
    return 3 * t * t - 2 * t * t * t

def ease_out_expo(t):
    t = clamp(t)
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)

# ---------- drawing helpers ----------
def txt(d, xy, s, font, fill, anchor="mm"):
    d.text((xy[0] * S, xy[1] * S), s, font=font, fill=fill, anchor=anchor)

def rrect(d, cx, cy_base, w, h, r, fill):
    """rounded bar standing on a baseline: (cx, cy_base) is the bottom-centre."""
    d.rounded_rectangle(
        [(cx - w / 2) * S, (cy_base - h) * S, (cx + w / 2) * S, cy_base * S],
        radius=r * S, fill=fill)

def disc(d, cx, cy, r, fill):
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=fill)

def paste_masked_text(frame, text, cx, cy, font, fill, open_frac):
    """Words slide up out of a mask - never letter by letter, never a wipe."""
    layer = Image.new("RGBA", (WP, HP), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((cx * S, cy * S), text, font=font, fill=fill + (255,), anchor="mm")
    bbox = layer.getbbox()
    if not bbox:
        return
    top, bot = bbox[1], bbox[3]
    hide = int((bot - top) * (1.0 - open_frac))
    clip = layer.crop((0, 0, WP, bot - hide))
    frame.paste(clip, (0, 0), clip)

# ---------- the film ----------
def render(t):
    img = Image.new("RGB", (WP, HP), CREAM)
    d = ImageDraw.Draw(img)

    # ground: dot grid, anchored to the frame
    for gy in range(60, H, 60):
        for gx in range(60, W, 60):
            d.ellipse([(gx - 3) * S, (gy - 3) * S, (gx + 3) * S, (gy + 3) * S], fill=DOT)

    # --- beat A: the coral disc pops in (overshoot entrance)
    if t < 2.45:
        p = ease_out_back(seg(-0.12, 0.50, t))
        exit_k = 1.0 - ease_in_out(seg(2.15, 2.40, t))
        r = 118 * p * exit_k
        if r > 1:
            disc(d, 540, 600, r, CORAL)

    # --- beat B: three ink bars grow from the baseline, staggered
    if 0.55 <= t < 2.45:
        exit_k = 1.0 - ease_in_out(seg(2.15, 2.40, t))
        base_y = 1520
        for i, (hh, x) in enumerate([(210, 330), (360, 540), (520, 750)]):
            p = ease_out_back(seg(0.60 + i * 0.13, 1.15 + i * 0.13, t))
            h = hh * p * exit_k
            if h > 1:
                rrect(d, x, base_y, 132, h, 22, INK)

    # --- beat C: the giant number counts up (long-tail ease, lands exact)
    if 2.35 <= t < 3.80:
        p = ease_out_expo(seg(2.45, 3.45, t))
        val = str(int(round(4 * p)))
        a = ease_in_out(seg(2.35, 2.55, t)) * (1 - ease_in_out(seg(3.62, 3.78, t)))
        col = tuple(int(CREAM[c] + (CORAL[c] - CREAM[c]) * a) for c in range(3))
        txt(d, (540, 880), val, fb(560), col, anchor="mm")
        txt(d, (540, 1200), "t h e   a c c e n t", fr(40), META, anchor="mm")

    # --- beat D: the disc grows to fill the frame and BECOMES the next ground
    if t >= 3.78:
        r = 1180 * ease_in_out(seg(3.78, 4.28, t))
        if r > 1:
            disc(d, 540, 960, r, CORAL)

    # --- beat E: type on the new ground, drawn word-whole out of a mask
    if t >= 4.28:
        paste_masked_text(img, "ONE ACCENT.", 540, 820, fb(104), CREAM, seg(4.28, 4.62, t))
        paste_masked_text(img, "ONE MEANING.", 540, 960, fb(104), CREAM, seg(4.46, 4.80, t))
        rl = 320 * ease_in_out(seg(4.70, 5.10, t))
        if rl > 1:
            d2 = ImageDraw.Draw(img)
            d2.rectangle([(540 - rl / 2) * S, 1052 * S, (540 + rl / 2) * S, 1056 * S], fill=CREAM)
        if t >= 5.05:
            d2 = ImageDraw.Draw(img)
            txt(d2, (540, 1180), "claude animation style", fr(38), CREAM, anchor="mm")

    return img.resize((W, H), Image.LANCZOS)


def main():
    os.makedirs("frames", exist_ok=True)
    out = "claude-animation-style-demo-1080x1920.mp4"
    cmd = [FFMPEG, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N):
        t = i / FPS
        frame = render(t)
        p.stdin.write(frame.tobytes())
        if i in (0, 15, 60, 90, 120, 170):
            frame.save("frames/f%03d.png" % i)
        if i % 30 == 0:
            print("  frame %d/%d  t=%.2fs" % (i, N, t), flush=True)
    p.stdin.close()
    p.wait()
    print("done:", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
