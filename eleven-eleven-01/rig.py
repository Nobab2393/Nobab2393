"""The actors for এগারোটা এগারো — a small two-tone cel rig.

Everything is drawn in *units* (a body is 1000 units tall) and scaled to the frame, so a pose is
written once and the same figure can stand close to camera or far down the park path.

Cel shading is done the cheap way, without masks: every shape is drawn twice — the shadow tone
first, nudged a few pixels toward the dark side, then the base tone on top. What is left showing is
a hard-edged crescent of shadow. Then one ink contour. No gradients, no blur.

A figure is a list of keyframes in shot-relative seconds, sampled with a smoothstep:

    dict(who="anika", x=540, feet=1820, h=760,
         keys=[(0.0, dict(rb=52, phone=1, head=-6)), (2.4, dict(rb=44, head=4))])

Pose knobs: lean, crouch, head (turn), headup, la/lb (arm), ra/rb, walk=(amp, hz), brow (+1
worried … −1 angry), eye (0 shut … 1.25 wide), mouth (−1 … +1), hair (sway), phone (0/1),
scarf (0/1), view="front"/"back".
"""

import math

from PIL import ImageDraw

INK = (14, 12, 14)
SHADOW = (8, 8, 16, 145)


def _sh(col, k=0.84, cool=0.10):
    """One base tone in, one shadow tone out — darker and pushed cool."""
    r, g, b = col
    r, g, b = r * k - 255 * cool * 0.35, g * k, b * k + 255 * cool * 0.5
    return tuple(max(0, min(255, int(v))) for v in (r, g, b))


LOOKS = {
    "anika": dict(skin=(199, 141, 104), hair=(38, 31, 30), hair2=(66, 54, 50),
                  top=(46, 96, 118), leg=(52, 56, 66), shoe=(92, 62, 48),
                  scarf=(176, 62, 56), lip=(158, 88, 86), body="woman"),
    "sabbir": dict(skin=(176, 124, 92), hair=(30, 27, 26), hair2=(52, 47, 44),
                   top=(44, 54, 76), leg=(58, 60, 66), shoe=(40, 36, 34),
                   scarf=None, lip=(124, 82, 78), body="man"),
    "ryan": dict(skin=(186, 133, 98), hair=(36, 31, 28), hair2=(62, 52, 45),
                 top=(124, 94, 50), leg=(64, 66, 74), shoe=(74, 56, 42),
                 scarf=None, lip=(130, 86, 80), body="man"),
}

BASE = dict(lean=0.0, crouch=0.0, head=0.0, headup=0.0, la=6.0, lb=8.0, ra=6.0, rb=8.0,
            brow=0.0, eye=1.0, mouth=0.0, hair=0.0, phone=0.0, scarf=0.0, sit=0.0,
            ik1=0.0, hx1=0.0, hy1=0.0, ik0=0.0, hx0=0.0, hy0=0.0)

R_UPPER, R_FORE = 148.0, 132.0


def two_bone(shoulder, target, r1=R_UPPER, r2=R_FORE, out=1.0):
    """Elbow and hand for a two-bone arm reaching a point in body units (x right, y down).

    Folded arms are the whole reason this exists: a pose like *phone to the ear* cannot be written
    as two angles without guessing, and guessing puts the hand through her chin.
    """
    sx, sy = shoulder
    tx, ty = target
    dx, dy = tx - sx, ty - sy
    d = math.hypot(dx, dy)
    d = max(abs(r1 - r2) + 0.5, min(d, r1 + r2 - 0.5))
    a = math.atan2(dy, dx)
    cos_t = max(-1.0, min(1.0, (r1 * r1 + d * d - r2 * r2) / (2 * r1 * d)))
    theta = math.acos(cos_t)
    # two ways to fold; the elbow goes down and out, never up over her face
    cands = [(sx + math.cos(a + q * theta) * r1, sy + math.sin(a + q * theta) * r1)
             for q in (1, -1)]
    ex, ey = max(cands, key=lambda c: abs(c[0] - sx) * 0.8 + c[1] * 0.2)
    # re-aim the forearm at the target from wherever the elbow landed
    hx, hy = sx + math.cos(a) * d, sy + math.sin(a) * d
    return (ex, ey), (hx, hy)


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def sample(keys, t):
    if not keys:
        return dict(BASE, swing=0.0, bobs=0.0)
    if t <= keys[0][0]:
        return dict(BASE, swing=0.0, bobs=0.0, **keys[0][1])
    if t >= keys[-1][0]:
        return dict(BASE, swing=0.0, bobs=0.0, **keys[-1][1])
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            p0, p1 = dict(BASE, swing=0.0, bobs=0.0, **a), dict(BASE, swing=0.0, bobs=0.0, **b)
            k = ease((t - t0) / max(1e-6, t1 - t0))
            return {n: p0[n] + (p1[n] - p0[n]) * k for n in p0}
    return dict(BASE, swing=0.0, bobs=0.0, **keys[-1][1])


