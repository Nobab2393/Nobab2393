# Law 5 cast — B1 stickman portraits

Five separate character images, drawn in the
[B1 · Minimal Line Art](../../.claude/skills/directing-stickman-videos/references/b1-minimal-handdrawn.md)
language: near-white paper `#FDFDFC`, 64 px faint grid, fine irregular black ink lines,
slender 4–4.5-head figures, small oval hands/feet, one marker accent colour per character.

| File | Character | Marker accent | Pose / acting beat |
|---|---|---|---|
| `king.png` | King | red (cape, belt) | hand on hip, one arm raised commanding, chin up |
| `rival.png` | Rival courtier | ink/navy (high collar) | arms folded, shoulders hunched, raised brow, smirk |
| `businessman.png` | Businessman | navy (suit, tie) | mid-stride, swinging arm, briefcase in the lowered hand |
| `student.png` | Student | green (backpack, folder) | hunched, gripping the strap, brows knit, uneasy mouth |
| `mentor.png` | Mentor | warm yellow (saree border, bindi) | open palm-up explaining gesture, head tilted, warm smile |

`_lineup.png` is the five cards butted together as a 5120×1280 contact sheet (not a deliverable).

Uniform spec: 1024×1280 cards, figure height 1000 px, feet on the same ground line at y=1150.

Generated with `generate_image` from the original `images/*.png` art as identity references,
then normalised: background removed via a paper-distance alpha ramp, each figure rescaled to a
common height, re-laid on the shared B1 paper + grid.
