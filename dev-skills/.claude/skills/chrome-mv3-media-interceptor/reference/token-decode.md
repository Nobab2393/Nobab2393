# The `qAAB` token, and the two bugs the tests found in the original

Everything here was verified with [`../tools/verify-decode.mjs`](../tools/verify-decode.mjs) —
run it, it builds tokens the way the server does and decodes them the way the extension does.

## 1. "qAAB" is not a brand, it is base64

```
a8 00 01 00   →  base64  →  "qAAB"   ( + the rest of the string )
```

Four header bytes — `A8 00 01 00` — are what make a token start with `qAAB`. So
`if (token.startsWith('qAAB'))` is really `if (payload has the 4-byte magic)`, and the string
must be decoded **whole**, prefix included. The reference build got this right by accident
(it checks the prefix, then passes the full string to the decoder); a re-implementation that
strips the "prefix" first will decrypt nothing, forever.

| Bytes | Meaning |
|---|---|
| `a8 00 01 00` | magic / version |
| `…` | AES-CBC ciphertext, PKCS#7 padded, 16-byte aligned |

## 2. Key derivation

```
seed    = base64(key_seed)                 // travel with the same API response
d1      = SHA-512(seed[0 .. 32])           // only the first 32 bytes of the seed
salt    = 32-byte constant                 // lifted from the site's own JS bundle
d2      = SHA-512(d1 ‖ salt)               // 64 bytes
key     = d2[0 .. 16]
iv      = d2[16 .. 32]
plain   = AES-CBC-decrypt(ciphertext, key, iv)
```

`d2` is deliberately over-provisioned: 64 bytes of digest, of which only the first 32 are used,
split into key and IV. That split is why the "swapped key/iv" attempt exists at all — both
halves are equally plausible as either role when you are reverse-engineering blind.

## 3. Why four attempts and not one

The header tells you the ciphertext starts at offset 4 — but some builds put a 16-byte IV at
offset 20 and start the ciphertext at 36, and some swap key for IV. Each permutation costs one
`crypto.subtle.decrypt` promise, and a failed decrypt throws, so the loop is cheap:

| # | payload | key | iv |
|---|---|---|---|
| 1 | `data[4..]` | `d2[0..16]` | `d2[16..32]` |
| 2 | `data[4..]` | `d2[16..32]` | `d2[0..16]` |
| 3 | `data[36..]` | `d2[0..16]` | `data[20..36]` |
| 4 | `data[36..]` | `d2[0..16]` | `d2[16..32]` |

**AES-CBC will happily "decrypt" with the wrong key** — it just produces garbage. So "did it
throw?" is not the success test.

## 4. Bug the test found #1 — the base64 variant ladder short-circuits

The original:

```js
for (const candidate of variants) {
  try { return atob(pad(candidate)); } catch {}
}
```

`_`, `-` and `+` are all legal base64 characters. If a token maps `+` → `$` and the first
variant maps `$` → `_` (not `+`), `atob` **succeeds** — with the wrong bytes — and the function
returns before ever trying the correct substitution. Your derivation is right, your bytes are
wrong, and you will spend an evening blaming the salt.

Fix: return **all** distinct decodings and drive the decrypt attempts over the product.

```js
for (const bytes of base64Candidates(token))     // 2 mappings × (raw | url-safe)
  for (const attempt of layouts(bytes))          // 1–4 permutations
    if (looksLikeUrl(decrypt(attempt))) return url;
```

## 5. Bug the test found #2 — `/^https?:\/\//` accepts garbage

A wrong-key decrypt can still produce bytes that *begin* with `https://` (and, when the
ciphertext is misaligned by a few bytes, even a correct-looking tail). The reference build
accepted any prefix match, so an aligned-garbage plaintext could be handed to
`chrome.downloads.download`.

Fix: validate the whole string.

```js
function looksLikeUrl(text) {
  if (!text || text.length < 12 || text.length > 2048) return false;
  if (/[^\x20-\x7E]/.test(text)) return false;      // printable ASCII only — kills U+FFFD
  try {
    const u = new URL(text);
    return (u.protocol === 'http:' || u.protocol === 'https:') && u.hostname.includes('.');
  } catch { return false; }
}
```

Run `node tools/verify-decode.mjs` with the naive check and the swapped case reproduces the
bug: `https://v16-weba\u000bGb…` — accepted by the prefix test, rejected by the strict one.

## 6. Re-deriving it for a different site

1. **Find the seed.** The response that carries the media almost always carries `key_seed`
   (query string or JSON field). Grep the response body around the token.
2. **Find the salt.** Search the site's JS for a 64-hex-char string near `SHA-512`, `subtle`,
   or `decrypt`. It is a constant, it will be there.
3. **Confirm the shape.** A magic header of `A8 00 01 00`, or a 16/36-byte offset, tells you
   which permutation list to try. Base64-decode the first 8 bytes by hand in the console:
   `atob(token.slice(0, 8))`.
4. **Prove it offline before shipping** — build a token with a seed you control, decode it,
   assert round-trip. That is what `tools/verify-decode.mjs` is for; swap the salt and the
   derivation and it becomes your test for the new site.

## 7. Cost

`crypto.subtle` in a service worker: ~1 ms per attempt, no WASM, no Node crypto, nothing to
ship. Four attempts × a handful of tokens per session is free. The only real cost is the
salt: it is a build-time constant, so a site-side rotation means an extension update.
Pull it from the page at runtime (fetch the bundle, regex the hex) if the target rotates often.
