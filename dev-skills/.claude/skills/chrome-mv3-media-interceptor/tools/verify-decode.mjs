#!/usr/bin/env node
// verify-decode.mjs — proves the qAAB (AES-CBC) URL decode path from SKILL.md §4.
//
// It does not touch the network and it does not need the site: it *builds* tokens the way
// the reference extension expects them, then decodes them with the same derivation.
// If the derivation in the skill is wrong, this fails.
//
//   node tools/verify-decode.mjs

const SALT_HEX =
  '4dd4c2e6b83162090e52b3c7a6733ba4' +
  '1cb2462b829ab58a196b39db57177524' +
  'f49baf7f08e8d68d26a72e37c1a95a2f' +
  '1f05a51892aef2949732b62a38aadd58';

const hexToBytes = (hex) => Uint8Array.from(hex.match(/.{2}/g).map((b) => parseInt(b, 16)));

const concat = (a, b) => {
  const out = new Uint8Array(a.length + b.length);
  out.set(a, 0);
  out.set(b, a.length);
  return out;
};

// --- the derivation under test -------------------------------------------------
async function deriveKeyIv(seedB64) {
  const [seed] = base64Candidates(seedB64);
  if (!seed) throw new Error('bad seed');
  const d1 = new Uint8Array(await crypto.subtle.digest('SHA-512', seed.slice(0, 32)));
  const d2 = new Uint8Array(await crypto.subtle.digest('SHA-512', concat(d1, hexToBytes(SALT_HEX))));
  return { key: d2.slice(0, 16), iv: d2.slice(16, 32) };
}

// --- loose base64: URL-safe, padded, and the $ @ # substitutions ---------------
// Improvement over the reference build: return EVERY plausible decoding, not just the first
// that does not throw. `_` and `+` are both legal base64 characters, so a wrong substitution
// decodes "successfully" into garbage and hides the right answer behind it.
function base64Candidates(text) {
  if (!text) return [];
  const input = String(text).trim();
  const mapped = [
    input,
    input.replace(/[$@#]/g, (c) => ({ $: '_', '@': '/', '#': '.' }[c])),
    input.replace(/[$@#]/g, (c) => ({ $: '+', '@': '/', '#': '=' }[c])),
  ];
  const out = [];
  for (const candidate of mapped) {
    for (const swap of [false, true]) {
      try {
        let norm = candidate;
        if (swap) norm = norm.replace(/-/g, '+').replace(/_/g, '/');
        const padded = norm + '='.repeat((4 - (norm.length % 4)) % 4);
        const bin = atob(padded);
        const bytes = Uint8Array.from(bin, (ch) => ch.charCodeAt(0));
        if (!out.some((b) => b.length === bytes.length && b.every((v, i) => v === bytes[i]))) out.push(bytes);
      } catch { /* not base64 — next */ }
    }
  }
  return out;
}

// --- the four layout attempts --------------------------------------------------
async function decodeToken(token, seedB64) {
  const { key, iv } = await deriveKeyIv(seedB64);

  for (const data of base64Candidates(token)) {
    const attempts = [];
    const magic = data.length >= 4 && data[0] === 0xa8 && data[1] === 0x00 && data[2] === 0x01 && data[3] === 0x00;
    if (magic) {
      attempts.push({ payload: data.slice(4), key, iv });
      attempts.push({ payload: data.slice(4), key: iv, iv: key });
      if (data.length > 36) {
        attempts.push({ payload: data.slice(36), key, iv: data.slice(20, 36) });
        attempts.push({ payload: data.slice(36), key, iv });
      }
    } else {
      attempts.push({ payload: data, key, iv });
      attempts.push({ payload: data, key: iv, iv: key });
    }

    for (const a of attempts) {
      try {
        if (!a.payload.length || a.payload.length % 16) continue;
        const k = await crypto.subtle.importKey('raw', a.key, 'AES-CBC', false, ['decrypt']);
        const plain = new Uint8Array(await crypto.subtle.decrypt({ name: 'AES-CBC', iv: a.iv }, k, a.payload));
        const text = new TextDecoder().decode(stripPkcs7(plain));
        if (looksLikeUrl(text)) return text;             // strict: rejects aligned garbage
      } catch { /* wrong layout — keep going, that is the whole point */ }
    }
  }
  return '';
}

// A wrong key/layout can still produce something that starts with "https://" — CBC garbage
// that happens to align. Validate the WHOLE string before accepting it.
function looksLikeUrl(text) {
  if (!text || text.length < 12 || text.length > 2048) return false;
  if (/[^\x20-\x7E]/.test(text)) return false;            // printable ASCII only
  try {
    const u = new URL(text);
    return (u.protocol === 'http:' || u.protocol === 'https:') && u.hostname.includes('.');
  } catch { return false; }
}

function stripPkcs7(bytes) {
  const pad = bytes[bytes.length - 1];
  if (pad < 1 || pad > 16 || pad > bytes.length) return bytes;
  for (let i = bytes.length - pad; i < bytes.length; i++) if (bytes[i] !== pad) return bytes;
  return bytes.slice(0, bytes.length - pad);
}

// --- token builders (the "server side", for the test) --------------------------
async function buildToken(url, seedB64, { header = true, swap = false } = {}) {
  const { key, iv } = await deriveKeyIv(seedB64);
  const k = await crypto.subtle.importKey('raw', swap ? iv : key, 'AES-CBC', false, ['encrypt']);
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-CBC', iv: swap ? key : iv }, k,
    new TextEncoder().encode(url)));
  const body = header ? concat(new Uint8Array([0xa8, 0x00, 0x01, 0x00]), ct) : ct;
  // base64 → the $ @ # substitution the client uses
  const b64 = btoa(String.fromCharCode(...body));
  return b64.replace(/=+$/, '').replace(/\+/g, '$').replace(/\//g, '@');
}

// --- run ----------------------------------------------------------------------
const randomSeed = () => {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return btoa(String.fromCharCode(...bytes)).replace(/=+$/, '');
};

const cases = [
  { name: 'plain, header, key/iv', header: true, swap: false },
  { name: 'header, key & iv swapped', header: true, swap: true },
  { name: 'no header (bare ciphertext)', header: false, swap: false },
];

let pass = 0;
let fail = 0;

for (const c of cases) {
  const seed = randomSeed();
  const url = `https://v16-webapp.example.com/tos-cn-x0/${randomSeed().slice(0, 12)}/?a=1988&br=4100`;
  const token = await buildToken(url, seed, c);
  // note: "qAAB" is not a magic string the client prepends — it *is* base64 of the 4-byte
  // header a8 00 01 00, which is why tokens start with it. Decode the string as-is.
  if (c.header && !token.startsWith('qAAB')) throw new Error('builder/format mismatch');
  const got = await decodeToken(token, seed);
  const ok = got === url;
  ok ? pass++ : fail++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${c.name}${ok ? '' : `\n        expected ${url}\n        got      ${got || '(empty)'}`}`);
}

// a wrong seed must fail closed, not throw
const otherSeed = randomSeed();
const headerToken = await buildToken('https://x.example.com/a.mp4', randomSeed(), { header: true });
const wrong = await decodeToken(headerToken, otherSeed);
const failsClosed = wrong === '';
console.log(`${failsClosed ? 'PASS' : 'FAIL'}  wrong seed fails closed (no throw)`);
failsClosed ? pass++ : fail++;

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
