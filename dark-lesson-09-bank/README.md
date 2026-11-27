# অন্ধকার পাঠ · পর্ব ৯ — এক শাখা, দশ জন

**A Dhaka bank branch, eight forty at night.** The cash does not tally by twenty-six
lakh. The shutter should have come down at six. Ten people are still inside, and none of
them is saying anything.

**2:00 · 1080×1920 · 24 fps · Bangla, one narrator, ten silent figures.**

- `dark-lesson-09-bank-1080x1920.mp4` — the film
- `dark-lesson-09-bank-contact.png` — twelve frames
- `01-script.md` — the script, scene by scene, with the sync method written down
- `sheets/lineup.png` + `sheets/0N-*-card.png` — the cast

## What it is

Episode 8 was a wedding on a street, five people talking over each other. This one goes
inside: a room, a closed door, and ten people who have all stopped speaking. The voice
belongs to someone standing behind you, telling you what happened — conversational,
level, never raising itself. The fear is in the room tone and in how long the camera is
willing to stand still.

Told in nine scenes and eighteen shots, on four hand-drawn rooms: the hall with its
counter and grille, the corridor to the strongroom, the IT corner with its dead monitor,
and the entrance where the shutter is already two-thirds down.

## Cast

Ten figures, seven women and three men, aged 23 to 60, drawn as screenprint plates —
black, deep indigo and brick red on warm cream, hand-cut contours, woodgrain and
halftone, no background in the plate itself. Every one of them is silent from the first
frame to the last.

| # | | age | role |
|---|---|---|---|
| 01 | শিরিন আক্তার | 38 | শাখা ব্যবস্থাপক — branch manager |
| 02 | রোকেয়া বেগম | 47 | প্রধান ক্যাশিয়ার — head cashier |
| 03 | নাসরিন সুলতানা | 29 | অ্যাকাউন্ট ডেস্ক — account desk |
| 04 | তাসলিমা খাতুন | 34 | ঋণ কর্মকর্তা — loan officer |
| 05 | পারভীন আক্তার | 52 | ক্লিয়ারিং — clearing |
| 06 | সুমাইয়া ইসলাম | 23 | প্রবেশনারি অফিসার — probationary officer |
| 07 | ফরিদা ইয়াসমিন | 44 | হিসাব রক্ষক — accountant |
| 08 | হাবিবুর রহমান | 58 | নিরাপত্তা প্রহরী — security guard |
| 09 | কামরুল হাসান | 31 | আইটি ও জেনারেল ব্যাংকিং — IT |
| 10 | জাহাঙ্গীর আলম | 60 | অফিস সহায়ক — office assistant |

## How it is built

Four scripts, each one thing:

**`plan.py`** — the timeline. Decodes the nine narration clips, trims the silence the
generator leaves at each end, measures the real pauses *inside* each line, and lays the
clips end to end with a fixed 0.45 s gap. A scene that carries two shots cuts at the
longest real pause near its middle, so the picture turns over in silence, not on a word.

**`film.py`** — the picture. Each shot is composited once into a 1350×2400 master: the
hand-drawn room, the figures keyed off their own paper, a soft ground shadow under each
pair of feet. The camera then crops and resizes that master per frame, which is what
makes a pan smooth without resampling the figures twice. On top: paper grain, a vignette,
dust specks, and two frames of colour misregistration on every cut — a print artefact
that also lands the cut as a physical beat.

Two details worth keeping: the figures are keyed by flooding paper from the border
inwards, never by colour, so a white saree inside an ink contour survives; and the room's
clock is repainted at 8:40, because the drawing came with 10:10 on it and the narrator
says the time out loud.

**`mix.py`** — the sound. The voice, placed sample-exactly, with a small room reverb under
it and a soft limiter over it; then room tone, tube-light hum, a clock at one tick a
second, a low drone that swells through the last third, the strongroom door, and the
shutter coming down — all of it mixed 20–30 dB under the narration, because the room
should never compete with the voice.

**`verify.py`** — the proof. It measures, rather than assumes: audio and picture the same
length to within one frame; every cut sitting *inside* a measured silence in the voice
track; every scene's first word landing within a frame or two of that scene's first frame.

```bash
python3 plan.py      # print the timeline, write timeline.json
python3 film.py      # render -> build/video.mp4   (~10 min at 1080x1920)
python3 mix.py       # -> build/mix.wav, mux -> dark-lesson-09-bank-1080x1920.mp4
python3 verify.py    # cuts, entries, lengths
python3 contact.py   # twelve frames on one sheet
```

## Notes

Text is set through `deva.py` (harfbuzz shaping, then outlines) because PIL here has no
libraqm and would set Bengali as broken glyphs. The rooms were drawn as four separate
plates and are moved against the figures by the camera, not by a compositor — there is no
real parallax, but a slow push across a flat plate reads as depth once the grain moves
with it.
