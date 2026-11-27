"""Render অন্ধকার পাঠ · পর্ব ১১ — দশ প্লেট.

The cast are 2D cutout puppets, so the acting is in the joints, not in the legs. Every
figure is a flat RGBA plate; per frame it is cut into slabs and each slab is turned a
degree or two about its own pin:

    head slab    — y 0 → NECK, turned about the neck pins (a look)
    shoulder slab— NECK → COLLAR, shifted and turned about the collar (a breath, a shrug)
    whole body   — turned about the feet (a lean), or pushed a centimetre forward

Nothing walks. The camera does the travelling, inside the one room.

    python3 film.py                     # whole film -> build/video.mp4
    python3 film.py --stills 5,40,100   # stills into build/
"""

import argparse
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import deva
import plan as P

HERE = os.path.dirname(os.path.abspath(__file__))
CAST = os.path.join(HERE, "cast")
SC = os.path.join(HERE, "scene")
BUILD = os.path.join(HERE, "build")
W, H = 1080, 1920
M = 1.25
MW, MH = int(W * M), int(H * M)
CREAM = (243, 236, 222)
INK = (28, 25, 22)
BRICK = (163, 66, 44)
NECK = 0.155             # head slab ends here, as a fraction of the figure's height
COLLAR = 0.245           # shoulder slab ends here

_bg, _plate, _scaled, _master = {}, {}, {}, {}


# --------------------------------------------------------------------------- helpers
def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def stage_dark(stage, u):
    d = stage.get("dark", 1.0)
    if isinstance(d, (tuple, list)):
        return d[0] + (d[1] - d[0]) * ease(u)
    return d


def grade(im, dark):
    """Night: pull the light down and let the indigo in. 1.0 leaves the plate alone."""
    if dark >= 0.999:
        return im
    a = np.asarray(im).astype(np.float32)
    a[..., :3] *= dark
    a[..., 2] = np.clip(a[..., 2] * (1 + 0.16 * (1 - dark)) + 10 * (1 - dark), 0, 255)
    a[..., 0] *= 1 - 0.10 * (1 - dark)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), im.mode)


def background(name):
    key = name
    if key not in _bg:
        im = Image.open(os.path.join(SC, "bg-%s.png" % name)).convert("RGB")
        s = max(MW / im.width, MH / im.height)
        im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
        x = (im.width - MW) // 2
        y = (im.height - MH) // 2
        _bg[key] = im.crop((x, y, x + MW, y + MH))
    return _bg[key]


def plate(cid):
    if cid not in _plate:
        _plate[cid] = Image.open(os.path.join(CAST, cid + "-neutral.png")).convert("RGBA")
    return _plate[cid]


def scaled(cid, h, dim, dark):
    key = (cid, int(h), round(dim, 2), round(dark, 2))
    if key not in _scaled:
        im = plate(cid)
        s = h * M / im.height
        im = im.resize((max(1, int(im.width * s)), max(1, int(h * M))), Image.LANCZOS)
        if dim < 0.999:
            a = np.asarray(im).astype(np.float32)
            a[..., :3] *= dim
            im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
        _scaled[key] = im
    return _scaled[key].copy()


def turn(band, ang, pivot_in_band):
    return band.rotate(ang, resample=Image.BICUBIC, center=pivot_in_band, expand=False)


def add_slab(base, band, y0, ang, pivot_y):
    """Paste a turned slab back into the figure, clearing what was under it first."""
    rot = turn(band, ang, (band.width / 2.0, pivot_y - y0))
    base.paste(Image.new("RGBA", band.size, (0, 0, 0, 0)), (0, y0))
    base.alpha_composite(rot, (0, y0))
    return base


# --------------------------------------------------------------------------- acting
def act_value(fig, kind, t):
    """How far through a gesture the figure is (0..1), and its signed amount."""
    for a in fig["acts"]:
        if a[0] != kind or len(a) < 4:
            continue
        k, t0, t1, amt = a[0], a[1], a[2], a[3]
        if t0 <= t <= t1:
            u = (t - t0) / max(1e-6, (t1 - t0))
            # in over the first third, out over the last third
            w = ease(min(1.0, u / 0.34)) * ease(min(1.0, (1 - u) / 0.34))
            return w * amt
    return 0.0


