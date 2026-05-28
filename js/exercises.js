// Per-type renderers. Each one returns an object with:
//   - mount(container, item)        → render the question UI
//   - answer()                       → return current attempt (or null if none)
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

  // ----- CLOZE: single blank, sentence with ___; choices on chips. -----
  const cloze = {
    mount(container, item) {
      let chosen = null;
      container.innerHTML = '';

      const prompt = document.createElement('p');
      prompt.className = 'prompt';
      prompt.textContent = 'Vul het juiste woord in';
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
      const buttons = (item.choices || []).map(opt =>
        chip(opt, () => {
          if (this._locked) return;
          chosen = opt;
          buttons.forEach(b => b.classList.toggle('selected', b.textContent === opt));
          blank.textContent = opt;
          blank.classList.add('filled');
        })
      );
      buttons.forEach(b => choices.appendChild(b));
      container.appendChild(choices);

      this._blank = blank;
      this._buttons = buttons;
      this._chosen = () => chosen;
      this._locked = false;
    },
    answer() { return this._chosen(); },
    reveal(chosen, isCorrect, item) {
      this._locked = true;
      this._blank.classList.add(isCorrect ? 'correct' : 'wrong');
      if (!isCorrect) this._blank.textContent = item.answer;
      this._buttons.forEach(b => {
        b.disabled = true;
        if (b.textContent === item.answer) b.classList.add('correct');
        else if (b.textContent === chosen && !isCorrect) b.classList.add('wrong');
      });
    },
  };

  // ----- MCQ: same idea but no sentence blank — full sentence visible, answer is option chosen. -----
  const mcq = {
    mount(container, item) {
      let chosen = null;
      container.innerHTML = '';

      const prompt = document.createElement('p');
      prompt.className = 'prompt';
      prompt.textContent = 'Kies het juiste woord';
      container.appendChild(prompt);

      const sentenceEl = document.createElement('p');
      sentenceEl.className = 'sentence';
      // Show sentence with a ___ placeholder visually (same as cloze) so the eye anchors.
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
      const buttons = (item.options || []).map(opt =>
        chip(opt, () => {
          if (this._locked) return;
          chosen = opt;
          buttons.forEach(b => b.classList.toggle('selected', b.textContent === opt));
          blank.textContent = opt;
          blank.classList.add('filled');
        })
      );
      buttons.forEach(b => choices.appendChild(b));
      container.appendChild(choices);

      this._blank = blank;
      this._buttons = buttons;
      this._chosen = () => chosen;
      this._locked = false;
    },
    answer() { return this._chosen(); },
    reveal(chosen, isCorrect, item) {
      this._locked = true;
      this._blank.classList.add(isCorrect ? 'correct' : 'wrong');
      if (!isCorrect) this._blank.textContent = item.answer;
      this._buttons.forEach(b => {
        b.disabled = true;
        if (b.textContent === item.answer) b.classList.add('correct');
        else if (b.textContent === chosen && !isCorrect) b.classList.add('wrong');
      });
    },
  };

  // ----- TRANS-INTRANS: two-button variant (same shape as MCQ, but conventionally 2 options). -----
  // Re-uses the MCQ rendering — separate object so we can show a slightly different prompt.
  const transIntrans = {
    mount(container, item) {
      mcq.mount.call(this, container, item);
      const prompt = container.querySelector('.prompt');
      if (prompt) prompt.textContent = 'Wat doet iemand vs. waar iets is';
    },
    answer() { return this._chosen(); },
    reveal(chosen, isCorrect, item) { mcq.reveal.call(this, chosen, isCorrect, item); },
  };

  // ----- MATCH: pair left items with right items by tapping one of each. -----
  const match = {
    mount(container, item) {
      container.innerHTML = '';
      const prompt = document.createElement('p');
      prompt.className = 'prompt';
      prompt.textContent = item.prompt || 'Match de uitdrukking met de juiste betekenis';
      container.appendChild(prompt);

      const shuffle = arr => arr.map(v => [Math.random(), v]).sort((a, b) => a[0] - b[0]).map(([, v]) => v);
      const leftItems  = shuffle(item.pairs.map((p, i) => ({ idx: i, text: p.left })));
      const rightItems = shuffle(item.pairs.map((p, i) => ({ idx: i, text: p.right })));

      const grid = document.createElement('div');
      grid.className = 'match-grid';

      const leftCol  = document.createElement('div');
      const rightCol = document.createElement('div');
      leftCol.style.display = 'flex'; leftCol.style.flexDirection = 'column'; leftCol.style.gap = '10px';
      rightCol.style.display = 'flex'; rightCol.style.flexDirection = 'column'; rightCol.style.gap = '10px';

      let selectedLeft = null, selectedRight = null;
      const pairs = {}; // leftIdx -> rightIdx
      this._pairs = pairs;
      this._locked = false;

      const tryPair = () => {
        if (selectedLeft == null || selectedRight == null) return;
        pairs[selectedLeft.dataset.idx] = selectedRight.dataset.idx;
        selectedLeft.classList.remove('selected'); selectedLeft.classList.add('paired');
        selectedRight.classList.remove('selected'); selectedRight.classList.add('paired');
        selectedLeft.dataset.paired = '1'; selectedRight.dataset.paired = '1';
        selectedLeft = null; selectedRight = null;
      };

      const makeCell = (text, idx, side) => {
        const c = document.createElement('div');
        c.className = 'match-cell';
        c.dataset.idx = idx;
        c.dataset.side = side;
        c.textContent = text;
        c.addEventListener('click', () => {
          if (this._locked || c.dataset.paired) return;
          if (side === 'L') {
            if (selectedLeft) selectedLeft.classList.remove('selected');
            selectedLeft = c;
          } else {
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
    answer() {
      // Return null until all pairs are placed.
      const total = Object.keys(this._pairs).length;
      const cells = this._cells || [];
      const expectedLefts = Array.from(cells).filter(c => c.dataset.side === 'L').length;
      if (total < expectedLefts) return null;
      return this._pairs;
    },
    reveal(chosen, isCorrect, item) {
      this._locked = true;
      const cells = this._cells;
      // Build a map of correct rightIdx for each leftIdx (identity, since pairs are stored as { left, right }).
      cells.forEach(c => {
        if (c.dataset.side !== 'L') return;
        const li = c.dataset.idx;
        const ri = chosen[li];
        const ok = String(li) === String(ri);
        const rightCell = Array.from(cells).find(x => x.dataset.side === 'R' && x.dataset.idx === ri);
        c.classList.add(ok ? 'correct' : 'wrong');
        if (rightCell) rightCell.classList.add(ok ? 'correct' : 'wrong');
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
