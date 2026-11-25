# অন্ধকার পাঠ · স্টিকম্যান — a 30 s A1 Dark short (worked example)

This folder exists to prove the skill was *understood*, not just installed: it applies
[`stickman-video-director`](../dev-skills/.claude/skills/stickman-video-director/SKILL.md) to a
new film in our "অন্ধকার পাঠ" brand, in the A1 · Classic Black & White (Dark) style, vertical
9:16, Bangla narration.

| file | what |
|---|---|
| `01-direction.md` | director proposal: story, metaphor chain, beat times, audio plan, constraint audit |
| `prompts/a1-clip-1.md` | 0–10 s — the gift and the receipt |
| `prompts/a1-clip-2.md` | 10–20 s — the chain that grew from it |
| `prompts/a1-clip-3.md` | 20–30 s — the knot opens |
| `b1-alternative.md` | how the same story would be built in B1 with the local manifest runtime |

## Honest status

**Prompts are the deliverable.** That is a complete stopping point under the skill's own A-mode
rule, and it is the only honest one available here: no video model is reachable from this box
(no Flow session, no API key), so nothing in this folder has been *generated*, *viewed* or
*accepted*. Every gate in `reference/gates.md` therefore reads **PENDING**, not passed. The
reference film A1 compares against (`assets/a1/…`) is not vendored either — see the skill's
`MEDIA-NOT-INSTALLED.md`.

Bangla narration is written for a model that supports native Bangla speech. If the chosen model
does not, the honest route is: generate silent footage, record the three lines with the project
TTS voice, and edit the narration onto the A audio timeline — not to fake native audio.
