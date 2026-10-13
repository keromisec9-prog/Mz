import shutil

FILE = "index.html"
shutil.copy(FILE, FILE + ".bak_shortstoggle")

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# 1. CSS — mirror the African Cinema slider styling for a new #shortsSlider
old_css = """#africanCinemaSlider::before {
  content: ''; position: absolute; height: 20px; width: 20px; left: 3px; bottom: 3px;
  background: #fff; border-radius: 50%; transition: 0.2s;
}
#africanCinemaToggle:checked + #africanCinemaSlider { background: #e5b93c; }
#africanCinemaToggle:checked + #africanCinemaSlider::before { transform: translateX(22px); }"""

new_css = old_css + """
#shortsSlider::before {
  content: ''; position: absolute; height: 20px; width: 20px; left: 3px; bottom: 3px;
  background: #fff; border-radius: 50%; transition: 0.2s;
}
#shortsToggle:checked + #shortsSlider { background: #e5b93c; }
#shortsToggle:checked + #shortsSlider::before { transform: translateX(22px); }"""

assert content.count(old_css) == 1, "CSS block not found or not unique"
content = content.replace(old_css, new_css)

# 2. HTML row — insert a Shorts toggle card right after the African Cinema one
old_html = """        <label style="position:relative;display:inline-block;width:48px;height:26px;flex-shrink:0;">
          <input type="checkbox" id="africanCinemaToggle" onchange="toggleAfricanCinema(this.checked)" style="opacity:0;width:0;height:0;">
          <span id="africanCinemaSlider" style="position:absolute;cursor:pointer;inset:0;background:#333;border-radius:26px;transition:0.2s;"></span>
        </label>
      </div>
      <div id="githubTokenSection" """

new_html = """        <label style="position:relative;display:inline-block;width:48px;height:26px;flex-shrink:0;">
          <input type="checkbox" id="africanCinemaToggle" onchange="toggleAfricanCinema(this.checked)" style="opacity:0;width:0;height:0;">
          <span id="africanCinemaSlider" style="position:absolute;cursor:pointer;inset:0;background:#333;border-radius:26px;transition:0.2s;"></span>
        </label>
      </div>
      <div style="background:var(--card-bg,#1a1a1a);border:1px solid var(--border,#333);border-radius:8px;padding:1rem;margin-bottom:1rem;display:flex;align-items:center;justify-content:space-between;">
        <div>
          <div style="font-size:0.9rem;font-weight:600;">\U0001F3AC Shorts</div>
          <div style="font-size:0.75rem;color:var(--gray);margin-top:0.15rem;">Show the Shorts tab and feed on the live site</div>
        </div>
        <label style="position:relative;display:inline-block;width:48px;height:26px;flex-shrink:0;">
          <input type="checkbox" id="shortsToggle" onchange="toggleShorts(this.checked)" style="opacity:0;width:0;height:0;">
          <span id="shortsSlider" style="position:absolute;cursor:pointer;inset:0;background:#333;border-radius:26px;transition:0.2s;"></span>
        </label>
      </div>
      <div id="githubTokenSection" """

assert content.count(old_html) == 1, "HTML toggle row not found or not unique"
content = content.replace(old_html, new_html)

# 3. loadSiteSettings() — read shortsEnabled into the new toggle
old_js1 = """    const toggle = document.getElementById('africanCinemaToggle');
    if (toggle) toggle.checked = settings.africanCinemaEnabled !== false;
  } catch (e) {}
}"""

new_js1 = """    const toggle = document.getElementById('africanCinemaToggle');
    if (toggle) toggle.checked = settings.africanCinemaEnabled !== false;
    const shortsToggle = document.getElementById('shortsToggle');
    if (shortsToggle) shortsToggle.checked = settings.shortsEnabled !== false;
  } catch (e) {}
}"""

assert content.count(old_js1) == 1, "loadSiteSettings block not found or not unique"
content = content.replace(old_js1, new_js1)

# 4. toggleShorts() function — mirror toggleAfricanCinema()
old_js2 = """async function toggleAfricanCinema(enabled) {
  try {
    await fetch(`${ADMIN_API}/settings`, {
      method: 'POST',
      headers: { 'X-Session-Token': sessionToken, 'Content-Type': 'application/json' },
      body: JSON.stringify({ africanCinemaEnabled: enabled })
    });
  } catch (e) {
    alert('Failed to update setting. Please try again.');
  }
}"""

new_js2 = old_js2 + """

async function toggleShorts(enabled) {
  try {
    await fetch(`${ADMIN_API}/settings`, {
      method: 'POST',
      headers: { 'X-Session-Token': sessionToken, 'Content-Type': 'application/json' },
      body: JSON.stringify({ shortsEnabled: enabled })
    });
  } catch (e) {
    alert('Failed to update setting. Please try again.');
  }
}"""

assert content.count(old_js2) == 1, "toggleAfricanCinema function not found or not unique"
content = content.replace(old_js2, new_js2)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Admin panel patched: Shorts toggle added.")
