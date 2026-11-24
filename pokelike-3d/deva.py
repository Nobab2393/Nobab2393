"""Devanagari text as pixels — harfbuzz shaping + fontTools outlines.

PIL cannot shape Indic scripts without libraqm (this box has none), so a raw
ImageFont.truetype().text() would scatter matras. Instead: shape with harfbuzz, pull the
glyph outlines with fontTools, flatten them to polygons and fill them with even-odd parity.
"""
import numpy as np
from PIL import Image, ImageDraw
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONT = "fonts/NotoSansDevanagari.ttf"
_tt_cache = {}


def _instance(weight):
    if weight not in _tt_cache:
        tt = TTFont(FONT)
        if "fvar" in tt:
            tt = instantiateVariableFont(tt, {"wght": weight, "wdth": 100}, inplace=False)
        _tt_cache[weight] = tt
    return _tt_cache[weight]


def _contours(tt, glyph_name, scale, dx, dy):
    gs = tt.getGlyphSet()
    pen_ops = []
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    pen = DecomposingRecordingPen(gs)      # resolves addComponent → real contours
    gs[glyph_name].draw(pen)

    out, cur = [], []
    for op, args in pen.value:
        if op == "moveTo":
            if cur:
                out.append(cur)
            cur = [(args[0][0], args[0][1])]
        elif op == "lineTo":
            cur.append((args[0][0], args[0][1]))
        elif op == "qCurveTo":
            pts = list(args)
            start = cur[-1]
            # implied on-curve points between off-curve pairs
            seq = []
            for p in pts[:-1]:
                seq.append(p)
            end = pts[-1]
            p0 = start
            for i, c in enumerate(seq):
                p2 = end if i == len(seq) - 1 else ((c[0] + seq[i + 1][0]) / 2, (c[1] + seq[i + 1][1]) / 2)
                for k in range(1, 7):
                    s = k / 6.0
                    x = (1 - s) ** 2 * p0[0] + 2 * (1 - s) * s * c[0] + s * s * p2[0]
                    y = (1 - s) ** 2 * p0[1] + 2 * (1 - s) * s * c[1] + s * s * p2[1]
                    cur.append((x, y))
                p0 = p2
            cur.append(end)
        elif op == "curveTo":
            cur.append(args[-1])
        elif op == "closePath":
            if cur:
                out.append(cur)
            cur = []
    if cur:
        out.append(cur)

    polys = []
    for c in out:
        polys.append([((x + dx) * scale, (dy - y) * scale) for x, y in c])
    return polys


def layout(text, size, weight=700):
    """Returns (polygons, width, height, baseline) in pixels."""
    blob = hb.Blob.from_file_path(FONT)
    face = hb.Face(blob)
    hbfont = hb.Font(face)
    hbfont.set_variations({"wght": weight, "wdth": 100})
    hbfont.scale = (face.upem, face.upem)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": True, "calt": True})

    tt = _instance(weight)
    upem = tt["head"].unitsPerEm
    scale = size / upem
    order = tt.getGlyphOrder()

    groups = []          # one polygon list per glyph: XOR inside a glyph, OR between glyphs
    x = 0.0
    y = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        polys = _contours(tt, name, scale, x + pos.x_offset, y + pos.y_offset)
        if polys:
            groups.append(polys)
        x += pos.x_advance
        y += pos.y_advance
    width = x * scale
    return groups, width, size * 1.3


def text_image(text, size, weight=700, color=(255, 255, 255), pad=8, align="left"):
    groups, width, height = layout(text, size, weight)
    xs = [p[0] for g in groups for poly in g for p in poly] or [0]
    ys = [p[1] for g in groups for poly in g for p in poly] or [0]
    w = int(max(xs) - min(xs)) + pad * 2
    h = int(max(ys) - min(ys)) + pad * 2
    w, h = max(w, 4), max(h, 4)
    mask = Image.new("L", (w, h), 0)
    for group in groups:
        glyph = Image.new("L", (w, h), 0)
        for poly in group:                  # counters: XOR within one glyph only
            one = Image.new("L", (w, h), 0)
            ImageDraw.Draw(one).polygon([(x - min(xs) + pad, y - min(ys) + pad) for x, y in poly], fill=255)
            glyph = Image.fromarray(np.bitwise_xor(np.array(glyph), np.array(one)))
        mask = Image.fromarray(np.maximum(np.array(mask), np.array(glyph)))   # union across glyphs

    img = Image.new("RGBA", (w, h), color + (0,))
    img.putalpha(mask)
    return img


def draw_text(base, xy, text, size, weight=700, color=(255, 255, 255), anchor="mm", shadow=None, shadow_blur=10):
    img = text_image(text, size, weight, color)
    x, y = xy
    if anchor == "mm":
        pos = (int(x - img.width / 2), int(y - img.height / 2))
    elif anchor == "lm":
        pos = (int(x), int(y - img.height / 2))
    else:
        pos = (int(x), int(y))
    if shadow:
        halo = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sh = Image.new("RGBA", img.size, shadow + (0,))
        sh.putalpha(img.split()[3])
        halo.alpha_composite(sh, pos)
        from PIL import ImageFilter
        halo = halo.filter(ImageFilter.GaussianBlur(shadow_blur))
        base.alpha_composite(halo)
    base.alpha_composite(img, pos)
    return img.size


if __name__ == "__main__":
    im = Image.new("RGB", (1080, 500), (18, 17, 24)).convert("RGBA")
    draw_text(im, (540, 120), "अंगार और बादल", 96, 700, (255, 236, 200))
    draw_text(im, (540, 250), "एक छोटी सी आग, एक बड़ा तूफ़ान", 44, 500, (200, 196, 190))
    draw_text(im, (540, 360), "फॉलो करो — हर शुक्रवार नई कड़ी", 40, 600, (240, 200, 120))
    im.convert("RGB").save("frames/deva-test.png")
    print("wrote frames/deva-test.png")
