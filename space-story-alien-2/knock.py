"""Turn one raw plate into a cut-out PNG on a solid alpha (same rules as sheets.py)."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BG = (243, 232, 200)


def knock(path, out):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    # the field colour is whatever the corners are — do not assume the palette
    k = max(4, min(im.size) // 30)
    corners = np.concatenate([a[:k, :k].reshape(-1, 3), a[:k, -k:].reshape(-1, 3),
                              a[-k:, :k].reshape(-1, 3), a[-k:, -k:].reshape(-1, 3)])
    bgc = np.median(corners, axis=0)
    m = (np.abs(a - bgc).max(axis=2) > 9).astype(np.uint8) * 255
    mask = Image.fromarray(m, "L").copy()
    ImageDraw.floodfill(mask, (0, 0), 128, thresh=20)
    alpha = np.where(np.asarray(mask) == 128, 0, 255).astype(np.uint8)
    alpha = np.asarray(Image.fromarray(alpha, "L").filter(ImageFilter.GaussianBlur(0.7)))
    # A plate's off-register halo is drawn *inside* the ink line, so the flood fill cannot
    # reach it: kill thin bands that sit within a few steps of the field colour. Wide areas
    # of the same colour (a cream smock) survive the erosion, thin rings do not.
    near = (np.abs(a - bgc).max(axis=2) < 22).astype(np.uint8)
    er = near.copy()
    for _ in range(4):
        er = er & np.roll(er, 1, 0) & np.roll(er, -1, 0) & np.roll(er, 1, 1) & np.roll(er, -1, 1)
    alpha = np.where(er > 0, 0, alpha).astype(np.uint8)

    ys = np.nonzero(alpha > 40)[0]
    xs = np.nonzero(alpha > 40)[1]
    pad = 8
    box = (max(0, xs.min() - pad), max(0, ys.min() - pad),
           min(im.width, xs.max() + pad + 1), min(im.height, ys.max() + pad + 1))
    im = im.crop(box)
    alpha = Image.fromarray(alpha).crop(box)
    rgba = im.convert("RGBA")
    rgba.putalpha(alpha)
    # normalise to 1225 px tall, like the crew plates
    s = 1225 / rgba.height
    rgba = rgba.resize((max(1, int(rgba.width * s)), 1225), Image.LANCZOS)
    rgba.save(out)
    print(out, rgba.size)


if __name__ == "__main__":
    knock(sys.argv[1], sys.argv[2])
