# Delivery gates (checkable, in order)

Run these against the **actual encoded file**, not the plan, not a contact sheet, not the source
frames. Each line is either PASS (with the evidence you looked at), FAIL (with a timestamp), or
PENDING (tool/reference missing — say which).

## 1. Story and picture

- [ ] Shot ledger exists and every shot traces to a spoken phrase with real word times.
- [ ] **First 30 s**: concrete line, audience-relevant tension, a real picture/sound payoff, and
      the body delivers the opening promise (no generic greeting, no logo hold).
- [ ] **No principal-picture inactivity > 2.5 s.** Checked by event times through body and ending,
      including shot heads/tails. Subtitle changes, zooms, fades, decorative pulses do not count.
- [ ] Every shot that "means" something new changes focal subject, viewpoint, action or the
      information relationship — not the same composition with new text.
- [ ] Entry order varies with meaning; no repeated title → icon → underline build.
- [ ] Style-specific visual rules hold (e.g. B1: 4–4.5 head proportions, fine irregular line,
      near-white faint grid, handwritten hierarchy above quieter captions; A1: hollow head, two
      arms + two legs, no filled torso, no duplicate limbs).

## 2. Captions

- [ ] Line count per style respected (B1–B4/B6: one visible line; B5: up to three).
- [ ] Cue boundaries follow meaning and real pauses; noun phrases, verb+object, names, numbers
      and units stay together; no stranded prepositions or determiners.
- [ ] Each cue starts on its own first spoken word; no overlap, no gaps that break a sentence.
- [ ] Readable in the final encoded frame at the intended playback size; inside safe area;
      never over faces/hands/evidence. Burned-in and sidecar agree.

## 3. Sound

- [ ] Voice at native rate, fixed across the film, intelligible under everything else.
- [ ] SFX sit on visible contacts/changes, are material-appropriate (near/far, weight), and are
      not one pop per word.
- [ ] Music bed present by default and mix-balanced; explicit omission is recorded if the user
      asked for silence.
- [ ] Measured loudness/true peak recorded; listen for clipping, masking, loop joins, phone
      speaker.

## 4. Ratio and platform

- [ ] Native per-ratio authoring — 9:16 composed, not cropped; safe areas and caption band
      declared per shot.
- [ ] 1× phone-size review of the encoded portrait, every shot, actual action legible.
- [ ] Nothing meaningful hides under platform UI (bottom bar, right rail).

## 5. Records — keep them separate

| record | who | what it proves |
|---|---|---|
| technical check | runtime | encode, duration, loudness, coverage — nothing aesthetic |
| sample comparison | reviewer agent | actual playback vs the approved reference film, per gate |
| user approval | the user | they watched it and accepted that exact cut |
| limitation | whoever hit it | which tool was missing, what was therefore not verified |

A pass in one row never implies another. "Rendered" ≠ "accepted". Unwatched reference = PENDING.

## 6. Stop conditions

- Anything unknown/failing stays pending; do not rewrite the template to green.
- Repair only the affected shots/cues, then re-check those plus neighbours and the joins.
- Never regenerate accepted narration or approved media for a convenience change.
- Upload/publication/paid retries are separate authorizations, never implied by "render".
