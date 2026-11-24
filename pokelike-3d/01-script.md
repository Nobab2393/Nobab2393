# अंगार और बादल · ANGAAR AUR BAADAL
### A 3D-anime creature short in Hindi — 1080×1920, 24 fps, ~52 s

**Logline:** A boy finds a fire pup on a night ridge. A storm hawk steals its flame.
The pup could burn the thief — instead it lights the way home.

Original characters only. This is *Pokémon-shaped* (a trainer, two creatures, one clash,
one bond) without borrowing a single existing design or name — no Pikachu, no Poké Ball,
no franchise logo. That matters commercially: fan-art gets claimed, an original cast
becomes a series you own.

---

## Cast

| | Character | Design | Function |
|---|---|---|---|
| 🔥 | **अंगार / ANGAAR** | ember-orange pup, cream muzzle + chest, big ears, a flame that rides on its tail | the hero: power used carefully |
| 🌩 | **बादल / BAADAL** | slate-blue storm hawk, cyan eyes, three-segment wings, hooked beak | the rival: takes what it wants, ends up a friend |
| 🧒 | **रवि / RAVI** | 12, coral jacket, jeans | the human who finds him — the audience's eyes |

Palette: ink `#0A090B` · night `#10111A` · slate `#4D5980` · **ember `#ED6B33`** ·
flame `#FFA852` · cream `#F7EBCC`. Ember is the accent; only the fire is allowed to use it.

---

## Seven blocks — VO + on-screen Hindi + what the frame does

| # | ⏱ | Hindi voice-over | On-screen | Picture |
|---|---|---|---|---|
| 1 | 0.0–7.4 | रात के पहाड़ पर एक चिंगारी जलती है। कोई नहीं जानता, वो किसकी है। | **अंगार और बादल** / *ANGAAR AUR BAADAL* / एक छोटी सी आग, एक बड़ा तूफ़ान | slow push-in, moon, embers rising, the pup curled on a rock |
| 2 | 7.4–13.8 | रवि उसे ढूँढ लेता है। छोटा सा अंगार, जो छींकते ही आग उगलता है। | रवि को मिला एक छोटा सा अंगार | Ravi walks in, kneels; the pup wakes, blinks, sneezes sparks |
| 3 | 13.8–19.6 | तभी आसमान काला पड़ता है। बादल आता है, और आग उड़ा ले जाता है। | आसमान से उतरा बादल — और आग ले गया | sky darkens, wind streaks, hawk dives in an arc from the moon, the flame goes out |
| 4 | 19.6–25.3 | अंगार कूद पड़ता है। आग और तूफ़ान, आमने सामने। | आग और तूफ़ान — आमने-सामने | the leap, 30 speed lines, impact star, spark burst, camera shake |
| 5 | 25.3–32.6 | बादल गिरता है। अंगार के पास आग है, पर वो जलाता नहीं। वो रास्ता दिखाता है। | अंगार ने जलाया नहीं — रास्ता दिखाया | hawk down, pup standing over it, a warm cone of light on the ground |
| 6 | 32.6–37.9 | तूफ़ान भी अब दोस्त है। और पहाड़ पर तीनों साथ बैठे हैं। | अब वो तीनों साथ हैं | wide, three silhouettes, embers, slow drift back |
| 7 | 37.9–45.6 | अगली कड़ी में अंगार को मिलेगा नया दोस्त। कमेंट करो, अंगार। और फॉलो करना मत भूलना। | see the CTA card below | the end card |

Tail: 6.2 s of card hold after the last word, so the CTA is readable without pausing.

---

## The CTA — why this one, and not "subscribe please"

Most Hindi shorts lose the viewer in the last 3 seconds. The card is built as **four beats**,
each asking for something cheaper than the last:

```
कहानी पसंद आई?                       ← a question (makes the brain answer)
अगली कड़ी में अंगार को मिलेगा नया दोस्त  ← a reason to stay subscribed
कमेंट करो: ANGAAR                    ← the cheapest action (one word, in the video's own name)
[ फॉलो करें ]                        ← the pill: one visual target
हर शुक्रवार नई कड़ी                   ← the promise that turns a follow into a habit
```

1. **Hook, not a plea.** "कहानी पसंद आई?" is answerable; "subscribe" is not.
2. **Comment before follow.** A one-word comment costs nothing and the algorithm weights
   comments far above likes. It also seeds the comment section with the character's name —
   which is exactly the keyword the next episode's search will need.
3. **One button, one job.** The pill is the only filled shape on the card, so the eye lands
   on it even at 30 % brightness on a phone.
4. **A cadence promise.** "हर शुक्रवार" converts a one-off watch into a return visit; without
   it a follow is a coin flip.
5. **Spoken as well as written.** The last VO line says the same three things, because
   roughly half of vertical viewers never read the card.

### Variants you can drop in (same card, different ask)

| Goal | Hook | Middle | Button |
|---|---|---|---|
| Series growth | कहानी पसंद आई? | अगली कड़ी: बादल का राज़ | फॉलो करें |
| Comment engine | अंगार का नाम क्या रखें? | कमेंट में लिखो — अगली कड़ी में नाम आएगा | कमेंट करें |
| WhatsApp/Facebook reach | इसे उस दोस्त को भेजो जो कहानियाँ पसंद करता है | शेयर करो — 3 दोस्तों को | शेयर करें |
| Monetised channel | पूरी कहानी देखनी है? | प्लेलिस्ट: अंगार की दुनिया | प्लेलिस्ट देखें |

> Do **not** put an engagement-exchange link (Like4Like & co.) on a kids' animation card: it
> asks a 9-year-old viewer for a click they cannot give, it violates YouTube/Meta policy, and
> it teaches the algorithm that your audience doesn't finish videos.

---

## Sound

Seven Hindi VO clips (masculine, narration), 0.45 s of air between blocks, 0.6 s before the
card, 6.2 s tail. No music bed yet — the gaps are deliberate so the VO lands.

## Rebuild

```bash
pip install --break-system-packages numpy pillow imageio-ffmpeg matplotlib uharfbuzz fonttools
python3 sheet.py            # cast sheet
python3 film.py --still 33  # one frame
python3 film.py             # full render + mux -> angaar-baadal-1080x1920.mp4
```
