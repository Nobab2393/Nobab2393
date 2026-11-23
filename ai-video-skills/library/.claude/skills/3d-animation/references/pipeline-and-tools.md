# Pipeline & tools

## The order that saves time

```
1  Reference       one real film/still, MEASURED: cuts, moves, lens feel, light direction, pace
2  Shot table      one row per shot: move · subject · fill · motivation · duration
3  Look-dev        stills at start/middle/end of each shot — iterate here, 100x cheaper than frames
4  Motion previz   preview quality, cut together, compared against the reference
5  Blocking        extremes only, linear interpolation, honest spacing
6  Breakdown       passing positions, arcs, overlap
7  Spline          curves, then re-check spacing in the graph editor
8  Light           key / rim / practicals / sweep, one light event per beat
9  Final render    1.5-4 s/frame at 1080p is normal on a GPU
10 Comp            grade, titles (2D, in negative space), sound, QC
```

Two rules that come from doing it badly first:
- **Never render the final before the stills pass.** Look-dev stills catch 80 % of the defects for
  0.5 % of the render cost.
- **Name the weakest shot** and what would fix it while it's still cheap to fix.

## Render budget reality

| Route | Cost | Notes |
|---|---|---|
| GPU path trace / Cycles | 1.5–4 s/frame @1080p | what a product film is budgeted on |
| Eevee / rasterised engine | 0.05–0.3 s/frame | fine for previz, good enough for stylised finals |
| three.js headless | 0.2–1 s/frame | needs Chromium; WebGL on CPU is slow but works |
| numpy software rasteriser | 0.4–0.8 s/frame @1440×2560 | z-buffer + Lambert only; no reflections, no GI |

A 12-second 1080×1920 shot is 360 frames; at 0.7 s/frame that's ~4 minutes — which is exactly what
`3d-demo/build.py` costs in this sandbox.

## Route 1 — Blender (best)

```bash
blender -b -P scene.py            # headless: build, animate, render, save
blender -b file.blend -o //out/#### -F PNG -a
```

- Drive it from a JSON shot spec rather than by hand; then "re-render shot 3 at higher samples" is one
  command.
- Cycles for glass/metal; Eevee for stylised, fast iteration.
- Always render stills of the first/middle/last frame before the animation.

## Route 2 — three.js in a headless browser

- Best for glass, transmission, dispersion, and any look that needs a real renderer without a DCC.
- Build a tiny emissive studio scene instead of an HDRI; re-bake the environment when the sweep moves.
- Needs Chromium/Playwright, which many sandboxes cannot download (allowlisted egress).

## Route 3 — the software rasteriser (this sandbox)

What it does, honestly:

```
vertices -> model matrix (squash, spin) -> look-at view -> perspective project
        -> per-triangle barycentric fill with a z-buffer
        -> flat Lambert + rim per face (facet = the detail)
        -> projected hard shadow on y=0 along the key light
        -> depth fog to the horizon colour
        -> vignette -> 1.44x supersample downscale -> ffmpeg
```

What it cannot do: reflections, refraction/glass, global illumination, area lights, soft shadows,
motion blur, depth of field. Say so instead of pretending a look is "3D rendered" when it's a raster.

Working reference: `3d-demo/build.py` (repo root) — icosphere ball with speed-driven squash, decaying
bounces, orbiting-dolly camera, faceted ground, projected shadows, stars, end card.

## QC pass (before delivery)

1. Contact sheet: one still per beat; the form must read at 360 px.
2. Shadow direction matches the key in every shot.
3. No z-fighting, no seam, no pop on a cut.
4. Motion: are the keys evenly spaced anywhere they shouldn't be?
5. Titles in negative space, never over the subject.
6. Every shot has a move, a subject, a fill and a motivation — or it's a still and should be cut.
7. Say which renderer produced the file, and at what resolution it was really rendered.
