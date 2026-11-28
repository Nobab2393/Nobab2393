"""A contact sheet: twelve frames, in order, with the beat under each one.

    python3 contact.py build/eleven-eleven-p1.mp4 eleven-eleven-p1-contact.png
"""

import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

import deva

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
COLS, ROWS = 3, 4
TW, TH = 540, 960          # a 1080×1920 frame at half size
GAP, PAD, HEAD = 18, 46, 150


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def grab(video, t, out):
    subprocess.run([ffmpeg(), "-y", "-v", "error", "-ss", "%.3f" % t, "-i", video,
                    "-frames:v", "1", out], check=True)
    return Image.open(out).convert("RGB")


def main(video, out):
    tl = json.load(open(os.path.join(BUILD, "timeline.json")))
    n = COLS * ROWS
    total = tl["total"]
    times = [total * (i + 0.55) / n for i in range(n)]
    W = PAD * 2 + COLS * TW + (COLS - 1) * GAP
    H = HEAD + PAD + ROWS * TH + (ROWS - 1) * GAP + PAD
    sheet = Image.new("RGBA", (W, H), (12, 14, 22, 255))
    d = ImageDraw.Draw(sheet)
    deva.draw_text(sheet, (PAD, 52), "এগারোটা এগারো", 52, 700, (238, 234, 226), anchor="lm")
    deva.draw_text(sheet, (PAD + 470, 56), "পার্ট ১ · ভুল নম্বর · %0.1f সেকেন্ড" % total,
                   26, 500, (140, 152, 172), anchor="lm")
    d.line([(PAD, 104), (W - PAD, 104)], fill=(120, 40, 44), width=2)

    for i, t in enumerate(times):
        im = grab(video, t, os.path.join(BUILD, "_grab.png"))
        im = im.resize((TW, TH), Image.LANCZOS)
        x = PAD + (i % COLS) * (TW + GAP)
        y = HEAD + (i // COLS) * (TH + GAP)
        sheet.alpha_composite(im.convert("RGBA"), (x, y))
        deva.draw_text(sheet, (x + 8, y + TH - 6), "%0.1f s" % t, 22, 500, (220, 216, 208),
                       anchor="lm")
    sheet.convert("RGB").save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    v = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BUILD, "video.mp4")
    o = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "eleven-eleven-p1-contact.png")
    main(v, o)
