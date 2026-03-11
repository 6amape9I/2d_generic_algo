from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from knapsack2d.ga.history import IndividualSnapshot
from knapsack2d.geometry import is_fully_inside_container
from knapsack2d.models import Placement, ProblemInstance


class GeneTableModel(QAbstractTableModel):
    _headers = ["Pos", "Item ID", "Rotated", "Can Rotate", "Placed", "Inside Container"]

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[tuple[int, str, bool, bool, bool, bool]] = []

    def set_individual(
        self,
        problem: ProblemInstance,
        snapshot: IndividualSnapshot,
    ) -> None:
        item_map = {item.item_id: item for item in problem.items}
        placement_map = self._placement_map(snapshot.decoded_layout.placements)

        rows: list[tuple[int, str, bool, bool, bool, bool]] = []
        for idx, (item_id, rotated) in enumerate(
            zip(snapshot.chromosome_order, snapshot.chromosome_rotations, strict=True)
        ):
            item = item_map[item_id]
            placement = placement_map.get(item_id)
            placed = placement is not None
            inside = (
                is_fully_inside_container(placement, problem.container)
                if placement is not None
                else False
            )
            rows.append((idx, item_id, rotated, item.can_rotate, placed, inside))

        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def clear(self) -> None:
        self.beginResetModel()
        self._rows = []
        self.endResetModel()

    def row_for_item_id(self, item_id: str | None) -> int | None:
        if item_id is None:
            return None
        for row, data in enumerate(self._rows):
            if data[1] == item_id:
                return row
        return None

    def item_id_at(self, row: int) -> str | None:
        if row < 0 or row >= len(self._rows):
            return None
        return self._rows[row][1]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return self._rows[index.row()][index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return section + 1

    def _placement_map(self, placements: list[Placement]) -> dict[str, Placement]:
        mapping: dict[str, Placement] = {}
        for placement in placements:
            if placement.item_id is None:
                continue
            mapping.setdefault(placement.item_id, placement)
        return mapping
