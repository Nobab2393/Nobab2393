# The multiplane (2.5D) rig

## The model

A plane sits at depth `z` from the camera. Its **depth weight** is `w = 1/z`. Everything else follows:

```
scale on a push-in     s  = 1 + A * w            A ~ 0.5 for a 10 % push
lateral drift (truck)     = pan * k * w          k ~ 6 (tuned so fg drifts ~3x the far plane)
vertical drift (tilt)     = tilt * k * w
```

Reference numbers for one push-in over three planes (`z = 10 / 5.5 / 3.5` -> `w = 0.10 / 0.18 / 0.29`):

| Plane | Scale at end | Lateral drift (pan 40 px) |
|---|---|---|
| far (w 0.10) | 1.05 | 24 px |
| mid (w 0.18) | 1.09 | 43 px |
| foreground (w 0.29) | 1.14 | 70 px |

If your far and foreground scales come out within 2 % of each other, the shot will read flat no matter
what else you do — fix the depth weights first.

## Layer budget

| Scene | Planes | Notes |
|---|---|---|
| Graphic / type | 3 | far, mid, foreground; often only for parallax during a push |
| Interior or still-life | 5–8 | walls, furniture, props, hero, dust |
| Landscape | 8–12 | sky, two ranges, haze, ridge, trees, ground, foreground frame |
| Rich establishing shot | 20–100 | needs real paint-out work per plane |

## Paint-out — the thing that kills 2.5D

Cutting an object out of a photo leaves a hole that the camera will reveal. For every plane you must
**repaint the region the camera can see into**. Budget this as the majority of the work, not the
animation.

For vector work this mostly disappears: redraw the hidden part rather than cutting.

## Overscan & seams

- Draw every plane **5–10 % larger than frame**, extending past all four edges.
- **Feathered plates:** separate layers by horizontal bands with ~100 px alpha ramps, so at rest the
  photo is pixel-perfect and the feather hides the seam while drifting. Feathered bands forgive about
  **25 px** of travel; past that, cut real object masks.
- **Vector art:** don't feather — overscan and use hard edges; a visible feather reads as a mistake.
- Audit both ends of the camera move: scrub to the extremes and look at all four edges for a gap.

## Camera

- One move per shot: **dolly** (Z), **truck** (X), **tilt** (Y). Never all three.
- A dolly under ~10 % scale change is invisible-but-felt; above ~20 % flat art starts to shear
  (billboard distortion).
- Keep the subject on the same screen point during the move — pin the hero and let the background
  travel. A push "about a point" drops the subject under the caption.
- Ease the ends, hold the middle fast: `power4.out` in, `power3.in` out; a linear middle reads as a
  real dolly, an eased-everywhere move reads as a slideshow.

## Depth of field

- Blur increases toward the camera when focus is far, and vice versa; far planes **never** bleed over
  a sharp foreground.
- Keep the focus band on the subject for the whole move, or rack focus deliberately once.

## Failure list

1. Every layer moving at one rate -> flat.
2. Seam exposure at the extreme of the move -> 10 % overscan, then re-audit.
3. Camera arc too wide -> the flat art shears; keep it conservative.
4. Dolly + pan + tilt together -> drone footage, not animation.
5. Haze or gradient used to fake depth instead of value separation -> put the value difference into the
   flat colours of the planes.
6. Never showing the split, then expecting the audience to feel the depth -> show it once, then use it.
