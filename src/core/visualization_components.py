"""
Music-Reactive Kaleidoscope Visualization Module
- Contains core particle and rendering components
"""

import math
import random
import colorsys
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QImage, QRadialGradient
import numpy as np



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
        self.z = random.uniform(-100, 100)  # Add Z coordinate for 3D
        self.size = random.uniform(particle_size * 0.5, particle_size * 1.5)
        self.speed = random.uniform(0.5, 2.0)
        self.angle = random.uniform(0, math.pi * 2)
        self.z_speed = random.uniform(-0.5, 0.5)  # Z-axis movement speed
        self.trail = []
        self.trail_length = trail_length
        self.color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.current_size = self.size

    def update(self, speed_mod, size_mod, z_mod=1.0):
        """Update particle position and trail"""
        self.angle += 0.02 * speed_mod
        self.x += math.cos(self.angle) * self.speed * speed_mod * 0.5
        self.y += math.sin(self.angle) * self.speed * speed_mod * 0.5
        self.z += self.z_speed * z_mod  # Update Z position

        # Z-axis boundaries (wrap around)
        if self.z > 200 or self.z < -200:
            self.z_speed = -self.z_speed

        # Store trail positions
        self.trail.append((self.x, self.y, self.z))
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


class WireframeCube:
    """3D Wireframe cube that reacts to audio"""
    def __init__(self, size=100):
        self.size = size
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.position = [0, 0, 0]  # Center position
        self.vertices = self._generate_vertices()
        self.edges = self._generate_edges()
        self.pulse_size = 1.0
        self.base_color = QColor(255, 255, 255)
        self.edge_thickness = 2

    def _generate_vertices(self):
        """Generate the 8 vertices of a cube"""
        half = self.size / 2
        return [
            [-half, -half, -half],  # 0: back bottom left
            [half, -half, -half],   # 1: back bottom right
            [half, half, -half],    # 2: back top right
            [-half, half, -half],   # 3: back top left
            [-half, -half, half],   # 4: front bottom left
            [half, -half, half],    # 5: front bottom right
            [half, half, half],     # 6: front top right
            [-half, half, half]     # 7: front top left
        ]

    def _generate_edges(self):
        """Define the 12 edges connecting vertices"""
        return [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Back face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Front face
            (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
        ]

    def update(self, bass, mids, highs, volume, rotation_speed=1.0):
        """Update cube rotation and effects based on audio"""
        # Rotate cube based on different frequency bands, modified by rotation speed
        self.rotation_x += bass * 0.01 * rotation_speed
        self.rotation_y += mids * 0.008 * rotation_speed
        self.rotation_z += highs * 0.005 * rotation_speed

        # Pulse size with beat detection
        self.pulse_size = 1.0 + volume * 0.5

        # Change color based on frequencies or color mode
        r = min(255, int(bass * 150 + 100))
        g = min(255, int(mids * 150 + 100))
        b = min(255, int(highs * 150 + 100))
        self.base_color = QColor(r, g, b)

        # Adjust edge thickness with volume
        self.edge_thickness = 1 + int(volume * 3)

    def render(self, painter, center_x, center_y, perspective=800):
        """Render the wireframe cube with perspective projection"""
        # Set up pen for drawing
        pen = QPen(self.base_color)
        pen.setWidth(self.edge_thickness)
        painter.setPen(pen)

        # Get current size accounting for audio-reactive pulse
        current_size = self.size * self.pulse_size

        # Transform and project vertices
        projected_vertices = []
        for vertex in self.vertices:
            # Scale by current size
            x, y, z = [v * self.pulse_size for v in vertex]

            # Apply 3D rotations
            x, y, z = self._rotate_point(x, y, z)

            # Apply perspective projection
            scale = perspective / (perspective + z)
            px = center_x + x * scale
            py = center_y + y * scale

            projected_vertices.append((px, py))

        # Draw edges
        for edge in self.edges:
            start = projected_vertices[edge[0]]
            end = projected_vertices[edge[1]]
            painter.drawLine(int(start[0]), int(start[1]), int(end[0]), int(end[1]))

    def _rotate_point(self, x, y, z):
        """Apply 3D rotation to a point"""
        # Rotate around X axis
        y_rot = y * math.cos(self.rotation_x) - z * math.sin(self.rotation_x)
        z_rot = y * math.sin(self.rotation_x) + z * math.cos(self.rotation_x)
        y, z = y_rot, z_rot

        # Rotate around Y axis
        x_rot = x * math.cos(self.rotation_y) + z * math.sin(self.rotation_y)
        z_rot = -x * math.sin(self.rotation_y) + z * math.cos(self.rotation_y)
        x, z = x_rot, z_rot

        # Rotate around Z axis
        x_rot = x * math.cos(self.rotation_z) - y * math.sin(self.rotation_z)
        y_rot = x * math.sin(self.rotation_z) + y * math.cos(self.rotation_z)
        x, y = x_rot, y_rot

        return x, y, z

class CircularWaveform:
    """Circular waveform display that surrounds the kaleidoscope"""
    def __init__(self, radius=300, inner_radius_pct=0.8, num_samples=128):
        self.radius = radius  # Outer radius
        self.inner_radius_pct = inner_radius_pct  # Inner radius as percentage of outer
        self.inner_radius = radius * inner_radius_pct
        self.num_samples = num_samples  # Number of sample points to use
        self.waveform_data = np.zeros(num_samples)  # Current waveform data
        self.smoothed_data = np.zeros(num_samples)  # Smoothed data for display
        self.smoothing = 0.3  # Smoothing factor
        self.line_width = 2  # Line width
        self.color = QColor(255, 255, 255, 180)  # Default color with alpha
        self.secondary_color = QColor(0, 200, 255, 180)  # For gradient effect
        self.rotate_speed = 0.01  # Rotation speed
        self.rotation = 0  # Current rotation
        self.use_gradient = True  # Whether to use gradient coloring
        self.amplitude = 1.0  # Amplitude multiplier
        self.bass_influence = 0.5  # How much bass affects the waveform
        self.show_reflection = True  # Show reflection/mirror
        self.reflection_alpha = 0.3  # Reflection opacity

    def update(self, raw_audio_data, spectrum, volume, bass_value):
        """Update the waveform with new audio data"""
        # Resample raw audio to number of points we want to display
        # (We'll use spectrum data as a simpler alternative to resampling raw audio)
        if len(spectrum) > self.num_samples:
            # Downsample
            step = len(spectrum) / self.num_samples
            self.waveform_data = np.array([spectrum[int(i * step)] for i in range(self.num_samples)])
        else:
            # Upsample or use as is
            self.waveform_data = np.interp(
                np.linspace(0, len(spectrum), self.num_samples),
                np.arange(len(spectrum)),
                spectrum
            )

        # Apply smoothing
        self.smoothed_data = self.smoothed_data * self.smoothing + self.waveform_data * (1 - self.smoothing)

        # Scale based on overall volume and bass
        self.amplitude = 0.5 + (volume * 1.5) + (bass_value * self.bass_influence)

        # Update rotation
        self.rotation += self.rotate_speed
        if self.rotation > 2 * math.pi:
            self.rotation -= 2 * math.pi

    def render(self, painter, center_x, center_y):
        """Render the circular waveform"""
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Calculate the actual inner radius to use
        inner_radius = self.inner_radius

        # Draw the waveform
        for i in range(self.num_samples):
            # Calculate angle for this sample
            angle = (i / self.num_samples * 2 * math.pi) + self.rotation

            # Get normalized value and apply amplitude
            value = self.smoothed_data[i] * self.amplitude

            # Clamp value to reasonable range
            value = max(0, min(1, value))

            # Calculate start and end points
            start_x = center_x + math.cos(angle) * inner_radius
            start_y = center_y + math.sin(angle) * inner_radius

            end_x = center_x + math.cos(angle) * (inner_radius + (value * (self.radius - inner_radius)))
            end_y = center_y + math.sin(angle) * (inner_radius + (value * (self.radius - inner_radius)))

            # Set color with gradient based on position or value
            if self.use_gradient:
                # Use gradient based on amplitude/value
                ratio = value
                r = int(self.color.red() * (1 - ratio) + self.secondary_color.red() * ratio)
                g = int(self.color.green() * (1 - ratio) + self.secondary_color.green() * ratio)
                b = int(self.color.blue() * (1 - ratio) + self.secondary_color.blue() * ratio)
                a = int(self.color.alpha() * (1 - ratio) + self.secondary_color.alpha() * ratio)

                line_color = QColor(r, g, b, a)
            else:
                line_color = self.color

            # Draw line
            pen = QPen(line_color)
            pen.setWidth(self.line_width)
            painter.setPen(pen)
            painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))

            # Draw reflection if enabled
            if self.show_reflection:
                reflection_color = QColor(line_color)
                reflection_color.setAlpha(int(line_color.alpha() * self.reflection_alpha))
                reflection_pen = QPen(reflection_color)
                reflection_pen.setWidth(self.line_width)
                painter.setPen(reflection_pen)

                # Reflect point across the center
                reflected_start_x = center_x - (start_x - center_x)
                reflected_start_y = center_y - (start_y - center_y)
                reflected_end_x = center_x - (end_x - center_x)
                reflected_end_y = center_y - (end_y - center_y)

                painter.drawLine(int(reflected_start_x), int(reflected_start_y),
                                int(reflected_end_x), int(reflected_end_y))

    def set_radius(self, radius, inner_radius_pct=None):
        """Set the radius of the circular waveform"""
        self.radius = radius
        if inner_radius_pct is not None:
            self.inner_radius_pct = inner_radius_pct
        self.inner_radius = self.radius * self.inner_radius_pct

    def set_colors(self, primary_color, secondary_color=None):
        """Set the colors for the waveform"""
        self.color = primary_color
        if secondary_color:
            self.secondary_color = secondary_color
            self.use_gradient = True
        else:
            self.use_gradient = False

    def set_line_width(self, width):
        """Set the line width"""
        self.line_width = width

    def set_rotation_speed(self, speed):
        """Set the rotation speed"""
        self.rotate_speed = speed

    def set_reflection(self, show, alpha=0.3):
        """Enable/disable reflection and set opacity"""
        self.show_reflection = show
        self.reflection_alpha = alpha
