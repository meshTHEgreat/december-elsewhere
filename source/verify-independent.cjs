'use strict';
/* Package/data verification and browserless app integration checks. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const data = html.match(/<script type="application\/json" id="dataset">([\s\S]*?)<\/script>/)[1];
const javascript = html.match(/<\/script><script>([\s\S]*?)<\/script>/)[1];
const book = JSON.parse(data);
const execution = new vm.Script(javascript);

function fresh(storage = new Map()) {
  const make = () => ({ innerHTML: '', value: '', focus() {}, scrollIntoView() {}, querySelector: make });
  const nodes = new Map();
  const events = {};
  const windowEvents = {};
  const browser = vm.createContext({
    document: {
      getElementById(id) {
        if (!nodes.has(id)) nodes.set(id, make());
        return nodes.get(id);
      },
      querySelector: () => ({ textContent: data }),
      querySelectorAll: () => [],
      addEventListener: (name, fn) => { events[name] = fn; },
    },
    window: { addEventListener: (name, fn) => { windowEvents[name] = fn; } },
    localStorage: { getItem: key => storage.get(key), setItem: (key, value) => storage.set(key, value) },
  });
  execution.runInContext(browser);
  return {
    nodes, storage, windowEvents,
    get: id => nodes.get(id).innerHTML,
    eval: code => vm.runInContext(code, browser),
    click: (dataset, attrs = []) => events.click({
      target: { closest: () => ({ dataset, hasAttribute: name => attrs.includes(name) }) },
    }),
    input: (cost, value) => events.input({ target: { dataset: { cost }, value: String(value) } }),
    change: (id, value) => events.change({ target: { id, value } }),
  };
}

assert.equal(book.cities.length, 5);
assert.match(html, /connect-src 'none'/);
assert.doesNotMatch(html, /<(?:script|img|iframe|audio|video)\s[^>]*src=["']https?:/i);
assert.doesNotMatch(html, /<link\s[^>]*href=["'](?:https?:|\/\/)/i);
assert.doesNotMatch(html, /@import\s|__DATA__|__STYLE__|__SCRIPT__/);
const proofs = {};
const s = fresh();
const f = fresh();
assert.equal(s.eval('current.id'), f.eval('current.id'));
for (const city of book.cities) {
  const id = city.id;
  assert.ok(city.stays.length >= 2);
  assert.equal(city.days.length, city.nights + 1);
  const photos = book.photos[id];
  assert.ok(photos.length >= 2);
  for (const p of photos) {
    assert.match(p.data, /^data:image\/webp;base64,/);
    const binary = Buffer.from(p.data.split(',')[1], 'base64');
    assert.equal(binary.subarray(0, 4).toString(), 'RIFF');
    assert.equal(binary.subarray(8, 12).toString(), 'WEBP');
    assert.ok(p.author && p.license && p.licenseUrl && p.url);
  }
  s.click({ city: id });
  assert.match(s.get('city'), new RegExp('>' + city.city + '</h2>'));
  assert.equal(s.eval('current.id'), id);
  assert.equal(s.eval('slide'), 0);
  const first = s.get('gallery');
  s.click({ gallery: '1' });
  assert.equal(s.eval('slide'), 1);
  assert.notEqual(s.get('gallery'), first);
  const anchors = book.maps[id].anchors;
  assert.ok(anchors.length >= 2);
  let paths = 0, estimates = 0, unavailable = 0;
  for (const anchor of anchors) {
    s.change('anchor-select', anchor.id);
    anchor.routes.forEach((route, index) => {
      const isRouted = route.path && route.path.length > 1;
      const hasEstimate = route.km > 0 && route.min > 0;
      if (isRouted) {
        assert.ok(hasEstimate);
        assert.ok(route.path.every(pt => pt.length === 2 && pt.every(Number.isFinite)));
        paths += 1;
      } else if (hasEstimate) {
        assert.match(route.status, /estim|approx|straight|proxy|heuristic/i);
        estimates += 1;
      } else {
        assert.match(route.status, /not (yet )?retrieved|unavailable|not verified|unknown/i);
        unavailable += 1;
      }
      s.click({ route: String(index) });
      assert.match(s.get('map'), new RegExp('data-route="' + index + '" aria-pressed="true"'));
      if (isRouted) assert.match(s.get('map'), /<polyline/);
      if (hasEstimate && !isRouted) assert.match(s.get('map'), /stroke-dasharray=/);
      if (hasEstimate) assert.match(s.get('map'), /[0-9]+ min · ~?[0-9.]+ km/);
    });
  }
  const total = s.eval('total(current)');
  s.input('flight', s.eval('budget(current).flight') + 53);
  assert.equal(s.eval('total(current)'), total + 159);
  s.input('car', s.eval('budget(current).car') + 269);
  assert.equal(s.eval('total(current)'), total + 428);
  const perStay = s.eval('budget(current).stay');
  s.click({ stay: '1' });
  const afterStay = s.eval('budget(current).stay');
  assert.equal(s.eval('total(current)'), total + 428 + afterStay - perStay);
  assert.match(s.get('total'), /Group total/);
  assert.match(s.get('compare'), /Per adult/);
  assert.equal([...s.get('city').matchAll(/class="day"/g)].length, city.days.length);
  proofs[id] = { anchors: anchors.length, photos: photos.length, paths, estimates, unavailable, days: city.days.length, stays: city.stays.length };
}
s.change('right-city', 'prague');
const restored = fresh(s.storage);
assert.equal(restored.eval('current.id'), 'prague');
assert.equal(restored.eval('state.right'), 'prague');
assert.equal(restored.eval('budget(current).car'), s.eval('budget(current).car'));
restored.click({}, ['data-reset']);
assert.equal(restored.eval('budget(current).car'), book.cities[4].budget.car || 0);
const report = {
  artifact: 'index.html',
  sha256: crypto.createHash('sha256').update(html).digest('hex'),
  bytes: Buffer.byteLength(html),
  status: 'Browserless checks passed. This report does not qualify as a full browser dry round.',
  runtime: process.version,
  network: 'No APIs or browser fetches in clean isolated Node contexts. Generated markup verified as self-contained with connect-src none.',
  coverage: proofs,
  checks: ['fresh isolated JS runtime', 'all city/galleries', 'all path geometry and route actions', 'shared/per-adult pricing', 'stay selections', 'comparison update and persistence', 'itinerary day markup', 'reset', 'photo container format and attribution', 'embedded assets/CSP'],
  excluded: ['browser layout and touch/keyboard events', 'actual decoded rendering and assistive technology', 'live external link and inventory verification'],
};
const reportText = JSON.stringify(report, null, 2) + '\n';
if (process.argv[2]) fs.writeFileSync(process.argv[2], reportText);
process.stdout.write(reportText);
