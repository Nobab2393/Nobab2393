# design-lab — what I got wrong, what the rules are, and the plates that prove I can apply them

This is a study, not a portfolio piece. It exists because the backgrounds and the cast in
`stickman-fight/` were weak, and "try harder" is not a fix. Below: the specific failures, the
rules that address them, and three code-generated plates that apply each rule where you can
check it.

Everything here is drawn by `cast2.py` (the cast rig), `bg_design.py` (the layered field) and
`sheets.py` (the plates). No stock art, no traced reference.

```bash
python3 sheets.py character    # out/character-sheet.png
python3 sheets.py background   # out/background-studies.png
python3 sheets.py compare      # out/compare-v1-v2.png
```

---

## 1. The diagnosis, in the film's own terms

These are the things a viewer would feel without being able to name. Naming them is the point.

**Background** (`stickman-fight/stage.py`)

| what the film does | why it reads flat |
|---|---|
| one flat sky gradient and one flat ground band, horizon at 65–70% | two values, no depth cue: the eye has nothing to walk back on |
| skyline bars drawn at nearly the hero's contrast | the background competes with the subject, so the subject stops being the subject |
| a crowd drawn as see-through outlines in the same line language as the hero | unreadable clutter at the same value as the figure; a see-through extra reads as a ghost, not a person |
| nothing in front of the character, ever | no near plane → no parallax cue → the plate is a single sheet of paper |
| no light direction | no cast shadow, no rim, so nothing is attached to the ground |
| the hero stood dead centre with nothing behind him but sky | a composition with no destination; the frame has no "third" to rest on |

**Cast** (`stickman-fight/fight.py`)

| what the film does | why it reads flat |
|---|---|
| hero and bully are the same rig at different scales | size is not characterisation; at 44 px on a phone they were the same person |
| same round head, same line weight, no prop | no silhouette identity, so nothing survives a small screen |
| no faces at all | a fight with no expressions is two diagrams colliding |
| every pose change is a limb angle, never a posture change | the character never *occupies* space differently |

---

## 2. Rules for building a character

The order matters. Skipping a step is what produces a "drawing" instead of a character.

1. **One sentence first.** Who are they, what do they want, what is in the way. If that sentence
   is vague, the design will be vague. (Ayan: *a boy who wants to stop flinching.*)
2. **Silhouette before detail.** Fill the shape solid black at 44–92 px. If you cannot tell who
   it is, no costume, texture or colour will save it. This is the single highest-value test.
3. **One dominant shape per character, contrasted across the cast.** Circle = soft, young, quick.
   Square = solid, stubborn, immovable. Triangle = sharp, thin, uneasy. Tall rectangle = aloof.
   Pear = worn down. The shapes must differ *between* characters; varying them randomly inside one
   cast just looks noisy.
4. **Head-count is the tone dial.** ~4 heads = childlike / comic. ~5 = grounded adult. 7–8 =
   heroic / serious. Fix it per character and never drift: a head-count that changes between shots
   changes the character. (Mine: 4.2 / 4.6 / 5.4.)
5. **Asymmetry + one signature prop.** A perfectly symmetric design is dead on arrival. One prop
   that only that character has (scarf, flat-top, satchel) is what makes them recognisable at
   phone size and from behind.
6. **The face has to be able to act.** Two eyes, brows, a mouth is enough — but the *brows* carry
   the emotion and the mouth confirms it. Build a range that includes the extremes (rage, shock),
   not just six flavours of neutral.
7. **Appeal = clarity, rhythm, and the sense that they can move.** Not cuteness. Clear at a
   glance, varied enough to feel alive, posed so the body looks like it could leave the pose.
8. **The model sheet is the proof.** Same construction lines, front / 3-4 / side / back, an
   expression range at one head diameter, a size comparison, and a desaturated value check.
   If it cannot be redrawn from the sheet, it was a one-off drawing, not a design.

## 3. Rules for building a background

1. **Value structure first (notan).** Block 3–5 values and one light direction before any detail.
   If the grayscale thumbnail doesn't read, colour and texture will only make it muddier.
