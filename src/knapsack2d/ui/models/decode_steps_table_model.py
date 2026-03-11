from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from knapsack2d.models import DecodeStep


class DecodeStepsTableModel(QAbstractTableModel):
    _headers = ["Step", "Gene", "Tested", "Chosen", "Placement", "Reason"]

    def __init__(self) -> None:
        super().__init__()
        self._steps: list[DecodeStep] = []

    def set_steps(self, steps: list[DecodeStep]) -> None:
        self.beginResetModel()
        self._steps = steps
        self.endResetModel()

    def step_at(self, row: int) -> DecodeStep | None:
        if row < 0 or row >= len(self._steps):
            return None
        return self._steps[row]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._steps)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        step = self._steps[index.row()]
        tested = ", ".join(f"({p.x},{p.y})" for p in step.tested_points)
        chosen = (
            None
            if step.chosen_point is None
            else f"({step.chosen_point.x},{step.chosen_point.y})"
        )
        placement = None
        if step.placement is not None:
            p = step.placement
            placement = f"{p.item_id}@({p.x},{p.y}) {p.width}x{p.height}"

        values = [
            index.row(),
            step.gene.item_id,
            tested,
            chosen,
            placement,
            step.reason,
        ]
        return values[index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return section + 1
