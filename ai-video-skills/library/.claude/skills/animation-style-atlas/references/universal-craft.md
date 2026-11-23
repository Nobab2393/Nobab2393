# Universal Craft — the rules that survived 119 style files

Two sources, and they agree: `cth9191/animate` (`craft.md`, `grammar/FRAME.md`, `STORY.md`, `FORMATS.md`)
written from shipped pieces, and the 99 `STYLE.md` files in `lemomo-ai/lemo-opuscar`, where the same
demands appear over and over in different words ("the medium shows", "one reserved colour", "boil on
2s"). Where they conflict, the more specific rule wins.

## Story

- **The plot is a true process.** Real steps in their real order; every beat follows from the one
  before. Pace belongs to what a beat *means*, not to a fixed seconds-per-beat.
- **One constant the eye can hold** — a hero, a stage, a page — while everything else changes. In
  character styles it's a hero with a face and a mood; in diagram styles it's the object or the axes.
- **Colour means one thing** for the whole piece (orange = the machine's mind; red = sound). Never spend
  that colour on decoration. In the atlas: cut paper reserves orange for the spark, ukiyo-e reserves
  vermilion, dark keynote gives the accent to one number.
- **Silence before the payoff, loudest on the payoff.** 0.5–4 s of near-silence on a held image, then
  the single loudest hit. Find the beat the true story already has.
- **The busiest moment is not the loudest.** Peak density goes just *before* the silence; the loud hit
  is the turn.
- **The end is the start, changed.** Return to the opening image with the difference the story made.
- **One device you can say in a sentence** ("the spark gains a ray each era").
- **Facts supply the arc — and must be true.** Web-check every date and number; say "a", not "the
  first", unless sourced.

## Frame — the 9 checks (every key frame, every style)

1. **One constant the eye can hold.**
2. **Colour means one thing.**
3. **The medium shows** — torn paper, hatching, halftone dots, graphite, pixels — visible at phone
   size in every frame. A frame that could be any style is clip art.
4. **The idea is acted out, not labelled.** "AI winter" is snow on a closed lab and an empty piggy
   bank. A caption may name it; the picture has to show it.
5. **Something is happening** — mid-move, mid-reaction, mid-build. Held frames keep idle life: a blink,
   a bob, steam, a blinking LED, a cursor. Character styles want 3+ details of background life.
6. **Text lives in the world** (a note, a sign, a tag, a screen, a face of an object) or is set like the
   style's own type. One short caption per beat, ≥ 50 px at 1080 wide.
7. **Scale varies across the board**, including at least one extreme close-up. Same framing every panel
   = slideshow.
8. **A recurring thread**: a callback prop, a critter, a colour, a shape that returns changed.
9. **Phone-safe:** on 9:16 keep what matters inside x 60–940, y 250–1500; anything that matters is
   ≥ ~100 px. Captions ≥ 50 px. (Other platforms: Instagram covers ~250 px top / ~320 px bottom.)

**Banned defaults** — they read as generic AI video: a centred title on a gradient; everything fading
in; labels or frame borders in the corners; glows on UI chrome; generic particle bursts; a logo sting
as the only ending.

## Motion

- **Springs over easing curves** for anything with mass; a tiny overshoot on UI, none on big type. A
  value with many targets gets one spring per change, never a restarted ease.
- **Everything moves on 2s** in step-based styles: boil, camera and every move share `B = floor(F/2)`.
- **Entrances overshoot and settle** (UI/vector looks): `cubic-bezier(0.34,1.56,0.64,1)`, 12 frames.
- **Stagger groups by 2–4 frames**, and shrink the stagger as the group grows.
- **Cameras put a world point on a screen point** — never "zoom about a point", which drops the
  subject under the caption. Pin the hero in the fastest stretch.
- **Hard cuts land on finished frames:** what defines the new shot is fully drawn on its first frame.
- **What existed before the step is on screen from frame 0**; only the step's own effects animate in.
- **Captions hold:** ≥ 1.25 s on screen, ≤ 3.5 words/s.

## Transitions

- **Match the transition to the format.** Chronologies bridge *from the scene* (shape morph, draw-off /
  draw-on); catalogue and character pieces cut hard on the beat.
- **Keep at most one hard cut** in a morph-joined piece — the slam on the payoff.
- **Shape-morph bridge:** the old world closes in on one object through a window shaped like it (a torn
  hole, an inked iris, a printed circle), the object blends into its counterpart on blank paper, the new
  world opens out of it.
- **Budget morphs in short pieces:** each bridge costs ~1.2 s (0.4 s of it blank); under 30 s use ≤ 3.
- **Bridge objects stay ≥ 200 px at the boundary**, or the world shrinks into a tiny window early.
- **Morph on the style's blank sheet**, never a blend of two wall colours (mud).
- No fades between worlds. A fade is a hole where a transition should be.

## Timing

- **24 fps + 120 BPM** makes an 8th = 6 frames and a 16th = 3 — every cut and morph lands on a whole
  frame. At 30 fps the equivalent is 112.5 BPM; at 60 fps, 900/7 BPM.
- Cuts and morph centres sit on the 8th grid, proven by measurement, not by eye.
- **Loop length = frames / fps**, so the loop point sits on the frame grid; fold the audio tail over
  the start.

## Sound (when scored)

- **With a voice-over the voice is the clock**; each beat starts ~0.3 s after a sentence ends, and the
  payoff lands in the pause *before* the line that names it.
- **With the user's track the song is the arc**: find its drop and biggest hit; cut on its beats.
- **The score improves with the story** — thin early, fullest at the peak; motifs carry characters.
- **Loudness stage:** RMS-normalise to −17 dBFS, look-ahead limiter at −1 dBFS. Balance by removing
  energy, not adding it.
- **You can't hear your own mix.** Measure it (loudest 100 ms window, act arc) and ask the user to
  listen.

## Review

- **Three layers, every time:** test tiles while building, the measured checks, and contact sheets per
  shot with a written pass table.
- **Don't trust your eye for text** — a fresh run shipped a shot whose caption was cut off at the frame
  edge. Measure text bounds.
- Read the phone sheet (one frame a second at 360 px) before calling a piece done.
- Flag **DEAD BEATS**: nothing new for more than ~2–4 s (silence acts exempt).
- **Eras that differ only in motion look identical on a contact sheet** — give each a still-visible
  signature.
- Name the weakest shot and what would fix it; that's the next run's to-do list.

## References, measured not reskinned

- Reference media stays local and uncommitted — it's someone else's work, kept for study.
- **Measure a reference into a timed table first:** cuts, holds, what's on screen, the loudest moment,
  the silence. Then map its beats onto the new subject — find its thesis, spine, problem and callback,
  and give each a true counterpart. Never reskin it.
- **Compare proportions, not pixels** (an element's width as % of frame) when matching a look.
