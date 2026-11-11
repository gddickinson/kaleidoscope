"""Reference runs of the real Python visualiser, for testing the JavaScript port (node tests, Verify page).

Audio: the demo loop (demo_signal.py), as int16 samples, is analysed by the real `analyze_chunk`.

Engine: a real `KaleidoscopeEngine` (PyQt5, offscreen) is configured through the real desktop `ControlPanel`
(`apply_to_engine`, with optional widget overrides) and fed the analysed demo loop chunk by chunk. The `random`
module of the engine modules is swapped for `PyRandomShim` (mulberry32), so the JS engine given the same seed draws
the same numbers. Snapshots of the engine state are recorded for comparison.

Needs PyQt5 for the engine part; scripts/make_fixtures.py writes the results to tests/fixtures/.
"""
import contextlib
import io
import os

import numpy as np

from src.core.audio_analysis import CHUNK_SIZE, AnalysisState, analyze_chunk
from .demo_signal import demo_int16
from .pyrandom import Mulberry32, PyRandomShim

AUDIO_CASE = {"seed": 1, "level": 0.5, "sensitivity": 1.3, "smoothing": 0.3, "chunks": 8}

CASES = [
    {"name": "desktop_defaults", "seed": 3, "width": 800, "height": 600, "steps": 160, "snap_every": 20,
     "level": 0.25, "settings": {}},
    {"name": "busy", "seed": 9, "width": 640, "height": 640, "steps": 160, "snap_every": 20, "level": 0.6,
     "settings": {"sensitivity_slider": 150, "symmetry_combo": "Spiral", "shape_combo": "Star",
                  "color_mode_combo": "Gradient", "effects_beat_threshold_slider": 10, "effects_random_slider": 20,
                  "effects_intensity_slider": 200, "wireframe_auto_morph_check": True,
                  "wireframe_beat_morph_check": True, "wireframe_multi_check": True, "wireframe_echo_check": True,
                  "wireframe_color_combo": "Rainbow", "particles_slider": 60, "trail_slider": 8,
                  "pulse_strength_slider": 150, "pulse_decay_slider": 5}},
]
CASE_BY_NAME = {c["name"]: c for c in CASES}


def _draws(rand, n):
    return [rand() for _ in range(n)]


def _sig(x, digits):
    return float(f"{float(x):.{digits}g}")


def audio_reference():
    """The demo loop chunks (int16) and their analysis by analyze_chunk."""
    c = AUDIO_CASE
    n = c["chunks"] * CHUNK_SIZE
    samples = demo_int16(n, seed=c["seed"], level=c["level"])
    out = {"case": c, "samples": samples.tolist(), "demo_head": demo_int16(4096).tolist(),
           "mulberry32_seed1": _draws(Mulberry32(1), 5)}
    state = AnalysisState(sensitivity=c["sensitivity"], smoothing=c["smoothing"])
    rows = []
    for i in range(c["chunks"]):
        spectrum, bands, volume, raw = analyze_chunk(state, samples[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE])
        rows.append({"spectrum": spectrum.tolist(), "bands": bands.tolist(), "volume": float(volume),
                     "fft_sum": float(state.fft_data.sum()), "raw_sum": float(np.sum(raw))})
    out["rows"] = rows
    return out


def features(case, state):
    """Analysed demo chunks for an engine case, rounded (spectrum 6, bands/volume 9 significant digits)."""
    samples = demo_int16(case["steps"] * CHUNK_SIZE, seed=1, level=case["level"])
    rows = []
    for i in range(case["steps"]):
        spectrum, bands, volume, _ = analyze_chunk(state, samples[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE])
        rows.append({"spectrum": [_sig(v, 6) for v in spectrum], "bands": [_sig(v, 9) for v in bands],
                     "volume": _sig(volume, 9)})
    return rows


def _qcolor(c):
    return [c.red(), c.green(), c.blue(), c.alpha()]


def snapshot(engine, step):
    """Engine state after `step` updates."""
    wf, wm, em = engine.circular_waveform, engine.wireframe_manager, engine.effects_manager
    return {
        "step": step, "rotation": engine.rotation,
        "rot3d": [engine.rotation_3d_x, engine.rotation_3d_y, engine.rotation_3d_z],
        "is_beat": engine.is_beat, "beat_cooldown": engine.beat_cooldown,
        "current_pulse": engine.current_pulse, "target_pulse": engine.target_pulse,
        "particles": [[p.x, p.y, p.z, p.angle, p.current_size, len(p.trail)] for p in engine.particles],
        "waveform": {"rotation": wf.rotation, "amplitude": wf.amplitude, "smoothed": wf.smoothed_data.tolist()},
        "wireframe": {
            "current": type(wm.current_shape).__name__, "beat_counter": wm.beat_counter,
            "last_beat_time": wm.last_beat_time, "rainbow_offset": wm.rainbow_offset,
            "shapes": [{"type": type(s).__name__, "rot": [s.rotation_x, s.rotation_y, s.rotation_z],
                        "pulse_size": s.pulse_size, "color": _qcolor(s.base_color), "thickness": s.edge_thickness,
                        "size": s.size, "morph_progress": s.morph_progress, "n_vertices": len(s.vertices),
                        "morph_target": type(s.morph_target).__name__ if s.morph_target else None}
                       for s in wm.shapes]},
        "effects": {"beat_cooldown": em.beat_cooldown, "list": [
            {"type": type(e).__name__, "lifetime": e.lifetime, "max_lifetime": e.max_lifetime, "active": e.active,
             "n": len(e.particles), "particles": [[p.x, p.y, p.alpha, p.size] for p in e.particles[:4]]}
            for e in em.effects]},
    }


def _apply_overrides(panel, settings):
    from PyQt5.QtWidgets import QCheckBox, QComboBox
    for name, value in settings.items():
        w = getattr(panel, name)
        if isinstance(w, QCheckBox):
            w.setChecked(bool(value))
        elif isinstance(w, QComboBox):
            w.setCurrentText(value)
        else:
            w.setValue(value)


def run_case(case):
    """Run one engine case; returns the inputs, a per-step trace and snapshots."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication
    _app = QApplication.instance() or QApplication([])
    import src.core.kaleidoscope_engine as ke
    import src.core.particle_effects as pe
    import src.core.visualization_components as vc
    from src.ui.control_panel import ControlPanel

    shim = PyRandomShim(0)
    saved = (vc.random, ke.random, pe.random)
    vc.random = ke.random = pe.random = shim
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            engine = ke.KaleidoscopeEngine(case["width"], case["height"])
            panel = ControlPanel()
            _apply_overrides(panel, case["settings"])
            state = AnalysisState()
            panel.apply_to_engine(engine, state)
            shim.rand = Mulberry32(case["seed"])
            engine.init_particles()
            inputs = features(case, state)
            trace, snaps = [], []
            for i, f in enumerate(inputs, start=1):
                engine.update(np.array(f["spectrum"]), np.array(f["bands"]), f["volume"])
                trace.append([engine.rotation, int(engine.is_beat), engine.current_pulse,
                              len(engine.effects_manager.effects)])
                if i % case["snap_every"] == 0:
                    snaps.append(snapshot(engine, i))
            final_draw = shim.rand()
    finally:
        vc.random, ke.random, pe.random = saved
    return {"case": case, "sensitivity": state.sensitivity, "smoothing": state.smoothing, "inputs": inputs,
            "trace": trace, "snapshots": snaps, "next_random": final_draw}
