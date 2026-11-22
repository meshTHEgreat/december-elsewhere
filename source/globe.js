import {
  AmbientLight, BufferGeometry, CanvasTexture, Color, DirectionalLight, Group, Line, LineBasicMaterial,
  Mesh, MeshLambertMaterial, PerspectiveCamera, Scene, SphereGeometry, SRGBColorSpace, Vector3, WebGLRenderer
} from 'three';

const rad = Math.PI / 180;
const vector = ({ lat, lon }) => new Vector3(
  Math.cos(lat * rad) * Math.cos(lon * rad),
  Math.sin(lat * rad),
  -Math.cos(lat * rad) * Math.sin(lon * rad)
);

function makeTexture(land) {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 512;
  const ink = canvas.getContext('2d');
  ink.fillStyle = '#182d29';
  ink.fillRect(0, 0, 1024, 512);
  ink.fillStyle = '#849181';
  for (const polygon of land) {
    ink.beginPath();
    for (const ring of polygon) {
      let previous = ring[0][0];
      const unwrapped = ring.map(([lon, lat]) => {
        const next = lon + 360 * Math.round((previous - lon) / 360);
        previous = next;
        return [next, lat];
      });
      const first = unwrapped[0][0];
      const last = unwrapped.at(-1)[0];
      if (Math.abs(last - first) > 180) {
        // A ring that travels all the way around a pole closes at that pole.
        const pole = unwrapped[0][1] < 0 ? -90 : 90;
        unwrapped.push([last, pole], [first, pole]);
      }
      const longitudes = unwrapped.map(([lon]) => lon);
      const start = Math.ceil((-180 - Math.max(...longitudes)) / 360);
      const end = Math.floor((180 - Math.min(...longitudes)) / 360);
      for (let wrap = start; wrap <= end; wrap++) {
        unwrapped.forEach(([lon, lat], index) => {
          const x = (lon + wrap * 360 + 180) * 1024 / 360;
          const y = (90 - lat) * 512 / 180;
          if (index === 0) ink.moveTo(x, y);
          else ink.lineTo(x, y);
        });
        ink.closePath();
      }
    }
    ink.fill('evenodd');
  }
  ink.strokeStyle = '#d5d9c32b';
  ink.beginPath();
  for (let x = 0; x < 1024; x += 1024 / 24) {
    ink.moveTo(x, 0);
    ink.lineTo(x, 512);
  }
  for (let y = 0; y < 512; y += 512 / 12) {
    ink.moveTo(0, y);
    ink.lineTo(1024, y);
  }
  ink.stroke();
  const texture = new CanvasTexture(canvas);
  texture.colorSpace = SRGBColorSpace;
  return texture;
}

