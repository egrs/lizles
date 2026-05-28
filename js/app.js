// Home screen: render topic cards from topics/index.json with per-topic progress.
(async function () {
  const root = document.getElementById('app');

  let index;
  try {
    const res = await fetch('topics/index.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    index = await res.json();
  } catch (err) {
    root.innerHTML = `<p class="muted">Kon onderwerpen niet laden: ${err.message}</p>`;
    return;
  }

  if (!Array.isArray(index) || index.length === 0) {
    root.innerHTML = `<p class="muted">Nog geen onderwerpen.</p>`;
    return;
  }

  const cards = index.map(t => {
    const agg = Progress.getAgg(t.slug);
    const pct = agg.answered ? Math.round(100 * agg.correct / agg.answered) : null;
    const counts = t.counts || {};

    const badges = [
      counts.verified ? `<span class="badge verified">${counts.verified} verified</span>` : '',
      counts.template ? `<span class="badge template">${counts.template} template</span>` : '',
      counts.review   ? `<span class="badge review">${counts.review} review</span>` : '',
    ].filter(Boolean).join(' ');

    return `
      <a class="topic-card" href="topic.html?topic=${encodeURIComponent(t.slug)}">
        <h2>${escapeHtml(t.title)}</h2>
        <p class="desc">${escapeHtml(t.description || '')}</p>
        <div class="stats">
          <span class="stat"><strong>${agg.answered}</strong> beantwoord</span>
          ${pct !== null ? `<span class="stat"><strong>${pct}%</strong> goed</span>` : ''}
          <span class="stat">${badges}</span>
        </div>
      </a>`;
  }).join('');

  root.innerHTML = cards + `
    <div class="home-footer">
      <button class="btn ghost" id="reset-all">Voortgang wissen</button>
    </div>
  `;

  document.getElementById('reset-all').addEventListener('click', () => {
    if (confirm('Alle voortgang wissen op dit toestel? Dit zet alles terug op 0.')) {
      Progress.resetAll();
      location.reload();
    }
  });
})();

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
}
