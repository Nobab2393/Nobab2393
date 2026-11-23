# Timing charts & velocity-matched seams

## Timing chart, in code

A timing chart is `frame -> where`. Write it as a list of `(frame, value, ease out)` and interpolate:

```python
chart = [(0, 0.0, "hold"), (4, 0.0, "in"), (10, -18, "out"),    # anticipation
         (16, 240, "in"), (22, 300, "out"), (30, 300, "hold")]   # action + hold
```

Rules:
- **Overlapping charts** for connected parts: the head arrives 2 frames after the body, a scarf 3
  frames after the head.
- **A chart's last entry must be a hold**, or the move never lands.
- Keep a chart under ~8 entries; more and you wanted straight-ahead animation instead.

## Velocity-matched seams (cuts that don't stutter)

| Parameter | Value |
|---|---|
| Partial travel across a cut | ~12 % of frame (+-230 px at 1080p) |
| Eases | exit `power4.in`, entry `power4.out` (mirrored) |
| Blur peak at the swap | 10 px text-scale, 18–20 px full-frame |
| Zoom-through | exit `1 -> 1.2` growing, entry `0.75 -> 1` growing |
| Inverse zoom-through | exit `1 -> 0.8` shrinking, entry `1.25 -> 1` shrinking |
| Cut duration | ~0.4 s total (12 frames at 30 fps) |

**Scale-sign rule:** the sign of `d(scale)/dt` must match on both sides. Never answer a push with a
retraction, or a pull with a grow-from-small entrance.

## Waterfall entry (staggered arrival)

| Element | Y offset | Duration | Overlap |
|---|---|---|---|
| Anchor / heavy | 60–80 px | 0.16–0.20 s | 0–2 f gap |
| Normal word | 40–50 px | 0.13–0.16 s | 1 f |
| Light / punctuation | 30–48 px | 0.10–0.13 s | 1–2 f |

- One direction per cascade; gaps **shrink** as the cascade runs; the last element snaps.
- Opacity is binary (set at entry) — never a fade; the velocity is the trick.
- `power4.out` (or `expo.out` for extra snap); never `inOut` on an entrance.

## Nudge curve (group slide, 10/65/25)

| Phase | Ease | Distance | Time |
|---|---|---|---|
| ramp-in | `power3.in` | 10 % | 20 % |
| burst | linear | 65 % | 18 % |
| tail | `power4.out` | 25 % | 62 % |

- Tail >= 3x the ramp-in in *time*. If it still smacks, lengthen the tail, don't shorten the distance.
- Phase 2 stays linear or the burst contrast is lost.
- Reveal new content during phase 2 — the burst masks it.

## Antipatterns

| Don't | Instead |
|---|---|
| Exit easing to a stop, entry starting from zero | Match velocity across the cut |
| 20 px blur on a headline | 10 px on text, 18–20 on full frame |
| Inverse-zoom exit answered by grow-from-small | Match the scale-velocity sign |
| Fading text in | Set it at entry and let it travel |
| Uniform on-2s for everything | Body on 2s, eyes/hands on 1s |
