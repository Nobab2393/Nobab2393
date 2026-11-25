"""Cast for অন্ধকার পাঠ (DARK LESSON) — three original characters.

Built from the same primitives as the fire-pup film (sphere / cone / box), so every
pose is a function of numbers: nothing here is a sprite or a baked animation.
Units: 1.0 = 1 metre, +Y up, characters face +Z.
"""
import math
import numpy as np


def lerp(a, b, k):
    return a + (b - a) * k

from cel3d import Part, Model, T, S, R

# ---- palette (night, cold, one warm accent)
INK = (0.055, 0.050, 0.065)
INK2 = (0.10, 0.09, 0.115)
IRON = (0.14, 0.13, 0.16)
IRON_HI = (0.26, 0.25, 0.30)
VOID = (0.42, 0.62, 1.00)          # the borrowed light: cold blue
VOID2 = (0.62, 0.42, 1.00)         # …and its violet edge
SKIN = (0.82, 0.62, 0.48)
SKIN_D = (0.62, 0.44, 0.35)
HAIR = (0.10, 0.085, 0.10)
SHIRT = (0.86, 0.84, 0.78)
SHAWL = (0.24, 0.17, 0.21)
PANTS = (0.17, 0.18, 0.24)
WAX = (0.93, 0.89, 0.76)
GOLD = (0.95, 0.76, 0.34)
PALE = (0.86, 0.93, 1.0)
EMBER = (1.0, 0.66, 0.30)          # his own candle — the only warm light in the film


def _part(kind, color, mat, emissive=0.0, subdiv=2, shade=1.0, rim=True):
    return Part(kind, mat, color, emissive=emissive, subdiv=subdiv, shade=shade, rim=rim)


def _ball(color, mat, r=None, subdiv=2, **kw):
    """A sphere written as (radius, matrix) — or with the scale already in `mat`."""
    return _part("sphere", color, mat if r is None else mat @ S(r), subdiv=subdiv, **kw)


def _egg(color, mat, rx=None, ry=None, rz=None, subdiv=2, **kw):
    """A sphere already carrying its own scale in `mat`."""
    if ry is None:
        return _part("sphere", color, mat, subdiv=subdiv, **kw)
    return _part("sphere", color, mat @ S(rx, ry, rz), subdiv=subdiv, **kw)


# ---------------------------------------------------------------- Ayan (the boy)
def ayan(t=0.0, walk=0.0, arm=0.0, look=0.0, head=0.0, candle=0.0, blink=0.0, slump=0.0):
    """Ayan, 12. Height ~1.46. `arm` raises his right hand; `candle` lights what it holds."""
    p = []
    swing = math.sin(walk * math.pi * 2) * 20 if walk else 0.0
    breathe = 1.0 + 0.015 * math.sin(t * 1.9)
    bend = 5 * slump

    # legs + sandals
    for sx in (-1, 1):
        p.append(_part("box", PANTS, T(sx * 0.098, 0.33, 0) @ R("x", sx * swing * 0.45 + bend * 0.25)
                       @ S(0.115, 0.54, 0.135)))
        p.append(_part("box", INK, T(sx * 0.092, 0.032, 0.03) @ S(0.155, 0.075, 0.24)))

    # hips, torso (rounded, tapered) — spheres, not boxes: this is what makes it read as a body
    p.append(_egg(PANTS, T(0, 0.66, 0) @ S(0.168, 0.125, 0.138)))
    p.append(_egg(SHIRT, T(0, 0.90, 0) @ S(0.183, 0.25 * breathe, 0.142)))
    p.append(_egg(SHIRT, T(0, 1.045, 0) @ S(0.185, 0.145, 0.15)))
    p.append(_part("box", INK2, T(0, 0.655, 0) @ S(0.185, 0.055, 0.155)))          # belt

    # scarf: one dark ring under the chin, one end hanging down the chest
    p.append(_egg(SHAWL, T(0, 1.135, 0) @ S(0.132, 0.055, 0.122)))
    p.append(_part("box", SHAWL, T(0.062, 1.02, 0.118) @ R("z", 8) @ S(0.048, 0.16, 0.028)))

    # arms — chains, so the hand (and whatever it holds) is exact
    hands = {}
    for sx in (-1, 1):
        lift = arm if sx > 0 else 0.0
        sh = T(sx * 0.185, 1.075, 0) @ R("z", sx * (10 + 58 * lift)) @ R("x", -swing * 0.4 + bend * 0.4)
        p.append(_egg(SHIRT, sh @ T(0, -0.10, 0) @ S(0.072, 0.125, 0.078)))
        el = sh @ T(0, -0.215, 0) @ R("z", sx * (12 + 22 * lift))
        p.append(_egg(SHIRT, el @ T(0, -0.098, 0) @ S(0.062, 0.115, 0.068)))
        hm = el @ T(0, -0.20, 0.01)
        p.append(_ball(SKIN, hm @ S(0.056), subdiv=2))
        hands[sx] = hm

    # head
    hd = T(0, 1.235 + 0.02 * slump, 0.008) @ R("x", bend) @ R("y", look * 24) @ R("z", -head)
    p.append(_part("box", SKIN_D, hd @ T(0, -0.085, 0) @ S(0.075, 0.08, 0.075)))       # neck
    p.append(_egg(SKIN, hd @ S(0.148, 0.165, 0.145), subdiv=3))
    p.append(_egg(HAIR, hd @ T(0, 0.042, -0.024) @ S(0.157, 0.152, 0.152), subdiv=3))
    p.append(_egg(HAIR, hd @ T(0, 0.100, 0.020) @ S(0.140, 0.062, 0.118), subdiv=3))
    for sx in (-1, 1):                                                                  # anime eyes
        p.append(_egg(PALE, hd @ T(sx * 0.058, 0.004, 0.126) @ S(0.036, 0.042 * (1 - 0.85 * blink), 0.020)))
        if blink < 0.6:
            p.append(_egg(INK, hd @ T(sx * 0.058, 0.0, 0.145) @ S(0.019, 0.022, 0.013)))
    p.append(_part("box", SKIN_D, hd @ T(0, -0.062, 0.134) @ S(0.040, 0.011, 0.018)))    # mouth

    # the candle he carries — placed from the hand, not guessed
    if candle > 0.01:
        hm = hands[1]
        p.append(_part("box", WAX, hm @ T(0, 0.075, 0.02) @ S(0.042, 0.15, 0.042)))
        if candle > 0.5:
            fl = 0.85 + 0.15 * math.sin(t * 9.0)
            p.append(_part("cone", EMBER, hm @ T(0, 0.22, 0.02) @ S(0.036, 0.13 * fl, 0.036),
                           emissive=0.95, subdiv=1, rim=False))
    return Model(p)


