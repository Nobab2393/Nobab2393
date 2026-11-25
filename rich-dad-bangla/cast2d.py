"""cast2d.py — the four characters, drawn flat: ink outline, warm fill, cream paper.

Everything is expressed in a 1920x1080 design space and scaled by S when drawn, so a
2x canvas gives clean outlines at 1080p. No textures, no gradients: the look of the
character sheets is exactly a flat fill inside a brown line.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

INK = (59, 42, 30)

# palette, straight off the sheets
CREAM = (247, 239, 222)
CREAM_D = (232, 219, 196)
HILL = (224, 205, 173)
HILL_D = (206, 183, 148)
WALL = (223, 196, 158)
WALL_D = (201, 168, 128)
ROOF = (176, 108, 74)
ROOF_D = (146, 86, 58)
GOLD = (201, 162, 39)

EAGLE = (201, 138, 46)
EAGLE_D = (169, 111, 34)
EAGLE_L = (232, 190, 120)
EHEAD = (247, 243, 234)
BEAK = (242, 178, 51)
BEAK_D = (214, 148, 38)
VEST = (42, 74, 115)
VEST_L = (58, 96, 143)
PEN = (250, 250, 250)

GREY = (168, 168, 168)
GREY_L = (207, 207, 207)
GREY_D = (138, 138, 138)
EARPINK = (231, 198, 198)
GREEN = (61, 194, 68)
GREEN_D = (44, 155, 52)
SATCH = (139, 94, 80)
SATCH_D = (112, 73, 62)
NOSE = (255, 168, 168)

FOX = (228, 112, 42)
FOX_D = (192, 88, 30)
FOXC = (251, 235, 211)
PURPLE = (107, 74, 142)
APRON = (232, 211, 168)
APRON_D = (201, 169, 124)

TUR = (143, 160, 90)
TUR_D = (111, 127, 66)
SHELL = (94, 107, 55)
SHELL_D = (70, 81, 42)
PLAST = (217, 201, 138)
STICK = (139, 90, 43)
BOOKS = [(178, 74, 58), (94, 122, 74), (150, 106, 62)]


class Pen:
    """Draws in design pixels on a supersampled canvas."""

    def __init__(self, img, S=2, ox=0.0, oy=0.0):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.S = S
        self.ox, self.oy = ox, oy

    def P(self, x, y):
        return ((x + self.ox) * self.S, (y + self.oy) * self.S)

    def pts(self, pts):
        return [self.P(x, y) for x, y in pts]

    def poly(self, pts, fill, ow=4.5, oc=INK):
        p = self.pts(pts)
        self.d.polygon(p, fill=fill)
        if ow:
            self.d.line(p + [p[0]], fill=oc, width=max(1, int(ow * self.S)), joint="curve")

    def ell(self, box, fill, ow=4.5, oc=INK):
        x0, y0, x1, y1 = box
        x0, x1 = (x0, x1) if x0 <= x1 else (x1, x0)
        y0, y1 = (y0, y1) if y0 <= y1 else (y1, y0)
        b = [self.P(x0, y0), self.P(x1, y1)]
        self.d.ellipse(b, fill=fill,
                       outline=oc if ow else None, width=max(1, int(ow * self.S)))

    def line(self, pts, col=INK, w=4.0):
        self.d.line(self.pts(pts), fill=col, width=max(1, int(w * self.S)), joint="curve")

    def arc(self, box, a0, a1, col=INK, w=4.0):
        x0, y0, x1, y1 = box
        self.d.arc([self.P(x0, y0)[0], self.P(x0, y0)[1], self.P(x1, y1)[0], self.P(x1, y1)[1]],
                   a0, a1, fill=col, width=max(1, int(w * self.S)))

    def ring(self, box, w, col):
        x0, y0, x1, y1 = box
        self.d.ellipse([self.P(x0, y0)[0], self.P(x0, y0)[1],
                        self.P(x1, y1)[0], self.P(x1, y1)[1]],
                       outline=col, width=max(1, int(w * self.S)))

    def rrect(self, box, r, fill, ow=4.5, oc=INK):
        x0, y0, x1, y1 = box
        x0, x1 = (x0, x1) if x0 <= x1 else (x1, x0)
        y0, y1 = (y0, y1) if y0 <= y1 else (y1, y0)
        self.d.rounded_rectangle([self.P(x0, y0)[0], self.P(x0, y0)[1],
                                  self.P(x1, y1)[0], self.P(x1, y1)[1]],
                                 radius=r * self.S, fill=fill,
                                 outline=oc if ow else None,
                                 width=max(1, int(ow * self.S)) if ow else 0)


def _eye(p, x, y, r, iris=(122, 75, 42), lid=0.0, look=(0, 0), white=(252, 250, 244)):
    """A cartoon eye: white, iris, pupil, one highlight. lid closes from the top."""
    p.ell([x - r, y - r * 1.05, x + r, y + r * 1.05], white, 3.2)
    ix, iy = x + look[0] * r * 0.3, y + look[1] * r * 0.3
    if lid < 0.9:
        p.ell([ix - r * 0.62, iy - r * 0.62, ix + r * 0.62, iy + r * 0.62], iris, 0)
        p.ell([ix - r * 0.30, iy - r * 0.30, ix + r * 0.30, iy + r * 0.30], (32, 22, 16), 0)
        p.ell([ix - r * 0.30, iy - r * 0.42, ix + r * 0.02, iy - r * 0.10], (255, 255, 255), 0)
    if lid > 0.02:
        h = r * 1.15 * lid
        p.rrect([x - r * 1.05, y - r * 1.1, x + r * 1.05, y - r * 1.1 + h], r * 0.3, (0, 0, 0), 0)
    p.arc([x - r, y - r * 1.05, x + r, y + r * 1.05], 200, 340, INK, 3.0)


def _clip_lid(p, x, y, r, lid, skin):
    """Paints the lid back over the eye with the character's own colour."""
    if lid > 0.02:
        h = r * 1.2 * lid
        p.ell([x - r * 1.15, y - r * 1.15, x + r * 1.15, y - r * 1.15 + h * 2], skin, 0)


