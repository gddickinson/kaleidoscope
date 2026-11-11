// Canvas port of KaleidoscopeEngine.render(), ShapeRenderer, ColorGenerator, SymmetryRenderer and EffectProcessor
// (src/core/kaleidoscope_engine.py, visualization_components.py). Particle trails are drawn to a transparent buffer,
// the buffer is repeated by the symmetry mode onto a black frame, then the waveform ring, particle effects and
// wireframes are drawn on top, then blur and distortion. Like the desktop widget (opaque paint, no clear), the frame
// is painted over the previous one, which only shows where the distortion leaves pixels transparent.
import { int } from './pyrandom.js';
import { qcolor, css, hsv255 } from './colors.js';

function makeCanvas() { return document.createElement('canvas'); }

function particleColor(e, px, i, n, trailLen, alpha) {
  if (e.color_mode === 'spectrum') {
    const len = e.spectrum_data.length;
    const fi = Math.min(int(Math.abs(px / e.radius) * len), len - 1);
    const intensity = Math.min(1.0, e.spectrum_data[fi] * 2);
    const [r, g, b] = hsv255((fi / len) % 1.0, 0.8, intensity);
    return qcolor(r, g, b, alpha);
  }
  if (e.color_mode === 'solid') return qcolor(e.base_color.r, e.base_color.g, e.base_color.b, alpha);
  const ratio = (Math.sin(e.rotation * 2 + i / trailLen * Math.PI) + 1) / 2;
  const a = e.base_color, b = e.secondary_color;
  return qcolor(int(a.r * ratio + b.r * (1 - ratio)), int(a.g * ratio + b.g * (1 - ratio)), int(a.b * ratio + b.b * (1 - ratio)), alpha);
}

export function renderShape(ctx, type, x, y, size, color) {
  ctx.fillStyle = css(color);
  ctx.beginPath();
  if (type === 'square') {
    ctx.rect(int(x - size / 2), int(y - size / 2), int(size), int(size));
  } else if (type === 'triangle') {
    ctx.moveTo(int(x), int(y - size));
    ctx.lineTo(int(x - size * 0.866), int(y + size * 0.5));
    ctx.lineTo(int(x + size * 0.866), int(y + size * 0.5));
    ctx.closePath();
  } else if (type === 'star') {
    for (let i = 0; i < 5; i++) {
      let angle = Math.PI / 2 + i * 2 * Math.PI / 5;
      ctx.lineTo(int(x + Math.cos(angle) * size), int(y + Math.sin(angle) * size));
      angle += Math.PI / 5;
      ctx.lineTo(int(x + Math.cos(angle) * size * 0.4), int(y + Math.sin(angle) * size * 0.4));
    }
    ctx.closePath();
  } else { // circle: drawEllipse(QPoint(int(x), int(y)), int(size), int(size))
    const r = Math.abs(int(size));
    if (r === 0) return;
    ctx.ellipse(int(x), int(y), r, r, 0, 0, 2 * Math.PI);
  }
  ctx.fill();
}

export class Renderer {
  constructor(engine, canvas) {
    this.e = engine; this.canvas = canvas; this.ctx = canvas.getContext('2d');
    this.buffer = makeCanvas(); this.final = makeCanvas(); this.small = makeCanvas();
  }

  render() {
    const e = this.e, W = e.width, H = e.height;
    for (const c of [this.buffer, this.final]) if (c.width !== W || c.height !== H) { c.width = W; c.height = H; }
    if (this.canvas.width !== W || this.canvas.height !== H) { this.canvas.width = W; this.canvas.height = H; }
    const b = this.buffer.getContext('2d');
    b.clearRect(0, 0, W, H);
    this.drawParticles(b);
    const f = this.final.getContext('2d');
    f.globalAlpha = 1; f.fillStyle = '#000'; f.fillRect(0, 0, W, H);
    this.applySymmetry(f);
    if (e.enable_waveform) e.circular_waveform.render(f, e.center_x, e.center_y);
    e.effects_manager.render(f);
    if (e.enable_wireframe) e.wireframe_manager.render(f, e.center_x, e.center_y, e.perspective);
    if (e.blur_amount > 0) this.blur(f, W, H, e.blur_amount);
    if (e.distortion > 0) this.distort(f, W, H);
    this.ctx.drawImage(this.final, 0, 0);
  }

  drawParticles(b) {
    const e = this.e;
    for (const p of e.particles) {
      if (!p.trail.length) continue;
      const n = p.trail.length;
      p.trail.forEach(([tx, ty, tz], i) => {
        let px = tx, py = ty, scale = 1.0;
        if (e.enable_3d) {
          const [rx, ry, rz] = e.apply_3d_rotation(tx, ty, tz);
          scale = e.perspective / (e.perspective + rz);
          px = rx * scale; py = ry * scale;
        }
        const alpha = int(255 * (i / n));
        if (alpha === 0) return; // fully transparent: QPainter draws nothing
        const size = p.current_size * (i / n) * scale;
        renderShape(b, e.shape_type, e.center_x + px, e.center_y + py, size, particleColor(e, px, i, n, p.trail.length, alpha));
      });
    }
  }

