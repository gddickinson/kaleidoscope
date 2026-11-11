// Built-in demo music, a line-by-line port of src/web/demo_signal.py: 120 BPM, Am - F - C - G, one bar per chord,
// with kick, bass, pad, arpeggio and off-beat hats (noise from mulberry32). Deterministic for a given seed.
import { rng } from './core.js';

export const RATE = 44100;
export const BPM = 120;
export const CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]];
export const LEVEL = 0.25;
export const LOOP_SECONDS = 4 * CHORDS.length * 60 / BPM; // the progression repeats every 8 s

export const midiHz = m => 440.0 * 2.0 ** ((m - 69) / 12.0);

export function demoFloat(n, rate = RATE, seed = 1) {
  const noise = rng(seed), beat = 60.0 / BPM, out = new Float64Array(n);
  let prevNoise = 0.0;
  for (let k = 0; k < n; k++) {
    const t = k / rate;
    const chord = CHORDS[Math.trunc(t / (4 * beat)) % CHORDS.length];
    const tb = t % beat, t8 = t % (beat / 2), t16 = t % (beat / 4);
    const step16 = Math.trunc(t / (beat / 4)) % 4;
    const ph = 2 * Math.PI * (50 * tb + (70 / 18.0) * (1 - Math.exp(-18 * tb)));
    let x = 0.9 * Math.exp(-tb * 18) * Math.sin(ph);
    const f0 = midiHz(chord[0] - 24);
    let bass = 0.0;
    for (const h of [1, 2, 3]) bass += Math.sin(2 * Math.PI * f0 * h * t) / h;
    x += 0.25 * Math.exp(-t8 * 6) * bass;
    const trem = 0.75 + 0.25 * Math.sin(2 * Math.PI * 0.5 * t);
    for (const m of chord) x += 0.06 * trem * Math.sin(2 * Math.PI * midiHz(m) * t);
    const note = chord[step16 % 3] + 12;
    x += 0.12 * Math.exp(-t16 * 10) * Math.sin(2 * Math.PI * midiHz(note) * t);
    const r = noise() * 2 - 1;
    if (Math.trunc(t / (beat / 2)) % 2 === 1) x += 0.15 * Math.exp(-t8 * 60) * (r - prevNoise);
    prevNoise = r;
    out[k] = x;
  }
  return out;
}

// int16 sample values (like a microphone stream) at the given level; numpy rounds half to even, so a value exactly
// halfway may differ by one from the Python version.
export function demoInt16(n, rate = RATE, seed = 1, level = LEVEL) {
  const x = demoFloat(n, rate, seed), out = new Float64Array(n);
  for (let i = 0; i < n; i++) out[i] = Math.max(-32768, Math.min(32767, Math.round(x[i] * level * 32767)));
  return out;
}
