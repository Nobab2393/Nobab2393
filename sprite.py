"""Cut characters out of their white studio backgrounds -> transparent RGBA sprites."""
import os

import numpy as np
from PIL import Image, ImageFilter
from collections import deque

SRC = "images"
OUT = "assets/sprites"


def remove_background(img):
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    h, w, _ = a.shape
    # near-white background seeded from the border
    near_white = (a.min(axis=2) >= 238)
    visited = np.zeros((h, w), dtype=bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near_white[y, x] and not visited[y, x]:
                visited[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near_white[y, x] and not visited[y, x]:
                visited[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and near_white[ny, nx] and not visited[ny, nx]:
                visited[ny, nx] = True
                q.append((ny, nx))
    alpha = np.where(visited, 0, 255).astype(np.uint8)

    # soften a 1px halo left over from the antialiased border
    am = Image.fromarray(alpha, "L").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))

    # kill the painted grey contact shadow in the lower part of the plate
    rgb = np.asarray(img.convert("RGB")).astype(np.int16)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    lum = rgb.mean(axis=2)
    yb = int(h * 0.86)
    shadow = (np.arange(h)[:, None] >= yb) & (sat < 14) & (lum > 150) & (lum < 246)
    am_np = np.asarray(am).copy()
    am_np[shadow] = 0
    am = Image.fromarray(am_np, "L").filter(ImageFilter.GaussianBlur(0.6))

    out = img.convert("RGBA")
    out.putalpha(am)
    return out


def trim(img, pad=4):
    bbox = img.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox()
    if not bbox:
        return img
    l, t, r, b = bbox
    return img.crop((max(0, l - pad), max(0, t - pad), min(img.width, r + pad), min(img.height, b + pad)))


def build(name, src_file, target_h=None):
    src = Image.open(os.path.join(SRC, src_file))
    sp = trim(remove_background(src))
    if target_h:
        k = target_h / sp.height
        sp = sp.resize((int(sp.width * k), target_h), Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".png")
    sp.save(path)
    print(f"{name:16s} {sp.size}  <- {src_file}")
    return path


CHARACTERS = {
    "king_idle": ("king.png", 760),
    "king_declare": ("king_declare.png", 760),
    "rival": ("rival.png", 700),
    "biz_walk": ("businessman.png", 720),
    "biz_stand": ("businessman_stand.png", 720),
    "student_walk": ("student_walk.png", 720),
    "student_idle": ("youngman.png", 720),
    "mentor": ("mentor.png", 740),
}

if __name__ == "__main__":
    for n, (f, h) in CHARACTERS.items():
        build(n, f, h)

    # quick contact sheet over a dark background to judge the cut-outs
    sheet = Image.new("RGBA", (1800, 900), (22, 30, 46, 255))
    x = 10
    for n in CHARACTERS:
        sp = Image.open(os.path.join(OUT, n + ".png"))
        k = min(1.0, 850 / sp.height)
        sp = sp.resize((int(sp.width * k), int(sp.height * k)), Image.LANCZOS)
        sheet.alpha_composite(sp, (x, 870 - sp.height))
        x += sp.width + 12
        if x > 1700:
            break
    sheet.convert("RGB").save("/tmp/sheet.png")
    print("sheet ok")
