// Port of the wireframe classes in src/core/visualization_components.py: WireframeShape and its seven solids,
// WireframeShapeFactory and WireframeManager (audio-driven rotation, pulse, colour modes, morphing, echo, glow).
// Colour objects are shared and mutated exactly as the QColor objects are (set_colors() sets the alpha in place).
import { R, int, pymod } from './pyrandom.js';
import { qcolor, copyColor, css, hsv255 } from './colors.js';

export class WireframeShape {
  constructor(size = 100) {
    this.size = size;
    this.rotation_x = 0; this.rotation_y = 0; this.rotation_z = 0;
    this.position = [0, 0, 0];
    this.vertices = []; this.edges = [];
    this.pulse_size = 1.0;
    this.base_color = qcolor(255, 255, 255);
    this.edge_thickness = 2;
    this.morph_target = null; this.morph_progress = 0.0;
    this.edge_opacity = 255; this.show_edges = true;
    this.rotation_speed_x = 0.01; this.rotation_speed_y = 0.008; this.rotation_speed_z = 0.005;
    this.pulse_strength = 0.5; this.color_reactivity = 1.0; this.thickness_reactivity = 1.0;
    this._generate_shape();
  }
  _generate_shape() {}

  update(bass, mids, highs, volume, rotationSpeed = 1.0) {
    this.rotation_x += bass * this.rotation_speed_x * rotationSpeed;
    this.rotation_y += mids * this.rotation_speed_y * rotationSpeed;
    this.rotation_z += highs * this.rotation_speed_z * rotationSpeed;
    this.pulse_size = 1.0 + volume * this.pulse_strength;
    const r = Math.min(255, int(bass * 150 * this.color_reactivity + 100));
    const g = Math.min(255, int(mids * 150 * this.color_reactivity + 100));
    const b = Math.min(255, int(highs * 150 * this.color_reactivity + 100));
    this.base_color = qcolor(r, g, b, this.edge_opacity);
    this.edge_thickness = 1 + int(volume * 3 * this.thickness_reactivity);
    if (this.morph_target && this.morph_progress < 1.0) {
      this.morph_progress += 0.02;
      if (this.morph_progress > 1.0) {
        this.morph_progress = 1.0;
        this.vertices = this.morph_target.vertices.slice();
        this.edges = this.morph_target.edges.slice();
        this.morph_target = null;
        this.morph_progress = 0.0;
      }
    }
  }

  _rotate_point(x, y, z) {
    let yRot = y * Math.cos(this.rotation_x) - z * Math.sin(this.rotation_x);
    let zRot = y * Math.sin(this.rotation_x) + z * Math.cos(this.rotation_x);
    y = yRot; z = zRot;
    const xRot = x * Math.cos(this.rotation_y) + z * Math.sin(this.rotation_y);
    zRot = -x * Math.sin(this.rotation_y) + z * Math.cos(this.rotation_y);
    x = xRot; z = zRot;
    const xr = x * Math.cos(this.rotation_z) - y * Math.sin(this.rotation_z);
    yRot = x * Math.sin(this.rotation_z) + y * Math.cos(this.rotation_z);
    return [xr, yRot, z];
  }

  _transform_vertices(vertices, size, cx, cy, perspective = 800) {
    return vertices.map(v => {
      const [x, y, z] = this._rotate_point(v[0] * size, v[1] * size, v[2] * size);
      const scale = perspective / (perspective + z);
      return [cx + x * scale, cy + y * scale];
    });
  }

  start_morph(target) { this.morph_target = target; this.morph_progress = 0.0; }

  set_colors(color, opacity = 255) {
    this.base_color = color;
    this.edge_opacity = opacity;
    this.base_color.a = opacity;
  }

  // QPainter drawing: pen of base_color, width edge_thickness, integer line ends.
  render(ctx, cx, cy, perspective = 800) {
    const size = this.size * this.pulse_size;
    let pts;
    if (this.morph_target && this.morph_progress < 1.0) {
      const main = this._transform_vertices(this.vertices, size, cx, cy, perspective);
      const target = this._transform_vertices(this.morph_target.vertices, size, cx, cy, perspective);
      const t = this.morph_progress;
      pts = main.map((p, i) => (i < target.length ? [p[0] * (1 - t) + target[i][0] * t, p[1] * (1 - t) + target[i][1] * t] : p));
    } else {
      pts = this._transform_vertices(this.vertices, size, cx, cy, perspective);
    }
    if (this.show_edges) strokeEdges(ctx, pts, this.edges, css(this.base_color), this.edge_thickness);
  }
}

