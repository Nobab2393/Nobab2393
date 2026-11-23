---
name: animation-style-atlas
description: The full atlas of animation video styles — 119 styles extracted from four open skill libraries, grouped in 17 families, with palettes, media, motion systems and "use for" tags. Use when the user asks "what animation styles are there", wants to pick a look for a video, asks to make something in a named style (riso, woodcut, ukiyo-e, paper-cut, pixel, isometric, stickman, kinetic type, dark keynote…), or wants to mix/define a new style. Start at references/by-use-case.md, then references/atlas.md.
---

# Animation Style Atlas — every style, and how to choose one

**119 styles.** 99 from `lemomo-ai/lemo-opuscar`, 7 from `cth9191/animate`, 13 from
`artemnovitckii/claude-animation-skills` + `tuzhechen2005/opus-video-skills`. Each record in
`references/atlas.json` is machine-extracted from that library's own `STYLE.md`: the tagline, the
section-1 essence bullets, its "not this" contrast, its printed hexes, its first timing line and its
declared uses. `references/atlas.md` is the readable version, grouped in 17 families.

**Read the atlas as evidence, not as a menu.** A style file exists because someone shipped a film in
that look and wrote down what made it work. The value is in the *specifics* — "fill printed 4 px off
its line, re-rolled on twos" — not in the name.

## 0. A style is three decisions, not one adjective

Almost every failed attempt gets this wrong: they name the *era* ("1950s", "retro", "anime") and never
choose the other two.

| Axis | Question | Examples |
|---|---|---|
| **Medium** | What is the picture *made of*? | ink on paper · torn paper · halftone dots · 3 px flat vector · graphite · pixels · glass · light on a table · printed ink layers |
| **Era / visual culture** | Which picture-making tradition? | UPA 1950s · 80s cel anime · Soviet montage · Swiss typographic · Ukiyo-e · risograph zine · 90s CRT |
| **Motion system** | How does it move? | on-2s stop-motion step · springy UI motion · camera-only over one drawing · live drawing · data draw-on · 3D miniature with real light · era texture over a clean move |

A style is a **medium + an era + a motion system**, and the medium has to be visible at phone size in
every frame. That's the single most repeated rule in all 119 files.

## 1. The 17 families

| Family | n | Feel | Examples |
|---|---|---|---|
| Line Diagrams | 8 | precise, explanatory, hairline hairlines | blueprint · exploded teardown · line-art cutaway · isometric line art |
| Graphic & Type | 8 | poster logic, type as architecture | Swiss motion · pictogram motion · art deco · silhouettes |
| Instruments & Evidence | 8 | we are looking at *records* | archive light table · security x-ray · microscope · satellite briefing |
| Edit & Documentary | 8 | footage-native, archive-native | city symphony · constructivist montage · vintage collage · split-screen |
| Print & Printmaking | 8 | ink on paper, visible registration | riso · pop art · halftone dossier · woodcut · copperplate · silkscreen |
| 3D & Miniature | 8 | a tabletop world with real light | memphis diorama · tilt-shift · paper-cut lightbox · crayon world · low-poly island |
| Sketch & Board | 7 | someone is drawing, now | whiteboard · chalkboard · sketchnote · marker on paper · urban sketch · tablet sketch |
| Traditional Crafts | 7 | a material craft, honoured | ukiyo-e · shadow puppet · stained glass · red paper-cut · gilded illumination · ink wash |
| Cartoons | 6 | character, expression, gags | 30s rubber hose · 80s cel anime · mid-century toon · comic-history · manga panels |
| Screens & Interfaces | 6 | the interface is the subject | tablet app flythrough · live screencast · mascot screencast · dark keynote · hologram HUD |
| Data & Maps | 6 | one number, one territory | data storytelling · data physicalization · transit map · 3D map explainer |
| Film & Tape | 5 | the recording medium shows | 1920s silent film · 1920s newsreel · CRT ASCII · double exposure · scratch film |
| Light & Lines | 5 | light itself draws | neon tubes · flow-field wind lines · oscilloscope math · firefly pointillism |
| Painting & Illustration | 5 | brush, colour, storybook | watercolour brush · impasto · coloured pencil · crayon picture book |
| Games | 4 | a playable grammar | 16-bit pixel RPG · rhythm game show · microgame frenzy · 2.5D pixel art |
| Procedural canvas | 7 | code-drawn, boil-on-2s | cut paper · crosshatch · riso · sketchbook · math · pixel · isometric |
| Code-drawn style skill | 13 | single-spec, 10-second renders | graph · map-route · breakdown · kurzgesagt · low-poly · minecraft · dan-koe |

## 2. Choose in this order

1. **What is the subject?** A fact, a process, a person, a product, a place, a feeling.
2. **Is there a character?** If the piece needs faces, acting and continuity → Cartoons / Sketch & Board /
   Traditional Crafts, and expect to lock character sheets. If not → diagrams, print, data, type.
