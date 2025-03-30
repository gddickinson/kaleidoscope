import random
import math
import colorsys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QRadialGradient

class ParticleEffect:
    """Base class for atmospheric particle effects"""
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.particles = []
        self.lifetime = 0
        self.max_lifetime = 100  # Default lifetime in frames
        self.active = False
        self.color = QColor(255, 255, 255)

    def start(self):
        """Start the effect"""
        self.active = True
        self.lifetime = 0
        self.generate_particles()

    def update(self, bass, mids, highs, volume):
        """Update the effect state"""
        if not self.active:
            return

        # Update lifetime
        self.lifetime += 1
        if self.lifetime >= self.max_lifetime:
            self.active = False
            return

        # Update particles
        for particle in self.particles:
            particle.update(bass, mids, highs, volume)

        # Remove dead particles
        self.particles = [p for p in self.particles if p.active]

    def render(self, painter):
        """Render the effect"""
        if not self.active:
            return

        for particle in self.particles:
            particle.render(painter)

    def generate_particles(self):
        """Generate particles for this effect - override in subclasses"""
        pass


class Particle:
    """Base particle class"""
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z  # For 3D effects
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.ax = 0
        self.ay = 0
        self.az = 0
        self.size = 3
        self.color = QColor(255, 255, 255)
        self.alpha = 255  # Make sure this is always an integer
        self.fade_rate = 2
        self.lifetime = 0
        self.max_lifetime = 100
        self.active = True

    def update(self, bass, mids, highs, volume):
        """Update particle position and state"""
        # Update lifetime
        self.lifetime += 1
        if self.lifetime >= self.max_lifetime:
            self.active = False
            return

        # Apply physics
        self.vx += self.ax
        self.vy += self.ay
        self.vz += self.az

        self.x += self.vx
        self.y += self.vy
        self.z += self.vz

        # Apply fade - ensure alpha stays an integer
        self.alpha = max(0, int(self.alpha - self.fade_rate))
        if self.alpha <= 0:
            self.active = False

    def render(self, painter):
        """Render the particle"""
        if not self.active:
            return

        # Apply color with current alpha - ensure alpha is an integer
        current_color = QColor(self.color)
        current_color.setAlpha(int(self.alpha))

        # Draw particle
        painter.setBrush(QBrush(current_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(self.x - self.size/2), int(self.y - self.size/2),
                          int(self.size), int(self.size))


class SparkParticle(Particle):
    """Bright, fast-moving spark particle"""
    def __init__(self, x, y, z=0):
        super().__init__(x, y, z)
        self.size = random.uniform(1, 3)
        self.color = QColor(255, 220, 150)  # Yellowish-orange
        self.fade_rate = random.uniform(3, 7)
        self.max_lifetime = random.randint(30, 60)

        # Set initial velocity (faster than other particles)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(3, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.vz = random.uniform(-1, 1) * speed * 0.5

        # Add slight gravity
        self.ay = 0.05

    def render(self, painter):
        """Render with a glow effect"""
        if not self.active:
            return

        # Base particle
        current_color = QColor(self.color)
        current_color.setAlpha(int(self.alpha))  # Ensure alpha is an integer

        painter.setBrush(QBrush(current_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(self.x - self.size/2), int(self.y - self.size/2),
                          int(self.size), int(self.size))

        # Add glow (larger, more transparent circle)
        glow_color = QColor(self.color)
        glow_color.setAlpha(int(self.alpha // 3))  # Ensure alpha is an integer
        glow_size = self.size * 2

        painter.setBrush(QBrush(glow_color))
        painter.drawEllipse(int(self.x - glow_size/2), int(self.y - glow_size/2),
                          int(glow_size), int(glow_size))


class FlareParticle(Particle):
    """Bright, large flare particle with color shift"""
    def __init__(self, x, y, z=0):
        super().__init__(x, y, z)
        self.base_size = random.uniform(4, 10)
        self.size = self.base_size
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.pulse_speed = random.uniform(0.1, 0.2)

        # Set color (bright, warm tones)
        hue = random.uniform(0, 0.1)  # Red to yellow
        self.color = QColor()
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.8, 1.0)]
        self.color.setRgb(r, g, b)

        self.fade_rate = random.uniform(1, 3)
        self.max_lifetime = random.randint(60, 120)

        # Slower movement than sparks
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.5, 2)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.vz = random.uniform(-0.5, 0.5)

    def update(self, bass, mids, highs, volume):
        super().update(bass, mids, highs, volume)

        # Pulse size with phase
        self.pulse_phase += self.pulse_speed
        pulse_factor = 0.5 * math.sin(self.pulse_phase) + 1.5

        # Make size reactive to audio
        audio_factor = 1.0 + volume + (bass * 0.5)
        self.size = self.base_size * pulse_factor * audio_factor

    def render(self, painter):
        """Render with a radial gradient"""
        if not self.active:
            return

        # Use a radial gradient for a soft glow
        gradient = QRadialGradient(self.x, self.y, self.size)

        # Core color (brighter)
        core_color = QColor(self.color)
        core_color.setAlpha(int(self.alpha))  # Ensure alpha is an integer

        # Outer color (more transparent)
        outer_color = QColor(self.color)
        outer_color.setAlpha(int(self.alpha // 4))  # Ensure alpha is an integer

        gradient.setColorAt(0, core_color)
        gradient.setColorAt(1, outer_color)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(self.x - self.size), int(self.y - self.size),
                          int(self.size * 2), int(self.size * 2))


class FireworkParticle(Particle):
    """Firework explosion particle"""
    def __init__(self, x, y, z=0, color=None):
        super().__init__(x, y, z)
        self.trail = []
        self.trail_length = random.randint(3, 8)
        self.size = random.uniform(1, 3)

        # Use provided color or generate random bright color
        if color:
            self.color = color
        else:
            hue = random.random()
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.9, 1.0)]
            self.color = QColor(r, g, b)

        self.fade_rate = random.uniform(2, 4)
        self.max_lifetime = random.randint(40, 80)

        # High initial velocity that slows down
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.vz = random.uniform(-1, 1)

        # Add gravity
        self.ay = 0.08

        # Add drag/friction
        self.drag = 0.98

    def update(self, bass, mids, highs, volume):
        # Store current position in trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

        # Apply physics with drag
        self.vx *= self.drag
        self.vy *= self.drag
        self.vz *= self.drag

        super().update(bass, mids, highs, volume)

    def render(self, painter):
        """Render particle with trail"""
        if not self.active or len(self.trail) < 2:
            return

        # Draw trail
        for i in range(len(self.trail) - 1):
            # Calculate alpha for this trail segment
            segment_alpha = int(self.alpha * (i / len(self.trail)))  # Ensure alpha is an integer

            # Set color with diminishing alpha for trail
            trail_color = QColor(self.color)
            trail_color.setAlpha(segment_alpha)

            # Set pen for trail
            pen = QPen(trail_color)
            pen.setWidth(max(1, int(self.size * (i / len(self.trail)))))
            painter.setPen(pen)

            # Draw line segment
            x1, y1 = self.trail[i]
            x2, y2 = self.trail[i + 1]
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Draw the particle head
        current_color = QColor(self.color)
        current_color.setAlpha(int(self.alpha))  # Ensure alpha is an integer

        painter.setBrush(QBrush(current_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(self.x - self.size/2), int(self.y - self.size/2),
                          int(self.size), int(self.size))


class MistParticle(Particle):
    """Soft, slow-moving mist particle"""
    def __init__(self, x, y, z=0):
        super().__init__(x, y, z)
        self.size = random.uniform(5, 15)

        # Mist is typically white/blue but semi-transparent
        self.color = QColor(220, 230, 255)  # Light blue-ish
        self.alpha = random.randint(40, 120)  # Start semi-transparent

        self.fade_rate = random.uniform(0.5, 1.0)
        self.max_lifetime = random.randint(100, 200)

        # Very slow movement with some randomness
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.3, 0.3)

        # Slow size change
        self.growth_rate = random.uniform(-0.02, 0.05)

    def update(self, bass, mids, highs, volume):
        super().update(bass, mids, highs, volume)

        # Slowly change size
        self.size += self.growth_rate

        # Add slight random movement (drifting)
        self.vx += random.uniform(-0.05, 0.05)
        self.vy += random.uniform(-0.05, 0.05)

        # Limit velocity (mist moves slowly)
        self.vx = max(-0.5, min(0.5, self.vx))
        self.vy = max(-0.5, min(0.5, self.vy))

    def render(self, painter):
        """Render with a soft, diffuse appearance"""
        if not self.active:
            return

        # Use a radial gradient for soft edges
        gradient = QRadialGradient(self.x, self.y, self.size)

        # Core color
        core_color = QColor(self.color)
        core_color.setAlpha(int(self.alpha))  # Ensure alpha is an integer

        # Outer color (transparent)
        outer_color = QColor(self.color)
        outer_color.setAlpha(0)

        gradient.setColorAt(0, core_color)
        gradient.setColorAt(1, outer_color)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(self.x - self.size), int(self.y - self.size),
                          int(self.size * 2), int(self.size * 2))

