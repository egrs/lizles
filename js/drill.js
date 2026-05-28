// Drill loop: load topic exercises, filter by confidence, shuffle (weak-first), present one at a time.
(async function () {
  const params = new URLSearchParams(location.search);
  const slug = params.get('topic');
  if (!slug) { location.href = 'index.html'; return; }

  const root = document.getElementById('drill');
  const titleEl = document.getElementById('topic-title');
  const progressFill = document.getElementById('progress-fill');

  // Load meta + exercises in parallel.
  let meta, all;
  try {
    const [metaRes, exRes] = await Promise.all([
      fetch(`topics/${slug}/meta.json`, { cache: 'no-store' }),
      fetch(`topics/${slug}/exercises.json`, { cache: 'no-store' }),
    ]);
    if (!metaRes.ok) throw new Error(`meta.json HTTP ${metaRes.status}`);
    if (!exRes.ok)   throw new Error(`exercises.json HTTP ${exRes.status}`);
    meta = await metaRes.json();
    all  = await exRes.json();
  } catch (err) {
    root.innerHTML = `<p class="muted">Kon dit onderwerp niet laden: ${err.message}</p>`;
    return;
  }

  titleEl.textContent = meta.title || slug;

  // Schema sanity.
  const issues = validate(all);
  if (issues.length) {
    root.innerHTML = `<p class="muted">Schema-fout: ${escapeHtml(issues[0])}</p>`;
    return;
  }

  // --- Settings (persisted per-device, not per-topic) ---
  const settings = loadSettings();
  document.getElementById('opt-include-review').checked = settings.includeReview;
  document.getElementById('opt-weak-first').checked = settings.weakFirst;
  document.getElementById('opt-include-review').addEventListener('change', e => {
    settings.includeReview = e.target.checked; saveSettings(settings); rebuildDeck();
  });
  document.getElementById('opt-weak-first').addEventListener('change', e => {
    settings.weakFirst = e.target.checked; saveSettings(settings);
  });
  document.getElementById('settings-btn').addEventListener('click', () => {
    document.getElementById('settings-panel').hidden = false;
  });
  document.getElementById('settings-close').addEventListener('click', () => {
    document.getElementById('settings-panel').hidden = true;
  });
  document.getElementById('reset-progress').addEventListener('click', () => {
    if (confirm('Voortgang voor dit onderwerp resetten?')) { Progress.reset(slug); location.reload(); }
  });

  // Wrap settings panel content (delegated wrapping so existing markup is preserved).
  const panel = document.getElementById('settings-panel');
  if (panel && !panel.querySelector('.panel-inner')) {
    const inner = document.createElement('div'); inner.className = 'panel-inner';
    while (panel.firstChild) inner.appendChild(panel.firstChild);
    panel.appendChild(inner);
    panel.addEventListener('click', e => { if (e.target === panel) panel.hidden = true; });
  }

  let deck = [], cursor = 0, wrongIds = [];

  function rebuildDeck() {
    let pool = all.filter(item => settings.includeReview || item.confidence !== 'review');
    deck = settings.weakFirst ? weightedShuffle(pool) : shuffle(pool);
    cursor = 0;
    wrongIds = [];
    renderCurrent();
  }

  function weightedShuffle(items) {
    // Sample without replacement, picking weighted-randomly each step.
    const pool = items.slice();
    const weights = pool.map(it => Progress.weight(slug, it.id));
    const out = [];
    while (pool.length) {
      const sum = weights.reduce((a, b) => a + b, 0);
      let r = Math.random() * sum;
      let pick = 0;
      for (; pick < weights.length; pick++) {
        r -= weights[pick];
        if (r <= 0) break;
      }
      if (pick >= pool.length) pick = pool.length - 1;
      out.push(pool[pick]);
      pool.splice(pick, 1);
      weights.splice(pick, 1);
    }
    return out;
  }

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function renderCurrent() {
    if (cursor >= deck.length) return renderSummary();
    const item = deck[cursor];
    progressFill.style.width = `${(cursor / deck.length) * 100}%`;

    root.innerHTML = '';
    const card = document.createElement('article');
    card.className = 'exercise';
    root.appendChild(card);

    const renderer = Exercises.forType(item.type);
    renderer.mount(card, item);

    // Meta row: confidence badge + report link.
    const meta = document.createElement('div');
    meta.className = 'item-meta';
    const flagged = (Progress.getItem(slug, item.id) || {}).flagged;
    meta.innerHTML = `
      <span class="badge ${item.confidence}">${item.confidence}</span>
      <span style="flex:1"></span>
      <button class="report-btn ${flagged ? 'flagged' : ''}">${flagged ? '⚑ gemeld' : 'Klopt dit niet?'}</button>
    `;
    meta.querySelector('.report-btn').addEventListener('click', (e) => {
      const wasFlagged = e.target.classList.contains('flagged');
      Progress.flag(slug, item.id, !wasFlagged);
      e.target.classList.toggle('flagged');
      e.target.textContent = wasFlagged ? 'Klopt dit niet?' : '⚑ gemeld';
    });
    card.appendChild(meta);

    // Action bar (Check / Volgende).
    const bar = document.createElement('div');
    bar.className = 'actionbar';
    const checkBtn = document.createElement('button');
    checkBtn.className = 'btn'; checkBtn.textContent = 'Controleer';
    bar.appendChild(checkBtn);
    document.body.appendChild(bar);
    root.dataset.barAttached = '1';

    let revealed = false;
    checkBtn.addEventListener('click', () => {
      if (!revealed) {
        const chosen = renderer.answer();
        if (chosen == null || (typeof chosen === 'object' && Object.keys(chosen).length === 0)) return;
        const isCorrect = typeof renderer.isCorrect === 'function'
          ? renderer.isCorrect(chosen, item)
          : chosen === item.answer;

        renderer.reveal(chosen, isCorrect, item);
        Progress.record(slug, item.id, isCorrect);
        if (!isCorrect) wrongIds.push(item.id);

        const fb = document.createElement('div');
        fb.className = 'feedback ' + (isCorrect ? 'correct' : 'wrong');
        fb.innerHTML = `<strong>${isCorrect ? 'Goed zo!' : 'Helaas.'}</strong>${item.explanation ? `<div class="explain">${escapeHtml(item.explanation)}</div>` : ''}`;
        card.appendChild(fb);

        checkBtn.textContent = 'Volgende';
        revealed = true;
      } else {
        // Clean up the bar (it's per-render).
        bar.remove();
        cursor += 1;
        renderCurrent();
      }
    });
  }

  function renderSummary() {
    progressFill.style.width = '100%';
    const agg = Progress.getAgg(slug);
    const total = deck.length;
    const wrong = wrongIds.length;
    const right = total - wrong;
    const pct = total ? Math.round(100 * right / total) : 0;

    root.innerHTML = `
      <section class="summary">
        <p class="muted">Deck klaar</p>
        <div class="score">${pct}%</div>
        <p>${right} van ${total} goed</p>
        <p class="muted">Totaal beantwoord op dit toestel: ${agg.answered} (${agg.answered ? Math.round(100*agg.correct/agg.answered) : 0}% goed)</p>
        <div class="actions">
          ${wrong ? '<button class="btn ghost" id="redo-wrong">Doe de foute opnieuw</button>' : ''}
          <button class="btn" id="redo-all">Nieuwe ronde</button>
        </div>
      </section>
    `;

    const redoWrong = document.getElementById('redo-wrong');
    if (redoWrong) redoWrong.addEventListener('click', () => {
      const wrongSet = new Set(wrongIds);
      deck = all.filter(it => wrongSet.has(it.id));
      deck = settings.weakFirst ? weightedShuffle(deck) : shuffle(deck);
      cursor = 0; wrongIds = [];
      renderCurrent();
    });
    document.getElementById('redo-all').addEventListener('click', rebuildDeck);
  }

  rebuildDeck();
})();

