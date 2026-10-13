#!/usr/bin/env python3
import sys

FILE = "/data/data/com.termux/files/home/mz-admin/index.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

changes = []

# 1. confirmManualShort() — title no longer required, default if blank
OLD = """function confirmManualShort() {
  const title = document.getElementById('manualShortTitle').value.trim();
  if (!title) { showStatus('manualShortStatus', '❌ Title is required', 'error'); return; }
  selectedShort = {
    tmdbId: null, title,"""
NEW = """function confirmManualShort() {
  const title = document.getElementById('manualShortTitle').value.trim() || 'Untitled Short';
  selectedShort = {
    tmdbId: null, title,"""
if OLD in content:
    content = content.replace(OLD, NEW, 1)
    changes.append("confirmManualShort() title optional")
else:
    print("❌ confirmManualShort anchor not found — aborting.")
    sys.exit(1)

# 2. Update the success message to not always assume a real title
OLD2 = "  showStatus('manualShortStatus', `✅ \"${title}\" ready to add. Select VJ below.`, 'success');"
NEW2 = "  showStatus('manualShortStatus', `✅ Ready to add. Select VJ below.`, 'success');"
if OLD2 in content:
    content = content.replace(OLD2, NEW2, 1)
    changes.append("status message simplified")

# 3. Video file onchange — auto-detect duration via HTML5 video metadata
OLD3 = '''<input type="file" id="shortVideoFile" accept="video/*" style="display:none;" onchange="document.getElementById('shortVideoFileName').textContent=this.files[0]?.name||''"/>'''
NEW3 = '''<input type="file" id="shortVideoFile" accept="video/*" style="display:none;" onchange="handleShortVideoSelect(this)"/>'''
if OLD3 in content:
    content = content.replace(OLD3, NEW3, 1)
    changes.append("video input onchange → handleShortVideoSelect")
else:
    print("❌ video input anchor not found — aborting.")
    sys.exit(1)

# 4. Add handleShortVideoSelect() function right before addShort()
OLD4 = "async function addShort() {"
NEW4 = '''function handleShortVideoSelect(input) {
  const file = input.files[0];
  document.getElementById('shortVideoFileName').textContent = file?.name || '';
  if (!file) return;
  const tempVideo = document.createElement('video');
  tempVideo.preload = 'metadata';
  tempVideo.onloadedmetadata = () => {
    URL.revokeObjectURL(tempVideo.src);
    const secs = Math.round(tempVideo.duration) || 0;
    document.getElementById('shortDurationSecs').value = secs;
  };
  tempVideo.src = URL.createObjectURL(file);
}

async function addShort() {'''
if OLD4 in content:
    content = content.replace(OLD4, NEW4, 1)
    changes.append("handleShortVideoSelect() added (auto-detect duration)")
else:
    print("❌ addShort anchor not found — aborting.")
    sys.exit(1)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Applied:", ", ".join(changes))
