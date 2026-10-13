#!/usr/bin/env python3
import sys

FILE = "index.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

changes_made = []

# ── 1. Replace the videoUrl text field with a real file picker ───────
OLD_VIDEO_FIELD = '''          <label>Video URL / filename</label>
          <input type="text" id="shortVideoUrl" class="input" placeholder="Video file URL" style="margin-bottom:0.5rem;"/>
          <label>Duration (seconds)</label>'''
NEW_VIDEO_FIELD = '''          <label>Video File</label>
          <input type="file" id="shortVideoFile" accept="video/*" style="display:none;" onchange="document.getElementById('shortVideoFileName').textContent=this.files[0]?.name||''"/>
          <button class="btn" onclick="document.getElementById('shortVideoFile').click()" style="width:100%;margin-bottom:0.3rem;">📁 Choose Video</button>
          <div id="shortVideoFileName" style="font-size:0.72rem;color:#888;margin-bottom:0.5rem;"></div>
          <label>Duration (seconds)</label>'''

if OLD_VIDEO_FIELD in content:
    content = content.replace(OLD_VIDEO_FIELD, NEW_VIDEO_FIELD, 1)
    changes_made.append("video field → file picker")
else:
    print("❌ Video field anchor not found — aborting, no changes made.")
    sys.exit(1)

# ── 2. Make poster optional: strip poster-required checks for shorts ──
# (searchShortTMDB/selectShortResult/confirmManualShort never enforced
#  a poster requirement themselves — only addShort() might reference it
#  indirectly via selectedShort. Ensure addShort() doesn't require poster.)
# No explicit poster-required check exists yet in addShort(), so this is
# a no-op safety pass — just confirm poster is treated as optional string.
if "if (!selectedShort.poster)" in content:
    content = content.replace("if (!selectedShort.poster) return toast('A poster is required", "if (false) return toast('A poster is required", 1)
    changes_made.append("removed poster-required check")

# ── 3. loadShorts(): render placeholder instead of broken <img> when no poster ──
OLD_LIST_ROW = '''        <img src="${s.poster||''}" style="width:50px;height:70px;object-fit:cover;border-radius:4px;"/>'''
NEW_LIST_ROW = '''        ${s.poster ? `<img src="${s.poster}" style="width:50px;height:70px;object-fit:cover;border-radius:4px;"/>` : `<div style="width:50px;height:70px;border-radius:4px;background:#222;display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">🎬</div>`}'''

if OLD_LIST_ROW in content:
    content = content.replace(OLD_LIST_ROW, NEW_LIST_ROW, 1)
    changes_made.append("loadShorts() poster placeholder")
else:
    print("⚠️  loadShorts() poster row pattern not found — skipping that part.")

# ── 4. Rewrite addShort() to upload the video file via B2 before saving ──
OLD_ADDSHORT_START = "async function addShort() {\n  if (!selectedShort) return toast('Select or enter a title first (Step 1)', 'error');"
if OLD_ADDSHORT_START not in content:
    print("❌ addShort() start anchor not found — aborting, no changes made.")
    sys.exit(1)

start_idx = content.find(OLD_ADDSHORT_START)
# Find the matching end of addShort() — its closing brace is right before
# the blank line + "async function loadShorts()"
end_marker = "\n\nasync function loadShorts() {"
end_idx = content.find(end_marker, start_idx)
if end_idx == -1:
    print("❌ addShort() end anchor not found — aborting, no changes made.")
    sys.exit(1)

NEW_ADDSHORT = '''async function addShort() {
  if (!selectedShort) return toast('Select or enter a title first (Step 1)', 'error');
  const vj = document.getElementById('shortVjCustom').value.trim() || selectedShortVJ;
  const btn = document.getElementById('addShortBtn');
  const body = { ...selectedShort, vj, contentType: currentShortType };

  if (currentShortType === 'series') {
    body.paywallFreeEpisodes = parseInt(document.getElementById('shortFreeEpisodes').value) || 3;
  } else {
    const fileInput = document.getElementById('shortVideoFile');
    if (!fileInput.files[0]) return toast('Select a video file', 'error');
    const file = fileInput.files[0];
    const fileName = 'shorts/' + Date.now() + '_' + file.name.replace(/[^a-zA-Z0-9._-]/g, '_');

    btn.disabled = true; btn.innerHTML = '⏳ Uploading video...';
    try {
      const urlRes = await fetch(`${ADMIN_API}/b2-upload-url?fileName=${encodeURIComponent(fileName)}`, {
        headers: { 'X-Session-Token': sessionToken }
      });
      const b2 = await urlRes.json();
      if (!b2.uploadUrl) throw new Error('Could not get upload URL from server');
      await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('PUT', b2.uploadUrl);
        if (b2.headers) Object.entries(b2.headers).forEach(([k,v]) => xhr.setRequestHeader(k, v));
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            const pct = Math.round(e.loaded / e.total * 100);
            showStatus('addShortStatus', `⏳ Uploading video... ${pct}%`, 'info');
          }
        };
        xhr.onload = () => xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(`Upload failed (${xhr.status})`));
        xhr.onerror = () => reject(new Error('Network error during upload'));
        xhr.send(file);
      });
      body.videoUrl = `https://f003.backblazeb2.com/file/picha-plus-videos/` + fileName;
    } catch(e) {
      showStatus('addShortStatus', '❌ Upload failed: ' + e.message, 'error');
      btn.disabled = false; btn.innerHTML = '⚡ Add Short Drama to Picha+';
      return;
    }
    body.durationSecs = parseInt(document.getElementById('shortDurationSecs').value) || 0;
    body.paywallThresholdPct = parseInt(document.getElementById('shortThresholdPct').value) || 25;
  }

  btn.disabled = true; btn.innerHTML = '⏳ Saving...';
  try {
    const res = await fetch(`${ADMIN_API}/add-short`, { method:'POST', headers:{'Content-Type':'application/json','X-Session-Token':sessionToken}, body:JSON.stringify(body) });
    const data = await res.json();
    if (data.success) {
      showStatus('addShortStatus', `✅ "${selectedShort.title}" added!`, 'success');
      toast(`"${selectedShort.title}" added to Picha+`, 'success');
      selectedShort = null;
      document.getElementById('shortPreview').innerHTML = '';
      document.getElementById('shortPosterGrid').innerHTML = '';
      document.getElementById('shortTmdbQuery').value = '';
      document.getElementById('shortVideoFile').value = '';
      document.getElementById('shortVideoFileName').textContent = '';
    } else throw new Error(data.error);
  } catch(e) { showStatus('addShortStatus', '❌ '+e.message, 'error'); }
  btn.disabled = false; btn.innerHTML = '⚡ Add Short Drama to Picha+';
}'''

content = content[:start_idx] + NEW_ADDSHORT + content[end_idx:]
changes_made.append("addShort() rewritten with real B2 upload flow")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Applied:", ", ".join(changes_made))