2. **Layers, in painter order.** Sky/far → midground → ground → *character* → foreground. The
   character is inserted, not composited on top of a finished picture.
3. **Distance = lower contrast, cooler colour, fewer edges, thinner line.** Not more haze and not
   more detail. Near field ~70% contrast, mid ~18–30%, far ~8%.
4. **The character must hold the highest contrast in the frame.** If the background reaches it,
   the eye stops finding the subject. This is why the skyline bars and the crowd in the film hurt.
5. **A near plane.** Something dark, out of focus, in front — a branch, grass, a shoulder. It
   costs nothing and buys all the depth.
6. **Projections.** Let the character pass *behind* something (a post, a pillar, a branch). Overlap
   is the strongest depth cue in 2D and it costs one extra draw call.
7. **One light direction, honoured everywhere.** Sun upper-right → every cast shadow falls left,
   every rim faces right. Break it once and the plate goes flat again.
8. **Staging, not decoration.** Subject on a third, leading lines (path, wall, branch) aimed at
   it, and a reserved calm zone for the caption/type — never over the face.
9. **Guard the action zone.** Nothing busy within roughly a head-width of the contact point.

---

## 4. The plates

### `out/character-sheet.png` — the cast as decisions

- **Panel 1** the three characters in a neutral A-pose at one shared scale, with head-unit ticks
  drawn beside them, plus the dial table (head shape, head-count, height, shoulder:hip, limb
  thickness, hands, posture). Those numbers *are* the design; changing one changes the character.
- **Panel 2** solid-black silhouettes and a 44 px squint strip. Lean / heavy / hunched still read
  at phone size with zero detail — that is the test passing.
- **Panel 3** a 2D turnaround. In 2D a "rotation" is not a rotation: it is four decisions held
  constant (head shape and size, shoulder:hip, eye-line offset, prop direction). The strap-down
  warning is the honest trade: lose the prop, lose recognition.
- **Panel 4** eight expressions per character at one head diameter, so the head shape is the
  constant and the face is the variable. Rage and shock are included because a range that stops
  at "mildly annoyed" is useless in a fight.

### `out/background-studies.png` — the field as structure

- **Study 1** the notan: four values only, figure as the lightest shape. This is the design.
- **Study 2** the same plate with its four layers labelled by actual measured contrast (8 / 18 /
  30 / 70%), including the near plane.
- **Study 3** the staged frame: subject on the left third, eye line on the lower third, path, wall
  and branch all aimed at him, contact shadow so he's attached to the ground, caption band
  reserved below the knees, a soft paper halo instead of an outline to separate him from the sky.

### `out/compare-v1-v2.png` — same beat, before and after

Left is the film's plate rebuilt as it was (one value, ghost crowd, no near plane, faceless hero).
Right is the same beat with the rules applied. The list of twelve changes is the argument: not one
of them is "more detail".

---

## 5. What this study does **not** prove, honestly

- These are **stills**. The rules hold for a frame; a 24 fps sequence adds new failure modes
  (prop continuity, light consistency across camera moves, whether the silhouette still reads in
  motion). That test is the next render, not this sheet.
- This is a **2D ink language**, so the turnaround is width-modulation and eye-line offset, not a
  true 3D rotation. It is consistent, not complete.
- Expressions are **iconographic** (brows + eyes + mouth on a ring). They read at 44 px; they will
  not carry a close-up monologue.
- The background is **one location in one light**. Dawn / night / interior need their own value
  keys, and I have not built those yet.
- Nothing here fixes the film retroactively. `stickman-fight-1080x1920.mp4` still has the old
  plates; that is why it is left as it shipped.

## 6. Next, in order

1. Render a 10-second test shot with the new cast and the new field, at 1080×1920, and check the
   silhouette at phone size *in motion*.
2. Build two more value keys for the same location (dusk, and a lit interior) from study 1.
3. Add projections: walk a character behind the path-side posts and through the branch.
4. Only then rebuild a full film on these rules.
