// Per-type renderers. Each one returns an object with:
//   - mount(container, item, onSubmit) → render the question UI; call onSubmit(answer) as soon
//                                         as the answer is complete (auto-submit, no confirm step)
//   - reveal(answer, isCorrect, item) → show feedback styling
// The drill engine handles feedback text, "Volgende", and persistence.

const Exercises = (() => {

  // Shared helper: build a list of tap-chip buttons.
  const chip = (label, onClick) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'chip';
    b.textContent = label;
    b.addEventListener('click', onClick);
    return b;
  };

  // Shared chip-question mounter: cloze / mcq / trans-intrans all use the same shape.
  // `choicesField` says whether to read item.choices (cloze) or item.options (mcq, trans-intrans).
  const mountChipQuestion = function (container, item, onSubmit, { promptText, choicesField }) {
    container.innerHTML = '';

    const prompt = document.createElement('p');
    prompt.className = 'prompt';
    prompt.textContent = promptText;
    container.appendChild(prompt);

    const sentenceEl = document.createElement('p');
    sentenceEl.className = 'sentence';
    const [before, after] = item.sentence.split('___');
    sentenceEl.appendChild(document.createTextNode(before ?? ''));
    const blank = document.createElement('span');
    blank.className = 'blank';
    blank.textContent = '____';
    sentenceEl.appendChild(blank);
    sentenceEl.appendChild(document.createTextNode(after ?? ''));
    container.appendChild(sentenceEl);

    const choices = document.createElement('div');
    choices.className = 'choices';
    const buttons = (item[choicesField] || []).map(opt =>
      chip(opt, () => {
        if (this._locked) return;
        this._locked = true;
        buttons.forEach(b => b.classList.toggle('selected', b.textContent === opt));
        blank.textContent = opt;
        blank.classList.add('filled');
        onSubmit(opt);
      })
    );
    buttons.forEach(b => choices.appendChild(b));
    container.appendChild(choices);

    this._blank = blank;
    this._buttons = buttons;
    this._locked = false;
  };

  const revealChipQuestion = function (chosen, isCorrect, item) {
    this._locked = true;
    this._blank.classList.add(isCorrect ? 'correct' : 'wrong');
    if (!isCorrect) this._blank.textContent = item.answer;
    this._buttons.forEach(b => {
      b.disabled = true;
      if (b.textContent === item.answer) b.classList.add('correct');
      else if (b.textContent === chosen && !isCorrect) b.classList.add('wrong');
    });
  };

  // ----- CLOZE: single blank, sentence with ___; choices on chips. -----
  const cloze = {
    mount(container, item, onSubmit) {
      mountChipQuestion.call(this, container, item, onSubmit,
        { promptText: 'Vul het juiste woord in', choicesField: 'choices' });
    },
    reveal: revealChipQuestion,
  };

  // ----- MCQ: full sentence with placeholder, choose from options. -----
  const mcq = {
    mount(container, item, onSubmit) {
      mountChipQuestion.call(this, container, item, onSubmit,
        { promptText: 'Kies het juiste woord', choicesField: 'options' });
    },
    reveal: revealChipQuestion,
  };

  // ----- TRANS-INTRANS: two-button variant (same shape as MCQ, different prompt). -----
  const transIntrans = {
    mount(container, item, onSubmit) {
      mountChipQuestion.call(this, container, item, onSubmit,
        { promptText: 'Wat doet iemand vs. waar iets is', choicesField: 'options' });
    },
    reveal: revealChipQuestion,
  };

  // ----- MATCH: pair left items with right items by tapping one of each. -----
  // Each completed pair gets a shared colour + number badge so the association is
  // visible. Tap a paired cell to un-pair it; tap a selected-but-unpaired cell to
  // deselect. Auto-submits once the final pair completes the grid.
  const MATCH_PALETTE = ['#2f7d3a', '#234a63', '#7a4f00', '#7d2f6a', '#2f6f7d', '#a3471f', '#4a5d23', '#5a2f7d'];

  const match = {
    mount(container, item, onSubmit) {
      container.innerHTML = '';
      const prompt = document.createElement('p');
      prompt.className = 'prompt';
      prompt.textContent = item.prompt || 'Match de uitdrukking met de juiste betekenis';
      container.appendChild(prompt);

      const hint = document.createElement('p');
      hint.className = 'match-hint';
      hint.textContent = 'Tik links en rechts om te koppelen. Tik op een gekoppeld vakje om het weer los te maken.';
      container.appendChild(hint);

      const shuffle = arr => arr.map(v => [Math.random(), v]).sort((a, b) => a[0] - b[0]).map(([, v]) => v);
      const leftItems  = shuffle(item.pairs.map((p, i) => ({ idx: i, text: p.left })));
      const rightItems = shuffle(item.pairs.map((p, i) => ({ idx: i, text: p.right })));
      const totalPairs = item.pairs.length;

      const grid = document.createElement('div');
      grid.className = 'match-grid';

      const leftCol  = document.createElement('div');
      const rightCol = document.createElement('div');
      leftCol.style.display = 'flex'; leftCol.style.flexDirection = 'column'; leftCol.style.gap = '10px';
      rightCol.style.display = 'flex'; rightCol.style.flexDirection = 'column'; rightCol.style.gap = '10px';

      let selectedLeft = null, selectedRight = null;
      const pairs = {};                 // leftIdx -> rightIdx
      const colorByLeft = {};           // leftIdx -> palette index
      const usedColors = new Set();
      const cellMap = { L: {}, R: {} }; // side -> idx -> cell
      this._pairs = pairs;
      this._locked = false;

      const takeColor = () => {
        for (let i = 0; i < MATCH_PALETTE.length; i++) {
          if (!usedColors.has(i)) { usedColors.add(i); return i; }
        }
        return 0;
      };

      const applyPairStyle = (cell, ci) => {
        const color = MATCH_PALETTE[ci];
        cell.style.borderColor = color;
        cell.style.background = color + '20'; // soft tint (hex alpha)
        const badge = cell.querySelector('.match-badge');
        badge.textContent = String(ci + 1);
        badge.style.background = color;
      };

      const clearPairStyle = (cell) => {
        cell.classList.remove('paired');
        delete cell.dataset.paired;
        cell.style.borderColor = '';
        cell.style.background = '';
        const badge = cell.querySelector('.match-badge');
        badge.textContent = '';
        badge.style.background = '';
      };

      const unpair = (li) => {
        const ri = pairs[li];
        delete pairs[li];
        const ci = colorByLeft[li];
        if (ci != null) { usedColors.delete(ci); delete colorByLeft[li]; }
        clearPairStyle(cellMap.L[li]);
        if (cellMap.R[ri]) clearPairStyle(cellMap.R[ri]);
      };

      const tryPair = () => {
        if (selectedLeft == null || selectedRight == null) return;
        const li = selectedLeft.dataset.idx, ri = selectedRight.dataset.idx;
        const ci = takeColor();
        pairs[li] = ri;
        colorByLeft[li] = ci;
        [selectedLeft, selectedRight].forEach(c => {
          c.classList.remove('selected');
          c.classList.add('paired');
          c.dataset.paired = '1';
          applyPairStyle(c, ci);
        });
        selectedLeft = null; selectedRight = null;
        if (Object.keys(pairs).length >= totalPairs) {
          this._locked = true;
          onSubmit(pairs);
        }
      };

      const makeCell = (text, idx, side) => {
        const c = document.createElement('div');
        c.className = 'match-cell';
        c.dataset.idx = idx;
        c.dataset.side = side;
        const badge = document.createElement('span');
        badge.className = 'match-badge';
        const label = document.createElement('span');
        label.className = 'match-text';
        label.textContent = text;
        c.appendChild(badge);
        c.appendChild(label);
        cellMap[side][idx] = c;
        c.addEventListener('click', () => {
          if (this._locked) return;
          // Tap a paired cell → un-pair it (find the left index of this pair).
          if (c.dataset.paired) {
            const li = side === 'L'
              ? idx
              : Object.keys(pairs).find(k => String(pairs[k]) === String(idx));
            if (li != null) unpair(li);
            return;
          }
          if (side === 'L') {
            if (selectedLeft === c) { c.classList.remove('selected'); selectedLeft = null; return; }
            if (selectedLeft) selectedLeft.classList.remove('selected');
            selectedLeft = c;
          } else {
            if (selectedRight === c) { c.classList.remove('selected'); selectedRight = null; return; }
            if (selectedRight) selectedRight.classList.remove('selected');
            selectedRight = c;
          }
          c.classList.add('selected');
          tryPair();
        });
        return c;
      };

      leftItems.forEach(({ idx, text }) => leftCol.appendChild(makeCell(text, idx, 'L')));
      rightItems.forEach(({ idx, text }) => rightCol.appendChild(makeCell(text, idx, 'R')));

      grid.appendChild(leftCol);
      grid.appendChild(rightCol);
      container.appendChild(grid);

      this._cells = container.querySelectorAll('.match-cell');
    },
    reveal(chosen, isCorrect, item) {
      this._locked = true;
      const cells = this._cells;
      // Keep each pair's colour tint + badge so the grouping stays visible; show
      // correctness with a ✓/✗ marker and a coloured ring on top of the tint.
      cells.forEach(c => {
        if (c.dataset.side !== 'L') return;
        const li = c.dataset.idx;
        const ri = chosen[li];
        const ok = String(li) === String(ri);
        const rightCell = Array.from(cells).find(x => x.dataset.side === 'R' && x.dataset.idx === ri);
        [c, rightCell].forEach(x => {
          if (!x) return;
          x.classList.add(ok ? 'match-correct' : 'match-wrong');
          const status = document.createElement('span');
          status.className = 'match-status ' + (ok ? 'ok' : 'bad');
          status.textContent = ok ? '✓' : '✗';
          x.appendChild(status);
        });
      });
    },
    // Match scores correct only if every pair is right.
    isCorrect(chosen, item) {
      return Object.entries(chosen).every(([l, r]) => String(l) === String(r));
    },
  };

  const dispatch = {
    cloze, mcq, match,
    'trans-intrans': transIntrans,
  };

  return {
    forType(type) {
      const proto = dispatch[type];
      if (!proto) throw new Error(`Onbekend exercise type: ${type}`);
      // Each call returns a fresh object so renderer state doesn't leak between items.
      return Object.assign({}, proto);
    },
  };
})();
