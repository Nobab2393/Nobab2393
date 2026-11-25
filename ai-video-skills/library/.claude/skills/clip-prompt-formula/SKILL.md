---
name: clip-prompt-formula
description: Write AI video clip prompts that stay consistent across a whole film — eight fixed questions per clip, locked style/character/world blocks pasted verbatim, one action per shot, camera language instead of adjectives, and a hard split between what the generator makes and what the edit adds (all text, prices, titles, narration). Use for "write prompts for my story", "keep the character consistent across clips", "shot list for a 2-minute AI film", "prompt template for Veo/Sora/Kling/Seedance", or when generated clips keep drifting in face, props or style.
---

# Clip Prompt Formula

Consistency is not a model setting. It is a **specification** problem: if two prompts describe the
rabbit in two different word-orders, two different rabbits come back. The fix is boring and it
works — lock every repeated string, change one field at a time, and never ask the generator for
anything the edit can do better.

## The eight questions, in this order

Every prompt answers the same eight questions in the same sequence. The order is the discipline:
subject before action, style before camera, audio before constraints.

| # | Question | What goes in it |
|---|---|---|
| 1 | **Subject** | who/what, with the locked character block, word for word |
| 2 | **Action** | exactly one beat, present tense, one verb |
| 3 | **Setting** | place + time of day, from the locked world block |
| 4 | **Style** | the locked style line, word for word |
| 5 | **Camera** | shot size, angle, movement — one move only |
| 6 | **Lighting and colour** | source and direction of light, palette, mood |
| 7 | **Audio** | ambience, music mood, at most one short line (usually none) |
| 8 | **Constraints** | what must not appear, specific to this shot |

## Locked blocks

Write them once, paste them into every prompt unchanged. Changing wording — not the model — is
the number one cause of a character changing between clips.

