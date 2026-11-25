# Provenance — directing-stickman-videos

| field | value |
|---|---|
| upstream | `https://github.com/kaomei/stickman-video-director` (MIT) |
| commit | `10287822ba47579321068da1b93801face9160dd` — “Document B8 Greek Mythology samples and routing (#179)”, 2026-11-24 |
| skill path | `skills/directing-stickman-videos/` |
| vendored here | 515 text files, 4.75 MB (`SKILL.md`, `references/`, `scripts/`, `agents/`, `assets/**` manifests, `tests/`, `package.json`, `package-lock.json`) |
| omitted | **all binary media** (554 MB: mp4/png/jpg/wav/ogg/mp3 reference films, samples, contact sheets, fonts) and `assets/b-audio-library/catalog.json` (1.7 MB media index) |
| `SKILL.md` sha256 | `fcbab3e8ec1b96d7…` |
| full local install | `~/.claude/skills/directing-stickman-videos/` — sparse clone, complete with media, `node_modules/` installed |

## Why the repo copy is text-only

A 554 MB vendored skill would blow the repository (and the patchset budget), and the media is
comparison footage — it is not source code. The text layer is what defines the doctrine: the
style catalogue, the per-style contracts, the runtime CLI, the QA gates. Everything needed to
**plan, prompt and grade** a video is here; nothing needed to **watch** a reference film is.

`MEDIA-NOT-INSTALLED.md` lists exactly which media files the references expect and the two
commands that fetch them.

## Verification performed

```
$ node scripts/autopilot.mjs doctor
{ "node": true, "ffmpeg": true, "ffprobe": true, "canvas": true,
  "sharp": true, "fonts": true, "b4_hook_font": true,
  "gemini_key_present": false, "network_checked": false }

$ node scripts/autopilot.mjs workflow --style B1 --ratio 9:16
{ "schema": "b-style-installed-workflow/1", "style": "B1", "ratio": "9:16",
  "status": "guide_only", "quality_verified": false, ... }

$ node scripts/autopilot.mjs init /tmp/b1demo --style B1 --ratio 9:16
{"project":"/tmp/b1demo/project.json","stage":"scaffold; add approved narration,
 aligned captions and authored native scenes before rendering", ...}
```

`ffmpeg` resolves to the ffmpeg bundled with `imageio_ffmpeg` (9.0.2) and `ffprobe` to the
static binary from `ffprobe-static`, both symlinked into `~/.local/bin`. `canvas` and `sharp`
come from `npm install` in the installed skill. `gemini_key_present: false` is the one real
gap: no image/TTS service key is configured here, so **B-mode asset generation** would need
the user's provider, even though encoding works.

## Licence

Upstream is MIT (`LICENSE` in the upstream repo). Files here are unmodified copies. The
distilled layer next door (`../stickman-video-director/`) is my own summary and is not
upstream material.
