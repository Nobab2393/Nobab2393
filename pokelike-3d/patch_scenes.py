import re

p = "film.py"
s = open(p).read()

# ---------------------------------------------------------------- 1. helpers
helpers = '''

def _bbox(models, cam):
    """Unclamped screen bbox of every point of every model."""
    xs, ys = [], []
    for m in models:
        for part in m.parts:
            v, _ = C.mesh(part.kind, part.subdiv)
            hom = np.concatenate([v, np.ones((len(v), 1))], 1) @ part.m.T
            uv, _z = cam.project(cam.to_view(hom[:, :3]))
            xs.append(uv[:, 0])
            ys.append(uv[:, 1])
    x = np.concatenate(xs)
    y = np.concatenate(ys)
    return float(x.min()), float(x.max()), float(y.min()), float(y.max())


def _solve_fit(models, eye, target, fov, top, bottom, side):
    """Find the (pan, zoom-out) that puts the models inside the safe area."""
    e = np.array(eye, float)
    g = np.array(target, float)
    dx = dy = 0.0
    s = 1.0
    for _ in range(6):
        c = cam_for(tuple(e), tuple(g), fov)
        x0, x1, y0, y1 = _bbox(models, c)
        need = max((x1 - x0) / (W - 2 * side), (y1 - y0) / (bottom - top))
        if need > s:
            s = min(2.3, need * 1.05)
            e = g + (np.array(eye, float) - g) * s + np.array([dx, dy, 0.0])
            continue
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        dist = float(np.linalg.norm(e - g))
        upp = 2 * math.tan(math.radians(fov) / 2) * dist / H
        ox = (cx - W / 2.0) * upp
        oy = -(cy - (top + bottom) / 2.0) * upp
        dx = float(np.clip(dx + ox, -1.5, 1.5))
        dy = float(np.clip(dy + oy, -1.5, 1.5))
        g = np.array(target, float) + np.array([dx, dy, 0.0])
        e = g + (np.array(eye, float) - np.array(target, float)) * s
        if abs(ox) < 3 and abs(oy) < 3:
            break
    return dx, dy, s


_FIT = {}


def scene_cam(name, build, t_hero, eye, target, fov, top=230, bottom=1540, side=80):
    """One constant framing correction per scene, solved on a hero pose.

    Keeping it constant (instead of re-fitting every frame) stops the camera from
    breathing while characters move, and keeps the render deterministic.
    """
    if name not in _FIT:
        models, _glow = build(t_hero)
        _FIT[name] = _solve_fit(models, eye, target, fov, top, bottom, side)
    dx, dy, s = _FIT[name]
    off = np.array([dx, dy, 0.0])
    g = np.array(target, float) + off
    e = g + (np.array(eye, float) - np.array(target, float)) * s
    return cam_for(tuple(e), tuple(g), fov)
'''

s = s.replace('''

# ---------------------------------------------------------------- scenes''',
              helpers + '''

# ---------------------------------------------------------------- scenes''')

# ---------------------------------------------------------------- 2. scenes
start = s.index("def s1(img, lt, dur):")
end = s.index("def s7(img, lt, dur):")

