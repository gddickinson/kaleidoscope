import numpy as np
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal

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

                # Store normalized raw audio for waveform visualization
                if len(data) > 0:
                    self.last_raw_audio = data / 32768.0  # Normalize to [-1, 1] range

                # Calculate volume/amplitude (RMS)
                # Avoid NaN by ensuring there's valid data
                if len(data) > 0 and np.any(data):
                    self.rms_volume = np.sqrt(np.mean(data**2)) / 32768.0 * self.sensitivity
                    self.rms_volume = self.prev_volume * self.smoothing + self.rms_volume * (1 - self.smoothing)
                    self.prev_volume = self.rms_volume
                else:
                    # Use previous volume if no data is available
                    self.rms_volume = self.prev_volume

                # Compute FFT
                if len(data) > 0:
                    fft = np.abs(np.fft.rfft(data / 32768.0))

                    # Make sure the arrays have the same shape
                    if len(fft) != len(self.prev_fft):
                        self.prev_fft = np.zeros_like(fft)

                    self.fft_data = self.prev_fft * self.smoothing + fft * (1 - self.smoothing) * self.sensitivity
                    self.prev_fft = self.fft_data.copy()  # Use .copy() to avoid reference issues

                    # Replace any NaN values with zeros
                    self.fft_data = np.nan_to_num(self.fft_data)

                    # Prepare frequency bands (low, mid, high)
                    bass = np.mean(self.fft_data[1:20])
                    mids = np.mean(self.fft_data[20:100])
                    highs = np.mean(self.fft_data[100:])

                    # Calculate spectrum for visualization
                    spectrum = self.fft_data[1:100]  # Take most relevant frequencies for visualization

                    # Replace any remaining NaN values with zeros
                    spectrum = np.nan_to_num(spectrum)
                    bands = np.nan_to_num(np.array([bass, mids, highs]))
                    volume = 0.0 if np.isnan(self.rms_volume) else self.rms_volume

                    # Emit signal with raw audio data
                    self.audio_data.emit(spectrum, bands, volume, self.last_raw_audio)
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
