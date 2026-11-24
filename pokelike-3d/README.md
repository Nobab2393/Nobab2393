# angaar-baadal — a 3D-anime short rendered in pure Python

The film described in [`01-script.md`](01-script.md), built from scratch in this folder with
nothing but numpy + Pillow + HarfBuzz. No Blender, no GPU, no game engine — so the whole
thing is reproducible on a CPU-only box, and every frame is a function of `t`.

```
cel3d.py    # software 3D: mesh, transform stack, camera, painter's sort, cel shading, outline, bloom
cast.py     # the three characters, rigged as parameterised low-poly models
bg.py       # sky, stars, moon, ridge silhouettes, ground, speed lines, impact, sparks, dust, wind
deva.py     # Devanagari shaping (HarfBuzz) -> outline -> pixel mask, composited as text
film.py     # the timeline: 7 scenes, one draw(t) for the whole film, ffmpeg pipe
sheet.py    # character sheet -> frames/sheet.png
audio/      # s1..s7.mp3  Hindi voice-over, one clip per block
fonts/      # NotoSansDevanagari.ttf (SIL OFL)
```

**Output:** [`angaar-baadal-1080x1920.mp4`](angaar-baadal-1080x1920.mp4) — 1080×1920, 24 fps,
51.80 s, 4.9 MB, H.264 + AAC stereo.

| file | what |
|---|---|
| `angaar-baadal-1080x1920.mp4` | the film (Vertical 9:16, Hindi) |
| `poster.png` | 1080×1920 cover / thumbnail frame (the CTA card) |
| `preview-contact-sheet.png` | 16 frames across the whole timeline |

## How the look is made

The brief was *3D anime*, so the geometry is real 3D but the shading is deliberately flat:

- **3-band cel ramp.** Each face's lambert term is quantised into shadow / mid / light and
  mapped through the character's own 3-colour palette. No gradients on faces — that is what
  reads as "anime" rather than "cheap 3D".
- **Hard terminator.** The light vector is rotated slightly per shot so the shadow edge cuts
  *across* the form (cheek, chest, thigh) instead of hugging the silhouette.
- **Warm key + cool rim.** Key `[-0.42, 0.78, 0.46]` is ember-warm; rim `[0.62, 0.76, 1.0]`
  is moonlight, drawn on the back-facing edges — the single strongest 3D cue in a still frame.
- **Ink outline.** Each model is rendered into its own bbox tile, dilated ~7 px, then the
  colour pass is composited over it. Outlining per model (not per frame) keeps overlapping
  parts from growing.
- **Emissive bloom.** The flame's own faces are flagged emissive, blurred, and added back —
  so the pup lights his side of the frame and the night stays dark.
- **Supersampling only where it matters.** Rendering the full 1080×1920 frame at 1.7× costs
  ~4.5 s/frame. Rendering each *character tile* at 1.7× costs ~2 s/frame for the same edge
  quality; the sky and ground are vector-clean at 1× anyway. That 2× speed-up is what makes a
  52-second film renderable in ~40 minutes on one core.

## Hindi text without Raqm

Pillow in this environment is built without Raqm, so `ImageDraw.text` cannot shape Devanagari
(it renders dotted boxes or wrong matras). `deva.py` therefore:

1. runs `uharfbuzz` over the string to get glyph ids + advances (real conjuncts, real matras,
   real reordering);
2. pulls each glyph's contours with `fontTools.pens.recordingPen`'s **`DecomposingRecordingPen`**
   — the plain `RecordingPen` silently drops composite glyphs (which is most of Devanagari);
3. scan-converts each contour with an even-odd fill **per glyph**, then unions glyph masks.
   XOR-ing all contours at once cancels the overlaps between letters and eats half the text.

## Rebuild

```bash
pip install --break-system-packages numpy pillow imageio-ffmpeg matplotlib uharfbuzz fonttools
python3 sheet.py                 # cast sheet
python3 film.py --still 12.5     # inspect a single frame at t=12.5 s
python3 film.py                  # full render -> angaar-baadal-1080x1920.mp4
python3 film.py --sheet          # contact sheet of the finished frames
```

`ffmpeg` comes from `imageio_ffmpeg.get_ffmpeg_exe()`; raw RGB frames are piped straight into
it with the VO mixed to `audio/mix.wav` (`adelay` + `amix`) beforehand.

## Render pipeline (and why it is segmented)

`python3 film.py` renders the whole film in one pass, but a 40-minute single pass is a bad
place to lose work — so `film.py --seg A B out.mp4` renders a frame range to its own silent
segment, and `film.py --join seg1 ... seg7` concatenates the segments and muxes the VO. A
mistake in one scene costs 4 minutes instead of 40, and re-cutting one scene needs no re-render
of the rest.

Framing is solved, not eyeballed: `scene_cam()` fits the camera to the cast's projected bbox
(one constant correction per scene, computed on a hero pose so the camera never breathes) and
`stage()` paints the ground at the corrected world line, so feet and horizon always agree.
