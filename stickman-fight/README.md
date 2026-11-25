# অন্ধকার পাঠ ০৩ · লড়াই — a daylight stickman fight in Bangla

The story is in [`01-script.md`](01-script.md). **Output:**
[`stickman-fight-1080x1920.mp4`](stickman-fight-1080x1920.mp4) — 1080×1920, 24 fps, 41.9 s,
H.264 + AAC, Bangla voice-over, Bangla captions.

This is a different engine from the two 3D "dark lesson" films next door: **no 3D at all.** It is
flat 2D line art drawn straight onto a PIL canvas, one skeleton per fighter, and a pose is just a
dict of joint angles.

```
stage.py   daylight stage: camera, sun (a scaled radial gradient), dusty ground, skyline,
           stick skeleton (hip -> spine -> head, two arms, two legs) and its shadow
fight.py   poses + the strike engine (windup -> extend -> recover), seven scenes, captions,
           the lesson card, procedural SFX, the segmented renderer and the ffmpeg mux
deva.py    Bengali shaping (HarfBuzz) -> outlines -> pixel mask, from the 3D films
audio/     s1..s7.mp3 (voice-08), v1..v7.mp3 (silence-trimmed), sfx/*.wav (generated), mix.wav
```

## How the fight is animated

A pose is `dict(lean, hipdy, rot, l1, l2, r1, r2, a1, a2, b1, b2, head)` — every number is an
angle in degrees measured from straight down, positive toward the direction the figure faces. Two
poses can be `mix()`ed, so the whole film is keyframes plus a strike engine:

```
strike(t, events) -> (windup_weight, extend_weight)
```

For a punch at `te`: wind up from `te-0.26`, snap out at `te-0.07`, hold, recover by `te+0.34`.
The attacker blends `GUARD -> WIND -> OUT`; the defender blends `GUARD -> SLIP/DUCK/WEAVE` a frame
later. Ten punches and three kicks are just two lists of `te` values — which is why the barrage in
scene 5 stays readable: every hit is a single, timed, physical move.

## Two things that took a rewrite

- **PIL's `"RGBA"` draw mode replaces alpha, it does not add.** Drawing a semi-transparent shadow
  straight onto the frame punched a hole that turned black on flatten — the first contact sheet
  had black discs in the sky and black ovals under every figure. Everything translucent now goes
  onto one accumulating ink layer, composited once per frame; type goes onto a second layer above
  it, so a caption can never be buried by a later line.
- **The sun cannot be drawn as three circles.** It came out as a target, then as a fog blob. It is
  now one radial-gradient tile (`_glow_tile`) scaled to the frame and composited, so the falloff is
  smooth at any size.

## Render

```bash
python3 fight.py --poses                 # pose sheet (design aid)
python3 fight.py --still 17.8            # one frame
python3 fight.py --mix                   # voice + procedural SFX -> audio/mix.wav
python3 fight.py --seg 0 260 f1.mp4      # 4 chunks, ~0.9 s/frame on one core
python3 fight.py --join f1.mp4 f2.mp4 f3.mp4 f4.mp4
```

Timeline: VO starts at `[0.90, 5.68, 9.80, 15.43, 20.46, 27.76, 33.18]`, scene bounds
`[0, 5.38, 9.50, 15.13, 20.16, 27.46, 32.88, 38.41]`, total 41.86 s / 1005 frames.

## Honest notes

- The voice is Bangla TTS (`voice_id="voice-08"`), not a human read — same constraint as the
  previous two episodes.
- Sound effects are **synthesised** in `fight.py` (band-passed noise plus decaying sines): no
  sample library, no licence questions, and no impact sample pretending to be a real recording.
- Captions are one semantic line, auto-shrunk to fit the 950-px text measure so a long Bangla
  sentence never runs off the frame.
