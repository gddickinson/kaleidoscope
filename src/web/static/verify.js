// #/verify: the JS port against the Python code. Replays the reference runs (computed by src/web/reference.py with
// the real analyze_chunk and KaleidoscopeEngine) in the browser and compares every value; with the local server, an
// audio file of your own can be analysed by both.
import { route, api, app, esc, list, isStatic, needsServer } from './core.js';
import { runAudioCase, runEngineCase, compare } from './reference.js';
import { AnalysisState, analyzeChunk, CHUNK_SIZE, toInt16 } from './audio_analysis.js';
import { decodeFile } from './audio_input.js';

const row = (name, r, what) => `<tr><td>${esc(name)}</td><td>${esc(what)}</td><td class="mono">${r.n.toLocaleString('en')}</td>
  <td class="mono">${r.maxRel.toExponential(1)}</td><td class="${r.bad.length ? 'err' : 'ok'}">${r.bad.length ? `${r.bad.length} differ` : 'match'}</td></tr>`;

route('verify', async () => {
  const [index, defaults, audio] = await Promise.all([api('/reference'), api('/defaults'), api('/reference/audio')]);
  app().innerHTML = `<p class="kicker">Verify</p><h1 class="glow">Browser engine vs Python</h1>
  <p class="lead">The reference runs below were computed by the repository's Python code (<code>src/web/reference.py</code>):
  the demo loop analysed by the real <code>analyze_chunk</code>, and a real <code>KaleidoscopeEngine</code> configured through the
  real desktop <code>ControlPanel</code>, with the <code>random</code> module swapped for a seeded mulberry32 stream. Your browser
  now repeats them with the JavaScript port and compares every number (tolerance: relative 10⁻⁹ for the analysis, 10⁻⁷ for the engine).</p>
  <div class="scroll"><table><tr><th>Run</th><th>What is compared</th><th>Values</th><th>Max rel. diff</th><th>Result</th></tr>
  <tbody id="rows"><tr><td colspan="5" class="mute">Running…</td></tr></tbody></table></div>
  <div id="details"></div>
  <h2>Your own audio</h2>
  <p>Pick an audio file: the browser decodes it to 44.1 kHz int16 chunks, analyses the first 64 chunks (about 3 s) in JS,
  sends the same samples to the Python <code>analyze_chunk</code> and compares.</p>
  ${isStatic() ? needsServer('Analysing your own audio with Python') : `<label for="own">Audio file</label><input type="file" id="own" accept="audio/*"><div id="ownout"></div>`}`;

  const rows = [], details = [];
  const js = runAudioCase(audio);
  const ra = compare(audio.rows, js.rows, 1e-9);
  rows.push(row('audio analysis', ra, `${audio.case.chunks} chunks of the demo loop: spectrum, bands, volume, FFT sums`));
  for (const name of index.engine) {
    const ref = await api(`/reference/engine/${name}`);
    const out = runEngineCase(ref, defaults);
    const { case: c, inputs: _i, ...py } = ref;
    const r = compare(py, out, 1e-7);
    const beats = ref.trace.reduce((a, t) => a + t[1], 0);
    rows.push(row(`engine, ${name}`, r, `${ref.trace.length} updates, ${beats} beats, ${c.width}×${c.height}, seed ${c.seed}`));
    details.push(`<h3>${esc(name)}</h3><p class="small">Settings changed from the desktop defaults:
      ${Object.keys(c.settings).length ? list(Object.entries(c.settings), ([k, v]) => `<span class="tag">${esc(k)} = ${esc(v)}</span>`) : 'none'}.
      Compared every ${c.snap_every} updates: rotation and 3D angles, beat and pulse state, every particle, the waveform ring,
      wireframe rotation/colour/morphing, and each particle effect; plus the rotation, beat, pulse and effect count after every update.</p>
      ${r.bad.length ? `<pre>${esc(r.bad.slice(0, 10).join('\n'))}</pre>` : ''}`);
  }
  document.getElementById('rows').innerHTML = rows.join('');
  document.getElementById('details').innerHTML = details.join('');
  const own = document.getElementById('own');
  if (own) own.onchange = () => ownAudio(own.files[0]);
});

async function ownAudio(file) {
  const out = document.getElementById('ownout');
  if (!file) return;
  out.innerHTML = '<p class="mute">Decoding…</p>';
  try {
    const mono = await decodeFile(file);
    const n = Math.min(64, Math.floor(mono.length / CHUNK_SIZE));
    const samples = Array.from(toInt16(mono.subarray(0, n * CHUNK_SIZE)));
    const py = await api('/analyze', { body: { samples, sensitivity: 1.0, smoothing: 0.3 } });
    const st = new AnalysisState(1.0, 0.3), mine = [];
    for (let i = 0; i < n; i++) {
      const r = analyzeChunk(st, samples.slice(i * CHUNK_SIZE, (i + 1) * CHUNK_SIZE));
      mine.push({ spectrum: r.spectrum, bands: r.bands, volume: r.volume });
    }
    const cmp = compare(py.rows, mine, 1e-9);
    const meanVol = py.rows.reduce((a, r) => a + r.volume, 0) / py.rows.length;
    out.innerHTML = `<div class="scroll"><table><tr><th>Chunks</th><th>Values</th><th>Max rel. diff</th><th>Result</th><th>Mean volume (Python)</th></tr>
      <tr><td class="mono">${n}</td><td class="mono">${cmp.n.toLocaleString('en')}</td><td class="mono">${cmp.maxRel.toExponential(1)}</td>
      <td class="${cmp.bad.length ? 'err' : 'ok'}">${cmp.bad.length ? `${cmp.bad.length} differ` : 'match'}</td>
      <td class="mono">${meanVol.toFixed(4)}</td></tr></table></div>
      <p class="small mute">First ${n} chunks of ${esc(file.name)}.</p>`;
  } catch (e) {
    out.innerHTML = `<p class="err">${esc(e.message)}</p>`;
  }
}
