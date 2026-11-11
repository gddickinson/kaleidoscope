// The control panel: the desktop ControlPanel's tabs, groups, labels, ranges and defaults (from /api/defaults), built
// as HTML controls. onChange(name, value) fires on every change; the page then re-applies all settings to the engine
// as the desktop does (apply_to_engine on every slider, combo or check-box change).
import { esc } from './core.js';
import { HIDDEN, UNPORTED_GROUPS, UNPORTED_TABS } from './settings.js';

// Shown next to sliders whose desktop value is scaled when applied (see settings.js).
const SCALE = {
  rotation_slider: 100, distortion_slider: 100, depth_slider: 100, pulse_strength_slider: 100, pulse_attack_slider: 100,
  pulse_decay_slider: 100, sensitivity_slider: 100, smoothing_slider: 100, bass_slider: 100, mids_slider: 100,
  highs_slider: 100, waveform_rotation_slider: 1000, waveform_amplitude_slider: 100, waveform_reflection_slider: 100,
  wireframe_rotation_slider: 100, wireframe_glow_slider: 100, wireframe_echo_opacity_slider: 100,
  effects_intensity_slider: 100, effects_beat_threshold_slider: 100, effects_random_slider: 1000,
  effects_bass_slider: 100, effects_mids_slider: 100, effects_highs_slider: 100, effects_volume_slider: 100,
};
const fmt = (name, v) => (SCALE[name] ? String(+(v / SCALE[name]).toFixed(3)) : String(v));

function controlHtml(c, value) {
  const id = `c-${c.name}`;
  const label = esc((c.label || c.text || c.name) + (c.name.endsWith('_weight_slider') ? ' weight' : ''));
  if (c.kind === 'slider' || c.kind === 'spin') {
    return `<div class="ctl"><label for="${id}">${label} <b id="${id}-v">${fmt(c.name, value)}</b></label>
      <input type="range" id="${id}" data-name="${c.name}" min="${c.min}" max="${c.max}" step="1" value="${value}"></div>`;
  }
  if (c.kind === 'combo') {
    return `<div class="ctl"><label for="${id}">${label}</label><select id="${id}" data-name="${c.name}">
      ${c.items.map(it => `<option${it === value ? ' selected' : ''}>${esc(it)}</option>`).join('')}</select></div>`;
  }
  if (c.kind === 'check') {
    return `<div class="ctl chk"><label for="${id}"><input type="checkbox" id="${id}" data-name="${c.name}"${value ? ' checked' : ''}> ${label}</label></div>`;
  }
  if (c.kind === 'color') {
    return `<div class="ctl colr"><label for="${id}">${label}</label><input type="color" id="${id}" data-name="${c.name}" value="${value.toLowerCase()}"></div>`;
  }
  return '';
}

// Group controls by tab and group, keeping the desktop order.
function structure(defaults) {
  const tabs = new Map();
  for (const c of defaults.controls) {
    if (HIDDEN.has(c.name)) continue;
    if (!tabs.has(c.tab)) tabs.set(c.tab, new Map());
    const groups = tabs.get(c.tab);
    if (!groups.has(c.group)) groups.set(c.group, []);
    groups.get(c.group).push(c);
  }
  return tabs;
}

export function buildPanel(host, defaults, values, onChange) {
  const tabs = structure(defaults);
  const names = [...tabs.keys()];
  host.innerHTML = `<div class="seg tabs" role="tablist">${names.map((t, i) =>
    `<button role="tab" aria-selected="${i === 0}" class="${i === 0 ? 'on' : ''}" data-tab="${i}">${esc(t)}</button>`).join('')}</div>
    ${names.map((t, i) => `<div class="tabpane" data-pane="${i}"${i ? ' hidden' : ''}>${tabHtml(t, tabs.get(t), values)}</div>`).join('')}`;
  host.querySelectorAll('[data-tab]').forEach(b => b.addEventListener('click', () => {
    host.querySelectorAll('[data-tab]').forEach(x => { x.classList.toggle('on', x === b); x.setAttribute('aria-selected', x === b); });
    host.querySelectorAll('[data-pane]').forEach(p => { p.hidden = p.dataset.pane !== b.dataset.tab; });
  }));
  host.querySelectorAll('[data-name]').forEach(el => {
    const name = el.dataset.name;
    const ev = el.type === 'range' ? 'input' : 'change';
    el.addEventListener(ev, () => {
      const v = el.type === 'checkbox' ? el.checked : el.type === 'range' ? +el.value
        : el.type === 'color' ? el.value.toUpperCase() : el.value;
      const out = host.querySelector(`#c-${name}-v`);
      if (out) out.textContent = fmt(name, v);
      onChange(name, v);
    });
  });
}

function tabHtml(tab, groups, values) {
  if (UNPORTED_TABS.has(tab)) {
    return `<p class="small mute">The experimental effects (dimensional portal, liquid metal, audio mycelia, gravitational
      lens; all off by default) are only in the desktop app.</p>`;
  }
  return `<div class="groups-grid">${[...groups].map(([g, cs]) => UNPORTED_GROUPS.has(g)
    ? `<fieldset class="grp"><legend>${esc(g)}</legend><p class="small mute">Desktop only (off by default).</p></fieldset>`
    : `<fieldset class="grp"><legend>${esc(g)}</legend>${cs.map(c => controlHtml(c, values[c.name])).join('')}</fieldset>`).join('')}</div>`;
}

// Put the values back into the controls (after "reset to defaults").
export function setPanelValues(host, values) {
  host.querySelectorAll('[data-name]').forEach(el => {
    const v = values[el.dataset.name];
    if (el.type === 'checkbox') el.checked = v;
    else if (el.type === 'color') el.value = String(v).toLowerCase();
    else el.value = v;
    const out = host.querySelector(`#c-${el.dataset.name}-v`);
    if (out) out.textContent = fmt(el.dataset.name, v);
  });
}
