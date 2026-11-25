#!/usr/bin/env python3
"""Assemble and lint a Higgsfield prompt (MCSLA).

    python3 build_prompt.py --model "Kling 3.0" --ratio 9:16 --dur 8 \
        --subject "a 12-year-old boy in a cream tunic, dark scarf" \
        --action "he lifts a black lantern, its cold flame catching his face" \
        --camera "Dolly In" --look "night, ink black, one warm candle accent, cel-shaded anime" \
        --neg face,body

Checks it runs before printing:
  * all five MCSLA layers present (Model, Camera, Subject, Look, Action)
  * single-shot word cap (~200) and Cinema Studio character cap (512)
  * retired / legacy model names that must not be used as a first pick
  * camera name is one of the platform's named moves (or explicitly free-form)

The point is not to be clever — it is to stop a prompt leaving the house with a layer missing
or a model that no longer exists.
"""
import argparse
import json
import sys

NAMED_CAMERAS = {
    "dolly in", "dolly out", "dolly left", "dolly right", "dolly zoom in", "dolly zoom out",
    "super dolly in", "super dolly out", "truck", "crane up", "crane down", "crane over the head",
    "levitation", "tilt up", "tilt down", "360 orbit", "orbit", "arc", "lazy susan", "robo arm",
    "crash zoom in", "crash zoom out", "rack focus", "action run", "fpv drone", "handheld",
    "head tracking", "snorricam", "bullet time", "dutch angle", "fisheye", "whip pan",
    "overhead", "flying", "low angle", "high angle", "eye level", "bird's-eye view",
    "static", "locked-off", "static locked-off",
}

RETIRED = {
    "sora 2": "retired 2026-09-24 — use Seedance 2.0 or Minimax Hailuo 2.3",
    "kling 2.1 master": "removed from the platform — use Kling 2.6 or 3.0",
    "kling 2.5 turbo": "not in the API catalog",
    "wan 2.5": "not in the API catalog",
    "seedance pro": "legacy UI label only",
    "kling o1": "legacy, not in the API catalog",
}

UI_ONLY = {
    "kling 3.0 omni", "kling 3.0 omni edit", "kling image 3.0", "kling image omni",
    "higgsfield dop", "soul cinema preview",
}

NEG = {
    "body": ("Body/motion: anatomically correct, all limbs visible and naturally positioned; "
             "distinct body separation between characters; one continuous action."),
    "face": ("Face/identity: consistent facial structure across the shot; the same character "
             "throughout; natural skin texture, subtle imperfections."),
    "texture": ("Texture/light: natural optical softness, no digital sharpening; smooth tonal "
                "gradients in shadow; one clear light source with a named direction."),
    "temporal": ("Temporal: wardrobe, props and background population stay identical for the "
                 "whole shot; the named light never changes direction."),
    "filter": ("Content: outcome and aftermath implied rather than shown; no weapon emphasis, "
               "no real brand, no real person."),
}


def build(a):
    body_parts = []
    if a.subject:
        body_parts.append(a.subject.strip().rstrip(".") + ".")
    if a.env:
        body_parts.append(a.env.strip().rstrip(".") + ".")
    if a.action:
        body_parts.append(a.action.strip().rstrip(".") + ".")
    if a.camera:
        body_parts.append("Camera: %s." % a.camera.strip().rstrip("."))
    if a.look:
        body_parts.append("Style: %s." % a.look.strip().rstrip("."))
    body = " ".join(body_parts)
    if body:
        body = body[0].upper() + body[1:]

    lines = []
    if not a.body_only:
        head = "**Model**: %s" % (a.model or "(pick one)")
        if a.ratio:
            head += "   **Aspect**: %s" % a.ratio
        if a.dur:
            head += "   **Duration**: %ss" % a.dur
        if a.style_tag:
            head += "   **Style**: %s" % a.style_tag
        lines += [head, "", body, ""]
        if a.camera:
            lines.append("**Camera**: %s" % a.camera)
        if a.preset:
            lines.append("**Motion preset**: %s" % a.preset)
        negs = [n.strip().lower() for n in (a.neg or "").split(",") if n.strip()]
        if negs:
            lines.append("**Negatives**:")
            for n in negs:
                if n in NEG:
                    lines.append("- " + NEG[n])
                else:
                    print("  ! unknown negative block %r (have: %s)" % (n, ", ".join(NEG)),
                          file=sys.stderr)
    else:
        lines += [body]

    text = "\n".join(lines).strip()

    warn = []
    words = len(body.split())
    if words > 200:
        warn.append("body is %d words (>200 short-form cap) — cut adjectives or a second action"
                    % words)
    if a.studio:
        chars = len(text)
        if chars > 512:
            warn.append("Cinema Studio hard cap is 512 chars; this is %d" % chars)
        elif chars > 400:
            warn.append("Cinema Studio: %d chars — trim to leave room for @ element chips" % chars)
    for layer, val in (("Model", a.model), ("Camera", a.camera), ("Subject", a.subject),
                       ("Look", a.look), ("Action", a.action)):
        if not val and not a.body_only:
            warn.append("MCSLA layer missing: %s" % layer)

    if a.camera and not a.body_only:
        core = a.camera.lower().split("—")[0].split(",")[0].strip()
        if not any(core.startswith(c) or c.startswith(core) for c in NAMED_CAMERAS):
            warn.append("camera %r is not a named platform move — either use one of the "
                        "vocabulary names or describe it physically (arc 30°, 35mm)" % a.camera)

    if a.model:
        m = a.model.lower()
        for k, why in RETIRED.items():
            if k in m:
                warn.append("model %r: %s" % (a.model, why))
        for k in UI_ONLY:
            if k in m:
                warn.append("model %r is UI-only / unverified in the API catalog — say so before "
                            "promising a call" % a.model)

    return text, words, warn


def main():
    p = argparse.ArgumentParser(description="Build + lint a Higgsfield MCSLA prompt")
    p.add_argument("--model")
    p.add_argument("--ratio")
    p.add_argument("--dur")
    p.add_argument("--style-tag", default="")
    p.add_argument("--camera")
    p.add_argument("--preset", help="named motion preset, verbatim")
    p.add_argument("--subject")
    p.add_argument("--env", help="environment / atmosphere line")
    p.add_argument("--action")
    p.add_argument("--look")
    p.add_argument("--neg", default="", help="comma list: body,face,texture,temporal,filter")
    p.add_argument("--studio", action="store_true", help="enforce Cinema Studio 512-char cap")
    p.add_argument("--body-only", action="store_true", help="print just the prompt text")
    p.add_argument("--json", action="store_true", help="emit a shot card instead of prose")
    a = p.parse_args()

    text, words, warn = build(a)
    if a.json:
        card = {
            "model": a.model, "aspect": a.ratio, "duration": a.dur,
            "camera": a.camera, "motion_preset": a.preset,
            "subject": a.subject, "environment": a.env, "action": a.action, "look": a.look,
            "negatives": [n.strip() for n in a.neg.split(",") if n.strip()],
            "prompt": text, "words": words, "warnings": warn,
        }
        print(json.dumps(card, ensure_ascii=False, indent=1))
        return 0

    print(text)
    print()
    print("— %d words, %d chars" % (words, len(text)))
    for w in warn:
        print("! " + w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
