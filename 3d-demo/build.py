#!/usr/bin/env python3
"""
3D demo — 12 s, 1080x1920, 30 fps, rendered by a small software rasteriser (numpy + PIL).

No Blender, no GPU, no browser: geometry -> model/view/projection -> z-buffer -> Lambert + rim
-> depth fog -> projected hard shadow -> ffmpeg. Every frame is a pure function of t.

What it demonstrates (3D animation craft, not just a pretty render):
  - squash & stretch along the path, volume-preserving, driven by vertical speed
  - timing that carries weight: bounces decay, ground contact shortens as the energy dies
  - arcs live in the trajectory, not in an easing curve
  - one camera move (orbit + dolly), slow and eased; focal length fixed
  - facets as the light source of detail: flat shading, one warm key, one cool rim
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RW, RH = 1440, 2560          # render size (1.33x), downscaled to 1080x1920
OW, OH = 1080, 1920
FPS, DUR = 30, 12.0
N = int(FPS * DUR)

SKY_TOP = np.array([0.055, 0.052, 0.070])
SKY_HOR = np.array([0.145, 0.115, 0.105])
GROUND = np.array([0.145, 0.130, 0.118])
ROCK = np.array([0.34, 0.30, 0.26])
BALL = np.array([0.851, 0.467, 0.341])       # #D97757 — the one accent
MOON = np.array([0.72, 0.70, 0.66])

L_KEY = np.array([-0.45, 0.86, 0.34]); L_KEY /= np.linalg.norm(L_KEY)
C_KEY = np.array([1.00, 0.93, 0.84])
AMB = np.array([0.16, 0.17, 0.22])
C_RIM = np.array([0.55, 0.68, 1.00])

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
if not os.path.exists(FFMPEG):
    FFMPEG = "ffmpeg"


# ---------------------------------------------------------------- geometry
def icosphere(subdiv=1):
    t = (1 + 5 ** 0.5) / 2
    v = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
         (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    v = [np.array(p, float) / np.linalg.norm(p) for p in v]
    f = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2),
         (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5),
         (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
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
    return np.array(v), np.array(f)


def ground_grid(n=9, size=34.0):
    verts, faces, shades = [], [], []
    step = size / n
    for i in range(n + 1):
        for j in range(n + 1):
            verts.append(((-size / 2 + i * step), 0.0, (-size / 2 + j * step)))
    for i in range(n):
        for j in range(n):
            a = i * (n + 1) + j
            b, c, d = a + 1, a + (n + 1), a + (n + 1) + 1
            faces += [(a, c, b), (b, c, d)]
            s = 0.82 + 0.36 * ((i * 7 + j * 13) % 5) / 4.0
            shades += [s, s]
    return np.array(verts, float), np.array(faces), np.array(shades, float)


def box(cx, cy, cz, sx, sy, sz):
    v = np.array([[-1, -1, -1], [1, -1, -1], [1, -1, 1], [-1, -1, 1],
                  [-1, 1, -1], [1, 1, -1], [1, 1, 1], [-1, 1, 1]], float)
    v = v * np.array([sx, sy, sz]) / 2 + np.array([cx, cy, cz])
    f = np.array([[0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6], [0, 4, 5], [0, 5, 1],
                  [1, 5, 6], [1, 6, 2], [2, 6, 7], [2, 7, 3], [3, 7, 4], [3, 4, 0]])
    return v, f


# ---------------------------------------------------------------- camera
def look_at(eye, tgt, up=(0, 1, 0)):
    fwd = tgt - eye
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array(up, float))
    right /= np.linalg.norm(right)
    upv = np.cross(right, fwd)
    return np.stack([right, upv, fwd])


def project(P, eye, R, focal):
    d = P - eye
    x = d @ R[0]
    y = d @ R[1]
    z = d @ R[2]
    z = np.where(z < 0.05, 0.05, z)
    return np.stack([RW / 2 + focal * x / z, RH / 2 - focal * y / z, z], axis=1)


# ---------------------------------------------------------------- raster
def raster(rgb, zbuf, S, faces, cols, bias=0.0, two_sided=True):
    """Fill triangles with flat colour, numpy per-triangle. S: (n,3) screen x,y,z."""
    for k, (a, b, c) in enumerate(faces):
        p0, p1, p2 = S[a], S[b], S[c]
        minx = int(max(0, math.floor(min(p0[0], p1[0], p2[0]))))
        maxx = int(min(RW - 1, math.ceil(max(p0[0], p1[0], p2[0]))))
        miny = int(max(0, math.floor(min(p0[1], p1[1], p2[1]))))
        maxy = int(min(RH - 1, math.ceil(max(p0[1], p1[1], p2[1]))))
        if minx >= maxx or miny >= maxy:
            continue
        x0, y0 = p0[0], p0[1]; x1, y1 = p1[0], p1[1]; x2, y2 = p2[0], p2[1]
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9:
            continue
        xs = np.arange(minx, maxx + 1) + 0.5
        ys = np.arange(miny, maxy + 1) + 0.5
        X, Y = np.meshgrid(xs, ys)
        w0 = ((y1 - y2) * (X - x2) + (x2 - x1) * (Y - y2)) / den
        w1 = ((y2 - y0) * (X - x2) + (x0 - x2) * (Y - y2)) / den
        w2 = 1.0 - w0 - w1
        m = (w0 >= -0.002) & (w1 >= -0.002) & (w2 >= -0.002)
        if not m.any():
            continue
        z = w0 * p0[2] + w1 * p1[2] + w2 * p2[2] + bias
        zb = zbuf[miny:maxy + 1, minx:maxx + 1]
        m &= z < zb
        if not m.any():
            continue
        zb[m] = z[m]
        rgb[miny:maxy + 1, minx:maxx + 1][m] = cols[k]


# ---------------------------------------------------------------- scene
BALL_V, BALL_F = icosphere(1)
ROCK_V, ROCK_F = icosphere(0)
GRID_V, GRID_F, GRID_S = ground_grid()

ROCKS = [(np.array([-7.5, 0.0, -3.0]), 1.9, 0.4),
         (np.array([6.8, 0.0, -5.0]), 1.4, 1.9),
         (np.array([2.0, 0.0, 6.5]), 1.1, 3.1),
         (np.array([-4.0, 0.0, 5.2]), 0.8, 0.9)]


def bounces():
    """[(t_start, duration, height)] — energy dies, ground contact shortens."""
    segs, t, h = [], 0.55, 8.4
    while t < DUR - 0.4 and h > 0.9:
        T = 2.0 * math.sqrt(2 * h / 26.0)
        segs.append((t, T, h))
        t += T + 0.10 * math.sqrt(h)
        h *= 0.56
    return segs


SEGS = bounces()


def ball_state(t):
    """centre y above the floor, stretch factor along the path, rotation."""
    base = 1.15
    if t < SEGS[0][0]:
        return base, 1.0
    for (t0, T, h) in SEGS:
        if t0 <= t < t0 + T:
            u = (t - t0) / T
            y = h * (1 - (2 * u - 1) ** 2)
            v = 8 * h * abs(2 * u - 1) / T           # vertical speed (arbitrary units)
            k = min(1.0 + 0.055 * v, 1.42)           # stretch along the path
            return base + y, k
    return base + 0.0, 1.0


_yy, _xx = np.mgrid[0:RH, 0:RW]
_rs = np.random.RandomState(7)
_stars = _rs.randint(0, RW, 260), _rs.randint(0, int(RH * 0.62), 260)
STAR_X, STAR_Y = _stars
STAR_B = _rs.uniform(0.05, 0.30, 260)
_r = np.sqrt(((_xx - RW / 2) / (RW / 2)) ** 2 + ((_yy - RH / 2) / (RH / 2)) ** 2 * 0.55)
VIG = np.clip(1.0 - 0.30 * _r ** 2, 0.0, 1.0)[:, :, None]


def shade(n, base, view):
    lam = max(0.0, float(n @ -L_KEY * -1) if False else float(n @ L_KEY))
    rim = max(0.0, 1.0 - abs(float(n @ view))) ** 3
    return np.clip(base * (AMB + C_KEY * lam) + C_RIM * rim * 0.55, 0, 1)


def render(t):
    # --- camera: one eased orbit + dolly, focal length fixed
    p = 0.5 - 0.5 * math.cos(math.pi * min(max(t / 11.6, 0), 1))     # ease in/out
    az = -0.42 + 0.66 * p
    dist = 27.0 - 6.4 * p
    hgt = 6.4 + 1.5 * p
    tgt = np.array([0.0, 3.4, 0.0])
    eye = tgt + np.array([math.sin(az) * dist, hgt, math.cos(az) * dist])
    R = look_at(eye, tgt)
    focal = (RH / 2) / math.tan(math.radians(38) / 2)

    # --- sky (vertical gradient, cached once per frame from a ramp)
    bg = SKY_HOR[None, :] + (SKY_TOP - SKY_HOR)[None, :] * np.linspace(0, 1, RH)[:, None] ** 0.8
    rgb = np.repeat(bg[:, None, :], RW, axis=1).copy()
    rgb[STAR_Y, STAR_X] += STAR_B[:, None]                      # stars: fixed, at infinity
    px, py = RW / 2 + focal * 0.0, RH * 0.36           # light pool behind the subject
    _glow = np.exp(-((( _xx - px) ** 2 / (1.0 * RW ** 2) + (_yy - py) ** 2 / (0.55 * RH ** 2))))
    rgb += _glow[:, :, None] * np.array([0.16, 0.12, 0.10])[None, None, :]
    zbuf = np.full((RH, RW), 1e9, dtype=np.float32)

    # --- ground
    S = project(GRID_V, eye, R, focal)
    gcols = [np.clip(GROUND * s * (0.55 + 0.45 * max(0, float(np.cross(
        GRID_V[f[1]] - GRID_V[f[0]], GRID_V[f[2]] - GRID_V[f[0]]) @ L_KEY)) * 3.2), 0, 1)
        for s, f in zip(GRID_S, GRID_F)]
    raster(rgb, zbuf, S, GRID_F, gcols)

    # --- objects
    objs = []
    for pos, rad, rot in ROCKS:
        Rm = np.array([[math.cos(rot), 0, math.sin(rot)], [0, 1, 0], [-math.sin(rot), 0, math.cos(rot)]])
        V = (ROCK_V @ Rm.T) * rad + pos
        V[:, 1] = np.maximum(V[:, 1], 0.0) * 0.85 + 0.0
        objs.append((V, ROCK_F, ROCK, True))

    yb, k = ball_state(t)
    spin = t * 0.55
    Rm = np.array([[math.cos(spin), 0, math.sin(spin)], [0, 1, 0], [-math.sin(spin), 0, math.cos(spin)]])
    Vb = (BALL_V @ Rm.T) * np.array([1 / math.sqrt(k), k, 1 / math.sqrt(k)]) * 1.55
    Vb[:, 1] += yb
    objs.append((Vb, BALL_F, BALL, True))



    # --- hard shadows: project onto y=0 along the key light
    for V, F, col, casts in objs:
        if not casts:
            continue
        Vs = V.copy()
        Vs[:, 1] = np.maximum(Vs[:, 1], 0.0)
        sc = Vs - L_KEY[None, :] * (Vs[:, 1:2] / L_KEY[1])
        sc[:, 1] = 0.012
        S = project(sc, eye, R, focal)
        raster(rgb, zbuf, S, F, [np.array([0.055, 0.050, 0.052])] * len(F), bias=-0.02)

    # --- shade and draw
    for V, F, base, casts in objs:
        view = V.mean(axis=0) - eye
        view /= np.linalg.norm(view)
        cols = []
        for f in F:
            n = np.cross(V[f[1]] - V[f[0]], V[f[2]] - V[f[0]])
            nn = np.linalg.norm(n)
            if nn < 1e-9:
                cols.append(base * 0.5)
                continue
            n = n / nn
            if n @ view > 0:
                n = -n
            cols.append(shade(n, base, view))
        S = project(V, eye, R, focal)
        raster(rgb, zbuf, S, F, cols)

    # --- depth fog (to the horizon colour)
    z = np.clip((zbuf - 22.0) / 46.0, 0, 1)[:, :, None]
    rgb = rgb * (1 - z * 0.92) + SKY_HOR * (z * 0.92)

    # --- vignette: keeps the eye on the middle of a dark stage
    rgb = rgb * VIG

    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    return img.resize((OW, OH), Image.LANCZOS)


def end_card(img, t):
    if t < 9.6:
        return img
    d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(FONT, 54)
    f2 = ImageFont.truetype(FONT_R, 34)
    d.text((540, 1620), "GEOMETRY · LIGHT · MOTION", font=f1, fill=(240, 238, 230), anchor="mm")
    d.text((540, 1692), "software rasteriser — no 3D package", font=f2, fill=(196, 190, 178), anchor="mm")
    return img


def main():
    os.makedirs("frames", exist_ok=True)
    out = "3d-demo-1080x1920.mp4"
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (OW, OH), "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    marks = (0, 40, 75, 130, 200, 300, 348)
    for i in range(N):
        t = i / FPS
        fr = end_card(render(t), t)
        p.stdin.write(fr.tobytes())
        if i in marks:
            fr.save("frames/f%03d.png" % i)
        if i % 60 == 0:
            print("  %d/%d t=%.2fs" % (i, N, t), flush=True)
    p.stdin.close()
    p.wait()
    print("done:", out, os.path.getsize(out))


if __name__ == "__main__":
    if "--test" in sys.argv:
        os.makedirs("frames", exist_ok=True)
        for i in (10, 40, 200, 340):
            end_card(render(i / FPS), i / FPS).save("frames/test_%03d.png" % i)
        print("test frames written")
    else:
        main()
