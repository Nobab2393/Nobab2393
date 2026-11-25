# GRAND THEFT AUTO: VICE CITY — a 50 s flat-vector trailer

Fan-made, code-drawn, no footage and no samples anywhere. 1080×1920, 30 fps, 50.0 s,
H.264 + AAC.

**Deliverable:** `vice-city-trailer-1080x1920.mp4`

Built from the story brief: the setup, the protagonist, the rise, the conflict, the payoff,
then the endcard. Every frame is a pure function of `t` — `--still 26.0` reproduces any
frame on its own.

---

## Beats

| t | beat | what happens |
|---|---|---|
| 0.0–3.2 | cold open | a neon line draws, the skyline fades up behind the title |
| 3.2–8.0 | the city | the skyline rises building by building, the neon sun comes up behind it, two palms snap in |
| 8.0–13.0 | the car | a wedge drives through the rain, headlights on the wet road, lane dashes sliding |
| 13.0–15.0 | the name | full pink card: **TOMMY VERCETTI** |
| 15.0–23.0 | the rise | the empire as a bar chart built out of blocks, sun setting behind it |
| 23.0–33.0 | the conflict | eight hard cuts, 1.25 s each: muzzle flash, explosion, sirens, the mob walking |
| 33.0–41.0 | the payoff | slow push on the mansion, the question lands in two beats |
| 41.0–50.0 | endcard | **VICE CITY**, "coming this summer", the price line, one last neon flicker |

## Look

Five tones, no gradients: `#0E0C12` night, `#1B1726` far skyline, `#2C243C` near skyline,
`#F4EFE4` cream ink, and the accent family — neon pink `#FF3D8B`, cyan `#45D8E8` for the
headlights and sirens, amber `#FFB54A` for the sun. Type is DejaVu Sans Bold in caps with
wide tracking — the closest heavy grotesk on this box.

The whole thing is drawn from primitives: buildings are rectangles with a seeded window
lattice, palms are eight fanned quads, the car is a nine-point polygon, explosions are two
star polygons. Even the CRT feel is drawn — scanlines every 5 px and flat corner wedges,
not a blur.

## Sound

`track.py` synthesises the entire bed with numpy — 110 BPM, A minor (Am–F–C–G), 50 s:

- pad: detuned additive saws, one chord per bar
- kick: pitch-swept sine; snare: differentiated noise plus a 190 Hz body; hats: noise ticks
- bass: 8th-note saw pulses; arp: 16th-note squares that pan left/right
- arrangement gates by section — drums enter at 4 s, arp at 15 s, drive at 24 s
- a 4 s noise-and-pitch riser into the endcard, an impact on it, a crash on the downbeat

## Files

| file | what it is |
|---|---|
| `craft.py` | canvas, palette, easing, letter-spaced type, neon glow, scanlines, grain |
| `night.py` | skyline, palms, sun, car, rain, explosion, silhouettes |
| `track.py` | the synthesised soundtrack → `audio/track.wav` (not committed — 1 s to rebuild) |
| `trailer.py` | the eight beats, timeline, render / segment / join |

## Rebuilding

```bash
python3 track.py                     # audio/track.wav (1 s to synthesise)
python3 trailer.py --still 26.0      # one frame
python3 trailer.py --seg 0 750 segA.mp4
python3 trailer.py --seg 750 1500 segB.mp4
python3 trailer.py --join segA.mp4 segB.mp4
```

## Honest notes

- **Fan work.** Grand Theft Auto and Vice City are Rockstar's; this is a code-drawn
  interpretation of a written brief, not a copy of any frame, asset or logo.
- **No voice-over.** The script's narration is carried by type only. Adding a read would
  need a TTS pass and I did not want to bake a voice without you picking one.
- **The music is synthesis, not composition.** It is a serviceable synthwave bed with a
  fixed four-chord loop; it does not duck, swell or hit picture beyond the one riser and
  one impact at the endcard.
- **Aspect is 9:16**, to match everything else in this repo. The renderer is one constant
  away from 16:9 if you want the cinematic frame.
- No motion blur, no depth of field, no particles — the flat look is the point, but the
  car and the explosion are polygons on eased curves, not simulated.
