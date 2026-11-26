# অন্ধকার পাঠ ০৩ · কেনা সম্মান — Bought Respect

A flat-vector 2D short, **1080×1920, 24 fps, 1:44.9**, Bangla voice-over and Bangla on-screen
type. Every frame is drawn by code — no image model, no stock footage.

**Deliverable:** `dark-lesson-03-bought-respect-1080x1920.mp4` (H.264 High + AAC 192k stereo).

> গ্রামে রহিমকে সবাই সালাম দিত, কারণ সে সবার চা-এর বিল দিত। বাঁধ ভাঙার পর সকালে কেউ তাকে
> চিনল না — শুধু সেই বুড়ো এল, যে কখনো তার টাকা নেয়নি, হাতে এক গ্লাস পানি।

---

## The one decision everything else follows

**Gold means exactly one thing in this film: respect that was bought.** It is on Rahim's
body as a sash, on the bulb over the tea stall, on the medal, on the banner with his name,
in the coins falling through the applause. Then the flood comes — and **there is no gold in
the film again, not one pixel.** The palette tells you the ending before the narration does.

**Blue appears exactly once:** the glass of water the old man gives away for nothing, and
a single lit window as the two men walk out of the story.

| tone | value | meaning |
|---|---|---|
| paper | `#F0EEE6` | the world, daylight |
| ink | `#1A1714` | people, night |
| gold | `#C8963E` | bought respect — gone after the flood |
| blue | `#6A9BCC` | the thing that was never for sale — used once |

**The camera never moves.** This is the series' grammar (`dark-lesson-02`, `dark-lesson-03-2d`):
type sits still and shapes move. The only motion is what the story needs — the clap, the
falling coins, the rain, the water, the jab, the held-out glass.

## Why they have no faces

Code-drawn characters cannot hold a repeatable face, and faking one breaks the style. So
identity is carried by **silhouette, tone and gesture**:

- **রহিম** — broad, ink, a gold band tied round him, a shawl over one shoulder
- **বুড়ো** — thin, hunched, bearded, seated, a dustier cloth, a stick
- **গ্রাম** — a row of smaller, lighter bodies that never quite look at him

Arms are driven by **hand-targets with a bowed elbow** (`fig3.arm`), so a gesture is two
numbers. That is how the jab in the courtyard, the wave from the podium and the glass held
*out and down* where the other man can actually reach it are made.

## Beats

| time | set | caption | what happens |
|---|---|---|---|
| 0:00 | title | — | a `০৩` the height of the frame |
| 0:02 | tea stall | **সালাম** | coins arcing to the counter, the paid-for gold bulb, three regulars |
| 0:23 | podium | **দাম** | bunting, his name in gold, the medal dropping onto his chest, coin confetti, the crowd clapping |
| 0:42 | courtyard | **একজন বাদে** | a bare tree, an old man perfectly still on a stool, Rahim looming |
| 0:57 | flood | **ভাঙন** | rain, a sinking godown, sacks drifting, coins dimming as they go under |
| 1:08 | morning | **সকাল** | the stall shut, the bulb dead, three backs walking away |
| 1:18 | doorway | **এক গ্লাস** | the only blue in the film, offered down to a man on the ground |
| 1:28 | dusk road | — | two men walking, one blue window |
| 1:38 | end card | — | **ভাড়া শেষ — সম্মানও শেষ।** / সম্মান কি সত্যিই কেনা যায়? |

Full script, all 23 lines and the sound table: [`01-script.md`](01-script.md).

## Sound

A D-minor drone breathes under the whole piece. While the money works there is an
arpeggio that never resolves; on the podium every bell is **inharmonic** (f, 2.76f, 5.40f) —
the sound of something *bought*, not played — with a 58 Hz thump under it, a bill being
settled. At the flood the melody stops and only rain and a 46 Hz rumble remain. The last
sound is a single E5 bell: the glass of water. Then silence.

Speech is trimmed at both ends, normalised to 0.92, and the bed is ducked by
`1/(1+10·clip(env·6))`; master peak 0.96, mean −18.4 dB. Narrator: `voice-15`; Rahim `voice-13`, the old man `voice-14`.

## Voice-over only

`audio/voiceover-clean.mp3` (and `voiceover-clean.wav`, regenerate with `python3 cleanvo.py`)
is the same twenty takes on the film's own timeline with **nothing else in it** — no drone,
no arpeggio, no bells, no rain, no ducking, no room taps. Each take is trimmed of the
synthesised silence, matched to one speaking level (−20.5 dB RMS, ceiling −0.45 dBFS) with
8 ms fades so nothing clicks, and spaced at the picture's own 0.36 s. 1:45, 72.5 s of speech.
It drops straight onto the cut, or onto anyone else's cut.

## Files

| file | what it does |
|---|---|
| `fig3.py` | the silhouette rig — `person()` on hand-targets, plus `coin`, `glass`, `medal`, `mic`, `steam` |
| `film3.py` | clips, timeline, 7 sets, captions, cards, `--still T` / `--seg A B` / `--out` |
| `audio3.py` | `score` → `audio/score.wav`, `mix` → `audio/mix.wav` |
| `deva.py` | Bangla type: harfbuzz shaping + fontTools outlines (PIL has no Raqm here) |
| `audio/s01…s20.mp3` | one recording per clip; three clips carry two lines and split their subtitle |
| `preview-contact-sheet.png` | 12 frames, four times three |

```bash
python3 film3.py --still 47
python3 film3.py --out film3.mp4
python3 audio3.py score && python3 audio3.py mix
ffmpeg -i film3.mp4 -i audio/mix.wav -c:v copy -c:a aac -b:a 192k -shortest \
       -movflags +faststart dark-lesson-03-bought-respect-1080x1920.mp4
```

Render time on 2 vCPU: 3 min 32 s for 2517 frames.
