#!/usr/bin/env node
// match-cards.mjs — pairing a DOM card with a network-captured asset, with confidence.
//
// The reference extension used a 4-tier ladder that ends in `allMedia[i % length]`, which
// silently pairs the WRONG video when the tiers miss. That is worse than failing: the user
// downloads the wrong clip and never knows. This version returns a confidence instead.
//
//   node tools/match-cards.mjs      (runs the built-in tests)

// ---------------------------------------------------------------- asset identity
export function assetKey(url) {
  if (!url) return '';
  try {
    const path = new URL(url, 'https://x.invalid').pathname;
    const m = path.match(/tos-[a-zA-Z0-9_-]+\/([a-zA-Z0-9_-]+)/i);
    if (m) return m[1].split('~')[0].split('.')[0];
    const last = path.split('/').filter(Boolean).pop() || '';
    return last.split('~')[0].split('.')[0];
  } catch {
    return '';
  }
}

function keysOf(media) {
  return [assetKey(media.poster), assetKey(media.url), assetKey(String(media.vid || ''))]
    .filter((k) => k && k.length > 8);
}

// ---------------------------------------------------------------- the ladder
/**
 * @param {{keys: string[], index: number}} card   keys scraped from the card's <img>/<video>
 * @param {Array} media                            captured media, in capture order
 * @param {number} cardCount                       how many cards the page shows
 * @returns {{media: object|null, confidence: 'exact'|'substring'|'positional'|'none', reason: string}}
 */
export function pickMedia(card, media, cardCount = media.length) {
  if (!media.length) return { media: null, confidence: 'none', reason: 'nothing captured yet' };

  // Tier 1 — exact asset key. A key that matches more than one capture is not a match at all.
  for (const key of card.keys) {
    const hits = media.filter((m) => keysOf(m).includes(key));
    if (hits.length === 1) return { media: hits[0], confidence: 'exact', reason: `key ${key}` };
    if (hits.length > 1) {
      return { media: null, confidence: 'none', reason: `key ${key} matches ${hits.length} captures` };
    }
  }

  // Tier 2 — the key appears somewhere inside the URL (older CDN paths, proxied links).
  for (const key of card.keys) {
    const hits = media.filter((m) => [m.poster, m.url, String(m.vid || '')]
      .some((v) => v && String(v).includes(key)));
    if (hits.length === 1) return { media: hits[0], confidence: 'substring', reason: `key inside url` };
    if (hits.length > 1) return { media: null, confidence: 'none', reason: 'substring is ambiguous' };
  }

  // Tier 3 — position, but ONLY when the counts agree. 3 cards and 3 captures in the same
  // order is a reasonable guess; 3 cards and 7 captures is not.
  if (cardCount === media.length && card.index >= 0 && card.keys.length === 0) {
    return { media: media[card.index], confidence: 'positional', reason: 'same count, same order' };
  }

  return { media: null, confidence: 'none', reason: 'no key, counts differ — ask the user' };
}

// ---------------------------------------------------------------- tests
import assert from 'node:assert/strict';

const A = { url: 'https://v16.example.com/tos-cn-x0/aaa111/?sig=1', poster: 'https://p.example.com/tos-cn-x0/aaa111~tplv.jpg', vid: 'v1' };
const B = { url: 'https://v16.example.com/tos-cn-x0/bbb222/?sig=9', poster: 'https://p.example.com/tos-cn-x0/bbb222~tplv.jpg', vid: 'v2' };
const C = { url: 'https://v16.example.com/tos-cn-x0/ccc333/?sig=4', poster: '', vid: 'v3' };

// 1. exact key wins even when capture order is scrambled
assert.equal(pickMedia({ keys: ['bbb222'], index: 0 }, [A, B, C], 3).media, B);

// 2. substring tier still resolves, with lower confidence
assert.equal(pickMedia({ keys: ['ccc333'], index: 2 }, [A, C], 3).confidence, 'substring');

// 3. positional only when the counts agree
const pos = pickMedia({ keys: [], index: 1 }, [A, B], 2);
assert.equal(pos.confidence, 'positional');
assert.equal(pos.media, B);

// 4. unequal counts must NOT guess
assert.deepEqual(pickMedia({ keys: [], index: 1 }, [A, B, C], 1), {
  media: null, confidence: 'none', reason: 'no key, counts differ — ask the user',
});

// 5. two captures sharing one key is ambiguous, not a hit
const dup = { ...C, url: 'https://v16.example.com/tos-cn-x0/ccc333/?sig=99' };
assert.equal(pickMedia({ keys: ['ccc333'], index: 0 }, [C, dup], 1).media, null);

// 6. nothing captured
assert.equal(pickMedia({ keys: ['aaa111'], index: 0 }, [], 0).media, null);

// 7. assetKey survives a signed URL being re-issued
assert.equal(assetKey(A.url), assetKey(A.url.replace('sig=1', 'sig=777')));

console.log('7/7 matcher assertions passed');
