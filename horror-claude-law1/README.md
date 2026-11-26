# নিয়ম ১ — ভৌতিক পাঠ ২

A 2:00 Bangla horror short (1080×1920, 30 fps) starring the five
`characters-bd-claude` designs: five distinct voices, Bangla captions,
ducked score, and the same flat-vector language in the frame as in the
characters.

`horror-claude-law1-1080x1920.mp4` — 120.17 s, 3 605 frames, 15.65 MB,
h264 High + AAC 44.1 kHz stereo, peak −4.0 dB.

**Story.** One rule in this bazaar: after midnight, if someone behind you calls
your name, don't turn and don't answer — because the thing that calls has no face
of its own. Rafiq the rickshaw puller hears his name three times and keeps
pedalling. Rohima remembers the tailor who did answer: smooth, eyeless, still
walking, everyone greeting him by a different name. Tootu, seven years old and
unafraid, decides to answer whatever calls. Mim tells him there is no way back.
Rohima explains the trick — it calls in your mother's voice, saying exactly what
you said last. At midnight Tootu answers. Next morning he sits up, turns his face
to Mim, and speaks in **her** voice. Now the bazaar has five faces; one of them
belongs to nobody.

## কীভাবে বানানো হলো

Same renderer family as `horror-gona`, three things changed:

1. **No keying step.** The `characters-bd-claude` cut-outs are already
   transparent and trimmed, so a figure is just `alpha_composite`d with its feet
   on `FEET = 1330`. Relative heights are per-character (`CAST` table: rafiq 1.00,
   teacher 0.97, rohima 0.93, mim 0.86, tutu 0.72) so a seven-year-old does not
   stand as tall as the schoolmaster.
2. **The frame follows the character palette.** Ink ground `#0C0D0F`, cream type
   `#F0EEE6`, coral accent `#D97757`, sage/slate only in the set dressing. Flat
   props — a crescent moon, an awning with a scalloped hem, a lamp post with a
   coral bulb, motion streaks on the road, a grey dawn. No photographic
   gradients; the only soft edges are the vignette and the light bloom.
3. **Night tint.** Bright cream-ground sprites on black read as stickers, so
   each scene multiplies the figure by a cool tint (`(0.90, 0.93, 1.0)` at night,
   `(0.48, 0.53, 0.72)` for the answer beat) *and* a brightness factor.

## সময়রেখা (প্রোব করা)

```
NAR    [5.6, 18.7, 35.72, 51.08, 62.3, 74.06, 84.18, 89.82, 101.22]
DUR    [11.6, 15.12, 13.76, 9.52, 10.16, 8.12, 4.24, 9.8, 5.8]
BOUNDS [0, 18.35, 35.37, 50.73, 61.95, 73.71, 83.83, 89.47, 100.87, 107.77]
TOTAL  120.17
```

Bed: 43.6 Hz drone with a slow swell, air, clock ticks across lines 2–4, a
heartbeat from line 4 that speeds up after the answer, a riser into line 7, and
three stings (the answer, the morning, the five faces). The bed ducks to 0.55
under every line — speech sits at −19…−22 dB RMS, gaps at −24…−28 dB.

## যা ভুল হয়েছিল

- **The kite's white paper.** `c5-boy.png` has a large near-white patch behind the
  boy's raised arm (it reads as paper on cream). On a black frame it glowed like a
  hole, so the film's copy is recoloured: pale pixels inside
  `x 226–414, y 150–442` → `#D97757`. The sheet in `characters-bd-claude` is
  untouched.
- **First render was too bright.** At `dim≈1.0` a full-body sprite looks pasted
  on. Night figures now sit at tint × dim ≈ 0.62 of the drawn value.
- **The stall was a floating plank.** A horizontal board at chest height plus
  posts read as a fence through the character. Replaced with a beam, a cloth band
  and a `pieslice` scalloped hem — drawn *before* the figures, so it stays behind.
- **The dawn card was near-black.** Sky `(46,51,58)` was indistinguishable from
  the night scenes; now `(56,62,70)` with a pale sun disc and cloud bars.

## ফাইল

```
film.py                     renderer (--mix / --still / --seg / --join)
01-script.md               নয় লাইন, টাইমিং, কণ্ঠ
img/*-cut.png               পাঁচটি ক্যারেক্টার (c5-এর কাইট রঙ করা)
audio/v1…v9.mp3            নয়টি টেক
audio/mix.wav              ভয়েস + স্কোর (gitignored)
preview-contact-sheet.png ১২ ফ্রেম
```

Rebuild: `python3 film.py --mix`, then four `--seg` runs
(`0 900 / 900 1800 / 1800 2700 / 2700 3605`) and `--join`. ~4 minutes on two cores.
