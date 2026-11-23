#!/usr/bin/env python3
"""
render_atlas.py — turn atlas.json into the readable atlas, the use-case index and the poster.

    python3 render_atlas.py --json atlas.json --outdir ../references --poster ../atlas-poster.png

Everything it writes is derived from the extracted records; nothing is invented.
"""
import argparse, json, os, re
from collections import defaultdict, OrderedDict

from PIL import Image, ImageDraw, ImageFont

CJK = re.compile(r"[\u4e00-\u9fff]")
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def clean(s, limit=None):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = s.replace("`", "")
    if limit and len(s) > limit:
        s = s[: limit - 1].rsplit(" ", 1)[0] + "…"
    return s


def sort_key(r):
    try:
        num = int(re.sub(r"\D", "", str(r.get("num", ""))) or 0)
    except Exception:
        num = 0
    return (num == 0, num, r["name"].lower())


def render_atlas(records, path):
    cats = OrderedDict()
    for r in records:
        cats.setdefault(r["category"] or "Code-drawn styles", []).append(r)
    order = sorted(cats.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    out = ["# The Atlas — 119 animation styles, by category", "",
           "Auto-extracted from four open skill libraries, then grouped. Every line below comes from a",
           "real `STYLE.md` / `SKILL.md`; nothing is paraphrased into generic advice. Palettes are the",
           "hexes that file actually prints (the first few, in order of appearance).", ""]
    for cat, rows in order:
        out.append("## %s — %d styles" % (cat, len(rows)))
        out.append("")
        for r in sorted(rows, key=sort_key):
            name = clean(r["name"])
            cn = (" · " + r["name_cn"]) if r.get("name_cn") else ""
            out.append("### %s%s" % (name, cn))
            tl = r.get("tagline") or r.get("description") or ""
            if tl:
                out.append("> %s" % clean(tl, 480))
            if r.get("palette"):
                out.append("- **Palette:** " + " ".join(r["palette"][:6]))
            for b in (r.get("essence") or [])[:3]:
                out.append("- " + clean(b, 300))
            if r.get("not_this"):
                out.append("- **Not:** " + clean(r["not_this"], 300))
            if r.get("timing"):
                t0 = clean(r["timing"][0], 260)
                label = "Motion" if re.search(r"frame|fps|ease|boil|stagger|overshoot|\d\s*s\b", t0, re.I) else "Tech"
                out.append("- **%s:** %s" % (label, t0))
            if r.get("uses"):
                out.append("- **Use for:** " + ", ".join(r["uses"][:4]))
            out.append("- **Source:** `%s` → `%s`" % (r["source"], r["slug"]))
            out.append("")
    open(path, "w", encoding="utf-8").write("\n".join(out))
    return len(out)


def render_use_cases(records, path):
    by = defaultdict(list)
    for r in records:
        for u in r.get("uses") or []:
            by[u.strip()].append(r)
    out = ["# Quick pick — what are you making?", "",
           "The `use for` tags the style files themselves declare, inverted. Start here, not at the atlas.",
           ""]
    for use, rows in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(rows) < 2:
            continue
        out.append("## %s" % use)
        out.append("")
        out.append(" · ".join("**%s**" % clean(r["name"]) for r in rows[:14]))
        out.append("")
    open(path, "w", encoding="utf-8").write("\n".join(out))
    return len(by)


def render_poster(records, path):
    cards_col = 10
    rows = (len(records) + cards_col - 1) // cards_col
    CW, CH, PAD = 158, 96, 10
    W = cards_col * (CW + PAD) + PAD
    H = rows * (CH + PAD) + PAD + 54
    im = Image.new("RGB", (W, H), (240, 238, 230))
    d = ImageDraw.Draw(im)
    f_title = ImageFont.truetype(FB, 26)
    f_name = ImageFont.truetype(FR, 11)
    d.text((PAD + 4, 16), "119 ANIMATION STYLES — palette card index", font=f_title, fill=(25, 25, 25))
    for i, r in enumerate(sorted(records, key=sort_key)):
        cx = PAD + (i % cards_col) * (CW + PAD)
        cy = 54 + PAD + (i // cards_col) * (CH + PAD)
        pal = r["palette"][:5] or ["#EDEBE4"]
        sw = CW // len(pal)
        for j, hexv in enumerate(pal):
            try:
                col = tuple(int(hexv[k:k + 2], 16) for k in (1, 3, 5))
            except Exception:
                col = (237, 235, 228)
            d.rectangle([cx + j * sw, cy, cx + (j + 1) * sw - 1, cy + 52], fill=col)
        d.rectangle([cx, cy, cx + CW - 1, cy + CH - 1], outline=(200, 196, 186))
        nm = clean(r["name"])
        nm = nm if len(nm) <= 24 else nm[:23] + "…"
        d.text((cx + 4, cy + 58), nm, font=f_name, fill=(25, 25, 25))
        cat = clean(r["category"])[:26]
        d.text((cx + 4, cy + 74), cat, font=f_name, fill=(120, 116, 108))
    im.save(path)
    return im.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="atlas.json")
    ap.add_argument("--outdir", default="../references")
    ap.add_argument("--poster", default="")
    a = ap.parse_args()
    records = json.load(open(a.json, encoding="utf-8"))
    os.makedirs(a.outdir, exist_ok=True)
    n = render_atlas(records, os.path.join(a.outdir, "atlas.md"))
    u = render_use_cases(records, os.path.join(a.outdir, "by-use-case.md"))
    print("atlas.md lines:", n, "| use-case groups:", u)
    if a.poster:
        print("poster:", render_poster(records, a.poster))


if __name__ == "__main__":
    main()
