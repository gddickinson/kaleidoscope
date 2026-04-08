"""
Main control panel widget for the kaleidoscope visualizer.

Composes control groups from mixin modules:
- visual_controls: General, Visual, Display, 3D, Pulse, Audio
- wireframe_controls: Wireframe basic, visual, advanced
- effect_controls: Waveform, Particle effects, Effect types, Reactivity, Tunnel
- experimental_controls: Dimensional, Liquid Metal, Mycelia, Gravitational Lens
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTabWidget)
from PyQt5.QtGui import QColor

from src.ui.visual_controls import VisualControlsMixin
from src.ui.wireframe_controls import WireframeControlsMixin
from src.ui.effect_controls import EffectControlsMixin
from src.ui.experimental_controls import ExperimentalControlsMixin


class ControlPanel(
    VisualControlsMixin,
    WireframeControlsMixin,
    EffectControlsMixin,
    ExperimentalControlsMixin,
    QWidget,
):
    """Control panel with UI settings for the visualization"""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()

        # --- Visual Controls tab ---
        visual_tab = QWidget()
        visual_layout = QVBoxLayout()
        visual_tab.setLayout(visual_layout)
        visual_layout.addWidget(self._create_general_controls())
        visual_layout.addWidget(self._create_visual_controls())
        visual_layout.addWidget(self._create_display_controls())
        visual_layout.addStretch(1)

        # --- Technical Controls tab ---
        technical_tab = QWidget()
        technical_layout = QVBoxLayout()
        technical_tab.setLayout(technical_layout)
        technical_layout.addWidget(self._create_3d_controls())
        technical_layout.addWidget(self._create_pulse_controls())
        technical_layout.addWidget(self._create_audio_controls())
        technical_layout.addStretch(1)

        # --- Visualizations tab ---
        vis_tab = QWidget()
        vis_layout = QVBoxLayout()
        vis_tab.setLayout(vis_layout)
        vis_layout.addWidget(self._create_waveform_controls())
        vis_layout.addStretch(1)

        # --- Wireframe tab ---
        wireframe_tab = QWidget()
        wireframe_layout = QVBoxLayout()
        wireframe_tab.setLayout(wireframe_layout)
        wireframe_layout.addWidget(self._create_wireframe_controls())
        wireframe_layout.addWidget(self._create_wireframe_visual_controls())
        wireframe_layout.addWidget(self._create_wireframe_advanced_controls())
        wireframe_layout.addStretch(1)

        # --- Particle Effects tab ---
        effects_tab = QWidget()
        effects_layout = QVBoxLayout()
        effects_tab.setLayout(effects_layout)
        effects_layout.addWidget(self._create_particle_effects_controls())
        effects_layout.addWidget(self._create_effect_types_controls())
        effects_layout.addWidget(self._create_tunnel_controls())
        effects_layout.addWidget(self._create_effects_reactivity_controls())
        effects_layout.addStretch(1)

        # --- Experimental Effects tab ---
        experimental_tab = QWidget()
        experimental_layout = QVBoxLayout()
        experimental_tab.setLayout(experimental_layout)
        experimental_layout.addWidget(self._create_dimensional_controls())
        experimental_layout.addWidget(self._create_liquid_metal_controls())
        experimental_layout.addWidget(self._create_mycelia_controls())
        experimental_layout.addWidget(self._create_gravitational_lens_controls())
        experimental_layout.addWidget(self._create_global_experimental_controls())
        experimental_layout.addStretch(1)

        # Add tabs
        self.tab_widget.addTab(visual_tab, "Visual Controls")
        self.tab_widget.addTab(technical_tab, "Technical Controls")
        self.tab_widget.addTab(vis_tab, "Visualizations")
        self.tab_widget.addTab(wireframe_tab, "Wireframe Shapes")
        self.tab_widget.addTab(effects_tab, "Particle Effects")
        self.tab_widget.addTab(experimental_tab, "Experimental Effects")

        main_layout.addWidget(self.tab_widget)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        main_layout.addWidget(reset_btn)

        self.setLayout(main_layout)

    def reset_to_defaults(self):
        """Reset all controls to default values"""
        # General controls
        self.segments_slider.setValue(8)
        self.rotation_slider.setValue(50)
        self.symmetry_combo.setCurrentIndex(0)

        # Visual controls
        self.color_mode_combo.setCurrentIndex(0)
        self.base_color_btn.setStyleSheet("background-color: #FF007F")
        self.secondary_color_btn.setStyleSheet("background-color: #007FFF")
        self.shape_combo.setCurrentIndex(0)
        self.blur_slider.setValue(0)
        self.distortion_slider.setValue(0)
        self.particles_slider.setValue(100)
        self.size_slider.setValue(10)
        self.trail_slider.setValue(5)

        # 3D controls
        self.enable_3d_check.setChecked(True)
        self.depth_slider.setValue(100)
        self.perspective_slider.setValue(800)

        # Pulse controls
        self.enable_pulse_check.setChecked(True)
        self.pulse_strength_slider.setValue(100)
        self.pulse_attack_slider.setValue(10)
        self.pulse_decay_slider.setValue(20)

        # Audio controls
        self.sensitivity_slider.setValue(100)
        self.smoothing_slider.setValue(30)
        self.bass_slider.setValue(100)
        self.mids_slider.setValue(100)
        self.highs_slider.setValue(100)

        # Display controls
        self.fps_spin.setValue(60)
        self.fullscreen_check.setChecked(False)
        self.monitor_combo.setCurrentIndex(0)
        self.freq_display_check.setChecked(True)
        self.freq_height_slider.setValue(150)

        # Wireframe controls
        if hasattr(self, 'enable_wireframe_check'):
            self.enable_wireframe_check.setChecked(True)
            if hasattr(self, 'wireframe_edges_check'):
                self.wireframe_edges_check.setChecked(True)
            self.wireframe_shape_combo.setCurrentIndex(0)
            self.wireframe_morph_check.setChecked(True)
            self.wireframe_size_slider.setValue(100)
            self.wireframe_rotation_slider.setValue(100)
            self.wireframe_color_combo.setCurrentIndex(0)
            self.wireframe_color_btn.setStyleSheet("background-color: #FFFFFF")
            self.wireframe_secondary_color_btn.setStyleSheet("background-color: #00C8FF")
            self.wireframe_vertices_check.setChecked(False)
            self.wireframe_vertex_slider.setValue(3)
            self.wireframe_glow_check.setChecked(False)
            self.wireframe_glow_slider.setValue(50)

        # Wireframe advanced controls
        if hasattr(self, 'wireframe_multi_check'):
            self.wireframe_multi_check.setChecked(False)
            self.wireframe_count_slider.setValue(3)
            self.wireframe_echo_check.setChecked(False)
            self.wireframe_echo_count_slider.setValue(3)
            self.wireframe_echo_opacity_slider.setValue(30)
            self.wireframe_auto_morph_check.setChecked(False)
            self.wireframe_beat_morph_check.setChecked(False)

        # Waveform controls
        if hasattr(self, 'enable_waveform_check'):
            self.enable_waveform_check.setChecked(True)
            self.waveform_radius_slider.setValue(80)
            self.waveform_width_slider.setValue(2)
            self.waveform_rotation_slider.setValue(10)
            self.waveform_amplitude_slider.setValue(100)
            self.waveform_color_combo.setCurrentIndex(0)
            self.waveform_color_btn.setStyleSheet("background-color: #FFFFFF")
            self.waveform_secondary_color_btn.setStyleSheet("background-color: #00C8FF")
            self.waveform_reflection_check.setChecked(True)
            self.waveform_reflection_slider.setValue(30)

        # Particle effects controls
        if hasattr(self, 'enable_effects_check'):
            self.enable_effects_check.setChecked(True)
            self.effects_intensity_slider.setValue(100)
            self.effects_beat_check.setChecked(True)
            self.effects_beat_threshold_slider.setValue(50)
            self.effects_random_check.setChecked(True)
            self.effects_random_slider.setValue(10)

        # Effect types
        if hasattr(self, 'effect_spark_check'):
            self.effect_spark_check.setChecked(True)
            self.effect_spark_weight_slider.setValue(40)
            self.effect_flare_check.setChecked(True)
            self.effect_flare_weight_slider.setValue(30)
            self.effect_firework_check.setChecked(True)
            self.effect_firework_weight_slider.setValue(15)
            self.effect_mist_check.setChecked(True)
            self.effect_mist_weight_slider.setValue(15)

        # Effects reactivity
        if hasattr(self, 'effects_bass_slider'):
            self.effects_bass_slider.setValue(100)
            self.effects_mids_slider.setValue(70)
            self.effects_highs_slider.setValue(50)
            self.effects_volume_slider.setValue(80)

        # Tunnel settings
        if hasattr(self, 'tunnel_enable_check'):
            self.tunnel_enable_check.setChecked(False)
            self.tunnel_auto_change_check.setChecked(True)
            self.tunnel_interval_slider.setValue(600)
            self.tunnel_direction_combo.setCurrentIndex(0)

        # Experimental effects
        if hasattr(self, 'experimental_opacity_slider'):
            self.experimental_opacity_slider.setValue(80)
            self.dimensional_enable_check.setChecked(False)
            self.dimensional_intensity_slider.setValue(80)
            self.dimensional_inner_color_btn.setStyleSheet("background-color: #140028")
            self.dimensional_outer_color_btn.setStyleSheet("background-color: #6400FF")
            self.dimensional_glow_color_btn.setStyleSheet("background-color: #B478FF")
            self.liquid_metal_enable_check.setChecked(False)
            self.liquid_metal_intensity_slider.setValue(80)
            self.liquid_metal_color_btn.setStyleSheet("background-color: #C8C8DC")
            self.liquid_highlight_color_btn.setStyleSheet("background-color: #FFFFFF")
            self.liquid_shadow_color_btn.setStyleSheet("background-color: #464664")
            self.mycelia_enable_check.setChecked(False)
            self.mycelia_intensity_slider.setValue(80)
            self.mycelia_growth_slider.setValue(150)
            self.mycelia_base_color_btn.setStyleSheet("background-color: #50DC78")
            self.mycelia_tip_color_btn.setStyleSheet("background-color: #DCFFC8")
            self.mycelia_bg_color_btn.setStyleSheet("background-color: #0A140A")
            self.mycelia_bg_opacity_slider.setValue(100)
            self.lens_enable_check.setChecked(False)
            self.lens_intensity_slider.setValue(80)
            self.lens_distortion_slider.setValue(100)
            self.lens_grid_color_btn.setStyleSheet("background-color: #323250")
            self.lens_center_color_btn.setStyleSheet("background-color: #6496FF")
            self.lens_edge_color_btn.setStyleSheet("background-color: #3264C8")
            self.lens_grid_check.setChecked(True)

    def apply_to_engine(self, engine, audio_processor):
        """Apply all settings to the engine and audio processor"""
        if not engine or not audio_processor:
            return

        self._apply_general_settings(engine, audio_processor)
        self._apply_wireframe_settings(engine)
        self._apply_waveform_settings(engine)
        self._apply_particle_effects_settings(engine)
        self._apply_experimental_settings(engine)

    def _apply_general_settings(self, engine, audio_processor):
        """Apply general, visual, 3D, pulse, and audio settings."""
        engine.set_segments(self.segments_slider.value())
        engine.set_rotation_speed(self.rotation_slider.value() / 100)
        engine.set_symmetry_mode(self.symmetry_combo.currentText().lower())

        engine.set_color_mode(self.color_mode_combo.currentText().lower())
        base_color = QColor()
        base_color.setNamedColor(self.base_color_btn.styleSheet().split(":")[1].strip())
        engine.set_base_color(base_color)
        secondary_color = QColor()
        secondary_color.setNamedColor(self.secondary_color_btn.styleSheet().split(":")[1].strip())
        engine.set_secondary_color(secondary_color)
        engine.set_shape_type(self.shape_combo.currentText().lower())
        engine.set_blur_amount(self.blur_slider.value())
        engine.set_distortion(self.distortion_slider.value() / 100)
        engine.set_particle_settings(
            self.particles_slider.value(),
            self.size_slider.value(),
            self.trail_slider.value()
        )

        engine.set_3d_enabled(self.enable_3d_check.isChecked())
        engine.set_depth_influence(self.depth_slider.value() / 100)
        engine.set_perspective(self.perspective_slider.value())

        engine.set_pulse_enabled(self.enable_pulse_check.isChecked())
        engine.set_pulse_parameters(
            self.pulse_strength_slider.value() / 100,
            1.0,
            self.pulse_attack_slider.value() / 100,
            self.pulse_decay_slider.value() / 100
        )

        audio_processor.set_sensitivity(self.sensitivity_slider.value() / 100)
        audio_processor.set_smoothing(self.smoothing_slider.value() / 100)
        engine.set_audio_influence(
            self.bass_slider.value() / 100,
            self.mids_slider.value() / 100,
            self.highs_slider.value() / 100
        )

    def _apply_wireframe_settings(self, engine):
        """Apply wireframe settings to the engine."""
        try:
            if not hasattr(self, 'enable_wireframe_check'):
                return

            engine.set_wireframe_enabled(self.enable_wireframe_check.isChecked())

            if hasattr(self, 'wireframe_edges_check'):
                engine.set_wireframe_edges_visible(self.wireframe_edges_check.isChecked())

            shape_type = self.wireframe_shape_combo.currentText().lower().strip()
            morph_enabled = self.wireframe_morph_check.isChecked()
            engine.set_wireframe_shape(shape_type, morph_enabled)

            engine.set_wireframe_size(self.wireframe_size_slider.value())
            engine.set_wireframe_rotation(self.wireframe_rotation_slider.value() / 100.0)

            color_mode = self.wireframe_color_combo.currentText().lower().replace(" ", "_")
            engine.set_wireframe_color_mode(color_mode)

            primary_color = QColor()
            primary_color.setNamedColor(self.wireframe_color_btn.styleSheet().split(":")[1].strip())
            secondary_color = QColor()
            secondary_color.setNamedColor(self.wireframe_secondary_color_btn.styleSheet().split(":")[1].strip())
            engine.set_wireframe_colors(primary_color, secondary_color)

            engine.set_wireframe_effects(
                self.wireframe_vertices_check.isChecked(),
                self.wireframe_vertex_slider.value(),
                self.wireframe_glow_check.isChecked(),
                self.wireframe_glow_slider.value() / 100.0
            )

            if hasattr(self, 'wireframe_multi_check'):
                engine.set_wireframe_multi_shape(
                    self.wireframe_multi_check.isChecked(),
                    self.wireframe_count_slider.value()
                )
                engine.set_wireframe_echo(
                    self.wireframe_echo_check.isChecked(),
                    self.wireframe_echo_count_slider.value(),
                    self.wireframe_echo_opacity_slider.value() / 100.0,
                    0.2
                )
                engine.set_wireframe_beat_response(
                    self.wireframe_auto_morph_check.isChecked(),
                    self.wireframe_beat_morph_check.isChecked()
                )
        except Exception as e:
            print(f"Error applying wireframe settings: {e}")

    def _apply_waveform_settings(self, engine):
        """Apply circular waveform settings to the engine."""
        try:
            if not hasattr(self, 'enable_waveform_check'):
                return

            engine.set_waveform_enabled(self.enable_waveform_check.isChecked())
            engine.set_waveform_parameters(
                self.waveform_radius_slider.value(),
                self.waveform_width_slider.value(),
                self.waveform_rotation_slider.value() / 1000.0,
                self.waveform_amplitude_slider.value() / 100.0
            )

            primary_color = QColor()
            primary_color.setNamedColor(self.waveform_color_btn.styleSheet().split(":")[1].strip())
            secondary_color = QColor()
            secondary_color.setNamedColor(self.waveform_secondary_color_btn.styleSheet().split(":")[1].strip())
            use_gradient = self.waveform_color_combo.currentText() == "Gradient"
            engine.set_waveform_colors(primary_color, secondary_color, use_gradient)

            engine.set_waveform_reflection(
                self.waveform_reflection_check.isChecked(),
                self.waveform_reflection_slider.value()
            )
        except Exception as e:
            print(f"Error applying waveform settings: {e}")

    def _apply_particle_effects_settings(self, engine):
        """Apply particle effects settings to the engine."""
        try:
            if not hasattr(self, 'enable_effects_check'):
                return

            engine.set_effects_enabled(self.enable_effects_check.isChecked())
            engine.set_effects_intensity(self.effects_intensity_slider.value() / 100.0)
            engine.set_effects_beat_response(
                self.effects_beat_check.isChecked(),
                self.effects_beat_threshold_slider.value() / 100.0
            )
            engine.set_effects_random_generation(
                self.effects_random_check.isChecked(),
                self.effects_random_slider.value() / 1000.0
            )

            if hasattr(self, 'effect_spark_check'):
                engine.set_effect_type_enabled("spark", self.effect_spark_check.isChecked())
                engine.set_effect_type_enabled("flare", self.effect_flare_check.isChecked())
                engine.set_effect_type_enabled("firework", self.effect_firework_check.isChecked())
                engine.set_effect_type_enabled("mist", self.effect_mist_check.isChecked())
                weights = {
                    "spark": self.effect_spark_weight_slider.value(),
                    "flare": self.effect_flare_weight_slider.value(),
                    "firework": self.effect_firework_weight_slider.value(),
                    "mist": self.effect_mist_weight_slider.value()
                }
                engine.set_effects_weights(weights)

            if hasattr(self, 'effects_bass_slider'):
                engine.set_effects_audio_reactivity(
                    self.effects_bass_slider.value() / 100.0,
                    self.effects_mids_slider.value() / 100.0,
                    self.effects_highs_slider.value() / 100.0,
                    self.effects_volume_slider.value() / 100.0
                )

            if hasattr(self, 'tunnel_enable_check'):
                engine.set_tunnel_enabled(self.tunnel_enable_check.isChecked())
                engine.set_tunnel_auto_change(
                    self.tunnel_auto_change_check.isChecked(),
                    self.tunnel_interval_slider.value()
                )
                engine.set_tunnel_direction(self.tunnel_direction_combo.currentText().lower())

        except Exception as e:
            print(f"Error applying particle effects settings: {e}")
            import traceback
            traceback.print_exc()

    def _apply_experimental_settings(self, engine):
        """Apply experimental effects settings to the engine."""
        try:
            if not (hasattr(self, 'dimensional_enable_check') and hasattr(engine, 'experimental_effects')):
                return

            exp = engine.experimental_effects

            # Dimensional Portal
            exp.set_effect_enabled('dimensional_portal', self.dimensional_enable_check.isChecked())
            exp.set_effect_intensity('dimensional_portal', self.dimensional_intensity_slider.value() / 100.0)

            # Liquid Metal
            exp.set_effect_enabled('liquid_metal', self.liquid_metal_enable_check.isChecked())
            exp.set_effect_intensity('liquid_metal', self.liquid_metal_intensity_slider.value() / 100.0)

            # Audio Mycelia
            exp.set_effect_enabled('audio_mycelia', self.mycelia_enable_check.isChecked())
            exp.set_effect_intensity('audio_mycelia', self.mycelia_intensity_slider.value() / 100.0)

            if hasattr(exp.effects['audio_mycelia'], 'set_growth_rate'):
                exp.effects['audio_mycelia'].set_growth_rate(self.mycelia_growth_slider.value() / 100.0)

            # Gravitational Lens
            exp.set_effect_enabled('gravitational_lens', self.lens_enable_check.isChecked())
            exp.set_effect_intensity('gravitational_lens', self.lens_intensity_slider.value() / 100.0)

            if hasattr(exp.effects['gravitational_lens'], 'set_distortion_strength'):
                exp.effects['gravitational_lens'].set_distortion_strength(self.lens_distortion_slider.value() / 100.0)

            if hasattr(exp.effects['gravitational_lens'], 'set_grid_visible'):
                exp.effects['gravitational_lens'].set_grid_visible(self.lens_grid_check.isChecked())

            # Global opacity
            if hasattr(self, 'experimental_opacity_slider'):
                exp.set_global_opacity(self.experimental_opacity_slider.value() / 100.0)

            # Dimensional Portal colors
            if hasattr(self, 'dimensional_inner_color_btn'):
                self._apply_dimensional_colors(exp)

            # Liquid Metal colors
            if hasattr(self, 'liquid_metal_color_btn'):
                self._apply_liquid_metal_colors(exp)

            # Audio Mycelia colors
            if hasattr(self, 'mycelia_base_color_btn'):
                self._apply_mycelia_colors(exp)

            # Gravitational Lens colors
            if hasattr(self, 'lens_grid_color_btn'):
                self._apply_lens_colors(exp)

        except Exception as e:
            print(f"Error applying experimental effects settings: {e}")
            import traceback
            traceback.print_exc()

    def _apply_dimensional_colors(self, exp):
        """Apply dimensional portal color settings."""
        inner_color = QColor()
        inner_color.setNamedColor(self.dimensional_inner_color_btn.styleSheet().split(":")[1].strip())
        exp.effects['dimensional_portal'].set_inner_color(inner_color)

        outer_color = QColor()
        outer_color.setNamedColor(self.dimensional_outer_color_btn.styleSheet().split(":")[1].strip())
        exp.effects['dimensional_portal'].set_outer_color(outer_color)

        glow_color = QColor()
        glow_color.setNamedColor(self.dimensional_glow_color_btn.styleSheet().split(":")[1].strip())
        exp.effects['dimensional_portal'].set_glow_color(glow_color)

        if hasattr(self, 'dimensional_reactive_inner_check') and \
           hasattr(exp.effects['dimensional_portal'], 'enable_color_reactivity'):
            exp.effects['dimensional_portal'].enable_color_reactivity(
                enable_inner=self.dimensional_reactive_inner_check.isChecked(),
                enable_outer=self.dimensional_reactive_outer_check.isChecked(),
                enable_glow=self.dimensional_reactive_glow_check.isChecked()
            )

    def _apply_liquid_metal_colors(self, exp):
        """Apply liquid metal color settings."""
        metal_color = QColor()
        metal_color.setNamedColor(self.liquid_metal_color_btn.styleSheet().split(":")[1].strip())
        exp.effects['liquid_metal'].set_metal_color(metal_color)

        highlight_color = QColor()
        highlight_color.setNamedColor(self.liquid_highlight_color_btn.styleSheet().split(":")[1].strip())
        exp.effects['liquid_metal'].set_highlight_color(highlight_color)

        shadow_color = QColor()
        shadow_color.setNamedColor(self.liquid_shadow_color_btn.styleSheet().split(":")[1].strip())
        exp.effects['liquid_metal'].set_shadow_color(shadow_color)

    def _apply_mycelia_colors(self, exp):
        """Apply audio mycelia color settings."""
        base_color = QColor()
        base_color.setNamedColor(self.mycelia_base_color_btn.styleSheet().split(":")[1].strip())
        exp.effects['audio_mycelia'].set_base_color(base_color)

        tip_color = QColor()
        tip_color.setNamedColor(self.mycelia_tip_color_btn.styleSheet().split(":")[1].strip())
        exp.effects['audio_mycelia'].set_tip_color(tip_color)

        bg_color = QColor()
        bg_color.setNamedColor(self.mycelia_bg_color_btn.styleSheet().split(":")[1].strip())
        alpha = self.mycelia_bg_opacity_slider.value()
        exp.effects['audio_mycelia'].set_bg_color(bg_color, alpha)

        if hasattr(exp.effects['audio_mycelia'], 'set_growth_rate'):
            exp.effects['audio_mycelia'].set_growth_rate(self.mycelia_growth_slider.value() / 100.0)

    def _apply_lens_colors(self, exp):
        """Apply gravitational lens color settings."""
        grid_color = QColor()
        grid_color.setNamedColor(self.lens_grid_color_btn.styleSheet().split(":")[1].strip())
        exp.effects['gravitational_lens'].set_grid_color(grid_color, 100)

        lens_color = QColor()
        lens_color.setNamedColor(self.lens_center_color_btn.styleSheet().split(":")[1].strip())
        exp.effects['gravitational_lens'].set_lens_color(lens_color)

        edge_color = QColor()
        edge_color.setNamedColor(self.lens_edge_color_btn.styleSheet().split(":")[1].strip())
        exp.effects['gravitational_lens'].set_edge_color(edge_color)

        if hasattr(exp.effects['gravitational_lens'], 'set_distortion_strength'):
            exp.effects['gravitational_lens'].set_distortion_strength(
                self.lens_distortion_slider.value() / 100.0
            )

        if hasattr(exp.effects['gravitational_lens'], 'set_grid_visible'):
            exp.effects['gravitational_lens'].set_grid_visible(self.lens_grid_check.isChecked())
