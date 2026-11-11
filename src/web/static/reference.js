// Replays the Python reference runs (src/web/reference.py) in JS and compares the results value by value.
// Used by the node tests (*.test.mjs) and the Verify page.
import { R } from './pyrandom.js';
import { rng } from './core.js';
import { AnalysisState, analyzeChunk, CHUNK_SIZE } from './audio_analysis.js';
import { demoInt16 } from './demo_signal.js';
import { KaleidoscopeEngine } from './kaleido_engine.js';
import { applyToEngine, defaultValues } from './settings.js';

const name = o => o.constructor.name;
const color = c => [c.r, c.g, c.b, c.a];

export function snapshot(e, step) { // same fields as reference.snapshot()
  const wf = e.circular_waveform, wm = e.wireframe_manager, em = e.effects_manager;
  return {
    step, rotation: e.rotation, rot3d: [e.rotation_3d_x, e.rotation_3d_y, e.rotation_3d_z],
    is_beat: e.is_beat, beat_cooldown: e.beat_cooldown, current_pulse: e.current_pulse, target_pulse: e.target_pulse,
    particles: e.particles.map(p => [p.x, p.y, p.z, p.angle, p.current_size, p.trail.length]),
    waveform: { rotation: wf.rotation, amplitude: wf.amplitude, smoothed: Array.from(wf.smoothed_data) },
    wireframe: {
      current: name(wm.current_shape), beat_counter: wm.beat_counter, last_beat_time: wm.last_beat_time, rainbow_offset: wm.rainbow_offset,
      shapes: wm.shapes.map(s => ({ type: name(s), rot: [s.rotation_x, s.rotation_y, s.rotation_z], pulse_size: s.pulse_size,
        color: color(s.base_color), thickness: s.edge_thickness, size: s.size, morph_progress: s.morph_progress,
        n_vertices: s.vertices.length, morph_target: s.morph_target ? name(s.morph_target) : null })),
    },
    effects: { beat_cooldown: em.beat_cooldown, list: em.effects.map(x => ({ type: name(x), lifetime: x.lifetime,
      max_lifetime: x.max_lifetime, active: x.active, n: x.particles.length,
      particles: x.particles.slice(0, 4).map(p => [p.x, p.y, p.alpha, p.size]) })) },
  };
}

// Build an engine the way reference.run_case does: settings through the panel mapping, then reseed and re-create particles.
export function makeEngine(c, defaults) {
  R.seed(0);
  const engine = new KaleidoscopeEngine(c.width, c.height);
  const audio = new AnalysisState();
  applyToEngine(engine, audio, { ...defaultValues(defaults), ...c.settings });
  R.seed(c.seed);
  engine.init_particles();
  return { engine, audio };
}

export function runEngineCase(ref, defaults) {
  const c = ref.case, { engine, audio } = makeEngine(c, defaults);
  const trace = [], snapshots = [];
  ref.inputs.forEach((f, k) => {
    const i = k + 1;
    engine.update(f.spectrum, f.bands, f.volume);
    trace.push([engine.rotation, engine.is_beat ? 1 : 0, engine.current_pulse, engine.effects_manager.effects.length]);
    if (i % c.snap_every === 0) snapshots.push(snapshot(engine, i));
  });
  return { sensitivity: audio.sensitivity, smoothing: audio.smoothing, trace, snapshots, next_random: R.random() };
}

export function runAudioCase(ref) {
  const out = { rows: [] }, c = ref.case, st = new AnalysisState(c.sensitivity, c.smoothing);
  for (let i = 0; i < c.chunks; i++) {
    const r = analyzeChunk(st, ref.samples.slice(i * CHUNK_SIZE, (i + 1) * CHUNK_SIZE));
    out.rows.push({ spectrum: r.spectrum, bands: r.bands, volume: r.volume,
      fft_sum: st.fft_data.reduce((a, b) => a + b, 0), raw_sum: r.raw.reduce((a, b) => a + b, 0) });
  }
  const m = rng(1);
  out.mulberry32_seed1 = [m(), m(), m(), m(), m()];
  return out;
}

export const demoHead = n => Array.from(demoInt16(n));

// Recursive comparison. Numbers: |a - b| <= tol * max(1, |a|); everything else must be equal.
export function compare(py, js, tol = 1e-9, path = '', acc = { n: 0, maxRel: 0, bad: [] }) {
  if (typeof py === 'number' && typeof js === 'number') {
    acc.n += 1;
    const rel = Math.abs(py - js) / Math.max(1, Math.abs(py));
    if (rel > acc.maxRel) acc.maxRel = rel;
    if (!(rel <= tol)) acc.bad.push(`${path}: python ${py} js ${js}`);
  } else if (Array.isArray(py) && Array.isArray(js)) {
    if (py.length !== js.length) acc.bad.push(`${path}: length ${py.length} vs ${js.length}`);
    else py.forEach((v, i) => compare(v, js[i], tol, `${path}[${i}]`, acc));
  } else if (py && js && typeof py === 'object' && typeof js === 'object') {
    for (const k of Object.keys(py)) compare(py[k], js[k], tol, path ? `${path}.${k}` : k, acc);
  } else if (py !== js) {
    acc.n += 1;
    acc.bad.push(`${path}: python ${JSON.stringify(py)} js ${JSON.stringify(js)}`);
  }
  return acc;
}
