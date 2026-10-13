#!/usr/bin/env python3
import sys

FILE = "index.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# ── 1. Replace the tab-addshort + tab-shorts panels ──────────────────
START_MARK = "<!-- ADD SHORT DRAMA -->"
END_MARK = "<!-- USERS -->"

start_idx = content.find(START_MARK)
end_idx = content.find(END_MARK)
if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
    print("❌ Could not locate ADD SHORT DRAMA / USERS markers — aborting, no changes made.")
    sys.exit(1)

NEW_PANELS = '''<!-- ADD SHORT DRAMA -->
    <div class="tab-content" id="tab-addshort">
      <div class="step">
        <div class="step-header"><div class="step-num">1</div><div class="step-title">Find Short Drama on TMDB</div></div>
        <div style="display:flex;gap:0.5rem;margin-bottom:0.6rem;">
          <button class="btn" id="shortTmdbModeBtn" onclick="setShortMode('tmdb')" style="font-size:0.75rem;flex:1;background:var(--gold);color:#000;">🔍 TMDB Search</button>
          <button class="btn" id="shortManualModeBtn" onclick="setShortMode('manual')" style="font-size:0.75rem;flex:1;">✏️ Manual Entry</button>
        </div>
        <div id="shortTmdbSection">
          <div class="search-row">
            <input type="text" id="shortTmdbQuery" placeholder="Search title..." onkeydown="if(event.key==='Enter')searchShortTMDB()" style="margin-bottom:0;"/>
            <button class="btn btn-gold" onclick="searchShortTMDB()">Search</button>
          </div>
          <div class="poster-grid" id="shortPosterGrid"></div>
          <div id="shortPreview"></div>
          <div class="status" id="shortTmdbStatus"></div>
        </div>
        <div id="shortManualSection" style="display:none;">
          <input type="text" id="manualShortTitle" class="input" placeholder="Title *" style="margin-bottom:0.5rem;"/>
          <input type="text" id="manualShortYear" class="input" placeholder="Year" style="margin-bottom:0.5rem;"/>
          <textarea id="manualShortOverview" class="input" placeholder="Description (optional)" rows="3" style="margin-bottom:0.5rem;resize:vertical;"></textarea>
          <label>Genre</label>
          <select id="manualShortGenre" style="margin-bottom:0.5rem;">
            <option value="28">Action</option><option value="12">Adventure</option><option value="16">Animation</option>
            <option value="35">Comedy</option><option value="80">Crime</option><option value="99">Documentary</option>
            <option value="18" selected>Drama</option><option value="10751">Family</option><option value="14">Fantasy</option>
            <option value="36">History</option><option value="27">Horror</option><option value="10402">Music</option>
            <option value="9648">Mystery</option><option value="10749">Romance</option><option value="878">Science Fiction</option>
            <option value="10770">TV Movie</option><option value="53">Thriller</option><option value="10752">War</option><option value="37">Western</option>
          </select>
          <button class="btn btn-gold" onclick="confirmManualShort()" style="width:100%;">✅ Use This Info</button>
          <div class="status" id="manualShortStatus"></div>
        </div>
        <details style="margin-top:0.6rem;">
          <summary style="font-size:0.75rem;color:#666;cursor:pointer;user-select:none;">⚙️ Custom Poster (optional)</summary>
          <div style="margin-top:0.5rem;">
            <div style="font-size:0.72rem;color:#888;margin-bottom:0.4rem;">Upload a custom poster image to override TMDB. Served via Cloudflare CDN.</div>
            <input type="file" id="shortCustomPosterFile" accept="image/*" style="display:none;" onchange="previewCustomPoster_short(this)"/>
            <div style="display:flex;gap:0.5rem;align-items:center;flex-wrap:wrap;">
              <button class="btn" onclick="document.getElementById('shortCustomPosterFile').click()" style="font-size:0.75rem;padding:0.35rem 0.7rem;">📁 Choose Image</button>
              <button class="btn btn-gold" id="shortCustomPosterUploadBtn" onclick="uploadCustomPoster_short()" style="font-size:0.75rem;padding:0.35rem 0.7rem;display:none;">⬆️ Upload</button>
              <span id="shortCustomPosterStatus" style="font-size:0.72rem;color:#888;"></span>
            </div>
            <img id="shortCustomPosterPreview" src="" style="display:none;width:70px;margin-top:0.4rem;border-radius:4px;"/>
          </div>
        </details>
      </div>
      <div class="step">
        <div class="step-header"><div class="step-num">2</div><div class="step-title">Type & Paywall</div></div>
        <div style="display:flex;gap:0.5rem;margin-bottom:0.6rem;">
          <button class="btn" id="shortTypeSeriesBtn" onclick="setShortType('series')" style="font-size:0.75rem;flex:1;background:var(--gold);color:#000;">📺 Series (many episodes)</button>
          <button class="btn" id="shortTypeFeatureBtn" onclick="setShortType('feature')" style="font-size:0.75rem;flex:1;">🎬 Feature (single ~2hr file)</button>
        </div>
        <div id="shortSeriesFields">
          <label>Free episode count (before paywall)</label>
          <input type="number" id="shortFreeEpisodes" class="input" placeholder="3" style="margin-bottom:0.5rem;" min="0"/>
        </div>
        <div id="shortFeatureFields" style="display:none;">
          <label>Video URL / filename</label>
          <input type="text" id="shortVideoUrl" class="input" placeholder="Video file URL" style="margin-bottom:0.5rem;"/>
          <label>Duration (seconds)</label>
          <input type="number" id="shortDurationSecs" class="input" placeholder="7200" style="margin-bottom:0.5rem;"/>
          <label>Paywall threshold (% watched)</label>
          <input type="number" id="shortThresholdPct" class="input" placeholder="25" style="margin-bottom:0.5rem;" min="1" max="100"/>
        </div>
      </div>
      <div class="step">
        <div class="step-header"><div class="step-num">3</div><div class="step-title">Select VJ & Add</div></div>
        <label>VJ Name</label>
        <div class="vj-row">
          <div id="shortVjPills" style="display:flex;flex-wrap:wrap;gap:0.5rem;"></div>
        </div>
        <label>Custom VJ (optional)</label>
        <input type="text" id="shortVjCustom" placeholder="Type a different VJ name..."
          oninput="if(this.value.trim()){document.querySelectorAll('#tab-addshort .vj-pill').forEach(p=>p.classList.remove('active'));selectedShortVJ=this.value.trim();}" onblur="registerNewVJ(this.value)"/>
        <button class="btn btn-gold btn-full btn-lg" id="addShortBtn" onclick="addShort()">⚡ Add Short Drama to Picha+</button>
        <div class="status" id="addShortStatus"></div>
      </div>
    </div>

    <!-- SHORT DRAMAS LIST -->
    <div class="tab-content" id="tab-shorts">
      <div id="shortsList"><div style="text-align:center;padding:2rem;color:var(--gray);">Loading...</div></div>
    </div>

    '''

