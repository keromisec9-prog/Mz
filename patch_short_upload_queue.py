#!/usr/bin/env python3
import sys

FILE = "/data/data/com.termux/files/home/mz-admin/index.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

changes = []

# 1. Add a queue list container right after the Add button
OLD_BTN = '''<button class="btn btn-gold btn-full btn-lg" id="addShortBtn" onclick="addShort()">⚡ Add Short Drama to Picha+</button>
        <div class="status" id="addShortStatus"></div>'''
NEW_BTN = '''<button class="btn btn-gold btn-full btn-lg" id="addShortBtn" onclick="addShort()">⚡ Add Short Drama to Picha+</button>
        <div class="status" id="addShortStatus"></div>
        <div id="shortQueueList" style="margin-top:0.5rem;"></div>'''
if OLD_BTN in content:
    content = content.replace(OLD_BTN, NEW_BTN, 1)
    changes.append("queue list container added")
else:
    print("❌ Add button anchor not found — aborting.")
    sys.exit(1)

# 2. Replace addShort() entirely with a queue-based version
OLD_START = "async function addShort() {"
END_MARKER = "\n\nasync function loadShorts() {"
start_idx = content.find(OLD_START)
end_idx = content.find(END_MARKER, start_idx)
if start_idx == -1 or end_idx == -1:
    print("❌ addShort() boundaries not found — aborting.")
    sys.exit(1)

NEW_ADDSHORT = '''function _shortMakeRow(label) {
  const list = document.getElementById('shortQueueList');
  const wrap = document.createElement('div');
  wrap.className = 'progress-wrap';
  wrap.style.display = 'block';
  wrap.style.marginBottom = '0.75rem';
  wrap.innerHTML = `
    <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:0.2rem;">
      <span>${label}</span>
      <span class="ep-row-status" style="color:var(--gray);">Queued</span>
    </div>
    <div class="progress-track"><div class="progress-fill ep-row-fill" style="width:0%;"></div></div>
    <div class="progress-label ep-row-pct">0%</div>
  `;
  list.appendChild(wrap);
  return {
    statusEl: wrap.querySelector('.ep-row-status'),
    fillEl: wrap.querySelector('.ep-row-fill'),
    pctEl: wrap.querySelector('.ep-row-pct')
  };
}

let _shortPendingQueue = [];
let _shortActiveCount = 0;
const _shortMaxConcurrent = 2;

function addShort() {
  if (!selectedShort) return toast('Select or enter a title first (Step 1)', 'error');
  const vj = document.getElementById('shortVjCustom').value.trim() || selectedShortVJ;
  const body = { ...selectedShort, vj, contentType: currentShortType };
  let file = null;

  if (currentShortType === 'series') {
    body.paywallFreeEpisodes = parseInt(document.getElementById('shortFreeEpisodes').value) || 3;
  } else {
    const fileInput = document.getElementById('shortVideoFile');
    if (!fileInput.files[0]) return toast('Select a video file', 'error');
    file = fileInput.files[0];
    body.durationSecs = parseInt(document.getElementById('shortDurationSecs').value) || 0;
    body.paywallThresholdPct = parseInt(document.getElementById('shortThresholdPct').value) || 25;
  }

  const label = body.title;
  const ui = _shortMakeRow(label);
  _shortPendingQueue.push({ body, file, ui });

  // Reset form immediately
  selectedShort = null;
  document.getElementById('shortPreview').innerHTML = '';
  document.getElementById('shortPosterGrid').innerHTML = '';
  document.getElementById('shortTmdbQuery').value = '';
  document.getElementById('shortVideoFile').value = '';
  document.getElementById('shortVideoFileName').textContent = '';
  document.getElementById('manualShortTitle').value = '';
  document.getElementById('manualShortYear').value = '';
  document.getElementById('manualShortOverview').value = '';
  document.getElementById('manualShortStatus').innerHTML = '';
  document.getElementById('shortFreeEpisodes').value = '';
  document.getElementById('shortVideoUrl') && (document.getElementById('shortVideoUrl').value = '');
  document.getElementById('shortDurationSecs').value = '';
  document.getElementById('shortThresholdPct').value = '';
  document.getElementById('shortVjCustom').value = '';

  toast(`Queued "${label}"`, 'info');
  _shortProcessQueue();
}

function _shortProcessQueue() {
  while (_shortActiveCount < _shortMaxConcurrent && _shortPendingQueue.length > 0) {
    const item = _shortPendingQueue.shift();
    _shortActiveCount++;
    _shortUploadItem(item).finally(() => {
      _shortActiveCount--;
      _shortProcessQueue();
    });
  }
}

async function _shortUploadItem({ body, file, ui }) {
  const setStatus = (text, color) => { ui.statusEl.textContent = text; if (color) ui.statusEl.style.color = color; };
  try {
    if (file) {
      setStatus('Uploading...', 'var(--gold)');
      const totalMB = (file.size / 1024 / 1024).toFixed(1);
      const setPct = (loaded) => {
        const pct = Math.round(loaded / file.size * 100);
        ui.fillEl.style.width = pct + '%';
        const loadedMB = (loaded / 1024 / 1024).toFixed(1);
        ui.pctEl.textContent = `${pct}% — ${loadedMB} MB / ${totalMB} MB`;
      };
      const fileName = 'shorts/' + Date.now() + '_' + file.name.replace(/[^a-zA-Z0-9._-]/g, '_');
      const urlRes = await fetch(`${ADMIN_API}/b2-upload-url?fileName=${encodeURIComponent(fileName)}`, {
        headers: { 'X-Session-Token': sessionToken }
      });
      const b2 = await urlRes.json();
      if (!b2.uploadUrl) throw new Error('Could not get upload URL from server');
      await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', b2.uploadUrl);
        xhr.setRequestHeader('Authorization', b2.authorizationToken);
        xhr.setRequestHeader('X-Bz-File-Name', encodeURIComponent(fileName));
        xhr.setRequestHeader('Content-Type', file.type || 'video/mp4');
        xhr.setRequestHeader('X-Bz-Content-Sha1', 'do_not_verify');
        xhr.upload.onprogress = (e) => { if (e.lengthComputable) setPct(e.loaded); };
        xhr.onload = () => xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(`Upload failed (${xhr.status}): ${xhr.responseText || 'no response body'}`));
        xhr.onerror = () => reject(new Error('Network error during upload'));
        xhr.send(file);
      });
      body.videoUrl = `https://f003.backblazeb2.com/file/picha-plus-videos/` + fileName;
    }

    setStatus('Saving...', 'var(--gold)');
    const res = await fetch(`${ADMIN_API}/add-short`, { method:'POST', headers:{'Content-Type':'application/json','X-Session-Token':sessionToken}, body:JSON.stringify(body) });
    const data = await res.json();
    if (data.success) {
      setStatus('✅ Added', '#4ade80');
      toast(`"${body.title}" added to Picha+`, 'success');
    } else throw new Error(data.error);
  } catch(e) {
    setStatus('❌ ' + e.message, '#f87171');
  }
}'''

content = content[:start_idx] + NEW_ADDSHORT + content[end_idx:]
changes.append("addShort() converted to concurrent queue pattern")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Applied:", ", ".join(changes))
