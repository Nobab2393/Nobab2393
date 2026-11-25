"""test-cast2d.py — the 2D cast bench. python3 test-cast2d.py"""
import math
import sys

from PIL import Image

import flat
import rig2d
from flat import (INK, INK2, HAIR, SKIN, WHITE, CLAY, OLIVE, SLATE, SAND, PAPER2, PAPER3,
                  CLAY_D, OLIVE_D, SLATE_D)

AYAN = dict(shirt=WHITE, shorts=SLATE_D, skin=SKIN, hair=HAIR, bag=SAND, shoe=INK2)
RAFIQ = dict(shirt=CLAY, shorts=INK2, skin=SKIN, hair=HAIR, belt=(240, 226, 198), shoe=HAIR)
MIRA = dict(shirt=SLATE, shorts=OLIVE_D, skin=SKIN, hair=HAIR, hood=OLIVE,
            scarf=CLAY, shoe=INK2)


def main():
    cv = flat.Canvas(w=1080, h=1080, bg=flat.PAPER)
    cv.rect([0, 760, 1080, 1080], flat.SAND, None)
    cv.line([(0, 760), (1080, 760)], flat.SAND_D, 3, caps=False)
    gy = 980
    sc = 470

    rig2d.draw(cv, AYAN, sc, gy, 170, pose=dict(walk=0.0))
    rig2d.draw(cv, RAFIQ, sc * 1.15, gy, 420, pose=dict(walk=0.35))
    rig2d.draw(cv, AYAN, sc, gy, 700, pose=dict(kneel=1.0, reach=0.9))
    rig2d.draw(cv, MIRA, sc * 0.92, gy + 60, 950, pose=dict(walk=0.7))

    cv.text((540, 90), "কাস্ট · ২ডি", 46, 700, INK)
    rig2d.bag_on_back(cv, AYAN, sc, rig2d.joints(sc, gy, 170, {}), {}, max(2.0, 0.006 * sc))
    cv.finish().save("frames/cast2d.png")
    print("cast ok")


if __name__ == "__main__":
    main()
