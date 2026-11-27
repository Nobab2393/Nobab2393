# stickman-video-director — installed

Source: https://github.com/kaomei/stickman-video-director (MIT)

## Where it lives

| Path | Contents |
|---|---|
| `.claude/skills/directing-stickman-videos/` | the skill: `SKILL.md`, `references/`, `scripts/`, `assets/`, `examples/`, `tests/` |
| `skills-lock.json` | installer lock file (source, hash, copy mode) |
| `.claude/skills/directing-stickman-videos/node_modules/` | `@napi-rs/canvas`, `sharp` (installed, git-ignored) |

Installed with:

```sh
npx skills add /tmp/svd --skill directing-stickman-videos --copy -y -a claude-code
cd .claude/skills/directing-stickman-videos && npm install --no-audit --no-fund
```

## Runtime prerequisites

The skill shells out to `ffmpeg` and `ffprobe` on `PATH`. This sandbox has no
system ffmpeg, so working symlinks are provided in `./bin` (git-ignored):

- `bin/ffmpeg` → imageio-ffmpeg's bundled `ffmpeg-linux-x86_64-v9.0.2` (from `.venv`)
- `bin/ffprobe` → static ffprobe from the `@ffprobe-installer/ffprobe` npm package

Activate before using the skill:

```sh
export PATH="$PWD/bin:$PATH"
```

Status — `node scripts/autopilot.mjs doctor`:

```json
{"node": true, "ffmpeg": true, "ffprobe": true,
 "canvas": true, "sharp": true, "fonts": true, "b4_hook_font": true}
```

`gemini_key_present: false` — only needed for styles that call Gemini for
voice/imagery (A6 etc.); the local Code Engine (B) renderers do not require it.

## Space trimming

The upstream package ships ~490 MB of showcase video (README previews, B4/B5/B6
reference films, the 248 MB SFX/music library). These study-only folders were
removed to keep the workspace portable; all **code, references, scripts, tests,
fonts and the small style showcases** are intact:

```
assets/b-audio-library/audio   assets/b6/reference   assets/b5/local-baselines
assets/b6/hong-kong-v90        assets/b4/public-showcases   assets/b6/paint
```

Re-download them with `git -C <fresh clone> checkout -- skills/directing-stickman-videos/assets`
if a specific style's sample films are needed for comparison.

## Usage

Ask for a style, e.g. "make a B1 Minimal Line Art stickman video about …".
`node scripts/autopilot.mjs workflow --style <B1..B7> --ratio 16:9|9:16` prints
the exact documents and acceptance rules for that style. B7 · Pixel Theater,
B5 · Avatar Explainer and B6 · Meme Story each have dedicated renderers under
`scripts/`; A-styles (A1–A8) deliver prompts/storyboards for a video model
instead of local rendering.

---

## Also installed: MiniMax H3 skill suite

`npx skills add https://github.com/MiniMax-AI/MiniMax-H3 --skill '*' --copy -y -a claude-code`
→ 9 skills (`h3-prompt-writing` + 8 style generators + `directing-stickman-videos`) in `.claude/skills/`.

Study notes, the H3 prompt contract, and why H3 cannot be run locally in this sandbox are in
**`H3_SKILLS_NOTES.md`**; a worked prompt pack is in **`h3-prompts/law5_bangla_h3.md`**.
