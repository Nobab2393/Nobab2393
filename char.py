"""Pose + renderer for the flat-vector Bengali characters (3/4 front view)."""
import math
from dataclasses import dataclass

from PIL import Image, ImageFilter

from rig import Layer, add, clamp01, dist, ik2, norm, rot, sub, vlerp

TAU = math.pi * 2


@dataclass
class Pose:
    hip: tuple = (0.0, 0.0)
    torso: float = 0.0
    head: float = 0.0
    foot_n: tuple = (0.09, 0.46)
    foot_f: tuple = (-0.09, 0.46)
    hand_n: tuple = (0.175, 0.215)
    hand_f: tuple = (-0.195, 0.225)
    coat: float = 0.0
    blink: float = 1.0
    mouth: float = 0.0
    smile: float = 0.5
    brow: float = 0.0
    look: float = 0.0
    hand_open: float = 0.6
    flip: bool = False


# ---------------------------------------------------------------- legs & arms
def _leg(layer, ch, hip, foot, pal, near=True):
    P = ch.height
    knee = ik2(hip, foot, ch.thigh * P, (ch.shin + ch.ankle) * P, bend=-1.0)
    w_hip = (0.098 if near else 0.092) * P
    w_knee = 0.074 * P
    w_ank = 0.052 * P
    pant = pal.pants
    layer.capsule(hip, knee, w_hip, w_knee, pant, pal.outline, 0.008 * P)
    layer.capsule(knee, add(foot, (0, -ch.ankle * P * 0.8)), w_knee * 0.95, w_ank, pant, pal.outline, 0.008 * P)
    return knee


def _shoe(layer, ch, foot, pal, near=True):
    P = ch.height
    up = -ch.ankle * P
    if ch.key == "king":
        pts = [add(foot, (-0.055 * P, up - 0.012 * P)), add(foot, (-0.048 * P, up + 0.016 * P)),
               add(foot, (0.020 * P, up + 0.024 * P)), add(foot, (0.078 * P, up + 0.004 * P)),
               add(foot, (0.072 * P, up - 0.016 * P)), add(foot, (0.030 * P, up - 0.026 * P)),
               add(foot, (-0.034 * P, up - 0.026 * P))]
    else:
        pts = [add(foot, (-0.060 * P, up - 0.008 * P)), add(foot, (-0.052 * P, up + 0.020 * P)),
               add(foot, (0.040 * P, up + 0.026 * P)), add(foot, (0.092 * P, up + 0.004 * P)),
               add(foot, (0.084 * P, up - 0.018 * P)), add(foot, (0.010 * P, up - 0.028 * P))]
    layer.blob(pts, pal.shoe, pal.outline, 0.008 * P)


def _arm(layer, ch, shoulder, hand, pal, near=True):
    P = ch.height
    ua, fa = ch.upper_arm * P, ch.fore_arm * P
    d = dist(shoulder, hand)
    reach = (ua + fa) * 0.985
    if d > reach:
        hand = add(shoulder, norm(sub(hand, shoulder)), reach)
    elbow = ik2(shoulder, hand, ua, fa, bend=1.0 if near else 1.0)
    outer = pal.top_l if near else pal.top_d
    short = ch.key in ("student", "mentor")
    w1, w2, w3 = 0.058 * P, 0.047 * P, 0.038 * P
    layer.ellipse(shoulder, 0.044 * P, 0.042 * P, outer, pal.outline, 0.007 * P)
    if short:
        ue = vlerp(shoulder, elbow, 0.52)
        layer.capsule(shoulder, ue, w1, w2 * 0.98, outer, pal.outline, 0.007 * P)
        layer.capsule(ue, elbow, w2 * 0.95, w2 * 0.88, pal.skin, pal.outline, 0.007 * P)
        layer.capsule(elbow, hand, w2 * 0.88, w3, pal.skin, pal.outline, 0.007 * P)
    else:
        layer.capsule(shoulder, elbow, w1, w2, outer, pal.outline, 0.007 * P)
        cuff = vlerp(elbow, hand, 0.78)
        layer.capsule(elbow, cuff, w2, w3 * 1.05, outer, pal.outline, 0.007 * P)
        layer.capsule(cuff, hand, w3 * 1.05, w3 * 0.9, pal.skin, pal.outline, 0.006 * P)
    layer.ellipse(hand, 0.034 * P, 0.031 * P, pal.skin, pal.outline, 0.006 * P)
    return elbow


