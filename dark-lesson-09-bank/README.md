# এক শাখা, দশ জন — one branch, ten people

**Dark Lesson 09 — cast.** A Dhaka bank branch, drawn as a woodcut. Ten characters,
full figure, on cream paper, with Bangla names and roles. Episode 9 is silent — nobody
speaks on camera — so the mouths are drawn closed and the faces carry the work.

**`sheets/lineup.png`** — all ten, one scale, feet on one line: 1900×1780.
**`sheets/NN-name-card.png`** — one card per character, 900×1200, name and role in Bengali.

## The ten

| # | name | English | age | role |
|---|---|---|---|---|
| 01 | শিরিন আক্তার | Shirin Akter | 38 | শাখা ব্যবস্থাপক — branch manager |
| 02 | রোকেয়া বেগম | Rokeya Begum | 47 | প্রধান ক্যাশিয়ার — head cashier |
| 03 | নাসরিন সুলতানা | Nasrin Sultana | 29 | অ্যাকাউন্ট ডেস্ক — account desk |
| 04 | তাসলিমা খাতুন | Taslima Khatun | 34 | ঋণ কর্মকর্তা — loan officer |
| 05 | পারভীন আক্তার | Parveen Akter | 52 | ক্লিয়ারিং — clearing |
| 06 | সুমাইয়া ইসলাম | Sumaiya Islam | 23 | প্রবেশনারি অফিসার — probationary officer |
| 07 | ফরিদা ইয়াসমিন | Farida Yasmin | 44 | হিসাব রক্ষক — accountant |
| 08 | হাবিবুর রহমান | Habibur Rahman | 58 | নিরাপত্তা প্রহরী — security guard |
| 09 | কামরুল হাসান | Kamrul Hasan | 31 | আইটি ও জেনারেল ব্যাংকিং — IT |
| 10 | জাহাঙ্গীর আলম | Jahangir Alam | 60 | অফিস সহায়ক — office assistant |

Seven women, three men. The branch is run by women and cleaned up after by a man who has
been there longer than the manager has been alive — that is the whole social map of the
place, and it is meant to be visible in a single row.

## The look

Screenprint, three inks and nothing else: **black, deep indigo, brick red** on warm cream
paper, with grey used only as a tint of black. Heavy hand-cut contours, visible
woodgrain, halftone dots in the shadows, misregistration at the edges. No gradients, no
soft light, no background — every figure stands on bare paper so the set can be composed
around it later.

## How it is built

`build_sheets.py` does all of it:

1. **trim** — the paper colour is the plate's dominant colour (not its edge: some plates
   carry a thin white margin or a dark rule, and the guard's has both), then a binary
   mask is median-filtered so paper grain and dust cannot hold the frame open.
2. **key** — the paper is flooded away from the four corners with a 40-point tolerance,
   so a plate can be laid on the sheet's own cream instead of showing as a rectangle.
   Only paper the flood can reach is removed, so a white blouse inside an ink outline
   survives.
3. **scale** — ten drawings of ten different sizes are impossible to compare, so each is
   scaled to one height times a small `STATURE` factor (0.90 for the 52-year-old clerk,
   1.0 for the 34-year-old loan officer) and all feet land on the same baseline.
4. **set** — names and roles are painted with `deva.py` (harfbuzz shaping + fontTools
   outlines), because PIL here has no libraqm and would set Bangla as broken glyphs.

```bash
python3 build_sheets.py        # -> sheets/lineup.png + ten cards
```

## Expressions

Four expressions per character were generated for each of the ten — neutral, speaking,
angry, grieving — by editing each character's own neutral plate, so the face, saree and
jewellery stay put while only the expression changes. Four-up sheets exist for 01 and 02
(`sheets/01-shirin-sheet.png`, `sheets/02-rokeya-sheet.png`). The rest of that set was
dropped when the brief became ten portraits; the leftover expression plates stay in
`raw/` for whenever the episode needs them.
