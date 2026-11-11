# Session log

## 2026-11-11 — Web interface and static GitHub Pages site (branch `web-interface`)

Done
- Factored the per-chunk analysis out of `AudioProcessor.run` into `src/core/audio_analysis.py` (numpy only); the
  desktop thread calls it, behaviour unchanged (separate commit).
- Web app `src/web/` (FastAPI, port 8224) + static site: the visualiser runs in the browser. JS ports of the analysis,
  `KaleidoscopeEngine`, particles, waveform ring, wireframes, particle effects and `apply_to_engine`; canvas renderer.
  Control panel built from the real desktop `ControlPanel` (read offscreen into `desktop_defaults.json`).
- Audio in the browser: built-in demo loop (`demo_signal.py`/`.js`), a user-picked file (decoded, mono, 44.1 kHz), or the
  microphone after an explicit click. Chunks of 2048 samples at 44.1 kHz as on the desktop.
- Verify page + node tests: JS vs seeded runs of the real Python engine (random module swapped for mulberry32): all
  values match to ~1e-14 relative (2 engine cases x 160 updates, 8 analysis chunks).
- README web section with screenshots; INTERFACE.md, CLAUDE.md created; Pages workflow added.

Bugs found and fixed (each in its own "Fix" commit, with a regression test that failed first)
- RMS volume overflow: int16 samples were squared in int16 (`data**2`), wrapping for |sample| > 181; loud input gave a
  wrong volume and, once the mean went negative, NaN, reported as 0 forever. Now squared as float64
  (`tests/test_audio_analysis.py`). Volume-driven effects (particle size, waveform amplitude, wireframe pulse,
  beat-triggered effects) now react to loud audio on the desktop.
- Wireframe echo ignored Echo Opacity: `set_colors()` reset the alpha to 255 (`tests/test_wireframe_echo.py`).
- README listed F/Esc/R/Space shortcuts that the desktop code never implemented; corrected (the web version has them).
  Install step said `cd kaleidoscope-visualizer`; corrected to `cd kaleidoscope`.
- ROADMAP.md described control_panel.py as 1831 lines and a top-level standalone/ directory; updated to the current layout.

Notes / open
- Not ported to the web: particle tunnel and the experimental effects (all off by default), multi-monitor fullscreen.
- With the fixed volume, the sensitivity default (1.0) and FFT magnitudes (unnormalised, bass band ~10-60 for music)
  make rotation very fast for loud input; this is the desktop's own scaling, kept as is.
- Pre-existing files over the 500-line budget (not touched beyond the fixes): `visualization_components.py` (1259),
  `particle_effects.py` (1124), `kaleidoscope_engine.py` (658), `control_panel.py` (568).
