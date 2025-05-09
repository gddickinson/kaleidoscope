import math
import random
import numpy as np
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QTime, QRect, QPoint, QObject
from PyQt5.QtGui import QColor, QPainter, QImage, QBrush, QPen

from src.core.visualization_components import (
    Particle, ShapeRenderer, ColorGenerator, SymmetryRenderer, EffectProcessor, WireframeCube,
    CircularWaveform, WireframeManager
)

from src.core.particle_effects import EffectsManager
from src.experimental.experimental_manager import ExperimentalEffectsManager

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

        # 3D parameters
        self.enable_3d = True
        self.depth_influence = 1.0
        self.perspective = 800  # Perspective factor (higher = less pronounced)
        self.rotation_3d_x = 0
        self.rotation_3d_y = 0
        self.rotation_3d_z = 0

        # Pulse system parameters
        self.enable_pulse = True
        self.pulse_strength = 1.0
        self.pulse_speed = 1.0
        self.pulse_size = 1.0
        self.current_pulse = 1.0
        self.target_pulse = 1.0
        self.pulse_attack = 0.1  # How quickly pulse grows
        self.pulse_decay = 0.2   # How quickly pulse diminishes
        self.last_beat_time = 0
        self.beat_threshold = 0.5

        # Beat detection
        self.prev_bass = 0
        self.is_beat = False
        self.beat_cooldown = 0
        self.beat_history = []  # For calculating average and threshold

        # Create rendering buffers
        self.buffer_image = QImage(width, height, QImage.Format_ARGB32)
        self.buffer_image.fill(Qt.transparent)
        self.final_image = QImage(width, height, QImage.Format_ARGB32)
        self.final_image.fill(Qt.black)

        # Wireframe cube settings
        self.enable_wireframe = True
        self.wireframe_manager = WireframeManager(size=min(width, height) // 4)
        self.cube_color_mode = "audio_reactive"  # "audio_reactive", "solid", "rainbow"
        self.cube_rotation_speed = 1.0

        # Circular waveform
        self.enable_waveform = True
        self.circular_waveform = CircularWaveform(radius=min(width, height) // 2)

        # Store raw audio data for waveform
        self.raw_audio_data = np.zeros(1024)

        # Particle effects system
        self.effects_manager = EffectsManager(width, height)

        # Initialize particles
        self.init_particles()

        # Initialize experimental effects
        self.experimental_effects = ExperimentalEffectsManager(width, height)

    def init_particles(self):
        """Initialize particles for animation"""
        self.particles = []
        for _ in range(self.max_particles):
            self.particles.append(Particle(self.radius, self.particle_size, self.trail_length))

    def update(self, spectrum, bands, volume, raw_audio=None):
        """Update visualization parameters based on audio data"""

        if raw_audio is not None and len(raw_audio) > 0:
            self.raw_audio_data = raw_audio

        self.spectrum_data = spectrum
        self.bands = bands
        self.volume = volume

        # Apply audio-reactive effects
        base_rotation = self.rotation_speed * 0.01
        bass_rotation = self.bands[0] * self.bass_influence * 0.1
        self.rotation += base_rotation + bass_rotation

        # 3D rotations
        if self.enable_3d:
            self.rotation_3d_x += self.bands[1] * 0.005 * self.depth_influence
            self.rotation_3d_y += self.bands[2] * 0.003 * self.depth_influence
            self.rotation_3d_z += base_rotation * 0.5

        # Update beat detection
        self.detect_beat()

        # Update pulse effect
        self.update_pulse()

        # Update particles
        for p in self.particles:
            # Apply audio influence to particle movement
            speed_mod = 1.0 + self.bands[1] * self.mids_influence
            size_mod = 1.0 + self.volume * 4

            # Apply pulse effect to size
            if self.enable_pulse:
                size_mod *= self.current_pulse

            # Apply Z-axis influence if 3D is enabled
            z_mod = self.bands[2] * self.depth_influence if self.enable_3d else 1.0

            p.update(speed_mod, size_mod, z_mod)

            # Reset particles that go out of bounds
            dist = math.sqrt(p.x**2 + p.y**2)
            if dist > self.radius * 0.8:
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(0, self.radius * 0.3)
                p.x = math.cos(angle) * dist
                p.y = math.sin(angle) * dist
                p.trail = []

        # Detect beat for wireframe effects
        beat_detected = self.is_beat  # Use the beat detection from kaleidoscope engine

        # Update wireframe visualization with beat information
        if self.enable_wireframe:
            self.wireframe_manager.update(
                self.bands[0] * self.bass_influence,
                self.bands[1] * self.mids_influence,
                self.bands[2] * self.highs_influence,
                self.volume,
                beat_detected
            )

        # Update circular waveform
        if self.enable_waveform:
            self.circular_waveform.update(
                self.raw_audio_data,
                self.spectrum_data,
                self.volume,
                self.bands[0] * self.bass_influence
            )

        # Update effects manager
        self.effects_manager.update(spectrum, bands, volume, self.is_beat)

        # Update experimental effects
        if hasattr(self, 'experimental_effects'):
            self.experimental_effects.update(spectrum, bands, volume, self.is_beat)

    def detect_beat(self):
        """Simple beat detection based on bass energy"""
        # Get current bass energy
        bass = self.bands[0]

        # Add to history (keep last 30 samples)
        self.beat_history.append(bass)
        if len(self.beat_history) > 30:
            self.beat_history.pop(0)

        # Calculate dynamic threshold based on history
        if len(self.beat_history) > 5:
            avg_bass = sum(self.beat_history) / len(self.beat_history)
            # Beat is detected when bass exceeds average by a threshold factor
            # and is increasing from previous sample
            if bass > avg_bass * 1.5 and bass > self.prev_bass and self.beat_cooldown <= 0:
                self.is_beat = True
                self.beat_cooldown = 10  # Prevent beats too close together

                # Trigger a pulse
                if self.enable_pulse:
                    # Stronger beat = stronger pulse
                    pulse_intensity = 1.0 + (bass / avg_bass - 1) * self.pulse_strength
                    self.target_pulse = min(2.0, pulse_intensity)
            else:
                self.is_beat = False

        # Update cooldown
        if self.beat_cooldown > 0:
            self.beat_cooldown -= 1

        self.prev_bass = bass

    def update_pulse(self):
        """Update the pulse effect"""
        if not self.enable_pulse:
            self.current_pulse = 1.0
            return

        # Move current_pulse toward target_pulse
        if self.current_pulse < self.target_pulse:
            # Attack phase (grow quickly)
            self.current_pulse += (self.target_pulse - self.current_pulse) * self.pulse_attack
        else:
            # Decay phase (shrink more slowly)
            self.current_pulse += (1.0 - self.current_pulse) * self.pulse_decay

        # Reset target if we've mostly decayed
        if abs(self.current_pulse - 1.0) < 0.05:
            self.current_pulse = 1.0
            self.target_pulse = 1.0


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

            # Apply 3D projection for each point in the trail
            projected_trail = []
            for i, (tx, ty, tz) in enumerate(p.trail):
                if self.enable_3d:
                    # Apply 3D rotations
                    rx, ry, rz = self.apply_3d_rotation(tx, ty, tz)

                    # Apply perspective projection
                    scale = self.perspective / (self.perspective + rz)
                    px = rx * scale
                    py = ry * scale

                    # Store projected coordinates and scale
                    projected_trail.append((px, py, scale))
                else:
                    # 2D mode - just pass through coordinates with a default scale
                    projected_trail.append((tx, ty, 1.0))

            # Draw trail with fading opacity
            for i, (px, py, scale) in enumerate(projected_trail):
                alpha = int(255 * (i / len(projected_trail)))
                size = p.current_size * (i / len(projected_trail)) * scale

                # Get color based on mode
                if self.color_mode == "spectrum":
                    # Map particle position to spectrum colors
                    freq_index = min(int(abs(px / self.radius) * len(self.spectrum_data)), len(self.spectrum_data) - 1)
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
                    self.center_x + px,
                    self.center_y + py,
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

        # Render circular waveform if enabled
        if self.enable_waveform:
            self.circular_waveform.render(
                final_painter,
                self.center_x,
                self.center_y
            )

        # Render particle effects - MOVED BEFORE the end of painter
        if hasattr(self, 'effects_manager') and self.effects_manager:
            try:
                self.effects_manager.render(final_painter)
            except Exception as e:
                print(f"Error rendering effects: {e}")

        # Render wireframe shapes if enabled
        if self.enable_wireframe:
            self.wireframe_manager.render(
                final_painter,
                self.center_x,
                self.center_y,
                self.perspective
            )

        # Render experimental effects
        if hasattr(self, 'experimental_effects'):
            try:
                self.experimental_effects.render(final_painter)
            except Exception as e:
                print(f"Error rendering experimental effects: {e}")
                import traceback
                traceback.print_exc()


        # End painter after all rendering is done
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

    def apply_3d_rotation(self, x, y, z):
        """Apply 3D rotation matrix to a point"""
        # Convert to radians
        rx = self.rotation_3d_x
        ry = self.rotation_3d_y
        rz = self.rotation_3d_z

        # Apply Z rotation first
        x_rot = x * math.cos(rz) - y * math.sin(rz)
        y_rot = x * math.sin(rz) + y * math.cos(rz)

        # Apply Y rotation
        x_rot2 = x_rot * math.cos(ry) + z * math.sin(ry)
        z_rot = -x_rot * math.sin(ry) + z * math.cos(ry)

        # Apply X rotation
        y_rot2 = y_rot * math.cos(rx) - z_rot * math.sin(rx)
        z_rot2 = y_rot * math.sin(rx) + z_rot * math.cos(rx)

        return x_rot2, y_rot2, z_rot2

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

        # Update wireframe manager if it exists
        if hasattr(self, 'wireframe_manager'):
            # Update size based on new dimensions
            self.wireframe_manager.set_size(min(width, height) // 4)

        # Update effects manager
        if hasattr(self, 'effects_manager'):
            self.effects_manager.resize(width, height)

        if hasattr(self, 'experimental_effects'):
            self.experimental_effects.resize(width, height)

    # 3D settings
    def set_3d_enabled(self, enabled):
        """Enable or disable 3D effects"""
        self.enable_3d = enabled

    def set_depth_influence(self, value):
        """Set the influence of audio on depth movement"""
        self.depth_influence = value

    def set_perspective(self, value):
        """Set the perspective effect strength"""
        self.perspective = value

    # Pulse system
    def set_pulse_enabled(self, enabled):
        """Enable or disable pulse effects"""
        self.enable_pulse = enabled

    def set_pulse_parameters(self, strength, speed, attack, decay):
        """Set pulse system parameters"""
        self.pulse_strength = strength
        self.pulse_speed = speed
        self.pulse_attack = attack
        self.pulse_decay = decay

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


    def set_wireframe_enabled(self, enabled):
        """Enable or disable wireframe visualization"""
        self.enable_wireframe = enabled

    def set_wireframe_shape(self, shape_type, morph=False):
        """Set the wireframe shape type"""
        try:
            # Debug output
            print(f"Setting wireframe shape to: {shape_type}, morph={morph}")

            # Convert shape type to lowercase for case-insensitive matching
            shape_type = shape_type.lower().strip()

            # Check if shape type is valid
            valid_shapes = ["cube", "pyramid", "sphere", "octahedron",
                            "dodecahedron", "tetrahedron", "torus"]

            if shape_type not in valid_shapes:
                print(f"Invalid shape type: {shape_type}. Using cube instead.")
                shape_type = "cube"

            self.wireframe_manager.set_shape(shape_type, morph)

        except Exception as e:
            print(f"Error setting wireframe shape: {e}")
            import traceback
            traceback.print_exc()

    def set_wireframe_size(self, size):
        """Set the wireframe shape size"""
        try:
            self.wireframe_manager.set_size(size)
        except Exception as e:
            print(f"Error setting wireframe size: {e}")

    def set_wireframe_rotation(self, speed):
        """Set wireframe rotation speed"""
        self.wireframe_manager.set_rotation_speed(speed)

    def set_wireframe_color_mode(self, mode):
        """Set wireframe color mode"""
        self.wireframe_manager.set_color_mode(mode)

    def set_wireframe_colors(self, primary_color, secondary_color=None):
        """Set wireframe custom colors"""
        self.wireframe_manager.set_custom_colors(primary_color, secondary_color)

    def set_wireframe_effects(self, show_vertices, vertex_size, edge_glow, glow_intensity):
        """Set wireframe visual effects"""
        self.wireframe_manager.set_effects(show_vertices, vertex_size, edge_glow, glow_intensity)

    def set_wireframe_echo(self, enabled, count=3, opacity=0.3, spacing=0.2):
        """Set wireframe echo/trail effect"""
        self.wireframe_manager.set_echo_effect(enabled, count, opacity, spacing)

    def set_wireframe_beat_response(self, auto_morph, morph_on_beat, beat_interval=30):
        """Set wireframe beat response options"""
        self.wireframe_manager.set_beat_response(auto_morph, morph_on_beat, beat_interval)

    def set_wireframe_multi_shape(self, enabled, count=3):
        """Enable/disable multiple shapes mode"""
        self.wireframe_manager.set_multi_shape_mode(enabled, count)

    def set_waveform_enabled(self, enabled):
        """Enable or disable circular waveform"""
        self.enable_waveform = enabled

    def set_waveform_parameters(self, inner_radius_pct, line_width, rotation_speed, amplitude):
        """Set circular waveform parameters"""
        # Update radius when window size changes
        radius = min(self.width, self.height) // 2

        self.circular_waveform.set_radius(radius, inner_radius_pct / 100.0)
        self.circular_waveform.set_line_width(line_width)
        self.circular_waveform.set_rotation_speed(rotation_speed)
        self.circular_waveform.amplitude = amplitude

    def set_waveform_colors(self, primary_color, secondary_color, use_gradient):
        """Set circular waveform colors"""
        if use_gradient:
            self.circular_waveform.set_colors(primary_color, secondary_color)
        else:
            self.circular_waveform.set_colors(primary_color)

    def set_waveform_reflection(self, show_reflection, reflection_alpha):
        """Set circular waveform reflection settings"""
        self.circular_waveform.set_reflection(show_reflection, reflection_alpha / 100.0)

    def set_wireframe_edges_visible(self, visible):
        """Enable or disable wireframe edges"""
        try:
            self.wireframe_manager.set_edges_visible(visible)
        except Exception as e:
            print(f"Error setting wireframe edges visibility: {e}")

    def set_effects_enabled(self, enabled):
        """Enable or disable particle effects"""
        self.effects_manager.set_enabled(enabled)

    def set_effects_intensity(self, intensity):
        """Set overall effect intensity"""
        self.effects_manager.set_intensity(intensity)

    def set_effect_type_enabled(self, effect_type, enabled):
        """Enable or disable specific effect type"""
        self.effects_manager.set_effect_enabled(effect_type, enabled)

    def set_effects_beat_response(self, enabled, threshold):
        """Set effects beat response parameters"""
        self.effects_manager.set_beat_response(enabled, threshold)

    def set_effects_random_generation(self, enabled, chance):
        """Set effects random generation parameters"""
        self.effects_manager.set_random_generation(enabled, chance)

    def set_effects_weights(self, weights):
        """Set effect type weights"""
        self.effects_manager.set_effect_weights(weights)

    def set_effects_audio_reactivity(self, bass, mids, highs, volume):
        """Set effects audio reactivity parameters"""
        self.effects_manager.set_audio_reactivity(bass, mids, highs, volume)


    def set_tunnel_enabled(self, enabled):
        """Enable or disable the particle tunnel effect"""
        try:
            self.effects_manager.set_tunnel_enabled(enabled)
        except Exception as e:
            print(f"Error setting tunnel enabled: {e}")

    def set_tunnel_auto_change(self, enabled, interval):
        """Set tunnel auto-change settings"""
        try:
            self.effects_manager.set_tunnel_auto_change(enabled, interval)
        except Exception as e:
            print(f"Error setting tunnel auto-change: {e}")

    def set_tunnel_direction(self, direction):
        """Set tunnel flow direction"""
        try:
            # Get active tunnel
            tunnel = self.effects_manager.active_tunnel
            if tunnel:
                if direction == "inward":
                    tunnel.flow_direction = -1
                elif direction == "outward":
                    tunnel.flow_direction = 1
                # "auto" is handled by the effect itself
        except Exception as e:
            print(f"Error setting tunnel direction: {e}")
