from __future__ import annotations

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from knapsack2d.ga.history import GenerationSnapshot
from knapsack2d.ui.models.generation_table_model import GenerationTableModel

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_generation_table_model_dimensions_and_values() -> None:
    _app()
    model = GenerationTableModel()
    model.set_generations(
        [
            GenerationSnapshot(
                generation_index=3,
                generation_time_ms=11.2,
                best_individual_id="x",
                best_total_value=42,
                avg_total_value=30.5,
                best_fill_ratio=0.6,
                avg_fill_ratio=0.5,
                diversity=0.15,
                best_valid_items=4,
                best_overflow_items=1,
                individuals=(),
            )
        ]
    )

    assert model.rowCount() == 1
    assert model.columnCount() == 8
    assert model.data(model.index(0, 0), Qt.DisplayRole) == 3
    assert model.data(model.index(0, 1), Qt.DisplayRole) == 42
