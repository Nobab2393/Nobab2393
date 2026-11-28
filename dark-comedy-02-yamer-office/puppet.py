"""A small vector rig for the people in যমের অফিস.

The plates are painted rooms; the people in them are drawn here, frame by frame, so they can act:
breathe, turn a head, put a file through a window, take a pair of glasses off, walk away down a
corridor. Same paper as the cast cards — flat pastel fills, one thick dark outline, dot eyes — so a
figure standing in a painted office still looks cut from the same sheet.

Every actor is a list of keyframes in *shot-relative* seconds:

    dict(who="habib", x=676, feet=2260, h=1180, view="back",
         keys=[(0.0, dict(la=6)), (1.4, dict(la=46, head=-8)), (2.6, dict(la=6))])

`draw()` samples the two neighbouring keys with a smooth ease, adds the breathing and the head
sway, and draws the figure straight onto the master canvas.

Units: the body is 1000 units tall whatever `h` says, so poses are written once and every actor
can be any size. y runs from the feet (0) upwards (negative).
"""

import math

from PIL import ImageDraw

INK = (21, 20, 19)
SHADOW = (150, 146, 138, 44)

LOOK = {
    "habib": dict(skin=(206, 152, 113), hair=(158, 155, 150), crown=(188, 185, 180),
                  shirt=(233, 221, 193), trousers=(126, 130, 136), shoe=(62, 54, 48),
                  scarf=None, specs="half", mouser=(168, 165, 160)),
    "clerk": dict(skin=(182, 128, 91), hair=(242, 240, 234), crown=(242, 240, 234),
                  shirt=(223, 233, 238), trousers=(78, 82, 88), shoe=(52, 46, 42),
                  scarf=(214, 234, 214), specs="round", mouser=(232, 230, 224)),
    "karim": dict(skin=(182, 128, 91), hair=(242, 240, 234), crown=(242, 240, 234),
                  shirt=(223, 233, 238), trousers=(78, 82, 88), shoe=(52, 46, 42),
                  scarf=(214, 234, 214), specs="round", mouser=(232, 230, 224)),
}

BASE = dict(lean=0.0, crouch=0.0, head=0.0, headup=0.0, la=7.0, lb=9.0, ra=7.0, rb=9.0,
            glasses=1.0, smile=0.0, swing=0.0, bobs=0.0)


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def sample(keys, t):
    if not keys:
        return dict(BASE)
    if t <= keys[0][0]:
        return dict(BASE, **keys[0][1])
    if t >= keys[-1][0]:
        return dict(BASE, **keys[-1][1])
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            p0, p1 = dict(BASE, **a), dict(BASE, **b)
            k = ease((t - t0) / max(1e-6, t1 - t0))
            return {n: p0[n] + (p1[n] - p0[n]) * k for n in p0}
    return dict(BASE, **keys[-1][1])


