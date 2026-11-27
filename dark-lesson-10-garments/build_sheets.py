"""build_sheets.py — turns the forty generated plates into ten face sheets and a lineup.

Each character: four expressions, trimmed to the figure, laid on one cream sheet with
the Bangla name, the Bangla role and the four expression labels set in Noto Sans Bengali
(PIL has no Raqm here, so the type goes through deva.py).

    python3 build_sheets.py
"""
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deva

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "sheets")
os.makedirs(OUT, exist_ok=True)

PAPER = (236, 228, 210)
PAPER_D = (222, 212, 191)
INK = (26, 23, 20)
INK_S = (104, 96, 86)
INDIGO = (43, 48, 94)
BRICK = (150, 62, 44)

EXPR = [("neutral", "নির্বিকার"), ("speaking", "বলছে"),
        ("angry", "ক্রুদ্ধ"), ("grieving", "শোকাহত")]

CAST = [
    ("01-nasima", "নাসিমা খাতুন", "Nasima Khatun", "ফ্যাক্টরি ম্যানেজার", 48),
    ("02-shahana", "শাহানা পারভীন", "Shahana Parvin", "লাইন সুপারভাইজার", 31),
    ("03-rezaul", "রেজাউল করিম", "Rezaul Karim", "কাটিং মাস্টার", 41),
    ("04-marium", "মরিয়ম বেগম", "Marium Begum", "সেলাই অপারেটর", 24),
    ("05-rubina", "রুবিনা আক্তার", "Rubina Akter", "নতুন অপারেটর", 19),
    ("06-josna", "জোসনা ফেরদৌস", "Josna Ferdous", "কোয়ালিটি চেকার", 27),
    ("07-rahima", "রহিমা খাতুন", "Rahima Khatun", "সিনিয়র অপারেটর", 45),
    ("08-firoza", "ফিরোজা বেগম", "Firoza Begum", "কাটারের সহকারী", 22),
    ("09-nazma", "নাজমা সুলতানা", "Nazma Sultana", "প্রেসিং সেকশন", 35),
    ("10-babul", "বাবুল মিয়া", "Babul Mia", "মেশিন মেকানিক", 52),
]


