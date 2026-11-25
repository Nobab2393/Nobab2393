#!/usr/bin/env python3
"""sheets.py — the delivery art for a character and for a background, drawn by code.

    python3 sheets.py character     -> out/character-sheet.png
    python3 sheets.py background    -> out/background-studies.png
    python3 sheets.py compare       -> out/compare-v1-v2.png

Design doctrine applied here (see 01-doctrine.md):
  1 silhouette before detail · 2 one dominant shape per character, contrasted across the cast ·
  3 head-count is the tone dial · 4 asymmetry + one signature prop · 5 the face must be able to act
  6 background = value structure, then layers · 7 distance = lower contrast + cooler colour ·
  8 the character holds the highest contrast in frame · 9 a near plane and a leading line ·
  10 leave negative space for type.
"""
import math, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from cast2 import Rig, CAST, EXPRESSIONS, pose
import bg_design as BG

D = os.path.dirname(os.path.abspath(__file__))
LATIN = FONT = "/usr/local/lib/python3.11/dist-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf"
LATINB = "/usr/local/lib/python3.11/dist-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans-Bold.ttf"
BANGLA = os.path.join(D, "..", "dark-lesson-3d", "fonts", "NotoSansBengali.ttf")

INK = (24, 25, 29)
GREY = (104, 106, 112)
PAPER = (250, 248, 242)
RULE = (206, 200, 188)
ACC = (150, 40, 30)


def f(sz, bold=False):
    return ImageFont.truetype(LATINB if bold else LATIN, sz)


def bn(sz):
    return ImageFont.truetype(BANGLA, sz)


def label(d, xy, text, sz=24, col=INK, bold=False, anchor="lm"):
    d.text(xy, text, font=f(sz, bold), fill=col, anchor=anchor)


def bangla(d, xy, text, sz=24, col=GREY, anchor="lm"):
    d.text(xy, text, font=bn(sz), fill=col, anchor=anchor)


def rule(d, a, b, col=RULE, w=2):
    d.line([a, b], fill=col, width=w)


# ------------------------------------------------------------------ figure helpers
def spec_for(key, face=1, **over):
    s = dict(CAST[key])
    s.update(x=0.0, y=0.0, face=face)
    s.update(over)
    return s


def mapper(cx, feet_y, pxm):
    """world (metres, y up-positive) -> canvas px."""
    return (lambda p: (cx + p[0] * pxm, feet_y - p[1] * pxm)), pxm


def draw_figure(d, key, cx, feet_y, pxm, p=None, flat=None, face=None, face_dir=1, **over):
    s = spec_for(key, face=face_dir, **over)
    rig = Rig(s)
    M = mapper(cx, feet_y, pxm)
    rig.draw(d, p or pose(a1=-38, b1=38, a2=8, b2=-8, l1=-10, r1=10), M, t=0.4, flat=flat, face=face)
    return M


