---
name: 3d-animation
description: Make 3D animation — geometry, light and motion — with real numbers. Squash and stretch on scaled geometry, weight through spacing, arcs on the path, one eased camera move, focal lengths and depth of field that mean something, PBR values for glass/metal/plastic, flat-shaded low-poly and dark-stage product looks, and a pipeline that survives a GPU-less sandbox (software rasteriser, three.js, or Blender CLI). Use for "3D animation", "3D product film", "low-poly", "render this in 3D", "make it look rendered", or any shot that needs a camera in a volume.
---

# 3D Animation

3D is three separable crafts, and they fail in this order: **geometry** (does the form read),
**light** (does the surface read), **motion** (does the weight read). A shot can survive weak
geometry with great light; it never survives motion that ignores mass.

The trap is thinking a renderer is the skill. It isn't. A path-traced frame with linear keys and a
95 mm lens pointed at nothing reads as a screensaver.

## 1. Motion — the part that is animation, not rendering

3D is animated **on 1s** (a new value every frame), so there is no drawing economy to hide behind:
timing is entirely in the spacing between keys.

| Idea | Number |
|---|---|
| Squash & stretch | Scale along the path, inverse on the other two axes so **volume stays constant**: `s_y · s_x · s_z = 1`. Landing `s_y 0.70 / s_xy 1.20`; launch `s_y 1.30 / s_xy 0.88` |
| Strobing | When something moves more than its own width per frame, its positions stop overlapping and the eye sees separate images. Fix by **stretching along the path** until they overlap again |
| Arcs | In 3D the path curve *is* the arc — but a spline that eases also **flattens** the arc at speed. Add breakdowns on fast moves so the bow survives |
| Weight | Heavier = slower start, slower stop, shorter arc, longer settle. Nothing else about the model changes it |
| Contact | Ground contact is short and precise: 2–4 frames for a small object, an impact squash on the first contact frame |
| Holds | A held pose is a **moving hold**: 1–2 cm of drift, a breath, 12–20 frames between micro-moves |
| Overlap | Child parts lag the body by 1–3 frames; extremities drag a further 1–2 |
| Keys | Block on extremes only, then breakdown, then spline. Never spline before the spacing is right |

Full table with settling curves, walk/run cycle counts and the "volume constant" algebra:
`references/motion-craft.md`.

## 2. Camera — lens, move, fill

One move per shot, named in the plan, with a *motivation*. Premium 3D moves slowly.

| Move | Spec | Use |
|---|---|---|
| Hero reveal | `dolly_in`, fill 0.70→0.80, **85 mm**, light sweep | opening / closing |
| Macro slide | 60–100 mm, fill 0.90→0.92, angle ±3° | material proof |
| Orbit | azimuth −25°→+10°, fill 0.70→0.75, height rising slightly | reveal the form |
| Crane | dolly out + target rising | scale |
| Rack focus | 100 mm, f/2.8, focus 0.4 m → 1.2 m | foreground → subject |
| Static + sweep | camera locked, a light moves | a text beat that stays alive |

- **Depth of field by depth, not f-number.** Compute the f-stop from camera distance; a macro at f/3.5
  leaves ~2 mm sharp, which is unusable. Focus on the subject's front surface.
- A dolly under ~10 % scale change is invisible-but-felt; above ~20 % flat-ish art shears.
- Titles are 2D in negative space: 0.06–0.09 of frame height for a headline, never over the subject.
- Focal lengths: 18–24 mm = space and drama (distortion), 35–50 mm = neutral, 85–100+ mm = compression
  and product glamour, and a shallower-looking background for the same f-stop.

Lens/DOF/shutter tables and the 180° shutter rule: `references/camera-and-light.md`.

## 3. Light & material

- **Light is the subject.** A dark stage with a rim strip and one moving sweep beats a bright flat
  background every time. Key low, rims model the silhouette, one sweep per hero shot.
- **Every surface needs a reason to catch light**: roughness variation, an edge, a facet.
- **Physically-based starting points** — glass: transmission 1, roughness ~0.015, IOR 1.5, dispersion
  on; frosted glass transmission ~0.85, roughness ~0.4, and something bright behind or inside it or it
  reads as grey plastic; chrome roughness ≥ 0.14; satin plastic roughness 0.35–0.5; low-poly flat
  shading roughness ~0.9 with no textures at all.
- **Tone mapping is a look decision.** AgX washes saturated accents toward white; Neutral keeps them.
  Pick before you light, not after.
- **Bloom threshold ~1.1**, not "add glow". 2× supersample before any post.
- **Flat-shaded low-poly** lives or dies on three tones per material: top brightest, lit sides base,
  away sides ×0.5–0.95, hard edges, no smooth normals.

Material and post numbers: `references/materials-and-look.md`.

## 4. Pipeline

```
0  Reference      one real film or still, measured (cuts, moves, light direction)
1  Previz        shot table: move, subject, fill, motivation, duration
2  Look-dev      3 stills per shot (start / middle / end) — iterate HERE, it's 100× cheaper
3  Motion previz a rough cut at preview quality, compared against the reference
4  Animation     block → breakdown → spline; arcs and spacing checked in the graph editor
5  Light          key / rim / practicals / sweep; one light change per beat at most
6  Render        final quality; 1.5–4 s/frame at 1080p on a GPU is normal
7  Comp & QC     contact sheet, phone-size read, the 9 checks
```

## 5. When there is no DCC in the sandbox

Three honest routes, in order of fidelity:

1. **Blender CLI** (`blender -b -P script.py`) if it's installed — the real thing, headless, GPU or CPU.
2. **three.js / WebGL** in a headless browser — needs Chromium, which many sandboxes can't download.
3. **A software rasteriser** (numpy + PIL): model/view/projection → z-buffer → Lambert + rim → fog →
   projected hard shadow → ffmpeg. No reflections, no GI, no motion blur, but it renders real geometry
   with real perspective and real light, and it is fast enough for 12 s at 1080p.
   Working code: `3d-demo/build.py` at the repo root (12 s in 4 m 15 s, 1.44× supersample).

Be explicit about which route you used. A rasteriser is not a renderer with a denoiser, and a shot that
needs glass refraction or soft GI cannot be faked in one.

## 6. QC

1. Does the form read at 360 px wide, in silhouette?
2. Does the light have a direction, and does the shadow agree with it?
3. Is there exactly one accent (if any), and is it a *material* or a *light*, not a paint colour?
4. Does every shot move (camera, subject, or light) — no dead stills?
5. Is the subject filling the frame (≥ 0.7 of height for a hero)?
6. Does the motion carry weight — or are the keys evenly spaced?
7. Do close-ups hold up, or is the texture a blur?
8. Any seam, pop, or z-fight in the geometry?
9. Do the titles sit in negative space, and are they outside the subject?

## Files

```
SKILL.md                        this router
references/motion-craft.md      weight, squash, arcs, cycles, holds — the animation half
references/camera-and-light.md  lenses, moves, DOF, shutter, 3-point, sweeps, stage builds
references/materials-and-look.md PBR numbers, flat-shaded low-poly, glass, post & tone mapping
references/pipeline-and-tools.md previz→final, render budgets, the three sandbox routes
```

Provenance: `edenfunf/reelmimic` (`blender-product-film` — the camera-move table and premium-stage
rules), `lemomo-ai/lemo-opuscar` (`glass-product`, `lowpoly-island`, `memphis-diorama` — material and
render specs), plus the standard animation literature for timing and spacing. Numbers are quoted, not
invented.
