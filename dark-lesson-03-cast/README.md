# অন্ধকার পাঠ ০৩ · কেনা সম্মান — illustrated cut, 1:57.9

Same story as `../dark-lesson-03-bought-respect/` and `../dark-lesson-03-2d/`, but now told with
the five character designs from `../characters-bd/` used as **cut-out puppets**.

**`dark-lesson-03-cast-1080x1920.mp4`** — 1080 × 1920, 30 fps, 117.91 s (3537 frames),
13.3 MB, H.264 High + AAC stereo.

## Why a cut-out cut

The two earlier versions of this episode are drawn from primitives (`dark-lesson-03/` in cels,
`dark-lesson-03-2d/` in flat shapes). This one answers a different brief: *use the illustrated
characters*. So each PNG is keyed off its cream ground and treated as a paper puppet — breath,
sway, slide, tilt, dim — over a drawn set.

- `characters-bd/c1-patron.png` → **রফিক**, the man who pays for the village
- `c2-boy.png` → a customer / villager
- `c3-elder.png` → **বুড়ো**, the one who will not sell
- `c4-rickshaw.png` → **রিকশাওয়ালা**
- `c5-teastall.png` → **দোকানদার**

## Twelve beats, eleven scenes

| scene | in | out | what happens | on-screen |
|---|---|---|---|---|
| 1 | 0.00 | 11.41 | the tea stall, a tab nobody pays; two customers, one kettle | দোকানদার · আজ সবাই রফিক সাহেবের মেহমান |
| 2 | 11.41 | 23.00 | he arrives, the notes fly, the crowd bows in a stagger and the carets rise | রফিক · টাকা থাকলে সম্মানও থাকে |
| 3 | 23.00 | 34.27 | the stage edge, his name on the banner, the medal lands on his chest, applause | মঞ্চ, মাইকে নাম, বুকে রুপোর পদক |
| 4 | 34.27 | 43.78 | the elder hands the money back and it falls at his feet | বুড়ো · এই টাকা আমার দরকার নেই |
| 5 | 43.78 | 57.45 | he leans in — *তুমি কে?* — and gets the answer | রফিক · আমার টাকায় পুরো গ্রাম চলে — তুমি কে? / বুড়ো · যে সম্মান কিনতে হয়, সে সম্মান নয় — ভাড়া |
| 6 | 57.45 | 68.28 | the river climbs behind him, the ledger drifts | নদী ফুলে উঠল, খাতা শূন্য |
| 7 | 68.28 | 78.23 | morning; three villagers turn away | তারা আজ চোখ ফিরিয়ে নিল |
| 8 | 78.23 | 89.66 | the cup is pushed back across the counter | দোকানদার · বাকিতে দিই না / রিকশাওয়ালা · আজ আপনার ভাড়া নেব না |
| 9 | 89.66 | 98.29 | the elder crosses the frame with a glass of water | বুড়ো · কিছু না বলে এক গ্লাস পানি |
| 10 | 98.29 | 108.91 | the lesson, set as type | সম্মান কিনেছিলে, / তাই ভাড়াটে ছিল। / ভাড়া শেষ — সম্মানও শেষ। |
| 11 | 108.91 | 117.91 | end card | সম্মান কি সত্যিই কেনা যায়? + CTA |

## Voice

Ten takes, `audio/v1…v10.mp3`, one narrator (`voice-15`, the narrator of record for this line),
101.76 s of speech. One voice plays all five speakers: **identity is carried by the caption tag
and by who is lit in the frame**, not by timbre. If you want separate voices for রফিক / বুড়ো /
দোকানদার, that is a re-record of the same ten lines — the timeline re-derives itself from
whatever the takes measure (see below).

Timings are **probed, never hardcoded**:

```
NAR    = [1.60, 11.71, 23.30, 34.57, 44.08, 57.75, 68.58, 78.53, 89.96, 98.59]
BOUNDS = [0.00, 11.41, 23.00, 34.27, 43.78, 57.45, 68.28, 78.23, 89.66, 98.29, 108.91]
TOTAL  = 117.91
```

`NAR[k+1] = NAR[k] + dur + 0.55`; each cut lands 0.30 s before its line, so the caption is on
screen as the narrator starts. Change a take and captions, cuts and scenes follow.

## Build

```bash
python3 cast.py --mix
python3 cast.py --seg 0 900 /tmp/c1.mp4        # ~35 s per 900 frames on 2 vCPU
python3 cast.py --seg 900 1800 /tmp/c2.mp4
python3 cast.py --seg 1800 2700 /tmp/c3.mp4
python3 cast.py --seg 2700 3537 /tmp/c4.mp4
python3 cast.py --join /tmp/c1.mp4 /tmp/c2.mp4 /tmp/c3.mp4 /tmp/c4.mp4
```

`--still <t>` writes one frame for QA. `OUT=` overrides the output name — `--join` defaults to
`dark-lesson-03-cast-1080x1920.mp4`, so set it explicitly when experimenting.

## Two things that bit, worth knowing

1. **Keying.** A global colour-distance key punched holes in the patron's white pajama and the
   elder's kurta — they sit only ~14 levels off the paper. Flood-filling in from eight edge seeds
   removes the ground while leaving enclosed whites alone; then a 3×3 open/close kills the
   speckle the fill leaves on the silhouette. The baked ground shadow in each PNG is *kept* and
   every set is drawn on the same cream, so it reads as a shadow instead of a pale halo (on a
   darker floor it reads as a halo — that's why there are no dark scenes here).
2. **Two off-by-ones, both caught in stills.** The caption table was keyed as if the elder's
   reply had its own scene; and the scene scanner looped `len(BOUNDS) - 1`, so the end card was
   never reached — the lesson scene quietly covered the last nine seconds. Both were invisible
   in code review and obvious in a contact sheet.

## Typography

Bangla is shaped with harfbuzz + fontTools (`deva.py`, copied from the episode-3 build) because
this box has no libraqm; PIL's own text() would scatter the matras. Font: Noto Sans Bengali
(variable, `wght` 600/700). The end card's 👇 is drawn as an arrow — the font has no emoji glyph
and tofu is worse than a shape.
