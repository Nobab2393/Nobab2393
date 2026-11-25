# অন্ধকার পাঠ · DARK LESSON — a 3D-anime dark lesson rendered in pure Python

The film described in [`01-script.md`](01-script.md). Built from nothing but numpy + Pillow +
HarfBuzz: no Blender, no GPU, no engine — so it re-renders on a CPU-only box and every frame is
a pure function of `t`.

**Output:** [`dark-lesson-1080x1920.mp4`](dark-lesson-1080x1920.mp4) — 1080×1920, 24 fps,
59.36 s, H.264 + AAC stereo.

| file | what |
|---|---|
| `dark-lesson-1080x1920.mp4` | the film (9:16, Bangla VO) |
| `poster.png` | 1080×1920 cover frame (the CTA card) |
| `preview-contact-sheet.png` | 16 frames across the timeline |
| `01-script.md` | the seven beats, the VO lines, the CTA and its variants |

```
cel3d.py   software 3D: mesh, transforms, camera, painter's sort, cel ramp, ink outline, bloom
cast.py    Ayan, the black lantern, the shade (and the props: coin, photo)
bg2.py     the alley and the room: brick wall, floor falloff, light pools, fog, window shaft, coins
deva.py    Bengali shaping (HarfBuzz) -> outlines -> pixel mask
film.py    the timeline: seven scenes, draw(t), segmented renderer, ffmpeg
audio/     s1..s7.mp3 (voice-08, Bangla) and v1..v7.mp3 (silence-trimmed)
fonts/     NotoSansBengali[wdth,wght].ttf (SIL OFL)
```

## How the look is made

- **One warm accent.** The whole film is ink, brick and cold blue (`#8FAEFF`). Ayan's own
  candle is the only warm thing on screen, which is why the last beat reads instantly: the
  frame turns warm the moment he stops borrowing.
- **Three-band cel ramp, hard terminator**, warm key from below (the lantern) and a cool rim
  from the window — the shading model lives in `cel3d.toon()`.
- **Ink outline per model, not per frame**: each model renders into its own bounding-box tile,
  is dilated ~6 px at 1.35× supersampling, and is composited back. Outlining per model keeps
  overlapping limbs from growing into each other.
- **Light is painted, not lit.** The pools, the glow and the fog are 2D blurs drawn at ¼
  resolution and upscaled; they cost ~40 ms instead of ~400 ms, which is what makes a
  1 425-frame film renderable in about half an hour on one core.
- **The shade has no feet.** It tapers into the floor as one cone, so it never looks like it is
  standing *in* the room — it looks like it is drawn *by* it.

## Bengali type without libraqm

Pillow here has no Raqm, so Indic text cannot be shaped by `ImageDraw.text` (matras would
scatter). `deva.py` runs HarfBuzz for glyph ids and positions, pulls contours with fontTools'
**`DecomposingRecordingPen`** (the plain `RecordingPen` silently drops composite glyphs, which
is most of a Bengali consonant cluster), and scan-converts each glyph with an even-odd fill —
XOR *within* a glyph, union *across* glyphs. Getting that parity wrong cancels overlapping
letters, which is exactly the bug the first version had.

## Render pipeline

```bash
pip install --break-system-packages numpy pillow imageio-ffmpeg matplotlib uharfbuzz fonttools
python3 film.py --still 22.0          # inspect one frame
python3 film.py --mix                 # build audio/mix.wav (adelay + amix)
python3 film.py --seg 820 990 segs/s5.mp4   # render a frame range to a silent segment
python3 film.py --join segs/s1.mp4 ... segs/s7.mp4
```

Segments exist because a 35-minute single pass is a bad place to lose work: a mistake in one
scene costs two minutes to redo, and re-cutting one scene needs no re-render of the rest.

## Note on tooling

This was built with the in-house renderer above, **not** with MiniMax: no MiniMax credentials
exist in this environment and its API hosts (`api.minimax.io`, `api.minimaxi.com`) are not
reachable from it, so MiniMax video generation could not be used here.