**Character block**
- 12–24 words: nouns, colours, and **one quirk you can draw** ("one missing tail feather", "a
  plaster on the left ear"). The quirk is also your continuity check.
- Species → size relative to the world → clothing → prop → distinguishing mark. Same order every time.
- No moods ("sad", "kind"), no age numbers, no backstory. A model cannot render a backstory.
- Never describe a character differently for a close-up. Same block for a silhouette and a 4 m face.

**Style line**
- Medium + palette + light + one technical term, under ~30 words. Longer ones average into mush.
- *"Stylized 3D storybook animation, muted autumn palette, soft golden-hour light, matte low-poly
  volumes, shallow depth of field, slow camera moves."*
- "Beautiful", "epic", "cinematic" are not style. They are wishes.

**World block** — one string for the location, pasted into every shot that shows it.

## One action per clip

A 5–10 s clip holds **one beat**. "Walks in, sees the sign, gets sad, runs" renders as four
half-finished actions. Split it into four shots and cut them together — cutting is free,
regeneration is not.

Do the arithmetic before writing: **shots = runtime ÷ clip length**.

| Runtime | at 4–6 s | at 6–8 s |
|---|---|---|
| 15 s | 3–4 clips | 2–3 clips |
| 30 s | 5–7 | 4–5 |
| 60 s | 10–14 | 8–10 |
| 2 min | 20–27 | 16–20 |

Sweet spot is **4–6 s**; past ~8 s faces soften and held props start to melt. Ask for 1 s of
handle at each end and cut the handles off — the first and last frames are the worst.

## Camera words, not feelings

| Instead of | Write |
|---|---|
| "make it dramatic" | "slow push-in from medium to close-up" |
| "epic reveal" | "static wide, subject enters frame left" |
| "dynamic camera" | "slow tracking right, subject centred" |
| "emotional" | "hold on the face, no camera movement" |

One move per clip. Fast or compound moves (orbit + push + tilt) are exactly where geometry warps
and limbs swap. A move plus a reveal is two shots.

Vocabulary worth keeping: *wide / medium / close-up / two-shot*, *eye level / low angle / high
angle*, *static / slow push-in / pull-back / pan / tracking / tilt*, *shallow depth of field*.

## Never ask for text, and rarely for speech

Generators garble lettering and mangle names, and one garbled price tag poisons an otherwise
perfect clip. Everything legible is **post work**:

| The generator makes | The edit adds |
|---|---|
| blank paper, blank tags, blank signs | the words, numbers, prices |
| mouths closed, no dialogue | narration, the one spoken line |
| generic shapes | logos, titles, end cards, moral text |
| ambience, wind, footsteps, paper | music, mix, ducking under voice |

Describe the object as *blank* and say so in the constraints — `"a blank cream paper tag, no
letters, no numbers"` — then track the real text on in the edit, where it stays crisp and can be
fixed without regenerating a frame.

## Say what to avoid — per shot

A generic "no text, no extra characters" gets ignored. Three to five items chosen for the failure
you actually expect:

- sign shot: `no letters, no numbers, no readable text — the sign stays blank`
- crowd shot: `no background animals in focus, no second owl`
- close-up: `no teeth, no cartoon sparkle, no expression change beyond the ears`
- always: `no style change, no camera shake, no morphing`

## Continuity chain

1. **Stills first.** Generate each character once on a neutral ground in the locked style. Lock
   the ones you like. Every clip is image-to-video from that still, not text-to-video.
2. **Chain adjacent shots.** Where two shots share a set-up, feed the last frame of clip N as the
   first frame of N+1 (same doorway, same two-shot). List those pairs before generating.
3. **Same seed family** for the whole film if the tool exposes seeds.
4. **Reject on sight** any clip with warped props, readable lettering, or a drifting face. A
   beautiful clip of the wrong rabbit costs more than the clip is worth.

## The template

```
[STYLE LINE — identical in every clip]
[CHARACTER BLOCK(S) — identical in every clip]
[WORLD BLOCK — only if the location is in frame]

Shot: [wide / medium / close-up], [eye level / low angle / high angle]
Action: [one beat, present tense, one verb]
Setting: [place, time of day]
Camera movement: [static / slow push-in / pan / tracking / tilt]
Lighting: [source, direction, colour, mood]
Audio: [ambience, music mood, at most one short line]
Duration: [4-8 seconds]
Avoid: [3-5 items specific to this shot]
```

## Worked example

```
Stylized 3D storybook animation, muted autumn palette, soft golden-hour light, matte low-poly volumes, shallow depth of field, slow camera moves.
Olive: old barn owl, round wire glasses, worn grey scarf, speckled cream-and-brown feathers, one missing tail feather.
Bruno: young brown rabbit, cream belly, small green backpack, red coin purse, long upright ears.

Shot: close-up, eye level
Action: Olive slowly tilts her head to one side and blinks once
Setting: shop doorway in a small animal town, late afternoon
Camera movement: slow push-in on her eyes
Lighting: warm low sun from the left, soft shadows, backlit rim on the scarf
Audio: faint wind, quiet paper rustle, no music
Duration: 5 seconds
Avoid: no text, no wing flap, no second owl, no style change
```

Note what is *not* there: no price, no dialogue, no "she looks knowing". The knowing is the tilt
and the blink.

## Failure modes

| Symptom | Cause | Fix (change one field) |
|---|---|---|
| Character drifts between clips | block reworded | paste the identical block, diff the strings |
| Everything mushy, no style | style line too long or too vague | cut to ≤30 words, add one technical term |
| Clip does a bit of everything | two or three actions | split into shots |
| Subject warps, limbs swap | compound or fast move | one slow move, or static |
| Lettering garbled | text asked of the generator | blank prop + overlay in the edit |
| Face softens, prop melts | clip too long | 4–6 s, cut the handles |
| Extra characters appear | constraints too generic | name what must not appear, per shot |
| Continuity breaks at a cut | no chain | last frame → first frame on shared set-ups |

**Debug rule:** when a shot comes back wrong, change exactly one field, regenerate, compare.
Changing the action and the camera together tells you nothing about which one broke it.

## Review checklist

- [ ] style line and character blocks byte-identical to the locked versions
- [ ] one verb in Action
- [ ] one camera move, and it is slow
- [ ] no text, no speech asked for
- [ ] 3–5 avoid items, specific to the shot
- [ ] 4–6 s including handles
- [ ] a still exists for every character in frame
- [ ] chained pairs identified before generating

## Sibling skills

- `film-breakdown`, `shot-prompt`, `asset-passport` — the heavier studio version: shot cards and asset passports when the project needs a registry.
- `seedance-*`, `flux-3-*` — style and API-specific prompt packs; keep this block order, swap their style line in.
- `add-voiceover`, `add-captions`, `add-music` — the post side of the split above.
- `3d-animation`, `2d-2point5d-animation` — when the answer is "don't generate it, render it".

## Honest limits

- This is a **specification** discipline. It raises the hit rate; it does not rescue a model that
  cannot hold a prop. Budget roughly one usable clip in three.
- Locked blocks do nothing if the tool drifts on seeds. Verify continuity on one pair of clips
  before committing to a 24-shot film.
- The formula gives you footage that cuts together. It does not give you timing, pace or a
  performance — the cut and the sound are still yours.
