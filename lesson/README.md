# সোনার হরিণ — production notes

Script `SCRIPT.md` · film `film.py` · environments `lbg.py` · audio `level_audio.py`
Voice chain: `vo/` (TTS) → `vo_fx/` (pitch + EQ, loudness-matched)

## Improvements over the horror short

| Area | Horror short | This film |
|---|---|---|
| Lip sync | synthetic sine on the line window | **amplitude envelope of the real recording**, 60 fps sampling, fast-attack / slow-release |
| Blocking | everyone on one ground line | `place(depth, x)` — scale and ground line from depth, so near/far reads |
| Listeners | brow only | brow + chin + torso weight, per character, driven by "is someone else talking" |
| Loudness | fixed per-clip gain | re-levelled after pitch shifts, then verified per line in the final mix |
| Title | over the characters | reserved sky band with a soft dark wash behind it |

## The five voices (measured, not assumed)

| Character | F0 | Gap above next |
|---|---|---|
| Rahul (boy) | 248 Hz | 62 |
| Malati (grandmother) | 186 Hz | 21 |
| Sujon (returned rich) | 165 Hz | 26 |
| Kamal (woodcutter) | 139 Hz | 18 |
| Headman | 121 Hz | — |

Measured on the delivered MP4, all ten lines:

| line | speaker | RMS |
|---|---|---|
| L1 | Rahul | 0.1025 |
| L2 | Malati | 0.0997 |
| L3 | Sujon | 0.1032 |
| L4 | Kamal | 0.1015 |
| L5 | Rahul | 0.1001 |
| L6 | Kamal | 0.1027 |
| L7 | Headman | 0.1017 |
| L8 | Sujon | 0.1005 |
| L9 | Malati | 0.1019 |
| L10 | Headman | 0.1009 |

Spread **1.04×**, peak 0.864 — nobody is buried, nobody shouts, nothing clips.

## Lip sync

Mouth openness vs. the real audio envelope correlates at **r = 0.998** on every one
of the ten lines, and stays exactly 0.000 in silence. It is not a generic flapper:
the shape of each sentence is in the mouth.

## Shots

1. Porch, dusk — title, L1, L2
2. Square, evening — L3 (Sujon walks in)
3. Fireside — L4, L5
4. Forest, cold — L6, the golden deer
5. Banyan, last light — L7
6. Square — L8
7. Banyan — L9
8. Porch wide → headman close → empty porch — L10, down to the moral card

## Script note

"লোভে পাপ, পাপে মৃত্যু" is a proverb, not a claim about the world; the moral card uses it
in that spirit. Part 1 sets up the trap; part 2 is available if you want the payoff.
