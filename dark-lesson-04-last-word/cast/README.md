# চরিত্র · অন্ধকার পাঠ ০৪ — the five people in *শেষ কথা*

Five character designs for episode 4, drawn in the same flat-vector grammar as the film:
thick uniform ink outline, flat fills, no gradients, no shading, no texture, no faces faked
on top of a silhouette system — these are the *design* pass, the film itself stays
silhouette-driven.

**Sheet:** `cast-sheet.png` (2500×1720) — five figures on one baseline, Bangla names and
roles in the film's own type, and the film's palette underneath.

| # | file | চরিত্র | who they are in the story | the one gesture that carries them |
|---|---|---|---|---|
| ১ | `c1-elder-brother.png` | **বড় ভাই** | the elder brother, 47 — wins every argument for ten years | right arm up, index finger pointing: still making the point after everyone left |
| ২ | `c2-younger-brother.png` | **ছোট ভাই** | the younger brother, 39 — listens, stops first, leaves | both hands down at his sides, eyes lowered: nothing raised, nothing owed |
| ৩ | `c3-boudi.png` | **বৌদি** | his wife, 35 — the house behind the lit door | a glass of tea held out at waist height, offered before you ask |
| ৪ | `c5-old-customer.png` | **পুরনো কাস্টমার** | a customer, 66 — stopped coming to the shop years ago | weight on a stick, shopping bag hanging: the walk he no longer makes |
| ৫ | `c4-niece.png` | **ভাইঝি** | his daughter, 9 — the laugh on the other side of the door | one hand up in a wave, a folded kite in the other |

Sheet order is story order: the two brothers, the house, the man who stopped coming, the
child who is the reason the house is loud.

## The rules these were drawn to

- **Five colours, no more** — paper `#F0EEE6`, ink `#1A1714`, wall `#DBD6CA`, mid grey
  `#8E887C`, plus one skin tone `#C98B62` shared by all five (it is the same family).
- **Coral `#D97757` is never clothing.** In the film it means one thing — an argument won,
  tallied on the wall. On this sheet it exists only in the palette row, labelled.
- **Blue `#6A9BCC` is one object.** The blue tumbler stands on the counter in
  `c2-younger-brother.png` — the cup he leaves behind, the only blue in the episode. The
  sheet crops to the person, so the cup shows in the full character file, not on the sheet.
- **Outline weight is constant** — about 4 px at 1080 width, the same as the film's
  `fig4.py` ink, so these read as stills from the same drawing kit.
- **No face on the film, a face on the sheet.** The film's people are silhouettes because a
  code-drawn face cannot hold a repeatable expression; these sheets exist so the two
  brothers have a *fixed* face, build and wardrobe to design gestures against.

## Rebuild the sheet

```bash
cd dark-lesson-04-last-word
python3 cast/flatten.py         # snap the renders onto the five colours, in place
python3 cast/make_sheet.py      # -> cast/cast-sheet.png
```

`flatten.py` is the reason the files are honest: the image model returns art that is
*nearly* flat — paper at `#EDEDE1` here, `#EFECE3` there, a few thousand in-between greys.
Every pixel within 24 of a palette entry is pulled onto that exact value (99% of them),
which leaves only the anti-aliased edges alone. After that the paper is exactly `#F0EEE6`,
so `make_sheet.py` can flood-fill the background from the frame corners and keep the
off-white kurta solid instead of punching through it.

`make_sheet.py` then crops each figure out of its own paper, drops the baked-in ground line,
places everyone on one shared baseline at proportional heights (elder tallest, child
shortest), labels them with `deva.py` (harfbuzz shaping — not PIL's raw text), and prints
the palette with hex values.

Colour check on any single file:

```bash
python3 - <<'EOF'
from PIL import Image
from collections import Counter
im = Image.open("cast/c1-elder-brother.png").convert("RGB")
print(Counter(im.getdata()).most_common(8))
EOF
```