function strokeEdges(ctx, pts, edges, style, width) {
  ctx.strokeStyle = style; ctx.lineWidth = Math.max(1, width); ctx.lineCap = 'square';
  ctx.beginPath();
  for (const [a, b] of edges) {
    if (a >= pts.length || b >= pts.length) continue;
    ctx.moveTo(int(pts[a][0]), int(pts[a][1])); ctx.lineTo(int(pts[b][0]), int(pts[b][1]));
  }
  ctx.stroke();
}

export class WireframeCube extends WireframeShape {
  _generate_shape() {
    const h = 0.5;
    this.vertices = [[-h, -h, -h], [h, -h, -h], [h, h, -h], [-h, h, -h], [-h, -h, h], [h, -h, h], [h, h, h], [-h, h, h]];
    this.edges = [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]];
  }
}
export class WireframePyramid extends WireframeShape {
  _generate_shape() {
    const h = 0.5;
    this.vertices = [[-h, -h, -h], [h, -h, -h], [h, -h, h], [-h, -h, h], [0, h, 0]];
    this.edges = [[0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 4], [2, 4], [3, 4]];
  }
}
export class WireframeSphere extends WireframeShape {
  _generate_shape() {
    const slices = 12, stacks = 6;
    this.vertices = [[0, 0.5, 0], [0, -0.5, 0]];
    for (let i = 1; i < stacks; i++) {
      const phi = Math.PI * i / stacks, y = 0.5 * Math.cos(phi), radius = 0.5 * Math.sin(phi);
      for (let j = 0; j < slices; j++) {
        const theta = 2 * Math.PI * j / slices;
        this.vertices.push([radius * Math.cos(theta), y, radius * Math.sin(theta)]);
      }
    }
    this.edges = [];
    for (let i = 0; i < slices; i++) { this.edges.push([0, i + 2]); this.edges.push([1, i + 2 + (stacks - 2) * slices]); }
    for (let i = 1; i < stacks; i++) {
      const start = 2 + (i - 1) * slices;
      for (let j = 0; j < slices; j++) this.edges.push([start + j, start + (j + 1) % slices]);
    }
    for (let i = 1; i < stacks - 1; i++) {
      for (let j = 0; j < slices; j++) this.edges.push([2 + (i - 1) * slices + j, 2 + i * slices + j]);
    }
  }
}
export class WireframeOctahedron extends WireframeShape {
  _generate_shape() {
    this.vertices = [[0.5, 0, 0], [-0.5, 0, 0], [0, 0.5, 0], [0, -0.5, 0], [0, 0, 0.5], [0, 0, -0.5]];
    this.edges = [[0, 2], [0, 3], [0, 4], [0, 5], [1, 2], [1, 3], [1, 4], [1, 5], [2, 4], [2, 5], [3, 4], [3, 5]];
  }
}
export class WireframeDodecahedron extends WireframeShape {
  _generate_shape() {
    const phi = (1 + Math.sqrt(5)) / 2, a = 0.5 / phi, b = phi / (2 * phi);
    const v = [[a, a, a], [-a, a, a], [-a, -a, a], [a, -a, a], [a, a, -a], [-a, a, -a], [-a, -a, -a], [a, -a, -a],
      [0, 0.5, b], [0, -0.5, b], [0, 0.5, -b], [0, -0.5, -b], [b, 0, 0.5], [-b, 0, 0.5], [b, 0, -0.5], [-b, 0, -0.5],
      [0.5, b, 0], [-0.5, b, 0], [0.5, -b, 0], [-0.5, -b, 0]];
    const maxDim = Math.max(...v.map(p => Math.max(Math.abs(p[0]), Math.abs(p[1]), Math.abs(p[2]))));
    this.vertices = v.map(p => [p[0] / maxDim, p[1] / maxDim, p[2] / maxDim]);
    this.edges = [[0, 12], [12, 4], [4, 16], [16, 8], [8, 0], [1, 8], [8, 16], [16, 17], [17, 13], [13, 1],
      [2, 13], [13, 19], [19, 9], [9, 3], [3, 2], [0, 3], [3, 9], [9, 18], [18, 12], [12, 0],
      [4, 14], [14, 7], [7, 11], [11, 10], [10, 4], [5, 10], [10, 11], [11, 19], [19, 15], [15, 5],
      [6, 15], [15, 19], [19, 13], [13, 17], [17, 6], [7, 18], [18, 9], [9, 19], [19, 11], [11, 7],
      [0, 8], [8, 1], [1, 13], [13, 2], [2, 0], [14, 4], [4, 10], [10, 5], [5, 15], [15, 14],
      [6, 17], [17, 16], [16, 4], [4, 14], [14, 6], [7, 14], [14, 18], [18, 3], [3, 0], [0, 7]];
  }
}
export class WireframeTetrahedron extends WireframeShape {
  _generate_shape() {
    this.vertices = [[0, 0.5, 0], [-0.5, -0.289, 0.289], [0.5, -0.289, 0.289], [0, -0.289, -0.577]];
    this.edges = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]];
  }
}
export class WireframeTorus extends WireframeShape {
  _generate_shape() {
    const Rr = 0.3, r = 0.1, segments = 16, rings = 16;
    this.vertices = [];
    for (let i = 0; i < rings; i++) {
      const theta = 2 * Math.PI * i / rings, ct = Math.cos(theta), st = Math.sin(theta);
      for (let j = 0; j < segments; j++) {
        const phi = 2 * Math.PI * j / segments, cp = Math.cos(phi), sp = Math.sin(phi);
        this.vertices.push([(Rr + r * cp) * ct, r * sp, (Rr + r * cp) * st]);
      }
    }
    this.edges = [];
    for (let i = 0; i < rings; i++) for (let j = 0; j < segments; j++) this.edges.push([i * segments + j, i * segments + (j + 1) % segments]);
    for (let i = 0; i < rings; i++) for (let j = 0; j < segments; j++) this.edges.push([i * segments + j, ((i + 1) % rings) * segments + j]);
  }
}

