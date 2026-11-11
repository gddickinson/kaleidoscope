// Home page: hero with a live (silent) kaleidoscope driven by the demo loop, counts from the API, entry cards.
import { route, api, app, list, animate } from './core.js';
import { R } from './pyrandom.js';
import { KaleidoscopeEngine } from './kaleido_engine.js';
import { Renderer } from './kaleido_render.js';
import { AudioFeed } from './audio_input.js';
import { applyToEngine, defaultValues } from './settings.js';

const DOORS = [
  ['#/visualiser', 'Visualiser', 'The full kaleidoscope with the desktop control panel. Drive it with the built-in demo loop, an audio file of your own, or your microphone.'],
  ['#/verify', 'Verify', 'The browser engine against the Python code: the same audio and the same random stream, compared value by value.'],
  ['#/about', 'About', 'How the audio becomes pictures, what the web version covers, how to run the desktop and web apps, credits.'],
];

route('home', async () => {
  const [info, defaults] = await Promise.all([api('/info'), api('/defaults')]);
  app().innerHTML = `
  <section class="hero two herokal">
    <div>
      <p class="kicker">Audio analysis · symmetry · particles</p>
      <h1 class="glow">Music-Reactive Kaleidoscope</h1>
      <p class="lead">${info.summary} This site runs the visualiser in your browser: a JavaScript port of the Python
      engine, fed by the same audio analysis.</p>
      <a class="btn" href="#/visualiser">Open the visualiser</a><a class="btn alt" href="#/about">How it works</a>
    </div>
    <figure class="fig"><canvas id="hero" width="560" height="420" role="img" aria-label="Live kaleidoscope reacting to the built-in demo loop"></canvas>
      <figcaption class="small mute">Desktop default settings, driven (silently) by the built-in demo loop.</figcaption></figure>
  </section>
  <div class="tiles">
    <div class="tile"><b>${info.symmetry_modes.length}</b><span>symmetry modes</span></div>
    <div class="tile"><b>${info.particle_shapes.length}</b><span>particle shapes</span></div>
    <div class="tile"><b>${info.wireframe_shapes.length}</b><span>wireframe solids</span></div>
    <div class="tile"><b>${info.effect_types.length}</b><span>particle effects</span></div>
    <div class="tile"><b>${info.controls_ported}</b><span>desktop controls in the web panel</span></div>
    <div class="tile"><b>${(info.updates_per_second).toFixed(1)}</b><span>audio updates per second</span></div>
  </div>
  <div class="grid wide">${list(DOORS, ([href, t, d]) => `<a class="card door" href="${href}"><b>${t}</b><span>${d}</span></a>`)}</div>
  <h2>Symmetry modes</h2>
  <p>${list(info.symmetry_modes, s => `<span class="tag a">${s}</span>`)} ${list(info.color_modes, s => `<span class="tag b">${s} colour</span>`)}
    ${list(info.particle_shapes, s => `<span class="tag c">${s}</span>`)}</p>`;
  hero(defaults);
});

function hero(defaults) {
  const canvas = document.getElementById('hero');
  R.seed(11);
  const engine = new KaleidoscopeEngine(canvas.width, canvas.height);
  const feed = new AudioFeed();
  applyToEngine(engine, feed.state, defaultValues(defaults));
  const renderer = new Renderer(engine, canvas);
  const step = () => { for (const r of feed.pull()) engine.update(r.spectrum, r.bands, r.volume, r.raw); renderer.render(); };
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    feed.offset = 60 * 2048; step(); return; // one still frame after ~3 s of the loop
  }
  animate(step);
}
