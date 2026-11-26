"""rig2d.py — a cut-out 2D character: flat shapes, ink outline, one three-quarter profile.

Everything is measured from the height `h` in pixels and drawn with the feet on
(x, gy). Facing is baked in (the profile looks to the right); mirror by flipping cx.
"""
import math

from flat import INK, INK2, mix

TAU = math.pi * 2


def limb(ax, ay, a1, l1, a2, l2):
    """Two-bone chain: a1/a2 are clockwise from straight-down, +a leans forward (+x)."""
    kx, ky = ax + math.sin(a1) * l1, ay + math.cos(a1) * l1
    ex, ey = kx + math.sin(a1 + a2) * l2, ky + math.cos(a1 + a2) * l2
    return (kx, ky), (ex, ey)


def _mix_pt(a, b, k):
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


def joints(h, gy, cx, pose):
    walk = pose.get("walk", 0.0)
    amp = pose.get("stride", 1.0)
    kneel = pose.get("kneel", 0.0)
    phase = walk * TAU
    breath = pose.get("breath", 0.0)

    hip_y = gy - 0.445 * h - breath * 0.004 * h
    sh_y = hip_y - 0.300 * h
    sh_x = cx


    # ---- legs ---------------------------------------------------------------
    legs = []
    for off in (0.0, math.pi):
        th = 0.40 * amp * math.sin(phase + off)
        kn = 0.85 * amp * max(0.0, math.sin(phase + off - 1.05))
        knee, ankle = limb(cx, hip_y, th, 0.212 * h, th - kn, 0.200 * h)
        legs.append([(cx, hip_y), knee, ankle])

    if kneel > 0.02:                       # sit back on the heels, front foot planted
        k = kneel
        hipk = (cx - 0.020 * h, gy - 0.238 * h)
        front = [hipk, (cx + 0.152 * h, gy - 0.170 * h), (cx + 0.140 * h, gy - 0.030 * h)]
        back = [hipk, (cx - 0.140 * h, gy - 0.110 * h), (cx - 0.292 * h, gy - 0.032 * h)]
        for i, tgt in ((1, front), (0, back)):
            for j in range(3):
                legs[i][j] = _mix_pt(legs[i][j], tgt[j], k)
        # the torso comes down with the hips and leans forward
        hip_y = hip_y + (hipk[1] - hip_y) * k
        sh_y = sh_y + ((hipk[1] - 0.295 * h) - sh_y) * k
        sh_x = cx + 0.085 * h * k

    # ---- arms ---------------------------------------------------------------
    swing = 0.44 * amp * math.sin(phase + math.pi)
    reach = pose.get("reach", 0.0)
    raise_ = pose.get("arm", 0.0)
    arms = []
    for side in (0, 1):
        s = 1.0 if side == 0 else -1.0
        a1 = 0.05 + s * swing + 0.34 * raise_
        a2 = -0.26 - 0.30 * raise_
        if side == 1 and reach > 0.01:                 # the near arm does the reaching
            a1 = a1 * (1 - reach) + (1.02 + 0.18 * pose.get("grab", 0.0)) * reach
            a2 = a2 * (1 - reach) + (-0.10 - 0.34 * pose.get("grab", 0.0)) * reach
        el, hand = limb(sh_x - 0.010 * h, sh_y + 0.016 * h, a1, 0.168 * h, a2, 0.158 * h)
        if kneel > 0.02 and side == 1:
            tgt_hd = (cx + (0.215 + 0.055 * reach) * h, gy - (0.130 - 0.090 * reach) * h)
            hand = _mix_pt(hand, tgt_hd, kneel)
            shp = (sh_x - 0.010 * h, sh_y + 0.016 * h)
            mid = ((shp[0] + hand[0]) / 2 + 0.030 * h, (shp[1] + hand[1]) / 2 - 0.020 * h)
            el = _mix_pt(el, mid, kneel)
        elif kneel > 0.02:
            el = _mix_pt(el, (cx - 0.090 * h, gy - 0.320 * h), kneel)
            hand = _mix_pt(hand, (cx - 0.135 * h, gy - 0.150 * h), kneel)
        arms.append([(sh_x - 0.010 * h, sh_y + 0.016 * h), el, hand])
    head_c = (sh_x + 0.014 * h, sh_y - 0.093 * h - breath * 0.004 * h)
    return dict(hip=(cx, hip_y), sh=(sh_x, sh_y), head=head_c, legs=legs, arms=arms)


# ---------------------------------------------------------------------------- drawing
MONO = [None]          # module flag: when set, everything is drawn in one ink, no outline


