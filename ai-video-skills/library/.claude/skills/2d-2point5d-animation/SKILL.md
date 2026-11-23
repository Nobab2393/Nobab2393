---
name: 2d-2point5d-animation
description: Make 2D animation and 2.5D parallax shots — squash/stretch, anticipation, arcs, follow-through, moving holds, timing charts, plus a real multiplane camera rig (depth weights, overscan, feathered seams, dolly/push-in at three speeds). Use when the user says "2D animation", "2.5D", "parallax", "multiplane", "make a still move like a camera", "animate this drawing", or wants code-drawn cartoon motion with proper weight and timing rather than slideshow pops.
---

# 2D & 2.5D Animation

Two things live here, and they stack:

- **2D craft** — the animation principles that make a flat drawing *act*: squash and stretch,
  anticipation, arcs, follow-through, and above all **timing and spacing**.
- **2.5D** — depth faked from flat artwork with a **multiplane camera**: separate layers, moved at
  different rates. Ten to twenty layers for a simple scene, fifty to a hundred for a rich one.

Depth is not a filter and it is not a zoom. **If every layer moves at one speed, the frame stays flat
no matter how fancy the camera rig looks.**

## 1. The 2D rule that people skip

Timing is not the same as easing. **Easing is the shape of a move; timing is how many frames it
occupies and how the drawings are spaced inside them.**

| Concept | What it means in practice |
|---|---|
| **On-1s / on-2s / on-3s** | A new drawing every 1, 2 or 3 frames. On-2s at 24 fps = 12 drawings/s — the classic cartoon feel. Mixing on-2s body with on-1s hands is how limited animation stays alive. |
| **Spacing** | Ease-out = drawings far apart, then close together. Ease-in = close, then far. The *drawing count* stays constant; only the gaps change. |
| **Moving hold** | A held pose is never frozen: 2–3 frames of a 1–2 px drift, a breath, a blink. Frozen holds read as a broken render. |
| **Smear / multiple** | When something moves more than its own width in one frame, stretch it along the path instead of teleporting it. |
| **Arcs** | Nothing organic travels in a straight line. Give every path a bow (5–15 % of its chord). |
| **Anticipation** | 20–30 % of the action's duration in the *opposite* direction, before it goes. |
| **Follow-through** | After something stops, the soft parts keep going for 6–12 frames, overshooting once and settling. |

Nine of the twelve classic principles translate directly into numbers you can code. The full table —
squash amounts, overshoot percentages, hold lengths, smear widths — is in
`references/twelve-principles.md`.

## 2. The 2.5D rig

A multiplane shot is five decisions:

