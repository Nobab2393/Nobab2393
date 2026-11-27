# অন্ধকার পাঠ ০৬ · সই — কথ্য সংস্করণ
## DARK LESSON 06: THE SIGNATURE

The five cards you sent, in their own flat-pastel language: head-and-shoulder busts, a heavy
contour, a sun, a cloud, two hills. Ten turns of dialogue, five voices, no narrator.
**1080×1920, 24 fps, 2:04.**

**Deliverable** — `dark-lesson-06-signature-1080x1920.mp4` (H.264 High + AAC 160k stereo,
faststart, 12.4 MB).

> **On MiniMax:** no MiniMax/Hailuo tool exists in this environment, and no skill here calls
> one. The closest skill in the repo is `claude-animation-style`, and its rules are what this
> film follows (flat fills, one contour weight, no shading). Every frame is drawn by
> `film7.py` and encoded locally; the ten voices are the only external input.

---

## The story

An old man sits at the table he was born beside. His son has a bank loan in his own name and
one asset in his father's: the house. The daughter-in-law asks only that her fourteen years
in it be mentioned before the pen comes out. The paper man says the deed is clean. The
granddaughter asks the only useful question — *if you sign, where will you live?* — and the
answer is written into the deed: he stays until his last breath.

Then the paper man says out loud what everybody has been pretending: that condition will not
hold in any court. The old man signs anyway, and says why.

**কাগজে সব ঠিক লেখা ছিল। মানুষটার জায়গাটা লেখা ছিল না।**

---

## Cast and voices

| চরিত্র | who | voice | turns |
|---|---|---|---|
| **দাদা** | grandfather — glasses, white beard, red shawl | `voice-26` | 1, 6, 10 |
| **ছেলে** | the son — headband, green checked shirt | `voice-27` | 2, 7 |
| **বৌমা** | the daughter-in-law — bun, bindi, green/red saree | `voice-28` | 3 |
| **নাতনি** | the granddaughter — two buns, yellow polka frock | `voice-29` | 4, 8 |
| **কাগজওয়ালা** | the paper man — glasses, white kurta, blue placket | `voice-30` | 5, 9 |

## Timeline

| t | scene | speaker | line |
|---|---|---|---|
| 0:05 | ঘর | দাদা | এই টেবিলে আমার বাবা খেতেন… আজ তোরা কাগজ নিয়ে এসেছিস, চা নিয়ে আসিস নাই। |
| 0:16 | ঘর | ছেলে | ঋণটা আমার নামে। বাড়ি বেচে দিলে সব শোধ… |
| 0:27 | ঘর | বৌমা | এই ঘরে আমি চৌদ্দ বছর আছি। সই করার আগে আমার নামটা অন্তত শোনো। |
| 0:38 | উঠোন | নাতনি | দাদা, সই করলে তুমি থাকবে কোথায়? |
| 0:49 | উঠোন | কাগজওয়ালা | কাগজ সব ঠিক আছে, আমি নিজে দেখেছি। |
| 0:59 | উঠোন | দাদা | যে ঘরে তোর দাদি শেষ নিঃশ্বাস নিয়েছে, আমি সেই ঘরেই থাকব। |
| 1:09 | সন্ধ্যা | ছেলে | আমার কিছু করার নাই… আমাকে বাঁচতে দে। |
| 1:19 | সন্ধ্যা | নাতনি | কাগজে লেখো, দাদা এই ঘরে থাকবে। শেষ নিঃশ্বাস পর্যন্ত। |
| 1:30 | সন্ধ্যা | কাগজওয়ালা | এই শর্তটা আদালতে টিকবে না। দাদা, বুঝে সই করেন। |
| 1:44 | সই | দাদা | তাহলে সই করি। আমার নামে ঘর থাকল না, কারও দয়ার ঘরে থাকব না। |

Full Bangla text and blocking: `01-script.md`.

## What was built, and how

**The cards, cut out.** Each card is a black frame around a pastel sky with a bust standing
in it. `prep6.py` strips the frame, learns the card's own background from the two side
strips (where the figure can never reach), and takes the connected blob that touches the
bottom edge — that is the bust. Holes are filled, so glasses and gaps in cloth stay solid.
Saved as RGBA in `cast/`, plus `frames/proof-cast.png`.

**The flat bottom is the reason for the table.** A bust cut off at the chest would float, so
every scene has a foreground strip (a table edge in the room, a courtyard wall outside) and
the busts are tucked behind it. Nothing of the cut edge is ever visible.

**The mouths are the audio.** `envelope()` turns each take into a 24 loudness values per
second; the speaker's mouth is an ink shape whose width and height are that number. Above
0.30 a tongue appears — below that it stays shut. Mouth positions were measured from the
cards, then nudged down for the two moustached men so an open mouth never merges with the
tash; a proof sheet of all five, closed and open, was checked before rendering.

**Scenes, in the cards' own language.**

| scene | ground | light |
|---|---|---|
| **ঘর** | sand wall, a green window, a pendant lamp | morning indoors |
| **উঠোন** | sage sky, sun, cloud, two hills, a courtyard wall | bright, and the sun is high |
| **সন্ধ্যা** | rose sky, the sun already down behind the hills | dusk |
| **সই** | lilac sky, low sun, the old man alone, close | last light |

The last four seconds are a single insert of the deed itself: the nib loops out a signature,
an underline, and a red seal comes down on it.

## Sound (`mix7.py`)

Room tone, a low 62/93 Hz drone, a wall clock in the room (one tick a second, panned right),
four birds over the courtyard, paper handled at each change of place, the pen scratching
through the signature and the stamp coming down on the seal. The bed ducks to 0.42 under
every line; the mix peaks at −3 dB.

## Rebuild

```bash
python3 prep6.py                       # once: frame/sky/hills off, cast/*.png out
python3 mix7.py
python3 film7.py --seg 0    1000 --out /tmp/e6a.mp4
python3 film7.py --seg 1000 2000 --out /tmp/e6b.mp4
python3 film7.py --seg 2000 2978 --out /tmp/e6c.mp4
printf "file '/tmp/e6a.mp4'\nfile '/tmp/e6b.mp4'\nfile '/tmp/e6c.mp4'\n" > segs.txt
ffmpeg -y -f concat -safe 0 -i segs.txt -i audio/mix.wav \
       -c:v copy -c:a aac -b:a 160k -movflags +faststart \
       dark-lesson-06-signature-1080x1920.mp4
```

A still: `python3 film7.py --still 116 --out frames/x.png`.

| file | what |
|---|---|
| `prep6.py` | takes the five supplied cards apart, writes `cast/` |
| `film7.py` | script, timeline, four sets, blocking, mouth sync, cards, render |
| `sprites7.py` | the busts, their mouth map and patch colours |
| `mix7.py` | five voices + synthesised room → `audio/mix.wav` |
| `01-script.md` | the dialogue beat by beat |
| `preview-contact-sheet.png` | sixteen frames from the delivered file |
