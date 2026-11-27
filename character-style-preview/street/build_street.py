#!/usr/bin/env python3
"""build_street.py — cut the ten neighbours out of their paper and lay them out.

The off-white clothes are the same value as the paper, so the cut is geometric: close
the ink outline by a few pixels, flood the outside only, keep everything inside opaque.

    python3 build_street.py
    ->  plates/NN-name.png   (RGBA, trimmed)
        street-lineup.png     (ten cards, Bangla role + English + note)
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import deva

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plates")
PAPER = np.array([240, 238, 230], dtype=np.int16)
INK = (26, 23, 20)
PAPER_RGB = (240, 238, 230)

CAST = [
    ("01-elder", "মোড়ল", "ELDER", "74 · white beard, punjabi, lungi"),
    ("02-shopkeeper", "দোকানদার", "SHOPKEEPER", "48 · moustache, gamchha on the shoulder"),
    ("03-tailor", "দর্জি", "TAILOR", "35 · tape round the neck, thin, patient"),
    ("04-boatman", "মাঝি", "BOATMAN", "30 · vest, lungi hitched, bare feet"),
    ("05-widow", "বিধবা", "WIDOW", "66 · white sari, grey bun"),
    ("06-bride", "নববধূ", "BRIDE", "22 · mustard sari, coral border"),
    ("07-teacher", "শিক্ষিকা", "TEACHER", "41 · specs, sari, canvas tote"),
    ("08-postman", "ডাকপিয়ন", "POSTMAN", "28 · khaki, peaked cap, mail bag"),
    ("09-student", "ছাত্রী", "STUDENT", "16 · two braids, salwar kameez"),
    ("10-moneylender", "মহাজন", "MONEYLENDER", "56 · plump, half-moon specs, dhoti"),
]


STATURE = {"01-elder": 0.97, "02-shopkeeper": 1.00, "03-tailor": 0.98, "04-boatman": 1.03,
           "05-widow": 0.93, "06-bride": 0.96, "07-teacher": 0.96, "08-postman": 1.00,
           "09-student": 0.90, "10-moneylender": 0.95}


def cut(path):
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    h, w, _ = a.shape
    lum = a.mean(2)
    ink = (lum < 175).astype(np.uint8) * 255
    closed = np.asarray(Image.fromarray(ink, "L").filter(ImageFilter.MaxFilter(7))) > 128
    free = ~closed
    seen = np.zeros((h, w), bool)
    stack = [(0, x) for x in range(w)] + [(h - 1, x) for x in range(w)]
    stack += [(y, 0) for y in range(h)] + [(y, w - 1) for y in range(h)]
    while stack:
        y, x = stack.pop()
        if y < 0 or x < 0 or y >= h or x >= w or seen[y, x] or not free[y, x]:
            continue
        seen[y, x] = True
        stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    for _ in range(2):
        seen = np.asarray(Image.fromarray(seen.astype(np.uint8) * 255, "L")
                          .filter(ImageFilter.MaxFilter(3))) > 128
    rgb = a.copy()
    rgb[seen] = PAPER
    alpha = np.where(seen, 0, 255).astype(np.uint8)
    ys, xs = np.where(alpha > 8)
    y0, y1 = max(0, ys.min() - 2), min(h, ys.max() + 3)
    x0, x1 = max(0, xs.min() - 2), min(w, xs.max() + 3)
    return Image.fromarray(np.dstack([rgb.astype(np.uint8), alpha])[y0:y1, x0:x1], "RGBA")


def fit(im, h):
    k = h / im.height
    return im.resize((max(1, round(im.width * k)), h), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    plates = []
    for key, bn, en, note in CAST:
        im = cut(os.path.join(HERE, key + ".png"))
        im.save(os.path.join(OUT, key + ".png"))
        plates.append(im)
        print(key, im.size)

    CW, CH, GAP, HEAD = 484, 1078, 16, 108
    sheet = Image.new("RGBA", (GAP + 5 * (CW + GAP), HEAD + 2 * (CH + GAP) + GAP), INK + (255,))
    d = ImageDraw.Draw(sheet)
    deva.draw_text(sheet, (GAP + 8, 34), "এক পাড়ার মানুষ", 42, 700, PAPER_RGB, anchor="lm")
    d.text((GAP + 10, 78), "one street · ten neighbours · claude 2d flat vector",
           fill=(150, 144, 134))

    for i, (key, bn, en, note) in enumerate(CAST):
        col, row = i % 5, i // 5
        x = GAP + col * (CW + GAP)
        y = HEAD + row * (CH + GAP)
        d.rectangle([x, y, x + CW, y + CH], fill=PAPER_RGB)
        target = int(800 * STATURE.get(key, 1.0))
        fig = fit(plates[i], target)
        if fig.width > CW - 40:
            fig = fit(plates[i], int(target * (CW - 40) / fig.width))
        sheet.paste(fig, (x + (CW - fig.width) // 2, y + CH - 150 - fig.height), fig)
        deva.draw_text(sheet, (x + 22, y + 40), bn, 40, 700, (30, 27, 24), anchor="lm")
        d.text((x + 24, y + 78), en, fill=(140, 120, 96))
        d.text((x + 24, y + CH - 116), note.split(" · ")[0] + " years", fill=(60, 54, 48))
        d.text((x + 24, y + CH - 88), " · ".join(note.split(" · ")[1:]), fill=(120, 112, 100))

    out = os.path.join(HERE, "street-lineup.png")
    sheet.convert("RGB").save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main()
