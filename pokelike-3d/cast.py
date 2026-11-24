"""The cast — three original characters (no existing franchise designs).

Everything is built from spheres, cones and boxes so it can be animated by numbers.
Units: 1.0 = 1 metre, +Y up, the character faces +Z.
"""
import math
import numpy as np
from cel3d import Part, Model, T, S, R

# ---- palette
EMBER = (0.93, 0.42, 0.20)
EMBER_DARK = (0.62, 0.24, 0.12)
CREAM = (0.97, 0.92, 0.80)
INK = (0.09, 0.08, 0.09)
FLAME = (1.0, 0.62, 0.24)
SLATE = (0.30, 0.35, 0.50)
SLATE_DARK = (0.18, 0.22, 0.34)
CYAN = (0.45, 0.90, 1.0)
BEAK = (0.94, 0.76, 0.30)
SKIN = (0.86, 0.66, 0.52)
HAIR = (0.10, 0.08, 0.08)
JACKET = (0.90, 0.44, 0.28)
JEANS = (0.30, 0.35, 0.48)


def _part(kind, color, mat, emissive=0.0, subdiv=2, shade=1.0):
    return Part(kind, mat, color, emissive=emissive, subdiv=subdiv, shade=shade)


# ---------------------------------------------------------------- Angaar (fire pup)
def angaar(t=0.0, bounce=0.0, lean=0.0, ear=0.0, tail=0.0, blink=0.0, flame=1.0, look=0.0):
    """Fire pup. Total height ~1.36 with the ears. Faces +Z."""
    p = []
    y0 = bounce
    breathe = 1.0 + 0.02 * math.sin(t * 2.1)
    by = 0.56 + y0
    # torso
    p.append(_part("sphere", EMBER, T(0, by, -0.02) @ S(0.40, 0.38 * breathe, 0.46), subdiv=3))
    # cream chest
    p.append(_part("sphere", CREAM, T(0, by - 0.16, 0.30) @ S(0.115, 0.135, 0.10)))
    # head, tipped by `lean`
    hd = T(0, 1.02 + y0, 0.02) @ R("z", -lean * 14)
    p.append(_part("sphere", EMBER, hd @ S(0.35, 0.33, 0.33), subdiv=3))
    # muzzle + nose
    p.append(_part("sphere", CREAM, hd @ T(0, -0.10, 0.27) @ S(0.125, 0.095, 0.115)))
    p.append(_part("sphere", INK, hd @ T(0, -0.045, 0.375) @ S(0.05, 0.038, 0.035)))
    # ears: cones, angled up and slightly out
    for sx in (-1, 1):
        p.append(_part("cone", EMBER, hd @ T(sx * 0.19, 0.24, -0.02) @ R("x", -8)
                       @ R("z", sx * (12 + ear * 22)) @ S(0.085, 0.30, 0.065)))
        p.append(_part("cone", EMBER_DARK, hd @ T(sx * 0.175, 0.29, 0.02) @ R("x", -14)
                       @ R("z", sx * (12 + ear * 22)) @ S(0.045, 0.13, 0.035)))
    # eyes (blink squashes them to a slit)
    for sx in (-1, 1):
        p.append(_part("sphere", CREAM, hd @ T(sx * 0.145, 0.075, 0.275) @ S(0.065, 0.075 * (1 - 0.85 * blink), 0.045)))
        if blink < 0.6:
            p.append(_part("sphere", INK, hd @ T(sx * 0.145 + 0.012 + look * 0.02, 0.075, 0.30) @ S(0.038, 0.045, 0.03)))
    # legs
    for sx in (-1, 1):
        for sz in (0.20, -0.20):
            p.append(_part("sphere", EMBER_DARK, T(sx * 0.16, 0.10 + y0, sz) @ S(0.07, 0.095, 0.075)))
    # tail: cone back-and-up, flame at the tip
    tip = T(0, by + 0.10, -0.40) @ R("x", -40) @ R("y", 6 * math.sin(tail + t))
    p.append(_part("cone", EMBER, tip @ S(0.10, 0.36, 0.09)))
    flick = 1.0 + 0.13 * math.sin(t * 9.0) + 0.09 * math.sin(t * 13.7)
    p.append(_part("sphere", FLAME, T(0.10, by + 0.66, -0.30) @ S(0.13 * flick * flame, 0.26 * flick * flame, 0.12),
                   emissive=0.85))
    p.append(_part("sphere", (1.0, 0.86, 0.50), T(0.10, by + 0.72, -0.28) @ S(0.065 * flame, 0.13 * flame, 0.065),
                   emissive=1.0))
    return Model(p)


