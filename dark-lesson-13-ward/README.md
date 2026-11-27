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

## Next

Story, hook, the ten lines and the two-minute timeline. The world is chosen — a ward at
night — and the cast is five strangers.