const SHAPE_MAP = { cube: WireframeCube, pyramid: WireframePyramid, sphere: WireframeSphere, octahedron: WireframeOctahedron,
  dodecahedron: WireframeDodecahedron, tetrahedron: WireframeTetrahedron, torus: WireframeTorus };

export function createShape(type, size = 100) {
  const cls = SHAPE_MAP[type.toLowerCase()] || WireframeCube;
  return new cls(size);
}
const typeName = shape => shape.constructor.name.replace('Wireframe', '').toLowerCase();

export class WireframeManager {
  constructor(size = 100) {
    this.base_size = size; this.current_shape = null; this.shapes = [];
    this.available_shapes = Object.keys(SHAPE_MAP);
    this.beat_sensitivity = 1.0; this.auto_morph = false; this.morph_on_beat = false; this.rotation_speed = 1.0;
    this.multi_shape_mode = false; this.shape_count = 1; this.beat_counter = 0; this.last_beat_time = 0; this.beat_interval = 30;
    this.show_edges = true; this.show_vertices = false; this.vertex_size = 3; this.edge_glow = false; this.glow_intensity = 0.5;
    this.show_echo = false; this.echo_count = 3; this.echo_opacity = 0.3; this.echo_spacing = 0.2;
    this.color_mode = 'audio_reactive';
    this.custom_color = qcolor(255, 255, 255); this.secondary_color = qcolor(0, 150, 255);
    this.rainbow_speed = 0.02; this.rainbow_offset = 0;
    this.current_shape = createShape('cube', this.base_size);
    this.shapes = [this.current_shape];
  }

  update(bass, mids, highs, volume, isBeat) {
    if (this.color_mode === 'rainbow') {
      this.rainbow_offset += this.rainbow_speed;
      if (this.rainbow_offset > 1.0) this.rainbow_offset -= 1.0;
    }
    this._handle_morphing(isBeat, volume);
    for (const shape of this.shapes) {
      shape.update(bass, mids, highs, volume, this.rotation_speed);
      if (this.color_mode === 'solid') {
        shape.set_colors(this.custom_color);
      } else if (this.color_mode === 'rainbow') {
        const hue = pymod(this.rainbow_offset + shape.rotation_z / Math.PI, 1.0);
        const [r, g, b] = hsv255(hue, 0.8, 0.9);
        shape.set_colors(qcolor(r, g, b));
      } else if (this.color_mode === 'gradient') {
        const ratio = (Math.sin(shape.rotation_z * 2) + 1) / 2;
        const c = this.custom_color, s = this.secondary_color;
        shape.set_colors(qcolor(int(c.r * (1 - ratio) + s.r * ratio), int(c.g * (1 - ratio) + s.g * ratio), int(c.b * (1 - ratio) + s.b * ratio)));
      }
    }
  }

  _handle_morphing(isBeat, volume) {
    if (isBeat && volume > 0.1) {
      this.beat_counter += 1;
      this.last_beat_time = 0;
      if (this.morph_on_beat && this.beat_counter % 4 === 0) this._morph_to_random_shape();
    } else {
      this.last_beat_time += 1;
    }
    if (this.auto_morph && this.last_beat_time > this.beat_interval) {
      this._morph_to_random_shape();
      this.last_beat_time = 0;
    }
  }

