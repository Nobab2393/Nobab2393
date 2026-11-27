# মঙ্গল কলোনি — the crew

**A standalone space story — five characters.** Mars, sixty years from now: a red-dust colony
of tin huts, a buried greenhouse, three rovers and a comms mast. Five people work the night
shift of the colony, and the tone is thriller, not fable — something in the colony is not
where it should be.

**Look: 1970s science-fiction comic.** Thick confident black ink outlines of even weight, flat
poster colours only — mustard yellow, burnt orange, cream, teal — solid black shadows, one flat
highlight band per surface, a hint of off-register print at the edges, faint paper tooth. No
gradients, no airbrush, no photorealism, no halftone dots.

Each plate is drawn on a flat pale sand field (with no drawn frame) so it trims cleanly and
drops onto a drawn set later.

**`sheets/lineup.png`** — five, one scale, feet on one line.
**`sheets/0N-*-card.png`** — one card per character, 900×1200, name and role in Bengali.
**`cast/0N-*-neutral.png`** — trimmed plate with the field knocked out (RGBA), ~1225 px tall.

## The five

| # | | age | role | the one thing you see first |
|---|---|---|---|---|
| 01 | রওশন আরা | 48 | কলোনি কমান্ডার | burnt-orange pressure suit, helmet under one arm, scar on the cheek |
| 02 | হাবিবুল্লাহ | 35 | ইঞ্জিনিয়ার | mustard overalls tied at the waist, goggles on the forehead, big wrench |
| 03 | ডা. তানিয়া সুলতানা | 31 | কলোনি ডাক্তার | cream smock over a teal suit, stethoscope, boxy medical case |
| 04 | জুয়েল রানা | 26 | পাইলট | orange flight jacket with mission patches, leather flying cap, goggles up |
| 05 | শিশির চন্দ্র | 19 | কমিউনিকেশন টেক | teal jumpsuit, headset, square antenna pack, spiral notebook |

They work the same shift; they do not all trust each other. That is the point of the crew.

## Stature

`STATURE` for the five: 01 `1.00` · 02 `1.02` · 03 `0.99` · 04 `1.02` · 05 `0.96`.

## How it is built

`sheets.py` drops a thin drawn frame if the plate has one (`deframe`), takes the field colour
from the corners, trims to the figure, knocks the field out to a solid alpha (threshold, then
flood the outside — a soft difference mask would make pale clothes translucent), scales every
figure to one height, and sets the Bengali names and roles through `deva.py` (harfbuzz shaping;
PIL here has no libraqm and would break the conjuncts).

```bash
python3 sheets.py            # -> cast/*.png, sheets/lineup.png, five cards
```

## Next

The story: a thriller for these five — hook, ten beats, the two-minute cut. Sets to draw: the
colony dome at night, the comms shack, the greenhouse, the rover bay, the dust outside.
