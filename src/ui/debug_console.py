from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QFont



# =============================================================================
# UI Module: Debug Console
# =============================================================================

class DebugConsole(QWidget):
    """Debug console to display technical information"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Console output
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Courier New", 10))
        layout.addWidget(self.console)

        # Clear button
        clear_btn = QPushButton("Clear Console")
        clear_btn.clicked.connect(self.clear_console)
        layout.addWidget(clear_btn)

        self.setLayout(layout)

    def log(self, message):
        """Add a message to the console"""
        self.console.append(f"[{QTime.currentTime().toString('hh:mm:ss.zzz')}] {message}")

    def clear_console(self):
        """Clear the console"""
        self.console.clear()

