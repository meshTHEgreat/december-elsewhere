selector => {
  const root = document.querySelector(selector);
  const visible = node => {
    const r = node.getBoundingClientRect();
    const computed = getComputedStyle(node);
    const closed = node.closest('details:not([open])');
    if (closed && node.closest('summary')?.parentElement !== closed) return false;
    return Boolean(r.width && r.height && computed.visibility === 'visible' && !node.closest('[inert]'));
  };
  const n = value => Math.round(value * 100) / 100;
  const box = node => {
    const r = node.getBoundingClientRect();
    return { x: n(r.x), y: n(r.y), w: n(r.width), h: n(r.height), right: n(r.right), bottom: n(r.bottom) };
  };
  const normalize = str => str.trim().replace(/\s+/g, ' ');
  const rendered = node => {
    const rows = [];
    const range = document.createRange();
    const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
    for (let next = walker.nextNode(); next; next = walker.nextNode()) {
      const parent = next.parentElement;
      if (parent.closest('[aria-hidden=true]') || !visible(parent)) continue;
      let offset = 0;
      for (const char of next.textContent) {
        range.setStart(next, offset);
        offset += char.length;
        range.setEnd(next, offset);
        const r = range.getBoundingClientRect();
        if (!r.width || !r.height) continue;
        // Rect top can vary by font. Centre points stay close across inline uses of small and strong.
        const y = r.top + r.height / 2;
        let row = rows.find(l => Math.abs(l.y - y) < 6);
        if (!row) {
          row = { y, raw: '', x: r.x, end: r.right };
          rows.push(row);
        }
        row.raw += char;
        row.x = Math.min(row.x, r.x);
        row.end = Math.max(row.end, r.right);
      }
    }
    return rows.sort((a,b) => a.y - b.y).map(row => {
      const text = normalize(row.raw);
      return { text, count: [...text].length, left: n(row.x), right: n(row.end), baseline: n(row.y) };
    }).filter(row => row.text);
  };
  const targets = [...root.querySelectorAll('a[href], button, summary, select, input')].filter(visible);
  const textNodes = [...root.querySelectorAll('p, h2, h3, dd, figcaption, summary, label, a, button, .flight-leg > strong, .flight-leg > small, .day summary strong, .route-time, .stops li')].filter(visible);
  const sections = [...root.querySelectorAll('.wrap, .arrival-facts, .stays, .stay, .outdoor-guide, .anchor-picker, .route-layout, .map-stage, .mapbox, .walking-list, .transport-notes, .winter-options, .winter-option-layout, .winter-figure, .winter-option-facts, .winter-film, .ss-stage, .itinerary-layout, .daylist, .journey-photo, #gallery, .lightbox-figure, .gallery-tools')].filter(visible);
  const guides = {
    'stay card tops': root.querySelectorAll('.stay'),
    'stay title baselines': root.querySelectorAll('.stay h3'),
    'stay price baselines': root.querySelectorAll('.stay .price'),
    'stay action tops': root.querySelectorAll('.stay-cta'),
    'selected walk and list tops': root.querySelectorAll('.map-stage,.walking-list'),
    'route name rail': root.querySelectorAll('.route-toggle strong'),
    'route time rail': root.querySelectorAll('.route-toggle small'),
    'winter photo and copy tops': root.querySelectorAll('.winter-figure,.winter-option-facts'),
    'itinerary date rail': root.querySelectorAll('.day summary > span'),
    'itinerary title rail': root.querySelectorAll('.day summary > strong'),
  };
  const alignment = Object.fromEntries(Object.entries(guides).map(([name, group]) => {
    const edge = name.endsWith('rail') ? (name.startsWith('route time') ? 'right' : 'x') : 'y';
    const measurements = [...group].filter(visible).map(node => name.includes('baselines') ? rendered(node)[0]?.baseline : box(node)[edge]).filter(v => v !== undefined);
    return [name, measurements.length > 1 ? {spread: n(Math.max(...measurements)-Math.min(...measurements)), measurements} : null];
  }).filter(([,v])=>v));
  return {
    content: box(root), viewport: [innerWidth, innerHeight],
    overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth),
    firstView: targets.filter(node => { const r = node.getBoundingClientRect(); return r.bottom > 105 && r.top < innerHeight; }).length,
    targets: targets.map(node => ({
      text: normalize(node.getAttribute('aria-label') || node.innerText.replace(/\s+/g,' ') || node.value || ''),
      tag: node.tagName.toLowerCase(), class: node.className, rect: box(node),
    })),
    text: textNodes.map(node => ({
      tag: node.tagName.toLowerCase(), class: node.className,
      rect: box(node), length: normalize(node.textContent).length, lines: rendered(node),
      foreground: getComputedStyle(node).color, background: getComputedStyle(node).backgroundColor,
    })),
    rails: sections.map(node => ({key: node.id || node.classList[0], ...box(node)})),
    alignment,
  };
}