# ---------------------------------------------------------------- garments
def _torso(layer, ch, hip, ang, pal):
    P = ch.height
    T = ch.torso_len * P
    base = [(-0.092, 0.014), (-0.098, -0.080), (-0.100, -0.180), (-0.086, -0.234),
            (0.000, -0.256), (0.086, -0.234), (0.100, -0.180), (0.098, -0.080),
            (0.092, 0.014), (0.000, 0.034)]
    pts = [add(hip, rot((x * P, y * P), ang)) for x, y in base]
    layer.blob(pts, pal.top, pal.outline, 0.009 * P)
    # shaded far side + lit near side
    far = [add(hip, rot((x * P, y * P), ang)) for x, y in
           [(-0.092, 0.008), (-0.098, -0.080), (-0.100, -0.180), (-0.084, -0.232),
            (-0.026, -0.250), (-0.032, -0.120), (-0.036, 0.020)]]
    layer.blob(far, pal.top_d, None, 0)
    lit = [add(hip, rot((x * P, y * P), ang)) for x, y in
           [(0.048, -0.196), (0.082, -0.184), (0.088, -0.116), (0.068, -0.046),
            (0.046, -0.068), (0.042, -0.148)]]
    layer.blob(lit, pal.top_l, None, 0)
    return add(hip, rot((0, -T), ang))


def _coat(layer, ch, hip, ang, pal, swing=0.0):
    P = ch.height
    L = ch.coat_len
    def q(x, y):
        return add(hip, rot((x * P, y * P), ang * 0.28))
    # back panel (behind the legs)
    layer.blob([q(-0.080, -0.030), q(0.080, -0.034),
                q(0.104 + swing * 0.4, L * 0.55), q(0.096 + swing * 0.9, L),
                q(-0.100 + swing * 0.7, L), q(-0.112 + swing * 0.3, L * 0.52)],
               pal.top_d, pal.outline, 0.009 * P)



def _drape(layer, ch, hip, ang, pal):
    """Saree pleats + pallu."""
    P = ch.height
    def q(x, y, k=0.3):
        return add(hip, rot((x * P, y * P), ang * k))
    layer.blob([q(-0.078, -0.010), q(0.080, -0.018), q(0.092, 0.20), q(0.070, 0.42),
                q(-0.090, 0.42), q(-0.104, 0.18)], pal.top, pal.outline, 0.009 * P)
    for i in range(5):
        t = -0.05 + i * 0.032
        layer.line([q(t, 0.04), q(t + 0.014, 0.41)], pal.top_d, 0.010 * P)
    layer.poly([q(-0.090, 0.36), q(0.074, 0.36), q(0.070, 0.42), q(-0.092, 0.42)], pal.accent, None, 0)
    layer.blob([q(-0.082, -0.244, 1.0), q(0.010, -0.262, 1.0), q(0.034, -0.150, 1.0),
                q(-0.062, -0.120, 1.0)], pal.top_l, pal.outline, 0.007 * P)


def _shawl(layer, ch, hip, ang, pal, swing=0.0):
    P = ch.height
    layer.blob([add(hip, rot((x * P, y * P), ang)) for x, y in
                [(-0.092, -0.244), (0.008, -0.262), (0.030, -0.150), (-0.080, -0.130)]],
               pal.accent_d, pal.outline, 0.007 * P)
    layer.blob([add(hip, rot((x * P, y * P), ang * 0.8)) for x, y in
                [(-0.086, -0.240), (-0.040, -0.252), (-0.052 - swing * 0.02, 0.06),
                 (-0.098 - swing * 0.02, 0.05)]], (22, 24, 30), pal.outline, 0.007 * P)


