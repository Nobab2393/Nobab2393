"""Cel-shaded default look — measurable constants + helpers.

The rule (see STYLE.md): every material gets exactly TWO fills — a base and one shadow —
plus a dark contour. `shade()` produces the shadow tone the way the reference plate does it:
10-25 % darker, pushed slightly cool/desaturated.

    python3 style-reference/cel.py            # print the palette + derived shadows
    python3 style-reference/cel.py --swatch   # write cel-shaded/swatches.png
"""
from __future__ import annotations

INK = "#0B0B0C"
PAPER = "#FDF6E4"

# Measured from cel-shaded/reference.png (k-means over the figure, background removed).
PALETTE = {
    "skin":   "#C0895C",
    "shirt":  "#E4D5B9",
    "pants":  "#676461",
    "hair":   "#4A433D",
    "leather": "#382A23",
    "cloth_red": "#983935",
}

# Shadow of a base tone: value x 0.85, pushed ~6 % toward cool blue-grey.
SHADOW_VALUE = 0.85
SHADOW_COOL = 0.06


def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _hex(c) -> str:
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(v)))) for v in c)


def shade(color: str, value: float = SHADOW_VALUE, cool: float = SHADOW_COOL) -> str:
    """One base tone in, one shadow tone out. No gradients, ever."""
    r, g, b = _rgb(color)
    r, g, b = r * value, g * value, b * value
    # cool shift: lean on the blue, ease off the red
    r -= 255 * cool * 0.5
    b += 255 * cool * 0.5
    return _hex((r, g, b))


def ramp(color: str) -> tuple[str, str]:
    """(base, shadow) for a material — the whole cel ramp."""
    return color, shade(color)


def swatch(path: str = "style-reference/cel-shaded/swatches.png", w: int = 1200, h: int = 460):
    from PIL import Image, ImageDraw, ImageFont
    try:
        f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        f_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        f_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    except OSError:
        f_big = f_sm = f_title = None
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    names = list(PALETTE)
    cw = (w - 80) // len(names)
    for i, n in enumerate(names):
        base = PALETTE[n]
        dark = shade(base)
        x = 40 + i * cw
        d.rectangle([x, 90, x + cw - 24, 250], fill=_rgb(base), outline=_rgb(INK), width=5)
        d.rectangle([x, 250, x + cw - 24, 330], fill=_rgb(dark), outline=_rgb(INK), width=5)
        d.line([x, 250, x + cw - 24, 250], fill=_rgb(INK), width=4)
        d.text((x + 4, 348), n, fill=_rgb(INK), font=f_big)
        d.text((x + 4, 384), base, fill=_rgb(INK), font=f_sm)
        d.text((x + 4, 412), dark, fill=_rgb(INK), font=f_sm)
    d.rectangle([0, 0, w - 1, h - 1], outline=_rgb(INK), width=8)
    d.text((40, 40), "cel-shaded default - base + one shadow per material",
           fill=_rgb(INK), font=f_title)
    img.save(path)
    return path


if __name__ == "__main__":
    import sys
    for k, v in PALETTE.items():
        print("%-10s base %s  shadow %s" % (k, v, shade(v)))
    if "--swatch" in sys.argv:
        print(swatch())
