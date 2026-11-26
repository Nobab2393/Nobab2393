"""flatten.py — snap the rendered character art back onto the film's five colours.

The image model returns near-flat art with a slightly noisy paper and a dozen in-between
greys. This pulls every pixel within reach of a palette entry onto the exact value, so the
sheet and the film agree on the same numbers, while leaving the anti-aliased edge pixels
untouched (they are further than the tolerance away).

    python3 cast/flatten.py            # in place, prints a colour count per file
    python3 cast/flatten.py --check    # report only
"""
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image

CAST = os.path.dirname(os.path.abspath(__file__))

PAPER = (240, 238, 230)
INK = (26, 23, 20)
WALL = (219, 214, 202)
MID = (142, 136, 124)
SKIN = (201, 139, 98)
BLUE = (106, 155, 204)

BASE = [PAPER, INK, WALL, MID, SKIN]
FILES = ["c1-elder-brother.png", "c2-younger-brother.png", "c3-boudi.png",
         "c4-niece.png", "c5-old-customer.png"]
TOL = 24.0


def flatten(path, extra=()):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    pal = np.array(BASE + list(extra), np.float32)
    d = np.linalg.norm(a[:, :, None, :] - pal[None, None, :, :], axis=3)
    near = d.min(2) < TOL
    idx = d.argmin(2)
    out = a.copy()
    out[near] = pal[idx[near]]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8)), int(near.mean() * 100)


def main():
    check = "--check" in sys.argv
    for fn in FILES:
        p = os.path.join(CAST, fn)
        extra = (BLUE,) if "younger" in fn else ()
        im, pct = flatten(p, extra)
        c = len(Counter(im.get_flattened_data() if hasattr(im, "get_flattened_data")
                        else im.getdata()))
        print("%-24s snapped %2d%% of pixels   %5d distinct colours" % (fn, pct, c))
        if not check:
            im.save(p)


if __name__ == "__main__":
    main()
