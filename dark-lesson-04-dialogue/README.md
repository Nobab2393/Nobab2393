# অন্ধকার পাঠ ০৪ · শেষ কথা — কথ্য সংস্করণ / THE LAST WORD, in dialogue

The same episode as the narration cut, told as a conversation instead of a voice-over:
**five characters, five voices, ten turns**, no narrator. Vertical **1080×1920, 24 fps,
2:08.5**, Bangla speech and Bangla on-screen type.

**Deliverable:** `dark-lesson-04-dialogue-1080x1920.mp4` (H.264 High + AAC 160k stereo, faststart).

> দুই ভাইয়ের একটাই দোকান। প্রতিটা তর্কে বড় ভাই জেতে, দেয়ালে একটা লাল দাগ পড়ে। একদিন
> ছোট ভাই আর তর্ক করল না — শুধু বলল, *তুমি ঠিক*, আর কাপটা রেখে চলে গেল। দশ বছর পর বড়
> ভাই সেই দরজায় দাঁড়িয়ে শুনল ভেতরে হাসি, চায়ের শব্দ, অনেকগুলো কণ্ঠ। হাত তুলল, নামিয়ে নিল।

**No video model was used.** Rendering is local: `film5.py` draws every frame with PIL, then
H.264 in this box. MiniMax / Hailuo is not available in this environment — say the word if
you want a shot list prepared for an external video model instead.

---

## The cast, and who speaks

Five designs from `dark-lesson-04-last-word/cast/`, cut out and animated here.

| চরিত্র | voice | turns | tells |
|---|---|---|---|
| **বড় ভাই** — the elder brother | `voice-26` | 1, 4, 9, 10 | the ledger, the wall, the tally he chalks while he talks |
| **ছোট ভাই** — the younger brother | `voice-27` | 2, 5, 7 | the bag on his shoulder, the cup he sets down before he leaves |
| **পুরনো কাস্টমার** — a customer | `voice-30` | 3 | walks in mid-argument, waits, and leaves without buying |
| **বৌদি** — the younger brother's wife | `voice-28` | 6 | the lit doorway, the glass of tea at her waist |
| **ভাইঝি** — the niece | `voice-29` | 8 | opens the door ten years later, laughing |

Every character has their own voice — never one narrator reading everybody — and each turn
is panned to where that person stands on screen (elder left, niece right).

## The ten turns

| t | speaker | line |
|---|---|---|
| 0:03 | বড় ভাই | এই দামে কেউ কিনবে না। খাতায় লেখা আছে, নিজের চোখে দেখ… |
| 0:15 | ছোট ভাই | খাতা তোমার, দোকানও তোমার। আমি শুধু হিসাব মেলাই… |
| 0:25 | কাস্টমার | ভাই, আধা কেজি চাল দেন। দাম যা হয় বলবেন… |
| 0:34 | বড় ভাই | বসেন, বসেন। আগে এই কথাটা মিটুক। এই দেয়ালে যত দাগ… |
| 0:46 | ছোট ভাই | আর যতবার আমি চুপ করেছি, সেটা কেউ গোনে নাই… |
| 0:57 | বৌদি | তোমার ভাইয়ের সাথে তর্ক করে কী লাভ?… |
| 1:09 | ছোট ভাই | তুমি ঠিক। সবটাতেই তুমি ঠিক। দোকানটা তোমারই থাক… |
| 1:21 | ভাইঝি | চাচা! তুমি এলে? বাবা বলেছিল, তুমি কখনো আসবে না… |
| 1:35 | বড় ভাই | না রে, আমার দোকানে কাজ আছে… |
| 1:45 | বড় ভাই | দেয়ালে সব দাগ এখনো আছে। শুধু তর্ক করার লোকটা নেই… |

Full text, captions and mixing notes: `01-script.md`.

## How the mouths are synced

The lip movement is not a loop and not a guess. `film5.envelope()` decodes each of the ten
voice takes, cuts it into 24 loudness values per second, smooths them, and normalises them.
The speaker's mouth is an ink shape whose height is that number for that exact frame — so a
loud syllable opens it, a pause closes it, and silence closes it completely. Everyone else
on screen gets a closed mouth drawn back over their art, so only one person is ever talking.

On top of the mouth: the same envelope stretches the body by 0.4%, the speaker leans in
toward the listener at the start of their turn, listeners breathe on their own slow sine,
and the customer walks in and out on his own line.

## Colour, kept from the narration cut

| tone | value | meaning |
|---|---|---|
| paper | `#F0EEE6` | shop daylight |
| wall | `#DBD6CA` | the wall that keeps score |
| ink | `#1A1714` | outlines, night |
| coral | `#D97757` | **one won argument, tallied** — never on a body |
| blue | `#6A9BCC` | **the cup he leaves behind** — appears once, at 1:10 |

## Score (`mix5.py`, synthesised)

Low room tone at 58 Hz, a tick for every mark going up, one door thud when he leaves, and
a bell at the end card. The bed ducks to 0.40 under every spoken line; the whole mix peaks
at −3 dB.

## Rebuild

```bash
python3 mix5.py                 # ten takes -> audio/mix.wav
python3 film5.py --seg 0    1030 --out /tmp/a.mp4
python3 film5.py --seg 1030 2060 --out /tmp/b.mp4
python3 film5.py --seg 2060 3084 --out /tmp/c.mp4
printf "file '/tmp/a.mp4'\nfile '/tmp/b.mp4'\nfile '/tmp/c.mp4'\n" > segs.txt
ffmpeg -y -f concat -safe 0 -i segs.txt -i audio/mix.wav \
       -c:v copy -c:a aac -b:a 160k -movflags +faststart \
       dark-lesson-04-dialogue-1080x1920.mp4
```

A still: `python3 film5.py --still 33 --out frames/x.png` (same `frame()` as the render, so
a still is guaranteed to match).

## Files

| file | what |
|---|---|
| `film5.py` | script, timeline, four sets, stage blocking, mouth sync, cards, render |
| `sprites.py` | cuts the five cast designs out of their paper, writes `cast-mouths.json` |
| `cast-mouths.json` | each mouth's position and size, in source pixels — readable, editable |
| `mix5.py` | five voices + synthesised room, ducked bed → `audio/mix.wav` |
| `audio/d01…d10.mp3` | the ten takes, in timeline order |
| `fig5.py`, `deva.py` | drawing kit and Bangla shaping (harfbuzz, not PIL text) |
| `01-script.md` | the dialogue beat by beat, with mixing and sync notes |
| `preview-contact-sheet.png` | sixteen frames from the delivered mp4 |
