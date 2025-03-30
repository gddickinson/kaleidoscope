import numpy as np
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor

from src.core.kaleidoscope_engine import KaleidoscopeEngine



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

    def process_audio(self, spectrum, bands, volume, raw_audio=None):
        """Process audio data and update visualization"""
        if self.engine:
            self.engine.update(spectrum, bands, volume, raw_audio)

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
