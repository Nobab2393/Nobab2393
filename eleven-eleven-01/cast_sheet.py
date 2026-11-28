"""The cast sheet — three designs, one page, so part 2 and part 3 cannot drift.

    python3 cast_sheet.py            -> eleven-eleven-01-cast.png
"""

import os

from PIL import Image, ImageDraw, ImageOps

import deva
import lines as L

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
W, H = 1080, 1600
BG = (12, 15, 24)


def main():
    sheet = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(sheet)
    d.line([(90, 300), (W - 90, 300)], fill=(120, 40, 44), width=2)
    deva.draw_text(sheet, (W // 2, 148), "এগারোটা এগারো", 76, 700, (238, 234, 226))
    deva.draw_text(sheet, (W // 2, 236), "চরিত্র · পার্ট ১", 34, 500, (150, 162, 180))

    order = ["anika", "sabbir", "ryan"]
    slot = W // 3
    for i, cid in enumerate(order):
        src = Image.open(os.path.join(RAW, "%s-01.png" % cid)).convert("RGB")
        im = ImageOps.fit(src, (slot - 46, 940), Image.LANCZOS, centering=(0.5, 0.42))
        x = i * slot + (slot - im.width) // 2
        sheet.alpha_composite(im.convert("RGBA"), (x, 340))
        cy = 340 + 940 + 40
        c = L.CAST[cid]
        deva.draw_text(sheet, (i * slot + slot // 2, cy), c["name"], 54, 700, (240, 236, 228))
        deva.draw_text(sheet, (i * slot + slot // 2, cy + 62), c["role"], 26, 400, (138, 150, 168))

    deva.draw_text(sheet, (W // 2, H - 74), "2D cel-shaded · ঠান্ডা নীল রাত · এক কণ্ঠ",
                   26, 500, (110, 122, 140))
    out = os.path.join(HERE, "eleven-eleven-01-cast.png")
    sheet.convert("RGB").save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main()
