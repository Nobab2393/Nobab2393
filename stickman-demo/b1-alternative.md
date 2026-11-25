# The same story in B1 (local runtime) — plan only

If this were produced with **B · Code Engine** instead of a video model, the shape changes:
B renders the film locally from an authored manifest, so the drawings, poses and timing are code,
and narration/captions/SFX are files.

## Verified commands on this box

```sh
S=~/.claude/skills/directing-stickman-videos/scripts/autopilot.mjs
export PATH="$HOME/.local/bin:$PATH"          # ffmpeg + ffprobe

node $S doctor                                 # node/ffmpeg/ffprobe/canvas/sharp/fonts → all true
node $S workflow --style B1 --ratio 9:16       # says which references + review templates apply
node $S init ./b1-project --style B1 --ratio 9:16
node $S captions words.json captions.json --lead 0.2
node $S validate ./b1-project --seconds 30
node $S preview  ./b1-project --seconds 10     # candidate + review-template.json (all "unknown")
node $S render   ./b1-project
```

`init` produced exactly this, and nothing about the story:

```json
{ "version": 1, "style": "B1", "width": 720, "height": 1280, "fps": 30,
  "voice": { "path": "narration.wav", "lead": 0, "tail": 0 },
  "captions": [], "shots": [], "sfx": [],
  "reference_review": { "author_id": "",
    "capability": { "mode": "sample_target", "environment": "", "limitations": [] } } }
```

## Shot ledger for the B1 version

| # | spoken phrase (Bangla) | focal action | scene text | notes |
|---|---|---|---|---|
| 1 | সে কাঁপছিল। | figure A hands a line to figure B; B's shoulders tremble | — | hands genuinely touch; feet planted |
| 2 | আমি দিলাম। | the line leaves A's hand entirely | — | negative space left of A |
| 3 | কিন্তু একটা হিসাব মনে রেখে দিলাম। | A's palm closes; a small knot is drawn in ink | হিসাব | first handwritten word, larger than caption |
| 4 | বছর গেল। | three quick time cuts, same framing, snow/dust marks accumulate | বছর | B1 portrait contract: safe area checked per shot |
| 5 | দানটা তার কাছে গল্প হলো। | the line, off-frame, is drawn as a flat marker stroke | গল্প | |
| 6 | আমার কাছে হলো দেনা। | the same stroke is redrawn heavier across A's wrist | দেনা | the heaviest line in the film |
| 7 | যে দান ফেরত চাই, সেটা দান নয়। | A tugs; the stroke snaps taut and drags him one step | — | |
| 8 | গিঁটটা খুলে দিলাম — | knot loosens in three drawn states | — | |
| 9 | দড়িটাই তখন হালকা হলো। | the heavy stroke reverts to a fine line and exits frame | সেটা দান নয়। | final hold, 1.5 s |

B1 specifics that differ from the A1 prompts: near-white paper `#FDFDFC` with the faint 64 px
grid, **fine irregular pen** rather than uniform line weight, 4–4.5 head proportions, handwritten
scene words above a quieter 64-unit single-line caption, and per-shot safe-area declarations under
`b1-b2-b3-native-portrait.md`.

## What blocks a real B1 render here

- `doctor` reports **`gemini_key_present: false`** — no image/TTS provider. A B1 film needs
  narration audio and authored artwork; this box has neither service.
- The approved B1 comparison media is not in the repo copy (`MEDIA-NOT-INSTALLED.md`), so the
  reference-effect gate would be **PENDING** even if a render existed.

So this stays a plan. Writing a manifest and calling it a film would be exactly the failure the
skill's gates are built to catch.
