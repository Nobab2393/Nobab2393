# অন্ধকার পাঠ ০৫ · আঙুলের ছাপ — কথ্য সংস্করণ
## DARK LESSON 05: THE THUMBPRINT

Five faces, five voices, ten turns of dialogue, no narrator. **1080×1920, 24 fps, 2:03**,
Bangla speech, Bangla on-screen type. Vertical, conversational, built to be watched with
the sound on.

**Deliverable** — `dark-lesson-05-thumbprint-1080x1920.mp4` (H.264 High + AAC 160k stereo,
faststart, 13.3 MB).

> **On MiniMax:** there is no MiniMax/Hailuo tool in this environment. Nothing in this film
> came from a video model. Every frame is drawn in code by `film6.py` and encoded locally;
> the voices are the only external input.

---

## The story

বাকিতে চাল নিতে গিয়ে রিকশাচালক একটা খাতায় আঙুলের ছাপ দেয়। পড়তে জানে না, তাই কথাটাই
তার কাছে সত্যি — চার মাসের বাকি, একসাথে শোধ। কিন্তু খাতার লেখায় ছিল অন্য কথা: বাকি না
দিলে রিকশাটাই দোকানদারের। সাত মাস পরে সে দাবি করে, আইন তার পাশে। মেয়েটি সব পড়ে ফেলে,
কিন্তু দেরি হয়ে গেছে। পাশ দিয়ে যায় এক ভিডিওওয়ালা — ক্যামেরা তোলে, বলে "এটা ভাইরাল হবে"।
একটা বুড়ো চাচা ক্যামেরা নামাতে বলে, কিন্তু কারও কথা কেউ শোনে না।

দুই দিনে চল্লিশ লাখ মানুষ ভিডিওটা দেখে। রিকশা ফেরত আসে না। কেউ একটা টাকাও দেয় না।

**একটা ছাপ। সারা জীবনের জমানো বন্ধ।**

---

## Cast and voices

Five designs from `../bangla-reel-cast/`, cut on their own alpha and animated here.

| চরিত্র | who | voice | turns |
|---|---|---|---|
| **দোকানদার** | the shopkeeper — saree, ledger, hard calm | `voice-28` | 1, 5, 9 |
| **রিকশাচালক** | the rickshaw puller — vest, gamcha, hand at his brow | `voice-30` | 2, 4 |
| **মেয়ে** | his daughter — braid, notebook, the only one who reads | `voice-29` | 3, 6 |
| **ভিডিওওয়ালা** | the man filming — phone up, mouth already open | `voice-27` | 7, 10 |
| **চাচা** | the old customer — cap, stick, forty years of tea | `voice-26` | 8 |

Each voice is panned to where that person stands: the puller sits left, the daughter and
the presenter right, the shopkeeper just off centre.

## Timeline

| t | scene | speaker | line (short) |
|---|---|---|---|
| 0:03 | দোকান | দোকানদার | বাকিতে নিবি? খাতায় আঙুলের ছাপ দে… |
| 0:13 | দোকান | রিকশাচালক | আমি পড়তে জানি না, বৌ… আঙুলের ছাপ দিলাম। |
| 0:25 | দোকান | মেয়ে | এখানে লেখা আছে — বাকি না দিলে রিকশাটা ওদের। |
| 0:37 | সাত মাস পর | রিকশাচালক | রিকশা আমার জান, মা… আমি শোধ দিব, দিবই। |
| 0:50 | সাত মাস পর | দোকানদার | আজ মেয়াদ। কাগজে যেটা লেখা, সেটাই সত্যি। |
| 1:00 | রাতের রাস্তা | মেয়ে | একটা ছাপ। শুধু একটা আঙুলের ছাপ। |
| 1:10 | রাতের রাস্তা | ভিডিওওয়ালা | এটা ভাইরাল হবে, বিশ্বাস করেন। |
| 1:20 | রাতের রাস্তা | চাচা | ক্যামেরাটা নামা… কেউ কখনো ছাপগুলো নিয়ে কথা বলে নি। |
| 1:33 | পরের সকাল | দোকানদার | আমি অন্যায় করি নাই। আইন আমার পাশে। |
| 1:42 | পরের সকাল | ভিডিওওয়ালা | চল্লিশ লাখ মানুষ দেখল। সবাই শুধু শেয়ার করল। |

Full Bangla text: `01-script.md`.

## The two things this film is built on

**1. The thumbprint.** One coral mark, `#D97757`, and it appears exactly twice: in the
ledger at 0:09 when he presses, and on the eviction notice in the morning shot, and on the
end card. It is the only saturated colour in the film — nothing else in frame competes with
it, which is why the eye finds it in the dark scene.

**2. The mouths follow the audio.** `envelope()` decodes each take, cuts it into 24
loudness values per second, smooths, normalises. The speaker's mouth is an ink shape whose
height is that number on that frame; under 0.04 it closes completely. Every listener's mouth
is painted shut (skin patch plus one thin lip line), because all five designs arrived drawn
mid-sentence — without that, four people would be talking at once.

Positions for those are not eyeballed: `sprites6.py` finds each mouth by scanning for the
dark interior cluster in the lower face and is verified against a proof sheet, and the mouth
is nudged down for the two moustached men so the open shape never merges with the tash.

## Sets

| scene | what is drawn |
|---|---|
| **দোকান** | her shop: door, four shelves of flat packets, counter, the open khata and the stamp pad |
| **সাত মাস পর** | the same room at dusk — the door is the only light, the bulb is on, the leaf has been turned |
| **রাতের রাস্তা** | night: poster wall, street lamp, the shutter down, his rickshaw parked where he left it |
| **পরের সকাল** | the shopfront closed, slats, one notice with a coral stamp, the bulb dead |

## Sound (`mix6.py`)

Room tone, a low 58/87 Hz drone, the **thud of the thumb** at 0:09 (the sound the film turns
on), a cycle bell in the street and another over the end card, two camera shutter clicks
while the presenter talks, and the metal shutter coming down before the last scene. The bed
ducks to 0.40 under every line; the mix peaks at −3 dB.

## Rebuild

```bash
python3 mix6.py
python3 film6.py --seg 0    1000 --out /tmp/e5a.mp4
python3 film6.py --seg 1000 2000 --out /tmp/e5b.mp4
python3 film6.py --seg 2000 2956 --out /tmp/e5c.mp4
printf "file '/tmp/e5a.mp4'\nfile '/tmp/e5b.mp4'\nfile '/tmp/e5c.mp4'\n" > segs.txt
ffmpeg -y -f concat -safe 0 -i segs.txt -i audio/mix.wav \
       -c:v copy -c:a aac -b:a 160k -movflags +faststart \
       dark-lesson-05-thumbprint-1080x1920.mp4
```

A still: `python3 film6.py --still 72 --out frames/x.png`.

| file | what |
|---|---|
| `film6.py` | script, timeline, four sets, blocking, mouth sync, cards, render |
| `sprites6.py` | the five cuts, their mouth map, per-face skin colour, night tint |
| `mix6.py` | five voices + synthesised street → `audio/mix.wav` |
| `cast/c1…c5.png` | the cut sprites this film stands on |
| `01-script.md` | the dialogue beat by beat |
| `preview-contact-sheet.png` | sixteen frames from the delivered file |
