---
name: stickman-video-director
description: "Distilled playbook for the upstream kaomei/stickman-video-director skill: choose A (Model Engine — prompts for a video model) or B (Code Engine — local manifest runtime), pick one of 16 stickman styles, write prompts that survive generation, and grade the encoded result against the real gates (2.5-second principal-picture progress, semantic captions, three-layer sound, native per-ratio authoring, sample acceptance ≠ user approval)."
---

# Stickman Video Director — distilled

Upstream (installed, verbatim): `dev-skills/.claude/skills/directing-stickman-videos/`
(`SKILL.md`, 83 reference files, the B runtime in `scripts/`, tests). This page is the layer I
actually hold in my head: the routing decision, the prompt formula, the runtime commands and
the gates that decide whether a film is finished.

## 1. Two engines, one skill

| | **A · Model Engine** (模型引擎) | **B · Code Engine** (代码引擎, ex-Autopilot) |
|---|---|---|
| What it makes | moving shots from a video model | a finished MP4: narration, captions, drawn art, micro-motion, SFX | 
| Deliverable | storyboard + standalone prompts (a *complete* stopping point) | the encoded film + subtitle sidecars |
| Needs | a video model (upstream defaults to Google Flow) | image tool, TTS, local renderer (`scripts/autopilot.mjs`) |
| Best for | 30 s – 3 min, reversals, physical acting, TikTok/Shorts | explainers, stories, 5–10 min faceless channels |
| Styles | A1–A8 | B1–B8 |

Never silently cross the modes: an A prompt does not become a B scene, a B style does not own an
A palette.

## 2. Style map

| code | name | one-line identity |
|---|---|---|
| A1 | Classic Black & White | pure white/black canvas, hollow circular head, one accent colour as idea-marker |
| A2 | Modern Pop | red beanie / yellow shirt character, Minimal Tech or Colorful Story |
| A3 | Prehistoric Cave | dark cave comedy |
| A4 | Cozy Storytelling | warm everyday scenes |
| A5 | Historical Cartoon | period stories (Edo Japan etc.) |
| A6 | Amber Noir | reference-guided warm-shadow shots, Gemini Puck narration |
| A7 | Rubber Hose | thin two-tuft hero, 1930s ink-and-paint |
| A8 | Studio Ghibli | hand-painted warmth, text-to-video, last-frame continuity |
| B1 | Minimal Line Art | near-white paper + faint grid, fine irregular pen, handwritten hierarchy |
| B2 | Colorful Hand-Drawn | coloured marker world, softer storytelling |
| B3 | Retro TV | rounded white figures, CRT finish, semantic line-art motion |
| B4 | Survival Thriller | white-glove held illustrations, ≤3 s shots, picture animation mandatory |
| B5 | Avatar Explainer | real presenter + left-stage stick action, 3-line caption block allowed |
| B6 | Dynamic Meme | painted world, puppet binding, portrait-first |
| B7 | Pixel Theater | crisp pixel geometry, single-line captions |
| B8 | Greek Mythology | whole-cel drawing family, local-only renderer, contact-unit poses |

## 3. A-mode: the five-block prompt

Order is fixed: **one-line brief → STYLE → TIMED SEQUENCE → AUDIO → CONSTRAINTS**. Repeat the
entire character description in every standalone prompt (the model has no memory). Beats are
`[0–3s] … [3–7s] … [7–10s]`, each beat *changes the situation* and carries one visible
consequence into the next. Full skeleton: [`reference/a-prompt-formula.md`](reference/a-prompt-formula.md).

Three things the upstream examples prove and novices miss:

1. **One action per beat, one focus per frame.** A chain (push → pressure mark → travel →
   return → new decision) beats six unrelated icons.
2. **The last beat earns its time.** There is always one more graphic change and a visible payoff
   before the hold — a bridge he steps onto, a small steady pulse after a towering zigzag.