# ---------------------------------------------------------------- helpers
def capsule(p, x0, y0, x1, y1, w, fill, ow=4.2, oc=INK):
    """A rounded limb between two points."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    ang = math.atan2(dy, dx)
    pts = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny)]
    for k in range(7):
        a = ang + math.pi / 2 - math.pi * k / 6
        pts.append((x1 + math.cos(a) * w / 2, y1 + math.sin(a) * w / 2))
    pts.append((x1 - nx, y1 - ny))
    pts.append((x0 - nx, y0 - ny))
    for k in range(7):
        a = ang - math.pi / 2 - math.pi * k / 6
        pts.append((x0 + math.cos(a) * w / 2, y0 + math.sin(a) * w / 2))
    p.poly(pts, fill, ow, oc)


def ear(p, x, y0, x1, y1, w, fill, inner=None, ow=4.2):
    """A long rounded ear, tapering toward the tip."""
    capsule(p, x, y0, x1, y1, w, fill, ow)
    if inner:
        capsule(p, x + (x1 - x) * 0.15, y0 + (y1 - y0) * 0.12,
                x1, y1 + (y0 - y1) * 0.18, w * 0.52, inner, 0)


def eye(p, x, y, r, iris=(122, 75, 42), lid=0.0, look=(0, 0), skin=None):
    p.ell([x - r * 1.05, y - r * 1.1, x + r * 1.05, y + r * 1.1], (252, 250, 244), 3.0)
    if lid < 0.92:
        ix, iy = x + look[0] * r * 0.28, y + look[1] * r * 0.28
        p.ell([ix - r * 0.60, iy - r * 0.60, ix + r * 0.60, iy + r * 0.60], iris, 0)
        p.ell([ix - r * 0.28, iy - r * 0.28, ix + r * 0.28, iy + r * 0.28], (34, 24, 18), 0)
        p.ell([ix - r * 0.34, iy - r * 0.40, ix - r * 0.02, iy - r * 0.08], (255, 255, 255), 0)
    if lid > 0.03 and skin:
        p.rrect([x - r * 1.12, y - r * 1.2, x + r * 1.12, y - r * 1.2 + 2 * r * 1.2 * lid],
                0, skin)
        p.arc([x - r * 1.05, y - r * 1.1, x + r * 1.05, y + r * 1.1], 200, 340, INK, 2.8)
    p.arc([x - r * 1.05, y - r * 1.1, x + r * 1.05, y + r * 1.1], 200, 340, INK, 3.0)


# ---------------------------------------------------------------- Rabbit
def rabbit(p, x, y, s=1.0, ears=0.0, blink=0.0, mouth=0.0, look=(0, 0), arm=0.0,
           scarf=True, satchel=True, hops=0.0):
    """y is the ground line; hops lifts the whole figure."""
    y = y - hops
    def T(px, py):
        return (x + px * s, y + py * s)

    # feet
    for sx in (-1, 1):
        p.ell([*T(sx * 36 - 30, -22), *T(sx * 36 + 30, 2)], GREY_D, 4.2)
    # body
    p.ell([*T(-64, -240), *T(64, -46)], GREY, 4.6)
    p.ell([*T(-38, -206), *T(38, -74)], GREY_L, 0)
    # tail
    p.ell([*T(-96, -140), *T(-48, -92)], GREY_L, 4.2)
    # far arm
    p.ell([*T(46, -190), *T(92, -110 - 24 * arm)], GREY, 4.2)
    # satchel strap + bag
    if satchel:
        p.line([T(-44, -196), T(34, -122)], SATCH_D, 8)
        p.rrect([*T(-8, -136), *T(62, -66)], 10, SATCH, 4.2)
        p.rrect([*T(-8, -136), *T(62, -108)], 8, SATCH_D, 4.0)
        p.ell([*T(22, -98), *T(32, -88)], GOLD, 2.6)
    # near arm
    p.ell([*T(-92, -186), *T(-46, -108 + 10 * arm)], GREY, 4.2)
    # ears
    flop = 40 * ears
    for sx in (-1, 1):
        ear(p, T(sx * 26, -330)[0], T(0, -330)[1],
            T(sx * 34 + flop, -470 + 60 * ears)[0], T(0, -470 + 60 * ears)[1],
            40 * s, GREY, EARPINK, 4.2)
    # head
    p.ell([*T(-58, -348), *T(58, -232)], GREY, 4.6)
    # muzzle
    p.ell([*T(-26, -292), *T(26, -256)], GREY_L, 0)
    p.ell([*T(-13, -300), *T(13, -284)], NOSE, 3.2)
    p.line([T(0, -284), T(0, -274)], INK, 2.6)
    if mouth > 0.06:
        p.ell([*T(-15, -276), *T(15, -276 + 20 * mouth)], (122, 64, 58), 2.6)
    else:
        p.arc([*T(-16, -286), *T(0, -270)], 0, 90, INK, 2.6)
        p.arc([*T(0, -286), *T(16, -270)], 90, 180, INK, 2.6)
    for sx in (-1, 1):
        eye(p, T(sx * 27, -312)[0], T(0, -312)[1], 16 * s, lid=blink, look=look, skin=GREY)
        for k in range(3):
            yy = -302 + k * 10
            p.line([T(sx * 40, yy), T(sx * (74 + 8 * k), yy - 8 + k * 5)], INK, 2.2)
    # scarf
    if scarf:
        p.rrect([*T(-56, -252), *T(56, -214)], 16, GREEN, 4.2)
        p.poly([T(30, -222), T(54, -222), T(46, -160), T(26, -166)], GREEN_D, 4.0)
    # satchel above the near arm edge
    return


# ---------------------------------------------------------------- Eagle
def eagle(p, x, y, s=1.0, wings=0.0, blink=0.0, mouth=0.0, tilt=0.0, look=(0, 0),
          legs=True):
    def T(px, py):
        return (x + px * s, y + py * s)

    # legs and talons
    for sx in ((-1, 1) if legs else ()):
        capsule(p, T(sx * 34, -104)[0], T(0, -104)[1], T(sx * 34, -26)[0], T(0, -26)[1],
                30 * s, BEAK_D, 4.2)
        p.ell([*T(sx * 34 - 30, -34), *T(sx * 34 + 34, -2)], BEAK, 4.2)
        for k in (-1, 0, 1):
            p.line([T(sx * 34 + k * 16, -12), T(sx * 34 + k * 24, 2)], INK, 2.6)
    # wings: one silhouette per side, with feather notches at the tip
    for sx in (-1, 1):
        if wings < 0.18:                      # folded: a rounded shoulder mass
            p.ell([*T(sx * 40, -318), *T(sx * 100, -150)], EAGLE_D, 4.4)
        else:
            sp = wings
            tipx = T(sx * (110 + 200 * sp), -300 + 70 * sp)[0]
            tipy = T(0, -238 - 30 * sp)[1]
            base_x = T(sx * 52, 0)[0]
            base_y = T(0, -300)[1]
            top_y = T(0, -330)[1]
            p.poly([(base_x, base_y), (T(sx * 96, -326)[0], top_y), (tipx, tipy),
                    (tipx - sx * 30 * s, tipy + 44 * s), (tipx - sx * 70 * s, tipy + 26 * s),
                    (base_x + sx * 20, T(0, -180)[1])], EAGLE, 4.4)
            for k in range(3):
                px = tipx - sx * (34 + k * 34) * s
                py = tipy + (30 + k * 16) * s
                p.line([(px, py), (px - sx * 22 * s, py + 26 * s)], EAGLE_D, 3.0)
    # body
    p.ell([*T(-84, -318), *T(84, -72)], EAGLE, 4.8)
    # vest
    p.poly([T(-66, -300), T(66, -300), T(72, -128), T(30, -110), T(0, -134),
            T(-30, -110), T(-72, -128)], VEST, 4.6)
    p.poly([T(-24, -300), T(24, -300), T(0, -216)], EAGLE_L, 3.2)
    p.poly([T(-24, -300), T(-6, -300), T(-16, -206)], VEST_L, 2.4)
    p.poly([T(24, -300), T(6, -300), T(16, -206)], VEST_L, 2.4)
    for k in range(4):
        p.ell([*T(-7, -212 + k * 26), *T(7, -198 + k * 26)], GOLD, 2.2)
    # pocket
    p.rrect([*T(30, -244), *T(66, -196)], 5, VEST_L, 3.4)
    p.line([T(42, -242), T(40, -214)], PEN, 4.4)
    p.line([T(54, -240), T(53, -218)], (232, 216, 178), 7.0)
    # head
    p.ell([*T(-62, -430), *T(62, -300)], EHEAD, 4.8)
    # brows
    p.line([T(-44, -392 + 5 * tilt), T(-12, -400)], INK, 5.0)
    p.line([T(12, -400), T(44, -392 + 5 * tilt)], INK, 5.0)
    # beak
    p.poly([T(-34, -376), T(34, -376), T(16, -330), T(-16, -330)], BEAK, 4.4)
    p.poly([T(-18, -332), T(18, -332), T(0, -308)], BEAK_D, 3.6)
    if mouth > 0.06:
        p.poly([T(-12, -318), T(12, -318), T(0, -308 + 8 * mouth)], (110, 58, 44), 2.4)
    # glasses
    for sx in (-1, 1):
        cxd, cyd = T(sx * 26, -382)
        p.ell([T(sx * 26 - 21, -404)[0], T(0, -404)[1], T(sx * 26 + 21, -360)[0],
               T(0, -360)[1]], (252, 250, 244), 0)
        p.ell([*T(sx * 26 - 11, -396), *T(sx * 26 + 11, -370)], (150, 104, 30), 0)
        p.ell([*T(sx * 26 - 5, -390), *T(sx * 26 + 5, -378)], (30, 20, 14), 0)
        p.ell([*T(sx * 26 - 10, -396), *T(sx * 26 - 3, -389)], (255, 255, 255), 0)
        if blink > 0.05:
            p.rrect([T(sx * 26 - 22, -406)[0], T(0, -406)[1], T(sx * 26 + 22, -406 + 46 * blink)[0],
                     T(0, -406 + 46 * blink)[1]], 0, EHEAD)
        p.ring([*T(sx * 26 - 24, -408), *T(sx * 26 + 24, -358)], 3.8, GOLD)
    p.line([T(-4, -384), T(4, -384)], GOLD, 3.6)
    p.line([T(-50, -386), T(-64, -390)], GOLD, 3.2)
    p.line([T(50, -386), T(64, -390)], GOLD, 3.2)


# ---------------------------------------------------------------- Fox
def fox(p, x, y, s=1.0, blink=0.45, mouth=0.0, tilt=0.0, look=(-1, 0), hands=0.0):
    def T(px, py):
        return (x + px * s, y + py * s)

    # tail: one fat crescent, cream tip
    p.poly([T(56, -110), T(96, -120), T(140, -160), T(158, -222), T(148, -268),
            T(122, -292), T(104, -276), T(128, -238), T(134, -196), T(112, -158),
            T(72, -136)], FOX_D, 4.6)
    p.poly([T(146, -290), T(140, -262), T(112, -258), T(100, -282), T(126, -292)], FOXC, 3.4)
    # legs
    for sx in (-1, 1):
        capsule(p, T(sx * 28, -108)[0], T(0, -108)[1], T(sx * 28, -16)[0], T(0, -16)[1],
                32 * s, FOX, 4.2)
        p.ell([*T(sx * 28 - 30, -24), *T(sx * 28 + 30, -2)], FOX_D, 4.2)
    # body + apron
    p.ell([*T(-68, -246), *T(68, -78)], FOX, 4.8)
    p.poly([T(-52, -212), T(52, -212), T(62, -60), T(-62, -60)], APRON, 4.4)
    for k in range(-2, 3):
        p.line([T(k * 19, -210), T(k * 24, -62)], APRON_D, 9.0)
    p.poly([T(-52, -212), T(-34, -212), T(-40, -60), T(-62, -60)], APRON, 0)
    p.rrect([*T(-30, -132), *T(32, -92)], 6, APRON, 3.6)
    p.ring([*T(36, -104), *T(52, -88)], 3.2, GOLD)
    p.line([T(44, -100), T(44, -70)], GOLD, 3.0)
    # arms behind the back
    for sx in (-1, 1):
        capsule(p, T(sx * 56, -208)[0], T(0, -208)[1], T(sx * 30, -140)[0], T(0, -140)[1],
                34 * s, FOX, 4.0)
    # neckerchief
    p.poly([T(-42, -252), T(42, -252), T(30, -220), T(0, -230), T(-30, -220)], PURPLE, 4.2)
    p.poly([T(-10, -228), T(18, -222), T(4, -176)], PURPLE, 3.8)
    # head: skull + snout wedge
    p.poly([T(-54, -318), T(-30, -366), T(30, -366), T(54, -318), T(34, -286),
            T(-34, -286)], FOX, 4.8)
    p.poly([T(-46, -318), T(-84, -300), T(-52, -278)], FOX, 4.0)
    p.poly([T(46, -318), T(84, -300), T(52, -278)], FOX, 4.0)
    p.ell([*T(-34, -312), *T(34, -266)], FOXC, 3.4)
    p.ell([*T(-12, -306), *T(12, -288)], (58, 38, 32), 3.2)
    if mouth > 0.06:
        p.ell([*T(-16, -290), *T(16, -290 + 16 * mouth)], (110, 56, 44), 2.6)
    else:
        p.arc([*T(-20, -300), *T(20, -276)], 20, 160, (58, 38, 32), 3.0)
    # ears
    for sx in (-1, 1):
        p.poly([T(sx * 20, -352), T(sx * 54, -444), T(sx * 66, -344)], FOX, 4.4)
        p.poly([T(sx * 34, -354), T(sx * 54, -420), T(sx * 58, -352)], FOXC, 2.8)
    # eyes: smug, half-lidded
    for sx in (-1, 1):
        cxd, cyd = T(sx * 26, -330)
        p.ell([T(sx * 26 - 16, -344)[0], T(0, -344)[1], T(sx * 26 + 16, -316)[0],
               T(0, -316)[1]], (252, 250, 244), 0)
        p.ell([*T(sx * 26 - 7 + look[0] * 3, -336), *T(sx * 26 + 7 + look[0] * 3, -322)],
              (58, 38, 32), 0)
        p.ell([*T(sx * 26 - 7 + look[0] * 3, -336), *T(sx * 26 - 2 + look[0] * 3, -331)],
              (255, 255, 255), 0)
        lid = max(0.12, blink * 0.5)
        top = T(0, -346 + 30 * lid)[1]
        p.poly([(T(sx * 26 - 17, 0)[0], T(0, -348)[1]), (T(sx * 26 + 17, 0)[0], T(0, -348)[1]),
                (T(sx * 26 + 17, 0)[0], top), (T(sx * 26 - 17, 0)[0], top)], FOX, 0)
        p.line([(T(sx * 26 - 17, 0)[0], top), (T(sx * 26 + 17, 0)[0], top)], INK, 3.4)
    p.line([T(-44, -356 - 5 * tilt), T(-14, -362)], INK, 4.0)
    p.line([T(14, -362), T(46, -352 + 8 * tilt)], INK, 4.0)
    # freckles
    for sx in (-1, 1):
        for k in range(3):
            p.ell([*T(sx * (30 + k * 9) - 3, -300 + k * 7), *T(sx * (30 + k * 9) + 3,
                                                             -294 + k * 7)], FOX_D, 0)


# ---------------------------------------------------------------- Turtle
def turtle(p, x, y, s=1.0, blink=0.0, mouth=0.0, tilt=0.0):
    def T(px, py):
        return (x + px * s, y + py * s)

    # stick
    capsule(p, T(104, -286)[0], T(0, -286)[1], T(116, -4)[0], T(0, -4)[1], 16 * s, STICK, 4.0)
    # legs
    for sx in (-1, 1):
        capsule(p, T(sx * 34, -110)[0], T(0, -110)[1], T(sx * 34, -12)[0], T(0, -12)[1],
                52 * s, TUR, 4.4)
        p.ell([*T(sx * 34 - 36, -26), *T(sx * 34 + 36, -2)], TUR_D, 4.0)
    # shell: dome behind, rim, scutes
    p.ell([*T(-104, -326), *T(104, -120)], SHELL, 5.0)
    p.poly([T(-104, -220), T(-86, -120), T(-40, -110), T(0, -104), T(40, -110),
            T(86, -120), T(104, -220)], SHELL_D, 4.2)
    for k in range(3):
        p.arc([*T(-74 + k * 8, -300 + k * 26), *T(74 - k * 8, -170 - k * 10)],
              200, 340, SHELL_D, 3.2)
    # books strapped to the shell
    for k, col in enumerate(BOOKS):
        yy = -352 - k * 26
        p.rrect([*T(-46, yy - 22), *T(52, yy)], 4, col, 3.6)
        p.line([T(-32, yy - 12), T(38, yy - 12)], (242, 234, 212), 3.4)
    p.line([T(-6, -404), T(-14, -226)], (198, 176, 138), 5.2)
    # plastron
    p.ell([*T(-62, -216), *T(62, -104)], PLAST, 4.2)
    p.line([T(-32, -206), T(-34, -114)], (178, 160, 104), 2.8)
    p.line([T(32, -206), T(34, -114)], (178, 160, 104), 2.8)
    # neck + head
    capsule(p, T(0, -246)[0], T(0, -246)[1], T(0, -300)[0], T(0, -300)[1], 62 * s, TUR, 3.6)
    p.ell([*T(-56, -356), *T(56, -242)], TUR, 4.8)
    p.arc([*T(-34, -344), *T(-4, -318)], 20, 160, TUR_D, 2.4)
    p.arc([*T(6, -348), *T(36, -322)], 20, 160, TUR_D, 2.4)
    # eyes + half-moon glasses
    for sx in (-1, 1):
        p.ell([*T(sx * 24 - 13, -322), *T(sx * 24 + 13, -294)], (250, 248, 240), 0)
        p.ell([*T(sx * 24 - 6, -314), *T(sx * 24 + 6, -302)], (48, 44, 32), 0)
        if blink > 0.05:
            p.rrect([T(sx * 24 - 14, -323)[0], T(0, -323)[1],
                     T(sx * 24 + 14, -323 + 28 * blink)[0], T(0, -323 + 28 * blink)[1]], 0, TUR)
        p.arc([*T(sx * 24 - 20, -322), *T(sx * 24 + 20, -286)], 185, 355, INK, 3.6)
    p.line([T(-7, -300), T(7, -300)], INK, 3.2)
    # muzzle + smile
    p.ell([*T(-22, -292), *T(22, -266)], (167, 180, 116), 0)
    p.arc([*T(-24, -292), *T(24, -262)], 15, 165, INK, 3.4)
    p.ell([*T(-3, -292), *T(3, -286)], TUR_D, 0)
    p.ell([*T(-3, -280), *T(3, -274)], TUR_D, 0)
    # spots
    for sx, sy in [(-38, -270), (-30, -252), (34, -268), (28, -250)]:
        p.ell([*T(sx - 5, sy - 4), *T(sx + 5, sy + 4)], TUR_D, 0)


# ---------------------------------------------------------------- props
def bench(p, x, y, w=300, col=(150, 106, 70)):
    for sx in (-1, 1):
        p.rrect([x + sx * (w / 2 - 30) - 8, y - 104, x + sx * (w / 2 - 30) + 8, y], 4,
                (126, 88, 58), 3.6)
    p.rrect([x - w / 2, y - 108, x + w / 2, y - 88], 6, col, 4.2)
    p.rrect([x - w / 2, y - 62, x + w / 2, y - 40], 6, col, 4.2)


def lamp(p, x, y, h=420):
    p.rrect([x - 8, y - h, x + 8, y], 4, (96, 84, 74), 3.6)
    p.poly([(x - 44, y), (x + 44, y), (x + 32, y + 12), (x - 32, y + 12)], (96, 84, 74), 3.6)
    p.rrect([x - 32, y - h - 48, x + 32, y - h + 2], 10, (250, 226, 150), 4.0)
    p.poly([(x - 42, y - h - 48), (x + 42, y - h - 48), (x, y - h - 88)], (96, 84, 74), 3.6)


def house(p, x, y, w=260, h=180, wall=WALL, roof=ROOF, win=True, door=True):
    p.rrect([x - w / 2, y - h, x + w / 2, y], 4, wall, 4.2)
    p.poly([(x - w / 2 - 20, y - h + 4), (x + w / 2 + 20, y - h + 4), (x + 0, y - h - 104),
            (x - 0, y - h - 104), (x - 20, y - h - 60), (x - w / 2 + 20, y - h + 4)],
           roof, 4.2)
    if win:
        p.rrect([x - w * 0.34, y - h + 42, x - w * 0.06, y - h + 112], 4, (250, 232, 186), 3.4)
        p.line([(x - w * 0.20, y - h + 42), (x - w * 0.20, y - h + 112)], (200, 170, 120), 3.0)
        p.line([(x - w * 0.34, y - h + 77), (x - w * 0.06, y - h + 77)], (200, 170, 120), 3.0)
    if door:
        p.rrect([x + w * 0.10, y - 118, x + w * 0.34, y], 4, (140, 92, 62), 4.0)


def bicycle(p, x, y, s=1.0):
    r = 46 * s
    for sx in (-1, 1):
        cx = x + sx * 64 * s
        p.ring([cx - r, y - r, cx + r, y + r], 6.0, INK)
        p.ell([cx - 6, y - 6, cx + 6, y + 6], (150, 140, 130), 2.6)
    p.line([(x - 64 * s, y - r), (x - 4 * s, y - 96 * s)], (62, 122, 132), 8)
    p.line([(x - 4 * s, y - 96 * s), (x + 30 * s, y - 12 * s)], (62, 122, 132), 8)
    p.line([(x - 64 * s, y - r), (x - 26 * s, y - 12 * s)], (62, 122, 132), 8)
    p.line([(x - 26 * s, y - 12 * s), (x + 64 * s, y - r)], (62, 122, 132), 8)
    p.line([(x + 30 * s, y - 12 * s), (x + 64 * s, y - r)], (62, 122, 132), 8)
    p.rrect([x - 38 * s, y - 106 * s, x + 2 * s, y - 94 * s], 5, (120, 70, 52), 3.8)
    p.line([(x + 26 * s, y - 94 * s), (x + 46 * s, y - 106 * s)], INK, 6)
    p.rrect([x + 34 * s, y - 116 * s, x + 58 * s, y - 104 * s], 5, (120, 70, 52), 3.6)


def coin(p, x, y, r=16, tilt=1.0, face=GOLD):
    p.ell([x - r, y - r * tilt, x + r, y + r * tilt], face, 3.4)
    if tilt > 0.6:
        p.line([(x, y - r * 0.5), (x, y + r * 0.5)], (170, 132, 30), 2.6)


def card(p, x, y, w=280, h=180, tone=(250, 244, 228)):
    p.rrect([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 10, tone, 4.4)
