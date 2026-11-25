"""cast2.py — a cast built on shape language and a fixed set of dials, not one template recoloured.

Every character is the same skeleton, but the design is a set of dials that must stay constant:
head shape, head-count, shoulder : hip ratio, limb thickness, posture, silhouette prop, accent
colour, and a face module. Height is real metres; head-count is derived from head diameter, so the
proportion dial is honest (a 4.2-head figure is actually 4.2 heads tall).

    round   -> AYAN   narrow shoulders, scarf, upright, 4.6 heads
    square  -> RAFIQ  flat-top head, wide shoulders, thick forearms, heavy boots, 5.4 heads
    hood    -> MIRA   pointed hood, small shoulders, satchel, slouched, 4.2 heads

Coordinates are metres, y up-positive, feet at y = 0.
"""
import math
from PIL import Image, ImageDraw

INK = (26, 27, 31)
PAPER = (250, 248, 242)

SPEC = {
    "ayan": dict(
        name="AYAN", role="hero", shape="circle",
        H=1.52, heads=4.6,
        head_shape="round", head_w=1.00, head_h=1.00,
        shoulder=0.145, hipw=0.085, hipf=0.475, waist=0.80,
        thick=0.0205, armr=1.00, legr=1.00, hands="fist", boots=False,
        prop="scarf", accent=(48, 122, 132), face_default="determined",
    ),
    "rafiq": dict(
        name="RAFIQ", role="bully", shape="square",
        H=1.72, heads=5.4,
        head_shape="flat", head_w=1.02, head_h=0.96,
        shoulder=0.205, hipw=0.125, hipf=0.455, waist=0.99,
        thick=0.0265, armr=1.30, legr=1.15, hands="fist", boots=True,
        prop="band", accent=(176, 62, 40), face_default="angry",
    ),
    "mira": dict(
        name="MIRA", role="witness", shape="triangle",
        H=1.30, heads=4.2,
        head_shape="hood", head_w=0.97, head_h=1.05,
        shoulder=0.118, hipw=0.070, hipf=0.495, waist=1.30,
        thick=0.0158, armr=0.80, legr=0.86, hands="point", boots=False,
        prop="satchel", accent=(206, 158, 62), face_default="surprised",
    ),
}

A_POSE = dict(lean=0, hipdx=0, hipdy=0, head=0,
              l1=-9, l2=7, r1=9, r2=-7, a1=-34, a2=10, b1=34, b2=-10)
GUARD = dict(lean=6, hipdx=0.02, hipdy=0.03, head=-2,
             l1=-16, l2=12, r1=14, r2=-12, a1=14, a2=76, b1=48, b2=98)


def pose(**kw):
    p = dict(A_POSE)
    p.update(kw)
    return p


def pt(x, y, a, L):
    """a = degrees from straight down (limbs hang), positive toward +x. World is y-up."""
    r = math.radians(a)
    return x + math.sin(r) * L, y - math.cos(r) * L


