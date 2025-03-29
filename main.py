"""
Music-Reactive Kaleidoscope Visualization Application
- Modular architecture for extensibility
- PyQt5 for all rendering (no Pygame)
- Real-time audio analysis and visualization
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.app.main_window import MainWindow

# =============================================================================
# Entry Point: Application Start
# =============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
