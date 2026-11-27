"""prep6.py — take the five supplied character cards apart.

Each card is the same construction: a black rounded frame, a pastel sky, a white cloud, a
yellow sun, two hills — and a flat bust standing in the middle, cut off at the bottom edge.

For the film we want only the bust, on our own background. So:

    1. find the inner canvas (strip the black frame)
    2. learn the card's own background colours (sky, both hills, sun, cloud) by sampling
       known regions
    3. keep every pixel that is none of those, take the big connected blob in the middle,
       fill its holes, and use it as alpha
    4. save the bust as RGBA, plus a proof sheet to look at

    python3 prep6.py
"""
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
UP = "/tmp/arena-coding-uploads"
OUT = os.path.join(HERE, "cast")

FILES = {
    "dada": "image-10.png",      # grandfather — glasses, white beard, red shawl
    "chele": "image-11.png",     # the son — headband, green checked shirt
    "bou": "image-12.png",       # the daughter-in-law — bun, green/red saree
    "natni": "image-13.png",     # the granddaughter — two buns, yellow polka frock
    "kagojwala": "image-14.png",  # the paper man — glasses, white kurta, blue placket
}


def inner_canvas(a):
    """The card inside the black frame: walk in from the middle until the frame starts."""
    dark = a.sum(2) < 90
    h, w = dark.shape
    cy, cx = h // 2, w // 2
    top = np.where(~dark[:, cx])[0].min()
    bot = np.where(~dark[:, cx])[0].max() + 1
    left = np.where(~dark[cy])[0].min()
    right = np.where(~dark[cy])[0].max() + 1
    return top, bot, left, right


def outside(canvas):
    """Everything reachable from the corners without crossing the figure's ink contour.

    Each card is drawn with a continuous dark outline around the whole bust, so a flood fill
    through the light pixels stops dead at the figure — no colour bookkeeping needed. The
    bust runs off the bottom edge of the card, and the only way in would be under it, which
    the canvas edge blocks.
    """
    light = canvas.sum(2) >= 300
    h, w = light.shape
    seen = np.zeros_like(light, bool)
    stack = []
    for sy, sx in ((2, 2), (2, w - 3), (h // 3, 2), (h // 3, w - 3), (2, w // 2)):
        if light[sy, sx] and not seen[sy, sx]:
            seen[sy, sx] = True
            stack.append((sy, sx))
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and light[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                stack.append((ny, nx))
    return seen


def is_background(canvas):
    """Background colours, learned from the two side strips — the figure never reaches them."""
    h, w, _ = canvas.shape
    strips = np.concatenate([canvas[:, :28].reshape(-1, 3), canvas[:, -28:].reshape(-1, 3)])
    palette = []
    for c in strips[::7]:
        if not any(max(abs(int(c[i]) - o[i]) for i in range(3)) < 8 for o in palette):
            palette.append(tuple(int(v) for v in c))
    bg = np.zeros((h, w), bool)
    for c in palette:
        bg |= (np.abs(canvas - np.array(c, np.int16)).max(2) < 10)
    return bg


def fill_holes(mask):
    """Close the pockets the figure encloses (eyes behind glasses, teeth, gaps in cloth)."""
    h, w = mask.shape
    free = ~mask
    seen = np.zeros((h, w), bool)
    stack = [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]
    for y, x in stack:
        seen[y, x] = True
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and free[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                stack.append((ny, nx))
    return mask | (free & ~seen)


def blob(mask):
    """Flood from the bottom centre — the bust always touches the bottom edge."""
    h, w = mask.shape
    seen = np.zeros_like(mask, bool)
    seeds = [(h - 1, x) for x in range(w // 2 - 40, w // 2 + 40) if mask[h - 1, x]]
    if not seeds:
        ys, xs = np.where(mask)
        seeds = [(int(ys.mean()), int(xs.mean()))]
    stack = seeds[:]
    for y, x in stack:
        seen[y, x] = True
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                stack.append((ny, nx))
    # close pinholes left by anti-aliased edges
    for _ in range(2):
        g = seen.copy()
        g[1:, :] |= seen[:-1, :] & seen[1:, :]
        g[:-1, :] |= seen[1:, :] & seen[:-1, :]
        g[:, 1:] |= seen[:, :-1] & seen[:, 1:]
        g[:, :-1] |= seen[:, 1:] & seen[:, :-1]
        seen = g
    return seen


def main():
    os.makedirs(OUT, exist_ok=True)
    proof = []
    for name, fn in FILES.items():
        a = np.asarray(Image.open(os.path.join(UP, fn)).convert("RGB")).astype(np.int16)
        y0, y1, x0, x1 = inner_canvas(a)
        canvas = a[y0:y1, x0:x1]
        m = blob(~is_background(canvas))
        m = fill_holes(m)
        ys, xs = np.where(m)
        box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        alpha = (m * 255).astype(np.uint8)
        cut = Image.fromarray(canvas.astype(np.uint8)).crop(box).convert("RGBA")
        cut.putalpha(Image.fromarray(alpha[box[1]:box[3], box[0]:box[2]], "L"))
        cut.save(os.path.join(OUT, f"{name}.png"))
        proof.append((name, cut))
        print(f"{name:10s} canvas {canvas.shape[1]}x{canvas.shape[0]}  "
              f"cut {cut.width}x{cut.height}  kept {100 * m.mean():.0f}%")

    # proof: every bust on one strip, same scale, for eyeballing
    strip = Image.new("RGB", (5 * 300, 380), (245, 243, 236))
    for i, (name, cut) in enumerate(proof):
        k = 340 / cut.height
        im = cut.resize((max(1, int(cut.width * k)), 340), Image.LANCZOS)
        strip.paste(im, (i * 300 + (300 - im.width) // 2, 380 - im.height), im)
        ImageDraw.Draw(strip).text((i * 300 + 10, 10), name, fill=(30, 30, 30))
    strip.save(os.path.join(HERE, "frames", "proof-cast.png"))
    print("wrote frames/proof-cast.png")


if __name__ == "__main__":
    main()