def _belt(layer, ch, hip, ang, pal):
    P = ch.height
    layer.poly([add(hip, rot((x * P, y * P), ang)) for x, y in
                [(-0.090, -0.014), (0.088, -0.018), (0.090, 0.016), (-0.092, 0.020)]],
               pal.accent_d, pal.outline, 0.006 * P)
    layer.ellipse(add(hip, rot((0.052 * P, 0.000 * P), ang)), 0.024 * P, 0.022 * P, pal.accent, pal.outline, 0.006 * P)


def _tie(layer, ch, hip, ang, pal):
    P = ch.height
    T = ch.torso_len * P
    sh = add(hip, rot((0, -T), ang))
    def q(x, y):
        return add(sh, rot((x * P, y * P), ang))
    layer.poly([q(-0.036, 0.014), q(0.030, 0.020), q(0.034, 0.052), q(-0.040, 0.046)],
               (248, 250, 253), pal.outline, 0.005 * P)
    layer.poly([q(-0.006, 0.026), q(0.014, 0.028), q(0.020, 0.048), q(-0.010, 0.046)],
               pal.accent, pal.outline, 0.004 * P)
    layer.poly([q(0.002, 0.050), q(0.018, 0.052), q(0.028, 0.150), q(0.008, 0.156)], pal.accent, pal.outline, 0.005 * P)


