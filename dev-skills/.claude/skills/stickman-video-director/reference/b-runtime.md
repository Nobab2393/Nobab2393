# B-mode: the local manifest runtime

The runtime is `scripts/autopilot.mjs` inside the installed skill (node ≥ 20, deps `sharp` +
`@napi-rs/canvas`). It renders `project.json` to an MP4 with ffmpeg. It does **not** draw your
story for you: `init` writes an empty manifest on purpose.

## Command surface (verified on this box)

```
workflow --style B1..B6 [--ratio 16:9|9:16] [--project PATH]   read-only plan: docs + references + review templates
doctor                                                          node/ffmpeg/ffprobe/canvas/sharp/fonts checks
probe FILE                                                      media probe
init DIR [--style Bx] [--ratio R]                               empty native manifest
preflight B6_PROJECT --ratio R                                  B6 only
draft B6_PROJECT --ratio R --trusted-code [--draft-scale .5]    B6 only: true low-res draft
captions WORDS OUTPUT [--lead N]                                draft caption grouping from aligned words
validate PROJECT [--seconds N]
preview PROJECT [--seconds N] [--replace]                       encode candidate + extract review template
approve PROJECT --note TEXT [--visual-review REVIEW_JSON]
render PROJECT [--replace]                                      full encode
accept-visual|accept-picture|accept-text PROJECT --review REVIEW_JSON
```

`workflow` is the only read-only entry point and it answers with JSON: which reference documents
apply to that style/ratio, which approved media to compare against, and the exact review-template
paths (`output/preview-reference/review-template.json`, `output/film-reference/…`) whose entries
start as `unknown`. Fill them from real playback only.

## project.json after `init --style B1 --ratio 9:16`

```json
{ "version": 1, "style": "B1", "width": 720, "height": 1280, "fps": 30,
  "voice": { "path": "narration.wav", "lead": 0, "tail": 0 },
  "captions": [], "shots": [], "sfx": [],
  "reference_review": { "author_id": "",
    "capability": { "mode": "sample_target", "environment": "", "limitations": [] } } }
```

Notes that matter:
- 9:16 initialises at 720×1280 for speed; the approved portrait contract is written on the
  1280-wide design plane, so sizes (e.g. 64-unit captions) scale with the plane, not the export.
- `shots[]` is where authored scene code lives; the story, poses and timing are yours.
- `capability.mode: "sample_target"` means you are claiming you will target the style sample.
  If a tool genuinely cannot reach it, record the limitation there and deliver a disclosed
  limited result — never flip it to a pass.

## Shot ledger (plan on paper before any code)

Per shot: spoken phrase + real word times · idea to communicate · focal subject/action/expression ·
short scene text · timed picture events · evidence source/language/date · caption phrase ·
SFX event · connection to the next shot. This is the artifact that makes the 2.5-second and hook
gates checkable instead of vibes.

## Audio

- Voice at native 1× — never stretch speech to fit pictures; move pictures.
- Captions come from the actual recording's word times (`captions` subcommand drafts, a human/
  agent regroups by meaning), one visible line for B1–B4/B6.
- SFX sit on real contacts, below dialogue; a music bed is included **by default**.
- B4 only: fixed Brian narrator, plot-needed secondary roles, its own audio contract.

## Two ratios

B1–B6 must support 16:9 and 9:16. A "both" request shares script/voice/assets, never one
composition: portrait gets its own stage, focal regions, caption band and phone-size review.

## What the runtime cannot do here

No image-generation tool and no TTS key are configured in this sandbox (`doctor` →
`gemini_key_present: false`). The runtime can still validate/render an authored manifest with a
supplied `narration.wav`, but asset generation needs the user's provider. Do not pretend a
template render is a finished film.
