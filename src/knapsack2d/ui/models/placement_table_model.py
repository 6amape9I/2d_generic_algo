from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from knapsack2d.models import Placement


class PlacementTableModel(QAbstractTableModel):
    _headers = ["Item", "X", "Y", "W", "H", "Rotated", "Value", "Virtual"]

    def __init__(self) -> None:
        super().__init__()
        self._placements: list[Placement] = []

    def set_placements(self, placements: list[Placement]) -> None:
        self.beginResetModel()
        self._placements = placements
        self.endResetModel()

    def clear(self) -> None:
        self.beginResetModel()
        self._placements = []
        self.endResetModel()

    def placement_at(self, row: int) -> Placement | None:
        if row < 0 or row >= len(self._placements):
            return None
        return self._placements[row]

    def row_for_item_id(self, item_id: str | None) -> int | None:
        if item_id is None:
            return None
        for row, placement in enumerate(self._placements):
            if placement.item_id == item_id:
                return row
        return None

    def row_for_placement(self, target: Placement | None) -> int | None:
        if target is None:
            return None
        for row, placement in enumerate(self._placements):
            if placement is target:
                return row
            if (
                placement.item_id == target.item_id
                and placement.x == target.x
                and placement.y == target.y
                and placement.width == target.width
                and placement.height == target.height
                and placement.rotated == target.rotated
                and placement.value == target.value
                and placement.is_virtual == target.is_virtual
            ):
                return row
        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._placements)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        placement = self._placements[index.row()]
        values = [
            placement.item_id,
            placement.x,
            placement.y,
            placement.width,
            placement.height,
            placement.rotated,
            placement.value,
            placement.is_virtual,
        ]
        return values[index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return section + 1