# ---------------------------------------------------------------- Baadal (storm hawk)
def baadal(t=0.0, flap=0.0, dive=0.0, y=0.0, bank=0.0):
    """Storm hawk. flap 0..1 drives the wing angle; dive tips the body forward."""
    p = []
    body = T(0, 1.05 + y, 0) @ R("x", -dive * 44) @ R("z", bank)
    p.append(_part("sphere", SLATE, body @ S(0.26, 0.31, 0.46), subdiv=3))
    p.append(_part("sphere", SLATE_DARK, body @ T(0, -0.05, 0.18) @ S(0.175, 0.21, 0.18)))
    # head + hooked beak
    p.append(_part("sphere", SLATE, body @ T(0, 0.30, 0.34) @ S(0.26, 0.25, 0.25), subdiv=3))
    p.append(_part("cone", BEAK, body @ T(0, 0.27, 0.52) @ R("x", 108) @ S(0.075, 0.24, 0.06)))
    p.append(_part("cone", BEAK, body @ T(0, 0.19, 0.53) @ R("x", 150) @ S(0.045, 0.08, 0.04)))
    # crest: two swept feathers
    for sx in (-1, 1):
        p.append(_part("cone", SLATE_DARK, body @ T(sx * 0.08, 0.40, 0.28) @ R("x", -34)
                       @ R("z", sx * 16) @ S(0.05, 0.26, 0.035)))
    # eyes: small, cyan, emissive — the storm inside
    for sx in (-1, 1):
        p.append(_part("sphere", INK, body @ T(sx * 0.11, 0.31, 0.495) @ S(0.05, 0.055, 0.025)))
        p.append(_part("sphere", CYAN, body @ T(sx * 0.11, 0.31, 0.515) @ S(0.028), emissive=1.0))
    # wings: three tapered segments per side, sweeping back as they go out
    for sx in (-1, 1):
        ang = -26 - 34 * flap
        root = body @ T(sx * 0.26, 0.08 + 0.10 * flap, -0.02) @ R("z", sx * ang)
        p.append(_part("box", SLATE, root @ T(sx * 0.22, 0, 0) @ S(0.44, 0.055, 0.30)))
        mid = root @ T(sx * 0.44, 0, -0.05) @ R("z", sx * 9) @ R("y", sx * -8)
        p.append(_part("box", SLATE, mid @ T(sx * 0.20, 0, 0) @ S(0.40, 0.045, 0.24)))
        tip = mid @ T(sx * 0.40, 0, -0.06) @ R("z", sx * 12) @ R("y", sx * -10)
        p.append(_part("box", SLATE_DARK, tip @ T(sx * 0.16, 0, 0) @ S(0.32, 0.035, 0.16)))
    # tail fan
    p.append(_part("box", SLATE_DARK, body @ T(0, -0.06, -0.52) @ R("x", 8) @ S(0.24, 0.04, 0.34)))
    p.append(_part("box", SLATE, body @ T(0, -0.04, -0.60) @ R("x", 8) @ S(0.12, 0.035, 0.26)))
    # talons, only in a dive
    if dive > 0.15:
        for sx in (-1, 1):
            p.append(_part("cone", BEAK, body @ T(sx * 0.11, -0.30, 0.04) @ R("x", 176) @ S(0.045, 0.16, 0.035)))
    return Model(p)


