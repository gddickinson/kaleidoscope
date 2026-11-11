"""Read the desktop control panel (real `ControlPanel`, PyQt5 offscreen) into a JSON description for the web app.

For every slider, combo box, check box, spin box and colour button the panel creates, in on-screen order: the
attribute name (as used by `ControlPanel.apply_to_engine`), tab, group, label, range and default value. The web app
builds its control panel from this and maps values to the engine exactly as `apply_to_engine` does
(static/settings.js), so the browser starts from the desktop defaults.

`scripts/make_fixtures.py` writes the result to src/web/desktop_defaults.json (served at /api/defaults); the API
itself does not need PyQt5.
"""
import contextlib
import io
import os


def _label_for(widget, layout):
    """Text of the QLabel in column 0 of the widget's grid row (the desktop panel's layout)."""
    from PyQt5.QtWidgets import QGridLayout, QLabel
    if not isinstance(layout, QGridLayout):
        return ""
    idx = layout.indexOf(widget)
    if idx < 0:
        return ""
    row, col, _, _ = layout.getItemPosition(idx)
    if col == 0:
        return ""
    item = layout.itemAtPosition(row, 0)
    w = item.widget() if item else None
    return w.text().rstrip(":") if isinstance(w, QLabel) else ""


def read_panel():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QGroupBox, QPushButton, QSlider, QSpinBox,
                                 QTabWidget)
    _app = QApplication.instance() or QApplication([])
    from src.ui.control_panel import ControlPanel
    with contextlib.redirect_stdout(io.StringIO()):
        panel = ControlPanel()
    names = {id(v): k for k, v in vars(panel).items()}
    tabs = panel.findChild(QTabWidget)
    controls = []
    for t in range(tabs.count()):
        tab_name = tabs.tabText(t)
        for group in tabs.widget(t).findChildren(QGroupBox):
            layout = group.layout()
            if layout is None:
                continue
            for i in range(layout.count()):
                w = layout.itemAt(i).widget()
                name = names.get(id(w))
                if not name:
                    continue
                c = {"name": name, "tab": tab_name, "group": group.title(), "label": _label_for(w, layout)}
                if isinstance(w, QSlider):
                    c.update(kind="slider", min=w.minimum(), max=w.maximum(), value=w.value())
                elif isinstance(w, QSpinBox):
                    c.update(kind="spin", min=w.minimum(), max=w.maximum(), value=w.value())
                elif isinstance(w, QComboBox):
                    c.update(kind="combo", items=[w.itemText(k) for k in range(w.count())], value=w.currentText())
                elif isinstance(w, QCheckBox):
                    c.update(kind="check", value=w.isChecked(), text=w.text())
                elif isinstance(w, QPushButton) and "background-color" in w.styleSheet():
                    c.update(kind="color", value=w.styleSheet().split(":")[1].strip())
                else:
                    continue
                controls.append(c)
    return {"source": "src/ui/control_panel.py (ControlPanel, read offscreen by src/web/desktop_defaults.py)",
            "tabs": [tabs.tabText(t) for t in range(tabs.count())], "controls": controls}
