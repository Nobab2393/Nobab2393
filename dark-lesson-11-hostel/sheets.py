"""sheets.py — episode 11 plates: trim, normalise, card, line up.

The plates come back as flat-colour cutout puppets standing on an empty slate field,
so the trim is a background-difference mask rather than paper keying: whatever colour
the four corners agree on is the stage, everything else is the puppet.

    python3 sheets.py            # -> cast/*.png, sheets/lineup.png, ten cards
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
CASTDIR = os.path.join(HERE, "cast")
OUT = os.path.join(HERE, "sheets")
FONT = os.path.join(HERE, "fonts", "NotoSansBengali.ttf")

os.makedirs(CASTDIR, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

PAPER = (243, 236, 222)
INK = (28, 25, 22)
INK_S = (110, 100, 88)
BRICK = (163, 66, 44)

FIG_H = 1180          # normalised figure height, in plate pixels
BASE = 1240           # feet baseline inside a 1500-tall plate

#  key            name                  role                    age   takes
CAST = [
    ("01-nurjahan", "নূরজাহান বেগম", "হোস্টেল ম্যাট্রন", 54),
    ("02-afsana", "আফসানা আক্তার", "দশম শ্রেণির ছাত্রী", 17),
    ("03-mizanur", "মিজানুর রহমান", "হোস্টেল সুপার", 58),
    ("04-shahed", "শাহেদ আলী", "একাদশ শ্রেণির ছাত্র", 19),
    ("05-rebeka", "রেবেকা খাতুন", "হোস্টেলের রাঁধুনি", 42),
    ("06-tanvir", "তানভীর হাসান", "নবম শ্রেণির ছাত্র", 16),
    ("07-suraiya", "সুরাইয়া পারভীন", "সহকারী শিক্ষিকা", 31),
    ("08-kalam", "কালাম শেখ", "কেয়ারটেকার", 25),
    ("09-jobeda", "জোবেদা বিবি", "পুরনো আয়া", 60),
    ("10-the-tenth", "দশম জন", "নাম নেই", 20),
]


def stage_colour(im):
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    h, w, _ = a.shape
    k = max(4, h // 40)
    corners = np.concatenate([a[:k, :k].reshape(-1, 3), a[:k, -k:].reshape(-1, 3),
                              a[-k:, :k].reshape(-1, 3), a[-k:, -k:].reshape(-1, 3)])
    return np.median(corners, axis=0)


def trim(im, pad=0.02):
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    bg = stage_colour(im)
    d = np.abs(a - bg).max(axis=2)
    m = d > 14
    # keep the largest connected blob only (stray specks from the model)
    ys, xs = np.nonzero(m)
    if len(ys) == 0:
        return im
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    # column/row density trim: drop thin outliers far from the body
    colsum = m.sum(axis=0)
    keep = np.nonzero(colsum > (y1 - y0) * 0.004)[0]
    if len(keep):
        x0, x1 = max(x0, keep.min()), min(x1, keep.max())
    rowsum = m.sum(axis=1)
    keep = np.nonzero(rowsum > (x1 - x0) * 0.004)[0]
    if len(keep):
        y0, y1 = max(y0, keep.min()), min(y1, keep.max())
    px, py = int((x1 - x0) * pad), int((y1 - y0) * pad)
    box = (max(0, x0 - px), max(0, y0 - py),
           min(a.shape[1], x1 + px + 1), min(a.shape[0], y1 + py + 1))
    out = im.crop(box)
    # knock the stage out so the plate drops onto a scene cleanly later
    aa = np.asarray(out.convert("RGB")).astype(np.int16)
    dm = np.abs(aa - bg).max(axis=2)
    alpha = np.clip((dm - 8) * 22, 0, 255).astype(np.uint8)
    alpha = np.asarray(Image.fromarray(alpha, "L").filter(ImageFilter.GaussianBlur(0.6)))
    rgba = out.convert("RGBA")
    rgba.putalpha(Image.fromarray(alpha))
    return rgba


def normalise(rgba, h=FIG_H):
    a = np.asarray(rgba)
    ys = np.nonzero(a[..., 3] > 40)[0]
    if len(ys) == 0:
        return rgba
    y0, y1 = ys.min(), ys.max()
    fig_h = max(1, y1 - y0)
    s = h / fig_h
    nw, nh = max(1, int(round(rgba.width * s))), max(1, int(round(rgba.height * s)))
    return rgba.resize((nw, nh), Image.LANCZOS)


def plate(rgba, w=760, h=1500):
    canvas = Image.new("RGBA", (w, h), PAPER + (255,))
    nw, nh = rgba.size
    a = np.asarray(rgba)
    ys = np.nonzero(a[..., 3] > 40)[0]
    bottom = ys.max() if len(ys) else nh
    canvas.alpha_composite(rgba, ((w - nw) // 2, BASE - bottom))
    return canvas.convert("RGB")


def card(key, name, role, age, rgba):
    W, H = 900, 1200
    im = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 8], fill=BRICK)
    body = normalise(rgba, int(H * 0.66))
    im.paste(body, ((W - body.width) // 2, int(H * 0.72) - body.height + 60), body)
    deva.draw_text(im, (64, 82), name, 62, color=INK, anchor="lm")
    deva.draw_text(im, (64, 166), "%s · %d" % (role, age), 34, color=BRICK, anchor="lm")
    d.line([64, 216, W - 64, 216], fill=INK_S, width=2)
    im.convert("RGB").save(os.path.join(OUT, "%s-card.png" % key))
    return im


def main():
    rows = []
    for key, name, role, age in CAST:
        p = os.path.join(RAW, "%s-neutral.png" % key)
        if not os.path.exists(p):
            print("  %-12s missing" % key)
            continue
        rgba = normalise(trim(Image.open(p)))
        rgba.save(os.path.join(CASTDIR, "%s-neutral.png" % key))
        rows.append((key, name, role, age, rgba))
        card(key, name, role, age, rgba)
        print("  %-12s %dx%d" % (key, rgba.width, rgba.height))

    # lineup — five across, two rows
    COLS = 5
    tw, th = 400, 660
    pad = 34
    rows_n = (len(rows) + COLS - 1) // COLS
    W = COLS * tw + pad * 2
    head = 250
    H = head + rows_n * (th + 40) + 40
    im = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(im)
    deva.draw_text(im, (pad, 74), "এক শিফট, দশ জন — পর্ব ১১", 54, color=INK, anchor="lm")
    deva.draw_text(im, (pad, 142), "মফস্বলের স্কুল-হোস্টেল · কাটআউট পাপেট · দশ জন",
                   30, color=INK_S, anchor="lm")
    d.line([pad, 196, W - pad, 196], fill=INK_S, width=2)
    for i, (key, name, role, age, rgba) in enumerate(rows):
        r, c = divmod(i, COLS)
        top = head + r * (th + 40)
        s = (th - 140) / rgba.height
        b = rgba.resize((int(rgba.width * s), int(rgba.height * s)), Image.LANCZOS)
        x = pad + c * tw + (tw - b.width) // 2
        im.paste(b, (x, top + (th - 140) - b.height + 24), b)
        d.line([pad + c * tw + 56, top + th - 112, pad + (c + 1) * tw - 56, top + th - 112],
               fill=INK_S, width=2)
        deva.draw_text(im, (pad + c * tw, top + th - 88), name, 36, color=INK, anchor="lm")
        deva.draw_text(im, (pad + c * tw, top + th - 38), "%s · %d" % (role, age),
                       24, color=BRICK, anchor="lm")
    im.convert("RGB").save(os.path.join(OUT, "lineup.png"))
    print("wrote sheets/lineup.png (%dx%d) and %d cards" % (W, H, len(rows)))


if __name__ == "__main__":
    main()
