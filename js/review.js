// review.html — local-only reviewer for confidence: review items.
// Loads exercises.json for the chosen topic, lets the reviewer approve / edit / reject pending items,
// and offers a download of the resulting JSON (overwrite topics/<slug>/exercises.json by hand).
(async function () {
  const topicSel = document.getElementById('topic-select');
  const list = document.getElementById('review-list');
  const dl = document.getElementById('download');

  let topics;
  try {
    topics = await fetch('topics/index.json').then(r => r.json());
  } catch (err) {
    list.innerHTML = `<li class="muted">Kon topics/index.json niet laden: ${err.message}</li>`;
    return;
  }

  topics.forEach(t => {
    const o = document.createElement('option');
    o.value = t.slug; o.textContent = t.title;
    topicSel.appendChild(o);
  });

  let currentSlug = topics[0]?.slug;
  let currentExercises = [];

  async function load(slug) {
    currentSlug = slug;
    list.innerHTML = '<li class="muted">Laden…</li>';
    currentExercises = await fetch(`topics/${slug}/exercises.json`).then(r => r.json());
    render();
  }

  function render() {
    const pending = currentExercises.filter(e => e.confidence === 'review');
    if (pending.length === 0) {
      list.innerHTML = '<li class="muted">Geen items met label "review" voor dit onderwerp. 🎉</li>';
      return;
    }
    list.innerHTML = '';
    pending.forEach(item => list.appendChild(renderItem(item)));
  }

  function renderItem(item) {
    const li = document.createElement('li');
    li.className = 'review-item';
    const meta = `<div class="muted" style="font-size:.85rem">${item.id} · ${item.type} · bron: ${item.source || '—'}</div>`;

    if (item.type === 'cloze' || item.type === 'mcq' || item.type === 'trans-intrans') {
      li.innerHTML = `
        ${meta}
        <label>Zin (gebruik <code>___</code> voor de blank)</label>
        <textarea data-field="sentence">${escapeAttr(item.sentence || '')}</textarea>
        <label>Antwoord</label>
        <input type="text" data-field="answer" value="${escapeAttr(item.answer || '')}">
        <label>Opties / choices (komma-gescheiden)</label>
        <input type="text" data-field="options" value="${escapeAttr((item.choices || item.options || []).join(', '))}">
        <label>Uitleg</label>
        <textarea data-field="explanation">${escapeAttr(item.explanation || '')}</textarea>
      `;
    } else if (item.type === 'match') {
      li.innerHTML = `
        ${meta}
        <label>Paren (één per regel, vorm <code>links | rechts</code>)</label>
        <textarea data-field="pairs" style="min-height:140px">${escapeAttr((item.pairs || []).map(p => `${p.left} | ${p.right}`).join('\n'))}</textarea>
        <label>Uitleg</label>
        <textarea data-field="explanation">${escapeAttr(item.explanation || '')}</textarea>
      `;
    }

    const row = document.createElement('div');
    row.className = 'row';
    row.innerHTML = `
      <button class="btn" data-act="approve">Goedkeuren → verified</button>
      <button class="btn ghost" data-act="save">Bewerking opslaan</button>
      <button class="btn ghost" data-act="reject" style="color:var(--wrong); border-color:var(--wrong)">Verwijderen</button>
    `;
    li.appendChild(row);

    row.querySelector('[data-act="approve"]').addEventListener('click', () => {
      apply(li, item);
      item.confidence = 'verified';
      item.reviewedBy = 'native';
      item.reviewedAt = new Date().toISOString().slice(0, 10);
      render();
    });
    row.querySelector('[data-act="save"]').addEventListener('click', () => { apply(li, item); render(); });
    row.querySelector('[data-act="reject"]').addEventListener('click', () => {
      if (!confirm(`Item ${item.id} verwijderen?`)) return;
      currentExercises = currentExercises.filter(e => e.id !== item.id);
      render();
    });

    return li;
  }

  function apply(li, item) {
    const get = sel => li.querySelector(`[data-field="${sel}"]`)?.value ?? '';
    if (item.type === 'match') {
      item.pairs = get('pairs').split('\n').map(s => s.trim()).filter(Boolean)
        .map(line => {
          const [l, r] = line.split('|').map(s => s.trim());
          return { left: l, right: r };
        });
    } else {
      item.sentence = get('sentence');
      item.answer = get('answer');
      const opts = get('options').split(',').map(s => s.trim()).filter(Boolean);
      if (item.type === 'cloze') item.choices = opts;
      else item.options = opts;
    }
    item.explanation = get('explanation');
  }

  dl.addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(currentExercises, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `exercises.${currentSlug}.json`;
    a.click();
  });

  topicSel.addEventListener('change', e => load(e.target.value));
  if (currentSlug) load(currentSlug);
})();

function escapeAttr(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
}
