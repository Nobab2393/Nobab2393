# VICE CITY 2D — top-down gameplay

A 30 s gameplay clip, not a trailer: a top-down (GTA-2 style) screen with a real
HUD, one continuous scripted drive through a neon city, a drift, a police chase
and a delivery. Landscape 1920×1080 @ 30 fps, H.264 + AAC, 18.0 MB.

**Deliverable:** `vice-city-2d-gameplay-1920x1080.mp4`

Fan-made, drawn and synthesised entirely in code. No footage, no sprites, no
samples, nothing from the game itself.

| t | beat |
|---|---|
| 0.0–1.9 | title overlay, HUD sliding in, driving north |
| 1.9–15.5 | the long east run: traffic both ways, pedestrians on the kerbs |
| 15.5–18.4 | sweeping left onto the shore road — drift, skid marks, tyre squeal |
| 18.9–24.4 | ★★★ — two cruisers on you, siren, beach on your right |
| 24.4–26.0 | stars drop one at a time as the cruisers fall back |
| 26.0 | you reach the marker: **MISSION PASSED!** + $4,200 |
| 26.0–30.0 | idle at the marker, fade |

## How the drive is built

The car is not keyframed. Three stages, and everything else reads off them:

1. **The route** is a turtle-built polyline (`build_path`): `to(axis, target)` runs
   along the current heading, `corner(sign, R)` sweeps a quarter arc that lands
   exactly on the next road's centreline. 5 888 px, four corners.
2. **Curvature** is measured from the real point spacing (not an assumed step),
   then smoothed. A **speed profile** falls out of it physically: in a corner
   `v = √(a_lat/κ)` with `a_lat = 260 px/s²`, then a braking pass
   (`v_i ≤ √(v_j² + 2·a·Δs)`) makes it slow *before* the corner rather than in it.
3. **Integration**: stepping that profile at 30 fps gives `S[t]`, and a small
   fixed-point loop scales the whole thing until the car arrives at exactly 26.0 s.

So the speedometer (119 km/h cruising, 76 through the drift, 0 at the marker), the
minimap, the slip angle (`v²κ`), the skid marks and the engine pitch all come from
one arc-length table and cannot disagree with each other.

## What is on screen

Top-down world on a 520 px road grid: asphalt bands with lane dashes and
crossings, sidewalks, blocks with four seeded layouts (rooftop slab, split lot with
parked cars, palm court with a lit pool, shop row), neon strips with a three-step
flat bloom, street-lamp pools, and past x=2900 the sand and the sea.

HUD: cash, health/armour, five wanted stars, mission plate with a countdown,
speedometer arc with a digital readout, and a circular minimap that clips the road
grid to the disc and tracks traffic, cruisers and the marker. CRT scanlines and a
flat vignette on top.

Audio (`sound.py`, all numpy): 118 BPM synthwave in A minor (pad, 8th saw bass,
16th arp, kick/snare/hats), an engine drone whose pitch follows the *actual* speed
curve per 256-sample block, band-passed tyre squeal across the drift, a two-tone
siren that dulls as the cruisers drop back, and a four-note cash chime on the
payout. Levels are set in dB per element rather than by ear-by-hope: mix RMS runs
−21 dB intro → −18 cruise → −14 chase → −10 on the payout.

## যা ভুল হয়েছিল

- **`to()` drove backwards.** The turtle moved by the *coordinate difference*, so a
  target behind the heading sent it the wrong way — the car drove south out of
  frame and the polyline doubled back, which is also what produced the 0.04
  curvature spike that pinned the speedometer to 27 km/h in corners.
- **HUD drawn through the camera.** `screen()` reset the camera to 0,0 but the
  transform also adds `W/2`, so the whole HUD sat 960×540 down-right — the cash
  bars were floating in the middle of the road.
- **The road was invisible.** Asphalt, sidewalk, block and building were four
  near-identical purples. Roads are now painted as bands and the building set is
  two stops brighter.
- **The shore had no beach.** Water started at the road edge, and palms stood in
  the traffic. The sea moved out to x=2900 and the sand strip carries the palms.
- **Skid marks were black.** On dark asphalt that read as a trench; they are now
  scuffed violet-grey at 80 % and fade over 8 s.
- **Rooftop clutter made holes.** Small dark rectangles on a flat slab read as
  glitches, so they were removed rather than shaded.

## Files

```
game.py                    renderer + world + HUD (--still / --seg / --join)
sound.py                   the entire soundtrack, reads the speed curve from game.py
preview-contact-sheet.png  12 frames from the encoded file
audio/mix.wav              generated mix (gitignored)
```

Rebuild: `python3 sound.py`, then `python3 game.py --seg 0 450 /tmp/v1.mp4`,
`--seg 450 900 /tmp/v2.mp4`, `--join /tmp/v1.mp4 /tmp/v2.mp4`. ~4m50s on two cores.
