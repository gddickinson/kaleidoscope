// node kaleido_engine.test.mjs: the JS engine (particles, beat/pulse, waveform, wireframes, particle effects, panel
// mapping) against seeded runs of the real Python KaleidoscopeEngine in tests/fixtures/engine_*.json.
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { runEngineCase, compare } from './reference.js';

const fix = new URL('../../../tests/fixtures/', import.meta.url);
const defaults = JSON.parse(readFileSync(new URL('../desktop_defaults.json', import.meta.url)));
const files = readdirSync(fix).filter(f => f.startsWith('engine_') && f.endsWith('.json')).sort();
assert.ok(files.length >= 2, 'engine fixtures missing');

for (const f of files) {
  const ref = JSON.parse(readFileSync(new URL(f, fix)));
  const js = runEngineCase(ref, defaults);
  const { case: _c, inputs: _i, ...py } = ref;
  const r = compare(py, js, 1e-7);
  assert.equal(r.bad.length, 0, `${f}:\n${r.bad.slice(0, 8).join('\n')}`);
  const beats = ref.trace.reduce((a, t) => a + t[1], 0);
  console.log(`ok   ${ref.case.name}: ${ref.trace.length} steps, ${beats} beats, ${r.n} values, max rel diff ${r.maxRel.toExponential(1)}`);
}
