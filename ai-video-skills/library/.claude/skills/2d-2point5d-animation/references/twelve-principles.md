# The principles, as numbers

Each row is the classic principle rewritten as something a renderer can do. Amounts are starting
points measured against shipped work, not laws.

| # | Principle | What to code | Numbers |
|---|---|---|---|
| 1 | **Squash & stretch** | Scale the shape along its motion axis, inversely on the other | Anticipation squash `1.25 × 0.75`, launch stretch `0.80 × 1.30`, impact squash `1.30 × 0.70`; settle ≤ 3 bounces |
| 2 | **Anticipation** | Counter-move before the action | 20–30 % of the action's duration, 8–20 px, ease-in-out |
| 3 | **Staging** | One idea per frame; silhouette must read | Test at 360 px wide; one accent-coloured subject per frame |
| 4 | **Straight-ahead vs pose-to-pose** | Pose-to-pose for acting, straight-ahead for effects | Poses every 6–12 f; effects drawn per frame |
| 5 | **Follow-through & overlapping action** | Damped spring on everything soft | `1 - e^(-6t)·cos(2π·2t)`; 6–12 f to settle; overshoot 8–15 % |
| 6 | **Slow in / slow out** | Ease only the ends of a move; keep the middle fast | `power4.out` for entries, `power3.in` for exits, never `inOut` on an entrance |
| 7 | **Arcs** | Bend every path | Bow = 5–15 % of the chord; the fastest stretch of the arc has the widest spacing |
| 8 | **Secondary action** | A small thing reacting to the main thing | 2–4 frames later, 10–25 % of the main amplitude |
| 9 | **Timing** | Frames, not seconds | Blink 3–4 f; head turn 8–12 f; sit 16–24 f; a "take" 6–10 f |
| 10 | **Exaggeration** | Push the extremes, not the middle | Extremes +25 % on the key pose, holds untouched |
| 11 | **Solid drawing** | Weight, volume, symmetry | Volume constant under squash: `w·h = const` |
| 12 | **Appeal** | One clear, likeable shape language | One silhouette rule: all shapes share a corner radius / line weight |

## Exposure (what a drawing *is*)

- **On-1s** 24 drawings/s — glossy, expensive, needs 24 unique drawings.
- **On-2s** 12 drawings/s — the cartoon default. All body motion keys to `B = floor(F/2)`.
- **On-3s** 8 drawings/s — holds and slow turns; use for a held moment inside an on-2s piece.
- **Mix on purpose:** body on 2s, eyes/hands on 1s, background on 2s. A uniform exposure reads as
  either cheap or fake, depending on which uniform you chose.

## Holds

- A hold is **never frozen**: 1–2 px drift, a breath every 12–20 f, a blink every 40–80 f.
- A **moving hold** (drift toward the next pose) is cheaper than a new key and reads as life.
- Never hold a caption still for more than ~1.25 s without a change; type is the first thing to look
  dead.

## Smears and multiples

- If an object travels more than **its own width in one frame**, draw it stretched along the path
  instead (a smear frame), or draw 3 ghost copies at 30/60/100 % of the travel (a multiple).
- Smears live for exactly one frame. Two frames and it reads as a glitch.
- On-2s pieces can't smear honestly — cut instead.

## Weight

- Heavy things: shorter arcs, harder landings, longer settle, dust.
- Light things: higher arcs, longer float, wind.
- Two objects of different weight must never share an ease curve.
