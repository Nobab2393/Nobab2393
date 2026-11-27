"""Render অন্ধকার পাঠ · পর্ব ১০ — গেটে তালা.

Same camera as episode 9 (one master per shot, cropped per frame), except that a shot
with a walking figure is composited fresh every frame: the figure travels across the
frame, bobs on a step cycle, rolls about its own feet, and swaps to its mid-stride
plate. Shots with nobody moving take the cheaper cached path and get their life from a
slow drift of the frame.

    python3 film.py                     # whole film -> build/video.mp4
    python3 film.py --stills 3,40,100   # stills into build/
"""

import argparse
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import build_sheets as B
import deva
import plan as P

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "scene")
RAW = os.path.join(HERE, "raw")
BUILD = os.path.join(HERE, "build")
W, H = 1080, 1920
M = 1.25
MW, MH = int(W * M), int(H * M)
CREAM = (240, 231, 209)
INK = (26, 23, 20)
BRICK = (150, 62, 44)
STEP = 0.46                     # seconds per step
MARK_UNTIL = 9.0

_bg, _plate, _scaled, _master = {}, {}, {}, {}


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def tint(im, factor, indigo=0.0):
    a = np.asarray(im).astype(np.float32)
    if factor != 1.0:
        a[..., :3] *= factor
    if indigo:
        a[..., 2] = np.clip(a[..., 2] * (1 + indigo) + 5 * indigo, 0, 255)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), im.mode)


# --------------------------------------------------------------------------- keying
def key_alpha(im, thr=34, paperish=False):
    if paperish:
        return key_alpha_light(im)
    return key_alpha_colour(im, thr)


def key_alpha_light(im):
    """Key on "light and near-neutral" instead of on one paper colour.

    10-babul's sheet was drawn inside a second, lighter cream panel; a colour-distance
    flood stops dead at that panel's edge and leaves a rectangle behind him. His coverall
    is dark blue and his skin is saturated, so a brightness test cannot eat him, and the
    panel is only reachable because it touches the outer margin.
    """
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    h, w = a.shape[:2]
    sf = 2 if max(h, w) > 400 else 1
    small = a[::sf, ::sf]
    lo = small.min(2)
    hi = small.max(2)
    like = (lo > 182) & ((hi - lo) < 52)
    reach = np.zeros_like(like)
    reach[0, :] = like[0, :]
    reach[-1, :] = like[-1, :]
    reach[:, 0] = like[:, 0]
    reach[:, -1] = like[:, -1]
    while True:
        new = (reach | np.roll(reach, 1, 0) | np.roll(reach, -1, 0)
               | np.roll(reach, 1, 1) | np.roll(reach, -1, 1)) & like
        if new.sum() == reach.sum():
            break
        reach = new
    figm = ~reach
    figm = (figm & np.roll(figm, 1, 0) & np.roll(figm, -1, 0)
            & np.roll(figm, 1, 1) & np.roll(figm, -1, 1))
    alpha = Image.fromarray((figm * 255).astype(np.uint8), "L")
    alpha = alpha.resize((w, h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.0))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out


