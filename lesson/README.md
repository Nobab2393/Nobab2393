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

Verified in the finished mix: all ten lines land between 0.0997 and 0.1033 RMS,
2.6× above the music bed — nobody is buried and nobody shouts over anyone.

## Script note

"লোভে পাপ, পাপে মৃত্যু" is a proverb, not a claim about the world; the moral card uses it
in that spirit. Part 1 sets up the trap; part 2 is available if you want the payoff.
