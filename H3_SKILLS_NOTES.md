# MiniMax H3 — installed skills + study notes

Source: https://github.com/MiniMax-AI/MiniMax-H3 (commit `199b7d0`)
Installed: all 9 skills, `--copy -a claude-code`, into `.claude/skills/` (472 KB total — **no model weights**).

```sh
npx skills add https://github.com/MiniMax-AI/MiniMax-H3 --skill '*' --copy -y -a claude-code
npx skills ls          # 10 skills registered (9 × H3 + directing-stickman-videos)
```

---

## 1 · h3-prompt-writing — the one that works here

Actually portable: plain Markdown + two reference guides, **no API calls, no Hub runtime**.
Use it to rewrite any request into an H3-shaped prompt. Two guides:

| Guide | For |
|---|---|
| `references/base-en.txt` (15.7 KB) | T2VA · I2VA · FL2VA · L2VA |
| `references/ref-en.txt` (23.5 KB) | Ref2VA (full-reference) |

### Base modes — final prompt shape

```
<instruction line, only for keyframe modes>

integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

Keyframe instruction lines (must be the very first line, then one blank line):

- **I2VA** — `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
- **FL2VA** — `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
- **L2VA** — same form, `<Picture 1>` lands on the **final** shot at `S.SS`.

### Rules that actually change output quality

- `[Shot 1]` carries **no timestamp**; later shots open with `[Shot 2] At 00:03.500, the camera cuts to …`. Timestamps must strictly increase and stay inside the runtime.
- Camera = **motion type + amplitude + speed**, written as prose inside the sentence:
  `The camera pushes in with small amplitude at slow speed toward the letter.` Vocabulary: Zoom/Push/Pan/Truck/Tilt/Pedestal/Arc/Tracking/Static/Shake/POV/Roll.
- Prefer camera motion over a new shot when only distance or angle changes.
- Speakers get stable IDs `(S1)`, `(S2)`; dialogue is `<d>[Bengali] …</d>` — **verbatim, never translated**. Voiceover: use the exact phrase `says in an off-screen voiceover` and then state the lips stay closed.
- `<scenetrans>` when a line crosses a cut, `<cutoff>` when the video ends mid-line.
- On-screen text goes in English double quotes, verbatim: `a gold banner reading "সুনাম রক্ষা করুন"`.
- `overall_soundscape` = 1–4 sentences of ambience/physical action/non-verbal human sound. **No dialogue, no diegetic music.**
- `non_diegetic_music` = 1–3 sentences on instrumentation, tempo, rhythm, dynamics — no mood words.
- Duration must match the ask: **H3 generates 4–15 s, 24 fps, 32 kHz stereo, shorter side 768 px default** (2K via the H3-Regenerate-2K API).

### Ref2VA — six sections, in this order

`subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → `overall_soundscape` → `non_diegetic_music`

- Labels: `<Subject N>` (reusable visible content), `<Picture N>` (a concrete frame/shot anchor), `<Video N>` (edit source / continuation / whole-video structure), `<Audio N>` (copied or referenced signal). Numbering is per-category and stable across all sections.
- Pictures used only to *define* a character/scene/style are cited **inside** the `<Subject N>` line, not as their own entry.
- `summary` opens with bracketed task types: `[reference generation]`, `[keyframe completion]`, `[video editing]`, `[video continuation]`, `[audio reuse]`, `[audio reference]`, combined with ` + `.
- `retention_analysis` markers — visual: `fully_preserved` / `partially_preserved` / `attribute_transfer` / `weak_reference`; audio: `fully_copy` / `partially_copy` / `reference` / `weak_reference`. Never put `(Sx)` in this section.
- `detailed_description` ≈ 350–500 words, style established in 1–2 sentences **before** `[Shot 1]`.
- Limits: ≤ 9 images, ≤ 3 video clips (2–15 s each, ≤ 15 s total), ≤ 3 audio clips, ≤ 12 files overall.

---

## 2 · The eight style skills — planning works, generation needs MiniMax Hub

