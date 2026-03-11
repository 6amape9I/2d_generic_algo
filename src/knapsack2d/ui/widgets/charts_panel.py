from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

import pyqtgraph as pg

from knapsack2d.ga.history import RunHistory


class ChartsPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.best_value_plot = pg.PlotWidget(title="Best Value")
        self.avg_value_plot = pg.PlotWidget(title="Average Value")
        self.diversity_plot = pg.PlotWidget(title="Diversity")
        self.fill_ratio_plot = pg.PlotWidget(title="Best Fill Ratio")
        self.overflow_plot = pg.PlotWidget(title="Best Overflow Count")

        layout.addWidget(self.best_value_plot)
        layout.addWidget(self.avg_value_plot)
        layout.addWidget(self.diversity_plot)
        layout.addWidget(self.fill_ratio_plot)
        layout.addWidget(self.overflow_plot)

        for plot in (
            self.best_value_plot,
            self.avg_value_plot,
            self.diversity_plot,
            self.fill_ratio_plot,
            self.overflow_plot,
        ):
            plot.showGrid(x=True, y=True, alpha=0.25)

    def set_history(self, history: RunHistory) -> None:
        generations = [snapshot.generation_index for snapshot in history.generations]
        best_values = [snapshot.best_total_value for snapshot in history.generations]
        avg_values = [snapshot.avg_total_value for snapshot in history.generations]
        diversities = [snapshot.diversity for snapshot in history.generations]
        fill_ratios = [snapshot.best_fill_ratio for snapshot in history.generations]
        overflows = [snapshot.best_overflow_items for snapshot in history.generations]

        self.best_value_plot.clear()
        self.avg_value_plot.clear()
        self.diversity_plot.clear()
        self.fill_ratio_plot.clear()
        self.overflow_plot.clear()

        self.best_value_plot.plot(generations, best_values, pen="#00A65A")
        self.avg_value_plot.plot(generations, avg_values, pen="#0073B7")
        self.diversity_plot.plot(generations, diversities, pen="#F39C12")
        self.fill_ratio_plot.plot(generations, fill_ratios, pen="#3C8DBC")
        self.overflow_plot.plot(generations, overflows, pen="#DD4B39")
