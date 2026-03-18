from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel, QTabWidget, QVBoxLayout, QWidget

import pyqtgraph as pg

from knapsack2d.baseline.exhaustive import ExhaustiveSearchResult
from knapsack2d.ga.history import RunHistory
from knapsack2d.ga.optimizer import GAResult
from knapsack2d.ui.run_models import PopulationStudyResult


class ChartsPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._history_generation_count = 0
        self._population_study_point_count = 0

        root = QVBoxLayout(self)
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        history_tab = QWidget()
        history_layout = QGridLayout(history_tab)

        self.best_value_plot = pg.PlotWidget(title="Best Value by Generation")
        self.avg_value_plot = pg.PlotWidget(title="Average Value by Generation")
        self.diversity_plot = pg.PlotWidget(title="Diversity by Generation")
        self.fill_ratio_plot = pg.PlotWidget(title="Best Fill Ratio by Generation")
        self.overflow_plot = pg.PlotWidget(title="Best Overflow Count by Generation")

        history_layout.addWidget(self.best_value_plot, 0, 0)
        history_layout.addWidget(self.avg_value_plot, 0, 1)
        history_layout.addWidget(self.diversity_plot, 1, 0)
        history_layout.addWidget(self.fill_ratio_plot, 1, 1)
        history_layout.addWidget(self.overflow_plot, 2, 0, 1, 2)

        study_tab = QWidget()
        study_layout = QVBoxLayout(study_tab)
        self.population_study_summary = QLabel("Population study is not available for this run.")
        self.population_study_summary.setWordWrap(True)
        self.population_value_plot = pg.PlotWidget(title="Population Size vs Best Value")
        self.population_duration_plot = pg.PlotWidget(title="Population Size vs Duration")
        study_layout.addWidget(self.population_study_summary)
        study_layout.addWidget(self.population_value_plot)
        study_layout.addWidget(self.population_duration_plot)

        baseline_tab = QWidget()
        baseline_layout = QVBoxLayout(baseline_tab)
        self.baseline_summary = QLabel("Exhaustive baseline is not available for this run.")
        self.baseline_summary.setWordWrap(True)
        self.baseline_value_plot = pg.PlotWidget(title="GA vs Exhaustive Best Value")
        self.baseline_duration_plot = pg.PlotWidget(title="GA vs Exhaustive Duration")
        baseline_layout.addWidget(self.baseline_summary)
        baseline_layout.addWidget(self.baseline_value_plot)
        baseline_layout.addWidget(self.baseline_duration_plot)

        self.tabs.addTab(history_tab, "Run History")
        self.tabs.addTab(study_tab, "Population Study")
        self.tabs.addTab(baseline_tab, "Baseline")

        for plot in (
            self.best_value_plot,
            self.avg_value_plot,
            self.diversity_plot,
            self.fill_ratio_plot,
            self.overflow_plot,
            self.population_value_plot,
            self.population_duration_plot,
            self.baseline_value_plot,
            self.baseline_duration_plot,
        ):
            plot.showGrid(x=True, y=True, alpha=0.25)
            plot.setBackground("w")

        self._configure_bar_axis(self.baseline_value_plot)
        self._configure_bar_axis(self.baseline_duration_plot)

    @property
    def history_generation_count(self) -> int:
        return self._history_generation_count

    @property
    def population_study_point_count(self) -> int:
        return self._population_study_point_count

    def set_history(self, history: RunHistory) -> None:
        generations = [snapshot.generation_index for snapshot in history.generations]
        best_values = [snapshot.best_total_value for snapshot in history.generations]
        avg_values = [snapshot.avg_total_value for snapshot in history.generations]
        diversities = [snapshot.diversity for snapshot in history.generations]
        fill_ratios = [snapshot.best_fill_ratio for snapshot in history.generations]
        overflows = [snapshot.best_overflow_items for snapshot in history.generations]

        self._history_generation_count = len(generations)

        self.best_value_plot.clear()
        self.avg_value_plot.clear()
        self.diversity_plot.clear()
        self.fill_ratio_plot.clear()
        self.overflow_plot.clear()

        self.best_value_plot.plot(generations, best_values, pen="#00A65A", symbol="o", symbolSize=5)
        self.avg_value_plot.plot(generations, avg_values, pen="#0073B7", symbol="o", symbolSize=5)
        self.diversity_plot.plot(generations, diversities, pen="#F39C12", symbol="o", symbolSize=5)
        self.fill_ratio_plot.plot(generations, fill_ratios, pen="#3C8DBC", symbol="o", symbolSize=5)
        self.overflow_plot.plot(generations, overflows, pen="#DD4B39", symbol="o", symbolSize=5)

    def set_population_study(self, study: PopulationStudyResult | None) -> None:
        self.population_value_plot.clear()
        self.population_duration_plot.clear()

        if study is None:
            self._population_study_point_count = 0
            self.population_study_summary.setText("Population study is not available for this run.")
            return

        points = sorted(study.points, key=lambda point: point.population_size)
        populations = [point.population_size for point in points]
        best_values = [point.best_total_value for point in points]
        durations = [point.duration_seconds for point in points]

        self._population_study_point_count = len(points)
        best_point = study.best_point
        self.population_study_summary.setText(
            "Best study point: population "
            f"{best_point.population_size}, value {best_point.best_total_value}, "
            f"fill {best_point.best_fill_ratio:.3f}, duration {best_point.duration_seconds:.3f}s"
        )

        self.population_value_plot.plot(
            populations,
            best_values,
            pen="#111827",
            symbol="o",
            symbolBrush="#111827",
            symbolSize=7,
        )
        self.population_duration_plot.plot(
            populations,
            durations,
            pen="#8B1E3F",
            symbol="o",
            symbolBrush="#8B1E3F",
            symbolSize=7,
        )

    def set_baseline_comparison(
        self,
        ga_result: GAResult,
        exhaustive_result: ExhaustiveSearchResult | None,
    ) -> None:
        self.baseline_value_plot.clear()
        self.baseline_duration_plot.clear()

        ga_value = ga_result.best_individual.fitness_breakdown.total_value
        ga_duration = ga_result.duration_seconds

        if exhaustive_result is None:
            self.baseline_summary.setText(
                f"GA best value {ga_value}, duration {ga_duration:.3f}s. Exhaustive baseline was not run."
            )
            return

        exhaustive_value = exhaustive_result.best_value or 0
        exhaustive_duration = exhaustive_result.duration_seconds
        self.baseline_summary.setText(
            f"GA: value {ga_value}, duration {ga_duration:.3f}s. "
            f"Exhaustive: status {exhaustive_result.status}, value {exhaustive_value}, "
            f"duration {exhaustive_duration:.3f}s, evaluated {exhaustive_result.evaluated_solutions} candidates."
        )

        self._plot_bar_pair(
            self.baseline_value_plot,
            (ga_value, exhaustive_value),
            ("GA", "Exhaustive"),
            "#2563EB",
            "#DC2626",
        )
        self._plot_bar_pair(
            self.baseline_duration_plot,
            (ga_duration, exhaustive_duration),
            ("GA", "Exhaustive"),
            "#2563EB",
            "#DC2626",
        )

    def clear_population_study(self) -> None:
        self.set_population_study(None)

    def _configure_bar_axis(self, plot: pg.PlotWidget) -> None:
        axis = plot.getPlotItem().getAxis("bottom")
        axis.setTicks([[(0, "GA"), (1, "Exhaustive")]])

    def _plot_bar_pair(
        self,
        plot: pg.PlotWidget,
        values: tuple[float, float],
        labels: tuple[str, str],
        color_a: str,
        color_b: str,
    ) -> None:
        axis = plot.getPlotItem().getAxis("bottom")
        axis.setTicks([[(0, labels[0]), (1, labels[1])]])
        plot.addItem(pg.BarGraphItem(x=[0], height=[values[0]], width=0.35, brush=color_a))
        plot.addItem(pg.BarGraphItem(x=[1], height=[values[1]], width=0.35, brush=color_b))
