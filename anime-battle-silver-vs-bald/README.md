# SILVER vs BALD — 2-minute anime battle short

Original-character anime fight built on the *Goku* / *Saitama* archetypes (spiky-haired invincible martial artist vs bored one-punch hero). **Not the licensed characters** — original designs, so it's safe to publish.

| File | What it is |
|---|---|
| `silver-vs-bald-1080p.mp4` | **Finished video** — 1920×1080, 30fps, exactly 2:00, 28 MB |
| `01-script-and-beats.md` | Beat sheet, character lock-sheet, dialogue |
| `frames/` | 10 anime key frames (standoff, powerup, punch caught, aerial trade, energy blast, beam walk, crater, final form) |
| `audio/` | 5 English dialogue clips — Silver and Bald have separate voices |

**Built with:** generated key frames → per-shot Ken Burns/punch-in + shake + impact flashes in ffmpeg → numpy-synthesized score (taiko + bass + risers) and SFX (whooshes, impacts, beam) mixed at fixed offsets → concatenated and muxed.

**Structure:** 0:00 title · 0:05 standoff · 0:12 dialogue · 0:26 power-up · 0:44 first clash · 1:04 energy blast · 1:19 beam walk · 1:27 final form · 1:38 white-out clash · 1:44 silence · 1:47 aftermath · 1:54 end card.

**Known limitation:** shots at 1:33, 1:36 and 1:47 currently reuse stand-in art (the "bald goes serious", "final clash" and "aftermath" frames hit the 10-image-per-turn cap). Swapping in the three final frames only requires re-rendering those segments and re-concatenating.
