# এগারোটা এগারো — part 1 · prompt pack (Hailuo / Veo / Kling / Runway)

The film in this folder is drawn and rendered locally (no video-model API in this sandbox), so this
pack is the same 28 shots written for a generative model. Feed one row per clip, 4–6 s each, and cut
on the narration pauses listed at the bottom.

## Global tokens — put these on every prompt

```
2D cel-shaded animation, TV-animation finish, flat base colours with exactly two shadow tones and a
cold blue rim light, bold black contour lines of uneven weight, painterly-flat night interiors with
warm amber practical lamps, South Asian (Bangladeshi) cast, vertical 9:16, shallow depth of field,
film grain, no on-screen text
```

**Negative:** `3d render, cgi, photoreal, glossy skin, gradient shading, airbrush, extra fingers,
extra limbs, deformed hands, western faces, text, watermark, logo, fast cuts, camera shake`

**Cast lock** (keep identical across all clips):

- **Anika** — 26, long dark braid over one shoulder, teal kurti with thin red trim, dark leggings,
  flat sandals, tired eyes, never smiles with her teeth.
- **Sabbir** — 33, tall, cropped black hair, crisp navy shirt buttoned to the wrist, charcoal
  trousers, cold flat stare, hands still.
- **Ryan** — 32, unkempt hair over the brow, light stubble, mustard-brown sweater, an old phone
  always in his hand. *He is only ever heard; if he must be seen, keep him out of focus.*

## Shots

| # | id | sec | prompt |
|---|---|---|---|
| 1 | h01 | 5.5 | Anika stands at a rain-streaked window at night, phone held to her chest, city lights bokeh behind the glass, slow push-in |
| 2 | h02 | 5.5 | Same room, closer: her face in the window light, phone at her ear, brow tightening, rain shadows moving over her cheek |
| 3 | w01 | 5.0 | Full-bleed handset screen: incoming call, unknown number, 11:11, dark navy UI, soft pulse on the accept button |
| 4 | w02 | 6.5 | Dark bedroom, phone glowing on the pillow, Anika sits on the bed edge listening, cold blue light on one side of her face |
| 5 | w03 | 6.5 | Medium close: Anika at the window, phone at her ear, eyes wet, rain running down the glass behind her |
| 6 | w04 | 5.0 | Dark study: Sabbir from behind at his desk, phone at his ear, one warm lamp, cold window light, papers squared |
| 7 | d01 | 3.0 | Insert: a phone lying on a bed, screen lit, slow push-in, everything else black |
| 8 | d02 | 4.0 | Anika by the window, phone low in her hands, the first small smile of the film, rain outside |
| 9 | k01 | 4.5 | Extreme close on rain hitting a window pane, warm lamp reflection, nobody in frame |
| 10 | k02 | 4.5 | Childhood memory: a blanket tent on a bed, a torch standing upright, an open storybook glowing, dust in the beam |
| 11 | k03 | 5.0 | Same tent, closer, the torch flickers, the blanket folds move a little, warm amber against deep navy |
| 12 | k04 | 6.0 | Anika at the window, hand at her chin, smiling at nothing, warm lamp on one side, rain on the other |
| 13 | l01 | 4.5 | Wide: Anika small in the dark room, leaning on the window frame, city rain beyond |
| 14 | l02 | 4.0 | Close: her eyes closing slowly, phone loose in her hand, the lamp warming her face |
| 15 | m01 | 6.5 | Park at dusk: Anika walking a wet gravel path in a red muffler, a krishnachura tree in full red bloom, petals falling |
| 16 | m02 | 5.0 | Same park, she stops and looks off past the bench, wind moving the muffler, lamp post flickering on |
| 17 | n01 | 5.5 | The empty bench under the krishnachura, petals collecting on the seat, slow push-in, nobody there |
| 18 | n02 | 4.5 | Insert: a folded red muffler and a cream envelope on the wet bench, one petal landing |
| 19 | n03 | 3.5 | Anika standing still on the path, arms down, face falling, the bench far behind her |
| 20 | r01 | 5.5 | Dark study: Anika enters and reaches for a bank of locked desk drawers, cold blue window light |
| 21 | r02 | 5.0 | Top-down insert: a wooden drawer open, an old phone glowing pale blue among papers and a key |
| 22 | r03 | 5.5 | Full-bleed old handset screen: a photograph of Anika as wallpaper, the name "আনিকা ♥", incoming call |
| 23 | r04 | 4.0 | Close: Anika holding the old phone, screen light under her chin, eyes wide |
| 24 | s01 | 5.0 | Bedroom looking at a half-open door, a long male shadow thrown across the floor, cold corridor light |
| 25 | s02 | 5.5 | Study two-shot: Anika in the foreground with the phone at her ear, Sabbir standing behind her, perfectly still |
| 26 | c01 | 5.5 | Tight close: Anika's face, phone pressed to her ear, the whisper landing, she stops breathing |
| 27 | c02 | 4.5 | Full-bleed call screen: connected, waveform alive, the timer running |
| 28 | c03 | 2.0 | Extreme close on her eye and the phone edge, then the frame falls to black |

## Sound (build it, don't source it)

The signature is **clock tick + ring at the same instant**, once per eleven-eleven: `0:12`, `0:37`,
`1:41`, `2:12` (approx, from `build/timeline.json`).

| cue | where |
|---|---|
| rain bed + room tone | every window/door shot |
| clock tick, 1 Hz | under the whole film, comes up from the wrong-number call |
| two-tone ring (440/480), 2.4 s | the four phone events; muffled (low-pass) when it rings inside the drawer |
| soft piano, minor | beats 4–6; thinner music-box octave on the childhood memory |
| birds, gravel steps, wind | the park |
| drawer creak, door thud, paper | the study |
| heartbeat, rising 58→128 bpm | from the drawer to the last line |
| drone (55 Hz, then 41 Hz) | the reveal to the cliffhanger |
| 2 s of true silence, line-cut click, 1.1 kHz beep, black | before *"আমি রায়ান না"* and after it |

## Cut rule

Every cut lands inside a measured pause — never on a syllable. In this repo that is done by
`plan.py` (silence detection + snapping) and checked by `verify.py` (`0 cuts need a look`).