  _morph_to_random_shape() {
    const available = this.available_shapes.filter(s => !(this.current_shape instanceof SHAPE_MAP[s]));
    if (!available.length) return;
    const type = R.choice(available);
    const newShape = createShape(type, this.base_size);
    for (const shape of this.shapes) {
      const target = createShape(type, this.base_size);
      target.rotation_x = shape.rotation_x; target.rotation_y = shape.rotation_y; target.rotation_z = shape.rotation_z;
      shape.start_morph(target);
    }
    this.current_shape = newShape;
  }

  render(ctx, cx, cy, perspective = 800) {
    ctx.save();
    if (this.show_echo) this._render_echo(ctx, cx, cy, perspective);
    for (const shape of this.shapes) {
      shape.show_edges = this.show_edges;
      if (this.edge_glow) {
        const glow = copyColor(shape.base_color); glow.a = 100;
        strokeEdges(ctx, this._project(shape, cx, cy, perspective), shape.edges, css(glow), shape.edge_thickness + 4);
      }
      shape.render(ctx, cx, cy, perspective);
      if (this.show_vertices) {
        ctx.fillStyle = css(shape.base_color);
        const d = this.vertex_size;
        for (const [px, py] of this._project(shape, cx, cy, perspective)) {
          ctx.beginPath(); ctx.ellipse(int(px - d / 2) + d / 2, int(py - d / 2) + d / 2, d / 2, d / 2, 0, 0, 2 * Math.PI); ctx.fill();
        }
      }
    }
    ctx.restore();
  }

  _project(shape, cx, cy, perspective) {
    return shape._transform_vertices(shape.vertices, shape.size * shape.pulse_size, cx, cy, perspective);
  }

  _render_echo(ctx, cx, cy, perspective) {
    for (let i = 0; i < this.echo_count; i++) {
      const echoOpacity = int(255 * this.echo_opacity * (1 - i / this.echo_count));
      for (const shape of this.shapes) {
        const echo = new shape.constructor(shape.size);
        echo.vertices = shape.vertices.slice(); echo.edges = shape.edges.slice();
        const offset = (i + 1) * this.echo_spacing;
        echo.rotation_x = shape.rotation_x - offset; echo.rotation_y = shape.rotation_y - offset; echo.rotation_z = shape.rotation_z - offset;
        const c = copyColor(shape.base_color); c.a = echoOpacity;
        echo.set_colors(c, echoOpacity);
        echo.edge_thickness = Math.max(1, shape.edge_thickness - i);
        echo.render(ctx, cx, cy, perspective);
      }
    }
  }

  set_shape(type, morph = false) {
    if (morph) {
      for (const shape of this.shapes) {
        const target = createShape(type, this.base_size);
        target.rotation_x = shape.rotation_x; target.rotation_y = shape.rotation_y; target.rotation_z = shape.rotation_z;
        shape.start_morph(target);
      }
    } else {
      this.current_shape = createShape(type, this.base_size);
      this.shapes = [this.current_shape];
      if (this.multi_shape_mode) {
        for (let i = 1; i < this.shape_count; i++) {
          const shape = createShape(type, this.base_size);
          shape.rotation_x = Math.PI * i / this.shape_count; shape.rotation_z = Math.PI * i / this.shape_count;
          this.shapes.push(shape);
        }
      }
    }
  }
  set_multi_shape_mode(enabled, count = 3) {
    this.multi_shape_mode = enabled;
    this.shape_count = enabled ? count : 1;
    this.set_shape(typeName(this.current_shape));
  }
  set_size(size) { this.base_size = size; for (const s of this.shapes) s.size = size; }
  set_rotation_speed(v) { this.rotation_speed = v; }
  set_color_mode(m) { this.color_mode = m; }
  set_custom_colors(primary, secondary = null) { this.custom_color = primary; if (secondary) this.secondary_color = secondary; }
  set_effects(showVertices, vertexSize, edgeGlow, glowIntensity) {
    this.show_vertices = showVertices; this.vertex_size = vertexSize; this.edge_glow = edgeGlow; this.glow_intensity = glowIntensity;
  }
  set_echo_effect(enabled, count = 3, opacity = 0.3, spacing = 0.2) {
    this.show_echo = enabled; this.echo_count = count; this.echo_opacity = opacity; this.echo_spacing = spacing;
  }
  set_beat_response(autoMorph, morphOnBeat, beatInterval = 30) {
    this.auto_morph = autoMorph; this.morph_on_beat = morphOnBeat; this.beat_interval = beatInterval;
  }
  set_edges_visible(v) { this.show_edges = v; for (const s of this.shapes) s.show_edges = v; }
}
