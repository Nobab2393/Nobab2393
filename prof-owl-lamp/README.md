# 🦉 The Lamp and the Owl / লণ্ঠন আর পেঁচা

A ~83-second vertical fable starring **Prof. Owl**, made in the **Claude flat-vector** style:
flat shapes, no gradients, ≤3 tones per panel, and exactly **one accent colour — coral — which
means only one thing: the flame**.

Bangle voice-over, English on-screen lines (no Bangla font in this sandbox, so on-screen type
stays English; the narration carries the Bangla).

## Watch

| File | What |
|---|---|
| `prof-owl-lamp-1080x1920.mp4` | final, 1080×1920 · 30 fps · h264 + AAC |
| `frames/sheet.png` | character sheet — Prof. Owl, the crow, the lantern in three states |
| `frames/scene1.png`…`scene7.png` | proof stills, one per block |
| `01-script.md` | full script, palette table, transition and sound spec |

## The fable

A road has one lamp. An old owl keeps it; nobody knows his name, everybody knows the light.
A young crow says the light is too dim and asks to hold it — “I'll burn it like the sky.”
The owl says only: *let's see.* The crow blows, the flame flares white, every window in the
village lights up, the crowd claps. Then the insects come for the light, the insects bring
the wind, the wind takes the flame, and the road goes dark. The owl relights one small flame
from the old wick — the same size as before. People come back, blame nobody, thank nobody.
The road is visible. That is enough.

> **THE LIGHT THAT SHOWS OFF GOES OUT.
> THE LIGHT THAT SHOWS THE WAY STAYS LIT.**

## Why it's built this way

- **One accent = one meaning.** Coral is the flame and nothing else. When the flame is
  overblown the frame floods coral; when it dies, coral leaves the frame completely. The
  colour does the story's argument without a word of explanation.
- **Every frame is a pure function of `t`.** No image model, no video model, no per-frame
  drift — the owl has the same glasses in frame 1 and frame 2 497.
- **The owl never gets the accent colour.** Not a scarf, not a lens, not a button. The
  character who does not show off is literally drawn without the colour of showing off.
- **Cuts are made of the subject.** Transitions are coral disc wipes, not fades.
- **Restraint is a number, not a mood.** The relight flame is set to exactly the scene-1
  size, so “the same” is something you can measure in the code.

## Cast

- **Prof. Owl** — ink egg body, ear tufts, cream eyes with movable pupils and a working
  blink, **round glasses**, **small grey scarf**, grey beak and feet. Reacts with one blink.
- **The crow** — leaner, `#3E3A35` body, `#302D29` wing, one bright eye, grey beak with an
  open wedge for shouting. Greedy, not villainous.
- **The lantern** — black post, glass box, coral flame inside, blurred RGBA glow layer.
  Three states: steady · flared · out.

## Palette

```
CREAM #F0EEE6   INK #191919   NIGHT #1B1A18
GREY  #C4BFB5   META #96908A
CORAL #D97757  ← the flame only     CORAL_HOT #F7BE84
```

## Rebuild

```bash
pip install pillow imageio-ffmpeg --break-system-packages
python3 build.py --sheet                 # character sheet
python3 build.py --test                  # 3 proof stills
python3 build.py                         # full render (~5 min, 2 500 frames, S=2 supersample)
```

`build.py` probes the seven Bangla TTS clips, builds the timeline
(`COLD 1.40 · GAP 0.80 · TAIL 4.20`), mixes the audio, then pipes raw RGB frames straight
into ffmpeg — nothing intermediate is written to disk except a handful of proof stills.
