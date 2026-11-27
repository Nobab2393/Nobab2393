# এক পাড়ার মানুষ — one street, ten neighbours

Ten characters for one village street, in the Claude-2D house style: flat fills, even ink
outlines, paper `#F0EEE6`, one coral accent per person, no gradients, no texture.

| # | file | role | age | the read |
|---|---|---|---|---|
| 1 | `01-elder.png` | মোড়ল · elder | 74 | white beard, punjabi and lungi, the one who decides |
| 2 | `02-shopkeeper.png` | দোকানদার · shopkeeper | 48 | moustache, specs, coral-checked gamchha on the shoulder |
| 3 | `03-tailor.png` | দর্জি · tailor | 35 | tape round the neck, thin, patient |
| 4 | `04-boatman.png` | মাঝি · boatman | 30 | vest, lungi hitched, gamchha on the head, bare feet |
| 5 | `05-widow.png` | বিধবা · widow | 66 | white sari over the head, grey bun |
| 6 | `06-bride.png` | নববধূ · bride | 22 | mustard sari, coral border, bangles |
| 7 | `07-teacher.png` | শিক্ষিকা · teacher | 41 | round specs, canvas tote, brisk |
| 8 | `08-postman.png` | ডাকপিয়ন · postman | 28 | khaki, peaked cap, mail bag |
| 9 | `09-student.png` | ছাত্রী · student | 16 | two braids, salwar kameez, school bag |
| 10 | `10-moneylender.png` | মহাজন · moneylender | 56 | plump, half-moon specs, white shirt, dhoti |

`street-lineup.png` is the sheet: ten cards, Bangla role, English role, age and one-line
description, relative stature preserved.

## Files

- `[01–10]-*.png` — the generated plates, untouched
- `plates/` — cut out, trimmed, RGBA, exact paper background
- `build_street.py` — the cut and the sheet
- `deva.py` + `fonts/` — Bangla type as pixels (harfbuzz shaping; PIL here has no libraqm)

## The cut

Every figure wears off-white, and off-white is the paper. So the cut is geometric, not
chromatic: close the ink outline by 7 px so anti-aliased gaps seal, flood the **outside**
only, and keep everything inside the outline opaque. The same routine carries over to
`../stickman/prep_stick.py`.

## Next

- Face rigs (mouth cleared, eyes measured) so any of the ten can talk — `prep7b.py` in
  `dark-lesson-07-last-instalment/` is the template.
- Their first scene: the street at dawn, the shopkeeper opening up, the postman
  crossing with one letter for the moneylender.
