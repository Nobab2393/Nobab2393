// popup.js — list, save one, save all. Everything that came off a page is escaped.
const $ = (id) => document.getElementById(id);

const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ESC[c]);
const safeHttp = (u) => {
  try {
    const p = new URL(String(u));
    return (p.protocol === 'http:' || p.protocol === 'https:') ? p.href : '';
  } catch { return ''; }
};

let videos = [];

function row(video, index) {
  const li = document.createElement('li');
  const poster = safeHttp(video.poster);
  const title = String(video.prompt || `Clip ${index + 1}`).slice(0, 90);
  const res = video.width && video.height ? `${video.width}×${video.height}` : 'unknown res';

  const thumb = poster
    ? `<img src="${esc(poster)}" alt="">`
    : `<div class="ph"></div>`;

  li.innerHTML = `
    ${thumb}
    <div class="meta">
      <div class="title" title="${esc(title)}">${esc(title)}</div>
      <div class="sub">${esc(res)}</div>
    </div>
    <button class="save">Save</button>
  `;

  const img = li.querySelector('img');
  if (img) {
    img.addEventListener('error', () => {
      const ph = document.createElement('div');
      ph.className = 'ph';
      img.replaceWith(ph);
    }, { once: true });
  }

  const btn = li.querySelector('.save');
  btn.addEventListener('click', () => {
    btn.disabled = true;
    btn.textContent = '…';
    chrome.runtime.sendMessage({ type: 'TRIGGER_DOWNLOAD', media: video }, (res) => {
      btn.textContent = res?.ok ? 'Started' : 'Failed';
      setTimeout(() => { btn.textContent = 'Save'; btn.disabled = false; }, 2200);
    });
  });

  return li;
}

function render() {
  const list = $('list');
  list.textContent = '';
  $('count').textContent = `${videos.length} clip${videos.length === 1 ? '' : 's'}`;

  if (!videos.length) {
    const empty = document.createElement('li');
    empty.className = 'empty';
    empty.textContent = 'Open the app and play a clip — it will show up here.';
    list.appendChild(empty);
    $('all').hidden = true;
    return;
  }

  videos.forEach((v, i) => list.appendChild(row(v, i)));
  $('all').hidden = false;
}

$('all').addEventListener('click', async () => {
  const btn = $('all');
  btn.disabled = true;
  for (const v of videos) {                      // sequential: bursts get throttled
    await new Promise((r) => chrome.runtime.sendMessage({ type: 'TRIGGER_DOWNLOAD', media: v }, () => r()));
    await new Promise((r) => setTimeout(r, 400));
  }
  btn.disabled = false;
});

// optional host permission, requested from a real user gesture
chrome.permissions.contains({ origins: ['https://*/*'] }, (granted) => {
  $('perm').hidden = granted;
});
$('grant').addEventListener('click', () => {
  chrome.permissions.request({ origins: ['https://*/*'] }, (granted) => {
    if (granted) $('perm').hidden = true;
  });
});

// ask the page for DOM order first, then fall back to the worker
function load() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tab = tabs && tabs[0];
    if (!tab?.id) return fromWorker();
    chrome.tabs.sendMessage(tab.id, { type: 'GET_PAGE_ORDERED_VIDEOS' }, (res) => {
      if (chrome.runtime.lastError || !res?.videos?.length) return fromWorker();
      videos = res.videos;
      render();
    });
  });
}

function fromWorker() {
  chrome.runtime.sendMessage({ type: 'GET_CAPTURED_VIDEOS' }, (res) => {
    videos = res?.videos || [];
    render();
  });
}

load();
