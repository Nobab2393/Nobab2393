#!/usr/bin/env python3
"""prep8.py — rig the street cast for episode 8.

Plates come pre-cut from character-style-preview/street/plates. Here each face gets:
  * eyes located (small round dot pairs)
  * mouth located (the wide flat ink blob under them)
  * the drawn-in mouth inpainted out with the band of cheek above it
so film9.py can redraw the mouth from the take, frame by frame.

    python3 prep8.py
    -> cast/<name>.png  cast/<name>-rig.png  cast/rigs8.json  cast/rig-check8.png
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
PLATES = os.path.join(HERE, "..", "character-style-preview", "street", "plates")
OUT = os.path.join(HERE, "cast")

CAST = [
    ("elder", "01-elder"),
    ("shopkeeper", "02-shopkeeper"),
    ("moneylender", "10-moneylender"),
    ("postman", "08-postman"),
    ("widow", "05-widow"),
    ("bride", "06-bride"),
]

# hand corrections after the automatic pass, in sprite pixels: (ex, ey, r) / (mx,my,hw,hh)
FIX = {
    # (eye1 x,y,r) (eye2 x,y,r) (mouth cx,cy,halfw,halfh) — sprite pixels
    "elder": ((157, 84, 6), (204, 84, 6), (180, 141, 20, 8)),
    "shopkeeper": ((190, 102, 6), (244, 102, 6), (217, 161, 12, 4)),
    "postman": ((169, 112, 6), (218, 112, 6), (194, 157, 16, 4)),
    "widow": ((166, 103, 6), (218, 104, 6), (192, 152, 17, 4)),
}


def blobs(im, frac=0.34):
    a = np.asarray(im)
    head = a[: int(im.height * frac)]
    lum = head[:, :, :3].astype(np.int16).mean(2)
    ink = (lum < 100) & (head[:, :, 3] > 200)
    H, W = ink.shape
    seen = np.zeros_like(ink)
    out = []
    for y in range(H):
        for x in range(W):
            if ink[y, x] and not seen[y, x]:
                st = [(y, x)]
                seen[y, x] = True
                pix = []
                while st:
                    cy, cx = st.pop()
                    pix.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and ink[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            st.append((ny, nx))
                yy = [p[0] for p in pix]
                xx = [p[1] for p in pix]
                out.append(dict(n=len(pix), x0=min(xx), x1=max(xx), y0=min(yy), y1=max(yy),
                                cx=(min(xx) + max(xx)) / 2, cy=(min(yy) + max(yy)) / 2,
                                w=max(xx) - min(xx) + 1, h=max(yy) - min(yy) + 1))
    return out, H


def find(bs, H):
    dots = [b for b in bs if 10 <= b["n"] <= 9000 and 0.55 < b["w"] / max(1, b["h"]) < 1.8
            and b["h"] < 0.16 * H]
    dots.sort(key=lambda b: b["n"], reverse=True)
    eyes = None
    for i, b1 in enumerate(dots):
        for b2 in dots[i + 1:]:
            if abs(b1["cy"] - b2["cy"]) <= 0.03 * H and 0.35 < b1["n"] / b2["n"] < 2.9:
                eyes = sorted([b1, b2], key=lambda b: b["cx"])
                break
        if eyes:
            break
    if not eyes:
        return None, None
    ey = (eyes[0]["cy"] + eyes[1]["cy"]) / 2
    wide = [b for b in bs if b["w"] > 2.6 * b["h"] and b["cy"] > ey + 0.02 * H
            and abs(b["cx"] - (eyes[0]["cx"] + eyes[1]["cx"]) / 2) < 0.09 * H]
    mouth = max(wide, key=lambda b: b["w"]) if wide else None
    return eyes, mouth


def main():
    os.makedirs(OUT, exist_ok=True)
    rigs, tiles = {}, []
    for name, plate in CAST:
        im = Image.open(os.path.join(PLATES, plate + ".png")).convert("RGBA")
        im.save(os.path.join(OUT, name + ".png"))
        bs, H = blobs(im)
        eyes, mouth = find(bs, H)
        if not mouth or not eyes or name in FIX:
            if name in FIX:
                eyes = [dict(cx=FIX[name][0][0], cy=FIX[name][0][1], w=FIX[name][0][2] * 2,
                             h=FIX[name][0][2] * 2, n=400),
                        dict(cx=FIX[name][1][0], cy=FIX[name][1][1], w=FIX[name][1][2] * 2,
                             h=FIX[name][1][2] * 2, n=400)]
                m = FIX[name][2]
                mouth = dict(cx=m[0], cy=m[1], w=m[2] * 2, h=m[3] * 2, n=400)
            else:
                print("!! could not rig", name)
                continue
        rig = dict(
            eyes=[[round(b["cx"]), round(b["cy"]), round(max(b["w"], b["h"]) / 2 + 1)]
                  for b in eyes],
            mouth=[round(mouth["cx"]), round(mouth["cy"]),
                   round(mouth["w"] / 2), max(2, round(mouth["h"] / 2))],
        )
        rigs[name] = rig

        rigged = im.copy()
        mx, my, mw, mh = rig["mouth"]
        # The mouth has to be painted out with something face-coloured. Above it there is
        # often a moustache, and cloning that leaves a dark block where a closed mouth
        # should be — which reads as a mouth that never shuts. Take whichever band is
        # lighter: for a moustache that is the chin, for a beard both are beard.
        def band(box):
            c = im.crop(box)
            a = np.asarray(c.convert("RGBA"), dtype=np.float32)
            m = a[:, :, 3] > 180
            lum = (0.30 * a[:, :, 0] + 0.59 * a[:, :, 1] + 0.11 * a[:, :, 2])[m]
            return c, float(lum.mean()) if lum.size else 0.0
        up, lu = band((mx - mw - 8, my - mh - 20, mx + mw + 8, my - mh - 4))
        dn, ld = band((mx - mw - 8, my + mh + 4, mx + mw + 8, my + mh + 20))
        src = up if lu >= ld else dn
        rigged.paste(src.resize((2 * (mw + 8), 2 * (mh + 8)), Image.LANCZOS),
                     (mx - mw - 8, my - mh - 8))
        rigged.save(os.path.join(OUT, name + "-rig.png"))

        top = max(0, min(e[1] for e in rig["eyes"]) - 70)
        crop = im.crop((max(0, mx - 170), top, min(im.width, mx + 170),
                        min(im.height, my + 90)))
        crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
        card = Image.new("RGB", crop.size, (240, 238, 230))
        card.paste(crop, (0, 0), crop)
        d = ImageDraw.Draw(card)
        ox, oy = max(0, mx - 170), top
        for ex, ey, er in rig["eyes"]:
            x, y = (ex - ox) * 2, (ey - oy) * 2
            d.ellipse([x - er * 2, y - er * 2, x + er * 2, y + er * 2],
                      outline=(210, 60, 50), width=2)
        x, y = (mx - ox) * 2, (my - oy) * 2
        d.ellipse([x - mw * 2, y - mh * 2, x + mw * 2, y + mh * 2],
                  outline=(50, 110, 210), width=2)
        tiles.append((name, card))
        print(name, "eyes", rig["eyes"], "mouth", rig["mouth"])

    W = sum(t[1].width for t in tiles) + 8 * (len(tiles) + 1)
    Hh = max(t[1].height for t in tiles) + 26
    sheet = Image.new("RGB", (W, Hh), (26, 23, 20))
    d = ImageDraw.Draw(sheet)
    x = 8
    for name, card in tiles:
        sheet.paste(card, (x, 22))
        d.text((x + 2, 6), name, fill=(235, 228, 214))
        x += card.width + 8
    sheet.save(os.path.join(OUT, "rig-check8.png"))
    json.dump(rigs, open(os.path.join(OUT, "rigs8.json"), "w"), indent=1)
    print("wrote rig-check8.png", sheet.size)


if __name__ == "__main__":
    main()
