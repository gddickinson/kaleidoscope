"""
Wireframe shape control mixins for the kaleidoscope control panel.

Contains controls for: Wireframe basic, visual effects, and advanced settings.
"""

from PyQt5.QtWidgets import (QLabel, QSlider, QComboBox, QPushButton,
                            QCheckBox, QColorDialog, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class WireframeControlsMixin:
    """Mixin providing wireframe shape control creation methods."""

    def _create_wireframe_controls(self):
        """Create controls for enhanced wireframe effects"""
        group = QGroupBox("Wireframe Shapes")
        layout = QGridLayout()

        layout.addWidget(QLabel("Show Wireframe:"), 0, 0)
        self.enable_wireframe_check = QCheckBox()
        self.enable_wireframe_check.setChecked(True)
        layout.addWidget(self.enable_wireframe_check, 0, 1)

        layout.addWidget(QLabel("Show Edges:"), 1, 0)
        self.wireframe_edges_check = QCheckBox()
        self.wireframe_edges_check.setChecked(True)
        layout.addWidget(self.wireframe_edges_check, 1, 1)

        layout.addWidget(QLabel("Shape:"), 2, 0)
        self.wireframe_shape_combo = QComboBox()
        self.wireframe_shape_combo.addItems([
            "Cube", "Pyramid", "Sphere", "Octahedron",
            "Dodecahedron", "Tetrahedron", "Torus"
        ])
        layout.addWidget(self.wireframe_shape_combo, 2, 1, 1, 2)

        layout.addWidget(QLabel("Morph on Change:"), 3, 0)
        self.wireframe_morph_check = QCheckBox()
        self.wireframe_morph_check.setChecked(True)
        layout.addWidget(self.wireframe_morph_check, 3, 1)

        layout.addWidget(QLabel("Size:"), 4, 0)
        self.wireframe_size_slider = QSlider(Qt.Horizontal)
        self.wireframe_size_slider.setRange(50, 300)
        self.wireframe_size_slider.setValue(100)
        layout.addWidget(self.wireframe_size_slider, 4, 1)
        self.wireframe_size_value = QLabel("100")
        layout.addWidget(self.wireframe_size_value, 4, 2)
        self.wireframe_size_slider.valueChanged.connect(
            lambda v: self.wireframe_size_value.setText(str(v)))

        layout.addWidget(QLabel("Rotation Speed:"), 5, 0)
        self.wireframe_rotation_slider = QSlider(Qt.Horizontal)
        self.wireframe_rotation_slider.setRange(0, 200)
        self.wireframe_rotation_slider.setValue(100)
        layout.addWidget(self.wireframe_rotation_slider, 5, 1)
        self.wireframe_rotation_value = QLabel("1.0")
        layout.addWidget(self.wireframe_rotation_value, 5, 2)
        self.wireframe_rotation_slider.valueChanged.connect(
            lambda v: self.wireframe_rotation_value.setText(f"{v/100:.1f}"))

        group.setLayout(layout)
        return group

    def _create_wireframe_visual_controls(self):
        """Create controls for wireframe visual effects"""
        group = QGroupBox("Wireframe Effects")
        layout = QGridLayout()

        layout.addWidget(QLabel("Color Mode:"), 0, 0)
        self.wireframe_color_combo = QComboBox()
        self.wireframe_color_combo.addItems([
            "Audio Reactive", "Solid", "Rainbow", "Gradient"
        ])
        layout.addWidget(self.wireframe_color_combo, 0, 1, 1, 2)

        layout.addWidget(QLabel("Primary Color:"), 1, 0)
        self.wireframe_color_btn = QPushButton()
        self.wireframe_color_btn.setStyleSheet("background-color: #FFFFFF")
        self.wireframe_color_btn.clicked.connect(self._select_wireframe_color)
        layout.addWidget(self.wireframe_color_btn, 1, 1, 1, 2)

        layout.addWidget(QLabel("Secondary Color:"), 2, 0)
        self.wireframe_secondary_color_btn = QPushButton()
        self.wireframe_secondary_color_btn.setStyleSheet("background-color: #00C8FF")
        self.wireframe_secondary_color_btn.clicked.connect(self._select_wireframe_secondary_color)
        layout.addWidget(self.wireframe_secondary_color_btn, 2, 1, 1, 2)

        layout.addWidget(QLabel("Show Vertices:"), 3, 0)
        self.wireframe_vertices_check = QCheckBox()
        self.wireframe_vertices_check.setChecked(False)
        layout.addWidget(self.wireframe_vertices_check, 3, 1)

        layout.addWidget(QLabel("Vertex Size:"), 4, 0)
        self.wireframe_vertex_slider = QSlider(Qt.Horizontal)
        self.wireframe_vertex_slider.setRange(1, 10)
        self.wireframe_vertex_slider.setValue(3)
        layout.addWidget(self.wireframe_vertex_slider, 4, 1)
        self.wireframe_vertex_value = QLabel("3")
        layout.addWidget(self.wireframe_vertex_value, 4, 2)
        self.wireframe_vertex_slider.valueChanged.connect(
            lambda v: self.wireframe_vertex_value.setText(str(v)))

        layout.addWidget(QLabel("Edge Glow:"), 5, 0)
        self.wireframe_glow_check = QCheckBox()
        self.wireframe_glow_check.setChecked(False)
        layout.addWidget(self.wireframe_glow_check, 5, 1)

        layout.addWidget(QLabel("Glow Intensity:"), 6, 0)
        self.wireframe_glow_slider = QSlider(Qt.Horizontal)
        self.wireframe_glow_slider.setRange(10, 100)
        self.wireframe_glow_slider.setValue(50)
        layout.addWidget(self.wireframe_glow_slider, 6, 1)
        self.wireframe_glow_value = QLabel("0.5")
        layout.addWidget(self.wireframe_glow_value, 6, 2)
        self.wireframe_glow_slider.valueChanged.connect(
            lambda v: self.wireframe_glow_value.setText(f"{v/100:.1f}"))

        group.setLayout(layout)
        return group

    def _create_wireframe_advanced_controls(self):
        """Create advanced controls for wireframe effects"""
        group = QGroupBox("Advanced Wireframe")
        layout = QGridLayout()

        layout.addWidget(QLabel("Multiple Shapes:"), 0, 0)
        self.wireframe_multi_check = QCheckBox()
        self.wireframe_multi_check.setChecked(False)
        layout.addWidget(self.wireframe_multi_check, 0, 1)

        layout.addWidget(QLabel("Shape Count:"), 1, 0)
        self.wireframe_count_slider = QSlider(Qt.Horizontal)
        self.wireframe_count_slider.setRange(2, 10)
        self.wireframe_count_slider.setValue(3)
        layout.addWidget(self.wireframe_count_slider, 1, 1)
        self.wireframe_count_value = QLabel("3")
        layout.addWidget(self.wireframe_count_value, 1, 2)
        self.wireframe_count_slider.valueChanged.connect(
            lambda v: self.wireframe_count_value.setText(str(v)))

        layout.addWidget(QLabel("Show Echo:"), 2, 0)
        self.wireframe_echo_check = QCheckBox()
        self.wireframe_echo_check.setChecked(False)
        layout.addWidget(self.wireframe_echo_check, 2, 1)

        layout.addWidget(QLabel("Echo Count:"), 3, 0)
        self.wireframe_echo_count_slider = QSlider(Qt.Horizontal)
        self.wireframe_echo_count_slider.setRange(1, 10)
        self.wireframe_echo_count_slider.setValue(3)
        layout.addWidget(self.wireframe_echo_count_slider, 3, 1)
        self.wireframe_echo_count_value = QLabel("3")
        layout.addWidget(self.wireframe_echo_count_value, 3, 2)
        self.wireframe_echo_count_slider.valueChanged.connect(
            lambda v: self.wireframe_echo_count_value.setText(str(v)))

        layout.addWidget(QLabel("Echo Opacity:"), 4, 0)
        self.wireframe_echo_opacity_slider = QSlider(Qt.Horizontal)
        self.wireframe_echo_opacity_slider.setRange(10, 80)
        self.wireframe_echo_opacity_slider.setValue(30)
        layout.addWidget(self.wireframe_echo_opacity_slider, 4, 1)
        self.wireframe_echo_opacity_value = QLabel("0.3")
        layout.addWidget(self.wireframe_echo_opacity_value, 4, 2)
        self.wireframe_echo_opacity_slider.valueChanged.connect(
            lambda v: self.wireframe_echo_opacity_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Auto Morph:"), 5, 0)
        self.wireframe_auto_morph_check = QCheckBox()
        self.wireframe_auto_morph_check.setChecked(False)
        layout.addWidget(self.wireframe_auto_morph_check, 5, 1)

        layout.addWidget(QLabel("Morph on Beat:"), 6, 0)
        self.wireframe_beat_morph_check = QCheckBox()
        self.wireframe_beat_morph_check.setChecked(False)
        layout.addWidget(self.wireframe_beat_morph_check, 6, 1)

        group.setLayout(layout)
        return group

    def _select_wireframe_color(self):
        """Open color dialog for wireframe primary color selection"""
        color = QColorDialog.getColor(QColor(255, 255, 255), self, "Select Wireframe Color")
        if color.isValid():
            self.wireframe_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_wireframe_secondary_color(self):
        """Open color dialog for wireframe secondary color selection"""
        color = QColorDialog.getColor(QColor(0, 200, 255), self, "Select Wireframe Secondary Color")
        if color.isValid():
            self.wireframe_secondary_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_cube_color(self):
        """Open color dialog for cube color selection"""
        color = QColorDialog.getColor(QColor(255, 255, 255), self, "Select Cube Color")
        if color.isValid():
            self.cube_color_btn.setStyleSheet(f"background-color: {color.name()}")
