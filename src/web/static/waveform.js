// Port of CircularWaveform (src/core/visualization_components.py): the ring of spectrum bars around the kaleidoscope.
import { int } from './pyrandom.js';
import { qcolor, css } from './colors.js';

// np.interp(np.linspace(0, n, num), np.arange(n), fp) for the upsampling branch.
export function interpLinspace(fp, num) {
  const n = fp.length, step = n / (num - 1), out = new Float64Array(num);
  for (let i = 0; i < num; i++) {
    const x = i === num - 1 ? n : i * step;
    if (x >= n - 1) { out[i] = fp[n - 1]; continue; }
    const j = Math.floor(x), slope = (fp[j + 1] - fp[j]) / 1.0;
    out[i] = slope * (x - j) + fp[j];
  }
  return out;
}

export class CircularWaveform {
  constructor(radius = 300, innerRadiusPct = 0.8, numSamples = 128) {
    this.radius = radius;
    this.inner_radius_pct = innerRadiusPct;
    this.inner_radius = radius * innerRadiusPct;
    this.num_samples = numSamples;
    this.waveform_data = new Float64Array(numSamples);
    this.smoothed_data = new Float64Array(numSamples);
    this.smoothing = 0.3;
    this.line_width = 2;
    this.color = qcolor(255, 255, 255, 180);
    this.secondary_color = qcolor(0, 200, 255, 180);
    this.rotate_speed = 0.01;
    this.rotation = 0;
    this.use_gradient = true;
    this.amplitude = 1.0;
    this.bass_influence = 0.5;
    this.show_reflection = true;
    this.reflection_alpha = 0.3;
  }

  update(rawAudio, spectrum, volume, bassValue) {
    if (spectrum.length > this.num_samples) {
      const step = spectrum.length / this.num_samples;
      this.waveform_data = Float64Array.from({ length: this.num_samples }, (_, i) => spectrum[int(i * step)]);
    } else {
      this.waveform_data = interpLinspace(spectrum, this.num_samples);
    }
    const s = this.smoothing;
    this.smoothed_data = this.smoothed_data.map((v, i) => v * s + this.waveform_data[i] * (1 - s));
    this.amplitude = 0.5 + (volume * 1.5) + (bassValue * this.bass_influence);
    this.rotation += this.rotate_speed;
    if (this.rotation > 2 * Math.PI) this.rotation -= 2 * Math.PI;
  }

  render(ctx, cx, cy) {
    const inner = this.inner_radius;
    ctx.lineWidth = Math.max(1, this.line_width); ctx.lineCap = 'square';
    for (let i = 0; i < this.num_samples; i++) {
      const angle = (i / this.num_samples * 2 * Math.PI) + this.rotation;
      const value = Math.max(0, Math.min(1, this.smoothed_data[i] * this.amplitude));
      const c = Math.cos(angle), s = Math.sin(angle);
      const sx = cx + c * inner, sy = cy + s * inner;
      const ex = cx + c * (inner + (value * (this.radius - inner))), ey = cy + s * (inner + (value * (this.radius - inner)));
      let col = this.color;
      if (this.use_gradient) {
        const a = this.color, b = this.secondary_color, t = value;
        col = qcolor(int(a.r * (1 - t) + b.r * t), int(a.g * (1 - t) + b.g * t), int(a.b * (1 - t) + b.b * t), int(a.a * (1 - t) + b.a * t));
      }
      line(ctx, css(col), sx, sy, ex, ey);
      if (this.show_reflection) {
        const rc = { ...col, a: int(col.a * this.reflection_alpha) };
        line(ctx, css(rc), cx - (sx - cx), cy - (sy - cy), cx - (ex - cx), cy - (ey - cy));
      }
    }
  }

  set_radius(radius, innerRadiusPct = null) {
    this.radius = radius;
    if (innerRadiusPct !== null) this.inner_radius_pct = innerRadiusPct;
    this.inner_radius = this.radius * this.inner_radius_pct;
  }
  set_colors(primary, secondary = null) {
    this.color = primary;
    if (secondary) { this.secondary_color = secondary; this.use_gradient = true; } else this.use_gradient = false;
  }
  set_line_width(w) { this.line_width = w; }
  set_rotation_speed(s) { this.rotate_speed = s; }
  set_reflection(show, alpha = 0.3) { this.show_reflection = show; this.reflection_alpha = alpha; }
}

function line(ctx, style, x1, y1, x2, y2) {
  ctx.strokeStyle = style;
  ctx.beginPath(); ctx.moveTo(int(x1), int(y1)); ctx.lineTo(int(x2), int(y2)); ctx.stroke();
}
