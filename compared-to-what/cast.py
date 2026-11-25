"""cast.py — the animals, the shops and the props, as low-poly meshes."""
import math

import numpy as np

from studio import (SH_V, SH_F, SH0_V, SH0_F, BX_V, BX_F, CY8_V, CY8_F, CO_V, CO_F, TO_V, TO_F,
                    put, O, FUR, FUR_D, EAR, CREAM, OWL, OWL_L, SCARF, HEDGE, WOOD, WOOD_D,
                    RUST, TEAL, SAGE, BRICK, GLOW, DARK, STONE, GROUND)

LEATHER = np.array([0.50, 0.31, 0.22])


def _sh(col, pos, scale, rot=(0, 0, 0), sub=1, cast=True):
    V, F = (SH_V, SH_F) if sub else (SH0_V, SH0_F)
    return put(V, F, col, pos, scale, rot, cast=cast)


def _bx(col, pos, scale, rot=(0, 0, 0), cast=True, matte=False):
    return put(BX_V, BX_F, col, pos, scale, rot, cast=cast, matte=matte)


def _cy(col, pos, scale, rot=(0, 0, 0), v8=True, cast=True):
    return put(CY8_V if v8 else CY8_V, CY8_F, col, pos, scale, rot, cast=cast)


def _cone(col, pos, scale, rot=(0, 0, 0)):
    return put(CO_V, CO_F, col, pos, scale, rot)


def _torus(col, pos, scale, rot=(0, 0, 0)):
    return put(TO_V, TO_F, col, pos, scale, rot)


# ---------------------------------------------------------------- Bruno
def bruno(pos, ry=0.0, hop=0.0, lean=0.0, tilt=0.0, ears=0.0, arm=0.0, look=0.0,
          purse=True, pack=True, held=None, eyes=1.0):
    """pos = (x, z), y is the ground. hop lifts the whole body, ears flopped back."""
    x, z = pos
    y = hop
    c, s = math.cos(ry), math.sin(ry)

    def L(px, py, pz):
        """local -> world, so the whole rabbit can turn to face its heading."""
        return (x + px * c + pz * s, y + py, z - px * s + pz * c)

    o = []
    lean_r = (lean, 0, 0)
    # feet
    for sx in (-1, 1):
        o.append(_sh(FUR_D, L(0.11 * sx, 0.055, 0.07), (0.085, 0.05, 0.14), sub=0))
    # body + belly
    o.append(_sh(FUR, L(0, 0.44, 0), (0.235, 0.30, 0.215)))
    o.append(_sh(CREAM, L(0, 0.41, 0.135), (0.165, 0.20, 0.10), sub=0))
    # tail
    o.append(_sh(CREAM, L(0, 0.40, -0.22), (0.085, 0.085, 0.075), sub=0))
    # arms
    for sx in (-1, 1):
        o.append(_sh(FUR, L(0.215 * sx, 0.50 + 0.02 * arm * sx, 0.06), (0.055, 0.13, 0.055), sub=0))
    # head
    o.append(_sh(FUR, L(0, 0.80 + 0.012 * tilt, 0.02 + 0.02 * look), (0.185, 0.185, 0.175)))
    o.append(_sh(CREAM, L(0, 0.755 + 0.01 * tilt, 0.155), (0.10, 0.085, 0.085), sub=0))
    o.append(_sh(np.array([0.72, 0.48, 0.46]), L(0, 0.785 + 0.01 * tilt, 0.225), (0.035, 0.028, 0.03), sub=0))
    for sx in (-1, 1):
        o.append(_sh(DARK, L(0.078 * sx, 0.845 + 0.01 * tilt, 0.155),
                     (0.030 * eyes, 0.034 * eyes, 0.028), sub=0))
        o.append(_sh(CREAM, L(0.088 * sx, 0.858 + 0.01 * tilt, 0.176),
                     (0.009, 0.009, 0.006), sub=0, cast=False))
        # ears: long, leaning back with speed, tilting with attention
        o.append(_sh(FUR, L(0.082 * sx, 1.02 + 0.01 * tilt, -0.02 - 0.06 * ears),
                     (0.052, 0.185, 0.032), rot=(-0.20 - 0.5 * ears, 0, 0.16 * sx + 0.2 * tilt * sx)))
        o.append(_sh(EAR, L(0.082 * sx, 1.03 + 0.01 * tilt, 0.012 - 0.06 * ears),
                     (0.030, 0.150, 0.020), rot=(-0.20 - 0.5 * ears, 0, 0.16 * sx + 0.2 * tilt * sx)))
    if pack:
        o.append(_bx(np.array([0.58, 0.40, 0.26]), L(0, 0.55, -0.20), (0.24, 0.26, 0.14), rot=(0, 0, 0)))
        o.append(_bx(np.array([0.46, 0.30, 0.20]), L(0, 0.73, -0.20), (0.18, 0.07, 0.13)))
    if purse:
        hx, hy, hz = held or (0.30, 0.36, 0.16)
        o.append(_sh(LEATHER, L(hx, hy, hz), (0.095, 0.085, 0.075), sub=0))
        o.append(_sh(np.array([0.78, 0.68, 0.42]), L(hx, hy + 0.075, hz), (0.045, 0.022, 0.04), sub=0))
    return o


