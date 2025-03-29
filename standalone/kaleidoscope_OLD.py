"""
Music-Reactive Kaleidoscope Visualization Application
- Modular architecture for extensibility
- PyQt5 for all rendering (no Pygame)
- Real-time audio analysis and visualization
"""

import sys
import numpy as np
import pyaudio
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QCheckBox,
                           QTextEdit, QSpinBox, QColorDialog, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QTime, QRect, QPoint, QObject
from PyQt5.QtGui import QColor, QFont, QPainter, QImage, QPen, QBrush, QRadialGradient
import colorsys
import random
import math

# =============================================================================
# Core Module: Audio Processing
# =============================================================================

class AudioProcessor(QThread):
    """Thread for capturing and processing audio input"""
    audio_data = pyqtSignal(np.ndarray, np.ndarray, float)

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

                    self.audio_data.emit(spectrum, bands, volume)
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


# =============================================================================
# Core Module: Visualization Components
# =============================================================================

class Particle:
    """Individual particle for the visualization"""
    def __init__(self, radius, particle_size, trail_length):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(0, radius * 0.7)
        self.x = math.cos(angle) * dist
        self.y = math.sin(angle) * dist
        self.size = random.uniform(particle_size * 0.5, particle_size * 1.5)
        self.speed = random.uniform(0.5, 2.0)
        self.angle = random.uniform(0, math.pi * 2)
        self.trail = []
        self.trail_length = trail_length
        self.color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.current_size = self.size

    def update(self, speed_mod, size_mod):
        """Update particle position and trail"""
        self.angle += 0.02 * speed_mod
        self.x += math.cos(self.angle) * self.speed * speed_mod * 0.5
        self.y += math.sin(self.angle) * self.speed * speed_mod * 0.5

        # Store trail positions
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

        # Update current size
        self.current_size = self.size * size_mod


class ShapeRenderer:
    """Factory for rendering different particle shapes"""
    @staticmethod
    def render_shape(painter, shape_type, x, y, size, color):
        """Render a shape at the given position with the specified color"""
        if shape_type == "circle":
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPoint(int(x), int(y)), int(size), int(size))
        elif shape_type == "square":
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            rect = QRect(int(x - size/2), int(y - size/2), int(size), int(size))
            painter.drawRect(rect)
        elif shape_type == "triangle":
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            points = [
                QPoint(int(x), int(y - size)),
                QPoint(int(x - size * 0.866), int(y + size * 0.5)),
                QPoint(int(x + size * 0.866), int(y + size * 0.5))
            ]
            painter.drawPolygon(points)
        elif shape_type == "star":
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            points = []
            for i in range(5):
                # Outer points
                angle = math.pi/2 + i * 2*math.pi/5
                points.append(QPoint(
                    int(x + math.cos(angle) * size),
                    int(y + math.sin(angle) * size)
                ))
                # Inner points
                angle += math.pi/5
                points.append(QPoint(
                    int(x + math.cos(angle) * size * 0.4),
                    int(y + math.sin(angle) * size * 0.4)
                ))
            painter.drawPolygon(points)


class ColorGenerator:
    """Factory for generating colors based on different modes"""
    @staticmethod
    def get_color(mode, params):
        """Generate color based on the specified mode and parameters"""
        if mode == "spectrum":
            # Map to spectrum colors
            freq_index = params.get('freq_index', 0)
            intensity = params.get('intensity', 1.0)
            hue = (freq_index / params.get('spectrum_length', 100)) % 1.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.8, intensity)]
            return QColor(r, g, b, params.get('alpha', 255))
        elif mode == "solid":
            # Use base color
            base_color = params.get('base_color', QColor(255, 0, 127))
            return QColor(base_color.red(), base_color.green(), base_color.blue(), params.get('alpha', 255))
        elif mode == "gradient":
            # Create gradient between base and secondary colors
            base_color = params.get('base_color', QColor(255, 0, 127))
            secondary_color = params.get('secondary_color', QColor(0, 127, 255))
            ratio = params.get('ratio', 0.5)

            r = int(base_color.red() * ratio + secondary_color.red() * (1 - ratio))
            g = int(base_color.green() * ratio + secondary_color.green() * (1 - ratio))
            b = int(base_color.blue() * ratio + secondary_color.blue() * (1 - ratio))

            return QColor(r, g, b, params.get('alpha', 255))


class SymmetryRenderer:
    """Factory for rendering different symmetry modes"""
    @staticmethod
    def apply_symmetry(painter, buffer_image, mode, params):
        """Apply symmetry effect to the buffer image"""
        if mode == "radial":
            # Create multiple reflected segments in a circle
            segments = params.get('segments', 8)
            rotation = params.get('rotation', 0)
            center_x = params.get('center_x', 0)
            center_y = params.get('center_y', 0)

            for i in range(segments):
                angle = i * (2 * math.pi / segments) + rotation

                # Create rotated version of buffer
                transform = painter.transform()
                painter.translate(center_x, center_y)
                painter.rotate(math.degrees(-angle))
                painter.drawImage(-center_x, -center_y, buffer_image)
                painter.setTransform(transform)

        elif mode == "mirror":
            # Simple mirror reflection across x and y axes
            painter.drawImage(0, 0, buffer_image)

            # Create flipped versions
            flipped_h = buffer_image.mirrored(True, False)
            flipped_v = buffer_image.mirrored(False, True)
            flipped_both = buffer_image.mirrored(True, True)

            painter.drawImage(0, 0, flipped_h)
            painter.drawImage(0, 0, flipped_v)
            painter.drawImage(0, 0, flipped_both)

        elif mode == "spiral":
            # Create a spiral effect by rotating and scaling segments
            center_x = params.get('center_x', 0)
            center_y = params.get('center_y', 0)
            rotation = params.get('rotation', 0)

            for i in range(8):
                scale = 1.0 - (i * 0.1)
                angle = rotation + i * math.pi / 4

                transform = painter.transform()
                painter.translate(center_x, center_y)
                painter.rotate(math.degrees(-angle))
                painter.scale(scale, scale)
                painter.drawImage(-center_x, -center_y, buffer_image)
                painter.setTransform(transform)


