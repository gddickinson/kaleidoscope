"""
Particle effect and waveform control mixins for the kaleidoscope control panel.

Contains controls for: Circular Waveform, Particle Effects, Effect Types,
Effects Reactivity, and Particle Tunnel.
"""

from PyQt5.QtWidgets import (QLabel, QSlider, QComboBox, QPushButton,
                            QCheckBox, QColorDialog, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class EffectControlsMixin:
    """Mixin providing particle effect and waveform control creation methods."""

    def _create_waveform_controls(self):
        """Create controls for circular waveform visualization"""
        group = QGroupBox("Circular Waveform")
        layout = QGridLayout()

        layout.addWidget(QLabel("Show Waveform:"), 0, 0)
        self.enable_waveform_check = QCheckBox()
        self.enable_waveform_check.setChecked(True)
        layout.addWidget(self.enable_waveform_check, 0, 1)

        layout.addWidget(QLabel("Inner Radius:"), 1, 0)
        self.waveform_radius_slider = QSlider(Qt.Horizontal)
        self.waveform_radius_slider.setRange(50, 95)
        self.waveform_radius_slider.setValue(80)
        layout.addWidget(self.waveform_radius_slider, 1, 1)
        self.waveform_radius_value = QLabel("80%")
        layout.addWidget(self.waveform_radius_value, 1, 2)
        self.waveform_radius_slider.valueChanged.connect(
            lambda v: self.waveform_radius_value.setText(f"{v}%"))

        layout.addWidget(QLabel("Line Width:"), 2, 0)
        self.waveform_width_slider = QSlider(Qt.Horizontal)
        self.waveform_width_slider.setRange(1, 10)
        self.waveform_width_slider.setValue(2)
        layout.addWidget(self.waveform_width_slider, 2, 1)
        self.waveform_width_value = QLabel("2")
        layout.addWidget(self.waveform_width_value, 2, 2)
        self.waveform_width_slider.valueChanged.connect(
            lambda v: self.waveform_width_value.setText(str(v)))

        layout.addWidget(QLabel("Rotation:"), 3, 0)
        self.waveform_rotation_slider = QSlider(Qt.Horizontal)
        self.waveform_rotation_slider.setRange(0, 50)
        self.waveform_rotation_slider.setValue(10)
        layout.addWidget(self.waveform_rotation_slider, 3, 1)
        self.waveform_rotation_value = QLabel("0.01")
        layout.addWidget(self.waveform_rotation_value, 3, 2)
        self.waveform_rotation_slider.valueChanged.connect(
            lambda v: self.waveform_rotation_value.setText(f"{v/1000:.3f}"))

        layout.addWidget(QLabel("Amplitude:"), 4, 0)
        self.waveform_amplitude_slider = QSlider(Qt.Horizontal)
        self.waveform_amplitude_slider.setRange(50, 300)
        self.waveform_amplitude_slider.setValue(100)
        layout.addWidget(self.waveform_amplitude_slider, 4, 1)
        self.waveform_amplitude_value = QLabel("1.0")
        layout.addWidget(self.waveform_amplitude_value, 4, 2)
        self.waveform_amplitude_slider.valueChanged.connect(
            lambda v: self.waveform_amplitude_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Color Mode:"), 5, 0)
        self.waveform_color_combo = QComboBox()
        self.waveform_color_combo.addItems(["Gradient", "Solid"])
        layout.addWidget(self.waveform_color_combo, 5, 1, 1, 2)

        layout.addWidget(QLabel("Primary Color:"), 6, 0)
        self.waveform_color_btn = QPushButton()
        self.waveform_color_btn.setStyleSheet("background-color: #FFFFFF")
        self.waveform_color_btn.clicked.connect(self._select_waveform_color)
        layout.addWidget(self.waveform_color_btn, 6, 1, 1, 2)

        layout.addWidget(QLabel("Secondary Color:"), 7, 0)
        self.waveform_secondary_color_btn = QPushButton()
        self.waveform_secondary_color_btn.setStyleSheet("background-color: #00C8FF")
        self.waveform_secondary_color_btn.clicked.connect(self._select_waveform_secondary_color)
        layout.addWidget(self.waveform_secondary_color_btn, 7, 1, 1, 2)

        layout.addWidget(QLabel("Show Reflection:"), 8, 0)
        self.waveform_reflection_check = QCheckBox()
        self.waveform_reflection_check.setChecked(True)
        layout.addWidget(self.waveform_reflection_check, 8, 1)

        layout.addWidget(QLabel("Refl. Opacity:"), 9, 0)
        self.waveform_reflection_slider = QSlider(Qt.Horizontal)
        self.waveform_reflection_slider.setRange(10, 100)
        self.waveform_reflection_slider.setValue(30)
        layout.addWidget(self.waveform_reflection_slider, 9, 1)
        self.waveform_reflection_value = QLabel("30%")
        layout.addWidget(self.waveform_reflection_value, 9, 2)
        self.waveform_reflection_slider.valueChanged.connect(
            lambda v: self.waveform_reflection_value.setText(f"{v}%"))

        group.setLayout(layout)
        return group

    def _select_waveform_color(self):
        """Open color dialog for waveform primary color selection"""
        color = QColorDialog.getColor(QColor(255, 255, 255), self, "Select Waveform Color")
        if color.isValid():
            self.waveform_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_waveform_secondary_color(self):
        """Open color dialog for waveform secondary color selection"""
        color = QColorDialog.getColor(QColor(0, 200, 255), self, "Select Waveform Secondary Color")
        if color.isValid():
            self.waveform_secondary_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _create_particle_effects_controls(self):
        """Create controls for particle effects"""
        group = QGroupBox("Particle Effects")
        layout = QGridLayout()

        layout.addWidget(QLabel("Enable Effects:"), 0, 0)
        self.enable_effects_check = QCheckBox()
        self.enable_effects_check.setChecked(True)
        layout.addWidget(self.enable_effects_check, 0, 1)

        layout.addWidget(QLabel("Intensity:"), 1, 0)
        self.effects_intensity_slider = QSlider(Qt.Horizontal)
        self.effects_intensity_slider.setRange(10, 200)
        self.effects_intensity_slider.setValue(100)
        layout.addWidget(self.effects_intensity_slider, 1, 1)
        self.effects_intensity_value = QLabel("1.0")
        layout.addWidget(self.effects_intensity_value, 1, 2)
        self.effects_intensity_slider.valueChanged.connect(
            lambda v: self.effects_intensity_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("On Beat:"), 2, 0)
        self.effects_beat_check = QCheckBox()
        self.effects_beat_check.setChecked(True)
        layout.addWidget(self.effects_beat_check, 2, 1)

        layout.addWidget(QLabel("Beat Sensitivity:"), 3, 0)
        self.effects_beat_threshold_slider = QSlider(Qt.Horizontal)
        self.effects_beat_threshold_slider.setRange(10, 90)
        self.effects_beat_threshold_slider.setValue(50)
        layout.addWidget(self.effects_beat_threshold_slider, 3, 1)
        self.effects_beat_threshold_value = QLabel("0.5")
        layout.addWidget(self.effects_beat_threshold_value, 3, 2)
        self.effects_beat_threshold_slider.valueChanged.connect(
            lambda v: self.effects_beat_threshold_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Random Effects:"), 4, 0)
        self.effects_random_check = QCheckBox()
        self.effects_random_check.setChecked(True)
        layout.addWidget(self.effects_random_check, 4, 1)

        layout.addWidget(QLabel("Random Rate:"), 5, 0)
        self.effects_random_slider = QSlider(Qt.Horizontal)
        self.effects_random_slider.setRange(1, 20)
        self.effects_random_slider.setValue(10)
        layout.addWidget(self.effects_random_slider, 5, 1)
        self.effects_random_value = QLabel("0.01")
        layout.addWidget(self.effects_random_value, 5, 2)
        self.effects_random_slider.valueChanged.connect(
            lambda v: self.effects_random_value.setText(f"{v/1000:.3f}"))

        group.setLayout(layout)
        return group

    def _create_effect_types_controls(self):
        """Create controls for enabling/disabling specific effect types"""
        group = QGroupBox("Effect Types")
        layout = QGridLayout()

        # Sparks
        layout.addWidget(QLabel("Sparks:"), 0, 0)
        self.effect_spark_check = QCheckBox()
        self.effect_spark_check.setChecked(True)
        layout.addWidget(self.effect_spark_check, 0, 1)
        self.effect_spark_weight_slider = QSlider(Qt.Horizontal)
        self.effect_spark_weight_slider.setRange(0, 100)
        self.effect_spark_weight_slider.setValue(40)
        layout.addWidget(self.effect_spark_weight_slider, 0, 2)
        self.effect_spark_weight_value = QLabel("40")
        layout.addWidget(self.effect_spark_weight_value, 0, 3)
        self.effect_spark_weight_slider.valueChanged.connect(
            lambda v: self.effect_spark_weight_value.setText(str(v)))

        # Flares
        layout.addWidget(QLabel("Flares:"), 1, 0)
        self.effect_flare_check = QCheckBox()
        self.effect_flare_check.setChecked(True)
        layout.addWidget(self.effect_flare_check, 1, 1)
        self.effect_flare_weight_slider = QSlider(Qt.Horizontal)
        self.effect_flare_weight_slider.setRange(0, 100)
        self.effect_flare_weight_slider.setValue(30)
        layout.addWidget(self.effect_flare_weight_slider, 1, 2)
        self.effect_flare_weight_value = QLabel("30")
        layout.addWidget(self.effect_flare_weight_value, 1, 3)
        self.effect_flare_weight_slider.valueChanged.connect(
            lambda v: self.effect_flare_weight_value.setText(str(v)))

        # Fireworks
        layout.addWidget(QLabel("Fireworks:"), 2, 0)
        self.effect_firework_check = QCheckBox()
        self.effect_firework_check.setChecked(True)
        layout.addWidget(self.effect_firework_check, 2, 1)
        self.effect_firework_weight_slider = QSlider(Qt.Horizontal)
        self.effect_firework_weight_slider.setRange(0, 100)
        self.effect_firework_weight_slider.setValue(15)
        layout.addWidget(self.effect_firework_weight_slider, 2, 2)
        self.effect_firework_weight_value = QLabel("15")
        layout.addWidget(self.effect_firework_weight_value, 2, 3)
        self.effect_firework_weight_slider.valueChanged.connect(
            lambda v: self.effect_firework_weight_value.setText(str(v)))

        # Mist
        layout.addWidget(QLabel("Mist:"), 3, 0)
        self.effect_mist_check = QCheckBox()
        self.effect_mist_check.setChecked(True)
        layout.addWidget(self.effect_mist_check, 3, 1)
        self.effect_mist_weight_slider = QSlider(Qt.Horizontal)
        self.effect_mist_weight_slider.setRange(0, 100)
        self.effect_mist_weight_slider.setValue(15)
        layout.addWidget(self.effect_mist_weight_slider, 3, 2)
        self.effect_mist_weight_value = QLabel("15")
        layout.addWidget(self.effect_mist_weight_value, 3, 3)
        self.effect_mist_weight_slider.valueChanged.connect(
            lambda v: self.effect_mist_weight_value.setText(str(v)))

        group.setLayout(layout)
        return group

    def _create_effects_reactivity_controls(self):
        """Create controls for effect audio reactivity"""
        group = QGroupBox("Effects Reactivity")
        layout = QGridLayout()

        layout.addWidget(QLabel("Bass:"), 0, 0)
        self.effects_bass_slider = QSlider(Qt.Horizontal)
        self.effects_bass_slider.setRange(0, 200)
        self.effects_bass_slider.setValue(100)
        layout.addWidget(self.effects_bass_slider, 0, 1)
        self.effects_bass_value = QLabel("1.0")
        layout.addWidget(self.effects_bass_value, 0, 2)
        self.effects_bass_slider.valueChanged.connect(
            lambda v: self.effects_bass_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Mids:"), 1, 0)
        self.effects_mids_slider = QSlider(Qt.Horizontal)
        self.effects_mids_slider.setRange(0, 200)
        self.effects_mids_slider.setValue(70)
        layout.addWidget(self.effects_mids_slider, 1, 1)
        self.effects_mids_value = QLabel("0.7")
        layout.addWidget(self.effects_mids_value, 1, 2)
        self.effects_mids_slider.valueChanged.connect(
            lambda v: self.effects_mids_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Highs:"), 2, 0)
        self.effects_highs_slider = QSlider(Qt.Horizontal)
        self.effects_highs_slider.setRange(0, 200)
        self.effects_highs_slider.setValue(50)
        layout.addWidget(self.effects_highs_slider, 2, 1)
        self.effects_highs_value = QLabel("0.5")
        layout.addWidget(self.effects_highs_value, 2, 2)
        self.effects_highs_slider.valueChanged.connect(
            lambda v: self.effects_highs_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Volume:"), 3, 0)
        self.effects_volume_slider = QSlider(Qt.Horizontal)
        self.effects_volume_slider.setRange(0, 200)
        self.effects_volume_slider.setValue(80)
        layout.addWidget(self.effects_volume_slider, 3, 1)
        self.effects_volume_value = QLabel("0.8")
        layout.addWidget(self.effects_volume_value, 3, 2)
        self.effects_volume_slider.valueChanged.connect(
            lambda v: self.effects_volume_value.setText(f"{v/100:.1f}"))

        group.setLayout(layout)
        return group

    def _create_tunnel_controls(self):
        """Create controls for particle tunnel effect"""
        group = QGroupBox("Particle Tunnel")
        layout = QGridLayout()

        layout.addWidget(QLabel("Enable Tunnel:"), 0, 0)
        self.tunnel_enable_check = QCheckBox()
        self.tunnel_enable_check.setChecked(False)
        layout.addWidget(self.tunnel_enable_check, 0, 1)

        layout.addWidget(QLabel("Auto-change:"), 1, 0)
        self.tunnel_auto_change_check = QCheckBox()
        self.tunnel_auto_change_check.setChecked(True)
        layout.addWidget(self.tunnel_auto_change_check, 1, 1)

        layout.addWidget(QLabel("Change Interval:"), 2, 0)
        self.tunnel_interval_slider = QSlider(Qt.Horizontal)
        self.tunnel_interval_slider.setRange(300, 1200)
        self.tunnel_interval_slider.setValue(600)
        layout.addWidget(self.tunnel_interval_slider, 2, 1)
        self.tunnel_interval_value = QLabel("10s")
        layout.addWidget(self.tunnel_interval_value, 2, 2)
        self.tunnel_interval_slider.valueChanged.connect(
            lambda v: self.tunnel_interval_value.setText(f"{v/60:.1f}s"))

        layout.addWidget(QLabel("Flow Direction:"), 3, 0)
        self.tunnel_direction_combo = QComboBox()
        self.tunnel_direction_combo.addItems(["Auto", "Inward", "Outward"])
        layout.addWidget(self.tunnel_direction_combo, 3, 1, 1, 2)

        group.setLayout(layout)
        return group
