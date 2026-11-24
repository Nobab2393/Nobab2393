# Skeleton — generic media interceptor

A cleaned-up clone of the architecture in `../SKILL.md`, with everything app-specific removed.
Valid as-is (`node --check` clean, every manifest reference resolves) but it will capture
nothing until you point it at a real site.

## Adapt it in five edits

1. **`manifest.json`** — replace the three `*.example.com` hosts in `host_permissions`,
   `content_scripts.matches` and `web_accessible_resources.matches`.
2. **`interceptor.js` → `CONFIG.watch`** — the request URLs that carry media references
   (DevTools → Network, look for `text/event-stream`).
3. **`interceptor.js` → `CONFIG.tokenFields`** — the JSON fields holding the media URL or
   token. Add the query-param flips (the "clean rendition" flags) next to it.
4. **`content.js` → `ALLOWED_HOSTS`** — the CDN hostnames the downloader may touch. Keep this
   list as short as the site lets you.
5. **`background.js` → `assetKey()`** — the CDN path rule that identifies one clip. If your CDN
   has no stable key, fall back to `vid` and accept weaker dedupe.

If the token comes back as an encrypted blob rather than base64, port the AES-CBC derivation
from `../SKILL.md` §4 into `resolveToken()`.

## Load it

`chrome://extensions` → Developer mode → **Load unpacked** → this folder.

## What already works

- main-world `fetch`/XHR hook with stream-safe buffering and `stream: true` decoding
- `event.source` check + host allow-list before anything reaches the worker
- `storage.session` persistence, so the list survives the worker being killed
- one `.mp4` in the filename, sanitised, `conflictAction: 'uniquify'`
- completion-accurate counter via `downloads.onChanged`
- sequential batch download (no burst throttling)
- escaped page text in the popup, `error` listener instead of inline `onerror`
- optional `https://*/*` behind a user-gesture button instead of a permanent install warning