class EffectProcessor:
    """Applies post-processing effects to images"""
    @staticmethod
    def apply_blur(image, amount):
        """Apply blur effect to the image"""
        if amount <= 0:
            return image

        # Create a temporary copy to avoid modifying the original during operation
        result = QImage(image)

        # Create a smaller version and scale it back up for blur effect
        for _ in range(int(amount)):
            # Note: explicitly specify the transformation mode as the last parameter
            small_image = result.scaled(
                result.width() // 4,
                result.height() // 4,
                Qt.IgnoreAspectRatio,  # aspectRatioMode
                Qt.SmoothTransformation  # transformMode
            )

            blurred = small_image.scaled(
                result.width(),
                result.height(),
                Qt.IgnoreAspectRatio,  # aspectRatioMode
                Qt.SmoothTransformation  # transformMode
            )

            # Paint the blurred image onto the result
            painter = QPainter(result)
            painter.setOpacity(0.7)
            painter.drawImage(0, 0, blurred)
            painter.end()

        return result

    @staticmethod
    def apply_distortion(image, amount, center_x, center_y, radius, rotation):
        """Apply wave distortion effect to the image"""
        if amount <= 0:
            return image

        # Create a new image for the distorted result
        result = QImage(image.size(), QImage.Format_ARGB32)
        result.fill(Qt.transparent)

        painter = QPainter(result)

        # Apply distortion by sampling from original with offset
        for x in range(0, image.width(), 2):
            for y in range(0, image.height(), 2):
                # Calculate displacement based on distance from center
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx*dx + dy*dy)

                if distance < radius:
                    # Apply sine wave distortion
                    angle = math.atan2(dy, dx)
                    factor = amount * math.sin(distance / 20 + rotation * 10) * 10

                    src_x = int(x + math.cos(angle) * factor)
                    src_y = int(y + math.sin(angle) * factor)

                    if 0 <= src_x < image.width() and 0 <= src_y < image.height():
                        result.setPixelColor(x, y, image.pixelColor(src_x, src_y))

        painter.end()
        return result


# =============================================================================
# Core Module: Kaleidoscope Engine
# =============================================================================

