# জমিদার বাড়ি — The Zamindar's House

A 2-minute Bengali conversational horror film using the five B1 stickman characters
(`images/stickman/*.png`). Five speakers, one voice each, no subtitles.

## Cast and voices

| Character | Role in this film | Voice direction |
|---|---|---|
| **মালতী** (mentor) | the old caretaker's widow at the gate | feminine, elderly, low and weary, speaks slowly, never raises her voice |
| **সুজন** (businessman) | property developer, wants to demolish it | masculine, brash, loud, fast, contemptuous |
| **রাহুল** (student) | young, films everything | masculine, young, thin, nervous, breaks mid-sentence |
| **কামাল** (rival) | Sujon's silent partner | masculine, shaky, close to tears, whispers |
| **জমিদার** (king) | the dead landlord | masculine, very deep, very slow, echoing, no breath |

## Dialogue (10 lines, verbatim — never translated on screen)

1. **মালতী** — এই বাড়িতে ঢুকবেন না। সন্ধ্যার পর ওই দরজা নিজে নিজে খোলে। যারা ঢুকেছে, তারা ফিরে আসেনি।
2. **সুজন** — গুজব ঢের শুনেছি, মা। বাড়িটা ভাঙলে সোনার টুকরো বেরোবে। আজ রাতেই কাজ শুরু।
3. **মালতী** — টাকার লোভে পাঁচটা লোক মরেছে এই উঠোনে। ওদের নাম আজও দেয়ালে লেখা আছে। তোমার নামটাও উঠে যাবে।
4. **সুজন** — চল কামাল। খবরদার, কেউ পিছিয়ে যাবে না। টর্চ জ্বালো।
5. **রাহুল** — দাদা... এই দেয়ালে সত্যিই নাম লেখা। একটা নাম... আজকের তারিখে।
6. **কামাল** — আমি ওই জানালার পাশে একটা লোককে দাঁড়িয়ে থাকতে দেখলাম। মুখটা... মুখটা নেই।
7. **রাহুল** — ক্যামেরায় কিছু ধরা পড়ছে না। কিন্তু শব্দ... ওই শব্দটা কোথা থেকে আসছে?
8. **সুজন** — বে-কুফ! এই বাড়ি আমার। আমার বাপের টাকায় কেনা। কে আছে এখানে? বেরো!
9. **জমিদার** — তোমার বাপের টাকায় কেনা? এই বাড়ির প্রতিটা ইট আমার রক্তে গাঁথা। আমি চলে গেছি, কিন্তু বাড়ি যায়নি।
10. **জমিদার** — এখন তোমরাও থাকবে। চিরকাল। আমার সাথে।

## Structure (~120 s)

| Beat | Visual | Audio |
|---|---|---|
| Cold open | fog, gate, moon, dead tree; title card on the iron gate | wind, creaking, a single temple bell far off |
| 1–2 | Malati at the gate, Sujon arriving with torch | lines 1–2 |
| 3–4 | Malati's hand on the gate; Sujon pushes past, door swings | lines 3–4 |
| 5–6 | corridor, dust in torchlight; wall of carved names | lines 5–6 |
| 7–8 | window with a shape that isn't there; Sujon shouting | lines 7–8 |
| 9–10 | throne room; the zamindar rises out of the dark | lines 9–10 |
| End | doors slam shut on a black frame, one held beat | slam, silence, title |

## Craft rules

- **Sync:** mouth opens only inside each measured line (`mouth_for(start, end)` per clip), never
  during silence. Every cut lands on a line boundary or a deliberate held beat.
- **Horror grammar:** the light source is always motivated (torch, moon, dying lamp); the frame
  gets darker and the camera closer as the film proceeds; nothing supernatural is shown clearly
  until line 9.
- **No subtitles.** On-screen Bengali only as the title card and the carved names, which are story
  props, not captions.
- **Voices:** five distinct speakers, no narrator.

## MiniMax note

H3 itself cannot run in this sandbox (no GPU, 33 B model, no Hugging Face egress). The film is
rendered by the local rig pipeline; an equivalent H3 prompt pack for the same script lives in
`h3-prompts/`.