3. **Is there a number or a datum?** Then the style must have a *first-class* way to show magnitude
   (data storytelling, pictogram motion, dark keynote, data physicalization).
4. **Is the subject already an object?** Then the style should be a *medium about that object*: an
   archive item wants an archive light table; a device wants a teardown; a place wants a transit map.
5. **How long?** Under 15 s: one idea + one look, no morphs. 15–45 s: 2–3 beats, 1–3 morphs.
   45 s+: chapters, each with its own ground colour — or the fatigue wins.
6. **Then open `references/by-use-case.md`** and take 2–3 candidates; the atlas entry tells you the
   medium specifics you must reproduce.

## 3. Universal rules (they hold in every one of the 119)

Distilled from `cth9191/animate`'s craft notes and cross-checked against all 99 lemo style files.
Full version: `references/universal-craft.md`.

**Story**
- The plot is a true process: real steps, real order; pace follows meaning, not a fixed bpm.
- **One constant the eye can hold** (a hero, a stage, a page) while everything else changes.
- **Colour means one thing** for the whole piece; never spend it on decoration.
- Silence before the payoff, loudest *on* the payoff.
- The end is the start, changed.
- One device you can say in a sentence ("the spark gains a ray each era").

**Frame**
- **The medium shows** at phone size in every frame — torn edge, hatch, dots, grain, pixels.
- Aimed-out, not labelled: "AI winter" = snow on a closed lab, not the word WINTER.
- Something is happening; held frames still have idle life (steam, blink, LED, cursor).
- Scale varies: wides, mids, and at least one extreme close-up.
- Phone-safe: 9:16 content inside x 60–940, y 250–1500; anything that matters ≥ 100 px.

**Motion**
- Cuts and morphs land on the beat grid; on-2s styles step the whole world at once.
- One hard cut in a morph-joined piece — the slam on the payoff.
- Cameras move *a world point to a screen point*, never "zoom about a point".
- Hard cuts land on finished frames: the new shot is fully drawn on its first frame.

**Banned defaults** (they read as generic AI slop in any style): a centred title on a gradient;
everything fading in; labels or borders in the corners; glows on chrome; generic particle bursts;
a logo sting as the whole ending.

## 4. Mixing styles without making mud

Allowed, because they sit on different axes:

- a **medium** × a **type system** (torn paper with Swiss flush-left grotesk)
- an **era texture** over a **clean motion system** (1920s gate weave over a still diagram)
- a **diagram family** × a **medium** (halftone-dotted teardown)

Forbidden, because they fight on the same axis:

- two media in one frame (halftone dots *and* torn paper edges)
- two eras in one piece (80s cel anime next to art deco)
- two motion systems (springy UI pops inside an on-2s stop-motion world)
- anything photoreal inside a hand-drawn medium

Rule of thumb: **one medium, one era, one motion system, one reserved colour, per piece.**

## 5. Write the brief medium-first

The failure mode is adjective-first prompting ("make it cinematic and retro and premium"). Describe
the *making*, because that's what the renderer has to do:

```
Make a <N>-second <FORMAT> about <SUBJECT> in the <STYLE NAME> style.

MEDIUM      what the picture is physically made of, and what must be visible at phone size
ERA         the tradition it belongs to, and what it must never borrow
MOTION      the motion system, its fps/step, its easing, its stagger
PALETTE     ground / ink / accent hexes + the one reserved meaning
TYPE        family, weights, sizes at 1080 wide, where the caption sits
BEATS       timecoded: what appears, what changes, what the loop hands back
FORBIDDEN   the 2–3 things that would break the look
OUTPUT      1080x1920, 30 fps, H.264 + a contact sheet with the safe area marked
```

## 6. Self-review before delivery

1. Contact sheet of one still per beat. If two beats look like the same picture, cut one.
2. Phone test: open a still at 360 px wide. Is the medium still visible? Is the caption readable?
3. The 9 frame checks from `references/universal-craft.md` §Frame.
4. Name the weakest beat and what would fix it — that's the next run's to-do list.

## 7. What this atlas does not cover — say so plainly

No 3D CGI / Pixar-grade rendering, no anime sakuga (hand-keyed 2s/3s animation with impact frames),
no rotoscoping, no mocap or live-action hybrid, no generative-video-model looks (Sora/Veo/Kling
"cinematic" texture). Those need tools this library does not teach. If the user asks for them, name
the gap instead of faking it with an atlas style.

## Files

```
SKILL.md                        this router + the three axes + the mixing rules
references/atlas.md             119 styles, grouped in 17 families, with palettes + specifics
references/by-use-case.md       the 261 "use for" tags, inverted — start here when choosing
references/universal-craft.md   story / frame / motion / sound / review rules, in full
references/atlas.json           the extracted records (source of both .md files)
atlas-poster.png                one card per style: its palette and family
scripts/build_atlas.py          re-extract from cloned source repos (--src, repeatable)
scripts/render_atlas.py         atlas.json -> atlas.md, by-use-case.md, poster
```
