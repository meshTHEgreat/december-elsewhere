// npm install --no-save --package-lock=false three@0.183.2 esbuild@0.28.2 world-atlas@2.0.2 topojson-client@3.1.0
// node source/prepare-globe.mjs [path-to-node_modules]
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { readFileSync, writeFileSync } from 'node:fs';

const require = createRequire(resolve(process.argv[2] || 'node_modules', 'package.json'));
const { build } = require('esbuild');
const { feature } = require('topojson-client');
const vendor = new URL('./vendor/', import.meta.url);
const topology = require('world-atlas/land-110m.json');
const shapes = feature(topology, topology.objects.land).features;
const land = shapes.flatMap(item => item.geometry.coordinates)
  .map(polygon => polygon.map(ring => ring.map(([x, y]) => [Math.round(x * 10) / 10, Math.round(y * 10) / 10])));
writeFileSync(new URL('land.json', vendor), JSON.stringify(land) + '\n');
writeFileSync(new URL('THREE-LICENSE.txt', vendor), readFileSync(require.resolve('three').replace(/build[\\/][^\\/]+$/, 'LICENSE')));
await build({
  entryPoints: [fileURLToPath(new URL('./globe.js', import.meta.url))],
  nodePaths: [resolve(process.argv[2] || 'node_modules')],
  outfile: fileURLToPath(new URL('globe.js', vendor)),
  bundle: true,
  minify: true,
  format: 'iife',
  globalName: 'DecemberGlobe',
  target: 'es2020',
  legalComments: 'inline'
});
