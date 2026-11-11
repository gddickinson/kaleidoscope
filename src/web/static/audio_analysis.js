// Port of src/core/audio_analysis.py (the per-chunk analysis of the desktop AudioProcessor): one chunk of int16
// sample values -> spectrum (99 FFT bins), bands [bass, mids, highs], smoothed RMS volume, raw audio in [-1, 1].
import { rfftAbs } from './fft.js';

export const CHUNK_SIZE = 2048;
export const RATE = 44100;

export class AnalysisState {
  constructor(sensitivity = 1.0, smoothing = 0.3, chunkSize = CHUNK_SIZE) {
    this.chunk_size = chunkSize;
    this.sensitivity = sensitivity;
    this.smoothing = smoothing;
    this.fft_data = new Float64Array(chunkSize / 2 + 1);
    this.prev_fft = new Float64Array(chunkSize / 2 + 1);
    this.rms_volume = 0;
    this.prev_volume = 0;
    this.last_raw_audio = new Float64Array(chunkSize);
  }
  set_sensitivity(v) { this.sensitivity = v; }
  set_smoothing(v) { this.smoothing = v; }
}

const nanToNum = v => (Number.isNaN(v) ? 0 : v === Infinity ? Number.MAX_VALUE : v === -Infinity ? -Number.MAX_VALUE : v);
const mean = (a, lo, hi) => { let s = 0; for (let i = lo; i < hi; i++) s += a[i]; return s / (hi - lo); };

export function analyzeChunk(state, data) {
  const n = data.length;
  if (n > 0) state.last_raw_audio = Float64Array.from(data, v => v / 32768.0);
  let any = false;
  for (let i = 0; i < n && !any; i++) any = data[i] !== 0;
  if (n > 0 && any) {
    let sq = 0;
    for (let i = 0; i < n; i++) sq += data[i] * data[i];
    state.rms_volume = Math.sqrt(sq / n) / 32768.0 * state.sensitivity;
    state.rms_volume = state.prev_volume * state.smoothing + state.rms_volume * (1 - state.smoothing);
    state.prev_volume = state.rms_volume;
  } else {
    state.rms_volume = state.prev_volume;
  }
  if (n === 0) return null;

  const fft = rfftAbs(state.last_raw_audio);
  if (fft.length !== state.prev_fft.length) state.prev_fft = new Float64Array(fft.length);
  const s = state.smoothing, raw = new Float64Array(fft.length);
  for (let k = 0; k < fft.length; k++) raw[k] = state.prev_fft[k] * s + fft[k] * (1 - s) * state.sensitivity;
  state.prev_fft = raw.slice();
  const out = raw.map(nanToNum);
  state.fft_data = out;

  const bands = [mean(out, 1, 20), mean(out, 20, 100), mean(out, 100, out.length)].map(nanToNum);
  const spectrum = Array.from(out.subarray(1, 100), nanToNum);
  const volume = Number.isNaN(state.rms_volume) ? 0.0 : state.rms_volume;
  return { spectrum, bands, volume, raw: state.last_raw_audio };
}

// Float samples (Web Audio, -1..1) to the int16 values a microphone stream would deliver.
export function toInt16(floats) {
  const out = new Float64Array(floats.length);
  for (let i = 0; i < floats.length; i++) out[i] = Math.max(-32768, Math.min(32767, Math.round(floats[i] * 32767)));
  return out;
}
