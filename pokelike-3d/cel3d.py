"""cel3d — a tiny cel-shading renderer (numpy + PIL) for a 3D-anime look.

No Blender, no GPU. Painter's algorithm per model, 3-band toon ramp, rim light,
emissive parts, and a silhouette outline made by dilating each model's own mask.

Conventions: right-handed, +X right, +Y up, +Z toward the camera.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ---------------------------------------------------------------- geometry


def _normalize(v):
    n = np.linalg.norm(v)
    return v / n if n else v


def icosphere(subdiv=2):
    t = (1 + 5 ** 0.5) / 2
    verts = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t),
             (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    verts = [np.array(v, float) / np.linalg.norm(v) for v in verts]
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4),
             (11, 10, 2), (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8),
             (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    for _ in range(subdiv):
        cache = {}
        new_faces = []

        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache:
                m = (verts[a] + verts[b]) / 2
                verts.append(m / np.linalg.norm(m))
                cache[k] = len(verts) - 1
            return cache[k]

        for a, b, c in faces:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            new_faces += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        faces = new_faces
    return np.array(verts), np.array(faces)


def sphere_mesh(subdiv=2):
    return icosphere(subdiv)


def cone_mesh(seg=14):
    """unit cone: base radius 1 at y=0, apex at y=1"""
    v = [(0.0, 1.0, 0.0)]
    for i in range(seg):
        a = 2 * math.pi * i / seg
        v.append((math.cos(a), 0.0, math.sin(a)))
    v.append((0.0, 0.0, 0.0))          # base centre
    faces = []
    for i in range(seg):
        faces.append((0, 1 + i, 1 + (i + 1) % seg))
        faces.append((seg + 1, 1 + (i + 1) % seg, 1 + i))
    return np.array(v, float), np.array(faces)


def box_mesh():
    v = np.array([(x, y, z) for x in (-.5, .5) for y in (-.5, .5) for z in (-.5, .5)])
    f = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1),
         (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    return v, np.array(f)


_CACHE = {}


def mesh(kind, subdiv=2):
    key = (kind, subdiv)
    if key not in _CACHE:
        if kind == "sphere":
            _CACHE[key] = sphere_mesh(subdiv)
        elif kind == "cone":
            _CACHE[key] = cone_mesh()
        elif kind == "box":
            _CACHE[key] = box_mesh()
        else:
            raise ValueError(kind)
    return _CACHE[key]


# ---------------------------------------------------------------- transforms


def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def S(x=1.0, y=None, z=None):
    y = x if y is None else y
    z = x if z is None else z
    return np.diag([x, y, z, 1.0])


def R(axis, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4)
    if axis == "x":
        m[1, 1], m[1, 2], m[2, 1], m[2, 2] = c, -s, s, c
    elif axis == "y":
        m[0, 0], m[0, 2], m[2, 0], m[2, 2] = c, s, -s, c
    else:
        m[0, 0], m[0, 1], m[1, 0], m[1, 1] = c, -s, s, c
    return m


# ---------------------------------------------------------------- camera


class Cam:
    def __init__(self, eye, target, fov=38.0, up=(0, 1, 0), w=1080, h=1920):
        self.eye = np.array(eye, float)
        f = _normalize(np.array(target, float) - self.eye)
        r = _normalize(np.cross(f, np.array(up, float)))
        u = np.cross(r, f)
        self.basis = np.stack([r, u, -f])     # world -> view
        self.f = (h / 2) / math.tan(math.radians(fov / 2))
        self.w, self.h = w, h

    def to_view(self, p):
        return (np.asarray(p, float) - self.eye) @ self.basis.T

    def project(self, pv):
        z = np.maximum(pv[..., 2] * -1.0, 1e-4)
        x = self.w / 2 + self.f * pv[..., 0] / z
        y = self.h / 2 - self.f * pv[..., 1] / z
        return np.stack([x, y], -1), z


# ---------------------------------------------------------------- model


class Part:
    """One primitive with a transform, a colour and a shading model."""

    def __init__(self, kind, matrix, color, emissive=0.0, subdiv=2, shade=1.0, rim=True):
        self.kind = kind
        self.m = np.asarray(matrix, float)
        self.color = np.array(color, float)
        self.emissive = emissive
        self.subdiv = subdiv
        self.shade = shade
        self.rim = rim


class Model:
    def __init__(self, parts):
        self.parts = parts


# ---------------------------------------------------------------- shading
L_KEY = _normalize(np.array([-0.42, 0.78, 0.46]))
L_FILL = _normalize(np.array([0.66, 0.22, 0.52]))
RIM_COL = np.array([0.62, 0.76, 1.0])


def toon(n_dot_l, base, shade=1.0):
    """3-band cel ramp: shadow / mid / light, plus a hard terminator."""
    if n_dot_l > 0.52:
        k = 1.10
    elif n_dot_l > 0.05:
        k = 1.0
    elif n_dot_l > -0.28:
        k = 0.74
    else:
        k = 0.58
    return np.clip(base * k * shade, 0, 1)


# ---------------------------------------------------------------- render


def model_bbox(model, cam, pad=60):
    """Screen-space bbox of every part's vertices (full-frame coords)."""
    xs, ys = [], []
    for part in model.parts:
        v, _ = mesh(part.kind, part.subdiv)
        hom = np.concatenate([v, np.ones((len(v), 1))], 1) @ part.m.T
        pv = cam.to_view(hom[:, :3])
        uv, z = cam.project(pv)
        xs.append(uv[:, 0]); ys.append(uv[:, 1])
    x = np.concatenate(xs); y = np.concatenate(ys)
    return (max(0, int(x.min() - pad)), max(0, int(y.min() - pad)),
            min(cam.w, int(x.max() + pad)), min(cam.h, int(y.max() + pad)))