# ------------------------------------------------------------------ trimming
def trim(im, need=12):
    """Cut the cream field away.

    The generated paper is speckled, so "differs from paper" flags the whole canvas.
    Take the paper colour from the border, build a binary mask, then median-filter it:
    grain and dust vanish, the figure survives, and a row or column only counts if a
    whole line of it is left.
    """
    a = np.asarray(im.convert("RGB"), dtype=np.int16)
    h, w = a.shape[:2]
    # paper colour as the dominant colour of the whole plate: some drawings carry a thin
    # white margin or a dark rule at the border, so sampling the edge is not safe
    flat = a.reshape(-1, 3)
    keys, counts = np.unique(flat // 8, axis=0, return_counts=True)
    dom = keys[counts.argmax()]
    sel = (flat // 8 == dom).all(1)
    paper = flat[sel].mean(0) if sel.any() else np.median(flat, 0)
    mask = (np.abs(a - paper).max(2) > 46).astype(np.uint8) * 255
    m = Image.fromarray(mask, "L").filter(ImageFilter.MedianFilter(9))
    b = np.asarray(m) > 127
    b[:10, :] = b[-10:, :] = False      # some plates are drawn inside a thin dark border
    b[:, :10] = b[:, -10:] = False
    rows = np.where(b.sum(1) >= need)[0]
    cols = np.where(b.sum(0) >= need)[0]
    if len(rows) == 0 or len(cols) == 0:
        return im
    pad = 6
    return im.crop((max(0, cols[0] - pad), max(0, rows[0] - pad),
                    min(im.width, cols[-1] + pad), min(im.height, rows[-1] + pad)))


def plate(cid, expr, rgba=False):
    """The figure alone. With rgba=True the paper is flooded away from the corners, so
    the plate can be laid on the sheet's own cream instead of showing as a rectangle —
    only paper the flood could reach is removed, never a white blouse inside an outline."""
    p = os.path.join(RAW, "%s-%s.png" % (cid, expr))
    if not os.path.exists(p):
        return None
    im = trim(Image.open(p).convert("RGB"))
    if not rgba:
        return im
    keyed = im.copy()
    sentinel = (255, 0, 255)
    w, h = keyed.size
    for seed in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        try:
            ImageDraw.floodfill(keyed, seed, sentinel, thresh=40)
        except Exception:
            pass
    a = np.asarray(keyed, dtype=np.int16)
    gone = np.abs(a - np.array(sentinel, dtype=np.int16)).sum(2) <= 30
    out = im.convert("RGBA")
    al = np.where(gone, 0, 255).astype(np.uint8)
    out.putalpha(Image.fromarray(al, "L").filter(ImageFilter.GaussianBlur(0.8)))
    return out


def fit(im, w, h):
    k = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


# ------------------------------------------------------------------ sheets
def sheet(cid, name, eng, role, age):
    W, H = 1800, 1240
    art = Image.new("RGBA", (W, H), PAPER + (255,))   # deva needs RGBA
    d = ImageDraw.Draw(art)
    d.rectangle([0, 0, W, 10], fill=INK)
    d.rectangle([0, H - 10, W, H], fill=INK)
    d.line([(64, 210), (W - 64, 210)], fill=INK, width=3)

    deva.draw_text(art, (64, 120), name, 66, 700, INK, anchor="lm")
    deva.draw_text(art, (70, 172), "%s · %d · %s" % (eng, age, role), 30, 500, INK_S, anchor="lm")
    deva.draw_text(art, (W - 64 - deva.layout("অন্ধকার পাঠ · ১০", 26)[1], 118),
                   "অন্ধকার পাঠ · ১০", 26, 500, BRICK, anchor="lm")

    cell = (W - 128) // 4
    top, bottom = 250, H - 120
    for i, (key, lab) in enumerate(EXPR):
        im = plate(cid, key, rgba=True)
        x0 = 64 + i * cell
        if im is None:
            d.rectangle([x0 + 12, top, x0 + cell - 12, bottom], outline=PAPER_D, width=3)
            continue
        f = fit(im, cell - 26, bottom - top - 40)
        art.alpha_composite(f, (x0 + (cell - f.width) // 2, bottom - 40 - f.height))
        lw = deva.layout(lab, 34)[1]
        deva.draw_text(art, (x0 + cell // 2 - lw // 2, bottom - 6), lab, 34, 600, INK, anchor="lm")
        d.line([(x0 + 14, bottom - 52), (x0 + cell - 14, bottom - 52)], fill=PAPER_D, width=2)
    return art


STATURE = {"01-nasima": 0.93, "02-shahana": 1.03, "03-rezaul": 1.0, "04-marium": 0.97,
           "05-rubina": 0.92, "06-josna": 0.97, "07-rahima": 0.95, "08-firoza": 0.98,
           "09-nazma": 0.96, "10-babul": 0.98}


def placed(im, height):
    h = int(height)
    w = max(1, int(im.width * h / im.height))
    return im.resize((w, h), Image.LANCZOS)     # keeps RGBA if given RGBA


def portrait(cid, name, eng, role, age):
    W, H = 900, 1200
    art = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(art)
    d.rectangle([0, 0, W, 6], fill=INK)
    im = plate(cid, "neutral", rgba=True)
    if im is not None:
        f = placed(im, 1010 * STATURE.get(cid, 1.0))
        if f.width > W - 90:
            f = placed(im, int(f.height * (W - 90) / f.width))
        art.alpha_composite(f, ((W - f.width) // 2, 1074 - f.height))
        d.line([(150, 1078), (W - 150, 1078)], fill=PAPER_D, width=3)
    deva.draw_text(art, (60, 1122), name, 44, 700, INK, anchor="lm")
    deva.draw_text(art, (62, 1168), "%s · %d · %s" % (eng, age, role), 24, 500, INK_S, anchor="lm")
    return art.convert("RGB")


def lineup():
    cols, rows = 5, 2
    cw, ch = 356, 760
    W = cols * cw + 120
    head, base0 = 196, 690
    H = head + rows * ch + 96
    art = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(art)
    d.rectangle([0, 0, W, 8], fill=INK)
    d.rectangle([0, H - 8, W, H], fill=INK)
    deva.draw_text(art, (60, 96), "এক শিফট, দশ জন", 62, 700, INK, anchor="lm")
    deva.draw_text(art, (64, 150), "a Gazipur garment factory · woodcut · ten characters",
                   27, 500, INK_S, anchor="lm")
    for i, (cid, name, eng, role, age) in enumerate(CAST):
        im = plate(cid, "neutral", rgba=True)
        x = 60 + (i % cols) * cw
        y = head + (i // cols) * ch
        base = y + base0 - head + 40
        if im is not None:
            f = placed(im, 560 * STATURE.get(cid, 1.0))
            if f.width > cw - 30:
                f = placed(im, int(f.height * (cw - 30) / f.width))
            art.alpha_composite(f, (x + (cw - f.width) // 2, base - f.height))
        d.line([(x + 26, base + 6), (x + cw - 26, base + 6)], fill=PAPER_D, width=2)
        lw = deva.layout(name, 29)[1]
        deva.draw_text(art, (x + cw // 2 - lw // 2, base + 48), name, 29, 600, INK, anchor="lm")
        rw = deva.layout(role, 21)[1]
        deva.draw_text(art, (x + cw // 2 - rw // 2, base + 84), role, 21, 500, INK_S, anchor="lm")
    return art


def main():
    made = 0
    for cid, name, eng, role, age in CAST:
        have = [k for k, _ in EXPR if os.path.exists(os.path.join(RAW, "%s-%s.png" % (cid, k)))]
        if len(have) < 4:
            print("  %-12s %d/4 — skipped" % (cid, len(have)))
            continue
        p = os.path.join(OUT, cid + "-sheet.png")
        sheet(cid, name, eng, role, age).convert("RGB").save(p)
        made += 1
        print("  wrote", os.path.basename(p))
    p = os.path.join(OUT, "lineup.png")
    lineup().convert("RGB").save(p)
    print("wrote", os.path.basename(p), "· %d four-up sheets" % made)
    for cid, name, eng, role, age in CAST:
        if os.path.exists(os.path.join(RAW, "%s-neutral.png" % cid)):
            portrait(cid, name, eng, role, age).save(os.path.join(OUT, cid + "-card.png"))
    print("wrote ten character cards")


if __name__ == "__main__":
    main()
