#!/usr/bin/env python3
import sys

FILE = "/data/data/com.termux/files/home/mz-admin/index.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

OLD_FN = '''async function _shortUploadItem({ body, file, ui }) {
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

NEW_FN = '''async function _shortUploadItem({ body, file, ui }) {
  const setStatus = (text, color) => { ui.statusEl.textContent = text; if (color) ui.statusEl.style.color = color; };
  const MAX_ATTEMPTS = 8;

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    try {
      if (file) {
        await _shortUploadFile(file, body, ui, setStatus);
      }
      setStatus('Saving...', 'var(--gold)');
      const res = await fetch(`${ADMIN_API}/add-short`, { method:'POST', headers:{'Content-Type':'application/json','X-Session-Token':sessionToken}, body:JSON.stringify(body) });
      const data = await res.json();
      if (data.success) {
        setStatus('✅ Added', '#4ade80');
        toast(`"${body.title}" added to Picha+`, 'success');
        return;
      } else throw new Error(data.error);
    } catch(e) {
      if (attempt === MAX_ATTEMPTS) {
        setStatus('❌ ' + e.message + ` (failed after ${MAX_ATTEMPTS} attempts)`, '#f87171');
        return;
      }
      setStatus(`⚠️ Retry ${attempt}/${MAX_ATTEMPTS - 1}: ${e.message}`, '#fbbf24');
      await new Promise(r => setTimeout(r, 2000 * attempt));
    }
  }
}

async function _shortUploadFile(file, body, ui, setStatus) {
  const totalMB = (file.size / 1024 / 1024).toFixed(1);
  let partLabel = '';
  const setPct = (loaded) => {
    const pct = Math.round(loaded / file.size * 100);
    ui.fillEl.style.width = pct + '%';
    const loadedMB = (loaded / 1024 / 1024).toFixed(1);
    ui.pctEl.textContent = `${pct}% — ${loadedMB} MB / ${totalMB} MB${partLabel}`;
  };
  setStatus('Uploading...', 'var(--gold)');
  const CHUNK_SIZE = 20 * 1024 * 1024;
  const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
  const fileName = 'shorts/' + Date.now() + '_' + file.name.replace(/[^a-zA-Z0-9._-]/g, '_');

  if (file.size <= CHUNK_SIZE) {
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
      xhr.onerror = () => reject(new Error(`Network error during upload (status=${xhr.status})`));
      xhr.send(file);
    });
  } else {
    const startRes = await fetch(`${ADMIN_API}/b2-start-large-file`, {
      method: 'POST',
      headers: { 'X-Session-Token': sessionToken, 'Content-Type': 'application/json' },
      body: JSON.stringify({ fileName })
    });
    const startData = await startRes.json();
    if (!startRes.ok) throw new Error(startData.error || 'Failed to start upload');
    const { fileId, authorizationToken, apiUrl } = startData;
    const partSha1Array = [];
    let uploadedBytes = 0;
    for (let i = 0; i < totalChunks; i++) {
      const partNumber = i + 1;
      partLabel = ` • Part ${partNumber}/${totalChunks}`;
      const chunk = file.slice(i * CHUNK_SIZE, Math.min((i + 1) * CHUNK_SIZE, file.size));
      let partUrl, partAuth;
      for (let a = 0; a < 8; a++) {
        try {
          const partUrlRes = await fetch(`${ADMIN_API}/b2-upload-part-url`, {
            method: 'POST',
            headers: { 'X-Session-Token': sessionToken, 'Content-Type': 'application/json' },
            body: JSON.stringify({ fileId, authorizationToken, apiUrl })
          });
          const partUrlData = await partUrlRes.json();
          partUrl = partUrlData.uploadUrl; partAuth = partUrlData.authorizationToken;
          break;
        } catch(e) { if (a === 7) throw e; await new Promise(r => setTimeout(r, 1500 * (a + 1))); }
      }
      let sha1;
      for (let a = 0; a < 8; a++) {
        try {
          sha1 = await new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', partUrl);
            xhr.setRequestHeader('Authorization', partAuth);
            xhr.setRequestHeader('X-Bz-Part-Number', partNumber);
            xhr.setRequestHeader('X-Bz-Content-Sha1', 'do_not_verify');
            xhr.upload.onprogress = e => { if (e.lengthComputable) setPct(uploadedBytes + e.loaded); };
            xhr.onload = () => {
              if (xhr.status === 200) {
                const resp = JSON.parse(xhr.responseText);
                resolve((resp.contentSha1 || '').replace('unverified:', ''));
              } else reject(new Error('Part failed: ' + xhr.status));
            };
            xhr.onerror = () => reject(new Error('Network error on part ' + partNumber));
            xhr.send(chunk);
          });
          break;
        } catch(e) { if (a === 7) throw e; await new Promise(r => setTimeout(r, 2000 * (a + 1))); }
      }
      partSha1Array.push(sha1);
      uploadedBytes += chunk.size;
      setPct(uploadedBytes);
    }
    const finishRes = await fetch(`${ADMIN_API}/b2-finish-large-file`, {
      method: 'POST',
      headers: { 'X-Session-Token': sessionToken, 'Content-Type': 'application/json' },
      body: JSON.stringify({ fileId, partSha1Array, authorizationToken, apiUrl })
    });
    const finishData = await finishRes.json();
    if (!finishRes.ok) throw new Error(finishData.error || 'Failed to finish upload');
  }
  setPct(file.size);
  body.videoUrl = `https://f003.backblazeb2.com/file/picha-plus-videos/` + fileName;
}'''

count = content.count(OLD_FN)
if count != 1:
    print(f"❌ Anchor found {count} times — aborting, no changes made.")
    sys.exit(1)
content = content.replace(OLD_FN, NEW_FN, 1)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Patched — _shortUploadItem now supports chunked large-file uploads + 8-attempt retry.")
