# THE LAMP AND THE OWL / লণ্ঠন আর পেঁচা

**Format:** 9:16 · 1080×1920 · 30 fps · ~83 s · বাংলা VO + English on-screen lines
**Style:** Claude flat vector (≤3 tones per panel, one accent colour only)
**Star:** অধ্যাপক পেঁচা — Prof. Owl (ink body, cream eyes, round glasses, small grey scarf)

---

## Palette (locked)

| Token | Hex | Meaning |
|---|---|---|
| CREAM | `#F0EEE6` | paper / moral card |
| INK | `#191919` | character body, line |
| NIGHT | `#1B1A18` | night ground |
| GREY | `#C4BFB5` | beak, scarf, lampshade metal |
| META | `#96908A` | secondary type |
| **CORAL** | `#D97757` | **the flame and nothing else** |
| CORAL_HOT | `#F7BE84` | flame flared too high |

One accent, one meaning. When the flame is overblown the whole frame burns coral;
when it is out, the coral disappears from the frame entirely.

---

## The seven blocks

### 1 — ONE LAMP, ONE ROAD *(0.0 – 12.0 s)*
> এক রাস্তার মোড়ে একটা লণ্ঠন। রাতের পর রাত জ্বলে থাকে।
> কে রাখে? এক বুড়ো পেঁচা। কেউ তাঁর নাম জানে না। সবাই শুধু আলোটা চেনে।

Wide. Stars, low houses, one lantern on a post. Owl walks in from the right and stops
inside the pool of light — never centre-frame, always beside the light, not in it.

### 2 — THE CROW'S OFFER *(14.4 – 26.8 s)*
> একদিন এক তরুণ কাক নামল। বলল, অধ্যাপক, আপনার আলো এত মিটমিটে কেন?
> আমাকে দিন, আমি আকাশের মতো জ্বালাব। পেঁচা শুধু বললেন, দেখি।

Crow drops in from above with a small stall-and-settle. It talks with its whole body,
owl answers with one blink. The offer is greed; the answer is a pause.

### 3 — TOO MUCH LIGHT *(27.2 – 38.2 s)*
> কাক জোরে ফুঁ দিল। শিখা সাদা হয়ে ফুলে উঠল।
> ঘরের জানালা জ্বলে উঠল, গ্রাম তালি দিল। কাক ভাবল, এই বুঝি জেতা।

Blow → flame scales to 2.6×, turns CORAL_HOT, glow radius triples, rays snap out of
the housing, every window in the village ignites. This is the loudest frame of the film.
(It is also the trap: earlier we said the coral *is* the flame — and now there is too much of it.)

### 4 — THE WIND ANSWERS *(39.0 – 51.8 s)*
> কিন্তু বেশি আলো মানে বেশি পোকা। পোকা মানে বাতাস।
> বাতাস এসে শিখা কেঁপে নিভে গেল। রাস্তা অন্ধকার, কাকের ডানায় পোড়া পালক।

Flame stutters twice, then dies. Coral drains out of the frame — glow, windows, rays all
go. Last coral on screen is the ember on the crow's wing.

### 5 — THE RELIGHT *(52.6 – 63.2 s)*
> পেঁচা কিছু বললেন না। পুরনো সলতে থেকে ছোট একটা শিখা জ্বালালেন।
> আগের মতোই স্থির, আগের মতোই কম।

Owl steps in, one small flame comes back exactly at its scene-1 size. No speech, no
gesture. Restraint drawn as a fixed number, not a feeling.

### 6 — THE ROAD REMEMBERS *(64.0 – 72.2 s)*
> লোক ফিরে এল। কাককে দোষ দিল না, পেঁচাকে ধন্যবাদও দিল না।
> রাস্তা দেখা যাচ্ছে — এই পর্যন্তই যথেষ্ট।

Silhouettes cross the road and keep walking. Neither character is praised, neither is
blamed. The road is visible; that is the whole win.

### 7 — THE MORAL *(73.0 – 83.2 s)*
> যে আলো নিজেকে দেখায়, সে নিভে যায়। যে আলো পথ দেখায়, সে জ্বলে থাকে।

Ground flips to CREAM — the film steps out of the night and into print.

```
THE LIGHT THAT SHOWS OFF
GOES OUT.
THE LIGHT THAT SHOWS THE WAY
STAYS LIT.
```
`THE LAMP AND THE OWL` set small beneath, owl at 0.62 scale, coral flame above it.

---

## Transitions
Coral disc wipe (no crossfade): cover `1180 · ease(seg(t0−0.32, t0, t))`,
reveal `1180 · (1 − ease(seg(t0, t0+0.44, t)))`. A wipe that is the same colour as the
flame means the cut itself is made of the subject.

## Sound
Seven Bangla TTS segments, 0.80 s of dry air between them, 0.55 s before the moral card,
4.2 s tail so the last line lands in silence rather than being cut off.

## Rebuild
```bash
pip install pillow imageio-ffmpeg --break-system-packages
python3 build.py --sheet   # character sheet
python3 build.py --test    # 3 proof stills
python3 build.py           # full render -> prof-owl-lamp-1080x1920.mp4
```
