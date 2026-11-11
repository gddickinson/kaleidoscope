// Port of src/core/particle_effects.py: spark bursts, flares, fireworks and mist clouds, spawned on beats and at
// random by EffectsManager. The particle tunnel (off by default on the desktop) is not ported.
import { R, int } from './pyrandom.js';
import { qcolor, copyColor, css, hsv255 } from './colors.js';

class ParticleEffect {
  constructor(cx, cy, radius) {
    this.center_x = cx; this.center_y = cy; this.radius = radius;
    this.particles = []; this.lifetime = 0; this.max_lifetime = 100; this.active = false;
    this.color = qcolor(255, 255, 255);
  }
  start() { this.active = true; this.lifetime = 0; this.generate_particles(); }
  update(bass, mids, highs, volume) {
    if (!this.active) return;
    this.lifetime += 1;
    if (this.lifetime >= this.max_lifetime) { this.active = false; return; }
    for (const p of this.particles) p.update(bass, mids, highs, volume);
    this.particles = this.particles.filter(p => p.active);
  }
  render(ctx) { if (this.active) for (const p of this.particles) p.render(ctx); }
  generate_particles() {}
}

function ellipse(ctx, style, x, y, w, h) {
  if (w <= 0 || h <= 0) return;
  ctx.fillStyle = style;
  ctx.beginPath(); ctx.ellipse(x + w / 2, y + h / 2, w / 2, h / 2, 0, 0, 2 * Math.PI); ctx.fill();
}
const withAlpha = (c, a) => { const k = copyColor(c); k.a = Math.max(0, Math.min(255, a)); return css(k); };

class EffectParticle { // "Particle" in particle_effects.py
  constructor(x, y, z = 0) {
    this.x = x; this.y = y; this.z = z;
    this.vx = 0; this.vy = 0; this.vz = 0; this.ax = 0; this.ay = 0; this.az = 0;
    this.size = 3; this.color = qcolor(255, 255, 255); this.alpha = 255; this.fade_rate = 2;
    this.lifetime = 0; this.max_lifetime = 100; this.active = true;
  }
  update() {
    this.lifetime += 1;
    if (this.lifetime >= this.max_lifetime) { this.active = false; return; }
    this.vx += this.ax; this.vy += this.ay; this.vz += this.az;
    this.x += this.vx; this.y += this.vy; this.z += this.vz;
    this.alpha = Math.max(0, int(this.alpha - this.fade_rate));
    if (this.alpha <= 0) this.active = false;
  }
  render(ctx) {
    if (!this.active) return;
    ellipse(ctx, withAlpha(this.color, int(this.alpha)), int(this.x - this.size / 2), int(this.y - this.size / 2), int(this.size), int(this.size));
  }
}

class SparkParticle extends EffectParticle {
  constructor(x, y, z = 0) {
    super(x, y, z);
    this.size = R.uniform(1, 3);
    this.color = qcolor(255, 220, 150);
    this.fade_rate = R.uniform(3, 7);
    this.max_lifetime = R.randint(30, 60);
    const angle = R.uniform(0, Math.PI * 2), speed = R.uniform(3, 7);
    this.vx = Math.cos(angle) * speed; this.vy = Math.sin(angle) * speed;
    this.vz = R.uniform(-1, 1) * speed * 0.5;
    this.ay = 0.05;
  }
  render(ctx) {
    if (!this.active) return;
    ellipse(ctx, withAlpha(this.color, int(this.alpha)), int(this.x - this.size / 2), int(this.y - this.size / 2), int(this.size), int(this.size));
    const g = this.size * 2;
    ellipse(ctx, withAlpha(this.color, int(Math.floor(this.alpha / 3))), int(this.x - g / 2), int(this.y - g / 2), int(g), int(g));
  }
}

function radial(ctx, x, y, size, inner, outer) {
  const w = int(size * 2);
  if (w <= 0 || size <= 0) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, size);
  g.addColorStop(0, inner); g.addColorStop(1, outer);
  ctx.fillStyle = g;
  const bx = int(x - size), by = int(y - size);
  ctx.beginPath(); ctx.ellipse(bx + w / 2, by + w / 2, w / 2, w / 2, 0, 0, 2 * Math.PI); ctx.fill();
}

