#!/usr/bin/env python3
import sys

FILE = "/data/data/com.termux/files/home/mz-admin/index.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

if "shortEpisodeModal" in content:
    print("⚠️  Already patched — skipping.")
    sys.exit(0)

# ── 1. Clone the episode modal HTML, right after the original's closing </div> ──
MODAL_END_ANCHOR = '''      <button class="btn btn-gold btn-full" id="epPartUploadBtn" onclick="uploadAndAddEpisodePart()" style="display:none;">⬆️ Upload & Add Part</button>
    </div>
  </div>'''

NEW_MODAL = MODAL_END_ANCHOR + '''

<div class="modal-overlay" id="shortEpisodeModal" style="display:none;">
  <div class="modal" style="max-width:420px;width:92%;">
    <div style="display:flex;gap:0.5rem;margin-bottom:1rem;">
      <button class="btn" id="shortEpModeNew" onclick="setShortEpMode('new')" style="flex:1;font-size:0.75rem;background:var(--gold);color:#000;">➕ New Episode</button>
      <button class="btn" id="shortEpModePart" onclick="setShortEpMode('part')" style="flex:1;font-size:0.75rem;">🎬 Add Part to Episode</button>
    </div>
    <p style="font-size:0.82rem;color:var(--gray);margin-bottom:1rem;" id="shortEpisodeSeriesTitle"></p>
    <input type="hidden" id="shortEpisodeSeriesId"/>
    <label>Season <span style="color:var(--gray);font-size:0.75rem;">(optional)</span></label>
    <input type="number" id="shortEpisodeSeason" value="1" min="1" placeholder="1 (default)"/>
    <label>Episode Number</label>
    <input type="number" id="shortEpisodeNum" placeholder="e.g. 1" min="1"/>
    <label>Episode Title (optional)</label>
    <input type="text" id="shortEpisodeTitle" placeholder="e.g. Part 1"/>
    <label>File Path (save as)</label>
    <input type="text" id="shortEpisodeFileName" placeholder="shorts/123/s1e1_title.mp4"/>
    <label>Video File</label>
    <div style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.5rem;">
      <button class="btn btn-outline btn-sm" onclick="document.getElementById('shortEpisodeFileInput').click()">Browse</button>
      <span id="shortEpSelFileName" style="font-size:0.8rem;color:var(--gray);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"></span>
    </div>
    <input type="file" id="shortEpisodeFileInput" accept="video/*" style="display:none;"/>
    <div class="progress-wrap" id="shortEpProgressWrap" style="display:none;">
      <div class="progress-track"><div class="progress-fill" id="shortEpProgressFill"></div></div>
      <div class="progress-label" id="shortEpProgressLabel">0%</div>
    </div>
    <div id="shortEpQueueList" style="margin-bottom:0.5rem;"></div>
    <div class="status" id="shortEpisodeAddStatus" style="display:none;"></div>
    <div id="shortEpPartSection" style="display:none;">
      <label>Episode Key (e.g. s1e2)</label>
      <input type="text" id="shortEpPartKey" placeholder="s1e1, s1e2..." style="margin-bottom:0.5rem;"/>
      <label>Part Label (optional)</label>
      <input type="text" id="shortEpPartLabel" placeholder="Part 2, Part 3..." style="margin-bottom:0.5rem;"/>
      <label>Video File</label>
      <div style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.5rem;">
        <button class="btn btn-outline btn-sm" onclick="document.getElementById('shortEpPartFileInput').click()">Browse</button>
        <span id="shortEpPartSelFileName" style="font-size:0.8rem;color:var(--gray);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"></span>
      </div>
      <input type="file" id="shortEpPartFileInput" accept="video/*" style="display:none;" onchange="document.getElementById('shortEpPartSelFileName').textContent=this.files[0]?.name||''"/>
      <div class="progress-wrap" id="shortEpPartProgressWrap" style="display:none;">
        <div class="progress-track"><div class="progress-fill" id="shortEpPartProgressFill"></div></div>
        <div class="progress-label" id="shortEpPartProgressLabel">0%</div>
      </div>
      <div class="status" id="shortEpPartStatus" style="display:none;"></div>
    </div>
    <div class="modal-actions">
      <button class="btn btn-outline btn-full" onclick="closeShortEpisodeModal()">Cancel</button>
      <button class="btn btn-gold btn-full" id="shortEpisodeUploadBtn" onclick="queueShortEpisodeUpload()">⬆️ Upload & Add Episode</button>
      <button class="btn btn-gold btn-full" id="shortEpPartUploadBtn" onclick="uploadAndAddShortEpisodePart()" style="display:none;">⬆️ Upload & Add Part</button>
    </div>
  </div>
</div>'''

count = content.count(MODAL_END_ANCHOR)
if count != 1:
    print(f"❌ Modal anchor found {count} times — aborting, no changes made.")
    sys.exit(1)
content = content.replace(MODAL_END_ANCHOR, NEW_MODAL, 1)

# ── 2. Add JS functions right before closeEpisodeModal() ──
JS_ANCHOR = "function closeEpisodeModal() {"

