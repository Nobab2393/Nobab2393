# Provenance

## Vendored upstream

| field | value |
|---|---|
| repo | <https://github.com/OSideMedia/higgsfield-ai-prompt-skill> |
| commit | `e90ed07753b879bb6be157a7cb12e3043a2cbe6f` (2026-11-18) |
| skill version | 3.42.0 (`SKILL.md` frontmatter) |
| licence | MIT — see `../higgsfield-ai-prompt-skill/LICENSE` and `THIRD_PARTY_NOTICES.md` |
| installed to | `dev-skills/.claude/skills/higgsfield-ai-prompt-skill/` (project) and `~/.claude/skills/higgsfield-ai-prompt-skill/` (global) |
| install mode | copy (verbatim) |

**Excluded from the copy** (size, not policy): `.git/`, `assets/fonts/` (DejaVu ~2.2 MB, already
available via matplotlib), `docs/archive/`, `evals/`, `tests/`, and the dated
`specs/models_explore_snapshot_*.json` dumps. The live spec layer
(`specs/model-specs.yaml`, `MODEL-SPECS.md`) **is** kept — it is what the prompt enums are
verified against.

Vendored `SKILL.md` sha256: `fc595c4ef2576b6cc07020709423e5628002bb01b0ae201eb7f9dc9a3a5e7180`.

## What this skill adds on top

`SKILL.md` + `reference/` + `tools/` in this folder are the distilled working layer written
after reading the pack:

- `SKILL.md` — the MCSLA routine, ten rules that change output, lanes, failure triage, and how
  this repo actually uses the skill (as a writing layer, since there is no Higgsfield access
  here).
- `reference/prompt-formula.md` — T2V / I2V / timestamped skeletons, budgets, identity-vs-motion.
- `reference/model-lanes.md` — the lane table with durations/ratios and the retired/UI-only
  caveats, dated to the upstream snapshot.
- `reference/negative-blocks.md` — the exact prevention phrasings, grouped by artifact family.
- `reference/camera-vocab.md` — the named camera moves, plus how to write a camera line.
- `tools/build_prompt.py` — assembler + lint: missing MCSLA layers, 200-word cap, Cinema Studio
  512-char budget, retired model names, unnamed camera moves.

Anything that must be exact (preset spellings, model enums, character budgets) is deferred to
the vendored pack rather than restated here, because the platform's lineup changes between
releases.

## Update procedure

```bash
git clone --depth 1 https://github.com/OSideMedia/higgsfield-ai-prompt-skill.git /tmp/hf
cd /tmp/hf && git log -1 --format='%H %cs'
# re-copy with the same exclusions, then bump the commit/version fields above and in
# dev-skills/.claude/skills/higgsfield-ai-prompt/SKILL.md frontmatter
```
