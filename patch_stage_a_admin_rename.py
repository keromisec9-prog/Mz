import shutil

FILE = "index.html"
shutil.copy(FILE, FILE + ".bak_stageA")

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

def do_replace(old, new, label):
    global content
    n = content.count(old)
    assert n == 1, f"{label}: expected 1 match, found {n}"
    content = content.replace(old, new)

# CSS
old_css = """#shortsSlider::before {
  content: ''; position: absolute; height: 20px; width: 20px; left: 3px; bottom: 3px;
  background: #fff; border-radius: 50%; transition: 0.2s;
}
#shortsToggle:checked + #shortsSlider { background: #e5b93c; }
#shortsToggle:checked + #shortsSlider::before { transform: translateX(22px); }"""

new_css = """#shortFilmSlider::before {
  content: ''; position: absolute; height: 20px; width: 20px; left: 3px; bottom: 3px;
  background: #fff; border-radius: 50%; transition: 0.2s;
}
#shortFilmToggle:checked + #shortFilmSlider { background: #e5b93c; }
#shortFilmToggle:checked + #shortFilmSlider::before { transform: translateX(22px); }"""

do_replace(old_css, new_css, "CSS block")

# HTML toggle card
old_html = """      <div style="background:var(--card-bg,#1a1a1a);border:1px solid var(--border,#333);border-radius:8px;padding:1rem;margin-bottom:1rem;display:flex;align-items:center;justify-content:space-between;">
        <div>
          <div style="font-size:0.9rem;font-weight:600;">\U0001F3AC Shorts</div>
          <div style="font-size:0.75rem;color:var(--gray);margin-top:0.15rem;">Show the Shorts tab and feed on the live site</div>
        </div>
        <label style="position:relative;display:inline-block;width:48px;height:26px;flex-shrink:0;">
          <input type="checkbox" id="shortsToggle" onchange="toggleShorts(this.checked)" style="opacity:0;width:0;height:0;">
          <span id="shortsSlider" style="position:absolute;cursor:pointer;inset:0;background:#333;border-radius:26px;transition:0.2s;"></span>
        </label>
      </div>"""

new_html = """      <div style="background:var(--card-bg,#1a1a1a);border:1px solid var(--border,#333);border-radius:8px;padding:1rem;margin-bottom:1rem;display:flex;align-items:center;justify-content:space-between;">
        <div>
          <div style="font-size:0.9rem;font-weight:600;">\U0001F3AC Short Film</div>
          <div style="font-size:0.75rem;color:var(--gray);margin-top:0.15rem;">Show the Short Film category and feed on the live site</div>
        </div>
        <label style="position:relative;display:inline-block;width:48px;height:26px;flex-shrink:0;">
          <input type="checkbox" id="shortFilmToggle" onchange="toggleShortFilm(this.checked)" style="opacity:0;width:0;height:0;">
          <span id="shortFilmSlider" style="position:absolute;cursor:pointer;inset:0;background:#333;border-radius:26px;transition:0.2s;"></span>
        </label>
      </div>"""

do_replace(old_html, new_html, "toggle card HTML")

# loadSiteSettings()
old_js1 = """    const shortsToggle = document.getElementById('shortsToggle');
    if (shortsToggle) shortsToggle.checked = settings.shortsEnabled !== false;"""

new_js1 = """    const shortFilmToggle = document.getElementById('shortFilmToggle');
    if (shortFilmToggle) shortFilmToggle.checked = settings.shortFilmEnabled !== false;"""

do_replace(old_js1, new_js1, "loadSiteSettings block")

# toggle function
old_js2 = """async function toggleShorts(enabled) {
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

new_js2 = """async function toggleShortFilm(enabled) {
  try {
    await fetch(`${ADMIN_API}/settings`, {
      method: 'POST',
      headers: { 'X-Session-Token': sessionToken, 'Content-Type': 'application/json' },
      body: JSON.stringify({ shortFilmEnabled: enabled })
    });
  } catch (e) {
    alert('Failed to update setting. Please try again.');
  }
}"""

do_replace(old_js2, new_js2, "toggleShorts function")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Admin panel renamed: Shorts toggle is now Short Film.")
