from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from knapsack2d.ga.history import GenerationSnapshot


class GenerationTableModel(QAbstractTableModel):
    _headers = [
        "Gen",
        "Best Value",
        "Avg Value",
        "Best Fill %",
        "Diversity",
        "Best Valid",
        "Best Overflow",
        "Elapsed ms",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._generations: list[GenerationSnapshot] = []

    def set_generations(self, generations: list[GenerationSnapshot]) -> None:
        self.beginResetModel()
        self._generations = generations
        self.endResetModel()

    def generation_at(self, row: int) -> GenerationSnapshot:
        return self._generations[row]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._generations)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        snapshot = self._generations[index.row()]
        column = index.column()
        if column == 0:
            return snapshot.generation_index
        if column == 1:
            return snapshot.best_total_value
        if column == 2:
            return round(snapshot.avg_total_value, 3)
        if column == 3:
            return round(snapshot.best_fill_ratio * 100.0, 3)
        if column == 4:
            return round(snapshot.diversity, 4)
        if column == 5:
            return snapshot.best_valid_items
        if column == 6:
            return snapshot.best_overflow_items
        if column == 7:
            return round(snapshot.generation_time_ms, 3)
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return section + 1
