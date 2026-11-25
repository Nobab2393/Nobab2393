# অন্ধকার পাঠ ০৩ · দুপুর — *Dark Lesson 03: Noon*

Third episode of the *অন্ধকার পাঠ* series, and the first one made in **daylight**.
Vertical 1080×1920, 24 fps, Bangla voice-over, Bangla on-screen text, 56 s.

**Deliverable:** `dark-lesson-03-1080x1920.mp4`

> দুপুরের রোদে মাঠের মাঝখানে একটা ছেলের ব্যাগ মাটিতে পড়ে গেল।
> দশজনে দেখল, কেউ এগোল না — কারণ আলো এত তীক্ষ্ণ ছিল যে ছায়াটা কারও চোখে পড়ল না।

**Lesson:** অন্ধকার আলোর অভাব নয়। অন্ধকার ওখানে, যেখানে সবাই দেখেও দেখতে পায় না।

---

## The one visual idea

Every bystander casts a **separate** shadow. Nobody's shadow touches anybody else's — that
is the whole thesis of the film, and it is stated in a single frame in scene 3. When Mira
finally kneels down and hands Ayan one book, the two shadows run into each other and become
one shape. Geometry replaces dialogue: the film never says "একসাথে" — you watch the shadows
do it.

The CTA card breaks the series' habit of ending on black: episode 03 ends on a bright paper
card with the sun still up.

## Structure (7 beats)

| # | scene | on-screen text |
|---|---|---|
| 1 | noon field, after school | দুপুরের রোদে সব পরিষ্কার |
| 2 | the bag hits the ground | ব্যাগটা মাটিতে পড়ল |
| 3 | the ring of bystanders, shadows apart | সবাই দেখছিল, কেউ এগোল না |
| 4 | alone, picking the books up | সে কিছু বলল না |
| 5 | one girl walks out of the ring | একজন এগিয়ে এল |
| 6 | emptying field, long light | অন্ধকার দেখার অভাব, আলোর নয় |
| 7 | bright CTA card | তুমি দেখেছিলে — / তারপর কী করলে? |

Full timeline, exact on-screen strings and the verbatim CTA: `01-script.md`.

---

## Designing daylight instead of sliding a brightness slider

The point of the exercise was to take the series' night grammar (one warm key, deep
falloff, ink-black background) and rebuild it as a **value structure** rather than a
washed-out version of the night film. The rules came from `../design-lab/`.

**Contrast ladder, checked in the render, not asserted:**

| plane | luminance | how it is made |
|---|---|---|
| sky (BG) | ~8 % value | 3-stop gradient `SKY_TOP → SKY_MID → SKY_BOT`, nothing drawn on it but the sun tile and the horizon haze |
| far ridge / treeline (MG) | 18–20 % | one continuous crown band on the horizon + fence line, deliberately low contrast, almost no edges |
| field floor (MG) | 30–35 % | 3-stop ground gradient (`G_FAR → G_MID → G_NEAR`) with world-space tufts and rocks |
| characters | 45–95 % | the only thing in frame allowed to reach paper-white (Ayan's shirt) |
| near plane (FG) | 70 % | out-of-focus grass at the bottom corners only, `blur 9` |

So the character is always the highest-contrast object in frame, the background is always
below it, and distance is carried by *simplification* (fewer edges, less saturation) rather
than by fog alone. `bg3.grade()` does one warm tint (`255,248,234`) at the very end, ~4 %
saturation — the daylight is designed in the palette, not in the grade.

**One light direction, obeyed everywhere.** `SUN_DIR = (0.46, 0.80, 0.38)` for the key and
`SHADOW_DIR = (-0.86, -0.51)` for every ground shadow. Every cast shadow is a *projected
ground polygon* (`bg3.cast_shadow` with a `slope` term), not a decal pasted under the feet —
so shadows lengthen correctly as the sun drops in scene 6, and so two shadows can genuinely
merge in scene 5.

**Composition.** The action never crosses the caption band (`y 1620`) or the near plane;
heads sit at the horizon line in the medium shots. Camera heights are all below eye level of
a standing adult (1.22–1.86 m) so the field reads as a field and not as a table top.

## What the character rig had to survive

The episode needed three characters at very different heights (Ayan 1.44 m, Rafiq 1.66 m,
Mira 1.32 m) who can walk, crouch, kneel, reach and hand something over, from a single
`_person()` rig in `cast3.py` (dial-driven: `walk, arm, reach, look, head, slump, crouch,
blink, brow, laugh`).

The hard part was the legs. A crouch dial that only shortens the torso leaves the feet
locked where they were and the character floats; rotating the shin without carrying the
thigh angle drops the ankle through the ground. The rig now solves the leg as FK: the hip
angle is `A = 54°·crouch + 15°·|walk|`, the knee bend `Bk` is solved so the ankle stays on
`y = 0`, and the shin and foot subtrees are rotated in the thigh's frame (`A + Bk`), not in
the world frame. That single fix is why the kneel in scene 5 holds up next to a standing
character.

## Files

| file | what it is |
|---|---|
| `01-script.md` | timeline, exact Bangla strings, beats, verbatim CTA |
| `bg3.py` | daylight background: sky, ridge, treeline, ground, projected shadows, near plane, dust/heat, grade |
| `cast3.py` | one parametric rig → Ayan / Rafiq / Mira / crowd / book / bag |
| `film.py` | 7 scenes, captions, camera moves, audio mix, segments, join |
| `cel3d.py` | painter-sorted 3D→2D cel renderer (capsules, balls, boxes, toon ramp) |
| `deva.py` | Bangla text shaping/rendering for PIL |
| `test-cast.py` | character bench → `frames/cast-test.png` |
| `audio/v1..v7.mp3` | trimmed, loudness-matched voice-over (48.00 s total) |

## Rebuilding

```bash
python3 test-cast.py            # character bench
python3 film.py --still 24.0    # one frame → frames/still-24.00.png
python3 film.py --mix           # audio/mix.wav
python3 film.py --seg 0 673 segA.mp4
python3 film.py --seg 673 1346 segB.mp4
python3 film.py --join segA.mp4 segB.mp4
```

Roughly 1.2 s/frame single-process on this 2-core box; the full 1346 frames were rendered as
two parallel halves (~3 s/frame each under contention, ~30 min wall clock).

Output: **1080×1920, 24 fps, H.264 (yuv420p) + AAC 44.1 kHz stereo, 56.10 s, 8.9 MB.**

## Honest notes

- The audio was checked by ear and by waveform only — there is no speech recogniser in this
  environment, so the voice-over has not been transcribed back to text for verification.
- The crowd in scene 3 is six instanced `_person` rigs with per-instance yaw, not six
  characters; at that distance it reads as a ring, but it is deliberately low-detail.
- Scene 6's walk-away turns the rigs 180° and walks them *in place* while they slide down
  the z-axis. It sells the exit — they get smaller, the two shadows stay merged — but the
  feet are not planted on a real path; there is no walk cycle sync to ground distance.
- Scene 2's throw is a 0.45 s bag flight with a single rotation key; at 24 fps it is eight
  frames and it reads as a drop, not as a throw with a hand releasing it.
- The daylight is a designed ramp, but it is still a stylised, flat cel look: this is not
  physically-based lighting, and the toon ramp was brightened for day rather than replaced
  with a new shading model.
- No bloom/lens effects were added to the sun; it is one radial gradient tile, because
  stacked translucent circles read as a second moon.