NEW_JS = '''function openAddShortEpisode(shortTmdbId, shortTitle) {
  document.getElementById('shortEpisodeSeriesId').value = shortTmdbId;
  document.getElementById('shortEpisodeSeriesTitle').textContent = shortTitle;
  document.getElementById('shortEpisodeModal').style.display = 'flex';
  setShortEpMode('new');
}
function closeShortEpisodeModal() {
  if (_shortEpXHR) { try { _shortEpXHR.abort(); } catch(e){} _shortEpXHR = null; }
  document.getElementById('shortEpisodeModal').style.display = 'none';
  document.getElementById('shortEpisodeFileInput').value = '';
  document.getElementById('shortEpisodeFileName').value = '';
  document.getElementById('shortEpSelFileName').textContent = '';
  document.getElementById('shortEpisodeNum').value = '';
  document.getElementById('shortEpisodeSeason').value = '1';
  document.getElementById('shortEpisodeTitle').value = '';
  document.getElementById('shortEpisodeAddStatus').style.display = 'none';
  document.getElementById('shortEpProgressWrap').style.display = 'none';
  document.getElementById('shortEpProgressFill').style.width = '0%';
  document.getElementById('shortEpQueueList').innerHTML = '';
}
function setShortEpMode(mode) {
  const isNew = mode === 'new';
  document.getElementById('shortEpModeNew').style.background = isNew ? 'var(--gold)' : '';
  document.getElementById('shortEpModeNew').style.color = isNew ? '#000' : '';
  document.getElementById('shortEpModePart').style.background = !isNew ? 'var(--gold)' : '';
  document.getElementById('shortEpModePart').style.color = !isNew ? '#000' : '';
  document.getElementById('shortEpPartSection').style.display = isNew ? 'none' : 'block';
  document.getElementById('shortEpisodeUploadBtn').style.display = isNew ? 'block' : 'none';
  document.getElementById('shortEpPartUploadBtn').style.display = isNew ? 'none' : 'block';
}

let _shortEpXHR = null;
let _shortEpPendingQueue = [];
let _shortEpActiveCount = 0;
const _shortEpMaxConcurrent = 2;

function _shortEpMakeRow(label) {
  const list = document.getElementById('shortEpQueueList');
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

function queueShortEpisodeUpload() {
  const shortTmdbId = document.getElementById('shortEpisodeSeriesId').value;
  const season = parseInt(document.getElementById('shortEpisodeSeason').value) || 1;
  const epNum  = parseInt(document.getElementById('shortEpisodeNum').value);
  const epTitle = document.getElementById('shortEpisodeTitle').value.trim();
  const fileName = document.getElementById('shortEpisodeFileName').value.trim();
  const fileInput = document.getElementById('shortEpisodeFileInput');

  if (!epNum) return toast('Enter episode number', 'error');
  if (!fileName) return toast('Enter a file path', 'error');
  if (!fileInput.files[0]) return toast('Select a video file', 'error');

  const file = fileInput.files[0];
  const label = `S${season}E${epNum}${epTitle ? ' — ' + epTitle : ''}`;
  const ui = _shortEpMakeRow(label);

  _shortEpPendingQueue.push({ shortTmdbId, season, epNum, epTitle, fileName, file, ui });

  document.getElementById('shortEpisodeNum').value = '';
  document.getElementById('shortEpisodeTitle').value = '';
  document.getElementById('shortEpisodeFileName').value = '';
  document.getElementById('shortEpSelFileName').textContent = '';
  fileInput.value = '';

  toast(`Queued ${label}`, 'info');
  _shortEpProcessQueue();
}

function _shortEpProcessQueue() {
  while (_shortEpActiveCount < _shortEpMaxConcurrent && _shortEpPendingQueue.length > 0) {
    const item = _shortEpPendingQueue.shift();
    _shortEpActiveCount++;
    _shortEpUploadItem(item).finally(() => {
      _shortEpActiveCount--;
      _shortEpProcessQueue();
    });
  }
}

async function _shortEpUploadItem({ shortTmdbId, season, epNum, epTitle, fileName, file, ui }) {
  const setStatus = (text, color) => { ui.statusEl.textContent = text; if (color) ui.statusEl.style.color = color; };
  const totalMB = (file.size / 1024 / 1024).toFixed(1);
  const setPct = (loaded) => {
    const pct = Math.round(loaded / file.size * 100);
    ui.fillEl.style.width = pct + '%';
    const loadedMB = (loaded / 1024 / 1024).toFixed(1);
    ui.pctEl.textContent = `${pct}% — ${loadedMB} MB / ${totalMB} MB`;
  };
  try {
    setStatus('Uploading...', 'var(--gold)');
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
      xhr.upload.onprogress = e => { if (e.lengthComputable) setPct(e.loaded); };
      xhr.onload = () => xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(`Upload failed (${xhr.status}): ${xhr.responseText || 'no response body'}`));
      xhr.onerror = () => reject(new Error('Network error during upload'));
      xhr.send(file);
    });
    setPct(file.size);
    setStatus('Saving to catalog...', 'var(--gold)');
    const res = await fetch(`${ADMIN_API}/add-short-episode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Session-Token': sessionToken },
      body: JSON.stringify({ shortTmdbId, season, episode: epNum, title: epTitle, fileName }),
    });
    const data = await res.json();
    if (data.success) {
      setStatus('✅ Added', '#4ade80');
      toast(`S${season}E${epNum} added!`, 'success');
      loadShorts();
    } else throw new Error(data.error);
  } catch(e) {
    setStatus('❌ ' + e.message, '#f87171');
  }
}

let _shortEpPartXHR = null;

async function uploadAndAddShortEpisodePart() {
  const shortKey = document.getElementById('shortEpisodeSeriesId').value;
  const epKey = document.getElementById('shortEpPartKey').value.trim();
  const label = document.getElementById('shortEpPartLabel').value.trim();
  const file = document.getElementById('shortEpPartFileInput').files[0];
  if (!epKey) return showStatus('shortEpPartStatus', '❌ Episode key required (e.g. s1e1)', 'error');
  if (!file) return showStatus('shortEpPartStatus', '❌ Select a video file', 'error');
  const btn = document.getElementById('shortEpPartUploadBtn');
  btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Uploading...';
  showStatus('shortEpPartStatus', '⬆️ Uploading...', 'info');
  try {
    const slug = file.name.replace(/\\.[^.]+$/, '').replace(/[^a-z0-9]+/gi, '_').toLowerCase();
    const fileName = `shorts/${shortKey}/parts/${epKey}_${slug}_part.mp4`;
    const urlRes = await fetch(`${ADMIN_API}/upload-url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Session-Token': sessionToken },
      body: JSON.stringify({ fileName }),
    });
    const { uploadUrl, authToken } = await urlRes.json();
    await new Promise((resolve, reject) => {
      _shortEpPartXHR = new XMLHttpRequest();
      _shortEpPartXHR.open('POST', uploadUrl);
      _shortEpPartXHR.setRequestHeader('Authorization', authToken);
      _shortEpPartXHR.setRequestHeader('X-Bz-File-Name', encodeURIComponent(fileName));
      _shortEpPartXHR.setRequestHeader('Content-Type', 'video/mp4');
      _shortEpPartXHR.setRequestHeader('X-Bz-Content-Sha1', 'do_not_verify');
      _shortEpPartXHR.upload.onprogress = e => {
        if (e.lengthComputable) {
          const pct = Math.round(e.loaded/e.total*100);
          document.getElementById('shortEpPartProgressWrap').style.display = 'block';
          document.getElementById('shortEpPartProgressFill').style.width = pct+'%';
          document.getElementById('shortEpPartProgressLabel').textContent = pct+'%';
        }
      };
      _shortEpPartXHR.onload = () => _shortEpPartXHR.status < 400 ? resolve() : reject(new Error('Upload failed'));
      _shortEpPartXHR.onerror = () => reject(new Error('Upload error'));
      _shortEpPartXHR.send(file);
    });
    const res = await fetch(`${ADMIN_API}/add-short-episode-part`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Session-Token': sessionToken },
      body: JSON.stringify({ shortKey, epKey, fileName, label }),
    });
    const data = await res.json();
    if (data.success) {
      showStatus('shortEpPartStatus', `✅ Part added! (${data.totalParts} parts total)`, 'success');
      btn.innerHTML = '✅ Added!';
      loadShorts();
    } else throw new Error(data.error);
  } catch(e) {
    showStatus('shortEpPartStatus', '❌ '+e.message, 'error');
    btn.disabled = false; btn.innerHTML = '⬆️ Upload & Add Part';
  }
}

function closeEpisodeModal() {'''

