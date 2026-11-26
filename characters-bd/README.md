# Bangladeshi 2D character set

Five flat-vector character designs, drawn in the palette and shape language of
`../dark-lesson-03-2d/` so they can be dropped straight into the *কেনা সম্মান* films.

| file | who | reads as |
|---|---|---|
| `c1-patron.png` | the patron — 50s, ink panjabi, gold-trimmed terracotta waistcoat, hand behind the back | the man who pays for the village (Rafiq) |
| `c2-boy.png` | the boy — 14, terracotta tee, grey shorts, one-strap backpack, sandals | the one who has to pick things up (Ayan) |
| `c3-elder.png` | the elder — white kurta, prayer cap, checked `gamchha`, cane, open palm | the man who takes nobody's money |
| `c4-rickshaw.png` | the rickshaw puller — checked lungi, sleeveless vest, `gamchha` at the neck, hand on the bamboo shaft | the street |
| `c5-teastall.png` | the tea-stall owner — apron, thick moustache, kettle high, tray of glasses, steam |  whose bill everyone drinks |

`cast-sheet.png` is the five side by side (2188 × 708).

## Style spec

- Flat vector shapes, **no black outlines**, no gradients.
- Palette: cream `#F0EEE6`, ink `#191919`, terracotta `#D97757`, dusty blue `#7A9CB5`, warm grey.
- Full body, three-quarter view, one dot eye, pale ellipse shadow under the feet,
  generous empty space, vertical portrait crop — so a figure can be lifted out and
  animated without re-compositing a background.
- 768 × 1376 (the tea-stall one is 848 × 1264).

## Regenerating

Text-to-image, one character per prompt, prompt = the style spec above plus a one-line
description of who they are. Keep the "no outlines" instruction: the first rickshaw
attempt came back with heavy contour lines and a shaft that read as a cleaver, which
did not cut with the other four.
