#!/usr/bin/env python3
"""Contact sheet for the 3D demo."""
import os
from PIL import Image, ImageDraw, ImageFont

FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
TILES = [("f000", "0.00s  the stage"), ("f040", "1.33s  apex"), ("f075", "2.50s  speed-driven stretch"),
         ("f130", "4.33s  orbit + dolly"), ("f200", "6.67s  rest"),
         ("f300", "10.00s  end card in")]
TW, TH, PAD = 270, 480, 18
sheet = Image.new("RGB", (TW * 6 + PAD * 7, TH + PAD * 2 + 46), (20, 19, 24))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype(FR, 19)
for i, (name, label) in enumerate(TILES):
    x = PAD + i * (TW + PAD)
    p = "frames/%s.png" % name
    if not os.path.exists(p):
        continue
    im = Image.open(p).convert("RGB").resize((TW, TH), Image.LANCZOS)
    sheet.paste(im, (x, PAD))
    d.rectangle([x, PAD, x + TW - 1, PAD + TH - 1], outline=(70, 66, 62))
    d.text((x, PAD + TH + 14), label, font=f, fill=(230, 226, 218))
sheet.save("frames/contact-sheet.jpg", quality=92)
print("sheet", sheet.size, os.path.getsize("frames/contact-sheet.jpg"))
