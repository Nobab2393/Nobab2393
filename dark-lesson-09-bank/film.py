"""Render অন্ধকার পাঠ · পর্ব ৯ to frames and encode.

Every shot is composited once into a 1350x2400 master (1.25x screen), then the camera
crops and resizes that master per frame, so a pan is smooth and the figures are only
resampled once. Paper grain, vignette and a two-frame colour misregistration on each
cut are applied last — the misregistration is a print artefact, and it also makes the
cut land as a physical beat.

    python3 film.py                    # whole film -> build/video.mp4
    python3 film.py --stills 3,40,100  # dump frames to build/ for inspection
"""

import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import build_sheets as B
import deva
import plan as P

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "scene")
BUILD = os.path.join(HERE, "build")
W, H = 1080, 1920
M = 1.25
MW, MH = int(W * M), int(H * M)
CREAM = (240, 231, 209)
INK = (26, 23, 20)
BRICK = (150, 62, 44)
MARK_UNTIL = 9.0


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


# --------------------------------------------------------------------------- plates
_bg_cache, _fig_cache, _master_cache = {}, {}, {}


def key_alpha(im, thr=34):
    """Alpha that keeps only the figure.

    Paper is the plate's dominant colour; everything of that colour reachable from the
    border by a 4-connected flood becomes transparent. Because the flood cannot cross an
    ink contour, a white blouse or a pale saree *inside* the figure survives.
    """
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


