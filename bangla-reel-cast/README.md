# পাঁচ মুখ · Bangla Reel Cast (Claude flat-vector)

Five Bangladeshi 2D characters drawn in the same flat-vector language as
`dark-lesson-04-last-word/cast/`, made to carry short vertical Reels: one face on screen,
one line of Bangla, no narrator needed.

**Deliverables**
- `cast-sheet.png` — all five on one baseline, labelled, with the palette (2500×1720)
- `c1-presenter.png` … `c5-elder.png` — full-frame designs, 1408×768
- `c1…c5-flat.png` — same frames, background forced to exact `#F0EEE6`
- `cut/c1…c5.png` — the figure alone, cropped, real alpha
- `hooks-bd.md` — all 47 hooks you sent, rewritten as Bangla on-screen lines, each matched
  to the character who should say it

> Generated with an image model, then flattened and cut locally. No video model was used.

## The five

| # | চরিত্র | who | prop that does the acting |
|---|---|---|---|
| 1 | **উপস্থাপক** — presenter, 27 | short hair, stubble, rolled sleeves | phone held up at chest height |
| 2 | **দোকানদার** — shopkeeper, 32 | saree, low bun, bindi, hand on hip | cloth ledger against her waist |
| 3 | **রিকশাচালক** — rickshaw puller, 48 | vest, lungi, gamcha | gamcha at his forehead, wiping sweat |
| 4 | **ছাত্রী** — student, 17 | braid, salwar kameez, dupatta, backpack strap | notebook and pen in both hands |
| 5 | **চাচা** — uncle, 66 | topi, white moustache, long kurta | walking stick, raised hand |

Each one is mid-motion rather than posing for a portrait — that is deliberate: a raised hand,
a towel at the forehead, a pen already moving. Those are the three things that can be
animated without redrawing the body.

## Style rules (kept, not approximated)

- flat shapes, hard vector edges — **no gradients, no shading, no hatching**, no grain
- **ink outline ≈ 4 px at 1408 px wide**, one weight everywhere, colour `#1A1714`
- **five colours plus paper**: paper `#F0EEE6`, ink `#1A1714`, off-white `#EDEAE2`,
  warm grey `#8E887C`, skin `#C98B62`/`#B87A4E`
- **one coral accent per figure, `#D97757`**, on one small object only — the phone's back,
  a saree border, a gamcha stripe, a notebook cover, a shawl edge
- generous negative space; eyes are solid ink dots with no highlights; no drop shadows

The first pass of the rickshaw puller came back with a bright red plaid gamcha — a sixth
colour and a pattern, both off-style. It was regenerated rather than shipped.

## Rebuild

```bash
python3 flatten.py      # exact paper + cut/<name>.png
python3 make_sheet.py   # cast-sheet.png
```

Needs `pillow`, `numpy`, `uharfbuzz`, `fonttools`; Bangla is shaped by `deva.py` with
`fonts/NotoSansBengali.ttf`, not by PIL's own text renderer.

## Using them

1. Pick a hook from `hooks-bd.md` (or write your own in the same shape).
2. Cast the character whose prop argues for the line — not the prettiest one.
3. Animate the prop and the mouth; the body can stay still for two seconds.
4. Keep the caption to two lines; the face is the first thing that has to move.
