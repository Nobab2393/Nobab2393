#!/usr/bin/env python3
"""Cast test bench: three characters side by side at one scale, on a flat field.

    python3 test-cast.py            -> frames/cast-test.png
    python3 test-cast.py 5.0        -> one time sample
"""
import sys
import numpy as np
from PIL import Image, ImageDraw

import cel3d as C
import cast3
from cel3d import Cam, place, T, S, R

W, H = 1080, 1000
C.L_KEY = C._normalize(np.array([0.46, 0.80, 0.34]))
C.RIM_COL = np.array([1.00, 0.97, 0.86])
cam = Cam(eye=(0.0, 1.55, 7.2), target=(0.0, 1.0, 0.0), fov=30, w=W, h=H)


def main():
    tq = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    img = Image.new("RGBA", (W, H), (206, 210, 206, 255))
    d = ImageDraw.Draw(img)
    y0 = int(cam.project(cam.to_view(np.array([0.0, 0.0, 0.0])))[0][1])
    d.rectangle([0, y0, W, H], fill=(196, 190, 172))
    d.line([(0, y0), (W, y0)], fill=(140, 140, 130), width=2)
    models = [("ayan", cast3.ayan(t=tq, look=0.2)[0], -1.15),
              ("rafiq", cast3.rafiq(t=tq, look=-0.1), 0.0),
              ("mira", cast3.mira(t=tq, look=0.0)[0], 1.05)]
    for name, m, x in models:
        tile, pos = C.render_model_tiled(place(m, T(x, 0, 0)), cam, ss=1.6, outline=(26, 24, 22),
                                         outline_px=5)
        img.alpha_composite(tile, pos)
        p = cam.project(cam.to_view(np.array([x, 0.0, 0.0])))[0]
        d.text((p[0], H - 26), name, anchor="mm", fill=(30, 30, 30))
    img.convert("RGB").save("frames/cast-test.png")
    print("wrote frames/cast-test.png", y0)


if __name__ == "__main__":
    main()
