// About: how the audio becomes pictures (from the code), what the web version covers, how to run it, credits.
import { route, app, api } from './core.js';

route('about', async () => {
  const info = await api('/info');
  app().innerHTML = `<p class="kicker">About</p><h1 class="glow">How the kaleidoscope works</h1>
  <p class="lead">${info.summary} This site is the web version of
  <a href="https://github.com/gddickinson/kaleidoscope">kaleidoscope</a>: the engine, the audio analysis and the control panel
  ported to JavaScript and checked against the Python code.</p>

  <h2>From sound to features</h2>
  <p>Audio arrives in chunks of ${info.chunk_size} samples at ${info.rate.toLocaleString('en')} Hz, about
  ${info.updates_per_second.toFixed(1)} chunks a second (<code>src/core/audio_analysis.py</code>). For each chunk:</p>
  <ul>
    <li><b>volume</b>: the RMS of the samples / 32768 × sensitivity, smoothed with the previous value
      (<span class="mono">v = v<sub>prev</sub>·s + v·(1 − s)</span>, s = smoothing);</li>
    <li><b>spectrum</b>: |FFT| of the samples, smoothed the same way and multiplied by the sensitivity; FFT bins 1–99
      (about 21 Hz to 2.1 kHz) drive the colours and the waveform ring;</li>
    <li><b>bands</b>: the mean of bins 1–19 (bass, up to ~400 Hz), 20–99 (mids, to ~2.1 kHz) and 100 and above (highs).</li>
  </ul>

  <h2>From features to pictures</h2>
  <ul>
    <li><b>Rotation</b> advances by rotation speed × 0.01 plus bass × 0.1 per update; with 3D on, the mids and highs tilt the scene.</li>
    <li><b>Beats</b>: a beat is bass above 1.5× its average over the last 30 updates and rising, at most one every 10 updates.
      A beat sets a <b>pulse</b> (up to 2× size) that grows with the attack and falls back with the decay.</li>
    <li><b>Particles</b> (default 100) circle and drift with the mids, leave fading trails, grow with volume and pulse, and are
      drawn as circles, squares, triangles or stars, coloured by the spectrum, a solid colour or a gradient.</li>
    <li><b>Symmetry</b>: the particle layer is repeated around the centre: <i>radial</i> (N rotated copies),
      <i>mirror</i> (four reflections) or <i>spiral</i> (eight rotated, shrinking copies).</li>
    <li><b>Waveform ring</b>: 128 spectrum bars around the centre with an optional reflection.</li>
    <li><b>Wireframes</b>: ${info.wireframe_shapes.length} solids (${info.wireframe_shapes.join(', ')}) rotated by bass, mids and highs,
      coloured by the bands, morphing between shapes on beats or over time.</li>
    <li><b>Particle effects</b>: spark bursts, flares, fireworks and mist clouds, spawned on loud beats and at random.</li>
    <li>Optional <b>blur</b> and a sine-wave <b>distortion</b> of the finished frame.</li>
  </ul>

  <h2>What the web version covers</h2>
  <p>A line-by-line JavaScript port of the analysis, <code>KaleidoscopeEngine</code>, the particles, waveform ring, wireframes,
  particle effects and the desktop panel's settings mapping, drawn on a canvas. The control panel is built from the desktop
  <code>ControlPanel</code> itself (${info.controls_ported} of its ${info.controls} controls; labels, ranges and defaults read from
  the Qt widgets). The <a href="#/verify">Verify</a> page replays seeded runs of the Python engine in your browser and compares
  every number. Not ported: the particle tunnel and the four experimental effects (all off by default on the desktop) and
  multi-monitor fullscreen. Web additions: the built-in demo loop, audio files, and the keys F (fullscreen), R (reset) and Space (pause).
  Drawing uses the canvas rather than QPainter, so antialiasing and blur look slightly different.</p>
  <p class="callout">Porting turned up two bugs in the desktop code, now fixed in the repository: the volume of loud input
  overflowed (int16 samples were squared in int16, so the volume was wrong and could get stuck at 0), and the wireframe echo
  ignored its opacity setting.</p>

  <h2>Audio input in the browser</h2>
  <p>The demo loop is synthesised in code (120 BPM, A minor – F – C – G, kick, bass, pad, arpeggio and hats) and plays
  silently unless you turn the sound on. An audio file is decoded by the browser, mixed to mono and resampled to 44.1 kHz.
  The microphone is used only after you click <b>Microphone</b> and allow it; nothing is recorded or sent anywhere.</p>

  <h2>Run it yourself</h2>
  <h3>Desktop app (PyQt5 + PyAudio)</h3>
  <pre>pip install -r requirements.txt
python main.py</pre>
  <h3>Web app (this site, with the Python API)</h3>
  <pre>pip install -r requirements-web.txt
python run_web.py          # http://127.0.0.1:8224</pre>
  <p>The local app also serves the Python analysis for your own audio on the Verify page. The static GitHub Pages site is
  built by <code>scripts/build_static.py</code>.</p>

  <h2>Credits</h2>
  <p>Music-Reactive Kaleidoscope Visualizer by George Dickinson, developed with Claude AI; MIT licence. FFT in the desktop app
  by NumPy. Web version built with AI assistance from <a href="https://claude.com/">Claude (Anthropic)</a>.</p>`;
});