export function mount(host, { land, origin, places, initialId, onLoss }) {
  const canvas = document.createElement('canvas');
  canvas.setAttribute('aria-hidden', 'true');
  canvas.className = 'globe-canvas';
  const context = canvas.getContext('webgl2', { alpha: true, antialias: true, powerPreference: 'low-power' });
  if (!context) return null;

  const renderer = new WebGLRenderer({ canvas, context, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.5));
  const scene = new Scene();
  const camera = new PerspectiveCamera(33, 1, 0.1, 12);
  const globe = new Group();
  scene.add(globe, new AmbientLight(0xffe8c1, 1.55));
  const key = new DirectionalLight(0xfff4d7, 1.35);
  key.position.set(2, 3, 1);
  scene.add(key);
  const texture = makeTexture(land);
  globe.add(new Mesh(new SphereGeometry(1, 48, 32), new MeshLambertMaterial({ map: texture })));

  const from = vector(origin);
  const overlay = document.createElement('div');
  overlay.className = 'globe-markers';
  const start = document.createElement('span');
  start.className = 'globe-origin';
  start.textContent = 'MED';
  overlay.append(start);
  const records = places.map(place => {
    const point = vector(place);
    const angle = from.angleTo(point);
    const edge = [];
    for (let i = 0; i <= 40; i++) {
      const t = i / 40;
      edge.push(from.clone().multiplyScalar(Math.sin((1 - t) * angle) / Math.sin(angle))
        .addScaledVector(point, Math.sin(t * angle) / Math.sin(angle)).multiplyScalar(1.012 + Math.sin(Math.PI * t) * .042));
    }
    const line = new Line(new BufferGeometry().setFromPoints(edge), new LineBasicMaterial({ transparent: true }));
    globe.add(line);
    const marker = document.createElement('span');
    marker.className = 'globe-pin';
    marker.setAttribute('aria-hidden', 'true');
    overlay.append(marker);
    return { place, point, marker, line };
  });
  host.append(canvas, overlay);

  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const center = vector({ lat: 36, lon: 30 });
  const position = center.clone();
  const target = center.clone();
  const scratch = new Vector3();
  let frame = 0;
  let disposed = false;

  function placeMarker(marker, point, width, height) {
    scratch.copy(point).multiplyScalar(1.025).project(camera);
    const visible = point.dot(position) > .28 && Math.abs(scratch.x) < 1 && Math.abs(scratch.y) < 1;
    marker.hidden = !visible;
    if (visible) {
      marker.style.setProperty('--x', ((scratch.x + 1) * width / 2).toFixed(1) + 'px');
      marker.style.setProperty('--y', ((1 - scratch.y) * height / 2).toFixed(1) + 'px');
    }
  }
  function draw() {
    const width = host.clientWidth;
    const height = host.clientHeight;
    if (!width || !height || disposed) return;
    camera.position.copy(position).multiplyScalar(width / height > 1.2 ? 3.85 : 4.2);
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
    placeMarker(start, from, width, height);
    for (const { marker, point } of records) placeMarker(marker, point, width, height);
  }
  function resize() {
    const width = host.clientWidth;
    const height = host.clientHeight;
    if (!width || !height || disposed) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    draw();
  }
  const observer = new ResizeObserver(resize);
  observer.observe(host);
  const fromCamera = position.clone();
  function select(id, immediate = false) {
    if (disposed) return;
    const active = records.find(record => record.place.id === id);
    for (const record of records) {
      const selected = record === active;
      record.marker.classList.toggle('is-active', selected);
      record.marker.textContent = selected ? record.place.label : '';
      record.line.material.color.set(selected ? '#ffe4a3' : '#c3ceaa');
      record.line.material.opacity = selected ? 1 : .38;
      record.line.renderOrder = selected ? 1 : 0;
    }
    target.copy(center);
    if (active) target.lerp(active.point, .52).normalize();
    cancelAnimationFrame(frame);
    if (immediate || reduced.matches || document.hidden) {
      position.copy(target);
      draw();
      return;
    }
    fromCamera.copy(position);
    const startTime = performance.now();
    function animate(now) {
      const fraction = Math.min((now - startTime) / 620, 1);
      position.copy(fromCamera).lerp(target, 1 - (1 - fraction) ** 3).normalize();
      draw();
      if (fraction < 1 && !document.hidden) frame = requestAnimationFrame(animate);
    }
    frame = requestAnimationFrame(animate);
  }
  function stopOnPreference() {
    cancelAnimationFrame(frame);
    position.copy(target);
    draw();
  }
  function dispose(contextLost = false) {
    if (disposed) return;
    disposed = true;
    cancelAnimationFrame(frame);
    observer.disconnect();
    reduced.removeEventListener('change', stopOnPreference);
    document.removeEventListener('visibilitychange', stopOnPreference);
    canvas.removeEventListener('webglcontextlost', handleLoss);
    globe.traverse(object => {
      object.geometry?.dispose();
      object.material?.dispose();
    });
    texture.dispose();
    renderer.dispose();
    if (!contextLost) renderer.forceContextLoss();
    canvas.remove();
    overlay.remove();
  }
  function handleLoss(event) {
    event.preventDefault();
    dispose(true);
    onLoss();
  }
  canvas.addEventListener('webglcontextlost', handleLoss);
  reduced.addEventListener('change', stopOnPreference);
  document.addEventListener('visibilitychange', stopOnPreference);
  resize();
  select(initialId, true);
  return { select, dispose };
}
