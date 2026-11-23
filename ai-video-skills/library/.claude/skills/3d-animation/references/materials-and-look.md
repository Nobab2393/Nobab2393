# Materials, shading & post

## PBR starting points

| Surface | Values |
|---|---|
| Clear glass | transmission 1 · roughness 0.015 · IOR 1.5 · thickness sets lensing · dispersion on (three.js r163+) · double-sided |
| Frosted glass | transmission 0.85 · roughness 0.4 · milky tint · thick · **needs light behind or inside** |
| Chrome | metalness 1 · roughness ≥ 0.14 |
| Brushed metal | metalness 1 · roughness 0.25–0.4 with a roughness map along the brush direction |
| Satin plastic | metalness 0 · roughness 0.35–0.5 |
| Matte plastic / clay | metalness 0 · roughness 0.8–0.95 |
| Low-poly flat | `flatShading: true` · roughness ~0.9 · **no textures at all** |
| Painted metal | metalness 0.6–0.8 · roughness 0.3 · clearcoat 0.2 |

- **Anything inside transmissive glass must be opaque** — only opaque objects reach the transmission
  buffer.
- Model in real units (mm/m). Near plane 1 mm for product macro.

## Flat-shaded low-poly

The whole look is three tones per material and hard edges:

- Top face brightest; sun-facing sides keep the base colour; faces turned away ×0.5–0.95.
- **No smooth normals, no textures.** Jitter each tile's lightness a few percent so the ground isn't a
  spreadsheet.
- Hard shadows, tinted toward the sky colour (e.g. base × (0.70, 0.58, 0.90) for a cool shadow).
- Ambient occlusion draws the seams: render GTAO/AO, or paint a dark line where tiles meet.
- Facets *are* the detail — if a surface has no visible facet change, it's the wrong surface for this
  look.
- A screen-space outline pass (from normals + depth), ~2 px, gives the illustrated read. Skip the
  outline on thin objects and particles, or it becomes an ink scribble.

## Post chain (in order)

```
render 2x supersampled
  -> depth of field (physical, from scene depth)
  -> bloom (threshold ~1.1, never "add glow")
  -> AO/GTAO if not baked
  -> outline pass (optional, flat looks)
  -> grade + tone map
  -> vignette / grain (light)
  -> downscale
```

- **Tone mapping is a look decision.** AgX desaturates and washes accents toward white; Neutral keeps
  them punchy; Filmic lifts the midtones. Choose before lighting.
- **Grain**: 0 for product and graphic looks, 0.02–0.05 for filmic ones. Grain over flat colour bands
  reads as compression, not texture.
- **No horizon line** in a dark stage: the floor fades into the background.

## Colour logic

- Neutral world (black, greys, whites of reflections) + **one accent colour family reserved for light**:
  emission, caustics, the dispersion edge. Pick it from what the subject does, never from a brand.
- Dispersion rainbows only at thick glass edges and in caustics — never as a gradient on a surface or
  type.
- Emitters that only illuminate stay dim and neutral; emitters that *are* the subject carry the accent.
- Time of day = a keyframed set of colours (zenith, horizon, sun colour, intensity, elevation). Pick 3
  keys (day / dusk / night) and interpolate; don't grade a single still.

## Common material failures

1. Clear glass in a dark field with nothing behind it → reads as black plastic.
2. Bloom used as "premium" → everything glows, nothing reads.
3. Perfectly uniform roughness → surfaces look like untextured plastic.
4. Accent colour painted onto geometry *and* used for emission → the accent loses its meaning.
5. Smooth shading on low-poly geometry → plastic blobs instead of facets.
6. 1× render with no AA → stair-stepped edges everywhere; 2× supersample is the floor.
