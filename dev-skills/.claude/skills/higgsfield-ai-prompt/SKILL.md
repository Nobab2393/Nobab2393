---
name: higgsfield-ai-prompt
description: >
  Write, review and lint prompts for Higgsfield AI (Kling, Veo, Wan, Seedance, Minimax Hailuo,
  DoP, Soul, Nano Banana, Seedream, GPT Image, FLUX) using the MCSLA formula, the platform's
  named camera/motion vocabulary, the shared negative blocks and a one-variable-at-a-time
  iteration loop. Use whenever the ask mentions higgsfield.ai, "AI video prompt", shot cards
  for a generation engine, model choice for a shot, or why a generation came out wrong.
  Distilled from OSideMedia/higgsfield-ai-prompt-skill v3.42.0; the full pack is vendored in
  ../higgsfield-ai-prompt-skill/ and is the source of truth for named vocabulary and specs.
user-invocable: true
metadata:
  tags: [higgsfield, prompt, video, image, mcsla, camera, seedance, kling, veo, wan]
  version: 1.0.0
  updated: 2026-11-23
  upstream: https://github.com/OSideMedia/higgsfield-ai-prompt-skill
  upstream_commit: e90ed07753b879bb6be157a7cb12e3043a2cbe6f
  upstream_version: 3.42.0
  license: MIT (upstream), notes MIT
---

# Higgsfield prompt craft — the working cheat sheet

Higgsfield is not one model. It is a **platform that hosts many engines** (Kling 3.0,
Veo 3.1, Wan 2.7, Seedance 2.5/2.0, Minimax Hailuo 2.3, FLUX 3, DoP, plus image models
Soul 2.0 / Nano Banana Pro / Seedream 5.0 / GPT Image 2.x), a library of **named Motion
Presets**, **Soul ID** for character consistency, **Cinema Studio 2.5/3.0/3.5**, and 80+
one-click Apps. Two consequences:

1. **The model is part of the prompt.** "A cinematic shot of X" is a half-specified request;
   the first thing to fix is *which engine*, because each engine has different duration,
   aspect-ratio and audio behaviour.
2. **Named vocabulary beats adjectives.** The platform knows its own preset names
   (`Dolly In`, `360 Orbit`, `Crash Zoom In`, `FPV Drone`, `Snorricam`, `Bullet Time`,
   `Rack Focus`…). Use them verbatim; generic "camera moves dramatically" is a fidelity loss.

> **Before writing anything:** open the vendored pack (`../higgsfield-ai-prompt-skill/SKILL.md`,
> `model-guide.md`, `vocab.md`, `specs/model-specs.yaml`). Model names, enums, durations and
> aspect ratios change every release. Never invent a model version or a preset name — if a name
> is not in the files, say so and ask.

---

## The formula: MCSLA

| M | C | S | L | A |
|---|---|---|---|---|
| **Model** | **Camera** | **Subject** | **Look** | **Action** |

Every video prompt carries all five layers. The reliable *writing* order inside the prompt body
is different from the acronym:

```
Subject (who + what they look like)
→ Action (one primary action, 0–2 secondary)
→ Camera (named control)
→ Look (style, lens, grade, light)
```

- **Short-form regime:** one prompt under ~200 words. If it is longer, the extra words are
  usually describing appearance the model already has, or a second action it cannot do.
- **Block-scaffold regime** (production Seedance briefs) replaces the word cap with structure —
  see `../higgsfield-ai-prompt-skill/skills/higgsfield-seedance/SKILL.md` § Official Prompt
  Architecture. Real briefs there run 218–2,059 words; that is not a rule violation.
- See `reference/prompt-formula.md` for the T2V / I2V / timestamped skeletons.

### The five questions before a prompt

| Question | What to specify |
|---|---|
| Who? | subject + 2–3 appearance facts, not ten |
| Where? | location + time + weather/atmosphere |
| What happens? | **one** primary action |
| Camera? | a named preset, or "static locked-off" |
| Mood? | style + colour grade (+ genre if Cinema Studio) |

---

## Rules that change the output

1. **One primary action per clip.** Two complex actions = jitter, morphing or limb chaos.
   Split the beat into two generations and cut them together in the edit.
2. **Fast motion is generated slow, then sped up.** If a run/punch keeps morphing, render it in
   slow motion and retime in post.
3. **Give the subject something to DO.** Over-described appearance + under-described behaviour is
   the #1 failure. A verb of intention (`he flinches, then reaches for the handle`) beats five
   adjectives.
4. **Never leave a generic emotion.** Decompose it: "sad" → *jaw set, eyes downcast, one slow
   swallow*; "angry" → *nostrils flared, weight forward, shoulders raised*. `higgsfield-prompt`
   § Generic-Emotion Decomposition has the full table.
5. **Separate Identity from Motion.** Identity block = static descriptors only (face, hair,
   clothing, build). Motion block = temporal + camera only. Mixing them is what makes faces warp
   *during camera moves*.
6. **I2V describes only what changes.** Do not re-describe the still you supplied; describe the
   motion and the camera. Over-describing a starting frame confuses the model.
7. **Cinema Studio has a hard 512-character prompt limit** (2.5: @ chips eat ~80–100 hidden
   chars each, so keep visible text under ~250; 3.0: under ~350–400 with references).
