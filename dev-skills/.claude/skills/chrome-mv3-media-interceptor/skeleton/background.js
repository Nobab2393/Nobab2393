// background.js — service worker. Store, dedupe, download, count completions.

const MEDIA_KEY = 'MediaCapture';
const CONFIG_KEY = 'MediaConfig';
const MAX_ITEMS = 100;

let videos = [];
let downloading = new Map();        // downloadId -> { media, filename }
let saveTimer = null;

let config = {
  autoDownload: false,
  subfolder: 'MediaSaves',
  notifications: true,
  totalSaved: 0,
};

// Settings load once; every writer awaits it (a fast message must not persist defaults).
const configReady = new Promise((resolve) => {
  chrome.storage.local.get(CONFIG_KEY, (res) => {
    if (res[CONFIG_KEY]) config = { ...config, ...res[CONFIG_KEY] };
    resolve();
  });
});

// A service worker is killed after ~30 s idle: memory alone loses the list.
function persist() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    chrome.storage.session.set({ [MEDIA_KEY]: videos.slice(-MAX_ITEMS) }).catch(() => {});
  }, 200);
}

chrome.storage.session.get(MEDIA_KEY).then((res) => {
  const saved = res?.[MEDIA_KEY];
  if (Array.isArray(saved) && videos.length === 0) videos = saved;
}).catch(() => {});

// ---------------------------------------------------------------- helpers
const EXT = '.mp4';

function sanitize(text) {
  return String(text || 'video')
    .replace(/[/\\?%*:|"<>#]/g, '_')
    .replace(/\s+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '')
    .slice(0, 60) || 'video';
}

function filenameFor(media) {
  const now = new Date();
  const stamp = now.toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_');
  const folder = config.subfolder ? `${config.subfolder}/` : '';
  const base = sanitize(media.prompt || 'clip').replace(new RegExp(`\\${EXT}$`, 'i'), '');
  return `${folder}${stamp}_${base}${EXT}`;      // the extension is added exactly once
}

function assetKey(url) {
  // stable CDN object key: /tos-<bucket>/<key>~tplv-...  (signature params change per request)
  try {
    const path = new URL(url).pathname;
    const m = path.match(/tos-[^/]+\/([^~/]+)/i);
    return m ? m[1] : '';
  } catch { return ''; }
}

function sameAsset(a, b) {
  const ka = assetKey(a.url) || a.vid;
  const kb = assetKey(b.url) || b.vid;
  return !!ka && !!kb && ka === kb;
}

function upsert(media) {
  const i = videos.findIndex((v) => sameAsset(v, media) || (media.vid && v.vid === media.vid));
  if (i >= 0) videos[i] = { ...videos[i], ...media };
  else {
    videos.push(media);
    if (videos.length > MAX_ITEMS) videos.shift();
  }
  persist();
}

// ---------------------------------------------------------------- downloads
async function download(media, isAuto = false) {
  await configReady;
  if (!media?.url) return { ok: false, error: 'No URL' };
  if (isAuto && downloading.size > 0) return { ok: false, error: 'Busy' };

  try {
    const downloadId = await chrome.downloads.download({
      url: media.url,
      filename: filenameFor(media),
      saveAs: false,
      conflictAction: 'uniquify',
    });
    downloading.set(downloadId, { media, filename: filenameFor(media) });
    return { ok: true, downloadId };              // Started, not finished — see onChanged
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

// Count completions, not starts.
chrome.downloads.onChanged.addListener(async (delta) => {
  if (!delta.state) return;
  const entry = downloading.get(delta.id);
  if (!entry) return;
  downloading.delete(delta.id);

  if (delta.state.current === 'complete') {
    await configReady;
    config.totalSaved = (config.totalSaved || 0) + 1;
    chrome.storage.local.set({ [CONFIG_KEY]: config });
    chrome.action.setBadgeText({ text: String(config.totalSaved) });
    chrome.action.setBadgeBackgroundColor({ color: '#D97757' });
    if (config.notifications) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon128.png',
        title: 'Saved',
        message: entry.filename.split('/').pop(),
      }).catch?.(() => {});
    }
  } else if (delta.state.current === 'interrupted') {
    videos = videos.filter((v) => v.url !== entry.media.url);
    persist();
  }
});

// ---------------------------------------------------------------- messages
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'NEW_MEDIA_DETECTED') {
    if (message.media?.url) {
      upsert({ ...message.media, timestamp: Date.now() });
      if (config.autoDownload) download(message.media, true);
    }
    sendResponse({ ok: true });
    return;
  }

  if (message.type === 'TRIGGER_DOWNLOAD') {
    download(message.media).then(sendResponse);
    return true;                                   // async response
  }

  if (message.type === 'GET_CAPTURED_VIDEOS') {
    sendResponse({ videos, config });
    return;
  }

  if (message.type === 'UPDATE_CONFIG') {
    configReady.then(() => {
      config = { ...config, ...message.config };
      chrome.storage.local.set({ [CONFIG_KEY]: config });
      sendResponse({ ok: true, config });
    });
    return true;
  }
});
