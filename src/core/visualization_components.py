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
import sys



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


class WireframeShape:
    """Base class for all 3D wireframe shapes"""
    def __init__(self, size=100):
        self.size = size
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.position = [0, 0, 0]  # Center position
        self.vertices = []
        self.edges = []
        self.pulse_size = 1.0
        self.base_color = QColor(255, 255, 255)
        self.edge_thickness = 2
        self.morph_target = None
        self.morph_progress = 0.0
        self.edge_opacity = 255  # Alpha value for edges
        self.show_edges = True  # New flag to toggle edge visibility

        # Audio-reactive parameters
        self.rotation_speed_x = 0.01
        self.rotation_speed_y = 0.008
        self.rotation_speed_z = 0.005
        self.pulse_strength = 0.5
        self.color_reactivity = 1.0
        self.thickness_reactivity = 1.0

        self._generate_shape()

    def _generate_shape(self):
        """Generate vertices and edges for the shape - override in subclasses"""
        pass

    def update(self, bass, mids, highs, volume, rotation_speed=1.0):
        """Update shape rotation and effects based on audio"""
        # Rotate based on different frequency bands, modified by rotation speed
        self.rotation_x += bass * self.rotation_speed_x * rotation_speed
        self.rotation_y += mids * self.rotation_speed_y * rotation_speed
        self.rotation_z += highs * self.rotation_speed_z * rotation_speed

        # Pulse size with beat detection
        self.pulse_size = 1.0 + volume * self.pulse_strength

        # Change color based on frequencies and reactivity
        r = min(255, int(bass * 150 * self.color_reactivity + 100))
        g = min(255, int(mids * 150 * self.color_reactivity + 100))
        b = min(255, int(highs * 150 * self.color_reactivity + 100))
        self.base_color = QColor(r, g, b, self.edge_opacity)

        # Adjust edge thickness with volume and reactivity
        self.edge_thickness = 1 + int(volume * 3 * self.thickness_reactivity)

        # Update morph if we have a target
        if self.morph_target and self.morph_progress < 1.0:
            self.morph_progress += 0.02  # Gradual morphing
            if self.morph_progress > 1.0:
                self.morph_progress = 1.0
                # Swap vertices when morph is complete
                if self.morph_progress >= 1.0:
                    self.vertices = self.morph_target.vertices.copy()
                    self.edges = self.morph_target.edges.copy()
                    self.morph_target = None
                    self.morph_progress = 0.0

    def render(self, painter, center_x, center_y, perspective=800):
        """Render the wireframe shape with perspective projection"""
        # Set up pen for drawing
        pen = QPen(self.base_color)
        pen.setWidth(self.edge_thickness)
        painter.setPen(pen)

        # Get current size accounting for audio-reactive pulse
        current_size = self.size * self.pulse_size

        # If in morphing state, prepare both sets of vertices
        if self.morph_target and self.morph_progress < 1.0:
            # Transform and project vertices for both current and target
            main_vertices = self._transform_vertices(self.vertices, current_size, center_x, center_y, perspective)
            target_vertices = self._transform_vertices(
                self.morph_target.vertices,
                current_size,
                center_x,
                center_y,
                perspective
            )

            # Interpolate between vertices based on morph progress
            projected_vertices = []
            for i in range(len(main_vertices)):
                if i < len(target_vertices):
                    # Linear interpolation between vertices
                    px = main_vertices[i][0] * (1 - self.morph_progress) + target_vertices[i][0] * self.morph_progress
                    py = main_vertices[i][1] * (1 - self.morph_progress) + target_vertices[i][1] * self.morph_progress
                    projected_vertices.append((px, py))
                else:
                    projected_vertices.append(main_vertices[i])

            # Draw edges if enabled
            if self.show_edges:
                for edge in self.edges:
                    if edge[0] < len(projected_vertices) and edge[1] < len(projected_vertices):
                        start = projected_vertices[edge[0]]
                        end = projected_vertices[edge[1]]
                        painter.drawLine(int(start[0]), int(start[1]), int(end[0]), int(end[1]))
        else:
            # Transform and project vertices
            projected_vertices = self._transform_vertices(self.vertices, current_size, center_x, center_y, perspective)

            # Draw edges if enabled
            if self.show_edges:
                for edge in self.edges:
                    start = projected_vertices[edge[0]]
                    end = projected_vertices[edge[1]]
                    painter.drawLine(int(start[0]), int(start[1]), int(end[0]), int(end[1]))

    def _transform_vertices(self, vertices, current_size, center_x, center_y, perspective=800):
        """Transform and project vertices with 3D rotation and perspective"""
        projected_vertices = []
        for vertex in vertices:
            # Scale by current size
            x = vertex[0] * current_size
            y = vertex[1] * current_size
            z = vertex[2] * current_size

            # Apply 3D rotations
            x, y, z = self._rotate_point(x, y, z)

            # Apply perspective projection
            scale = perspective / (perspective + z)
            px = center_x + x * scale
            py = center_y + y * scale

            projected_vertices.append((px, py))

        return projected_vertices

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

    def start_morph(self, target_shape):
        """Begin morphing to another shape"""
        self.morph_target = target_shape
        self.morph_progress = 0.0

    def set_audio_reactivity(self, rotation, pulse, color, thickness):
        """Set how reactive the shape is to audio parameters"""
        self.rotation_speed_x = 0.01 * rotation
        self.rotation_speed_y = 0.008 * rotation
        self.rotation_speed_z = 0.005 * rotation
        self.pulse_strength = 0.5 * pulse
        self.color_reactivity = color
        self.thickness_reactivity = thickness

    def set_colors(self, color, opacity=255):
        """Set the base color and opacity"""
        self.base_color = color
        self.edge_opacity = opacity
        # Update alpha in the color
        self.base_color.setAlpha(opacity)


