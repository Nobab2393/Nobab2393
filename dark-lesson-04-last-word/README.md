# অন্ধকার পাঠ ০৪ · শেষ কথা — The Last Word

A flat-vector 2D short, **1080×1920, 24 fps, 1:15.0**, Bangla voice-over and Bangla on-screen
type. Every frame is drawn by code — no video model, no image generation, no stock footage.
Rendering is local (`film4.py` → H.264), the same pipeline as `dark-lesson-03-bought-respect`.

**Deliverable:** `dark-lesson-04-1080x1920.mp4` (H.264 High, AAC 160k stereo, faststart).

> দুই ভাইয়ের একটাই দোকান ছিল। বড় ভাই বলত, ছোট ভাই শুনত। প্রতিটা তর্কে বড় ভাই জিতত,
> আর দেয়ালে একটা দাগ পড়ত। দশ বছরে দেয়াল ভরে গেল, দোকান বড় হলো — আর শেষ দিন ছোট ভাই
> তর্ক করল না, শুধু বলল, *তুমি ঠিক।* দশ বছর পর বড় ভাই সেই দরজায় গিয়ে দাঁড়াল, যেখানে হাসি
> আর চায়ের শব্দ। হাত তুলল। নামিয়ে নিল।

---

## The one decision everything else follows

**Coral means exactly one thing in this film: an argument won, counted.** Every coral mark
on that wall is one tally — forty-six of them, one per win, and they only ever go up. Coral
never touches a body, a caption, a lamp or the end-card type. It is the shop's ledger, drawn
on plaster.

**Blue appears exactly twice, and it is the same cup:** the cup the younger brother leaves on
the counter on his last day, and the same cup still standing there on the last night.

| tone | value | meaning |
|---|---|---|
| paper | `#F0EEE6` | the world, daylight, the shop that was |
| wall | `#DBD6CA` | the wall that keeps the score |
| ink | `#1A1714` | people, and the whole second half of the film |
| coral | `#D97757` | **a won argument, tallied — nothing else, ever** |
| blue | `#6A9BCC` | the cup that was left behind — used twice |

**The camera never moves.** Series grammar: type and shapes hold still; only what the story
needs moves — the marks going up, a hand, a bag, a shrug, a breath.

## Why they have no faces

Code-drawn characters cannot hold a repeatable face, and faking one breaks the flat-vector
style. So identity is carried by **silhouette, tone and gesture**:

- **বড় ভাই (elder)** — taller, broad, a shawl over one shoulder, always the one whose arm
  is up mid-sentence
- **ছোট ভাই (younger)** — shorter, no shawl, still, hands down; the one who stops first
- **the crowd behind the lit door** — two small lighter bodies that laugh and never come out

Arms are hand-targets with a bowed elbow (`fig4.arm`), so a gesture is two numbers: the arm
that keeps making its point at the counter, the arm that stops halfway to the door and comes
back down.

## Beats

| time | set | caption | what happens |
|---|---|---|---|
| 0:00 | title | — | a `০৪` the height of the frame, kicker + the lesson underneath |
| 0:03 | shop | **দুই ভাই** | two brothers at one counter, marks already on the wall behind them |
| 0:15 | wall | **দাগ** | coral tallies multiplying across the plaster; the two shrink to figures |
| 0:27 | leave | **শেষ দিন** | the younger one stops arguing, puts the blue cup down, walks to the lit doorway |
| 0:36 | years | **দশ বছর** | the shop is wider, the counter is wider, one chair is empty |
| 0:44 | door | **দরজা** | night, a lit doorway, small bodies laughing inside; his arm rises and comes down |
| 1:00 | chair | **একা** | the wall still full of coral, the empty chair, the lamp, the cup |
| 1:07 | end card | — | **দেয়ালে দাগ রয়ে গেল। তর্ক করার লোকটা রইল না।** / তুমি দেখলে — এখন কী করবে? |

Speech: 51.96 s across 10 lines. `LEAD` 3.2 s title, `TAIL` 9.5 s end card, `GAP` 1.15 s.

## Voices

Two distinct voices, one per speaker — never a single narrator reading everything:

| speaker | voice | lines |
|---|---|---|
| narrator (বড় ভাইয়ের ভয়েস, বাইরে থেকে) | `voice-26` — masculine, narration | s01–s05, s07–s10 |
| ছোট ভাই | `voice-27` — masculine, characters | s06 — the only line he gets, and it ends every argument in the film |

The younger brother's line is on screen in coral-labelled text (`ছোট ভাই`), so the ear and
the eye agree about who just spoke.

## Score (`mix4.py`)

Synthesised, not sampled — a low drone at 55 Hz that breathes and never resolves; a
**pencil-on-plaster tick for every mark going up** while the wall fills; one soft door thud
when he leaves; three bursts of muffled laughter behind the lit door, panned right; and one
bell twice — the empty chair, then the end card. The bed ducks to 0.42 under every spoken
line, and the whole mix peaks at −3 dB.

## Rebuild

```bash
# 1. score + voice-over bed  (needs the ten takes in audio/)
python3 mix4.py                          # -> audio/mix.wav

# 2. picture, in segments — the box has 2 vCPU
python3 film4.py --seg 0    600 --out /tmp/a.mp4
python3 film4.py --seg 600 1200 --out /tmp/b.mp4
python3 film4.py --seg 1200 1800 --out /tmp/c.mp4

# 3. join picture, mux the mix
printf "file '/tmp/a.mp4'\nfile '/tmp/b.mp4'\nfile '/tmp/c.mp4'\n" > segs.txt
ffmpeg -y -f concat -safe 0 -i segs.txt -i audio/mix.wav \
       -c:v copy -c:a aac -b:a 160k -movflags +faststart dark-lesson-04-1080x1920.mp4
```

A single frame, for checking type and colour:

```bash
python3 film4.py --still 62.0 --out frames/chair.png
```

`--still` renders through the same `frame()` function the video does, so a still is a
guaranteed match for the frame at that timestamp. Rendering is deterministic: same
`film4.py` + same `audio/*.mp3` → byte-identical frames.

## Files

| file | what |
|---|---|
| `film4.py` | script, timeline, six sets, title/end cards, caption and subtitle type, render loop |
| `fig4.py` | the drawing kit — palette, capsule/poly/ellipse primitives, `person()`, `crowd_row()` |
| `deva.py` | Bangla shaping + layout (`deva.layout`, `deva.draw_text`), Noto Sans Bengali |
| `mix4.py` | ten VO takes + synthesised score → `audio/mix.wav` |
| `audio/s01…s10.mp3` | the ten voice takes, in timeline order |
| `01-script.md` | the script beat by beat, both languages, with the mixing notes |
| `preview-contact-sheet.png` | sixteen frames across the film, from the delivered mp4 |

## Note on runtime

This cut is **1:15.0** — a tight vertical short, three beats shorter than episode 3's 1:44.9.
The four extra beats that would push it back to series length (customers walking out, the
younger brother always stopping first, the shop growing without a second chair, the last
mark he doesn't draw) were written but their voice takes could not be generated in the same
session — the speech quota was spent on the ten takes above. Say the word and they go in as
`01-script.md` § *Extended cut* describes.