1. **How many depth planes.** 3 for a quick hit (far / mid / foreground); 8–12 for a landscape;
   20+ only if you can afford the paint-out work. Each plane needs its own artwork — including the
   regions the camera will reveal (this is the paint-out problem, and it's where most attempts die).
2. **Depth weight per plane.** `w = 1/z`. Screen scale `s = 1 + 0.5w` and lateral offset
   `= pan · k · w` gives the reference numbers: far 1.05, mid 1.09, foreground 1.14 over one push-in,
   with the foreground drifting ~3× further sideways than the far plane.
3. **Overscan.** Every layer is drawn 5–10 % larger than frame and extends past all four edges, so a
   drift never exposes a seam. Feather the alpha ramp over ~100 px on cut-out photos; for vector art,
   overscan instead of feathering.
4. **The camera.** One move per shot. Dolly (push-in), truck (lateral), or tilt — never all three.
   Keep total drift under ~25 px on feathered plates; beyond that you need real masks.
5. **Depth of field.** Nearer planes blur slightly as the camera pulls focus; far planes never bleed
   over a sharp foreground.

**Show the split before you use it.** For one beat, physically separate the layers with FAR / MID / FG
chips, then glide them back together and push in. An audience that has seen the layers come apart
reads the subsequent push as *depth* instead of *zoom* — this is the single most shareable 15 frames
in the format.

Full rig spec, the projection math, and the failure list: `references/parallax-rig.md`.

## 3. Cut and seam discipline

Transitions are where amateur motion dies. Two rules:

- **Cut at peak velocity and match direction + speed on both sides** (partial travel ~12 % of frame,
  mirrored `power4` eases). Never let the exit decelerate into a stop and the entry start from zero.
- **Scale-velocity has a sign.** A push exit (`1 → 1.2`) must be answered by a growing entry
  (`0.75 → 1`); a pull exit (`1 → 0.8`) by a shrinking entry (`1.25 → 1`). The common mistake is
  answering a pull with the default grow-from-small entrance.
- **Blur peaks at the swap:** 10 px on text-scale subjects, 18–20 px on a full-frame surface, both
  sides equal. 20 px on a headline smears the letterforms into a glitch.

Arrival cascades, the slow-fast-slow "nudge curve" (10 % / 65 % / 25 % distance), and the velocity
seam tables: `references/timing-and-seams.md`.

## 4. Pipeline

```
1  Art         one drawing per layer, overscanned, flat colour, one reserved accent
2  Rig         depth weights, camera path, easing, frame exposure (on-1s / on-2s)
3  Beats       timecoded: what moves, what holds, where the cut is
4  The split   one beat that shows the layers (if 2.5D)
5  Render      frames are a pure function of t — deterministic, re-renderable
6  QC          contact sheet, phone-size read, seam audit at the extremes of the move
```

Renderer notes for this repo: PIL/OpenCV → ffmpeg works (no browser needed), 2× supersample then
LANCZOS down; a working 12-second example is `2d-2point5d-demo/build.py` at the repo root.

## 5. Brief template

```
Make a <N>-second <FORMAT> 2D/2.5D shot of <SCENE>.

2D CRAFT
- timing: on-2s body / on-1s accents, <beats>; anticipation <x>f, follow-through <y>f
- squash & stretch <amounts>; arcs on every path; moving holds on held poses

DEPTH (if 2.5D)
- planes: <far / mid / fg> (+ what is painted on each, + what must be painted out)
- camera: <one move>, total drift <px>, depth weights <w1, w2, w3>
- overscan <pct>, seams audited at both ends of the move

LOOK
- ground / ink / accent hexes; one reserved colour meaning; medium visible at phone size

BEATS
- timecoded, with the layer-split reveal if the shot is 2.5D

OUTPUT
- 1080x1920, 30 fps, H.264, plus a contact sheet and a still at the furthest camera point
```

## 6. QC — what actually goes wrong

1. **Flat parallax** — all layers moving at one rate. Check scale ratios, not vibes.
2. **Seam exposure** — the far edge of a layer slides into frame. Draw 10 % past every edge.
3. **Billboard distortion** — too wide a camera arc on flat art; the picture shears. Keep the dolly
   under ~10 % and the pan under ~40 px.
4. **Holds that freeze** — add a breathing offset of 1–2 px.
5. **Pops instead of arcs** — the middle of a path is a straight line and the ease is doing all the
   work. Bend it.
6. **Two moves at once** — dolly + pan + tilt in one shot reads as a drone, not a camera.
7. **Accent creep** — the reserved colour appearing on decoration.
8. **Flat at phone size** — check a 360 px still: if the medium and the depth cue vanish, they don't
   exist.

## 7. Honesty notes

- 2.5D is not 3D: there is no geometry, so a large camera arc exposes that instantly. Keep moves
  conservative and let the layers do the work.
- Depth from a single AI-generated still needs either real masks or a depth map; a feathered horizontal
  band split only survives ~25 px of travel.
- Photoreal 3D CGI, rotoscoping and mocap are out of scope — say so rather than faking them.

## Files

```
SKILL.md                        this router
references/twelve-principles.md the principles as numbers (squash, arcs, holds, smears, follow-through)
references/parallax-rig.md      the multiplane rig: math, layer budget, overscan, camera, failure modes
references/timing-and-seams.md  timing charts, on-2s/3s, velocity-matched seams, waterfall, nudge curve
```

Sources: `edenfunf/reelmimic` (`cut-the-curve` seam catalog), `cth9191/animate` (frame/craft rules),
`artemnovitckii/claude-animation-skills` (2.5D and 3D miniatures), plus the standard multiplane
literature. Numbers are quoted from those files, not invented.
