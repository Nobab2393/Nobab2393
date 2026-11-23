#!/usr/bin/env python3
"""Contact sheet: six stills, tagged with the beat each one lands on."""
import os
from PIL import Image, ImageDraw, ImageFont

FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TILES = [("f045", "1.50s  apex hold"), ("f080", "2.67s  impact + settle"),
         ("f112", "3.73s  THE SPLIT"), ("f130", "4.33s  layers back"),
         ("f200", "6.67s  dolly mid"), ("f350", "11.67s  end card")]
TW, TH = 270, 480
PAD = 18
sheet = Image.new("RGB", (TW * 6 + PAD * 7, TH + PAD * 2 + 46), (240, 238, 230))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype(FR, 19)
for i, (name, label) in enumerate(TILES):
    x = PAD + i * (TW + PAD)
    im = Image.open("frames/%s.png" % name).convert("RGB").resize((TW, TH), Image.LANCZOS)
    sheet.paste(im, (x, PAD))
    d.rectangle([x, PAD, x + TW - 1, PAD + TH - 1], outline=(205, 200, 190))
    d.text((x, PAD + TH + 14), label, font=f, fill=(25, 25, 25))
sheet.save("frames/contact-sheet.jpg", quality=92)
print("sheet", sheet.size, os.path.getsize("frames/contact-sheet.jpg"))