class WireframeCube(WireframeShape):
    """3D Wireframe cube"""
    def _generate_shape(self):
        """Generate the 8 vertices and 12 edges of a cube"""
        half = 0.5  # Using unit coordinates (-0.5 to 0.5)
        self.vertices = [
            [-half, -half, -half],  # 0: back bottom left
            [half, -half, -half],   # 1: back bottom right
            [half, half, -half],    # 2: back top right
            [-half, half, -half],   # 3: back top left
            [-half, -half, half],   # 4: front bottom left
            [half, -half, half],    # 5: front bottom right
            [half, half, half],     # 6: front top right
            [-half, half, half]     # 7: front top left
        ]

        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Back face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Front face
            (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
        ]


class WireframePyramid(WireframeShape):
    """3D Wireframe pyramid with square base"""
    def _generate_shape(self):
        """Generate the 5 vertices and 8 edges of a pyramid"""
        half = 0.5  # Using unit coordinates
        self.vertices = [
            [-half, -half, -half],  # 0: base front left
            [half, -half, -half],   # 1: base front right
            [half, -half, half],    # 2: base back right
            [-half, -half, half],   # 3: base back left
            [0, half, 0]            # 4: apex
        ]

        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Base
            (0, 4), (1, 4), (2, 4), (3, 4)   # Edges to apex
        ]


class WireframeSphere(WireframeShape):
    """3D Wireframe sphere approximation using latitude and longitude lines"""
    def _generate_shape(self):
        """Generate vertices and edges for sphere approximation"""
        # Parameters for detail level
        slices = 12  # longitude lines
        stacks = 6   # latitude lines

        # Generate vertices
        self.vertices = []

        # Add top and bottom poles
        self.vertices.append([0, 0.5, 0])  # Top pole
        self.vertices.append([0, -0.5, 0])  # Bottom pole

        # Generate vertices for each stack and slice
        for i in range(1, stacks):
            phi = math.pi * i / stacks  # 0 to pi
            y = 0.5 * math.cos(phi)
            radius = 0.5 * math.sin(phi)

            for j in range(slices):
                theta = 2 * math.pi * j / slices  # 0 to 2pi
                x = radius * math.cos(theta)
                z = radius * math.sin(theta)
                self.vertices.append([x, y, z])

        # Generate edges
        self.edges = []

        # Connect the poles to the first and last stacks
        for i in range(slices):
            # Connect top pole to first stack
            self.edges.append((0, i + 2))

            # Connect bottom pole to last stack
            self.edges.append((1, i + 2 + (stacks - 2) * slices))

        # Connect vertices in the same stack (longitude lines)
        for i in range(1, stacks):
            stack_start = 2 + (i - 1) * slices
            for j in range(slices):
                next_j = (j + 1) % slices
                self.edges.append((stack_start + j, stack_start + next_j))

        # Connect vertices between stacks (latitude lines)
        for i in range(1, stacks - 1):
            for j in range(slices):
                self.edges.append((2 + (i - 1) * slices + j, 2 + i * slices + j))


