// content.js — ISOLATED world. Bridges the page hook to the extension, and owns page order.
(function () {
  'use strict';

  // 1. inject the main-world hook
  const el = document.createElement('script');
  el.src = chrome.runtime.getURL('interceptor.js');
  el.onload = () => el.remove();
  (document.head || document.documentElement).appendChild(el);

  const ALLOWED_HOSTS = [/\.example\.com$/, /\.examplecdn\.com$/];

  function allowedUrl(value) {
    try {
      const u = new URL(String(value));
      if (u.protocol !== 'https:') return '';
      return ALLOWED_HOSTS.some((re) => re.test(u.hostname)) ? u.href : '';
    } catch { return ''; }
  }

  // 2. only accept media the page hook actually produced
  window.addEventListener('message', (event) => {
    if (event.source !== window) return;              // an iframe must not drive the worker
    const data = event.data;
    if (!data || data.type !== 'APP_NEW_MEDIA' || !data.media) return;

    const url = allowedUrl(data.media.url);
    if (!url) return;

    const media = {
      url,
      vid: String(data.media.vid || '').slice(0, 120),
      poster: allowedUrl(data.media.poster),
      prompt: String(data.media.prompt || '').slice(0, 300),
      width: Number(data.media.width) || 0,
      height: Number(data.media.height) || 0,
      timestamp: Date.now(),
    };
    chrome.runtime.sendMessage({ type: 'NEW_MEDIA_DETECTED', media });
  });

  // 3. answer the popup with DOM order — the only ordering the user recognises
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type !== 'GET_PAGE_ORDERED_VIDEOS') return;
    const cards = [...document.querySelectorAll('[data-media-card], .video-card, video')];
    const videos = cards.map((card, i) => {
      const videoEl = card.querySelector?.('video') || (card.tagName === 'VIDEO' ? card : null);
      const img = card.querySelector?.('img');
      return {
        url: videoEl ? (videoEl.currentSrc || videoEl.src) : '',
        poster: img ? (img.currentSrc || img.src) : '',
        prompt: (card.dataset?.prompt || card.getAttribute?.('aria-label') || `Scene ${i + 1}`),
        sceneIndex: i + 1,
        timestamp: 0,
      };
    }).filter((v) => v.url);
    sendResponse({ videos });
  });
})();