  applySymmetry(f) {
    const e = this.e, cx = e.center_x, cy = e.center_y, buf = this.buffer, W = e.width, H = e.height;
    if (e.symmetry_mode === 'radial') {
      for (let i = 0; i < e.segments; i++) {
        const angle = i * (2 * Math.PI / e.segments) + e.rotation;
        f.save(); f.translate(cx, cy); f.rotate(-angle); f.drawImage(buf, -cx, -cy); f.restore();
      }
    } else if (e.symmetry_mode === 'mirror') {
      f.drawImage(buf, 0, 0);
      for (const [sx, sy] of [[-1, 1], [1, -1], [-1, -1]]) {
        f.save(); f.translate(sx < 0 ? W : 0, sy < 0 ? H : 0); f.scale(sx, sy); f.drawImage(buf, 0, 0); f.restore();
      }
    } else if (e.symmetry_mode === 'spiral') {
      for (let i = 0; i < 8; i++) {
        const scale = 1.0 - (i * 0.1), angle = e.rotation + i * Math.PI / 4;
        f.save(); f.translate(cx, cy); f.rotate(-angle); f.scale(scale, scale); f.drawImage(buf, -cx, -cy); f.restore();
      }
    }
  }

  // EffectProcessor.apply_blur: `amount` passes of quarter-size smooth downscale + upscale painted at opacity 0.7.
  blur(f, W, H, amount) {
    const sw = Math.max(1, int(W / 4)), sh = Math.max(1, int(H / 4)), s = this.small;
    if (s.width !== sw || s.height !== sh) { s.width = sw; s.height = sh; }
    const sc = s.getContext('2d');
    for (let k = 0; k < int(amount); k++) {
      sc.imageSmoothingQuality = 'high'; sc.clearRect(0, 0, sw, sh); sc.drawImage(this.final, 0, 0, sw, sh);
      f.save(); f.globalAlpha = 0.7; f.imageSmoothingQuality = 'high'; f.drawImage(s, 0, 0, W, H); f.restore();
    }
  }

  // EffectProcessor.apply_distortion: every second pixel inside the radius is sampled from a sine-displaced source.
  distort(f, W, H) {
    const e = this.e, src = f.getImageData(0, 0, W, H), out = f.createImageData(W, H);
    const s = src.data, o = out.data, amount = e.distortion, cx = e.center_x, cy = e.center_y;
    for (let x = 0; x < W; x += 2) {
      for (let y = 0; y < H; y += 2) {
        const dx = x - cx, dy = y - cy, d = Math.sqrt(dx * dx + dy * dy);
        if (d >= e.radius) continue;
        const angle = Math.atan2(dy, dx), factor = amount * Math.sin(d / 20 + e.rotation * 10) * 10;
        const sx = int(x + Math.cos(angle) * factor), sy = int(y + Math.sin(angle) * factor);
        if (sx < 0 || sx >= W || sy < 0 || sy >= H) continue;
        const si = (sy * W + sx) * 4, oi = (y * W + x) * 4;
        o[oi] = s[si]; o[oi + 1] = s[si + 1]; o[oi + 2] = s[si + 2]; o[oi + 3] = s[si + 3];
      }
    }
    f.putImageData(out, 0, 0);
  }
}

// FrequencyDisplayWidget (src/ui/widgets.py): spectrum bars, band indicators and the volume meter.
export function drawFrequencyDisplay(ctx, spectrum, bands, volume) {
  const W = ctx.canvas.width, H = ctx.canvas.height;
  if (!spectrum.some(v => v)) return;
  ctx.fillStyle = 'rgb(30,30,30)'; ctx.fillRect(0, 0, W, H);
  const bw = W / spectrum.length;
  spectrum.forEach((v, i) => {
    const norm = Number.isNaN(v) ? 0 : Math.min(1.0, v * 2), bh = int(norm * H);
    const [r, g, b] = qtHsv(int(240 - (i / spectrum.length * 240)), 240, 200);
    ctx.fillStyle = `rgb(${r},${g},${b})`;
    ctx.fillRect(int(i * bw), H - bh, Math.max(1, int(bw - 1)), bh);
  });
  const bandW = W / 3, cols = ['rgb(0,0,200)', 'rgb(0,200,0)', 'rgb(200,0,0)'];
  ctx.font = '12px sans-serif';
  bands.forEach((v, i) => {
    const norm = Number.isNaN(v) ? 0 : Math.min(1.0, v * 2), ih = int(norm * H * 0.2);
    ctx.fillStyle = cols[i]; ctx.fillRect(int(i * bandW), 0, Math.max(1, int(bandW - 1)), ih);
    ctx.fillStyle = '#fff'; ctx.fillText(['Bass', 'Mids', 'Highs'][i], int(i * bandW + 5), ih + 15);
  });
  const vol = Number.isNaN(volume) ? 0 : volume;
  ctx.fillStyle = 'rgb(200,200,0)'; ctx.fillRect(0, H - 10, int(vol * W), 10);
  ctx.fillStyle = '#fff'; ctx.fillText(`Volume: ${int(volume * 100)}%`, 5, H - 15);
}

// QColor.fromHsv(h 0-359, s 0-255, v 0-255) -> [r, g, b]
function qtHsv(h, s, v) {
  const [r, g, b] = hsv255(((h % 360) + 360) % 360 / 360, s / 255, v / 255);
  return [r, g, b];
}
