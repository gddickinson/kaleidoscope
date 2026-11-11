// Colours as {r, g, b, a} (0-255 integers, like QColor) and Python's colorsys.hsv_to_rgb.
export const qcolor = (r, g, b, a = 255) => ({ r, g, b, a });
export const copyColor = c => ({ ...c });
export const css = c => `rgba(${c.r},${c.g},${c.b},${(c.a / 255).toFixed(3)})`;

// '#RRGGBB' (QColor.setNamedColor) -> colour with alpha 255.
export function named(hex) {
  const v = parseInt(String(hex).replace('#', ''), 16);
  return qcolor((v >> 16) & 255, (v >> 8) & 255, v & 255);
}
export const toHex = c => '#' + [c.r, c.g, c.b].map(v => v.toString(16).padStart(2, '0')).join('').toUpperCase();

export function hsvToRgb(h, s, v) {
  if (s === 0.0) return [v, v, v];
  let i = Math.trunc(h * 6.0);
  const f = (h * 6.0) - i;
  const p = v * (1.0 - s), q = v * (1.0 - s * f), t = v * (1.0 - s * (1.0 - f));
  i = i % 6;
  return [[v, t, p], [q, v, p], [p, v, t], [p, q, v], [t, p, v], [v, p, q]][i];
}

// [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
export const hsv255 = (h, s, v) => hsvToRgb(h, s, v).map(c => Math.trunc(c * 255));