# ---------------------------------------------------------------- the black lantern
def lantern(t=0.0, lit=1.0, tilt=0.0, float_=0.0):
    """The black lantern. Cold flame when `lit` is high; dead iron when it is 0."""
    p = []
    y0 = float_ * (0.02 + 0.03 * math.sin(t * 1.6))
    base = T(0, y0, 0) @ R("z", tilt)

    p.append(_part("box", IRON, base @ T(0, 0.00, 0) @ S(0.28, 0.09, 0.28)))            # base
    p.append(_part("box", IRON, base @ T(0, 0.42, 0) @ S(0.28, 0.07, 0.28)))            # top plate
    for sx in (-1, 1):                                                                  # four posts
        for sz in (-1, 1):
            p.append(_part("box", IRON_HI, base @ T(sx * 0.13, 0.21, sz * 0.13) @ S(0.032, 0.42, 0.032)))
    p.append(_part("cone", IRON, base @ T(0, 0.46, 0) @ S(0.27, 0.20, 0.27), subdiv=1))  # cap
    p.append(_part("box", IRON_HI, base @ T(0, 0.68, 0) @ S(0.045, 0.10, 0.045)))        # ring post

    # the flame inside the glass
    if lit > 0.02:
        k = lit
        h = 0.20 + 0.045 * math.sin(t * 11.0)
        p.append(_part("cone", VOID, base @ T(0, 0.24, 0) @ S(0.062 * k, h * k, 0.062 * k),
                       emissive=1.0, subdiv=1, rim=False))
        p.append(_egg(PALE, base @ T(0, 0.20, 0) @ S(0.055 * k, 0.068 * k, 0.055 * k),
                      emissive=1.0, rim=False))
    return Model(p)


# ---------------------------------------------------------------- the shade
def shade(t=0.0, high=1.0, reach=0.0, eyes=1.0, sway=0.0):
    """A tall thing made of borrowed light. No feet — it tapers into the floor."""
    p = []
    s = 0.86 + 0.22 * high
    sway *= math.sin(t * 0.9) * 4
    root = T(0, 0, 0) @ R("z", sway)
    H = 2.10 * s
    # one continuous body: wide shoulders, apex on the floor
    p.append(_part("cone", INK, root @ T(0, H, 0) @ R("x", 180) @ S(0.46 * s, H, 0.34 * s),
                   subdiv=3, rim=False))
    p.append(_part("sphere", INK, root @ T(0, H - 0.06 * s, 0) @ S(0.44 * s, 0.20 * s, 0.32 * s), subdiv=3, rim=False))
    # neck + head
    hd = root @ T(0, H + 0.24 * s, 0.015) @ R("x", -reach * 8)
    p.append(_egg(INK, hd @ S(0.20 * s, 0.26 * s, 0.19 * s), subdiv=3, rim=False))
    if eyes > 0.02:
        for sx in (-1, 1):
            p.append(_egg(PALE, hd @ T(sx * 0.072, 0.02, 0.165 * s)
                          @ S(0.038 * eyes, 0.026 * eyes, 0.015), emissive=0.9, rim=False))
    # arms: long, thin, reaching
    for sx in (-1, 1):
        ang = (26 + 56 * reach) if sx > 0 else 12
        p.append(_part("box", INK, root @ T(sx * 0.34 * s, H - 0.22 * s, 0) @ R("z", -sx * ang)
                       @ R("x", -8 - 22 * reach) @ S(0.075 * s, 0.80 * s, 0.08 * s), subdiv=2, rim=False))
        ex = sx * (0.34 + 0.80 * math.sin(math.radians(ang))) * s
        ey = (H - 0.22 * s) - 0.80 * math.cos(math.radians(ang)) * s
        p.append(_ball(INK, root @ T(ex, ey, 0.16 * reach) @ S(0.065 * s), subdiv=2, rim=False))
    return Model(p)


# ---------------------------------------------------------------- props
def coin(t=0.0, spin=0.0):
    return Model([_part("box", GOLD, T(0, 0, 0) @ R("y", spin * 360 + t * 90) @ S(0.075, 0.075, 0.012),
                        subdiv=1, rim=True)])


def photo(t=0.0, fade=1.0):
    """A photograph: a pale frame around a fading picture."""
    p = [_part("box", (0.86, 0.84, 0.78), T(0, 0, 0) @ S(0.30, 0.36, 0.012))]
    if fade > 0.02:
        # a memory has a warm inside; as it is taken it washes out to nothing
        warm = (0.90, 0.62, 0.52)
        col = tuple(lerp(warm[i], 0.86, 1 - fade) for i in range(3))
        p.append(_part("box", col, T(0, 0, 0.012) @ S(0.24 * fade, 0.30 * fade, 0.004)))
    return Model(p)
