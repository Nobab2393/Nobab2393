"""craft.py — flat motion-graphics canvas for the Vice City trailer.

Same frame contract as the rest of this repo: every frame is a pure function of t,
2x supersample for clean edges, flat planes only, one neon accent family.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
SS = 2

# ---- night palette: no pure black, no pure white -----------------------------------
BG = (14, 12, 18)          # #0E0C12
CITY = (27, 23, 38)        # one step up: far skyline
CITY2 = (44, 36, 60)       # near skyline
CREAM = (244, 239, 228)    # ink
MUTED = (150, 138, 160)    # meta text
PINK = (255, 61, 139)      # accent: neon
PINK_D = (172, 32, 92)
CYAN = (69, 216, 232)      # counterweight
AMBER = (255, 181, 74)     # the sun
VIOLET = (122, 30, 92)     # sky band

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
_fc = {}


def clamp(v, a=0.0, b=1.0):
    return a if v < a else (b if v > b else v)


def seg(a, b, t):
    return clamp((t - a) / (b - a)) if b > a else 1.0


def back(t, s=1.70158):
    t = clamp(t) - 1.0
    return t * t * ((s + 1) * t + s) + 1.0


def snap(t):
    t = clamp(t)
    return 3 * t * t - 2 * t * t * t


def expo(t):
    t = clamp(t)
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)


def lerp(a, b, k):
    return a + (b - a) * k


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def font(size, mono=False):
    key = (size, mono)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(FONT_M if mono else FONT_B, int(size))
    return _fc[key]


class Canvas:
    def __init__(self, bg=BG):
        # RGB base + RGBA draw mode: PIL then BLENDS alpha fills instead of replacing
        # the pixel, which is what makes rain, scanlines, vignettes and flashes work.
        self.img = Image.new("RGB", (W * SS, H * SS), bg)
        self.d = ImageDraw.Draw(self.img, "RGBA")

    # ---- primitives ---------------------------------------------------------------
    def rect(self, box, fill, r=0):
        b = [box[0] * SS, box[1] * SS, box[2] * SS, box[3] * SS]
        if r:
            self.d.rounded_rectangle(b, r * SS, fill=fill)
        else:
            self.d.rectangle(b, fill=fill)

    def poly(self, pts, fill):
        if len(pts) < 3:
            return
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)

    def circle(self, x, y, r, fill):
        self.d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=fill)

    def ring(self, x, y, r, w, fill):
        self.d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS],
                       outline=fill, width=max(1, int(w * SS)))

    def line(self, pts, fill, w=4, caps=True):
        p = [(x * SS, y * SS) for x, y in pts]
        self.d.line(p, fill=fill, width=max(1, int(w * SS)), joint="curve")
        if caps:
            for x, y in (p[0], p[-1]):
                self.d.ellipse([x - w * SS / 2, y - w * SS / 2, x + w * SS / 2, y + w * SS / 2],
                               fill=fill)

    # ---- type ---------------------------------------------------------------------
    def text(self, xy, s, size, fill, tracking=0.0, anchor="mm", mono=False, alpha=1.0):
        """Letter-spaced caps, drawn as one string per letter — no per-glyph animation."""
        if alpha <= 0.02 or not s:
            return 0
        f = font(size * SS, mono)
        track = tracking * size * SS
        widths = [f.getlength(ch) for ch in s]
        total = sum(widths) + track * (len(s) - 1)
        x, y = xy[0] * SS, xy[1] * SS
        if anchor[0] == "m":
            x -= total / 2
        elif anchor[0] == "r":
            x -= total
        col = fill + (int(255 * clamp(alpha)),)
        for ch, w in zip(s, widths):
            self.d.text((x, y), ch, font=f, fill=col, anchor="lm")
            x += w + track
        return total / SS

    def glow_text(self, xy, s, size, fill, halo=PINK, tracking=0.0, anchor="mm", k=1.0):
        """Neon: two flat halos and the core — no blur, so it stays graphic."""
        if k <= 0.02:
            return
        # the halo is the SAME text stamped around the glyphs, never a scaled copy:
        # scaling shifted every letter against the core and fused the words into blobs.
        for r, a in ((7, 0.10), (5, 0.14), (3, 0.20), (1.5, 0.26)):
            for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
                self.text((xy[0] + dx / SS, xy[1] + dy / SS), s, size, halo, tracking,
                          anchor, alpha=a * k)
        self.text(xy, s, size, fill, tracking, anchor, alpha=k)

    # ---- output -------------------------------------------------------------------
    def finish(self, grain=4, crop=None):
        im = self.img
        if crop:
            im = im.crop([int(v * SS) for v in crop])
        im = im.resize((W, H), Image.LANCZOS)
        if grain:
            im = self._grain(im, grain)
        return im if im.mode == "RGB" else im.convert("RGB")

    _g = {}

    def _grain(self, img, strength):
        if img.size not in self._g:
            rng = np.random.default_rng(11)
            n = rng.normal(0, strength, (img.height // 2, img.width // 2)).astype(np.float32)
            g = Image.fromarray(np.clip(n + 128, 0, 255).astype(np.uint8)).resize(
                img.size, Image.BILINEAR)
            self._g[img.size] = (np.asarray(g, dtype=np.float32) - 128.0)[..., None]
        a = np.clip(np.asarray(img, dtype=np.float32) + self._g[img.size],
                    0, 255).astype(np.uint8)
        return Image.fromarray(a)


# ---- shared scenery -----------------------------------------------------------------
def scanlines(cv, alpha=26, gap=6):
    for y in range(0, H, gap):
        cv.rect([0, y, W, y + 2], (0, 0, 0, alpha))


def vignette(cv, strength=0.55):
    """Flat corner wedges rather than a blur — the cheap, graphic way to darken edges."""
    for i in range(9):
        a = int(20 * strength * (1 - i / 9))
        cv.rect([0, i * 26, W, i * 26 + 26], (0, 0, 0, a))
        cv.rect([0, H - (i + 1) * 26, W, H - i * 26], (0, 0, 0, a))
