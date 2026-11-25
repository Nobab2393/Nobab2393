# Negative blocks — the exact phrasings to append

Pulled from `../../higgsfield-ai-prompt-skill/skills/shared/negative-constraints.md`
(MIT upstream). Use the wording as written: these are tuned, and Kling 3.0 in particular
prefers **positive prevention phrasing** ("all limbs clearly separated") over negations
("no extra limbs") — negations can summon the thing they name.

## How to use

Append only the blocks that match the shot. Three or four lines is normal; the whole file is not.

```
Body / motion  → when people move, fight, dance, or touch
Face / identity→ when a face is visible for more than a moment, or a character recurs
Texture / light→ when the shot is close, low-light, or relies on skin/material realism
Temporal       → when the shot is long, or the character must survive a camera move
Content filter → when the action is violent, medical, or weapon-adjacent
```

---

## Body / motion artifacts

| Artifact | Prevention phrasing |
|---|---|
| floating / extra limbs | "Anatomically correct, all limbs visible and naturally positioned" |
| limb merging (two characters) | keep them at arm's length; "distinct body separation between characters" |
| unnatural proportions | pick **one** body descriptor and keep it consistent |
| jitter / stutter | 1 primary action + ≤2 secondary; split the sequence |
| morphing on fast action | generate in slow motion, retime in post |
| named martial-arts moves failing | describe the *outcome* ("he is knocked back", "general fighting energy"), not the technique |
| grappling reads as embracing | describe body positions, use plain text instead of @ elements |

## Face / identity artifacts

| Artifact | Prevention phrasing |
|---|---|
| face morphing | Soul ID reference; remove contradictory descriptors |
| identity drift across shots | copy-paste the **identical** identity block into every shot |
| character swap in a two-hander | plain text for action shots; hero character named first |
| face warping during camera moves | identity block and motion block kept separate |
| wrong / frozen expression | one emotion per shot + specific micro-expression |
| plastic, waxy skin | Kling 3.0 or Soul Cast; "natural skin texture, subtle imperfections" |

## Texture / lighting artifacts

| Artifact | Prevention phrasing |
|---|---|
| crunchy / over-sharpened detail | "natural optical softness, no digital sharpening" |
| banding in dark gradients | "smooth tonal gradients in shadow" |
| flat store-bought lighting | name the source and the direction: "single practical lamp, screen-left, hard falloff" |
| depth-of-field mush | pick *one* intent — "shallow DOF on the face" or "deep focus across the frame" |

## Temporal / consistency artifacts

| Artifact | Prevention phrasing |
|---|---|
| wardrobe / prop drift | name the prop once in the identity block and never re-describe it |
| background population changing | "the same three bystanders remain in the background" |
| lighting flipping between shots | repeat the light line verbatim in every prompt of the sequence |

## Content filter

| Situation | Do |
|---|---|
| violence | describe outcome and aftermath, not the strike; drop weapon nouns |
| medical / body | describe the *procedure's intent*, keep the frame clinical |
| real public figures | recast as an original character rather than a likeness |

---

## The words you write are the words you summon

Quality-word piles are not neutral: `4k, 8k, ultra-detailed, masterpiece, hyperreal, trending on
artstation` push the image toward the over-processed register that makes everything look
AI-generated. If the frame needs detail, name **what** is detailed ("the grain of the wooden
handle"), not how impressive it is.

Where a negation is still correct: platform-level bans (logos, real brands, real people).
Those belong in the prompt's own constraints, not in the artifact block.
