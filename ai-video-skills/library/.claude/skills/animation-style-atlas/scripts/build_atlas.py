#!/usr/bin/env python3
"""
build_atlas.py — extract structured style data from STYLE.md files.

Reads:  --src <dir> (repeatable), each containing styles/*/STYLE.md or skills/*/(SKILL.md)
Writes: atlas.json (one record per style) and a compact report on stdout.

Nothing here invents content: every field is lifted from the source file, trimmed.
"""
import argparse, glob, json, os, re, sys

HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")
TIMING = re.compile(r"(\d+(?:\.\d+)?\s*(?:frames?|fps|s\b|px|%)|ease[- ]?\w+|boil|stagger|overshoot)", re.I)


def first_blockquote(text):
    out, on = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(">"):
            on = True
            out.append(s.lstrip("> ").strip())
        elif on and not s:
            break
        elif on:
            out.append(s)
    return " ".join(out).strip()


def title_of(text, fallback):
    for line in text.splitlines():
        if line.startswith("# "):
            t = line[2:].strip()
            t = re.sub(r"\s+[—-]\s+(Style Prompt|Skill|风格提示词)$", "", t)
            return t
    return fallback


def section(text, *names):
    """Return the body of the first ## section whose heading contains all names."""
    lines = text.splitlines()
    grab, out = False, []
    for i, line in enumerate(lines):
        if line.startswith("## "):
            head = line[3:].lower()
            grab = all(n.lower() in head for n in names)
            continue
        if grab:
            out.append(line)
    return "\n".join(out).strip()


def bullets(body, limit=6):
    out = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("- "):
            out.append(s[2:].strip())
        elif s.startswith("* "):
            out.append(s[2:].strip())
        if len(out) >= limit:
            break
    return out


def not_line(text):
    for line in text.splitlines():
        s = line.strip()
        if s.lower().startswith("not ") or s.lower().startswith("but not"):
            return re.sub(r"\s+", " ", s)[:400]
    return ""


def timing_notes(text, limit=3):
    hits = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith(">") or s.startswith("|"):
            continue
        low = s.lower()
        if "references (grammar only" in low or "never copy" in low or "never name" in low:
            continue
        if len(TIMING.findall(s)) >= 2:
            hits.append(re.sub(r"\s+", " ", s)[:220])
        if len(hits) >= limit:
            break
    return hits


def palettes(text, limit=6):
    seen, out = set(), []
    for h in HEX.findall(text):
        h = h.upper()
        if h not in seen:
            seen.add(h)
            out.append(h)
        if len(out) >= limit:
            break
    return out


def first_paragraph(text):
    """First prose paragraph after the H1, skipping images/links/code fences."""
    out, started = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# ") and not started:
            continue
        if not s or s.startswith("!") or s.startswith("#") or s.startswith("```"):
            if started and not s:
                break
            continue
        if s.startswith("|") or s.startswith("`"):
            continue
        started = True
        out.append(s)
        if s.endswith("."):
            break
    return " ".join(out).strip()


def parse_canvas(path, source):
    """cth9191/animate STYLE.md: H1, prose paragraph, ## Palette, ## Motion habits."""
    text = open(path, encoding="utf-8").read()
    slug = os.path.basename(os.path.dirname(path))
    pal_sec = section(text, "Palette")
    mot = bullets(section(text, "Motion"), 4)
    return {
        "slug": slug,
        "name": title_of(text, slug),
        "name_cn": "", "aka": "",
        "category": "Procedural canvas",
        "source": source,
        "tagline": first_paragraph(text),
        "essence": bullets(section(text, "The medium"), 4),
        "not_this": not_line(text),
        "palette": palettes(pal_sec) or palettes(text),
        "timing": mot or timing_notes(text),
        "uses": [], "demo_film": "",
    }


