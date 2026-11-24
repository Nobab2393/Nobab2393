# AUDIT — MNS Graphix Dola Downloader v1.0.0

Review of the uploaded build. Everything below was found by reading the four JS files and
the manifest, then checking them with `node --check` (all parse clean). Grouped by severity.

---

## 🔴 Bugs that broke behaviour — **fixed in this copy**

### 1. Every saved file was `.mp4.mp4`
```js
// background.js, before
const filename = generateFilename(media) + ".mp4";
```
`generateFilename()` already returns `…_<slug>.mp4`, so the string was doubled and the
downloader produced `MNSGraphix_2026-11-23_…_Scene_1.mp4.mp4`. Chrome accepted it, so
nothing looked broken until you opened the folder. **Now: single `.mp4`.**

### 2. The captured list vanished whenever the worker slept
`capturedVideos` lived only in service-worker memory. MV3 kills an idle worker after ~30 s,
so opening the popup a minute after watching the videos showed “DETECTED 0” and an empty
list — the videos were still on the page, so the in-page path still worked, which made it
look random. **Now: mirrored to `chrome.storage.session` (debounced 200 ms) and rehydrated on
wake-up.** Requires Chrome 116+, declared as `minimum_chrome_version`.

### 3. A fast message could wipe your settings
Config loads asynchronously, but `UPDATE_CONFIG` and `triggerDownload` wrote
`chrome.storage.local` immediately. Toggling AUTO-SAVE within the first few hundred
milliseconds of a worker start could persist the **defaults** over your saved settings —
including `totalDownloaded: 0`. **Now: a `configReady` promise that every writer awaits.**

### 4. Broken thumbnails never fell back
```html
<img … onerror="this.outerHTML='…'">
```
Inline event handlers are blocked by the MV3 extension CSP (`script-src 'self'`), so the
fallback tile never appeared — dead posters stayed as broken-image icons. **Now: a real
`error` listener, attached per thumbnail.**

### 5. Page text was interpolated straight into the popup DOM
`video.prompt` went into `innerHTML` unescaped, and `video.poster` into an `src` without a
scheme check — anything the page put in a prompt string could inject markup into the
extension's own privileged page. **Now: `esc()` on every string, `safeHttp()` on every URL.**

## 🟠 Robustness — **fixed**

### 6. “Download All” fired N `sendMessage` calls in the same tick
Chrome throttles/queues bursts; with 20–30 scenes some downloads silently didn't start.
**Now: sequential, awaiting each response, 400 ms apart**, button disabled while running.

### 7. `chrome.tabs.sendMessage` failure was unhandled
On a non-Dola tab (or before the content script is ready) the callback fired with
`lastError` set and the popup stalled on a blank state. **Now: `lastError` → fall back to the
background list immediately.**

### 8. `downloadedKeys` grew forever
One entry per auto-downloaded video, never trimmed. Small, but a long-lived browser session
leaks. **Now: cleared past 500 entries.**

## 🟡 Manifest hygiene — **fixed**

### 9. `declarativeNetRequest` was declared and never used
No `declarative_net_request.rule_resources`, no `updateDynamicRules()` call anywhere in the
code. An unused permission is an extra install warning and a Web Store review flag.
**Now: removed** (add `declarativeNetRequestWithHostAccess` back the day you actually need a
header/UA rewrite rule).

### 10. Byte-order mark on `manifest.json`
The file began with `EF BB BF`. Chrome tolerates it, but every JSON tool that touches the
manifest — and some build steps — will choke. **Now: stripped and re-serialised (2-space).**

---

## 🔵 Still open — deliberately not touched

| # | Issue | Why it's open | Suggested fix |
|---|---|---|---|
| 1 | `host_permissions: "https://*/*"` | Narrowing it would break resolution for CDNs that aren't in the list today. It is genuinely broad. | Move to `optional_host_permissions` + a “Grant wide access” button; keep the four ByteDance hosts required. |
| 2 | `content.js` trusts any `window.message` | Any script on the page (or a malicious iframe) can post a fake `NUMAN_MUGHAL_*` message and make the worker fetch an arbitrary URL. | Check `event.source === window` and validate `fallbackUrl` against an allow-list of hosts before fetching. |
| 3 | `processedApis` / `processedUrls` are unbounded `Set`s | Same shape as #8, larger. | Evict oldest past N, or key them to a session id. |
| 4 | `extractTOSKey()` is guesswork | The `tos-…/<key>` regex is inferred from observed URLs; it silently returns `''` on a new CDN layout, which degrades dedupe to `vid`-only. | Log a miss counter and surface it in the popup when dedupe falls back. |
| 5 | No `chrome.downloads.onChanged` tracking | The badge counts *starts*, not successes. A failed download still increments TOTAL SAVED. | Listen for `state: 'interrupted'` and decrement / mark the row. |
| 6 | `README`/popup say “1080P” unconditionally | `pickBestToken()` picks the highest bitrate×area, which may be 720p on older clips. | Label the row with the real `width×height` (the data is already in `media`). |
| 7 | No i18n, no dark/light switch | Cosmetic. | — |
| 8 | Extension name says “Without Watermark” | Fine for personal use; Web Store review reads it as circumvention. | Rename to “Dola 1080P Saver” if you ever publish. |

---

## Verification performed

- `node --check` on `background.js`, `content.js`, `page-interceptor.js`, `popup.js` — all clean.
- `manifest.json` parsed as JSON; all **10** referenced files exist on disk (worker, popup,
  content js/css, 3 icons, 2 web-accessible resources).
- Static trace of all 8 `chrome.runtime` message types: `NEW_MEDIA_DETECTED`,
  `NEW_MEDIA_RESOLVED`, `FETCH_AND_RESOLVE_FALLBACK`, `TRIGGER_DOWNLOAD`,
  `GET_CAPTURED_VIDEOS`, `GET_PAGE_ORDERED_VIDEOS`, `UPDATE_CONFIG` — every one has a
  listener, and every `sendResponse` path either replies synchronously or returns `true`.
- Not run in a browser: this sandbox has no Chromium and no access to `dola.com`, so the
  network hook and the `qAAB` decode path are reviewed by reading only.