# ---------------------------------------------------------------- Olive
def olive(pos, ry=0.0, flap=0.0, tilt=0.0, glance=0.0, wing_out=0.0, scarf=True, eyes=1.0,
          head=0.0):
    x, z = pos
    c, s = math.cos(ry), math.sin(ry)

    def L(px, py, pz):
        return (x + px * c + pz * s, py, z - px * s + pz * c)

    o = []
    # tail feathers
    o.append(_bx(OWL, L(0, 0.20, -0.16), (0.14, 0.22, 0.05), rot=(0.35, 0, 0)))
    # body
    o.append(_sh(OWL, L(0, 0.40, 0), (0.225, 0.285, 0.205)))
    o.append(_sh(OWL_L, L(0, 0.36, 0.115), (0.135, 0.19, 0.09), sub=0))
    # wings
    for sx in (-1, 1):
        o.append(_sh(OWL, L(0.235 * sx, 0.42 + 0.03 * flap, -0.01),
                     (0.045, 0.24, 0.145), rot=(0, 0, (0.10 + 0.9 * wing_out) * sx)))
    # feet
    for sx in (-1, 1):
        o.append(_bx(np.array([0.68, 0.50, 0.28]), L(0.075 * sx, 0.035, 0.05), (0.06, 0.07, 0.13)))
    # head
    o.append(_sh(OWL, L(0, 0.735 + 0.01 * head, 0.01), (0.215, 0.20, 0.20)))
    o.append(_sh(OWL_L, L(0, 0.725 + 0.01 * head, 0.125), (0.165, 0.155, 0.075), sub=0))
    for sx in (-1, 1):
        o.append(_sh(np.array([0.90, 0.86, 0.74]), L(0.078 * sx, 0.765, 0.185), (0.072, 0.072, 0.05), sub=0))
        o.append(_sh(DARK, L(0.078 * sx, 0.765 + 0.008 * head, 0.215),
                     (0.045, 0.045 * max(0.08, eyes), 0.03), sub=0))
        # the glasses: a wire ring, two lenses, a temple arm
        o.append(_torus(np.array([0.86, 0.72, 0.42]), L(0.078 * sx, 0.765, 0.235),
                        (0.085, 0.085, 0.085), rot=(math.pi / 2, 0, 0)))
        o.append(_bx(np.array([0.86, 0.72, 0.42]), L(0.20 * sx, 0.775, 0.145),
                     (0.11, 0.012, 0.012), rot=(0, 0.35 * sx, 0)))
        # ear tufts
        o.append(_cone(OWL, L(0.13 * sx, 0.90, -0.02), (0.055, 0.13, 0.055), rot=(0, 0, -0.3 * sx)))
    o.append(_bx(np.array([0.86, 0.72, 0.42]), L(0, 0.775, 0.245), (0.05, 0.012, 0.012)))
    o.append(_cone(np.array([0.85, 0.66, 0.40]), L(0, 0.70, 0.19), (0.045, 0.10, 0.045),
                   rot=(math.pi * 0.62, 0, 0)))
    if scarf:
        o.append(_torus(SCARF, L(0, 0.585, 0.0), (0.19, 0.19, 0.16), rot=(math.pi / 2, 0, 0)))
        o.append(_bx(SCARF, L(0.10, 0.47, 0.10), (0.10, 0.24, 0.035), rot=(0.12, 0, 0.1)))
    return o