class FlareParticle extends EffectParticle {
  constructor(x, y, z = 0) {
    super(x, y, z);
    this.base_size = R.uniform(4, 10); this.size = this.base_size;
    this.pulse_phase = R.uniform(0, Math.PI * 2); this.pulse_speed = R.uniform(0.1, 0.2);
    const hue = R.uniform(0, 0.1);
    this.color = qcolor(...hsv255(hue, 0.8, 1.0));
    this.fade_rate = R.uniform(1, 3);
    this.max_lifetime = R.randint(60, 120);
    const angle = R.uniform(0, Math.PI * 2), speed = R.uniform(0.5, 2);
    this.vx = Math.cos(angle) * speed; this.vy = Math.sin(angle) * speed;
    this.vz = R.uniform(-0.5, 0.5);
  }
  update(bass, mids, highs, volume) {
    super.update(bass, mids, highs, volume);
    this.pulse_phase += this.pulse_speed;
    const pulseFactor = 0.5 * Math.sin(this.pulse_phase) + 1.5;
    const audioFactor = 1.0 + volume + (bass * 0.5);
    this.size = this.base_size * pulseFactor * audioFactor;
  }
  render(ctx) {
    if (!this.active) return;
    radial(ctx, this.x, this.y, this.size, withAlpha(this.color, int(this.alpha)), withAlpha(this.color, Math.floor(this.alpha / 4)));
  }
}

class FireworkParticle extends EffectParticle {
  constructor(x, y, z = 0, color = null) {
    super(x, y, z);
    this.trail = [];
    this.trail_length = R.randint(3, 8);
    this.size = R.uniform(1, 3);
    if (color) this.color = color;
    else this.color = qcolor(...hsv255(R.random(), 0.9, 1.0));
    this.fade_rate = R.uniform(2, 4);
    this.max_lifetime = R.randint(40, 80);
    this.vx = R.uniform(-3, 3); this.vy = R.uniform(-3, 3); this.vz = R.uniform(-1, 1);
    this.ay = 0.08; this.drag = 0.98;
  }
  update(bass, mids, highs, volume) {
    this.trail.push([this.x, this.y]);
    if (this.trail.length > this.trail_length) this.trail.shift();
    this.vx *= this.drag; this.vy *= this.drag; this.vz *= this.drag;
    super.update(bass, mids, highs, volume);
  }
  render(ctx) {
    if (!this.active || this.trail.length < 2) return;
    ctx.lineCap = 'square';
    for (let i = 0; i < this.trail.length - 1; i++) {
      const f = i / this.trail.length;
      ctx.strokeStyle = withAlpha(this.color, int(this.alpha * f));
      ctx.lineWidth = Math.max(1, int(this.size * f));
      const [x1, y1] = this.trail[i], [x2, y2] = this.trail[i + 1];
      ctx.beginPath(); ctx.moveTo(int(x1), int(y1)); ctx.lineTo(int(x2), int(y2)); ctx.stroke();
    }
    ellipse(ctx, withAlpha(this.color, int(this.alpha)), int(this.x - this.size / 2), int(this.y - this.size / 2), int(this.size), int(this.size));
  }
}

class MistParticle extends EffectParticle {
  constructor(x, y, z = 0) {
    super(x, y, z);
    this.size = R.uniform(5, 15);
    this.color = qcolor(220, 230, 255);
    this.alpha = R.randint(40, 120);
    this.fade_rate = R.uniform(0.5, 1.0);
    this.max_lifetime = R.randint(100, 200);
    this.vx = R.uniform(-0.3, 0.3); this.vy = R.uniform(-0.3, 0.3);
    this.growth_rate = R.uniform(-0.02, 0.05);
  }
  update(bass, mids, highs, volume) {
    super.update(bass, mids, highs, volume);
    this.size += this.growth_rate;
    this.vx += R.uniform(-0.05, 0.05); this.vy += R.uniform(-0.05, 0.05);
    this.vx = Math.max(-0.5, Math.min(0.5, this.vx)); this.vy = Math.max(-0.5, Math.min(0.5, this.vy));
  }
  render(ctx) {
    if (!this.active) return;
    radial(ctx, this.x, this.y, this.size, withAlpha(this.color, int(this.alpha)), withAlpha(this.color, 0));
  }
}

export class SparkBurst extends ParticleEffect {
  constructor(cx, cy, radius) {
    super(cx, cy, radius);
    this.max_lifetime = R.randint(60, 100); this.burst_strength = R.uniform(0.8, 1.5); this.particle_count = R.randint(15, 30);
  }
  generate_particles() {
    const angle = R.uniform(0, Math.PI * 2), dist = R.uniform(0, this.radius * 0.7);
    const ox = this.center_x + Math.cos(angle) * dist, oy = this.center_y + Math.sin(angle) * dist;
    this.particles = [];
    for (let i = 0; i < this.particle_count; i++) {
      const s = new SparkParticle(ox, oy);
      s.vx *= this.burst_strength; s.vy *= this.burst_strength;
      this.particles.push(s);
    }
  }
}

