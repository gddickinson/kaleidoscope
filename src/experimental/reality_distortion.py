# src/experimental/reality_distortion.py
import numpy as np
import math
import random
from PyQt5.QtCore import Qt, QPointF, QRect
from PyQt5.QtGui import QColor, QPainter, QImage, QPainterPath, QRadialGradient, QBrush, QPen, QTransform

class GravitationalLens:
    """Creates reality-distortion effect similar to gravitational lensing"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2

        # Lens parameters
        self.lens_count = 3
        self.lenses = []
        self.initialize_lenses()

        # Distortion strength
        self.distortion_strength = 1.0
        self.max_distortion = 50

        # Grid parameters for visualization
        self.grid_size = 40
        self.grid_visible = True

        # Buffers
        self.buffer = QImage(width, height, QImage.Format_ARGB32)
        self.buffer.fill(Qt.transparent)

        # Audio reactivity
        self.energy = 1.0
        self.lens_pulse = 0.0
        self.pulse_decay = 0.95

        # Colors
        self.grid_color = QColor(50, 50, 80, 100)
        self.lens_color = QColor(100, 150, 255, 10)
        self.edge_color = QColor(50, 100, 200, 50)

    def initialize_lenses(self):
        """Initialize gravitational lenses"""
        self.lenses = []

        for i in range(self.lens_count):
            lens = {
                'x': random.randint(self.width // 5, self.width * 4 // 5),
                'y': random.randint(self.height // 5, self.height * 4 // 5),
                'mass': random.uniform(0.5, 2.0),
                'radius': random.randint(50, 150),
                'motion_x': random.uniform(-1, 1),
                'motion_y': random.uniform(-1, 1),
                'rotation': random.uniform(0, math.pi * 2),
                'rotation_speed': random.uniform(-0.02, 0.02)
            }
            self.lenses.append(lens)

    def resize(self, width, height):
        """Handle resizing of the visualization area"""
        ratio_x = width / self.width
        ratio_y = height / self.height

        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2

        # Scale lens positions
        for lens in self.lenses:
            lens['x'] *= ratio_x
            lens['y'] *= ratio_y
            lens['radius'] *= min(ratio_x, ratio_y)

        # Update buffer
        self.buffer = QImage(width, height, QImage.Format_ARGB32)
        self.buffer.fill(Qt.transparent)

        # Grid size scales with resolution
        self.grid_size = int(40 * min(ratio_x, ratio_y))

    def update(self, spectrum, bands, volume, is_beat=False):
        """Update reality distortion based on audio data"""
        bass, mids, highs = bands

        # Update energy based on audio
        target_energy = 0.5 + volume * 3.0
        self.energy += (target_energy - self.energy) * 0.1
        self.energy = max(0.5, min(4.0, self.energy))

        # Distortion strength varies with mids and highs
        self.distortion_strength = 0.5 + mids * 2.0 + highs * 1.0

        # Pulse on beat
        if is_beat and volume > 0.4:
            self.lens_pulse = 0.5 + bass * 1.5
        else:
            # Decay pulse
            self.lens_pulse *= self.pulse_decay

        # Update each lens
        for lens in self.lenses:
            # Apply audio influence to lens mass
            lens['mass'] = 0.5 + bass * 1.0 + random.uniform(-0.1, 0.1)

            # Update lens position with motion
            lens['x'] += lens['motion_x'] * self.energy
            lens['y'] += lens['motion_y'] * self.energy

            # Bounce off edges
            if lens['x'] < lens['radius'] or lens['x'] > self.width - lens['radius']:
                lens['motion_x'] *= -1
            if lens['y'] < lens['radius'] or lens['y'] > self.height - lens['radius']:
                lens['motion_y'] *= -1

            # Update rotation
            lens['rotation'] += lens['rotation_speed'] * self.energy

            # Add some randomness to motion on beats
            if is_beat and bass > 0.7:
                lens['motion_x'] += random.uniform(-0.2, 0.2)
                lens['motion_y'] += random.uniform(-0.2, 0.2)

                # Limit motion speed
                max_speed = 2.0
                lens['motion_x'] = max(-max_speed, min(max_speed, lens['motion_x']))
                lens['motion_y'] = max(-max_speed, min(max_speed, lens['motion_y']))

    def render(self, painter):
        """Render the reality distortion effect"""
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Clear buffer
        self.buffer.fill(Qt.transparent)
        buffer_painter = QPainter(self.buffer)
        buffer_painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw reference grid
        if self.grid_visible:
            self.draw_grid(buffer_painter)

        # Apply distortion effect
        self.apply_distortion(buffer_painter)

        # Draw lens visuals
        self.draw_lenses(buffer_painter)

        buffer_painter.end()

        # Draw buffer to main painter
        painter.drawImage(0, 0, self.buffer)

    def draw_grid(self, painter):
        """Draw a reference grid that will be distorted"""
        painter.setPen(QPen(QColor(50, 50, 80, 100), 1, Qt.SolidLine))

        # Draw vertical lines
        for x in range(0, self.width, self.grid_size):
            painter.drawLine(x, 0, x, self.height)

        # Draw horizontal lines
        for y in range(0, self.height, self.grid_size):
            painter.drawLine(0, y, self.width, y)

    def apply_distortion(self, painter):
        """Apply gravitational lensing distortion to the grid"""
        # Draw distorted grid
        painter.setPen(QPen(QColor(150, 200, 255, 150), 1.5, Qt.SolidLine))

        # Distort vertical lines
        for x in range(0, self.width, self.grid_size):
            # Create path for distorted line
            path = QPainterPath()
            path.moveTo(x, 0)

            for y in range(0, self.height, 5):
                # Calculate distortion for this point
                dx, dy = self.calculate_distortion(x, y)
                path.lineTo(x + dx, y + dy)

            painter.drawPath(path)

        # Distort horizontal lines
        for y in range(0, self.height, self.grid_size):
            # Create path for distorted line
            path = QPainterPath()
            path.moveTo(0, y)

            for x in range(0, self.width, 5):
                # Calculate distortion for this point
                dx, dy = self.calculate_distortion(x, y)
                path.lineTo(x + dx, y + dy)

            painter.drawPath(path)

    def calculate_distortion(self, x, y):
        """Calculate distortion vector for a point based on all lenses"""
        total_dx = 0
        total_dy = 0

        for lens in self.lenses:
            # Vector from lens to point
            dx = x - lens['x']
            dy = y - lens['y']

            # Distance
            distance = math.sqrt(dx*dx + dy*dy)

            # Avoid division by zero
            if distance < 1:
                continue

            # Normalize direction vector
            nx = dx / distance
            ny = dy / distance

            # Calculate distortion strength based on distance
            # Use inverse square law for gravitational-like effect
            strength = lens['mass'] * self.distortion_strength
            factor = strength / (1 + distance / lens['radius'])

            # Limit maximum distortion
            factor = min(factor, self.max_distortion / distance)

            # Apply some rotation for a more interesting effect
            cos_rot = math.cos(lens['rotation'])
            sin_rot = math.sin(lens['rotation'])

            # Add pulse effect to distortion
            factor *= (1.0 + self.lens_pulse * 0.5)

            # Calculate distortion vector (with rotation)
            dist_x = -nx * factor * cos_rot + ny * factor * sin_rot
            dist_y = -ny * factor * cos_rot - nx * factor * sin_rot

            # Add to total distortion
            total_dx += dist_x
            total_dy += dist_y

        return total_dx, total_dy

    def draw_lenses(self, painter):
        """Draw visual representation of the lenses"""
        for lens in self.lenses:
            # Calculate visual radius with pulse
            visual_radius = lens['radius'] * (1.0 + self.lens_pulse * 0.3)

            # Create gradient for lens appearance
            gradient = QRadialGradient(lens['x'], lens['y'], visual_radius)

            # Core is nearly transparent
            center_color = QColor(100, 150, 255, 10)

            # Edge is more visible
            edge_color = QColor(50, 100, 200, 50)

            gradient.setColorAt(0, center_color)
            gradient.setColorAt(0.7, edge_color)
            gradient.setColorAt(1.0, QColor(20, 50, 120, 0))

            # Draw lens
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                int(lens['x'] - visual_radius),
                int(lens['y'] - visual_radius),
                int(visual_radius * 2),
                int(visual_radius * 2)
            )

            # Draw lens center
            center_size = lens['radius'] * 0.1 * (1.0 + self.lens_pulse * 0.5)
            painter.setBrush(QBrush(QColor(200, 220, 255, 150)))
            painter.drawEllipse(
                int(lens['x'] - center_size),
                int(lens['y'] - center_size),
                int(center_size * 2),
                int(center_size * 2)
            )

    def set_grid_color(self, color, alpha=100):
        """Set the grid color"""
        self.grid_color = color
        self.grid_color.setAlpha(alpha)

    def set_lens_color(self, color):
        """Set the lens color"""
        self.lens_color = color
        # Preserve original alpha
        self.lens_color.setAlpha(10)  # Or whatever default alpha was

    def set_edge_color(self, color):
        """Set the edge color"""
        self.edge_color = color
        # Preserve original alpha
        self.edge_color.setAlpha(50)  # Or whatever default alpha was
