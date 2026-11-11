// Audio input for the browser visualiser: the built-in demo loop, an audio file the user picks, or the microphone
// (only after an explicit click). Whatever the source, it is cut into consecutive 2048-sample chunks at 44.1 kHz, the
// chunk size and rate of the desktop AudioProcessor, converted to int16 values and analysed by audio_analysis.js,
// so the engine receives one update per chunk (about 21.5 per second) as on the desktop.
import { AnalysisState, analyzeChunk, CHUNK_SIZE, RATE, toInt16 } from './audio_analysis.js';
import { demoFloat, LOOP_SECONDS } from './demo_signal.js';

let actx = null;
// One AudioContext at 44.1 kHz (created on a user gesture); falls back to the device rate if that is refused.
export function audioContext() {
  if (!actx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    try { actx = new AC({ sampleRate: RATE }); } catch { actx = new AC(); }
  }
  return actx;
}

let demoCache = null;
const demoLoop = () => (demoCache ||= demoFloat(Math.round(LOOP_SECONDS * RATE)));

// Decode a file to mono float samples at 44.1 kHz.
export async function decodeFile(file) {
  const ctx = audioContext();
  const buf = await ctx.decodeAudioData(await file.arrayBuffer());
  let mono = new Float32Array(buf.length);
  for (let c = 0; c < buf.numberOfChannels; c++) {
    const d = buf.getChannelData(c);
    for (let i = 0; i < d.length; i++) mono[i] += d[i] / buf.numberOfChannels;
  }
  if (buf.sampleRate !== RATE) {
    const off = new OfflineAudioContext(1, Math.ceil(buf.length * RATE / buf.sampleRate), RATE);
    const b = off.createBuffer(1, buf.length, buf.sampleRate);
    b.copyToChannel(mono, 0);
    const src = off.createBufferSource(); src.buffer = b; src.connect(off.destination); src.start();
    mono = (await off.startRendering()).getChannelData(0);
  }
  return mono;
}

export class AudioFeed {
  constructor() {
    this.state = new AnalysisState();
    this.level = 0.25;        // demo loop level (fraction of full scale)
    this.kind = 'demo';
    this.data = demoLoop(); this.loop = true; this.label = 'Demo loop';
    this.node = null; this.gain = null; this.mic = null; this.sound = false;
    this.next = 0; this.offset = 0; this.t0 = performance.now(); this.paused = false; this.ended = false;
  }

  // Current playback position in samples.
  position() {
    if (this.kind === 'mic') return actx.currentTime * actx.sampleRate;
    if (this.node) return (actx.currentTime - this.startAt) * RATE;
    return this.offset + (this.paused ? 0 : (performance.now() - this.t0) / 1000 * RATE);
  }

  // Analysed chunks that became due since the last call (at most 6; a hidden tab skips ahead).
  pull() {
    if (this.paused || this.ended) return [];
    const due = Math.floor(this.position() / CHUNK_SIZE);
    if (due < this.next) return [];
    if (this.kind === 'mic') { this.next = due + 1; return [this.analyse(this.micChunk())]; }
    if (due - this.next > 6) this.next = due - 6;
    const out = [];
    for (; this.next <= due; this.next++) {
      const start = this.next * CHUNK_SIZE;
      if (!this.loop && start + CHUNK_SIZE > this.data.length) { this.ended = true; break; }
      const chunk = new Float64Array(CHUNK_SIZE);
      for (let j = 0; j < CHUNK_SIZE; j++) chunk[j] = this.data[(start + j) % this.data.length] * (this.kind === 'demo' ? this.level : 1);
      out.push(this.analyse(toInt16(chunk)));
    }
    return out;
  }

  analyse(int16) { return analyzeChunk(this.state, int16); }

  micChunk() {
    const f = new Float32Array(CHUNK_SIZE);
    this.mic.analyser.getFloatTimeDomainData(f);
    return toInt16(f);
  }

  stopNodes() {
    if (this.node) { try { this.node.stop(); } catch { /* already stopped */ } this.node.disconnect(); this.node = null; }
    if (this.mic) { this.mic.stream.getTracks().forEach(t => t.stop()); this.mic.source.disconnect(); this.mic = null; }
  }

  reset(kind, data, label, loop) {
    this.stopNodes();
    Object.assign(this, { kind, data, label, loop, next: 0, offset: 0, t0: performance.now(), ended: false, paused: false });
  }

  useDemo() { this.reset('demo', demoLoop(), 'Demo loop', true); if (this.sound) this.play(); }

  async useFile(file) {
    const data = await decodeFile(file);
    this.reset('file', data, file.name, false);
    this.sound = true;
    this.play();
  }

  async useMic() {
    const ctx = audioContext();
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.reset('mic', null, 'Microphone', false);
    const source = ctx.createMediaStreamSource(stream), analyser = ctx.createAnalyser();
    analyser.fftSize = CHUNK_SIZE;
    source.connect(analyser); // not connected to the speakers
    this.mic = { stream, source, analyser };
    await ctx.resume();
    this.next = Math.floor(this.position() / CHUNK_SIZE);
  }

  // Play the current buffer source through the speakers from the current position (demo: loop).
  play() {
    if (this.kind === 'mic') return;
    const ctx = audioContext(), pos = this.position();
    if (this.node) { this.node.stop(); this.node.disconnect(); }
    const buf = ctx.createBuffer(1, this.data.length, RATE);
    const scaled = Float32Array.from(this.data, v => v * (this.kind === 'demo' ? this.level : 1));
    buf.copyToChannel(scaled, 0);
    const node = ctx.createBufferSource();
    node.buffer = buf; node.loop = this.loop;
    this.gain ||= ctx.createGain();
    this.gain.connect(ctx.destination);
    node.connect(this.gain);
    const at = (pos % this.data.length) / RATE;
    node.start(0, at);
    this.startAt = ctx.currentTime - pos / RATE;
    this.node = node;
    this.sound = true;
    ctx.resume();
  }

  mute() {
    if (!this.node) return;
    this.offset = this.position(); this.t0 = performance.now();
    this.node.stop(); this.node.disconnect(); this.node = null;
    this.sound = false;
  }

  setPaused(p) {
    if (p === this.paused) return;
    if (p) { this.offset = this.position(); if (actx && this.node) actx.suspend(); }
    else { this.t0 = performance.now(); if (actx && this.node) actx.resume(); }
    this.paused = p;
  }

  rateNote() {
    return this.kind === 'mic' && actx && actx.sampleRate !== RATE
      ? `The browser runs the microphone at ${actx.sampleRate} Hz, not 44,100 Hz, so FFT bins are slightly wider than on the desktop.` : '';
  }
}
