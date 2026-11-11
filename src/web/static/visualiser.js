// #/visualiser: the full kaleidoscope. Audio (demo loop, a file, or the microphone) -> analysis per 2048-sample chunk
// -> KaleidoscopeEngine.update; the frame is rendered every animation frame (capped at the FPS control), as the
// desktop widget renders on its own timer while audio updates arrive at about 21.5 per second.
import { route, api, app, esc, animate, onLeave } from './core.js';
import { R } from './pyrandom.js';
import { KaleidoscopeEngine } from './kaleido_engine.js';
import { Renderer, drawFrequencyDisplay } from './kaleido_render.js';
import { AudioFeed } from './audio_input.js';
import { applyToEngine, defaultValues } from './settings.js';
import { buildPanel, setPanelValues } from './panel.js';

const W = 960, H = 600;

route('visualiser', async () => {
  const defaults = await api('/defaults');
  let values = defaultValues(defaults);
  app().innerHTML = `
  <div class="vis-head"><div><p class="kicker">Music-reactive</p><h1 class="glow">Kaleidoscope</h1></div>
    <p class="small mute" id="status" aria-live="polite"></p></div>
  <div class="srcbar">
    <div class="seg" role="group" aria-label="Audio source">
      <button id="src-demo" class="on" aria-pressed="true">Demo loop</button>
      <button id="src-file" aria-pressed="false">Audio file…</button>
      <button id="src-mic" aria-pressed="false">Microphone</button>
    </div>
    <input type="file" id="file" accept="audio/*" hidden aria-label="Choose an audio file">
    <button class="alt" id="sound" aria-pressed="false">Sound on</button>
    <button class="alt" id="pause" aria-pressed="false">Pause</button>
    <button class="alt" id="full">Fullscreen</button>
    <button class="alt" id="reset">Reset</button>
  </div>
  <div class="row small demo-row">
    <div class="ctl" id="level-ctl"><label for="level">Demo level <b id="level-v">0.25</b></label>
      <input type="range" id="level" min="0.02" max="1" step="0.01" value="0.25"></div>
  </div>
  <div class="stage kal" id="stage"><canvas id="kal" width="${W}" height="${H}" role="img"
    aria-label="Kaleidoscope animation reacting to the audio"></canvas></div>
  <canvas id="freq" class="freq" width="${W}" height="150" role="img" aria-label="Frequency spectrum, bands and volume"></canvas>
  <p class="small mute">Keys: <b>F</b> fullscreen, <b>Esc</b> leave it, <b>R</b> reset to the defaults, <b>Space</b> pause.
    Controls mirror the desktop panel; every change re-applies all settings, as on the desktop (particles restart).</p>
  <div id="panel" class="panel"></div>`;

  const canvas = document.getElementById('kal'), freq = document.getElementById('freq');
  const status = document.getElementById('status');
  R.seed((Date.now() % 2147483647) || 1);
  const engine = new KaleidoscopeEngine(W, H);
  const feed = new AudioFeed();
  const renderer = new Renderer(engine, canvas);
  const apply = () => {
    applyToEngine(engine, feed.state, values);
    freq.hidden = !values.freq_display_check;
    freq.style.height = `${values.freq_height_slider}px`;
  };
  apply();
  buildPanel(document.getElementById('panel'), defaults, values, (name, v) => { values[name] = v; apply(); });

  const setStatus = (extra = '') => {
    const what = feed.kind === 'mic' ? 'listening to the microphone' : feed.kind === 'file'
      ? `playing ${esc(feed.label)}${feed.ended ? ' (ended)' : ''}` : `demo loop${feed.sound ? ' with sound' : ' (silent)'}`;
    status.innerHTML = `Source: ${what}${feed.paused ? ' · paused' : ''}. ${extra || feed.rateNote()}`;
    document.getElementById('sound').textContent = feed.sound ? 'Sound off' : 'Sound on';
    document.getElementById('sound').setAttribute('aria-pressed', feed.sound);
    document.getElementById('sound').disabled = feed.kind === 'mic';
    document.getElementById('level-ctl').hidden = feed.kind !== 'demo';
    for (const k of ['demo', 'file', 'mic']) {
      const b = document.getElementById(`src-${k}`);
      b.classList.toggle('on', feed.kind === k); b.setAttribute('aria-pressed', feed.kind === k);
    }
  };
  const fail = e => setStatus(`<span class="err">${esc(e.message || e)}</span>`);

  document.getElementById('src-demo').onclick = () => { feed.useDemo(); setStatus(); };
  document.getElementById('src-file').onclick = () => document.getElementById('file').click();
  document.getElementById('file').onchange = async ev => {
    const f = ev.target.files[0];
    if (!f) return;
    setStatus('Decoding…');
    try { await feed.useFile(f); setStatus(); } catch (e) { fail(new Error(`Could not decode ${f.name}: ${e.message}`)); }
  };
  document.getElementById('src-mic').onclick = async () => {
    if (!navigator.mediaDevices?.getUserMedia) { fail(new Error('This browser offers no microphone access here (it needs https or localhost).')); return; }
    try { await feed.useMic(); setStatus(); } catch (e) { fail(new Error(`Microphone not available: ${e.message}`)); }
  };
  document.getElementById('sound').onclick = () => { if (feed.sound) feed.mute(); else feed.play(); setStatus(); };
  const pause = () => { feed.setPaused(!feed.paused); document.getElementById('pause').setAttribute('aria-pressed', feed.paused); setStatus(); };
  document.getElementById('pause').onclick = pause;
  const stage = document.getElementById('stage');
  const full = () => (document.fullscreenElement ? document.exitFullscreen() : stage.requestFullscreen?.());
  document.getElementById('full').onclick = full;
  const reset = () => { values = defaultValues(defaults); setPanelValues(document.getElementById('panel'), values); apply(); };
  document.getElementById('reset').onclick = reset;
  const level = document.getElementById('level');
  level.oninput = () => { feed.level = +level.value; document.getElementById('level-v').textContent = level.value; if (feed.node) feed.play(); };

  // Fullscreen: the engine takes the screen size (as the desktop widget does when resized), and back afterwards.
  const onFs = () => {
    const fs = document.fullscreenElement === stage;
    const w = fs ? Math.round(stage.clientWidth) : W, h = fs ? Math.round(stage.clientHeight) : H;
    engine.resize(w, h); apply();
  };
  document.addEventListener('fullscreenchange', onFs);
  const onKey = ev => {
    if (ev.target.closest?.('input, select, textarea, button')) return;
    const k = ev.key.toLowerCase();
    if (k === 'f') full(); else if (k === 'r') reset(); else if (k === ' ') { ev.preventDefault(); pause(); } else return;
  };
  document.addEventListener('keydown', onKey);

  setStatus();
  const fctx = freq.getContext('2d');
  let last = 0;
  const stop = animate(t => {
    for (const r of feed.pull()) {
      if (!r) continue;
      engine.update(r.spectrum, r.bands, r.volume, r.raw);
      if (!freq.hidden) drawFrequencyDisplay(fctx, r.spectrum, r.bands, r.volume);
    }
    if (feed.ended && !status.textContent.includes('ended')) setStatus();
    if (feed.paused || t - last < 1000 / values.fps_spin - 2) return;
    last = t;
    renderer.render();
  });
  onLeave(() => {
    stop(); feed.stopNodes();
    document.removeEventListener('keydown', onKey); document.removeEventListener('fullscreenchange', onFs);
  });
});
