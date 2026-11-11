import numpy as np
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal

from src.core.audio_analysis import analyze_chunk

# =============================================================================
# Core Module: Audio Processing
# =============================================================================

class AudioProcessor(QThread):
    """Thread for capturing and processing audio input"""
    # Update the signal definition to include raw audio data
    audio_data = pyqtSignal(np.ndarray, np.ndarray, float, np.ndarray)

    def __init__(self):
        super().__init__()
        self.chunk_size = 1024 * 2
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.running = True
        self.sensitivity = 1.0
        self.smoothing = 0.3

        # Audio processing variables - initialize with correct size
        # The FFT output size will be (chunk_size // 2) + 1 for real input
        self.fft_data = np.zeros((self.chunk_size // 2) + 1)
        self.prev_fft = np.zeros((self.chunk_size // 2) + 1)
        self.rms_volume = 0
        self.prev_volume = 0

        # Store the last raw audio chunk for waveform visualization
        self.last_raw_audio = np.zeros(self.chunk_size)

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk_size)

        while self.running:
            try:
                # Read audio data
                data = np.frombuffer(stream.read(self.chunk_size, exception_on_overflow=False), dtype=np.int16)

                # Analyse the chunk (shared with the web app: src/core/audio_analysis.py)
                result = analyze_chunk(self, data)
                if result is not None:
                    spectrum, bands, volume, raw_audio = result
                    # Emit signal with raw audio data
                    self.audio_data.emit(spectrum, bands, volume, raw_audio)
            except Exception as e:
                print(f"Audio processing error: {e}")
                import traceback
                traceback.print_exc()  # This will print the stack trace for better debugging

        stream.stop_stream()
        stream.close()
        p.terminate()

    def set_sensitivity(self, value):
        self.sensitivity = value

    def set_smoothing(self, value):
        self.smoothing = value

    def stop(self):
        self.running = False
        self.wait()
