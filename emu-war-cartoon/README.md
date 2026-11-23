# The Emu War — cartoon short (9:16, English)

Quiet-Wolf-style talking-animal short: **Professor Hoot (owl)** tells **Remy (raccoon)** about the Great Emu War of 1932 — the war Australia lost to birds.

| File | What it is |
|---|---|
| `emu-war-1932-vertical-1080x1920.mp4` | **Finished video** — 1080×1920, 30fps, 54s, English two-voice dialogue, burned captions, 8.3 MB |
| `01-script-english.md` | Line-by-line script, character lock-sheet, verified facts |
| `frames/` | 6 flat-2D cartoon frames (owl, raccoon, study room, emu field, emu vs army, emu victory) |
| `audio/` | 8 dialogue clips (l1–l8): owl = one voice, raccoon = another |

**How it was built:** each line = its own audio clip + one frame with a slow Ken Burns zoom + a caption burned in with ffmpeg (`drawtext`, DejaVu Sans Bold). Segments concatenated losslessly.

**To extend:** add lines 9+ in `01-script-english.md`, generate the audio, and re-run the builder pattern — the style stays consistent because the frames and voices are locked.

**Style rule that matters:** thick black outlines, muted earthy palette, flat backgrounds, zero gradients — that's what makes it read as the viral "quiet animal" format rather than generic 3D cartoon.
