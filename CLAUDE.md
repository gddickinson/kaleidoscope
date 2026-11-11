# Kaleidoscope — notes for Claude

Navigation map: @INTERFACE.md. Progress: SESSION_LOG.md.

- Desktop app: `python main.py` (PyQt5, PyAudio). Web app: `python run_web.py` (port 8224); static site via `scripts/build_static.py`.
- The JS engine in `src/web/static/` is a line-by-line port tested against `tests/fixtures/` (regenerate with
  `scripts/make_fixtures.py` after changing the engine, the analysis or the control panel; needs PyQt5).
- Tests: `python -m pytest -q tests/`.
