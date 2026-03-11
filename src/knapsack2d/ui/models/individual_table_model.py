from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from knapsack2d.ga.history import IndividualSnapshot


class IndividualTableModel(QAbstractTableModel):
    _headers = ["Rank", "Value", "Fill %", "Valid", "Overflow", "Origin", "Parents"]

    def __init__(self) -> None:
        super().__init__()
        self._individuals: list[IndividualSnapshot] = []

    def set_individuals(self, individuals: list[IndividualSnapshot]) -> None:
        self.beginResetModel()
        self._individuals = individuals
        self.endResetModel()

    def individual_at(self, row: int) -> IndividualSnapshot:
        return self._individuals[row]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._individuals)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        snapshot = self._individuals[index.row()]
        breakdown = snapshot.fitness_breakdown
        column = index.column()
        if column == 0:
            return snapshot.rank_in_generation
        if column == 1:
            return breakdown.total_value
        if column == 2:
            return round(breakdown.fill_ratio * 100.0, 3)
        if column == 3:
            return breakdown.valid_items_count
        if column == 4:
            return breakdown.overflow_items_count
        if column == 5:
            return snapshot.origin_type
        if column == 6:
            return "" if not snapshot.parent_ids else ",".join(snapshot.parent_ids)
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return section + 1
