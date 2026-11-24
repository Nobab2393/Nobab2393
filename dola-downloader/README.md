# MNS Graphix — Dola 1080P Downloader (Chrome MV3)

A Manifest V3 extension that watches the network traffic of **Dola AI / Doubao** chat pages,
finds the **unwatermarked 1080P** rendition of every generated video, and saves them to
`Downloads/MNS_Graphix_Dola_Videos/` — one click per clip, or all of them in scene order.

This repo copy is your uploaded build (`v1.0.0`) with a handful of real bugs fixed.
See **[AUDIT.md](AUDIT.md)** for exactly what changed and what is still open.

---

## Install (unpacked)

1. Download this folder (or `git clone` and use the `dola-downloader/` directory).
2. Open `chrome://extensions` → enable **Developer mode** (top right).
3. **Load unpacked** → select the `dola-downloader` folder.
4. Pin the extension. Open `dola.com` (or `doubao.com`), play / generate a video,
   then click the toolbar icon.

Requires **Chrome 116+** (uses `chrome.storage.session` so the captured list survives the
service worker being killed).

## Using it

| Control | What it does |
|---|---|
| **TOTAL SAVED** | lifetime download count (also the number on the toolbar badge) |
| **DETECTED** | how many videos the current session has captured |
| **AUTO-SAVE** | download every new video the moment it is resolved |
| **NOTIFY** | desktop notification on each save |
| **Save** (per row) | one clip → `MNS_Graphix_Dola_Videos/MNSGraphix_<date>_<time>_<prompt>.mp4` |
| **🔍** | opens the raw CDN URL in a tab |
| **📥 Download All** | saves every listed clip in scene order, 400 ms apart |

Rows are sorted by `sceneIndex` → `Scene N` in the prompt → capture time, so a multi-scene
story downloads in the order it was written, not the order it was cached.

---

## How it works

```
page (dola.com)
  ├── page-interceptor.js   ← injected into the MAIN world at document_start
  │      hooks fetch() and XMLHttpRequest, sniffs JSON responses for
  │      video_list / main_url / play_url, and re-requests the fallback API with
  │      channel=no & codec_type=8 & logo_type=unwatermarked
  │      ↓ window.postMessage('NUMAN_MUGHAL_*')
  ├── content.js            ← isolated world; matches media to on-page cards,
  │      orders them by DOM position, injects the in-page Save buttons
  │      ↓ chrome.runtime.sendMessage
  ├── background.js         ← service worker; dedupes, decodes `qAAB` tokens
  │      (SHA-512 seed → AES-CBC key/iv), downloads, notifies, keeps the badge
  └── popup.js / popup.html ← the HUD; lists, sorts, saves, toggles settings
```

**Token decode** (`decodeQaabToken`): the CDN URL arrives base64'd as a `qAAB…` blob.
The key is derived from the `key_seed` that travels with the response —
`SHA-512(seed[0..32])` → `SHA-512(digest1 ‖ SALT)` → first 16 bytes = AES key,
next 16 = IV — and several layouts are tried (header-stripped, key/iv swapped, embedded IV)
before giving up. Everything happens locally with `crypto.subtle`; nothing leaves the browser.

## File map

| File | Lines | Role |
|---|---|---|
| `manifest.json` | 64 | MV3 manifest, Dola/Doubao host permissions |
| `background.js` | ~400 | service worker: capture store, token decode, downloads |
| `page-interceptor.js` | 366 | main-world network hook |
| `content.js` | 341 | card matching, ordering, in-page buttons |
| `popup.js` / `popup.html` / `popup.css` | 178 / 119 / 490 | the HUD |
| `content.css` | 115 | in-page button styling |
| `icon16/48/128.png` | — | logo |

## Permissions, and why they're there

| Permission | Reason |
|---|---|
| `downloads` | saving the resolved file |
| `storage` | settings + the captured-video list (`storage.session`) |
| `notifications` | “Saved” toasts |
| `host_permissions: https://*/*` | the CDN host changes per video (`*.ibytedtos.com`, `*.byteintlapi.com`, …) and the fallback API call is cross-origin. **This is broad** — it is the price of an unwatermarked-URL resolver. If you ever publish to the Web Store, expect review friction on this one (see AUDIT). |

## Rebuilding / editing

Plain ES2020, no build step, no bundler, no npm. Edit the file, hit ↻ on
`chrome://extensions`, reload the tab.
