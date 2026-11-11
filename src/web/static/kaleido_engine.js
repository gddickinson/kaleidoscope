// Port of src/core/kaleidoscope_engine.py (KaleidoscopeEngine state and update) and the Particle class of
// src/core/visualization_components.py. Field names follow the Python (snake_case) so the reference runs can be
// compared one to one. Drawing lives in kaleido_render.js; the experimental effects are not ported.
import { R, int } from './pyrandom.js';
import { qcolor } from './colors.js';
import { WireframeManager } from './wireframe.js';
import { CircularWaveform } from './waveform.js';
import { EffectsManager } from './effects.js';

export class Particle {
  constructor(radius, particleSize, trailLength) {
    const angle = R.uniform(0, Math.PI * 2);
    const dist = R.uniform(0, radius * 0.7);
    this.x = Math.cos(angle) * dist;
    this.y = Math.sin(angle) * dist;
    this.z = R.uniform(-100, 100);
    this.size = R.uniform(particleSize * 0.5, particleSize * 1.5);
    this.speed = R.uniform(0.5, 2.0);
    this.angle = R.uniform(0, Math.PI * 2);
    this.z_speed = R.uniform(-0.5, 0.5);
    this.trail = [];
    this.trail_length = trailLength;
    this.color = qcolor(R.randint(0, 255), R.randint(0, 255), R.randint(0, 255));
    this.current_size = this.size;
  }

  update(speedMod, sizeMod, zMod = 1.0) {
    this.angle += 0.02 * speedMod;
    this.x += Math.cos(this.angle) * this.speed * speedMod * 0.5;
    this.y += Math.sin(this.angle) * this.speed * speedMod * 0.5;
    this.z += this.z_speed * zMod;
    if (this.z > 200 || this.z < -200) this.z_speed = -this.z_speed;
    this.trail.push([this.x, this.y, this.z]);
    if (this.trail.length > this.trail_length) this.trail.shift();
    this.current_size = this.size * sizeMod;
  }
}

export const WIREFRAME_SHAPES = ['cube', 'pyramid', 'sphere', 'octahedron', 'dodecahedron', 'tetrahedron', 'torus'];

export class KaleidoscopeEngine {
  constructor(width, height) {
    this.width = width; this.height = height;
    this.center_x = int(width / 2); this.center_y = int(height / 2);
    this.radius = int(Math.min(width, height) / 2);
    this.segments = 8; this.zoom = 1.0; this.rotation = 0; this.rotation_speed = 0.5;
    this.color_mode = 'spectrum';
    this.base_color = qcolor(255, 0, 127); this.secondary_color = qcolor(0, 127, 255);
    this.blur_amount = 0; this.shape_type = 'circle'; this.distortion = 0.0; this.symmetry_mode = 'radial';
    this.particles = []; this.max_particles = 100; this.particle_size = 10; this.trail_length = 5;
    this.bass_influence = 1.0; this.mids_influence = 1.0; this.highs_influence = 1.0;
    this.spectrum_data = new Array(100).fill(0); this.bands = [0, 0, 0]; this.volume = 0;
    this.enable_3d = true; this.depth_influence = 1.0; this.perspective = 800;
    this.rotation_3d_x = 0; this.rotation_3d_y = 0; this.rotation_3d_z = 0;
    this.enable_pulse = true; this.pulse_strength = 1.0; this.pulse_speed = 1.0; this.pulse_size = 1.0;
    this.current_pulse = 1.0; this.target_pulse = 1.0; this.pulse_attack = 0.1; this.pulse_decay = 0.2;
    this.last_beat_time = 0; this.beat_threshold = 0.5;
    this.prev_bass = 0; this.is_beat = false; this.beat_cooldown = 0; this.beat_history = [];
    this.enable_wireframe = true;
    this.wireframe_manager = new WireframeManager(int(Math.min(width, height) / 4));
    this.cube_color_mode = 'audio_reactive'; this.cube_rotation_speed = 1.0;
    this.enable_waveform = true;
    this.circular_waveform = new CircularWaveform(int(Math.min(width, height) / 2));
    this.raw_audio_data = new Float64Array(1024);
    this.effects_manager = new EffectsManager(width, height);
    this.init_particles();
  }

  init_particles() {
    this.particles = [];
    for (let i = 0; i < this.max_particles; i++) this.particles.push(new Particle(this.radius, this.particle_size, this.trail_length));
  }