# ---------------------------------------------------------------- Ravi (the trainer)
def ravi(t=0.0, walk=0.0, arm=0.0, look=0.0):
    """A twelve-year-old in a coral jacket. Blocky on purpose — reads at phone size."""
    p = []
    swing = math.sin(walk * 7.0)
    p.append(_part("box", (0.10, 0.09, 0.10), T(-0.11, 0.05, 0.03) @ S(0.20, 0.10, 0.30)))   # shoes
    p.append(_part("box", (0.10, 0.09, 0.10), T(0.11, 0.05, 0.03) @ S(0.20, 0.10, 0.30)))
    p.append(_part("box", JEANS, T(-0.11, 0.36, 0) @ R("x", 7 * swing) @ S(0.17, 0.62, 0.19)))
    p.append(_part("box", JEANS, T(0.11, 0.36, 0) @ R("x", -7 * swing) @ S(0.17, 0.62, 0.19)))
    p.append(_part("box", JACKET, T(0, 1.00, 0) @ S(0.38, 0.60, 0.23)))
    p.append(_part("box", (0.97, 0.93, 0.86), T(0, 1.00, 0.13) @ S(0.035, 0.58, 0.02)))      # zip
    p.append(_part("box", (0.22, 0.26, 0.36), T(0, 0.70, 0) @ S(0.40, 0.10, 0.24)))            # hem
    for sx in (-1, 1):
        p.append(_part("box", JACKET, T(sx * 0.27, 1.02, 0.02) @ R("x", -arm * 68) @ S(0.13, 0.52, 0.14)))
        p.append(_part("sphere", SKIN, T(sx * 0.27, 0.70 + arm * 0.36, 0.02 + arm * 0.30) @ S(0.075)))
    p.append(_part("sphere", SKIN, T(0, 1.42, 0.02) @ S(0.195, 0.205, 0.19)))
    p.append(_part("sphere", HAIR, T(0, 1.52, -0.01) @ S(0.205, 0.15, 0.20)))
    p.append(_part("box", HAIR, T(0, 1.545, 0.135) @ S(0.30, 0.075, 0.10)))                    # fringe
    for sx in (-1, 1):
        p.append(_part("sphere", (0.99, 0.98, 0.96), T(sx * 0.078 + look * 0.02, 1.432, 0.148) @ S(0.050, 0.058, 0.020)))
        p.append(_part("sphere", INK, T(sx * 0.078 + look * 0.025, 1.432, 0.165) @ S(0.026, 0.036, 0.016)))
        p.append(_part("box", HAIR, T(sx * 0.078 + look * 0.02, 1.500, 0.170) @ S(0.070, 0.013, 0.02)))
    p.append(_part("box", (0.45, 0.16, 0.14), T(0, 1.372, 0.172) @ S(0.055, 0.014, 0.015)))     # mouth
    return Model(p)


# ---------------------------------------------------------------- props
def rock(x=0.0, z=0.0, s=1.0, h=0.0):
    return Model([_part("sphere", (0.21, 0.20, 0.21), T(x, h - 0.12 * s, z) @ S(0.40 * s, 0.26 * s, 0.34 * s), subdiv=3),
                  _part("sphere", (0.16, 0.15, 0.17), T(x + 0.22 * s, h - 0.17 * s, z - 0.12 * s)
                        @ S(0.20 * s, 0.14 * s, 0.18 * s), subdiv=3)])


def ember_lamp(x=0.0, y=0.0, z=0.0, s=1.0, t=0.0):
    flick = 1.0 + 0.12 * math.sin(t * 8.0)
    return Model([_part("sphere", FLAME, T(x, y, z) @ S(0.10 * s * flick, 0.16 * s * flick, 0.10 * s), emissive=1.0),
                  _part("sphere", (1.0, 0.86, 0.55), T(x, y + 0.03 * s, z) @ S(0.05 * s, 0.09 * s, 0.05 * s),
                        emissive=1.0)])
