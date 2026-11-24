---
name: chrome-mv3-media-interceptor
description: Reverse-engineer and rebuild a Manifest V3 browser extension that captures the best-quality media stream a web app loads — network hooking from the MAIN world, stream-safe (SSE/chunked) response sniffing, flip-the-flag "clean rendition" API params, opaque token decoding (AES-CBC from a derived key), metadata scraping without JSON parsing, dedupe by CDN asset key, and the MV3 landmines that silently break all of it. Use when the user says "learn from this extension", "build a downloader extension", "intercept network media", "MV3 service worker", "grab the 1080p version", or hands over an unpacked Chrome extension to study, harden or clone.
---

# Chrome MV3 Media Interceptor

Learned by taking apart **MNS Graphix "Dola 1080P Downloader"** (v1.0.0, 4 JS files, 1 260 lines)
line by line, then fixing it. Two halves: **how the trick works** (so it can be rebuilt for
another site) and **why it quietly breaks** (so the rebuild doesn't rot).

The pattern generalises to any single-page app that streams a chat response and hands the
browser a *signed, sometimes obfuscated* URL for the resulting media.

---

## 1. The shape of the solution

A web app cannot be intercepted from an extension's isolated world alone, because the page's
`fetch`/`XMLHttpRequest` live in the **main world**. So the design is three worlds and five files:

```
 MAIN WORLD (the page's own JS context)
   interceptor.js   ← injected as a <script src=chrome.runtime.getURL(...)> tag
        │            patches fetch + XHR, sniffs responses
        │  window.postMessage({type:'APP_NEW_MEDIA', media})
        ▼
 ISOLATED WORLD (content script, has chrome.* APIs)
   content.js       ← validates, matches media to on-page cards, in-page buttons
        │  chrome.runtime.sendMessage({type:'NEW_MEDIA_DETECTED'})
        ▼
 EXTENSION (service worker, no DOM, can fetch cross-origin with host permissions)
   background.js    ← dedupe, decode, download, notify, badge, persistence
        ▲
        │  chrome.runtime.sendMessage
   popup.html/js    ← the only UI the user actually clicks
```

`interceptor.js` must be listed in `web_accessible_resources` for the page to load it. The
modern alternative is `"world": "MAIN"` in the content_scripts entry (Chrome 111+); the
script-tag trick still works everywhere and keeps the hook out of the manifest's content
script list, which is why it survives on older builds.

**Rule:** whoever holds `chrome.*` must never trust a message that came from the page.

---

## 2. Sniffing without breaking the stream

The response that carries the media reference is usually **`text/event-stream`** — a token
stream that arrives in dozens of chunks over 10–40 s. You cannot buffer it and parse once, and
you must not consume it (the app still needs it). So: **clone, read the clone, keep a growing
buffer, re-scan the tail of it.**

```js
const originalFetch = window.fetch;
window.fetch = async function (...args) {
  const response = await originalFetch.apply(this, args);
  const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');

  if (interesting(url)) {
    const clone = response.clone();                     // page keeps the original
    const reader = clone.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    (async () => {
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });   // stream:true — multi-byte safe
        scan(buffer);                                        // re-scan the whole buffer
      }
    })().catch(() => {});
  }
  return response;                                       // hand the original straight back
};
```

Three details that matter:

| Detail | Why |
|---|---|
| `response.clone()` **before** any body read | the app's own `await res.json()` must still work |
| `decoder.decode(value, {stream: true})` | without it a UTF-8 character split across chunks becomes  and the regex misses |
| accumulate and **re-scan the buffer**, not the chunk | the JSON key you need is regularly split across two chunks |

Also wrap `XMLHttpRequest` (`open` records `this._url`, `send` adds a `load` listener) — some
legacy paths never use `fetch`. And scan `document.documentElement.innerHTML` ~1.5 s after
load, because older chats are server-rendered and will never appear in a fetch.

---

## 3. "Clean rendition" is usually a query param

The page's own API answer contains *two* kinds of URL: a **display** asset (watermarked,
capped) and a **fallback_api** endpoint that can serve the original. The trick is not a
decryption, it is a **flag flip** — the endpoint already knows how to serve the clean file,
it is just asked not to:

```js
u.searchParams.set('channel',    'no');            // server default: 'yes' → branded
u.searchParams.set('codec_type', '8');             // h264 vs the streaming codec
u.searchParams.set('logo_type',  'unwatermarked'); // the whole point
```

Generalise: open DevTools → Network, capture the request the page makes for its player, then
compare it with the request it makes when it renders a *preview* or an export. The difference
is normally one or two query params, or a different `Referer`. Flip them.

Resolve from **two places at once** — the service worker (`fetch`, no CORS, uses host
permissions) *and* the page (`originalFetch(..., {credentials:'include'})`, carries the
session cookie). Whichever wins first posts the media; the loser is deduped. Belt and braces
beats a 30 %-failure rate on cookie-gated endpoints.

---

## 4. When the URL is a blob, not a URL

The `main_url` field may be an opaque token, e.g. `qAAB…` — base64 with `$ @ #` substituted
for `_ / =`, wrapping an **AES-CBC** ciphertext. The key material travels in the *same*
response as a `key_seed`. The derivation, as recovered:

```js
seed    = b64(seedB64)                       // first 32 bytes are used
d1      = SHA-512(seed[0..32])
salt    = hexToBytes(SALT_HEX)               // 32-byte constant lifted from the client bundle
d2      = SHA-512(d1 ‖ salt)                 // 64 bytes
key     = d2[0..16]
iv      = d2[16..32]
plain   = AES-CBC-decrypt(ciphertext, key, iv)   // PKCS#7
url     = ascii(plain)                        // must match /^https?:\/\//
```

**Never trust one layout.** The build tried four before giving up — and that is the actual
craft here: a header-branch (`A8 00 01 00` magic) means the ciphertext starts at offset 4, and
some variants embed a 16-byte IV at offset 20 with the payload from offset 36. Also try
key/iv swapped. Cheap permutations, big robustness win:

```js
attempts = [
  { payload: data.slice(4),  key, iv },
  { payload: data.slice(4),  key: iv, iv: key },
  { payload: data.slice(36), key, iv: data.slice(20, 36) },
  { payload: data.slice(36), key, iv },
];
```

All of this runs in `crypto.subtle`, so it works in a service worker (no Node crypto, no WASM).
Keep a plain-base64 path first — half of all tokens are just base64 of the URL.

---

## 5. Metadata without a JSON parser

You have a partially-arrived event stream, so `JSON.parse` is off the table. Scrape **a window
around the match** instead, and always match both the escaped and unescaped form, because the
same payload appears quoted inside a JSON string:

```js
const slice = text.slice(Math.max(0, i - 2000), i + 2000);
/\b"prompt"\s*:\s*"([^"]+)"/g           // normal
/\\"(?:prompt|query|content)\\"\s*:\s*\\"(.*?)\\"/g   // double-escaped inside a string
```

Normalise `\\u0026 → &` and `\\/ → /` before validating a URL — CDN links are almost always
escaped. Unescape a string properly with `JSON.parse('"' + s + '"')` inside a `try`; do not
hand-roll it.

---

## 6. Identity: dedupe by asset key, rank by pixels

The same video is re-issued constantly with fresh signatures, so `url` is a terrible key.
ByteDance-style CDN paths carry a stable object key:

```
/tos-<bucket>/<assetKey>~tplv-xxxx:...    →  assetKey
```

Use `assetKey(poster) || assetKey(url) || vid` as identity; fall back to `vid`, then to the
full URL. Without this you get the same clip three times in the list — which users read as
"the downloader is broken".

Ranking, when several renditions arrive:

```js
score = bitrate + width * height        // then pick the first max, not the last
```

---

## 7. The handoff protocol (copy this table into any clone)

| Message | From → To | Payload | Answer |
|---|---|---|---|
| `NEW_MEDIA` | interceptor → content (`window.postMessage`) | `{vid,url,poster,prompt,width,height,ts}` | — |
| `RESOLVE_FALLBACK` | interceptor → content | `{fallbackUrl,keySeed,meta}` | — |
| `NEW_MEDIA_DETECTED` | content → background | same media | `{ok}` |
| `FETCH_AND_RESOLVE_FALLBACK` | content → background | same as above | `{ok, media}` |
| `NEW_MEDIA_RESOLVED` | background → content | media | — |
| `TRIGGER_DOWNLOAD` | popup/content → background | `{media}` | `{ok, downloadId, filename}` |
| `GET_CAPTURED_VIDEOS` | popup/content → background | — | `{videos, config}` |
| `GET_PAGE_ORDERED_VIDEOS` | popup → content | — | `{videos}` (DOM order) |
| `UPDATE_CONFIG` | popup → background | `{config}` | `{ok, config}` |