export class FlareEmission extends ParticleEffect {
  constructor(cx, cy, radius) {
    super(cx, cy, radius);
    this.max_lifetime = R.randint(120, 180); this.emission_angle = R.uniform(0, Math.PI * 2);
    this.emission_width = R.uniform(Math.PI / 6, Math.PI / 3); this.particle_count = R.randint(5, 12);
  }
  generate_particles() {
    const angle = R.uniform(0, Math.PI * 2), dist = R.uniform(this.radius * 0.5, this.radius * 0.8);
    const ox = this.center_x + Math.cos(angle) * dist, oy = this.center_y + Math.sin(angle) * dist;
    const toward = R.choice([true, false]);
    const base = toward ? Math.atan2(this.center_y - oy, this.center_x - ox) : Math.atan2(oy - this.center_y, ox - this.center_x);
    this.particles = [];
    for (let i = 0; i < this.particle_count; i++) {
      const f = new FlareParticle(ox, oy);
      const a = base + R.uniform(-this.emission_width / 2, this.emission_width / 2), speed = R.uniform(0.5, 1.5);
      f.vx = Math.cos(a) * speed; f.vy = Math.sin(a) * speed;
      this.particles.push(f);
    }
  }
}

export class FireworkExplosion extends ParticleEffect {
  constructor(cx, cy, radius) {
    super(cx, cy, radius);
    this.max_lifetime = R.randint(150, 200); this.particle_count = R.randint(30, 60);
    this.color = qcolor(...hsv255(R.random(), 0.9, 1.0));
    this.explosion_height = R.uniform(0.4, 0.7); this.explosion_size = R.uniform(30, 60);
    this.explosion_stage = false; this.launch_particle = null;
  }
  start() {
    this.active = true; this.lifetime = 0; this.explosion_stage = false;
    const angle = R.uniform(0, Math.PI * 2), dist = this.radius * 0.8;
    const sx = this.center_x + Math.cos(angle) * dist, sy = this.center_y + Math.sin(angle) * dist;
    const ta = Math.atan2(this.center_y - sy, this.center_x - sx), td = dist * this.explosion_height;
    const tx = this.center_x + Math.cos(ta) * td, ty = this.center_y + Math.sin(ta) * td;
    const lp = new FireworkParticle(sx, sy, 0, this.color);
    lp.size = 3; lp.trail_length = 10;
    lp.vx = (tx - sx) / 30; lp.vy = (ty - sy) / 30; lp.ay = 0;
    this.launch_particle = lp;
    this.particles = [lp];
  }
  update(bass, mids, highs, volume) {
    super.update(bass, mids, highs, volume);
    if (!this.explosion_stage && this.launch_particle) {
      const dx = this.launch_particle.x - this.center_x, dy = this.launch_particle.y - this.center_y;
      if (Math.sqrt(dx * dx + dy * dy) <= this.radius * this.explosion_height) {
        this.explosion_stage = true;
        const ex = this.launch_particle.x, ey = this.launch_particle.y;
        this.particles = [];
        for (let i = 0; i < this.particle_count; i++) this.particles.push(new FireworkParticle(ex, ey, 0, this.color));
      }
    }
  }
}

export class MistCloud extends ParticleEffect {
  constructor(cx, cy, radius) {
    super(cx, cy, radius);
    this.max_lifetime = R.randint(200, 300); this.particle_count = R.randint(15, 30);
  }
  generate_particles() {
    const angle = R.uniform(0, Math.PI * 2), dist = R.uniform(0, this.radius * 0.8);
    const cx = this.center_x + Math.cos(angle) * dist, cy = this.center_y + Math.sin(angle) * dist;
    const cloud = R.uniform(50, 100);
    this.particles = [];
    for (let i = 0; i < this.particle_count; i++) {
      const oa = R.uniform(0, Math.PI * 2), od = R.uniform(0, cloud);
      this.particles.push(new MistParticle(cx + Math.cos(oa) * od, cy + Math.sin(oa) * od));
    }
  }
}

const EFFECTS = { spark: SparkBurst, flare: FlareEmission, firework: FireworkExplosion, mist: MistCloud };