class SparkBurst(ParticleEffect):
    """Burst of sparks from a point, good for beat hits"""
    def __init__(self, center_x, center_y, radius):
        super().__init__(center_x, center_y, radius)
        self.max_lifetime = random.randint(60, 100)
        self.burst_strength = random.uniform(0.8, 1.5)
        self.particle_count = random.randint(15, 30)

    def generate_particles(self):
        """Generate spark particles in a burst pattern"""
        # Generate random origin point within the kaleidoscope
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(0, self.radius * 0.7)
        origin_x = self.center_x + math.cos(angle) * dist
        origin_y = self.center_y + math.sin(angle) * dist

        # Create particles
        self.particles = []
        for _ in range(self.particle_count):
            spark = SparkParticle(origin_x, origin_y)

            # Adjust velocity for burst effect (outward)
            spark.vx *= self.burst_strength
            spark.vy *= self.burst_strength

            self.particles.append(spark)


class FlareEmission(ParticleEffect):
    """Slow-moving flares that pulse with the music"""
    def __init__(self, center_x, center_y, radius):
        super().__init__(center_x, center_y, radius)
        self.max_lifetime = random.randint(120, 180)
        self.emission_angle = random.uniform(0, math.pi * 2)
        self.emission_width = random.uniform(math.pi/6, math.pi/3)  # 30-60 degrees
        self.particle_count = random.randint(5, 12)

    def generate_particles(self):
        """Generate flare particles in a directional emission"""
        # Generate origin point near edge of kaleidoscope
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(self.radius * 0.5, self.radius * 0.8)
        origin_x = self.center_x + math.cos(angle) * dist
        origin_y = self.center_y + math.sin(angle) * dist

        # Calculate emission direction (toward or away from center)
        toward_center = random.choice([True, False])
        if toward_center:
            base_angle = math.atan2(self.center_y - origin_y, self.center_x - origin_x)
        else:
            base_angle = math.atan2(origin_y - self.center_y, origin_x - self.center_x)

        # Create particles
        self.particles = []
        for _ in range(self.particle_count):
            flare = FlareParticle(origin_x, origin_y)

            # Set velocity in emission direction with some spread
            emission_angle = base_angle + random.uniform(-self.emission_width/2, self.emission_width/2)
            speed = random.uniform(0.5, 1.5)

            flare.vx = math.cos(emission_angle) * speed
            flare.vy = math.sin(emission_angle) * speed

            self.particles.append(flare)


