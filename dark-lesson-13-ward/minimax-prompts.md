# MiniMax (Hailuo 2.3 / H3) shot pack — অন্ধকার পাঠ · পর্ব ১৩ «ঘণ্টা»

The sandbox has no MiniMax endpoint, so the shipped film (`dark-lesson-13-ward-1080x1920.mp4`)
was rendered with the local puppet pipeline. This file is the *same edit* written for MiniMax:
fourteen clips, the timings measured from `plan.py`, the narration line that plays over each,
one still prompt (to seed image-to-video) and one motion prompt in Hailuo's house grammar.

**How to run it**

1. Generate each still with `image_generation` (or reuse the plates in `scene/` and `cast/`,
   which are already in the same noir idiom — image-to-video keeps the faces consistent).
2. Feed still + motion prompt to Hailuo 2.3, duration = the shot length below (round up to the
   nearest 6 s/10 s preset and trim), 16:9 vertical **720×1280 or 1080×1920**, seed fixed per
   shot so retries stay on model.
3. Cut every generated clip to the exact in/out below against `build/mix.wav` (120.500 s).
   The voice is already placed sample-exactly in that mix; do not re-time the audio.
4. Global style token, put it at the front of every motion prompt:
   `black-and-white film-noir 2D animation, crisp black ink line, flat greys only, hard key light from upper left, sharp-edged shadows, thin white rim light on left edges, no colour, no gradients, no halftone`
5. Global negative prompt for every shot:
   `colour, sepia tint, gradients, airbrush, halftone dots, photographic texture, lens flare, blooming highlights, extra fingers, extra limbs, warped faces, text, subtitles, watermark, camera shake, fast cuts`

---

## Clip table

| # | id | in | out | len | narration |
|---|---|---|---|---|---|
| 1 | p0 | 0.00 | 5.17 | 5.17 | — (cold open) |
| 2 | p1 | 5.17 | 9.92 | 4.75 | — |
| 3 | s1a | 9.92 | 21.42 | 11.50 | line 1 |
| 4 | s2a | 21.42 | 31.17 | 9.75 | line 2 |
| 5 | s3a | 31.17 | 41.38 | 10.21 | line 3 |
| 6 | s4a | 41.38 | 51.29 | 9.91 | line 4 |
| 7 | s5a | 51.29 | 62.08 | 10.79 | line 5 |
| 8 | s6a | 62.08 | 72.79 | 10.71 | line 6 |
| 9 | s7a | 72.79 | 82.21 | 9.42 | line 7 |
| 10 | s8a | 82.21 | 93.17 | 10.96 | line 8 |
| 11 | s9a | 93.17 | 105.29 | 12.12 | line 9 |
| 12 | s10a | 105.29 | 115.17 | 9.88 | line 10 |
| 13 | out | 115.17 | 117.71 | 2.54 | — |
| 14 | card | 117.71 | 120.50 | 2.79 | — |

---

## 1 · p0 — the ward, 2:10 (0.00–5.17)

**Still.** `Inside a government hospital ward at two in the morning, vertical 9:16: two rows of iron beds with thin sheets, one bed empty with its sheet folded, a folding screen, a barred window with moonlight at the left, the corridor doorway throwing one hard strip of light across the floor, a ceiling fan overhead, a wall clock reading 2:10, a nurse's desk at the lower right with a small brass hand-bell and an open register.` + style token.

**Motion (5 s).** `Slow push in down the ward aisle, camera height 1.4 m, no handheld. The ceiling fan turns slowly overhead. Dust hangs in the corridor light. The clock hand does not move. Nothing else moves; the room breathes. Hold the last frame.`

**Sound.** Fan, room tone, one distant door.

## 2 · p1 — the corridor (5.17–9.92)

**Still.** `An empty hospital corridor at night in vertical 9:16, tiled floor receding to a far door with a glowing panel, doors with small high windows, a long bench, a folded wheelchair, a steel trolley, one bare tube light throwing a hard pool of light in the middle distance while the foreground stays deep black.` + style token.

**Motion (5 s).** `Very slow dolly forward down the corridor. The tube light flickers once, hard on-off, at frame 60. Dust drifts through the pool of light. No people enter the frame.`

**Sound.** Trolley far off, room tone.

## 3 · s1a — five awake (9.92–21.42) · line 1