class WireframeOctahedron(WireframeShape):
    """3D Wireframe octahedron (8-sided shape)"""
    def _generate_shape(self):
        """Generate the 6 vertices and 12 edges of an octahedron"""
        self.vertices = [
            [0.5, 0, 0],   # 0: right
            [-0.5, 0, 0],  # 1: left
            [0, 0.5, 0],   # 2: top
            [0, -0.5, 0],  # 3: bottom
            [0, 0, 0.5],   # 4: front
            [0, 0, -0.5]   # 5: back
        ]

        self.edges = [
            (0, 2), (0, 3), (0, 4), (0, 5),  # Edges from right vertex
            (1, 2), (1, 3), (1, 4), (1, 5),  # Edges from left vertex
            (2, 4), (2, 5), (3, 4), (3, 5)   # Edges between top/bottom and front/back
        ]


class WireframeDodecahedron(WireframeShape):
    """3D Wireframe dodecahedron (12-sided shape)"""
    def _generate_shape(self):
        """Generate vertices and edges of a dodecahedron"""
        # Golden ratio for proper dodecahedron proportions
        phi = (1 + math.sqrt(5)) / 2

        # Generate the vertices
        self.vertices = [
            # Cube vertices scaled by 1/phi
            [0.5/phi, 0.5/phi, 0.5/phi], [-0.5/phi, 0.5/phi, 0.5/phi],
            [-0.5/phi, -0.5/phi, 0.5/phi], [0.5/phi, -0.5/phi, 0.5/phi],
            [0.5/phi, 0.5/phi, -0.5/phi], [-0.5/phi, 0.5/phi, -0.5/phi],
            [-0.5/phi, -0.5/phi, -0.5/phi], [0.5/phi, -0.5/phi, -0.5/phi],

            # Additional vertices for dodecahedron
            [0, 0.5, phi/(2*phi)], [0, -0.5, phi/(2*phi)],
            [0, 0.5, -phi/(2*phi)], [0, -0.5, -phi/(2*phi)],
            [phi/(2*phi), 0, 0.5], [-phi/(2*phi), 0, 0.5],
            [phi/(2*phi), 0, -0.5], [-phi/(2*phi), 0, -0.5],
            [0.5, phi/(2*phi), 0], [-0.5, phi/(2*phi), 0],
            [0.5, -phi/(2*phi), 0], [-0.5, -phi/(2*phi), 0]
        ]

        # Scale vertices to fit in unit cube
        max_dim = max([max(abs(v[0]), abs(v[1]), abs(v[2])) for v in self.vertices])
        self.vertices = [[v[0]/max_dim, v[1]/max_dim, v[2]/max_dim] for v in self.vertices]

        # Define edges (simplified for clarity - actual dodecahedron has 30 edges)
        # We'll define the key edges to give the appearance of a dodecahedron
        self.edges = [
            # Pentagonal face edges
            (0, 12), (12, 4), (4, 16), (16, 8), (8, 0),
            (1, 8), (8, 16), (16, 17), (17, 13), (13, 1),
            (2, 13), (13, 19), (19, 9), (9, 3), (3, 2),
            (0, 3), (3, 9), (9, 18), (18, 12), (12, 0),
            (4, 14), (14, 7), (7, 11), (11, 10), (10, 4),
            (5, 10), (10, 11), (11, 19), (19, 15), (15, 5),
            (6, 15), (15, 19), (19, 13), (13, 17), (17, 6),
            (7, 18), (18, 9), (9, 19), (19, 11), (11, 7),
            (0, 8), (8, 1), (1, 13), (13, 2), (2, 0),
            (14, 4), (4, 10), (10, 5), (5, 15), (15, 14),
            (6, 17), (17, 16), (16, 4), (4, 14), (14, 6),
            (7, 14), (14, 18), (18, 3), (3, 0), (0, 7)
        ]