All eight declare `compatibility: Requires the MiniMax Hub agent (canvas workspace, choice cards, hub_generate_image / hub_generate_video / hub_generate_image / hub_synthesize_speech …)`. **They are not portable** — but their direction, templates and checklists are usable as writing frameworks, and I can pair them with the skill I *can* run (stickman renderer) or with H3 prompts.

| Skill | Default look | Workflow | Use for |
|---|---|---|---|
| `3d-animation-short-generator` | Pixar-style 3D, 2.5–3 head-tall, Octane look | 8 steps: brief → 8-beat outline → character cards → environment-only scene cards → **6-column shot table with per-second directives** → self-check gate → text storyboard doc (pencil opt-in) → H3 (default) / Seedance 2.0 (fallback) per shot → assembly + BGM | narrative 3D shorts, 30–90 s |
| `minimalist-product-ad-generator` | Apple-style white-tech / dark rim light | 10 steps: start gate → 3 anchor photos + beat-synced **typography** → H3 clip → music-2.6 BGM → delivery check | e-commerce, 5/10/15 s, product in hand |
| `music-video-subtitle-generator` | lyric typography as a designed layer | 9 steps: format lock → music window → creative contract → **Natural Stitching Protocol** for >15 s → prompt template → canvas delivery | MVs, 卡点 cuts, subtitle-as-art |
| `papercraft-stop-motion-explainer` | layered paper diorama, stop-motion | 19 steps: style DNA → 3–5 directions → paper characters → sets → **layered diorama staging** → 5 s I2V prompts → storyboard → camera/transition/sound → negative prompts → checklist | science/knowledge explainers |
| `paper-collage-explainer-generator` | halftone collage, tactile SFX, no music by default | 8 steps: parse → plan gate → still spec → **Gate 2 still approval** → stop-motion assembly → SFX clips → review → optional assemble | abstract ideas, 4 s beats |
| `brand-promo-video-generator` | any; brand-truth driven | 10 steps: assets → **brand truth sheet** → **provenance manifest** → story spine → beats → motion language → hard confirm → generate → verify → deliver | launches, apps, sites |
| `co-op-game-intro-generator` | fixed menu framework | 7 steps: style → player names/title → confirmation-image template → approval → H3 video template → repair | 2-player game menus |
| `handdrawn-live-video-generator` | glowing crayon/chalk drawn-on-live-action | 5 steps: contact → morph → escape → delayed chase; **prompt in the user's own language** | 15 s single-scene surreal clips |

Recurring quality rules across all eight (worth reusing even without Hub):

1. Lock **character cards** and **environment-only scene cards** before any shot is generated; scene cards must contain no people.
2. Shot tables get `Continuity Handoff` + `Reference Anchors` (fixed landmarks, character positions, exited-character status, lighting baseline) + per-second directives covering action, camera, position, audio, handoff.
3. Approve stills before spending on video; never silently assemble drifted clips.
4. Duck BGM under dialogue/SFX; no subtitles unless asked; no storyboard labels in the final render.

---

## 3 · Can H3 actually run in this sandbox? No — and here is exactly why

| Requirement | Sandbox |
|---|---|
| NVIDIA GPU, `sglang serve --num-gpus 4 --ulysses-degree 4`; H3-Base is a **33 B** omni-transformer (hidden 5376, 50 layers, 56 heads) + Qwen3-VL text encoder + visual + audio VAEs | **no GPU**, 2 vCPU, 3.9 GB RAM |
| Checkpoint download from `huggingface.co` | outbound hosts are GitHub / npm / PyPI only |
| `torch>=2.4`, `diffusers @ git+…f53d552`, `transformers>=4.57` | possible to install, but useless without weights or a GPU |

So: **prompt generation ✅, local inference ❌.** Realistically H3 is reached one of two ways —
the official API (`platform.minimax.io`, `video-generation-v2-create`, needs the user's key) or the
**MiniMax Hub** canvas, which is what the eight style skills target.

Demonstration of the portable half: `h3-prompts/law5_bangla_h3.md` rewrites the Law 5 concept into
a legal T2VA prompt and a Ref2VA prompt that uses the existing `images/*.png` character art.