def draw(canvas, spec, t):
    look = LOOK.get(spec.get("who", "habib"), LOOK["habib"])
    p = sample(spec.get("keys", []), t)
    x, feet, h = float(spec["x"]), float(spec["feet"]), float(spec["h"])
    s = h / 1000.0
    back = spec.get("view", "back") == "back"
    flip = -1.0 if spec.get("flip") else 1.0

    # breathing and a slow sway: nothing is ever perfectly still
    ph = t + spec.get("seed", 0.0)
    p["la"] += 1.2 * math.sin(2 * math.pi * 0.29 * ph)
    p["ra"] += 1.2 * math.sin(2 * math.pi * 0.29 * ph + 0.7)
    p["head"] += 1.4 * math.sin(2 * math.pi * 0.17 * ph + 1.1)
    p["headup"] += 0.8 * math.sin(2 * math.pi * 0.13 * ph)
    breath = 3.2 * math.sin(2 * math.pi * 0.31 * ph)

    w = spec.get("walk")
    if w:
        ph2 = 2 * math.pi * w[1] * t
        p["swing"] += w[0] * math.sin(ph2)
        p["bobs"] = 5.0 * abs(math.sin(ph2))
        p["la"] += 7.0 * math.sin(ph2 + math.pi)
        p["ra"] += 7.0 * math.sin(ph2)

    ol = max(3, int(round(6.2 * s)))
    hip_y = -424.0 + p["crouch"] * 44.0
    hip = (x, feet + hip_y * s)
    la = math.radians(p["lean"])
    cos_l, sin_l = math.cos(la), math.sin(la)

    def U(dx, dy):
        """A point given in units above the floor; leaned about the hip; scaled."""
        ry0 = dy - hip_y
        return (hip[0] + (dx * cos_l - ry0 * sin_l) * s * flip,
                hip[1] + (dx * sin_l + ry0 * cos_l) * s)

    def G(dx, dy):
        return (x + dx * s * flip, feet + dy * s)

    def line(a, b, fill, wu, outline=True):
        if outline:
            d.line([a, b], fill=INK, width=int(wu * s) + 2 * ol, joint="curve")
        d.line([a, b], fill=fill, width=int(wu * s), joint="curve")

    d = ImageDraw.Draw(canvas)

    # ---- shadow
    sw, sh = 230 * s, 42 * s
    d.ellipse((x - sw / 2, feet - sh * 0.4, x + sw / 2, feet + sh * 0.6), fill=SHADOW)

    # ---- legs
    swing = p["swing"]
    bob = p["bobs"] * s
    for sign in (-1, 1):
        a = math.radians(sign * swing)
        hp = G(sign * 52, hip_y)      # units: G scales by s
        knee = (hp[0] + math.sin(a) * 196 * s, hp[1] + math.cos(a) * 196 * s - bob)
        kb = math.radians(sign * (swing * 0.35 + max(0.0, swing) * 0.45))
        ankle = (knee[0] + math.sin(kb) * 176 * s, knee[1] + math.cos(kb) * 176 * s)
        line(hp, knee, look["trousers"], 86)
        line(knee, ankle, look["trousers"], 74)
        # a shoe: a rounded block on the floor, toe pointing the way he faces
        fx = ankle[0] + sign * 6 * s * flip
        fy = feet - 26 * s
        d.rounded_rectangle([fx - 42 * s - ol, fy - 26 * s - ol, fx + 42 * s + ol, fy + 24 * s + ol],
                            radius=26 * s, fill=INK)
        d.rounded_rectangle([fx - 42 * s, fy - 26 * s, fx + 42 * s, fy + 24 * s],
                            radius=22 * s, fill=look["shoe"])

    # ---- torso, with the shoulders rounded off
    sh_y = -742 + breath * 0.4
    body = [U(-116, -404), U(-130, sh_y + 62), U(-104, sh_y + 8), U(104, sh_y + 8),
            U(130, sh_y + 62), U(116, -404)]
    d.polygon(body, fill=look["shirt"], outline=INK, width=ol)
    d.line([U(0, sh_y + 24), U(0, -420)], fill=(206, 194, 168), width=max(2, ol - 2))
    if spec.get("pocket", True):
        for sign in (-1, 1):
            d.rectangle([U(sign * 78 - 23, sh_y + 66), U(sign * 78 + 23, sh_y + 114)],
                        outline=INK, width=max(2, ol - 3))

    # ---- the gamchha the clerk never takes off
    if look.get("scarf"):
        sc = [U(-118, sh_y + 16), U(-24, sh_y + 8), U(112, -380), U(36, -376)]
        d.polygon(sc, fill=look["scarf"], outline=INK, width=ol)
        for i in range(3):
            d.line([U(-112 + i * 28, sh_y + 26 - i * 16), U(-22 + i * 28, sh_y + 18 - i * 16)],
                   fill=(200, 98, 86), width=max(2, ol - 3))

    # ---- arms
    for sign, ka, kb in ((-1, "la", "lb"), (1, "ra", "rb")):
        sx, sy = sign * 108, sh_y + 22
        A = math.radians(sign * p[ka] * flip)
        elbow = (sx + math.sin(A) * 152, sy + math.cos(A) * 152)
        B = math.radians(sign * (p[ka] + p[kb]) * flip)
        hand = (elbow[0] + math.sin(B) * 138, elbow[1] + math.cos(B) * 138)
        sp = U(sx, sy)
        line(sp, U(*elbow), look["shirt"], 68)
        line(U(*elbow), U(*hand), look["skin"], 50)
        hx, hy = U(*hand)
        r = 21 * s
        d.ellipse((hx - r - ol, hy - r - ol, hx + r + ol, hy + r + ol), fill=INK)
        d.ellipse((hx - r, hy - r, hx + r, hy + r), fill=look["skin"])

    # ---- neck
    neck = [U(-40, sh_y + 10), U(40, sh_y + 10), U(34, sh_y - 54), U(-34, sh_y - 54)]
    d.polygon(neck, fill=look["skin"], outline=INK, width=ol)

    # ---- head
    hr = 106.0
    tilt = math.radians(p["head"] * 0.30)
    cx, cy = U(0, sh_y - 132 + p["headup"] * 0.8)

    def R(dx, dy):
        return (cx + (dx * math.cos(tilt) - dy * math.sin(tilt)) * s * flip,
                cy + (dx * math.sin(tilt) + dy * math.cos(tilt)) * s)

    d.ellipse([cx - hr * s - ol, cy - hr * s - ol, cx + hr * s + ol, cy + hr * s + ol], fill=INK)
    d.ellipse([cx - hr * s, cy - hr * s, cx + hr * s, cy + hr * s], fill=look["skin"])

    if back:
        # a dome of hair, and the nape left as skin
        dome = [R(-hr * 1.02, 40), R(-hr, -20), R(-80, -84), R(0, -110), R(80, -84),
                R(hr, -20), R(hr * 1.02, 40), R(48, 46), R(-48, 46)]
        d.polygon(dome, fill=look["hair"], outline=INK, width=ol)
        pass
    else:
        # hair over the top two thirds, ears, then the face
        cap = [R(-hr + 4, -6), R(-84, -74), R(-30, -96), R(30, -96), R(84, -74),
               R(hr - 4, -6), R(66, 10), R(0, -18), R(-66, 10)]
        d.polygon(cap, fill=look["hair"], outline=INK, width=ol)
        for sign in (-1, 1):
            ex, ey = R(sign * (hr - 2), 22)
            d.ellipse([ex - 17 * s, ey - 22 * s, ex + 17 * s, ey + 22 * s],
                      fill=look["skin"], outline=INK, width=max(2, ol - 2))
        # brows, eyes, nose
        for sign in (-1, 1):
            d.line([R(sign * 54, 2), R(sign * 18, -4)], fill=INK, width=max(3, int(6 * s)))
            ex, ey = R(sign * 36, 26)
            r = 11 * s
            d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=INK)
        nx, ny = R(0, 46)
        d.line([(nx, ny), (nx + 8 * s * flip, ny + 20 * s)], fill=INK, width=max(2, int(5 * s)))
        # moustache, then a mouth that turns up when the man is being kind
        if look.get("mouser"):
            mx, my = R(0, 70)
            d.line([(mx - 30 * s, my), (mx + 30 * s, my)], fill=look["mouser"],
                   width=max(4, int(10 * s)))
        m = p.get("smile", 0.0)
        d.line([R(-26, 88), R(0, 90 + 6 + m * 9), R(26, 88)], fill=INK,
               width=max(3, int(6 * s)), joint="curve")
        # spectacles
        if p["glasses"] > 0.5 and look.get("specs"):
            thick = max(2, int(5 * s)) if look["specs"] == "round" else max(2, int(3.6 * s))
            for sign in (-1, 1):
                ox, oy = R(sign * 36, 24)
                r = 34 * s
                d.ellipse([ox - r, oy - r, ox + r, oy + r], outline=INK, width=thick)
            d.line([R(-4, 24), R(4, 24)], fill=INK, width=thick)
