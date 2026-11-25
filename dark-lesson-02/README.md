# অন্ধকার পাঠ ০২ · শোধ — DARK LESSON 02: THE DEBT

The film described in [`01-script.md`](01-script.md). Same engine as ep-01: numpy + Pillow +
HarfBuzz, no Blender, no GPU, no engine — every frame is a pure function of `t`, so the render
is resumable and deterministic.

**Output:** [`dark-lesson-02-1080x1920.mp4`](dark-lesson-02-1080x1920.mp4) — 1080×1920, 24 fps,
66.66 s, H.264 + AAC stereo, Bangla voice-over.

| file | what |
|---|---|
| `dark-lesson-02-1080x1920.mp4` | the film (9:16, Bangla VO) |
| `poster.png` | 1080×1920 cover frame |
| `preview-contact-sheet.png` | 10 frames across the timeline |
| `01-script.md` | the seven beats, the timeline, the CTA |

```
cel3d.py   software 3D: mesh, transforms, camera, painter's sort, cel ramp, ink outline, bloom (from ep-01)
cast.py    Ayan, the passer (the friend, later rich), the coat
bg2.py     the alley: brick, floor falloff, light pools, fog, snow, frost
deva.py    Bengali shaping (HarfBuzz) -> outlines -> pixel mask
film.py    the timeline: seven scenes, draw(t), segmented renderer, ffmpeg
audio/     s1..s7.mp3 (voice-08, Bangla) and v1..v7.mp3 (silence-trimmed), mix.wav
fonts/     NotoSansBengali[wdth,wght].ttf (SIL OFL)
```

## What is new in ep-02

- **A thread instead of a candle.** The warm accent of ep-01 is gone; the only bright thing here
  is one cyan filament (`#80D8FF`) that stands for the debt. It is born in s1, thickens through
  s2–s3, goes taut in s4, hangs slack in s5, and breaks into drifting embers in s6.
- **Filaments are anchored to the cast, not the frame.** Each end of the thread is a world point
  (a hand, a wrist, a neck) projected through the same camera as the models — so it attaches to
  the bodies even while they move, and never drifts when a camera pulls back.
- **A new character: the passer.** A tall boy in a floor-length coat cone — hooded and shivering
  in s1, hood down and gold-scarfed (rich) from s2 on. Two states, one mesh, one parameter.
- **A new prop: the coat.** Three flat stacked cloth slabs with a collar roll and folded sleeves;
  it is the only warm-coloured object in s1 and s6.
- **Snow and frost overlays** (`bg2.snow`, `bg2.frost`) — the winter the whole film happens in.
- **Grade flip.** Cold `(232,240,255)` tint for s1–s5, warm `(246,240,232)` for s6 — the frame
  itself relaxes when he stops keeping accounts.

## Render pipeline

```bash
python3 film.py --still 22.0                # inspect one frame
python3 film.py --mix                       # build audio/mix.wav (adelay + amix, normalize=0)
python3 film.py --seg 0 400 s1.mp4          # render a frame range to a silent segment
python3 film.py --join s1.mp4 s2.mp4 s3.mp4 s4.mp4
```

Timeline (from `film.py`): VO starts at `[1.10, 10.20, 18.01, 25.63, 35.68, 45.06, 55.02]`,
scene bounds `[0.0, 9.86, 17.67, 25.29, 35.34, 44.72, 54.68, 61.96]`, total 1600 frames.

## Honest notes

- The voice-over is Bangla TTS with `voice_id="voice-08"`, not a human read and not MiniMax
  (MiniMax was unreachable from this box). The mp3s are silence-trimmed at the head only —
  trimming at the tail with `silenceremove`/`areverse` ate real speech.
- Rendering is CPU-only: ~1.3 s/frame on one core at 1.2× supersampling, so the 1600-frame film
  takes roughly half an hour across two cores.