> রাত দুটো দশ। ওয়ার্ডে পাঁচজন জেগে, পাঁচজন আলাদা মানুষ। করিডোরে আলো জ্বলে, ভেতরে কারও মুখে একটা কথাও নেই, শুধু ফ্যানের শব্দ।

**Still.** `Five strangers stand apart in the ward aisle under the corridor light, full figures, vertical 9:16: a 34-year-old woman in a cotton saree with a shawl crossed over her arms, a lean 52-year-old ward boy in a faded white uniform with keys on his belt and a mop, a 29-year-old woman doctor in a white coat with a clipboard, a 21-year-old man with a plastered forearm in a sling and a leather jacket, a 70-year-old man in a checked shawl with a wheeled IV stand. They do not look at each other.` + style token.

**Motion (12 s).** `Static camera, slow breathing motion only. The five stand still and separate; each turns their head a few degrees at a different moment, never meeting anyone's eyes. The shawl of the woman moves slightly. The old man's drip bag sways a millimetre. The fan turns above. No walking, no gestures.`

**Sound.** Fan; five breaths; monitor beep at 2.4 s intervals.

## 4 · s2a — the corridor again (21.42–31.17) · line 2

**Still.** Same corridor plate as p1, now `seen from a lower angle, the pool of light empty, a faint scuff mark on the tiles where someone fell.`

**Motion (10 s).** `Slow lateral drift to the right along the wall, 30 cm only. The tube light settles. A door at the far end closes on its own with a click at second 6. Nobody appears. The scuff mark stays in frame.`

**Sound.** Door closing; trolley; room tone.

## 5 · s3a — the bell (31.17–41.38) · line 3

**Still.** `Extreme close of a hospital night-duty desk in vertical 9:16: a small old brass hand-bell on a folded newspaper, a thick register with a pen clipped to it, a glass of water, a steel tumbler, a table lamp with a paper shade throwing one hard cone of light; the right half of the frame in deep black.` + style token.

**Motion (10 s).** `Locked-off camera, macro. The lamp cone does not move; dust turns inside it. The bell's brass edge carries a single thin white highlight. At second 7 the bell rocks once, a quarter of a millimetre, and settles. No hand enters frame.`

**Sound.** Room tone; the first bell is heard later, not here.

## 6 · s4a — two lies (41.38–51.29) · line 4

> ওয়ার্ড বয় বলল, আমি সিঁড়িতে ছিলাম না। ঘণ্টা বাজল। ডাক্তার বলল, আমি ডিউটিতে ছিলাম। ঘণ্টা আবার বাজল।

**Still.** `Medium two-shot in the ward, vertical 9:16: the ward boy with his mop on the left, the woman doctor with her clipboard on the right, both lit hard from the corridor doorway, beds and screens behind them, the desk out of focus at frame right.` + style token.

**Motion (10 s).** `Static camera. The ward boy speaks (mouth moves, no audio) then looks down; at that instant the desk lamp at frame right flicks once and the bell on it shakes and settles. The doctor speaks and folds her arms; the same flick, the same shake. Shadows do not move.`

**Sound.** Bell at 2.9 s and 7.6 s.

## 7 · s5a — two more (51.29–62.08) · line 5

> রুমা বলল, আমি কিছু দেখিনি। তানভীর বলল, আমি এখানেই ছিলাম না — দুবারই ঘণ্টা। ওয়ার্ডের আলো যেন এক ধাপ কমে গেল।

**Still.** `Medium two-shot: the woman in the saree and the young man with the plastered arm in sling, facing the camera, the corridor light between them, a bedsheet edge in the foreground.` + style token.

**Motion (11 s).** `Static, then a single step: at second 6 the corridor light behind them dims by one clear step — the background goes a shade darker, the shadows stay hard — and stays there. The woman's hands tighten on her shawl; the young man's jaw moves but he says nothing. Two bell shakes off-screen, seen only as a flicker on the desk edge.`

**Sound.** Bell at 2.4 s and 7.0 s.

## 8 · s6a — the fifth ring (62.08–72.79) · line 6

> পাঁচবার বেজে গেল। করিম চুপ করে বসে ছিলেন, তারপর বললেন, চুপ থাকাটাও একটা কথা — আর সেই কথাটাও এখানে মিথ্যে।

**Still.** `The 70-year-old man in the checked shawl beside his wheeled IV stand, standing very still in the aisle, vertical 9:16, the ward dark behind him and one hard light on his face; a younger ward boy half out of frame behind him.` + style token.

