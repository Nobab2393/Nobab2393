"""make_sheet.py — puts the five episode-4 character designs on one sheet.

    cd dark-lesson-04-last-word && python3 cast/make_sheet.py

Figures are placed on a common baseline at proportional heights (the elder tallest, the
child shortest), labelled in Bangla with the film's own type, and the palette under them is
the film's palette — nothing else is allowed on the sheet.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CAST = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(CAST)
os.chdir(ROOT)
sys.path.insert(0, ROOT)
import deva  # noqa: E402

PAPER = (240, 238, 230)
INK = (26, 23, 20)
INK_S = (110, 105, 97)
WALL = (219, 214, 202)
CORAL = (217, 119, 87)
BLUE = (106, 155, 204)

W, H, BASE = 2500, 1720, 1276
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# file, x-window in the source (the person only), target height on the sheet, labels
CAST_LIST = [
    ("c1-elder-brother.png", (520, 920), 880, "বড় ভাই", "বলাটাই কাজ · প্রতিবার জেতে"),
    ("c2-younger-brother.png", (575, 855), 845, "ছোট ভাই", "শোনাটাই কাজ · শেষ দিনে থামে"),
    ("c3-boudi.png", (500, 845), 790, "বৌদি", "দরজার ভেতরে · চায়ের শব্দ"),
    ("c5-old-customer.png", (565, 840), 825, "পুরনো কাস্টমার", "আসা বন্ধ করে দিল"),
    ("c4-niece.png", (525, 900), 528, "ভাইঝি", "আলো-দরজার ভেতরে · হাসে"),
]
CENTRES = (300, 800, 1290, 1790, 2290)

PALETTE = [
    (PAPER, "কাগজ", "#F0EEE6"),
    (INK, "কালি", "#1A1714"),
    (WALL, "দেয়াল", "#DBD6CA"),
    (CORAL, "প্রবাল = এক জেতা তর্ক", "#D97757"),
    (BLUE, "নীল = যে কাপ রয়ে গেল", "#6A9BCC"),
]


def person(path, xw):
    """Cut the figure out of its own paper.

    After flatten.py the paper is exactly PAPER, so the background is an exact match and can
    be flood-filled from the corners: only the *outside* becomes transparent, which keeps the
    off-white kurta solid instead of punching a hole in it.
    """
    im = Image.open(os.path.join(CAST, path)).convert("RGB")
    a = np.asarray(im)
    bg = np.all(a == np.array(PAPER, np.uint8), axis=2)
    cand = Image.fromarray((bg * 255).astype(np.uint8), "L")
    d = ImageDraw.Draw(cand)
    for seed in ((0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1)):
        if cand.getpixel(seed) == 255:
            ImageDraw.floodfill(cand, seed, 128, thresh=0)
    alpha = np.where(np.asarray(cand) == 128, 0, 255).astype(np.uint8)
    alpha[:, : xw[0]] = 0
    alpha[:, xw[1]:] = 0
    # the render draws a thin ground line under the feet — drop it, the sheet has one baseline
    h, cleared = alpha.shape[0], 0
    for row in range(h - 1, max(h - 110, 0), -1):
        seg = alpha[row, xw[0]:xw[1]]
        if (seg > 0).mean() > 0.6:
            alpha[row] = 0
            cleared += 1
            if cleared >= 8:
                break
        elif cleared:
            break
    ys, xs = np.where(alpha > 0)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    cut = im.crop(box).convert("RGBA")
    cut.putalpha(Image.fromarray(alpha[box[1]:box[3], box[0]:box[2]], "L"))
    return cut


def main():
    sheet = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(sheet)

    deva.draw_text(sheet, (96, 96), "পাঁচ চরিত্র", 92, 700, INK, anchor="lm")
    deva.draw_text(sheet, (100, 186), "অন্ধকার পাঠ ০৪ · শেষ কথা — ফ্ল্যাট ভেক্টর, পাঁচ রঙের বেশি নয়",
                   34, 500, INK_S, anchor="lm")

    for (fn, xw, th, name, role), cx in zip(CAST_LIST, CENTRES):
        im = person(fn, xw)
        k = th / im.height
        im = im.resize((max(1, round(im.width * k)), th), Image.LANCZOS)
        sheet.alpha_composite(im, (cx - im.width // 2, BASE - im.height))
        deva.draw_text(sheet, (cx, BASE + 76), name, 54, 700, INK, anchor="mm")
        sz = 30
        while sz > 20 and deva.layout(role, sz)[1] > 420:
            sz -= 1
        deva.draw_text(sheet, (cx, BASE + 132), role, sz, 500, INK_S, anchor="mm")

    # the palette, and the two colours that are only allowed to mean one thing
    yy = 1552
    for i, (col, cap, hx) in enumerate(PALETTE):
        x = 150 + i * 460
        deva.draw_text(sheet, (x, yy), cap, 30, 500, INK_S, anchor="lm")
        bx, by, s = x, yy + 32, 56
        d.rectangle([bx, by, bx + s, by + s], fill=col, outline=INK, width=3 if col == PAPER else 0)
        f = ImageFont.truetype(MONO, 24)
        d.text((bx, by + s + 10), hx, font=f, fill=INK)
    d.line([(96, 1520), (W - 96, 1520)], fill=WALL, width=3)

    out = os.path.join(CAST, "cast-sheet.png")
    sheet.convert("RGB").save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main()
