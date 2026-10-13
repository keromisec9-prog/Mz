import re

path = "index.html"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

original = content

old_nav = """    <div class="tab" id="promoTab" style="display:none;" onclick="switchTab('promo')">🏷️ Promotions</div>"""
new_nav = """    <div class="tab" id="promoTab" style="display:none;" onclick="switchTab('promo')">🏷️ Promotions</div>
    <div class="tab" id="firstOfferTab" style="display:none;" onclick="switchTab('firstoffer'); loadFirstOfferStatus();">🎁 First Offer</div>"""

if old_nav in content:
    content = content.replace(old_nav, new_nav)
    print("[1/4] Added nav tab")
else:
    print("[1/4] WARNING: nav tab anchor not found — skipping")

old_section_anchor = """    <!-- ANALYTICS -->
    <div class="tab-content" id="tab-analytics">"""

new_section = """    <!-- FIRST SUBSCRIPTION OFFER -->
    <div class="tab-content" id="tab-firstoffer">
      <div class="step">
        <div class="step-header"><div class="step-title">First Subscription Offer</div></div>
        <div style="font-size:0.82rem;color:var(--gray);margin-bottom:0.8rem;">
          A standing discount applied automatically to a user's very first subscription purchase.
          Tracked per-device and per-account so it can only be claimed once. Stays on until you turn
          it off — unlike Promotions, it has no end date. When a Promotion is live, that takes
          priority and this offer is skipped for everyone.
        </div>
        <div id="firstOfferBanner" style="padding:0.8rem;border-radius:8px;margin-bottom:1rem;font-weight:bold;text-align:center;"></div>

        <label style="display:flex;align-items:center;gap:0.5rem;">
          <input type="checkbox" id="firstOfferActive"/> Enabled
        </label>

        <label style="margin-top:0.8rem;display:block;">Percent off</label>
        <input type="number" id="firstOfferPercent" min="1" max="95" placeholder="e.g. 50"/>

        <label style="margin-top:0.8rem;display:block;">Applies to</label>
        <div style="display:flex;flex-direction:column;gap:0.3rem;margin-top:0.3rem;">
          <label style="display:flex;align-items:center;gap:0.4rem;font-weight:normal;"><input type="checkbox" class="firstOfferPlanCheck" value="daily"/> Daily</label>
          <label style="display:flex;align-items:center;gap:0.4rem;font-weight:normal;"><input type="checkbox" class="firstOfferPlanCheck" value="dailyplus"/> Daily+</label>
          <label style="display:flex;align-items:center;gap:0.4rem;font-weight:normal;"><input type="checkbox" class="firstOfferPlanCheck" value="weekly"/> Weekly</label>
          <label style="display:flex;align-items:center;gap:0.4rem;font-weight:normal;"><input type="checkbox" class="firstOfferPlanCheck" value="weeklyplus"/> Weekly+</label>
          <label style="display:flex;align-items:center;gap:0.4rem;font-weight:normal;"><input type="checkbox" class="firstOfferPlanCheck" value="monthly"/> Monthly</label>
          <label style="display:flex;align-items:center;gap:0.4rem;font-weight:normal;"><input type="checkbox" class="firstOfferPlanCheck" value="monthlyplus"/> Monthly+</label>
          <label style="display:flex;align-items:center;gap:0.4rem;font-weight:normal;"><input type="checkbox" class="firstOfferPlanCheck" value="quarterly"/> Quarterly</label>
          <label style="display:flex;align-items:center;gap:0.4rem;font-weight:normal;"><input type="checkbox" class="firstOfferPlanCheck" value="yearly"/> Yearly</label>
        </div>

        <div style="margin-top:1rem;display:flex;gap:0.6rem;">
          <button class="btn btn-gold" onclick="saveFirstOffer()">Save</button>
        </div>
        <div class="status" id="firstOfferStatus"></div>
      </div>
    </div>

    <!-- ANALYTICS -->
    <div class="tab-content" id="tab-analytics">"""

if old_section_anchor in content:
    content = content.replace(old_section_anchor, new_section)
    print("[2/4] Added tab-content section")
else:
    print("[2/4] WARNING: analytics anchor not found — skipping")

match = re.search(r"document\.getElementById\('promoTab'\)\.style\.display\s*=\s*[^;]+;", content)
if match:
    line = match.group(0)
    addition = "\n    document.getElementById('firstOfferTab').style.display" + line.split("style.display", 1)[1]
    content = content.replace(line, line + addition, 1)
    print("[3/4] Added firstOfferTab visibility toggle alongside promoTab")
else:
    print("[3/4] WARNING: promoTab visibility line not found — you'll need to manually show #firstOfferTab wherever #promoTab is shown")

old_js_anchor = """function renderPromoBanner(data) {"""
new_js = """function renderFirstOfferBanner(data) {
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
}

async function fetchFirstOfferStatus() {
  const res = await fetch(`${ADMIN_API}/admin/first-offer-status`, { headers: { 'X-Session-Token': sessionToken } });
  if (!res.ok) throw new Error('fetch failed');
  return await res.json();
}

async function loadFirstOfferStatus() {
  try {
    const data = await fetchFirstOfferStatus();
    document.getElementById('firstOfferActive').checked = !!data.active;
    document.getElementById('firstOfferPercent').value = data.percentOff || '';
    document.querySelectorAll('.firstOfferPlanCheck').forEach(cb => { cb.checked = (data.plans || []).includes(cb.value); });
    renderFirstOfferBanner(data);
  } catch (e) {
    document.getElementById('firstOfferStatus').textContent = 'Failed to load';
  }
}

async function saveFirstOffer() {
  const statusEl = document.getElementById('firstOfferStatus');
  const active = document.getElementById('firstOfferActive').checked;
  const percentOff = Number(document.getElementById('firstOfferPercent').value);
  const plans = Array.from(document.querySelectorAll('.firstOfferPlanCheck:checked')).map(cb => cb.value);
  if (!percentOff || percentOff <= 0 || percentOff > 95) { statusEl.textContent = '❌ Enter a percent off between 1 and 95'; return; }
  if (plans.length === 0) { statusEl.textContent = '❌ Select at least one plan'; return; }
  statusEl.textContent = 'Saving...';
  try {
    const res = await fetch(`${ADMIN_API}/admin/set-first-offer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Session-Token': sessionToken },
      body: JSON.stringify({ active, percentOff, plans })
    });
    if (res.ok) {
      statusEl.textContent = '✅ Saved';
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

if old_js_anchor in content:
    content = content.replace(old_js_anchor, new_js, 1)
    print("[4/4] Added JS functions")
else:
    print("[4/4] WARNING: renderPromoBanner anchor not found — skipping")

if content != original:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("\nFile saved:", path)
else:
    print("\nNo changes made — check warnings above.")