# ---------------------------------------------------------------- head
def _head(layer, ch, hip, torso_ang, pose, pal):
    P = ch.height
    r = ch.head_r * P
    neck = add(add(hip, rot((0, -ch.torso_len * P), torso_ang)), rot((0, -0.030 * P), torso_ang))
    ang = torso_ang * 0.4 + pose.head
    c = add(neck, rot((0.004 * P, -0.66 * r), ang))

    hw = ch.head_w

    def hp(x, y):
        return add(c, rot((x * r * hw, y * r), ang))

    layer.capsule(add(hip, rot((0, -0.25 * P), torso_ang)), add(neck, rot((0.004 * P, -0.060 * P), ang)),
                  0.060 * P, 0.048 * P, pal.skin_d, pal.outline, 0.006 * P)

    # ears
    for sx, e in ((-1, pal.skin_d), (1, pal.skin)):
        layer.ellipse(hp(sx * 0.90, 0.10), 0.14 * r, 0.20 * r, e, pal.outline, 0.005 * P)

    # face
    face = [hp(0.00, -1.06), hp(0.56, -0.92), hp(0.86, -0.52), hp(0.90, 0.02),
            hp(0.74, 0.44), hp(0.44, 0.76), hp(0.04, 0.92), hp(-0.38, 0.86),
            hp(-0.72, 0.62), hp(-0.90, 0.14), hp(-0.86, -0.44), hp(-0.56, -0.88)]
    layer.blob(face, pal.skin, pal.outline, 0.006 * P)
    # cheek shadow on the far side
    layer.blob([hp(-0.88, -0.30), hp(-0.30, -0.50), hp(-0.28, 0.40), hp(-0.70, 0.60),
                hp(-0.92, 0.10)], pal.skin_d, None, 0)

    # hair
    if ch.female:
        hair = [hp(0.00, -1.38), hp(0.60, -1.26), hp(0.96, -0.92), hp(1.08, -0.36),
                hp(1.02, 0.12), hp(0.82, -0.18), hp(0.30, -0.62), hp(-0.30, -0.60),
                hp(-0.94, -0.64), hp(-1.10, -0.12), hp(-1.08, -0.76), hp(-0.74, -1.26)]
        layer.blob(hair, pal.hair, pal.outline, 0.006 * P)
        # bun at the back of the head
        layer.ellipse(hp(-0.10, -1.24), 0.44 * r, 0.34 * r, pal.hair, pal.outline, 0.006 * P)
        layer.ellipse(hp(-0.98, 0.42), 0.16 * r, 0.34 * r, pal.hair, pal.outline, 0.005 * P)
        layer.ellipse(hp(0.96, 0.44), 0.13 * r, 0.30 * r, pal.hair, pal.outline, 0.005 * P)
    else:
        hair = [hp(0.00, -1.36), hp(0.58, -1.24), hp(0.94, -0.90), hp(1.06, -0.34),
                hp(1.00, 0.10), hp(0.80, -0.20), hp(0.30, -0.64), hp(-0.30, -0.62),
                hp(-0.92, -0.66), hp(-1.08, -0.14), hp(-1.06, -0.74), hp(-0.72, -1.24)]
        layer.blob(hair, pal.hair, pal.outline, 0.006 * P)
        # side sweep highlight
        layer.blob([hp(0.16, -1.06), hp(0.72, -0.86), hp(0.90, -0.56), hp(0.34, -0.70)],
                   tuple(min(255, c + 26) for c in pal.hair), None, 0)

    # fringe / hairline
    if ch.female:
        layer.blob([hp(-1.02, -0.46), hp(-0.40, -0.86), hp(0.30, -0.88), hp(0.98, -0.52),
                    hp(0.86, -0.24), hp(0.30, -0.52), hp(-0.30, -0.50), hp(-0.90, -0.20)],
                   pal.hair, None, 0)
    else:
        layer.blob([hp(-1.04, -0.50), hp(-0.44, -0.90), hp(0.26, -0.92), hp(0.94, -0.58),
                    hp(0.88, -0.28), hp(0.34, -0.58), hp(-0.26, -0.56), hp(-0.92, -0.24)],
                   pal.hair, None, 0)

    # sideburns / temple hair
    for sx in (-1, 1):
        layer.blob([hp(sx * 1.02, -0.30), hp(sx * 0.86, -0.24), hp(sx * 0.84, 0.16),
                    hp(sx * 1.00, 0.20)], pal.hair, None, 0)

    if ch.beard:
        layer.blob([hp(0.92, 0.44), hp(0.80, 0.72), hp(0.44, 0.98), hp(0.02, 1.10),
                    hp(-0.42, 1.00), hp(-0.76, 0.76), hp(-0.62, 0.50), hp(-0.20, 0.66),
                    hp(0.24, 0.60), hp(0.60, 0.46)], pal.hair, pal.outline, 0.005 * P)

    # eyes (near eye a touch bigger for the 3/4 read)
    ey_y = -0.06
    lx = pose.look * 0.10
    for ex, sz in ((-0.33, 0.95), (0.32, 1.0)):
        o = max(0.05, pose.blink)
        layer.ellipse(hp(ex + lx, ey_y), 0.205 * r * sz, 0.205 * r * o * sz + 0.010 * r,
                      (252, 252, 254), pal.outline, 0.0035 * P)
        if o > 0.6:
            layer.line([hp(ex - 0.20, ey_y - 0.10), hp(ex + 0.20, ey_y - 0.11)],
                       pal.outline, 0.030 * r)
        layer.ellipse(hp(ex + lx + 0.026 + pose.look * 0.06, ey_y + 0.012),
                      0.112 * r * sz, 0.120 * r * o * sz + 0.006 * r, pal.eye, None, 0)
        layer.ellipse(hp(ex + lx + 0.055 + pose.look * 0.06, ey_y - 0.035),
                      0.032 * r * sz, 0.035 * r * o * sz, (255, 255, 255), None, 0)
        if pose.blink < 0.45:
            layer.line([hp(ex - 0.21, ey_y), hp(ex + 0.21, ey_y + 0.01)], pal.outline, 0.035 * r)
    # brows
    by = -0.42 - 0.10 * pose.brow
    for ex in (-0.36, 0.35):
        layer.line([hp(ex - 0.20, by + 0.05 * pose.brow), hp(ex + 0.20, by - 0.05 * pose.brow)],
                   pal.hair, 0.090 * r)

    # nose
    layer.blob([hp(0.10, -0.10), hp(0.26, 0.14), hp(0.20, 0.26), hp(0.00, 0.20)],
               pal.skin_d, None, 0)
    layer.line([hp(0.00, 0.24), hp(0.19, 0.22)], pal.outline, 0.028 * r)

    if ch.moustache:
        layer.blob([hp(-0.30, 0.44), hp(-0.04, 0.34), hp(0.26, 0.38), hp(0.34, 0.50),
                    hp(0.06, 0.50), hp(-0.20, 0.54)], pal.hair, None, 0)

    mo = clamp01(pose.mouth)
    my = 0.64
    if mo < 0.10:
        layer.line([hp(-0.24, my), hp(0.0, my + 0.02), hp(0.24, my - 0.04 * pose.smile)],
                   pal.outline, 0.042 * r)
    else:
        layer.blob([hp(-0.20, my), hp(0.0, my - 0.03), hp(0.20, my),
                    hp(0.16, my + 0.06 + 0.11 * mo), hp(-0.02, my + 0.09 + 0.13 * mo),
                    hp(-0.18, my + 0.04 + 0.07 * mo)], (78, 34, 40), pal.outline, 0.004 * P)
        if mo > 0.6:
            layer.blob([hp(-0.14, my + 0.01), hp(0.14, my + 0.01), hp(0.12, my + 0.05),
                        hp(-0.12, my + 0.05)], (250, 248, 250), None, 0)

    if ch.glasses:
        for ex in (-0.42, 0.40):
            layer.ellipse(hp(ex, ey_y), 0.34 * r, 0.32 * r, None, pal.outline, 0.035 * r)
        layer.line([hp(-0.10, ey_y + 0.02), hp(0.10, ey_y + 0.02)], pal.outline, 0.035 * r)
        layer.line([hp(-0.76, ey_y), hp(-0.94, ey_y - 0.06)], pal.outline, 0.030 * r)
        layer.line([hp(0.74, ey_y), hp(0.94, ey_y - 0.06)], pal.outline, 0.030 * r)

    if ch.crown:
        top = hp(0.02, -1.16)
        w = 0.66 * r
        layer.blob([add(top, (-w, 0.10 * r)), add(top, (-w * 0.60, -0.52 * r)), add(top, (-w * 0.24, 0.00 * r)),
                    add(top, (0.02 * r, -0.70 * r)), add(top, (w * 0.30, -0.02 * r)),
                    add(top, (w * 0.62, -0.48 * r)), add(top, (w, 0.10 * r)),
                    add(top, (w * 0.94, 0.50 * r)), add(top, (-w * 0.94, 0.50 * r))],
                   pal.accent, pal.outline, 0.007 * P)
        layer.line([add(top, (-w * 0.94, 0.26 * r)), add(top, (w * 0.94, 0.26 * r))], pal.accent_d, 0.075 * r)
        for k in (-0.62, 0.0, 0.62):
            layer.ellipse(add(top, (w * k, -0.18 * r)), 0.075 * r, 0.075 * r, (228, 86, 94), pal.outline, 0.004 * P)
    return c


