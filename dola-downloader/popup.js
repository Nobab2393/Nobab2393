// Numan Mughal Dola Popup Script

document.addEventListener('DOMContentLoaded', () => {
  const totalDownloadedEl = document.getElementById('totalDownloaded');
  const detectedCountEl = document.getElementById('detectedCount');
  const autoDownloadToggle = document.getElementById('autoDownloadToggle');
  const notificationsToggle = document.getElementById('notificationsToggle');
  const videosList = document.getElementById('videosList');
  const downloadAllBtn = document.getElementById('downloadAllBtn');

  let currentVideos = [];

  // Anything that came off a page gets escaped before it goes back into HTML.
  const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ESC[c]);
  const safeHttp = (u) => {
    try {
      const parsed = new URL(String(u));
      return (parsed.protocol === 'http:' || parsed.protocol === 'https:') ? parsed.href : '';
    } catch { return ''; }
  };

  function loadState() {
    // 1. First ask active tab for exact on-page order
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs && tabs[0];
      if (activeTab && activeTab.id) {
        chrome.tabs.sendMessage(activeTab.id, { type: 'GET_PAGE_ORDERED_VIDEOS' }, (tabRes) => {
          if (chrome.runtime.lastError) { fetchFromBackground(); return; }
          if (tabRes && tabRes.videos && tabRes.videos.length > 0) {
            chrome.runtime.sendMessage({ type: 'GET_CAPTURED_VIDEOS' }, (bgRes) => {
              const config = bgRes ? bgRes.config : {};
              currentVideos = tabRes.videos;
              updateUI(currentVideos, config);
            });
            return;
          }
          // Fallback to background stored list
          fetchFromBackground();
        });
      } else {
        fetchFromBackground();
      }
    });
  }

  function fetchFromBackground() {
    chrome.runtime.sendMessage({ type: 'GET_CAPTURED_VIDEOS' }, (response) => {
      if (!response) return;
      const { videos, config } = response;
      currentVideos = videos || [];
      updateUI(currentVideos, config);
    });
  }

  function updateUI(videos, config) {
    totalDownloadedEl.textContent = config?.totalDownloaded || 0;
    detectedCountEl.textContent = videos.length;
    autoDownloadToggle.checked = !!config?.autoDownload;
    notificationsToggle.checked = config?.notifications !== false;
    renderVideosList(videos);
  }

  function renderVideosList(videos) {
    if (!videos || videos.length === 0) {
      videosList.innerHTML = `
        <div class="empty-state">
          <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5">
            <polygon points="23 7 16 12 23 17 23 7"></polygon>
            <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
          </svg>
          <p>Open any Dola chat with videos to download 1080P files!</p>
        </div>
      `;
      downloadAllBtn.style.display = 'none';
      return;
    }

    // Strict 1-by-1 chronological sort (Scene 1 on top, Scene 2 second, etc.)
    const sortedVideos = [...videos].sort((a, b) => {
      const aIdx = a.sceneIndex || 0;
      const bIdx = b.sceneIndex || 0;
      if (aIdx && bIdx) return aIdx - bIdx;

      const aMatch = String(a.prompt || '').match(/Scene[_\s]*(\d+)/i);
      const bMatch = String(b.prompt || '').match(/Scene[_\s]*(\d+)/i);
      if (aMatch && bMatch) {
        return parseInt(aMatch[1], 10) - parseInt(bMatch[1], 10);
      }
      return (a.timestamp || 0) - (b.timestamp || 0);
    });

    currentVideos = sortedVideos;
    downloadAllBtn.style.display = 'block';
    videosList.innerHTML = '';

    sortedVideos.forEach((video, index) => {
      const item = document.createElement('div');
      item.className = 'video-item';

      const poster = safeHttp(video.poster);
      const posterHtml = poster
        ? `<img class="video-thumb" src="${esc(poster)}" alt="Preview">`
        : `<div class="video-thumb-fallback">🎬</div>`;

      const promptTitle = String(video.prompt || `Scene ${index + 1} Video`).slice(0, 120);
      const resText = (video.width && video.height) ? `${video.width}x${video.height}` : '1080P';
      const sceneNum = video.sceneIndex || (index + 1);

      item.innerHTML = `
        <div class="video-card-left">
          ${posterHtml}
          <div class="video-info">
            <div class="video-prompt" title="${esc(promptTitle)}">
              <span class="scene-number-badge">#${esc(sceneNum)}</span>${esc(promptTitle)}
            </div>
            <div class="video-badge">🔹 1080P Without Watermark (${resText})</div>
          </div>
        </div>
        <div class="video-actions">
          <button class="preview-btn" title="Open Preview">🔍</button>
          <button class="dl-btn" data-index="${index}">Save</button>
        </div>
      `;

      // A broken poster falls back to the placeholder (inline onerror is blocked by MV3 CSP)
      const thumb = item.querySelector('.video-thumb');
      if (thumb) {
        thumb.addEventListener('error', () => {
          const ph = document.createElement('div');
          ph.className = 'video-thumb-fallback';
          ph.textContent = '🎬';
          thumb.replaceWith(ph);
        }, { once: true });
      }

      // Preview button
      item.querySelector('.preview-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        if (video.url) {
          window.open(video.url, '_blank');
        }
      });

      // Save button
      const dlBtn = item.querySelector('.dl-btn');
      dlBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dlBtn.textContent = 'Saving...';
        dlBtn.disabled = true;
        chrome.runtime.sendMessage({ type: 'TRIGGER_DOWNLOAD', media: video }, (res) => {
          if (res && res.ok) {
            dlBtn.textContent = 'Saved!';
            dlBtn.style.background = '#00e676';
            setTimeout(() => {
              dlBtn.textContent = 'Save';
              dlBtn.style.background = '';
              dlBtn.disabled = false;
            }, 2500);
            fetchFromBackground();
          } else {
            dlBtn.textContent = 'Failed';
            setTimeout(() => {
              dlBtn.textContent = 'Save';
              dlBtn.disabled = false;
            }, 2000);
          }
        });
      });

      videosList.appendChild(item);
    });
  }

  // Toggles
  autoDownloadToggle.addEventListener('change', () => {
    chrome.runtime.sendMessage({
      type: 'UPDATE_CONFIG',
      config: { autoDownload: autoDownloadToggle.checked }
    });
  });

  notificationsToggle.addEventListener('change', () => {
    chrome.runtime.sendMessage({
      type: 'UPDATE_CONFIG',
      config: { notifications: notificationsToggle.checked }
    });
  });

  // Batch download
  downloadAllBtn.addEventListener('click', async () => {
    // One at a time: a burst of 30 downloads gets throttled by Chrome.
    downloadAllBtn.disabled = true;
    for (const v of currentVideos) {
      await new Promise((resolve) => {
        chrome.runtime.sendMessage({ type: 'TRIGGER_DOWNLOAD', media: v }, () => resolve());
      });
      await new Promise((r) => setTimeout(r, 400));
    }
    downloadAllBtn.disabled = false;
    downloadAllBtn.textContent = 'All Triggered!';
    setTimeout(() => {
      downloadAllBtn.textContent = '📥 Download All';
    }, 2500);
  });

  loadState();
});