class KaleidoscopeEngine(QObject):
    """Core engine for kaleidoscope visualization"""
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = min(width, height) // 2

        # Visual parameters
        self.segments = 8
        self.zoom = 1.0
        self.rotation = 0
        self.rotation_speed = 0.5
        self.color_mode = "spectrum"  # "spectrum", "solid", "gradient"
        self.base_color = QColor(255, 0, 127)
        self.secondary_color = QColor(0, 127, 255)
        self.blur_amount = 0
        self.shape_type = "circle"  # "circle", "square", "triangle", "star"
        self.distortion = 0.0
        self.symmetry_mode = "radial"  # "radial", "mirror", "spiral"

        # Animation variables
        self.particles = []
        self.max_particles = 100
        self.particle_size = 10
        self.trail_length = 5

        # Audio reactive variables
        self.bass_influence = 1.0
        self.mids_influence = 1.0
        self.highs_influence = 1.0
        self.spectrum_data = np.zeros(100)
        self.bands = np.zeros(3)
        self.volume = 0

        # Create rendering buffers
        self.buffer_image = QImage(width, height, QImage.Format_ARGB32)
        self.buffer_image.fill(Qt.transparent)
        self.final_image = QImage(width, height, QImage.Format_ARGB32)
        self.final_image.fill(Qt.black)

        # Initialize particles
        self.init_particles()

    def init_particles(self):
        """Initialize particles for animation"""
        self.particles = []
        for _ in range(self.max_particles):
            self.particles.append(Particle(self.radius, self.particle_size, self.trail_length))

    def update(self, spectrum, bands, volume):
        """Update visualization parameters based on audio data"""
        self.spectrum_data = spectrum
        self.bands = bands
        self.volume = volume

        # Apply audio-reactive effects
        base_rotation = self.rotation_speed * 0.01
        bass_rotation = self.bands[0] * self.bass_influence * 0.1
        self.rotation += base_rotation + bass_rotation

        # Update particles
        for p in self.particles:
            # Apply audio influence to particle movement
            speed_mod = 1.0 + self.bands[1] * self.mids_influence
            size_mod = 1.0 + self.volume * 4

            p.update(speed_mod, size_mod)

            # Reset particles that go out of bounds
            dist = math.sqrt(p.x**2 + p.y**2)
            if dist > self.radius * 0.8:
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(0, self.radius * 0.3)
                p.x = math.cos(angle) * dist
                p.y = math.sin(angle) * dist
                p.trail = []

    def render(self):
        """Render the current state of the kaleidoscope"""
        # Clear buffers
        self.buffer_image.fill(Qt.transparent)
        self.final_image.fill(Qt.black)

        # Setup painters
        buffer_painter = QPainter(self.buffer_image)
        buffer_painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw particles to buffer
        for p in self.particles:
            if not p.trail:
                continue

            # Draw trail with fading opacity
            for i, (tx, ty) in enumerate(p.trail):
                alpha = int(255 * (i / len(p.trail)))
                size = p.current_size * (i / len(p.trail))

                # Get color based on mode
                if self.color_mode == "spectrum":
                    # Map particle position to spectrum colors
                    freq_index = min(int(abs(tx / self.radius) * len(self.spectrum_data)), len(self.spectrum_data) - 1)
                    intensity = min(1.0, self.spectrum_data[freq_index] * 2)
                    color = ColorGenerator.get_color("spectrum", {
                        'freq_index': freq_index,
                        'intensity': intensity,
                        'spectrum_length': len(self.spectrum_data),
                        'alpha': alpha
                    })
                elif self.color_mode == "solid":
                    color = ColorGenerator.get_color("solid", {
                        'base_color': self.base_color,
                        'alpha': alpha
                    })
                else:  # gradient
                    ratio = (math.sin(self.rotation * 2 + i / len(p.trail) * math.pi) + 1) / 2
                    color = ColorGenerator.get_color("gradient", {
                        'base_color': self.base_color,
                        'secondary_color': self.secondary_color,
                        'ratio': ratio,
                        'alpha': alpha
                    })

                # Draw the shape
                ShapeRenderer.render_shape(
                    buffer_painter,
                    self.shape_type,
                    self.center_x + tx,
                    self.center_y + ty,
                    size,
                    color
                )

        buffer_painter.end()

        # Apply symmetry effect
        final_painter = QPainter(self.final_image)
        final_painter.setRenderHint(QPainter.Antialiasing, True)

        SymmetryRenderer.apply_symmetry(
            final_painter,
            self.buffer_image,
            self.symmetry_mode,
            {
                'segments': self.segments,
                'rotation': self.rotation,
                'center_x': self.center_x,
                'center_y': self.center_y
            }
        )

        final_painter.end()

        # Apply post-processing effects
        if self.blur_amount > 0:
            self.final_image = EffectProcessor.apply_blur(self.final_image, self.blur_amount)

        if self.distortion > 0:
            self.final_image = EffectProcessor.apply_distortion(
                self.final_image,
                self.distortion,
                self.center_x,
                self.center_y,
                self.radius,
                self.rotation
            )

        return self.final_image

    def resize(self, width, height):
        """Handle resizing of the rendering area"""
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = min(width, height) // 2

        # Recreate buffers at new size
        self.buffer_image = QImage(width, height, QImage.Format_ARGB32)
        self.buffer_image.fill(Qt.transparent)
        self.final_image = QImage(width, height, QImage.Format_ARGB32)
        self.final_image.fill(Qt.black)

    # Setter methods for all parameters
    def set_segments(self, value):
        self.segments = value

    def set_zoom(self, value):
        self.zoom = value

    def set_rotation_speed(self, value):
        self.rotation_speed = value

    def set_color_mode(self, mode):
        self.color_mode = mode

    def set_base_color(self, color):
        self.base_color = color

    def set_secondary_color(self, color):
        self.secondary_color = color

    def set_blur_amount(self, value):
        self.blur_amount = value

    def set_shape_type(self, shape):
        self.shape_type = shape

    def set_distortion(self, value):
        self.distortion = value

    def set_symmetry_mode(self, mode):
        self.symmetry_mode = mode

    def set_particle_settings(self, count, size, trail):
        self.max_particles = count
        self.particle_size = size
        self.trail_length = trail
        self.init_particles()

    def set_audio_influence(self, bass, mids, highs):
        self.bass_influence = bass
        self.mids_influence = mids
        self.highs_influence = highs


# =============================================================================
# UI Module: Visualization Widget
# =============================================================================