export class EffectsManager {
  constructor(width, height) {
    this.effects = [];
    this.resize(width, height);
    this.enabled = true; this.intensity = 1.0; this.max_effects = 20;
    this.generate_on_beat = true; this.beat_threshold = 0.5; this.beat_cooldown = 0; this.beat_cooldown_time = 10;
    this.random_generation = true; this.generation_chance = 0.01;
    this.tunnel_enabled = false; this.active_tunnel = null;
    this.effect_weights = { spark: 40, flare: 30, firework: 15, mist: 15, tunnel: 0 };
    this.bass_reactivity = 1.0; this.mids_reactivity = 0.7; this.highs_reactivity = 0.5; this.volume_reactivity = 0.8;
    this.effect_enabled = { spark: true, flare: true, firework: true, mist: true, tunnel: false };
  }

  update(spectrum, bands, volume, isBeat = false) {
    if (!this.enabled) return;
    if (this.generate_on_beat && isBeat && volume > this.beat_threshold) {
      if (this.beat_cooldown <= 0) {
        this.generate_effect_on_beat(bands[0], bands[1], bands[2], volume);
        this.beat_cooldown = this.beat_cooldown_time;
      }
    }
    if (this.beat_cooldown > 0) this.beat_cooldown -= 1;
    if (this.random_generation && R.random() < this.generation_chance * this.intensity) {
      this.generate_random_effect(bands[0], bands[1], bands[2], volume);
    }
    for (const e of this.effects) {
      e.update(bands[0] * this.bass_reactivity, bands[1] * this.mids_reactivity, bands[2] * this.highs_reactivity, volume * this.volume_reactivity);
    }
    this.effects = this.effects.filter(e => e.active);
  }

  render(ctx) { if (this.enabled) for (const e of this.effects) e.render(ctx); }

  generate_effect_on_beat(bass, mids, highs, volume) {
    if (this.effects.length >= this.max_effects) return;
    const w = this.effect_weights;
    const probs = { spark: highs * 2 * w.spark, flare: mids * 1.5 * w.flare, firework: bass * 3 * w.firework, mist: (1.0 - volume) * w.mist };
    const filtered = Object.fromEntries(Object.entries(probs).filter(([k]) => this.effect_enabled[k]));
    if (!Object.keys(filtered).length) return;
    this.create_effect(this.weighted_choice(filtered));
  }

  generate_random_effect() {
    if (this.effects.length >= this.max_effects) return;
    const filtered = Object.fromEntries(Object.entries(this.effect_weights).filter(([k]) => this.effect_enabled[k]));
    if (!Object.keys(filtered).length) return;
    this.create_effect(this.weighted_choice(filtered));
  }

  create_effect(type) {
    const cls = EFFECTS[type];
    if (!cls) return;
    const e = new cls(this.center_x, this.center_y, this.radius);
    e.start();
    this.effects.push(e);
  }

  weighted_choice(weights) {
    const keys = Object.keys(weights);
    let total = 0;
    for (const k of keys) total += weights[k];
    if (total <= 0) return R.choice(keys);
    const r = R.uniform(0, total);
    let running = 0;
    for (const k of keys) { running += weights[k]; if (running > r) return k; }
    return R.choice(keys);
  }

  resize(width, height) {
    this.width = width; this.height = height;
    this.center_x = int(width / 2); this.center_y = int(height / 2);
    this.radius = int(Math.min(width, height) / 2);
  }
  clear_effects() { this.effects = []; }
  set_enabled(v) { this.enabled = v; }
  set_intensity(v) { this.intensity = Math.max(0.0, Math.min(2.0, v)); }
  set_effect_enabled(type, v) { if (type in this.effect_enabled) this.effect_enabled[type] = v; }
  set_beat_response(enabled, threshold) { this.generate_on_beat = enabled; this.beat_threshold = Math.max(0.0, Math.min(1.0, threshold)); }
  set_random_generation(enabled, chance) { this.random_generation = enabled; this.generation_chance = Math.max(0.0, Math.min(0.1, chance)); }
  set_effect_weights(weights) { for (const [k, v] of Object.entries(weights)) if (k in this.effect_weights) this.effect_weights[k] = Math.max(0, v); }
  set_audio_reactivity(b, m, h, v) {
    this.bass_reactivity = Math.max(0.0, b); this.mids_reactivity = Math.max(0.0, m);
    this.highs_reactivity = Math.max(0.0, h); this.volume_reactivity = Math.max(0.0, v);
  }
}
