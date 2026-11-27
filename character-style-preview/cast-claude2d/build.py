#!/usr/bin/env python3
"""Flatten generated paper grain and compose the Claude-2D cast deliverables.

Run from anywhere:  python3 build.py
Outputs: flat/*.png, cast-lineup.png, heads-preview.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = (240, 238, 230)      # #F0EEE6
INK = (26, 23, 20)
BANGLA = os.path.join(HERE, "..", "..", "dark-lesson-06-signature", "fonts", "NotoSansBengali.ttf")
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

CAST = [
    ("01-dada", "DADA", "দাদা", "72 · white beard, walking stick", "doorway"),
    ("02-bou", "BOU", "বউ", "28 · mustard kurta, coral-flap satchel", "laundry line"),
    ("03-chele", "CHELE", "ছেলে", "15 · off-white tee, coral pocket", "clean wall"),
    ("04-natni", "NATNI", "নাতনি", "7 · coral ribbons, bare feet", "mango tree"),
    ("05-kagojwala", "KAGOJWALA", "কাগজওয়ালা", "52 · skullcap, paper bundle", "paper stacks"),
]


def flatten(src, dst):
    """Fill the paper background with exact #F0EEE6, leaving all art untouched."""
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    near = np.abs(a - np.array(PAPER)).max(2) <= 20
    # connected to the border only
    h, w = near.shape
    seen = np.zeros_like(near)
    stack = [(0, x) for x in range(w)] + [(h - 1, x) for x in range(w)]
    stack += [(y, 0) for y in range(h)] + [(y, w - 1) for y in range(h)]
    while stack:
        y, x = stack.pop()
        if y < 0 or x < 0 or y >= h or x >= w or seen[y, x] or not near[y, x]:
            continue
        seen[y, x] = True
        stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    out = a.copy()
    out[seen] = PAPER
    Image.fromarray(out.astype(np.uint8)).save(dst)
    return dst


def trim(im, tol=18, pad=14):
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    m = np.abs(a - np.array(PAPER)).max(2) > tol
    ys, xs = np.where(m)
    return im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad),
                    min(im.width, xs.max() + pad), min(im.height, ys.max() + pad)))


def fit(im, height):
    k = height / im.height
    return im.resize((max(1, round(im.width * k)), height), Image.LANCZOS)


def lineup(flatdir):
    CW, CH, GAP, HEAD = 470, 1060, 14, 96
    sheet = Image.new("RGB", (GAP + len(CAST) * (CW + GAP), HEAD + CH + GAP), INK)
    d = ImageDraw.Draw(sheet)
    f_tag = ImageFont.truetype(SANS_B, 30)
    f_name = ImageFont.truetype(SANS, 22)
    f_bn = ImageFont.truetype(BANGLA, 30) if os.path.exists(BANGLA) else f_name
    f_note = ImageFont.truetype(SANS, 19)
    d.text((GAP + 6, 30), "DARK LESSON — CAST", font=f_tag, fill=(240, 238, 230))
    d.text((GAP + 6, 62), "claude 2d · flat vector · five characters, one palette", font=f_note, fill=(150, 144, 134))

    for i, (key, name, bn, note, prop) in enumerate(CAST):
        x = GAP + i * (CW + GAP)
        d.rectangle([x, HEAD, x + CW, HEAD + CH], fill=PAPER)
        fig = trim(Image.open(os.path.join(flatdir, key + ".png")))
        k = min(760 / fig.height, (CW - 34) / fig.width)
        fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.LANCZOS)
        sheet.paste(fig, (x + (CW - fig.width) // 2, HEAD + CH - 132 - fig.height))
        d.text((x + 18, HEAD + 16), str(i + 1), font=f_tag, fill=(190, 120, 80))
        d.text((x + 54, HEAD + 18), name, font=f_name, fill=(40, 36, 32))
        d.text((x + 18, HEAD + CH - 96), note, font=f_note, fill=(52, 47, 42))
        d.text((x + 18, HEAD + CH - 64), "behind: " + prop, font=f_note, fill=(150, 120, 90))
    out = os.path.join(HERE, "cast-lineup.png")
    sheet.save(out)
    print("wrote", out, sheet.size)


def heads_preview(flatdir):
    rows = [("dada", "neutral"), ("bou", "neutral"), ("chele", "neutral")]
    CW = 360
    sheet = Image.new("RGB", (3 * CW + 4 * 14, 470), INK)
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(SANS, 20)
    n = 0
    for i, (k, e) in enumerate(rows):
        p = [os.path.join(HERE, "heads", f) for f in sorted(os.listdir(os.path.join(HERE, "heads"))) if k in f][0]
        im = fit(trim(Image.open(p)), 420)
        x = 14 + i * (CW + 14)
        sheet.paste(im, (x + (CW - im.width) // 2, 36))
        d.text((x + 10, 8), k.upper(), font=f, fill=(200, 160, 130))
        n += 1
    out = os.path.join(HERE, "heads-preview.png")
    sheet.save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    flatdir = os.path.join(HERE, "flat")
    os.makedirs(flatdir, exist_ok=True)
    for key, *_ in CAST:
        flatten(os.path.join(HERE, key + ".png"), os.path.join(flatdir, key + ".png"))
    lineup(flatdir)
    if os.path.isdir(os.path.join(HERE, "heads")):
        heads_preview(flatdir)
