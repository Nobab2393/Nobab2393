"""Character sheet — the visual gate before any scene is animated.

Three separate portrait renders tiled into one 1080x1920 sheet, so each character gets a
camera that actually frames it.

    python3 sheet.py        -> frames/sheet.png
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import cel3d as C
from cel3d import Cam, place, render_model, T, S, R
import cast

W, H = 1080, 1920
TTF = "/usr/local/lib/python3.11/dist-packages/matplotlib/mpl-data/fonts/ttf/"
FONT_B, FONT_R = TTF + "DejaVuSans-Bold.ttf", TTF + "DejaVuSans.ttf"
INK = (10, 9, 11)


def render_char(model, eye, target, fov, glow=False, w=W, h=H, cx=0.0, cy=0.0):
    cam = Cam(eye=eye, target=target, fov=fov, w=w, h=h)
    layer, _ = render_model(model, cam, outline=INK, glow=glow, outline_px=7)
    if cx or cy:
        layer = Image.fromarray(np.roll(np.array(layer), (int(cy), int(cx)), (0, 1)), "RGBA")
    return layer


def main():
    sheet = Image.new("RGBA", (W, H), (16, 17, 26, 255))

    # --- the three portraits, each framed on its own scale
    cards = []
    ang = cast.angaar(t=0.0, ear=0.5, flame=1.0)
    cards.append(("ANGAAR", "fire pup · 1.4 m", ang,
                  dict(eye=(1.45, 0.98, 3.15), target=(0.0, 0.62, 0.0), fov=30, glow=True)))
    haw = cast.baadal(t=0.0, flap=0.45, y=0.15)
    cards.append(("BAADAL", "storm hawk · 1.9 m span", haw,
                  dict(eye=(1.9, 1.15, 3.9), target=(0.0, 1.0, 0.0), fov=32)))
    rav = cast.ravi(arm=0.55, look=0.45)
    cards.append(("RAVI", "the trainer · 12", rav,
                  dict(eye=(0.35, 1.35, 3.4), target=(0.0, 0.95, 0.0), fov=32)))

    cw, ch = 344, 780
    for i, (name, sub, model, cam_kw) in enumerate(cards):
        layer = render_char(model, **cam_kw)
        bbox = layer.getbbox()
        if bbox:
            pad = 46
            box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                   min(layer.width, bbox[2] + pad), min(layer.height, bbox[3] + pad))
            layer = layer.crop(box)
        scale = min(cw / layer.width, ch / layer.height)
        thumb = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.LANCZOS)
        x = 24 + i * (cw + 12)
        sheet.alpha_composite(thumb, (x, 300))

    d = ImageDraw.Draw(sheet)
    fb, fr = ImageFont.truetype(FONT_B, 46), ImageFont.truetype(FONT_R, 25)
    fsm = ImageFont.truetype(FONT_B, 30)
    fsm2 = ImageFont.truetype(FONT_R, 20)

    d.text((W / 2, 90), "3D ANIME CEL CAST", font=fb, fill=(242, 240, 232), anchor="mm")
    d.text((W / 2, 140), "original characters · software-rendered, no engine", font=fr,
           fill=(150, 144, 138), anchor="mm")

    for i, (name, sub, _, _) in enumerate(cards):
        x = 24 + i * (cw + 12) + cw / 2
        d.text((x, 1150), name, font=fsm, fill=(242, 240, 232), anchor="mm")
        d.text((x, 1188), sub, font=fsm2, fill=(150, 144, 138), anchor="mm")

    # palette strip
    y = 1270
    d.text((W / 2, y - 36), "PALETTE — one accent does the story", font=fsm2, fill=(150, 144, 138), anchor="mm")
    swatches = [("ink", (10, 9, 11)), ("night", (16, 17, 26)), ("slate", (77, 89, 128)),
                ("ember", (237, 107, 51)), ("flame", (255, 168, 82)), ("cream", (247, 235, 204))]
    for i, (label, col) in enumerate(swatches):
        x = 60 + i * 165
        d.rounded_rectangle([x, y, x + 140, y + 90], 14, fill=col + (255,))
        d.text((x + 70, y + 112), label, font=fsm2, fill=(160, 152, 145), anchor="mm")

    d.text((W / 2, 1520), "cel ramp 3 bands · rim light · dilated silhouette outline",
           font=fsm2, fill=(120, 115, 110), anchor="mm")
    d.text((W / 2, 1556), "px-perfect at 1080x1920 · every frame a pure function of t",
           font=fsm2, fill=(120, 115, 110), anchor="mm")

    sheet.convert("RGB").save("frames/sheet.png")
    print("frame-ok frames/sheet.png")


if __name__ == "__main__":
    import os
    os.makedirs("frames", exist_ok=True)
    main()