content = content[:start_idx] + NEW_PANELS + content[end_idx:]

# ── 2. Replace the JS functions block (currentShortType..loadShorts) ──
JS_START = "let currentShortType = 'series';"
JS_END_MARKER = "Failed to load: ' + e.message + '</div>'; }"

js_start_idx = content.find(JS_START)
if js_start_idx == -1:
    print("❌ JS start marker not found — aborting.")
    sys.exit(1)
marker_idx = content.find(JS_END_MARKER, js_start_idx)
if marker_idx == -1:
    print("❌ JS end marker not found — aborting.")
    sys.exit(1)
js_end_idx = content.find("\n}", marker_idx) + len("\n}")

NEW_JS = '''let currentShortType = 'series';
let selectedShort = null;
let selectedShortVJ = null;
let _shortMode = 'tmdb';

function setShortType(t) {
  currentShortType = t;
  document.getElementById('shortTypeSeriesBtn').style.background = t==='series' ? 'var(--gold)' : '';
  document.getElementById('shortTypeSeriesBtn').style.color = t==='series' ? '#000' : '';
  document.getElementById('shortTypeFeatureBtn').style.background = t==='feature' ? 'var(--gold)' : '';
  document.getElementById('shortTypeFeatureBtn').style.color = t==='feature' ? '#000' : '';
  document.getElementById('shortSeriesFields').style.display = t==='series' ? 'block' : 'none';
  document.getElementById('shortFeatureFields').style.display = t==='feature' ? 'block' : 'none';
}

function setShortMode(mode) {
  _shortMode = mode;
  document.getElementById('shortTmdbSection').style.display = mode === 'tmdb' ? 'block' : 'none';
  document.getElementById('shortManualSection').style.display = mode === 'manual' ? 'block' : 'none';
  document.getElementById('shortTmdbModeBtn').style.background = mode === 'tmdb' ? 'var(--gold)' : '';
  document.getElementById('shortTmdbModeBtn').style.color = mode === 'tmdb' ? '#000' : '';
  document.getElementById('shortManualModeBtn').style.background = mode === 'manual' ? 'var(--gold)' : '';
  document.getElementById('shortManualModeBtn').style.color = mode === 'manual' ? '#000' : '';
  if (mode === 'tmdb') { selectedShort = null; document.getElementById('shortPreview').innerHTML = ''; }
}

async function searchShortTMDB() {
  const query = document.getElementById('shortTmdbQuery').value.trim();
  if (!query) return;
  showStatus('shortTmdbStatus', '🔍 Searching...', 'info');
  try {
    const res = await fetch(`https://api.themoviedb.org/3/search/tv?query=${encodeURIComponent(query)}&api_key=${TMDB_KEY}`);
    const data = await res.json();
    const results = data.results || [];
    if (!results.length) { showStatus('shortTmdbStatus','❌ No results found.','error'); document.getElementById('shortPosterGrid').innerHTML=''; return; }
    document.getElementById('shortTmdbStatus').style.display='none';
    window._shortResults = results;
    document.getElementById('shortPosterGrid').innerHTML = results.slice(0,9).map((s,i) => {
      const poster = s.poster_path ? `https://image.tmdb.org/t/p/w342${s.poster_path}` : null;
      return `<div class="poster-item ${i===0?'selected':''}" onclick="selectShortResult(${i},this)">
        ${poster ? `<img src="${poster}" alt="${esc(s.name)}"/>` : `<div class="poster-placeholder">🎬</div>`}
        <div class="poster-title">${esc(s.name)} (${(s.first_air_date||'').slice(0,4)||'?'})</div>
      </div>`;
    }).join('');
    selectShortResult(0, document.querySelector('#shortPosterGrid .poster-item'));
  } catch { showStatus('shortTmdbStatus','❌ Search failed.','error'); }
}

async function selectShortResult(idx, el) {
  document.querySelectorAll('#shortPosterGrid .poster-item').forEach(e=>e.classList.remove('selected'));
  if (el) el.classList.add('selected');
  const s = window._shortResults[idx];
  showStatus('shortTmdbStatus','Loading details...','info');
  try {
    const res = await fetch(`https://api.themoviedb.org/3/tv/${s.id}?api_key=${TMDB_KEY}`);
    const full = await res.json();
    selectedShort = {
      tmdbId: full.id, title: full.name,
      poster: full.poster_path ? `https://image.tmdb.org/t/p/w300${full.poster_path}` : '',
      backdrop: full.backdrop_path ? `https://image.tmdb.org/t/p/w780${full.backdrop_path}` : '',
      year: (full.first_air_date||'').slice(0,4),
      rating: full.vote_average ? full.vote_average.toFixed(1) : 'N/A',
      overview: full.overview || '',
      genreId: (full.genres||[])[0]?.id || null,
    };
    document.getElementById('shortTmdbStatus').style.display='none';
    document.getElementById('shortPreview').innerHTML = `
      <div class="movie-preview">
        ${selectedShort.poster ? `<img src="${selectedShort.poster}" alt="${esc(selectedShort.title)}"/>` : ''}
        <div>
          <div style="font-weight:700;margin-bottom:0.3rem;">${esc(selectedShort.title)}</div>
          <div style="font-size:0.78rem;color:var(--gray);">${selectedShort.year} · ⭐${selectedShort.rating}</div>
          <div style="font-size:0.75rem;color:var(--gray2);margin-top:0.4rem;">${esc(selectedShort.overview.slice(0,120))}${selectedShort.overview.length>120?'…':''}</div>
        </div>
      </div>`;
  } catch { toast('Could not load details', 'error'); }
}

function confirmManualShort() {
  const title = document.getElementById('manualShortTitle').value.trim();
  if (!title) { showStatus('manualShortStatus', '❌ Title is required', 'error'); return; }
  selectedShort = {
    tmdbId: null, title,
    poster: shortCustomPosterUrl || '',
    backdrop: shortCustomPosterUrl || '',
    year: document.getElementById('manualShortYear').value.trim() || '',
    rating: 0,
    overview: document.getElementById('manualShortOverview').value.trim() || '',
    genreId: document.getElementById('manualShortGenre').value,
  };
  showStatus('manualShortStatus', `✅ "${title}" ready to add. Select VJ below.`, 'success');
}

function selectShortVJ(vj, el) {
  selectedShortVJ = vj;
  document.querySelectorAll('#tab-addshort .vj-pill').forEach(p=>p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('shortVjCustom').value = '';
}

let shortCustomPosterUrl = null;

function previewCustomPoster_short(input) {
  const file = input.files[0]; if (!file) return;
  document.getElementById('shortCustomPosterPreview').src = URL.createObjectURL(file);
  document.getElementById('shortCustomPosterPreview').style.display = 'block';
  document.getElementById('shortCustomPosterUploadBtn').style.display = 'inline-block';
  document.getElementById('shortCustomPosterStatus').textContent = file.name;
}

async function uploadCustomPoster_short() {
  const file = document.getElementById('shortCustomPosterFile').files[0];
  if (!file) return;
  document.getElementById('shortCustomPosterStatus').textContent = '⏳ Uploading...';
  try {
    shortCustomPosterUrl = await _uploadCustomPosterFile(file, selectedShort?.tmdbId, 'short');
    if (selectedShort) selectedShort.poster = shortCustomPosterUrl;
    document.getElementById('shortCustomPosterStatus').textContent = '✅ Uploaded';
  } catch(e) { document.getElementById('shortCustomPosterStatus').textContent = '❌ ' + e.message; }
}

async function addShort() {
  if (!selectedShort) return toast('Select or enter a title first (Step 1)', 'error');
  const vj = document.getElementById('shortVjCustom').value.trim() || selectedShortVJ;
  const btn = document.getElementById('addShortBtn');
  btn.disabled = true; btn.innerHTML = '⏳ Adding...';
  const body = { ...selectedShort, vj, contentType: currentShortType };
  if (currentShortType === 'series') {
    body.paywallFreeEpisodes = parseInt(document.getElementById('shortFreeEpisodes').value) || 3;
  } else {
    body.videoUrl = document.getElementById('shortVideoUrl').value.trim();
    body.durationSecs = parseInt(document.getElementById('shortDurationSecs').value) || 0;
    body.paywallThresholdPct = parseInt(document.getElementById('shortThresholdPct').value) || 25;
  }
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
    } else throw new Error(data.error);
  } catch(e) { showStatus('addShortStatus', '❌ '+e.message, 'error'); }
  btn.disabled = false; btn.innerHTML = '⚡ Add Short Drama to Picha+';
}

async function loadShorts() {
  const el = document.getElementById('shortsList');
  el.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--gray);">Loading...</div>';
  try {
    const res = await fetch(`${ADMIN_API}/shorts`, { headers: { 'X-Session-Token': sessionToken } });
    const data = await res.json();
    const shorts = data.shorts || {};
    const keys = Object.keys(shorts);
    if (!keys.length) { el.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--gray);">No short dramas yet.</div>'; return; }
    el.innerHTML = keys.map(k => {
      const s = shorts[k];
      return `<div style="display:flex;gap:0.7rem;padding:0.6rem;border-bottom:1px solid #222;">
        <img src="${s.poster||''}" style="width:50px;height:70px;object-fit:cover;border-radius:4px;"/>
        <div style="flex:1;">
          <div style="font-weight:700;">${s.title||''}</div>
          <div style="font-size:0.75rem;color:var(--gray);">${s.contentType==='series'?'📺 Series':'🎬 Feature'} · ${s.vj||''}</div>
        </div>
      </div>`;
    }).join('');
  } catch(e) { el.innerHTML = '<div style="text-align:center;padding:2rem;color:red;">Failed to load: ' + e.message + '</div>'; }
}'''

