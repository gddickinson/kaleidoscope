# src/experimental/dimensional_transitions.py
import numpy as np
import math
import random
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QColor, QPainter, QRadialGradient, QPainterPath, QLinearGradient, QPen, QBrush, QTransform

class DimensionalPortal:
    """Creates a portal effect that transitions between dimensions based on audio"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2

        # Portal parameters
        self.portal_radius = min(width, height) // 4
        self.rotation = 0
        self.depth = 0
        self.portal_segments = 12
        self.layer_count = 8
        self.distortion = 0

        # Audio reactivity
        self.bass_influence = 0.8
        self.pulse_amount = 0
        self.pulse_decay = 0.95

        # Color settings
        self.inner_color = QColor(20, 0, 40)
        self.outer_color = QColor(100, 0, 255)
        self.glow_color = QColor(180, 120, 255, 100)

        # Particle system
        self.particles = []
        self.max_particles = 200
        self.initialize_particles()

        # Dimension transition
        self.transition_progress = 0.0
        self.dimension_shapes = ['circle', 'triangle', 'square', 'pentagon', 'hexagon']
        self.current_shape = 'circle'
        self.target_shape = 'circle'

    def initialize_particles(self):
        """Initialize dimensional portal particles"""
        self.particles = []
        for _ in range(self.max_particles):
            self.particles.append({
                'distance': random.uniform(0, self.portal_radius),
                'angle': random.uniform(0, math.pi * 2),
                'speed': random.uniform(0.2, 3.0),
                'size': random.uniform(1, 5),
                'hue': random.uniform(0, 1),
                'orbit_speed': random.uniform(-0.02, 0.02),
                'alive': True
            })

    def resize(self, width, height):
        """Handle resizing of the visualization area"""
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.portal_radius = min(width, height) // 4
        self.initialize_particles()

    def update(self, spectrum, bands, volume, is_beat=False):
        """Update portal based on audio data"""
        bass, mids, highs = bands

        # Update rotation based on mids
        self.rotation += 0.01 + mids * 0.05

        # Update depth based on bass
        target_depth = bass * 15
        self.depth += (target_depth - self.depth) * 0.1

        # Pulse on beat
        if is_beat and volume > 0.4:
            self.pulse_amount = 0.5 + bass * 1.0

            # Potentially change shape on strong beats
            if bass > 0.7 and random.random() < 0.3:
                self.trigger_dimension_shift()

        # Apply pulse decay
        self.pulse_amount *= self.pulse_decay

        # Update distortion based on highs
        self.distortion = highs * 20

        # Update portal segments based on mids
        self.portal_segments = int(6 + mids * 15)

        # Update dimension transition
        if self.current_shape != self.target_shape:
            self.transition_progress += 0.02
            if self.transition_progress >= 1.0:
                self.transition_progress = 0.0
                self.current_shape = self.target_shape

        # Update particles
        self.update_particles(bass, volume)

        if hasattr(self, 'reactive_inner') and self.reactive_inner:
            # Modulate inner color with bass
            h, s, v = self.color_to_hsv(self.original_inner_color)
            # Shift hue based on mids, saturate with bass, brighten with highs
            h = (h + mids * 0.2) % 1.0
            s = min(1.0, s + bass * 0.3)
            v = min(1.0, v + highs * 0.3)
            self.inner_color = self.hsv_to_qcolor(h, s, v)

        if hasattr(self, 'reactive_outer') and self.reactive_outer:
            # Modulate outer color with mids
            h, s, v = self.color_to_hsv(self.original_outer_color)
            h = (h + bass * 0.1) % 1.0
            s = min(1.0, s + highs * 0.2)
            v = min(1.0, v + mids * 0.4)
            self.outer_color = self.hsv_to_qcolor(h, s, v)

        if hasattr(self, 'reactive_glow') and self.reactive_glow:
            # Modulate glow color with highs
            h, s, v = self.color_to_hsv(self.original_glow_color)
            h = (h + (bass + mids) * 0.15) % 1.0
            s = min(1.0, s + mids * 0.1)
            v = min(1.0, v + highs * 0.5)
            new_glow = self.hsv_to_qcolor(h, s, v)
            # Preserve alpha
            alpha = self.glow_color.alpha()
            self.glow_color = new_glow
            self.glow_color.setAlpha(alpha)


    def update_particles(self, bass, volume):
        """Update portal particles"""
        for p in self.particles:
            # Move particles toward/away from center based on bass
            if bass > 0.6 and random.random() < 0.1:
                p['speed'] *= -1  # Reverse direction

            # Update distance
            p['distance'] += p['speed'] * (0.5 + bass)

            # Update angle (rotation around center)
            p['angle'] += p['orbit_speed']

            # Reset particles that go out of bounds
            if p['distance'] < 0 or p['distance'] > self.portal_radius * 1.2:
                p['distance'] = random.uniform(0, self.portal_radius)
                p['angle'] = random.uniform(0, math.pi * 2)
                p['size'] = random.uniform(1, 5) * (1 + volume)
                p['hue'] = (p['hue'] + 0.2) % 1.0  # Shift hue

    def trigger_dimension_shift(self):
        """Start transition to a new dimension (shape)"""
        self.transition_progress = 0.0
        current_index = self.dimension_shapes.index(self.current_shape)

        # Pick a different shape
        available_shapes = self.dimension_shapes.copy()
        available_shapes.remove(self.current_shape)
        self.target_shape = random.choice(available_shapes)

    def render(self, painter):
        """Render the dimensional portal"""
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw outer glow
        glow_radius = self.portal_radius * (1.2 + self.pulse_amount * 0.3)
        gradient = QRadialGradient(self.center_x, self.center_y, glow_radius)
        glow_color = QColor(self.glow_color)
        glow_color.setAlpha(60 + int(self.pulse_amount * 50))
        gradient.setColorAt(0.7, glow_color)
        glow_color.setAlpha(0)
        gradient.setColorAt(1.0, glow_color)
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            int(self.center_x - glow_radius),
            int(self.center_y - glow_radius),
            int(glow_radius * 2),
            int(glow_radius * 2)
        )

        # Draw portal layers
        for i in range(self.layer_count):
            layer_depth = (self.layer_count - i) / self.layer_count
            layer_radius = self.portal_radius * (0.4 + layer_depth * 0.6)
            layer_radius *= (1.0 + self.pulse_amount * 0.2)

            # Create path for current/target shape blend
            path = self.create_dimension_shape(layer_radius, layer_depth)

            # Apply distortion
            if self.distortion > 0:
                path = self.apply_distortion(path, self.distortion * layer_depth)

            # Set color based on depth
            t = layer_depth
            r = int(self.inner_color.red() * (1-t) + self.outer_color.red() * t)
            g = int(self.inner_color.green() * (1-t) + self.outer_color.green() * t)
            b = int(self.inner_color.blue() * (1-t) + self.outer_color.blue() * t)
            color = QColor(r, g, b, 180)

            # Draw the portal layer
            painter.save()
            painter.translate(self.center_x, self.center_y)
            painter.rotate(self.rotation * (i+1) * 10)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(120), 1))
            painter.drawPath(path)
            painter.restore()

        # Draw particles
        for p in self.particles:
            # Calculate position
            x = self.center_x + math.cos(p['angle']) * p['distance']
            y = self.center_y + math.sin(p['angle']) * p['distance']

            # Calculate size based on distance (perspective effect)
            distance_factor = 1.0 - (p['distance'] / self.portal_radius)
            size = p['size'] * (0.5 + distance_factor * 1.5)

            # Set color with distance-based alpha
            h, s, v = p['hue'], 0.8, 0.9
            r, g, b = self.hsv_to_rgb(h, s, v)
            alpha = int(255 * distance_factor * distance_factor)
            color = QColor(r, g, b, alpha)

            # Draw particle
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(x, y), int(size), int(size))

    def create_dimension_shape(self, radius, depth):
        """Create a shape representing the current dimension, with transition if needed"""
        path = QPainterPath()

        # Get points for current and target shapes
        current_points = self.get_shape_points(self.current_shape, radius, self.portal_segments)

        if self.transition_progress > 0:
            # During transition, interpolate between shapes
            target_points = self.get_shape_points(self.target_shape, radius, self.portal_segments)

            # Start the path
            blended_points = []
            for i in range(len(current_points)):
                t = self.transition_progress
                # Apply easing function for smoother transition
                t = 0.5 - 0.5 * math.cos(t * math.pi)

                # Get current and target points
                cx, cy = current_points[i]
                tx, ty = target_points[i % len(target_points)]

                # Interpolate
                x = cx * (1-t) + tx * t
                y = cy * (1-t) + ty * t
                blended_points.append((x, y))

            # Create the path
            path.moveTo(blended_points[0][0], blended_points[0][1])
            for x, y in blended_points[1:]:
                path.lineTo(x, y)
            path.closeSubpath()
        else:
            # No transition, just draw current shape
            path.moveTo(current_points[0][0], current_points[0][1])
            for x, y in current_points[1:]:
                path.lineTo(x, y)
            path.closeSubpath()

        return path

    def get_shape_points(self, shape, radius, segments):
        """Get points for a specific shape"""
        points = []

        if shape == 'circle':
            # Circle uses more points for smoothness
            for i in range(segments):
                angle = 2 * math.pi * i / segments
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius
                points.append((x, y))

        elif shape == 'triangle':
            for i in range(3):
                angle = 2 * math.pi * i / 3 + math.pi/6  # Rotate slightly
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius
                points.append((x, y))

        elif shape == 'square':
            size = radius * 1.8  # Adjust for approximate same area
            half = size / 2
            points = [(-half, -half), (half, -half), (half, half), (-half, half)]

        elif shape == 'pentagon':
            for i in range(5):
                angle = 2 * math.pi * i / 5 - math.pi/2  # Start at top
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius
                points.append((x, y))

        elif shape == 'hexagon':
            for i in range(6):
                angle = 2 * math.pi * i / 6
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius
                points.append((x, y))

        return points

    def apply_distortion(self, path, amount):
        """Apply wave-like distortion to a path"""
        distorted = QPainterPath()

        # Sample points along the path
        step = 0.02  # Smaller step = more detailed distortion
        points = []

        for i in range(int(1/step) + 1):
            t = i * step
            if t > 1.0:
                t = 1.0
            point = path.pointAtPercent(t)
            points.append(point)

        # Apply distortion to sampled points
        distorted_points = []
        for point in points:
            x, y = point.x(), point.y()
            distance = math.sqrt(x*x + y*y)
            angle = math.atan2(y, x)

            # Apply wave distortion to radius
            distort = math.sin(angle * self.portal_segments + self.rotation) * amount
            new_dist = distance + distort

            # Calculate new point
            new_x = math.cos(angle) * new_dist
            new_y = math.sin(angle) * new_dist
            distorted_points.append(QPointF(new_x, new_y))

        # Create new path from distorted points
        if distorted_points:
            distorted.moveTo(distorted_points[0])
            for point in distorted_points[1:]:
                distorted.lineTo(point)
            distorted.closeSubpath()

        return distorted

    def set_inner_color(self, color):
        """Set inner color of the portal"""
        self.inner_color = color

    def set_outer_color(self, color):
        """Set outer color of the portal"""
        self.outer_color = color

    def set_glow_color(self, color):
        """Set glow color of the portal"""
        # Preserve alpha
        alpha = self.glow_color.alpha()
        self.glow_color = color
        self.glow_color.setAlpha(alpha)

    def enable_color_reactivity(self, enable_inner=False, enable_outer=False, enable_glow=False):
        """Enable/disable audio reactivity for colors"""
        self.reactive_inner = enable_inner
        self.reactive_outer = enable_outer
        self.reactive_glow = enable_glow

        # Store original colors for modulation
        if enable_inner:
            self.original_inner_color = QColor(self.inner_color)
        if enable_outer:
            self.original_outer_color = QColor(self.outer_color)
        if enable_glow:
            self.original_glow_color = QColor(self.glow_color)

    @staticmethod
    def hsv_to_rgb(h, s, v):
        """Convert HSV color to RGB values (0-255)"""
        r, g, b = 0, 0, 0

        h = h % 1.0
        i = int(h * 6)
        f = (h * 6) - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return int(r * 255), int(g * 255), int(b * 255)

    # Add these utility functions to each effect class
    def color_to_hsv(self, color):
        """Convert QColor to HSV values (0-1 range)"""
        h = color.hueF()
        s = color.saturationF()
        v = color.valueF()
        return h, s, v

    def hsv_to_qcolor(self, h, s, v):
        """Convert HSV values to QColor"""
        color = QColor()
        color.setHsvF(h, s, v)
        return color