def idle(fig, t):
    """Breath and micro-sway, seeded so ten puppets never move together."""
    ph = t * 2 * math.pi / 3.6 + fig["seed"] * 1.7
    breath = 0.55 * math.sin(ph)
    sway = 0.24 * math.sin(ph / 2.3 + 1.1)
    turn_ang = 0.5 * math.sin(ph / 3.1 + 0.4)
    return breath, sway, turn_ang


def pose(fig, t):
    breath, sway, micro = idle(fig, t)
    head = act_value(fig, "look", t) + (0.0 if fig["c"] == "10-the-tenth" else micro)
    lean = act_value(fig, "lean", t) + sway
    adv = act_value(fig, "advance", t)
    if fig["c"] == "10-the-tenth":
        head = 0.0        # the one thing you never see is his face turning
    return breath, head, lean, adv


# --------------------------------------------------------------------------- figures
def ground_shadow(w, h, dark):
    sh = Image.new("L", (max(6, w), max(6, h)), 0)
    ImageDraw.Draw(sh).ellipse((2, 2, sh.width - 3, sh.height - 3), fill=int(86 * dark))
    sh = sh.filter(ImageFilter.GaussianBlur(max(4, h * 0.34)))
    blk = Image.new("RGBA", sh.size, (16, 13, 11, 255))
    blk.putalpha(sh)
    return blk


def draw_puppet(canvas, fig, t, dark):
    breath, head, lean, adv = pose(fig, t)
    im = scaled(fig["c"], fig["h"], fig["dim"], dark)

    # the body leans about its feet; the head slab turns about the neck pins
    if abs(lean) > 0.02:
        im = im.rotate(lean, resample=Image.BICUBIC, center=(im.width / 2, im.height))
    if abs(head) > 0.02:
        hy = int(im.height * NECK)
        add_slab(im, im.crop((0, 0, im.width, hy)), 0, head, hy)

    # breath moves the shoulder slab, not the whole torso
    dy = int(round(breath * 0.9))
    x = fig["x"] * M - im.width / 2 + adv * M * 0.5
    feet = fig["feet"] * M + adv * M * 0.28
    y = feet - im.height + dy

    w = int(im.width * 0.92)
    sh = ground_shadow(w, int(im.height * 0.055), dark)
    canvas.paste(sh, (int(x + im.width * 0.04), int(feet - sh.height * 0.45)), sh)
    canvas.alpha_composite(im, (int(x), int(y)))


def compose(stage, t, dark, u=0.0):
    """Puppets and stage first, then one grade across the whole plate.

    Grading the pieces separately makes the actors look lit from a different room than
    the room they are standing in; one pass over the composite keeps them in the same air.
    """
    bg = background(stage["bg"])
    canvas = bg.convert("RGBA")
    for fig in sorted(stage.get("figs", []), key=lambda f: f["feet"]):
        draw_puppet(canvas, fig, t, 1.0)
    occ = stage.get("occ")
    if occ:
        y = int(occ[0] * M)
        x0 = int(occ[1] * M)
        x1 = int(occ[2] * M)
        canvas.paste(bg.crop((x0, y, x1, MH)), (x0, y))
    return grade(canvas.convert("RGB"), dark)


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


def any_acting(stage):
    return bool(stage.get("figs")) or isinstance(stage.get("dark"), (tuple, list))


