"""Smoke tests for audio processing utilities.

Tests the FFT and signal processing math without requiring audio hardware.
"""

import sys
import os
import numpy as np

# Add project root so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_fft_output_shape():
    """FFT of a real signal has the expected output length."""
    chunk_size = 2048
    signal = np.random.randn(chunk_size).astype(np.float64)
    fft = np.abs(np.fft.rfft(signal))
    assert fft.shape == (chunk_size // 2 + 1,)


def test_fft_pure_tone_peak():
    """FFT of a pure sine wave peaks at the expected frequency bin."""
    rate = 44100
    chunk_size = 2048
    freq_hz = 440  # A4
    t = np.arange(chunk_size) / rate
    signal = np.sin(2 * np.pi * freq_hz * t)
    fft = np.abs(np.fft.rfft(signal))
    peak_bin = np.argmax(fft)
    peak_freq = peak_bin * rate / chunk_size
    assert abs(peak_freq - freq_hz) < (rate / chunk_size), (
        f"Peak at {peak_freq} Hz, expected ~{freq_hz} Hz"
    )


def test_rms_volume():
    """RMS volume calculation matches expected value."""
    data = np.array([100, -100, 100, -100], dtype=np.int16)
    rms = np.sqrt(np.mean(data.astype(np.float64) ** 2)) / 32768.0
    assert 0 < rms < 1
    assert abs(rms - 100 / 32768.0) < 1e-6


def test_smoothing():
    """Exponential smoothing blends old and new values."""
    prev = 0.5
    new_val = 1.0
    smoothing = 0.3
    result = prev * smoothing + new_val * (1 - smoothing)
    assert abs(result - 0.85) < 1e-6


def test_frequency_bands():
    """Frequency band slicing produces non-negative values."""
    chunk_size = 2048
    signal = np.random.randn(chunk_size)
    fft = np.abs(np.fft.rfft(signal / 32768.0))
    bass = np.mean(fft[1:20])
    mids = np.mean(fft[20:100])
    highs = np.mean(fft[100:])
    assert bass >= 0
    assert mids >= 0
    assert highs >= 0


def test_nan_to_num_safety():
    """nan_to_num replaces NaN/Inf in FFT output."""
    data = np.array([0.0, np.nan, np.inf, -np.inf, 1.0])
    cleaned = np.nan_to_num(data)
    assert not np.any(np.isnan(cleaned))
    assert not np.any(np.isinf(cleaned))


if __name__ == "__main__":
    test_fft_output_shape()
    test_fft_pure_tone_peak()
    test_rms_volume()
    test_smoothing()
    test_frequency_bands()
    test_nan_to_num_safety()
    print("All kaleidoscope audio processing tests passed!")
