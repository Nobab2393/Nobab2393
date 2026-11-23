"""Bengali text layout + rendering: harfbuzz shaping -> freetype outlines -> PIL mask."""
from functools import lru_cache

import freetype
import numpy as np
import uharfbuzz as hb
from PIL import Image, ImageChops, ImageDraw, ImageFilter

FONT_SANS = "assets/fonts/NotoSansBengali-VF.ttf"
FONT_SERIF = "assets/fonts/NotoSerifBengali-VF.ttf"


class BengaliFont:
    def __init__(self, path, weight=400, size=64):
        with open(path, "rb") as f:
            data = f.read()
        self.hbfont = hb.Font(hb.Face(data))
        self.ft = freetype.Face(path)
        self.size = size
        self.ft.set_char_size(int(size * 64))
        self.ft.set_var_design_coords([float(weight), 100.0])
        self.upem = self.ft.units_per_EM

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {"kern": True, "liga": True})
        scale = self.size / self.upem
        out, x, y = [], 0.0, 0.0
        for i, p in zip(buf.glyph_infos, buf.glyph_positions):
            out.append((i.codepoint, x + p.x_offset * scale, y + p.y_offset * scale))
            x += p.x_advance * scale
            y += p.y_advance * scale
        return out, x, y

    def measure(self, text):
        return self.shape(text)[1]

    def line_metrics(self):
        s = self.size / self.upem
        return self.ft.ascender * s, -self.ft.descender * s

    def draw(self, text, color=(255, 255, 255), padding=8, shadow=None, shadow_offset=(0, 3),
             stroke=None, stroke_w=0):
        glyphs, adv, _ = self.shape(text)
        asc, desc = self.line_metrics()
        w = int(np.ceil(adv)) + padding * 2 + stroke_w * 2
        h = int(np.ceil(asc + desc)) + padding * 2 + stroke_w * 2
        base_y = padding + stroke_w + int(np.ceil(asc))

        mask = Image.new("L", (w, h), 0)
        for gid, ox, oy in glyphs:
            self.ft.load_glyph(gid, freetype.FT_LOAD_NO_BITMAP | freetype.FT_LOAD_NO_HINTING)
            ol = self.ft.glyph.outline
            if not ol.points:
                continue
            dx = padding + stroke_w + ox
            dy = base_y - oy
            gmask = Image.new("1", (w, h), 0)
            for poly in self._contours(ol, dx, dy):
                layer = Image.new("1", (w, h), 0)
                ImageDraw.Draw(layer).polygon(poly, fill=1)
                gmask = ImageChops.logical_xor(gmask, layer)
            if gmask.getbbox():
                mask = ImageChops.lighter(mask, gmask.convert("L").point(lambda v: 255 if v > 0 else 0))

        if stroke_w:
            big = mask.filter(ImageFilter.MaxFilter(stroke_w * 2 + 1))
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            img.paste(Image.new("RGBA", (w, h), stroke + (255,)), (0, 0), big)
            top = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            top.paste(Image.new("RGBA", (w, h), color + (255,)), (0, 0), mask)
            img.alpha_composite(top)
        else:
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            img.paste(Image.new("RGBA", (w, h), color + (255,)), (0, 0), mask)

        if shadow:
            sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            sh.paste(Image.new("RGBA", (w, h), shadow + (255,)), shadow_offset, img.split()[3])
            sh.alpha_composite(img)
            img = sh
        return img

    def block(self, lines, color=(255, 255, 255), leading=1.42, align="left",
              shadow=None, stroke=None, stroke_w=0, padding=8):
        """Render multiple lines into one RGBA image with consistent baselines."""
        if isinstance(lines, str):
            lines = [lines]
        glyph_sets = [self.shape(t) for t in lines]
        asc, desc = self.line_metrics()
        line_h = self.size * leading
        maxw = max(g[1] for g in glyph_sets) if glyph_sets else 0
        w = int(np.ceil(maxw)) + padding * 2 + stroke_w * 2
        h = int(np.ceil(line_h * (len(lines) - 1) + asc + desc)) + padding * 2 + stroke_w * 2
        base0 = padding + stroke_w + int(np.ceil(asc))

        mask = Image.new("L", (w, h), 0)
        for li, (glyphs, adv, _) in enumerate(glyph_sets):
            base_y = base0 + int(round(li * line_h))
            if align == "center":
                off = (maxw - adv) / 2
            elif align == "right":
                off = maxw - adv
            else:
                off = 0
            for gid, ox, oy in glyphs:
                self.ft.load_glyph(gid, freetype.FT_LOAD_NO_BITMAP | freetype.FT_LOAD_NO_HINTING)
                ol = self.ft.glyph.outline
                if not ol.points:
                    continue
                dx = padding + stroke_w + off + ox
                dy = base_y - oy
                gmask = Image.new("1", (w, h), 0)
                for poly in self._contours(ol, dx, dy):
                    layer = Image.new("1", (w, h), 0)
                    ImageDraw.Draw(layer).polygon(poly, fill=1)
                    gmask = ImageChops.logical_xor(gmask, layer)
                if gmask.getbbox():
                    mask = ImageChops.lighter(
                        mask, gmask.convert("L").point(lambda v: 255 if v > 0 else 0))

        if stroke_w:
            big = mask.filter(ImageFilter.MaxFilter(stroke_w * 2 + 1))
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            img.paste(Image.new("RGBA", (w, h), stroke + (255,)), (0, 0), big)
            top = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            top.paste(Image.new("RGBA", (w, h), color + (255,)), (0, 0), mask)
            img.alpha_composite(top)
        else:
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            img.paste(Image.new("RGBA", (w, h), color + (255,)), (0, 0), mask)
        if shadow:
            sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            sh.paste(Image.new("RGBA", (w, h), shadow + (255,)), shadow_offset, img.split()[3])
            sh.alpha_composite(img)
            img = sh
        return img

    def _contours(self, ol, dx, dy):
        pts, idx, contours = [], 0, []
        for c in range(ol.n_contours):
            end = ol.contours[c]
            cs = []
            while idx <= end:
                p = ol.points[idx]
                cs.append((p[0] / 64.0 + dx, dy - p[1] / 64.0, bool(ol.tags[idx] & 1)))
                idx += 1
            contours.append(cs)
        return [_flatten(cs, steps=8) for cs in contours if len(cs) > 1]


