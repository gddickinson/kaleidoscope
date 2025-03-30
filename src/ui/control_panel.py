from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
                            QComboBox, QPushButton, QCheckBox, QSpinBox,
                            QColorDialog, QGroupBox, QGridLayout, QApplication, QTabWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

# =============================================================================
# UI Module: Control Panel
# =============================================================================

class ControlPanel(QWidget):
    """Control panel with UI settings for the visualization"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create main layout
        main_layout = QVBoxLayout()

        # Create tab widget for control groups
        self.tab_widget = QTabWidget()

        # Create tabs for different control categories
        visual_tab = QWidget()
        visual_layout = QVBoxLayout()
        visual_tab.setLayout(visual_layout)

        technical_tab = QWidget()
        technical_layout = QVBoxLayout()
        technical_tab.setLayout(technical_layout)

        # Tab for additional visualizations
        effects_tab = QWidget()
        effects_layout = QVBoxLayout()
        effects_tab.setLayout(effects_layout)

        # Add control groups to Visual tab
        visual_layout.addWidget(self._create_general_controls())
        visual_layout.addWidget(self._create_visual_controls())
        visual_layout.addWidget(self._create_display_controls())
        visual_layout.addStretch(1)

        # Add control groups to Technical tab
        technical_layout.addWidget(self._create_3d_controls())
        technical_layout.addWidget(self._create_pulse_controls())
        technical_layout.addWidget(self._create_audio_controls())
        technical_layout.addStretch(1)

        # Add control groups to Effects tab
        effects_layout.addWidget(self._create_wireframe_controls())
        effects_layout.addWidget(self._create_waveform_controls())  # Add circular waveform controls
        effects_layout.addStretch(1)

        # Add tabs to tab widget
        self.tab_widget.addTab(visual_tab, "Visual Controls")
        self.tab_widget.addTab(technical_tab, "Technical Controls")
        self.tab_widget.addTab(effects_tab, "Effect Visualizations")

        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)

        # Add reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        main_layout.addWidget(reset_btn)

        self.setLayout(main_layout)

    def _create_general_controls(self):
        """Create general visualization controls"""
        group = QGroupBox("General Controls")
        layout = QGridLayout()

        # Segments control
        layout.addWidget(QLabel("Segments:"), 0, 0)
        self.segments_slider = QSlider(Qt.Horizontal)
        self.segments_slider.setRange(3, 24)
        self.segments_slider.setValue(8)
        layout.addWidget(self.segments_slider, 0, 1)
        self.segments_value = QLabel("8")
        layout.addWidget(self.segments_value, 0, 2)
        self.segments_slider.valueChanged.connect(
            lambda v: self.segments_value.setText(str(v)))

        # Rotation speed
        layout.addWidget(QLabel("Rotation:"), 1, 0)
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setRange(0, 100)
        self.rotation_slider.setValue(50)
        layout.addWidget(self.rotation_slider, 1, 1)
        self.rotation_value = QLabel("0.5")
        layout.addWidget(self.rotation_value, 1, 2)
        self.rotation_slider.valueChanged.connect(
            lambda v: self.rotation_value.setText(str(v/100)))

        # Symmetry mode
        layout.addWidget(QLabel("Symmetry:"), 2, 0)
        self.symmetry_combo = QComboBox()
        self.symmetry_combo.addItems(["Radial", "Mirror", "Spiral"])
        layout.addWidget(self.symmetry_combo, 2, 1, 1, 2)

        group.setLayout(layout)
        return group

    def _create_visual_controls(self):
        """Create visual effect controls"""
        group = QGroupBox("Visual Effects")
        layout = QGridLayout()

        # Color mode
        layout.addWidget(QLabel("Color Mode:"), 0, 0)
        self.color_mode_combo = QComboBox()
        self.color_mode_combo.addItems(["Spectrum", "Solid", "Gradient"])
        layout.addWidget(self.color_mode_combo, 0, 1, 1, 2)

        # Base color
        layout.addWidget(QLabel("Base Color:"), 1, 0)
        self.base_color_btn = QPushButton()
        self.base_color_btn.setStyleSheet("background-color: #FF007F")
        self.base_color_btn.clicked.connect(self._select_base_color)
        layout.addWidget(self.base_color_btn, 1, 1, 1, 2)

        # Secondary color
        layout.addWidget(QLabel("Secondary:"), 2, 0)
        self.secondary_color_btn = QPushButton()
        self.secondary_color_btn.setStyleSheet("background-color: #007FFF")
        self.secondary_color_btn.clicked.connect(self._select_secondary_color)
        layout.addWidget(self.secondary_color_btn, 2, 1, 1, 2)

        # Particle shape
        layout.addWidget(QLabel("Shape:"), 3, 0)
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Circle", "Square", "Triangle", "Star"])
        layout.addWidget(self.shape_combo, 3, 1, 1, 2)

        # Blur amount
        layout.addWidget(QLabel("Blur:"), 4, 0)
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 5)
        self.blur_slider.setValue(0)
        layout.addWidget(self.blur_slider, 4, 1)
        self.blur_value = QLabel("0")
        layout.addWidget(self.blur_value, 4, 2)
        self.blur_slider.valueChanged.connect(
            lambda v: self.blur_value.setText(str(v)))

        # Distortion
        layout.addWidget(QLabel("Distortion:"), 5, 0)
        self.distortion_slider = QSlider(Qt.Horizontal)
        self.distortion_slider.setRange(0, 100)
        self.distortion_slider.setValue(0)
        layout.addWidget(self.distortion_slider, 5, 1)
        self.distortion_value = QLabel("0.0")
        layout.addWidget(self.distortion_value, 5, 2)
        self.distortion_slider.valueChanged.connect(
            lambda v: self.distortion_value.setText(str(v/100)))

        # Particle count
        layout.addWidget(QLabel("Particles:"), 6, 0)
        self.particles_slider = QSlider(Qt.Horizontal)
        self.particles_slider.setRange(10, 300)
        self.particles_slider.setValue(100)
        layout.addWidget(self.particles_slider, 6, 1)
        self.particles_value = QLabel("100")
        layout.addWidget(self.particles_value, 6, 2)
        self.particles_slider.valueChanged.connect(
            lambda v: self.particles_value.setText(str(v)))

        # Particle size
        layout.addWidget(QLabel("Size:"), 7, 0)
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(10)
        layout.addWidget(self.size_slider, 7, 1)
        self.size_value = QLabel("10")
        layout.addWidget(self.size_value, 7, 2)
        self.size_slider.valueChanged.connect(
            lambda v: self.size_value.setText(str(v)))

        # Trail length
        layout.addWidget(QLabel("Trails:"), 8, 0)
        self.trail_slider = QSlider(Qt.Horizontal)
        self.trail_slider.setRange(1, 30)
        self.trail_slider.setValue(5)
        layout.addWidget(self.trail_slider, 8, 1)
        self.trail_value = QLabel("5")
        layout.addWidget(self.trail_value, 8, 2)
        self.trail_slider.valueChanged.connect(
            lambda v: self.trail_value.setText(str(v)))

        group.setLayout(layout)
        return group

    def _create_3d_controls(self):
        """Create 3D effect controls"""
        group = QGroupBox("3D Effects")
        layout = QGridLayout()

        # 3D toggle
        layout.addWidget(QLabel("Enable 3D:"), 0, 0)
        self.enable_3d_check = QCheckBox()
        self.enable_3d_check.setChecked(True)
        layout.addWidget(self.enable_3d_check, 0, 1)

        # Depth influence
        layout.addWidget(QLabel("Depth Effect:"), 1, 0)
        self.depth_slider = QSlider(Qt.Horizontal)
        self.depth_slider.setRange(0, 200)
        self.depth_slider.setValue(100)
        layout.addWidget(self.depth_slider, 1, 1)
        self.depth_value = QLabel("1.0")
        layout.addWidget(self.depth_value, 1, 2)
        self.depth_slider.valueChanged.connect(
            lambda v: self.depth_value.setText(str(v/100)))

        # Perspective
        layout.addWidget(QLabel("Perspective:"), 2, 0)
        self.perspective_slider = QSlider(Qt.Horizontal)
        self.perspective_slider.setRange(300, 1500)
        self.perspective_slider.setValue(800)
        layout.addWidget(self.perspective_slider, 2, 1)
        self.perspective_value = QLabel("800")
        layout.addWidget(self.perspective_value, 2, 2)
        self.perspective_slider.valueChanged.connect(
            lambda v: self.perspective_value.setText(str(v)))

        group.setLayout(layout)
        return group

    def _create_pulse_controls(self):
        """Create pulse effect controls"""
        group = QGroupBox("Pulse System")
        layout = QGridLayout()

        # Pulse toggle
        layout.addWidget(QLabel("Enable Pulse:"), 0, 0)
        self.enable_pulse_check = QCheckBox()
        self.enable_pulse_check.setChecked(True)
        layout.addWidget(self.enable_pulse_check, 0, 1)

        # Pulse strength
        layout.addWidget(QLabel("Strength:"), 1, 0)
        self.pulse_strength_slider = QSlider(Qt.Horizontal)
        self.pulse_strength_slider.setRange(0, 200)
        self.pulse_strength_slider.setValue(100)
        layout.addWidget(self.pulse_strength_slider, 1, 1)
        self.pulse_strength_value = QLabel("1.0")
        layout.addWidget(self.pulse_strength_value, 1, 2)
        self.pulse_strength_slider.valueChanged.connect(
            lambda v: self.pulse_strength_value.setText(str(v/100)))

        # Pulse attack
        layout.addWidget(QLabel("Attack:"), 2, 0)
        self.pulse_attack_slider = QSlider(Qt.Horizontal)
        self.pulse_attack_slider.setRange(1, 50)
        self.pulse_attack_slider.setValue(10)
        layout.addWidget(self.pulse_attack_slider, 2, 1)
        self.pulse_attack_value = QLabel("0.1")
        layout.addWidget(self.pulse_attack_value, 2, 2)
        self.pulse_attack_slider.valueChanged.connect(
            lambda v: self.pulse_attack_value.setText(str(v/100)))

        # Pulse decay
        layout.addWidget(QLabel("Decay:"), 3, 0)
        self.pulse_decay_slider = QSlider(Qt.Horizontal)
        self.pulse_decay_slider.setRange(1, 50)
        self.pulse_decay_slider.setValue(20)
        layout.addWidget(self.pulse_decay_slider, 3, 1)
        self.pulse_decay_value = QLabel("0.2")
        layout.addWidget(self.pulse_decay_value, 3, 2)
        self.pulse_decay_slider.valueChanged.connect(
            lambda v: self.pulse_decay_value.setText(str(v/100)))

        group.setLayout(layout)
        return group

    def _create_audio_controls(self):
        """Create audio processing controls"""
        group = QGroupBox("Audio Controls")
        layout = QGridLayout()

        # Audio sensitivity
        layout.addWidget(QLabel("Sensitivity:"), 0, 0)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(10, 500)
        self.sensitivity_slider.setValue(100)
        layout.addWidget(self.sensitivity_slider, 0, 1)
        self.sensitivity_value = QLabel("1.0")
        layout.addWidget(self.sensitivity_value, 0, 2)
        self.sensitivity_slider.valueChanged.connect(
            lambda v: self.sensitivity_value.setText(str(v/100)))

        # Audio smoothing
        layout.addWidget(QLabel("Smoothing:"), 1, 0)
        self.smoothing_slider = QSlider(Qt.Horizontal)
        self.smoothing_slider.setRange(0, 95)
        self.smoothing_slider.setValue(30)
        layout.addWidget(self.smoothing_slider, 1, 1)
        self.smoothing_value = QLabel("0.3")
        layout.addWidget(self.smoothing_value, 1, 2)
        self.smoothing_slider.valueChanged.connect(
            lambda v: self.smoothing_value.setText(str(v/100)))

        # Bass influence
        layout.addWidget(QLabel("Bass:"), 2, 0)
        self.bass_slider = QSlider(Qt.Horizontal)
        self.bass_slider.setRange(0, 200)
        self.bass_slider.setValue(100)
        layout.addWidget(self.bass_slider, 2, 1)
        self.bass_value = QLabel("1.0")
        layout.addWidget(self.bass_value, 2, 2)
        self.bass_slider.valueChanged.connect(
            lambda v: self.bass_value.setText(str(v/100)))

        # Mids influence
        layout.addWidget(QLabel("Mids:"), 3, 0)
        self.mids_slider = QSlider(Qt.Horizontal)
        self.mids_slider.setRange(0, 200)
        self.mids_slider.setValue(100)
        layout.addWidget(self.mids_slider, 3, 1)
        self.mids_value = QLabel("1.0")
        layout.addWidget(self.mids_value, 3, 2)
        self.mids_slider.valueChanged.connect(
            lambda v: self.mids_value.setText(str(v/100)))

        # Highs influence
        layout.addWidget(QLabel("Highs:"), 4, 0)
        self.highs_slider = QSlider(Qt.Horizontal)
        self.highs_slider.setRange(0, 200)
        self.highs_slider.setValue(100)
        layout.addWidget(self.highs_slider, 4, 1)
        self.highs_value = QLabel("1.0")
        layout.addWidget(self.highs_value, 4, 2)
        self.highs_slider.valueChanged.connect(
            lambda v: self.highs_value.setText(str(v/100)))

        group.setLayout(layout)
        return group

    def _create_display_controls(self):
        """Create display controls"""
        group = QGroupBox("Display Settings")
        layout = QGridLayout()

        # FPS control
        layout.addWidget(QLabel("FPS:"), 0, 0)
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(15, 120)
        self.fps_spin.setValue(60)
        layout.addWidget(self.fps_spin, 0, 1, 1, 2)

        # Fullscreen toggle
        layout.addWidget(QLabel("Fullscreen:"), 1, 0)
        self.fullscreen_check = QCheckBox()
        layout.addWidget(self.fullscreen_check, 1, 1)

        # Monitor selection (for multi-monitor setups)
        layout.addWidget(QLabel("Monitor:"), 2, 0)
        self.monitor_combo = QComboBox()
        # Populate with available monitors
        for i in range(QApplication.desktop().screenCount()):
            self.monitor_combo.addItem(f"Monitor {i+1}")
        layout.addWidget(self.monitor_combo, 2, 1, 1, 2)

        # Frequency display toggle
        layout.addWidget(QLabel("Show Frequency:"), 3, 0)
        self.freq_display_check = QCheckBox()
        self.freq_display_check.setChecked(True)
        layout.addWidget(self.freq_display_check, 3, 1)

        # Frequency display height
        layout.addWidget(QLabel("Freq. Height:"), 4, 0)
        self.freq_height_slider = QSlider(Qt.Horizontal)
        self.freq_height_slider.setRange(50, 300)
        self.freq_height_slider.setValue(150)
        layout.addWidget(self.freq_height_slider, 4, 1)
        self.freq_height_value = QLabel("150")
        layout.addWidget(self.freq_height_value, 4, 2)
        self.freq_height_slider.valueChanged.connect(
            lambda v: self.freq_height_value.setText(str(v)))

        group.setLayout(layout)
        return group

    def _select_base_color(self):
        """Open color dialog for base color selection"""
        color = QColorDialog.getColor(QColor(255, 0, 127), self, "Select Base Color")
        if color.isValid():
            self.base_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_secondary_color(self):
        """Open color dialog for secondary color selection"""
        color = QColorDialog.getColor(QColor(0, 127, 255), self, "Select Secondary Color")
        if color.isValid():
            self.secondary_color_btn.setStyleSheet(f"background-color: {color.name()}")

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

        # Reset wireframe controls
        if hasattr(self, 'enable_wireframe_check'):
            self.enable_wireframe_check.setChecked(True)
            self.cube_size_slider.setValue(100)
            self.cube_rotation_slider.setValue(100)
            self.cube_color_combo.setCurrentIndex(0)
            self.cube_color_btn.setStyleSheet("background-color: #FFFFFF")

        # Reset circular waveform controls
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

    def apply_to_engine(self, engine, audio_processor):
        """Apply all settings to the engine and audio processor"""
        if not engine or not audio_processor:
            return

        # Apply general settings
        engine.set_segments(self.segments_slider.value())
        engine.set_rotation_speed(self.rotation_slider.value() / 100)
        engine.set_symmetry_mode(self.symmetry_combo.currentText().lower())

        # Apply visual settings
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

        # Apply 3D settings
        engine.set_3d_enabled(self.enable_3d_check.isChecked())
        engine.set_depth_influence(self.depth_slider.value() / 100)
        engine.set_perspective(self.perspective_slider.value())

        # Apply pulse settings
        engine.set_pulse_enabled(self.enable_pulse_check.isChecked())
        engine.set_pulse_parameters(
            self.pulse_strength_slider.value() / 100,
            1.0,  # Speed fixed for now
            self.pulse_attack_slider.value() / 100,
            self.pulse_decay_slider.value() / 100
        )

        # Apply audio settings
        audio_processor.set_sensitivity(self.sensitivity_slider.value() / 100)
        audio_processor.set_smoothing(self.smoothing_slider.value() / 100)
        engine.set_audio_influence(
            self.bass_slider.value() / 100,
            self.mids_slider.value() / 100,
            self.highs_slider.value() / 100
        )

        # Apply wireframe settings with debugging
        try:
            # Check if wireframe controls exist
            if hasattr(self, 'enable_wireframe_check'):
                wireframe_enabled = self.enable_wireframe_check.isChecked()
                cube_size = self.cube_size_slider.value()
                rotation_speed = self.cube_rotation_slider.value() / 100

                # Get color mode with proper conversion
                color_mode = self.cube_color_combo.currentText().lower().replace(" ", "_")

                print(f"Setting wireframe: enabled={wireframe_enabled}, size={cube_size}, speed={rotation_speed}, mode={color_mode}")

                # Set wireframe enabled state
                engine.set_wireframe_enabled(wireframe_enabled)

                # Set wireframe parameters
                engine.set_wireframe_parameters(cube_size, rotation_speed, color_mode)

                # Set cube color if in solid mode
                if color_mode == "solid":
                    cube_color = QColor()
                    cube_color.setNamedColor(self.cube_color_btn.styleSheet().split(":")[1].strip())
                    engine.set_wireframe_color(cube_color)
        except Exception as e:
            print(f"Error applying wireframe settings: {e}")


        # Apply circular waveform settings
        try:
            if hasattr(self, 'enable_waveform_check'):
                # Enable/disable waveform
                engine.set_waveform_enabled(self.enable_waveform_check.isChecked())

                # Set waveform parameters
                inner_radius = self.waveform_radius_slider.value()
                line_width = self.waveform_width_slider.value()
                rotation_speed = self.waveform_rotation_slider.value() / 1000.0
                amplitude = self.waveform_amplitude_slider.value() / 100.0

                engine.set_waveform_parameters(inner_radius, line_width, rotation_speed, amplitude)

                # Set colors
                primary_color = QColor()
                primary_color.setNamedColor(self.waveform_color_btn.styleSheet().split(":")[1].strip())

                secondary_color = QColor()
                secondary_color.setNamedColor(self.waveform_secondary_color_btn.styleSheet().split(":")[1].strip())

                use_gradient = self.waveform_color_combo.currentText() == "Gradient"

                engine.set_waveform_colors(primary_color, secondary_color, use_gradient)

                # Set reflection
                show_reflection = self.waveform_reflection_check.isChecked()
                reflection_alpha = self.waveform_reflection_slider.value()

                engine.set_waveform_reflection(show_reflection, reflection_alpha)
        except Exception as e:
            print(f"Error applying waveform settings: {e}")


    def _create_wireframe_controls(self):
        """Create controls for wireframe effects"""
        group = QGroupBox("Wireframe Effects")
        layout = QGridLayout()

        # Enable wireframe cube
        layout.addWidget(QLabel("Show Cube:"), 0, 0)
        self.enable_wireframe_check = QCheckBox()
        self.enable_wireframe_check.setChecked(True)
        layout.addWidget(self.enable_wireframe_check, 0, 1)

        # Cube size
        layout.addWidget(QLabel("Cube Size:"), 1, 0)
        self.cube_size_slider = QSlider(Qt.Horizontal)
        self.cube_size_slider.setRange(50, 300)
        self.cube_size_slider.setValue(100)
        layout.addWidget(self.cube_size_slider, 1, 1)
        self.cube_size_value = QLabel("100")
        layout.addWidget(self.cube_size_value, 1, 2)
        self.cube_size_slider.valueChanged.connect(
            lambda v: self.cube_size_value.setText(str(v)))

        # Rotation speed
        layout.addWidget(QLabel("Rotation Speed:"), 2, 0)
        self.cube_rotation_slider = QSlider(Qt.Horizontal)
        self.cube_rotation_slider.setRange(0, 200)
        self.cube_rotation_slider.setValue(100)
        layout.addWidget(self.cube_rotation_slider, 2, 1)
        self.cube_rotation_value = QLabel("1.0")
        layout.addWidget(self.cube_rotation_value, 2, 2)
        self.cube_rotation_slider.valueChanged.connect(
            lambda v: self.cube_rotation_value.setText(str(v/100)))

        # Color mode
        layout.addWidget(QLabel("Cube Color:"), 3, 0)
        self.cube_color_combo = QComboBox()
        self.cube_color_combo.addItems(["Audio Reactive", "Solid", "Rainbow"])
        layout.addWidget(self.cube_color_combo, 3, 1, 1, 2)

        # Base color
        layout.addWidget(QLabel("Base Color:"), 4, 0)
        self.cube_color_btn = QPushButton()
        self.cube_color_btn.setStyleSheet("background-color: #FFFFFF")
        self.cube_color_btn.clicked.connect(self._select_cube_color)
        layout.addWidget(self.cube_color_btn, 4, 1, 1, 2)

        group.setLayout(layout)
        return group

    def _select_cube_color(self):
        """Open color dialog for cube color selection"""
        color = QColorDialog.getColor(QColor(255, 255, 255), self, "Select Cube Color")
        if color.isValid():
            self.cube_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _create_waveform_controls(self):
        """Create controls for circular waveform visualization"""
        group = QGroupBox("Circular Waveform")
        layout = QGridLayout()

        # Enable waveform
        layout.addWidget(QLabel("Show Waveform:"), 0, 0)
        self.enable_waveform_check = QCheckBox()
        self.enable_waveform_check.setChecked(True)
        layout.addWidget(self.enable_waveform_check, 0, 1)

        # Inner radius percentage
        layout.addWidget(QLabel("Inner Radius:"), 1, 0)
        self.waveform_radius_slider = QSlider(Qt.Horizontal)
        self.waveform_radius_slider.setRange(50, 95)
        self.waveform_radius_slider.setValue(80)
        layout.addWidget(self.waveform_radius_slider, 1, 1)
        self.waveform_radius_value = QLabel("80%")
        layout.addWidget(self.waveform_radius_value, 1, 2)
        self.waveform_radius_slider.valueChanged.connect(
            lambda v: self.waveform_radius_value.setText(f"{v}%"))

        # Line width
        layout.addWidget(QLabel("Line Width:"), 2, 0)
        self.waveform_width_slider = QSlider(Qt.Horizontal)
        self.waveform_width_slider.setRange(1, 10)
        self.waveform_width_slider.setValue(2)
        layout.addWidget(self.waveform_width_slider, 2, 1)
        self.waveform_width_value = QLabel("2")
        layout.addWidget(self.waveform_width_value, 2, 2)
        self.waveform_width_slider.valueChanged.connect(
            lambda v: self.waveform_width_value.setText(str(v)))

        # Rotation speed
        layout.addWidget(QLabel("Rotation:"), 3, 0)
        self.waveform_rotation_slider = QSlider(Qt.Horizontal)
        self.waveform_rotation_slider.setRange(0, 50)
        self.waveform_rotation_slider.setValue(10)
        layout.addWidget(self.waveform_rotation_slider, 3, 1)
        self.waveform_rotation_value = QLabel("0.01")
        layout.addWidget(self.waveform_rotation_value, 3, 2)
        self.waveform_rotation_slider.valueChanged.connect(
            lambda v: self.waveform_rotation_value.setText(f"{v/1000:.3f}"))

        # Amplitude
        layout.addWidget(QLabel("Amplitude:"), 4, 0)
        self.waveform_amplitude_slider = QSlider(Qt.Horizontal)
        self.waveform_amplitude_slider.setRange(50, 300)
        self.waveform_amplitude_slider.setValue(100)
        layout.addWidget(self.waveform_amplitude_slider, 4, 1)
        self.waveform_amplitude_value = QLabel("1.0")
        layout.addWidget(self.waveform_amplitude_value, 4, 2)
        self.waveform_amplitude_slider.valueChanged.connect(
            lambda v: self.waveform_amplitude_value.setText(f"{v/100:.1f}"))

        # Color mode
        layout.addWidget(QLabel("Color Mode:"), 5, 0)
        self.waveform_color_combo = QComboBox()
        self.waveform_color_combo.addItems(["Gradient", "Solid"])
        layout.addWidget(self.waveform_color_combo, 5, 1, 1, 2)

        # Primary color
        layout.addWidget(QLabel("Primary Color:"), 6, 0)
        self.waveform_color_btn = QPushButton()
        self.waveform_color_btn.setStyleSheet("background-color: #FFFFFF")
        self.waveform_color_btn.clicked.connect(self._select_waveform_color)
        layout.addWidget(self.waveform_color_btn, 6, 1, 1, 2)

        # Secondary color
        layout.addWidget(QLabel("Secondary Color:"), 7, 0)
        self.waveform_secondary_color_btn = QPushButton()
        self.waveform_secondary_color_btn.setStyleSheet("background-color: #00C8FF")
        self.waveform_secondary_color_btn.clicked.connect(self._select_waveform_secondary_color)
        layout.addWidget(self.waveform_secondary_color_btn, 7, 1, 1, 2)

        # Enable reflection
        layout.addWidget(QLabel("Show Reflection:"), 8, 0)
        self.waveform_reflection_check = QCheckBox()
        self.waveform_reflection_check.setChecked(True)
        layout.addWidget(self.waveform_reflection_check, 8, 1)

        # Reflection opacity
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