class VisualizationWidget(QWidget):
    """Widget to display the kaleidoscope visualization"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_NoSystemBackground)

        # Engine for visualization
        self.engine = None

        # Animation settings
        self.fps = 60
        self.is_fullscreen = False
        self.display_monitor = 0

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // self.fps)

    def init_engine(self):
        """Initialize or update the kaleidoscope engine"""
        width, height = self.width(), self.height()
        if width > 0 and height > 0:
            if not self.engine:
                self.engine = KaleidoscopeEngine(width, height)
            else:
                self.engine.resize(width, height)

    def resizeEvent(self, event):
        """Handle resize events"""
        self.init_engine()
        super().resizeEvent(event)

    def update_frame(self):
        """Update and render a new frame"""
        if self.engine:
            self.update()

    def process_audio(self, spectrum, bands, volume):
        """Process audio data and update visualization"""
        if self.engine:
            self.engine.update(spectrum, bands, volume)

    def paintEvent(self, event):
        """Paint the current frame"""
        if not self.engine:
            return

        # Render new frame
        image = self.engine.render()

        # Paint to widget
        painter = QPainter(self)
        painter.drawImage(0, 0, image)
        painter.end()

    def set_fps(self, fps):
        """Set frames per second"""
        self.fps = fps
        self.timer.setInterval(1000 // self.fps)

    def toggle_fullscreen(self, fullscreen, monitor=0):
        """Toggle fullscreen mode"""
        if fullscreen == self.is_fullscreen:
            return

        self.is_fullscreen = fullscreen
        self.display_monitor = monitor

        # Handle fullscreen mode
        if fullscreen:
            self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            self.showFullScreen()

            # Move to specified monitor
            desktop = QApplication.desktop()
            if monitor < desktop.screenCount():
                screen_geometry = desktop.screenGeometry(monitor)
                self.move(screen_geometry.x(), screen_geometry.y())
                self.resize(screen_geometry.width(), screen_geometry.height())
        else:
            self.setWindowFlags(Qt.Widget)
            self.showNormal()


# =============================================================================
# UI Module: Frequency Display Widget
# =============================================================================

class FrequencyDisplayWidget(QWidget):
    """Widget to display audio frequency spectrum"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spectrum_data = np.zeros(100)
        self.bands = np.zeros(3)
        self.volume = 0

        # Set minimum size
        self.setMinimumHeight(150)

    def update_data(self, spectrum, bands, volume):
        """Update with new audio data"""
        self.spectrum_data = spectrum
        self.bands = bands
        self.volume = volume
        self.update()

    def paintEvent(self, event):
        """Draw the frequency spectrum"""
        if not self.spectrum_data.any():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        # Fill background
        painter.fillRect(0, 0, width, height, QColor(30, 30, 30))

        # Draw spectrum
        bar_width = width / len(self.spectrum_data)
        for i, value in enumerate(self.spectrum_data):
            # Check for NaN and normalize value (with some amplification)
            if np.isnan(value):
                norm_value = 0
            else:
                norm_value = min(1.0, value * 2)
            bar_height = int(norm_value * height)

            # Color based on frequency (blue to red gradient)
            hue = 240 - (i / len(self.spectrum_data) * 240)
            color = QColor.fromHsv(int(hue), 240, 200)

            painter.fillRect(
                int(i * bar_width),
                height - bar_height,
                max(1, int(bar_width - 1)),
                bar_height,
                color
            )

        # Draw frequency band indicators
        band_width = width / 3
        band_colors = [QColor(0, 0, 200), QColor(0, 200, 0), QColor(200, 0, 0)]
        for i, (value, color) in enumerate(zip(self.bands, band_colors)):
            # Check for NaN and normalize with amplification
            if np.isnan(value):
                norm_value = 0
            else:
                norm_value = min(1.0, value * 2)
            indicator_height = int(norm_value * height * 0.2)

            painter.fillRect(
                int(i * band_width),
                0,
                max(1, int(band_width - 1)),
                indicator_height,
                color
            )

            painter.setPen(Qt.white)
            painter.drawText(
                int(i * band_width + 5),
                indicator_height + 15,
                ["Bass", "Mids", "Highs"][i]
            )

        # Draw volume meter
        # Check for NaN in volume
        safe_volume = 0 if np.isnan(self.volume) else self.volume
        volume_width = int(safe_volume * width)
        painter.fillRect(
            0,
            height - 10,
            volume_width,
            10,
            QColor(200, 200, 0)
        )

        painter.setPen(Qt.white)
        painter.drawText(5, height - 15, f"Volume: {int(self.volume * 100)}%")


# =============================================================================
# UI Module: Control Panel
# =============================================================================

