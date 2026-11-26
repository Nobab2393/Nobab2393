# অন্ধকার পাঠ ০৩ · দুপুর — the same film, redrawn in the Claude animation style

Episode 3 of the *অন্ধকার পাঠ* series, second version. Same script, same voice-over, same
56.1 s — but staged as **flat-vector code-drawn motion graphics** instead of 3D cel
animation.

**Deliverable:** `dark-lesson-03-2d-1080x1920.mp4` — 1080×1920, **30 fps**, H.264 + AAC.

Built to the grammar in
[`../ai-video-skills/library/.claude/skills/claude-animation-style/SKILL.md`](../ai-video-skills/library/.claude/skills/claude-animation-style/SKILL.md)
and the timing tables in its `references/motion-grammar.md`.

---

## The rules, and where each one shows up

| Rule from the skill | How this film obeys it |
|---|---|
| **Every frame is a pure function of `t`** | `film2d.draw(t)` reads nothing but `t`; no RNG, no state, so any frame can be re-rendered alone (`--still 32.0`). |
| **Warm paper ground, warm near-black ink, no pure black or white** | `#F0EEE6` ground, `#FBF9F4` card, `#191919` ink, `#5C5A55` meta. |
| **One accent, one meaning** | Coral `#D97757` is **Ayan and nothing else** — not the sun, not the buttons in the story, not a single caption glyph. Where he is, is where your eye goes. |
| **A cool counterweight, used at most once** | Blue `#6A9BCC` appears for exactly one thing: **Mira**, from the moment she steps out of the ring. |
| **4–5 tones, no gradients** | Every surface is one flat plane; shadow is its own flat tone (`#DEDAD1`), never an alpha. |
| **Ground rotates between scenes** | paper → card → paper → darker paper → card → paper → card. Ink and accent never move. |
| **Spring entrances** | `ease_out_back` on every entrance; groups stagger 3 frames; nothing floats in. |
| **Element-carried transitions** | Each cut is a shape growing until it fills the frame and *becomes* the next ground: the bag, a shadow, the boy, a book, the long shadow, the button. No cross-dissolves. |
| **Type is architecture** | One giant `০৩` at the top of scene 1 (~22 % of frame height), captions of 1–4 words, drawn whole, sitting still while the world moves. |
| **Safe area** | All text inside x 60–1020, y 250–1600. |
| **One slow move per piece** | Scene 6 pushes in 5.5 % over its whole length; everything else snaps. |

## Why the characters are silhouettes

The skill is explicit that this look is *not* for faces: *"Faces, emotion, dialogue, character
continuity → needs image generation…, because code-drawn characters cannot hold a repeatable
identity"*. Rather than fake a face that would break the style, the film drops faces entirely
and puts **silhouette + colour** in charge of identity:

- **Ayan** — coral, carries the bag, the only warm accent in the film
- **Rafiq** — ink, the tallest, no props
- **Mira** — blue, the hood and scarf read in silhouette
- **everyone else** — a grey between ink and paper, so the crowd is scenery, not cast

That also makes the film's argument graphic rather than acted: five grey people each have
their own shadow plane, and the moment the coral and the blue shadows overlap they become one
shape — no dialogue, no close-up, just the union of two silhouettes.

## The seven beats

| # | scene | on-screen (1–4 words) |
|---|---|---|
| 1 | noon field, the giant ০৩ | দুপুরের রোদে সব পরিষ্কার |
| 2 | the bag goes down | ব্যাগটা মাটিতে পড়ল |
| 3 | the ring, shadows apart | সবাই দেখছিল, কেউ এগোল না |
| 4 | alone with the books | সে কিছু বলল না |
| 5 | one girl steps out | একজন এগিয়ে এল |
| 6 | emptying field, one long shadow | অন্ধকার আলোর অভাব, আলোর নয় |
| 7 | endcard, coral button | তুমি দেখেছিলে — / তারপর কী করলে? |

Full script and verbatim CTA: `../dark-lesson-03/01-script.md`.

## Files

| file | what it is |
|---|---|
| `flat.py` | the paper canvas: 2× supersampled flat shapes, ink lines, paper grain, no gradients |
| `rig2d.py` | the cut-out figure: 2-bone limbs, walk / kneel / reach poses, mono-silhouette mode |
| `film2d.py` | timeline, the seven scenes, the carried transitions, mix / segment / join |
| `deva.py`, `fonts/` | Bangla shaping + Noto Sans Bengali (variable weight) |
| `audio/v1..v7.mp3` | the same voice-over as the 3D episode |

## Rebuilding

```bash
python3 film2d.py --still 32.0      # one frame
python3 film2d.py --mix             # audio/mix.wav
python3 film2d.py --seg 0 842 segA.mp4
python3 film2d.py --seg 842 1683 segB.mp4
python3 film2d.py --join segA.mp4 segB.mp4
```

## Honest notes

- **The transitions are circular masks, not element morphs.** The circle starts at the
  element that carries the cut and is filled with the incoming ground, which is the spirit of
  the rule — but a real element-carried transition would have the *bag* stretch into the
  ground. That animation is not in this renderer.
- **No boil, no inbetweens.** This is cut-out animation: shapes move on eased curves, they
  don't squash, smear or redraw. At 30 fps with 12-frame settles it reads as motion graphics,
  which is the intent, but it is not hand-drawn animation.
- **One heavy grotesk is not available for Bangla.** The spec asks for a single heavy grotesk;
  the renderer uses Noto Sans Bengali at weight 800, which is the heaviest Bangla face on this
  box. Latin meta text would use a grotesk if one were installed.
- **Two accents, technically.** Coral is the accent; blue is the skill's "cool counterweight,
  used at most once" — spent on Mira for the last three scenes. If that counts as breaking the
  one-accent rule, make Mira grey and lose the colour coding.
- The voice-over was not transcribed back — there is no speech recogniser in this sandbox, so
  sync is verified by waveform and by ear only.

---

## Re-voiced with the new narrator (`voice-15`)

**`dark-lesson-03-2d-voice15-1080x1920.mp4`** — the same film, 1:08.34 instead of 56.1 s,
now read by the narrator of episode 3 of the *rich-dad* line (*কেনা সম্মান*), so the two
series share one voice.

The original narration was never committed as text — only as `audio/v1…v7.mp3` — so the
seven lines were **rewritten to the same beats** and recorded fresh in `audio-v15/`. If you
have the original script, paste it and the same pipeline re-renders it verbatim.

What changed under the hood:

- `VO_DIR=audio-v15` switches every read — takes, mix, timings — to the new voice-over.
- `NAR`, `BOUNDS` and `TOTAL` are no longer hardcoded: `_timings()` probes the takes and
  `_bounds()` derives the seven scene cuts from them. Pointed at the original `audio/`, it
  reproduces the old `[0.9, 7.07, 14.19, …]` and 56.10 s exactly, so the first cut still
  renders identically.
- The cel build (`../dark-lesson-03/film.py`) takes the same `VO_DIR` / `OUT` variables;
  it was not re-rendered here because it needs well over 25 minutes on 2 vCPU.

```bash
VO_DIR=audio-v15 python3 film2d.py --mix
VO_DIR=audio-v15 python3 film2d.py --seg 0 1025 /tmp/segA.mp4
VO_DIR=audio-v15 python3 film2d.py --seg 1025 2050 /tmp/segB.mp4
VO_DIR=audio-v15 OUT=dark-lesson-03-2d-voice15-1080x1920.mp4 \
  python3 film2d.py --join /tmp/segA.mp4 /tmp/segB.mp4
```
