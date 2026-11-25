# Media not installed in the repository copy

The vendored text layer references **62 binary media files** (approved reference films, contact
sheets, style boards, character acting sheets, public showcases). They are not in this repo —
they total 554 MB. Every one of them is a *comparison* asset: the contracts say to play them
before authoring and against the encoded result, and none of them may be used as production
footage for a new story.

## If you need them

Full install, sparse (skill folder only, media included):

```sh
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/kaomei/stickman-video-director.git stickman-video-director
git -C stickman-video-director sparse-checkout set skills/directing-stickman-videos
```

Or copy them from an existing full install:

```sh
rsync -a ~/.claude/skills/directing-stickman-videos/assets/ \
  dev-skills/.claude/skills/directing-stickman-videos/assets/
```

Those two commands are the only difference between the repo copy and the installed one.

## What the missing files are for

| path | role |
|---|---|
| `assets/b1/approved-2026-10-23.mp4` | B1 · the approved Ryan V4 baseline — drawing, acting, typography, native voice |
| `assets/b1/portrait-approved-2026-11-13.mp4` | B1 · the approved 9:16 clip — vertical hierarchy, caption band, ordered reveals |
| `assets/b1/character-acting-reference.png` | B1 · slender proportions (≈4–4.5 heads) and whole-body acting guide |
| `assets/b2/**`, `assets/b3/**` | B2/B3 approved clips + their portrait clips and implementation boards |
| `assets/b4/**` | five white-glove illustrations, both showcase films, native portrait opening |
| `assets/b5/**` | Mei / Spider accepted baselines and their relay stages |
| `assets/b6/**` | the portrait V44 primary standard and V90 secondary evidence |
| `assets/b7/**`, `assets/b8/**` | pixel-theater and Greek-mythology drawing references |
| `assets/b-audio-library/**` | B-mode audio bed/effect library (575 `.ogg`, 275 `.wav`) + its 1.7 MB `catalog.json` |
| `assets/a6/**`, `assets/a7/**`, `assets/a8/**` | A6/A7/A8 reference stills for image-guided generation |

## Consequence, stated plainly

With this repo copy you can plan, prompt, storyboard, write the manifest and run every QA gate
— but you cannot *play* the reference film a gate asks you to compare against, and B-mode has
no audio library. That is a real limitation, not a pass: the skill's own rule is that an
unwatched reference stays **pending**, never “matched”.