# ---------------------------------------------------------------- hedgehog
def hedgehog(pos, ry=0.0, reach=0.0):
    x, z = pos
    c, s = math.cos(ry), math.sin(ry)

    def L(px, py, pz):
        return (x + px * c + pz * s, py, z - px * s + pz * c)

    o = []
    o.append(_sh(HEDGE, L(0, 0.20, 0), (0.235, 0.19, 0.27)))
    # quills: a spread of small cones over the back
    for i in range(11):
        a = -1.5 + i * 0.28
        r = 0.20
        px, pz = math.cos(a) * r, math.sin(a) * r * 0.75
        o.append(_cone(np.array([0.30, 0.22, 0.18]),
                       L(px, 0.24 + 0.06 * math.cos(a * 2), pz - 0.02),
                       (0.035, 0.12, 0.035), rot=(0.5, 0, -a)))
    o.append(_sh(np.array([0.62, 0.50, 0.40]), L(0, 0.16, 0.20), (0.10, 0.09, 0.11), sub=0))
    o.append(_sh(DARK, L(0, 0.17, 0.295), (0.035, 0.03, 0.03), sub=0))
    for sx in (-1, 1):
        o.append(_sh(DARK, L(0.06 * sx, 0.235, 0.20), (0.026, 0.028, 0.025), sub=0))
        o.append(_sh(HEDGE, L(0.09 * sx, 0.04, 0.08), (0.06, 0.04, 0.09), sub=0))
    o.append(_bx(np.array([0.72, 0.68, 0.60]), L(0, 0.12, 0.16), (0.16, 0.14, 0.03),
                 rot=(0.25 + 0.2 * reach, 0, 0)))
    return o


# ---------------------------------------------------------------- props
def bicycle(pos, ry=0.0, lean=0.0, wheel_spin=0.0, scale=1.0, frame=None):
    x, y, z = pos
    frame = frame if frame is not None else np.array([0.36, 0.44, 0.50])
    c, s = math.cos(ry), math.sin(ry)

    def L(px, py, pz):
        return (x + (px * c + pz * s) * scale, y + py * scale, z + (-px * s + pz * c) * scale)

    o = []
    for sx, r in ((-0.42, 0.0), (0.42, 0.0)):
        o.append(put(TO_V, TO_F, DARK, L(sx, 0.30, 0), (0.30 * scale,) * 3,
                     rot=(math.pi / 2, 0, wheel_spin)))
        o.append(put(TO_V, TO_F, np.array([0.62, 0.56, 0.44]), L(sx, 0.30, 0), (0.055 * scale,) * 3,
                     rot=(math.pi / 2, 0, wheel_spin)))
    # frame tubes
    tubes = [((-0.42, 0.30, 0), (-0.02, 0.56, 0)), ((-0.02, 0.56, 0), (0.20, 0.30, 0)),
             ((0.20, 0.30, 0), (0.42, 0.30, 0)), ((-0.02, 0.56, 0), (0.34, 0.62, 0)),
             ((0.34, 0.62, 0), (0.42, 0.30, 0)), ((0.34, 0.62, 0), (0.40, 0.78, 0)),
             ((-0.02, 0.56, 0), (-0.06, 0.74, 0)), ((-0.06, 0.74, 0), (-0.16, 0.76, 0))]
    for a, b in tubes:
        o.append(_tube(frame, L(*a), L(*b), 0.022 * scale))
    o.append(_bx(DARK, L(-0.04, 0.79, 0), (0.16 * scale, 0.05 * scale, 0.11 * scale)))
    o.append(_bx(DARK, L(-0.17, 0.78, 0), (0.16 * scale, 0.035 * scale, 0.035 * scale)))
    o.append(_bx(np.array([0.66, 0.58, 0.42]), L(-0.30, 0.62, 0), (0.03 * scale, 0.14 * scale, 0.03 * scale)))
    o.append(_bx(np.array([0.66, 0.58, 0.42]), L(-0.10, 0.62, 0), (0.03 * scale, 0.14 * scale, 0.03 * scale)))
    o.append(_bx(np.array([0.70, 0.62, 0.46]), L(-0.20, 0.52, 0), (0.26 * scale, 0.20 * scale, 0.20 * scale)))
    return o


