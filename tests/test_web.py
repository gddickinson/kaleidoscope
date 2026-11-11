"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific -------------------------------------------------------------------------------------------
import json  # noqa: E402

import numpy as np  # noqa: E402

FIX = ROOT / "tests" / "fixtures"


def _close(a, b, rtol=1e-9, path=""):
    """Recursive comparison with a relative tolerance on numbers (libm differs in the last digit across OSes)."""
    if isinstance(a, bool) or isinstance(b, bool) or isinstance(a, str) or a is None:
        assert a == b, path
    elif isinstance(a, (int, float)):
        assert abs(a - b) <= rtol * max(1.0, abs(a)), f"{path}: {a} vs {b}"
    elif isinstance(a, list):
        assert len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            _close(x, y, rtol, f"{path}[{i}]")
    else:
        assert a.keys() == b.keys(), path
        for k in a:
            _close(a[k], b[k], rtol, f"{path}.{k}")


def test_info_counts_come_from_desktop_panel():
    info = client.get("/api/info").json()
    assert info["symmetry_modes"] == ["Radial", "Mirror", "Spiral"]
    assert len(info["wireframe_shapes"]) == 7
    assert info["chunk_size"] == 2048 and info["rate"] == 44100
    assert 0 < info["controls_ported"] < info["controls"]


def test_audio_fixture_is_current():
    from src.web.reference import audio_reference
    _close(json.loads((FIX / "audio_reference.json").read_text()), json.loads(json.dumps(audio_reference())))


def test_engine_fixtures_and_defaults_are_current():
    pytest.importorskip("PyQt5.QtWidgets")
    from src.web.desktop_defaults import read_panel
    from src.web.reference import CASES, run_case
    assert json.loads((ROOT / "src" / "web" / "desktop_defaults.json").read_text()) == read_panel()
    for case in CASES:
        _close(json.loads((FIX / f"engine_{case['name']}.json").read_text()), json.loads(json.dumps(run_case(case))), 1e-7)


def test_analyze_endpoint_matches_analyze_chunk():
    from src.core.audio_analysis import AnalysisState, analyze_chunk
    from src.web.demo_signal import demo_int16
    samples = demo_int16(3 * 2048, level=0.6)
    r = client.post("/api/analyze", json={"samples": samples.tolist(), "sensitivity": 1.2, "smoothing": 0.4}).json()
    state = AnalysisState(1.2, 0.4)
    for i, row in enumerate(r["rows"]):
        spectrum, bands, volume, _ = analyze_chunk(state, samples[i * 2048:(i + 1) * 2048])
        assert np.allclose(row["spectrum"], spectrum) and np.allclose(row["bands"], bands) and row["volume"] == volume
    assert r["chunks"] == 3


def test_unknown_reference_is_404():
    assert client.get("/api/reference/engine/nope").status_code == 404
