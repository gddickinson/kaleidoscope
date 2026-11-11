"""Regression test: the wireframe echo trail must use the Echo Opacity setting (needs PyQt5; skipped without it)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PyQt5.QtGui")

from src.core import visualization_components as vc  # noqa: E402


def test_echo_opacity_is_applied(monkeypatch, capsys):
    manager = vc.WireframeManager(size=100)
    manager.set_echo_effect(True, count=3, opacity=0.3, spacing=0.2)
    alphas = []
    monkeypatch.setattr(vc.WireframeShape, "render",
                        lambda self, painter, cx, cy, perspective=800: alphas.append(self.base_color.alpha()))
    manager._render_echo_effect(None, 100, 100, 800)
    assert alphas == [int(255 * 0.3 * (1 - i / 3)) for i in range(3)]