# --------------------------------------------------------------------------- textures
class Textures:
    def __init__(self):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dx = (xx - W / 2) / (W / 2)
        dy = (yy - H / 2) / (H / 2)
        r = np.sqrt(dx * dx * 0.78 + dy * dy * 0.72)
        self.vig = np.clip(1.06 - 0.30 * np.power(np.clip(r, 0, 1.7), 2.1),
                           0.38, 1.0)[..., None].astype(np.float32)
        rng = np.random.default_rng(11)
        self.grain = []
        for _ in range(8):
            base = rng.normal(0, 5.2, (H // 4, W // 4))
            im = Image.fromarray(np.clip(base + 128, 0, 255).astype(np.uint8), "L")
            self.grain.append((np.asarray(im.resize((W, H), Image.BILINEAR))
                               .astype(np.float32) - 128)[..., None])
        sp = np.zeros((H, W), np.float32)
        for _ in range(70):
            x, y = rng.integers(0, W), rng.integers(0, H)
            r = int(rng.integers(1, 3))
            sp[max(0, y - r):y + r, max(0, x - r):x + r] = -14
        self.speck = sp[..., None]


def glow(tx, ty, r, colour, strength):
    """A soft pool of lamp light, added in screen space."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - tx) ** 2 + (yy - ty) ** 2) / max(1.0, r)
    f = np.clip(1.0 - d, 0, 1) ** 2 * strength
    lay = np.zeros((H, W, 3), np.float32)
    for i in range(3):
        lay[..., i] = f * colour[i]
    return lay


_ov = {}


def series_mark():
    if "mark" not in _ov:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rectangle((52, 74, 452, 158), fill=(18, 15, 12, 148))
        deva.draw_text(lay, (74, 98), "অন্ধকার পাঠ", 32, 600, CREAM, anchor="lm")
        deva.draw_text(lay, (76, 136), "পর্ব ১১ · দশ প্লেট", 22, 400,
                       (208, 197, 172), anchor="lm")
        _ov["mark"] = lay
    return _ov["mark"]


def end_card():
    if "card" not in _ov:
        tex = np.asarray(Image.fromarray(
            np.clip(np.random.default_rng(5).normal(0, 8, (H // 3, W // 3)) + 128, 0, 255)
            .astype(np.uint8), "L").resize((W, H), Image.BILINEAR)).astype(np.int16)
        a = np.zeros((H, W, 3), np.int16) + np.array(INK, np.int16)
        a = np.clip(a + (tex[..., None] - 128) // 3, 0, 255)
        art = Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")
        d = ImageDraw.Draw(art)
        deva.draw_text(art, (W // 2, 806), "দশ প্লেট", 96, 700, CREAM, anchor="mm")
        d.rectangle((W // 2 - 104, 890, W // 2 + 104, 894), fill=BRICK)
        deva.draw_text(art, (W // 2, 966), "অন্ধকার পাঠ · পর্ব ১১", 44, 600,
                       (206, 194, 168), anchor="mm")
        deva.draw_text(art, (W // 2, 1054), "একটা বাড়তি প্লেট, একটা কম নাম", 36, 500,
                       (228, 217, 192), anchor="mm")
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
        dark = stage_dark(stage, u)
        if any_acting(stage):
            ms = compose(stage, t, dark, u)
        else:
            key = shot["id"]
            if key not in _master:
                _master[key] = compose(stage, 0.0, dark, 0.0)
            ms = _master[key]
            u = min(1.0, u + 0.004 * math.sin(2 * math.pi * f / 82.0))
        x, y, w, h = camera(stage, u)
        im = ms.crop((int(x), int(y), int(x + w), int(y + h))).resize((W, H), Image.BICUBIC)
        out = np.asarray(im.convert("RGB")).astype(np.float32)

        g = stage.get("glow")
        if g:
            out += glow(g[0] * M, g[1] * M, g[2] * M, g[3], g[4])

        for c in plan["cuts"]:
            cf = int(round(c["t"] * plan["fps"]))
            if cf <= f < cf + 2:
                out[..., 0] = np.roll(out[..., 0].copy(), 2, axis=1)
                out[..., 2] = np.roll(out[..., 2].copy(), -2, axis=1)

    out *= tex.vig
    out += tex.grain[f % len(tex.grain)]
    out += tex.speck

    tt = f / plan["fps"]
    if tt < P.MARK_UNTIL:
        a = min(1.0, tt / 1.2) * max(0.0, min(1.0, (P.MARK_UNTIL - tt) / 1.6))
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