8. **Append the shared negative block** from `reference/negative-blocks.md` — and mind the
   phrasing: Kling 3.0 responds better to **positive** prevention phrasing ("all limbs clearly
   separated") than to negations.
9. **Aspect ratio is an enum, not a wish.** Seedance 2.0/2.5 take native 21:9; Kling 3.0 takes
   16:9 / 9:16 / 1:1 only. "2.35:1 anamorphic" belongs in the Look line as *style register*.
10. **Log what happened.** Kept / rejected / filter-flagged, one row per generation. Without a
    denominator you cannot tell a prompt problem from a variance problem.

---

## Model lanes (verify before use)

| Need | First pick | Why |
|---|---|---|
| Cinematic character drama, audio, multi-shot | **Kling 3.0** | realism + character + motion, 3–15 s, native audio |
| Long single take, complex camera grammar | **Seedance 2.5 / 2.0** | 4–30 s, 21:9 native, omni-reference up to 30 images |
| Physics, VFX, fluid, anime motion | **Minimax Hailuo 2.3** | motion + fluid quality, no audio |
| Stylised / artistic, wide style range | **Wan 2.7** | 60 fps, 2–15 s, strong grade control |
| Prompt-adherence + 4K, Google ecosystem | **Veo 3.1 / 3.1 Fast** | reference images, first/last frame, 4/6/8 s |
| Animate one still, camera preset library | **Higgsfield DoP** | I2V specialist, 50+ camera presets, 3–5 s |
| Character consistency across shots | **Soul ID / Soul 2.0** | identity lock, then animate |
| Cheap exploration | `* Fast` variants | half the credit, same family |

Do **not** recommend Sora 2 (retired 2026-09-24) or legacy labels (`Kling 2.1 Master`,
`Seedance Pro (UI label)`) as first picks. Several current models (Kling 3.0 Omni, Wan 2.5,
Kling Image 3.0/Omni) are **UI-only and absent from the API catalog** — say that rather than
pretending they are callable. Full table with durations/ratios: `reference/model-lanes.md`.

---

## Output format

```
**Model**: Kling 3.0   **Aspect**: 9:16   **Duration**: 8s   **Style**: night, cold, cel-look

[prompt body: subject → action → camera → look]

**Camera**: Dolly In (slow, 0.6× subject height)
**Motion preset**: (if used) named preset, verbatim
**Negatives**: [the matching block from reference/negative-blocks.md]
```

Then stop. No meta-commentary unless asked. Two variants only when the *style* actually forks.

---

## When a generation misses

Ask first: **is the miss systematic or stochastic?**

| Symptom | Usually | Fix |
|---|---|---|
| Same artifact every seed | systematic (prompt/model) | change the prompt or the engine |
| Different artifact every seed | stochastic (variance) | re-roll, or batch-and-select |
| Limb chaos / extra fingers | two actions or ambiguous pose | one action, "all limbs visible and naturally positioned" |
| Face warps during camera move | identity mixed with motion | split into identity block + motion block |
| Characters merge | bodies too close | arm's length, "distinct body separation" |
| Motion jitters/stutters | too many actions | one primary action; slow-mo then retime |
| Plastic skin | wrong model / over-smoothing | Kling 3.0 or Soul Cast + "natural skin texture, subtle imperfections" |
| Filter flag | wording, not content | rewrite the action as outcome, drop weapon/violence nouns |

Then **change one variable at a time** and keep the prompt window clean (one prompt per
generation, no "try this instead" stacking). Six-pass diagnostic sequence and batch-and-select
policy: `../higgsfield-ai-prompt-skill/skills/higgsfield-prompt/SKILL.md` § 6-Pass Diagnostic.

---

## How this repo uses it

This sandbox has **no Higgsfield access** (no API key; `mcp.higgsfield.ai` and the Higgsfield
API hosts are not reachable from here), so nothing here can generate on the platform. The skill
is used as a **writing layer**, in two places:

1. **Hand-off prompts.** When the user will paste into the Higgsfield UI, emit a finished MCSLA
   prompt + model + aspect + negatives, ready to paste.
2. **Shot cards for our own renderer.** `pokelike-3d/`, `dark-lesson-3d/` and friends are driven
   by camera + subject + action numbers. The same five layers map onto our shot dict:
   `model→renderer, camera→(eye, target, fov, named move), subject→cast params, look→palette+grade,
   action→eased curves`. Writing the shot in MCSLA first is what keeps those numbers sane — a
   prompt with two primary actions is a scene that will read badly in our renderer too.

Tool: `tools/build_prompt.py` assembles and lints a prompt (word count, 200-word cap warning,
Cinema Studio 512-char budget, missing layers, forbidden legacy model names).

```bash
python3 tools/build_prompt.py --model "Kling 3.0" --ratio 9:16 --dur 8 \
  --subject "a 12-year-old boy in a cream tunic, dark scarf" \
  --action "he lifts a black lantern, its cold flame catching his face" \
  --camera "Dolly In" --look "night, ink-black, one warm candle accent, cel-shaded anime" \
  --neg face
```

---

## Provenance

- Upstream: <https://github.com/OSideMedia/higgsfield-ai-prompt-skill> · MIT · v3.42.0
  (commit `e90ed07`, 2026-11-18), vendored verbatim under
  `dev-skills/.claude/skills/higgsfield-ai-prompt-skill/` minus `.git`, `assets/fonts`,
  `docs/archive`, `evals/`, `tests/` and the dated `models_explore_snapshot_*` JSONs (the spec
  layer itself is kept).
- This file is the distilled working layer, not a copy: it points into the pack for anything
  that must be exact (preset names, model enums, character budgets).
- Upstream licensing/attribution notes: `higgsfield-ai-prompt-skill/LICENSE` and
  `THIRD_PARTY_NOTICES.md`.
