# ফেরত — the one who came back
**New Dark Lesson cast member · stickman · character + animation test**

A 28-year-old Bangladeshi man who went to the city and came back. Drawn as a stickman
who is *dressed*: a circle head with dot eyes, ink-stroke limbs, and city clothes laid over
the stick — off-white shirt with a coral pocket, mustard trousers, loafers, an office
satchel, and a helmet in his hand.

| file | what it is |
|---|---|
| `stickman-a.png` | the generated character plate (chosen design) |
| `cut.png` | the plate cut out of its paper, RGBA, trimmed |
| `rig.png` / `rig.json` | same, with the drawn-in mouth removed and eye/mouth coordinates |
| `stickman-ferot-1080x1920.mp4` | 25.75 s test: he steps out of a phone screen, speaks, steps back in |
| `contact-sheet.png` | eight beats from that test |

## The cut

The shirt is the same off-white as the paper, so no colour threshold can separate them —
it is the ink outline that separates them. `prep_stick.py` closes the ink by 7 px
(`MaxFilter`) so anti-aliased gaps seal, floods the **outside** only, then grows that
background region back. Everything inside the outline stays fully opaque, however
paper-coloured it is. Getting this wrong is what punched coral speckles through his
shirt for two attempts.

## The animation

- **Lip-sync** — the take (`line.mp3`, voice `voice-37`) is reduced to a 24 fps loudness
  curve; the mouth is drawn from that number. Open/closed tracks the syllables; there is
  no cycle.
- **Blink** — on its own rhythm, drawn as a lid line over a paper-coloured patch.
- **Pops** — `back()` easing with overshoot out of the screen, `soft()` back into it.
- **Captions** — four Bangla sentences, cut at the three longest silences in the audio, so
  the type follows his breath. Shaped with harfbuzz (`deva.py`).

## Re-render

```bash
python3 prep_stick.py          # cut + rig
python3 mix_stick.py           # audio.wav
python3 film_stick.py --seg 0 594 --out t.mp4
ffmpeg -y -i t.mp4 -i audio.wav -c:v copy -c:a aac -b:a 160k -movflags +faststart out.mp4
```
