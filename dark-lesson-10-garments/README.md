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

## Status — পর্ব ১০ shipped

All ten plates are drawn and on the sheet. `dark-lesson-10-garments-1080x1920.mp4` —
2:00.62, 1080×1920, 24 fps, ten scenes, one narrator.

The episode: 9:10 p.m., shift over an hour ago, eight people still on the floor, the gate
chained from the outside, nine names on the roster — and a ninth body that nobody can
account for. The ninth name is never shown.

## The episode

```bash
python3 plan.py      # timeline: ten lines -> ten shots; prints the shot table
python3 film.py      # -> build/video-ship.mp4 (crf 24)
python3 mix.py       # -> build/mix.wav, then muxes the deliverable
python3 verify.py    # length, every cut's silence, every scene's first word
python3 contact.py   # -> dark-lesson-10-garments-contact.png
```

`plan.py` is the single source of truth for timing: ten narration files, one shot per
scene, each shot opening 80 ms before its line so that every cut falls in the silence
ahead of the first word. `film.py` stages the ten figures into the three plates
(`scene/bg-floor.png`, `bg-gate.png`, `bg-machine.png`) and walks them in and out at
`STEP = 0.46 s` — neutral plate, mid-stride plate, body bob, a little roll, shadow sliding
back. `mix.py` places the voice sample-exactly and builds the room: tone, a machine hum
that dies when the power goes, the relay, the chain, the gate, footsteps panned per walk.
`verify.py` measures the finished mp4, not the plan.

## How it is built

`build_sheets.py` is the same one used for the bank cast — trim against each plate's own
dominant paper colour, flood the paper away so no plate shows as a rectangle, scale every
figure to one height times a small `STATURE` factor, land all feet on one baseline, then set
the Bengali names and roles through `deva.py` (harfbuzz shaping; PIL here has no libraqm and
would break the conjuncts).

```bash
python3 build_sheets.py     # -> sheets/lineup.png + ten cards
```
