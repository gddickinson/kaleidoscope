# Music-Reactive Kaleidoscope — Interface Map

## Entry points

| File | Purpose |
|------|---------|
| `main.py` | Desktop app (PyQt5 + PyAudio): `python main.py` |
| `run_web.py` | Web app on http://127.0.0.1:8224 (`src.web.app:app`) |
| `scripts/build_static.py` | Export the static GitHub Pages site to `site/` |
| `scripts/make_fixtures.py` | Regenerate `tests/fixtures/*.json` and `src/web/desktop_defaults.json` from the Python code (needs PyQt5) |
| `scripts/screenshots.py` | Playwright smoke test (`--static` / `--base`) and README images (`--shots` → `docs/img/`) |
| `.github/workflows/pages.yml` | Test, build and publish the static site on push to `main` |

## Desktop package: `src/`

| File | Lines | Purpose | Key names |
|------|-------|---------|-----------|
| `app/main_window.py` | 154 | Main window: visualisation tab, controls tab, debug console; wires AudioProcessor → engine | `MainWindow` |
| `core/audio_analysis.py` | 84 | Per-chunk analysis (numpy only): RMS volume, smoothed FFT, bands, spectrum | `analyze_chunk`, `AnalysisState`, `CHUNK_SIZE`, `RATE` |
| `core/audio_processing.py` | 72 | PyAudio capture thread; calls `analyze_chunk` per 2048-sample chunk | `AudioProcessor` |
| `core/kaleidoscope_engine.py` | 658 | Engine: particles, beat detection, pulse, 3D, render pipeline, setters | `KaleidoscopeEngine` |
| `core/visualization_components.py` | 1259 | Particle, shapes, colours, symmetry, blur/distortion, waveform ring, wireframe solids + manager | `Particle`, `ShapeRenderer`, `ColorGenerator`, `SymmetryRenderer`, `EffectProcessor`, `CircularWaveform`, `WireframeManager` |
| `core/particle_effects.py` | 1124 | Spark/flare/firework/mist effects, particle tunnel, manager | `EffectsManager` |
| `ui/control_panel.py` | 568 | Control panel (tabs from mixins) and `apply_to_engine` | `ControlPanel` |
| `ui/visual_controls.py`, `wireframe_controls.py`, `effect_controls.py`, `experimental_controls.py` | ~200–330 | Control-creation mixins per tab | `*ControlsMixin` |
| `ui/widgets.py` | 197 | Visualisation widget (timer render) and frequency display | `VisualizationWidget`, `FrequencyDisplayWidget` |
| `ui/debug_console.py` | 37 | Log console tab | `DebugConsole` |
| `experimental/*.py` | | Dimensional portal, liquid metal, audio mycelia, gravitational lens, audio ML (off by default) | `ExperimentalEffectsManager` |
| `plugins/plugins.py` | 218 | Effect/shape/colour plugin examples | |

## Web: `src/web/` (no PyQt5/PyAudio needed to serve)

| File | Purpose | Key names |
|------|---------|-----------|
| `app.py` | FastAPI: static front end; `/api/info`, `/defaults`, `/reference`, `/reference/audio`, `/reference/engine/{name}`, POST `/analyze` | `app`, `STATIC`, `STATIC_ENDPOINTS` |
| `desktop_defaults.py` / `desktop_defaults.json` | Reads the real `ControlPanel` (offscreen) into tab/group/label/range/default JSON | `read_panel()` |
| `reference.py` | Seeded runs of the real `analyze_chunk` and `KaleidoscopeEngine` (random module swapped for mulberry32) | `audio_reference()`, `run_case()`, `CASES` |
| `demo_signal.py` | Built-in demo loop (120 BPM, Am–F–C–G) | `demo_float()`, `demo_int16()` |
| `pyrandom.py` | mulberry32 + `random`-module shim (same stream as JS) | `Mulberry32`, `PyRandomShim` |
| `static/index.html`, `style.css` (kit), `style_app.css`, `core.js` (kit), `main.js`, `static_api.js`, `icon.svg` | Shell, theme, router, static-site data layer | |
| `static/audio_analysis.js`, `fft.js` | Port of `audio_analysis.py`; radix-2 real FFT | `analyzeChunk`, `AnalysisState`, `rfftAbs` |
| `static/kaleido_engine.js` | Port of `KaleidoscopeEngine` state/update and `Particle` | `KaleidoscopeEngine` |
| `static/wireframe.js`, `waveform.js`, `effects.js` | Ports of the wireframe classes, `CircularWaveform`, `particle_effects.py` (no tunnel) | `WireframeManager`, `CircularWaveform`, `EffectsManager` |
| `static/kaleido_render.js` | Canvas port of `render()`, shapes, colours, symmetry, blur, distortion, frequency display | `Renderer`, `drawFrequencyDisplay` |
| `static/settings.js` | Port of `ControlPanel.apply_to_engine` | `applyToEngine`, `defaultValues` |
| `static/pyrandom.js`, `colors.js`, `demo_signal.js` | Shared random stream, colorsys, demo loop | `R`, `hsvToRgb`, `demoFloat` |
| `static/audio_input.js` | Demo / file / microphone sources cut into 2048-sample chunks at 44.1 kHz | `AudioFeed`, `decodeFile` |
| `static/panel.js` | Control panel DOM built from `/api/defaults` | `buildPanel` |
| `static/reference.js` | Replays reference runs in JS and compares | `runEngineCase`, `runAudioCase`, `compare` |
| `static/home.js`, `visualiser.js`, `verify.js`, `about.js` | Pages `#/`, `#/visualiser`, `#/verify`, `#/about` | |
| `static/*.test.mjs` | Node tests of the JS port against `tests/fixtures/` | |

## Tests

| File | Coverage |
|------|----------|
| `tests/test_audio_processing.py` | FFT/RMS/smoothing maths (numpy) |
| `tests/test_audio_analysis.py` | Regression: RMS of int16 input without overflow |
| `tests/test_wireframe_echo.py` | Regression: echo opacity applied (needs PyQt5) |
| `tests/test_web.py` | API endpoints, static build, node tests, fixtures/defaults current, `/analyze` vs `analyze_chunk` |

## Data flow

```
Desktop: AudioProcessor (PyAudio) ─ analyze_chunk ─▶ MainWindow.process_audio ─▶ KaleidoscopeEngine.update
         VisualizationWidget timer ─▶ KaleidoscopeEngine.render ─▶ QImage;  ControlPanel.apply_to_engine on every change
Web:     AudioFeed (demo/file/mic) ─ analyzeChunk ─▶ KaleidoscopeEngine (JS).update ─▶ Renderer ─▶ canvas
         /api/defaults (desktop_defaults.json) ─▶ panel.js ─▶ settings.applyToEngine
         scripts/build_static.py ─▶ site/ (static/ + api/*.json) ─▶ GitHub Pages
```