class FireworkExplosion(ParticleEffect):
    """Firework that shoots up and explodes into colorful particles"""
    def __init__(self, center_x, center_y, radius):
        super().__init__(center_x, center_y, radius)
        self.max_lifetime = random.randint(150, 200)
        self.particle_count = random.randint(30, 60)

        # Randomize firework color (all particles share same color)
        hue = random.random()
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.9, 1.0)]
        self.color = QColor(r, g, b)

        # Explosion parameters
        self.explosion_height = random.uniform(0.4, 0.7)  # How high before exploding
        self.explosion_size = random.uniform(30, 60)
        self.explosion_stage = False  # Start with launch stage
        self.launch_particle = None

    def start(self):
        """Start with launch particle"""
        self.active = True
        self.lifetime = 0
        self.explosion_stage = False

        # Create launch particle (trail rocket)
        # Select random edge point
        angle = random.uniform(0, math.pi * 2)
        dist = self.radius * 0.8
        start_x = self.center_x + math.cos(angle) * dist
        start_y = self.center_y + math.sin(angle) * dist

        # Calculate target near center but with some height
        target_angle = math.atan2(self.center_y - start_y, self.center_x - start_x)
        target_dist = dist * self.explosion_height
        target_x = self.center_x + math.cos(target_angle) * target_dist
        target_y = self.center_y + math.sin(target_angle) * target_dist

        # Create launch particle
        self.launch_particle = FireworkParticle(start_x, start_y, color=self.color)
        self.launch_particle.size = 3
        self.launch_particle.trail_length = 10

        # Calculate velocity to reach target (simplified)
        self.launch_particle.vx = (target_x - start_x) / 30
        self.launch_particle.vy = (target_y - start_y) / 30
        self.launch_particle.ay = 0  # No gravity during launch

        self.particles = [self.launch_particle]

    def update(self, bass, mids, highs, volume):
        """Handle launch and explosion stages"""
        super().update(bass, mids, highs, volume)

        # Check if we need to trigger explosion
        if not self.explosion_stage and self.launch_particle:
            # Calculate distance from center
            dx = self.launch_particle.x - self.center_x
            dy = self.launch_particle.y - self.center_y
            dist = math.sqrt(dx*dx + dy*dy)

            # Explode when close enough to target
            if dist <= self.radius * self.explosion_height:
                self.explosion_stage = True

                # Create explosion particles
                explosion_x = self.launch_particle.x
                explosion_y = self.launch_particle.y

                self.particles = []
                for _ in range(self.particle_count):
                    # Create particles with shared color
                    particle = FireworkParticle(explosion_x, explosion_y, color=self.color)
                    self.particles.append(particle)