class WireframeTetrahedron(WireframeShape):
    """3D Wireframe tetrahedron (4-sided shape)"""
    def _generate_shape(self):
        """Generate the 4 vertices and 6 edges of a tetrahedron"""
        # Vertices at the corners of a regular tetrahedron
        self.vertices = [
            [0, 0.5, 0],                    # Top vertex
            [-0.5, -0.289, 0.289],          # Bottom left
            [0.5, -0.289, 0.289],           # Bottom right
            [0, -0.289, -0.577]             # Bottom back
        ]

        # Connect every vertex to every other vertex
        self.edges = [
            (0, 1), (0, 2), (0, 3),  # Edges from top vertex
            (1, 2), (1, 3), (2, 3)   # Base edges
        ]


class WireframeTorus(WireframeShape):
    """3D Wireframe torus (donut shape)"""
    def _generate_shape(self):
        """Generate vertices and edges of a torus"""
        # Parameters
        R = 0.3  # Major radius (distance from center to center of tube)
        r = 0.1  # Minor radius (radius of the tube)
        segments = 16  # Number of segments in each ring
        rings = 16     # Number of rings

        # Generate vertices
        self.vertices = []
        for i in range(rings):
            theta = 2 * math.pi * i / rings
            cosTheta = math.cos(theta)
            sinTheta = math.sin(theta)

            for j in range(segments):
                phi = 2 * math.pi * j / segments
                cosPhi = math.cos(phi)
                sinPhi = math.sin(phi)

                x = (R + r * cosPhi) * cosTheta
                y = r * sinPhi
                z = (R + r * cosPhi) * sinTheta

                self.vertices.append([x, y, z])

        # Generate edges
        self.edges = []

        # Connect vertices in the same ring
        for i in range(rings):
            ring_start = i * segments
            for j in range(segments):
                next_j = (j + 1) % segments
                self.edges.append((ring_start + j, ring_start + next_j))

        # Connect vertices between rings
        for i in range(rings):
            next_i = (i + 1) % rings
            for j in range(segments):
                self.edges.append((i * segments + j, next_i * segments + j))


# Shape factory to create different shapes based on type
class WireframeShapeFactory:
    """Factory for creating different wireframe shapes"""
    @staticmethod
    def create_shape(shape_type, size=100):
        """Create a wireframe shape based on the specified type"""
        # Convert to lowercase for case-insensitive matching
        shape_type = shape_type.lower()

        # Map of shape types to classes
        shape_map = {
            "cube": WireframeCube,
            "pyramid": WireframePyramid,
            "sphere": WireframeSphere,
            "octahedron": WireframeOctahedron,
            "dodecahedron": WireframeDodecahedron,
            "tetrahedron": WireframeTetrahedron,
            "torus": WireframeTorus
        }

        # Debug output
        print(f"Creating shape of type: {shape_type}")

        if shape_type in shape_map:
            return shape_map[shape_type](size)
        else:
            # If not found, log the error and default to cube
            print(f"Shape type '{shape_type}' not found. Available types: {list(shape_map.keys())}")
            return WireframeCube(size)



