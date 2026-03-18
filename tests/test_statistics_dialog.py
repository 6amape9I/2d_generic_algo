from __future__ import annotations

import os
import sys

from PySide6.QtWidgets import QApplication

from knapsack2d.baseline.exhaustive import ExhaustiveSearchResult
from knapsack2d.ga.history import RunHistory
from knapsack2d.ga.optimizer import GAResult
from knapsack2d.ui.run_models import PopulationStudyPoint, PopulationStudyResult
from knapsack2d.ui.widgets.statistics_dialog import StatisticsDialog
from tests.test_ui_export import _build_result

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_statistics_dialog_updates_history_population_study_and_baseline() -> None:
    _app()
    dialog = StatisticsDialog()
    problem, ga_result = _build_result()

    dialog.set_history(RunHistory(generations=[]))
    dialog.set_population_study(
        PopulationStudyResult(
            points=(
                PopulationStudyPoint(140, 10, 2, 0.2, 0, 0.1, (10, 2, 4, 0, 0), "a"),
                PopulationStudyPoint(220, 14, 3, 0.3, 0, 0.2, (14, 3, 6, 0, 0), "b"),
                PopulationStudyPoint(320, 12, 2, 0.2, 1, 0.3, (12, 2, 5, -1, 0), "c"),
                PopulationStudyPoint(420, 15, 3, 0.4, 0, 0.4, (15, 3, 8, 0, 0), "d"),
                PopulationStudyPoint(560, 13, 2, 0.3, 0, 0.5, (13, 2, 7, 0, 0), "e"),
            )
        )
    )
    dialog.set_baseline_comparison(
        ga_result,
        ExhaustiveSearchResult(
            status="completed",
            duration_seconds=0.2,
            evaluated_solutions=24,
            total_search_space=24,
            best_chromosome=ga_result.best_individual.chromosome,
            best_fitness_breakdown=ga_result.best_individual.fitness_breakdown,
            best_decoded_layout=ga_result.best_individual.decoded_layout,
            reason=None,
        ),
    )

    assert dialog.charts_panel.history_generation_count == 0
    assert dialog.charts_panel.population_study_point_count == 5
    assert "population 420" in dialog.charts_panel.population_study_summary.text().lower()
    assert "exhaustive" in dialog.charts_panel.baseline_summary.text().lower()
