"""2D character rig: flat-vector Bengali characters with a real skeleton.

Local space: origin at the hip centre, +x = facing direction, +y = down.
All lengths are fractions of `height` (P).
"""
import math
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFilter

SS = 2  # supersample factor for character layers


# --------------------------------------------------------------------------- utils
def lerp(a, b, t):
    return a + (b - a) * t


def vlerp(p, q, t):
    return (lerp(p[0], q[0], t), lerp(p[1], q[1], t))


def add(p, q, k=1.0):
    return (p[0] + q[0] * k, p[1] + q[1] * k)


def sub(p, q):
    return (p[0] - q[0], p[1] - q[1])


def norm(p):
    d = math.hypot(*p) or 1e-6
    return (p[0] / d, p[1] / d)


def rot(p, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def clamp01(v):
    return 0.0 if v < 0 else (1.0 if v > 1 else v)


def smoothstep(a, b, x):
    if a == b:
        return 1.0 if x >= b else 0.0
    t = clamp01((x - a) / (b - a))
    return t * t * (3 - 2 * t)


def ik2(root, target, l1, l2, bend=1.0):
    """Two-bone IK -> middle joint. bend=+1 / -1 selects the elbow side."""
    d = dist(root, target)
    d = max(1e-3, min(d, (l1 + l2) * 0.999))
    u = norm(sub(target, root))
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    mid = add(root, u, a)
    perp = (-u[1], u[0])
    return add(mid, perp, h * bend)


# --------------------------------------------------------------------------- palette
@dataclass
class Palette:
    skin: tuple = (198, 141, 96)
    skin_d: tuple = (168, 114, 76)
    hair: tuple = (34, 26, 28)
    top: tuple = (176, 32, 48)
    top_d: tuple = (140, 24, 38)
    top_l: tuple = (204, 60, 72)
    pants: tuple = (58, 48, 62)
    shoe: tuple = (44, 34, 30)
    accent: tuple = (226, 176, 74)
    accent_d: tuple = (182, 134, 48)
    prop: tuple = (110, 74, 50)
    eye: tuple = (46, 34, 30)
    outline: tuple = (26, 20, 28)


@dataclass
class Character:
    key: str
    pal: Palette
    height: float = 700.0
    female: bool = False
    beard: bool = False
    moustache: bool = False
    crown: bool = False
    turban: bool = False
    glasses: bool = False
    bun: bool = False
    shawl: bool = False
    saree: bool = False
    belt: bool = False
    long_coat: bool = False
    tie: bool = False
    briefcase: bool = False
    backpack: bool = False
    notebook: bool = False
    # proportions (fraction of height)
    head_r: float = 0.076
    head_w: float = 1.0
    torso_len: float = 0.280
    thigh: float = 0.230
    shin: float = 0.200
    ankle: float = 0.042
    upper_arm: float = 0.150
    fore_arm: float = 0.140
    shoulder_x: float = 0.070     # half shoulder width at the joint
    shoulder_y: float = 0.245     # below the neck base, torso is 0.28
    hip_x: float = 0.032
    coat_len: float = 0.165


CHARACTERS = {
    "king": Character("king", Palette(skin=(196, 139, 94), skin_d=(162, 108, 70),
                                       hair=(30, 22, 24), top=(178, 34, 48), top_d=(126, 18, 32),
                                       top_l=(208, 62, 74), pants=(70, 44, 46), shoe=(62, 42, 30),
                                       accent=(234, 190, 90), accent_d=(184, 138, 52)),
                      beard=True, crown=True, long_coat=True, belt=True, head_w=0.95),
    "rival": Character("rival", Palette(skin=(184, 130, 90), skin_d=(148, 98, 66),
                                        hair=(28, 22, 24), top=(74, 76, 86), top_d=(50, 52, 60),
                                        top_l=(100, 102, 112), pants=(56, 58, 66), shoe=(30, 30, 34),
                                        accent=(146, 148, 158), accent_d=(104, 106, 114)),
                       moustache=True, shawl=True, long_coat=True, belt=True),
    "boss": Character("boss", Palette(skin=(200, 143, 100), skin_d=(166, 114, 76),
                                      hair=(32, 26, 28), top=(38, 62, 112), top_d=(24, 42, 84),
                                      top_l=(54, 82, 136), pants=(36, 58, 106), shoe=(28, 26, 30),
                                      accent=(150, 34, 46), accent_d=(112, 24, 34)),
                      moustache=True, tie=True, briefcase=True),
    "student": Character("student", Palette(skin=(198, 140, 98), skin_d=(164, 110, 72),
                                            hair=(30, 24, 26), top=(238, 240, 244), top_d=(198, 203, 212),
                                            top_l=(252, 253, 255), pants=(46, 82, 126), shoe=(236, 238, 242),
                                            accent=(58, 96, 146), accent_d=(38, 70, 114)),
                         glasses=True, backpack=True, notebook=True, height=672),
    "mentor": Character("mentor", Palette(skin=(196, 138, 96), skin_d=(162, 108, 70),
                                          hair=(116, 112, 116), top=(26, 112, 82), top_d=(16, 82, 60),
                                          top_l=(42, 136, 102), pants=(26, 112, 82), shoe=(84, 52, 36),
                                          accent=(214, 172, 74), accent_d=(170, 132, 48)),
                         female=True, bun=True, glasses=True, saree=True, height=672,
                         head_r=0.073, head_w=0.94),
}


# --------------------------------------------------------------------------- canvas
class Layer:
    """Supersampled RGBA canvas; local origin is the character's hip."""

    def __init__(self, w, h, origin, P):
        self.P = P
        self.img = Image.new("RGBA", (int(w * SS), int(h * SS)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.origin = origin

    def xy(self, p):
        return ((p[0] + self.origin[0]) * SS, (p[1] + self.origin[1]) * SS)

    def _cap(self, p1, p2, w1, w2, fill):
        a, b = self.xy(p1), self.xy(p2)
        u = norm((b[0] - a[0], b[1] - a[1]))
        n = (-u[1], u[0])
        w1, w2 = w1 * SS, w2 * SS
        poly = [add(a, n, w1 / 2), add(b, n, w2 / 2), add(b, n, -w2 / 2), add(a, n, -w1 / 2)]
        self.d.ellipse([a[0] - w1 / 2, a[1] - w1 / 2, a[0] + w1 / 2, a[1] + w1 / 2], fill=fill)
        self.d.ellipse([b[0] - w2 / 2, b[1] - w2 / 2, b[0] + w2 / 2, b[1] + w2 / 2], fill=fill)
        self.d.polygon(poly, fill=fill)

    def capsule(self, p1, p2, w1, w2, fill, outline=None, ow=0.0):
        if outline and ow:
            self._cap(p1, p2, w1 + 2 * ow, w2 + 2 * ow, outline)
        self._cap(p1, p2, w1, w2, fill)

    def poly(self, pts, fill, outline=None, ow=0.0):
        p = [self.xy(q) for q in pts]
        if outline and ow:
            self.d.polygon(p, fill=fill, outline=outline, width=max(1, int(ow * SS)))
        else:
            self.d.polygon(p, fill=fill)

    def blob(self, pts, fill, outline=None, ow=0.0, closed=True):
        dense = []
        n = len(pts)
        for i in range(n):
            p0, p1, p2, p3 = pts[(i - 1) % n], pts[i % n], pts[(i + 1) % n], pts[(i + 2) % n]
            for s in range(6):
                t = s / 6
                t2, t3 = t * t, t * t * t
                x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                           (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                           (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                           (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                           (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
                dense.append((x, y))
        self.poly(dense, fill, outline, ow)

    def ellipse(self, c, rx, ry, fill, outline=None, ow=0.0):
        x, y = self.xy(c)
        box = [x - rx * SS, y - ry * SS, x + rx * SS, y + ry * SS]
        if outline and ow:
            self.d.ellipse(box, fill=fill, outline=outline, width=max(1, int(ow * SS)))
        else:
            self.d.ellipse(box, fill=fill)

    def line(self, pts, fill, w, joint="curve"):
        self.d.line([self.xy(p) for p in pts], fill=fill, width=max(1, int(w * SS)), joint=joint)

    def finish(self, scale):
        w = max(1, int(self.img.width / SS * scale))
        h = max(1, int(self.img.height / SS * scale))
        return self.img.resize((w, h), Image.LANCZOS)
