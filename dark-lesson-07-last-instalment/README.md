# অন্ধকার পাঠ ০৭ · শেষ কিস্তি
**The Last Instalment** · 2:11 · 1080×1920 · 24 fps · Bangla, conversational

Dada believes the house loan is paid — he pressed his thumb on the receipt the paper
seller's boy handed him. Bou reads it out: the thumbprint is pen, and the signature
beside it belongs to her own son. Chele signed his grandfather's name on a school form
to get a phone, and asked his seven-year-old sister to say nothing. At dusk the paper
seller comes back, not to accuse anyone, but to say what paper is: a thing that keeps
what you wrote. The family keeps the house. The door keeps the name of the lie.

**File:** `dark-lesson-07-last-instalment-1080x1920.mp4` — 2:11.13, 23.5 MB,
H.264 High / yuv420p, AAC-LC 160 kbps stereo, faststart.

## Cast — five generated characters, five voices

The plates were made for this episode in the Claude-2D flat-vector house style
(`../character-style-preview/cast-claude2d/`), then cut out, rigged and puppeted here.

| character | plate | voice | design |
|---|---|---|---|
| দাদা · dada | `01-dada` | `voice-31` | 72, white beard, spectacles, walking stick |
| বউ · bou | `02-bou` | `voice-32` | 28, braid, mustard kurta, coral-flap satchel |
| ছেলে · chele | `03-chele` | `voice-33` | 15, off-white tee, coral pocket |
| নাতনি · natni | `04-natni` | `voice-36` | 7, coral ribbons, bare feet |
| কাগজওয়ালা · kagojwala | `05-kagojwala` | `voice-35` | 52, skullcap, paper bundle |

## How it is made

| file | what it does |
|---|---|
| `01-script.md` | the ten lines, with intent |
| `prep7.py` | cuts each plate out of its paper field by **connectivity**, not colour — the clothes are the same off-white as the paper, so a threshold would eat them |
| `prep7b.py` | finds eyes and mouth per face, samples a skin tone, paints the drawn-in mouth out, writes `cast/rigs.json` |
| `film8.py` | the film: sets, camera, puppets, lip-sync, Bangla captions |
| `mix8.py` | the sound: ten takes placed on the timeline, plus synthesised room |
| `deva.py` | Bangla type as pixels — harfbuzz shaping + fontTools outlines, because PIL here has no libraqm |

**Animation.** The mouth is not a cycle — it is the audio. Each take is turned into a
24 fps loudness envelope (`envelope()`), and the speaker's mouth is drawn from that
number, so open/closed tracks the syllables; the body gets breathing, a weight shift, a
bob that dips on open vowels, and a blink on its own period. Camera moves are the only
other motion: each shot eases between two framings, and the puppets are re-projected
through the camera so they scale and slide with the set instead of floating over it.

**Light.** Morning → noon → dusk → night. Puppets are graded with a multiply pass
(dusk warm, night cool-dark), and at night the lamp's glow is composited *in front* of
them, so they are lit by the same lamp as the wall.

**Bangla on screen.** Ten captions, speaker chip, scene word — all shaped with
harfbuzz, so conjuncts (গজ, স্ত, ক্ত) and matras are correct.

## Timeline

| # | t0 | who | s |
|---|---|---|---|
| 1 | 2.4 | কাগজওয়ালা (বাজার) | 14.60 |
| 2 | 17.55 | দাদা | 15.20 |
| 3 | 33.15 | বউ | 11.68 |
| 4 | 45.33 | ছেলে | 13.24 |
| 5 | 58.97 | নাতনি | 11.16 |
| 6 | 70.83 | দাদা (সন্ধ্যা) | 11.80 |
| 7 | 83.03 | ছেলে | 10.24 |
| 8 | 94.07 | কাগজওয়ালা (গেট) | 13.80 |
| 9 | 108.57 | নাতনি (রাত) | 3.36 |
| 10 | 112.53 | কাগজওয়ালা | 11.00 |
| — | 124.43 | paper card | 3.0 |
| — | 127.43 | end card | 3.0 |

## Re-render

```bash
python3 prep7.py && python3 prep7b.py                      # rigs
python3 mix8.py                                            # audio/mix.wav
python3 film8.py --seg 0 1040 --out /tmp/a.mp4             # 3 segments, sequentially
python3 film8.py --seg 1040 2080 --out /tmp/b.mp4
python3 film8.py --seg 2080 3123 --out /tmp/c.mp4
printf "file '/tmp/a.mp4'\nfile '/tmp/b.mp4'\nfile '/tmp/c.mp4'\n" > segs.txt
ffmpeg -y -f concat -safe 0 -i segs.txt -i audio/mix.wav \
       -c:v copy -c:a aac -b:a 160k -movflags +faststart out.mp4
```

Rendering is local PIL at ~5 fps, so the full pass is about eleven minutes of wall clock
on this box. No hosted video model is used anywhere in this pipeline.
