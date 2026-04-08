"""
Experimental effect control mixins for the kaleidoscope control panel.

Contains controls for: Dimensional Portal, Liquid Metal,
Audio Mycelia, Gravitational Lens, Global Experimental Settings,
and apply-to-engine helpers for experimental colors.
"""

from PyQt5.QtWidgets import (QLabel, QSlider, QPushButton, QCheckBox,
                            QColorDialog, QGroupBox, QGridLayout, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


def _color_from_btn(btn):
    """Extract QColor from a QPushButton's background-color stylesheet."""
    color = QColor()
    color.setNamedColor(btn.styleSheet().split(":")[1].strip())
    return color


class ExperimentalControlsMixin:
    """Mixin providing experimental effect control creation methods."""

    def _create_dimensional_controls(self):
        """Create controls for dimensional portal effect"""
        group = QGroupBox("Dimensional Portal")
        layout = QGridLayout()

        layout.addWidget(QLabel("Enable:"), 0, 0)
        self.dimensional_enable_check = QCheckBox()
        self.dimensional_enable_check.setChecked(False)
        layout.addWidget(self.dimensional_enable_check, 0, 1)

        layout.addWidget(QLabel("Intensity:"), 1, 0)
        self.dimensional_intensity_slider = QSlider(Qt.Horizontal)
        self.dimensional_intensity_slider.setRange(1, 100)
        self.dimensional_intensity_slider.setValue(80)
        layout.addWidget(self.dimensional_intensity_slider, 1, 1)
        self.dimensional_intensity_value = QLabel("0.8")
        layout.addWidget(self.dimensional_intensity_value, 1, 2)
        self.dimensional_intensity_slider.valueChanged.connect(
            lambda v: self.dimensional_intensity_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Inner Color:"), 2, 0)
        self.dimensional_inner_color_btn = QPushButton()
        self.dimensional_inner_color_btn.setStyleSheet("background-color: #140028")
        self.dimensional_inner_color_btn.clicked.connect(self._select_dimensional_inner_color)
        layout.addWidget(self.dimensional_inner_color_btn, 2, 1, 1, 2)

        layout.addWidget(QLabel("Outer Color:"), 3, 0)
        self.dimensional_outer_color_btn = QPushButton()
        self.dimensional_outer_color_btn.setStyleSheet("background-color: #6400FF")
        self.dimensional_outer_color_btn.clicked.connect(self._select_dimensional_outer_color)
        layout.addWidget(self.dimensional_outer_color_btn, 3, 1, 1, 2)

        layout.addWidget(QLabel("Glow Color:"), 4, 0)
        self.dimensional_glow_color_btn = QPushButton()
        self.dimensional_glow_color_btn.setStyleSheet("background-color: #B478FF")
        self.dimensional_glow_color_btn.clicked.connect(self._select_dimensional_glow_color)
        layout.addWidget(self.dimensional_glow_color_btn, 4, 1, 1, 2)

        layout.addWidget(QLabel("Reactive Colors:"), 5, 0)
        self.dimensional_reactive_inner_check = QCheckBox("Inner")
        self.dimensional_reactive_outer_check = QCheckBox("Outer")
        self.dimensional_reactive_glow_check = QCheckBox("Glow")
        reactive_layout = QHBoxLayout()
        reactive_layout.addWidget(self.dimensional_reactive_inner_check)
        reactive_layout.addWidget(self.dimensional_reactive_outer_check)
        reactive_layout.addWidget(self.dimensional_reactive_glow_check)
        layout.addLayout(reactive_layout, 5, 1, 1, 2)

        group.setLayout(layout)
        return group

    def _select_dimensional_inner_color(self):
        color = QColorDialog.getColor(QColor(20, 0, 40), self, "Select Inner Color")
        if color.isValid():
            self.dimensional_inner_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_dimensional_outer_color(self):
        color = QColorDialog.getColor(QColor(100, 0, 255), self, "Select Outer Color")
        if color.isValid():
            self.dimensional_outer_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_dimensional_glow_color(self):
        color = QColorDialog.getColor(QColor(180, 120, 255), self, "Select Glow Color")
        if color.isValid():
            self.dimensional_glow_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _create_liquid_metal_controls(self):
        """Create controls for liquid metal effect"""
        group = QGroupBox("Liquid Metal")
        layout = QGridLayout()

        layout.addWidget(QLabel("Enable:"), 0, 0)
        self.liquid_metal_enable_check = QCheckBox()
        self.liquid_metal_enable_check.setChecked(False)
        layout.addWidget(self.liquid_metal_enable_check, 0, 1)

        layout.addWidget(QLabel("Intensity:"), 1, 0)
        self.liquid_metal_intensity_slider = QSlider(Qt.Horizontal)
        self.liquid_metal_intensity_slider.setRange(1, 100)
        self.liquid_metal_intensity_slider.setValue(80)
        layout.addWidget(self.liquid_metal_intensity_slider, 1, 1)
        self.liquid_metal_intensity_value = QLabel("0.8")
        layout.addWidget(self.liquid_metal_intensity_value, 1, 2)
        self.liquid_metal_intensity_slider.valueChanged.connect(
            lambda v: self.liquid_metal_intensity_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Metal Color:"), 2, 0)
        self.liquid_metal_color_btn = QPushButton()
        self.liquid_metal_color_btn.setStyleSheet("background-color: #C8C8DC")
        self.liquid_metal_color_btn.clicked.connect(self._select_liquid_metal_color)
        layout.addWidget(self.liquid_metal_color_btn, 2, 1, 1, 2)

        layout.addWidget(QLabel("Highlight:"), 3, 0)
        self.liquid_highlight_color_btn = QPushButton()
        self.liquid_highlight_color_btn.setStyleSheet("background-color: #FFFFFF")
        self.liquid_highlight_color_btn.clicked.connect(self._select_liquid_highlight_color)
        layout.addWidget(self.liquid_highlight_color_btn, 3, 1, 1, 2)

        layout.addWidget(QLabel("Shadow:"), 4, 0)
        self.liquid_shadow_color_btn = QPushButton()
        self.liquid_shadow_color_btn.setStyleSheet("background-color: #464664")
        self.liquid_shadow_color_btn.clicked.connect(self._select_liquid_shadow_color)
        layout.addWidget(self.liquid_shadow_color_btn, 4, 1, 1, 2)

        group.setLayout(layout)
        return group

    def _select_liquid_metal_color(self):
        color = QColorDialog.getColor(QColor(200, 200, 220), self, "Select Metal Color")
        if color.isValid():
            self.liquid_metal_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_liquid_highlight_color(self):
        color = QColorDialog.getColor(QColor(255, 255, 255), self, "Select Highlight Color")
        if color.isValid():
            self.liquid_highlight_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_liquid_shadow_color(self):
        color = QColorDialog.getColor(QColor(70, 70, 100), self, "Select Shadow Color")
        if color.isValid():
            self.liquid_shadow_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _create_mycelia_controls(self):
        """Create controls for audio mycelia effect"""
        group = QGroupBox("Audio Mycelia")
        layout = QGridLayout()

        layout.addWidget(QLabel("Enable:"), 0, 0)
        self.mycelia_enable_check = QCheckBox()
        self.mycelia_enable_check.setChecked(False)
        layout.addWidget(self.mycelia_enable_check, 0, 1)

        layout.addWidget(QLabel("Intensity:"), 1, 0)
        self.mycelia_intensity_slider = QSlider(Qt.Horizontal)
        self.mycelia_intensity_slider.setRange(1, 100)
        self.mycelia_intensity_slider.setValue(80)
        layout.addWidget(self.mycelia_intensity_slider, 1, 1)
        self.mycelia_intensity_value = QLabel("0.8")
        layout.addWidget(self.mycelia_intensity_value, 1, 2)
        self.mycelia_intensity_slider.valueChanged.connect(
            lambda v: self.mycelia_intensity_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Growth Rate:"), 2, 0)
        self.mycelia_growth_slider = QSlider(Qt.Horizontal)
        self.mycelia_growth_slider.setRange(50, 300)
        self.mycelia_growth_slider.setValue(150)
        layout.addWidget(self.mycelia_growth_slider, 2, 1)
        self.mycelia_growth_value = QLabel("1.5")
        layout.addWidget(self.mycelia_growth_value, 2, 2)
        self.mycelia_growth_slider.valueChanged.connect(
            lambda v: self.mycelia_growth_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Base Color:"), 3, 0)
        self.mycelia_base_color_btn = QPushButton()
        self.mycelia_base_color_btn.setStyleSheet("background-color: #50DC78")
        self.mycelia_base_color_btn.clicked.connect(self._select_mycelia_base_color)
        layout.addWidget(self.mycelia_base_color_btn, 3, 1, 1, 2)

        layout.addWidget(QLabel("Tip Color:"), 4, 0)
        self.mycelia_tip_color_btn = QPushButton()
        self.mycelia_tip_color_btn.setStyleSheet("background-color: #DCFFC8")
        self.mycelia_tip_color_btn.clicked.connect(self._select_mycelia_tip_color)
        layout.addWidget(self.mycelia_tip_color_btn, 4, 1, 1, 2)

        layout.addWidget(QLabel("Background:"), 5, 0)
        self.mycelia_bg_color_btn = QPushButton()
        self.mycelia_bg_color_btn.setStyleSheet("background-color: #0A140A")
        self.mycelia_bg_color_btn.clicked.connect(self._select_mycelia_bg_color)
        layout.addWidget(self.mycelia_bg_color_btn, 5, 1, 1, 2)

        layout.addWidget(QLabel("BG Opacity:"), 6, 0)
        self.mycelia_bg_opacity_slider = QSlider(Qt.Horizontal)
        self.mycelia_bg_opacity_slider.setRange(0, 200)
        self.mycelia_bg_opacity_slider.setValue(100)
        layout.addWidget(self.mycelia_bg_opacity_slider, 6, 1)
        self.mycelia_bg_opacity_value = QLabel("100")
        layout.addWidget(self.mycelia_bg_opacity_value, 6, 2)
        self.mycelia_bg_opacity_slider.valueChanged.connect(
            lambda v: self.mycelia_bg_opacity_value.setText(str(v)))

        group.setLayout(layout)
        return group

    def _select_mycelia_base_color(self):
        color = QColorDialog.getColor(QColor(80, 220, 120), self, "Select Base Color")
        if color.isValid():
            self.mycelia_base_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_mycelia_tip_color(self):
        color = QColorDialog.getColor(QColor(220, 255, 200), self, "Select Tip Color")
        if color.isValid():
            self.mycelia_tip_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_mycelia_bg_color(self):
        color = QColorDialog.getColor(QColor(10, 20, 10), self, "Select Background Color")
        if color.isValid():
            self.mycelia_bg_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _create_gravitational_lens_controls(self):
        """Create controls for gravitational lens effect"""
        group = QGroupBox("Reality Distortion")
        layout = QGridLayout()

        layout.addWidget(QLabel("Enable:"), 0, 0)
        self.lens_enable_check = QCheckBox()
        self.lens_enable_check.setChecked(False)
        layout.addWidget(self.lens_enable_check, 0, 1)

        layout.addWidget(QLabel("Intensity:"), 1, 0)
        self.lens_intensity_slider = QSlider(Qt.Horizontal)
        self.lens_intensity_slider.setRange(1, 100)
        self.lens_intensity_slider.setValue(80)
        layout.addWidget(self.lens_intensity_slider, 1, 1)
        self.lens_intensity_value = QLabel("0.8")
        layout.addWidget(self.lens_intensity_value, 1, 2)
        self.lens_intensity_slider.valueChanged.connect(
            lambda v: self.lens_intensity_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Distortion:"), 2, 0)
        self.lens_distortion_slider = QSlider(Qt.Horizontal)
        self.lens_distortion_slider.setRange(10, 200)
        self.lens_distortion_slider.setValue(100)
        layout.addWidget(self.lens_distortion_slider, 2, 1)
        self.lens_distortion_value = QLabel("1.0")
        layout.addWidget(self.lens_distortion_value, 2, 2)
        self.lens_distortion_slider.valueChanged.connect(
            lambda v: self.lens_distortion_value.setText(f"{v/100:.1f}"))

        layout.addWidget(QLabel("Grid Color:"), 3, 0)
        self.lens_grid_color_btn = QPushButton()
        self.lens_grid_color_btn.setStyleSheet("background-color: #323250")
        self.lens_grid_color_btn.clicked.connect(self._select_lens_grid_color)
        layout.addWidget(self.lens_grid_color_btn, 3, 1, 1, 2)

        layout.addWidget(QLabel("Lens Color:"), 4, 0)
        self.lens_center_color_btn = QPushButton()
        self.lens_center_color_btn.setStyleSheet("background-color: #6496FF")
        self.lens_center_color_btn.clicked.connect(self._select_lens_center_color)
        layout.addWidget(self.lens_center_color_btn, 4, 1, 1, 2)

        layout.addWidget(QLabel("Edge Color:"), 5, 0)
        self.lens_edge_color_btn = QPushButton()
        self.lens_edge_color_btn.setStyleSheet("background-color: #3264C8")
        self.lens_edge_color_btn.clicked.connect(self._select_lens_edge_color)
        layout.addWidget(self.lens_edge_color_btn, 5, 1, 1, 2)

        layout.addWidget(QLabel("Show Grid:"), 6, 0)
        self.lens_grid_check = QCheckBox()
        self.lens_grid_check.setChecked(True)
        layout.addWidget(self.lens_grid_check, 6, 1)

        group.setLayout(layout)
        return group

    def _select_lens_grid_color(self):
        color = QColorDialog.getColor(QColor(50, 50, 80), self, "Select Grid Color")
        if color.isValid():
            self.lens_grid_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_lens_center_color(self):
        color = QColorDialog.getColor(QColor(100, 150, 255), self, "Select Lens Color")
        if color.isValid():
            self.lens_center_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _select_lens_edge_color(self):
        color = QColorDialog.getColor(QColor(50, 100, 200), self, "Select Edge Color")
        if color.isValid():
            self.lens_edge_color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _create_global_experimental_controls(self):
        """Create global controls for experimental effects"""
        group = QGroupBox("Global Settings")
        layout = QGridLayout()

        layout.addWidget(QLabel("Opacity:"), 0, 0)
        self.experimental_opacity_slider = QSlider(Qt.Horizontal)
        self.experimental_opacity_slider.setRange(10, 100)
        self.experimental_opacity_slider.setValue(80)
        layout.addWidget(self.experimental_opacity_slider, 0, 1)
        self.experimental_opacity_value = QLabel("80%")
        layout.addWidget(self.experimental_opacity_value, 0, 2)
        self.experimental_opacity_slider.valueChanged.connect(
            lambda v: self.experimental_opacity_value.setText(f"{v}%"))

        group.setLayout(layout)
        return group