def draw(cv, spec, h, gy, cx, pose=None, flip=False, mono=None, eye=None, props=()):
    """Draw one character. `h` = full height px, feet on gy, body axis at cx.
    With `mono`, the whole figure is one flat colour and no outline — a silhouette."""
    pose = pose or {}
    MONO[0] = None
    if mono is not None:
        MONO[0] = mono
        spec = {k: mono for k in ("shirt", "shorts", "skin", "hair", "shoe")}
        for pr in props:
            spec[pr] = mono
    J = joints(h, gy, cx, pose)
    shirt, shirt_d = spec["shirt"], mix(spec["shirt"], INK, 0.24)
    short, short_d = spec["shorts"], mix(spec["shorts"], INK, 0.24)
    skin = spec["skin"]
    skin_d = mix(spec["skin"], INK, 0.16)
    hair = spec["hair"]
    shoe = spec.get("shoe", INK2)
    lw = 0.0 if MONO[0] is not None else max(2.0, 0.0060 * h)

    # far side first, one ink darker: depth without gradients
    if spec.get("bag"):
        bag_on_back(cv, spec, h, J, pose, lw)
    _leg(cv, J["legs"][0], h, skin_d, short_d, shoe, lw, back=True)
    _arm(cv, J["arms"][0], h, shirt_d, skin_d, lw)

    sh, hip = J["sh"], J["hip"]
    cv.poly([(sh[0] - 0.116 * h, sh[1] + 0.030 * h),
             (sh[0] - 0.098 * h, sh[1] - 0.014 * h),
             (sh[0] - 0.030 * h, sh[1] - 0.030 * h),
             (sh[0] + 0.052 * h, sh[1] - 0.026 * h),
             (sh[0] + 0.104 * h, sh[1] - 0.006 * h),
             (sh[0] + 0.112 * h, sh[1] + 0.080 * h),
             (hip[0] + 0.098 * h, hip[1] + 0.045 * h),
             (hip[0] - 0.100 * h, hip[1] + 0.050 * h),
             (sh[0] - 0.116 * h, sh[1] + 0.075 * h)], shirt, INK, lw)

    # shorts block, sitting on the hips
    cv.poly([(hip[0] - 0.104 * h, hip[1] + 0.006 * h),
             (hip[0] + 0.102 * h, hip[1] + 0.002 * h),
             (hip[0] + 0.096 * h, hip[1] + 0.148 * h),
             (hip[0] - 0.098 * h, hip[1] + 0.150 * h)], short, INK, lw)
    if spec.get("belt"):
        cv.rect([hip[0] - 0.106 * h, hip[1] + 0.000 * h,
                 hip[0] + 0.104 * h, hip[1] + 0.024 * h], spec["belt"], INK, lw * 0.7, r=3)

    _leg(cv, J["legs"][1], h, skin, short, shoe, lw, back=False)
    cv.capsule((sh[0] + 0.012 * h, sh[1] + 0.020 * h), (sh[0] + 0.016 * h, sh[1] - 0.048 * h),
               0.036 * h, 0.034 * h, skin, INK, lw)                       # neck
    if spec.get("hood"):
        _hood(cv, spec, h, J, lw)
    _head(cv, spec, h, J, pose, lw, eye=eye)
    _arm(cv, J["arms"][1], h, shirt, skin, lw)
    if spec.get("scarf"):
        _scarf(cv, spec, h, J, lw)


def _leg(cv, lg, h, skin, short, shoe, lw, back):
    hip, knee, ankle = lg
    cv.capsule(hip, knee, 0.056 * h, 0.046 * h, skin, INK, lw)
    cv.capsule(knee, ankle, 0.046 * h, 0.036 * h, skin, INK, lw)
    fx, fy = ankle
    cv.poly([(fx - 0.042 * h, fy - 0.012 * h),
             (fx + 0.030 * h, fy - 0.014 * h),
             (fx + 0.070 * h, fy + 0.026 * h),
             (fx - 0.048 * h, fy + 0.028 * h)], shoe, INK, lw)


def _arm(cv, ar, h, sleeve, skin, lw):
    sh, el, hand = ar
    cv.capsule(sh, el, 0.048 * h, 0.040 * h, sleeve, INK, lw)
    cv.capsule(el, hand, 0.038 * h, 0.032 * h, skin, INK, lw)
    cv.circle(hand[0], hand[1], 0.040 * h, skin, INK, lw)