class ControlPanel(QWidget):
    """Control panel with UI settings for the visualization"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create layout
        main_layout = QVBoxLayout()

        # Add control groups
        main_layout.addWidget(self._create_general_controls())
        main_layout.addWidget(self._create_visual_controls())
        main_layout.addWidget(self._create_audio_controls())
        main_layout.addWidget(self._create_display_controls())

        # Add reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        main_layout.addWidget(reset_btn)

        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def _create_general_controls(self):
        """Create general visualization controls"""
        group = QGroupBox("General Controls")
        layout = QGridLayout()

        # Segments control
        layout.addWidget(QLabel("Segments:"), 0, 0)
        self.segments_slider = QSlider(Qt.Horizontal)
        self.segments_slider.setRange(3, 24)
        self.segments_slider.setValue(8)
        layout.addWidget(self.segments_slider, 0, 1)
        self.segments_value = QLabel("8")
        layout.addWidget(self.segments_value, 0, 2)
        self.segments_slider.valueChanged.connect(
            lambda v: self.segments_value.setText(str(v)))

        # Rotation speed
        layout.addWidget(QLabel("Rotation:"), 1, 0)
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setRange(0, 100)
        self.rotation_slider.setValue(50)
        layout.addWidget(self.rotation_slider, 1, 1)
        self.rotation_value = QLabel("0.5")
        layout.addWidget(self.rotation_value, 1, 2)
        self.rotation_slider.valueChanged.connect(
            lambda v: self.rotation_value.setText(str(v/100)))

        # Symmetry mode
        layout.addWidget(QLabel("Symmetry:"), 2, 0)
        self.symmetry_combo = QComboBox()
        self.symmetry_combo.addItems(["Radial", "Mirror", "Spiral"])
        layout.addWidget(self.symmetry_combo, 2, 1, 1, 2)

        group.setLayout(layout)
        return group

    def _create_visual_controls(self):
        """Create visual effect controls"""
        group = QGroupBox("Visual Effects")
        layout = QGridLayout()

        # Color mode
        layout.addWidget(QLabel("Color Mode:"), 0, 0)
        self.color_mode_combo = QComboBox()
        self.color_mode_combo.addItems(["Spectrum", "Solid", "Gradient"])
        layout.addWidget(self.color_mode_combo, 0, 1, 1, 2)

        # Base color
        layout.addWidget(QLabel("Base Color:"), 1, 0)
        self.base_color_btn = QPushButton()
        self.base_color_btn.setStyleSheet("background-color: #FF007F")
        self.base_color_btn.clicked.connect(self._select_base_color)
        layout.addWidget(self.base_color_btn, 1, 1, 1, 2)

        # Secondary color
        layout.addWidget(QLabel("Secondary:"), 2, 0)
        self.secondary_color_btn = QPushButton()
        self.secondary_color_btn.setStyleSheet("background-color: #007FFF")
        self.secondary_color_btn.clicked.connect(self._select_secondary_color)
        layout.addWidget(self.secondary_color_btn, 2, 1, 1, 2)

        # Particle shape
        layout.addWidget(QLabel("Shape:"), 3, 0)
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Circle", "Square", "Triangle", "Star"])
        layout.addWidget(self.shape_combo, 3, 1, 1, 2)

        # Blur amount
        layout.addWidget(QLabel("Blur:"), 4, 0)
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 5)
        self.blur_slider.setValue(0)
        layout.addWidget(self.blur_slider, 4, 1)
        self.blur_value = QLabel("0")
        layout.addWidget(self.blur_value, 4, 2)
        self.blur_slider.valueChanged.connect(
            lambda v: self.blur_value.setText(str(v)))

        # Distortion
        layout.addWidget(QLabel("Distortion:"), 5, 0)
        self.distortion_slider = QSlider(Qt.Horizontal)
        self.distortion_slider.setRange(0, 100)
        self.distortion_slider.setValue(0)
        layout.addWidget(self.distortion_slider, 5, 1)
        self.distortion_value = QLabel("0.0")
        layout.addWidget(self.distortion_value, 5, 2)
        self.distortion_slider.valueChanged.connect(
            lambda v: self.distortion_value.setText(str(v/100)))

        # Particle count
        layout.addWidget(QLabel("Particles:"), 6, 0)
        self.particles_slider = QSlider(Qt.Horizontal)
        self.particles_slider.setRange(10, 300)
        self.particles_slider.setValue(100)
        layout.addWidget(self.particles_slider, 6, 1)
        self.particles_value = QLabel("100")
        layout.addWidget(self.particles_value, 6, 2)
        self.particles_slider.valueChanged.connect(
            lambda v: self.particles_value.setText(str(v)))

        # Particle size
        layout.addWidget(QLabel("Size:"), 7, 0)
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(10)
        layout.addWidget(self.size_slider, 7, 1)
        self.size_value = QLabel("10")
        layout.addWidget(self.size_value, 7, 2)
        self.size_slider.valueChanged.connect(
            lambda v: self.size_value.setText(str(v)))

        # Trail length
        layout.addWidget(QLabel("Trails:"), 8, 0)
        self.trail_slider = QSlider(Qt.Horizontal)
        self.trail_slider.setRange(1, 30)
        self.trail_slider.setValue(5)
        layout.addWidget(self.trail_slider, 8, 1)
        self.trail_value = QLabel("5")
        layout.addWidget(self.trail_value, 8, 2)
        self.trail_slider.valueChanged.connect(
            lambda v: self.trail_value.setText(str(v)))

        group.setLayout(layout)
        return group

    def _create_audio_controls(self):
        """Create audio processing controls"""
        group = QGroupBox("Audio Controls")
        layout = QGridLayout()

        # Audio sensitivity
        layout.addWidget(QLabel("Sensitivity:"), 0, 0)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(10, 500)
        self.sensitivity_slider.setValue(100)
        layout.addWidget(self.sensitivity_slider, 0, 1)
        self.sensitivity_value = QLabel("1.0")
        layout.addWidget(self.sensitivity_value, 0, 2)
        self.sensitivity_slider.valueChanged.connect(
            lambda v: self.sensitivity_value.setText(str(v/100)))

        # Audio smoothing
        layout.addWidget(QLabel("Smoothing:"), 1, 0)
        self.smoothing_slider = QSlider(Qt.Horizontal)
        self.smoothing_slider.setRange(0, 95)
        self.smoothing_slider.setValue(30)
        layout.addWidget(self.smoothing_slider, 1, 1)
        self.smoothing_value = QLabel("0.3")
        layout.addWidget(self.smoothing_value, 1, 2)
        self.smoothing_slider.valueChanged.connect(
            lambda v: self.smoothing_value.setText(str(v/100)))

        # Bass influence
        layout.addWidget(QLabel("Bass:"), 2, 0)
        self.bass_slider = QSlider(Qt.Horizontal)
        self.bass_slider.setRange(0, 200)
        self.bass_slider.setValue(100)
        layout.addWidget(self.bass_slider, 2, 1)
        self.bass_value = QLabel("1.0")
        layout.addWidget(self.bass_value, 2, 2)
        self.bass_slider.valueChanged.connect(
            lambda v: self.bass_value.setText(str(v/100)))

        # Mids influence
        layout.addWidget(QLabel("Mids:"), 3, 0)
        self.mids_slider = QSlider(Qt.Horizontal)
        self.mids_slider.setRange(0, 200)
        self.mids_slider.setValue(100)
        layout.addWidget(self.mids_slider, 3, 1)
        self.mids_value = QLabel("1.0")
        layout.addWidget(self.mids_value, 3, 2)
        self.mids_slider.valueChanged.connect(
            lambda v: self.mids_value.setText(str(v/100)))

        # Highs influence
        layout.addWidget(QLabel("Highs:"), 4, 0)
        self.highs_slider = QSlider(Qt.Horizontal)
        self.highs_slider.setRange(0, 200)
        self.highs_slider.setValue(100)
        layout.addWidget(self.highs_slider, 4, 1)
        self.highs_value = QLabel("1.0")
        layout.addWidget(self.highs_value, 4, 2)
        self.highs_slider.valueChanged.connect(
            lambda v: self.highs_value.setText(str(v/100)))

        group.setLayout(layout)
        return group

    def _create_display_controls(self):
        """Create display controls"""
        group = QGroupBox("Display Settings")
        layout = QGridLayout()

        # FPS control
        layout.addWidget(QLabel("FPS:"), 0, 0)
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(15, 120)
        self.fps_spin.setValue(60)
        layout.addWidget(self.fps_spin, 0, 1, 1, 2)

        # Fullscreen toggle
        layout.addWidget(QLabel("Fullscreen:"), 1, 0)
        self.fullscreen_check = QCheckBox()
        layout.addWidget(self.fullscreen_check, 1, 1)

        # Monitor selection (for multi-monitor setups)
        layout.addWidget(QLabel("Monitor:"), 2, 0)
        self.monitor_combo = QComboBox()
        # Populate with available monitors
        for i in range(QApplication.desktop().screenCount()):
            self.monitor_combo.addItem(f"Monitor {i+1}")
        layout.addWidget(self.monitor_combo, 2, 1, 1, 2)

        # Frequency display toggle
        layout.addWidget(QLabel("Show Frequency:"), 3, 0)
        self.freq_display_check = QCheckBox()
        self.freq_display_check.setChecked(True)
        layout.addWidget(self.freq_display_check, 3, 1)

        # Frequency display height
        layout.addWidget(QLabel("Freq. Height:"), 4, 0)
        self.freq_height_slider = QSlider(Qt.Horizontal)
        self.freq_height_slider.setRange(50, 300)
        self.freq_height_slider.setValue(150)
        layout.addWidget(self.freq_height_slider, 4, 1)
        self.freq_height_value = QLabel("150")
        layout.addWidget(self.freq_height_value, 4, 2)
        self.freq_height_slider.valueChanged.connect(
            lambda v: self.freq_height_value.setText(str(v)))

        group.setLayout(layout)
        return group

    def _select_base_color(self):
        """Open color dialog for base color selection"""
        color = QColorDialog.getColor(QColor(255, 0, 127), self, "Select Base Color")
        if color.isValid():
            self.base_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_secondary_color(self):
        """Open color dialog for secondary color selection"""
        color = QColorDialog.getColor(QColor(0, 127, 255), self, "Select Secondary Color")
        if color.isValid():
            self.secondary_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def reset_to_defaults(self):
        """Reset all controls to default values"""
        # General controls
        self.segments_slider.setValue(8)
        self.rotation_slider.setValue(50)
        self.symmetry_combo.setCurrentIndex(0)

        # Visual controls
        self.color_mode_combo.setCurrentIndex(0)
        self.base_color_btn.setStyleSheet("background-color: #FF007F")
        self.secondary_color_btn.setStyleSheet("background-color: #007FFF")
        self.shape_combo.setCurrentIndex(0)
        self.blur_slider.setValue(0)
        self.distortion_slider.setValue(0)
        self.particles_slider.setValue(100)
        self.size_slider.setValue(10)
        self.trail_slider.setValue(5)

        # Audio controls
        self.sensitivity_slider.setValue(100)
        self.smoothing_slider.setValue(30)
        self.bass_slider.setValue(100)
        self.mids_slider.setValue(100)
        self.highs_slider.setValue(100)

        # Display controls
        self.fps_spin.setValue(60)
        self.fullscreen_check.setChecked(False)
        self.monitor_combo.setCurrentIndex(0)
        self.freq_display_check.setChecked(True)
        self.freq_height_slider.setValue(150)

    def apply_to_engine(self, engine, audio_processor):
        """Apply all settings to the engine and audio processor"""
        if not engine or not audio_processor:
            return

        # Apply general settings
        engine.set_segments(self.segments_slider.value())
        engine.set_rotation_speed(self.rotation_slider.value() / 100)
        engine.set_symmetry_mode(self.symmetry_combo.currentText().lower())

        # Apply visual settings
        engine.set_color_mode(self.color_mode_combo.currentText().lower())
        base_color = QColor()
        base_color.setNamedColor(self.base_color_btn.styleSheet().split(":")[1].strip())
        engine.set_base_color(base_color)
        secondary_color = QColor()
        secondary_color.setNamedColor(self.secondary_color_btn.styleSheet().split(":")[1].strip())
        engine.set_secondary_color(secondary_color)
        engine.set_shape_type(self.shape_combo.currentText().lower())
        engine.set_blur_amount(self.blur_slider.value())
        engine.set_distortion(self.distortion_slider.value() / 100)
        engine.set_particle_settings(
            self.particles_slider.value(),
            self.size_slider.value(),
            self.trail_slider.value()
        )

        # Apply audio settings
        audio_processor.set_sensitivity(self.sensitivity_slider.value() / 100)
        audio_processor.set_smoothing(self.smoothing_slider.value() / 100)
        engine.set_audio_influence(
            self.bass_slider.value() / 100,
            self.mids_slider.value() / 100,
            self.highs_slider.value() / 100
        )


# =============================================================================
# UI Module: Debug Console
# =============================================================================

class DebugConsole(QWidget):
    """Debug console to display technical information"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Console output
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Courier New", 10))
        layout.addWidget(self.console)

        # Clear button
        clear_btn = QPushButton("Clear Console")
        clear_btn.clicked.connect(self.clear_console)
        layout.addWidget(clear_btn)

        self.setLayout(layout)

    def log(self, message):
        """Add a message to the console"""
        self.console.append(f"[{QTime.currentTime().toString('hh:mm:ss.zzz')}] {message}")

    def clear_console(self):
        """Clear the console"""
        self.console.clear()