def render_model_tiled(model, cam, ss=1.8, outline=None, glow=False, outline_px=7):
    """Supersampled render of one model into its own bbox tile; returns (RGBA, (x, y))."""
    x0, y0, x1, y1 = model_bbox(model, cam, pad=70)
    tw, th = max(8, x1 - x0), max(8, y1 - y0)
    tile = Image.new("RGBA", (int(tw * ss), int(th * ss)), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)

    drawables = []
    for part in model.parts:
        v, f = mesh(part.kind, part.subdiv)
        hom = np.concatenate([v, np.ones((len(v), 1))], 1) @ part.m.T
        pw = hom[:, :3]
        pv = cam.to_view(pw)
        uv, z = cam.project(pv)
        drawables.append((pv[:, 2].mean(), part, pw, uv, f))
    drawables.sort(key=lambda t: t[0])

    for _, part, pw, uv, faces in drawables:
        cols = []
        for tri in faces:
            a, b, c = pw[tri[0]], pw[tri[1]], pw[tri[2]]
            n = _normalize(np.cross(b - a, c - a))
            centroid = (a + b + c) / 3.0
            view_dir = _normalize(cam.eye - centroid)
            if np.dot(n, view_dir) < 0:
                n = -n
            ndl = float(np.dot(n, L_KEY))
            col = toon(ndl, part.color, part.shade)
            if part.rim:
                fres = 1.0 - max(0.0, float(np.dot(n, view_dir)))
                if fres > 0.74 and ndl > 0.0:
                    col = np.clip(col + RIM_COL * (fres - 0.74) * 0.95, 0, 1)
            fill = np.clip(col + np.array([0.55, 0.30, 0.16]) * part.emissive, 0, 1)
            cols.append(tuple(int(round(x * 255)) for x in fill))
        for tri, col in zip(faces, cols):
            pts = [((float(uv[i][0]) - x0) * ss, (float(uv[i][1]) - y0) * ss) for i in tri]
            d.polygon(pts, fill=col + (255,))

    mask = tile.split()[3]
    if outline is not None:
        grown = mask.filter(ImageFilter.MaxFilter(int(outline_px * ss) | 1))
        edge = Image.new("RGBA", tile.size, outline + (255,))
        edge.putalpha(grown)
        out = Image.new("RGBA", tile.size, (0, 0, 0, 0))
        out.alpha_composite(edge)
        out.alpha_composite(tile)
        tile = out

    if glow:
        a = tile.split()[3]
        halo = Image.new("RGBA", tile.size, (255, 170, 90, 0))
        halo.putalpha(a.point(lambda v: int(v * 0.55)))
        halo = halo.filter(ImageFilter.GaussianBlur(14 * ss))
        tile = Image.alpha_composite(halo, tile)

    tile = tile.resize((tw, th), Image.LANCZOS)
    return tile, (x0, y0)


