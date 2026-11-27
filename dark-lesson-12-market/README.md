# বাজারের আড়ত — the market warehouse

**Dark Lesson 12 — cast.** A wholesale market godown in daylight. Five strangers are shut
in when the back door is sealed from the street side; none of them knows the other four, and
the crates in the yard are counted in a way that does not add up.

**Look: 2D cel-shaded TV anime.** Crisp dark line art, three flat tones per surface — base,
one hard-edged shadow, one highlight band — and a thin white rim light down the figure's
left edge. Daylight from the left, so every shadow has a clean, drawn edge. No gradients, no
airbrush, no paper texture: this is a different family from the woodcut of 9–10 and the paper
cutout of 11.

Each plate is drawn on a flat pale cool-grey field so the figure trims cleanly and drops onto
a drawn set.

**`sheets/lineup.png`** — five, one scale, feet on one line.
**`sheets/0N-*-card.png`** — one card per character, 900×1200, name and role in Bengali.
**`cast/0N-*-neutral.png`** — trimmed plate with the field knocked out (RGBA), ~1225 px tall.

## The five

| # | | age | role | the one thing you see first |
|---|---|---|---|---|
| 01 | রাফি হাসান | 19 | ছাত্র | grey hoodie, earphone wire down his chest, worn sneakers |
| 02 | সাদিয়া আফরিন | 27 | নার্স | teal scrubs under a cream cardigan, stethoscope, ID badge |
| 03 | আনোয়ার হোসেন | 45 | পাইকারি ব্যবসায়ী | checked shirt, brick red gamchha, cloth ledger under one arm |
| 04 | আব্দুল কাদের | 68 | অবসরপ্রাপ্ত শিক্ষক | off-white kurta, prayer cap, wooden stick |
| 05 | মীম আক্তার | 15 | স্কুলের ছাত্রী | two braids with red ribbons, green frock, school bag |

They do not know each other. That is the point of the cast.

## Stature

`STATURE` for the five: 01 `1.02` · 02 `1.00` · 03 `0.99` · 04 `0.94` · 05 `0.90`.

## How it is built

`sheets.py` trims each plate against the field colour taken from its four corners, keeps the
largest blob, knocks the field out to alpha, scales every figure to one height, and sets the
Bengali names and roles through `deva.py` (harfbuzz shaping — PIL here has no libraqm and
would break the conjuncts).

```bash
python3 sheets.py            # -> cast/*.png, sheets/lineup.png, five cards
```

## The film

**থলি (The Sack).** Five strangers are in a wholesale godown when the steel shutter comes
down from the street side. In the corner there is a jute sack with its mouth open, and every
time someone touches it the shutter drops another notch — one finger, a hand, to the knees.
The room darkens by degrees; the afternoon walks out of it. The old teacher is the only one
who knows the arithmetic: the sack belonged to a porter who died under that same shutter.
The way out is not to fight the door but to put back what is not yours — all five of them,
together.

> যা তোমার নয়, তার ওজন একদিন তোমার ঘাড়েই আসে।

- `01-script.md` — the ten scenes, the lines, the staging notes.
- `lines.py` — the ten narration lines, the source of truth for the recording.
- `audio/scene01…10.mp3` — one narrator, conversational, 99.7 s of speech.
- `plan.py` — timeline: 14 shots, every cut inside the silence before its line.
- `film.py` — the renderer: cel plates on drawn sets, walk cycles, breath, contact shadows,
  a grade that goes from noon to dusk as the shutter comes down.
- `mix.py` — the bazaar behind the wall, the shutter's steps, jute under a hand, the ratchet
  of it climbing again.
- `verify.py` — measures the finished mp4: length, drift, every cut, every entry.
- `contact.py` — the twelve-frame contact sheet.

```bash
python3 plan.py
python3 mix.py --no-mux      # -> build/mix.wav
python3 film.py --crf 24     # -> build/video.mp4
python3 mix.py               # mux -> dark-lesson-12-market-1080x1920.mp4
python3 verify.py
python3 contact.py
```

## Status

Rendered and checked. 2892 frames at 24 fps — 120.500 s of picture against 120.500 s of
audio, drift 0.0 ms; all ten cuts sit in silence, the worst first word lands 66 ms after its
shot opens.

- `dark-lesson-12-market-1080x1920.mp4` — 1080×1920, h264 + aac, 120.5 s
- `dark-lesson-12-market-720x1280.mp4` — 720×1280, lighter
- `dark-lesson-12-market-contact.png` — twelve frames, 0:00 to 1:58
