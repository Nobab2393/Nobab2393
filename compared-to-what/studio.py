"""studio.py — a small software renderer for a storybook film.

No 3D package, no GPU, no textures: geometry -> look-at -> perspective project ->
z-buffer + flat Lambert -> projected shadow -> autumn fog -> film grade.

Deliberately low-poly: every primitive is 20-80 triangles, so a frame with a town,
three characters and a bicycle stays under ~6k triangles and renders in about a second.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ---------------------------------------------------------------- palette
# Muted autumn, golden hour. Everything is a warm desaturated earth or a soft teal grey.
SKY_TOP = np.array([0.34, 0.42, 0.49])
SKY_MID = np.array([0.86, 0.71, 0.55])
SKY_LOW = np.array([0.99, 0.82, 0.58])
SUN = np.array([1.00, 0.88, 0.66])
FOG = np.array([0.78, 0.68, 0.58])
GROUND = np.array([0.47, 0.38, 0.29])
STONE = np.array([0.62, 0.58, 0.52])
FUR = np.array([0.80, 0.70, 0.57])          # Bruno
FUR_D = np.array([0.68, 0.55, 0.44])
EAR = np.array([0.86, 0.62, 0.58])
CREAM = np.array([0.93, 0.88, 0.78])
OWL = np.array([0.55, 0.47, 0.40])          # Olive
OWL_L = np.array([0.78, 0.70, 0.60])
SCARF = np.array([0.46, 0.32, 0.28])
HEDGE = np.array([0.40, 0.30, 0.24])
WOOD = np.array([0.52, 0.36, 0.24])
WOOD_D = np.array([0.36, 0.25, 0.18])
RUST = np.array([0.66, 0.35, 0.22])
TEAL = np.array([0.28, 0.36, 0.35])
SAGE = np.array([0.45, 0.48, 0.36])
BRICK = np.array([0.55, 0.36, 0.30])
GLOW = np.array([1.00, 0.82, 0.52])
DARK = np.array([0.13, 0.11, 0.10])

L_KEY = np.array([-0.42, 0.46, 0.78])
L_KEY /= np.linalg.norm(L_KEY)
C_KEY = np.array([1.00, 0.86, 0.66])
AMB = np.array([0.42, 0.38, 0.38])
C_RIM = np.array([0.62, 0.74, 0.86])
C_BOUNCE = np.array([0.56, 0.42, 0.30])


# ---------------------------------------------------------------- primitives
def icosphere(subdiv=1, squash=1.0):
    t = (1 + 5 ** 0.5) / 2
    v = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t),
         (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    v = [np.array(p, float) / np.linalg.norm(p) for p in v]
    f = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4),
         (11, 10, 2), (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8),
         (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    for _ in range(subdiv):
        nf, cache = [], {}

        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache:
                m = (v[a] + v[b]) / 2
                v.append(m / np.linalg.norm(m))
                cache[k] = len(v) - 1
            return cache[k]

        for a, b, c in f:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            nf += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        f = nf
    V = np.array(v)
    if squash != 1.0:
        V = V * np.array([1.0, squash, 1.0])
    return V, np.array(f, dtype=np.int32)


def box():
    v = np.array([[-1, -1, -1], [1, -1, -1], [1, -1, 1], [-1, -1, 1],
                  [-1, 1, -1], [1, 1, -1], [1, 1, 1], [-1, 1, 1]], float) * 0.5
    f = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4],
                  [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]],
                 dtype=np.int32)
    return v, f


def cyl(n=10, caps=True, r0=1.0, r1=1.0):
    """Cylinder/cone from y=0 to y=1, radius r0 at the base, r1 at the top."""
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    v = [(math.cos(a) * r0, 0.0, math.sin(a) * r0) for a in ang]
    v += [(math.cos(a) * r1, 1.0, math.sin(a) * r1) for a in ang]
    f = []
    for i in range(n):
        j = (i + 1) % n
        f += [(i, n + i, n + j), (i, n + j, j)]
    if caps:
        if r0 > 1e-6:
            v.append((0.0, 0.0, 0.0))
            c0 = len(v) - 1
            f += [(c0, i, (i + 1) % n) for i in range(n)]
        if r1 > 1e-6:
            v.append((0.0, 1.0, 0.0))
            c1 = len(v) - 1
            f += [(c1, n + (i + 1) % n, n + i) for i in range(n)]
    return np.array(v, float), np.array(f, dtype=np.int32)


def torus(R=1.0, r=0.2, nmaj=12, nmin=6):
    v, f = [], []
    for i in range(nmaj):
        a = 2 * math.pi * i / nmaj
        ca, sa = math.cos(a), math.sin(a)
        for j in range(nmin):
            b = 2 * math.pi * j / nmin
            cb, sb = math.cos(b), math.sin(b)
            v.append(((R + r * cb) * ca, r * sb, (R + r * cb) * sa))
    for i in range(nmaj):
        for j in range(nmin):
            a0 = i * nmin + j
            a1 = i * nmin + (j + 1) % nmin
            b0 = ((i + 1) % nmaj) * nmin + j
            b1 = ((i + 1) % nmaj) * nmin + (j + 1) % nmin
            f += [(a0, b0, b1), (a0, b1, a1)]
    return np.array(v, float), np.array(f, dtype=np.int32)


def plane(w=1.0, d=1.0):
    v = np.array([[-w / 2, 0, -d / 2], [w / 2, 0, -d / 2], [w / 2, 0, d / 2],
                  [-w / 2, 0, d / 2]], float)
    f = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
    return v, f


SH_V, SH_F = icosphere(1)
SH0_V, SH0_F = icosphere(0)
BX_V, BX_F = box()
CY_V, CY_F = cyl(10)
CY8_V, CY8_F = cyl(8)
CO_V, CO_F = cyl(8, r0=1.0, r1=0.0)
TO_V, TO_F = torus(1.0, 0.16, 10, 5)
PL_V, PL_F = plane()


def xform(V, pos=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0)):
    """Scale, then rotate X->Y->Z, then translate. Everything in metres-ish units."""
    V = V * np.asarray(scale, float)[None, :]
    rx, ry, rz = rot
    if rz:
        c, s = math.cos(rz), math.sin(rz)
        V = V @ np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)
    if rx:
        c, s = math.cos(rx), math.sin(rx)
        V = V @ np.array([[1, 0, 0], [0, c, -s], [0, s, c]], float)
    if ry:
        c, s = math.cos(ry), math.sin(ry)
        V = V @ np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)
    return V + np.asarray(pos, float)[None, :]


class O:
    """One object: a mesh, a base colour, and whether it casts a shadow."""
    __slots__ = ("V", "F", "col", "cast", "matte", "shade")

    def __init__(self, V, F, col, cast=True, matte=False):
        self.V, self.F, self.col, self.cast, self.matte = V, F, col, cast, matte


def put(V, F, col, pos=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), cast=True, matte=False):
    return O(xform(V, pos, scale, rot), F, np.asarray(col, float), cast, matte)


# ---------------------------------------------------------------- camera
class Cam:
    def __init__(self, eye, tgt, fov=34.0, roll=0.0):
        self.eye = np.asarray(eye, float)
        tgt = np.asarray(tgt, float)
        fwd = tgt - self.eye
        fwd /= np.linalg.norm(fwd)
        up = np.array([0.0, 1.0, 0.0])
        right = np.cross(fwd, up)
        right /= np.linalg.norm(right)
        upv = np.cross(right, fwd)
        if roll:
            c, s = math.cos(roll), math.sin(roll)
            right, upv = right * c + upv * s, upv * c - right * s
        self.R = np.stack([right, upv, fwd])
        self.fov = fov


def project(P, cam, W, H):
    d = P - cam.eye
    x = d @ cam.R[0]
    y = d @ cam.R[1]
    z = d @ cam.R[2]
    z = np.where(z < 0.08, 0.08, z)
    focal = (H / 2) / math.tan(math.radians(cam.fov) / 2)
    return np.stack([W / 2 + focal * x / z, H / 2 - focal * y / z, z], axis=1)


# ---------------------------------------------------------------- raster
def raster(rgb, zbuf, S, faces, cols, bias=0.0):
    H, W = zbuf.shape
    for k, (a, b, c) in enumerate(faces):
        p0, p1, p2 = S[a], S[b], S[c]
        if p0[2] <= 0.1 or p1[2] <= 0.1 or p2[2] <= 0.1:
            continue                     # straddles the eye: no clipping, just drop it
        minx = int(max(0, math.floor(min(p0[0], p1[0], p2[0]))))
        maxx = int(min(W - 1, math.ceil(max(p0[0], p1[0], p2[0]))))
        miny = int(max(0, math.floor(min(p0[1], p1[1], p2[1]))))
        maxy = int(min(H - 1, math.ceil(max(p0[1], p1[1], p2[1]))))
        if minx >= maxx or miny >= maxy:
            continue
        x0, y0 = p0[0], p0[1]
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9:
            continue
        X, Y = np.meshgrid(np.arange(minx, maxx + 1) + 0.5, np.arange(miny, maxy + 1) + 0.5)
        w0 = ((y1 - y2) * (X - x2) + (x2 - x1) * (Y - y2)) / den
        w1 = ((y2 - y0) * (X - x2) + (x0 - x2) * (Y - y2)) / den
        w2 = 1.0 - w0 - w1
        m = (w0 >= -0.004) & (w1 >= -0.004) & (w2 >= -0.004)
        if not m.any():
            continue
        z = w0 * p0[2] + w1 * p1[2] + w2 * p2[2] + bias
        zb = zbuf[miny:maxy + 1, minx:maxx + 1]
        m &= z < zb
        if not m.any():
            continue
        zb[m] = z[m]
        rgb[miny:maxy + 1, minx:maxx + 1][m] = cols[k]


FILL = [0.0]
_VIG_CACHE = {}


def shade_face(n, base, view):
    lam = max(0.0, float(n @ L_KEY))
    rim = max(0.0, 1.0 - abs(float(n @ view))) ** 4
    bounce = max(0.0, -float(n[1])) * 0.55           # light off the warm ground
    c = base * (AMB + C_KEY * lam + FILL[0]) + C_RIM * rim * 0.30 + C_BOUNCE * bounce * 0.35
    return np.clip(c, 0, 1)


# ---------------------------------------------------------------- sky
_SKY_CACHE = {}


def sky_layer(W, H, sun_xy=(0.72, 0.30), clouds=True, top=SKY_TOP, mid=SKY_MID, low=SKY_LOW,
              seed=3):
    key = (W, H, sun_xy, clouds, seed)
    if key in _SKY_CACHE:
        return _SKY_CACHE[key].copy()
    ys = (np.linspace(0, 1, H) ** 0.85)[:, None, None]
    rgb = np.repeat(mid[None, None, :], H, 0).repeat(W, 1)
    t = ys
    upper = np.clip(1.0 - t * 2.0, 0, 1) ** 0.8
    rgb = rgb * (1 - upper) + top[None, None, :] * upper
    lower = np.clip((t - 0.55) / 0.45, 0, 1) ** 1.3
    rgb = rgb * (1 - lower) + low[None, None, :] * lower
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sx, sy = sun_xy[0] * W, sun_xy[1] * H
    d = ((xx - sx) ** 2 + (yy - sy) ** 2) / (W * W * 0.020)
    glow = np.exp(-d)
    rgb += (SUN - 0.30)[None, None, :] * glow[:, :, None] * 0.55
    disc = np.exp(-(((xx - sx) ** 2 + (yy - sy) ** 2) / (W * W * 0.00075)))
    rgb = rgb * (1 - disc[:, :, None] * 0.85) + SUN[None, None, :] * disc[:, :, None] * 0.85
    if clouds:
        rng = np.random.RandomState(seed)
        im = Image.new("L", (W // 4, H // 4), 0)
        d2 = ImageDraw.Draw(im)
        for i in range(16):
            cx = rng.uniform(0, W / 4)
            cy = rng.uniform(H * 0.02, H * 0.42) / 4
            for j in range(rng.randint(3, 6)):
                rx = rng.uniform(0.02, 0.07) * W / 4
                ry = rx * rng.uniform(0.25, 0.45)
                d2.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=rng.randint(90, 150))
            cx = cx
        im = im.filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
        a = (np.asarray(im, float) / 255.0)[:, :, None] * 0.55
        rgb = rgb * (1 - a) + np.array([0.97, 0.86, 0.74])[None, None, :] * a
    out = np.clip(rgb, 0, 1)
    _SKY_CACHE[key] = out
    return out.copy()


def ground_layer(W, H, cam, n=8, depth=110.0, half=90.0, seed=5):
    """The plaza floor, laid only in front of the eye so no tile straddles the camera."""
    rgb = np.zeros((H, W, 3), np.float32)
    zbuf = np.full((H, W), 1e9, np.float32)
    z_near = cam.eye[2] - 7.0
    z_far = cam.eye[2] - depth
    rng = np.random.RandomState(seed)
    verts, faces, shades = [], [], []
    nx, nz = n, int(n * 1.5)
    for i in range(nx + 1):
        for j in range(nz + 1):
            x = -half + 2 * half * i / nx
            z = z_near + (z_far - z_near) * (j / nz) ** 1.6
            verts.append((x, 0.0, z))
    for i in range(nx):
        for j in range(nz):
            a = i * (nz + 1) + j
            b, c, d = a + 1, a + (nz + 1), a + (nz + 1) + 1
            faces += [(a, b, c), (b, d, c)]
            s = 0.80 + 0.34 * rng.rand()
            shades += [s, s]
    V = np.array(verts, float)
    S = project(V, cam, W, H)
    cols = [np.clip(GROUND * s * 1.3, 0, 1) for s in shades]
    raster(rgb, zbuf, S, faces, cols)
    return rgb, zbuf


# ---------------------------------------------------------------- film
def render(scene, cam, W, H, sky_kw=None, shadows=True, fog=(24.0, 95.0), grain=0.018,
           vignette=0.26, warm=1.0, fill=0.0):
    FILL[0] = fill
    rgb = sky_layer(W, H, **(sky_kw or {}))
    g_rgb, g_z = ground_layer(W, H, cam)
    m = g_z < 1e8
    rgb[m] = g_rgb[m]
    zbuf = np.where(m, g_z, np.full_like(g_z, 1e9))

    # shadows: project every caster onto y=0 along the key light, blur, multiply
    if shadows:
        sh = np.zeros((H // 6, W // 6), np.float32)
        shz = np.full((H // 6, W // 6), 1e9, np.float32)
        shrgb = np.zeros((H // 6, W // 6, 3), np.float32)
        for o in scene:
            if not o.cast:
                continue
            Vs = o.V.copy()
            Vs[:, 1] = np.maximum(Vs[:, 1], 0.0)
            sc = Vs - L_KEY[None, :] * (Vs[:, 1:2] / L_KEY[1])
            sc[:, 1] = 0.008
            if sc[:, 2].min() > cam.eye[2] + 4:
                pass
            S = project(sc, cam, W // 6, H // 6)
            raster(shrgb, shz, S, o.F, [np.ones(3, np.float32) * 0.55] * len(o.F), bias=-0.02)
        mask = Image.fromarray((np.clip(shrgb[:, :, 0], 0, 1) * 255).astype(np.uint8))
        mask = mask.filter(ImageFilter.GaussianBlur(2)).resize((W, H), Image.BILINEAR)
        a = (np.asarray(mask, float) / 255.0)[:, :, None]
        rgb = rgb * (1 - a * 0.62)

    order = sorted(range(len(scene)), key=lambda i: -float(np.linalg.norm(
        scene[i].V.mean(0) - cam.eye)))
    for i in order:
        o = scene[i]
        if o.V[:, 2].min() > cam.eye[2] + 60:
            continue
        view = o.V.mean(axis=0) - cam.eye
        nv = np.linalg.norm(view)
        if nv < 1e-6:
            continue
        view = view / nv
        if o.matte:
            cols = [np.clip(o.col, 0, 1)] * len(o.F)
        else:
            cols = []
            for f in o.F:
                n = np.cross(o.V[f[1]] - o.V[f[0]], o.V[f[2]] - o.V[f[0]])
                nn = np.linalg.norm(n)
                if nn < 1e-9:
                    cols.append(o.col * 0.6)
                    continue
                n = n / nn
                if n @ view > 0:
                    n = -n
                cols.append(shade_face(n, o.col, view))
        S = project(o.V, cam, W, H)
        raster(rgb, zbuf, S, o.F, cols)

    # autumn haze, so distance reads as weather rather than as geometry
    z = np.clip((zbuf - fog[0]) / (fog[1] - fog[0]), 0, 1)
    z = np.where(zbuf < 1e8, z, 0.0)[:, :, None]      # the sky is not fog, it is the sky
    rgb = rgb * (1 - z * 0.92) + FOG[None, None, :] * (z * 0.92)

    vkey = (W, H, round(vignette, 3))
    if vkey not in _VIG_CACHE:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2 * 0.7)
        _VIG_CACHE[vkey] = np.clip(1.0 - vignette * r ** 2, 0, 1)[:, :, None]
    vig = _VIG_CACHE[vkey]
    rgb = rgb * vig

    rgb = rgb * np.array([1.0, 0.985, 0.95])[None, None, :] * warm + \
        np.array([0.03, 0.018, 0.0])[None, None, :] * (1 - rgb)
    if grain:
        rng = np.random.RandomState(int(abs(0.0) * 1000) + 7)
        n = rng.normal(0, grain, (H // 2, W // 2, 1)).astype(np.float32)
        rgb = np.clip(rgb + np.repeat(np.repeat(n, 2, 0), 2, 1), 0, 1)
    return rgb
