from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLabel, QWidget

from knapsack2d.ga.history import IndividualSnapshot


class IndividualDetailsPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QFormLayout(self)

        self.total_value = QLabel("-")
        self.valid_items = QLabel("-")
        self.overflow_items = QLabel("-")
        self.virtual_blocks = QLabel("-")
        self.used_area = QLabel("-")
        self.fill_ratio = QLabel("-")
        self.origin_type = QLabel("-")
        self.parent_ids = QLabel("-")

        layout.addRow("Total Value", self.total_value)
        layout.addRow("Valid Items", self.valid_items)
        layout.addRow("Overflow Items", self.overflow_items)
        layout.addRow("Virtual Blocks", self.virtual_blocks)
        layout.addRow("Used Area", self.used_area)
        layout.addRow("Fill Ratio", self.fill_ratio)
        layout.addRow("Origin", self.origin_type)
        layout.addRow("Parents", self.parent_ids)

    def set_snapshot(self, snapshot: IndividualSnapshot) -> None:
        breakdown = snapshot.fitness_breakdown
        self.total_value.setText(str(breakdown.total_value))
        self.valid_items.setText(str(breakdown.valid_items_count))
        self.overflow_items.setText(str(breakdown.overflow_items_count))
        self.virtual_blocks.setText(str(breakdown.virtual_blocks_count))
        self.used_area.setText(str(breakdown.used_area_inside))
        self.fill_ratio.setText(f"{breakdown.fill_ratio:.4f}")
        self.origin_type.setText(snapshot.origin_type)
        self.parent_ids.setText("" if not snapshot.parent_ids else ",".join(snapshot.parent_ids))