content = content[:js_start_idx] + NEW_JS + content[js_end_idx:]

# ── 3. Patch renderVJPills to also populate shortVjPills ─────────────
OLD_RENDER_TAIL = """  if (seriesContainer) {
    seriesContainer.innerHTML = _allVJs.map((vj, i) =>
      `<div class="vj-pill${vj === selectedSeriesVJ ? ' active' : ''}" onclick="selectSeriesVJ('${esc(vj)}',this)">${esc(vj)}</div>`
    ).join('');
  }
}"""
NEW_RENDER_TAIL = """  if (seriesContainer) {
    seriesContainer.innerHTML = _allVJs.map((vj, i) =>
      `<div class="vj-pill${vj === selectedSeriesVJ ? ' active' : ''}" onclick="selectSeriesVJ('${esc(vj)}',this)">${esc(vj)}</div>`
    ).join('');
  }
  const shortContainer = document.getElementById('shortVjPills');
  if (shortContainer) {
    shortContainer.innerHTML = _allVJs.map((vj, i) =>
      `<div class="vj-pill${vj === selectedShortVJ ? ' active' : ''}" onclick="selectShortVJ('${esc(vj)}',this)">${esc(vj)}</div>`
    ).join('');
  }
}"""

if OLD_RENDER_TAIL not in content:
    print("⚠️  renderVJPills tail pattern not found — VJ pills for Shorts tab won't populate. Skipping this part, rest still applied.")
else:
    count = content.count(OLD_RENDER_TAIL)
    if count == 1:
        content = content.replace(OLD_RENDER_TAIL, NEW_RENDER_TAIL, 1)
    else:
        print(f"⚠️  renderVJPills pattern found {count} times — skipping that part to avoid a bad patch.")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Rebuilt Add Short Drama form with TMDB search, VJ pills, custom poster upload.")