def fix_clock(im):
    """The plate's clock was drawn at ten past ten; this story starts at eight forty."""
    cx, cy, R = 389, 446, 40
    box = (cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2)
    ss = 4
    sub = im.crop(box).resize(((box[2] - box[0]) * ss, (box[3] - box[1]) * ss), Image.LANCZOS)
    fl = np.asarray(im).reshape(-1, 3).astype(np.int16)
    keys, counts = np.unique(fl // 8, axis=0, return_counts=True)
    dom = keys[counts.argmax()]
    paper = tuple(int(v) for v in fl[(fl // 8 == dom).all(1)].mean(0))
    ink = (26, 23, 20)
    o = (cx - box[0]) * ss, (cy - box[1]) * ss
    d = ImageDraw.Draw(sub)
    d.ellipse((o[0] - 30 * ss, o[1] - 30 * ss, o[0] + 30 * ss, o[1] + 30 * ss), fill=paper)
    import math
    for i in range(12):
        ang = math.radians(i * 30)
        r0, r1 = (24 if i % 3 == 0 else 26) * ss, 30 * ss
        d.line((o[0] + r0 * math.sin(ang), o[1] - r0 * math.cos(ang),
                o[0] + r1 * math.sin(ang), o[1] - r1 * math.cos(ang)),
               fill=ink, width=2 * ss if i % 3 == 0 else 1 * ss)
    for ang_deg, ln, wd in (((8 + 40 / 60) * 30, 15, 3.4), (40 * 6, 23, 2.6)):
        ang = math.radians(ang_deg)
        d.line((o[0], o[1], o[0] + ln * ss * math.sin(ang), o[1] - ln * ss * math.cos(ang)),
               fill=ink, width=int(wd * ss))
    d.ellipse((o[0] - 3 * ss, o[1] - 3 * ss, o[0] + 3 * ss, o[1] + 3 * ss), fill=ink)
    sub = sub.resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS)
    im = im.copy()
    im.paste(sub, (box[0], box[1]))
    return im


def background(name, dark=1.0):
    key = (name, round(dark, 3))
    if key in _bg_cache:
        return _bg_cache[key]
    im = Image.open(os.path.join(SC, "bg-%s.png" % name)).convert("RGB")
    if name == "hall":
        im = fix_clock(im)
    s = max(MW / im.width, MH / im.height)
    im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
    x, y = (im.width - MW) // 2, (im.height - MH) // 2
    im = im.crop((x, y, x + MW, y + MH))
    if dark != 1.0:
        im = tint(im, dark, indigo=0.12 if dark < 0.8 else 0.0)
    im = im.convert("RGBA")
    _bg_cache[key] = im
    return im


def figure(cid):
    if cid not in _fig_cache:
        _fig_cache[cid] = key_alpha(B.trim(Image.open(
            os.path.join(HERE, "raw", "%s-neutral.png" % cid)).convert("RGB")))
    return _fig_cache[cid]


def ground_shadow(w, h, dark=1.0):
    sh = Image.new("L", (max(6, w), max(6, h)), 0)
    ImageDraw.Draw(sh).ellipse((1, 1, sh.width - 2, sh.height - 2), fill=int(110 * dark))
    sh = sh.filter(ImageFilter.GaussianBlur(max(3, h * 0.22)))
    blk = Image.new("RGBA", sh.size, (14, 11, 9, 255))
    blk.putalpha(sh)
    return blk


def master(shot_id, stage):
    if shot_id in _master_cache:
        return _master_cache[shot_id]
    dark = stage.get("dark", 1.0)
    base = background(stage["bg"], dark).copy()
    for cid, x, feet, h, dim in sorted(stage.get("figs", []), key=lambda f: f[2]):
        src = figure(cid)
        fh = int(h * M)
        fw = max(2, int(src.width * fh / src.height))
        im = src.resize((fw, fh), Image.LANCZOS)
        if dim * dark != 1.0:
            im = tint(im, dim * dark, indigo=0.12 if dark < 0.8 else 0.0)
        base.alpha_composite(ground_shadow(int(fw * 1.3), int(fh * 0.10), dark),
                             (int(x * M - fw * 0.65), int(feet * M - fh * 0.05)))
        base.alpha_composite(im, (int(x * M - fw / 2), int(feet * M - fh)))
    _master_cache[shot_id] = base
    return base


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


# --------------------------------------------------------------------------- overlays
_ov = {}


def series_mark():
    if "mark" not in _ov:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rectangle((52, 74, 464, 158), fill=(18, 15, 12, 150))
        deva.draw_text(lay, (76, 98), "অন্ধকার পাঠ", 32, 600, CREAM, anchor="lm")
        deva.draw_text(lay, (78, 136), "পর্ব ৯ · এক শাখা, দশ জন", 22, 400,
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
        deva.draw_text(art, (W // 2, 800), "অন্ধকার পাঠ", 92, 700, CREAM, anchor="mm")
        d.rectangle((W // 2 - 118, 884, W // 2 + 118, 888), fill=BRICK)
        deva.draw_text(art, (W // 2, 962), "পর্ব ৯", 60, 600, (204, 192, 166), anchor="mm")
        deva.draw_text(art, (W // 2, 1058), "এক শাখা, দশ জন", 52, 500,
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
        ms = master(shot["id"], stage)
        n = max(1, shot["f1"] - shot["f0"])
        u = (f - shot["f0"]) / n
        x, y, w, h = camera(stage, u)
        im = ms.crop((int(x), int(y), int(x + w), int(y + h))).resize((W, H), Image.BICUBIC)
        out = np.asarray(im.convert("RGB")).astype(np.float32)
        for c in plan["cuts"]:
            cf = int(round(c["t"] * plan["fps"]))
            if cf <= f < cf + 2:
                red = out[..., 0].copy()
                blu = out[..., 2].copy()
                out[..., 0] = np.roll(red, 2, axis=1)
                out[..., 2] = np.roll(blu, -2, axis=1)

    out *= tex.vig
    out += tex.grain[f % len(tex.grain)]
    out += tex.speck

    t = f / plan["fps"]
    if t < MARK_UNTIL:                       # the series mark, held over the first shots
        a = min(1.0, t / 1.2) * max(0.0, min(1.0, (MARK_UNTIL - t) / 1.6))
        if a > 0.01:
            lay = np.asarray(series_mark()).astype(np.float32)
            al = (lay[..., 3:4] / 255.0) * a
            out = out * (1 - al) + lay[..., :3] * al
    if f < 14:
        out *= ease(f / 14)
    if f > total - 22:
        out *= ease((total - f) / 22)
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--out", default=os.path.join(BUILD, "video.mp4"))
    ap.add_argument("--crf", default="18")
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

    ff = P.ffmpeg()
    cmd = [ff, "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(plan["fps"]), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", args.crf,
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", args.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(plan["frames"]):
        shot = next(s for s in plan["shots"] if s["f0"] <= i < s["f1"])
        proc.stdin.write(render_frame(plan, shot, i, tex).tobytes())
        if i % 240 == 0:
            print("  frame %4d / %d  (%.1f%%)" % (i, plan["frames"], 100.0 * i / plan["frames"]),
                  flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", args.out, os.path.getsize(args.out), "bytes")


if __name__ == "__main__":
    main()
