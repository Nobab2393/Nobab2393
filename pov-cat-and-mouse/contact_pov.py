"""The twelve-frame sheet for POV.

    python3 contact_pov.py      # -> pov-cat-and-mouse-contact.png
"""

import os
import subprocess

from PIL import Image, ImageDraw

import deva

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.join(HERE, "pov-cat-and-mouse-1080x1920.mp4")
BUILD = os.path.join(HERE, "build")

BG = (18, 18, 19)
INK = (245, 243, 238)
INK_S = (166, 163, 158)
RULE = (196, 74, 58)

TIMES = [2.0, 9.0, 18.0, 22.6, 27.0, 34.0, 41.0, 48.0, 53.0, 58.4, 64.0, 71.5]
COLS, ROWS = 6, 2
TH_W, TH_H = 378, 672
PAD = 26
HEAD = 182


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def grab(t):
    p = os.path.join(BUILD, "sheet-%05.1f.png" % t)
    subprocess.run([ffmpeg(), "-y", "-v", "error", "-ss", "%.3f" % t, "-i", FILM,
                    "-frames:v", "1", p], check=True)
    return Image.open(p).convert("RGB").resize((TH_W, TH_H), Image.LANCZOS)


def main():
    W = PAD + COLS * (TH_W + PAD)
    H = HEAD + ROWS * (TH_H + 56) + PAD
    sheet = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(sheet)
    deva.draw_text(sheet, (PAD + 6, 62), "POV", 62, 700, INK, anchor="lm")
    deva.draw_text(sheet, (PAD + 8, 116), "প্রথম পুরুষ · একটা বাড়ি, তিনটে প্রাণী · ১:১৫",
                   26, 400, INK_S, anchor="lm")
    d.rectangle((PAD + 6, HEAD - 22, PAD + 6 + 96, HEAD - 16), fill=RULE)

    for i, t in enumerate(TIMES):
        x = PAD + (i % COLS) * (TH_W + PAD)
        y = HEAD + (i // COLS) * (TH_H + 56)
        sheet.paste(grab(t), (x, y))
        mm, ss = int(t // 60), t - 60 * int(t // 60)
        deva.draw_text(sheet, (x + 3, y + TH_H + 22), "%d:%04.1f" % (mm, ss), 24, 600, INK_S,
                       anchor="lm")

    out = os.path.join(HERE, "pov-cat-and-mouse-contact.png")
    sheet.convert("RGB").save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main()
