# Camera & light

## Focal length

| Lens (35 mm equiv.) | Reads as | Use |
|---|---|---|
| 14–18 mm | huge space, strong distortion | architecture, "inside the machine", drama |
| 24 mm | wide, wide-ish distortion at the edges | establishing, an interior with a hero close |
| 35 mm | neutral reportage | the default for motion |
| 50 mm | neutral, close to the eye | dialogue, product in context |
| 85 mm | compression, flattering, thin DOF | hero product reveal, portrait |
| 100–135 mm | tight compression, macro | material proof, rack focus |

Vertical FOV for 9:16 at 1080×1920 is usually **28–40°**; keep it fixed inside a shot and only change
it on a cut.

## Moves (one per shot)

| Move | Parameters | Typical duration |
|---|---|---|
| Dolly in (push) | fill 0.70→0.80 at 85 mm | 3–4 s |
| Dolly out | fill 0.80→0.65 | 3 s |
| Orbit | azimuth −25°→+10°, height +0.05 | 3–4 s |
| Crane | dolly out + target rising | 2–3 s |
| Truck (lateral) | ±40 px of frame at slow pace | 2–3 s |
| Macro slide | 60–100 mm, region = the detail, angle ±3° | 2–3 s |
| Rack focus | focus 0.4 m → 1.2 m at f/2.8 | 2 s |
| Static + light sweep | camera locked, light travels | 2–3 s |

Rules:
- **Match a measured reference.** "Slow" is a measurement, not a mood.
- Ease both ends; hold the middle fast. A fully-eased move reads as a slideshow.
- Total travel for a ~3 s slow shot is small. On a macro region, fill 0.95→0.85 already reads as a 50 %
  zoom.
- Never dolly + pan + tilt in one shot unless the shot *is* a drone.

## Depth of field

- Compute the f-stop **from the camera distance to the subject**, not by taste: a macro at f/3.5 leaves
  ~2 mm sharp. Expose `dof: shallow | medium | deep` and let the rig solve the number.
- Focus sits on the subject's front surface by default; a deliberate rack focus is one move, not a
  drift.
- Far background never bleeds over a sharp foreground.

## Shutter & motion blur

- **180° shutter rule**: shutter angle 180° → shutter time = 1/(2·fps). At 24 fps that's 1/48 s; at
  30 fps, 1/60 s.
- Longer shutter (360°) = smeary, dreamy. Shorter (90°) = crisp, video-game, "gladiator". Pick one per
  project.
- Motion blur is the cheap cure for strobing on fast moves — but it must be consistent across a cut or
  the cut reads as a frame-rate change.

## Lighting a dark stage (the premium default)

- **Black stage, low key.** A soft coloured pool behind the subject, a low key light, rim strips doing
  the modelling, one moving sweep per hero shot. Never a flat bright background.
- **Ratio**: key : fill ~ 4:1 for drama, 2:1 for product clarity, 8:1+ for silhouette work.
- **Rim strip** at equal radiance on close-ups — a *thin* edge line. A thick continuous white outline
  reads as a cut-out sticker.
- **Sweep** energy ≈ 6–10; a bright strip passing between lens and subject washes labels to white, so
  keep it behind or to the side.
- **Practicals** (lamps, screens, emitters) carry the story: one accent colour reserved for light
  itself (emission, caustics, the dispersion edge), never for paint.
- **Fog / haze**: low rolling ground fog (density ~0.3, height ~0.08 m) for atmosphere; never a
  whole-frame grey wash — that's a bad grade wearing a costume.
- **Clear materials need light behind them.** In a dark field, water and glass read as black ink unless
  something bright sits behind or inside.

## Studio builds without an HDRI

Photo-studio HDRIs contain windows and clutter that print as messy streaks on glass. Build a tiny scene
of emissive planes instead: two tall side strips (silhouette), one wide far strip (horizon rim), a soft
top box (volume for frosted glass and metal), a weak front card, and the sweep strip behind the camera
on an arc. Bake to a prefiltered environment map, refresh per frame when the sweep moves.

## Composition for 9:16

- Subject fills ≥ 0.7 of frame height for a hero; a small product in a big black frame is the #1
  failure.
- A subject taller than wide (bottle) still covers little area: crop cap-to-label, go lower and closer,
  or put the title in the empty side.
- More than half the frame empty is only allowed when a title lives there.
- Open with a reveal — the light finding the subject is the most striking image of the film.
