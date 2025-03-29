import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QCheckBox,
                           QTextEdit, QSpinBox, QColorDialog, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

from src.core.audio_processing import AudioProcessor
from src.ui.widgets import VisualizationWidget, FrequencyDisplayWidget
from src.ui.control_panel import ControlPanel
from src.ui.debug_console import DebugConsole



# =============================================================================
# Application Module: Main Window
# =============================================================================

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music-Reactive Kaleidoscope Visualizer")
        self.resize(1200, 800)

        # Create central widget with tab layout
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        # Visualization tab
        self.viz_widget = QWidget()
        self.viz_layout = QVBoxLayout()

        # Create visualization widget
        self.visualization = VisualizationWidget()
        self.viz_layout.addWidget(self.visualization)

        # Add frequency display
        self.freq_display = FrequencyDisplayWidget()
        self.freq_display.setMinimumHeight(150)
        self.viz_layout.addWidget(self.freq_display)

        self.viz_widget.setLayout(self.viz_layout)
        self.central_widget.addTab(self.viz_widget, "Visualization")

        # Control panel tab
        self.control_panel = ControlPanel()
        self.central_widget.addTab(self.control_panel, "Controls")

        # Debug console tab
        self.debug_console = DebugConsole()
        self.central_widget.addTab(self.debug_console, "Debug Console")

        # Initialize audio processing
        self.audio_processor = AudioProcessor()
        self.audio_processor.audio_data.connect(self.process_audio)
        self.audio_processor.start()

        # Apply default settings
        self.control_panel.apply_to_engine(
            self.visualization.engine,
            self.audio_processor
        )

        # Connect control panel signals
        self.connect_signals()

        # Log startup
        self.debug_console.log("Application started")
        self.debug_console.log(f"PyAudio initialized, sampling rate: {self.audio_processor.rate}Hz")
        self.debug_console.log(f"Visualization initialized, FPS: {self.visualization.fps}")

    def connect_signals(self):
        """Connect UI control signals to actions"""
        # Connect FPS control
        self.control_panel.fps_spin.valueChanged.connect(self.visualization.set_fps)

        # Connect fullscreen toggle
        self.control_panel.fullscreen_check.stateChanged.connect(self.toggle_fullscreen)

        # Connect frequency display toggle and height
        self.control_panel.freq_display_check.stateChanged.connect(self.toggle_freq_display)
        self.control_panel.freq_height_slider.valueChanged.connect(self.set_freq_display_height)

        # Connect Apply button (we'll update this every time a control changes)
        for obj in self.control_panel.findChildren(QSlider) + \
                  self.control_panel.findChildren(QComboBox) + \
                  self.control_panel.findChildren(QSpinBox) + \
                  self.control_panel.findChildren(QCheckBox):
            if isinstance(obj, QSlider):
                obj.valueChanged.connect(self.apply_settings)
            elif isinstance(obj, QComboBox):
                obj.currentIndexChanged.connect(self.apply_settings)
            elif isinstance(obj, QSpinBox):
                obj.valueChanged.connect(self.apply_settings)
            elif isinstance(obj, QCheckBox):
                obj.stateChanged.connect(self.apply_settings)

        # Connect color buttons
        self.control_panel.base_color_btn.clicked.connect(
            lambda: self.apply_settings_after_delay())
        self.control_panel.secondary_color_btn.clicked.connect(
            lambda: self.apply_settings_after_delay())

    def toggle_freq_display(self, state):
        """Toggle visibility of the frequency display"""
        self.freq_display.setVisible(state == Qt.Checked)
        self.debug_console.log(f"Frequency display {'shown' if state == Qt.Checked else 'hidden'}")

    def set_freq_display_height(self, height):
        """Set the height of the frequency display"""
        self.freq_display.setMinimumHeight(height)
        self.freq_display.setMaximumHeight(height)
        self.debug_console.log(f"Frequency display height set to {height}px")

    def apply_settings(self):
        """Apply all settings from control panel to renderer"""
        self.control_panel.apply_to_engine(
            self.visualization.engine,
            self.audio_processor
        )
        self.debug_console.log("Settings applied")

    def apply_settings_after_delay(self):
        """Apply settings after a short delay (for color dialog)"""
        QTimer.singleShot(100, self.apply_settings)

    def toggle_fullscreen(self, state):
        """Toggle fullscreen mode based on checkbox state"""
        monitor = self.control_panel.monitor_combo.currentIndex()
        self.visualization.toggle_fullscreen(state == Qt.Checked, monitor)
        if state == Qt.Checked:
            self.debug_console.log(f"Entered fullscreen mode on monitor {monitor+1}")
        else:
            self.debug_console.log("Exited fullscreen mode")

    def process_audio(self, spectrum, bands, volume):
        """Process audio data from audio processor"""
        # Update visualizations
        self.visualization.process_audio(spectrum, bands, volume)
        self.freq_display.update_data(spectrum, bands, volume)

    def closeEvent(self, event):
        """Handle application close"""
        # Stop audio processing thread
        self.audio_processor.stop()
        self.debug_console.log("Shutting down...")
        super().closeEvent(event)