def _head(cv, spec, h, J, pose, lw, eye=None):
    cx, cy = J["head"]
    tilt = max(-9.5, min(9.5, float(pose.get("head", 0.0) or 0.0)))
    pose = dict(pose)
    pose["head"] = tilt
    if MONO[0] is not None:
        r = 0.108 * h
        cy += pose.get("head", 0.0) * r * 0.16
        cv.circle(cx + 0.03 * r, cy, r, MONO[0])
        nx, ny = cx + 0.98 * r, cy + 0.14 * r
        cv.poly([(nx - 0.12 * r, ny - 0.16 * r), (nx + 0.24 * r, ny + 0.12 * r),
                 (nx - 0.12 * r, ny + 0.24 * r)], MONO[0])
        if eye:
            cv.circle(cx + 0.40 * r, cy - 0.04 * r, r * 0.11, eye)
        return
    r = 0.108 * h
    cy += pose.get("head", 0.0) * r * 0.16
    skin = spec["skin"]
    hair = spec["hair"]

    cv.circle(cx + 0.03 * r, cy, r, skin, INK, lw)
    # nose: a small blunt wedge on the forward edge
    nx, ny = cx + 0.98 * r, cy + 0.14 * r
    cv.poly([(nx - 0.10 * r, ny - 0.14 * r), (nx + 0.20 * r, ny + 0.10 * r),
             (nx - 0.10 * r, ny + 0.22 * r)], skin, INK, lw * 0.85)
    # ear
    cv.circle(cx - 0.84 * r, cy + 0.12 * r, r * 0.17, skin, INK, lw * 0.85)

    # hair: one flat cap with a fringe notch, never a helmet
    cv.poly([(cx - 1.02 * r, cy + 0.28 * r),
             (cx - 1.06 * r, cy - 0.36 * r),
             (cx - 0.60 * r, cy - 0.96 * r),
             (cx + 0.10 * r, cy - 1.04 * r),
             (cx + 0.70 * r, cy - 0.74 * r),
             (cx + 0.86 * r, cy - 0.34 * r),
             (cx + 0.46 * r, cy - 0.50 * r),
             (cx + 0.04 * r, cy - 0.26 * r),
             (cx - 0.34 * r, cy - 0.54 * r),
             (cx - 0.72 * r, cy - 0.04 * r)], hair, INK, lw * 0.85)

    # eye, brow, mouth
    blink = pose.get("blink", 0.0)
    look = pose.get("look", 0.0)
    ex, ey = cx + 0.44 * r, cy - 0.04 * r
    if blink > 0.6:
        cv.line([(ex - 0.18 * r, ey), (ex + 0.16 * r, ey)], INK, lw * 0.85)
    else:
        cv.ellipse(ex + look * 0.08 * r, ey, r * 0.085, r * 0.13, INK)
    brow = pose.get("brow", 0.0)
    cv.line([(ex - 0.22 * r, ey - 0.40 * r - brow * 0.08 * r),
             (ex + 0.20 * r, ey - 0.34 * r + brow * 0.14 * r)], INK, lw * 0.8)
    m = pose.get("mouth", 0.0)
    my = cy + 0.50 * r
    cv.line([(cx + 0.30 * r, my - m * 0.06 * r), (cx + 0.62 * r, my + m * 0.12 * r)],
            INK, lw * 0.8)


def _scarf(cv, spec, h, J, lw):
    sh = J["sh"]
    col = spec["scarf"]
    line = None if MONO[0] is not None else INK
    cv.poly([(sh[0] - 0.080 * h, sh[1] - 0.020 * h), (sh[0] + 0.070 * h, sh[1] - 0.026 * h),
             (sh[0] + 0.074 * h, sh[1] + 0.030 * h), (sh[0] - 0.078 * h, sh[1] + 0.034 * h)],
            col, line, lw * 0.85)
    cv.poly([(sh[0] + 0.026 * h, sh[1] + 0.016 * h), (sh[0] + 0.074 * h, sh[1] + 0.018 * h),
             (sh[0] + 0.060 * h, sh[1] + 0.175 * h), (sh[0] + 0.016 * h, sh[1] + 0.165 * h)],
            col, line, lw * 0.85)


def _hood(cv, spec, h, J, lw):
    """A hood reads as a silhouette: a bigger rounded mass around the skull plus a drape
    down the back — never a separate hat sitting on top."""
    cx, cy = J["head"]
    r = 0.108 * h
    col = spec["hood"]
    line = None if MONO[0] is not None else INK
    cv.poly([(cx - 0.20 * r, cy + 1.30 * r), (cx - 1.28 * r, cy + 1.10 * r),
             (cx - 1.30 * r, cy - 0.30 * r), (cx - 0.70 * r, cy - 1.10 * r),
             (cx + 0.10 * r, cy - 1.16 * r), (cx + 0.62 * r, cy - 0.62 * r),
             (cx + 0.10 * r, cy - 0.72 * r), (cx - 0.62 * r, cy - 0.40 * r),
             (cx - 0.80 * r, cy + 0.60 * r)], col, line, lw)
    cv.circle(cx - 0.06 * r, cy - 0.10 * r, 1.24 * r, col, line, lw)


def bag_on_back(cv, spec, h, J, pose, lw):
    """Ayan's ochre bag: strap over the near shoulder, body hanging behind the hip."""
    sh, hip = J["sh"], J["hip"]
    col = spec["bag"]
    bx = hip[0] - 0.075 * h
    by = hip[1] - 0.030 * h
    cv.poly([(bx - 0.080 * h, by - 0.055 * h), (bx + 0.080 * h, by - 0.055 * h),
             (bx + 0.092 * h, by + 0.150 * h), (bx - 0.070 * h, by + 0.150 * h)],
            col, INK, lw)
    cv.rect([bx - 0.080 * h, by - 0.070 * h, bx + 0.080 * h, by - 0.040 * h],
            mix(col, INK, 0.28), INK, lw * 0.8)
    cv.line([(sh[0] + 0.070 * h, sh[1] + 0.010 * h), (bx + 0.030 * h, by - 0.050 * h)],
            INK, lw * 1.4)
