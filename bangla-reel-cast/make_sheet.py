"""make_sheet.py — one cast sheet for the five Reel characters.

    cd bangla-reel-cast && python3 flatten.py && python3 make_sheet.py

Figures stand on one baseline at proportional heights (the rickshaw puller tallest, the
schoolgirl shortest), labelled in Bangla, with the palette printed underneath. Nothing on
the sheet is outside the palette: no extra tone, no shadow, no gradient.
"""
import glob
import os

from PIL import Image, ImageDraw, ImageFont

import deva

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

PAPER = (240, 238, 230)
INK = (26, 23, 20)
INK_S = (110, 105, 97)
OFFWHITE = (237, 234, 226)
GREY = (142, 136, 124)
CORAL = (217, 119, 87)

W, H, BASE = 2500, 1720, 1276
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

CAST = [
    ("c1", 875, "উপস্থাপক", "ফোন হাতে · প্রথম দুই সেকেন্ড"),
    ("c2", 800, "দোকানদার", "খাতা হাতে · হিসাব মেলে"),
    ("c3", 900, "রিকশাচালক", "গামছা কাঁধে · ঘাম মোছে"),
    ("c4", 745, "ছাত্রী", "খাতা-কলম বুকে · প্রশ্ন করে"),
    ("c5", 812, "চাচা", "লাঠি হাতে · অভিজ্ঞতার কণ্ঠ"),
]
CENTRES = (310, 800, 1300, 1790, 2260)

PALETTE = [
    (PAPER, "কাগজ", "#F0EEE6"),
    (INK, "কালি", "#1A1714"),
    (OFFWHITE, "অফ-হোয়াইট", "#EDEAE2"),
    (GREY, "ধূসর", "#8E887C"),
    (CORAL, "প্রবাল = দিনে একবার", "#D97757"),
]


def cut(name, height):
    path = glob.glob(f"cut/{name}-*.png")[0]
    im = Image.open(path).convert("RGBA")
    k = height / im.height
    return im.resize((max(1, round(im.width * k)), height), Image.LANCZOS)


def main():
    sheet = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(sheet)

    deva.draw_text(sheet, (96, 96), "পাঁচ মুখ", 92, 700, INK, anchor="lm")
    deva.draw_text(sheet, (100, 186),
                   "রিল কাস্ট · ফ্ল্যাট ভেক্টর · পাঁচ রঙের বেশি নয়",
                   34, 500, INK_S, anchor="lm")

    for (name, th, label, role), cx in zip(CAST, CENTRES):
        im = cut(name, th)
        sheet.alpha_composite(im, (cx - im.width // 2, BASE - im.height))
        deva.draw_text(sheet, (cx, BASE + 76), label, 54, 700, INK, anchor="mm")
        sz = 30
        while sz > 20 and deva.layout(role, sz)[1] > 430:
            sz -= 1
        deva.draw_text(sheet, (cx, BASE + 132), role, sz, 500, INK_S, anchor="mm")

    # baseline and rule
    d.line([(96, BASE + 2), (W - 96, BASE + 2)], fill=INK, width=4)
    d.line([(96, 1516), (W - 96, 1516)], fill=(219, 214, 202), width=3)

    yy = 1548
    for i, (col, cap, hx) in enumerate(PALETTE):
        x = 150 + i * 460
        deva.draw_text(sheet, (x, yy), cap, 30, 500, INK_S, anchor="lm")
        bx, by, s = x, yy + 32, 56
        d.rectangle([bx, by, bx + s, by + s], fill=col, outline=INK,
                    width=3 if col == PAPER else 0)
        d.text((bx, by + s + 10), hx, font=ImageFont.truetype(MONO, 24), fill=INK)

    out = "cast-sheet.png"
    sheet.convert("RGB").save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main()
