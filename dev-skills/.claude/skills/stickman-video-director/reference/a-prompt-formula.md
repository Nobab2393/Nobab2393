# A-mode prompt formula (from the upstream A1 examples)

A standalone A prompt is a *self-contained* brief: the model has no memory of yesterday's clip,
so the character description and the style rules are repeated in full every time. Upstream calls
this the A1 structure and applies it to A2–A5/A7/A8 with their own palettes.

## Skeleton

```text
Create exactly one <N>-second <ratio> <kind: e.g. kinetic motion-graphics> clip with
<synchronized action sound effects | native narration | both>.

STYLE:
<canvas colour + paper/ink rules>. <accent colour = story function, one line each>.
Use <style family> 2D line animation. Show the same consistent stick figure with
<full character description — head shape, no face if applicable, limb count, line weight,
proportions, what is never filled>. Each limb appears only in its current pose: raising the
right arm replaces that arm's previous line, never leaving a resting arm beneath an active arm.
<what colours may / may not touch>.

CONTINUITY (only when it continues an approved clip):
Begin with the same <exact outgoing graphic state> that filled the end of Clip <n>.

TIMED SEQUENCE:
[0–3s] <shot size + angle>. <concrete first frame that establishes the situation or key prop>.
<the figure enters the action>. <the contact / pressure / gesture that starts the chain>.
[3–7s] <cut or follow>. <the consequence travels / the metaphor transforms>. <one new visual
idea>. <what the figure does in response>.
[7–10s] <the payoff>: <one more graphic change with a visible consequence>. <land on the
contrast or the new state>. Finish on <the exact frame the next clip can start from>.

VOICEOVER (only when narration is selected): use the same <named voice>. Read exactly:
"<verbatim line>"

AUDIO:
<3–6 cue events, each tied to a visible contact/change, in order>. <what stays under the voice>.
Sound effects only / narration dominant.

CONSTRAINTS:
Flat 2D <side/three-quarter> view. No perspective, extrusion, gradients, glow, grain, shadows,
3D, duplicate or disconnected limbs, motion trails on limbs, logos, captions, subtitles,
watermarks. The only readable text is "<exact allowed string>". Keep the canvas <colour> in
every frame. Do not alter or repeat the voiceover.
```

## Rules that decide whether the clip works

1. **Repeat the character, always.** Circle head, no eyes/mouth, exactly two arms and two legs,
   uniform medium line weight, proportions stable across cuts.
2. **Accent colours are meanings, not decoration.** "Red marks wasted effort, blue marks the point
   where a lever changes the force" — then never use red for anything else in that clip.
3. **One main action readable at a time.** A push flattens a mark, the mark travels, its return
   changes the figure's next decision. Carry grip, contact point, direction or consequence forward.
4. **Cut for reason:** close on contact to show the touch, wide to reveal what changed, follow to
   show where the motion goes. Keep screen direction and figure size consistent across the cut.
5. **The last beat is a change, not a pose.** Add one more consequence before the final hold, and
   make the final frame a state the next prompt can name.
6. **Constraints earn their keep.** Every "no gradients / no duplicate limbs / only this text"
   line exists because the model produced exactly that artefact otherwise.
7. **Audio is cued to pictures**: scrape-and-stop, click at contact, rising creak, solid impact,
   footstep. No pop per word, no music unless the project plan says so.
8. **Duration is stated once, up front** — the beats then have to fit it; never stretch a beat by
   adding dead air.

## Anti-patterns seen in the wild

- "A stickman thinks about money and success" — no chain, no consequence, the model invents props.
- Six icons in one 10-second clip — nothing gets read; upstream keeps one focus per frame.
- Restating the style only as "minimalist black and white" — the drawing drifts within two cuts.
- Adding captions in the prompt while also planning burned-in captions in the edit — double text.
- Asking for a 2-second action inside a 10-second prompt with no beat times — the model spreads it.