# ---------------------------------------------------------------- props
def _briefcase(layer, ch, hand, pal):
    P = ch.height
    c = add(hand, (0.0, 0.155 * P))
    w, h = 0.165 * P, 0.115 * P
    layer.poly([add(c, (-w, -h * 0.52)), add(c, (w, -h * 0.52)), add(c, (w * 1.02, h * 0.56)),
                add(c, (-w * 1.02, h * 0.56))], pal.prop, pal.outline, 0.009 * P)
    layer.poly([add(c, (-w * 1.02, -h * 0.02)), add(c, (w * 1.02, -h * 0.02)),
                add(c, (w * 1.02, h * 0.10)), add(c, (-w * 1.02, h * 0.10))], pal.accent_d, None, 0)
    for sx in (-0.036, 0.036):
        layer.line([add(hand, (sx * P, 0.010 * P)), add(c, (sx * P, -h * 0.52))], pal.outline, 0.014 * P)


def _notebook(layer, ch, hand, pal):
    P = ch.height
    c = add(hand, (0.018 * P, -0.030 * P))
    layer.poly([add(c, (-0.066 * P, -0.052 * P)), add(c, (0.064 * P, -0.064 * P)),
                add(c, (0.072 * P, 0.056 * P)), add(c, (-0.058 * P, 0.064 * P))],
               (70, 114, 166), pal.outline, 0.008 * P)
    layer.line([add(c, (-0.046 * P, -0.016 * P)), add(c, (0.032 * P, -0.024 * P))], (224, 234, 246), 0.010 * P)


