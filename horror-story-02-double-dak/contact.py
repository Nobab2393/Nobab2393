"""Contact sheet: twelve frames pulled from the finished film, on one page."""

import os
import subprocess

from PIL import Image, ImageDraw


import deva
import plan as P

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
FILM = os.path.join(HERE, "horror-story-02-double-dak-1080x1920.mp4")
TW, TH = 360, 640
COLS, ROWS = 6, 2
PAPER = (232, 220, 192)
INK = (26, 23, 20)
INK_S = (104, 96, 86)


def main():
    plan = P.build()
    times = [0.6 + i * (plan["total"] - 3.0) / 11 for i in range(12)]
    tiles = []
    for i, t in enumerate(times):
        p = os.path.join(BUILD, "cs-%02d.png" % i)
        subprocess.run([P.ffmpeg(), "-y", "-v", "error", "-ss", "%.3f" % t,
                        "-i", FILM, "-frames:v", "1", p], check=True)
        tiles.append((t, Image.open(p).convert("RGB").resize((TW, TH), Image.LANCZOS)))

    pad = 26
    top = 150
    W = COLS * TW + pad * (COLS + 1)
    H = top + ROWS * (TH + 46) + pad
    sheet = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(sheet)
    deva.draw_text(sheet, (pad, 62), "দুইবার ডাক", 54, 700, INK, anchor="lm")
    deva.draw_text(sheet, (pad + 2, 112),
                   "ভয়ের গল্প · পর্ব ২ · ভোর · বাস · শহর · ২:০১ · twelve frames", 26, 400, INK_S, anchor="lm")
    for i, (t, im) in enumerate(tiles):
        x = pad + (i % COLS) * (TW + pad)
        y = top + (i // COLS) * (TH + 46)
        sheet.alpha_composite(im.convert("RGBA"), (x, y))
        d.rectangle((x, y, x + TW - 1, y + TH - 1), outline=(150, 140, 120))
        lab = "%d:%04.1f" % (int(t // 60), t % 60)
        deva.draw_text(sheet, (x + 2, y + TH + 24), lab, 24, 500, INK_S, anchor="lm")
    out = os.path.join(HERE, "horror-story-02-double-dak-contact.png")
    sheet.convert("RGB").save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main()
