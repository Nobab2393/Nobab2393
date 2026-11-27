#!/usr/bin/env python3
"""prep_stick.py — cut the stickman plate out and rig his face.

The head is an off-white circle on a paper field: same value, so the cut uses
connectivity from the border, never a colour threshold. The mouth that is drawn in the
plate is painted out here and redrawn every frame from the take.
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = np.array([240, 238, 230], dtype=np.int16)
INK = np.array([26, 23, 20], dtype=np.int16)


def flatten(a, tol=22):
    h, w, _ = a.shape
    near = np.abs(a - PAPER).max(2) <= tol
    seen = np.zeros((h, w), bool)
    stack = [(0, x) for x in range(w)] + [(h - 1, x) for x in range(w)]
    stack += [(y, 0) for y in range(h)] + [(y, w - 1) for y in range(h)]
    while stack:
        y, x = stack.pop()
        if y < 0 or x < 0 or y >= h or x >= w or seen[y, x] or not near[y, x]:
            continue
        seen[y, x] = True
        stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    out = a.copy()
    out[seen] = PAPER
    return out, seen


def main():
    from PIL import ImageFilter

    src = os.path.join(HERE, "stickman-a.png")
    a = np.asarray(Image.open(src).convert("RGB")).astype(np.int16)
    a[1330:1520, 380:440] = PAPER                     # the stray hairline left of the helmet

    h, w, _ = a.shape
    # The shirt is the same off-white as the paper, so colour can never separate them.
    # Geometry can: the figure is ringed by ink. Close the ink by a few pixels so the
    # anti-aliased gaps seal, then flood the *outside* only.
    lum = a.mean(2)
    ink = (lum < 175).astype(np.uint8) * 255
    closed = np.asarray(Image.fromarray(ink, "L").filter(ImageFilter.MaxFilter(7))) > 128
    free = ~closed
    seen = np.zeros((h, w), bool)
    stack = [(0, x) for x in range(w)] + [(h - 1, x) for x in range(w)]
    stack += [(y, 0) for y in range(h)] + [(y, w - 1) for y in range(h)]
    while stack:
        y, x = stack.pop()
        if y < 0 or x < 0 or y >= h or x >= w or seen[y, x] or not free[y, x]:
            continue
        seen[y, x] = True
        stack += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    for _ in range(2):
        seen = np.asarray(Image.fromarray(seen.astype(np.uint8) * 255, "L")
                          .filter(ImageFilter.MaxFilter(3))) > 128

    rgb = a.copy()
    rgb[seen] = PAPER
    rgb = rgb.astype(np.uint8)
    alpha = np.where(seen, 0, 255).astype(np.uint8)
    d = np.abs(a - PAPER).max(2)
    grown = np.asarray(Image.fromarray((~seen).astype(np.uint8) * 255, "L")
                       .filter(ImageFilter.MinFilter(5))) > 128
    band = (~seen) & grown
    alpha[band] = 255

    ys, xs = np.where(alpha > 8)
    y0, y1 = max(0, ys.min() - 2), min(h, ys.max() + 3)
    x0, x1 = max(0, xs.min() - 2), min(w, xs.max() + 3)
    rgba = np.dstack([rgb, alpha])[y0:y1, x0:x1]
    im = Image.fromarray(rgba, "RGBA")
    im.save(os.path.join(HERE, "cut.png"))
    print("cut", im.size, "opaque %.3f" % ((np.asarray(im)[:, :, 3] > 200).mean()))

    # ---- find the face: two dots and a short line, in the top third
    h, w = im.height, im.width
    head = np.asarray(im)[: int(h * 0.34)]
    lum = head[:, :, :3].astype(np.int16).mean(2)
    ink = (lum < 100) & (head[:, :, 3] > 200)
    H, W = ink.shape
    seen = np.zeros_like(ink)
    blobs = []
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
                blobs.append(dict(n=len(pix), x0=min(xx), x1=max(xx), y0=min(yy), y1=max(yy),
                                  cx=(min(xx) + max(xx)) / 2, cy=(min(yy) + max(yy)) / 2,
                                  w=max(xx) - min(xx) + 1, h=max(yy) - min(yy) + 1))
    # an eye is a small round dot: 18-44 px across, roughly square, seen as a pair
    dots = [b for b in blobs if 18 <= b["w"] <= 44 and 18 <= b["h"] <= 44
            and 0.7 < b["w"] / max(1, b["h"]) < 1.4]
    eyes = []
    for i, b1 in enumerate(dots):
        for b2 in dots[i + 1:]:
            if abs(b1["cy"] - b2["cy"]) <= 0.02 * H and abs(b1["n"] - b2["n"]) < 0.35 * b1["n"]:
                eyes = sorted([b1, b2], key=lambda b: b["cx"])
                break
        if eyes:
            break
    assert len(eyes) == 2, "no eye pair found"
    face = [b for b in blobs if b not in eyes and b["w"] > 3.2 * b["h"] and b["n"] < 2500
            and b["cy"] > eyes[0]["cy"] + 20]
    mouth = max(face, key=lambda b: b["w"]) if face else None
    print("eyes", [(round(b["cx"]), round(b["cy"]), round(b["w"] / 2)) for b in eyes])
    print("mouth", mouth and (round(mouth["cx"]), round(mouth["cy"]),
                              round(mouth["w"] / 2), round(mouth["h"] / 2)))

    face_col = tuple(int(v) for v in np.median(
        np.asarray(im)[int(mouth["cy"]) - 40:int(mouth["cy"]) - 20,
                       int(mouth["cx"]) - 20:int(mouth["cx"]) + 20, :3].reshape(-1, 3), axis=0))
    rig = dict(
        eyes=[[round(b["cx"]), round(b["cy"]), round(max(b["w"], b["h"]) / 2 + 2)] for b in eyes],
        mouth=[round(mouth["cx"]), round(mouth["cy"]),
               round(mouth["w"] / 2), max(3, round(mouth["h"] / 2))],
        face=list(face_col),
    )

    # inpaint: the face is flat, so clone the band above the mouth over it
    cleared = im.copy()
    mx, my, mw, mh = rig["mouth"]
    band = im.crop((mx - mw - 10, my - mh - 22, mx + mw + 10, my - mh - 6))
    box = (mw + 10, mh + 7)
    cleared.paste(band.resize((2 * box[0], 2 * box[1]), Image.LANCZOS),
                  (mx - box[0], my - box[1]))
    cleared.save(os.path.join(HERE, "rig.png"))
    json.dump(rig, open(os.path.join(HERE, "rig.json"), "w"), indent=1)

    card = Image.new("RGB", (im.width * 2, im.height // 2), (240, 238, 230))
    head_img = cleared.crop((0, 0, im.width, int(im.height * 0.34)))
    k = min((card.width - 40) / head_img.width, (card.height - 40) / head_img.height) * 2
    head_img = head_img.resize((round(head_img.width * k), round(head_img.height * k)),
                               Image.LANCZOS)
    card.paste(head_img, (20, 20), head_img)
    card.save(os.path.join(HERE, "rig-check.png"))
    print("head crop", head_img.size, "face", face_col)


if __name__ == "__main__":
    main()