def key_alpha_colour(im, thr=34):
    """Keep only the figure: flood the paper inwards from the border."""
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    h, w = a.shape[:2]
    sf = 2 if max(h, w) > 400 else 1
    small = a[::sf, ::sf]
    flat = small.reshape(-1, 3)
    keys, counts = np.unique(flat // 8, axis=0, return_counts=True)
    dom = keys[counts.argmax()]
    sel = (flat // 8 == dom).all(1)
    paper = flat[sel].mean(0) if sel.any() else np.median(flat, 0)
    like = np.abs(small - paper).max(2) < thr
    reach = np.zeros_like(like)
    reach[0, :] = like[0, :]
    reach[-1, :] = like[-1, :]
    reach[:, 0] = like[:, 0]
    reach[:, -1] = like[:, -1]
    while True:
        new = (reach | np.roll(reach, 1, 0) | np.roll(reach, -1, 0)
               | np.roll(reach, 1, 1) | np.roll(reach, -1, 1)) & like
        if new.sum() == reach.sum():
            break
        reach = new
    figm = ~reach
    figm = (figm & np.roll(figm, 1, 0) & np.roll(figm, -1, 0)
            & np.roll(figm, 1, 1) & np.roll(figm, -1, 1))
    alpha = Image.fromarray((figm * 255).astype(np.uint8), "L")
    alpha = alpha.resize((w, h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.0))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out


def strip_rules(im, frac=0.55):
    """Drop any drawn border rule left at the edge of a plate.

    A couple of these sheets came with a black keyline around the drawing; the trim
    keeps it because it is content, and then it shows up as a thin strip under the feet.
    """
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    dark = a.max(2) < 95
    rows = dark.mean(1)
    cols = dark.mean(0)
    t, b, l, r = 0, rows.size, 0, cols.size
    while t < b and rows[t] > frac:
        t += 1
    while b > t + 8 and rows[b - 1] > frac:
        b -= 1
    while l < r and cols[l] > frac:
        l += 1
    while r > l + 8 and cols[r - 1] > frac:
        r -= 1
    if (t, b, l, r) != (0, rows.size, 0, cols.size):
        im = im.crop((l, t, r, b))
    return im


def figure(cid, pose="neutral"):
    key = (cid, pose)
    if key in _plate:
        return _plate[key]
    path = os.path.join(RAW, "%s-%s.png" % (cid, pose))
    if not os.path.exists(path):
        if pose != "neutral":
            _plate[key] = figure(cid, "neutral")
            return _plate[key]
        raise FileNotFoundError(path)
    panel = cid == "10-babul"
    src = strip_rules(B.trim(Image.open(path).convert("RGB")))
    im = key_alpha(src, paperish=panel)
    _plate[key] = im
    return im


# --------------------------------------------------------------------------- stage
def background(name, dark=1.0):
    key = (name, round(dark, 3))
    if key in _bg:
        return _bg[key]
    im = Image.open(os.path.join(SC, "bg-%s.png" % name)).convert("RGB")
    s = max(MW / im.width, MH / im.height)
    im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
    x, y = (im.width - MW) // 2, (im.height - MH) // 2
    im = im.crop((x, y, x + MW, y + MH))
    if dark != 1.0:
        im = tint(im, dark, indigo=0.12 if dark < 0.8 else 0.0)
    _bg[key] = im
    return im


def scaled(cid, pose, h, dim, dark):
    key = (cid, pose, int(h * M), round(dim * dark, 2))
    if key in _scaled:
        return _scaled[key]
    src = figure(cid, pose)
    fh = int(h * M)
    fw = max(2, int(src.width * fh / src.height))
    im = src.resize((fw, fh), Image.LANCZOS)
    f = dim * dark
    if round(f, 2) != 1.0:
        im = tint(im, f, indigo=0.12 if dark < 0.8 else 0.0)
    _scaled[key] = im
    return im


def ground_shadow(w, h, dark):
    sh = Image.new("L", (max(6, w), max(6, h)), 0)
    ImageDraw.Draw(sh).ellipse((2, 2, sh.width - 3, sh.height - 3), fill=int(72 * dark))
    sh = sh.filter(ImageFilter.GaussianBlur(max(4, h * 0.30)))
    blk = Image.new("RGBA", sh.size, (14, 11, 9, 255))
    blk.putalpha(sh)
    return blk


def motion(fig, t):
    cid, x0, x1, feet, h, dim, m0, m1 = fig
    moving = m1 > m0 and m0 <= t <= m1
    if moving:
        u = (t - m0) / max(1e-6, m1 - m0)
        x = x0 + (x1 - x0) * ease(u)
        phase = 2 * math.pi * t / STEP
        pose = "walk"
        amp, roll = 2.4, 1.35 * math.sin(phase)
    else:
        x = x0 if t < m0 else x1
        phase = 2 * math.pi * t / 3.4
        pose = "neutral"
        amp, roll = 0.9, 0.22 * math.sin(phase)
    dy = -abs(math.sin(phase)) * amp
    return x, dy, pose, roll, moving


def any_moving(stage):
    return any(f[7] > f[6] for f in stage.get("figs", []))


def compose(stage, t):
    dark = stage.get("dark", 1.0)
    canvas = background(stage["bg"], dark).copy()
    for fig in sorted(stage.get("figs", []), key=lambda f: f[3]):
        cid, x0, x1, feet, h, dim, m0, m1 = fig
        x, dy, pose, roll, moving = motion(fig, t)
        im = scaled(cid, pose, h, dim, dark)
        if moving and abs(roll) > 0.05:
            im = im.rotate(roll, resample=Image.BILINEAR, center=(im.width / 2, im.height))
        px = int(x * M - im.width / 2)
        py = int((feet + dy) * M - im.height)
        sh = ground_shadow(int(im.width * 0.95), int(im.height * 0.075), dark)
        canvas.paste(sh, (int(x * M - im.width * 0.475),
                          int((feet + dy) * M - im.height * 0.035)), sh)
        canvas.paste(im, (px, py), im)
    return canvas


def master(shot_id, stage):
    if shot_id not in _master:
        _master[shot_id] = compose(stage, 0.0)
    return _master[shot_id]


def camera(stage, u):
    cx0, cy0, z0, cx1, cy1, z1 = stage["cam"]
    k = ease(u)
    cx = (cx0 + (cx1 - cx0) * k) * M
    cy = (cy0 + (cy1 - cy0) * k) * M
    z = z0 + (z1 - z0) * k
    w, h = MW / z, MH / z
    x = min(max(cx - w / 2, 0), MW - w)
    y = min(max(cy - h / 2, 0), MH - h)
    return x, y, w, h


# --------------------------------------------------------------------------- textures
class Textures:
    def __init__(self):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dx = (xx - W / 2) / (W / 2)
        dy = (yy - H / 2) / (H / 2)
        r = np.sqrt(dx * dx * 0.80 + dy * dy * 0.70)
        self.vig = np.clip(1.05 - 0.28 * np.power(np.clip(r, 0, 1.7), 2.2),
                           0.40, 1.0)[..., None].astype(np.float32)
        rng = np.random.default_rng(7)
        self.grain = []
        for _ in range(8):
            base = rng.normal(0, 5.0, (H // 4, W // 4))
            im = Image.fromarray(np.clip(base + 128, 0, 255).astype(np.uint8), "L")
            self.grain.append((np.asarray(im.resize((W, H), Image.BILINEAR))
                               .astype(np.float32) - 128)[..., None])
        sp = np.zeros((H, W), np.float32)
        for _ in range(80):
            x, y = rng.integers(0, W), rng.integers(0, H)
            r = int(rng.integers(1, 3))
            sp[max(0, y - r):y + r, max(0, x - r):x + r] = -16
        self.speck = sp[..., None]


_ov = {}


def series_mark():
    if "mark" not in _ov:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rectangle((52, 74, 464, 158), fill=(18, 15, 12, 150))
        deva.draw_text(lay, (76, 98), "অন্ধকার পাঠ", 32, 600, CREAM, anchor="lm")
        deva.draw_text(lay, (78, 136), "পর্ব ১০ · গেটে তালা", 22, 400,
                       (206, 195, 170), anchor="lm")
        _ov["mark"] = lay
    return _ov["mark"]


def end_card():
    if "card" not in _ov:
        tex = np.asarray(Image.fromarray(
            np.clip(np.random.default_rng(3).normal(0, 8, (H // 3, W // 3)) + 128, 0, 255)
            .astype(np.uint8), "L").resize((W, H), Image.BILINEAR)).astype(np.int16)
        a = np.zeros((H, W, 3), np.int16) + np.array(INK, np.int16)
        a = np.clip(a + (tex[..., None] - 128) // 3, 0, 255)
        art = Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")
        d = ImageDraw.Draw(art)
        deva.draw_text(art, (W // 2, 800), "গেটে তালা", 96, 700, CREAM, anchor="mm")
        d.rectangle((W // 2 - 118, 884, W // 2 + 118, 888), fill=BRICK)
        deva.draw_text(art, (W // 2, 962), "অন্ধকার পাঠ · পর্ব ১০", 44, 600,
                       (204, 192, 166), anchor="mm")
        deva.draw_text(art, (W // 2, 1050), "এক শিফট, দশ জন", 40, 500,
                       (226, 215, 190), anchor="mm")
        _ov["card"] = art
    return _ov["card"]


# --------------------------------------------------------------------------- frames
def render_frame(plan, shot, f, tex):
    total = plan["frames"]
    if shot["id"] == "card":
        card = end_card()
        n = max(1, shot["f1"] - shot["f0"])
        u = (f - shot["f0"]) / n
        out = np.asarray(card.convert("RGB")).astype(np.float32) * ease(u / 0.22)
    else:
        stage = shot["stage"]
        n = max(1, shot["f1"] - shot["f0"])
        u = (f - shot["f0"]) / n
        t = (f - shot["f0"]) / plan["fps"]
        if any_moving(stage):
            ms = compose(stage, t)
        else:
            ms = master(shot["id"], stage)
            u = min(1.0, u + 0.004 * math.sin(2 * math.pi * f / 82.0))
        x, y, w, h = camera(stage, u)
        im = ms.crop((int(x), int(y), int(x + w), int(y + h))).resize((W, H), Image.BICUBIC)
        out = np.asarray(im.convert("RGB")).astype(np.float32)
        for c in plan["cuts"]:
            cf = int(round(c["t"] * plan["fps"]))
            if cf <= f < cf + 2:
                out[..., 0] = np.roll(out[..., 0].copy(), 2, axis=1)
                out[..., 2] = np.roll(out[..., 2].copy(), -2, axis=1)

    out *= tex.vig
    out += tex.grain[f % len(tex.grain)]
    out += tex.speck

    tt = f / plan["fps"]
    if tt < MARK_UNTIL:
        a = min(1.0, tt / 1.2) * max(0.0, min(1.0, (MARK_UNTIL - tt) / 1.6))
        if a > 0.01:
            lay = np.asarray(series_mark()).astype(np.float32)
            al = (lay[..., 3:4] / 255.0) * a
            out = out * (1 - al) + lay[..., :3] * al
    if f < 14:
        out *= ease(f / 14)
    if f > total - 26:
        out *= ease((total - f) / 26)
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--out", default=os.path.join(BUILD, "video.mp4"))
    ap.add_argument("--crf", default="22")
    args = ap.parse_args()
    os.makedirs(BUILD, exist_ok=True)
    plan = P.build()
    tex = Textures()

    if args.stills:
        for tv in [float(v) for v in args.stills.split(",")]:
            f = int(round(tv * plan["fps"]))
            shot = next(s for s in plan["shots"] if s["f0"] <= f < s["f1"])
            arr = render_frame(plan, shot, f, tex)
            p = os.path.join(BUILD, "still-%06.1f.png" % tv)
            Image.fromarray(arr).save(p)
            print("wrote", p, shot["id"])
        return

    cmd = [P.ffmpeg(), "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(plan["fps"]), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", args.crf,
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", args.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(plan["frames"]):
        shot = next(s for s in plan["shots"] if s["f0"] <= i < s["f1"])
        proc.stdin.write(render_frame(plan, shot, i, tex).tobytes())
        if i % 240 == 0:
            print("  frame %4d / %d  (%.1f%%)" % (i, plan["frames"],
                                                  100.0 * i / plan["frames"]), flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", args.out, os.path.getsize(args.out), "bytes")


if __name__ == "__main__":
    main()