class WireframeManager:
    """Manager for multiple wireframe shapes with transitions and effects"""
    def __init__(self, size=100):
        self.base_size = size
        self.current_shape = None
        self.shapes = []  # List of active shapes
        self.available_shapes = ["cube", "pyramid", "sphere", "octahedron",
                               "dodecahedron", "tetrahedron", "torus"]

        # Audio-reactive parameters
        self.beat_sensitivity = 1.0
        self.auto_morph = False
        self.morph_on_beat = False
        self.rotation_speed = 1.0
        self.multi_shape_mode = False
        self.shape_count = 1
        self.beat_counter = 0
        self.last_beat_time = 0
        self.beat_interval = 30  # Frames between auto shape changes

        # Visual effects
        self.show_edges = True
        self.show_vertices = False
        self.vertex_size = 3
        self.edge_glow = False
        self.glow_intensity = 0.5
        self.show_echo = False
        self.echo_count = 3
        self.echo_opacity = 0.3
        self.echo_spacing = 0.2  # Spacing between echo shapes
        self.show_edges = True  # Add this flag for edge visibility

        # Color effects
        self.color_mode = "audio_reactive"  # "audio_reactive", "solid", "rainbow", "gradient"
        self.custom_color = QColor(255, 255, 255)
        self.secondary_color = QColor(0, 150, 255)
        self.rainbow_speed = 0.02
        self.rainbow_offset = 0

        # Initialize with a default cube
        self._create_default_shapes()

    def _create_default_shapes(self):
        """Create initial shape(s)"""
        self.current_shape = WireframeShapeFactory.create_shape("cube", self.base_size)
        self.shapes = [self.current_shape]

        # If multi-shape mode, create additional shapes
        if self.multi_shape_mode:
            for i in range(1, self.shape_count):
                shape_type = self.available_shapes[i % len(self.available_shapes)]
                shape = WireframeShapeFactory.create_shape(shape_type, self.base_size)
                # Offset rotation to differentiate shapes
                shape.rotation_x = math.pi * i / self.shape_count
                shape.rotation_z = math.pi * i / self.shape_count
                self.shapes.append(shape)

    def update(self, bass, mids, highs, volume, is_beat):
        """Update all shapes based on audio and settings"""
        # Update rainbow effect if enabled
        if self.color_mode == "rainbow":
            self.rainbow_offset += self.rainbow_speed
            if self.rainbow_offset > 1.0:
                self.rainbow_offset -= 1.0

        # Handle auto morphing and beat detection
        self._handle_morphing(is_beat, volume)

        # Update all shapes with audio data
        for shape in self.shapes:
            # Apply audio update
            shape.update(bass, mids, highs, volume, self.rotation_speed)

            # Apply color based on mode
            if self.color_mode == "audio_reactive":
                # Color is set in the shape's update method
                pass
            elif self.color_mode == "solid":
                shape.set_colors(self.custom_color)
            elif self.color_mode == "rainbow":
                # Calculate color based on position in rainbow and rotation
                hue = (self.rainbow_offset + shape.rotation_z / math.pi) % 1.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.8, 0.9)]
                shape.set_colors(QColor(r, g, b))
            elif self.color_mode == "gradient":
                # Use gradient based on rotation
                ratio = (math.sin(shape.rotation_z * 2) + 1) / 2
                r = int(self.custom_color.red() * (1 - ratio) + self.secondary_color.red() * ratio)
                g = int(self.custom_color.green() * (1 - ratio) + self.secondary_color.green() * ratio)
                b = int(self.custom_color.blue() * (1 - ratio) + self.secondary_color.blue() * ratio)
                shape.set_colors(QColor(r, g, b))

    def _handle_morphing(self, is_beat, volume):
        """Handle shape morphing based on beats and settings"""
        # Increment beat counter
        if is_beat and volume > 0.1:
            self.beat_counter += 1
            self.last_beat_time = 0

            # If set to morph on beat, check if we should morph
            if self.morph_on_beat and self.beat_counter % 4 == 0:  # Every 4th beat
                self._morph_to_random_shape()
        else:
            self.last_beat_time += 1

        # Auto morphing based on time
        if self.auto_morph and self.last_beat_time > self.beat_interval:
            self._morph_to_random_shape()
            self.last_beat_time = 0

    def _morph_to_random_shape(self):
        """Start morphing to a random new shape"""
        # Pick a random shape type different from the current one
        available = [s for s in self.available_shapes
                    if not isinstance(self.current_shape,
                                     getattr(sys.modules[__name__], f"Wireframe{s.capitalize()}"))]

        if available:
            shape_type = random.choice(available)
            new_shape = WireframeShapeFactory.create_shape(shape_type, self.base_size)

            # Start morphing
            for shape in self.shapes:
                # Create a new instance of the target shape
                target = WireframeShapeFactory.create_shape(shape_type, self.base_size)
                # Match current rotation
                target.rotation_x = shape.rotation_x
                target.rotation_y = shape.rotation_y
                target.rotation_z = shape.rotation_z
                # Start the morph
                shape.start_morph(target)

            # Update current shape type
            self.current_shape = new_shape

    def render(self, painter, center_x, center_y, perspective=800):
        """Render all shapes with effects"""
        # Save the painter state for echo effect
        painter.save()

        # Render echo effect if enabled
        if self.show_echo:
            self._render_echo_effect(painter, center_x, center_y, perspective)

        # Render all active shapes
        for shape in self.shapes:
            # Apply the edge visibility setting to the shape
            shape.show_edges = self.show_edges

            # Render glow effect if enabled
            if self.edge_glow:
                self._render_glow_effect(painter, shape, center_x, center_y, perspective)

            # Render the shape
            shape.render(painter, center_x, center_y, perspective)

            # Render vertices if enabled
            if self.show_vertices:
                self._render_vertices(painter, shape, center_x, center_y, perspective)

        # Restore painter state
        painter.restore()

    def _render_echo_effect(self, painter, center_x, center_y, perspective):
        """Render echo/trail effect for shapes"""
        for i in range(self.echo_count):
            # Decrease opacity for each echo
            echo_opacity = int(255 * self.echo_opacity * (1 - i / self.echo_count))

            for shape in self.shapes:
                # Create temporary shape for echo
                echo_shape = type(shape)(shape.size)
                echo_shape.vertices = shape.vertices.copy()
                echo_shape.edges = shape.edges.copy()

                # Set echo rotation as an offset from current rotation
                offset = (i + 1) * self.echo_spacing
                echo_shape.rotation_x = shape.rotation_x - offset
                echo_shape.rotation_y = shape.rotation_y - offset
                echo_shape.rotation_z = shape.rotation_z - offset

                # Set echo color
                echo_color = QColor(shape.base_color)
                echo_color.setAlpha(echo_opacity)
                echo_shape.set_colors(echo_color)

                # Reduce line width for echoes
                echo_shape.edge_thickness = max(1, shape.edge_thickness - i)

                # Render the echo with proper center coordinates
                echo_shape.render(painter, center_x, center_y, perspective)

    def _render_glow_effect(self, painter, shape, center_x, center_y, perspective):
            """Render glow effect for shape edges"""
            # Create a softer, wider stroke for the glow
            glow_color = QColor(shape.base_color)
            glow_color.setAlpha(100)  # Semitransparent

            glow_pen = QPen(glow_color)
            glow_pen.setWidth(shape.edge_thickness + 4)  # Wider than the actual edge

            # Save the current pen
            old_pen = painter.pen()

            # Set glow pen and render the shape
            painter.setPen(glow_pen)

            # Transform and project vertices
            projected_vertices = []
            for vertex in shape.vertices:
                # Scale by current size
                x = vertex[0] * shape.size * shape.pulse_size
                y = vertex[1] * shape.size * shape.pulse_size
                z = vertex[2] * shape.size * shape.pulse_size

                # Apply 3D rotations
                x, y, z = shape._rotate_point(x, y, z)

                # Apply perspective projection
                scale = perspective / (perspective + z)
                px = center_x + x * scale
                py = center_y + y * scale

                projected_vertices.append((px, py))

            # Draw glow edges
            for edge in shape.edges:
                start = projected_vertices[edge[0]]
                end = projected_vertices[edge[1]]
                painter.drawLine(int(start[0]), int(start[1]), int(end[0]), int(end[1]))

            # Restore original pen
            painter.setPen(old_pen)

    def _render_vertices(self, painter, shape, center_x, center_y, perspective):
        """Render vertices as points"""
        # Transform and project vertices
        projected_vertices = []
        for vertex in shape.vertices:
            # Scale by current size
            x = vertex[0] * shape.size * shape.pulse_size
            y = vertex[1] * shape.size * shape.pulse_size
            z = vertex[2] * shape.size * shape.pulse_size

            # Apply 3D rotations
            x, y, z = shape._rotate_point(x, y, z)

            # Apply perspective projection
            scale = perspective / (perspective + z)
            px = center_x + x * scale
            py = center_y + y * scale

            projected_vertices.append((px, py))

        # Use current shape color with alpha
        vertex_color = QColor(shape.base_color)
        painter.setBrush(QBrush(vertex_color))
        painter.setPen(Qt.NoPen)

        # Draw vertices as small circles
        for px, py in projected_vertices:
            painter.drawEllipse(int(px - self.vertex_size/2), int(py - self.vertex_size/2),
                               self.vertex_size, self.vertex_size)

    def set_shape(self, shape_type, morph=False):
        """Switch to a new shape type"""
        if morph:
            # Morph to the new shape type
            for shape in self.shapes:
                target = WireframeShapeFactory.create_shape(shape_type, self.base_size)
                # Match current rotation
                target.rotation_x = shape.rotation_x
                target.rotation_y = shape.rotation_y
                target.rotation_z = shape.rotation_z
                # Start the morph
                shape.start_morph(target)
        else:
            # Replace shapes immediately
            self.shapes = []
            self.current_shape = WireframeShapeFactory.create_shape(shape_type, self.base_size)
            self.shapes.append(self.current_shape)

            # If multi-shape mode, create additional shapes
            if self.multi_shape_mode:
                for i in range(1, self.shape_count):
                    shape = WireframeShapeFactory.create_shape(shape_type, self.base_size)
                    # Offset rotation to differentiate shapes
                    shape.rotation_x = math.pi * i / self.shape_count
                    shape.rotation_z = math.pi * i / self.shape_count
                    self.shapes.append(shape)

    def set_multi_shape_mode(self, enabled, count=3):
        """Enable/disable multiple shapes mode"""
        self.multi_shape_mode = enabled
        self.shape_count = count if enabled else 1

        # Update shapes based on new settings
        current_type = type(self.current_shape).__name__.replace("Wireframe", "").lower()
        self.set_shape(current_type)

    def set_size(self, size):
        """Set the base size for all shapes"""
        self.base_size = size
        for shape in self.shapes:
            shape.size = size

    def set_rotation_speed(self, speed):
        """Set the rotation speed multiplier"""
        self.rotation_speed = speed

    def set_color_mode(self, mode):
        """Set the color mode"""
        self.color_mode = mode

    def set_custom_colors(self, primary, secondary=None):
        """Set custom colors for solid and gradient modes"""
        self.custom_color = primary
        if secondary:
            self.secondary_color = secondary

    def set_effects(self, show_vertices, vertex_size, edge_glow, glow_intensity):
        """Set visual effects options"""
        self.show_vertices = show_vertices
        self.vertex_size = vertex_size
        self.edge_glow = edge_glow
        self.glow_intensity = glow_intensity

    def set_echo_effect(self, enabled, count=3, opacity=0.3, spacing=0.2):
        """Set echo/trail effect options"""
        self.show_echo = enabled
        self.echo_count = count
        self.echo_opacity = opacity
        self.echo_spacing = spacing

    def set_beat_response(self, auto_morph, morph_on_beat, beat_interval=30):
        """Set beat detection and auto-morph options"""
        self.auto_morph = auto_morph
        self.morph_on_beat = morph_on_beat
        self.beat_interval = beat_interval


    def set_edges_visible(self, visible):
        """Set whether edges are visible"""
        self.show_edges = visible

        # Update all existing shapes
        for shape in self.shapes:
            shape.show_edges = visible
