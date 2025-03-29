import math
import random
import colorsys
from PyQt5.QtWidgets import (QLabel, QSlider, QComboBox, QPushButton)
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen

from src.core.visualization_components import EffectProcessor



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
