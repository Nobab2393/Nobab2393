# 3D motion craft — the animation half

## 1. Frame rate and keys

- 3D is animated **on 1s**: 24 or 30 unique values per second. There is no "on-2s" economy unless you
  deliberately hold.
- **Block** on the extremes (3–6 poses per action), **breakdown** the passing positions, then spline.
  If the spacing is wrong, no amount of curve work saves it, and if the curves are wrong, no amount of
  keys saves it either.
- Interpolation by intent: `linear` while blocking (so you see the spacing honestly), `spline` for the
  final pass, `constant` only for mechanical/hold frames.

## 2. Squash and stretch in 3D

Scale the geometry along the path, inverse-scale the other two axes, keep the volume:

```
s_y · s_x · s_z = 1          # a 1.30 stretch on Y needs 0.877 on X and Z
```

| Beat | Scale |
|---|---|
| Anticipation squash | y 0.75, x/z 1.155 |
| Launch stretch | y 1.30, x/z 0.877 |
| Impact squash | y 0.70, x/z 1.195 |
| Settle | ≤ 3 diminishing oscillations, then a moving hold |

Stretch must be **along the travel direction** — on a diagonal path, rotate the object first, or the
stretch reads as the wrong axis.

## 3. Strobing

When an object's positions in consecutive frames **don't overlap**, the eye reads separate images
instead of motion. Two cures:

1. Stretch along the path until the silhouettes overlap (squash/stretch doing double duty).
2. Add sub-frame motion blur (see the shutter rule in `camera-and-light.md`).

A fast action with correct spacing will still strobe if the shapes are small and the frame rate is 24.
That's a physics limit, not a bug.

## 4. Weight

| Cue | Heavy | Light |
|---|---|---|
| Start | slow, with anticipation | instant |
| Arc | low and flat | high and floaty |
| Contact | long, with a squash and a slide | short, one frame |
| Settle | many small oscillations, dies slowly | 1–2 oscillations |
| Secondary | ground dust, screen shake | a tiny follow-through on extremities |

Weight is **entirely** in the spacing. A cannonball model and a balloon model given the same keys read
as the same object.

## 5. Arcs

- In 3D the trajectory is a curve in space — the arc is free, but a spline that eases flattens the arc
  when the speed goes up. Add a breakdown at the fastest point so the bow survives.
- Vertical paths need a bow of 2–6 % of the travel to feel organic (throw, jump, wing).
- Never a straight-line path for anything alive.

## 6. Cycles

| Cycle | Length at 24 fps |
|---|---|
| Idle / breathing | 48–96 f (2–4 s) |
| Walk | 24 f (1 s) per full cycle; contact, down, passing, up ×2 |
| Run | 16 f; with 2–4 f of air time per step |
| Turn in place | 12–20 f |
| Blink | 3–4 f closed; 40–80 f between blinks |
| Head turn | 8–12 f |

- Cycle length must divide the shot length, or the loop pops.
- **Offset the layers**: body, arms, head and props on different phase offsets (1–3 frames), or the
  cycle reads mechanical.

## 7. Holds and moving holds

- A held pose is never frozen: 1–2 px of screen-space drift, a breath every 12–20 f, a weight shift.
- The cheapest "life" in 3D is a **moving hold**: drift 2–4 % toward the next pose across the hold.

## 8. Overlap and drag

- Child parts lag by 1–3 frames; extremities (antennae, hair, cloth corners) by 1–2 more.
- When everything goes down, make something go up — one opposing element stops the whole body reading
  as a single rigid block.
- Detail layer last: add drag on the smallest moving parts only after the main action is approved.

## 9. Camera as animation

Camera moves obey the same principles: anticipation (a tiny counter-push), easing, follow-through
(a settle at the end), and no unmotivated motion. A camera that never stops moving reads as a drone;
a camera that never moves reads as a screenshot.

## 10. Numbers worth memorising

| Thing | Value |
|---|---|
| Bounce flight time | `T = 2·sqrt(2h/g)` — height ratios 0.55 per bounce give a natural decay |
| Impact frames | 2–4 f on the ground, squash on the first |
| Anticipation | 20–30 % of the action's duration |
| Follow-through | 6–12 f to settle, 8–15 % overshoot |
| Micro-hold drift | 1–2 screen px, or 2–4 % of the pose |
| Cycle offset between layers | 1–3 f |
