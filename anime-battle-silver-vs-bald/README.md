# SILVER vs BALD — 2-minute anime battle short

Original-character anime fight built on the *Goku* / *Saitama* archetypes (spiky-haired invincible martial artist vs bored one-punch hero). **Not the licensed characters** — original designs, so it's safe to publish.

| File | What it is |
|---|---|
| `silver-vs-bald-smooth-1080p.mp4` | **Finished video (smooth cut)** — 1920×1080, 30fps, exactly 2:00, 25 MB |
| `01-script-and-beats.md` | Beat sheet, character lock-sheet, dialogue |
| `frames/` | 10 anime key frames (standoff, powerup, punch caught, aerial trade, energy blast, beam walk, crater, final form) |
| `audio/` | 5 English dialogue clips — Silver and Bald have separate voices |

**Built with:** generated key frames → per-shot Ken Burns/punch-in + shake + impact flashes in ffmpeg → numpy-synthesized score (taiko + bass + risers) and SFX (whooshes, impacts, beam) mixed at fixed offsets → concatenated and muxed.

**Structure:** 0:00 title · 0:05 standoff · 0:12 dialogue · 0:26 power-up · 0:44 first clash · 1:04 energy blast · 1:19 beam walk · 1:27 final form · 1:38 white-out clash · 1:44 silence · 1:47 aftermath · 1:54 end card.

## Smooth-motion pass (v2)

Every shot now has continuous, eased camera motion instead of a static hold:

- **Ease-in-out curves** on zoom and pan — `pow(min(on/N,1),2)*(3-2*min(on/N,1))` — so moves accelerate and settle like real camera work.
- **Alternating pan direction** per shot so match-on-action reads across cuts (right-to-left push, then left-to-right).
- **Per-shot handheld shake** on action beats (two sine frequencies on x/y).
- **Punch-ins** with cubic ease-out and a 32% zoom over 2–3.5 s on impact shots.
- **Global finish:** vignette + temporal film grain + chromatic shift on the 0:41–1:01 and 1:33–1:40 windows.
- Verified per-shot motion: mean frame-to-frame pixel delta is 2.4 (calm shots) to 8.4 (action shots), i.e. no frozen frames.

The 16 frames now include the missing climax art (bald-goes-serious, final clash, aftermath) plus three new action poses (silver rush, bald counter, debris rain).
