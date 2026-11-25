# কিসের তুলনায়? · "Compared to What?"

A two-minute storybook film about a crossed-out price. 1920×1080, 20 fps, 2:01,
Bangla narration, no dialogue except one line from the owl.

**Deliverable:** `compared-to-what-1920x1080.mp4`

---

## What it is

Bruno, a young rabbit with eighty dollars and a plan, sees a bicycle marked
"was 200, now 79" and mistakes the crossed-out number for a gift. Olive, an old owl
who has watched that sign for eleven years, says six words — and the number cracks.
He walks to the end of the lane, where a hedgehog sells him a better bicycle for
sixty-five, with nothing crossed out.

Every frame is drawn by code: a small numpy software renderer projects low-poly
geometry, shades it with flat Lambert light, casts projected shadows onto the square,
and the whole thing goes through autumn fog and a warm film grade. There is no 3D
package, no textures, no assets.

| | |
|---|---|
| picture | 1920×1080, 20 fps, rendered at 1600×900 and upscaled |
| length | 2:01.5 (121.5 s) |
| sound | 44.1 kHz stereo, all synthesised |
| language | Bangla narration + Bangla on-screen text |

## Shots

| time | scene | what happens |
|---|---|---|
| 0:00 | the sign | the square at golden hour, title, Bruno bounces past with his purse |
| 0:07 | | the shopfront and the crossed-out ২০০, and a push into his eyes |
| 0:21 | the watcher | Olive on the signpost, tilting; Bruno dances out, "saved ১২১" |
| 0:39 | the montage | a scooter (১৫০ → ৫৯), a helmet (৬০ → ২৫), the same purse |
| 0:54 | the question | the counter, Olive glides down, "কিসের তুলনায়?" |
| 1:02 | | the ২০০ cracks and falls as paper; receipts behind the counter all read ৭৯ |
| 1:17 | the honest shop | no sign, no sale, a plain tag: ৬৫; the bicycle rolls, and he pays |
| 1:36 | the moral | the ride home with the ribbon, one blink from the lamp post, and the line |

## Files

| file | what it is |
|---|---|
| `studio.py` | the renderer: primitives, camera, z-buffer raster, shading, shadows, fog, grade |
| `cast.py` | Bruno, Olive, the hedgehog, the bicycle, the scooter, the shops, the trees |
| `film.py` | the six scenes, the timeline, the 2D cards, Bangla type, the render CLI |
| `score.py` | the soundtrack: pad, bass, felt piano, air, paper rustle, narration mix |
| `deva.py` + `fonts/` | Bangla shaping (harfbuzz + fontTools outlines) — PIL alone scatters matras |
| `vo/` | the narration takes (one per beat) and `vo/track.wav` |

## Rebuilding

```bash
python3 score.py                       # needs vo/*.mp3 -> vo/track.wav -> audio/mix.wav
python3 film.py --still 66.0           # one frame
python3 film.py --seg 0 1230 segA.mp4
python3 film.py --seg 1230 2430 segB.mp4
python3 film.py --join segA.mp4 segB.mp4
```

## Honest notes

- **It is not really 3D in the sense a studio means.** It is a rasteriser I wrote
  for this: flat shading, one key light, one rim, projected hard shadows blurred at
  quarter resolution. No global illumination, no ambient occlusion, no reflections, no
  motion blur, no depth of field. "Stylized 3D storybook" here means low-poly volumes,
  soft light, matte materials and slow camera moves — not a rendered short.
- **The narration is TTS**, in Bangla, two voices: the narrator and Olive's one line.
  It is a calm read, but it is a read — not a performance with breath and timing.
- **The Bangla is a translation I wrote**, keeping the structure and the numbers of
  the English script. Dollar amounts stay dollars, with Bangla numerals (৮০, ২০০, ৭৯).
- **The music is a loop, not a score.** Four bars, D major, with layers that enter at
  section boundaries; it ducks under the voice but it does not hit picture.
- **Timing is built on the voice**, so the scenes are as long as the read needs; the
  total is 2:01, close to the 2:00 brief.
- The paper-rustle effects are synthesised noise, not recorded paper.