def _flatten(cs, steps=8):
    n = len(cs)
    if n == 0:
        return []
    start = next((i for i, p in enumerate(cs) if p[2]), None)
    if start is None:
        x0 = (cs[0][0] + cs[-1][0]) / 2
        y0 = (cs[0][1] + cs[-1][1]) / 2
        seq = [(x0, y0, True)] + cs
    else:
        seq = cs[start:] + cs[:start]
    out, cur, ctrl = [], None, None
    closed = seq + [seq[0]]
    i = 1
    while i < len(closed):
        x, y, on = closed[i]
        if on:
            if ctrl is None:
                out.append((x, y))
            else:
                px, py = cur if cur else (x, y)
                for s in range(1, steps + 1):
                    t = s / steps
                    out.append(((1 - t) ** 2 * px + 2 * (1 - t) * t * ctrl[0] + t * t * x,
                                (1 - t) ** 2 * py + 2 * (1 - t) * t * ctrl[1] + t * t * y))
            cur, ctrl = (x, y), None
        else:
            if ctrl is None:
                ctrl = (x, y)
            else:
                mx, my = (ctrl[0] + x) / 2, (ctrl[1] + y) / 2
                px, py = cur if cur else (ctrl[0], ctrl[1])
                for s in range(1, steps + 1):
                    t = s / steps
                    out.append(((1 - t) ** 2 * px + 2 * (1 - t) * t * ctrl[0] + t * t * mx,
                                (1 - t) ** 2 * py + 2 * (1 - t) * t * ctrl[1] + t * t * my))
                cur, ctrl = (mx, my), (x, y)
        i += 1
    return out


@lru_cache(maxsize=None)
def font(path, weight, size):
    return BengaliFont(path, weight=weight, size=size)


def wrap(text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.measure(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    from PIL import ImageFilter  # noqa
    f = font(FONT_SANS, 700, 72)
    img = f.block(["সুনাম রক্ষা করুন,", "প্রাণ দিয়ে।"])
    bg = Image.new("RGBA", (img.width + 40, img.height + 40), (18, 22, 38, 255))
    bg.alpha_composite(img, (20, 20))
    bg.convert("RGB").save("/tmp/t_view.png")
    print(img.size, f.measure("সুনাম রক্ষা করুন, প্রাণ দিয়ে।"))
