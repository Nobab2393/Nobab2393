# MCSLA in practice — the three prompt shapes

Source of truth: `../../higgsfield-ai-prompt-skill/skills/higgsfield-prompt/SKILL.md`.
This file is the short version I actually write from.

## M · C · S · L · A

| Letter | Element | Filled with | Example |
|---|---|---|---|
| **M** | Model | which engine | Kling 3.0 |
| **C** | Camera | named control, or "static locked-off" | Dolly In, slow |
| **S** | Subject | who + 2–3 appearance facts | a girl in a rust-red coat, shaved head |
| **L** | Look | style + lens + grade + light | night, cold blue, one warm practical |
| **A** | Action | **one** primary action | she lifts the lantern, flame guttering |

## 1. Text-to-video

```
[Subject + appearance].
[Environment — place, time, weather, atmosphere].
[Action — what happens and how].
[Camera — named control].
[Look — style + colour grade].
```

Worked example (kept short on purpose):

```
A lone fisherman in an oilskin coat stands in the bow of a small boat, grey sea behind him.
Dawn fog, first light bleeding through.
He hauls the net hand over hand, shoulders rolling, breath visible.
Camera: slow Dolly In from the stern.
Style: cinematic, desaturated teal and bone white, soft 35 mm grain.
```

## 2. Image-to-video

```
Starting from the provided image as the first frame.
[What moves / changes — nothing that is already visible].
[Camera — named control].
[Style / atmosphere cues].
```

**Rule:** describe only the delta. Re-describing the still is the classic I2V failure: the model
re-interprets what you told it instead of animating what it was given.

```
Starting from the provided image as the first frame.
His shoulders drop as he exhales; the flame in the lantern leans, then steadies.
Camera: subtle Dolly In, 10 % of frame.
Style: keep the grade; nothing else enters frame.
```

## 3. Timestamped (only for multi-beat precision)

Use when the *timing of separate actions* matters — transformations, fight beats, beat-synced
cuts. Otherwise use fluid narrative; timestamps invite the model to morph between beats.

```
0–3s: Wide. The fighter stands alone in the ring, chest heaving.
3–6s: Crash Zoom In on his face. Sweat, jaw clenched.
6–9s: Low Angle. He steps forward, gloves rising.
```

## Layer-by-layer discipline

| Layer | Do | Don't |
|---|---|---|
| Model | name it, verify it exists in `specs/` | invent versions ("Kling 3.5 Pro") |
| Camera | one named move per shot | stack three moves; "camera moves dramatically" |
| Subject | 2–3 stable identity facts | 10 adjectives, contradictory build cues |
| Look | one grade, one lens idea, one light source | "cinematic 8k hyperreal masterpiece" piles |
| Action | one primary + ≤2 secondary | a fight choreography in one clip |

## Two prompt-length budgets

| Regime | Budget | Notes |
|---|---|---|
| Single-shot MCSLA | < 200 words | longer = padding or a hidden second action |
| Cinema Studio 2.5 | < 512 chars total; aim < ~250 visible with 2 @ chips | each chip ≈ 80–100 hidden chars |
| Cinema Studio 3.0 | < 512 chars; aim < ~350–400 with references | references are attachments, cheaper |
| Production Seedance block scaffold | 218–2,059 words by register | structure replaces the cap |

## Identity block vs motion block

This is the single highest-value habit for character work.

```
IDENTITY (copy-paste identical across every shot, no verbs, no camera):
"Woman, late 30s, sharp jaw, black hair cut blunt at the chin, scar through left eyebrow,
grey wool coat over a cream shirt, silver ring on right thumb."

MOTION (this shot only, temporal + camera only):
"She turns her head toward the window as the train lights flicker; Camera: slow Arc, 30°."
```

If a face warps *while the camera moves*, the two blocks have been mixed.
