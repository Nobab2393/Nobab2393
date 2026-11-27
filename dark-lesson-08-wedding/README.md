# অন্ধকার পাঠ ০৮ · জামিন
**The Guarantee** · 2:01 · 1080×1920 · 24 fps · Bangla, conversational

A wedding the bride did not choose, paid for by a loan nobody can repay. The shopkeeper
wants his rice money, the elder has signed as guarantor, the moneylender holds the deed
with the elder's thumbprint on it, and the postman brings the letter that proves the
groom's family already knows. The widow speaks for the girl's mother, who once sold her
own gold on her wedding day. The shopkeeper tears up his bill, the moneylender hangs the
deed on the wall instead of taking it down, and the elder calls the wedding off — and
loses his face in the street to keep the girl's.

**File:** `dark-lesson-08-wedding-1080x1920.mp4` — 2:01.00, 31.1 MB,
H.264 High / yuv420p, AAC-LC 160 kbps stereo, faststart.

## Cast — the ten neighbours, five speaking

The plates are the street set (`../character-style-preview/street/`), made in the
Claude-2D flat-vector house style, cut out and rigged here. Silent neighbours are
puppeted from the same rig, with the mouth left alone: they breathe, they blink, they
shift their weight, and they never speak.

| character | plate | voice | in the episode |
|---|---|---|---|
| মোড়ল · elder | `elder` | `voice-38` | speaks (2, 7, 10) |
| দোকানদার · shopkeeper | `shopkeeper` | `voice-39` | speaks (1, 6) |
| মহাজন · moneylender | `moneylender` | `voice-40` | speaks (3, 8) |
| ডাকপিয়ন · postman | `postman` | `voice-41` | speaks (4) |
| বিধবা · widow | `widow` | `voice-42` | speaks (5, 9) |
| নববধূ · bride | `bride` | — | listens (5, 9, 10) |
| দর্জি · tailor | `tailor` | — | listens (3) |
| শিক্ষিক · teacher | `teacher` | — | listens (8) |
| ছাত্রী · student | `student` | — | listens (4) |
| মাঝি · boatman | `boatman` | — | listens (4) |

## How it is made

| file | what it does |
|---|---|
| `01-script.md` | the ten lines, with intent |
| `prep8.py` | rigs the six faces: floods the head for skin, finds the eye pair and the mouth, paints the drawn-in mouth out by cloning the cheek band above it, writes `cast/rigs8.json`. Four faces needed hand coordinates (`FIX`) — glasses, beard, veil and moustache defeat the detector |
| `film9.py` | the film: two sets, one camera, puppets, lip-sync, Bangla captions |
| `mix9.py` | the sound: ten takes placed on the timeline, plus a synthesised afternoon |
| `deva.py` | Bangla type as pixels — harfbuzz shaping + fontTools outlines, because PIL here has no libraqm |

**Animation.** The mouth is not a cycle — it is the audio. Each take is turned into a
24 fps loudness envelope (`envelope()`), cached to `audio/_env*.wav`, and the speaker's
mouth is drawn from that number: a line when silent, a widening oval when open, with the
tongue only on the loud frames. Open/close therefore tracks the syllables of that take
and nothing else. On top of it: breathing, a slow sway, a weight shift, a blink every few
seconds, and a small dip of the head on stressed syllables.

**One clock.** There is a single timeline: `ENTRIES` is built from the take durations,
`PAPER_A` and `CARD_A` fall out of it, and every frame is `frame(i / FPS)`. Nothing is
stretched or retimed afterwards — the video is encoded from that clock and the mix is
placed on the same one, so picture and voice cannot drift apart. Each turn owns its shot:
the camera starts moving at `t0` and lands before the next speaker's `pre` gap.

**One hour.** The light never changes. `grade()` returns its input untouched and the
palette is the light: paper `#F0EEE6`, ink `#1A1714`, mustard `#C99A2E`, coral `#D97757`,
sand `#D8B579`. Two sets, one afternoon: the shop with its shutter half up and its
counter of sacks and jars, and the lane with the scalloped shamiana, two garland
strands, the bride's gate, and the nail at `(952, 760)` where the deed hangs.

**Framing.** Every actor stands on the same ground line (`y = 1258` in set space); shot
scale is set by `h` and by the camera, never by moving feet off the floor. Feet land on
the line in every shot, the caption band starts at `y = 1596`, and the header sits on a
paper pill so it reads over cream wall and coral cloth alike.

## Rebuild

```bash
python3 prep8.py                                    # rigs  -> cast/
python3 film9.py --still 30 --out frames/s.png      # one frame
python3 film9.py --seg 0 968 --out seg0.mp4         # a third (≈5 fps)
python3 mix9.py                                     # -> audio/mix.wav
ffmpeg -f concat -safe 0 -i segs.txt -i audio/mix.wav \
       -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart \
       dark-lesson-08-wedding-1080x1920.mp4
```

`preview-contact-sheet.png` is twelve frames pulled from the finished file — cards, both
sets, all five speakers, the bride listening twice.
