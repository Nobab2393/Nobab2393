# Motion Grammar — the math behind the "Claude animation" feel

All values in frames at 30 fps unless stated. Port these verbatim into PIL/OpenCV, GSAP or CSS — the
curve is the style.

## Easing

| Name | Curve | Use |
|---|---|---|
| `overshoot` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | every entrance; settle ≤ 12 f |
| `snap` | `cubic-bezier(0.2, 0, 0, 1)` | exits, wipes, cut helpers |
| `keynote` | `cubic-bezier(.16, 1, .3, 1)` | one slow premium move per piece, 30–45 f |
| `spring` | closed-form damped spring | anything that should feel physical |
| `linear` | `t` | line drawing at constant pen speed |

```python
import math
def ease_out_back(t, s=1.70158):      # ~ cubic-bezier(0.34,1.56,0.64,1)
    t = min(max(t, 0.0), 1.0) - 1.0
    return t*t*((s + 1)*t + s) + 1.0
def ease_in_out(t):                   # snap, softened at both ends
    t = min(max(t, 0.0), 1.0); return 3*t*t - 2*t*t*t
def ease_out_expo(t):
    t = min(max(t, 0.0), 1.0); return 1.0 if t >= 1 else 1 - 2**(-10*t)
def spring(t, freq=2.0, damp=6.0):    # closed form, no iteration
    t = min(max(t, 0.0), 1.0)
    return 1 - math.exp(-damp*t)*math.cos(2*math.pi*freq*t)
```

`ease_out_back` overshoots ~10 % — that is the "confident" in the look. Never overshoot a caption;
overshoot shapes only.

## Stagger

- Group of N: `delay_i = i * (2..4) f`, and shrink the stagger as N grows (`4 - N/8`).
- The last element must finish **at least 8 f** before the beat, so the frame reads still before it cuts.

## Transitions

1. **Element-carried** (default): a shape's scale/position sweep grows until it fills the frame, then
   the next scene is drawn *inside* it. Never cross-dissolve.
2. **Morph**: old world's object → new world's counterpart, 18–30 f, eased in-out, anchor the
   silhouette's centroid so the eye holds one point.
3. **Wipe**: hard edge, 6–10 f, always in the direction of the camera's travel.
4. **Cut**: on a drum hit. Silence before the payoff, loudest on the payoff.

## Camera

- A 2D matrix (centre, scale, rotation) applied to the *drawing*, never a scaled bitmap: push in and
  lines thicken but stay crisp.
- One camera move per piece is enough. Push-in of 4–8 % over a scene reads as "expensive" because the
  frame edges never breathe.

## Boil (hand-drawn looks only)

- Re-roll the wobble phase every 2 frames from a per-element seed; keep the *seed* fixed so the same
  stroke is the same stroke.
- Amplitude: ±0.5–1 px at 1080p for a fineliner, ±2 px for crayon. More reads as noise, less as static.
- Never boil text more than ±0.3 px, and never boil the giant number at all.

## Sound and the picture (if scored)

- Cuts on the beat grid; the payoff lands on the loudest hit; add 6–10 f of near-silence before it.
- One sustained pad sets a section's loudness, not the plucks — mix to phone speakers at −14 LUFS.

## Loop

- The last 6–10 f should already be the first frame's composition (or an exact return). A loop cut on
  the same beat the piece opened on is invisible; a fade to black is a hole.