Two sources of truth on purpose: the background keeps capture order (survives tab reloads),
the content script keeps **page order** (what the user sees as Scene 1, 2, 3). The popup asks
the page first and falls back to the worker.

---

## 8. MV3 landmines — learned the hard way

Each of these was a real bug in the reference build. They are rules now.

| # | Landmine | Symptom | Fix |
|---|---|---|---|
| 1 | **Service worker memory dies after ~30 s idle** | popup shows 0 videos a minute after you watched them | mirror the list to `chrome.storage.session` (debounced), rehydrate on wake |
| 2 | **Async config load races your first write** | toggles reset, `totalDownloaded` jumps back to 0 | one `configReady` promise; every writer `await`s it |
| 3 | **`+ ".mp4"` on a name that already ends in `.mp4`** | `…_Scene_1.mp4.mp4` | one function owns the extension |
| 4 | **Inline `onerror=` / `onclick=` in extension HTML** | silently blocked by CSP, no console error | `addEventListener` |
| 5 | **Burst of `downloads.download` calls** | 30-scene story, 21 files | sequential, `await` each, ~400 ms apart |
| 6 | **Counting starts instead of finishes** | badge says 12, folder has 9 | `chrome.downloads.onChanged` → `state === 'complete' \| 'interrupted'` |
| 7 | **Unused permission** | extra install warning, store review flag | never ship `declarativeNetRequest` unless `rule_resources` exist |
| 8 | **UTF-8 BOM in `manifest.json`** | OK in Chrome, breaks every JSON tool | strip it |
| 9 | **`chrome.tabs.sendMessage` to a non-app tab** | promise rejects, popup spins forever | check `chrome.runtime.lastError`, fall back |
| 10 | **Unbounded `Set`s/arrays** in the worker | slow start after a long session | cap at N and evict |

---

## 9. Security rules for anything that reads the DOM or the network

- **Validate `window.message`**: `if (event.source !== window) return;` — otherwise any
  iframe on the page can post a fake payload that makes your privileged worker fetch an
  arbitrary URL.
- **Allow-list the hosts** you will `fetch` for the user: scheme `https:`, host in a regex of
  known API/CDN domains. Same for the URL you hand to `downloads.download`.
- **Escape page text before `innerHTML`**: prompt strings are user-generated content living in
  your extension's privileged page. `esc()` every string, `safeHttp()` every URL.
- **Narrow `host_permissions`** to what the app actually needs; put the wide
  `https://*/*` in `optional_host_permissions` and request it from a popup button
  (`chrome.permissions.request`, must be inside a user gesture). Ship-wide permissions are
  what get extensions delisted.
- **Never ship the page's own session token anywhere.** Everything stays local;
  `crypto.subtle` in the worker is enough.

---

## 10. Ship checklist

```
[ ] manifest: no unused permissions, no BOM, minimum_chrome_version set
[ ] every file referenced by the manifest exists (script the check, 10 refs is enough to typo)
[ ] node --check every .js  (or esbuild --bundle --outfile=/dev/null)
[ ] storage.session persistence + rehydrate path exercised by killing the worker
[ ] downloads.onChanged wired; badge counts completions
[ ] popup empty state renders with the worker dead
[ ] every chrome.runtime message type has exactly one listener (grep the table above)
[ ] host allow-list + event.source check in the content script
[ ] filenames: one extension, sanitised, collision-safe (conflictAction:'uniquify')
```

---

## 11. Scope and ethics

Read the target's Terms of Service before shipping. A local, personal "save my own generations"
tool and a redistributed bypass tool are the same code and different products. Keep the
processing on-device, never proxy traffic through a server you control, and never resell what
the extension fetches.

---

## Reference implementation

`skeleton/` in this skill folder is a **generic, cleaned-up clone** of the architecture above —
same three-world split, persistence, allow-list, completion accounting and sequential batch
download — with the app-specific bits (host names, the token salt) removed. Start there.
