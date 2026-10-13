path = "index.html"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

original = content

old_btn = """        <div style="margin-top:1rem;display:flex;gap:0.6rem;">
          <button class="btn btn-gold" onclick="saveFirstOffer()">Save</button>
        </div>
        <div class="status" id="firstOfferStatus"></div>"""

new_btn = """        <div style="margin-top:1rem;display:flex;gap:0.6rem;">
          <button class="btn btn-gold" onclick="saveFirstOffer()">Save</button>
          <button class="btn btn-red" id="turnOffFirstOfferBtn" style="display:none;" onclick="clearFirstOffer()">Turn Off</button>
        </div>
        <div class="status" id="firstOfferStatus"></div>"""

if old_btn in content:
    content = content.replace(old_btn, new_btn)
    print("[1/3] Added Turn Off button")
else:
    print("[1/3] WARNING: button anchor not found — skipping")

old_render = """function renderFirstOfferBanner(data) {
  const banner = document.getElementById('firstOfferBanner');
  if (data.active) {
    const planNames = (data.plans || []).join(', ');
    banner.style.background = 'rgba(0,200,120,0.15)';
    banner.style.color = '#3ddc97';
    banner.textContent = `🎁 LIVE: ${data.percentOff}% off first subscription (${planNames})`;
  } else {
    banner.style.background = 'rgba(255,255,255,0.05)';
    banner.style.color = '#888';
    banner.textContent = 'First-subscription offer is currently off';
  }
}"""

new_render = """function renderFirstOfferBanner(data) {
  const banner = document.getElementById('firstOfferBanner');
  const turnOffBtn = document.getElementById('turnOffFirstOfferBtn');
  if (data.active) {
    const planNames = (data.plans || []).join(', ');
    banner.style.background = 'rgba(0,200,120,0.15)';
    banner.style.color = '#3ddc97';
    banner.textContent = `🎁 LIVE: ${data.percentOff}% off first subscription (${planNames})`;
    turnOffBtn.style.display = 'inline-block';
  } else {
    banner.style.background = 'rgba(255,255,255,0.05)';
    banner.style.color = '#888';
    banner.textContent = 'First-subscription offer is currently off';
    turnOffBtn.style.display = 'none';
  }
}"""

if old_render in content:
    content = content.replace(old_render, new_render)
    print("[2/3] Updated renderFirstOfferBanner to toggle button visibility")
else:
    print("[2/3] WARNING: renderFirstOfferBanner block not found — skipping")

old_anchor = """function renderPromoBanner(data) {"""
new_fn = """async function clearFirstOffer() {
  const statusEl = document.getElementById('firstOfferStatus');
  statusEl.textContent = 'Turning off...';
  try {
    const res = await fetch(`${ADMIN_API}/admin/clear-first-offer`, {
      method: 'POST',
      headers: { 'X-Session-Token': sessionToken }
    });
    if (res.ok) {
      statusEl.textContent = '✅ Turned off';
      document.getElementById('firstOfferActive').checked = false;
      renderFirstOfferBanner(await fetchFirstOfferStatus());
    } else {
      const err = await res.json();
      statusEl.textContent = '❌ ' + (err.error || 'Failed');
    }
  } catch (e) {
    statusEl.textContent = '❌ ' + e.message;
  }
}

function renderPromoBanner(data) {"""

if old_anchor in content:
    content = content.replace(old_anchor, new_fn, 1)
    print("[3/3] Added clearFirstOffer() function")
else:
    print("[3/3] WARNING: renderPromoBanner anchor not found — skipping")

if content != original:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("\nFile saved:", path)
else:
    print("\nNo changes made — check warnings above.")
