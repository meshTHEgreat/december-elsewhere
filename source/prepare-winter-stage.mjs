// npm install --no-save --package-lock=false react@18.3.1 react-dom@18.3.1 esbuild@0.28.2
// node source/prepare-winter-stage.mjs <stageshow-skill-folder> [path-to-node_modules]
import { copyFileSync, readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const [skillFolder, packageFolder = 'node_modules'] = process.argv.slice(2);
if (!skillFolder) throw new Error('Pass the installed Stageshow skill folder.');
const deps = resolve(packageFolder);
const require = createRequire(resolve(deps, 'package.json'));
const { build } = require('esbuild');
const file = path => fileURLToPath(new URL(path, import.meta.url));

await build({
  entryPoints: [file('./winter-stage.tsx')],
  outfile: file('./vendor/winter-stage.js'),
  alias: { '@winter/stageshow': resolve(skillFolder, 'kit/stage.tsx') },
  nodePaths: [deps],
  globalName: 'DecemberWinterStage',
  bundle: true,
  format: 'iife',
  jsx: 'automatic',
  minify: true,
  target: 'es2020',
  define: { 'process.env.NODE_ENV': '"production"' },
  legalComments: 'inline',
});
const stageLicense = readFileSync(resolve(skillFolder, 'LICENSE'), 'utf8').replaceAll('\r\n', '\n');
writeFileSync(file('./vendor/STAGESHOW-LICENSE.txt'), stageLicense);
copyFileSync(resolve(deps, 'react/LICENSE'), file('./vendor/REACT-LICENSE.txt'));