def _tube(col, a, b, r):
    """A cylinder between two points — the one piece of geometry glue this rig needs."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    v = b - a
    L = np.linalg.norm(v)
    if L < 1e-6:
        return _sh(col, a, (r, r, r), sub=0)
    z = v / L
    up = np.array([0.0, 1.0, 0.0])
    if abs(z @ up) > 0.95:
        up = np.array([1.0, 0.0, 0.0])
    x = np.cross(up, z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    V, F = CY8_V, CY8_F
    P = np.zeros_like(V)
    for i, (px, py, pz) in enumerate(V):
        P[i] = a + x * px * r + y * py * r + z * pz * L
    return O(P, F, np.asarray(col, float))


def tree(pos, h=3.2, seed=0, season=0.0):
    """Autumn: three canopy blobs, warm on the sun side."""
    x, y, z = pos
    rng = np.random.RandomState(seed)
    o = [_cy(WOOD_D, (x, y, z), (0.16, h * 0.55, 0.16))]
    cols = [np.array([0.82, 0.52, 0.26]), np.array([0.76, 0.62, 0.30]),
            np.array([0.66, 0.38, 0.24]), np.array([0.85, 0.66, 0.36])]
    for i in range(5):
        cx = x + rng.uniform(-0.55, 0.55)
        cz = z + rng.uniform(-0.55, 0.55)
        cy = y + h * 0.62 + rng.uniform(-0.2, 0.55)
        r = rng.uniform(0.48, 0.86)
        o.append(_sh(cols[int(season * 4 + i) % 4], (cx, cy, cz), (r, r * 0.85, r), sub=0))
    return o


def lamp(pos, h=3.0):
    x, y, z = pos
    return [_cy(np.array([0.24, 0.23, 0.22]), (x, y, z), (0.06, h, 0.06)),
            _sh(GLOW, (x, y + h + 0.12, z), (0.14, 0.17, 0.14), sub=0, cast=False),
            _bx(np.array([0.24, 0.23, 0.22]), (x, y + h + 0.28, z), (0.22, 0.05, 0.22))]


def crate(pos, s=0.4, col=None):
    x, y, z = pos
    return [_bx(col if col is not None else WOOD, (x, y + s / 2, z), (s, s, s), rot=(0, 0.2, 0))]


def barrel(pos, s=0.36):
    x, y, z = pos
    return [_cy(WOOD_D, (x, y, z), (s, s * 2.1, s)),
            _cy(np.array([0.30, 0.28, 0.26]), (x, y + s * 0.5, z), (s * 1.04, 0.05, s * 1.04)),
            _cy(np.array([0.30, 0.28, 0.26]), (x, y + s * 1.5, z), (s * 1.04, 0.05, s * 1.04))]


def shop(pos, w=5.4, d=4.0, h=3.6, ry=0.0, wall=None, roof=None, awning=None, lit=True):
    """A townhouse: wall, pitched roof, door, two windows, awning. No textures."""
    x, y, z = pos
    wall = wall if wall is not None else np.array([0.72, 0.63, 0.53])
    roof = roof if roof is not None else np.array([0.52, 0.30, 0.26])
    awning = awning if awning is not None else np.array([0.52, 0.34, 0.30])
    c, s = math.cos(ry), math.sin(ry)

    def L(px, py, pz):
        return (x + px * c + pz * s, y + py, z - px * s + pz * c)

    o = [_bx(wall, L(0, h / 2, 0), (w, h, d), rot=(0, ry, 0))]
    # pitched roof as a wedge of two slabs
    o.append(_bx(roof, L(0, h + 0.42, -d * 0.24), (w * 1.08, 0.14, d * 0.72), rot=(0.55, ry, 0)))
    o.append(_bx(roof, L(0, h + 0.42, d * 0.24), (w * 1.08, 0.14, d * 0.72), rot=(-0.55, ry, 0)))
    # shopfront: a big lit window + door on the front face
    o.append(_bx(np.array([0.22, 0.20, 0.19]), L(-w * 0.14, 1.42, d / 2 + 0.02),
                 (w * 0.52, 1.42, 0.06)))
    o.append(_bx(GLOW * 0.92 if lit else np.array([0.55, 0.52, 0.46]),
                 L(-w * 0.14, 1.42, d / 2 + 0.05), (w * 0.47, 1.28, 0.05), matte=lit))
    for m in (-0.10, -0.03, 0.03, 0.10):
        o.append(_bx(np.array([0.26, 0.23, 0.21]), L(-w * 0.14 + w * m * 1.9, 1.42, d / 2 + 0.08),
                     (0.05, 1.30, 0.04)))
    o.append(_bx(WOOD_D, L(w * 0.34, 1.05, d / 2 + 0.03), (0.92, 2.00, 0.10)))
    o.append(_bx(np.array([0.78, 0.70, 0.52]), L(w * 0.34, 1.12, d / 2 + 0.09), (0.11, 0.11, 0.05)))
    # awning over the window
    o.append(_bx(awning, L(-w * 0.06, 2.32, d / 2 + 0.30), (w * 0.72, 0.07, 0.9), rot=(-0.22, ry, 0)))
    # upper window
    o.append(_bx(np.array([0.30, 0.30, 0.28]), L(-w * 0.18, h * 0.78, d / 2 + 0.02), (1.0, 0.9, 0.05)))
    o.append(_bx(np.array([0.60, 0.66, 0.64]), L(-w * 0.18, h * 0.78, d / 2 + 0.05),
                 (0.92, 0.82, 0.04), matte=True))
    return o


def signpost(pos, h=2.9):
    x, y, z = pos
    return [_cy(WOOD_D, (x, y, z), (0.07, h, 0.07)),
            _bx(WOOD, (x, y + h - 0.10, z), (0.58, 0.42, 0.05), rot=(0, 0.0, 0))]


def scooter(pos, ry=0.0, col=None, wheel_spin=0.0):
    """A little step-through scooter, the kind a town advertises with a crossed-out price."""
    x, y, z = pos
    col = col if col is not None else np.array([0.44, 0.50, 0.46])
    c, s = math.cos(ry), math.sin(ry)

    def L(px, py, pz):
        return (x + px * c + pz * s, y + py, z - px * s + pz * c)

    o = []
    for sx, r in ((-0.34, 0.20), (0.34, 0.20)):
        o.append(put(TO_V, TO_F, np.array([0.18, 0.17, 0.17]), L(sx, r, 0), (r, r, r),
                     rot=(math.pi / 2, 0, wheel_spin)))
        o.append(put(TO_V, TO_F, np.array([0.62, 0.56, 0.44]), L(sx, r, 0), (0.045, 0.045, 0.045),
                     rot=(math.pi / 2, 0, wheel_spin)))
    o.append(_sh(col, L(0, 0.42, 0), (0.30, 0.24, 0.20)))
    o.append(_sh(col, L(-0.16, 0.52, 0), (0.24, 0.14, 0.18)))
    o.append(_bx(np.array([0.30, 0.28, 0.26]), L(-0.20, 0.62, 0), (0.34, 0.07, 0.26)))
    o.append(_bx(DARK, L(0.30, 0.56, 0), (0.10, 0.34, 0.08), rot=(0, 0, -0.35)))
    o.append(_bx(DARK, L(0.36, 0.78, 0), (0.44, 0.045, 0.045)))
    o.append(_sh(GLOW * 0.9, L(0.38, 0.74, 0), (0.06, 0.06, 0.06), sub=0, cast=False))
    return o


def helmet(pos, ry=0.0, col=None):
    x, y, z = pos
    col = col if col is not None else np.array([0.60, 0.34, 0.28])
    return [_sh(col, (x, y + 0.16, z), (0.17, 0.15, 0.19)),
            _bx(np.array([0.30, 0.30, 0.30]), (x, y + 0.11, z + 0.17), (0.24, 0.09, 0.05)),
            _sh(col, (x, y + 0.30, z - 0.01), (0.09, 0.05, 0.12), sub=0)]


def pedestal(pos, h=0.5):
    x, y, z = pos
    return [_cy(np.array([0.60, 0.54, 0.46]), (x, y, z), (0.34, h, 0.34))]
