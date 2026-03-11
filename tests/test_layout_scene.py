from __future__ import annotations

import os
import sys

from PySide6.QtWidgets import QApplication

from knapsack2d.models import Container, DecodedLayout, Placement
from knapsack2d.ui.widgets.layout_scene import LayoutScene

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_layout_scene_draws_and_filters_items() -> None:
    _app()
    scene = LayoutScene()
    container = Container(4, 4)
    layout = DecodedLayout(
        placements=[
            Placement("A", 0, 0, 2, 2, False, 10),
            Placement("B", 3, 0, 2, 2, False, 10),
            Placement(None, 2, 0, 1, 1, False, 0, is_virtual=True),
        ],
        steps=[],
        used_solution_order=[],
    )

    scene.set_layout(layout, container, show_virtual=True, show_overflow=True)
    assert scene.placement_items_count() == 3

    scene.set_layout(layout, container, show_virtual=False, show_overflow=True)
    assert scene.placement_items_count() == 2

    scene.set_layout(layout, container, show_virtual=True, show_overflow=False)
    assert scene.placement_items_count() == 2