function validate(items) {
  if (!Array.isArray(items)) return ['exercises.json moet een array zijn'];
  const ids = new Set();
  for (const [i, it] of items.entries()) {
    if (!it || typeof it !== 'object') return [`item ${i} is geen object`];
    if (!it.id) return [`item ${i} mist id`];
    if (ids.has(it.id)) return [`dubbel id: ${it.id}`];
    ids.add(it.id);
    if (!['cloze','mcq','match','trans-intrans'].includes(it.type)) return [`item ${it.id} heeft onbekend type: ${it.type}`];
    if (!['verified','template','review'].includes(it.confidence)) return [`item ${it.id} heeft ongeldige confidence: ${it.confidence}`];
    if (it.type === 'cloze' && (!it.choices || !it.answer || !it.sentence?.includes('___'))) return [`cloze ${it.id} mist sentence/answer/choices`];
    if (it.type === 'mcq'   && (!it.options || !it.answer || !it.sentence?.includes('___'))) return [`mcq ${it.id} mist sentence/answer/options`];
    if (it.type === 'trans-intrans' && (!it.options || !it.answer || !it.sentence?.includes('___'))) return [`trans-intrans ${it.id} mist sentence/answer/options`];
    if (it.type === 'match' && (!Array.isArray(it.pairs) || it.pairs.length < 2)) return [`match ${it.id} mist pairs`];
  }
  return [];
}

function loadSettings() {
  try { return Object.assign({ includeReview: false, weakFirst: true }, JSON.parse(localStorage.getItem('lizles:__settings'))); }
  catch { return { includeReview: false, weakFirst: true }; }
}
function saveSettings(s) { localStorage.setItem('lizles:__settings', JSON.stringify(s)); }

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
}
