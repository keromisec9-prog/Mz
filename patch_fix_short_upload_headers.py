#!/usr/bin/env python3
import sys

FILE = "/data/data/com.termux/files/home/mz-admin/index.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

OLD = """      await new Promise((resolve, reject) => {
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
      });"""

NEW = """      await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', b2.uploadUrl);
        xhr.setRequestHeader('Authorization', b2.authorizationToken);
        xhr.setRequestHeader('X-Bz-File-Name', encodeURIComponent(fileName));
        xhr.setRequestHeader('Content-Type', file.type || 'video/mp4');
        xhr.setRequestHeader('X-Bz-Content-Sha1', 'do_not_verify');
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            const pct = Math.round(e.loaded / e.total * 100);
            showStatus('addShortStatus', `⏳ Uploading video... ${pct}%`, 'info');
          }
        };
        xhr.onload = () => xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(`Upload failed (${xhr.status}): ${xhr.responseText || 'no response body'}`));
        xhr.onerror = () => reject(new Error('Network error during upload'));
        xhr.send(file);
      });"""

count = content.count(OLD)
if count != 1:
    print(f"❌ Anchor found {count} times — aborting, no changes made.")
    sys.exit(1)
content = content.replace(OLD, NEW, 1)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Patched — addShort() upload now uses correct POST + B2 headers.")
