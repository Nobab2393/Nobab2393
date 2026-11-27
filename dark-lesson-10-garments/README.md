# এক শিফট, দশ জন — one shift, ten people

**Dark Lesson 10 — cast.** A garment factory in Gazipur, drawn in the same woodcut as the
bank branch: three flat inks (black, deep indigo, brick red) on warm cream, hand-cut
contours, halftone in the shadows, full figure on bare paper.

Eight women and two men, nineteen to fifty-two. A factory floor is a place where the
people doing the work are almost all women and the people with the titles are not — that
is the map of the room, and it should be visible in a single row.

**`sheets/lineup.png`** — all ten, one scale, feet on one line.
**`sheets/0N-*-card.png`** — one card per character, 900×1200, name and role in Bengali.

## The ten

| # | | age | role | the one thing you see first |
|---|---|---|---|---|
| 01 | নাসিমা খাতুন | 48 | ফ্যাক্টরি ম্যানেজার | indigo saree, spectacles on a chain, badge |
| 02 | শাহানা পারভীন | 31 | লাইন সুপারভাইজার | polo shirt, whistle, bun, no jewellery |
| 03 | রেজাউল করিম | 41 | কাটিং মাস্টার | checked shirt, tape round the neck, chalk behind the ear |
| 04 | মরিয়ম বেগম | 24 | সেলাই অপারেটর | cream headscarf, black apron, two spools in the pocket |
| 05 | রুবিনা আক্তার | 19 | নতুন অপারেটর | dupatta over her head, braid, ID on a string |
| 06 | জোসনা ফেরদৌস | 27 | কোয়ালিটি চেকার | pen clipped to her blouse, slip in her waistband |
| 07 | রহিমা খাতুন | 45 | সিনিয়র অপারেটর | maroon saree, glass bangles, grey at the temples |
| 08 | ফিরোজা বেগম | 22 | কাটারের সহকারী | canvas apron stiff with dust, shears at her hip |
| 09 | নাজমা সুলতানা | 35 | প্রেসিং সেকশন | scorched apron, bandaged wrist |
| 10 | বাবুল মিয়া | 52 | মেশিন মেকানিক | blue coverall, oil at the knees, red gamchha |

## Status

Plates 01–07 are drawn and on the sheet. Plates 08, 09 and 10 are being re-shot: two came
back as multi-figure sheets instead of one figure, and the mechanic's plate arrived with a
drawn panel behind him instead of bare paper. The sheet keeps their labels in place until
the replacements land.

## How it is built

`build_sheets.py` is the same one used for the bank cast — trim against each plate's own
dominant paper colour, flood the paper away so no plate shows as a rectangle, scale every
figure to one height times a small `STATURE` factor, land all feet on one baseline, then set
the Bengali names and roles through `deva.py` (harfbuzz shaping; PIL here has no libraqm and
would break the conjuncts).

```bash
python3 build_sheets.py     # -> sheets/lineup.png + ten cards
```
