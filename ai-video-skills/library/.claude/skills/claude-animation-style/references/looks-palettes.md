# Looks & Palettes

Each look = ground + ink + 3 tones + one accent. Hexes are starting points, keep the *relationships*.

## 1. Flat vector (the default "Claude" look)

- Ground `#F0EEE6` · Card `#FAF9F5` · Ink `#191919` · Grey `#B8B4AA` · Accent `#D97757`
- Shapes flat, no outline or a 3 px ink outline, generous negative space, grid-aligned layout.
- Motion: overshoot entrances, shape morphs, squash-and-stretch on moving objects.
- Pitfall: too many shapes. Cap a beat at **5 elements**.

## 2. Single line / live drawing

- Ground `#FAF9F5` · Line `#191919` · One flood fill `#D97757`
- Constant stroke width, round caps, linear drawing at ~800 px/s.
- One fill moment only, on a downbeat. Camera pans to keep the pen tip in the middle third.

## 3. Isometric miniature

- Ground `#EFEDE6` · Top `#FFFFFF`-ish tint · Left mid · Right dark (three tones **per material**).
- True isometric (30°), camera slides only, objects drop 40 px and bounce with a 3 f stagger.
- Open things to reveal their insides instead of cutting away.

## 4. Dark tech keynote

- Ground `#0E0E10` · Ink `#F5F3EE` · Accent `#D97757` or `#6A9BCC` (never both) · Meta `#8A8A8F`
- Long-tail eases, one giant number at 30 % of frame height, light sweep as the only gradient.
- Grain ≤ 3 % and visible only in a still, or it fights the type.

## 5. Watercolour & ink

- Paper `#F4F0E6` · Ink `#232323` · Washes `#C97B5A`, `#7C93A8`, `#9AA576`
- Washes reveal over 15–25 f and bleed 4–8 px past the line; linework re-randomises 12×/s from a seed.
- Pure white and pure black never appear.

## 6. Era texture

- **1920s film:** sepia `#C9B79C` grade, gate weave 1 px, 5 % flicker, heavy vignette, no audio-synced
  grain change (grain seeded by frame index).
- **1980s VHS:** chroma shift 2–3 px, scanlines, tracking wobble on cuts, saturated bloom.
- **1990s camcorder:** timestamp in the corner, soft focus, hand-held drift.
- Rule: the texture sits **on top of** a clear composition; it is never the composition.

## 7. Paper collage / mid-century toon

- Cream `#F1E9D8` · Ink `#20201E` · Coral / mustard / turquoise: `#D97757`, `#D9A03C`, `#4E8E8A`
- Off-register fills: colour offset a few px down-right from the line, jittering ±1–2 px on 2s.
- Layers step like stop-motion; every layer casts a tight soft shadow on the one below.

## Type stacks

- Heavy grotesk: Inter Tight / Inter / Poppins (SIL OFL, safe to embed).
- Mono meta: JetBrains Mono. Editorial serif (for the watercolour look): Lora.
- Sizes at 1080×1920: giant number 380–520 px · title 110–140 px · caption 72–88 px · meta 28–34 px.