def silhouette_thumb(key, w=48, h=104, face_dir=1):
    im = Image.new("RGBA", (w * 3, h * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw_figure(d, key, w * 1.5, h * 2.9, h * 2.6 / 1.45, flat=(20, 20, 24), face_dir=face_dir)
    return im.resize((w, h), Image.LANCZOS)



def head_plate(d, key, cx, cy, r, expr):
    """One head at a fixed diameter: the only thing allowed to change is the face."""
    s = spec_for(key)
    rig = Rig(s)
    w = max(3, int(r * 0.075))
    hw, hh = s["head_w"], s["head_h"]
    if s["head_shape"] == "round":
        d.ellipse([cx - r * hw, cy - r * hh, cx + r * hw, cy + r * hh], outline=INK, width=w)
    elif s["head_shape"] == "flat":
        d.rounded_rectangle([cx - r * hw, cy - r * hh, cx + r * hw, cy + r * hh],
                            radius=int(r * 0.34), outline=INK, width=w)
        d.line([(cx - r * hw, cy - r * hh * 0.62), (cx + r * hw, cy - r * hh * 0.62)],
               fill=INK, width=max(2, w - 1))
    else:
        d.polygon([(cx, cy - r * hh * 1.18), (cx + r * hw, cy + r * hh * 0.66),
                   (cx - r * hw, cy + r * hh * 0.66)], outline=INK, width=w)
    rig._face(d, (cx, cy), r, expr)


# ------------------------------------------------------------------ 1. character sheet
def character_sheet(path):
    W, H = 1720, 2440
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    label(d, (56, 30), "CHARACTER SHEET — an inventory of decisions", 42, INK, True)
    label(d, (56, 88), "Silhouette first · one dominant shape each, contrasted across the cast · "
                       "head-count is the tone dial · one accent colour, one job", 22, GREY)
    bangla(d, (56, 124), "আকৃতির ভাষা: বৃত্ত = আয়ান (নরম, দ্রুত) · বর্গ = রফিক (ভারী, অনড়) · "
                        "ত্রিভুজ = মীরা (সরু, চাপা)", 25, (96, 72, 58))

    # ---------------- panel 1: the cast
    d.rectangle((44, 166, 1676, 838), outline=RULE, width=2)
    label(d, (64, 182), "1 · THE CAST — neutral A-pose, one shared scale, head-unit construction",
          23, INK, True)
    pxm, feet = 318.0, 758
    for key, cx in (("ayan", 180), ("rafiq", 500), ("mira", 790)):
        s = CAST[key]
        hgt = s["H"] * pxm
        hh = s["H"] / s["heads"] * pxm
        rule(d, (cx, feet - hgt - 14), (cx, feet + 4), (152, 180, 198), 2)
        for i in range(int(round(s["heads"])) + 1):
            yy = feet - i * hh
            rule(d, (cx - 11, yy), (cx + 11, yy), (152, 180, 198), 3)
        draw_figure(d, key, cx, feet, pxm, face="neutral")
        label(d, (cx, feet + 24), s["name"], 20, INK, True, anchor="mm")
        label(d, (cx, feet + 44), "%s · %s" % (s["role"], s["shape"]), 16, GREY, anchor="mm")
        label(d, (cx, feet + 62), "%.1f heads · %.2f m" % (s["heads"], s["H"]), 15, GREY, anchor="mm")
        d.rounded_rectangle([cx - 38, feet + 72, cx + 38, feet + 82], 5, fill=s["accent"])

    ax = 1020
    rule(d, (ax - 26, 200), (ax - 26, 786), RULE, 2)
    label(d, (ax, 204), "ACCENT = ONE JOB", 21, INK, True)
    for i, key in enumerate(CAST):
        s = CAST[key]
        y = 244 + i * 74
        d.rounded_rectangle([ax, y, ax + 52, y + 36], 7, fill=s["accent"])
        label(d, (ax + 66, y + 2), s["name"], 21, INK, True)
        label(d, (ax + 66, y + 26), "only on: %s" % s["prop"], 16, GREY)
    label(d, (ax, 452), "Not on clothes, not on skin.\nRust = anger and impact only —\n"
                        "so it means something when\nit lands.", 16, GREY, anchor="la")

    dx = 1300
    rule(d, (dx - 26, 200), (dx - 26, 786), RULE, 2)
    label(d, (dx, 204), "THE DIALS", 21, INK, True)
    hdr_y = 236
    for i, nm in enumerate(("ayan", "rafiq", "mira")):
        label(d, (dx + 132 + i * 76, hdr_y), nm, 13, GREY)
    rows = [("head shape", "round", "flat-top", "hood"),
            ("head-count", "4.6", "5.4", "4.2"),
            ("height", "1.52 m", "1.72 m", "1.30 m"),
            ("shoulder:hip", "1.71", "1.64", "1.69"),
            ("limb thickness", "thin", "thick", "thin"),
            ("hands", "fist", "fist + boot", "point"),
            ("posture", "upright", "planted", "slouched")]
    for i, r in enumerate(rows):
        y = 262 + i * 30
        label(d, (dx, y), r[0], 14, INK, True)
        for j, v in enumerate(r[1:]):
            label(d, (dx + 132 + j * 76, y), v, 14, GREY)
    label(d, (dx, 470), "Same rig, different numbers. If a\nnumber changes between shots,\n"
                        "the character changed.", 15, ACC, anchor="la")

    # ---------------- panel 2: silhouette + squint
    d.rectangle((44, 858, 1676, 1272), outline=RULE, width=2)
    label(d, (64, 874), "2 · SILHOUETTE TEST — if the black shape does not say who it is, "
                        "the costume never will", 23, INK, True)
    for key, cx in (("ayan", 250), ("rafiq", 650), ("mira", 1040)):
        draw_figure(d, key, cx, 1246, 210, flat=(18, 18, 22))
        label(d, (cx, 1258), CAST[key]["name"], 15, GREY, anchor="mm")
    label(d, (1330, 900), "squint test", 19, INK, True)
    label(d, (1330, 924), "44 × 92 px — phone size", 16, GREY)
    for i, key in enumerate(("ayan", "rafiq", "mira")):
        th = silhouette_thumb(key)
        img.paste(th, (1330 + i * 74, 950), th)
    label(d, (1330, 1070), "Each still reads:\nlean · heavy · hunched.\nNo detail needed.", 15, GREY, anchor="la")

    # ---------------- panel 3: turnaround
    d.rectangle((44, 1290, 1676, 1782), outline=RULE, width=2)
    label(d, (64, 1306), "3 · TURNAROUND — in 2D, a rotation is four decisions held constant",
          23, INK, True)
    for i, (nm, shmul, fc) in enumerate([("front", 1.00, "determined"), ("3/4", 0.84, "determined"),
                                         ("side", 0.50, "profile"), ("back", 1.00, "none")]):
        cx = 200 + i * 220
        draw_figure(d, "ayan", cx, 1746, 278, face=fc,
                    shoulder=CAST["ayan"]["shoulder"] * shmul)
        label(d, (cx, 1758), nm.upper(), 14, GREY, anchor="mm")
    bx = 1010
    rule(d, (bx - 22, 1322), (bx - 22, 1762), RULE, 2)
    label(d, (bx, 1326), "What carries the rotation", 20, INK, True)
    for i, t in enumerate(["head shape + head size (never changes)",
                           "shoulder : hip ratio — narrows at 3/4 and side",
                           "eye line shifts toward the far side",
                           "the scarf trails the same way in every view",
                           "one centre line, one eye line, five head units"]):
        label(d, (bx, 1364 + i * 34), "· " + t, 17, GREY)
    label(d, (bx, 1548), "Lose the prop and you lose recognition\nat 44 px. That is the trade — decide\nit on purpose.", 16, ACC, anchor="la")

    # ---------------- panel 4: expressions
    d.rectangle((44, 1778, 1676, 2384), outline=RULE, width=2)
    label(d, (64, 1794), "4 · EXPRESSION SHEET — brows and eyes act; the mouth confirms",
          23, INK, True)
    for row, key in enumerate(("ayan", "rafiq")):
        top = 1866 + row * 232
        label(d, (66, top + 92), CAST[key]["name"], 15, ACC, True)
        for i, ex in enumerate(EXPRESSIONS):
            head_plate(d, key, 200 + i * 196, top + 74, 58, ex)
            if row == 0:
                label(d, (200 + i * 196, top + 156), ex, 15, GREY, anchor="mm")
    label(d, (64, 2330), "Drawn at one diameter per character: the head shape is the constant, "
                         "the face is the variable.", 17, GREY)

    label(d, (56, 2404), "Method: who they are in one sentence → 20 silhouette thumbnails → pick one "
                         "dominant shape → set the dials → test the face range → sheet.", 17, GREY)
    img.save(path)
    print("wrote", path, img.size)


def _notan(w, h):
    """Study 1: four values, no detail. This is the whole design; everything else is decoration."""
    img = Image.new("RGB", (w, h), (246, 240, 226))
    d = ImageDraw.Draw(img, "RGBA")
    hor = h * 0.58
    d.rectangle([0, 0, w, hor], fill=(202, 215, 227))
    d.rectangle([0, hor, w, h], fill=(216, 202, 174))
    d.rectangle([0, hor - 10, w, hor + 8], fill=(172, 178, 162))
    d.polygon([(0, h), (0, h * 0.84), (w * 0.22, h)], fill=(64, 68, 58))
    d.polygon([(w, h), (w, h * 0.88), (w * 0.86, h)], fill=(64, 68, 58))
    cx, cy, r = w * 0.38, h * 0.42, h * 0.042
    c = (255, 252, 244)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    d.line([(cx, cy + r), (cx, h * 0.86)], fill=c, width=int(w * 0.018))
    d.line([(cx, h * 0.60), (cx - w * 0.05, h * 0.73)], fill=c, width=int(w * 0.018))
    d.line([(cx, h * 0.60), (cx + w * 0.05, h * 0.73)], fill=c, width=int(w * 0.018))
    d.line([(cx, h * 0.86), (cx - w * 0.05, h)], fill=c, width=int(w * 0.018))
    d.line([(cx, h * 0.86), (cx + w * 0.05, h)], fill=c, width=int(w * 0.018))
    return img


def background_studies(path):
    W, H = 1720, 2060
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    label(d, (56, 34), "BACKGROUND SHEET — value structure first, then layers", 44, INK, True)
    label(d, (56, 92), "A flat background is not a style choice. It is a contrast problem: everything "
                       "in it competes with the character.", 23, GREY)

    pw, ph = 660, 580
    img.paste(_notan(pw, ph), (56, 160))
    d.rectangle([56, 160, 56 + pw, 160 + ph], outline=RULE, width=2)
    label(d, (56, 170), "1 · NOTAN — four values, no detail", 22, INK, True)
    for i, (nm, col) in enumerate([("1 figure (lightest)", (255, 252, 244)),
                                  ("2 sky", (202, 215, 227)),
                                  ("3 ground", (216, 202, 174)),
                                  ("4 near plane", (64, 68, 58))]):
        y = 760 + i * 34
        d.rounded_rectangle([56, y, 86, y + 24], 5, fill=col, outline=RULE)
        label(d, (98, y + 12), nm, 19, GREY)
    label(d, (56, 908), "Block these four first. If the thumbnail does not read,\n"
                        "no texture, tree or cloud will rescue it.", 19, GREY)

    plate = BG.build(pw, ph, 108.0, horizon_frac=0.58, blur_fg=0)
    img.paste(plate.convert("RGB"), (790, 160))
    d.rectangle([790, 160, 790 + pw, 160 + ph], outline=RULE, width=2)
    label(d, (790, 170), "2 · THE FOUR LAYERS, EACH AT ITS OWN CONTRAST", 22, INK, True)
    notes = [("BG", "sky + far hills", "8% contrast, coolest, no interior line", (176, 196, 208)),
             ("MG", "treeline + wall", "18%: one value step darker, soft edges", (150, 168, 158)),
             ("MG", "ground + path", "30%; the path is a leading line, not decor", (206, 194, 168)),
             ("FG", "branch + grass, blurred", "70%, darkest: the near plane that frames", (58, 62, 52))]
    for i, (tag, what, why, c) in enumerate(notes):
        y = 770 + i * 70
        d.rounded_rectangle([790, y, 846, y + 38], 7, fill=c)
        label(d, (858, y + 4), tag, 20, INK, True)
        label(d, (898, y + 4), what, 19, INK)
        label(d, (898, y + 26), why, 17, GREY)
    label(d, (790, 1062), "Distance is not detail. Distance = lower contrast + cooler colour + fewer edges.",
          19, ACC)

    # study 3: staging, tall
    big_w, big_h = 760, 900
    big = BG.build(big_w, big_h, 132.0, horizon_frac=0.62, blur_fg=5, path_x=big_w * 0.36)
    d2 = ImageDraw.Draw(big, "RGBA")
    fig_x, fig_feet, fig_pxm = big_w * 0.36 + 18, 700, 272
    halo = Image.new("RGBA", (520, 620), (0, 0, 0, 0))
    ImageDraw.Draw(halo, "RGBA").ellipse([90, 90, 430, 560], fill=(255, 252, 242, 30))
    halo = halo.filter(ImageFilter.GaussianBlur(64))
    big.alpha_composite(halo, (int(fig_x - 260), int(fig_feet - 560)))
    BG.contact_shadow(big, fig_x - 34, fig_feet + 1, 118, 62)
    draw_figure(d2, "ayan", fig_x, fig_feet, fig_pxm,
                p=pose(a1=-34, b1=30, a2=10, b2=-14, l1=-11, r1=11), face="determined")
    img.paste(big.convert("RGB"), (56, 1140))
    d.rectangle([56, 1140, 56 + big_w, 1140 + big_h], outline=RULE, width=2)
    ov = ImageDraw.Draw(img, "RGBA")
    for k in (1, 2):
        rule(ov, (56 + big_w * k / 3, 1140), (56 + big_w * k / 3, 1140 + big_h), (255, 255, 255, 70), 2)
        rule(ov, (56, 1140 + big_h * k / 3), (56 + big_w, 1140 + big_h * k / 3), (255, 255, 255, 70), 2)
    eye_y = 1140 + fig_feet - 1.30 * fig_pxm
    ov.line([(fig_x + 62, eye_y), (fig_x + 150, eye_y - 40)], fill=(255, 120, 90, 220), width=2)
    label(ov, (fig_x + 156, eye_y - 46), "eye line on the third", 14, (255, 160, 130))
    label(ov, (56, 1150), "3 · STAGING — subject on a third, type in the calm zone", 22, (255, 255, 255))
    band = [56 + 40, 1140 + big_h - 150, 56 + big_w - 40, 1140 + big_h - 46]
    ov.rounded_rectangle(band, 16, outline=(255, 255, 255, 160), width=2)
    label(ov, (56 + big_w / 2, 1140 + big_h - 116), "caption band — reserved, never over the face",
          18, (255, 255, 255), anchor="mm")

    nx = 880
    label(d, (nx, 1150), "Why this one reads", 24, INK, True)
    for i, s in enumerate([
        "the figure is the darkest value and the sharpest edge",
        "nothing in the background reaches its contrast",
        "horizon pushed low (62%) so the sky is a quiet field",
        "path, wall line and branch all point at the same third",
        "foreground is dark and blurred: depth without clutter",
        "one light source, upper right — every shadow falls left",
        "a soft paper halo separates the figure without an outline",
        "the bottom 190 px stay empty for the caption",
    ]):
        label(d, (nx, 1200 + i * 40), "· " + s, 20, GREY)
    label(d, (nx, 1560), "The old frame failed three of these:\n"
                        "horizon at 65% with a full skyline behind the head,\n"
                        "crowd and sandbag at the same contrast as the hero,\n"
                        "and no near plane at all — so nothing was in front\n"
                        "of anything and the whole plate read as one sheet.", 20, ACC)

    img.save(path)
    print("wrote", path, img.size)


# ------------------------------------------------------------------ 3. compare
def compare(path):
    W, H = 1720, 1160
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    label(d, (50, 34), "V1 → V2 · same beat, same cast size, different decisions", 38, INK, True)
    label(d, (50, 88), "Left: the flat plate from the fight film. Right: rebuilt with the rules on the "
                       "background sheet.", 21, GREY)

    pw, ph = 500, 880
    # ---- v1
    ys = np.linspace(0, 1, ph)[:, None]
    arr = np.repeat((np.array([150, 194, 228], float) * (1 - ys) +
                     np.array([238, 242, 242], float) * ys)[:, None, :], pw, axis=1).astype(np.uint8)
    v1 = Image.fromarray(arr, "RGB").convert("RGBA")
    d1 = ImageDraw.Draw(v1, "RGBA")
    d1.rectangle([0, ph * 0.655, pw, ph], fill=(214, 200, 176))
    for i in range(-4, 6):
        d1.rectangle([i * 70 + 40, ph * 0.50, i * 70 + 105, ph * 0.66], fill=(150, 168, 180))
    for i in range(4):
        cx = 50 + i * 128
        d1.ellipse([cx - 18, ph * 0.45, cx + 18, ph * 0.45 + 36], outline=(96, 108, 124, 90), width=6)
        d1.line([(cx, ph * 0.45 + 40), (cx, ph * 0.60)], fill=(96, 108, 124, 90), width=7)
        d1.line([(cx, ph * 0.60), (cx - 26, ph * 0.68)], fill=(96, 108, 124, 90), width=7)
        d1.line([(cx, ph * 0.60), (cx + 26, ph * 0.68)], fill=(96, 108, 124, 90), width=7)
    draw_figure(d1, "ayan", pw // 2, int(ph * 0.80), 300, face="none",
                p=pose(a1=-20, b1=20, a2=20, b2=-20, l1=-14, r1=14))
    img.paste(v1.convert("RGB"), (50, 130))
    d.rectangle([50, 130, 50 + pw, 130 + ph], outline=RULE, width=2)
    label(d, (50, 1024), "V1 — one value, no layers, no face; a see-through crowd", 19, GREY)
    label(d, (50, 1048), "drawn in the same line language as the hero; no near plane", 19, GREY)

    # ---- v2
    v2 = BG.build(pw, ph, 88.0, horizon_frac=0.60, blur_fg=4)
    d2 = ImageDraw.Draw(v2, "RGBA")
    halo = Image.new("RGBA", (260, 330), (0, 0, 0, 0))
    ImageDraw.Draw(halo, "RGBA").ellipse([40, 60, 220, 300], fill=(255, 252, 242, 58))
    halo = halo.filter(ImageFilter.GaussianBlur(22))
    v2.alpha_composite(halo, (pw // 3 - 130, 300))
    BG.contact_shadow(v2, int(pw * 0.30) - 14, int(ph * 0.855), 82, 70)
    draw_figure(d2, "ayan", int(pw * 0.30), int(ph * 0.85), 300,
                p=pose(a1=-34, b1=28, a2=10, b2=-16, l1=-12, r1=12), face="determined")
    BG.contact_shadow(v2, int(pw * 0.78) - 16, int(ph * 0.825), 88, 74)
    draw_figure(d2, "rafiq", int(pw * 0.78), int(ph * 0.82), 288, face_dir=-1, face="angry",
                p=pose(a1=-30, b1=34, a2=24, b2=-20, l1=-14, r1=14))
    img.paste(v2.convert("RGB"), (600, 130))
    d.rectangle([600, 130, 600 + pw, 130 + ph], outline=RULE, width=2)
    label(d, (600, 1024), "V2 — four values, four layers, one light, two shape-", 19, GREY)
    label(d, (600, 1048), "contrasted characters with faces, on the thirds", 19, GREY)

    # ---- the change list
    x = 1150
    label(d, (x, 140), "What changed — none of it is 'more detail'", 24, INK, True)
    rows = [("value", "1 value → 4 named values"),
            ("layers", "none → BG / MG / ground / FG"),
            ("distance", "equal contrast → 8% far, 70% near"),
            ("light", "no direction → one source, upper right"),
            ("cast", "one template, recoloured → shape language"),
            ("silhouette", "identical outlines → scarf / flat-top / hood"),
            ("face", "none → 8-expression module"),
            ("scale", "all equal → 4.1 / 4.6 / 5.1 heads"),
            ("staging", "centred → subject on a third, path leads to it"),
            ("type", "over the subject → reserved calm band"),
            ("near plane", "none → blurred branch + grass"),
            ("crowd", "see-through extras → pushed to 8% or cut")]
    for i, (k, v) in enumerate(rows):
        y = 200 + i * 62
        label(d, (x, y), k.upper(), 18, ACC, True)
        label(d, (x, y + 24), v, 19, GREY)

    img.save(path)
    print("wrote", path, img.size)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    os.makedirs(os.path.join(D, "out"), exist_ok=True)
    if what in ("character", "all"):
        character_sheet(os.path.join(D, "out", "character-sheet.png"))
    if what in ("background", "all"):
        background_studies(os.path.join(D, "out", "background-studies.png"))
    if what in ("compare", "all"):
        compare(os.path.join(D, "out", "compare-v1-v2.png"))