  update(spectrum, bands, volume, rawAudio = null) {
    if (rawAudio && rawAudio.length > 0) this.raw_audio_data = rawAudio;
    this.spectrum_data = spectrum; this.bands = bands; this.volume = volume;

    const baseRotation = this.rotation_speed * 0.01;
    const bassRotation = this.bands[0] * this.bass_influence * 0.1;
    this.rotation += baseRotation + bassRotation;
    if (this.enable_3d) {
      this.rotation_3d_x += this.bands[1] * 0.005 * this.depth_influence;
      this.rotation_3d_y += this.bands[2] * 0.003 * this.depth_influence;
      this.rotation_3d_z += baseRotation * 0.5;
    }
    this.detect_beat();
    this.update_pulse();

    for (const p of this.particles) {
      const speedMod = 1.0 + this.bands[1] * this.mids_influence;
      let sizeMod = 1.0 + this.volume * 4;
      if (this.enable_pulse) sizeMod *= this.current_pulse;
      const zMod = this.enable_3d ? this.bands[2] * this.depth_influence : 1.0;
      p.update(speedMod, sizeMod, zMod);
      let dist = Math.sqrt(p.x ** 2 + p.y ** 2);
      if (dist > this.radius * 0.8) {
        const angle = R.uniform(0, Math.PI * 2);
        dist = R.uniform(0, this.radius * 0.3);
        p.x = Math.cos(angle) * dist;
        p.y = Math.sin(angle) * dist;
        p.trail = [];
      }
    }
    if (this.enable_wireframe) {
      this.wireframe_manager.update(this.bands[0] * this.bass_influence, this.bands[1] * this.mids_influence,
        this.bands[2] * this.highs_influence, this.volume, this.is_beat);
    }
    if (this.enable_waveform) {
      this.circular_waveform.update(this.raw_audio_data, this.spectrum_data, this.volume, this.bands[0] * this.bass_influence);
    }
    this.effects_manager.update(spectrum, bands, volume, this.is_beat);
  }

  detect_beat() {
    const bass = this.bands[0];
    this.beat_history.push(bass);
    if (this.beat_history.length > 30) this.beat_history.shift();
    if (this.beat_history.length > 5) {
      let sum = 0;
      for (const b of this.beat_history) sum += b;
      const avgBass = sum / this.beat_history.length;
      if (bass > avgBass * 1.5 && bass > this.prev_bass && this.beat_cooldown <= 0) {
        this.is_beat = true;
        this.beat_cooldown = 10;
        if (this.enable_pulse) {
          const pulseIntensity = 1.0 + (bass / avgBass - 1) * this.pulse_strength;
          this.target_pulse = Math.min(2.0, pulseIntensity);
        }
      } else {
        this.is_beat = false;
      }
    }
    if (this.beat_cooldown > 0) this.beat_cooldown -= 1;
    this.prev_bass = bass;
  }

  update_pulse() {
    if (!this.enable_pulse) { this.current_pulse = 1.0; return; }
    if (this.current_pulse < this.target_pulse) {
      this.current_pulse += (this.target_pulse - this.current_pulse) * this.pulse_attack;
    } else {
      this.current_pulse += (1.0 - this.current_pulse) * this.pulse_decay;
    }
    if (Math.abs(this.current_pulse - 1.0) < 0.05) { this.current_pulse = 1.0; this.target_pulse = 1.0; }
  }

  apply_3d_rotation(x, y, z) {
    const rx = this.rotation_3d_x, ry = this.rotation_3d_y, rz = this.rotation_3d_z;
    const xRot = x * Math.cos(rz) - y * Math.sin(rz);
    const yRot = x * Math.sin(rz) + y * Math.cos(rz);
    const xRot2 = xRot * Math.cos(ry) + z * Math.sin(ry);
    const zRot = -xRot * Math.sin(ry) + z * Math.cos(ry);
    const yRot2 = yRot * Math.cos(rx) - zRot * Math.sin(rx);
    const zRot2 = yRot * Math.sin(rx) + zRot * Math.cos(rx);
    return [xRot2, yRot2, zRot2];
  }

  resize(width, height) {
    this.width = width; this.height = height;
    this.center_x = int(width / 2); this.center_y = int(height / 2);
    this.radius = int(Math.min(width, height) / 2);
    this.wireframe_manager.set_size(int(Math.min(width, height) / 4));
    this.effects_manager.resize(width, height);
  }