class Rig:
    def __init__(self, spec):
        self.s = spec
        self.H = spec["H"]
        self.r = self.H / (2.0 * spec["heads"])          # head radius, derives the head-count

    # ---------------------------------------------------------------- geometry
    def joints(self, p):
        s, H, r = self.s, self.H, self.r
        face = s.get("face", 1)
        x0 = s.get("x", 0.0)
        y0 = s.get("y", 0.0)

        hip = (x0 + p["hipdx"] * H * face, y0 + s["hipf"] * H + p["hipdy"] * H)
        lean = math.radians(p["lean"] * face)
        neck_y = H - 2.0 * r * 1.02
        spine = max(0.05, neck_y - s["hipf"] * H)
        neck = (hip[0] + math.sin(lean) * spine, hip[1] + math.cos(lean) * spine)
        chest = (hip[0] + math.sin(lean) * spine * 0.72, hip[1] + math.cos(lean) * spine * 0.72)
        hang = lean + math.radians(p["head"] * face)
        head = (neck[0] + math.sin(hang) * r * 1.02, neck[1] + math.cos(hang) * r * 1.02)

        shw = s["shoulder"] * H * face
        shy = neck[1] - 0.055 * H
        sh_l = (chest[0] - shw * 0.5, shy)
        sh_r = (chest[0] + shw * 0.5, shy)

        up, fo = 0.175 * H, 0.165 * H

        def limb(a1, a2, o, l1, l2):
            m = pt(o[0], o[1], a1 * face, l1)
            return m, pt(m[0], m[1], (a1 + a2) * face, l2)

        el_l, hd_l = limb(p["a1"], p["a2"], sh_l, up, fo)
        el_r, hd_r = limb(p["b1"], p["b2"], sh_r, up, fo)
        th, sn = s["hipf"] * H * 0.53, s["hipf"] * H * 0.47
        kn_l, ft_l = limb(p["l1"], p["l2"], (hip[0] - 0.028 * H * face, hip[1]), th, sn)
        kn_r, ft_r = limb(p["r1"], p["r2"], (hip[0] + 0.028 * H * face, hip[1]), th, sn)
        return dict(hip=hip, chest=chest, neck=neck, head=head, sh_l=sh_l, sh_r=sh_r,
                    el_l=el_l, hd_l=hd_l, el_r=el_r, hd_r=hd_r,
                    kn_l=kn_l, ft_l=ft_l, kn_r=kn_r, ft_r=ft_r, lean=lean, hang=hang,
                    hipw=s["hipw"] * H * face, shw=shw, r=r)

    # ---------------------------------------------------------------- drawing
    def draw(self, d, p, M, t=0.0, flat=None, face=None):
        s, H = self.s, self.H
        J = self.joints(p)
        Mf, pxm = M
        col = flat if flat else INK
        w = s["thick"] * H * pxm                    # base stroke, in canvas px

        def line(a, b, ww, cap=True):
            A, B = Mf(a), Mf(b)
            d.line([A, B], fill=col, width=max(1, int(round(ww))))
            if cap:
                rr = ww / 2
                for q in (A, B):
                    d.ellipse([q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr], fill=col)

        for kn, ft in ((J["kn_l"], J["ft_l"]), (J["kn_r"], J["ft_r"])):
            line(J["hip"], kn, w * s["legr"])
            line(kn, ft, w * s["legr"] * 0.94)
            if s["boots"]:
                a = math.atan2(ft[0] - kn[0], ft[1] - kn[1])
                tip = (ft[0] + math.sin(a) * 0.10 * H, ft[1] - 0.015 * H)
                line(ft, tip, w * s["legr"] * 1.30)
        # neck: without it the head reads as detached, hovering over the shoulders
        line((J["neck"][0], J["neck"][1] + J["r"] * 0.25),
             (J["neck"][0], J["sh_l"][1] + 0.012 * H), w * 0.78)
        self._torso(d, J, Mf, col, w)
        for a, b, k in ((J["sh_l"], J["el_l"], 1.0), (J["el_l"], J["hd_l"], 0.94),
                        (J["sh_r"], J["el_r"], 1.0), (J["el_r"], J["hd_r"], 0.94)):
            line(a, b, w * s["armr"] * k)
        for h, e in ((J["hd_l"], J["el_l"]), (J["hd_r"], J["el_r"])):
            self._hand(d, h, e, Mf, pxm, col, w)
        self._head(d, J, Mf, pxm, col, w, face if face is not None else s["face_default"],
                   flat=bool(flat))
        if not flat:
            self._props(d, J, Mf, pxm, t)

    # ---- pieces
    def _torso(self, d, J, Mf, col, w):
        """The torso is the main carrier of shape language: shoulders, waist, hips."""
        s, H = self.s, self.H
        hip, chest = J["hip"], J["chest"]
        top = J["sh_l"][1]
        shw = J["shw"] * 0.5
        hipw = J["hipw"] * 0.5
        waist = shw * s.get("waist", 1.0)
        wy = top + (hip[1] - top) * 0.58
        pts = [(chest[0] - shw, top),
               (chest[0] - waist, wy),
               (hip[0] - hipw, hip[1]),
               (hip[0] + hipw, hip[1]),
               (chest[0] + waist, wy),
               (chest[0] + shw, top)]
        d.polygon([Mf(q) for q in pts], fill=col)
        for q in pts[:1] + pts[5:]:
            c = Mf(q)
            rr = w * 0.70
            d.ellipse([c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr], fill=col)
        c = Mf(J["hip"])
        rr = w * 0.55
        d.ellipse([c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr], fill=col)

    def _hand(self, d, h, e, Mf, pxm, col, w):
        style = self.s["hands"]
        dx, dy = h[0] - e[0], h[1] - e[1]
        L = math.hypot(dx, dy) or 1.0
        a = math.atan2(dx, dy)
        if style == "fist":
            c = Mf(h)
            rr = 0.020 * self.H * pxm
            d.ellipse([c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr], fill=col)
        elif style == "point":
            tip = (h[0] + dx / L * 0.035 * self.H, h[1] + dy / L * 0.035 * self.H)
            d.line([Mf(h), Mf(tip)], fill=col, width=max(1, int(w * 0.55)))
        else:                                     # mitt, for the heavy
            c = Mf(h)
            rr = 0.021 * self.H * pxm
            d.ellipse([c[0] - rr * 0.9, c[1] - rr, c[0] + rr * 1.1, c[1] + rr * 0.9], fill=col)

    def _head(self, d, J, Mf, pxm, col, w, expr, flat=False):
        s = self.s
        c = Mf(J["head"])
        r = J["r"] * pxm
        hw, hh = s["head_w"], s["head_h"]
        shape = s["head_shape"]
        if shape == "round":
            d.ellipse([c[0] - r * hw, c[1] - r * hh, c[0] + r * hw, c[1] + r * hh],
                      outline=col, width=max(2, int(w * 1.05)))
        elif shape == "flat":
            d.rounded_rectangle([c[0] - r * hw, c[1] - r * hh, c[0] + r * hw, c[1] + r * hh],
                                radius=int(r * 0.36), outline=col, width=max(2, int(w * 1.10)))
            d.line([(c[0] - r * hw * 0.98, c[1] - r * hh * 0.80), (c[0] + r * hw * 0.98, c[1] - r * hh * 0.80)],
                   fill=col, width=max(2, int(w * 0.80)))
        else:                                     # hood
            d.polygon([(c[0], c[1] - r * hh * 1.18),
                       (c[0] + r * hw, c[1] + r * hh * 0.66),
                       (c[0] - r * hw, c[1] + r * hh * 0.66)],
                      outline=col, width=max(2, int(w * 1.05)))
        if flat:
            return
        self._face(d, c, r * min(hw, hh), expr)

    # expression table: (inner-brow lift, brow raise, eye opening, mouth)
    FACE = {
        "neutral":    (0.00, 0.00, 0.90, "flat"),
        "determined": (-0.18, -0.05, 0.72, "slant"),
        "angry":      (-0.42, -0.12, 0.55, "slant"),
        "surprised":  (0.10, 0.40, 1.55, "small_o"),
        "sad":        (0.48, 0.05, 0.85, "frown"),
        "happy":      (0.26, 0.22, 0.85, "smile"),
        "tired":      (0.30, 0.16, 0.40, "flat"),
        "profile":    (0.00, 0.00, 0.90, "flat"),
    }

    def _face(self, d, c, r, expr, k=1.0):
        """Brows and eyes do the acting; the mouth confirms. Everything is a fraction of r."""
        if expr == "none":
            return
        col = INK
        lift, raise_, op, mouth = self.FACE.get(expr, self.FACE["neutral"])
        mw = max(2, int(r * 0.10))
        dx = r * 0.36 * k
        ey = -r * 0.10 * k
        e = r * 0.19 * k * op
        ex_ = r * 0.125 * k * (1.15 if expr == "surprised" else 1.0)

        if expr == "profile":
            x = c[0] + dx * 0.85
            d.ellipse([x - ex_, c[1] + ey - e, x + ex_, c[1] + ey + e], fill=col)
            d.line([(x - ex_, c[1] + ey - e * 2.0), (x + ex_ * 1.4, c[1] + ey - e * 2.2)],
                   fill=col, width=mw)
            d.line([(c[0] + dx * 1.05, c[1] + ey - r * 0.02), (c[0] + dx * 1.28, c[1] + ey + r * 0.20)],
                   fill=col, width=mw)
            d.line([(c[0] + dx * 0.20, c[1] + r * 0.42), (c[0] + dx * 0.80, c[1] + r * 0.40)],
                   fill=col, width=mw)
            return

        for sx in (-1, 1):
            x = c[0] + sx * dx
            d.ellipse([x - ex_, c[1] + ey - e, x + ex_, c[1] + ey + e], fill=col)
            if expr in ("tired", "angry"):          # a lid cutting the top of the eye
                lid = e * (0.45 if expr == "tired" else 0.22)
                d.rectangle([x - ex_ - 2, c[1] + ey - e - 1, x + ex_ + 2, c[1] + ey - e + lid], fill=PAPER)

        by = c[1] + ey - e - r * 0.20 * k - raise_ * r * 0.26
        for sx in (-1, 1):
            xi = c[0] + sx * (dx - ex_ * 1.25)        # inner end
            xo = c[0] + sx * (dx + ex_ * 1.35)        # outer end
            # canvas y grows downward: a raised inner end is a *smaller* y
            d.line([(xi, by - lift * r * 0.30), (xo, by + lift * r * 0.08)],
                   fill=col, width=mw)

        my = c[1] + r * 0.44
        mr = r * 0.22
        if mouth == "slant":
            d.line([(c[0] - mr, my + mr * 0.34), (c[0] + mr * 0.85, my - mr * 0.10)], fill=col,
                   width=max(2, int(mw * 1.15)))
        elif mouth == "small_o":
            d.ellipse([c[0] - mr * 0.42, my - mr * 0.25, c[0] + mr * 0.42, my + mr * 0.75],
                      outline=col, width=mw)
        elif mouth == "frown":
            d.arc([c[0] - mr, my - mr * 0.55, c[0] + mr, my + mr * 0.95], 195, 345, fill=col, width=mw)
        elif mouth == "smile":
            d.arc([c[0] - mr, my - mr * 0.85, c[0] + mr, my + mr * 0.70], 15, 165, fill=col, width=mw)
        else:
            d.line([(c[0] - mr * 0.72, my), (c[0] + mr * 0.72, my)], fill=col, width=mw)

    def _props(self, d, J, Mf, pxm, t):
        s, H = self.s, self.H
        prop = s.get("prop")
        if prop == "scarf":
            col = s["accent"]
            a = (J["neck"][0] + 0.01 * H, J["neck"][1] + 0.015 * H)
            tail = [a]
            for i in range(1, 10):
                k = i / 9.0
                tail.append((a[0] + (0.05 + 0.30 * k) * H,
                             a[1] - (0.02 + 0.16 * k + 0.018 * math.sin(t * 2.0 + k * 3.6)) * H))
            d.line([Mf(q) for q in tail], fill=col, width=max(2, int(0.030 * H * pxm)), joint="curve")
            c = Mf(a)
            rr = 0.028 * H * pxm
            d.ellipse([c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr], fill=col)
        elif prop == "band":
            a, b = J["el_r"], J["hd_r"]
            c = Mf((a[0] * 0.30 + b[0] * 0.70, a[1] * 0.30 + b[1] * 0.70))
            rr = 0.021 * H * pxm
            d.ellipse([c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr], fill=s["accent"])
        elif prop == "satchel":
            col = s["accent"]
            a, b = J["sh_l"], (J["hip"][0] + 0.02 * H, J["hip"][1] - 0.01 * H)
            d.line([Mf(a), Mf(b)], fill=col, width=max(2, int(0.017 * H * pxm)))
            c = Mf((J["hip"][0] + 0.085 * H, J["hip"][1] - 0.015 * H))
            hw, hh = 0.062 * H * pxm, 0.048 * H * pxm
            d.rounded_rectangle([c[0] - hw, c[1] - hh, c[0] + hw, c[1] + hh],
                                radius=int(0.014 * H * pxm), fill=col)


CAST = SPEC
EXPRESSIONS = ["neutral", "determined", "angry", "surprised", "sad", "happy", "tired", "none"]