scenes = '''def s1(img, lt, dur):
    """The ember on the ridge. Title."""
    p = eio(seg(0, dur, lt))
    bg.sky(img, lt, 0.0)
    bg.stars(img, 130, 7, lt, fade=1.0)
    bg.moon(img, 800 - 26 * p, 300, 92, halo=1.0)
    bg.ridge(img, 1320, 240, seed=5, col=(20, 19, 28))
    bg.ridge(img, 1430, 160, seed=11, col=(15, 14, 19))

    def build(t):
        rock = place(cast.rock(0, 0, 0.85), T(-0.55, 0.06, 0.0))
        pup = place(cast.angaar(t=t, bounce=-0.14, flame=0.55, ear=0.7, tail=t),
                    T(-0.55, 0.30, 0.15) @ S(0.92))
        return [rock, pup], [pup]

    models, glow = build(lt)
    cam = scene_cam("s1", build, dur * 0.5, (2.05, 1.05 + 0.10 * p, 8.6 - 1.3 * p),
                    (0.0, 1.16, 0.0), 30, top=600, bottom=1740)
    stage(img, cam, 0.25, (13, 12, 15))
    compose_3d(img, [cam] * len(models), models, glow_models=glow)

    bg.sparks(img, lt, 430, 1080, n=16, spread=180, rise=520, col=(255, 168, 92))
    bg.vignette(img, 110)

    if lt > 1.1:
        k = eout(seg(1.1, 2.0, lt))
        deva.draw_text(img, (540, 360), "अंगार और बादल", int(74 + 6 * k), 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=16)
        d = ImageDraw.Draw(img)
        d.text((540, 432), "A N G A A R   A U R   B A A D A L", font=ImageFont.truetype(TTF + "DejaVuSans.ttf", 27),
               fill=(168, 160, 150, int(255 * k)), anchor="mm")
    if lt > 2.6:
        k = eout(seg(2.6, 3.4, lt))
        deva.draw_text(img, (540, 512), "एक छोटी सी आग, एक बड़ा तूफ़ान", 38, 500,
                       (210, 200, 190) if k > 0.3 else CREAM, shadow=(0, 0, 0), shadow_blur=12)


def s2(img, lt, dur):
    """Ravi finds him."""
    bg.sky(img, lt, 0.05)
    bg.stars(img, 120, 7, lt)
    bg.moon(img, 810, 320, 84)
    bg.ridge(img, 1320, 240, seed=5, col=(20, 19, 28))
    bg.ridge(img, 1430, 160, seed=11, col=(15, 14, 19))

    walk = eio(seg(0.0, 3.2, lt))

    def build(t):
        w = eio(seg(0.0, 3.2, t))
        rock = place(cast.rock(0, 0, 0.8), T(0.85, 0.05, -0.2))
        pup = place(cast.angaar(t=t, bounce=-0.10, ear=0.3 + 0.6 * eio(seg(2.6, 3.2, t)),
                               flame=0.6 + 0.25 * eio(seg(3.4, 4.2, t)),
                               blink=1.0 - eio(seg(2.5, 2.75, t)), tail=t),
                    T(0.85, 0.30, -0.05) @ S(0.92))
        rav = place(cast.ravi(t=t, walk=t if w < 0.98 else 0, arm=eio(seg(3.3, 3.9, t)) * 0.85,
                              look=0.7),
                    T(lerp(-2.7, -1.15, w), 0, 0.45) @ S(1.02))
        return [rock, pup, rav], [pup]

    models, glow = build(lt)
    cam = scene_cam("s2", build, 3.9, (1.10 + 0.30 * walk, 0.95, 8.4), (0.10, 1.02, 0.0), 30)
    stage(img, cam, 0.25, (13, 12, 15))
    compose_3d(img, [cam] * len(models), models, glow_models=glow)

    sneeze = seg(3.9, 4.15, lt) * (1 - seg(4.5, 4.9, lt))
    if sneeze > 0:
        bg.sparks(img, lt, 470, 900, n=30, spread=340, rise=380)
        bg.impact(img, lt, 0.22 * sneeze, cx=470, cy=900)
    bg.vignette(img, 105)
    if lt > 4.6:
        deva.draw_text(img, (540, 1660), "रवि को मिला एक छोटा सा अंगार", 40, 600, CREAM,
                       shadow=(0, 0, 0), shadow_blur=14)


def s3(img, lt, dur):
    """The storm takes the flame."""
    storm = eio(seg(0.0, 2.2, lt))
    bg.sky(img, lt, 0.55 * storm)
    bg.stars(img, 90, 7, lt, fade=1 - 0.7 * storm)
    bg.moon(img, 790, 330, 88, halo=1 - 0.5 * storm)
    bg.ridge(img, 1320, 240, seed=5, col=(20, 19, 28))
    bg.ridge(img, 1430, 160, seed=11, col=(15, 14, 19))
    bg.wind(img, lt, 0.5 + 0.5 * storm)

    k = eio(seg(0.6, 3.6, lt))

    def build(t):
        kk = eio(seg(0.6, 3.6, t))
        hx = lerp(3.0, -0.35, kk)
        hy = lerp(2.90, 1.30, kk) - 0.45 * math.sin(math.pi * kk)
        flame_out = 1.0 - eio(seg(3.4, 3.8, t))
        rock = place(cast.rock(0, 0, 0.75), T(-0.75, 0.05, -0.1))
        pup = place(cast.angaar(t=t, bounce=-0.05, ear=0.9, flame=0.8 * flame_out,
                                look=-0.6, tail=t),
                    T(-0.75, 0.30, 0.0) @ S(0.9))
        haw = place(cast.baadal(t=t, flap=0.5 + 0.5 * math.sin(t * 9.0), dive=0.55 * kk, y=0.0),
                    T(hx, hy, 0.15) @ S(0.95))
        return [rock, pup, haw], [pup]

    models, glow = build(lt)
    # anchor the framing on the pup; the hawk flies in from off-frame by design
    anchors = models[:2]
    cam = scene_cam("s3", lambda t: (build(t)[0][:2], None), 2.6,
                    (0.35, 1.45 + 0.30 * storm, 8.6 - 0.6 * k), (0.0, 1.50, 0.0), 32)
    stage(img, cam, 0.25, (13, 12, 15))
    compose_3d(img, [cam] * len(models), models, glow_models=glow)

    if lt > 3.6:
        bg.sparks(img, lt, 500, 780, n=10, spread=260, rise=420)
    bg.vignette(img, 120)
    if lt > 3.9:
        deva.draw_text(img, (540, 1660), "आसमान से उतरा बादल — और आग ले गया", 38, 600, CREAM,
                       shadow=(0, 0, 0), shadow_blur=14)


def s4(img, lt, dur):
    """The clash."""
    bg.sky(img, lt, 0.75)
    bg.stars(img, 70, 7, lt, fade=0.35)
    bg.ridge(img, 1320, 240, seed=5, col=(18, 17, 25))
    bg.ridge(img, 1430, 160, seed=11, col=(14, 13, 18))
    bg.wind(img, lt, 1.0)

    air = math.sin(math.pi * seg(0.5, 2.4, lt))
    hit = seg(1.9, 2.35, lt)
    sh = shake(lt, 26 * (1 - hit) * air)

    def build(t):
        a = math.sin(math.pi * seg(0.5, 2.4, t))
        h = seg(1.9, 2.35, t)
        pup = place(cast.angaar(t=t, bounce=0.10 + 0.95 * a, lean=0.9 * a, ear=1.0,
                               flame=1.0 + 0.5 * a, look=0.8, tail=t),
                    T(-0.15, 0.10 * a, 0.35) @ S(0.95))
        haw = place(cast.baadal(t=t, flap=0.85, dive=0.35 + 0.45 * h, bank=-20 * (1 - h)),
                    T(0.55 - 0.9 * h, 1.35 + 0.18 * a - 0.55 * h, 0.1) @ S(1.0))
        return [pup, haw], [pup]

    models, glow = build(lt)
    cam = scene_cam("s4", build, 1.4, (0.2 + sh[0] / 300, 1.15 + air * 0.30 + sh[1] / 300,
                                       8.0 - 0.5 * air), (0.0, 1.34 + air * 0.30, 0.0), 33)
    stage(img, cam, 0.25, (12, 11, 14))
    rav = place(cast.ravi(t=lt, arm=0.7, look=0.6), T(-2.35, 0, 0.15) @ S(0.92))
    compose_3d(img, [cam] * len(models) + [cam], models + [rav], glow_models=glow)

    if air > 0.35:
        bg.speed_lines(img, lt, n=30, cx=540, cy=950, inner=230, strength=air)
    if 1.85 < lt < 2.9:
        k = math.sin(math.pi * seg(1.85, 2.55, lt))
        bg.impact(img, lt, k, cx=560, cy=880)
        bg.sparks(img, lt, 560, 880, n=34, spread=520, rise=520)
    bg.vignette(img, 120)
    if lt > 2.7:
        deva.draw_text(img, (540, 1660), "आग और तूफ़ान — आमने-सामने", 42, 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=14)


def s5(img, lt, dur):
    """The choice: he lights the way instead of burning."""
    bg.sky(img, lt, 0.45)
    bg.stars(img, 80, 7, lt, fade=0.5)
    bg.moon(img, 250, 380, 74, halo=0.7)
    bg.ridge(img, 1330, 250, seed=5, col=(19, 18, 26))
    bg.ridge(img, 1440, 150, seed=11, col=(14, 13, 18))
    calm = eio(seg(0.4, 1.8, lt))

    def build(t):
        haw = place(cast.baadal(t=t, flap=0.0, dive=0.0, y=-0.60, bank=74),
                    T(0.55, 0.12, -0.15) @ S(0.95))
        pup = place(cast.angaar(t=t, bounce=0.02, ear=0.55, flame=0.85, look=0.5, tail=t),
                    T(-0.55, 0.08, 0.15) @ S(0.92))
        return [haw, pup], [pup]

    models, glow = build(lt)
    cam = scene_cam("s5", build, 2.2, (1.15, 0.95, 8.9 - 0.5 * calm), (0.05, 1.00, 0.0), 30)
    stage(img, cam, 0.25, (12, 11, 14))
    rav = place(cast.ravi(t=lt, arm=0.35, look=0.3), T(-2.15, 0, -0.15) @ S(0.9))
    compose_3d(img, [cam] * len(models) + [cam], models + [rav], glow_models=glow)

    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(300, 1560), (700, 1560), (900, 1920), (140, 1920)], fill=(255, 170, 90, 26))
    lay = lay.filter(ImageFilter.GaussianBlur(24))
    img.alpha_composite(lay)
    bg.sparks(img, lt, 380, 900, n=12, spread=200, rise=380)
    bg.vignette(img, 110)
    if lt > 2.0:
        deva.draw_text(img, (540, 1650), "अंगार ने जलाया नहीं — रास्ता दिखाया", 40, 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=14)


def s6(img, lt, dur):
    """Together."""
    bg.sky(img, lt, 0.12)
    bg.stars(img, 140, 3, lt)
    bg.moon(img, 860, 300, 96)
    bg.ridge(img, 1310, 235, seed=5, col=(20, 19, 28))
    bg.ridge(img, 1430, 150, seed=11, col=(15, 14, 19))
    k = eio(seg(0.0, dur, lt))

    def build(t):
        rock = place(cast.rock(0, 0, 0.9), T(-1.35, 0.05, -0.6))
        pup = place(cast.angaar(t=t, bounce=-0.02, ear=0.5, flame=0.9, tail=t),
                    T(-0.60, 0.14, 0.25) @ S(0.9))
        rav = place(cast.ravi(t=t, arm=0.2), T(0.35, 0, 0.30) @ S(0.95))
        haw = place(cast.baadal(t=t, flap=0.0, y=-0.64, dive=0.0), T(1.30, 0.10, -0.15) @ S(0.9))
        return [rock, pup, rav, haw], [pup]

    models, glow = build(lt)
    cam = scene_cam("s6", build, dur * 0.6, (0.62, 0.95, 9.4 - 1.0 * k), (0.05, 1.00, 0.0), 30)
    stage(img, cam, 0.25, (13, 12, 15))
    compose_3d(img, [cam] * len(models), models, glow_models=glow)

    bg.sparks(img, lt, 520, 780, n=14, spread=520, rise=520)
    bg.vignette(img, 110)
    if lt > 1.4:
        deva.draw_text(img, (540, 1640), "अब वो तीनों साथ हैं", 42, 700, CREAM,
                       shadow=(0, 0, 0), shadow_blur=14)


'''

s = s[:start] + scenes + s[end:]

# ---------------------------------------------------------------- 3. CTA card
s = s.replace('        scale = 330 / max(1, tile.width)',
              '        scale = 300 / max(1, tile.width)')
s = s.replace('img.alpha_composite(_CTA_TILE, (int(W / 2 - _CTA_TILE.width / 2), 1330))',
              'img.alpha_composite(_CTA_TILE, (int(W / 2 - _CTA_TILE.width / 2), 1300))')

open(p, "w").write(s)
print("film.py rewritten:", len(s), "bytes")
