#!/usr/bin/env python3
"""Contact sheet: 6 stills from the demo, each with the 9:16 safe area marked."""
import os
from PIL import Image, ImageDraw, ImageFont

FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TILES = [("f000", "0.00s disc"), ("f015", "0.50s bars"), ("f060", "2.00s bars settle"),
         ("f090", "3.00s number"), ("f120", "4.00s fill"), ("f170", "5.67s type")]
TW, TH = 270, 480
PAD = 18
sheet = Image.new("RGB", (TW * 6 + PAD * 7, TH + PAD * 2 + 46), (240, 238, 230))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype(FR, 20)
for i, (name, label) in enumerate(TILES):
    x = PAD + i * (TW + PAD)
    im = Image.open("frames/%s.png" % name).convert("RGB").resize((TW, TH), Image.LANCZOS)
    sheet.paste(im, (x, PAD))
    # safe area: x 60-1020, y 250-1600 at 1080x1920
    k = TH / 1920.0
    d.rectangle([x + 60 * k, PAD + 250 * k, x + 1020 * k, PAD + 1600 * k],
                outline=(0, 160, 90), width=2)
    d.text((x, PAD + TH + 12), label, font=f, fill=(25, 25, 25))
sheet.save("frames/contact-sheet.jpg", quality=92)
print("sheet", sheet.size, os.path.getsize("frames/contact-sheet.jpg"))
