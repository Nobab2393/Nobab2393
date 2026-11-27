#!/usr/bin/env python3
"""prep7b.py — measure face rigs (eyes, mouth) from the cut sprites.

Blob analysis found the ink features; this file stores the chosen coordinates,
samples a skin tone per character, paints the original mouth out, and saves
  cast/<name>-rig.png   sprite with the mouth zone cleared
  cast/rig-check.png    verification image with eye + mouth markers
  cast/rigs.json        the numbers film8.py animates with
"""
import json
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CAST = os.path.join(HERE, "cast")
INK = np.array([26, 23, 20])

# eyes: (x, y, r) sprite pixels · mouth: (x, y, halfwidth, halfheight)
RIGS = {
    "01-dada":      dict(eyes=[(168, 101, 9), (215, 100, 9)], mouth=(194, 158, 27, 13)),
    "02-bou":       dict(eyes=[(108, 102, 7), (159, 102, 7)], mouth=(134, 145, 19, 8)),
    "03-chele":     dict(eyes=[(134, 113, 8), (192, 113, 8)], mouth=(163, 161, 24, 9)),
    "04-natni":     dict(eyes=[(243, 163, 11), (347, 163, 11)], mouth=(295, 226, 40, 19)),
    "05-kagojwala": dict(eyes=[(120, 105, 8), (170, 104, 8)], mouth=(146, 153, 22, 9)),
}


def skin_tone(rgb, al, cx, cy, r):
    """Median of opaque, non-ink pixels on a ring outside the mouth zone."""
    h, w = al.shape
    patch = []
    for y in range(max(0, cy - 3 * r), min(h, cy + 3 * r)):
        for x in range(max(0, cx - 3 * r), min(w, cx + 3 * r)):
            d = ((x - cx) / (1.6 * r)) ** 2 + ((y - cy) / (1.6 * r)) ** 2
            px = rgb[y, x]
            if 1.0 < d < 2.6 and al[y, x] > 240 and np.abs(px - INK).max() > 90:
                patch.append(px)
    if not patch:
        return (200, 160, 110)
    return tuple(int(v) for v in np.median(np.array(patch), axis=0))


def clear_mouth(im, mouth, skin):
    """Paint a rounded skin patch over the original mouth so frames can redraw it."""
    im = im.copy()
    d = ImageDraw.Draw(im)
    cx, cy, hw, hh = mouth
    d.ellipse([cx - hw - 2, cy - hh - 1, cx + hw + 2, cy + hh + 1], fill=skin)
    return im


def main():
    rigs = {}
    checks = []
    for name, rig in RIGS.items():
        im = Image.open(os.path.join(CAST, name + ".png")).convert("RGBA")
        a = np.asarray(im)
        rgb, al = a[:, :, :3].astype(np.int16), a[:, :, 3]
        m = rig["mouth"]
        skin = skin_tone(rgb, al, m[0], m[1], max(m[2], m[3]))
        rig["skin"] = skin
        rigs[name] = rig
        cleared = clear_mouth(im, m, skin)
        cleared.save(os.path.join(CAST, name + "-rig.png"))
        # verification crop
        top = max(0, min(e[1] for e in rig["eyes"]) - 60)
        crop = im.crop((max(0, m[0] - 150), top, min(im.width, m[0] + 150), min(im.height, m[1] + 80)))
        crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
        card = Image.new("RGB", (crop.width, crop.height), (240, 238, 230))
        card.paste(crop, (0, 0), crop)
        d = ImageDraw.Draw(card)
        ox, oy = max(0, m[0] - 150), top
        for (ex, ey, er) in rig["eyes"]:
            x, y = (ex - ox) * 2, (ey - oy) * 2
            d.ellipse([x - er * 2, y - er * 2, x + er * 2, y + er * 2], outline=(220, 60, 60), width=2)
            d.line([x - 6, y, x + 6, y], fill=(220, 60, 60), width=1)
        x, y, hw, hh = (m[0] - ox) * 2, (m[1] - oy) * 2, m[2] * 2, m[3] * 2
        d.ellipse([x - hw, y - hh, x + hw, y + hh], outline=(60, 120, 220), width=2)
        d.rectangle([0, 0, 3, 3], fill=skin)
        checks.append((name, card, skin))

    W = sum(c[1].width for c in checks) + 8 * (len(checks) + 1)
    H = max(c[1].height for c in checks) + 30
    sheet = Image.new("RGB", (W, H), (26, 23, 20))
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    d = ImageDraw.Draw(sheet)
    x = 8
    for name, card, skin in checks:
        sheet.paste(card, (x, 24))
        d.text((x + 2, 6), f"{name}  skin {skin}", font=f, fill=(235, 228, 214))
        x += card.width + 8
    sheet.save(os.path.join(CAST, "rig-check.png"))
    with open(os.path.join(CAST, "rigs.json"), "w") as fh:
        json.dump(rigs, fh, indent=1)
    print("wrote rig-check.png", sheet.size)


if __name__ == "__main__":
    main()
