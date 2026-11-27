"""flatten.py — normalise the generated character art into a clean, cuttable cast.

The image model paints the paper background with a little variation (a few levels of noise
and a soft vignette). That is invisible on its own but it is texture, and texture is not
allowed in this style. So:

    * every background pixel is forced to exactly PAPER
    * a flood fill from the four corners finds the *outside* of the figure, so the off-white
      kurta / saree / vest — which is almost the same colour as the paper — stays solid
    * the figure is cropped to its own silhouette and saved as RGBA with a real alpha edge

    python3 flatten.py

Writes  <name>-flat.png  (full frame, exact paper)  and  cut/<name>.png  (cropped RGBA).
"""
import glob
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

PAPER = (240, 238, 230)
TOL = 22          # how far from PAPER still counts as "paper" (noise + vignette)
GROW = 2          # close speckle gaps in the background mask before filling


def outer_background(rgb):
    a = rgb.astype(np.int16)
    dist = np.abs(a - np.array(PAPER, np.int16)).max(axis=2)
    near = Image.fromarray(((dist < TOL) * 255).astype(np.uint8), "L")
    d = ImageDraw.Draw(near)
    for seed in ((0, 0), (near.width - 1, 0), (0, near.height - 1),
                 (near.width - 1, near.height - 1)):
        if near.getpixel(seed) == 255:
            ImageDraw.floodfill(near, seed, 128, thresh=0)
    bg = np.asarray(near) == 128

    # a stray noisy pixel inside the background leaves a hole in the flood fill: fill any
    # pixel whose whole neighbourhood is already background
    for _ in range(GROW):
        g = bg.copy()
        g[1:, :] &= bg[:-1, :]
        g[:-1, :] &= bg[1:, :]
        g[:, 1:] &= bg[:, :-1]
        g[:, :-1] &= bg[:, 1:]
        bg |= g
    return bg


def main():
    os.makedirs("cut", exist_ok=True)
    for path in sorted(glob.glob("c[1-5]-*.png")):
        if path.endswith("-flat.png"):
            continue
        name = os.path.splitext(os.path.basename(path))[0]
        rgb = np.asarray(Image.open(path).convert("RGB"))
        bg = outer_background(rgb)
        flat = rgb.copy()
        flat[bg] = PAPER
        Image.fromarray(flat).save(f"{name}-flat.png")

        alpha = (~bg * 255).astype(np.uint8)
        ys, xs = np.where(alpha > 0)
        box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        cut = Image.fromarray(flat).crop(box).convert("RGBA")
        cut.putalpha(Image.fromarray(alpha[box[1]:box[3], box[0]:box[2]], "L"))
        cut.save(f"cut/{name}.png")
        h, w = cut.size
        print(f"{name:26s} frame {rgb.shape[1]}x{rgb.shape[0]}  cut {w}x{h}  "
              f"bg removed {100 * bg.mean():.0f}%")


if __name__ == "__main__":
    main()
