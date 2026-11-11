"""Pure audio analysis (numpy only, no PyQt/PyAudio): one chunk of samples -> spectrum, bands, volume.

This is the per-chunk computation of `AudioProcessor.run` (audio_processing.py), factored out unchanged so that the
desktop app, the web API and the JavaScript port (src/web/static/audio_analysis.js) share one definition.

`state` is any object with the attributes `sensitivity`, `smoothing`, `prev_fft`, `fft_data`, `rms_volume`,
`prev_volume` and `last_raw_audio` (the `AudioProcessor` itself, or an `AnalysisState`).
"""
import numpy as np

CHUNK_SIZE = 1024 * 2
RATE = 44100


class AnalysisState:
    """Smoothing state carried from chunk to chunk (same attributes and initial values as AudioProcessor)."""

    def __init__(self, sensitivity=1.0, smoothing=0.3, chunk_size=CHUNK_SIZE):
        self.chunk_size = chunk_size
        self.sensitivity = sensitivity
        self.smoothing = smoothing
        self.fft_data = np.zeros((chunk_size // 2) + 1)
        self.prev_fft = np.zeros((chunk_size // 2) + 1)
        self.rms_volume = 0
        self.prev_volume = 0
        self.last_raw_audio = np.zeros(chunk_size)

    def set_sensitivity(self, value):
        self.sensitivity = value

    def set_smoothing(self, value):
        self.smoothing = value


def analyze_chunk(state, data):
    """Analyse one chunk of samples (int16 values) and update `state`.

    Returns (spectrum, bands, volume, raw_audio) exactly as AudioProcessor emits them, or None for an empty chunk.
    """
    # Store normalized raw audio for waveform visualization
    if len(data) > 0:
        state.last_raw_audio = data / 32768.0  # Normalize to [-1, 1] range

    # Calculate volume/amplitude (RMS)
    # Avoid NaN by ensuring there's valid data
    if len(data) > 0 and np.any(data):
        # Square in float64: int16 samples squared in int16 wrap around for |sample| > 181
        samples = np.asarray(data, dtype=np.float64)
        state.rms_volume = np.sqrt(np.mean(samples**2)) / 32768.0 * state.sensitivity
        state.rms_volume = state.prev_volume * state.smoothing + state.rms_volume * (1 - state.smoothing)
        state.prev_volume = state.rms_volume
    else:
        # Use previous volume if no data is available
        state.rms_volume = state.prev_volume

    if len(data) == 0:
        return None

    # Compute FFT
    fft = np.abs(np.fft.rfft(data / 32768.0))

    # Make sure the arrays have the same shape
    if len(fft) != len(state.prev_fft):
        state.prev_fft = np.zeros_like(fft)

    state.fft_data = state.prev_fft * state.smoothing + fft * (1 - state.smoothing) * state.sensitivity
    state.prev_fft = state.fft_data.copy()  # Use .copy() to avoid reference issues

    # Replace any NaN values with zeros
    state.fft_data = np.nan_to_num(state.fft_data)

    # Prepare frequency bands (low, mid, high)
    bass = np.mean(state.fft_data[1:20])
    mids = np.mean(state.fft_data[20:100])
    highs = np.mean(state.fft_data[100:])

    # Calculate spectrum for visualization
    spectrum = state.fft_data[1:100]  # Take most relevant frequencies for visualization

    # Replace any remaining NaN values with zeros
    spectrum = np.nan_to_num(spectrum)
    bands = np.nan_to_num(np.array([bass, mids, highs]))
    volume = 0.0 if np.isnan(state.rms_volume) else state.rms_volume
    return spectrum, bands, volume, state.last_raw_audio