**Motion (11 s).** `Slow push in to the old man's face over 8 seconds, 20 cm total. He lifts his head a few degrees and holds the camera's eye; his shawl does not move; the IV bag above him swings once and stops. Behind him the ward is nearly black.`

**Sound.** Fifth bell at 0.55 s; then the monitor beeps stop.

## 9 · s7a — the clock, the folded sheet (72.79–82.21) · line 7

**Still.** The desk plate again, `now framed tighter on the brass bell and the open register, the lamp cone shorter, the black at frame right larger.`

**Motion (9 s).** `Locked off. The register page turns by itself at second 5 — one flip, no hand. The bell does not move at all this time. Dust in the lamp cone.`

**Sound.** Page turn at 2.2 s; room tone; no bell.

## 10 · s8a — the first truth (82.21–93.17) · line 8

> রুমা উঠে দাঁড়াল। বলল, আমি ফোনে ছিলাম, ডাক শুনেও উঠিনি, সাহস পাইনি। ঘণ্টা বাজল না — প্রথমবার বাজল না।

**Still.** `The woman in the saree standing alone in the middle of the ward aisle, facing the camera, hands at her sides, the ward behind her in near darkness, one hard light on her from the corridor.` + style token.

**Motion (11 s).** `She stands, straightens her shawl over both shoulders, and speaks to the room; the camera holds. No push, no shake. At the moment she finishes, hold two full seconds of nothing — the room does not answer. The desk at frame right shows no movement at all.`

**Sound.** No bell. Room tone, fan, a distant trolley.

## 11 · s9a — three more (93.17–105.29) · line 9

> সেলিম বলল, আমি সিঁড়িতে ধূমপান করছিলাম। নাফিসা বলল, আমি ঘুমিয়ে ছিলাম। তানভীর বলল, আমি দেখেও চলে গিয়েছিলাম। ঘণ্টা চুপ।

**Still.** `Three of them in the aisle, vertical 9:16: the ward boy, the woman doctor, the young man with the sling, standing in a loose line facing camera, each lit from a different angle, beds and a screen behind.` + style token.

**Motion (12 s).** `Static camera. One at a time, left to right, each speaks a short sentence and looks down: the mop handle tips and he catches it; the doctor closes her clipboard; the young man touches his plastered arm. Between each, half a beat of silence. Nothing rings.`

**Sound.** No bell at all.

## 12 · s10a — dawn (105.29–115.17) · line 10

> ভোরের আলোয় ওয়ার্ড সাদা হয়ে গেল। যে টুকু চেপে রাখো, সেটাই একদিন ঘণ্টার মতো বেজে ওঠে — আর চুপ থাকাও একটা মিথ্যে।

**Still.** `The same ward at first light in vertical 9:16: hard bars of dawn light through the barred window falling across the tiled floor and the beds, one empty bed with its sheet folded square at the foot, the desk at lower right with the register and the brass bell, the corridor doorway now dark by comparison.` + style token.

**Motion (10 s).** `The light bars on the floor stretch slowly as the sun comes up — a continuous, even widening. Dust turns in the beam. The empty bed's folded sheet is perfectly still. The bell does not move.`

**Sound.** Birds outside; fan; one distant beep at 1.4 s.

## 13 · out — the empty ward (115.17–117.71)

**Still.** Same as s10a, wider.

**Motion (3 s).** `Hold, or a 10 cm drift left. Nothing moves but the dust.` (Generate 6 s, use the last 3.)

## 14 · card (117.71–120.50)

Built in code, not generated: black card, Bengali title «ঘণ্টা», series line «অন্ধকার পাঠ · পর্ব ১৩»,
moral «চুপ থাকাও একটা মিথ্যে». If generating instead, do it as a still with no motion:
`black card, thick cream Bengali lettering, film grain, no imagery` — and set the type in code
anyway, because Hailuo cannot spell Bengali.

---

## Continuity rules for the whole film

- The bell is **never** touched by a hand on camera. It moves by itself, exactly five times.
- The clock reads 2:10 in every shot until the dawn shot, where it is out of frame.
- Only two things ever brighten: the corridor light in s5 (it dims) and the window in s10 (it floods).
- Everyone stays in the same clothes, the same plaster cast on the same arm, the same shawl on
  the same shoulder, across all fourteen clips — seed-lock the reference still per character.
- No shot has more than one camera move, and no camera shake anywhere.
