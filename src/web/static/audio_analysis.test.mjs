// node audio_analysis.test.mjs: the JS FFT/analysis and demo signal against tests/fixtures/audio_reference.json
// (written by scripts/make_fixtures.py from the real src/core/audio_analysis.py and src/web/demo_signal.py).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runAudioCase, compare, demoHead } from './reference.js';

const ref = JSON.parse(readFileSync(new URL('../../../tests/fixtures/audio_reference.json', import.meta.url)));
const js = runAudioCase(ref);

const r = compare(ref.rows, js.rows, 1e-9);
assert.equal(r.bad.length, 0, r.bad.slice(0, 5).join('\n'));
console.log(`ok   analysis: ${ref.rows.length} chunks, ${r.n} values, max rel diff ${r.maxRel.toExponential(1)}`);
assert.deepEqual(js.mulberry32_seed1, ref.mulberry32_seed1);
console.log('ok   mulberry32 stream identical');

const head = demoHead(ref.demo_head.length);
let maxd = 0;
head.forEach((v, i) => { maxd = Math.max(maxd, Math.abs(v - ref.demo_head[i])); });
assert.ok(maxd <= 1, `demo signal differs by ${maxd}`);
console.log(`ok   demo signal: ${head.length} samples, max diff ${maxd} (int16 units)`);
