"""
Music-Reactive Kaleidoscope Visualization Application
Web module - FastAPI app and the browser visualiser (no PyQt/PyAudio needed to serve it).

Submodules:
    app               - FastAPI app: static front end + JSON API (/info, /defaults, /reference..., POST /analyze)
    demo_signal       - Built-in demo music loop (ported to static/demo_signal.js)
    pyrandom          - mulberry32 stream + random-module shim shared with the JS engine
    reference         - Seeded reference runs of the real analysis and engine (fixtures for the JS port)
    desktop_defaults  - Reads the desktop ControlPanel's controls into desktop_defaults.json (needs PyQt5)
    static/           - ES-module front end; JS engine port and its node tests
"""
