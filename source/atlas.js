const atlasPlaces = cities.map(city => ({ id: city.id, label: city.city, ...book.editorial.cities[city.id] }));
const atlasOrigin = book.editorial.origin;
let previewId = current.id;
let atlasGlobe = null;

function distanceTo(place) {
  const rad = Math.PI / 180;
  const a = atlasOrigin.lat * rad;
  const b = place.lat * rad;
  const dot = Math.sin(a) * Math.sin(b) + Math.cos(a) * Math.cos(b) * Math.cos((place.lon - atlasOrigin.lon) * rad);
  return Math.round(6371 * Math.acos(Math.max(-1, Math.min(1, dot))) / 10) * 10;
}

function paintAtlas() {
  const map = el('atlas-flat');
  const project = (lon, lat) => [(lon + 1) * 10, (55 - lat) * 10];
  const path = book.land.map(polygon => polygon.map(ring => ring.map(([lon, lat], i) => {
    const [x, y] = project(lon, lat);
    return (i ? 'L' : 'M') + x.toFixed(0) + ',' + y.toFixed(0);
  }).join('') + 'Z').join('')).join('');
  const origin = project(atlasOrigin.lon, atlasOrigin.lat);
  const labels = { prague: [-12, -14], vienna: [-12, 25], budapest: [13, 18], tbilisi: [-10, -13], baku: [11, 21] };
  const grid = [100, 200, 300, 400, 500].map(x => 'M' + x + ',0v360').join('')
    + [60, 160, 260].map(y => 'M0,' + y + 'h560').join('');
  const routes = atlasPlaces.map(place => {
    const [x, y] = project(place.lon, place.lat);
    return '<line data-bearing="' + place.id + '" x1="' + origin[0] + '" y1="' + origin[1] + '" x2="' + x + '" y2="' + y + '"/>';
  }).join('');
  const pins = atlasPlaces.map(place => {
    const [x, y] = project(place.lon, place.lat);
    const [dx, dy] = labels[place.id];
    return '<g data-pin="' + place.id + '"><line x1="' + x + '" y1="' + y + '" x2="' + (x + dx * .7) + '" y2="' + (y + dy * .7) + '"/>'
      + '<circle cx="' + x + '" cy="' + y + '" r="4"/>'
      + '<text x="' + (x + dx) + '" y="' + (y + dy) + '" text-anchor="' + (dx < 0 ? 'end' : 'start') + '">' + h(place.label) + '</text></g>';
  }).join('');
  map.innerHTML = '<svg viewBox="0 0 560 360" aria-hidden="true"><path class="atlas-grid" d="' + grid + '"/>'
    + '<path class="atlas-land" fill-rule="evenodd" d="' + path + '"/><g class="atlas-bearings">' + routes + '</g>'
    + '<g class="atlas-pins">' + pins + '<circle class="atlas-origin-dot" cx="' + origin[0] + '" cy="' + origin[1] + '" r="5"/>'
    + '<text class="atlas-origin-label" x="' + (origin[0] + 13) + '" y="' + (origin[1] + 4) + '">Medina</text></g></svg>';
}

function previewDestination(id, immediate = false) {
  const place = atlasPlaces.find(candidate => candidate.id === id);
  if (!place) return;
  previewId = id;
  for (const marker of el('atlas-flat').querySelectorAll('[data-bearing],[data-pin]')) {
    marker.classList.toggle('is-active', (marker.dataset.bearing || marker.dataset.pin) === id);
  }
  el('atlas-select').value = id;
  el('atlas-distance').textContent = distanceTo(place).toLocaleString('en-US') + ' km direct';
  el('atlas-open-label').textContent = 'Read ' + place.label;
  atlasGlobe?.select(id, immediate);
}

const guideModuleLoads = new Map();
function loadGuideModule(id, name) {
  if (window[name]) return Promise.resolve(window[name]);
  if (guideModuleLoads.has(id)) return guideModuleLoads.get(id);
  const script = document.createElement('script');
  const bundled = el(id);
  if (!bundled.dataset.src) {
    script.textContent = JSON.parse(bundled.textContent);
    document.head.append(script);
    script.remove();
    return Promise.resolve(window[name]);
  }
  const loading = new Promise((resolve, reject) => {
    script.src = bundled.dataset.src;
    script.addEventListener('load', () => { script.remove(); resolve(window[name]); }, {once: true});
    script.addEventListener('error', () => { script.remove(); reject(new Error('Visual asset unavailable')); }, {once: true});
    document.head.append(script);
  }).finally(() => guideModuleLoads.delete(id));
  guideModuleLoads.set(id,loading);
  return loading;
}

function useMap(message = '') {
  atlasGlobe?.dispose();
  atlasGlobe = null;
  el('atlas-visual').classList.remove('has-globe');
  const button = el('atlas-toggle');
  button.setAttribute('aria-pressed', 'false');
  button.textContent = 'View globe';
  el('atlas-feedback').textContent = message;
}
function bootAtlas() {
  paintAtlas();
  el('atlas-select').innerHTML = atlasPlaces.map(place => '<option value="' + place.id + '">' + h(place.label) + '</option>').join('');
  previewDestination(previewId, true);
  el('atlas-select').addEventListener('change', event => previewDestination(event.target.value));
  const button = el('atlas-toggle');
  const panel = el('atlas-visual');
  button.addEventListener('click', async () => {
    if (button.getAttribute('aria-disabled') === 'true') return;
    if (atlasGlobe) {
      useMap();
      return;
    }
    button.setAttribute('aria-disabled', 'true');
    button.textContent = 'Loading globe';
    try {
      const module = await loadGuideModule('globe-code', 'DecemberGlobe');
      const bounds = panel.getBoundingClientRect();
      if (bounds.bottom < -200 || bounds.top > innerHeight + 200) {
        useMap();
        return;
      }
      atlasGlobe = module?.mount(el('atlas-globe'), {
        land: book.land, origin: atlasOrigin, places: atlasPlaces, initialId: previewId,
        onLoss: () => useMap('The globe was interrupted. The map is still available.')
      });
    } catch {
      useMap('This browser is using the static atlas.');
      return;
    } finally {
      button.removeAttribute('aria-disabled');
    }
    if (!atlasGlobe) {
      useMap('This browser is using the static atlas.');
      return;
    }
    panel.classList.add('has-globe');
    button.setAttribute('aria-pressed', 'true');
    button.textContent = 'View map';
    el('atlas-feedback').textContent = '';
    if (panel.getBoundingClientRect().bottom > window.innerHeight) {
      panel.closest('.atlas-panel').scrollIntoView({block: 'nearest'});
    }
  });
  const observer = new IntersectionObserver(entries => {
    if (entries.some(entry => !entry.isIntersecting) && atlasGlobe) useMap();
  }, { rootMargin: '200px' });
  observer.observe(panel);
  window.addEventListener('pagehide', () => useMap());
}

bootGuide();
