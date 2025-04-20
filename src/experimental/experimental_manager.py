# src/experimental/experimental_manager.py
import numpy as np
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QPainter, QColor, QImage

from src.experimental.dimensional_transitions import DimensionalPortal
from src.experimental.liquid_physics import LiquidMetal
from src.experimental.organic_growth import AudioMycelia
from src.experimental.reality_distortion import GravitationalLens

class ExperimentalEffectsManager(QObject):
    """Manager for experimental audio-reactive effects"""

    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = min(width, height) // 2
        self.global_opacity = 0.8  # Default opacity (80%)

        # Initialize effects
        self.effects = {
            'dimensional_portal': DimensionalPortal(width, height),
            'liquid_metal': LiquidMetal(width, height),
            'audio_mycelia': AudioMycelia(width, height),
            'gravitational_lens': GravitationalLens(width, height)
        }

        # Effect settings
        self.active_effects = {}  # Maps effect_name -> (enabled, intensity)
        self.transition_speed = 0.05  # Speed to blend effects
        self.blend_buffer = QImage(width, height, QImage.Format_ARGB32)

        # By default, disable all effects
        for effect_name in self.effects:
            self.active_effects[effect_name] = (False, 0.0)

    def resize(self, width, height):
        """Handle resizing of the visualization area"""
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = min(width, height) // 2
        self.blend_buffer = QImage(width, height, QImage.Format_ARGB32)

        # Resize all effects
        for effect in self.effects.values():
            effect.resize(width, height)

    def update(self, spectrum, bands, volume, is_beat=False):
        """Update all active effects with audio data"""
        # Update each effect
        for effect_name, effect in self.effects.items():
            enabled, intensity = self.active_effects[effect_name]

            # Skip disabled effects
            if not enabled and intensity <= 0.001:
                continue

            # Update the effect with audio data
            effect.update(spectrum, bands, volume, is_beat)

            # Handle transitions for enabling/disabling effects
            if enabled and intensity < 1.0:
                # Fade in
                self.active_effects[effect_name] = (True, min(1.0, intensity + self.transition_speed))
            elif not enabled and intensity > 0.0:
                # Fade out
                new_intensity = max(0.0, intensity - self.transition_speed)
                self.active_effects[effect_name] = (False, new_intensity)


    def render(self, painter):
        """Render all active effects"""
        active_count = sum(1 for _, intensity in self.active_effects.values() if intensity > 0.001)

        if active_count == 0:
            return  # No active effects

        # Save painter state to restore opacity later
        painter.save()

        # Apply global opacity
        painter.setOpacity(self.global_opacity)

        if active_count > 1:
            self.blend_buffer.fill(Qt.transparent)
            blend_painter = QPainter(self.blend_buffer)

            # Render each active effect with its intensity
            for effect_name, effect in self.effects.items():
                _, intensity = self.active_effects[effect_name]
                if intensity > 0.001:
                    blend_painter.setOpacity(intensity)
                    effect.render(blend_painter)

            blend_painter.end()

            # Draw the blended result
            painter.drawImage(0, 0, self.blend_buffer)
        else:
            # If only one effect is active, render directly
            for effect_name, effect in self.effects.items():
                _, intensity = self.active_effects[effect_name]
                if intensity > 0.001:
                    painter.setOpacity(intensity * self.global_opacity)
                    effect.render(painter)

        # Restore painter state
        painter.restore()

    def set_effect_enabled(self, effect_name, enabled):
        """Enable or disable a specific effect"""
        if effect_name in self.active_effects:
            current_enabled, intensity = self.active_effects[effect_name]
            self.active_effects[effect_name] = (enabled, intensity)

    def set_effect_intensity(self, effect_name, intensity):
        """Set the intensity of a specific effect"""
        if effect_name in self.active_effects:
            enabled, _ = self.active_effects[effect_name]
            self.active_effects[effect_name] = (enabled, max(0.0, min(1.0, intensity)))

    def set_transition_speed(self, speed):
        """Set the speed of transitions between effects"""
        self.transition_speed = max(0.01, min(0.2, speed))


    def set_global_opacity(self, opacity):
        """Set global opacity for all experimental effects"""
        self.global_opacity = max(0.0, min(1.0, opacity))