def draw(canvas, spec, t, ink_width=1.0):
    look = LOOKS.get(spec.get("who", "anika"), LOOKS["anika"])
    p = sample(spec.get("keys", []), t)
    x, feet, h = float(spec["x"]), float(spec["feet"]), float(spec["h"])
    s = h / 1000.0
    back = spec.get("view", "front") == "back"
    flip = -1.0 if spec.get("flip") else 1.0
    ph = t + spec.get("seed", 0.0)

    # nothing is ever quite still: breath in the arms, a slow sway in the head
    p["la"] += 1.1 * math.sin(2 * math.pi * 0.30 * ph)
    p["ra"] += 1.1 * math.sin(2 * math.pi * 0.30 * ph + 0.6)
    p["head"] += 1.6 * math.sin(2 * math.pi * 0.16 * ph + 1.2)
    p["headup"] += 0.9 * math.sin(2 * math.pi * 0.11 * ph)
    p["hair"] += 2.4 * math.sin(2 * math.pi * 0.19 * ph + 0.4)
    breath = 3.4 * math.sin(2 * math.pi * 0.32 * ph)

    walk = spec.get("walk")
    if walk:
        amp, hz = walk
        ph2 = 2 * math.pi * hz * t
        p["swing"] = amp * math.sin(ph2)
        p["bobs"] = 6.0 * abs(math.sin(ph2))
        p["la"] += 5.0 * math.sin(ph2 + math.pi)
        p["ra"] += 5.0 * math.sin(ph2)

    ol = max(2, int(round(4.4 * s * ink_width)))
    d = ImageDraw.Draw(canvas)

    def G(dx, dy):
        return (x + dx * s * flip, feet + dy * s)

    crouch = p["crouch"] * 46.0 + p["sit"] * 120.0
    hip_y = -424.0 + crouch + p["bobs"]
    la_rad = math.radians(p["lean"])
    cos_l, sin_l = math.cos(la_rad), math.sin(la_rad)

    def U(dx, dy):
        ry = dy - hip_y
        return (x + (dx * cos_l - ry * sin_l) * s * flip,
                feet + (hip_y + (dx * sin_l + ry * cos_l)) * s)

    def seg(a, b, col, wu, caps=(True, True)):
        """A limb: one ink capsule, the shadow capsule nudged inside it, then the base capsule.
        Round caps mean no ink ring where two segments meet, so a knee reads as one limb."""
        w = max(2, int(wu * s))
        r = w / 2.0
        ends = [q for q, c in zip((a, b), caps) if c]
        for q in ends:
            d.ellipse([q[0] - r - ol, q[1] - r - ol, q[0] + r + ol, q[1] + r + ol], fill=INK)
        d.line([a, b], fill=INK, width=w + 2 * ol, joint="curve")
        dx, dy = 1.5 * ol * flip, 1.1 * ol
        d.line([(a[0] + dx, a[1] + dy), (b[0] + dx, b[1] + dy)], fill=_sh(col), width=w)
        d.line([a, b], fill=col, width=w, joint="curve")
        for q in ends:
            d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=col)

    def poly(pts, col, shift=(0.013, 0.011)):
        dp = (shift[0] * 1000 * s * flip, shift[1] * 1000 * s)
        d.polygon([(q[0] + dp[0], q[1] + dp[1]) for q in pts], fill=_sh(col))
        d.polygon(pts, fill=col)
        d.line(list(pts) + [pts[0]], fill=INK, width=ol, joint="curve")

    sh_y = -742 + breath * 0.35
    hr = 86.0
    tilt = math.radians(p["head"] * 0.28)
    cx, cy = U(0, sh_y - 116 + p["headup"] * 0.8)

    def R(dx, dy):
        return (cx + (dx * math.cos(tilt) - dy * math.sin(tilt)) * s * flip,
                cy + (dx * math.sin(tilt) + dy * math.cos(tilt)) * s)

    # ---- contact shadow
    sw, shd = 205 * s, 30 * s
    d.ellipse((x - sw / 2, feet - shd * 0.35, x + sw / 2, feet + shd * 0.65), fill=SHADOW)

    # ---- legs
    for sign in (-1, 1):
        a = math.radians(sign * p["swing"])
        hp = G(sign * 48, hip_y)
        knee = (hp[0] + math.sin(a) * 192 * s, hp[1] + math.cos(a) * 192 * s)
        kb = math.radians(sign * (p["swing"] * 0.4))
        ankle = (knee[0] + math.sin(kb) * 168 * s, knee[1] + math.cos(kb) * 168 * s)
        seg(hp, knee, look["leg"], 78, caps=(True, False))
        seg(knee, ankle, look["leg"], 66, caps=(False, True))
        fx, fy = ankle[0], feet - 20 * s
        d.rounded_rectangle([fx - 36 * s - ol, fy - 21 * s - ol, fx + 44 * s + ol, fy + 20 * s + ol],
                            radius=20 * s, fill=INK)
        d.rounded_rectangle([fx - 36 * s, fy - 21 * s, fx + 44 * s, fy + 20 * s],
                            radius=17 * s, fill=look["shoe"])

    # ---- hair that falls past the shoulders goes on first, so the body covers it
    if look["body"] == "woman":
        sway = p["hair"] * 0.6
        d.polygon([R(-hr * 1.02, -6), R(-hr * 1.34, 110), R(-hr * 1.22 + sway, 250),
                   R(-16 + sway, 272), R(34 + sway, 252), R(hr * 1.24, 120),
                   R(hr * 1.04, -6)], fill=look["hair"])

    # ---- torso
    if look["body"] == "woman":
        hem = -336 + crouch * 0.3
        body = [U(-76, hem), U(-92, hip_y + 40), U(-104, sh_y + 56), U(-86, sh_y + 4),
                U(86, sh_y + 4), U(104, sh_y + 56), U(92, hip_y + 40), U(76, hem)]
        poly(body, look["top"])
        d.line([U(-80, hem), U(80, hem)], fill=INK, width=ol)
        d.line([U(-2, sh_y + 26), U(-2, hem - 30)], fill=_sh(look["top"], 0.9),
               width=max(2, int(3.0 * s)))
        for i in range(3):
            d.ellipse([U(-7, sh_y + 96 + i * 96), U(3, sh_y + 104 + i * 96)], fill=INK)
    else:
        body = [U(-104, -404), U(-116, sh_y + 60), U(-94, sh_y + 6),
                U(94, sh_y + 6), U(116, sh_y + 60), U(104, -404)]
        poly(body, look["top"])
        d.line([U(0, sh_y + 22), U(0, -420)], fill=_sh(look["top"], 0.88), width=max(2, ol - 1))
        for sign in (-1, 1):
            d.rectangle([U(sign * 62 - 20, sh_y + 62), U(sign * 62 + 20, sh_y + 106)],
                        outline=INK, width=max(2, ol - 2))

    # ---- the red muffler: a band at the throat and a tail over one shoulder
    if look.get("scarf") and p["scarf"] > 0.05:
        tail = [U(-48, sh_y + 22), U(-14, sh_y + 18), U(-24, sh_y + 210), U(-62, sh_y + 204)]
        poly(tail, look["scarf"], shift=(0.010, 0.014))
        band = [U(-66, sh_y + 34), U(66, sh_y + 30), U(58, sh_y - 34), U(-58, sh_y - 30)]
        poly(band, look["scarf"], shift=(0.010, 0.012))

    # ---- arms: either two angles, or a hand target solved by two_bone()
    hands = {}
    for side, ka, kb in ((-1, "la", "lb"), (1, "ra", "rb")):
        sx, sy = side * 96, sh_y + 34
        A = math.radians(side * p[ka] * flip)
        e0 = (sx + math.sin(A) * R_UPPER, sy + math.cos(A) * R_UPPER)
        B = math.radians(side * (p[ka] + p[kb]) * flip)
        h0 = (e0[0] + math.sin(B) * R_FORE, e0[1] + math.cos(B) * R_FORE)

        ik = max(0.0, min(1.0, p["ik1" if side > 0 else "ik0"]))
        if ik > 0.001:
            e1, h1 = two_bone((sx, sy),
                              (p["hx1" if side > 0 else "hx0"], p["hy1" if side > 0 else "hy0"]),
                              out=side * flip)
            elbow = (e0[0] + (e1[0] - e0[0]) * ik, e0[1] + (e1[1] - e0[1]) * ik)
            hand = (h0[0] + (h1[0] - h0[0]) * ik, h0[1] + (h1[1] - h0[1]) * ik)
        else:
            elbow, hand = e0, h0
        seg(U(sx, sy), U(*elbow), look["top"], 58, caps=(True, False))
        seg(U(*elbow), U(*hand), look["skin"], 42, caps=(False, True))
        hx, hy = U(*hand)
        r = 19 * s
        d.ellipse([hx - r - ol, hy - r - ol, hx + r + ol, hy + r + ol], fill=INK)
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=look["skin"])
        hands[side] = (hx, hy, r)

    # ---- neck and head
    poly([U(-29, sh_y + 18), U(29, sh_y + 18), U(24, sh_y - 48), U(-24, sh_y - 48)],
         _sh(look["skin"], 0.94))

    d.ellipse([cx - hr * s - ol, cy - hr * s - ol, cx + hr * s + ol, cy + hr * s + ol], fill=INK)
    d.ellipse([cx - hr * s, cy - hr * s, cx + hr * s, cy + hr * s], fill=look["skin"])
    # the shadow crescent along the jaw, on the dark side
    d.chord([cx - hr * s * 0.98, cy - hr * s * 0.98, cx + hr * s * 0.98, cy + hr * s * 0.98],
            46, 150, fill=_sh(look["skin"], 0.9))

    if back:
        poly([R(-hr * 0.99, 40), R(-hr * 1.0, -30), R(-58, -92), R(0, -102), R(58, -92),
              R(hr * 1.0, -30), R(hr * 0.99, 40), R(40, 54), R(-40, 54)],
             look["hair"], shift=(0.006, 0.006))
    else:
        for sign in (-1, 1):
            ex, ey = R(sign * (hr - 2), 18)
            d.ellipse([ex - 13 * s, ey - 19 * s, ex + 13 * s, ey + 19 * s],
                      fill=_sh(look["skin"], 0.94), outline=INK, width=max(2, ol - 1))

        # hair: a cap with a side sweep, and a fringe that comes down over one brow
        cap = [R(-hr * 0.99, -6), R(-82, -80), R(-22, -104), R(42, -98), R(92, -68),
               R(hr * 0.99, -2), R(58, -30), R(16, -52), R(-50, -34)]
        poly(cap, look["hair"], shift=(0.007, 0.009))
        d.line([R(-52, 16), R(-20, -34), R(22, -62)], fill=look["hair2"], width=max(2, int(3.4 * s)))
        # brows — the whole performance lives here
        for sign in (-1, 1):
            inner = R(sign * 12, -4 - p["brow"] * 12)
            outer = R(sign * 58, 0 + p["brow"] * 5)
            d.line([inner, outer], fill=look["hair"], width=max(4, int(7.0 * s)))

        # eyes: a dark almond, a lid that comes down, one cold glint
        eye = max(0.0, min(1.25, p["eye"]))
        for sign in (-1, 1):
            ox, oy = R(sign * 34, 24)
            w_, h_ = 23 * s, 13 * s * eye
            if eye > 0.12:
                d.ellipse([ox - w_, oy - h_, ox + w_, oy + h_], fill=(22, 20, 24))
                d.ellipse([ox - 6 * s, oy - h_ * 0.4, ox + 1 * s, oy + h_ * 0.2],
                          fill=(224, 232, 238))
            d.line([R(sign * 10, 22 - 11 * eye), R(sign * 58, 21 - 10 * eye)],
                   fill=INK, width=max(2, int(3.2 * s)))
            if look["body"] == "woman":
                d.line([R(sign * 58, 21 - 10 * eye), R(sign * 68, 13 - 10 * eye)],
                       fill=INK, width=max(2, int(2.8 * s)))

        # nose and mouth
        nx, ny = R(3, 56)
        d.line([(nx, ny), (nx + 6 * s * flip, ny + 15 * s)], fill=_sh(look["skin"], 0.58),
               width=max(2, int(3.2 * s)))
        m = max(-1.0, min(1.0, p["mouth"]))
        d.line([R(-20, 80), R(0, 82 + 4 - m * 6), R(20, 80)], fill=look["lip"],
               width=max(3, int(4.6 * s)), joint="curve")

    # ---- the phone, last of all, so the hand and her jaw cannot swallow it
    if p["phone"] > 0.5:
        hx, hy, r = hands[1]
        pw, phh = 34 * s, 58 * s
        bx0, by0 = hx - pw * 0.30, hy - phh * 0.86
        d.rounded_rectangle([bx0 - ol, by0 - ol, bx0 + pw + ol, by0 + phh + ol],
                            radius=7 * s, fill=INK)
        d.rounded_rectangle([bx0, by0, bx0 + pw, by0 + phh], radius=5 * s, fill=(14, 18, 28))
        d.rounded_rectangle([bx0 + 3 * s, by0 + 4 * s, bx0 + pw - 3 * s, by0 + phh - 10 * s],
                            radius=3 * s, fill=(158, 212, 230))
