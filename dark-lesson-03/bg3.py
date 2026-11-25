"""bg3 — the field at noon: four layers, one measured light, shadows that are drawn where they fall.

This is the design-lab doctrine applied to a film background:
  L1 sky + sun + far ridge   ~8% contrast, coolest, no interior line
  L2 treeline + fence        ~20%
  L3 ground, path, stones    ~35%  (all placed in world space and projected, so perspective is real)
  L4 branch + grass, blurred ~70%  (near plane: frames the shot, never the subject)
and every cast shadow is a projected ground polygon, not a sticker under the feet.

World: +X right, +Y up, +Z toward the camera. Ground plane y = 0.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920

# ---- palette: a hard noon. Values are 0-255, chosen as a value ladder, not as "nice colours".
SKY_TOP = (86, 141, 205)
SKY_MID = (146, 187, 226)
SKY_BOT = (216, 229, 235)
HAZE = (246, 240, 224)
FAR = (176, 197, 210)
FAR2 = (156, 179, 196)
TREE = (120, 142, 118)
TREE2 = (101, 124, 104)
TRUNK = (96, 84, 70)
G_FAR = (198, 192, 170)
G_MID = (186, 173, 143)
G_NEAR = (166, 148, 118)
PATH = (218, 201, 170)
PATH_EDGE = (150, 132, 104)
GRASS = (128, 136, 96)
INK_FG = (44, 48, 40)

# sun direction, pointing from the ground toward the sun: high, right, slightly in front
SUN_DIR = np.array([0.46, 0.80, 0.38])
SUN_DIR = SUN_DIR / np.linalg.norm(SUN_DIR)
# horizon direction of a shadow (opposite the sun, flattened): left and slightly away
SHADOW_DIR = np.array([-0.86, -0.51])
SHADOW_DIR = SHADOW_DIR / np.linalg.norm(SHADOW_DIR)


# ---------------------------------------------------------------- small helpers
def _rng(seed):
    x = seed

    def nxt():
        nonlocal x
        x = (x * 1103515245 + 12345) % 2147483648
        return x / 2147483648.0
    return nxt


def _soft(img, draw_fn, blur, k=4):
    """Draw at 1/k resolution, blur, upscale — a big blur costs 1/16 as much."""
    lay = Image.new("RGBA", (max(1, W // k), max(1, H // k)), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay), 1.0 / k)
    lay = lay.filter(ImageFilter.GaussianBlur(max(0.5, blur / k))).resize((W, H), Image.BILINEAR)
    img.alpha_composite(lay)


def _glow(img, cx, cy, rx, ry, col, a, power=2.4):
    n = 220
    y, x = np.mgrid[0:n, 0:n]
    c = (n - 1) / 2.0
    d = np.sqrt(((x - c) / c) ** 2 + ((y - c) / c) ** 2)
    al = np.clip(1 - d, 0, 1) ** power
    arr = np.zeros((n, n, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = col
    arr[..., 3] = (al * a).astype(np.uint8)
    tile = Image.fromarray(arr, "RGBA").resize((int(rx * 2), int(ry * 2)), Image.BILINEAR)
    img.alpha_composite(tile, (int(cx - rx), int(cy - ry)))


def horizon(cam):
    """Screen row of the horizon for this camera: where a ground ray parallel to y=0 lands."""
    p = cam.project(cam.to_view(np.array([0.0, cam.eye[1], -1.0e5])))[0]
    return float(p[1])


def proj(cam, x, y, z):
    p = cam.project(cam.to_view(np.array([float(x), float(y), float(z)])))[0]
    return (float(p[0]), float(p[1]))


def scale_at(cam, z):
    """Pixels per metre on the ground plane at depth z."""
    v = cam.to_view(np.array([0.0, 0.0, z]))
    depth = max(0.2, -float(v[2]))
    return cam.f / depth


# ---------------------------------------------------------------- L1 sky
def sky(img, cam, sun=(0.70, 0.10), flare=0.5):
    y0 = int(max(0, min(H, horizon(cam))))
    hh = max(8, y0)
    ys = np.linspace(0, 1, hh)[:, None]
    k1 = np.clip(ys / 0.62, 0, 1)
    k2 = np.clip((ys - 0.62) / 0.38, 0, 1)
    top = np.array(SKY_TOP, float)
    mid = np.array(SKY_MID, float)
    bot = np.array(SKY_BOT, float)
    arr = (top * (1 - k1) + mid * k1) * (1 - k2) + (mid * (1 - k2) + bot * k2) * k2
    arr = np.repeat(arr[:, None, :], W, axis=1).astype(np.uint8)
    img.paste(Image.fromarray(arr, "RGB"), (0, 0))
    # haze band sitting on the horizon — distance reads as air
    _glow(img, W * 0.5, y0, W * 0.85, max(40, y0 * 0.18), HAZE, 120, 2.0)
    # the sun: one gradient tile plus a disc; stacked alpha circles would band
    sx, sy = W * sun[0], y0 * sun[1]
    _glow(img, sx, sy, 420, 420, (255, 246, 218), int(90 + 60 * flare), 2.8)
    d = ImageDraw.Draw(img)
    d.ellipse([sx - 46, sy - 46, sx + 46, sy + 46], fill=(255, 252, 240, 252))


def far_ridge(img, cam, seed=5, drift=0.0):
    """L1: a ridge at ~8% contrast, no interior line, base dissolved by haze."""
    y0 = horizon(cam)
    d = ImageDraw.Draw(img, "RGBA")
    r = _rng(seed)
    for depth, (col, a, amp) in enumerate(((FAR, 130, 0.055), (FAR2, 105, 0.032))):
        pts = [(-40 + drift * 8, y0 + 60)]
        x = -40 + drift * 8
        while x < W + 60:
            x += 90 + 140 * r()
            pts.append((x, y0 - H * amp * (0.4 + 0.6 * r()) + depth * 6))
        pts += [(W + 60, y0 + 60)]
        d.polygon(pts, fill=col + (a,))
    _glow(img, W * 0.5, y0, W * 0.9, max(30, H * 0.045), HAZE, 70, 1.8)


# ---------------------------------------------------------------- L2 treeline
def treeline(img, cam, spots, drift=0.0):
    """L2: a continuous crown band on the horizon (that is what a distant treeline is), plus a
    few planted things at the field edge for scale. Nothing busy near the action."""
    y0 = horizon(cam)
    d = ImageDraw.Draw(img, "RGBA")
    r = _rng(7)
    x = -70
    while x < W + 70:
        w = 34 + 70 * r()
        h = 14 + 40 * r()
        col = TREE if r() < 0.55 else TREE2
        d.ellipse([x, y0 - h, x + w, y0 + 10], fill=col + (165,))
        x += w * 0.58
    # a second, lighter row behind: overlap is depth
    x = -50
    while x < W + 60:
        w = 44 + 80 * r()
        h = 10 + 26 * r()
        d.ellipse([x, y0 - h - 12, x + w, y0 + 6], fill=TREE2 + (90,))
        x += w * 0.7
    # planted scale references: bushes at the edge of the field
    for (wx, wz, hgt, kind, seed) in spots:
        bx, _ = proj(cam, wx - drift * 0.02, 0.0, wz)
        s = scale_at(cam, wz)
        base = y0 + 0.004 * s
        hh = hgt * s
        if hh < 4:
            continue
        col = TREE if kind == 0 else TREE2
        rr = _rng(seed)
        for k in range(3):
            ox = (k - 1) * hh * 0.30 + (rr() - 0.5) * hh * 0.1
            oy = -hh * (0.55 + 0.12 * (1 - abs(k - 1)))
            rx = hh * (0.30 + 0.06 * rr())
            d.ellipse([bx + ox - rx, base + oy - rx * 0.8, bx + ox + rx, base + oy + rx * 0.5],
                      fill=col + (178,))
    # fence line: a man-made horizontal that also reads as a leading line
    d.line([(0, y0 + 1), (W, y0 + 1)], fill=(146, 148, 128, 90), width=3)
    for i in range(11):
        fx = (i + 0.5) * W / 11
        d.line([(fx, y0 + 2), (fx, y0 - H * 0.014)], fill=(132, 130, 112, 110), width=3)
        d.line([(fx - 6, y0 - H * 0.014), (fx + 6, y0 - H * 0.014)], fill=(132, 130, 112, 90), width=2)
    d.line([(0, y0 - H * 0.010), (W, y0 - H * 0.010)], fill=(140, 138, 120, 60), width=2)


# ---------------------------------------------------------------- L3 ground
def ground(img, cam, seed=3, path=True):
    y0 = int(max(0, min(H, horizon(cam))))
    n = H - y0
    if n <= 2:
        return y0
    ys = np.linspace(0, 1, n)[:, None]
    k = ys ** 0.8
    k2 = np.clip((k - 0.45) / 0.55, 0, 1)
    arr = (np.array(G_FAR, float) * (1 - k) + np.array(G_MID, float) * k) * (1 - k2) + \
          (np.array(G_MID, float) * (1 - k2) + np.array(G_NEAR, float) * k2) * k2
    arr = np.repeat(arr[:, None, :], W, axis=1).astype(np.uint8)
    img.paste(Image.fromarray(arr, "RGB"), (0, y0))
    d = ImageDraw.Draw(img, "RGBA")
    if path:
        # the track is a world-space polygon: it converges because the projection says so
        quad = [proj(cam, -1.05, 0.0, -14.0), proj(cam, 0.05, 0.0, -14.0),
                proj(cam, 3.0, 0.0, 6.0), proj(cam, -1.9, 0.0, 6.0)]
        d.polygon(quad, fill=PATH + (150,))
        _soft(img, lambda dd, k: (dd.polygon([(x * k, y * k) for x, y in quad],
                                             outline=PATH_EDGE + (110,), width=int(7 * k))), 5)
    # tufts of dry grass, placed in the world so their size follows depth
    r = _rng(seed + 40)
    for i in range(210):
        wz = -20.0 + 26.0 * r()
        wx = -9.0 + 18.0 * r()
        s_ = scale_at(cam, wz)
        px, py = proj(cam, wx, 0.0, wz)
        if not (-30 < px < W + 30 and y0 < py < H + 20) or s_ < 6:
            continue
        hh = min(0.42 * s_, 46)
        for kk in range(3):
            lean = (r() - 0.5) * 0.9
            d.line([(px, py), (px + lean * hh * 0.5, py - hh * (0.6 + 0.4 * r()))],
                   fill=GRASS + (int(120 * min(1.0, s_ / 120.0)) + 40,), width=max(1, int(hh * 0.10)))
    r = _rng(seed)
    for i in range(150):                       # stones: size follows the ground scale
        wz = -9.0 + 12.0 * r()
        wx = -6.5 + 13.0 * r()
        s = scale_at(cam, wz)
        px, py = proj(cam, wx, 0.0, wz)
        if not (0 < px < W and y0 < py < H):
            continue
        rr = max(0.6, 0.030 * s * (0.5 + r()))
        d.ellipse([px - rr, py - rr * 0.42, px + rr, py + rr * 0.42], fill=(150, 138, 116, 46))
    return y0


# ---------------------------------------------------------------- cast shadows
def cast_shadow(img, cam, x, z, height=1.55, width=0.20, slope=0.52, alpha=78, blur=9,
                head_r=0.13):
    """The ground shadow of a standing body: a tapered band plus a head blob.

    `slope` is horizontal travel per metre of height — the sun's elevation, in effect.
    """
    fx, fy = proj(cam, x, 0.004, z)
    fhx, fhy = proj(cam, x, 0.10, z)          # start a little up the leg: no gap at the ankle
    fx, fy = fhx, fhy + 2
    hx = x + SHADOW_DIR[0] * height * slope
    hz = z + SHADOW_DIR[1] * height * slope
    tx, ty = proj(cam, hx, 0.004, hz)
    s_f = scale_at(cam, z) * 0.0016
    s_t = scale_at(cam, hz) * 0.0016
    wf = max(2.0, width * scale_at(cam, z) * 0.5)
    wt = max(2.0, width * scale_at(cam, hz) * 0.85)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    dx, dy = tx - fx, ty - fy
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    d.polygon([(fx + nx * wf, fy + ny * wf), (fx - nx * wf, fy - ny * wf),
               (tx - nx * wt, ty - ny * wt), (tx + nx * wt, ty + ny * wt)],
              fill=(58, 54, 44, alpha))
    hr = max(2.0, head_r * scale_at(cam, hz) * 0.9)
    d.ellipse([tx - hr, ty - hr * 0.62, tx + hr, ty + hr * 0.62], fill=(58, 54, 44, alpha))
    if blur > 0:
        lay = lay.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(lay)


def shadow_blob(img, cam, x, z, r=0.42, alpha=90, blur=6):
    """A soft contact patch for a crouching or kneeling body."""
    px, py = proj(cam, x, 0.004, z)
    s = scale_at(cam, z)
    _soft(img, lambda d, k: d.ellipse([(px - r * s) * k, (py - r * s * 0.35) * k,
                                       (px + r * s) * k, (py + r * s * 0.35) * k],
                                      fill=(58, 54, 44, alpha)), blur)


# ---------------------------------------------------------------- L4 near plane
def near_plane(img, strength=1.0, shift=0.0):
    """Blurred branch top-left + grass along the bottom. Depth, not detail."""
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(fg)
    c = INK_FG + (255,)
    limb = [(-120 - shift, 120), (70 - shift, 60), (230 - shift, -10), (380 - shift, -60)]
    d.line(limb, fill=c, width=15, joint="curve")
    for i, (bx, by) in enumerate(((60 - shift, 78), (210 - shift, 18))):
        d.line([(bx, by), (bx + 70, by + 92)], fill=c, width=9)
        for j in range(3):
            lx, ly = bx + 20 + 46 * j, by + 30 + 30 * j
            leaf = Image.new("RGBA", (150, 90), (0, 0, 0, 0))
            ImageDraw.Draw(leaf).ellipse([6, 6, 144, 84], fill=c)
            leaf = leaf.rotate(-38 + j * 24, expand=True, resample=Image.BICUBIC)
            fg.alpha_composite(leaf, (int(lx - leaf.width / 2), int(ly - leaf.height / 2)))
    r = _rng(21)
    for _ in range(26):
        side = r()
        gx = -40 + W * 0.30 * r() if side < 0.5 else W * 0.70 + W * 0.32 * r()
        base = H + 6 - 18 * r()
        hh = 60 + 95 * r()
        for k in range(5):
            lean = (r() - 0.5) * 1.1
            mid = (gx + lean * hh * 0.35, base - hh * 0.5)
            d.line([(gx, base), mid, (mid[0] + lean * hh * 0.6, base - hh * (0.6 + 0.4 * r()))],
                   fill=INK_FG + (150,), width=max(2, int(2 + 2 * r())), joint="curve")
    fg = fg.filter(ImageFilter.GaussianBlur(9))
    if strength < 0.999:
        a = fg.split()[3].point(lambda v: int(v * strength))
        fg.putalpha(a)
    img.alpha_composite(fg)


# ---------------------------------------------------------------- air
def dust(img, t, n=90, seed=8, alpha=120, top=0.55):
    """Motes low in the frame, where the light actually catches them."""
    r = _rng(seed)
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(n):
        x = (r() * W + t * (7 + 12 * r()) * (0.4 + r())) % (W + 40) - 20
        y = H * top + (r() * H * (1 - top) + t * (10 + 16 * r())) % (H * (1 - top) + 20)
        rr = 0.7 + 1.7 * r()
        d.ellipse([x - rr, y - rr, x + rr, y + rr],
                  fill=(255, 250, 232, int(alpha * 0.55 * (0.4 + 0.6 * r()))))


def heat(img, t, y0, strength=0.0):
    """A shimmer band just above the ground: one strip displaced, cheap and readable."""
    if strength <= 0.01:
        return
    band_h = 90
    top = int(max(0, y0 - band_h))
    strip = img.crop((0, top, W, top + band_h))
    arr = np.asarray(strip).astype(np.uint8)
    out = np.zeros_like(arr)
    for row in range(band_h):
        sh = int(3.0 * strength * math.sin(t * 2.4 + row * 0.22) * (1 - row / band_h))
        out[row] = np.roll(arr[row], sh, axis=0)
    img.paste(Image.fromarray(out), (0, top))


def vignette(img, strength=64):
    _soft(img, lambda d, k: (d.rectangle([0, 0, W * k, H * k], outline=(30, 26, 20, strength),
                                         width=int(260 * k))), 220)


def grade(img, tint=(255, 248, 236), lift=0.0, sat=1.0):
    arr = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    t = np.array(tint, np.float32) / 255.0
    arr = arr * t
    if sat != 1.0:
        g = arr.mean(axis=2, keepdims=True)
        arr = g + (arr - g) * sat
    if lift:
        arr = arr + (1 - arr) * lift
    img.paste(Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)))