def _backpack(layer, ch, hip, torso_ang, pal):
    P = ch.height
    c = add(hip, rot((-0.100 * P, -0.150 * P), torso_ang))
    layer.blob([add(c, (-0.070 * P, -0.086 * P)), add(c, (0.048 * P, -0.098 * P)),
                add(c, (0.058 * P, 0.088 * P)), add(c, (-0.064 * P, 0.092 * P))],
               (92, 68, 50), pal.outline, 0.009 * P)


# ---------------------------------------------------------------- main
def render(ch, pose, scale=1.0):
    P = ch.height
    W, H = int(1.16 * P), int(1.22 * P)
    ox, oy = W * 0.5, H * 0.53
    layer = Layer(W, H, (ox, oy), P)
    pal = ch.pal
    hip = pose.hip
    ang = pose.torso
    flip = pose.flip

    def mx(p):
        return (-p[0], p[1]) if flip else p

    def _ispt(v):
        return isinstance(v, (tuple, list)) and len(v) == 2 and all(
            isinstance(k, (int, float)) for k in v)

    def _mir(v):
        if _ispt(v):
            return (-v[0], v[1]) if flip else v
        if isinstance(v, (list, tuple)) and v and all(_ispt(q) for q in v):
            return [(-q[0], q[1]) if flip else q for q in v]
        return v

    class Mirror:
        def __init__(self, lay):
            self.l = lay

        def __getattr__(self, name):
            fn = getattr(self.l, name)

            def wrapped(*args, **kw):
                # geometry args may be a single point or a list of points;
                # widths / radii must pass through untouched.
                if name == "capsule":
                    args = (_mir(args[0]), _mir(args[1])) + args[2:]
                elif name in ("line", "poly", "blob"):
                    args = (_mir(args[0]),) + args[1:]
                elif name == "ellipse":
                    args = (_mir(args[0]),) + args[1:]
                return fn(*args, **kw)

            return wrapped

    L = Mirror(layer)

    T = ch.torso_len * P
    sh_c = add(hip, rot((0, -T), ang))
    sh_n = add(hip, rot((0.082 * P, -0.224 * P), ang))
    sh_f = add(hip, rot((-0.086 * P, -0.230 * P), ang))
    hip_n = add(hip, (0.036 * P, 0))
    hip_f = add(hip, (-0.046 * P, 0))

    # far side
    _arm(L, ch, sh_f, mx(pose.hand_f), pal, near=False)
    _leg(L, ch, hip_f, mx(pose.foot_f), pal, near=False)
    _shoe(L, ch, mx(pose.foot_f), pal, near=False)
    _leg(L, ch, hip_n, mx(pose.foot_n), pal, near=True)
    _shoe(L, ch, mx(pose.foot_n), pal, near=True)

    # body
    if ch.long_coat:
        _coat(L, ch, hip, ang, pal, pose.coat)
    if ch.saree:
        _drape(L, ch, hip, ang, pal)
    if ch.backpack:
        _backpack(L, ch, hip, ang, pal)
    _torso(L, ch, hip, ang, pal)
    if ch.belt:
        _belt(L, ch, hip, ang, pal)
    if ch.shawl:
        _shawl(L, ch, hip, ang, pal, pose.coat)
    if ch.key == "king":
        # gold sash over the shoulder
        L.poly([add(hip, rot((x * P, y * P), ang)) for x, y in
                [(-0.070, -0.246), (0.016, -0.262), (0.030, -0.226), (-0.058, -0.212)]],
               pal.accent, pal.outline, 0.006 * P)
        L.poly([add(hip, rot((x * P, y * P), ang)) for x, y in
                [(-0.058, -0.228), (-0.040, -0.222), (0.030, 0.020), (0.012, 0.024)]],
               pal.accent_d, None, 0)
    _head(L, ch, hip, ang, pose, pal)
    if ch.tie:
        _tie(L, ch, hip, ang, pal)

    # near side
    if ch.briefcase:
        _briefcase(L, ch, mx(pose.hand_f), pal)
    _arm(L, ch, sh_n, mx(pose.hand_n), pal, near=True)
    if ch.notebook:
        _notebook(L, ch, mx(pose.hand_n), pal)

    return layer.finish(scale)
