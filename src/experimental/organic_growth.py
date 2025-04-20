# src/experimental/organic_growth.py
import numpy as np
import math
import random
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QPainterPath, QLinearGradient

class AudioMycelia:
    """Creates organic growth patterns that respond to audio"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2

        # Mycelia parameters
        self.branch_count = 5
        self.max_branches = 25
        self.growth_rate = 3.0
        self.split_chance = 0.05
        self.max_depth = 5
        self.min_branch_length = 30
        self.max_branch_length = 150

        # Branch array format:
        # [start_x, start_y, end_x, end_y, angle, length, age, growth, depth, energy]
        self.branches = []
        self.initialize_branches()

        # Colors
        self.base_color = QColor(80, 220, 120)
        self.tip_color = QColor(220, 255, 200)
        self.bg_color = QColor(10, 20, 10, 100)

        # Audio reactivity
        self.energy = 1.0
        self.growth_energy = 0.0
        self.pulse_amount = 0.0
        self.pulse_decay = 0.97

    def initialize_branches(self):
        """Initialize mycelia branches from center"""
        self.branches = []

        # Create initial branches
        for i in range(self.branch_count):
            angle = random.uniform(0, math.pi * 2)
            length = random.uniform(50, 100)

            start_x = self.center_x
            start_y = self.center_y
            end_x = start_x + math.cos(angle) * length
            end_y = start_y + math.sin(angle) * length

            # [start_x, start_y, end_x, end_y, angle, length, age, growth, depth, energy]
            branch = [start_x, start_y, end_x, end_y, angle, length, 0, 1.0, 0, 1.0]
            self.branches.append(branch)

    def resize(self, width, height):
        """Handle resizing of the visualization area"""
        ratio_x = width / self.width
        ratio_y = height / self.height

        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2

        # Scale all branches
        for branch in self.branches:
            branch[0] *= ratio_x  # start_x
            branch[1] *= ratio_y  # start_y
            branch[2] *= ratio_x  # end_x
            branch[3] *= ratio_y  # end_y
            branch[5] *= (ratio_x + ratio_y) / 2  # length

    def update(self, spectrum, bands, volume, is_beat=False):
        """Update organic growth based on audio data"""
        bass, mids, highs = bands

        # Update energy based on audio
        target_energy = 0.5 + volume * 3.0
        self.energy += (target_energy - self.energy) * 0.1
        self.energy = max(0.1, min(3.0, self.energy))

        # Growth energy increases with highs and mids
        growth_boost = highs * 0.7 + mids * 0.3
        self.growth_energy = 0.3 + growth_boost * 2.0

        # Pulse on beat
        if is_beat and volume > 0.4:
            self.pulse_amount = 0.5 + bass * 1.5

            # Trigger more splits on strong beats
            if bass > 0.7:
                self.split_chance = 0.15  # Higher split chance
            else:
                self.split_chance = 0.05  # Normal split chance
        else:
            # Decay pulse
            self.pulse_amount *= self.pulse_decay

        # Update each branch
        new_branches = []
        dead_branches = []

        for i, branch in enumerate(self.branches):
            # Unpack branch data
            start_x, start_y, end_x, end_y, angle, length, age, growth, depth, energy = branch

            # Update branch age
            age += 0.01 * self.energy

            # Update branch growth
            if growth < 1.0:
                # Still growing
                growth += 0.02 * self.growth_energy

                # Update end position based on growth
                end_x = start_x + math.cos(angle) * length * growth
                end_y = start_y + math.sin(angle) * length * growth

                # Update branch
                branch[2] = end_x
                branch[3] = end_y
                branch[6] = age
                branch[7] = growth
            else:
                # Fully grown - check for splitting
                if (len(self.branches) + len(new_branches) < self.max_branches and
                    depth < self.max_depth and
                    random.random() < self.split_chance * self.energy):

                    # Create new branches
                    branch_count = random.choices([1, 2], weights=[0.7, 0.3])[0]

                    for _ in range(branch_count):
                        # Angle deviation from parent
                        angle_dev = random.uniform(-math.pi/4, math.pi/4)
                        new_angle = angle + angle_dev

                        # New branch length
                        new_length = random.uniform(
                            self.min_branch_length,
                            self.max_branch_length
                        ) * (1.0 - depth / self.max_depth) * self.energy

                        # Create new branch
                        new_branch = [
                            end_x, end_y,  # Start at parent's end
                            end_x, end_y,  # End will update as it grows
                            new_angle,
                            new_length,
                            0,  # age
                            0.0,  # growth (starts at 0)
                            depth + 1,  # depth
                            energy * 0.9  # energy (slightly decreases)
                        ]

                        new_branches.append(new_branch)

                    # Reduce energy of parent branch after splitting
                    branch[9] *= 0.7

            # Decrease energy over time
            branch[9] -= 0.001 * (depth + 1)

            # Mark branches with no energy for removal
            if branch[9] <= 0:
                dead_branches.append(i)

        # Remove dead branches (backwards to avoid index issues)
        for i in sorted(dead_branches, reverse=True):
            if i < len(self.branches):
                self.branches.pop(i)

        # Add new branches
        self.branches.extend(new_branches)

    def render(self, painter):
        """Render the organic growth pattern"""
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw semi-transparent background
        painter.fillRect(0, 0, self.width, self.height, self.bg_color)

        # Sort branches by depth for proper rendering
        sorted_branches = sorted(self.branches, key=lambda b: b[8])

        # Draw each branch
        for branch in sorted_branches:
            self.draw_branch(painter, branch)

    def draw_branch(self, painter, branch):
        """Draw a single branch with organic appearance"""
        start_x, start_y, end_x, end_y, angle, length, age, growth, depth, energy = branch

        # Skip if zero length or no energy
        if length <= 0 or energy <= 0:
            return

        # Calculate thickness based on depth and energy
        max_thickness = 10 * (1.0 - depth / self.max_depth) * energy
        thickness = max(1, max_thickness)

        # Add pulse effect
        thickness *= (1.0 + self.pulse_amount * 0.3)

        # Create gradient along the branch
        branch_path = QPainterPath()
        branch_path.moveTo(start_x, start_y)

        # For a more organic look, add a slight curve
        # Control point perpendicular to the branch direction
        perp_x = -(end_y - start_y) * 0.2
        perp_y = (end_x - start_x) * 0.2

        # Add some randomness to the curve
        perp_x *= random.uniform(0.8, 1.2)
        perp_y *= random.uniform(0.8, 1.2)

        ctrl_x = (start_x + end_x) / 2 + perp_x
        ctrl_y = (start_y + end_y) / 2 + perp_y

        branch_path.quadTo(ctrl_x, ctrl_y, end_x, end_y)

        # Create gradient
        gradient = QLinearGradient(start_x, start_y, end_x, end_y)

        # Base color depends on depth
        r = int(self.base_color.red() * (1.0 - depth / self.max_depth * 0.5))
        g = int(self.base_color.green() * (1.0 - depth / self.max_depth * 0.3))
        b = int(self.base_color.blue() * (1.0 - depth / self.max_depth * 0.2))

        branch_base_color = QColor(r, g, b)

        # Tip color is brighter
        branch_tip_color = QColor(
            min(255, r + 60),
            min(255, g + 60),
            min(255, b + 40)
        )

        # Set colors with energy-based alpha
        alpha = int(min(255, energy * 180))
        branch_base_color.setAlpha(alpha)
        branch_tip_color.setAlpha(alpha)

        gradient.setColorAt(0.0, branch_base_color)
        gradient.setColorAt(1.0, branch_tip_color)

        # Draw the branch
        pen = QPen(QBrush(gradient), thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(branch_path)

        # Draw glowing tip for growing branches
        if growth < 1.0:
            tip_size = thickness * 2
            glow_color = QColor(self.tip_color)
            glow_color.setAlpha(int(150 * energy))

            painter.setBrush(QBrush(glow_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(end_x, end_y), int(tip_size), int(tip_size))

    def set_base_color(self, color):
        """Set the base color of mycelia branches"""
        self.base_color = color

    def set_tip_color(self, color):
        """Set the tip color of mycelia branches"""
        self.tip_color = color

    def set_bg_color(self, color, alpha=100):
        """Set the background color of the effect"""
        self.bg_color = color
        self.bg_color.setAlpha(alpha)

    def enable_color_reactivity(self, enable_base=False, enable_tip=False, enable_bg=False):
        """Enable/disable audio reactivity for colors"""
        self.reactive_base = enable_base
        self.reactive_tip = enable_tip
        self.reactive_bg = enable_bg

        # Store original colors
        if enable_base:
            self.original_base_color = QColor(self.base_color)
        if enable_tip:
            self.original_tip_color = QColor(self.tip_color)
        if enable_bg:
            self.original_bg_color = QColor(self.bg_color)