# =============================================================================
# Application Module: Main Window
# =============================================================================

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music-Reactive Kaleidoscope Visualizer")
        self.resize(1200, 800)

        # Create central widget with tab layout
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        # Visualization tab
        self.viz_widget = QWidget()
        self.viz_layout = QVBoxLayout()

        # Create visualization widget
        self.visualization = VisualizationWidget()
        self.viz_layout.addWidget(self.visualization)

        # Add frequency display
        self.freq_display = FrequencyDisplayWidget()
        self.freq_display.setMinimumHeight(150)
        self.viz_layout.addWidget(self.freq_display)

        self.viz_widget.setLayout(self.viz_layout)
        self.central_widget.addTab(self.viz_widget, "Visualization")

        # Control panel tab
        self.control_panel = ControlPanel()
        self.central_widget.addTab(self.control_panel, "Controls")

        # Debug console tab
        self.debug_console = DebugConsole()
        self.central_widget.addTab(self.debug_console, "Debug Console")

        # Initialize audio processing
        self.audio_processor = AudioProcessor()
        self.audio_processor.audio_data.connect(self.process_audio)
        self.audio_processor.start()

        # Apply default settings
        self.control_panel.apply_to_engine(
            self.visualization.engine,
            self.audio_processor
        )

        # Connect control panel signals
        self.connect_signals()

        # Log startup
        self.debug_console.log("Application started")
        self.debug_console.log(f"PyAudio initialized, sampling rate: {self.audio_processor.rate}Hz")
        self.debug_console.log(f"Visualization initialized, FPS: {self.visualization.fps}")

    def connect_signals(self):
        """Connect UI control signals to actions"""
        # Connect FPS control
        self.control_panel.fps_spin.valueChanged.connect(self.visualization.set_fps)

        # Connect fullscreen toggle
        self.control_panel.fullscreen_check.stateChanged.connect(self.toggle_fullscreen)

        # Connect frequency display toggle and height
        self.control_panel.freq_display_check.stateChanged.connect(self.toggle_freq_display)
        self.control_panel.freq_height_slider.valueChanged.connect(self.set_freq_display_height)

        # Connect Apply button (we'll update this every time a control changes)
        for obj in self.control_panel.findChildren(QSlider) + \
                  self.control_panel.findChildren(QComboBox) + \
                  self.control_panel.findChildren(QSpinBox) + \
                  self.control_panel.findChildren(QCheckBox):
            if isinstance(obj, QSlider):
                obj.valueChanged.connect(self.apply_settings)
            elif isinstance(obj, QComboBox):
                obj.currentIndexChanged.connect(self.apply_settings)
            elif isinstance(obj, QSpinBox):
                obj.valueChanged.connect(self.apply_settings)
            elif isinstance(obj, QCheckBox):
                obj.stateChanged.connect(self.apply_settings)

        # Connect color buttons
        self.control_panel.base_color_btn.clicked.connect(
            lambda: self.apply_settings_after_delay())
        self.control_panel.secondary_color_btn.clicked.connect(
            lambda: self.apply_settings_after_delay())

    def toggle_freq_display(self, state):
        """Toggle visibility of the frequency display"""
        self.freq_display.setVisible(state == Qt.Checked)
        self.debug_console.log(f"Frequency display {'shown' if state == Qt.Checked else 'hidden'}")

    def set_freq_display_height(self, height):
        """Set the height of the frequency display"""
        self.freq_display.setMinimumHeight(height)
        self.freq_display.setMaximumHeight(height)
        self.debug_console.log(f"Frequency display height set to {height}px")

    def apply_settings(self):
        """Apply all settings from control panel to renderer"""
        self.control_panel.apply_to_engine(
            self.visualization.engine,
            self.audio_processor
        )
        self.debug_console.log("Settings applied")

    def apply_settings_after_delay(self):
        """Apply settings after a short delay (for color dialog)"""
        QTimer.singleShot(100, self.apply_settings)

    def toggle_fullscreen(self, state):
        """Toggle fullscreen mode based on checkbox state"""
        monitor = self.control_panel.monitor_combo.currentIndex()
        self.visualization.toggle_fullscreen(state == Qt.Checked, monitor)
        if state == Qt.Checked:
            self.debug_console.log(f"Entered fullscreen mode on monitor {monitor+1}")
        else:
            self.debug_console.log("Exited fullscreen mode")

    def process_audio(self, spectrum, bands, volume):
        """Process audio data from audio processor"""
        # Update visualizations
        self.visualization.process_audio(spectrum, bands, volume)
        self.freq_display.update_data(spectrum, bands, volume)

    def closeEvent(self, event):
        """Handle application close"""
        # Stop audio processing thread
        self.audio_processor.stop()
        self.debug_console.log("Shutting down...")
        super().closeEvent(event)


