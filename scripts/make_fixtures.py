"""Regenerate the Python reference data used by the web app and the JavaScript tests (needs numpy and PyQt5).

    tests/fixtures/audio_reference.json    demo loop chunks + real analyze_chunk output (int16 and float samples)
    tests/fixtures/engine_<case>.json      real KaleidoscopeEngine runs on the analysed demo loop (seeded)
    src/web/desktop_defaults.json          the desktop ControlPanel's controls and defaults

Run: python scripts/make_fixtures.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.web.desktop_defaults import read_panel  # noqa: E402
from src.web.reference import CASES, audio_reference, run_case  # noqa: E402

FIX = ROOT / "tests" / "fixtures"
DEFAULTS = ROOT / "src" / "web" / "desktop_defaults.json"


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, separators=(",", ":")) + "\n")
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size / 1e3:.0f} kB)")


def main():
    write(FIX / "audio_reference.json", audio_reference())
    for case in CASES:
        write(FIX / f"engine_{case['name']}.json", run_case(case))
    DEFAULTS.write_text(json.dumps(read_panel(), indent=1) + "\n")
    print(f"wrote {DEFAULTS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
