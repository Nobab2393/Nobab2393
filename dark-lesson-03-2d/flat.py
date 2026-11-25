"""flat.py — a flat 2D canvas: paper, ink, chunky shapes, nothing that pretends to be 3D.

Everything is drawn at SS× and resized down once per frame, so every edge is smooth
without PIL's missing anti-aliasing. There are no gradients anywhere: light is a shape,
not a falloff.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import deva

W, H = 1080, 1920
SS = 2

# ---- the paper-and-ink palette (warm paper, one ink, four muted colours) ----------
PAPER = (244, 240, 230)
PAPER2 = (236, 230, 217)
PAPER3 = (226, 219, 203)
INK = (44, 40, 37)
INK2 = (84, 77, 70)
CLAY = (196, 100, 63)
CLAY_D = (162, 79, 49)
SAND = (226, 205, 172)
SAND_D = (203, 178, 140)
OLIVE = (110, 124, 91)
OLIVE_D = (86, 99, 71)
SLATE = (74, 107, 114)
SLATE_D = (56, 84, 91)
SKY = (206, 222, 221)
SKY2 = (226, 236, 232)
SUN = (242, 197, 132)
SKIN = (226, 172, 131)
SKIN2 = (200, 145, 106)
SKIN_D = (206, 150, 110)
WHITE = (250, 247, 238)
HAIR = (47, 41, 38)

FONT_DIR = "fonts/"


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def lerp(a, b, k):
    return a + (b - a) * k


def clamp(v, a=0.0, b=1.0):
    return a if v < a else (b if v > b else v)


def seg(a, b, t):
    return clamp((t - a) / (b - a)) if b > a else 1.0


def eio(x):
    x = clamp(x)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def eout(x, p=2.0):
    return 1.0 - (1.0 - clamp(x)) ** p


def ein(x, p=2.0):
    return clamp(x) ** p


class Canvas:
    """A supersampled sheet of paper. All coordinates are final-frame pixels."""

    def __init__(self, w=W, h=H, bg=PAPER):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w * SS, h * SS), bg + (255,))
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self.mirror = None          # mirror every shape about this x (for facing left)

    def _m(self, x):
        return x if self.mirror is None else 2.0 * self.mirror - x

    def _mp(self, pts):
        return [(self._m(x), y) for x, y in pts]

    # ---- primitives -------------------------------------------------------------
    def rect(self, box, fill, outline=None, w=0.0, r=0):
        x0, x1 = self._m(box[0]), self._m(box[2])
        b = [min(x0, x1) * SS, box[1] * SS, max(x0, x1) * SS, box[3] * SS]
        if r:
            self.d.rounded_rectangle(b, r * SS, fill=fill,
                                     outline=outline, width=int(w * SS) if outline else 0)
        else:
            self.d.rectangle(b, fill=fill, outline=outline, width=int(w * SS) if outline else 0)

    def poly(self, pts, fill, outline=None, w=0.0):
        p = [(x * SS, y * SS) for x, y in self._mp(pts)]
        if len(p) < 3:
            return
        self.d.polygon(p, fill=fill)
        if outline:
            self.d.line(p + [p[0]], fill=outline, width=max(1, int(w * SS)), joint="curve")

    def circle(self, x, y, r, fill, outline=None, w=0.0):
        x = self._m(x)
        b = [(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS]
        self.d.ellipse(b, fill=fill, outline=outline, width=max(1, int(w * SS)) if outline else 0)

    def ellipse(self, x, y, rx, ry, fill, outline=None, w=0.0):
        x = self._m(x)
        b = [(x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS]
        self.d.ellipse(b, fill=fill, outline=outline, width=max(1, int(w * SS)) if outline else 0)

    def line(self, pts, fill, w=4.0, caps=True):
        p = [(x * SS, y * SS) for x, y in self._mp(pts)]
        self.d.line(p, fill=fill, width=max(1, int(w * SS)), joint="curve")
        if caps:
            for x, y in (p[0], p[-1]):
                self.d.ellipse([x - w * SS / 2, y - w * SS / 2, x + w * SS / 2, y + w * SS / 2],
                               fill=fill)

    def _stadium(self, p0, p1, r0, r1, fill):
        x0, y0 = p0
        x1, y1 = p1
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1e-6
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        pts = []
        for i in range(17):                                   # cap around p1
            a = math.pi * i / 16
            pts.append((x1 + (nx * math.cos(a) + ux * math.sin(a)) * r1,
                        y1 + (ny * math.cos(a) + uy * math.sin(a)) * r1))
        for i in range(17):                                   # cap around p0
            a = math.pi * i / 16
            pts.append((x0 - (nx * math.cos(a) + ux * math.sin(a)) * r0,
                        y0 - (ny * math.cos(a) + uy * math.sin(a)) * r0))
        self.poly(pts, fill)

    def capsule(self, p0, p1, r0, r1, fill, outline=None, w=0.0):
        """A tapered limb segment with round caps — the whole character vocabulary."""
        p0 = (self._m(p0[0]), p0[1])
        p1 = (self._m(p1[0]), p1[1])
        if outline and w > 0:
            self._stadium(p0, p1, r0 + w, r1 + w, outline)
        self._stadium(p0, p1, r0, r1, fill)

    def taper(self, p0, p1, r0, r1, fill):
        """Filled limb with no outline (used for flat shadow shapes and hoods)."""
        self.capsule(p0, p1, r0, r1, fill)

    def text(self, xy, s, size, weight=700, color=INK, anchor="mm"):
        deva.draw_text(self.img, (xy[0] * SS, xy[1] * SS), s, int(size * SS), weight,
                       color, anchor=anchor)

    def blob_shadow(self, cx, cy, r, fill, squash=0.34):
        self.ellipse(cx, cy, r, r * squash, fill)

    # ---- output -----------------------------------------------------------------
    def finish(self, grain=True, card=False, crop=None):
        im = self.img
        if crop:
            x0, y0, x1, y1 = [v * SS for v in crop]
            im = im.crop((int(x0), int(y0), int(x1), int(y1)))
        im = im.resize((self.w, self.h), Image.LANCZOS)
        if grain:
            im = grain_over(im, 5 if not card else 9)
        return im.convert("RGB")


_grain_cache = {}


def grain_over(img, strength=5, seed=7):
    key = (img.size, strength)
    if key not in _grain_cache:
        rng = np.random.default_rng(seed)
        n = rng.normal(0, strength, (img.height // 2, img.width // 2)).astype(np.float32)
        g = Image.fromarray(np.clip(n + 128, 0, 255).astype(np.uint8)).resize(img.size,
                                                                             Image.BILINEAR)
        _grain_cache[key] = (np.asarray(g, dtype=np.float32) - 128.0)[..., None]
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    a = np.clip(a + _grain_cache[key], 0, 255).astype(np.uint8)
    return Image.fromarray(a)


# ---- shared shapes ------------------------------------------------------------------
def shadow_poly(cx, ground_y, height, lean, width, colour=SAND_D, alpha=150, squash=0.55):
    """A flat shadow cast on the ground plane: a parallelogram, no blur, no gradient."""
    h = height * squash
    tip = (cx + lean * height, ground_y - h * 0.06)
    return [(cx - width / 2, ground_y), (cx + width / 2, ground_y),
            (tip[0] + width * 0.42, tip[1]), (tip[0] - width * 0.42, tip[1])]


def sun(cv, x, y, r, glow=1.0):
    if glow > 0.01:
        cv.circle(x, y, r * 1.9, mix(PAPER, SUN, 0.22 * glow))
        cv.circle(x, y, r * 1.35, mix(PAPER, SUN, 0.42 * glow))
    cv.circle(x, y, r, SUN)


def paper_edge(cv, y, colour=PAPER3, h=6):
    cv.rect([0, y, W, y + h], colour)