# =============================================================================
# Plugin Architecture: Effect Plugins
# =============================================================================

class EffectPlugin:
    """Base class for effect plugins"""
    def __init__(self, name="Generic Effect"):
        self.name = name
        self.enabled = True

    def process(self, image, params):
        """Process the image with the effect"""
        # Base implementation just returns the image unchanged
        return image

    def get_controls(self):
        """Return UI controls for this plugin"""
        # Base implementation has no controls
        return []


class BlurPlugin(EffectPlugin):
    """Blur effect plugin"""
    def __init__(self):
        super().__init__("Blur")
        self.amount = 0

    def process(self, image, params):
        """Apply blur effect"""
        amount = params.get('amount', self.amount)
        if amount <= 0:
            return image

        return EffectProcessor.apply_blur(image, amount)

    def get_controls(self):
        """Get UI controls for blur effect"""
        controls = []

        # Blur amount slider
        blur_label = QLabel("Blur Amount:")
        blur_slider = QSlider(Qt.Horizontal)
        blur_slider.setRange(0, 10)
        blur_slider.setValue(self.amount)
        blur_slider.valueChanged.connect(lambda v: setattr(self, 'amount', v))

        controls.extend([blur_label, blur_slider])
        return controls


class DistortionPlugin(EffectPlugin):
    """Distortion effect plugin"""
    def __init__(self):
        super().__init__("Distortion")
        self.amount = 0

    def process(self, image, params):
        """Apply distortion effect"""
        amount = params.get('amount', self.amount)
        if amount <= 0:
            return image

        center_x = params.get('center_x', image.width() // 2)
        center_y = params.get('center_y', image.height() // 2)
        radius = params.get('radius', min(image.width(), image.height()) // 2)
        rotation = params.get('rotation', 0)

        return EffectProcessor.apply_distortion(
            image, amount, center_x, center_y, radius, rotation
        )

    def get_controls(self):
        """Get UI controls for distortion effect"""
        controls = []

        # Distortion amount slider
        distort_label = QLabel("Distortion Amount:")
        distort_slider = QSlider(Qt.Horizontal)
        distort_slider.setRange(0, 100)
        distort_slider.setValue(int(self.amount * 100))
        distort_slider.valueChanged.connect(lambda v: setattr(self, 'amount', v / 100.0))

        controls.extend([distort_label, distort_slider])
        return controls


# =============================================================================
# Plugin Architecture: Shape Plugins
# =============================================================================

class ShapePlugin:
    """Base class for shape plugins"""
    def __init__(self, name="Generic Shape"):
        self.name = name

    def render(self, painter, x, y, size, color):
        """Render the shape"""
        # Base implementation just draws a point
        painter.setPen(QPen(color, 1))
        painter.drawPoint(int(x), int(y))

    def get_controls(self):
        """Return UI controls for this plugin"""
        # Base implementation has no controls
        return []


class CircleShapePlugin(ShapePlugin):
    """Circle shape plugin"""
    def __init__(self):
        super().__init__("Circle")

    def render(self, painter, x, y, size, color):
        """Render a circle"""
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(int(x), int(y)), int(size), int(size))


class SquareShapePlugin(ShapePlugin):
    """Square shape plugin"""
    def __init__(self):
        super().__init__("Square")

    def render(self, painter, x, y, size, color):
        """Render a square"""
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        rect = QRect(int(x - size/2), int(y - size/2), int(size), int(size))
        painter.drawRect(rect)


class TriangleShapePlugin(ShapePlugin):
    """Triangle shape plugin"""
    def __init__(self):
        super().__init__("Triangle")

    def render(self, painter, x, y, size, color):
        """Render a triangle"""
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        points = [
            QPoint(int(x), int(y - size)),
            QPoint(int(x - size * 0.866), int(y + size * 0.5)),
            QPoint(int(x + size * 0.866), int(y + size * 0.5))
        ]
        painter.drawPolygon(points)


# =============================================================================
# Plugin Architecture: Color Plugins
# =============================================================================

class ColorPlugin:
    """Base class for color generation plugins"""
    def __init__(self, name="Generic Color"):
        self.name = name

    def get_color(self, params):
        """Generate a color based on parameters"""
        # Base implementation returns a default color
        return QColor(255, 255, 255, params.get('alpha', 255))

    def get_controls(self):
        """Return UI controls for this plugin"""
        # Base implementation has no controls
        return []


class SpectrumColorPlugin(ColorPlugin):
    """Spectrum-based color plugin"""
    def __init__(self):
        super().__init__("Spectrum")
        self.saturation = 0.8
        self.brightness_boost = 1.0

    def get_color(self, params):
        """Generate color based on frequency spectrum"""
        freq_index = params.get('freq_index', 0)
        intensity = params.get('intensity', 1.0) * self.brightness_boost
        spectrum_length = params.get('spectrum_length', 100)

        hue = (freq_index / spectrum_length) % 1.0
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, self.saturation, intensity)]

        return QColor(r, g, b, params.get('alpha', 255))

    def get_controls(self):
        """Get UI controls for spectrum color generator"""
        controls = []

        # Saturation slider
        sat_label = QLabel("Saturation:")
        sat_slider = QSlider(Qt.Horizontal)
        sat_slider.setRange(0, 100)
        sat_slider.setValue(int(self.saturation * 100))
        sat_slider.valueChanged.connect(lambda v: setattr(self, 'saturation', v / 100.0))

        # Brightness boost slider
        bright_label = QLabel("Brightness Boost:")
        bright_slider = QSlider(Qt.Horizontal)
        bright_slider.setRange(50, 200)
        bright_slider.setValue(int(self.brightness_boost * 100))
        bright_slider.valueChanged.connect(lambda v: setattr(self, 'brightness_boost', v / 100.0))

        controls.extend([sat_label, sat_slider, bright_label, bright_slider])
        return controls


# =============================================================================
# Entry Point: Application Start
# =============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