class MistCloud(ParticleEffect):
    """Gentle cloud of mist that drifts and reacts subtly to music"""
    def __init__(self, center_x, center_y, radius):
        super().__init__(center_x, center_y, radius)
        self.max_lifetime = random.randint(200, 300)
        self.particle_count = random.randint(15, 30)

    def generate_particles(self):
        """Generate a cloud of mist particles"""
        # Choose a random area to generate mist
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(0, self.radius * 0.8)
        cloud_x = self.center_x + math.cos(angle) * dist
        cloud_y = self.center_y + math.sin(angle) * dist

        cloud_size = random.uniform(50, 100)

        # Create particles
        self.particles = []
        for _ in range(self.particle_count):
            # Position within cloud area
            offset_angle = random.uniform(0, math.pi * 2)
            offset_dist = random.uniform(0, cloud_size)

            x = cloud_x + math.cos(offset_angle) * offset_dist
            y = cloud_y + math.sin(offset_angle) * offset_dist

            self.particles.append(MistParticle(x, y))

class EffectsManager:
    """Manager for all particle effects"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = min(width, height) // 2

        self.effects = []
        self.available_effects = {
            "spark": SparkBurst,
            "flare": FlareEmission,
            "firework": FireworkExplosion,
            "mist": MistCloud,
            "tunnel": ParticleTunnel  # Add new tunnel effect
        }

        # Effect generation parameters
        self.enabled = True
        self.intensity = 1.0
        self.max_effects = 20  # Maximum concurrent effects

        # Beat response
        self.generate_on_beat = True
        self.beat_threshold = 0.5
        self.beat_cooldown = 0
        self.beat_cooldown_time = 10  # Frames between beat triggered effects

        # Random generation
        self.random_generation = True
        self.generation_chance = 0.01  # Chance per frame to generate a random effect

        # Tunnel effect settings
        self.tunnel_enabled = False  # Off by default
        self.active_tunnel = None  # Reference to active tunnel effect
        self.tunnel_auto_change = True  # Change tunnel settings automatically
        self.tunnel_change_interval = 600  # Frames between tunnel changes (10 seconds at 60fps)
        self.tunnel_change_timer = 0

        # Effect type weights (higher = more common)
        self.effect_weights = {
            "spark": 40,
            "flare": 30,
            "firework": 15,
            "mist": 15,
            "tunnel": 0  # Don't randomly generate tunnels
        }

        # Audio reactivity settings
        self.bass_reactivity = 1.0
        self.mids_reactivity = 0.7
        self.highs_reactivity = 0.5
        self.volume_reactivity = 0.8

        # Specific effect type toggle
        self.effect_enabled = {
            "spark": True,
            "flare": True,
            "firework": True,
            "mist": True,
            "tunnel": False  # Off by default
        }

    def update(self, spectrum, bands, volume, is_beat=False):
        """Update all effects and potentially generate new ones"""
        if not self.enabled:
            return

        # Handle tunnel effect separately from other effects
        if self.tunnel_enabled and self.effect_enabled["tunnel"]:
            # Check if we need to create a tunnel
            if not self.active_tunnel:
                self.active_tunnel = ParticleTunnel(self.center_x, self.center_y, self.radius)
                self.active_tunnel.start()
                self.effects.append(self.active_tunnel)

            # Check if we need to change tunnel settings
            if self.tunnel_auto_change:
                self.tunnel_change_timer += 1
                if self.tunnel_change_timer >= self.tunnel_change_interval:
                    self._change_tunnel_settings(bands[0], bands[1], bands[2], volume)
                    self.tunnel_change_timer = 0
        else:
            # Disable tunnel if setting is off
            if self.active_tunnel:
                self.active_tunnel.active = False
                self.active_tunnel = None

        # Process beat-based generation
        if self.generate_on_beat and is_beat and volume > self.beat_threshold:
            if self.beat_cooldown <= 0:
                self.generate_effect_on_beat(bands[0], bands[1], bands[2], volume)
                self.beat_cooldown = self.beat_cooldown_time

        # Update beat cooldown
        if self.beat_cooldown > 0:
            self.beat_cooldown -= 1

        # Process random generation
        if self.random_generation and random.random() < self.generation_chance * self.intensity:
            self.generate_random_effect(bands[0], bands[1], bands[2], volume)

        # Update existing effects
        for effect in self.effects:
            effect.update(
                bands[0] * self.bass_reactivity,
                bands[1] * self.mids_reactivity,
                bands[2] * self.highs_reactivity,
                volume * self.volume_reactivity
            )

        # Remove inactive effects (keep tunnel if it exists)
        self.effects = [e for e in self.effects if e.active or e == self.active_tunnel]

    def render(self, painter):
        """Render all active effects"""
        if not self.enabled:
            return

        for effect in self.effects:
            effect.render(painter)

    def _change_tunnel_settings(self, bass, mids, highs, volume):
        """Change tunnel effect settings randomly"""
        if not self.active_tunnel:
            return

        # Change flow direction on bass hit
        if bass > 0.6 and random.random() < 0.3:
            self.active_tunnel.flow_direction *= -1

        # Change spiral effect
        if random.random() < 0.3:
            self.active_tunnel.spiral_effect = not self.active_tunnel.spiral_effect

        # Change flow speed based on overall energy
        energy = bass + mids + highs
        self.active_tunnel.flow_speed = 0.5 + energy

    # New method to set tunnel settings
    def set_tunnel_enabled(self, enabled):
        """Enable or disable the tunnel effect"""
        self.tunnel_enabled = enabled
        self.effect_enabled["tunnel"] = enabled

        # Clear existing tunnel if disabling
        if not enabled and self.active_tunnel:
            self.active_tunnel.active = False
            self.active_tunnel = None

    def set_tunnel_auto_change(self, enabled, interval=600):
        """Set whether the tunnel should automatically change settings"""
        self.tunnel_auto_change = enabled
        self.tunnel_change_interval = interval

    def generate_effect_on_beat(self, bass, mids, highs, volume):
        """Generate effects triggered by beats"""
        # Stop if we're at max effects
        if len(self.effects) >= self.max_effects:
            return

        # Choose effect type based on audio characteristics
        effect_probs = {}

        # Sparks more likely on sharp transients (high frequencies)
        effect_probs["spark"] = highs * 2 * self.effect_weights["spark"]

        # Flares more likely with mid frequencies
        effect_probs["flare"] = mids * 1.5 * self.effect_weights["flare"]

        # Fireworks more likely on loud bass hits
        effect_probs["firework"] = bass * 3 * self.effect_weights["firework"]

        # Mist more likely during quieter moments
        effect_probs["mist"] = (1.0 - volume) * self.effect_weights["mist"]

        # Filter disabled effects
        filtered_probs = {k: v for k, v in effect_probs.items() if self.effect_enabled[k]}

        # If no effects enabled, return
        if not filtered_probs:
            return

        # Choose effect type
        effect_type = self.weighted_choice(filtered_probs)

        # Create the effect
        self.create_effect(effect_type)

    def generate_random_effect(self, bass, mids, highs, volume):
        """Generate random background effects"""
        # Stop if we're at max effects
        if len(self.effects) >= self.max_effects:
            return

        # Use base weights, filtered by enabled effects
        filtered_weights = {k: v for k, v in self.effect_weights.items()
                           if self.effect_enabled[k]}

        # If no effects enabled, return
        if not filtered_weights:
            return

        # Choose effect type
        effect_type = self.weighted_choice(filtered_weights)

        # Create the effect
        self.create_effect(effect_type)

    def create_effect(self, effect_type):
        """Create a new effect of the specified type"""
        if effect_type not in self.available_effects:
            print(f"Unknown effect type: {effect_type}")
            return

        # Create the effect
        effect_class = self.available_effects[effect_type]
        effect = effect_class(self.center_x, self.center_y, self.radius)
        effect.start()

        # Add to active effects
        self.effects.append(effect)

    def resize(self, width, height):
        """Handle resizing of the visualization area"""
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = min(width, height) // 2

    def clear_effects(self):
        """Clear all active effects"""
        self.effects = []

    def set_enabled(self, enabled):
        """Enable or disable all effects"""
        self.enabled = enabled

    def set_intensity(self, intensity):
        """Set overall effect intensity"""
        self.intensity = max(0.0, min(2.0, intensity))

    def set_effect_enabled(self, effect_type, enabled):
        """Enable or disable a specific effect type"""
        if effect_type in self.effect_enabled:
            self.effect_enabled[effect_type] = enabled

    def set_beat_response(self, enabled, threshold):
        """Set beat response parameters"""
        self.generate_on_beat = enabled
        self.beat_threshold = max(0.0, min(1.0, threshold))

    def set_random_generation(self, enabled, chance):
        """Set random generation parameters"""
        self.random_generation = enabled
        self.generation_chance = max(0.0, min(0.1, chance))

    def set_effect_weights(self, weights):
        """Set the relative weights for different effect types"""
        for effect_type, weight in weights.items():
            if effect_type in self.effect_weights:
                self.effect_weights[effect_type] = max(0, weight)

    def set_audio_reactivity(self, bass, mids, highs, volume):
        """Set audio reactivity parameters"""
        self.bass_reactivity = max(0.0, bass)
        self.mids_reactivity = max(0.0, mids)
        self.highs_reactivity = max(0.0, highs)
        self.volume_reactivity = max(0.0, volume)

    def weighted_choice(self, weights):
        """Choose a random item based on weights"""
        total = sum(weights.values())
        if total <= 0:
            return random.choice(list(weights.keys()))

        r = random.uniform(0, total)
        running_total = 0

        for item, weight in weights.items():
            running_total += weight
            if running_total > r:
                return item

        # Fallback (shouldn't happen)
        return random.choice(list(weights.keys()))

class TunnelParticle(Particle):
    """Particle that creates a 3D tunnel effect flowing toward or away from viewer"""
    def __init__(self, center_x, center_y, z=0):
        # Initialize with position at center, but variable z depth
        super().__init__(center_x, center_y, z)

        # Set particle properties
        self.base_size = random.uniform(1, 6)  # Base size (will change with z position)
        self.size = self.base_size

        # Generate random position on a ring
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(10, 100)  # Start distance from center

        # Set x,y position on the ring
        self.x = center_x + math.cos(angle) * dist
        self.y = center_y + math.sin(angle) * dist

        # Set z position (depth)
        self.z = random.uniform(-500, -100)

        # Flow direction (toward or away from viewer)
        self.flow_direction = random.choice([-1, 1])  # -1 = toward viewer, 1 = away

        # Flow speed (affected by audio)
        self.base_speed = random.uniform(2, 8)
        self.current_speed = self.base_speed

        # Color (will vary based on z position)
        hue = random.random()
        self.hue = hue  # Store original hue for later modification
        self.saturation = random.uniform(0.7, 1.0)
        self.value = random.uniform(0.8, 1.0)

        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue, self.saturation, self.value)]
        self.color = QColor(r, g, b)

        # Longer lifetime than other particles
        self.fade_rate = 0  # Don't fade automatically, reset when out of bounds
        self.max_lifetime = 1000

        # Store original position for spiral movement
        self.original_angle = angle
        self.original_dist = dist
        self.spiral_amount = 0  # How much spiral effect to apply
        self.spiral_speed = random.uniform(0.0005, 0.002)

        # Trail behind the particle (optional)
        self.trail = []
        self.trail_length = random.randint(3, 10) if random.random() < 0.3 else 0  # Only some particles have trails

    def update(self, bass, mids, highs, volume):
        """Update tunnel particle position and state"""
        # Store position in trail if enabled
        if self.trail_length > 0:
            self.trail.append((self.x, self.y, self.z))
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)

        # Update spiral amount based on mids
        self.spiral_amount += self.spiral_speed * (1.0 + mids * 2)

        # Update speed based on audio
        self.current_speed = self.base_speed * (1.0 + bass * 2)

        # Move along z-axis based on flow direction
        self.z += self.current_speed * self.flow_direction

        # Calculate new x,y position based on spiral effect
        angle = self.original_angle + self.spiral_amount
        dist = self.original_dist * (abs(self.z) / 400)  # Distance increases with depth

        # Calculate center-relative coordinates
        center_x = self.x - (self.x - self.original_dist * math.cos(self.original_angle))
        center_y = self.y - (self.y - self.original_dist * math.sin(self.original_angle))

        self.x = center_x + math.cos(angle) * dist
        self.y = center_y + math.sin(angle) * dist

        # Reset if particle goes beyond view bounds
        if (self.flow_direction < 0 and self.z > 50) or (self.flow_direction > 0 and self.z < -1000):
            self.reset_position(center_x, center_y)

        # Update size based on z position (perspective effect)
        z_factor = 1000 / (1000 + abs(self.z))
        self.size = self.base_size * z_factor * (1.0 + volume * 0.5)

        # Update color based on audio
        # Shift hue based on highs
        hue_shift = (highs * 0.2) % 1.0
        new_hue = (self.hue + hue_shift) % 1.0

        # Increase saturation with bass
        new_saturation = min(1.0, self.saturation + bass * 0.3)

        # Increase brightness with volume
        new_value = min(1.0, self.value + volume * 0.3)

        # Apply new color
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(new_hue, new_saturation, new_value)]
        self.color = QColor(r, g, b)

        # Update lifetime
        self.lifetime += 1
        if self.lifetime >= self.max_lifetime:
            self.active = False

    def reset_position(self, center_x, center_y):
        """Reset particle to new position when it goes out of bounds"""
        # Clear trail
        self.trail = []

        # New random angle and distance
        self.original_angle = random.uniform(0, math.pi * 2)
        self.original_dist = random.uniform(10, 100)

        # Reset z position based on flow direction
        if self.flow_direction < 0:  # Toward viewer
            self.z = random.uniform(-500, -300)
        else:  # Away from viewer
            self.z = random.uniform(-100, 50)

        # Reset lifetime
        self.lifetime = 0

        # Reset color
        self.hue = random.random()
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(self.hue, self.saturation, self.value)]
        self.color = QColor(r, g, b)

    def render(self, painter, center_x, center_y, perspective=800):
        """Render the tunnel particle with perspective and optional trail"""
        if not self.active:
            return

        # Apply perspective projection to get screen coordinates
        # z ranges from about -500 to 50
        z_factor = perspective / (perspective - self.z)

        # Project particle position
        screen_x = center_x + (self.x - center_x) * z_factor
        screen_y = center_y + (self.y - center_y) * z_factor

        # Calculate alpha based on z position
        # Particles fade in as they approach viewer
        if self.flow_direction < 0:  # Toward viewer
            # Ensure alpha is in the valid range [0, 255]
            alpha = max(0, min(255, int(255 * min(1.0, (500 + self.z) / 500))))
        else:  # Away from viewer
            # Ensure alpha is in the valid range [0, 255]
            alpha = max(0, min(255, int(255 * min(1.0, (1000 - abs(self.z)) / 500))))

        # Draw trail if enabled
        if self.trail_length > 0 and len(self.trail) > 1:
            # Draw lines connecting trail points
            prev_x, prev_y = None, None

            for i, (trail_x, trail_y, trail_z) in enumerate(reversed(self.trail)):
                # Apply perspective to trail point
                trail_z_factor = perspective / (perspective - trail_z)
                trail_screen_x = center_x + (trail_x - center_x) * trail_z_factor
                trail_screen_y = center_y + (trail_y - center_y) * trail_z_factor

                # Calculate trail segment alpha (ensure it's in valid range)
                segment_ratio = i / len(self.trail)
                trail_alpha = max(0, min(255, int(alpha * segment_ratio)))

                # Set color with alpha
                trail_color = QColor(self.color)
                trail_color.setAlpha(trail_alpha)

                # Set pen for trail line
                pen = QPen(trail_color)
                pen_width = max(1, int(self.size * trail_z_factor * 0.5))
                pen.setWidth(pen_width)
                painter.setPen(pen)

                # Draw line segment if we have a previous point
                if prev_x is not None and prev_y is not None:
                    painter.drawLine(
                        int(trail_screen_x),
                        int(trail_screen_y),
                        int(prev_x),
                        int(prev_y)
                    )

                prev_x, prev_y = trail_screen_x, trail_screen_y

        # Draw the main particle
        # Set color with calculated alpha
        particle_color = QColor(self.color)
        particle_color.setAlpha(alpha)

        # Apply size based on perspective
        screen_size = self.size * z_factor

        # Draw the particle
        painter.setBrush(QBrush(particle_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            int(screen_x - screen_size/2),
            int(screen_y - screen_size/2),
            int(screen_size),
            int(screen_size)
        )

class ParticleTunnel(ParticleEffect):
    """Creates a 3D tunnel of flowing particles reacting to music"""
    def __init__(self, center_x, center_y, radius):
        super().__init__(center_x, center_y, radius)
        self.max_lifetime = float('inf')  # Tunnel continues indefinitely
        self.particle_count = random.randint(100, 200)

        # Tunnel parameters
        self.flow_direction = random.choice([-1, 1])  # -1 = toward viewer, 1 = away
        self.flow_speed = 1.0
        self.rotation_speed = random.uniform(0.001, 0.005)
        self.tunnel_radius = radius * 0.8

        # Pulse effect settings
        self.enable_pulse = True
        self.pulse_amount = 0
        self.pulse_speed = 0.02
        self.pulse_decay = 0.98

        # Enable spiral effect
        self.spiral_effect = random.choice([True, False])
        self.spiral_amount = 0
        self.spiral_speed = random.uniform(0.0001, 0.001)

        # Audio reactivity settings
        self.speed_reactivity = random.uniform(0.5, 1.5)
        self.size_reactivity = random.uniform(0.5, 1.5)
        self.color_reactivity = random.uniform(0.5, 1.5)

        # Fog effect (particles more visible at certain depths)
        self.enable_fog = True
        self.fog_near = -100
        self.fog_far = -500

        # Tunnel shape variations
        self.shape_variability = 0  # 0 = perfect circle, higher = more variation

        # Generate particles on startup
        self.generate_particles()

    def generate_particles(self):
        """Generate particles arranged in a tunnel formation"""
        self.particles = []

        for _ in range(self.particle_count):
            # Create tunnel particle
            particle = TunnelParticle(self.center_x, self.center_y)

            # Override some settings to match tunnel config
            particle.flow_direction = self.flow_direction

            # Add to active particles
            self.particles.append(particle)

    def update(self, bass, mids, highs, volume):
        """Update tunnel effect based on audio analysis"""
        super().update(bass, mids, highs, volume)

        # Update pulse effect on beat
        if bass > 0.6 and random.random() < bass * 0.3:
            # Strong bass hit - trigger pulse
            self.pulse_amount = 0.5 + bass * 0.5

        # Apply pulse decay
        self.pulse_amount *= self.pulse_decay

        # Update spiral amount
        if self.spiral_effect:
            self.spiral_amount += self.spiral_speed * (1.0 + mids * 2)

        # Update flow speed based on audio energy
        self.flow_speed = 1.0 + (volume * 3 * self.speed_reactivity)

        # Occasionally change flow direction on strong beat
        if bass > 0.8 and random.random() < 0.05:
            self.flow_direction *= -1

        # Update for particles that need respawning (instead of removing them)
        for particle in self.particles:
            if not particle.active:
                # Reset instead of removing
                particle.reset_position(self.center_x, self.center_y)
                particle.active = True

                # Apply current tunnel settings
                particle.flow_direction = self.flow_direction

    def render(self, painter):
        """Render the tunnel effect with depth sorting"""
        if not self.active or not self.particles:
            return

        # Sort particles by Z depth for proper rendering
        # When flowing toward viewer (negative direction), render back-to-front
        # When flowing away (positive direction), render front-to-back
        if self.flow_direction < 0:
            # Sort from back to front (most negative z first)
            sorted_particles = sorted(self.particles, key=lambda p: p.z)
        else:
            # Sort from front to back (most positive z first)
            sorted_particles = sorted(self.particles, key=lambda p: -p.z)

        # Render each particle with proper depth perspective
        for particle in sorted_particles:
            if particle.active:
                particle.render(painter, self.center_x, self.center_y, 800)