count = content.count(JS_ANCHOR)
if count != 1:
    print(f"❌ JS anchor found {count} times — aborting, no changes made.")
    sys.exit(1)
content = content.replace(JS_ANCHOR, NEW_JS, 1)

# ── 3. Add "Add Episode" button to series-type rows in loadShorts() ──
OLD_ROW = '''          <div style="font-size:0.75rem;color:var(--gray);">${s.contentType==='series'?'📺 Series':'🎬 Feature'} · ${s.vj||''}</div>
        </div>
      </div>`;'''
NEW_ROW = '''          <div style="font-size:0.75rem;color:var(--gray);">${s.contentType==='series'?'📺 Series':'🎬 Feature'} · ${s.vj||''}</div>
        </div>
        ${s.contentType==='series' ? `<button class="btn btn-outline btn-sm" onclick="openAddShortEpisode('${s.tmdbId}','${esc(s.title||'')}')">➕ Episode</button>` : ''}
      </div>`;'''

count = content.count(OLD_ROW)
if count != 1:
    print(f"⚠️  loadShorts() row anchor found {count} times — skipping button wiring, rest still applied.")
else:
    content = content.replace(OLD_ROW, NEW_ROW, 1)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Patched — shortEpisodeModal, all JS functions, and Add Episode button wired in.")
