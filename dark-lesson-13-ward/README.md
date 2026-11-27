# রাতের ওয়ার্ড — the night ward

**Dark Lesson 13 — cast.** A government hospital ward at two in the morning. Five people
who have never met: a woman keeping watch over a patient, the ward boy, the intern on night
duty, a boy with his arm in plaster, and an old man who has walked his drip stand to the end
of the row. The corridor light stays on. Something in the ward does not add up — and it is
not the machines.

**Look: black-and-white film noir.** Crisp black ink line, shading in four flat steps only —
paper white, two mid greys, one deep black — with the key light hard from the upper left so
every shadow has a drawn edge, and a thin white rim light down each figure's left side. No
colour anywhere, no gradients, no airbrush, no halftone dots. Night light: corridor strip,
window moon, the green glow of a monitor drawn as grey.

Each plate is drawn on a flat pale grey field so it trims cleanly and drops onto a drawn set.

**`sheets/lineup.png`** — five, one scale, feet on one line.
**`sheets/0N-*-card.png`** — one card per character, 900×1200, name and role in Bengali.
**`cast/0N-*-neutral.png`** — trimmed plate with the field knocked out (RGBA), ~1225 px tall.

## The five

| # | | age | role | the one thing you see first |
|---|---|---|---|---|
| 01 | রুমা বেগম | 34 | রোগীর দেখাশোনায় | cotton saree, shawl crossed over both arms, cloth bag in one hand |
| 02 | সেলিম মিয়া | 52 | ওয়ার্ড বয় | faded white uniform, keys on the belt, mop held like a stick |
| 03 | ডা. নাফিসা রহমান | 29 | ইন্টার্ন ডাক্তার | white coat, stethoscope, clipboard held to the chest |
| 04 | তানভীর হোসেন | 21 | দুর্ঘটনার রোগী | leather jacket, plastered forearm in a sling, cut taped above one brow |
| 05 | করিম মিয়া | 70 | বৃদ্ধ রোগী | checked shawl, dhoti, one hand on a wheeled IV stand |

They do not know each other. That is the point of the cast.

## Stature

`STATURE` for the five: 01 `1.00` · 02 `1.00` · 03 `1.00` · 04 `1.02` · 05 `0.98`
(the old man is bent, not small).

## How it is built

`sheets.py` takes the field colour from each plate's four corners, trims to the figure, keeps
the largest blob, knocks the field out to alpha, scales every figure to one height, and sets
the Bengali names and roles through `deva.py` (harfbuzz shaping — PIL here has no libraqm and
would break the conjuncts).

```bash
python3 sheets.py            # -> cast/*.png, sheets/lineup.png, five cards
```

## Where the MiniMax cut comes in

The sandbox has no MiniMax Hailuo/H3 endpoint, so the film itself is rendered here with the
same pipeline as 9–12. `minimax-prompts.md` holds the shot pack — for each of the twelve
shots: a still prompt (the plates and sets above), a motion prompt written in Hailuo's
house grammar (camera move, subject action, light, duration), the narration line and the
measured timecode — so the identical edit can be generated on MiniMax and cut against the
same `build/mix.wav`.

## The film

**ঘণ্টা (The Bell).** Two in the morning in a government hospital ward. Five strangers are
awake: a woman keeping watch over a patient, the ward boy, the intern on nights, a boy with
his arm in plaster, an old man with a drip stand. The night before, an old man fell in that
corridor and nobody came. On the nurses' desk there is an old brass hand-bell, and tonight
every lie told in the ward rings it once — two lies, two rings; two more, two more; the fifth
stops the monitor. The old man says the quiet part out loud. Then Ruma stands up, says what
she did, and the bell does not ring. One by one the others say it too. By dawn the ward is
white.

> চুপ থাকাও একটা মিথ্যে।

- `01-script.md` — the ten scenes, the lines, the staging notes.
- `lines.py` — the ten narration lines, source of truth for the recording.
- `audio/scene01…10.mp3` — one narrator, conversational, 106 s of speech.
- `plan.py` — timeline: 14 shots, every cut inside the silence before its line.
- `film.py` — the renderer: noir plates on drawn sets, breath and head turns, contact
  shadows, a grade that steps the ward down with every lie and lets the dawn in at the end.
- `mix.py` — the fan, the monitor beeping to nobody, the corridor, and the five rings.
- `verify.py` — measures the finished mp4: length, drift, every cut, every entry.
- `contact.py` — the twelve-frame contact sheet.
- `minimax-prompts.md` — the same film as fourteen Hailuo/H3 clips: still prompt, motion
  prompt, duration and timecode per shot, continuity rules.

```bash
python3 plan.py
python3 mix.py --no-mux      # -> build/mix.wav
python3 film.py --crf 24     # -> build/video.mp4
python3 mix.py               # mux -> dark-lesson-13-ward-1080x1920.mp4
python3 verify.py
python3 contact.py
```

## Status

Rendered and checked. 2892 frames at 24 fps — 120.500 s of picture against 120.500 s of
audio, drift 0.0 ms; all ten cuts sit in silence, the worst first word lands 80 ms after its
shot opens.

- `dark-lesson-13-ward-1080x1920.mp4` — 1080×1920, h264 + aac, 120.5 s
- `dark-lesson-13-ward-720x1280.mp4` — 720×1280, lighter
- `dark-lesson-13-ward-contact.png` — twelve frames, 0:00 to 1:58
