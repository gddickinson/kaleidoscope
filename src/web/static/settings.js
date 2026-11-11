// Port of ControlPanel.apply_to_engine (src/ui/control_panel.py): desktop control values -> engine and audio settings.
// `v` maps the desktop widget names (segments_slider, symmetry_combo, ...) to slider numbers, combo texts, check-box
// booleans and '#RRGGBB' colours; the defaults come from /api/defaults (read from the real ControlPanel).
// The experimental effects and the particle tunnel are not ported, so their controls are not applied.
import { named } from './colors.js';

export function defaultValues(defaults) {
  return Object.fromEntries(defaults.controls.map(c => [c.name, c.value]));
}

export function applyToEngine(engine, audio, v) {
  applyGeneral(engine, audio, v);
  applyWireframe(engine, v);
  applyWaveform(engine, v);
  applyEffects(engine, v);
}

function applyGeneral(e, audio, v) {
  e.set_segments(v.segments_slider);
  e.set_rotation_speed(v.rotation_slider / 100);
  e.set_symmetry_mode(v.symmetry_combo.toLowerCase());
  e.set_color_mode(v.color_mode_combo.toLowerCase());
  e.set_base_color(named(v.base_color_btn));
  e.set_secondary_color(named(v.secondary_color_btn));
  e.set_shape_type(v.shape_combo.toLowerCase());
  e.set_blur_amount(v.blur_slider);
  e.set_distortion(v.distortion_slider / 100);
  e.set_particle_settings(v.particles_slider, v.size_slider, v.trail_slider);
  e.set_3d_enabled(v.enable_3d_check);
  e.set_depth_influence(v.depth_slider / 100);
  e.set_perspective(v.perspective_slider);
  e.set_pulse_enabled(v.enable_pulse_check);
  e.set_pulse_parameters(v.pulse_strength_slider / 100, 1.0, v.pulse_attack_slider / 100, v.pulse_decay_slider / 100);
  audio.set_sensitivity(v.sensitivity_slider / 100);
  audio.set_smoothing(v.smoothing_slider / 100);
  e.set_audio_influence(v.bass_slider / 100, v.mids_slider / 100, v.highs_slider / 100);
}

function applyWireframe(e, v) {
  e.set_wireframe_enabled(v.enable_wireframe_check);
  e.set_wireframe_edges_visible(v.wireframe_edges_check);
  e.set_wireframe_shape(v.wireframe_shape_combo.toLowerCase().trim(), v.wireframe_morph_check);
  e.set_wireframe_size(v.wireframe_size_slider);
  e.set_wireframe_rotation(v.wireframe_rotation_slider / 100.0);
  e.set_wireframe_color_mode(v.wireframe_color_combo.toLowerCase().replaceAll(' ', '_'));
  e.set_wireframe_colors(named(v.wireframe_color_btn), named(v.wireframe_secondary_color_btn));
  e.set_wireframe_effects(v.wireframe_vertices_check, v.wireframe_vertex_slider, v.wireframe_glow_check, v.wireframe_glow_slider / 100.0);
  e.set_wireframe_multi_shape(v.wireframe_multi_check, v.wireframe_count_slider);
  e.set_wireframe_echo(v.wireframe_echo_check, v.wireframe_echo_count_slider, v.wireframe_echo_opacity_slider / 100.0, 0.2);
  e.set_wireframe_beat_response(v.wireframe_auto_morph_check, v.wireframe_beat_morph_check);
}

function applyWaveform(e, v) {
  e.set_waveform_enabled(v.enable_waveform_check);
  e.set_waveform_parameters(v.waveform_radius_slider, v.waveform_width_slider, v.waveform_rotation_slider / 1000.0,
    v.waveform_amplitude_slider / 100.0);
  e.set_waveform_colors(named(v.waveform_color_btn), named(v.waveform_secondary_color_btn), v.waveform_color_combo === 'Gradient');
  e.set_waveform_reflection(v.waveform_reflection_check, v.waveform_reflection_slider);
}

function applyEffects(e, v) {
  e.set_effects_enabled(v.enable_effects_check);
  e.set_effects_intensity(v.effects_intensity_slider / 100.0);
  e.set_effects_beat_response(v.effects_beat_check, v.effects_beat_threshold_slider / 100.0);
  e.set_effects_random_generation(v.effects_random_check, v.effects_random_slider / 1000.0);
  for (const t of ['spark', 'flare', 'firework', 'mist']) e.set_effect_type_enabled(t, v[`effect_${t}_check`]);
  e.set_effects_weights({ spark: v.effect_spark_weight_slider, flare: v.effect_flare_weight_slider,
    firework: v.effect_firework_weight_slider, mist: v.effect_mist_weight_slider });
  e.set_effects_audio_reactivity(v.effects_bass_slider / 100.0, v.effects_mids_slider / 100.0,
    v.effects_highs_slider / 100.0, v.effects_volume_slider / 100.0);
}

// Not shown in the web panel: fullscreen and monitor choice are the page's Fullscreen button; the tunnel and the
// experimental effects are not ported.
export const HIDDEN = new Set(['fullscreen_check', 'monitor_combo']);
export const UNPORTED_GROUPS = new Set(['Particle Tunnel']);
export const UNPORTED_TABS = new Set(['Experimental Effects']);