def render_model(model, cam, scale=1.0, outline=None, glow=False, outline_px=7):
    """Returns (RGBA layer, alpha mask). Painter's algorithm, back to front."""
    w, h = cam.w, cam.h
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    drawables = []
    for part in model.parts:
        v, f = mesh(part.kind, part.subdiv)
        hom = np.concatenate([v, np.ones((len(v), 1))], 1) @ part.m.T
        pw = hom[:, :3]
        pv = cam.to_view(pw)
        uv, z = cam.project(pv)
        centre_z = pv[:, 2].mean()
        # cheap back-face cull only for convex primitives
        drawables.append((centre_z, part, pw, pv, uv, f))

    drawables.sort(key=lambda t: t[0])            # view z: farther = more negative, so ascending = back to front

    for _, part, pw, pv, uv, faces in drawables:
        colours = []
        for tri in faces:
            a, b, c = pw[tri[0]], pw[tri[1]], pw[tri[2]]
            n = _normalize(np.cross(b - a, c - a))
            centroid = (a + b + c) / 3.0
            view_dir = _normalize(cam.eye - centroid)
            if np.dot(n, view_dir) < 0:
                n = -n
            ndl = float(np.dot(n, L_KEY))
            col = toon(ndl, part.color, part.shade)
            if part.rim:
                fres = 1.0 - max(0.0, float(np.dot(n, view_dir)))
                if fres > 0.74 and ndl > 0.0:
                    col = np.clip(col + RIM_COL * (fres - 0.74) * 0.95, 0, 1)
            fill_col = np.clip(col + np.array([0.55, 0.30, 0.16]) * part.emissive, 0, 1)
            colours.append(tuple(int(round(x * 255)) for x in fill_col))
        for tri, col in zip(faces, colours):
            pts = [(float(uv[i][0]), float(uv[i][1])) for i in tri]
            if max(p[0] for p in pts) < -8 or min(p[0] for p in pts) > w + 8:
                continue
            if max(p[1] for p in pts) < -8 or min(p[1] for p in pts) > h + 8:
                continue
            d.polygon(pts, fill=col + (255,))

    mask = img.split()[3]
    if outline is not None:
        grown = mask.filter(ImageFilter.MaxFilter(outline_px if outline_px % 2 else outline_px + 1))
        edge = Image.new("RGBA", (w, h), outline + (255,))
        edge.putalpha(grown)
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        out.alpha_composite(edge)
        out.alpha_composite(img)
        img = out

    if glow:                                       # emissive bloom, cheap and soft
        a = img.split()[3]
        halo = Image.new("RGBA", (w, h), (255, 170, 90, 0))
        halo.putalpha(a.point(lambda v: int(v * 0.55)))
        halo = halo.filter(ImageFilter.GaussianBlur(18))
        img = Image.alpha_composite(halo, img)

    return img, mask


def place(model, m):
    """Return a copy of `model` with an extra world transform applied to every part."""
    return Model([Part(p.kind, np.asarray(m, float) @ p.m, p.color,
                       emissive=p.emissive, subdiv=p.subdiv, shade=p.shade, rim=p.rim)
                  for p in model.parts])
