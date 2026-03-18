from __future__ import annotations

from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout

from knapsack2d.baseline.exhaustive import ExhaustiveSearchResult
from knapsack2d.ga.history import RunHistory
from knapsack2d.ga.optimizer import GAResult
from knapsack2d.ui.run_models import PopulationStudyResult
from knapsack2d.ui.widgets.charts_panel import ChartsPanel


class StatisticsDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Statistics")
        self.setModal(False)
        self.resize(1360, 920)

        root = QVBoxLayout(self)
        self.charts_panel = ChartsPanel(self)
        self.close_button = QPushButton("Close")

        root.addWidget(self.charts_panel, stretch=1)
        root.addWidget(self.close_button)

        self.close_button.clicked.connect(self.close)

    def set_history(self, history: RunHistory) -> None:
        self.charts_panel.set_history(history)

    def set_population_study(self, study: PopulationStudyResult | None) -> None:
        self.charts_panel.set_population_study(study)

    def set_baseline_comparison(
        self,
        ga_result: GAResult,
        exhaustive_result: ExhaustiveSearchResult | None,
    ) -> None:
        self.charts_panel.set_baseline_comparison(ga_result, exhaustive_result)
