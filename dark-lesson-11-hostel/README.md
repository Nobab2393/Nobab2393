# এক শিফট, দশ জন — one shift, ten people

**Dark Lesson 11 — cast.** A mofussil school hostel in the middle of the vacation. The rooms
are shut, the register is open on the table, and there are ten plates laid out in the dining
room — but only nine names on the list.

**Look: 2D cutout / puppet animation.** Every figure is built from separate flat paper
pieces with scissor-cut edges; the shoulders, elbows, hips and knees are joined by small
round paper fasteners that stay visible — the pins of an articulated puppet. A soft shadow
lifts each piece a millimetre off the stage. Fill: bold folk colour (brick red, mustard,
deep green, indigo, off-white), flat with no shading inside a piece, a faint paper fibre.
Faces are cut shapes: white almond eyes, a black pupil, a straight nose piece, a red mouth.

Each plate is drawn on one flat slate-blue-grey stage so the figure trims cleanly and can
be dropped onto a cutout set later.

**`sheets/lineup.png`** — one scale, feet on one line.
**`sheets/0N-*-card.png`** — one card per character, 900×1200, name and role in Bengali.
**`cast/0N-*-neutral.png`** — trimmed plate with the stage knocked out (RGBA), 1224 px tall.

## The ten

| # | | age | role | the one thing you see first |
|---|---|---|---|---|
| 01 | নূরজাহান বেগম | 54 | হোস্টেল ম্যাট্রন | brick saree, a ring of keys and a whistle at her waist |
| 02 | আফসানা আক্তার | 17 | দশম শ্রেণির ছাত্রী | one thick oiled braid, red sash, school shoes |
| 03 | মিজানুর রহমান | 58 | হোস্টেল সুপার | white shirt over a checked lungi, torch and register under one arm |
| 04 | শাহেদ আলী | 19 | একাদশ শ্রেণির ছাত্র | sleeves rolled, trousers short at the ankle, geometry box |
| 05 | রেবেকা খাতুন | 42 | হোস্টেলের রাঁধুনি | scorched apron, brass ladle, bare feet |
| 06 | তানভীর হাসান | 16 | নবম শ্রেণির ছাত্র | *to draw* |
| 07 | সুরাইয়া পারভীন | 31 | সহকারী শিক্ষিকা | *to draw* |
| 08 | কালাম শেখ | 25 | কেয়ারটেকার | *to draw* |
| 09 | জোবেদা বিবি | 60 | পুরনো আয়া | *to draw* |
| 10 | — | 20 | — | *to draw* — back turned, face never seen |

The tenth is the extra person: always in the frame, never facing the camera. The roster has
nine names; the room has ten bodies.

## Stature

`STATURE` ratios for the five drawn: 01 `0.96` · 02 `0.98` · 03 `1.04` · 04 `1.06` · 05 `0.99`.

## How it is built

`sheets.py` trims each plate against the stage colour taken from its four corners, keeps the
largest blob, knocks the stage out to alpha, scales every figure to one height, and sets the
Bengali names and roles through `deva.py` (harfbuzz shaping — PIL here has no libraqm and
would break the conjuncts).

```bash
python3 sheets.py            # -> cast/*.png, sheets/lineup.png, ten cards
```
