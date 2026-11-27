# বাজারের আড়ত — the market warehouse

**Dark Lesson 12 — cast.** A wholesale market godown in daylight. Five strangers are shut
in when the back door is sealed from the street side; none of them knows the other four, and
the crates in the yard are counted in a way that does not add up.

**Look: 2D cel-shaded TV anime.** Crisp dark line art, three flat tones per surface — base,
one hard-edged shadow, one highlight band — and a thin white rim light down the figure's
left edge. Daylight from the left, so every shadow has a clean, drawn edge. No gradients, no
airbrush, no paper texture: this is a different family from the woodcut of 9–10 and the paper
cutout of 11.

Each plate is drawn on a flat pale cool-grey field so the figure trims cleanly and drops onto
a drawn set.

**`sheets/lineup.png`** — five, one scale, feet on one line.
**`sheets/0N-*-card.png`** — one card per character, 900×1200, name and role in Bengali.
**`cast/0N-*-neutral.png`** — trimmed plate with the field knocked out (RGBA), ~1225 px tall.

## The five

| # | | age | role | the one thing you see first |
|---|---|---|---|---|
| 01 | রাফি হাসান | 19 | ছাত্র | grey hoodie, earphone wire down his chest, worn sneakers |
| 02 | সাদিয়া আফরিন | 27 | নার্স | teal scrubs under a cream cardigan, stethoscope, ID badge |
| 03 | আনোয়ার হোসেন | 45 | পাইকারি ব্যবসায়ী | checked shirt, brick red gamchha, cloth ledger under one arm |
| 04 | আব্দুল কাদের | 68 | অবসরপ্রাপ্ত শিক্ষক | off-white kurta, prayer cap, wooden stick |
| 05 | মীম আক্তার | 15 | স্কুলের ছাত্রী | two braids with red ribbons, green frock, school bag |

They do not know each other. That is the point of the cast.

## Stature

`STATURE` for the five: 01 `1.02` · 02 `1.00` · 03 `0.99` · 04 `0.94` · 05 `0.90`.

## How it is built

`sheets.py` trims each plate against the field colour taken from its four corners, keeps the
largest blob, knocks the field out to alpha, scales every figure to one height, and sets the
Bengali names and roles through `deva.py` (harfbuzz shaping — PIL here has no libraqm and
would break the conjuncts).

```bash
python3 sheets.py            # -> cast/*.png, sheets/lineup.png, five cards
```

## Next

Story, hook, sets and the two-minute script are still to come. The world is chosen — a
market godown, daylight, a sealed back door — and the cast is five strangers.
