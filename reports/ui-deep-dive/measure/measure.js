scope => {
  const root = document.querySelector(scope);
  if (!root) throw new Error('Missing scope ' + scope);
  const rounded = value => Math.round(value * 100) / 100;
  const box = element => element.getBoundingClientRect();
  const shown = element => element.getClientRects().length > 0 && getComputedStyle(element).visibility === 'visible';
  const name = element => (element.getAttribute('aria-label') || element.innerText || element.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 110);
  const selector = element => element.id ? '#' + element.id : element.tagName.toLowerCase() +
    [...element.classList].slice(0, 2).map(className => '.' + className).join('');
  const props = (element, edge) => box(element)[edge];
  const lineText = element => {
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    const lines = new Map();
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (!shown(node.parentElement) || !node.textContent.trim()) continue;
      let offset = 0;
      for (const character of node.textContent) {
        range.setStart(node, offset);
        offset += character.length;
        range.setEnd(node, offset);
        const rect = range.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) continue;
        let key = [...lines.keys()].find(top => Math.abs(rect.bottom - top) < 4);
        if (key === undefined) key = rect.bottom;
        lines.set(key, (lines.get(key) || '') + character);
      }
    }
    return [...lines.entries()].sort((a, b) => a[0] - b[0]).map(([, line]) => line.trim()).filter(Boolean);
  };
  const shape = box(root);
  const targets = [...root.querySelectorAll('a[href],button,input,select,summary')].filter(shown).map(element => {
    const rect = box(element);
    return {element: selector(element), name: name(element), width: rounded(rect.width), height: rounded(rect.height)};
  });
  const types = [...root.querySelectorAll('h1,h2,h3,p,dd,label,button,th,summary')]
    .filter(element => shown(element) && !element.closest('template') && box(element).width > 1)
    .map(element => {
      const body = element.matches('p,dd') && name(element).length >= 40;
      return {element: selector(element), body, lines: lineText(element)};
    }).filter(item => item.lines.length);
  const groupDefinitions = [
    ['budget label edges', '.budget-fields label > span', 'left'],
    ['budget amount right edges', '.budget-fields input', 'right'],
    ['chart label start', '.compare-budget-row b', 'left'],
    ['chart amount end', '.compare-budget-row strong', 'right'],
    ['compare picker tops', '.compare-controls select', 'top'],
    ['atlas picker and globe button', '.atlas-bar :is(select,button)', 'top'],
    ['chapter nav items', '.chapter-jumps a', 'top'],
    ['route button left edges', '.walking-list .route-toggle', 'left'],
    ['itinerary date left edges', '.day summary > span', 'left'],
    ['itinerary title left edges', '.day summary > strong', 'left'],
    ['winter option leftmost row tops', '.winter-options .winter-option', 'top', true],
  ];
  const alignments = groupDefinitions.flatMap(([label, query, edge, oneRow]) => {
    let siblings = [...root.querySelectorAll(query)].filter(shown);
    if (oneRow && siblings.length) siblings = siblings.filter(e => Math.abs(box(e).top - box(siblings[0]).top) < 8);
    if (siblings.length < 2) return [];
    const values = siblings.map(e => props(e, edge));
    return [{label, edge, count: siblings.length, spread: rounded(Math.max(...values) - Math.min(...values))}];
  });
  const scroll = [...root.querySelectorAll('table,.compare-scroll,dialog,.chapter-menu > div')]
    .filter(shown).map(element => ({element: selector(element), content: element.scrollWidth, visible: element.clientWidth}));
  const dir = getComputedStyle(root).direction;
  return {
    scope, direction: dir, language: document.documentElement.lang, width: innerWidth, height: innerHeight,
    rail: {content: rounded(shape.width), left: rounded(shape.left), right: rounded(innerWidth - shape.right)},
    documentOverflow: Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth),
    state: {hash: location.hash, focus: selector(document.activeElement)}, targets, types, alignments, scroll,
  };
}
