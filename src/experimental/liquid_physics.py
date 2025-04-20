# src/experimental/liquid_physics.py
import numpy as np
import math
import random
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QColor, QPainter, QRadialGradient, QPainterPath, QLinearGradient, QPen, QBrush, QTransform

class LiquidMetal:
    """Creates a liquid metal effect that reacts to audio frequencies"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2

        # Liquid parameters
        self.blob_count = 3
        self.point_count = 24  # Points per blob
        self.elasticity = 0.3
        self.damping = 0.8
        self.tension = 0.1

        # Blob points array format: [x, y, vx, vy, base_radius]
        self.blobs = []
        self.initialize_blobs()

        # Surface properties
        self.reflection_offset = 20
        self.ripple_count = 5
        self.ripple_speed = 0.05
        self.ripple_intensity = 0.2
        self.ripple_phases = [random.uniform(0, math.pi*2) for _ in range(self.ripple_count)]

        # Colors
        self.metal_color = QColor(200, 200, 220)
        self.highlight_color = QColor(255, 255, 255)
        self.shadow_color = QColor(70, 70, 100)

    def initialize_blobs(self):
        """Initialize liquid metal blobs"""
        self.blobs = []

        for i in range(self.blob_count):
            blob = {
                'points': [],
                'center_x': random.randint(self.width//4, self.width*3//4),
                'center_y': random.randint(self.height//4, self.height*3//4),
                'radius': random.randint(50, 120),
                'phase': random.uniform(0, math.pi*2),
                'drift_x': random.uniform(-0.5, 0.5),
                'drift_y': random.uniform(-0.5, 0.5)
            }

            # Create points around the blob
            for j in range(self.point_count):
                angle = 2 * math.pi * j / self.point_count
                x = blob['center_x'] + math.cos(angle) * blob['radius']
                y = blob['center_y'] + math.sin(angle) * blob['radius']

                # Format: [x, y, vx, vy, base_radius]
                point = [x, y, 0, 0, blob['radius']]
                blob['points'].append(point)

            self.blobs.append(blob)

    def resize(self, width, height):
        """Handle resizing of the visualization area"""
        scale_x = width / self.width
        scale_y = height / self.height

        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2

        # Scale blob positions
        for blob in self.blobs:
            blob['center_x'] *= scale_x
            blob['center_y'] *= scale_y
            blob['radius'] *= min(scale_x, scale_y)

            for point in blob['points']:
                point[0] *= scale_x
                point[1] *= scale_y
                point[4] *= min(scale_x, scale_y)  # Scale base radius

    def update(self, spectrum, bands, volume, is_beat=False):
        """Update liquid metal physics based on audio data"""
        bass, mids, highs = bands

        # Apply audio forces to blobs
        bass_force = bass * 15.0
        mid_force = mids * 8.0
        high_force = highs * 5.0

        # Update ripple phases
        for i in range(self.ripple_count):
            self.ripple_phases[i] = (self.ripple_phases[i] + self.ripple_speed) % (math.pi*2)

        # Set ripple intensity based on mids
        self.ripple_intensity = 0.1 + mids * 0.4

        # Update blob physics
        for b, blob in enumerate(self.blobs):
            # Update blob center with drift
            blob['center_x'] += blob['drift_x']
            blob['center_y'] += blob['drift_y']

            # Bounce off edges
            if blob['center_x'] < blob['radius'] or blob['center_x'] > self.width - blob['radius']:
                blob['drift_x'] *= -1
            if blob['center_y'] < blob['radius'] or blob['center_y'] > self.height - blob['radius']:
                blob['drift_y'] *= -1

            # Apply audio forces to each point
            for i, point in enumerate(blob['points']):
                # Get point data
                x, y, vx, vy, base_radius = point

                # Calculate angle from center
                dx = x - blob['center_x']
                dy = y - blob['center_y']
                angle = math.atan2(dy, dx)

                # Calculate current distance from center
                dist = math.sqrt(dx*dx + dy*dy)

                # Calculate target position (where the point should be)
                # Add ripple effect based on audio
                ripple = 0
                for i in range(self.ripple_count):
                    ripple += math.sin(angle * (i+1) + self.ripple_phases[i]) * self.ripple_intensity

                # Bass affects the base radius
                radius_mod = base_radius * (1.0 + bass * 0.3 + ripple)

                # Apply different forces based on frequency bands and point position
                angle_factor = i / self.point_count

                # Low frequencies affect bottom points more
                if angle_factor > 0.25 and angle_factor < 0.75:
                    radius_mod += bass_force * math.sin(angle_factor * math.pi) * 0.5

                # Mid frequencies affect side points
                if angle_factor < 0.25 or angle_factor > 0.75:
                    radius_mod += mid_force * math.cos(angle_factor * math.pi * 2) * 0.3

                # High frequencies create small ripples everywhere
                radius_mod += high_force * math.sin(angle * 5 + blob['phase']) * 0.2

                # On beat, create a pulse
                if is_beat and volume > 0.5:
                    radius_mod += base_radius * 0.2

                # Calculate target position
                target_x = blob['center_x'] + math.cos(angle) * radius_mod
                target_y = blob['center_y'] + math.sin(angle) * radius_mod

                # Apply spring physics
                force_x = (target_x - x) * self.tension
                force_y = (target_y - y) * self.tension

                # Update velocity
                vx = vx * self.damping + force_x
                vy = vy * self.damping + force_y

                # Update position
                x += vx
                y += vy

                # Store updated point
                point[0] = x
                point[1] = y
                point[2] = vx
                point[3] = vy

            # Update blob phase
            blob['phase'] = (blob['phase'] + 0.05) % (math.pi*2)

    def render(self, painter):
        """Render the liquid metal effect"""
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Render each blob
        for blob in self.blobs:
            self.render_blob(painter, blob)

    def render_blob(self, painter, blob):
        """Render a single liquid metal blob"""
        # Create path from points
        path = QPainterPath()

        points = blob['points']
        if not points:
            return

        # Start path with first point
        path.moveTo(points[0][0], points[0][1])

        # Add curved segments between points for smoothness
        for i in range(len(points)):
            # Get current point and next point (wrapping around)
            curr = points[i]
            next_idx = (i + 1) % len(points)
            next_point = points[next_idx]

            # Calculate control points for smooth curve
            # Use 1/3 distance between points for control points
            dx = next_point[0] - curr[0]
            dy = next_point[1] - curr[1]

            # Calculate perpendicular direction for control points
            length = math.sqrt(dx*dx + dy*dy)
            if length < 0.001:
                continue

            nx = -dy / length
            ny = dx / length

            # Control point distance (adjust for smoother or sharper curves)
            ctrl_dist = length * 0.4

            # Create control points with some perpendicular offset for natural curves
            ctrl1_x = curr[0] + dx * 0.25 + nx * ctrl_dist
            ctrl1_y = curr[1] + dy * 0.25 + ny * ctrl_dist

            ctrl2_x = curr[0] + dx * 0.75 - nx * ctrl_dist
            ctrl2_y = curr[1] + dy * 0.75 - ny * ctrl_dist

            # Add cubic curve to path
            path.cubicTo(
                ctrl1_x, ctrl1_y,
                ctrl2_x, ctrl2_y,
                next_point[0], next_point[1]
            )

        # Create metal surface gradient
        center_x = 0
        center_y = 0

        # Calculate center of blob for gradient
        for point in points:
            center_x += point[0]
            center_y += point[1]

        center_x /= len(points)
        center_y /= len(points)

        # Create metallic gradient
        gradient = QLinearGradient(
            center_x - 100, center_y - 100,
            center_x + 100, center_y + 100
        )

        # Create metallic look with multiple color stops
        gradient.setColorAt(0.0, self.highlight_color)
        gradient.setColorAt(0.3, self.metal_color)
        gradient.setColorAt(0.6, self.metal_color.darker(110))
        gradient.setColorAt(0.8, self.shadow_color)
        gradient.setColorAt(1.0, self.metal_color.darker(120))

        # Draw the liquid metal blob
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self.metal_color.darker(130), 1))
        painter.drawPath(path)

        # Add highlight reflection (a curved line across the top)
        highlight_path = QPainterPath()

        # Find the top points of the blob (approximately)
        top_left = None
        top_right = None

        # Find points closest to top left and top right quadrants
        min_dist_left = float('inf')
        min_dist_right = float('inf')

        for point in points:
            x, y = point[0], point[1]

            # Check if in top half
            if y < center_y:
                # Left side
                if x < center_x:
                    dist = (x - (center_x - blob['radius'])) ** 2 + (y - (center_y - blob['radius'])) ** 2
                    if dist < min_dist_left:
                        min_dist_left = dist
                        top_left = (x, y)
                # Right side
                else:
                    dist = (x - (center_x + blob['radius'])) ** 2 + (y - (center_y - blob['radius'])) ** 2
                    if dist < min_dist_right:
                        min_dist_right = dist
                        top_right = (x, y)

        if top_left and top_right:
            # Create curved highlight
            highlight_path.moveTo(top_left[0], top_left[1])

            # Control point for curve
            ctrl_x = (top_left[0] + top_right[0]) / 2
            ctrl_y = min(top_left[1], top_right[1]) - blob['radius'] * 0.2

            highlight_path.quadTo(ctrl_x, ctrl_y, top_right[0], top_right[1])

            # Draw highlight
            highlight_pen = QPen(self.highlight_color, 3)
            highlight_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(highlight_pen)
            painter.drawPath(highlight_path)

        # Add a subtle second highlight for extra realism
        if top_left and top_right:
            highlight2_path = QPainterPath()
            highlight2_path.moveTo(top_left[0] + 10, top_left[1] + 15)

            # Control point slightly below the main highlight
            ctrl_x = (top_left[0] + top_right[0]) / 2
            ctrl_y = min(top_left[1], top_right[1]) - blob['radius'] * 0.1 + 20

            highlight2_path.quadTo(ctrl_x, ctrl_y, top_right[0] - 10, top_right[1] + 15)

            # Draw second highlight with lower opacity
            highlight2_color = QColor(self.highlight_color)
            highlight2_color.setAlpha(90)
            highlight2_pen = QPen(highlight2_color, 2)
            highlight2_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(highlight2_pen)
            painter.drawPath(highlight2_path)

    def set_metal_color(self, color):
        """Set the main metal color"""
        self.metal_color = color

    def set_highlight_color(self, color):
        """Set the highlight color"""
        self.highlight_color = color

    def set_shadow_color(self, color):
        """Set the shadow color"""
        self.shadow_color = color

    def enable_color_reactivity(self, enable_metal=False, enable_highlight=False, enable_shadow=False):
        """Enable/disable audio reactivity for colors"""
        self.reactive_metal = enable_metal
        self.reactive_highlight = enable_highlight
        self.reactive_shadow = enable_shadow

        # Store original colors
        if enable_metal:
            self.original_metal_color = QColor(self.metal_color)
        if enable_highlight:
            self.original_highlight_color = QColor(self.highlight_color)
        if enable_shadow:
            self.original_shadow_color = QColor(self.shadow_color)

    def enable_color_reactivity(self, enable_grid=False, enable_lens=False, enable_edge=False):
        """Enable/disable audio reactivity for colors"""
        self.reactive_grid = enable_grid
        self.reactive_lens = enable_lens
        self.reactive_edge = enable_edge

        # Store original colors
        if enable_grid:
            self.original_grid_color = QColor(self.grid_color)
        if enable_lens:
            self.original_lens_color = QColor(self.lens_color)
        if enable_edge:
            self.original_edge_color = QColor(self.edge_color)
