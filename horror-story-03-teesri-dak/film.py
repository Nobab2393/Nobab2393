"""Render ভয়ের গল্প · পর্ব ৩ — তৃতীয় ডাক.

The cast are 2D cutout puppets, so the acting is in the joints, not in the legs. Every
figure is a flat RGBA plate; per frame it is cut into slabs and each slab is turned a
degree or two about its own pin:

    head slab    — y 0 → NECK, turned about the neck pins (a look)
    shoulder slab— NECK → COLLAR, shifted and turned about the collar (a breath, a shrug)
    whole body   — turned about the feet (a lean), or pushed a centimetre forward

Figures walk on a step cycle when a shot asks for it (walk=(x0, x1, t0, t1)); the rest of the
acting is in the neck and the shoulders. The camera does the rest of the travelling.

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
CREAM = (246, 235, 212)
INK = (26, 18, 12)
BRICK = (176, 84, 32)
STEP = 0.46              # seconds per step
NECK = 0.20              # fallback: head slab ends here, as a fraction of the height
_neck = {}               # per plate, the neck is where the silhouette is narrowest

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
    """Horror print: amber in the lamp light, green-black in the corners, hard contrast."""
    a = np.asarray(im).astype(np.float32)
    if dark < 0.999:
        a[..., :3] *= dark
        a[..., 2] *= 0.86 + 0.10 * dark
    a[..., 0] *= 1.06
    a[..., 1] *= 1.005
    a[..., 2] *= 0.90
    # crush the black end and let the lamp stay hot
    a[..., :3] = np.clip((a[..., :3] - 132.0) * 1.18 + 112.0, 0, 255)
    # a cold green breath in the shadows, so the dark is a colour and not just absence
    lum = a[..., :3].mean(axis=2, keepdims=True)
    shadow = np.clip((86.0 - lum) / 86.0, 0, 1)
    a[..., 1] += shadow[..., 0] * 9.0
    a[..., 2] += shadow[..., 0] * 5.0
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


def plate(key):
    """key is "01-rafi.neutral" or "01-rafi.walk"."""
    if key not in _plate:
        cid, pose = key.split(".")
        _plate[key] = Image.open(os.path.join(CAST, "%s-%s.png" % (cid, pose))).convert("RGBA")
    return _plate[key]


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


def neck_of(cid, im):
    """Where the head stops and the neck starts: the narrowest row in the top third.

    Cutting the head slab at a fixed fraction of the height put the seam across the
    cheek of every puppet with a big cutout head; measuring the silhouette puts it at
    the neck, which is where the pin is.
    """
    key = (cid, im.height)
    if key not in _neck:
        a = np.asarray(im)[..., 3] > 40
        h = im.height
        widths = a.sum(axis=1).astype(np.float32)
        lo, hi = int(h * 0.10), int(h * 0.34)
        band = widths[lo:hi]
        y = lo + int(np.argmin(band)) if band.size else int(h * NECK)
        _neck[key] = y
    return _neck[key]


def add_slab(base, ang, cut, pad=10):
    """Turn the head slab about the neck pins, blending back into the body.

    The slab is pasted through a ramp mask rather than onto a cleared rectangle, so
    the join is a gradient instead of a line across the face.
    """
    band = base.crop((0, 0, base.width, cut + pad))
    rot = band.rotate(ang, resample=Image.BICUBIC,
                      center=(band.width / 2.0, cut), expand=False)
    m = Image.new("L", band.size, 255)
    d = ImageDraw.Draw(m)
    for i in range(pad):
        d.line([(0, cut + i), (band.width, cut + i)], fill=int(255 * (1 - (i + 1) / pad)))
    base.paste(rot, (0, 0), m)
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


def walk_at(fig, t):
    """Where a walking figure is, and how far through its step cycle."""
    w = fig.get("walk")
    if not w:
        return fig["x"], 0.0, 0.0
    x0, x1, t0, t1 = w
    if t <= t0:
        return x0, 0.0, 0.0
    if t >= t1:
        return x1, 0.0, 0.0
    u = (t - t0) / max(1e-6, (t1 - t0))
    return x0 + (x1 - x0) * ease(u), min(1.0, u), 1.0


def pose(fig, t):
    breath, sway, micro = idle(fig, t)
    x, u, moving = walk_at(fig, t)
    head = act_value(fig, "look", t) + micro * (1.0 - moving)
    lean = act_value(fig, "lean", t) + sway * (1.0 - moving)
    adv = act_value(fig, "advance", t) + act_value(fig, "reach", t) * 10
    if moving:
        ph = 2 * math.pi * (u * (fig.get("walk")[3] - fig.get("walk")[2]) / STEP)
        lean += 1.1 * math.sin(ph)
        breath += 1.6 * math.sin(ph * 2)
    return breath, head, lean, adv


# --------------------------------------------------------------------------- figures
def ground_shadow(w, h, dark):
    sh = Image.new("L", (max(6, w), max(6, h)), 0)
    ImageDraw.Draw(sh).ellipse((2, 2, sh.width - 3, sh.height - 3), fill=int(120 * dark))
    sh = sh.filter(ImageFilter.GaussianBlur(max(2, h * 0.14)))
    blk = Image.new("RGBA", sh.size, (16, 13, 11, 255))
    blk.putalpha(sh)
    return blk


def draw_puppet(canvas, fig, t, dark):
    breath, head, lean, adv = pose(fig, t)
    x, u, moving = walk_at(fig, t)
    pose_name = "walk" if (moving and os.path.exists(
        os.path.join(CAST, fig["c"] + "-walk.png"))) else "neutral"
    im = scaled(fig["c"] + "." + pose_name, fig["h"], fig["dim"], dark)

    # the body leans about its feet; the head slab turns about the neck pins
    if abs(lean) > 0.02:
        im = im.rotate(lean, resample=Image.BICUBIC, center=(im.width / 2, im.height))
    if abs(head) > 0.02:
        add_slab(im, head, neck_of(fig["c"], im))

    # breath moves the shoulder slab, not the whole torso
    dy = int(round(breath * 0.9))
    x = x * M - im.width / 2 + adv * M * 0.5
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
        self.vig = np.clip(1.06 - 0.22 * np.power(np.clip(r, 0, 1.7), 2.1),
                           0.38, 1.0)[..., None].astype(np.float32)
        rng = np.random.default_rng(11)
        self.grain = []
        for _ in range(8):
            base = rng.normal(0, 3.2, (H // 4, W // 4))
            im = Image.fromarray(np.clip(base + 128, 0, 255).astype(np.uint8), "L")
            self.grain.append((np.asarray(im.resize((W, H), Image.BILINEAR))
                               .astype(np.float32) - 128)[..., None])
        sp = np.zeros((H, W), np.float32)
        for _ in range(34):
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
        d.rectangle((52, 74, 470, 158), fill=(24, 16, 10, 156))
        deva.draw_text(lay, (74, 98), "ভয়ের গল্প", 32, 600, CREAM, anchor="lm")
        deva.draw_text(lay, (76, 136), "পর্ব ৩ · তৃতীয় ডাক", 22, 400,
                       (236, 206, 160), anchor="lm")
        _ov["mark"] = lay
    return _ov["mark"]


def end_card():
    if "card" not in _ov:
        tex = np.asarray(Image.fromarray(
            np.clip(np.random.default_rng(5).normal(0, 8, (H // 3, W // 3)) + 128, 0, 255)
            .astype(np.uint8), "L").resize((W, H), Image.BILINEAR)).astype(np.int16)
        a = np.zeros((H, W, 3), np.int16) + np.array([238, 226, 199], np.int16)
        a = np.clip(a + (tex[..., None] - 128) // 3, 0, 255)
        art = Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")
        d = ImageDraw.Draw(art)
        # a printed card: hairline frame, heavy title, one orange rule
        d.rectangle((56, 56, W - 56, H - 56), outline=INK + (255,), width=4)
        deva.draw_text(art, (W // 2, 792), "আপনার নাম কী?", 92, 700, INK, anchor="mm")
        d.rectangle((W // 2 - 116, 882, W // 2 + 116, 890), fill=BRICK)
        deva.draw_text(art, (W // 2, 956), "ভয়ের গল্প · পর্ব ৩ · তৃতীয় ডাক", 38, 600,
                       (112, 74, 44), anchor="mm")
        deva.draw_text(art, (W // 2, 1050), "তিনবার ডাকলে…", 32, 500,
                       (74, 56, 40), anchor="mm")
        deva.draw_text(art, (W // 2, 1100), "তৃতীয়বার সাড়া দিলে?", 30, 500,
                       (74, 56, 40), anchor="mm")
        _ov["card"] = art
    return _ov["card"]



# --------------------------------------------------------------------------- the phone
SKIN = (214, 196, 168)
DIM = (146, 148, 152)
COLD = (122, 176, 214)
GREEN = (86, 150, 96)
RED = (152, 58, 52)


def handset(d, cx, cy, r, colour):
    """A little classic receiver, drawn as a thick arc with two lugs."""
    d.arc((cx - r, cy - r, cx + r, cy + r), 200, 340, fill=colour, width=14)
    d.ellipse((cx - r - 12, cy + r * 0.42, cx - r + 16, cy + r * 0.86), fill=colour)
    d.ellipse((cx + r - 16, cy + r * 0.42, cx + r + 12, cy + r * 0.86), fill=colour)


def phone_layer(state):
    """One of three stills of a locked phone screen: ringing, ringing with his own name, ended."""
    if state in _ov:
        return _ov[state]
    lay = Image.new("RGBA", (W, H), (11, 13, 18, 255))
    d = ImageDraw.Draw(lay)
    deva.draw_text(lay, (W // 2, 186), "ভোর ৩:০৭", 34, 500, DIM, anchor="mm")
    for i in range(4):
        hh = 12 + i * 9
        d.rectangle((W - 132 + i * 20, 200 - hh, W - 116 + i * 20, 200),
                    fill=DIM if i < 3 else (66, 68, 74))
    d.rectangle((W // 2 - 190, 320, W // 2 + 190, 326), fill=(48, 52, 60))

    if state == "ended":
        deva.draw_text(lay, (W // 2, 860), "কল শেষ", 76, 600, (150, 152, 158), anchor="mm")
        deva.draw_text(lay, (W // 2, 946), "মিসড কল · মা", 44, 500, (108, 112, 120), anchor="mm")
        deva.draw_text(lay, (W // 2, 1052), "০১:১২", 36, 400, (86, 90, 98), anchor="mm")
    else:
        name = "মা" if state == "mother" else "রাফি"
        sub = "মোবাইল" if state == "mother" else "আপনি"
        deva.draw_text(lay, (W // 2, 640), "কল আসছে…", 40, 500, DIM, anchor="mm")
        d.ellipse((W // 2 - 84, 690, W // 2 + 84, 858), outline=(70, 76, 86), width=4)
        # no photograph, only a silhouette: the contact has no face
        d.ellipse((W // 2 - 26, 724, W // 2 + 26, 776), fill=(78, 84, 94))
        d.pieslice((W // 2 - 54, 778, W // 2 + 54, 878), 190, 350, fill=(78, 84, 94))
        deva.draw_text(lay, (W // 2, 950), name, 112, 700, (238, 230, 212), anchor="mm")
        deva.draw_text(lay, (W // 2, 1036), sub, 44, 500, DIM, anchor="mm")
        d.ellipse((W // 2 - 330, 1500, W // 2 - 158, 1672), fill=RED)
        d.ellipse((W // 2 + 158, 1500, W // 2 + 330, 1672), fill=GREEN)
        handset(d, W // 2 - 244, 1616, 34, (246, 240, 232))
        d.arc((W // 2 + 190, 1572, W // 2 + 298, 1668), 300, 240, fill=(246, 240, 232), width=14)
        deva.draw_text(lay, (W // 2 - 244, 1720), "কেটে দিন", 30, 400, DIM, anchor="mm")
        deva.draw_text(lay, (W // 2 + 244, 1720), "ধরুন", 30, 400, DIM, anchor="mm")
    d.rectangle((46, 1810, W - 46, 1816), fill=(40, 44, 52))
    _ov[state] = lay
    return lay


def phone_frame(shot_id, t):
    """s10b rings; s10c rings, cuts out, rings again — and then the name is his own."""
    if shot_id == "s10b":
        state = "mother"
        if 3.45 <= t < 4.55:
            state = "ended"
    else:
        state = "mother"
        if t >= 1.02 and t < 1.34:
            state = "ended"
        elif t >= 1.34 and t < 2.52:
            state = "mother"
        elif t >= 2.52:
            state = "rafi"
    lay = phone_layer(state)
    out = np.asarray(lay.convert("RGB")).astype(np.float32)
    ring = 0.5 + 0.5 * math.sin(2 * math.pi * 0.85 * t)
    out += glow(W * 0.5, 900, 620, COLD, 0.16 + 0.10 * ring)
    if state == "rafi":
        out += glow(W * 0.5, 950, 700, (196, 120, 96), 0.10 + 0.05 * ring)
    return out



def call_layer(timer):
    """The other end of a call that should not exist: connected, and counting."""
    key = "call_%s" % timer
    if key in _ov:
        return _ov[key]
    lay = Image.new("RGBA", (W, H), (10, 12, 16, 255))
    d = ImageDraw.Draw(lay)
    deva.draw_text(lay, (W // 2, 186), "ভোর ৩:১১", 34, 500, DIM, anchor="mm")
    for i in range(4):
        hh = 12 + i * 9
        d.rectangle((W - 132 + i * 20, 200 - hh, W - 116 + i * 20, 200),
                    fill=DIM if i < 2 else (66, 68, 74))
    d.rectangle((W // 2 - 190, 320, W // 2 + 190, 326), fill=(48, 52, 60))
    d.ellipse((W // 2 - 96, 596, W // 2 + 96, 788), outline=(70, 76, 86), width=4)
    d.ellipse((W // 2 - 30, 634, W // 2 + 30, 694), fill=(78, 84, 94))
    d.pieslice((W // 2 - 62, 698, W // 2 + 62, 812), 190, 350, fill=(78, 84, 94))
    deva.draw_text(lay, (W // 2, 880), "মা", 112, 700, (238, 230, 212), anchor="mm")
    deva.draw_text(lay, (W // 2, 966), "সংযুক্ত", 40, 500, DIM, anchor="mm")
    deva.draw_text(lay, (W // 2, 1036), timer, 44, 600, (206, 198, 182), anchor="mm")
    d.ellipse((W // 2 - 86, 1560, W // 2 + 86, 1732), fill=RED)
    d.arc((W // 2 - 40, 1600, W // 2 + 40, 1668), 200, 340, fill=(246, 240, 232), width=14)
    deva.draw_text(lay, (W // 2, 1782), "কেটে দিন", 30, 400, DIM, anchor="mm")
    d.rectangle((46, 1858, W - 46, 1864), fill=(40, 44, 52))
    _ov[key] = lay
    return lay


def call_frame(t, frame_index):
    """A connected call: a live timer, and a band of line noise that never settles."""
    secs = int(max(0, t))
    timer = "%02d:%02d" % (secs // 60, secs % 60)
    lay = call_layer(timer)
    out = np.asarray(lay.convert("RGB")).astype(np.float32)
    rng = np.random.default_rng(frame_index // 2)
    bars = 46
    for i in range(bars):
        x = 96 + i * (W - 192) // bars
        hh = int(abs(rng.normal(0, 1)) * 26) + 3
        y = 1220 - hh
        out[y:1220, x:x + 8, :] = np.array([150, 168, 180], np.float32)
    out += glow(W * 0.5, 900, 620, COLD, 0.14 + 0.03 * math.sin(2 * math.pi * 0.4 * t))
    return out


# --------------------------------------------------------------------------- frames
def render_frame(plan, shot, f, tex):
    total = plan["frames"]
    if shot.get("stage", {}).get("bg") == "call-ui":
        out = call_frame((f - shot["f0"]) / plan["fps"], f)
    elif shot.get("stage", {}).get("bg") == "black":
        out = np.zeros((H, W, 3), np.float32)
    elif shot["id"] in ("s10b", "s10c"):
        n = max(1, shot["f1"] - shot["f0"])
        u = (f - shot["f0"]) / n
        out = phone_frame(shot["id"], (f - shot["f0"]) / plan["fps"])
        for c in plan["cuts"]:
            cf = int(round(c["t"] * plan["fps"]))
            if cf <= f < cf + 2:
                out[..., 0] = np.roll(out[..., 0].copy(), 2, axis=1)
                out[..., 2] = np.roll(out[..., 2].copy(), -2, axis=1)
    elif shot["id"] == "card":
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

        lt = stage.get("light")
        if lt:
            # daylight under the shutter: a hard-edged pool that grows as it lifts
            y0 = lt[0] + (lt[1] - lt[0]) * ease(u)
            py = int(round(y0 * H))
            out[py:, :, :] = np.array([250, 246, 232], np.float32)
            out[max(0, py - 10):py, :, :] = (out[max(0, py - 10):py, :, :] * 0.4
                                             + np.array([232, 224, 200], np.float32) * 0.6)

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
