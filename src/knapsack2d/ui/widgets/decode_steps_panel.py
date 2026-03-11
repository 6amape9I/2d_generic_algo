from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTableView, QVBoxLayout, QWidget

from knapsack2d.models import DecodeStep
from knapsack2d.ui.models.decode_steps_table_model import DecodeStepsTableModel


class DecodeStepsPanel(QWidget):
    step_selected = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.model = DecodeStepsTableModel()
        self.table = QTableView()
        self.table.setModel(self.model)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)

        self.table.selectionModel().selectionChanged.connect(
            lambda *_: self._emit_current_row()
        )

    def set_steps(self, steps: list[DecodeStep]) -> None:
        self.model.set_steps(steps)
        self.clear_selection()

    def current_step_index(self) -> int:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return -1
        return rows[0].row()

    def select_step(self, row: int) -> None:
        if row < 0 or row >= self.model.rowCount():
            self.clear_selection()
            return
        self.table.selectRow(row)

    def clear_selection(self) -> None:
        self.table.clearSelection()

    def _emit_current_row(self) -> None:
        self.step_selected.emit(self.current_step_index())
