"""Regression tests for the per-chunk analysis (src/core/audio_analysis.py, used by AudioProcessor)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.audio_analysis import AnalysisState, analyze_chunk  # noqa: E402


def _sine(amplitude, n=2048, rate=44100, freq=440.0):
    t = np.arange(n) / rate
    return (np.sin(2 * np.pi * freq * t) * amplitude).astype(np.int16)


def test_rms_volume_of_loud_int16_input():
    """int16 samples from PyAudio must not overflow when squared: RMS of a sine is amplitude / sqrt(2)."""
    data = _sine(8000)
    state = AnalysisState(sensitivity=1.0, smoothing=0.0)
    _, _, volume, _ = analyze_chunk(state, data)
    expected = np.sqrt(np.mean(data.astype(np.float64) ** 2)) / 32768.0
    assert abs(volume - expected) < 1e-12
    assert abs(volume - 8000 / np.sqrt(2) / 32768.0) < 1e-3


def test_rms_volume_stays_finite_for_full_scale_input():
    """A full-scale chunk used to give a negative mean of wrapped squares -> NaN volume, stuck at 0 afterwards."""
    state = AnalysisState(sensitivity=1.0, smoothing=0.3)
    for amp in (30000, 2000):
        _, _, volume, _ = analyze_chunk(state, _sine(amp))
        assert np.isfinite(state.prev_volume) and volume > 0


def test_int16_and_float_input_agree():
    data = _sine(20000)
    a = analyze_chunk(AnalysisState(), data)
    b = analyze_chunk(AnalysisState(), data.astype(np.float64))
    assert np.allclose(a[0], b[0]) and np.allclose(a[1], b[1]) and abs(a[2] - b[2]) < 1e-12
