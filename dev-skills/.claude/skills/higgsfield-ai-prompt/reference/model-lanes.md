# Model lanes — what to pick, and what to verify first

Snapshot: upstream `model-guide.md` + `specs/model-specs.yaml`, `models_explore` snapshot
**2026-09-26**, skill version **3.42.0**. Anything older than ~30 days should be re-verified
(`Higgsfield:models_explore`, or `higgsfield model get <id>` in the CLI) before it goes into a
paid generation. **Do not hand-edit these numbers into a prompt** — the enum is the source.

## Video

| Model | Duration | Aspect | Res | Audio | Use it for |
|---|---|---|---|---|---|
| **Kling 3.0** | 3–15 s | 16:9 · 9:16 · 1:1 | `mode` std/pro/4k | ✅ | cinematic character drama, native audio, multi-shot |
| Kling 3.0 Turbo | 3–15 s | 16:9 · 9:16 · 1:1 | 720/1080p | ✅ | budget Kling, first-frame animation |
| Kling 3.0 Motion Control | 3–30 s | — | — | optional | motion transfer from a reference video |
| Kling 3.0 Omni / Omni Edit | 3–15 s / 3–10 s in | — | — | ✅ | video clone, storyboard, edit-at-3.0 — **not in API catalog (UI only, unverified)** |
| **Seedance 2.5** | 4–30 s | auto · 21:9 · 16:9 · 4:3 · 1:1 · 3:4 · 9:16 | 480/720/1080p | ✅ | omni-reference (≤30 images), long takes |
| Seedance 2.0 (+ Fast / Mini) | 4–15 s | same set | up to 4k | ✅ | 12-asset multimodal, physics |
| **Wan 2.7** | 2–15 s | 16:9 · 9:16 · 1:1 · 4:3 · 3:4 | 720/1080p | ✅ | 60 fps, strongest style range, first+last frame |
| Wan 2.6 | 5/10/15 s | 16:9 · 9:16 · 1:1 | — | ❌ | artistic / stylised, better physics |
| **Veo 3.1** (+ Fast / Lite) | 4/6/8 s | 16:9 · 9:16 | 1080p–4k | ✅ | reference images, first/last frame, extension, prompt adherence |
| Veo 3 | 4–8 s | 16:9 · 9:16 | — | ✅ | nature, environment, stable |
| **Minimax Hailuo 2.3** (+ Fast) | 6/10 s | — | 512/768/1080 | ❌ | VFX, fluid motion, anime, physics |
| MiniMax H3 / H3 Max | 4–15 s / 5–15 s | incl. 21:9 | 2K / 480–768p | — | keyframes, image/video/audio refs, `batch_size` 1–4 |
| FLUX 3 Video | 5–20 s | auto · 21:9 · 2:1 · 16:9 · 4:3 · 1:1 · 3:4 · 9:16 | 720/1080p | ✅ | multi-frame I2V, video continuation |
| Higgsfield DoP (Lite/Std/Turbo) | 3–5 s | — | — | ❌ | I2V specialist, 50+ camera presets, optical physics |
| Grok Video / 1.5 | 1–15 s / 2–15 s | 16:9 · 9:16 · 1:1 | up to 1080p | ✅ | animate stills, social clips |
| Gemini Omni Flash (+1.1) | 4–10 s / 3–10 s | 16:9 · 9:16 | up to 4k | ✅ | reference-driven video, edit mode |

**Retired / do not recommend:** Sora 2 (API shut down 2026-09-24), Kling 2.1 Master (removed),
`Kling 2.5 Turbo`, `Wan 2.5 / 2.5 Fast`, `Kling O1 Video` — legacy or absent from the API
catalog. Say plainly that a UI-only model cannot be called from the API.

## Image

| Model | Use it for |
|---|---|
| **Soul 2.0 / Soul Cinema Preview / Soul Cast** | photoreal characters, identity lock (Soul ID), AI actors |
| Nano Banana Pro / 2 | reference-sheet edits, multi-image consistency |
| Seedream 5.0 Pro / Lite / Flash, 4.5 | high-detail stills, product, poster type |
| GPT Image 2.0 / 2.5 | layout-aware images, text rendering, ad comps |
| FLUX 2 / Kontext | style transfer, inpainting, precise edits |
| Kling Image 3.0 / Omni | Kling-native stills (UI-only, unverified in catalog) |

## Routing shortcuts

| The shot needs… | Pick | Because |
|---|---|---|
| a face to hold for 8 s with dialogue | Kling 3.0 | character consistency + native audio |
| one unbroken 20 s move | Seedance 2.5 | 4–30 s, omni-reference keeps the plate consistent |
| water, cloth, hair, impact | Minimax Hailuo 2.3 | fluid/particle physics |
| a specific colour-grade look | Wan 2.7 | widest style range at 60 fps |
| a still I already like, animated 3–5 s | DoP | preset library written for I2V |
| the same character in 12 shots | Soul ID → then Kling/DoP | identity lock happens before motion |
| cheap exploration before a paid take | any `* Fast` | same family, ~half cost |

## Cost & preflight

Before a high-cost or video-class generation, surface the two-step preflight: **schema first**
(`model get` / `models_explore` for enums and durations), **then** the credit estimate. Credit
costs in `model-guide.md` § Credit Cost Reference are approximations — treat them as order of
magnitude, not quotes.
