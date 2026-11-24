# Pairing a captured asset with a DOM card

You have two lists that were produced by different machinery: the **network** gives you media
in arrival order, the **DOM** shows cards in visual order. They are usually the same order —
and "usually" is what ships wrong downloads. The reference build's ladder ended in
`allMedia[i % allMedia.length]`, which guarantees a file, of the wrong video, silently.

Code: [`../tools/match-cards.mjs`](../tools/match-cards.mjs) (7 assertions, runnable).

## 1. Identity first: the CDN asset key

Signed URLs change every request; the object key does not.

```
https://v16-webapp.example.com/tos-cn-x0/aaa111/?a=1988&br=4100&sig=…
                                ^^^^^^  ← stable key
https://p.example.com/tos-cn-x0/aaa111~tplv-abc:300:400.jpg
```

```js
const key = path.match(/tos-[^/]+\/([^~/]+)/i)?.[1]     // "aaa111"
         ?? path.split('/').pop().split('~')[0].split('.')[0];
```

Scrape it from the card's `<img src>` **and** `<video src>`; a poster is often the only thing
rendered before playback. Require `key.length > 8` — short keys collide.

## 2. The ladder, with confidence instead of a guess

| Tier | Test | Confidence | Failure mode it prevents |
|---|---|---|---|
| 1 | card key **equals** a capture's poster/url/vid key, and exactly one capture matches | `exact` | capture-order drift |
| 2 | card key is a **substring** of a capture URL | `substring` | proxied/rewritten CDN paths |
| 3 | `cardCount === mediaCount`, capture order = visual order | `positional` | a page with no keys at all |
| — | anything else | `none` → **ask the user** | downloading the wrong clip |

Two rules that carry most of the value:

- **Ambiguity is not a match.** If one key hits two captures, return `null` — do not pick the
  first. Re-issued renditions of the same asset are common.
- **Position needs equal counts.** Three cards and three captures can be zipped; three cards
  and seven captures cannot. The reference build zipped them anyway (modulo!).

`pickMedia()` returns `{media, confidence, reason}` so the UI can say *"matched by position —
check it before saving"* instead of lying.

## 3. Getting a human title out of the DOM

The extension's own ladder, worth keeping:

1. **A structured table beats everything** — the app writes a scene breakdown into a
   `<table>`; row *n* ↔ card *n*, column 2 is the title → `Scene_3_The_River`.
2. **Nearest semantic container** — `card.closest('[data-message-id], [class*="message"]')`,
   then the first `h1..h4, strong` whose text is 4–80 chars and does not contain your own
   button text or the site name (stop-words, or you will title clips "1080P").
3. **Positional fallback** — `Scene ${n}`.

Sanitise before it becomes a filename: strip `/ \ ? % * : | " < > #`, collapse `_`, cap ~60
chars, and keep the extension in exactly one place.

## 4. Injecting buttons into a live SPA

The reference approach — `MutationObserver` on `body` + a 2-second `setInterval` + a
`:scope >` guard — is the right *idea* and the wrong *cost*: the observer fires on every
mutation of a chat app (dozens per second while streaming) and the callback re-runs
`querySelectorAll` over the whole document each time.

```js
let queued = false;
const observer = new MutationObserver(() => {
  if (queued) return;
  queued = true;
  requestAnimationFrame(() => { queued = false; attachButtons(); });   // ≤1 pass per frame
});
observer.observe(document.body, { childList: true, subtree: true });

// the interval is a safety net for late hydration, not the trigger
setInterval(attachButtons, 4000);
```

Idempotency, three checks in this order:

```js
if (card.querySelector(':scope > .my-btn')) return;      // ours already attached
card.querySelectorAll('.my-btn').forEach((b, i) => i && b.remove());   // kill duplicates
card.dataset.myBtnAttached = '1';
```

`card.style.position = 'relative'` before `appendChild(btn)` — the page may not be positioned,
and an `absolute` button will otherwise fly to the nearest positioned ancestor.

## 5. Never label a guess

The reference button says **“1080P”** even on the fallback path, where `video.src` is whatever
the page is showing (often the branded/watermarked rendition at 720p). The label is a promise;
derive it from `media.width × media.height` or say "best available".

Same rule for the popup row: show `width×height` from the payload, not a constant.
