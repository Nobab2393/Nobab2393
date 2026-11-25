"""stage.py — a 2D daylight stage for stick figures.

Everything lives in metres: y = 0 is the ground, up is negative y, the sun is up-right.
A camera is (centre_x, centre_y, zoom) plus shake, and maps world -> screen. Figures are a
small angle-driven skeleton (hip, spine, head, two arms, two legs) drawn as thick round lines,
so a pose is just a dict of numbers and every animation is a mix of two poses.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
SS = 1.5                      # supersampling factor: draw big, sample down
LW = 0.046                    # default limb thickness in metres


# ------------------------------------------------------------------ easing / mixing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def eout(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ein(t):
    t = clamp(t)
    return t ** 3


def seg(t0, t1, t):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def kf(t, frames, fn=ease):
    """Keyframes [(t, value), ...] -> interpolated value."""
    if t <= frames[0][0]:
        return frames[0][1]
    if t >= frames[-1][0]:
        return frames[-1][1]
    for (t0, v0), (t1, v1) in zip(frames, frames[1:]):
        if t0 <= t <= t1:
            w = fn(seg(t0, t1, t))
            return v0 + (v1 - v0) * w if isinstance(v0, (int, float)) else v1
    return frames[-1][1]


# ------------------------------------------------------------------ ink layer
# PIL's "RGBA" draw mode *replaces* the alpha of every pixel it touches, so drawing a
# semi-transparent shadow straight onto the frame punches a hole that turns black when the
# frame is flattened. Every translucent mark therefore goes onto one accumulating layer that is
# composited once, in order, at the end of the frame.
_INK = None
_UI = None


def ink(size):
    global _INK
    if _INK is None or _INK.size != size:
        _INK = Image.new("RGBA", size, (0, 0, 0, 0))
    return _INK


def ink_reset():
    if _INK is not None:
        _INK.paste((0, 0, 0, 0), (0, 0, _INK.size[0], _INK.size[1]))


def ui(size):
    """Type and cards live above the ink layer, so nothing drawn later can cover them."""
    global _UI
    if _UI is None or _UI.size != size:
        _UI = Image.new("RGBA", size, (0, 0, 0, 0))
    return _UI


def ui_reset():
    if _UI is not None:
        _UI.paste((0, 0, 0, 0), (0, 0, _UI.size[0], _UI.size[1]))


def draw_on(img):
    return ImageDraw.Draw(ink(img.size), "RGBA")


def flush(img):
    if _INK is not None:
        img.alpha_composite(_INK)
    if _UI is not None:
        img.alpha_composite(_UI)


# ------------------------------------------------------------------ camera
class Cam:
    def __init__(self, cx=0.0, cy=-1.0, zoom=380.0, shake=(0.0, 0.0)):
        self.cx, self.cy, self.zoom = cx, cy, zoom
        self.sx, self.sy = shake

    def p(self, x, y):
        return (W * SS / 2 + (x - self.cx + self.sx) * self.zoom,
                H * SS / 2 + (y - self.cy + self.sy) * self.zoom)

    def z(self, v):
        return v * self.zoom


# ------------------------------------------------------------------ sky / ground
def _vgrad(top, bot, h, w):
    ys = np.linspace(0, 1, h)[:, None]
    arr = (np.array(top, float) * (1 - ys) + np.array(bot, float) * ys)
    arr = np.repeat(arr[:, None, :], w, axis=1)
    return arr


def cam_for(zoom, cx=0.0, ground=0.655):
    """Camera whose horizon sits at `ground` of the frame height; zoom is SS px per metre."""
    return Cam(cx, -(ground - 0.5) * H * SS / zoom, zoom)


def sky(cam, top=(150, 196, 232), bot=(240, 244, 244)):
    """Daylight sky with a warm haze near the horizon."""
    h, w = H * SS // 1, W * SS // 1
    h, w = int(h), int(w)
    img = np.zeros((h, w, 3), np.float32)
    img[:] = _vgrad(top, bot, h, w)
    # horizon haze sits where the ground line is on screen
    _, gy = cam.p(0, 0)
    gy = clamp(gy, 0, h)
    if gy > 2:
        band = np.linspace(0, 1, int(h))[:, None]
        haze = np.exp(-((band - gy / h) ** 2) / 0.012) * 0.55
        warm = np.array((252, 238, 214), np.float32)
        img = img * (1 - haze[..., None]) + warm * haze[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def sun(img, cam, x=2.6, y=-3.1, r=0.42, warm=1.0):
    """A soft daylight sun: many cheap low-alpha rings instead of three hard bands."""
    d = draw_on(img)
    sx, sy = cam.p(x, y)
    R = cam.z(r)
    col = (int(255), int(244 - 34 * (1 - warm)), int(214 - 58 * (1 - warm)))
    for i in range(18, 0, -1):
        k = 1 + i * 0.26
        a = int(5 + 3 * (1 - i / 18))
        d.ellipse([sx - R * k, sy - R * k, sx + R * k, sy + R * k], fill=col + (a,))
        if i % 2 == 0:
            col = (min(255, col[0] + 0), min(255, col[1] + 1), min(255, col[2] + 2))
    d.ellipse([sx - R, sy - R, sx + R, sy + R], fill=col + (232,))
    d.ellipse([sx - R * 0.82, sy - R * 0.82, sx + R * 0.82, sy + R * 0.82], fill=(255, 250, 235, 90))


_GLOW = {}


def _glow_tile(n=360, power=2.6):
    key = (n, power)
    if key in _GLOW:
        return _GLOW[key]
    y, x = np.mgrid[0:n, 0:n]
    c = (n - 1) / 2
    d = np.sqrt(((x - c) / c) ** 2 + ((y - c) / c) ** 2)
    a = np.clip(1 - d, 0, 1) ** power
    arr = np.zeros((n, n, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = 255, 246, 226
    arr[..., 3] = (a * 190).astype(np.uint8)
    tile = Image.fromarray(arr, "RGBA")
    _GLOW[key] = tile
    return tile


def sun_screen(img, fx=0.76, fy=0.14, r=0.075, warm=1.0):
    """The sun lives in frame space: it must read in the same corner whatever the camera does."""
    d = draw_on(img)
    sx, sy = W * SS * fx, H * SS * fy
    R = W * SS * r
    col = (255, int(246 - 26 * (1 - warm)), int(226 - 44 * (1 - warm)))
    # a real radial falloff: one scaled gradient tile instead of stacked circles (no banding)
    tile = _glow_tile()
    big = int(R * 9)
    glow = tile.resize((big, big), Image.BILINEAR)
    ink(img.size).alpha_composite(glow, (int(sx - big / 2), int(sy - big / 2)))
    d.ellipse([sx - R, sy - R, sx + R, sy + R], fill=col + (244,))
    d.ellipse([sx - R * 0.6, sy - R * 0.6, sx + R * 0.6, sy + R * 0.6],
              fill=(255, 251, 238, 252))


def ground(img, cam, col=(222, 208, 184), line=(88, 92, 100), alpha=255):
    """Dusty ground plane: warm, lighter at the horizon, with sparse stones and tufts."""
    d = draw_on(img)
    _, gy = cam.p(0, 0)
    h = H * SS
    steps = 26
    for i in range(steps):
        y0 = gy + (h - gy) * i / steps
        y1 = gy + (h - gy) * (i + 1) / steps + 1
        k = i / steps
        c = (int(col[0] - 34 * k), int(col[1] - 32 * k), int(col[2] - 34 * k))
        d.rectangle([0, y0, W * SS, y1], fill=c + (alpha,))
    d.rectangle([0, gy, W * SS, gy + cam.z(0.10)], fill=(196, 190, 158, 90))
    d.line([(0, gy), (W * SS, gy)], fill=line + (110,), width=max(2, int(2.2 * SS)))
    rng = np.random.default_rng(4)
    for _ in range(26):
        wx = float(rng.uniform(-6, 6))
        depth = float(rng.uniform(0.05, 2.4))
        x, y = cam.p(wx, depth)
        rr = cam.z(0.006 + 0.004 * depth) * float(rng.uniform(0.7, 1.6))
        d.ellipse([x - rr, y - rr * 0.6, x + rr, y + rr * 0.6], fill=(150, 140, 122, 34))
    for _ in range(11):
        wx = float(rng.uniform(-5, 5))
        depth = float(rng.uniform(0.25, 2.2))
        x, y = cam.p(wx, depth)
        hh = cam.z(0.05 + 0.05 * depth) * float(rng.uniform(0.7, 1.4))
        for k in (-1, 0, 1):
            d.line([(x, y), (x + k * hh * 0.35, y - hh)], fill=(132, 142, 112, 34), width=max(1, int(1.6 * SS)))


def skyline(img, cam, seed=0, col=(158, 176, 194), alpha=58, base=-0.01):
    """A pale far treeline sitting on the horizon — depth without stealing the read."""
    rng = np.random.default_rng(seed)
    d = draw_on(img)
    x = -13.0
    while x < 13.0:
        w = float(rng.uniform(0.35, 1.1))
        hgt = float(rng.uniform(0.06, 0.30))
        if rng.random() < 0.55:                     # tree: a soft rounded lump
            cx = cam.p(x + w / 2, base - hgt * 0.45)
            rx, ry = cam.z(w * 0.55), cam.z(hgt * 0.85)
            d.ellipse([cx[0] - rx, cx[1] - ry, cx[0] + rx, cx[1] + ry], fill=col + (alpha,))
        else:                                        # low block / roof
            pts = [cam.p(x, base), cam.p(x + w, base), cam.p(x + w, base - hgt), cam.p(x, base - hgt)]
            d.polygon(pts, fill=col + (alpha,))
        x += w + float(rng.uniform(0.05, 0.45))


# ------------------------------------------------------------------ stick figure
BASE = dict(lean=0.0, hipdy=0.0, head=0.0, rot=0.0,
            l1=-7.0, l2=5.0, r1=7.0, r2=-5.0,
            a1=-12.0, a2=8.0, b1=12.0, b2=-8.0)


def pose(**kw):
    p = dict(BASE)
    p.update(kw)
    return p


def mix(pa, pb, w):
    w = clamp(w)
    return {k: pa[k] + (pb[k] - pa[k]) * w for k in BASE}


def seq(t, steps):
    """steps = [(time, pose), ...] — hold the last one past its time, ease between."""
    if t <= steps[0][0]:
        return steps[0][1]
    for (t0, p0), (t1, p1) in zip(steps, steps[1:]):
        if t0 <= t <= t1:
            return mix(p0, p1, ease(seg(t0, t1, t)))
    return steps[-1][1]


def _pt(x, y, a, length):
    r = math.radians(a)
    return x + math.sin(r) * length, y + math.cos(r) * length


def skeleton(fig, p):
    """Return the joint positions in world space for a figure + pose."""
    s = fig.get("scale", 1.0)
    face = fig.get("face", 1)
    x, y = fig["x"], fig["y"]
    hip = (x, y - 0.90 * s + p["hipdy"] * s)
    rot = math.radians(p["rot"] * face)

    def rotp(px, py, ox, oy):
        dx, dy = px - ox, py - oy
        c, sn = math.cos(rot), math.sin(rot)
        return ox + dx * c - dy * sn, oy + dx * sn + dy * c

    lean = math.radians(p["lean"] * face)
    chest = (hip[0] + math.sin(lean) * 0.56 * s, hip[1] - math.cos(lean) * 0.56 * s)
    neck = (chest[0] + math.sin(lean) * 0.10 * s, chest[1] - math.cos(lean) * 0.10 * s)
    headang = lean + math.radians(p["head"] * face)
    head = (neck[0] + math.sin(headang) * 0.205 * s, neck[1] - math.cos(headang) * 0.163 * s)

    def arm(a1, a2, shoulder):
        ex, ey = _pt(shoulder[0], shoulder[1], a1 * face, 0.30 * s)
        hx, hy = _pt(ex, ey, (a1 + a2) * face, 0.28 * s)
        return (ex, ey), (hx, hy)

    def leg(a1, a2, base):
        kx, ky = _pt(base[0], base[1], a1 * face, 0.46 * s)
        fx, fy = _pt(kx, ky, (a1 + a2) * face, 0.46 * s)
        return (kx, ky), (fx, fy)

    sh_l = (chest[0] - 0.055 * face * s, chest[1])
    sh_r = (chest[0] + 0.055 * face * s, chest[1])
    el_l, hd_l = arm(p["a1"], p["a2"], sh_l)
    el_r, hd_r = arm(p["b1"], p["b2"], sh_r)
    kn_l, ft_l = leg(p["l1"], p["l2"], (hip[0] - 0.05 * face * s, hip[1]))
    kn_r, ft_r = leg(p["r1"], p["r2"], (hip[0] + 0.05 * face * s, hip[1]))

    J = dict(hip=hip, chest=chest, neck=neck, head=head, sh_l=sh_l, sh_r=sh_r,
             el_l=el_l, hd_l=hd_l, el_r=el_r, hd_r=hd_r,
             kn_l=kn_l, ft_l=ft_l, kn_r=kn_r, ft_r=ft_r)
    if abs(p["rot"]) > 1e-3:
        J = {k: rotp(v[0], v[1], hip[0], hip[1]) for k, v in J.items()}
    J["scale"] = s
    return J


def shadow(img, cam, J):
    d = draw_on(img)
    for key in ("ft_l", "ft_r"):
        x, y = J[key]
        cx, cy = cam.p(x + 0.05, 0.01)
        rx, ry = cam.z(0.26), cam.z(0.048)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(84, 78, 66, 64))
    hipx, hipy = J["hip"]
    cx, cy = cam.p(hipx - 0.18, 0.02)
    rx, ry = cam.z(0.54), cam.z(0.070)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(84, 78, 66, 30))


def draw_fig(img, cam, fig, p):
    J = skeleton(fig, p)
    d = draw_on(img)
    col = fig.get("col", (18, 20, 26))
    w = fig.get("w", LW) * cam.zoom
    r = max(2.0, w * 0.50)
    s = J["scale"]

    def L(a, b, width=None):
        ww = width if width else w
        d.line([cam.p(*a), cam.p(*b)], fill=col, width=int(max(2, ww)))
        for q in (a, b):
            cx, cy = cam.p(*q)
            d.ellipse([cx - ww / 2, cy - ww / 2, cx + ww / 2, cy + ww / 2], fill=col)

    # legs, torso, arms, head — back to front
    L(J["hip"], J["kn_l"]); L(J["kn_l"], J["ft_l"])
    L(J["hip"], J["kn_r"]); L(J["kn_r"], J["ft_r"])
    for key, fk in (("ft_l", "kn_l"), ("ft_r", "kn_r")):
        fx, fy = J[key]
        kx, ky = J[fk]
        ang = math.atan2(fx - kx, fy - ky)
        L((fx, fy), (fx + math.sin(ang) * 0.16 * s, fy + math.cos(ang) * 0.06 * s), w * 0.9)
    L(J["hip"], J["chest"], w * 1.06)
    L(J["chest"], J["neck"], w * 1.02)
    L(J["sh_l"], J["el_l"]); L(J["el_l"], J["hd_l"])
    L(J["sh_r"], J["el_r"]); L(J["el_r"], J["hd_r"])
    for h in ("hd_l", "hd_r"):
        cx, cy = cam.p(*J[h])
        rr = cam.z(0.068 * s)
        d.ellipse([cx - rr, cy - rr * 1.1, cx + rr, cy + rr * 1.1], fill=col)
    cx, cy = cam.p(*J["head"])
    rr = cam.z(0.140 * s)
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=col, width=int(max(2, w * 0.92)))
    return J


def dust(img, cam, x, y, r, a=70, n=6, seed=0):
    """Small, soft, numerous puffs — a cloud is a fog blob, dust is particles."""
    rng = np.random.default_rng(seed)
    d = draw_on(img)
    for i in range(n * 3):
        ang = rng.uniform(0, math.tau)
        rr = cam.z(r * rng.uniform(0.10, 0.30))
        cx, cy = cam.p(x + math.cos(ang) * r * rng.uniform(0.1, 0.9),
                       y - abs(math.sin(ang)) * r * rng.uniform(0.0, 0.45))
        d.ellipse([cx - rr, cy - rr * 0.8, cx + rr, cy + rr * 0.8],
                  fill=(206, 194, 168, int(a * rng.uniform(0.35, 0.85) * 0.55)))


def speedlines(img, cam, x, y, ang, length, a=120, n=3):
    d = draw_on(img)
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(n):
        off = (i - (n - 1) / 2) * 0.10
        x0, y0 = x + ca * length * 0.35 - sa * off, y + sa * length * 0.35 + ca * off
        x1, y1 = x0 + ca * length, y0 + sa * length
        d.line([cam.p(x0, y0), cam.p(x1, y1)], fill=(60, 66, 74, a), width=int(max(2, 0.014 * cam.zoom)))


def arc(img, cam, x, y, r, a0, a1, col=(40, 46, 54, 190), w=0.016):
    d = draw_on(img)
    box = [cam.p(x - r, y - r), cam.p(x + r, y + r)]
    d.arc([box[0][0], box[0][1], box[1][0], box[1][1]], a0, a1, fill=col,
          width=int(max(2, w * cam.zoom)))


def grade(img, tint=(255, 250, 240), amount=0.10, vignette=0.22):
    flush(img)
    arr = np.asarray(img.convert("RGB"), np.float32)
    t = np.array(tint, np.float32)
    arr = arr * (1 - amount) + t * amount
    if vignette > 0:
        h, w, _ = arr.shape
        yy = np.linspace(-1, 1, h)[:, None]
        xx = np.linspace(-1, 1, w)[None, :]
        v = 1 - vignette * np.clip((xx ** 2 * 0.8 + yy ** 2 * 0.7), 0, 1.4)
        arr = arr * v[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def vignette_soft(img, a=26):
    d = draw_on(img)
    for i in range(5):
        k = i / 4
        d.rectangle([k * 40 - 20, k * 70 - 35, W * SS - k * 40 + 20, H * SS - k * 70 + 35],
                    outline=(20, 22, 26, int(a * (1 - k))), width=int(30 * SS))


def down(img):
    return img.convert("RGB").resize((W, H), Image.LANCZOS)