3. **CONSTRAINTS is where quality is lost or kept.** Flat 2D, no gradients/3D/duplicate limbs,
   exact allowed screen text, no captions, no logos, "each limb appears only in its current pose".

Continuity between clips is a *stated shared graphic*, not a hope: the red bars twisting down at
the end of clip 2 are the vines at the start of clip 3.

## 4. B-mode: the local runtime

```sh
node scripts/autopilot.mjs doctor                       # toolcheck (node, ffmpeg, ffprobe, canvas, sharp, fonts)
node scripts/autopilot.mjs workflow --style B1 --ratio 9:16   # read-only: documents + references + review templates
node scripts/autopilot.mjs init DIR --style B1 --ratio 9:16   # empty native manifest — not a design
node scripts/autopilot.mjs captions WORDS OUTPUT --lead N     # draft caption grouping (draft ≠ semantic review)
node scripts/autopilot.mjs validate DIR [--seconds N]
node scripts/autopilot.mjs preview DIR [--seconds N]    # candidate + extracted review template
node scripts/autopilot.mjs approve DIR --note TEXT --visual-review REVIEW.json
node scripts/autopilot.mjs render DIR
node scripts/autopilot.mjs accept-visual DIR --review REVIEW.json
```

`project.json` (9:16 init) is deliberately empty: `width 720, height 1280, fps 30`, a
`voice.path`, `captions: []`, `shots: []`, `sfx: []`, and a `reference_review` block with
`capability.mode: "sample_target"`. **Nothing about the story comes from `init`.** Details and
the shot-ledger fields: [`reference/b-runtime.md`](reference/b-runtime.md).

## 5. The gates that actually decide "finished"

- **Principal-picture progress ≤ 2.5 s.** Something meaningful must move or develop; subtitle
  turnover, whole-frame zoom, fades and decorative pulses do **not** reset the clock.
- **First 30 s is a dedicated hook pass** — concrete line, audience-relevant tension, a real
  picture/sound payoff, and the body must deliver the promise.
- **Captions are semantic.** One visible line for B1–B4/B6 (B5 up to three), aligned to the
  actual spoken word, never split to hit a word count. Pocketing a noun phrase is a bug.
- **Sound is three layers**, not an effect every word: voice at native 1×, cue-timed SFX at real
  contacts, and a music bed *by default* (only an explicit user omission removes it).
- **Native per ratio.** 9:16 is authored, not a crop of 16:9; portrait needs its own composition,
  safe areas, caption band and phone-size review.
- **Play the actual encoded file.** A contact sheet cannot certify timing or sound. "Rendered" is
  not "accepted"; "reviewed" is not "approved by the user".
- **Sample acceptance ≠ user approval ≠ tool capability.** Keep the three records apart; a
  limitation is disclosed, never converted into a pass.

Checklist to run before delivery: [`reference/gates.md`](reference/gates.md).

## 6. Local install state (this box)

| thing | state |
|---|---|
| full skill + media | `~/.claude/skills/directing-stickman-videos/` (554 MB, sparse clone at `1028782`) |
| repo copy (text only) | `dev-skills/.claude/skills/directing-stickman-videos/` — see its `PROVENANCE.md` |
| deps | `npm install` done: `sharp`, `@napi-rs/canvas` → doctor reports true |
| ffmpeg | `~/.local/bin/ffmpeg` → imageio_ffmpeg 9.0.2 |
| ffprobe | `~/.local/bin/ffprobe` → `ffprobe-static` 4.0.2 |
| image/TTS provider | **none configured** (`gemini_key_present: false`) — B-mode asset generation blocked, encoding not |
| reference media in repo | not vendored (554 MB) — `MEDIA-NOT-INSTALLED.md` |

## 7. Worked application

`stickman-demo/` in the repo root applies this doctrine to a new Bangla 9:16 short in our
"অন্ধকার পাঠ" brand: director proposal, shot ledger, three A1 clip prompts, plus a B1 manifest
plan — and it states what is not verified because no video model or image tool is available here.
