# Law 5 · সুনাম — MiniMax H3 prompt pack

Two prompts written to the `h3-prompt-writing` contract, for the same concept as
`output/law5_bangla_2d_animation.mp4`. Bengali is preserved verbatim inside `<d>`; every
instruction, style and sound sentence is English, as the guide requires.

- **A · T2VA** — no reference images. One 15 s clip (H3's per-generation ceiling).
- **B · Ref2VA** — reuses the character art already in `images/`, which is how you keep the
  cast consistent across the 54 s story. Split into four 15 s generations, stitched.

H3 limits: 4–15 s per generation · 24 fps · 768 px short side (2K via Regenerate-2K API) ·
≤ 9 images, ≤ 3 video clips, ≤ 3 audio clips, ≤ 12 files in Ref2VA.

---

## A · T2VA — single 15 s explainer beat

```text
integrated_multimodal_description: [Shot 1] 2D-animated, cinematic, flat vector illustration with hand-lettered Bengali typography, a medium-wide shot frames a deep crimson palace hall with tall arches and warm rim light. The king — middle-aged, heavy crown, short grey beard, long crimson coat with a gold belt — strides in from frame-left and stops at the centre third, then plants his feet and lifts his right arm toward a floating gold panel. The camera pushes in with small amplitude at slow speed as the panel resolves into Bengali lettering. A deep mature male narrator (S1) says in an off-screen voiceover: <d>[Bengali] সুনামই শক্তির সবচেয়ে বড় উৎস।</d> while every on-screen character's lips remain completely closed. [Shot 2] At 00:06.000, the shot cuts to a low-angle medium close-up of the king from below. He closes his raised hand into a fist against his chest, the crown catching a hard gold highlight, while the same narrator (S1) continues in an off-screen voiceover: <d>[Bengali] একজন রাজার আসল শক্তি তলোয়ারে নয়, প্রজাদের মনে তাঁর নামের ওজনে।</d> and the king's lips stay completely closed. The camera tilts up with small amplitude at slow speed toward a gold rule of light opening across the back wall.

overall_soundscape: A long stone hall carries a wide, quiet room tone with a faint high shimmer as the gold panel appears. Measured boot steps land on polished stone, then stop, and fabric shifts once as the king plants his stance.

non_diegetic_music: Sustained low strings at a slow tempo with a single struck bronze tone on each cut, gradually increasing in volume and cutting off on the final frame.
```

## B · Ref2VA — four connected 15 s generations

Shared reference bank (one line each, reuse verbatim across all four prompts):

```text
subject_definitions:
<Subject 1> is the king in <Picture 1> and <Picture 2>, with a red-and-gold crown, short grey beard, long crimson coat with a gold belt, and a 2D flat-vector illustration style.
<Subject 2> is the rival courtier in <Picture 3>, thin, dark moustache, slate-grey coat, walking with a stiff forward lean.
<Subject 3> is the businessman in <Picture 4>, blue suit, white shirt, dark tie, stocky build, hand inside his jacket.
<Subject 4> is the student in <Picture 5>, white tee, backpack, blue jeans, visible blue folder.
<Subject 5> is the mentor in <Picture 6>, grey bun, round glasses, green saree with a gold border.
<Subject 6> is the 2D flat-vector background style of all pictures, with hard shadows, warm rim light and no photographic texture.
```

### B1 · 00:00–00:15 — patronage / the palace

```text
summary:
[reference generation] The target video opens the Law 5 story: <Subject 2> crosses <Subject 6>'s palace hall to confront <Subject 1>, who answers without drawing a weapon.

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2]): fully_preserved - crown, grey beard, crimson coat and gold belt retained.
<Subject 2> (appears in [Shot 1], [Shot 2]): fully_preserved - grey coat, moustache and stiff forward lean retained.
<Subject 6> (appears in [Shot 1], [Shot 2]): fully_preserved - flat vector shading, hard shadows and warm rim light retained.

detailed_description:
The target video is a 2D-animated flat-vector illustration in the style of <Subject 6>, with hand-lettered Bengali text and a muted crimson-and-gold palace palette.
[Shot 1] A wide shot establishes a deep palace hall of tall arches and slow dust in the light beams. <Subject 1>, the crowned king, stands at the centre third facing frame-left, one hand resting on his gold belt. <Subject 2>, the thin courtier, walks in from frame-left with a stiff forward lean and stops two paces away, chin raised. The camera trucks right with small amplitude at slow speed, keeping both men in frame as the courtier's shadow stretches across the stone. The courtier glances at the king's empty scabbard, then at his face.
[Shot 2] At 00:07.500, the shot cuts to a medium close-up of <Subject 1> from a low angle. The king does not reach for a weapon; he lifts his open palm, and the wall behind him resolves into a gold Bengali inscription. The camera pushes in with small amplitude at slow speed as <Subject 2> steps back into the lower-left corner, deflating, and lowers his chin. The king's expression settles from assessment into calm authority, and the inscription holds through the final frame.

overall_soundscape: A wide stone hall tone with a faint metallic shimmer above it. Measured footsteps approach on polished stone, stop, and a single long fabric shift follows as the courtier's stance collapses.

non_diegetic_music: Low sustained strings at a slow tempo, a struck bronze tone under the second cut, and a soft rise that ends unresolved on the last frame.
```

### B2 · 00:00–00:15 — reputation as armour, the street

```text
summary:
[reference generation] Middle act: <Subject 3> walks a night street where <Subject 4> and <Subject 5> cross behind him as his reputation, not his authority, does the work.

retention_analysis:
<Subject 3> (appears in [Shot 1], [Shot 2]): fully_preserved - blue suit, dark tie, stocky build and open-jacket gesture retained.
<Subject 4> (appears in [Shot 1]): fully_preserved - white tee, backpack and blue folder retained.
<Subject 5> (appears in [Shot 1]): fully_preserved - grey bun, round glasses and green saree retained.
<Subject 6> (appears in [Shot 1], [Shot 2]): fully_preserved - flat vector night palette with hard shadows retained.

detailed_description:
The target video is a 2D-animated flat-vector illustration in the style of <Subject 6>, night city with violet sky and warm window grids.
[Shot 1] A wide tracking shot follows <Subject 3>, the businessman, walking right-to-left along a wet street of stacked buildings. The camera tracks with large amplitude at fast speed, then slows and settles as he stops at the centre third and adjusts his jacket with both hands. Behind him, semi-transparent figures cross the frame in the opposite direction: <Subject 4> with the blue folder, then <Subject 5> in the green saree, neither looking at him.
[Shot 2] At 00:08.000, the shot cuts to a medium shot from the front. <Subject 3> opens his jacket slightly, then closes it, and the street lamps behind him bloom one by one into a soft halo around his silhouette. The camera holds a static shot with small handheld shake as two passers-by in the background slow down to look at him and then move on. His face stays impassive through the final frame.

overall_soundscape: Night traffic hiss and distant horns under a low city hum. Wet footsteps approach across the foreground, fabric creaks twice as the jacket opens and closes, and street lamps tick as they brighten.

non_diegetic_music: A sparse electronic pulse at a moderate tempo, a sub-bass note entering at the cut and holding flat through the end.
```

### B3 · 00:00–00:15 — the shield cracks

```text
summary:
[reference generation] Third act: <Subject 4> stands on a campus lawn while a gold shield above the building behind him cracks, and the world drains around him.

retention_analysis:
<Subject 4> (appears in [Shot 1], [Shot 2]): fully_preserved - white tee, backpack, blue jeans and blue folder retained.
<Subject 6> (appears in [Shot 1], [Shot 2]): fully_preserved - flat vector daylight palette and hard shadows retained.

detailed_description:
The target video is a 2D-animated flat-vector illustration in the style of <Subject 6>, bright campus daylight against a pale sky.
[Shot 1] A wide shot frames a white campus building with indigo windows across a green lawn. <Subject 4>, the student, walks in from frame-left at the lower third carrying the blue folder, and stops. The camera pushes in with small amplitude at slow speed as a large translucent gold shield materialises above the building roof and turns slowly in place.
[Shot 2] At 00:07.000, the shot cuts to a medium close-up of <Subject 4>. Behind his shoulder the shield develops a hairline fracture that spreads outward in three branches, and small gold flakes drift down past his face. His expression drops from neutral to stricken, his shoulders lower, and the backpack strap slips down his arm. The camera holds a static shot, then tilts up with small amplitude at slow speed toward the widening crack, which holds through the final frame.

overall_soundscape: Open-air campus ambience with light wind across grass and a distant bell. A thin glassy crack propagates with a rising shimmer, followed by small flakes ticking as they land.

non_diegetic_music: Solo cello at a slow tempo, a single high piano tone on the crack, and the low string thinning out rather than resolving.
```

### B4 · 00:00–00:15 — the mentor's counsel and the end card

```text
summary:
[reference generation] Final act: <Subject 5> counsels <Subject 4> in a study, then the film lands on the gold end card.

retention_analysis:
<Subject 5> (appears in [Shot 1], [Shot 2]): fully_preserved - grey bun, round glasses and green saree retained.
<Subject 4> (appears in [Shot 1], [Shot 2]): fully_preserved - white tee, backpack and blue folder retained.
<Subject 6> (appears in [Shot 1], [Shot 2], [Shot 3]): fully_preserved - flat vector warm lamp light and hard shadows retained.

detailed_description:
The target video is a 2D-animated flat-vector illustration in the style of <Subject 6>, a warm study interior with a single lamp and a wall of books.
[Shot 1] A two-shot establishes the study: <Subject 5>, the mentor, stands at the left third with an open hand raised, and <Subject 4>, the student, sits at the right third with the blue folder on his knees. The camera pushes in with small amplitude at slow speed as the mentor leans forward and the student lifts his head to meet her eyes.
[Shot 2] At 00:07.000, the shot cuts to a medium close-up of the mentor. She closes her raised hand into a small deliberate fist at chest height, holds it, then nods once. The lamp behind her flares slightly and the student's shadow nods back on the book wall behind them.
[Shot 3] At 00:12.000, the shot cuts to a gold English-line end card on deep navy: two stacked lines of large Bengali lettering, "সুনাম রক্ষা করুন —" above "প্রাণ দিয়ে।", with a thin gold rule underneath. The camera holds a static shot and the lettering settles into place with no further motion through the final frame.

overall_soundscape: A close, quiet study room tone with a faint lamp buzz. Fabric shifts as the mentor leans in, a soft tap as her fist closes, and the room tone drops out under the end card.

non_diegetic_music: A single warm piano figure at a slow tempo, joined by low strings that resolve on the end card and decay in the last second.
```

### Speaker map

The narration is one continuous voice, so it is `(S1)` in every generation. Voiceover lines are
spoken by a deep mature male narrator in Bengali, delivered with `says in an off-screen voiceover`,
followed by the sentence that the on-screen character's lips stay closed — matching the delivered
54 s cut, which has no lip-sync dialogue.

---

## Assembling

1. Generate each Ref2VA block at the same resolution and ratio (16:9, 768p first pass).
2. Keep the last frame of each block as the next block's first-frame reference when continuity slips.
3. Stitch in order; the shared `<Subject 6>` line is what keeps the illustration style from drifting.
4. Trim each block to its spoken length before stitching — H3 output never lands exactly on 15.00 s.
