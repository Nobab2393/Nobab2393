// interceptor.js — MAIN world. Patches fetch + XHR and posts media to the content script.
// Nothing here touches chrome.*; it only reads what the page already receives.
(function () {
  'use strict';
  if (window.__MEDIA_INTERCEPTOR__) return;
  window.__MEDIA_INTERCEPTOR__ = true;

  const CONFIG = {
    // requests worth reading (streaming chat / feed endpoints)
    watch: [/\/api\/chat/, /\/api\/generate/, /\/api\/feed/],
    // fields that may hold a media reference
    tokenFields: ['main_url', 'play_url', 'url'],
    // query params that turn a branded/preview asset into the clean one (example values)
    cleanParams: {},
  };

  const seen = new Set();

  // ---- base64 helpers (loose: URL-safe, and $ @ # substitutions) -------------
  function b64Loose(text) {
    const input = String(text || '').trim();
    const variants = [
      input,
      input.replace(/[$@#]/g, (c) => ({ $: '_', '@': '/', '#': '.' }[c])),
      input.replace(/[$@#]/g, (c) => ({ $: '+', '@': '/', '#': '=' }[c])),
    ];
    for (const candidate of variants) {
      try {
        const norm = candidate.replace(/-/g, '+').replace(/_/g, '/');
        const padded = norm + '='.repeat((4 - (norm.length % 4)) % 4);
        const bin = atob(padded);
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        return bytes;
      } catch { /* try the next variant */ }
    }
    return null;
  }

  function asciiUrl(bytes) {
    if (!bytes || !bytes.length) return '';
    for (const b of bytes) {
      if (b !== 9 && b !== 10 && b !== 13 && (b < 32 || b > 126)) return '';
    }
    return new TextDecoder().decode(bytes);
  }

  // A token may be a plain URL, base64 of a URL, or an encrypted blob. Only the first two
  // are handled generically — see SKILL.md §4 for the AES-CBC derivation.
  function resolveToken(token) {
    if (!token) return '';
    if (/^https?:\/\//i.test(token.trim())) return token.trim();
    const text = asciiUrl(b64Loose(token));
    return /^https?:\/\//i.test(text) ? text : '';
  }

  function bestToken(data) {
    const list = data?.video_list ? Object.values(data.video_list) : [data];
    let best = '';
    let max = -1;
    for (const item of list) {
      const tok = CONFIG.tokenFields.map((f) => item?.[f]).find(Boolean);
      if (!tok) continue;
      const score = Number(item?.bitrate || 0) + Number(item?.width || 0) * Number(item?.height || 0);
      if (score > max) { max = score; best = tok; }
    }
    return best;
  }

  function scan(text) {
    if (!text || text.length < 20) return;
    // find media tokens by proximity — no JSON.parse, the stream is partial
    for (const field of CONFIG.tokenFields) {
      const re = new RegExp(`"${field}"\\s*:\\s*"([^"]+)"`, 'g');
      let m;
      while ((m = re.exec(text)) !== null) {
        const url = resolveToken(m[1]);
        if (!url || seen.has(url)) continue;
        seen.add(url);
        const slice = text.slice(Math.max(0, m.index - 1500), m.index + 1500);
        window.postMessage({
          type: 'APP_NEW_MEDIA',
          media: {
            url,
            vid: (slice.match(/"vid"\s*:\s*"([^"]+)"/) || [])[1] || '',
            poster: (slice.match(/"poster(?:_url)?"\s*:\s*"([^"]+)"/) || [])[1] || '',
            prompt: (slice.match(/"prompt"\s*:\s*"([^"]+)"/) || [])[1] || '',
            width: Number((slice.match(/"width"\s*:\s*(\d+)/) || [])[1] || 0),
            height: Number((slice.match(/"height"\s*:\s*(\d+)/) || [])[1] || 0),
            timestamp: Date.now(),
          },
        }, window.location.origin);          // explicit target origin, never '*'
      }
    }
  }

  function interesting(url) {
    return !!url && CONFIG.watch.some((re) => re.test(url));
  }

  // ---- fetch ----------------------------------------------------------------
  const realFetch = window.fetch;
  window.fetch = async function (...args) {
    const response = await realFetch.apply(this, args);
    const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
    if (interesting(url)) {
      const clone = response.clone();                 // the page keeps the original
      const reader = clone.body && clone.body.getReader ? clone.body.getReader() : null;
      if (reader) {
        const decoder = new TextDecoder();
        let buffer = '';
        (async () => {
          for (;;) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });   // multi-byte safe
            scan(buffer);                                        // re-scan the whole buffer
          }
        })().catch(() => {});
      } else {
        clone.text().then(scan).catch(() => {});
      }
    }
    return response;
  };

  // ---- XHR ------------------------------------------------------------------
  const realOpen = XMLHttpRequest.prototype.open;
  const realSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (method, url, ...rest) {
    this.__url = url;
    return realOpen.call(this, method, url, ...rest);
  };
  XMLHttpRequest.prototype.send = function (...args) {
    this.addEventListener('load', function () {
      if (this.__url && interesting(String(this.__url))) {
        try { scan(this.responseText); } catch { /* binary body */ }
      }
    });
    return realSend.apply(this, args);
  };

  // Server-rendered history never appears in a fetch response.
  setTimeout(() => scan(document.documentElement.innerHTML), 1500);
})();
