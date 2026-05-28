// localStorage-backed progress tracker.
// Key shape: lizles:<topic-slug>:<exercise-id> -> { seen, correct, lastWrongAt, flagged }
// Aggregate key: lizles:<topic-slug>:__agg -> { answered, correct }
const Progress = (() => {
  const PREFIX = 'lizles';
  const k = (slug, id) => `${PREFIX}:${slug}:${id}`;
  const aggK = (slug) => `${PREFIX}:${slug}:__agg`;

  const getItem = (slug, id) => {
    try { return JSON.parse(localStorage.getItem(k(slug, id))) || null; }
    catch { return null; }
  };
  const setItem = (slug, id, v) => localStorage.setItem(k(slug, id), JSON.stringify(v));

  const getAgg = (slug) => {
    try { return JSON.parse(localStorage.getItem(aggK(slug))) || { answered: 0, correct: 0 }; }
    catch { return { answered: 0, correct: 0 }; }
  };
  const setAgg = (slug, v) => localStorage.setItem(aggK(slug), JSON.stringify(v));

  const record = (slug, id, isCorrect) => {
    const cur = getItem(slug, id) || { seen: 0, correct: 0, lastWrongAt: 0, flagged: false };
    cur.seen += 1;
    if (isCorrect) cur.correct += 1;
    else cur.lastWrongAt = Date.now();
    setItem(slug, id, cur);

    const agg = getAgg(slug);
    agg.answered += 1;
    if (isCorrect) agg.correct += 1;
    setAgg(slug, agg);
  };

  const flag = (slug, id, on = true) => {
    const cur = getItem(slug, id) || { seen: 0, correct: 0, lastWrongAt: 0, flagged: false };
    cur.flagged = !!on;
    setItem(slug, id, cur);
  };

  // Returns a weight in [0.2, 3.0] — higher = more likely to be drawn.
  // Unseen items default to 1.0; weak / recently-wrong items get boosted; mastered items decay.
  const weight = (slug, id) => {
    const p = getItem(slug, id);
    if (!p || p.seen === 0) return 1.0;
    const acc = p.correct / p.seen;
    let w = 1.0;
    if (acc < 0.5) w *= 2.0;
    else if (acc < 0.8) w *= 1.4;
    else w *= 0.6;
    const dayAgo = Date.now() - 24 * 3600 * 1000;
    if (p.lastWrongAt && p.lastWrongAt > dayAgo) w *= 1.8;
    return Math.max(0.2, Math.min(3.0, w));
  };

  const reset = (slug) => {
    const prefix = `${PREFIX}:${slug}:`;
    const toRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix)) toRemove.push(key);
    }
    toRemove.forEach(key => localStorage.removeItem(key));
  };

  // Wipe every lizles progress key, leaving UI settings (lizles:__settings) intact.
  const resetAll = () => {
    const prefix = `${PREFIX}:`;
    const keep = `${PREFIX}:__settings`;
    const toRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix) && key !== keep) toRemove.push(key);
    }
    toRemove.forEach(key => localStorage.removeItem(key));
  };

  // Returns all flagged ids for a topic (for export later).
  const flaggedIds = (slug) => {
    const prefix = `${PREFIX}:${slug}:`;
    const out = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key || !key.startsWith(prefix) || key.endsWith(':__agg')) continue;
      try {
        const v = JSON.parse(localStorage.getItem(key));
        if (v && v.flagged) out.push(key.slice(prefix.length));
      } catch {}
    }
    return out;
  };

  return { record, flag, weight, reset, resetAll, getAgg, getItem, flaggedIds };
})();
