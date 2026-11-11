"""FastAPI web app for the Music-Reactive Kaleidoscope: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8224, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below.

The visualiser itself runs in the browser (JS port of the engine). The API serves what comes from the Python code:
the desktop control panel's controls and defaults (desktop_defaults.json, read from the real ControlPanel), the
reference runs of the real analysis and engine (tests/fixtures/, written by scripts/make_fixtures.py), and, locally,
the real `analyze_chunk` for audio the user picks on the Verify page. No PyQt5 or PyAudio is needed to serve it.
"""
import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.core.audio_analysis import CHUNK_SIZE, RATE, AnalysisState, analyze_chunk

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
STATIC = HERE / "static"
FIXTURES = ROOT / "tests" / "fixtures"
DEFAULTS = HERE / "desktop_defaults.json"
ENGINE_CASES = sorted(p.stem[len("engine_"):] for p in FIXTURES.glob("engine_*.json"))
# Controls the web panel does not apply (see static/settings.js): the tunnel and the experimental effects.
UNPORTED_GROUPS = {"Particle Tunnel"}
UNPORTED_TABS = {"Experimental Effects"}
NOT_SHOWN = {"fullscreen_check", "monitor_combo"}

app = FastAPI(title="Music-Reactive Kaleidoscope")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def _json(path):
    return json.loads(path.read_text())


def _readme_summary():
    text = (ROOT / "README.md").read_text()
    paras = [p.strip() for p in text.split("\n\n") if p.strip() and not p.lstrip().startswith(("#", "!"))]
    return paras[0] if paras else ""


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    """Project summary and counts for the home page (from the README, the desktop panel and the analysis code)."""
    controls = _json(DEFAULTS)["controls"]
    items = {c["name"]: c.get("items", []) for c in controls}
    ported = [c for c in controls if c["tab"] not in UNPORTED_TABS and c["group"] not in UNPORTED_GROUPS
              and c["name"] not in NOT_SHOWN]
    return {
        "title": "Music-Reactive Kaleidoscope", "summary": _readme_summary(),
        "symmetry_modes": items["symmetry_combo"], "color_modes": items["color_mode_combo"],
        "particle_shapes": items["shape_combo"], "wireframe_shapes": items["wireframe_shape_combo"],
        "effect_types": ["Sparks", "Flares", "Fireworks", "Mist"],
        "controls": len(controls), "controls_ported": len(ported),
        "chunk_size": CHUNK_SIZE, "rate": RATE, "updates_per_second": RATE / CHUNK_SIZE,
    }


@app.get("/api/defaults")
def defaults():
    """The desktop ControlPanel's controls (tab, group, label, range, default), read from the real panel."""
    return _json(DEFAULTS)


@app.get("/api/reference")
def reference_index():
    """Names of the reference runs (Python analysis and engine) used by the Verify page and the node tests."""
    return {"audio": _json(FIXTURES / "audio_reference.json")["case"], "engine": ENGINE_CASES}


@app.get("/api/reference/audio")
def reference_audio():
    """Demo-loop chunks (int16) and their analysis by the real analyze_chunk."""
    return _json(FIXTURES / "audio_reference.json")


@app.get("/api/reference/engine/{name}")
def reference_engine(name: str):
    """A seeded run of the real KaleidoscopeEngine on the analysed demo loop (inputs, trace, snapshots)."""
    if name not in ENGINE_CASES:
        raise HTTPException(404, f"unknown reference run {name!r}")
    return _json(FIXTURES / f"engine_{name}.json")


class Samples(BaseModel):
    samples: list[int]
    sensitivity: float = 1.0
    smoothing: float = 0.3


@app.post("/api/analyze")
def analyze(body: Samples):
    """Run the real analyze_chunk over int16 sample values (at most 64 chunks), as the desktop app would."""
    data = np.clip(np.array(body.samples[:64 * CHUNK_SIZE], dtype=np.int64), -32768, 32767).astype(np.int16)
    state = AnalysisState(body.sensitivity, body.smoothing)
    rows = []
    for i in range(len(data) // CHUNK_SIZE):
        spectrum, bands, volume, _ = analyze_chunk(state, data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE])
        rows.append({"spectrum": spectrum.tolist(), "bands": bands.tolist(), "volume": float(volume)})
    return {"chunks": len(rows), "rows": rows}


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/defaults", "/reference", "/reference/audio"] + [
    f"/reference/engine/{n}" for n in ENGINE_CASES]