  // --- setters (same names and arguments as the Python engine) ---
  set_3d_enabled(v) { this.enable_3d = v; }
  set_depth_influence(v) { this.depth_influence = v; }
  set_perspective(v) { this.perspective = v; }
  set_pulse_enabled(v) { this.enable_pulse = v; }
  set_pulse_parameters(strength, speed, attack, decay) {
    this.pulse_strength = strength; this.pulse_speed = speed; this.pulse_attack = attack; this.pulse_decay = decay;
  }
  set_segments(v) { this.segments = v; }
  set_zoom(v) { this.zoom = v; }
  set_rotation_speed(v) { this.rotation_speed = v; }
  set_color_mode(m) { this.color_mode = m; }
  set_base_color(c) { this.base_color = c; }
  set_secondary_color(c) { this.secondary_color = c; }
  set_blur_amount(v) { this.blur_amount = v; }
  set_shape_type(s) { this.shape_type = s; }
  set_distortion(v) { this.distortion = v; }
  set_symmetry_mode(m) { this.symmetry_mode = m; }
  set_particle_settings(count, size, trail) {
    this.max_particles = count; this.particle_size = size; this.trail_length = trail; this.init_particles();
  }
  set_audio_influence(bass, mids, highs) { this.bass_influence = bass; this.mids_influence = mids; this.highs_influence = highs; }

  set_wireframe_enabled(v) { this.enable_wireframe = v; }
  set_wireframe_shape(shapeType, morph = false) {
    shapeType = shapeType.toLowerCase().trim();
    if (!WIREFRAME_SHAPES.includes(shapeType)) shapeType = 'cube';
    this.wireframe_manager.set_shape(shapeType, morph);
  }
  set_wireframe_size(size) { this.wireframe_manager.set_size(size); }
  set_wireframe_rotation(speed) { this.wireframe_manager.set_rotation_speed(speed); }
  set_wireframe_color_mode(mode) { this.wireframe_manager.set_color_mode(mode); }
  set_wireframe_colors(primary, secondary = null) { this.wireframe_manager.set_custom_colors(primary, secondary); }
  set_wireframe_effects(showVertices, vertexSize, edgeGlow, glowIntensity) {
    this.wireframe_manager.set_effects(showVertices, vertexSize, edgeGlow, glowIntensity);
  }
  set_wireframe_echo(enabled, count = 3, opacity = 0.3, spacing = 0.2) {
    this.wireframe_manager.set_echo_effect(enabled, count, opacity, spacing);
  }
  set_wireframe_beat_response(autoMorph, morphOnBeat, beatInterval = 30) {
    this.wireframe_manager.set_beat_response(autoMorph, morphOnBeat, beatInterval);
  }
  set_wireframe_multi_shape(enabled, count = 3) { this.wireframe_manager.set_multi_shape_mode(enabled, count); }
  set_wireframe_edges_visible(v) { this.wireframe_manager.set_edges_visible(v); }

  set_waveform_enabled(v) { this.enable_waveform = v; }
  set_waveform_parameters(innerRadiusPct, lineWidth, rotationSpeed, amplitude) {
    const radius = int(Math.min(this.width, this.height) / 2);
    const w = this.circular_waveform;
    w.set_radius(radius, innerRadiusPct / 100.0);
    w.set_line_width(lineWidth);
    w.set_rotation_speed(rotationSpeed);
    w.amplitude = amplitude;
  }
  set_waveform_colors(primary, secondary, useGradient) {
    if (useGradient) this.circular_waveform.set_colors(primary, secondary);
    else this.circular_waveform.set_colors(primary);
  }
  set_waveform_reflection(show, alpha) { this.circular_waveform.set_reflection(show, alpha / 100.0); }

  set_effects_enabled(v) { this.effects_manager.set_enabled(v); }
  set_effects_intensity(v) { this.effects_manager.set_intensity(v); }
  set_effect_type_enabled(type, v) { this.effects_manager.set_effect_enabled(type, v); }
  set_effects_beat_response(enabled, threshold) { this.effects_manager.set_beat_response(enabled, threshold); }
  set_effects_random_generation(enabled, chance) { this.effects_manager.set_random_generation(enabled, chance); }
  set_effects_weights(w) { this.effects_manager.set_effect_weights(w); }
  set_effects_audio_reactivity(b, m, h, v) { this.effects_manager.set_audio_reactivity(b, m, h, v); }
}
