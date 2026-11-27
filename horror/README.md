# জমিদার বাড়ি — production notes

Script: `SCRIPT.md` · Film: `film.py` · Environments: `hbg.py` · Audio levels: `level_audio.py`
Voices: `vo/` (raw TTS) → `vo_fx/` (per-character EQ, pitch, reverb, loudness-matched)

## How the five voices were separated

| Character | Base voice | Treatment | Final F0 |
|---|---|---|---|
| Rahul (student) | male, young | presence lift 5 kHz, low cut | 232 Hz |
| Malati (mentor) | female, elderly | low-end lift, 3.5 kHz cut | 191 Hz |
| Kamal (rival) | male | pitch 0.88, 200 Hz boost | 154 Hz |
| Sujon (businessman) | male, brash | 2.5 kHz presence | 144 Hz |
| Zamindar (king) | male, deep | pitch 0.78, 160 Hz boost, 3-tap echo | 131 Hz |

Every clip is then RMS-matched to 0.105 with a 0.95 peak ceiling, so no character is
quieter than another. Verified per-line in the final mix: all ten land between
0.071 and 0.111 RMS against a ~0.05 drone bed.

## Sync

`mouth()` drives every mouth from the *measured* start and duration of that character's
own clip, with a 45 ms attack and 60 ms release so mouths never pop. Only the character
whose line is playing opens their mouth; everyone else runs a listener reaction
(brow raise, chin tuck, shoulders dropping).

## What was actually fixable vs. not

- **Voices**: five distinct TTS voices, pitch-separated and EQ'd per character.
- **Lip sync**: per-line envelope from measured clip timing.
- **Animation**: the stickman rig, driven procedurally (no pose library).
- **MiniMax / H3**: not runnable here — no GPU, 33 B checkpoint, and Hugging Face is not
  reachable from this sandbox. `h3-prompts/law5_bangla_h3.md` shows the equivalent H3
  prompt structure for the same cast if you want to generate it on Hailuo/Hub.