def parse_lemo(path, root):
    slug = os.path.basename(os.path.dirname(path))
    text = open(path, encoding="utf-8").read()
    meta = {}
    jp = os.path.join(os.path.dirname(path), "style.json")
    if os.path.exists(jp):
        meta = json.load(open(jp, encoding="utf-8"))
    return {
        "slug": slug,
        "name": meta.get("en") or title_of(text, slug),
        "name_cn": meta.get("cn", ""),
        "aka": meta.get("aka", ""),
        "category": meta.get("category_en", ""),
        "source": "lemomo-ai/lemo-opuscar",
        "tagline": first_blockquote(text) or meta.get("line", ""),
        "essence": bullets(section(text, "Essence"), 5),
        "not_this": not_line(text),
        "palette": (palettes(section(text, "Colour") or section(text, "Color"))
                    or palettes(text)),
        "timing": timing_notes(text),
        "uses": meta.get("uses", []),
        "demo_film": meta.get("film", ""),
    }


def parse_generic(path, source, fallback_name=None, category=""):
    text = open(path, encoding="utf-8").read()
    name = title_of(text, fallback_name or os.path.basename(os.path.dirname(path)))
    fm = re.search(r"^---\n(.*?)\n---", text, re.S)
    body = text
    if fm:
        body = text[fm.end():]
    return {
        "slug": os.path.basename(os.path.dirname(path)),
        "name": name,
        "name_cn": "",
        "aka": "",
        "category": category,
        "source": source,
        "tagline": first_blockquote(body) or "",
        "essence": bullets(section(body, "Essence") or section(body, "Overview"), 5),
        "not_this": not_line(body),
        "palette": palettes(body),
        "timing": timing_notes(body),
        "uses": [],
        "demo_film": "",
        "description": (re.search(r"^description:\s*(.+)$", fm.group(1), re.M).group(1).strip()
                        if fm and re.search(r"^description:\s*(.+)$", fm.group(1), re.M) else ""),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", action="append", required=True)
    ap.add_argument("--out", default="atlas.json")
    a = ap.parse_args()

    records = []
    for src in a.src:
        tag = os.path.basename(src.rstrip("/"))
        if os.path.isdir(os.path.join(src, "styles")):
            for path in sorted(glob.glob(os.path.join(src, "styles", "*", "STYLE.md"))):
                if "_template" in path:
                    continue
                records.append(parse_lemo(path, src))
        elif os.path.isdir(os.path.join(src, "plugins")):
            for path in sorted(glob.glob(os.path.join(src, "**", "styles", "*", "STYLE.md"), recursive=True)):
                records.append(parse_canvas(path, "cth9191/animate"))
        elif os.path.isdir(os.path.join(src, "skills")):
            src_label = ("tuzhechen2005/opus-video-skills" if "opus" in tag
                         else "artemnovitckii/claude-animation-skills")
            readme = os.path.join(src, "README.md")
            desc = {}
            if os.path.exists(readme):
                for line in open(readme, encoding="utf-8"):
                    m = re.match(r"\|\s*`/([\w-]+)`\s*\|\s*\*\*(.+?)\*\*\s*(.*?)\|", line)
                    if m:
                        desc[m.group(1)] = (m.group(2) + " " + m.group(3)).strip()
            for path in sorted(glob.glob(os.path.join(src, "skills", "*", "SKILL.md"))):
                rec = parse_generic(path, src_label, category="Code-drawn style skill")
                rec["name"] = rec["slug"]
                if not rec["tagline"]:
                    rec["tagline"] = desc.get(rec["slug"], "")
                records.append(rec)

    json.dump(records, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("styles:", len(records))
    cats = {}
    for r in records:
        cats[r["category"] or "(none)"] = cats.get(r["category"] or "(none)", 0) + 1
    for k, v in sorted(cats.items(), key=lambda kv: -kv[1]):
        print("  %-38s %d" % (k, v))
    missing = [r["slug"] for r in records if not r["tagline"]]
    print("no tagline:", missing)


if __name__ == "__main__":
    main()
